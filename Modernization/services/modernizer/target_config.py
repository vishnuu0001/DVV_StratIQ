# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer (target_config.py)
# Date: 2026-04-23
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



# ─── Target stack registry ────────────────────────────────────────────────────

TARGET_STACKS: Dict[str, dict] = {
    "aveva_mes": {
        "name":           "AVEVA MES (.NET 8 + JS + MS SQL)",
        "backend_tech":   ".NET 8 Minimal API (MES architecture)",
        "frontend_tech":  "JavaScript modules (MES UI architecture)",
        "db_tech":        "Microsoft SQL Server 2022 + EF Core 8",
        "db_target":      "mssql",
        "language":       "csharp",
        "llm_persona":    (
            "an AVEVA MES (Manufacturing Execution System) modernization expert. "
            "You convert legacy code to .NET 8 Minimal API backend services with "
            "JavaScript frontend UI modules and MS SQL Server database."
        ),
    },
    "dotnet8_blazor": {
        "name":           ".NET 8 Blazor Server + MS SQL",
        "backend_tech":   ".NET 8 Minimal API",
        "frontend_tech":  "Blazor Server + JavaScript interop",
        "db_tech":        "Microsoft SQL Server 2022 + EF Core 8",
        "db_target":      "mssql",
        "language":       "csharp",
        "llm_persona":    (
            "an ASP.NET Core 8 Blazor expert. "
            "You convert legacy .NET code to .NET 8 Minimal API microservices with "
            "Blazor Server frontend components and EF Core + MS SQL Server."
        ),
    },
    "dotnet8_mvc": {
        "name":           "ASP.NET Core 8 MVC + MS SQL",
        "backend_tech":   "ASP.NET Core 8 MVC",
        "frontend_tech":  "Razor Views + Tag Helpers",
        "db_tech":        "Microsoft SQL Server 2022 + EF Core 8",
        "db_target":      "mssql",
        "language":       "csharp",
        "llm_persona":    (
            "an ASP.NET Core 8 MVC expert. "
            "You modernize legacy .NET apps to ASP.NET Core 8 MVC with Razor Views, "
            "EF Core, Identity Framework, and SQL Server."
        ),
    },
    "dotnet10_blazor": {
        "name":           ".NET 10 Blazor Web App + MS SQL",
        "backend_tech":   ".NET 10 ASP.NET Core Minimal API",
        "frontend_tech":  "Blazor Web App + JavaScript interop",
        "db_tech":        "Microsoft SQL Server 2022 + EF Core 10",
        "db_target":      "mssql",
        "language":       "csharp",
        "llm_persona":    (
            "an ASP.NET Core 10 and Blazor expert. Generate .NET 10 code using "
            "current APIs, nullable reference types, native OpenAPI, EF Core 10 and MS SQL Server."
        ),
    },
    "dotnet10_mvc": {
        "name":           "ASP.NET Core 10 MVC + MS SQL",
        "backend_tech":   ".NET 10 ASP.NET Core MVC",
        "frontend_tech":  "Razor Views + Tag Helpers",
        "db_tech":        "Microsoft SQL Server 2022 + EF Core 10",
        "db_target":      "mssql",
        "language":       "csharp",
        "llm_persona":    (
            "an ASP.NET Core 10 MVC expert. Generate .NET 10 MVC applications with "
            "EF Core 10, Identity, nullable reference types and MS SQL Server."
        ),
    },
    "spring_boot": {
        "name":           "Java 21 Spring Boot 3 + PostgreSQL",
        "backend_tech":   "Java 21 Spring Boot 3",
        "frontend_tech":  "Thymeleaf / REST API",
        "db_tech":        "PostgreSQL 16 + Spring Data JPA",
        "db_target":      "postgres",
        "language":       "java",
        "llm_persona":    (
            "a Java Spring Boot 3 modernization expert. "
            "You convert legacy Java EE and .NET applications to Java 21 Spring Boot 3 "
            "with JPA entities, Spring Data repositories, REST controllers, and PostgreSQL."
        ),
    },
    "spring_boot_react": {
        "name":           "Spring Boot 3 + React 18 + PostgreSQL",
        "backend_tech":   "Java 21 Spring Boot 3",
        "frontend_tech":  "React 18 + TypeScript + Vite",
        "db_tech":        "PostgreSQL 16 + Spring Data JPA",
        "db_target":      "postgres",
        "language":       "java",
        "llm_persona":    (
            "a full-stack Java+React modernization expert. "
            "You build Java 21 Spring Boot 3 REST APIs (backend) and React 18 TypeScript "
            "frontend with Vite, replacing legacy monolith code."
        ),
    },
    "react_ts": {
        "name":           "React 18 + TypeScript + REST API",
        "backend_tech":   "REST API (framework-agnostic)",
        "frontend_tech":  "React 18 + TypeScript + Vite",
        "db_tech":        "PostgreSQL / MS SQL (via API)",
        "db_target":      "postgres",
        "language":       "typescript",
        "llm_persona":    (
            "a React 18 + TypeScript modernization expert. "
            "You convert legacy web UIs (jQuery, WebForms, JSP) into modern React 18 "
            "components with TypeScript, hooks, Vite, and clean REST API integration."
        ),
    },
    "angular_ts": {
        "name":           "Angular 17 + TypeScript + REST API",
        "backend_tech":   "REST API (framework-agnostic)",
        "frontend_tech":  "Angular 17 + TypeScript + RxJS",
        "db_tech":        "PostgreSQL / MS SQL (via API)",
        "db_target":      "postgres",
        "language":       "typescript",
        "llm_persona":    (
            "an Angular 17 modernization expert. "
            "You convert legacy UIs to Angular 17 standalone components, signals, "
            "TypeScript strict mode, and RxJS reactive patterns."
        ),
    },
    "vue3": {
        "name":           "Vue 3 + TypeScript + Vite",
        "backend_tech":   "REST API (framework-agnostic)",
        "frontend_tech":  "Vue 3 Composition API + Pinia + Vite",
        "db_tech":        "PostgreSQL / MS SQL (via API)",
        "db_target":      "postgres",
        "language":       "typescript",
        "llm_persona":    (
            "a Vue 3 modernization expert. "
            "You convert legacy UIs to Vue 3 Composition API with TypeScript, "
            "Pinia state management, and Vite build toolchain."
        ),
    },
    "oracle_to_postgres": {
        "name":           "Oracle → PostgreSQL Migration",
        "backend_tech":   "(database migration only)",
        "frontend_tech":  "(database migration only)",
        "db_tech":        "PostgreSQL 16",
        "db_target":      "postgres",
        "language":       "sql",
        "llm_persona":    (
            "an Oracle-to-PostgreSQL database migration expert. "
            "You convert Oracle PL/SQL DDL, stored procedures, functions, triggers, "
            "and type definitions to PostgreSQL 16 PL/pgSQL syntax."
        ),
    },
    "oracle_to_mongodb": {
        "name":           "Oracle → MongoDB Migration",
        "backend_tech":   "(database migration only)",
        "frontend_tech":  "(database migration only)",
        "db_tech":        "MongoDB 7 + Mongoose schemas",
        "db_target":      "mongodb",
        "language":       "javascript",
        "llm_persona":    (
            "an Oracle-to-MongoDB relational-to-document migration expert. "
            "You convert Oracle relational schema to MongoDB document model using "
            "Mongoose schemas, embedding vs referencing strategies, and migration scripts."
        ),
    },
    "oracle_to_mssql": {
        "name":           "Oracle → MS SQL Server Migration",
        "backend_tech":   "(database migration only)",
        "frontend_tech":  "(database migration only)",
        "db_tech":        "Microsoft SQL Server 2022",
        "db_target":      "mssql",
        "language":       "sql",
        "llm_persona":    (
            "an Oracle-to-SQL-Server database migration expert. "
            "You convert Oracle PL/SQL DDL, procedures, and Oracle-specific constructs "
            "(VARCHAR2, NUMBER, SYSDATE, ROWNUM, sequences) to T-SQL syntax."
        ),
    },
    "mssql_to_postgres": {
        "name":           "MS SQL Server → PostgreSQL Migration",
        "backend_tech":   "(database migration only)",
        "frontend_tech":  "(database migration only)",
        "db_tech":        "PostgreSQL 16",
        "db_target":      "postgres",
        "language":       "sql",
        "llm_persona":    (
            "a SQL Server to PostgreSQL migration expert. "
            "You convert T-SQL DDL and stored procedures to PL/pgSQL, handling "
            "type differences, identity vs sequence, and syntax conversions."
        ),
    },
    "python_fastapi": {
        "name":           "Python FastAPI + SQLAlchemy + PostgreSQL",
        "backend_tech":   "Python 3.12 FastAPI (async)",
        "frontend_tech":  "REST API (HTML/JS or separate SPA)",
        "db_tech":        "PostgreSQL 16 + SQLAlchemy 2 + Alembic",
        "db_target":      "postgres",
        "language":       "python",
        "llm_persona":    (
            "a Python FastAPI modernization expert. "
            "You convert legacy code to Python 3.12 FastAPI services with async endpoints, "
            "SQLAlchemy 2 ORM models, Pydantic v2 schemas, Alembic migrations, and pytest tests."
        ),
    },
    "python_django": {
        "name":           "Python Django 5 + DRF + PostgreSQL",
        "backend_tech":   "Django 5 + Django REST Framework",
        "frontend_tech":  "DRF browsable API / Django templates",
        "db_tech":        "PostgreSQL 16 + Django ORM",
        "db_target":      "postgres",
        "language":       "python",
        "llm_persona":    (
            "a Python Django modernization expert. "
            "You convert legacy code to Django 5 with Django REST Framework ViewSets, "
            "ORM models, serializers, URL routing, admin configuration, and pytest-django tests."
        ),
    },
}


# Function: _target
def _target(name: str, language: str, backend: str, frontend: str, database: str,
            db_target: str = "postgres") -> dict:
    return {
        "name": name, "language": language, "backend_tech": backend,
        "frontend_tech": frontend, "db_tech": database, "db_target": db_target,
        "llm_persona": (
            f"a production {name} engineering expert. Generate idiomatic, secure, testable code "
            "with pinned dependencies, explicit error handling, and no incomplete placeholders."
        ),
    }


TARGET_STACKS.update({
    "c_native": _target("C17 Native Application", "c", "C17", "CLI / native UI", "SQLite / external database"),
    "cpp_native": _target("C++23 Native Application", "cpp", "C++23", "CLI / native UI", "SQLite / external database"),
    # GnuCOBOL (open-source) in IBM-compatible fixed-format mode (-std=ibm), not
    # IBM's actual proprietary Enterprise COBOL compiler - that's a licensed
    # z/OS-only product with no path to installing it on this box. Named
    # accordingly rather than implying the specific IBM product is in use.
    "cobol_db2": _target("COBOL (GnuCOBOL, IBM-compatible fixed format) + DB2", "cobol", "GnuCOBOL", "3270 / batch", "IBM DB2", "db2"),
    "node_express_react": _target("Node.js Express + React + MongoDB", "typescript", "Node.js + Express", "React + TypeScript", "MongoDB", "mongodb"),
    "node_graphql_react": _target("Node.js GraphQL + React + PostgreSQL", "typescript", "Node.js + GraphQL", "React + TypeScript", "PostgreSQL", "postgres"),
    "javascript_web": _target("HTML + CSS + JavaScript", "javascript", "Node.js / REST API", "HTML5 + CSS3 + JavaScript", "API-managed database"),
    "php_laravel": _target("PHP 8 Laravel + MySQL", "php", "PHP 8 + Laravel", "Blade + JavaScript", "MySQL 8", "mysql"),
    "ruby_rails": _target("Ruby on Rails + PostgreSQL", "ruby", "Ruby 3 + Rails", "Hotwire / React", "PostgreSQL", "postgres"),
    "ruby_rails_react": _target("Ruby on Rails + React + PostgreSQL", "ruby", "Ruby 3 + Rails", "React + TypeScript", "PostgreSQL", "postgres"),
    "go_rest": _target("Go REST API + PostgreSQL", "go", "Go + net/http", "REST / HTML", "PostgreSQL", "postgres"),
    "go_gin_react": _target("Go Gin + React + PostgreSQL", "go", "Go + Gin", "React + TypeScript", "PostgreSQL", "postgres"),
    "oracle_sql": _target("Oracle SQL and PL/SQL", "sql", "Oracle PL/SQL", "Database API", "Oracle Database", "oracle"),
    "db2_sql": _target("IBM DB2 SQL and Procedures", "sql", "DB2 SQL PL", "Database API", "IBM DB2", "db2"),
    "mysql_sql": _target("MySQL SQL and Procedures", "sql", "MySQL SQL", "Database API", "MySQL 8", "mysql"),
    "java_quarkus": _target("Java 21 Quarkus + PostgreSQL", "java", "Quarkus", "REST API", "PostgreSQL 16 + Panache", "postgres"),
    "java_micronaut": _target("Java 21 Micronaut + PostgreSQL", "java", "Micronaut", "REST API", "PostgreSQL 16 + Micronaut Data JDBC", "postgres"),
    # Full-project presets.  Keeping these in the engine registry (instead of
    # UI-only "guided" aliases) preserves the exact stack through analysis,
    # generation, validation, repair, build, and release export.
    "dotnet_react": _target(".NET 8 Web API + React + PostgreSQL", "csharp", ".NET 8 Web API", "React + TypeScript", "PostgreSQL 16 + EF Core 8", "postgres"),
    "dotnet_angular": _target(".NET 8 Web API + Angular + SQL Server", "csharp", ".NET 8 Web API", "Angular 18 + TypeScript", "SQL Server 2022 + EF Core 8", "mssql"),
    "dotnet_microservices": _target(".NET 8 Microservices + Kubernetes", "csharp", ".NET 8 + Aspire microservices", "React + TypeScript", "PostgreSQL 16", "postgres"),
    "node_nest_react": _target("NestJS + React + PostgreSQL", "typescript", "NestJS", "React + TypeScript", "PostgreSQL 16", "postgres"),
    "nextjs_fullstack": _target("Next.js Full Stack + PostgreSQL", "typescript", "Next.js API routes", "Next.js App Router", "PostgreSQL + Prisma", "postgres"),
    "kotlin_spring": _target("Kotlin + Spring Boot + PostgreSQL", "kotlin", "Spring Boot", "REST API", "PostgreSQL 16", "postgres"),
    "go_fiber_vue": _target("Go Fiber + Vue + PostgreSQL", "go", "Go + Fiber", "Vue 3 + TypeScript", "PostgreSQL 16", "postgres"),
    "rust_axum_react": _target("Rust Axum + React + PostgreSQL", "rust", "Rust + Axum", "React + TypeScript", "PostgreSQL 16", "postgres"),
    "php_laravel_vue": _target("Laravel + Vue + MySQL", "php", "PHP 8 + Laravel", "Vue 3 + TypeScript", "MySQL 8", "mysql"),
    "flutter_dotnet": _target("Flutter + .NET 8 API", "dart", ".NET 8 Web API", "Flutter", "PostgreSQL 16", "postgres"),
    "javascript_node": _target("JavaScript + Node.js", "javascript", "Node.js", "CLI / REST API", "Optional database"),
    "swift_vapor": _target("Swift + Vapor", "swift", "Vapor", "REST API", "PostgreSQL 16", "postgres"),
    "kotlin_ktor": _target("Kotlin + Ktor", "kotlin", "Ktor", "REST API", "PostgreSQL 16", "postgres"),
    "shell_automation": _target("Shell / Bash automation", "shell", "Bash", "CLI", "Files / external services"),
    "r_analytics": _target("R analytics application", "r", "R 4.x", "CLI / Shiny", "Files / database"),
    "scala_play": _target("Scala + Play Framework", "scala", "Play Framework", "REST API", "PostgreSQL 16", "postgres"),
    "clojure_ring": _target("Clojure + Ring", "clojure", "Ring / Reitit", "REST API", "PostgreSQL 16", "postgres"),
    "haskell_servant": _target("Haskell + Servant", "haskell", "Servant", "REST API", "PostgreSQL 16", "postgres"),
    "common_lisp": _target("Common Lisp application", "lisp", "ANSI Common Lisp", "CLI / service", "Files / database"),
    "julia_application": _target("Julia application", "julia", "Julia 1.x", "CLI / HTTP service", "Files / database"),
    # Source-modernization journeys and current platform targets.
    "ibmi_as400": _target("Modernize IBM i (AS/400) ILE RPG → Java 21", "java", "Spring Boot 4.1 + Spring Batch", "REST / batch", "PostgreSQL / Db2", "postgres"),
    "react_native_node": _target("React Native 0.86 + NestJS", "typescript", "NestJS", "React Native 0.86 + TypeScript", "PostgreSQL", "postgres"),
    "cobol_java": _target("Modernize COBOL → Java 21 Spring Boot 4.1", "java", "Spring Boot 4.1 + Spring Batch", "REST / batch", "PostgreSQL / Db2", "postgres"),
    "cobol_dotnet": _target("Modernize COBOL → .NET 10 LTS", "csharp", ".NET 10 Web API", "React", "SQL Server / PostgreSQL", "mssql"),
    "elixir_phoenix": _target("Elixir + Phoenix 1.8", "elixir", "Phoenix 1.8.9", "LiveView / REST API", "PostgreSQL", "postgres"),
    "erlang_otp": _target("Erlang/OTP 29 application", "erlang", "Erlang/OTP 29", "Service / CLI", "Mnesia / external database"),
    "dart_server": _target("Dart 3.12 server + Shelf", "dart", "Dart 3.12 + Shelf 1.4", "REST API", "PostgreSQL", "postgres"),
})


_RELATIONAL_DB_TARGETS = {
    "mssql", "postgres", "oracle", "mysql", "db2", "sqlite", "bigquery",
    "snowflake", "redshift", "duckdb", "databricks", "spark", "hive",
    "trino", "presto", "clickhouse", "teradata",
}


def resolve_sql_dialect_hint(target: dict) -> str:
    """Return the target's authoritative SQL dialect.

    ``db_tech`` is descriptive and can be ambiguous (for example
    "PostgreSQL / MS SQL"). ``db_target`` is the governed machine-readable
    selection and must win whenever it names a relational engine. Falling
    back to descriptive text preserves custom stacks while avoiding an
    accidental generic/ANSI validation route for configured presets.
    """
    db_target = str(target.get("db_target") or "").strip().casefold()
    if db_target in _RELATIONAL_DB_TARGETS:
        return db_target
    return str(target.get("db_tech") or "").strip()


# Function: _infer_target_language
def _infer_target_language(description: str, default: str = "csharp") -> str:
    text = (description or "").lower()
    # Prefer the application's backend/runtime over incidental frontend,
    # infrastructure, or English substrings. In particular, "application"
    # contains "pli" but is not an IBM PL/I language declaration.
    primary_checks = (
        ("csharp", ("c#", ".net", "dotnet", "asp.net")),
        ("java", ("java", "spring boot", "quarkus")),
        ("python", ("python", "django", "fastapi", "flask")),
        ("go", ("golang", "go gin", "language:go")),
        ("php", ("php", "laravel")),
        ("ruby", ("ruby", "rails")),
        ("rust", ("rust", "cargo", "axum", "actix")),
        ("kotlin", ("kotlin", "ktor")),
        ("typescript", ("typescript", "javascript", "react", "angular", "vue", "node.js", "express", "graphql")),
    )
    primary = next(
        (language for language, needles in primary_checks if any(needle in text for needle in needles)),
        None,
    )
    if primary:
        return primary
    checks = (
        ("cloudformation", ("cloudformation", "cloud formation")),
        ("kubernetes", ("kubernetes manifest", "k8s manifest")),
        ("github_actions", ("github actions", "github workflow")),
        ("jenkinsfile", ("jenkinsfile", "jenkins pipeline")),
        ("dockerfile", ("dockerfile",)), ("helm", ("helm chart",)),
        ("ansible", ("ansible playbook",)), ("yaml", ("yaml",)),
        ("toml", ("toml",)), ("json", ("json",)), ("xml", ("xml",)),
        ("markdown", ("markdown",)), ("protobuf", ("protobuf", "protocol buffers")),
        ("graphql", ("graphql schema", "graphql query")),
        ("javascript", ("language: javascript", "javascript only")),
        ("cobol", ("cobol",)), ("cpp", ("c++", "cpp")), ("c", ("c17", " c ", "language:c")),
        ("rust", ("rust", "cargo", "axum", "actix")),
        ("swift", ("swift", "vapor")), ("kotlin", ("kotlin", "ktor")),
        ("scala", ("scala", "play framework")), ("clojure", ("clojure",)),
        ("haskell", ("haskell",)), ("lisp", ("common lisp", "lisp")),
        ("elixir", ("elixir", "phoenix")), ("dart", ("dart", "flutter")),
        ("julia", ("julia",)), ("r", ("r language", "rscript")),
        ("shell", ("shell script", "bash")), ("fortran", ("fortran",)),
        ("ada", ("ada",)), ("pascal", ("delphi", "pascal")),
        ("erlang", ("erlang",)), ("ocaml", ("ocaml",)), ("prolog", ("prolog",)),
        ("hcl", ("terraform", " hcl")), ("abap", ("abap",)),
        ("pli", ("pl/i", "ibm pli", "enterprise pli", "language:pli", ".pli")),
        ("rpg", ("rpgle", " rpg")),
        ("jcl", (" jcl",)), ("mumps", ("mumps",)),
        ("natural", ("natural 4gl",)), ("progress4gl", ("progress 4gl", "openedge abl")),
        ("apex", ("salesforce apex",)),
        ("go", ("golang", "go gin", "language:go")), ("php", ("php", "laravel")),
        ("ruby", ("ruby", "rails")), ("python", ("python", "django", "fastapi", "flask")),
        ("java", ("java", "spring boot", "quarkus")),
        ("typescript", ("typescript", "javascript", "react", "angular", "vue", "node.js", "express", "graphql")),
        ("sql", ("sql", "db2", "oracle", "postgresql", "mysql")),
        ("csharp", ("c#", ".net", "dotnet")),
    )
    return next((language for language, needles in checks if any(needle in text for needle in needles)), default)


# v4's build_system_prompt() replaced the single flat SYSTEM_PROMPT string with
# a composable CORE + STACK_PROFILES model — every call site that used to embed
# SYSTEM_PROMPT verbatim now needs to say WHICH profiles apply to the file it's
# generating. db_target values actually used by TARGET_STACKS today are only
# "mssql" (default)/"postgres"/"mongodb" — Oracle only ever appears as a
# migration SOURCE, never as this module's own output target.
_DB_TARGET_TO_PROFILES: Dict[str, List[str]] = {
    "mssql":    ["relational_generic", "sqlserver"],
    "postgres": ["relational_generic", "postgres"],
    "mongodb":  ["nosql_document"],
    "oracle":   ["relational_generic", "oracle"],
    "db2":      ["relational_generic", "db2_luw"],
    "mysql":    ["relational_generic"],
}
# Frontend frameworks with a STACK_PROFILES entry today. Vue (a valid
# TARGET_STACKS frontend_tech) has no profile yet — deliberately omitted
# rather than guessing; falls back to "javascript_web" alone for it.
_FRONTEND_TECH_TO_PROFILE: Dict[str, str] = {"react": "react", "angular": "angular"}
_LANGUAGE_TO_PROFILE: Dict[str, str] = {
    "csharp": "dotnet", "java": "java", "python": "python",
    "cobol": "cobol", "javascript": "javascript_web", "typescript": "javascript_web",
}


# Function: _stack_profiles_for
def _stack_profiles_for(lang: str, target: dict, include_datastore: bool = True) -> List[str]:
    """Map a target-stack's language/frontend/datastore to build_system_prompt()'s
    STACK_PROFILES keys. Never raises — omits a category it can't confidently
    resolve (e.g. Vue) rather than guessing wrong and feeding the LLM rules for
    the wrong technology."""
    profiles: List[str] = []
    if lang in ("typescript", "javascript"):
        frontend_tech = (target.get("frontend_tech") or "").lower()
        for needle, profile in _FRONTEND_TECH_TO_PROFILE.items():
            if needle in frontend_tech:
                profiles.append(profile)
                break
        profiles.append("javascript_web")
    else:
        lang_profile = _LANGUAGE_TO_PROFILE.get(lang)
        if lang_profile:
            profiles.append(lang_profile)

    if include_datastore:
        profiles.extend(_DB_TARGET_TO_PROFILES.get(target.get("db_target", "mssql"), []))

    return profiles
