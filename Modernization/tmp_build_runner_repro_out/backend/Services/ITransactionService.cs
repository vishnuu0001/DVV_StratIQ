using CreateAFullStackSolutionForABank.Domain;
using CreateAFullStackSolutionForABank.DTOs;

namespace CreateAFullStackSolutionForABank.Services;

public interface ITransactionService
{
    Task<TransferOutcome> TransferAsync(TransferRequestDto request, CancellationToken ct = default);
    Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync(CancellationToken ct = default);
}
