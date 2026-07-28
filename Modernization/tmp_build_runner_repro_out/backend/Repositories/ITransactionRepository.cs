using CreateAFullStackSolutionForABank.Domain;
using CreateAFullStackSolutionForABank.DTOs;

namespace CreateAFullStackSolutionForABank.Repositories;

public interface ITransactionRepository
{
    Task<TransferOutcome> ExecuteTransferAsync(TransferRequestDto request, CancellationToken ct = default);
    Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync(CancellationToken ct = default);
}
