namespace CreateAFullStackSolutionForABank.Domain;

public enum TransferStatus
{
    Success,
    DuplicateReplay,
    InsufficientFunds,
    AccountNotFound,
    ValidationError,
}
