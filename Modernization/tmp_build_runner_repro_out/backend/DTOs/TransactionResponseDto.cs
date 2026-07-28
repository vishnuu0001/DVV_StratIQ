namespace CreateAFullStackSolutionForABank.DTOs;

public class TransactionResponseDto
{
    public int Id { get; set; }
    public string IdempotencyKey { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public int SourceAccountId { get; set; }
    public int DestinationAccountId { get; set; }
    public decimal SourceBalanceAfter { get; set; }
    public decimal DestinationBalanceAfter { get; set; }
    public DateTime CreatedAt { get; set; }
}
