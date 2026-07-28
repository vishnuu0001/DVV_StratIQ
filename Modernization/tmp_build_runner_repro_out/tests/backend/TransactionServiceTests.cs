using CreateAFullStackSolutionForABank.DTOs;
using CreateAFullStackSolutionForABank.Domain;
using Microsoft.AspNetCore.Mvc.Testing;
using Moq;
using System.Net.Http;
using System.Text.Json;

namespace CreateAFullStackSolutionForABank.Tests.Backend;

public class TransactionServiceTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;
    private readonly Mock<ITransactionRepository> _mockRepository;
    private readonly TransferRequestDto _validRequest = new()
    {
        IdempotencyKey = "test-key-123",
        Amount = 50.00m,
        SourceAccountId = 1,
        DestinationAccountId = 2
    };

    public TransactionServiceTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = _factory.CreateClient();
        _mockRepository = new Mock<ITransactionRepository>();
    }

    [Fact]
    public async Task TransferAsync_WithValidRequest_ReturnsSuccess()
    {
        // Arrange
        var expectedOutcome = new TransferOutcome
        {
            Status = TransferStatus.Success,
            TransactionId = 100,
            SourceBalanceAfter = 950.00m,
            DestinationBalanceAfter = 250.00m,
            CreatedAt = DateTime.UtcNow
        };

        _mockRepository.Setup(r => r.ExecuteTransferAsync(_validRequest, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedOutcome);

        // Act
        var response = await _client.PostAsJsonAsync("/api/transactions", _validRequest);

        // Assert
        response.StatusCode.Should().Be(System.Net.HttpStatusCode.Created);
        
        var content = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<TransactionResponseDto>(content, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
        
        result!.Id.Should().Be(expectedOutcome.TransactionId);
        result.Amount.Should().Be(_validRequest.Amount);
    }

    [Fact]
    public async Task TransferAsync_WithDuplicateIdempotencyKey_ReturnsDuplicateReplay()
    {
        // Arrange
        var duplicateRequest = new TransferRequestDto
        {
            IdempotencyKey = _validRequest.IdempotencyKey,
            Amount = 50.00m,
            SourceAccountId = 1,
            DestinationAccountId = 2
        };

        var expectedOutcome = new TransferOutcome
        {
            Status = TransferStatus.DuplicateReplay,
            TransactionId = 0,
            CreatedAt = DateTime.UtcNow
        };

        _mockRepository.Setup(r => r.ExecuteTransferAsync(duplicateRequest, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedOutcome);

        // Act
        var response = await _client.PostAsJsonAsync("/api/transactions", duplicateRequest);

        // Assert
        response.StatusCode.Should().Be(System.Net.HttpStatusCode.Conflict);
    }

    [Fact]
    public async Task TransferAsync_WithInsufficientFunds_ReturnsInsufficientFunds()
    {
        // Arrange
        var insufficientRequest = new TransferRequestDto
        {
            IdempotencyKey = "insufficient-key",
            Amount = 1000.00m,
            SourceAccountId = 1,
            DestinationAccountId = 2
        };

        var expectedOutcome = new TransferOutcome
        {
            Status = TransferStatus.InsufficientFunds,
            TransactionId = 0,
            CreatedAt = DateTime.UtcNow
        };

        _mockRepository.Setup(r => r.ExecuteTransferAsync(insufficientRequest, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedOutcome);

        // Act
        var response = await _client.PostAsJsonAsync("/api/transactions", insufficientRequest);

        // Assert
        response.StatusCode.Should().Be(System.Net.HttpStatusCode.Conflict);
    }

    [Fact]
    public async Task TransferAsync_WithInvalidAmount_ReturnsValidationError()
    {
        // Arrange
        var invalidAmountRequest = new TransferRequestDto
        {
            IdempotencyKey = "invalid-amount-key",
            Amount = -10.00m,
            SourceAccountId = 1,
            DestinationAccountId = 2
        };

        _mockRepository.Setup(r => r.ExecuteTransferAsync(invalidAmountRequest, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new ValidationException("Amount must be greater than zero."));

        // Act
        var response = await _client.PostAsJsonAsync("/api/transactions", invalidAmountRequest);

        // Assert
        response.StatusCode.Should().Be(System.Net.HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task GetTransactionsAsync_ReturnsListOfTransactions()
    {
        // Arrange
        var mockResponse = new List<TransactionResponseDto>
        {
            new TransactionResponseDto
            {
                Id = 1,
                Amount = 50.00m,
                SourceAccountId = 1,
                DestinationAccountId = 2,
                CreatedAt = DateTime.UtcNow.AddHours(-1)
            }
        };

        _mockRepository.Setup(r => r.GetTransactionsAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(mockResponse);

        // Act - Note: This endpoint is typically GET /api/transactions/history or similar based on implementation
        var response = await _client.GetAsync("/api/transactions");

        // Assert
        response.StatusCode.Should().Be(System.Net.HttpStatusCode.OK);
    }
}
