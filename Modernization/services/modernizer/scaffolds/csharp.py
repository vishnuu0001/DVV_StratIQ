# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/scaffolds (csharp.py)
# Date: 2026-02-05
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



# ─── AVEVA MES JS module ───────────────────────────────────────────────────────
# Function: _gen_aveva_js_module
def _gen_aveva_js_module(output: Dict[str, str], root_ns: str, domain: str):
    base = f"ModernizedApp/Frontend/{domain}"
    output[f"{base}/{domain}Module.js"]   = _aveva_module(root_ns, domain)
    output[f"{base}/{domain}Config.json"] = _aveva_config(domain)


# Function: _aveva_module
def _aveva_module(root_ns: str, domain: str) -> str:
    return textwrap.dedent(f"""\
        /**
         * {domain} MES UI Module
         * AVEVA MES architecture — JavaScript UI module
         * Communicates with .NET 8 backend via REST API
         */

        const {domain}Module = (function () {{

          const API_BASE = window.MES_CONFIG?.apiBase || '/api/{domain.lower()}';

          async function _fetch(url, options = {{}}) {{
            const defaultHeaders = {{ 'Content-Type': 'application/json' }};
            const response = await fetch(url, {{ ...options, headers: {{ ...defaultHeaders, ...options.headers }} }});
            if (!response.ok) throw new Error(`API Error ${{response.status}}: ${{await response.text()}}`);
            return response.json();
          }}

          return {{
            /**
             * Load and render {domain} data into target element.
             * @param {{HTMLElement}} container - Target DOM element
             * @param {{object}} options - Filter/paging options
             */
            async load(container, options = {{}}) {{
              container.innerHTML = '<div class="mes-loading">Loading {domain}...</div>';
              try {{
                const data = await _fetch(`${{API_BASE}}?${{new URLSearchParams(options)}}`);
                this.render(container, data);
              }} catch (err) {{
                container.innerHTML = `<div class="mes-error">${{err.message}}</div>`;
              }}
            }},

            render(container, items) {{
              if (!items?.length) {{
                container.innerHTML = '<div class="mes-empty">No {domain} records found.</div>';
                return;
              }}
              container.innerHTML = `
                <table class="mes-data-grid">
                  <thead>
                    <tr>
                      ${{Object.keys(items[0]).map(k => `<th>${{k}}</th>`).join('')}}
                    </tr>
                  </thead>
                  <tbody>
                    ${{items.map(row => `<tr>${{Object.values(row).map(v =>
                      `<td>${{v ?? ''}}</td>`).join('')}}</tr>`).join('')}}
                  </tbody>
                </table>`;
            }},

            async create(data) {{
              return _fetch(API_BASE, {{ method: 'POST', body: JSON.stringify(data) }});
            }},

            async update(id, data) {{
              return _fetch(`${{API_BASE}}/${{id}}`, {{ method: 'PUT', body: JSON.stringify(data) }});
            }},

            async remove(id) {{
              return _fetch(`${{API_BASE}}/${{id}}`, {{ method: 'DELETE' }});
            }},
          }};
        }})();

        if (typeof module !== 'undefined') module.exports = {domain}Module;
    """)


# Function: _aveva_config
def _aveva_config(domain: str) -> str:
    import json as _json
    return _json.dumps({
        "moduleName":  domain,
        "apiEndpoint": f"/api/{domain.lower()}",
        "refreshInterval": 30000,
        "permissions": {"read": True, "write": True, "delete": False},
        "gridColumns": ["id", "name", "isActive", "createdAt"],
    }, indent=2)


# ─── MSSQL schema ─────────────────────────────────────────────────────────────
# Function: _mssql_schema
def _mssql_schema(tables: List[str], analysis: dict) -> str:
    lines = ["-- MS SQL Server schema — generated from Oracle analysis\n",
             "-- Review and adjust column types before applying to production.\n\n"]

    # Map Oracle column type patterns to MSSQL
    oracle_to_mssql = {
        "VARCHAR2": "NVARCHAR",
        "NUMBER":   "DECIMAL",
        "DATE":     "DATETIME2",
        "CLOB":     "NVARCHAR(MAX)",
        "BLOB":     "VARBINARY(MAX)",
        "CHAR":     "NCHAR",
    }

    known_tables = {
        "CUSTOMERS": [
            ("CustomerId",    "INT IDENTITY(1,1) PRIMARY KEY"),
            ("Username",      "NVARCHAR(50) NOT NULL UNIQUE"),
            ("PasswordHash",  "NVARCHAR(64) NOT NULL"),
            ("FirstName",     "NVARCHAR(50) NOT NULL"),
            ("LastName",      "NVARCHAR(50) NOT NULL"),
            ("Email",         "NVARCHAR(100) NOT NULL UNIQUE"),
            ("Phone",         "NVARCHAR(20)"),
            ("Address",       "NVARCHAR(200)"),
            ("City",          "NVARCHAR(50)"),
            ("State",         "NVARCHAR(50)"),
            ("ZipCode",       "NVARCHAR(10)"),
            ("Role",          "NVARCHAR(20) NOT NULL DEFAULT 'CUSTOMER'"),
            ("IsActive",      "BIT NOT NULL DEFAULT 1"),
            ("LastLoginDate", "DATETIME2"),
            ("CreatedDate",   "DATETIME2 NOT NULL DEFAULT GETUTCDATE()"),
            ("UpdatedDate",   "DATETIME2"),
        ],
        "ACCOUNTS": [
            ("AccountId",      "INT IDENTITY(1,1) PRIMARY KEY"),
            ("CustomerId",     "INT NOT NULL REFERENCES dbo.Customers(CustomerId)"),
            ("AccountNumber",  "NVARCHAR(20) NOT NULL UNIQUE"),
            ("AccountType",    "NVARCHAR(20) NOT NULL"),
            ("Balance",        "DECIMAL(18,2) NOT NULL DEFAULT 0"),
            ("Currency",       "NVARCHAR(3) NOT NULL DEFAULT 'USD'"),
            ("OpenDate",       "DATETIME2 NOT NULL DEFAULT GETUTCDATE()"),
            ("Status",         "NVARCHAR(20) NOT NULL DEFAULT 'ACTIVE'"),
            ("InterestRate",   "DECIMAL(5,4) NOT NULL DEFAULT 0"),
            ("OverdraftLimit", "DECIMAL(18,2) NOT NULL DEFAULT 0"),
            ("UpdatedDate",    "DATETIME2"),
        ],
        "TRANSACTIONS": [
            ("TransactionId",   "INT IDENTITY(1,1) PRIMARY KEY"),
            ("FromAccountId",   "INT NOT NULL REFERENCES dbo.Accounts(AccountId)"),
            ("ToAccountId",     "INT REFERENCES dbo.Accounts(AccountId)"),
            ("TransactionType", "NVARCHAR(20) NOT NULL"),
            ("Amount",          "DECIMAL(18,2) NOT NULL"),
            ("Currency",        "NVARCHAR(3) NOT NULL DEFAULT 'USD'"),
            ("TransactionDate", "DATETIME2 NOT NULL DEFAULT GETUTCDATE()"),
            ("Description",     "NVARCHAR(200)"),
            ("ReferenceNumber", "NVARCHAR(50)"),
            ("Status",          "NVARCHAR(20) NOT NULL DEFAULT 'COMPLETED'"),
        ],
        "AUDIT_LOG": [
            ("AuditId",    "INT IDENTITY(1,1) PRIMARY KEY"),
            ("EventType",  "NVARCHAR(30) NOT NULL"),
            ("UserId",     "INT"),
            ("Username",   "NVARCHAR(50)"),
            ("IpAddress",  "NVARCHAR(45)"),
            ("SessionId",  "NVARCHAR(100)"),
            ("Detail",     "NVARCHAR(500)"),
            ("EventDate",  "DATETIME2 NOT NULL DEFAULT GETUTCDATE()"),
        ],
    }

    lines.append("USE ModernizedBankingDB;\nGO\n\n")

    emitted = set()
    for table in (known_tables.keys() if not tables else [t.upper() for t in tables]):
        table_key = table.replace("BANKING_USER.", "")
        columns = known_tables.get(table_key)
        if not columns:
            col_sql = "    Id INT IDENTITY(1,1) PRIMARY KEY,\n    -- TODO: add columns"
        else:
            col_sql = ",\n".join(f"    {col} {dtype}" for col, dtype in columns)
        pascal = table_key.capitalize().rstrip("S") + "s"
        lines.append(f"CREATE TABLE dbo.{pascal} (\n{col_sql}\n);\nGO\n\n")
        emitted.add(table_key)

    # Index hints
    lines.append(
        "-- Recommended indexes\n"
        "CREATE INDEX IX_Accounts_CustomerId     ON dbo.Accounts(CustomerId);\n"
        "CREATE INDEX IX_Transactions_FromAccount ON dbo.Transactions(FromAccountId);\n"
        "CREATE INDEX IX_Transactions_Date        ON dbo.Transactions(TransactionDate);\n"
        "CREATE INDEX IX_AuditLog_UserId          ON dbo.AuditLog(UserId);\n"
        "CREATE INDEX IX_AuditLog_EventDate       ON dbo.AuditLog(EventDate);\nGO\n"
    )

    return "".join(lines)


# ─── Migration notes ──────────────────────────────────────────────────────────
# Function: _migration_notes
def _migration_notes(oracle_patterns: List[str]) -> str:
    mappings = {
        "Oracle ROWNUM pagination":  "Use `ROW_NUMBER() OVER (ORDER BY ...) BETWEEN @start AND @end`",
        "Oracle SYSDATE":            "Replace with `GETUTCDATE()`",
        "Oracle NVL function":       "Replace `NVL(a, b)` with `ISNULL(a, b)` or `COALESCE(a, b)`",
        "Oracle DECODE function":    "Replace `DECODE(x, v1, r1, ...)` with `CASE x WHEN v1 THEN r1 ... END`",
        "Oracle sequence NEXTVAL":   "Replace with `IDENTITY(1,1)` column property",
        "Oracle DUAL table":         "Remove `FROM DUAL`; use `SELECT <expr>` directly",
        "Oracle hierarchical query": "Replace `CONNECT BY ... START WITH` with recursive CTE `WITH ... AS`",
        "Oracle MERGE statement":    "MSSQL supports MERGE natively — syntax is identical",
        "Oracle VARCHAR2 type":      "Replace `VARCHAR2(n)` with `NVARCHAR(n)`",
        "Oracle NUMBER type":        "Replace `NUMBER(p,s)` with `DECIMAL(p,s)`",
        "Oracle LOB types":          "Replace `CLOB/NCLOB` with `NVARCHAR(MAX)`, `BLOB` with `VARBINARY(MAX)`",
        "Oracle dynamic SQL":        "Replace `EXECUTE IMMEDIATE` with `sp_executesql`",
        "Oracle DBMS_OUTPUT package": "Remove — use application logging instead",
        "Oracle TRIGGER":            "MSSQL supports triggers — rewrite using MSSQL syntax",
        "Oracle PROCEDURE":          "MSSQL supports stored procedures — rewrite using T-SQL syntax",
    }

    lines = ["# Oracle → MS SQL Migration Notes\n\n"]
    lines.append("## Detected Oracle Constructs\n")
    if oracle_patterns:
        for pat in oracle_patterns:
            mapping = mappings.get(pat, "Review manually")
            lines.append(f"- **{pat}**  \n  ↳ {mapping}\n")
    else:
        lines.append("_No Oracle-specific constructs detected in source code._\n")

    lines.append(textwrap.dedent("""
        ## Connection String Change
        **Oracle:**
        ```
        Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))
        (CONNECT_DATA=(SERVICE_NAME=ORCL)));User Id=BANKING_USER;Password=...;
        ```
        **MS SQL (EF Core):**
        ```
        Server=localhost;Database=ModernizedBankingDB;Trusted_Connection=True;
        ```

        ## ADO.NET → EF Core
        Replace all `OracleHelper.ExecuteReader / ExecuteNonQuery` calls with
        EF Core `DbContext` queries using LINQ or `FromSqlRaw`.

        ## Authentication / Password Hashing
        Replace Oracle `STANDARD_HASH('password','SHA256')` with
        `BCrypt.Net.BCrypt.HashPassword()` in the application layer.
    """))

    return "".join(lines)


# ─── .sln file ────────────────────────────────────────────────────────────────
# Function: _solution_file
def _solution_file(root_ns: str, domains: List[str]) -> str:
    project_entries = []
    for d in domains:
        dn = d.capitalize()
        guid = _deterministic_guid(dn)
        project_entries.append(
            f'Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = '
            f'"{dn}Service", "Services/{dn}Service/{dn}Service.csproj", '
            f'"{{{guid}}}"\n'
            f'EndProject'
        )
    gw_guid = _deterministic_guid("ApiGateway")
    project_entries.append(
        f'Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = '
        f'"ApiGateway", "ApiGateway/ApiGateway.csproj", "{{{gw_guid}}}"\n'
        f'EndProject'
    )
    return (
        "Microsoft Visual Studio Solution File, Format Version 12.00\n"
        "# Visual Studio Version 17\n"
        + "\n".join(project_entries)
    )


# Function: _deterministic_guid
def _deterministic_guid(name: str) -> str:
    import hashlib
    h = hashlib.sha256(name.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


# ─── Per-domain service generation ───────────────────────────────────────────
# Function: _gen_service
def _gen_service_scaffold(output: Dict[str, str], root_ns: str, domain: str, is_dapper: bool = False, db_target: str = "mssql"):
    """Project scaffolding only — csproj, Program.cs, appsettings.json, and
    (for Dapper) the connection factory. Used when the LLM already produced a
    complete Endpoints/Service/Repository trio for this domain, so the
    deterministic CRUD templates (_model_class/_repo_*/_service_*, which use
    the SAME I{domain}Service/{domain}ServiceImpl names as the LLM prompts)
    are skipped rather than emitting a second, colliding definition.
    """
    base = f"ModernizedApp/Services/{domain}Service"
    output[f"{base}/{domain}Service.csproj"] = _service_csproj(root_ns, domain, is_dapper, db_target)
    output[f"{base}/Program.cs"]             = _service_program_llm_backend(root_ns, domain, is_dapper, db_target)
    output[f"{base}/appsettings.json"]       = _appsettings(root_ns, domain)
    if is_dapper:
        output[f"{base}/Data/IDbConnectionFactory.cs"] = _db_connection_factory(root_ns, domain, db_target)
    # EF Core: the LLM repository prompt asks for its own {root_ns}DbContext
    # partial class embedded directly in Repositories/{domain}Repository.cs —
    # no separate Data/AppDbContext.cs, which would just be the same kind of
    # duplicate definition this function exists to avoid.


# Function: _service_program_llm_backend
def _service_program_llm_backend(root_ns: str, domain: str, is_dapper: bool = False, db_target: str = "mssql") -> str:
    """Program.cs that wires up the LLM-generated {domain}Endpoints /
    {domain}ServiceImpl / {domain}Repository for this domain — the
    LLM-backend counterpart to _service_program(), which wires up the
    deterministic template versions instead. Never mix the two: the classes
    have matching names but come from different files depending on which
    path ran (see _gen_service_scaffold)."""
    if is_dapper:
        extra_using = f"using {root_ns}.{domain}Service.Data;"
        data_access_registration = "builder.Services.AddSingleton<IDbConnectionFactory, SqlConnectionFactory>();"
    else:
        extra_using = "using Microsoft.EntityFrameworkCore;"
        provider = "UseNpgsql" if db_target == "postgres" else "UseSqlServer"
        data_access_registration = (
            f'builder.Services.AddDbContext<{root_ns}DbContext>(opt =>\n'
            f'            opt.{provider}(builder.Configuration.GetConnectionString("DefaultConnection")));'
        )
    return textwrap.dedent(f"""\
        {extra_using}
        using {root_ns}.{domain}Service.Endpoints;
        using {root_ns}.{domain}Service.Repositories;
        using {root_ns}.{domain}Service.Services;

        var builder = WebApplication.CreateBuilder(args);

        {data_access_registration}

        builder.Services.AddScoped<I{domain}Repository, {domain}Repository>();
        builder.Services.AddScoped<I{domain}Service, {domain}ServiceImpl>();
        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen();

        var app = builder.Build();

        if (app.Environment.IsDevelopment())
        {{
            app.UseSwagger();
            app.UseSwaggerUI();
        }}

        {domain}Endpoints.RegisterRoutes(app);

        await app.RunAsync();
    """)


# Function: _gen_service
def _gen_service(output: Dict[str, str], root_ns: str, domain: str, tables: List[str], is_dapper: bool = False, db_target: str = "mssql"):
    base = f"ModernizedApp/Services/{domain}Service"
    entity = domain.rstrip("s")  # naive singularize

    output[f"{base}/{domain}Service.csproj"] = _service_csproj(root_ns, domain, is_dapper, db_target)
    output[f"{base}/Program.cs"]             = _service_program(root_ns, domain, entity, is_dapper, db_target)
    output[f"{base}/Models/{entity}.cs"]     = _model_class(root_ns, domain, entity)
    output[f"{base}/Repositories/I{entity}Repository.cs"] = _repo_interface(root_ns, domain, entity)
    output[f"{base}/Repositories/{entity}Repository.cs"]  = _repo_impl(root_ns, domain, entity, is_dapper, db_target)
    output[f"{base}/Services/I{domain}Service.cs"]        = _service_interface(root_ns, domain, entity)
    output[f"{base}/Services/{domain}Service.cs"]         = _service_impl(root_ns, domain, entity)
    if is_dapper:
        # Dapper has no DbContext/change-tracker — a connection factory
        # replaces AppDbContext as the thing repositories depend on.
        output[f"{base}/Data/IDbConnectionFactory.cs"] = _db_connection_factory(root_ns, domain, db_target)
    else:
        output[f"{base}/Data/AppDbContext.cs"] = _db_context(root_ns, domain, entity)
    output[f"{base}/appsettings.json"]                     = _appsettings(root_ns, domain)


# Function: _service_csproj
def _service_csproj(root_ns: str, domain: str, is_dapper: bool = False, db_target: str = "mssql") -> str:
    data_access_pkgs = (
        (
            '<PackageReference Include="Dapper"                                 Version="2.1.35" />\n'
            '            <PackageReference Include="Npgsql"                                  Version="8.0.3" />'
            if db_target == "postgres" else
            '<PackageReference Include="Dapper"                                 Version="2.1.35" />\n'
            '            <PackageReference Include="Microsoft.Data.SqlClient"               Version="5.2.0" />'
        )
        if is_dapper else
        f'<PackageReference Include="{"Npgsql.EntityFrameworkCore.PostgreSQL" if db_target == "postgres" else "Microsoft.EntityFrameworkCore.SqlServer"}" Version="8.0.0" />\n'
        '            <PackageReference Include="Microsoft.EntityFrameworkCore.Design"    Version="8.0.0" />'
    )
    return textwrap.dedent(f"""\
        <Project Sdk="Microsoft.NET.Sdk.Web">
          <PropertyGroup>
            <TargetFramework>net8.0</TargetFramework>
            <Nullable>enable</Nullable>
            <ImplicitUsings>enable</ImplicitUsings>
            <RootNamespace>{root_ns}.{domain}Service</RootNamespace>
          </PropertyGroup>
          <ItemGroup>
            {data_access_pkgs}
            <PackageReference Include="BCrypt.Net-Next"                         Version="4.0.3" />
            <PackageReference Include="Swashbuckle.AspNetCore"                  Version="6.5.0" />
          </ItemGroup>
        </Project>
    """)


# Function: _db_connection_factory
def _db_connection_factory(root_ns: str, domain: str, db_target: str = "mssql") -> str:
    db_using = "using Npgsql;" if db_target == "postgres" else "using Microsoft.Data.SqlClient;"
    connection_ctor = "NpgsqlConnection" if db_target == "postgres" else "SqlConnection"
    return textwrap.dedent(f"""\
        using System.Data;
        {db_using}

        namespace {root_ns}.{domain}Service.Data;

        public interface IDbConnectionFactory
        {{
            IDbConnection CreateConnection();
        }}

        public class SqlConnectionFactory(IConfiguration configuration) : IDbConnectionFactory
        {{
            private readonly string _connectionString =
                configuration.GetConnectionString("DefaultConnection")
                ?? throw new InvalidOperationException("Missing DefaultConnection connection string.");

            public IDbConnection CreateConnection() => new {connection_ctor}(_connectionString);
        }}
    """)


# Function: _service_program
def _service_program(root_ns: str, domain: str, entity: str, is_dapper: bool = False, db_target: str = "mssql") -> str:
    data_access_using = (
        f"using {root_ns}.{domain}Service.Data;"
        if is_dapper else
        f"using {root_ns}.{domain}Service.Data;\n        using Microsoft.EntityFrameworkCore;"
    )
    provider = "UseNpgsql" if db_target == "postgres" else "UseSqlServer"
    data_access_registration = (
        "builder.Services.AddSingleton<IDbConnectionFactory, SqlConnectionFactory>();"
        if is_dapper else
        'builder.Services.AddDbContext<AppDbContext>(opt =>\n'
        f'            opt.{provider}(builder.Configuration.GetConnectionString("DefaultConnection")));'
    )
    return textwrap.dedent(f"""\
        {data_access_using}
        using {root_ns}.{domain}Service.Repositories;
        using {root_ns}.{domain}Service.Services;

        var builder = WebApplication.CreateBuilder(args);

        {data_access_registration}

        builder.Services.AddScoped<I{entity}Repository, {entity}Repository>();
        builder.Services.AddScoped<I{domain}Service, {domain}ServiceImpl>();
        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen();

        var app = builder.Build();

        if (app.Environment.IsDevelopment())
        {{
            app.UseSwagger();
            app.UseSwaggerUI();
        }}

        // ── {domain} endpoints ─────────────────────────────────────────────
        var group = app.MapGroup("/api/{domain.lower()}").WithTags("{domain}");

        group.MapGet("/",         async (I{domain}Service svc) =>
            Results.Ok(await svc.GetAllAsync()));

        group.MapGet("/{{id}}",   async (int id, I{domain}Service svc) =>
            await svc.GetByIdAsync(id) is {{ }} item
                ? Results.Ok(item)
                : Results.NotFound());

        group.MapPost("/",        async ({domain[:-1] if domain.endswith("s") else domain}Dto dto, I{domain}Service svc) =>
        {{
            var created = await svc.CreateAsync(dto);
            return Results.Created($"/api/{domain.lower()}/{{created.Id}}", created);
        }});

        group.MapPut("/{{id}}",   async (int id, {domain[:-1] if domain.endswith("s") else domain}Dto dto,
                                         I{domain}Service svc) =>
            await svc.UpdateAsync(id, dto)
                ? Results.NoContent()
                : Results.NotFound());

        group.MapDelete("/{{id}}", async (int id, I{domain}Service svc) =>
            await svc.DeleteAsync(id)
                ? Results.NoContent()
                : Results.NotFound());

        await app.RunAsync();
    """)


# Function: _model_class
def _model_class(root_ns: str, domain: str, entity: str) -> str:
    return textwrap.dedent(f"""\
        namespace {root_ns}.{domain}Service.Models;

        /// <summary>Domain model for {entity}.</summary>
        public class {entity}
        {{
            public int Id {{ get; set; }}
            public string Name {{ get; set; }} = string.Empty;
            public bool IsActive {{ get; set; }} = true;
            public DateTime CreatedAt {{ get; set; }} = DateTime.UtcNow;
            public DateTime? UpdatedAt {{ get; set; }}
        }}

        /// <summary>Data-transfer object for create / update operations.</summary>
        public record {entity}Dto(string Name, bool IsActive = true);
    """)


# Function: _repo_interface
def _repo_interface(root_ns: str, domain: str, entity: str) -> str:
    return textwrap.dedent(f"""\
        using {root_ns}.{domain}Service.Models;

        namespace {root_ns}.{domain}Service.Repositories;

        public interface I{entity}Repository
        {{
            Task<IEnumerable<{entity}>> GetAllAsync();
            Task<{entity}?> GetByIdAsync(int id);
            Task<{entity}> AddAsync({entity} entity);
            Task<bool> UpdateAsync({entity} entity);
            Task<bool> DeleteAsync(int id);
        }}
    """)


# Function: _repo_impl
def _repo_impl(root_ns: str, domain: str, entity: str, is_dapper: bool = False, db_target: str = "mssql") -> str:
    if is_dapper:
        table = f"{entity}s"
        is_postgres = db_target == "postgres"
        insert_sql = (
            f"INSERT INTO {table} (Name, IsActive, CreatedAt) "
            "VALUES (@Name, @IsActive, @CreatedAt) RETURNING Id"
            if is_postgres else
            f"INSERT INTO {table} (Name, IsActive, CreatedAt) "
            "OUTPUT INSERTED.Id VALUES (@Name, @IsActive, @CreatedAt)"
        )
        active_literal = "TRUE" if is_postgres else "1"
        inactive_literal = "FALSE" if is_postgres else "0"
        return textwrap.dedent(f"""\
            using Dapper;
            using {root_ns}.{domain}Service.Data;
            using {root_ns}.{domain}Service.Models;

            namespace {root_ns}.{domain}Service.Repositories;

            public class {entity}Repository(IDbConnectionFactory connectionFactory) : I{entity}Repository
            {{
                public async Task<IEnumerable<{entity}>> GetAllAsync()
                {{
                    using var conn = connectionFactory.CreateConnection();
                    return await conn.QueryAsync<{entity}>(
                        "SELECT * FROM {table} WHERE IsActive = {active_literal}");
                }}

                public async Task<{entity}?> GetByIdAsync(int id)
                {{
                    using var conn = connectionFactory.CreateConnection();
                    return await conn.QuerySingleOrDefaultAsync<{entity}>(
                        "SELECT * FROM {table} WHERE Id = @Id", new {{ Id = id }});
                }}

                public async Task<{entity}> AddAsync({entity} entity)
                {{
                    using var conn = connectionFactory.CreateConnection();
                    var newId = await conn.QuerySingleAsync<int>(
                        "{insert_sql}",
                        new {{ entity.Name, entity.IsActive, entity.CreatedAt }});
                    entity.Id = newId;
                    return entity;
                }}

                public async Task<bool> UpdateAsync({entity} entity)
                {{
                    using var conn = connectionFactory.CreateConnection();
                    var rows = await conn.ExecuteAsync(
                        "UPDATE {table} SET Name = @Name, IsActive = @IsActive, UpdatedAt = @UpdatedAt WHERE Id = @Id",
                        new {{ entity.Id, entity.Name, entity.IsActive, entity.UpdatedAt }});
                    return rows > 0;
                }}

                public async Task<bool> DeleteAsync(int id)
                {{
                    using var conn = connectionFactory.CreateConnection();
                    var rows = await conn.ExecuteAsync(
                        "UPDATE {table} SET IsActive = {inactive_literal}, UpdatedAt = @UpdatedAt WHERE Id = @Id",
                        new {{ Id = id, UpdatedAt = DateTime.UtcNow }});
                    return rows > 0;
                }}
            }}
        """)
    return textwrap.dedent(f"""\
        using {root_ns}.{domain}Service.Data;
        using {root_ns}.{domain}Service.Models;
        using Microsoft.EntityFrameworkCore;

        namespace {root_ns}.{domain}Service.Repositories;

        public class {entity}Repository(AppDbContext db) : I{entity}Repository
        {{
            public async Task<IEnumerable<{entity}>> GetAllAsync() =>
                await db.{entity}s.Where(x => x.IsActive).ToListAsync();

            public async Task<{entity}?> GetByIdAsync(int id) =>
                await db.{entity}s.FindAsync(id);

            public async Task<{entity}> AddAsync({entity} entity)
            {{
                db.{entity}s.Add(entity);
                await db.SaveChangesAsync();
                return entity;
            }}

            public async Task<bool> UpdateAsync({entity} entity)
            {{
                db.{entity}s.Update(entity);
                return await db.SaveChangesAsync() > 0;
            }}

            public async Task<bool> DeleteAsync(int id)
            {{
                var item = await db.{entity}s.FindAsync(id);
                if (item is null) return false;
                item.IsActive = false;
                return await db.SaveChangesAsync() > 0;
            }}
        }}
    """)


# Function: _service_interface
def _service_interface(root_ns: str, domain: str, entity: str) -> str:
    return textwrap.dedent(f"""\
        using {root_ns}.{domain}Service.Models;

        namespace {root_ns}.{domain}Service.Services;

        public interface I{domain}Service
        {{
            Task<IEnumerable<{entity}>> GetAllAsync();
            Task<{entity}?> GetByIdAsync(int id);
            Task<{entity}> CreateAsync({entity}Dto dto);
            Task<bool> UpdateAsync(int id, {entity}Dto dto);
            Task<bool> DeleteAsync(int id);
        }}
    """)


# Function: _service_impl
def _service_impl(root_ns: str, domain: str, entity: str) -> str:
    return textwrap.dedent(f"""\
        using {root_ns}.{domain}Service.Models;
        using {root_ns}.{domain}Service.Repositories;

        namespace {root_ns}.{domain}Service.Services;

        public class {domain}ServiceImpl(I{entity}Repository repo) : I{domain}Service
        {{
            public Task<IEnumerable<{entity}>> GetAllAsync() => repo.GetAllAsync();

            public Task<{entity}?> GetByIdAsync(int id) => repo.GetByIdAsync(id);

            public async Task<{entity}> CreateAsync({entity}Dto dto)
            {{
                var entity = new {entity} {{ Name = dto.Name, IsActive = dto.IsActive }};
                return await repo.AddAsync(entity);
            }}

            public async Task<bool> UpdateAsync(int id, {entity}Dto dto)
            {{
                var entity = await repo.GetByIdAsync(id);
                if (entity is null) return false;
                entity.Name      = dto.Name;
                entity.IsActive  = dto.IsActive;
                entity.UpdatedAt = DateTime.UtcNow;
                return await repo.UpdateAsync(entity);
            }}

            public Task<bool> DeleteAsync(int id) => repo.DeleteAsync(id);
        }}
    """)


# Function: _db_context
def _db_context(root_ns: str, domain: str, entity: str) -> str:
    return textwrap.dedent(f"""\
        using {root_ns}.{domain}Service.Models;
        using Microsoft.EntityFrameworkCore;

        namespace {root_ns}.{domain}Service.Data;

        public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
        {{
            public DbSet<{entity}> {entity}s => Set<{entity}>();

            protected override void OnModelCreating(ModelBuilder modelBuilder)
            {{
                modelBuilder.Entity<{entity}>(entity =>
                {{
                    entity.HasKey(e => e.Id);
                    entity.Property(e => e.Name).IsRequired().HasMaxLength(100);
                    entity.HasIndex(e => e.IsActive);
                }});
            }}
        }}
    """)


# Function: _appsettings
def _appsettings(root_ns: str, domain: str) -> str:
    import json as _json
    return _json.dumps({
        "ConnectionStrings": {
            "DefaultConnection": f"Server=localhost;Database=Modernized_{domain}DB;Trusted_Connection=True;TrustServerCertificate=True;"
        },
        "Logging": {"LogLevel": {"Default": "Information", "Microsoft.AspNetCore": "Warning"}},
        "AllowedHosts": "*",
    }, indent=2)


# ─── Blazor / JS frontend ─────────────────────────────────────────────────────
# Function: _gen_frontend
def _gen_frontend(output: Dict[str, str], root_ns: str, domain: str):
    entity = domain.rstrip("s")
    base   = f"ModernizedApp/Frontend/{domain}"
    output[f"{base}/{domain}.razor"]       = _blazor_component(root_ns, domain, entity)
    output[f"{base}/{domain}.razor.cs"]    = _blazor_codebehind(root_ns, domain, entity)
    output[f"{base}/{domain}.js"]          = _domain_js_module(domain, entity)


# Function: _blazor_component
def _blazor_component(root_ns: str, domain: str, entity: str) -> str:
    return textwrap.dedent(f"""\
        @page "/{domain.lower()}"
        @using {root_ns}.{domain}Service.Models
        @inject IJSRuntime JS
        @inject I{domain}Service Svc

        <h1>{domain}</h1>

        @if (_loading)
        {{
            <p>Loading...</p>
        }}
        else if (_items.Count == 0)
        {{
            <p>No {domain.lower()} found.</p>
        }}
        else
        {{
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Active</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                @foreach (var item in _items)
                {{
                    <tr>
                        <td>@item.Id</td>
                        <td>@item.Name</td>
                        <td>@(item.IsActive ? "✔" : "✘")</td>
                        <td>@item.CreatedAt.ToString("dd MMM yyyy")</td>
                        <td>
                            <button class="btn btn-sm btn-primary"
                                    @onclick="() => EditItem(item)">Edit</button>
                            <button class="btn btn-sm btn-danger"
                                    @onclick="() => DeleteItem(item.Id)">Delete</button>
                        </td>
                    </tr>
                }}
                </tbody>
            </table>
        }}

        <!-- Inline edit form -->
        @if (_editing is not null)
        {{
            <div class="card p-3 mt-3">
                <h4>Edit {entity}</h4>
                <div class="mb-2">
                    <label>Name</label>
                    <input class="form-control" @bind="_editing.Name" />
                </div>
                <button class="btn btn-success" @onclick="SaveItem">Save</button>
                <button class="btn btn-secondary ms-2" @onclick="CancelEdit">Cancel</button>
            </div>
        }}

        @code {{
            // Code is in {domain}.razor.cs
        }}
    """)


# Function: _blazor_codebehind
def _blazor_codebehind(root_ns: str, domain: str, entity: str) -> str:
    return textwrap.dedent(f"""\
        using {root_ns}.{domain}Service.Models;
        using {root_ns}.{domain}Service.Services;
        using Microsoft.AspNetCore.Components;
        using Microsoft.JSInterop;

        namespace {root_ns}.Frontend.Pages;

        public partial class {domain}
        {{
            [Inject] private I{domain}Service Svc {{ get; set; }} = default!;
            [Inject] private IJSRuntime JS {{ get; set; }} = default!;

            private List<{entity}> _items = new();
            private {entity}? _editing;
            private bool _loading = true;

            protected override async Task OnInitializedAsync()
            {{
                _items   = (await Svc.GetAllAsync()).ToList();
                _loading = false;
            }}

            private void EditItem({entity} item)  => _editing = item;
            private void CancelEdit()              => _editing = null;

            private async Task SaveItem()
            {{
                if (_editing is null) return;
                await Svc.UpdateAsync(_editing.Id,
                    new {entity}Dto(_editing.Name, _editing.IsActive));
                _editing = null;
                _items = (await Svc.GetAllAsync()).ToList();
            }}

            private async Task DeleteItem(int id)
            {{
                bool confirmed = await JS.InvokeAsync<bool>(
                    "{domain.lower()}Module.confirmDelete", id);
                if (!confirmed) return;
                await Svc.DeleteAsync(id);
                _items = (await Svc.GetAllAsync()).ToList();
            }}

            protected override async Task OnAfterRenderAsync(bool firstRender)
            {{
                if (firstRender)
                    await JS.InvokeVoidAsync("{domain.lower()}Module.init");
            }}
        }}
    """)


# Function: _domain_js_module
def _domain_js_module(domain: str, entity: str) -> str:
    return textwrap.dedent(f"""\
        // {domain}.js — JavaScript interop module for {domain} Blazor component
        // Handles client-side interactions that Blazor delegates to JS.

        export function init() {{
            console.log('[{domain}] module initialised');
        }}

        /**
         * Show a native confirm dialog and return the user's choice.
         * @param {{number}} id — the {entity} ID to be deleted
         * @returns {{boolean}}
         */
        export function confirmDelete(id) {{
            return window.confirm(`Delete {entity} #${{id}}? This action cannot be undone.`);
        }}

        /**
         * Animate a table row highlight when an item is saved.
         * @param {{string}} rowId — HTMLElement id of the row to highlight
         */
        export function highlightRow(rowId) {{
            const el = document.getElementById(rowId);
            if (!el) return;
            el.classList.add('table-success');
            setTimeout(() => el.classList.remove('table-success'), 2000);
        }}

        /**
         * Copy text to clipboard.
         * @param {{string}} text
         */
        export async function copyToClipboard(text) {{
            await navigator.clipboard.writeText(text);
        }}
    """)


# Function: _api_client_js
def _api_client_js() -> str:
    return textwrap.dedent("""\
        // Shared/ApiClient.js — lightweight fetch wrapper for microservice calls
        // Import in any JS module: import { get, post, put, del } from './ApiClient.js';

        const BASE_URLS = {
          customer:    '/api/customer',
          account:     '/api/account',
          transaction: '/api/transaction',
          auth:        '/api/auth',
        };

        async function request(method, url, body) {
          const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
          };
          if (body !== undefined) opts.body = JSON.stringify(body);
          const res = await fetch(url, opts);
          if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || `HTTP ${res.status}`);
          }
          return res.status === 204 ? null : res.json();
        }

        export const get  = (url)        => request('GET',    url);
        export const post = (url, body)  => request('POST',   url, body);
        export const put  = (url, body)  => request('PUT',    url, body);
        export const del  = (url)        => request('DELETE', url);

        export default {
          customer:    { base: BASE_URLS.customer },
          account:     { base: BASE_URLS.account },
          transaction: { base: BASE_URLS.transaction },
          get, post, put, del,
        };
    """)


# ─── Ocelot API Gateway ────────────────────────────────────────────────────────
# Function: _ocelot_config
def _ocelot_config(root_ns: str, domains: List[str], is_azure_auth: bool = False) -> str:
    import json as _json
    routes = []
    port = 7001
    for d in domains:
        route = {
            "DownstreamPathTemplate": f"/api/{d.lower()}/{{everything}}",
            "DownstreamScheme": "http",
            "DownstreamHostAndPorts": [{"Host": f"{d.lower()}-service", "Port": port}],
            "UpstreamPathTemplate": f"/api/{d.lower()}/{{everything}}",
            "UpstreamHttpMethod": ["GET", "POST", "PUT", "DELETE"],
        }
        if is_azure_auth:
            # Without this, AddMicrosoftIdentityWebApi() in Program.cs registers
            # the JWT bearer scheme but Ocelot won't actually enforce it on any
            # route unless the route opts in via AuthenticationProviderKey.
            route["AuthenticationOptions"] = {"AuthenticationProviderKey": "Bearer", "AllowedScopes": []}
        routes.append(route)
        port += 1
    return _json.dumps({"Routes": routes, "GlobalConfiguration": {"BaseUrl": "http://localhost:5000"}}, indent=2)


# Function: _gateway_program
def _gateway_program(root_ns: str, is_azure_auth: bool = False) -> str:
    if is_azure_auth:
        return textwrap.dedent("""\
            using Microsoft.AspNetCore.Authentication.JwtBearer;
            using Microsoft.Identity.Web;
            using Ocelot.DependencyInjection;
            using Ocelot.Middleware;

            var builder = WebApplication.CreateBuilder(args);
            builder.Configuration.AddJsonFile("ocelot.json", optional: false, reloadOnChange: true);

            // Validates bearer tokens issued by Azure Entra ID — tenant/client IDs
            // come from the "AzureAd" section in appsettings.json (see README for
            // the app registration steps: API permissions, exposed scopes, redirect URIs).
            builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
                .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));
            builder.Services.AddAuthorization();
            builder.Services.AddOcelot();

            var app = builder.Build();
            app.UseAuthentication();
            app.UseAuthorization();
            await app.UseOcelot();
            await app.RunAsync();
        """)
    return textwrap.dedent("""\
        using Ocelot.DependencyInjection;
        using Ocelot.Middleware;

        var builder = WebApplication.CreateBuilder(args);
        builder.Configuration.AddJsonFile("ocelot.json", optional: false, reloadOnChange: true);
        builder.Services.AddOcelot();

        var app = builder.Build();
        await app.UseOcelot();
        await app.RunAsync();
    """)


# Function: _gateway_csproj
def _gateway_csproj(root_ns: str, is_azure_auth: bool = False) -> str:
    auth_pkg = (
        '\n            <PackageReference Include="Microsoft.Identity.Web" Version="3.3.1" />'
        if is_azure_auth else ""
    )
    return textwrap.dedent(f"""\
        <Project Sdk="Microsoft.NET.Sdk.Web">
          <PropertyGroup>
            <TargetFramework>net8.0</TargetFramework>
            <Nullable>enable</Nullable>
            <ImplicitUsings>enable</ImplicitUsings>
            <RootNamespace>{root_ns}.ApiGateway</RootNamespace>
          </PropertyGroup>
          <ItemGroup>
            <PackageReference Include="Ocelot" Version="23.0.0" />{auth_pkg}
          </ItemGroup>
        </Project>
    """)


# Function: _gateway_azuread_appsettings
def _gateway_azuread_appsettings() -> str:
    import json as _json
    return _json.dumps({
        "AzureAd": {
            "Instance": "https://login.microsoftonline.com/",
            "TenantId": "<SET-VIA-ENV-OR-KEY-VAULT: AZURE_TENANT_ID>",
            "ClientId": "<SET-VIA-ENV-OR-KEY-VAULT: AZURE_CLIENT_ID>",
            "Audience": "api://<SET-VIA-ENV-OR-KEY-VAULT: AZURE_CLIENT_ID>",
        },
        "Logging": {"LogLevel": {"Default": "Information", "Microsoft.AspNetCore": "Warning"}},
    }, indent=2)
