using CreateAFullStackSolutionForABank.Domain;
using CreateAFullStackSolutionForABank.DTOs;
using CreateAFullStackSolutionForABank.Repositories;

namespace CreateAFullStackSolutionForABank.Services;

public class TransactionService : ITransactionService
{
    private readonly ITransactionRepository _repository;
    private readonly ILogger<TransactionService> _logger;

    public TransactionService(ITransactionRepository repository, ILogger<TransactionService> logger)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public Task<TransferOutcome> TransferAsync(TransferRequestDto request, CancellationToken ct = default)
    {
        if (request is null)
        {
            return Task.FromResult(new TransferOutcome(TransferStatus.ValidationError, null, "Request body is required."));
        }
        if (request.SourceAccountId == request.DestinationAccountId)
        {
            return Task.FromResult(new TransferOutcome(TransferStatus.ValidationError, null, "Source and destination accounts must differ."));
        }
        if (string.IsNullOrWhiteSpace(request.IdempotencyKey))
        {
            return Task.FromResult(new TransferOutcome(TransferStatus.ValidationError, null, "IdempotencyKey is required."));
        }

        _logger.LogInformation("Processing transfer of {Amount} from {Source} to {Destination}",
            request.Amount, request.SourceAccountId, request.DestinationAccountId);
        return _repository.ExecuteTransferAsync(request, ct);
    }

    public Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync(CancellationToken ct = default) =>
        _repository.GetTransactionsAsync(ct);
}
