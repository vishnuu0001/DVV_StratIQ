using CreateAFullStackSolutionForABank.DTOs;

namespace CreateAFullStackSolutionForABank.Domain;

// Plain result wrapper — NOT an enum. Callers switch on Status
// (outcome.Status switch { TransferStatus.Success => ..., ... }),
// never on the outcome itself.
public record TransferOutcome(TransferStatus Status, TransactionResponseDto? Transaction, string? Error);
