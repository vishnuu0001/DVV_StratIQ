using System.ComponentModel.DataAnnotations;

namespace CreateAFullStackSolutionForABank.DTOs;

public class TransferRequestDto
{
    [Required]
    public string IdempotencyKey { get; set; } = string.Empty;

    [Range(0.01, double.MaxValue, ErrorMessage = "Amount must be greater than zero.")]
    public decimal Amount { get; set; }

    public int SourceAccountId { get; set; }

    public int DestinationAccountId { get; set; }
}
