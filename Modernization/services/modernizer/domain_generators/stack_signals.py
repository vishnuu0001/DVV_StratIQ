# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/domain_generators (stack_signals.py)
# Date: 2025-10-30
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



# ─── Prompt-to-code generation ───────────────────────────────────────────────

# Function: _detect_stack_signals
def _detect_stack_signals(user_prompt: str) -> Dict[str, Optional[str]]:
    """Scan the free-text prompt for explicit technology mentions.

    The UI defaults `target_stack` to "aveva_mes" and most users never touch
    it when describing a brand-new app in the prompt box — so a request like
    "Angular + .NET 10 + Dapper + AKS + Entra ID" would otherwise be generated
    under an unrelated ".NET 8 Minimal API + JS modules" persona, producing
    incoherent output. Detected signals take priority over the preset.
    """
    text = user_prompt.lower()

    # Function: _first
    def _first(patterns: List[tuple]) -> Optional[str]:
        for needle, label in patterns:
            if needle in text:
                return label
        return None

    frontend = _first([
        ("angular", "Angular"), ("react", "React"), ("vue", "Vue"),
        ("blazor", "Blazor"), ("svelte", "Svelte"),
    ])
    backend = _first([
        (".net 10", ".NET 10"), ("dotnet 10", ".NET 10"),
        (".net 9", ".NET 9"), ("dotnet 9", ".NET 9"),
        (".net 8", ".NET 8"), ("dotnet 8", ".NET 8"),
        (".net core", "ASP.NET Core"), (".net", ".NET"), ("dotnet", ".NET"),
        ("spring batch", "Spring Boot + Spring Batch"),
        ("spring cloud", "Spring Boot + Spring Cloud"),
        ("spring boot", "Spring Boot"),
        ("quarkus", "Quarkus"), ("micronaut", "Micronaut"),
        ("jakarta ee", "Jakarta EE"), ("java ee", "Java EE Legacy"),
        ("struts", "Apache Struts Legacy"), ("ejb", "Java EE Legacy"),
        ("servlet", "Jakarta Servlet"), ("jsp", "Jakarta Servlet + JSP"),
        ("java se", "Java SE"), ("legacy java", "Java EE Legacy"),
        ("django", "Django"),
        ("fastapi", "FastAPI"), ("flask", "Flask"),
        ("nestjs", "NestJS"), ("express", "Express.js"), ("node.js", "Node.js"),
    ])
    orm = _first([
        ("dapper", "Dapper"), ("entity framework", "Entity Framework Core"),
        ("ef core", "Entity Framework Core"), ("sqlalchemy", "SQLAlchemy"),
        ("hibernate", "Hibernate"), ("mongoose", "Mongoose"), ("prisma", "Prisma"),
    ])
    auth = _first([
        ("entra id b2b", "Azure Entra ID (B2B)"), ("entra id b2c", "Azure Entra ID (B2C)"),
        ("entra id", "Azure Entra ID"), ("azure ad b2c", "Azure AD B2C"),
        ("azure ad", "Azure AD"), ("keycloak", "Keycloak"), ("auth0", "Auth0"),
        ("cognito", "AWS Cognito"), ("okta", "Okta"),
    ])
    deploy = _first([
        ("openshift", "Red Hat OpenShift"),
        ("amazon eks", "Amazon EKS"), ("aws eks", "Amazon EKS"), ("eks", "Amazon EKS"),
        ("aks", "Azure Kubernetes Service (AKS)"),
        ("azure kubernetes service", "Azure Kubernetes Service (AKS)"),
        ("google kubernetes engine", "Google Kubernetes Engine (GKE)"),
        ("gke", "Google Kubernetes Engine (GKE)"),
        ("kubernetes", "Kubernetes"), ("k8s", "Kubernetes"),
        ("aws ecs", "AWS ECS/Fargate"), ("fargate", "AWS ECS/Fargate"),
        ("cloud run", "Google Cloud Run"),
        ("azure app service", "Azure App Service"),
        ("docker", "Docker"),
    ])
    db_match = next((value for needle, value in [
        ("pgvector", ("PostgreSQL + pgvector", "pgvector")),
        ("mongodb atlas vector", ("MongoDB Atlas Vector Search", "mongodb-vector")),
        ("redis vector", ("Redis Vector Search", "redis-vector")),
        ("neo4j vector", ("Neo4j Vector Index", "neo4j-vector")),
        ("cassandra vector", ("Cassandra Vector Search", "cassandra-vector")),
        ("elasticsearch vector", ("Elasticsearch Vector Search", "elasticsearch-vector")),
        ("opensearch vector", ("OpenSearch Vector Search", "opensearch-vector")),
        ("pinecone", ("Pinecone Vector Database", "pinecone")),
        ("weaviate", ("Weaviate Vector Database", "weaviate")),
        ("milvus", ("Milvus Vector Database", "milvus")),
        ("vector database", ("Vector Database", "vector")),
        ("vector db", ("Vector Database", "vector")),
        ("opensearch", ("OpenSearch", "opensearch")),
        ("elasticsearch", ("Elasticsearch", "elasticsearch")),
        ("sql server", ("Microsoft SQL Server", "mssql")),
        ("postgres", ("PostgreSQL", "postgres")),
        ("cockroachdb", ("CockroachDB", "cockroachdb")),
        ("mariadb", ("MariaDB", "mariadb")),
        ("mysql", ("MySQL", "mysql")),
        ("oracle", ("Oracle Database", "oracle")),
        ("db2", ("IBM DB2", "db2")),
        ("sqlite", ("SQLite", "sqlite")),
        ("mongodb", ("MongoDB", "mongodb")),
        ("cosmos db", ("Azure Cosmos DB", "cosmosdb")),
        ("dynamodb", ("Amazon DynamoDB", "dynamodb")),
        ("cassandra", ("Apache Cassandra", "cassandra")),
        ("neo4j", ("Neo4j", "neo4j")),
        ("redis", ("Redis", "redis")),
    ] if needle in text), None)
    db = db_match[0] if db_match else None
    db_target = db_match[1] if db_match else None
    deployment_kind = (
        "kubernetes" if deploy and any(token in deploy.casefold() for token in (
            "kubernetes", "openshift", "eks", "aks", "gke",
        )) else
        "container" if deploy else None
    )
    backend_low = (backend or "").casefold()
    java_framework = (
        "quarkus" if "quarkus" in backend_low else
        "micronaut" if "micronaut" in backend_low else
        "jakarta" if any(token in backend_low for token in (
            "jakarta", "java ee", "struts", "servlet",
        )) else
        "java-se" if "java se" in backend_low else
        "spring" if "spring" in backend_low else None
    )
    return {"frontend": frontend, "backend": backend, "orm": orm,
            "auth": auth, "deploy": deploy, "deployment_kind": deployment_kind,
            "db": db, "db_target": db_target, "java_framework": java_framework}


def _merge_target_capabilities(
    target: dict, signals: Dict[str, Optional[str]],
) -> Dict[str, Optional[str]]:
    """Fill prompt omissions from the selected target without overriding prompt facts.

    Layer presence is a target capability, not a keyword-search side effect.  Database-
    only and frontend-only profiles are kept honest by excluding their descriptive
    placeholders from backend detection.
    """
    merged = dict(signals)
    backend = str(target.get("backend_tech") or "").strip()
    frontend = str(target.get("frontend_tech") or "").strip()
    language = str(target.get("language") or "").casefold()
    backend_low = backend.casefold()
    frontend_low = frontend.casefold()
    backend_placeholder = any(token in backend_low for token in (
        "database migration only", "framework-agnostic", "infer from the requested file",
    ))
    if not merged.get("backend") and language != "sql" and backend and not backend_placeholder:
        merged["backend"] = backend
    frontend_framework = next((label for token, label in (
        ("react native", "React Native"), ("angular", "Angular"),
        ("react", "React"), ("vue", "Vue"), ("svelte", "Svelte"),
        ("blazor", "Blazor"), ("flutter", "Flutter"),
    ) if token in frontend_low), None)
    if not merged.get("frontend") and frontend_framework:
        merged["frontend"] = frontend_framework
    for capability in ("deployment_kind", "deploy", "java_framework", "db_target", "db"):
        if not merged.get(capability) and target.get(capability):
            merged[capability] = target[capability]
    if not merged.get("db") and target.get("db_tech") and target.get("db_target"):
        merged["db"] = str(target["db_tech"])
    return merged


# Function: _apply_stack_signals
# Function: _apply_backend_language_override
def _apply_backend_language_override(merged: dict, signals: Dict[str, Optional[str]]) -> None:
    if not signals["backend"]:
        return
    merged["backend_tech"] = signals["backend"]
    low = signals["backend"].lower()
    if ".net" in low or "asp" in low:
        merged["language"] = "csharp"
    elif signals.get("java_framework"):
        merged["language"] = "java"
    elif signals["backend"] in ("Django", "FastAPI", "Flask"):
        merged["language"] = "python"
    elif signals["backend"] in ("Express.js", "NestJS", "Node.js"):
        merged["language"] = "typescript"


# Function: _apply_db_tech_override
def _apply_db_tech_override(merged: dict, signals: Dict[str, Optional[str]]) -> None:
    if signals["orm"] and signals["db"]:
        merged["db_tech"] = f"{signals['db']} + {signals['orm']}"
    elif signals["orm"]:
        # Preset db_tech is "<engine> + <preset ORM>" (e.g. "MS SQL Server + EF
        # Core 8") — keep only the engine name so we don't imply both ORMs.
        base_db = merged.get("db_tech", "").split(" + ")[0].strip()
        merged["db_tech"] = f"{base_db} + {signals['orm']}".strip(" +")
    elif signals["db"]:
        merged["db_tech"] = signals["db"]
    if signals.get("db_target"):
        merged["db_target"] = signals["db_target"]
    if signals.get("java_framework"):
        merged["java_framework"] = signals["java_framework"]
    if signals.get("deployment_kind"):
        merged["deployment_kind"] = signals["deployment_kind"]


# Function: _apply_llm_persona
def _apply_llm_persona(merged: dict, signals: Dict[str, Optional[str]]) -> None:
    if not any(signals.values()):
        return
    bits = [f"a senior full-stack engineer building production systems on: {merged['backend_tech']}"]
    if signals["frontend"]:
        bits.append(f"with a {merged['frontend_tech']} frontend")
    if signals["orm"]:
        bits.append(f"using {signals['orm']} as the data-access layer")
    if signals["auth"]:
        bits.append(f"authenticating via {signals['auth']}")
    if signals["deploy"]:
        bits.append(f"deployed to {signals['deploy']}")
    merged["llm_persona"] = (
        ", ".join(bits) + ". Generate production-ready code matching this exact tech "
        "stack — never substitute a different framework, ORM, or identity provider."
    )
    # "name" is echoed as "Target platform: {name}" on the FIRST line of
    # every single prompt (plan, per-file, README) — leaving it as the
    # stale preset name (e.g. "AVEVA MES (.NET 8 + JS + MS SQL)") directly
    # contradicts the "Backend: .NET 10" / "Frontend: Angular" lines that
    # follow it, which is exactly the kind of contradiction that pushes a
    # small model toward the wrong framework (e.g. emitting React .tsx
    # files for a requested Angular frontend).
    name_bits = [b for b in (signals["frontend"], merged["backend_tech"], signals["orm"]) if b]
    merged["name"] = " + ".join(name_bits) if name_bits else merged["backend_tech"]


# Function: _apply_stack_signals
def _apply_stack_signals(target: dict, signals: Dict[str, Optional[str]], target_stack: str) -> dict:
    """Override a preset's tech hints with technologies the user explicitly
    named in the prompt. A "custom" target is already fully user-authored via
    custom_stack_desc and is left untouched."""
    if target_stack == "custom":
        return target

    merged = dict(target)
    _apply_backend_language_override(merged, signals)
    if signals["frontend"]:
        merged["frontend_tech"] = signals["frontend"]
    _apply_db_tech_override(merged, signals)
    _apply_llm_persona(merged, signals)
    return merged


# Function: _stack_requirements_block
# Function: _auth_backend_guidance
def _auth_backend_guidance(auth: str, lang: str, is_azure: bool) -> str:
    if is_azure and lang == "csharp":
        return (
            f"- Identity provider: {auth}. Backend (ASP.NET Core Web API): use the "
            "Microsoft.Identity.Web NuGet package's AddMicrosoftIdentityWebApi(...) — this is a "
            "bearer-token-validating resource API, NOT AddMicrosoftIdentityWebApp (that's for "
            "interactive cookie sign-in and is WRONG here). Tokens are RS256, validated against "
            "the tenant's JWKS via Microsoft.Identity.Web — NEVER hand-roll JWT validation with a "
            "SymmetricSecurityKey/hardcoded secret, that cannot validate a real Entra token. "
            "Read Instance/TenantId/ClientId/Audience from an \"AzureAd\" config section (env vars "
            "in production), never hardcoded. Protect endpoints with [Authorize]."
        )
    if is_azure:
        return (
            f"- Identity provider: {auth}. Backend: validate the bearer token's RS256 signature "
            "against the tenant's JWKS (via the framework's standard OIDC/JWT-bearer middleware) — "
            "NEVER a hardcoded symmetric secret. Read tenant/client IDs from environment variables."
        )
    return (
        f"- Identity provider: {auth} — implement real token validation middleware on the "
        "backend, reading secrets/config from environment variables, never hardcoded."
    )


# Function: _auth_frontend_guidance
def _auth_frontend_guidance(signals: Dict[str, Optional[str]], frontend_tech: str, is_azure: bool) -> str:
    fw = (frontend_tech or "").lower()
    if is_azure and "angular" in fw:
        return (
            " Frontend (Angular): use @azure/msal-angular + @azure/msal-browser — "
            "MsalModule.forRoot(...) with the app's clientId/authority/redirectUri, MsalGuard on "
            "protected routes, MsalInterceptor to attach the bearer token to API calls. NEVER a "
            "hand-rolled username/password form or storing tokens directly in localStorage — MSAL "
            "manages the token cache itself."
        )
    if is_azure and any(k in fw for k in ("react", "vue")):
        return (
            f" Frontend: use the official Microsoft MSAL SDK for {frontend_tech} (@azure/msal-react "
            "or @azure/msal-browser) to acquire and attach tokens — NEVER a hand-rolled "
            "username/password form."
        )
    if signals["frontend"]:
        return (
            " Frontend: implement a real login/token-acquisition flow (auth service, route guard, "
            "HTTP interceptor attaching the bearer token) — never a bare username/password form "
            "that isn't wired to the identity provider above."
        )
    return ""


# Function: _auth_requirement_line
def _auth_requirement_line(signals: Dict[str, Optional[str]], lang: str, frontend_tech: str) -> Optional[str]:
    if not signals["auth"]:
        return None
    auth = signals["auth"]
    is_azure = "entra" in auth.lower() or "azure ad" in auth.lower()
    backend_guidance = _auth_backend_guidance(auth, lang, is_azure)
    frontend_guidance = _auth_frontend_guidance(signals, frontend_tech, is_azure)
    return backend_guidance + frontend_guidance


# Function: _stack_requirements_block
def _stack_requirements_block(signals: Dict[str, Optional[str]], lang: str = "", frontend_tech: str = "") -> str:
    """Render auth/ORM/deployment signals that don't fit the target dict's
    backend/frontend/db fields into an explicit prompt requirement block.

    The auth line is deliberately prescriptive (exact package/API names, not
    just "implement real token validation") — a 7B model asked only for
    "Entra ID auth" in practice invented AddMicrosoftIdentityWebApp (interactive
    cookie sign-in) instead of AddMicrosoftIdentityWebApi (bearer-token
    validation, what an API called by a SPA actually needs), validated tokens
    with a hardcoded symmetric key (Entra signs with RS256/JWKS, which a
    symmetric key can never validate), and built a username/password login
    on the frontend with no MSAL involved at all. Naming the exact library
    and method closes off the most common wrong answers.
    """
    lines = []
    auth_line = _auth_requirement_line(signals, lang, frontend_tech)
    if auth_line is not None:
        lines.append(auth_line)
    if signals["orm"]:
        lines.append(f"- Data access MUST use {signals['orm']} exactly — no other ORM/data-access library.")
    if signals["deploy"]:
        lines.append(
            f"- Deployment target: {signals['deploy']}. Include a Dockerfile per deployable component. "
            "Do NOT generate docker-compose.yml or Kubernetes/k8s manifests yourself — those are "
            "generated separately and already provided; generating your own would only conflict with them."
        )
    if signals.get("db"):
        database_kind = signals.get("db_target") or signals["db"]
        lines.append(
            f"- Database capability: {signals['db']} ({database_kind}). Use its native Java driver, "
            "data model, query semantics, migrations/index provisioning, health checks, and Testcontainers "
            "module. Never substitute PostgreSQL or JPA for a selected non-relational store."
        )
        if database_kind in {"pgvector", "pinecone", "weaviate", "milvus", "vector"}:
            lines.append(
                "- Vector storage requires configurable embedding dimensions and distance metric, explicit "
                "index/collection provisioning, metadata filtering, batching, idempotent upserts, and "
                "similarity-search integration tests."
            )
    if not lines:
        return ""
    return (
        "\n\nADDITIONAL AUTHORITATIVE REQUIREMENTS (must be reflected in the file plan and "
        "every relevant file):\n" + "\n".join(lines) + "\n"
    )


# Function: _detect_domain_requirements
def _detect_domain_requirements(user_prompt: str) -> str:
    """Catch domain-correctness requirements a generic "production code
    rules" prompt doesn't cover. Asked for "a money transaction" with no
    further guidance, a 7B model produces plain CRUD on a Transactions table
    — no atomicity, no balance check, no audit trail — which is not a money
    transfer no matter how clean the CRUD code is."""
    text = user_prompt.lower()
    money_kw = (
        "money transaction", "money transfer", "fund transfer", "wire transfer",
        "payment", "bank account", "banking application", "debit", "credit transfer",
        "wallet", "ledger",
    )
    movement_kw = (
        "transfer", "payment", "send money", "move funds", "withdraw",
        "deposit", "debit", "credit",
    )
    explicit_money_movement = any(phrase in text for phrase in (
        "money transaction", "money transfer", "fund transfer", "wire transfer",
        "credit transfer", "banking application",
    ))
    contextual_money_movement = (
        any(keyword in text for keyword in money_kw)
        and any(keyword in text for keyword in movement_kw)
    )
    if not (explicit_money_movement or contextual_money_movement):
        return ""
    return (
        "\n\nDOMAIN CORRECTNESS REQUIREMENTS for money movement (mandatory — plain CRUD on a "
        "transactions table is NOT a valid implementation of a transfer/payment):\n"
        "- A transfer must be ATOMIC: debit the source account and credit the destination account "
        "inside a single database transaction — if either side fails, roll back both.\n"
        "- Validate sufficient balance BEFORE debiting, inside the same transaction as the debit "
        "(row locking / SELECT ... FOR UPDATE or the ORM/driver equivalent) to avoid a race between "
        "the balance check and the debit under concurrent requests. Reject with 409/422 if insufficient.\n"
        "- Use a decimal/money type for every amount — NEVER float/double (rounding errors are a "
        "correctness bug, not a style issue, in a banking system).\n"
        "- Accept and persist an idempotency key on the transfer endpoint so a retried request cannot "
        "double-execute the same transfer.\n"
        "- Persist an immutable audit record of every transfer (who, when, amount, source account, "
        "destination account, resulting balances) — a compliance requirement, not optional logging.\n"
    )
