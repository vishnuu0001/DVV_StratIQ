using Dapper;
using Npgsql;
using CreateAFullStackSolutionForABank.Domain;
using CreateAFullStackSolutionForABank.DTOs;
using CreateAFullStackSolutionForABank.Entities;

namespace CreateAFullStackSolutionForABank.Repositories;

public class TransactionRepository : ITransactionRepository
{
    private readonly string _connectionString;
    private readonly ILogger<TransactionRepository> _logger;

    public TransactionRepository(IConfiguration configuration, ILogger<TransactionRepository> logger)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("Missing DefaultConnection connection string.");
        _logger = logger;
    }

    public async Task<TransferOutcome> ExecuteTransferAsync(TransferRequestDto request, CancellationToken ct = default)
    {
        await using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync(ct);
        await using var transaction = await connection.BeginTransactionAsync(ct);

        try
        {
            var existing = await connection.QuerySingleOrDefaultAsync<Transaction>(
                "SELECT * FROM Transactions WHERE IdempotencyKey = @IdempotencyKey",
                new { request.IdempotencyKey },
                transaction);

            if (existing is not null)
            {
                _logger.LogInformation("Duplicate transfer replay for idempotency key {Key}", request.IdempotencyKey);
                await transaction.CommitAsync(ct);
                return new TransferOutcome(TransferStatus.DuplicateReplay, MapToDto(existing), null);
            }

            var accounts = (await connection.QueryAsync<Account>(
                "SELECT * FROM Accounts WHERE Id IN (@SourceAccountId, @DestinationAccountId) ORDER BY Id FOR UPDATE",
                new { request.SourceAccountId, request.DestinationAccountId },
                transaction)).AsList();

            var source = accounts.FirstOrDefault(a => a.Id == request.SourceAccountId);
            var destination = accounts.FirstOrDefault(a => a.Id == request.DestinationAccountId);

            if (source is null || destination is null)
            {
                await transaction.RollbackAsync(ct);
                _logger.LogWarning("Transfer failed: account not found (source={Source}, destination={Destination})",
                    request.SourceAccountId, request.DestinationAccountId);
                return new TransferOutcome(TransferStatus.AccountNotFound, null, "One or both accounts were not found.");
            }

            if (source.Balance < request.Amount)
            {
                await transaction.RollbackAsync(ct);
                _logger.LogWarning("Transfer failed: insufficient funds on account {Source}", request.SourceAccountId);
                return new TransferOutcome(TransferStatus.InsufficientFunds, null, "Insufficient funds.");
            }

            var sourceBalanceAfter = source.Balance - request.Amount;
            var destinationBalanceAfter = destination.Balance + request.Amount;

            await connection.ExecuteAsync(
                "UPDATE Accounts SET Balance = @Balance WHERE Id = @Id",
                new { Balance = sourceBalanceAfter, Id = source.Id },
                transaction);

            await connection.ExecuteAsync(
                "UPDATE Accounts SET Balance = @Balance WHERE Id = @Id",
                new { Balance = destinationBalanceAfter, Id = destination.Id },
                transaction);

            var newId = await connection.QuerySingleAsync<int>(
                @"INSERT INTO Transactions
                    (IdempotencyKey, Amount, SourceAccountId, DestinationAccountId, SourceBalanceAfter, DestinationBalanceAfter)
                  VALUES
                    (@IdempotencyKey, @Amount, @SourceAccountId, @DestinationAccountId, @SourceBalanceAfter, @DestinationBalanceAfter)
                  RETURNING Id",
                new
                {
                    request.IdempotencyKey,
                    request.Amount,
                    request.SourceAccountId,
                    request.DestinationAccountId,
                    SourceBalanceAfter = sourceBalanceAfter,
                    DestinationBalanceAfter = destinationBalanceAfter,
                },
                transaction);

            await transaction.CommitAsync(ct);

            var createdDto = new TransactionResponseDto
            {
                Id = newId,
                IdempotencyKey = request.IdempotencyKey,
                Amount = request.Amount,
                SourceAccountId = request.SourceAccountId,
                DestinationAccountId = request.DestinationAccountId,
                SourceBalanceAfter = sourceBalanceAfter,
                DestinationBalanceAfter = destinationBalanceAfter,
                CreatedAt = DateTime.UtcNow,
            };

            _logger.LogInformation("Transfer {Id} completed: {Amount} from {Source} to {Destination}",
                newId, request.Amount, request.SourceAccountId, request.DestinationAccountId);

            return new TransferOutcome(TransferStatus.Success, createdDto, null);
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync(ct);
            _logger.LogError(ex, "Transfer failed for idempotency key {Key}", request.IdempotencyKey);
            throw;
        }
    }

    public async Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync(CancellationToken ct = default)
    {
        await using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync(ct);
        var rows = (await connection.QueryAsync<Transaction>(
            "SELECT * FROM Transactions ORDER BY CreatedAt DESC")).AsList();
        return rows.Select(MapToDto).ToList();
    }

    private static TransactionResponseDto MapToDto(Transaction t) => new()
    {
        Id = t.Id,
        IdempotencyKey = t.IdempotencyKey,
        Amount = t.Amount,
        SourceAccountId = t.SourceAccountId,
        DestinationAccountId = t.DestinationAccountId,
        SourceBalanceAfter = t.SourceBalanceAfter,
        DestinationBalanceAfter = t.DestinationBalanceAfter,
        CreatedAt = t.CreatedAt,
    };
}
