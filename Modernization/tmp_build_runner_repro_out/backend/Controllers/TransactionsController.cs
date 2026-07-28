using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using CreateAFullStackSolutionForABank.Domain;
using CreateAFullStackSolutionForABank.DTOs;
using CreateAFullStackSolutionForABank.Services;

namespace CreateAFullStackSolutionForABank.Controllers;

[ApiController]
[Route("api/transactions")]
[Authorize]
public class TransactionsController : ControllerBase
{
    private readonly ITransactionService _service;
    private readonly ILogger<TransactionsController> _logger;

    public TransactionsController(ITransactionService service, ILogger<TransactionsController> logger)
    {
        _service = service ?? throw new ArgumentNullException(nameof(service));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    [HttpPost]
    public async Task<IActionResult> Transfer([FromBody] TransferRequestDto request, CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        try
        {
            var outcome = await _service.TransferAsync(request, ct);
            return outcome.Status switch
            {
                TransferStatus.Success => CreatedAtAction(nameof(GetTransactions), null, outcome.Transaction),
                TransferStatus.DuplicateReplay => Ok(outcome.Transaction),
                TransferStatus.InsufficientFunds => Conflict(new ProblemDetails
                {
                    Title = "Insufficient funds", Detail = outcome.Error, Status = StatusCodes.Status409Conflict,
                }),
                TransferStatus.AccountNotFound => NotFound(new ProblemDetails
                {
                    Title = "Account not found", Detail = outcome.Error, Status = StatusCodes.Status404NotFound,
                }),
                TransferStatus.ValidationError => BadRequest(new ProblemDetails
                {
                    Title = "Validation error", Detail = outcome.Error, Status = StatusCodes.Status400BadRequest,
                }),
                _ => StatusCode(StatusCodes.Status500InternalServerError),
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled error processing transfer");
            return StatusCode(StatusCodes.Status500InternalServerError, new ProblemDetails
            {
                Title = "Unexpected error",
                Detail = "An unexpected error occurred while processing the transfer.",
                Status = StatusCodes.Status500InternalServerError,
            });
        }
    }

    [HttpGet]
    public async Task<IActionResult> GetTransactions(CancellationToken ct)
    {
        var transactions = await _service.GetTransactionsAsync(ct);
        return Ok(transactions);
    }
}
