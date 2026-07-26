# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/scaffolds (money_transfer_demo.py)
# Date: 2026-06-15
# ---------------------------------------------------------------------------
from __future__ import annotations

import functools
import hashlib
import json
import logging
import os
import re
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)



# Function: _money_transfer_contracts
def _money_transfer_contracts(user_prompt: str, signals: Dict[str, Optional[str]]) -> str:
    """Pin the seams most prone to cross-file drift for banking prompts."""
    from ..domain_generators.stack_signals import _detect_domain_requirements
    if not _detect_domain_requirements(user_prompt):
        return ""
    dapper_rule = ""
    if (signals.get("orm") or "").lower() == "dapper":
        dapper_rule = (
            "- TransactionRepository must inject IConfiguration and ILogger<TransactionRepository>. "
            "ExecuteTransferAsync must use one Microsoft.Data.SqlClient.SqlConnection and one DB "
            "transaction; check idempotency first, lock both rows with WITH (UPDLOCK, HOLDLOCK) "
            "(T-SQL — FOR UPDATE is Postgres/MySQL syntax and is a runtime error on SQL Server), "
            "debit, credit, insert the audit row, then commit.\n"
        )
    return (
        "\n\nPINNED MONEY-TRANSFER CONTRACTS (reproduce these exact signatures everywhere):\n"
        "ITransactionRepository: Task<TransferOutcome> ExecuteTransferAsync("
        "TransferRequestDto request, CancellationToken ct = default); and "
        "Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync("
        "CancellationToken ct = default).\n"
        "ITransactionService exposes the same two operations as TransferAsync and "
        "GetTransactionsAsync. Define every interface and implementation exactly once. "
        "Interface files contain interfaces only; implementation files contain implementations only.\n"
        "TransferStatus values: Success, DuplicateReplay, InsufficientFunds, AccountNotFound, "
        "ValidationError. POST maps them to 201/200/409/404/400; GET returns transaction history.\n"
        + dapper_rule +
        "- Program.cs is mandatory and must register controllers, DI, health checks, named CORS, "
        "authentication chained as AddAuthentication(JwtBearerDefaults.AuthenticationScheme)"
        ".AddMicrosoftIdentityWebApi(...), authorization, and middleware in valid order.\n"
        "- Angular uses MsalGuard and MsalInterceptor. Services return Observables; never interpolate "
        "a Promise into an Authorization header and never manually copy tokens from localStorage.\n"
    )


# Function: _money_transfer_backend_files
def _money_transfer_backend_files(root_ns: str) -> Dict[str, str]:
    """Deterministic backend contract + implementation layer for the
    money-transfer domain: entities, DTOs, the status enum + outcome record,
    repository, service, and controller.

    Every one of these was independently invented by the LLM across three
    reviewed iterations and conflated into the SAME failure pattern each
    time: TransferStatus (an enum) redeclared 2-3x, TransferOutcome (meant to
    be a plain result record) used as if IT were the enum in switch
    expressions, a second parallel controller/service pair with a different
    route, Dapper API calls that don't exist (QueryAsync().ToListAsync(),
    BeginTransaction(ct)), and T-SQL written as if it were Postgres (FOR
    UPDATE). None of that is a prompting problem — the exact correct code is
    fully known in advance, so it's generated here instead of asked for.
    """
    files: Dict[str, str] = {}

    files["backend/Domain/TransferStatus.cs"] = textwrap.dedent(f"""\
        namespace {root_ns}.Domain;

        public enum TransferStatus
        {{
            Success,
            DuplicateReplay,
            InsufficientFunds,
            AccountNotFound,
            ValidationError,
        }}
    """)

    files["backend/Domain/TransferOutcome.cs"] = textwrap.dedent(f"""\
        using {root_ns}.DTOs;

        namespace {root_ns}.Domain;

        // Plain result wrapper — NOT an enum. Callers switch on Status
        // (outcome.Status switch {{ TransferStatus.Success => ..., ... }}),
        // never on the outcome itself.
        public record TransferOutcome(TransferStatus Status, TransactionResponseDto? Transaction, string? Error);
    """)

    files["backend/DTOs/TransferRequestDto.cs"] = textwrap.dedent("""\
        using System.ComponentModel.DataAnnotations;

        namespace {root_ns}.DTOs;

        public class TransferRequestDto
        {{
            [Required]
            public string IdempotencyKey {{ get; set; }} = string.Empty;

            [Range(0.01, double.MaxValue, ErrorMessage = "Amount must be greater than zero.")]
            public decimal Amount {{ get; set; }}

            public int SourceAccountId {{ get; set; }}

            public int DestinationAccountId {{ get; set; }}
        }}
    """).format(root_ns=root_ns)

    files["backend/DTOs/TransactionResponseDto.cs"] = textwrap.dedent(f"""\
        namespace {root_ns}.DTOs;

        public class TransactionResponseDto
        {{
            public int Id {{ get; set; }}
            public string IdempotencyKey {{ get; set; }} = string.Empty;
            public decimal Amount {{ get; set; }}
            public int SourceAccountId {{ get; set; }}
            public int DestinationAccountId {{ get; set; }}
            public decimal SourceBalanceAfter {{ get; set; }}
            public decimal DestinationBalanceAfter {{ get; set; }}
            public DateTime CreatedAt {{ get; set; }}
        }}
    """)

    files["backend/Entities/Account.cs"] = textwrap.dedent(f"""\
        namespace {root_ns}.Entities;

        public class Account
        {{
            public int Id {{ get; set; }}
            public string AccountNumber {{ get; set; }} = string.Empty;
            public decimal Balance {{ get; set; }}
            public string Currency {{ get; set; }} = string.Empty;
            public DateTime CreatedAt {{ get; set; }}
        }}
    """)

    files["backend/Entities/Transaction.cs"] = textwrap.dedent(f"""\
        namespace {root_ns}.Entities;

        public class Transaction
        {{
            public int Id {{ get; set; }}
            public string IdempotencyKey {{ get; set; }} = string.Empty;
            public decimal Amount {{ get; set; }}
            public int SourceAccountId {{ get; set; }}
            public int DestinationAccountId {{ get; set; }}
            public decimal SourceBalanceAfter {{ get; set; }}
            public decimal DestinationBalanceAfter {{ get; set; }}
            public DateTime CreatedAt {{ get; set; }}
        }}
    """)

    files["backend/Repositories/ITransactionRepository.cs"] = textwrap.dedent(f"""\
        using {root_ns}.Domain;
        using {root_ns}.DTOs;

        namespace {root_ns}.Repositories;

        public interface ITransactionRepository
        {{
            Task<TransferOutcome> ExecuteTransferAsync(TransferRequestDto request, CancellationToken ct = default);
            Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync(CancellationToken ct = default);
        }}
    """)

    files["backend/Repositories/TransactionRepository.cs"] = textwrap.dedent(f"""\
        using Dapper;
        using Microsoft.Data.SqlClient;
        using {root_ns}.Domain;
        using {root_ns}.DTOs;
        using {root_ns}.Entities;

        namespace {root_ns}.Repositories;

        public class TransactionRepository : ITransactionRepository
        {{
            private readonly string _connectionString;
            private readonly ILogger<TransactionRepository> _logger;

            public TransactionRepository(IConfiguration configuration, ILogger<TransactionRepository> logger)
            {{
                _connectionString = configuration.GetConnectionString("DefaultConnection")
                    ?? throw new InvalidOperationException("Missing DefaultConnection connection string.");
                _logger = logger;
            }}

            public async Task<TransferOutcome> ExecuteTransferAsync(TransferRequestDto request, CancellationToken ct = default)
            {{
                await using var connection = new SqlConnection(_connectionString);
                await connection.OpenAsync(ct);
                await using var transaction = await connection.BeginTransactionAsync(ct);

                try
                {{
                    var existing = await connection.QuerySingleOrDefaultAsync<Transaction>(
                        "SELECT * FROM Transactions WHERE IdempotencyKey = @IdempotencyKey",
                        new {{ request.IdempotencyKey }},
                        transaction);

                    if (existing is not null)
                    {{
                        _logger.LogInformation("Duplicate transfer replay for idempotency key {{Key}}", request.IdempotencyKey);
                        await transaction.CommitAsync(ct);
                        return new TransferOutcome(TransferStatus.DuplicateReplay, MapToDto(existing), null);
                    }}

                    var accounts = (await connection.QueryAsync<Account>(
                        "SELECT * FROM Accounts WITH (UPDLOCK, HOLDLOCK) WHERE Id IN (@SourceAccountId, @DestinationAccountId)",
                        new {{ request.SourceAccountId, request.DestinationAccountId }},
                        transaction)).AsList();

                    var source = accounts.FirstOrDefault(a => a.Id == request.SourceAccountId);
                    var destination = accounts.FirstOrDefault(a => a.Id == request.DestinationAccountId);

                    if (source is null || destination is null)
                    {{
                        await transaction.RollbackAsync(ct);
                        _logger.LogWarning("Transfer failed: account not found (source={{Source}}, destination={{Destination}})",
                            request.SourceAccountId, request.DestinationAccountId);
                        return new TransferOutcome(TransferStatus.AccountNotFound, null, "One or both accounts were not found.");
                    }}

                    if (source.Balance < request.Amount)
                    {{
                        await transaction.RollbackAsync(ct);
                        _logger.LogWarning("Transfer failed: insufficient funds on account {{Source}}", request.SourceAccountId);
                        return new TransferOutcome(TransferStatus.InsufficientFunds, null, "Insufficient funds.");
                    }}

                    var sourceBalanceAfter = source.Balance - request.Amount;
                    var destinationBalanceAfter = destination.Balance + request.Amount;

                    await connection.ExecuteAsync(
                        "UPDATE Accounts SET Balance = @Balance WHERE Id = @Id",
                        new {{ Balance = sourceBalanceAfter, Id = source.Id }},
                        transaction);

                    await connection.ExecuteAsync(
                        "UPDATE Accounts SET Balance = @Balance WHERE Id = @Id",
                        new {{ Balance = destinationBalanceAfter, Id = destination.Id }},
                        transaction);

                    var newId = await connection.QuerySingleAsync<int>(
                        @"INSERT INTO Transactions
                            (IdempotencyKey, Amount, SourceAccountId, DestinationAccountId, SourceBalanceAfter, DestinationBalanceAfter, CreatedAt)
                          OUTPUT INSERTED.Id
                          VALUES
                            (@IdempotencyKey, @Amount, @SourceAccountId, @DestinationAccountId, @SourceBalanceAfter, @DestinationBalanceAfter, SYSUTCDATETIME())",
                        new
                        {{
                            request.IdempotencyKey,
                            request.Amount,
                            request.SourceAccountId,
                            request.DestinationAccountId,
                            SourceBalanceAfter = sourceBalanceAfter,
                            DestinationBalanceAfter = destinationBalanceAfter,
                        }},
                        transaction);

                    await transaction.CommitAsync(ct);

                    var createdDto = new TransactionResponseDto
                    {{
                        Id = newId,
                        IdempotencyKey = request.IdempotencyKey,
                        Amount = request.Amount,
                        SourceAccountId = request.SourceAccountId,
                        DestinationAccountId = request.DestinationAccountId,
                        SourceBalanceAfter = sourceBalanceAfter,
                        DestinationBalanceAfter = destinationBalanceAfter,
                        CreatedAt = DateTime.UtcNow,
                    }};

                    _logger.LogInformation("Transfer {{Id}} completed: {{Amount}} from {{Source}} to {{Destination}}",
                        newId, request.Amount, request.SourceAccountId, request.DestinationAccountId);

                    return new TransferOutcome(TransferStatus.Success, createdDto, null);
                }}
                catch (Exception ex)
                {{
                    await transaction.RollbackAsync(ct);
                    _logger.LogError(ex, "Transfer failed for idempotency key {{Key}}", request.IdempotencyKey);
                    throw;
                }}
            }}

            public async Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync(CancellationToken ct = default)
            {{
                await using var connection = new SqlConnection(_connectionString);
                await connection.OpenAsync(ct);
                var rows = (await connection.QueryAsync<Transaction>(
                    "SELECT * FROM Transactions ORDER BY CreatedAt DESC")).AsList();
                return rows.Select(MapToDto).ToList();
            }}

            private static TransactionResponseDto MapToDto(Transaction t) => new()
            {{
                Id = t.Id,
                IdempotencyKey = t.IdempotencyKey,
                Amount = t.Amount,
                SourceAccountId = t.SourceAccountId,
                DestinationAccountId = t.DestinationAccountId,
                SourceBalanceAfter = t.SourceBalanceAfter,
                DestinationBalanceAfter = t.DestinationBalanceAfter,
                CreatedAt = t.CreatedAt,
            }};
        }}
    """)

    files["backend/Services/ITransactionService.cs"] = textwrap.dedent(f"""\
        using {root_ns}.Domain;
        using {root_ns}.DTOs;

        namespace {root_ns}.Services;

        public interface ITransactionService
        {{
            Task<TransferOutcome> TransferAsync(TransferRequestDto request, CancellationToken ct = default);
            Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync(CancellationToken ct = default);
        }}
    """)

    files["backend/Services/TransactionService.cs"] = textwrap.dedent(f"""\
        using {root_ns}.Domain;
        using {root_ns}.DTOs;
        using {root_ns}.Repositories;

        namespace {root_ns}.Services;

        public class TransactionService : ITransactionService
        {{
            private readonly ITransactionRepository _repository;
            private readonly ILogger<TransactionService> _logger;

            public TransactionService(ITransactionRepository repository, ILogger<TransactionService> logger)
            {{
                _repository = repository ?? throw new ArgumentNullException(nameof(repository));
                _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            }}

            public Task<TransferOutcome> TransferAsync(TransferRequestDto request, CancellationToken ct = default)
            {{
                if (request is null)
                {{
                    return Task.FromResult(new TransferOutcome(TransferStatus.ValidationError, null, "Request body is required."));
                }}
                if (request.SourceAccountId == request.DestinationAccountId)
                {{
                    return Task.FromResult(new TransferOutcome(TransferStatus.ValidationError, null, "Source and destination accounts must differ."));
                }}
                if (string.IsNullOrWhiteSpace(request.IdempotencyKey))
                {{
                    return Task.FromResult(new TransferOutcome(TransferStatus.ValidationError, null, "IdempotencyKey is required."));
                }}

                _logger.LogInformation("Processing transfer of {{Amount}} from {{Source}} to {{Destination}}",
                    request.Amount, request.SourceAccountId, request.DestinationAccountId);
                return _repository.ExecuteTransferAsync(request, ct);
            }}

            public Task<IReadOnlyList<TransactionResponseDto>> GetTransactionsAsync(CancellationToken ct = default) =>
                _repository.GetTransactionsAsync(ct);
        }}
    """)

    files["backend/Controllers/TransactionsController.cs"] = textwrap.dedent(f"""\
        using Microsoft.AspNetCore.Authorization;
        using Microsoft.AspNetCore.Mvc;
        using {root_ns}.Domain;
        using {root_ns}.DTOs;
        using {root_ns}.Services;

        namespace {root_ns}.Controllers;

        [ApiController]
        [Route("api/transactions")]
        [Authorize]
        public class TransactionsController : ControllerBase
        {{
            private readonly ITransactionService _service;
            private readonly ILogger<TransactionsController> _logger;

            public TransactionsController(ITransactionService service, ILogger<TransactionsController> logger)
            {{
                _service = service ?? throw new ArgumentNullException(nameof(service));
                _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            }}

            [HttpPost]
            public async Task<IActionResult> Transfer([FromBody] TransferRequestDto request, CancellationToken ct)
            {{
                if (!ModelState.IsValid)
                {{
                    return ValidationProblem(ModelState);
                }}

                try
                {{
                    var outcome = await _service.TransferAsync(request, ct);
                    return outcome.Status switch
                    {{
                        TransferStatus.Success => CreatedAtAction(nameof(GetTransactions), null, outcome.Transaction),
                        TransferStatus.DuplicateReplay => Ok(outcome.Transaction),
                        TransferStatus.InsufficientFunds => Conflict(new ProblemDetails
                        {{
                            Title = "Insufficient funds", Detail = outcome.Error, Status = StatusCodes.Status409Conflict,
                        }}),
                        TransferStatus.AccountNotFound => NotFound(new ProblemDetails
                        {{
                            Title = "Account not found", Detail = outcome.Error, Status = StatusCodes.Status404NotFound,
                        }}),
                        TransferStatus.ValidationError => BadRequest(new ProblemDetails
                        {{
                            Title = "Validation error", Detail = outcome.Error, Status = StatusCodes.Status400BadRequest,
                        }}),
                        _ => StatusCode(StatusCodes.Status500InternalServerError),
                    }};
                }}
                catch (Exception ex)
                {{
                    _logger.LogError(ex, "Unhandled error processing transfer");
                    return StatusCode(StatusCodes.Status500InternalServerError, new ProblemDetails
                    {{
                        Title = "Unexpected error",
                        Detail = "An unexpected error occurred while processing the transfer.",
                        Status = StatusCodes.Status500InternalServerError,
                    }});
                }}
            }}

            [HttpGet]
            public async Task<IActionResult> GetTransactions(CancellationToken ct)
            {{
                var transactions = await _service.GetTransactionsAsync(ct);
                return Ok(transactions);
            }}
        }}
    """)

    return files


# Function: _money_transfer_program_cs
def _money_transfer_program_cs(root_ns: str) -> str:
    """Deterministic Program.cs for the money-transfer backend — bakes in
    the exact things every reviewed iteration got wrong or omitted: CORS
    (missing entirely), /health (missing, so the k8s probe CrashLoopBackOffs),
    and AddAuthentication(...).AddMicrosoftIdentityWebApi(...) chained
    correctly off AddAuthentication (not AddControllers).

    Program.cs's top-level statements have no implicit namespace search the
    way a file inside a `namespace` block does — `Repositories.Foo` only
    resolves if a namespace named exactly "Repositories" exists at the
    global scope, which it doesn't. This must explicitly `using
    {root_ns}.Repositories;` / `.Services;` (or fully qualify), same as any
    other file in the project.
    """
    # Plain (non-f, non-.format) string with a token substitution at the end
    # — this body is full of literal C# braces, and both f-strings and
    # .format() would require every single one doubled to avoid being
    # misread as a substitution field. A find-and-replace token sidesteps
    # that entirely.
    template = textwrap.dedent("""\
        using Microsoft.AspNetCore.Authentication.JwtBearer;
        using Microsoft.Identity.Web;
        using __ROOT_NS__.Repositories;
        using __ROOT_NS__.Services;

        var builder = WebApplication.CreateBuilder(args);

        builder.Services.AddControllers();
        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen();
        builder.Services.AddHealthChecks();

        builder.Services.AddCors(options =>
        {
            options.AddPolicy("AllowConfiguredOrigins", policy =>
            {
                var allowedOrigins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()
                    ?? new[] { "http://localhost:4200" };
                policy.WithOrigins(allowedOrigins)
                      .AllowAnyHeader()
                      .AllowAnyMethod()
                      .AllowCredentials();
            });
        });

        builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));
        builder.Services.AddAuthorization();

        builder.Services.AddScoped<ITransactionRepository, TransactionRepository>();
        builder.Services.AddScoped<ITransactionService, TransactionService>();

        var app = builder.Build();

        if (app.Environment.IsDevelopment())
        {
            app.UseSwagger();
            app.UseSwaggerUI();
        }

        app.UseCors("AllowConfiguredOrigins");
        app.UseAuthentication();
        app.UseAuthorization();

        app.MapControllers();
        app.MapHealthChecks("/health");

        app.Run();
    """)
    return template.replace("__ROOT_NS__", root_ns)


# Function: _money_transfer_schema_sql
def _money_transfer_schema_sql() -> str:
    """Deterministic schema matching the Entities/Repository field-for-field
    — a separately LLM-generated schema.sql defined a "Transactions" table
    with no IdempotencyKey column at all against a repository that queried
    exactly that column, so idempotency silently never worked."""
    return textwrap.dedent("""\
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Accounts')
        BEGIN
            CREATE TABLE Accounts (
                Id            INT IDENTITY(1,1) PRIMARY KEY,
                AccountNumber NVARCHAR(50)  NOT NULL UNIQUE,
                Balance       DECIMAL(18,2) NOT NULL,
                Currency      NVARCHAR(3)   NOT NULL,
                CreatedAt     DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
            );
        END;

        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Transactions')
        BEGIN
            CREATE TABLE Transactions (
                Id                      INT IDENTITY(1,1) PRIMARY KEY,
                IdempotencyKey          NVARCHAR(255)  NOT NULL UNIQUE,
                Amount                  DECIMAL(18,2)  NOT NULL CHECK (Amount > 0),
                SourceAccountId         INT            NOT NULL FOREIGN KEY REFERENCES Accounts(Id),
                DestinationAccountId    INT            NOT NULL FOREIGN KEY REFERENCES Accounts(Id),
                SourceBalanceAfter      DECIMAL(18,2)  NOT NULL,
                DestinationBalanceAfter DECIMAL(18,2)  NOT NULL,
                CreatedAt               DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
            );
            CREATE INDEX IX_Transactions_IdempotencyKey ON Transactions(IdempotencyKey);
        END;

        IF NOT EXISTS (SELECT 1 FROM Accounts)
        BEGIN
            INSERT INTO Accounts (AccountNumber, Balance, Currency) VALUES
                ('ACC-1001', 5000.00, 'USD'),
                ('ACC-1002', 2500.00, 'USD'),
                ('ACC-1003', 10000.00, 'USD');
        END;
    """)


# Function: _money_transfer_frontend_files
def _money_transfer_frontend_files(is_azure_auth: bool) -> Dict[str, str]:
    """Deterministic frontend model + the ONE data service + (when Entra ID
    is in play) a thin MSAL-backed auth service. Every reviewed iteration
    invented a second competing service (transaction.service AND
    transfer.service, posting to two different URLs, neither matching the
    controller's actual route) and a second competing auth mechanism (MSAL
    wired in AppModule, but a hand-rolled username/password AuthService
    reading a token from localStorage that MSAL never populates). Generating
    the one correct version of each here removes the LLM's opportunity to
    invent a competing one — see _prune_plan_for_baseline's stronger
    per-layer dedup for what happens if it tries anyway."""
    files: Dict[str, str] = {
        "frontend/src/app/core/models/transaction.model.ts": textwrap.dedent("""\
            export interface TransferRequest {
              idempotencyKey: string;
              amount: number;
              sourceAccountId: number;
              destinationAccountId: number;
            }

            export interface TransactionResponse {
              id: number;
              idempotencyKey: string;
              amount: number;
              sourceAccountId: number;
              destinationAccountId: number;
              sourceBalanceAfter: number;
              destinationBalanceAfter: number;
              createdAt: string;
            }
        """),
        "frontend/src/app/core/services/transaction.service.ts": textwrap.dedent("""\
            import { Injectable } from '@angular/core';
            import { HttpClient } from '@angular/common/http';
            import { Observable } from 'rxjs';
            import { environment } from '../../../environments/environment';
            import { TransferRequest, TransactionResponse } from '../models/transaction.model';

            @Injectable({ providedIn: 'root' })
            export class TransactionService {
              private readonly baseUrl = `${environment.apiUrl}/transactions`;

              constructor(private http: HttpClient) {}

              transfer(request: TransferRequest): Observable<TransactionResponse> {
                return this.http.post<TransactionResponse>(this.baseUrl, request);
              }

              getTransactions(): Observable<TransactionResponse[]> {
                return this.http.get<TransactionResponse[]>(this.baseUrl);
              }
            }
        """),
    }
    if is_azure_auth:
        files["frontend/src/app/core/services/auth.service.ts"] = textwrap.dedent("""\
            import { Injectable } from '@angular/core';
            import { MsalService } from '@azure/msal-angular';
            import { AccountInfo } from '@azure/msal-browser';

            // Thin wrapper over MsalService — MSAL owns token acquisition and the token
            // cache. Never read/write a token to localStorage here: MsalInterceptor
            // attaches it to outgoing requests directly, and a hand-rolled token store
            // here would silently disagree with the one MSAL actually uses.
            @Injectable({ providedIn: 'root' })
            export class AuthService {
              constructor(private msalService: MsalService) {}

              isAuthenticated(): boolean {
                return this.msalService.instance.getAllAccounts().length > 0;
              }

              getActiveAccount(): AccountInfo | null {
                return this.msalService.instance.getActiveAccount();
              }

              logout(): void {
                this.msalService.logoutRedirect();
              }
            }
        """)
        files.update({
            "frontend/src/app/app-routing.module.ts": textwrap.dedent("""\
                import { NgModule } from '@angular/core';
                import { RouterModule, Routes } from '@angular/router';
                import { MsalGuard } from '@azure/msal-angular';
                import { TransactionListComponent } from './features/transactions/transaction-list.component';
                import { TransferFormComponent } from './features/transactions/transfer-form.component';

                const routes: Routes = [
                  { path: 'transactions', component: TransactionListComponent, canActivate: [MsalGuard] },
                  { path: 'transfer', component: TransferFormComponent, canActivate: [MsalGuard] },
                  { path: '', redirectTo: 'transactions', pathMatch: 'full' },
                ];

                @NgModule({ imports: [RouterModule.forRoot(routes)], exports: [RouterModule] })
                export class AppRoutingModule {}
            """),
            "frontend/src/app/app.component.ts": textwrap.dedent("""\
                import { Component } from '@angular/core';
                import { MsalService } from '@azure/msal-angular';

                @Component({ selector: 'app-root', templateUrl: './app.component.html', styleUrls: ['./app.component.css'] })
                export class AppComponent {
                  constructor(private readonly msal: MsalService) {}
                  get isAuthenticated(): boolean { return this.msal.instance.getAllAccounts().length > 0; }
                  login(): void { this.msal.loginRedirect(); }
                  logout(): void { this.msal.logoutRedirect(); }
                }
            """),
            "frontend/src/app/app.component.html": textwrap.dedent("""\
                <header><h1>Bank Transfers</h1><nav><a routerLink="/transactions">Transactions</a> <a routerLink="/transfer">New transfer</a></nav>
                <button *ngIf="!isAuthenticated" type="button" (click)="login()">Sign in</button>
                <button *ngIf="isAuthenticated" type="button" (click)="logout()">Sign out</button></header>
                <main><router-outlet></router-outlet></main>
            """),
            "frontend/src/app/app.component.css": "header { display: flex; gap: 1rem; align-items: center; }\nmain { padding: 1rem; }\n",
            "frontend/src/app/app.module.ts": textwrap.dedent("""\
                import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
                import { NgModule } from '@angular/core';
                import { BrowserModule } from '@angular/platform-browser';
                import { ReactiveFormsModule } from '@angular/forms';
                import { MsalGuard, MsalInterceptor, MsalModule } from '@azure/msal-angular';
                import { InteractionType, PublicClientApplication } from '@azure/msal-browser';
                import { environment } from '../environments/environment';
                import { AppComponent } from './app.component';
                import { AppRoutingModule } from './app-routing.module';
                import { TransactionListComponent } from './features/transactions/transaction-list.component';
                import { TransferFormComponent } from './features/transactions/transfer-form.component';

                const protectedResourceMap = new Map<string, string[]>([[`${environment.apiUrl}/**`, [`api://${environment.azureAd.clientId}/access_as_user`]]]);
                @NgModule({
                  declarations: [AppComponent, TransactionListComponent, TransferFormComponent],
                  imports: [BrowserModule, HttpClientModule, ReactiveFormsModule, AppRoutingModule,
                    MsalModule.forRoot(new PublicClientApplication({ auth: { clientId: environment.azureAd.clientId,
                      authority: `https://login.microsoftonline.com/${environment.azureAd.tenantId}`,
                      redirectUri: environment.azureAd.redirectUri } }),
                      { interactionType: InteractionType.Redirect, authRequest: { scopes: ['openid', 'profile'] } },
                      { interactionType: InteractionType.Redirect, protectedResourceMap })],
                  providers: [MsalGuard, { provide: HTTP_INTERCEPTORS, useClass: MsalInterceptor, multi: true }],
                  bootstrap: [AppComponent],
                })
                export class AppModule {}
            """),
            "frontend/src/app/features/transactions/transaction-list.component.ts": textwrap.dedent("""\
                import { Component } from '@angular/core';
                import { Observable, catchError, of } from 'rxjs';
                import { TransactionResponse } from '../../core/models/transaction.model';
                import { TransactionService } from '../../core/services/transaction.service';
                @Component({ selector: 'app-transaction-list', templateUrl: './transaction-list.component.html', styleUrls: ['./transaction-list.component.css'] })
                export class TransactionListComponent {
                  readonly transactions$: Observable<TransactionResponse[]>;
                  constructor(private readonly service: TransactionService) {
                    this.transactions$ = this.service.getTransactions().pipe(catchError(() => of([])));
                  }
                }
            """),
            "frontend/src/app/features/transactions/transfer-form.component.ts": textwrap.dedent("""\
                import { Component } from '@angular/core';
                import { FormBuilder, FormGroup, Validators } from '@angular/forms';
                import { firstValueFrom } from 'rxjs';
                import { TransferRequest } from '../../core/models/transaction.model';
                import { TransactionService } from '../../core/services/transaction.service';
                @Component({ selector: 'app-transfer-form', templateUrl: './transfer-form.component.html', styleUrls: ['./transfer-form.component.css'] })
                export class TransferFormComponent {
                  isSubmitting = false;
                  readonly transferForm: FormGroup;
                  constructor(private readonly fb: FormBuilder, private readonly service: TransactionService) {
                    this.transferForm = this.fb.nonNullable.group({ idempotencyKey: ['', Validators.required], amount: [0, Validators.min(0.01)], sourceAccountId: [0, Validators.required], destinationAccountId: [0, Validators.required] });
                  }
                  async onSubmit(): Promise<void> {
                    if (this.transferForm.invalid || this.isSubmitting) return;
                    this.isSubmitting = true;
                    try { await firstValueFrom(this.service.transfer(this.transferForm.getRawValue() as TransferRequest)); this.transferForm.reset(); }
                    finally { this.isSubmitting = false; }
                  }
                }
            """),
            "frontend/src/app/features/transactions/transfer-form.component.html": "<form [formGroup]=\"transferForm\" (ngSubmit)=\"onSubmit()\"><input formControlName=\"idempotencyKey\" placeholder=\"Idempotency key\"><input type=\"number\" formControlName=\"amount\"><input type=\"number\" formControlName=\"sourceAccountId\"><input type=\"number\" formControlName=\"destinationAccountId\"><button type=\"submit\" [disabled]=\"transferForm.invalid || isSubmitting\">Transfer</button></form>\n",
            "frontend/src/app/features/transactions/transaction-list.component.html": "<ul><li *ngFor=\"let item of transactions$ | async\">{{ item.amount }} — {{ item.createdAt }}</li></ul>\n",
            "frontend/src/app/features/transactions/transfer-form.component.css": "form { display: grid; gap: 1rem; max-width: 32rem; }\n",
            "frontend/src/app/features/transactions/transaction-list.component.css": "ul { list-style: none; padding: 0; }\n",
        })
    return files
