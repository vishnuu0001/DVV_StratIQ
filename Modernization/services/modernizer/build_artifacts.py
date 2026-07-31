# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer (build_artifacts.py)
# Date: 2026-06-21
# ---------------------------------------------------------------------------
from __future__ import annotations

import functools
import hashlib
import json
import logging
import os
import posixpath
import re
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)



# Function: _frontend_scaffold_files
def _frontend_scaffold_files(frontend_tech: str, project_name: str, is_azure_auth: bool) -> Dict[str, str]:
    """Deterministic frontend project scaffolding (dependency manifest,
    framework config, index.html, entry point) — pure boilerplate that must
    be syntactically valid for `npm install`/build to even start, not
    something worth risking on a 7B model remembering to include it among
    the 24-45 other files it's also asked to invent business logic for. This
    was the review's #2 blocker: no package.json/angular.json/tsconfig/
    index.html/main.ts anywhere in the delivered output.
    """
    fw = (frontend_tech or "").lower()
    name = project_name.lower()
    files: Dict[str, str] = {}

    if "angular" in fw:
        deps = {
            "@angular/animations": "^17.0.0", "@angular/common": "^17.0.0",
            "@angular/compiler": "^17.0.0", "@angular/core": "^17.0.0",
            "@angular/forms": "^17.0.0", "@angular/platform-browser": "^17.0.0",
            "@angular/platform-browser-dynamic": "^17.0.0", "@angular/router": "^17.0.0",
            "rxjs": "^7.8.0", "tslib": "^2.6.0", "zone.js": "^0.14.0",
        }
        if is_azure_auth:
            deps["@azure/msal-angular"] = "^3.0.0"
            deps["@azure/msal-browser"] = "^3.0.0"
        files["frontend/package.json"] = json.dumps({
            "name": name, "version": "0.0.1", "private": True,
            "scripts": {"ng": "ng", "start": "ng serve", "build": "ng build", "test": "ng test"},
            "dependencies": deps,
            "devDependencies": {
                "@angular-devkit/build-angular": "^17.0.0", "@angular/cli": "^17.0.0",
                "@angular/compiler-cli": "^17.0.0", "typescript": "5.2.2",
            },
        }, indent=2)
        files["frontend/angular.json"] = json.dumps({
            "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
            "version": 1, "newProjectRoot": "projects",
            "projects": {name: {
                "projectType": "application", "root": "", "sourceRoot": "src",
                "architect": {
                    "build": {
                        "builder": "@angular-devkit/build-angular:browser",
                        "options": {
                            "outputPath": "dist", "index": "src/index.html", "main": "src/main.ts",
                            "tsConfig": "tsconfig.json", "assets": ["src/assets"], "styles": ["src/styles.css"],
                        },
                    },
                    "serve": {"builder": "@angular-devkit/build-angular:dev-server"},
                },
            }},
        }, indent=2)
        files["frontend/tsconfig.json"] = json.dumps({
            "compileOnSave": False,
            "compilerOptions": {
                "outDir": "./dist/out-tsc", "strict": True, "module": "ES2022", "target": "ES2022",
                "moduleResolution": "bundler", "experimentalDecorators": True, "importHelpers": True,
                "lib": ["ES2022", "dom"], "types": [], "baseUrl": ".", "skipLibCheck": True,
            },
        }, indent=2)
        files["frontend/tsconfig.app.json"] = json.dumps({
            "extends": "./tsconfig.json",
            "compilerOptions": {"outDir": "./dist/out-tsc/app", "types": []},
            "files": ["src/main.ts"],
            "include": ["src/**/*.d.ts"],
        }, indent=2)
        files["frontend/src/index.html"] = textwrap.dedent(f"""\
            <!doctype html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <title>{project_name}</title>
              <base href="/">
              <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
              <app-root></app-root>
            </body>
            </html>
        """)
        files["frontend/src/main.ts"] = textwrap.dedent("""\
            import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
            import { AppModule } from './app/app.module';

            platformBrowserDynamic().bootstrapModule(AppModule)
              .catch(err => console.error(err));
        """)
        files["frontend/src/environments/environment.ts"] = textwrap.dedent("""\
            export const environment = {
              production: false,
              apiBaseUrl: '/api',
              azureAdClientId: '',
              azureAdAuthority: '',
            };
        """)
        files["frontend/src/environments/environment.production.ts"] = textwrap.dedent("""\
            export const environment = {
              production: true,
              apiBaseUrl: '/api',
              azureAdClientId: '',
              azureAdAuthority: '',
            };
        """)
        return files

    if "vue" in fw:
        files["frontend/package.json"] = json.dumps({
            "name": name, "version": "0.0.1", "private": True,
            "scripts": {"dev": "vite", "build": "vite build"},
            "dependencies": {"vue": "^3.4.0", "vue-router": "^4.2.0"},
            "devDependencies": {"@vitejs/plugin-vue": "^5.0.0", "vite": "^5.0.0", "typescript": "^5.2.0"},
        }, indent=2)
        files["frontend/vite.config.ts"] = (
            "import { defineConfig } from 'vite';\n"
            "import vue from '@vitejs/plugin-vue';\n\n"
            "export default defineConfig({\n  plugins: [vue()],\n});\n"
        )
        files["frontend/index.html"] = textwrap.dedent(f"""\
            <!doctype html>
            <html lang="en">
            <head><meta charset="UTF-8"><title>{project_name}</title></head>
            <body>
              <div id="app"></div>
              <script type="module" src="/src/main.ts"></script>
            </body>
            </html>
        """)
        return files

    # React default
    deps = {"react": "^18.2.0", "react-dom": "^18.2.0", "react-router-dom": "^6.21.0"}
    if is_azure_auth:
        deps["@azure/msal-react"] = "^2.0.0"
        deps["@azure/msal-browser"] = "^3.0.0"
    files["frontend/package.json"] = json.dumps({
        "name": name, "version": "0.0.1", "private": True,
        "scripts": {"dev": "vite", "build": "vite build"},
        "dependencies": deps,
        "devDependencies": {
            "@vitejs/plugin-react": "^4.2.0", "vite": "^5.0.0", "typescript": "^5.2.0",
            "@types/react": "^18.2.0", "@types/react-dom": "^18.2.0",
        },
    }, indent=2)
    files["frontend/vite.config.ts"] = (
        "import { defineConfig } from 'vite';\n"
        "import react from '@vitejs/plugin-react';\n\n"
        "export default defineConfig({\n  plugins: [react()],\n});\n"
    )
    files["frontend/index.html"] = textwrap.dedent(f"""\
        <!doctype html>
        <html lang="en">
        <head><meta charset="UTF-8"><title>{project_name}</title></head>
        <body>
          <div id="root"></div>
          <script type="module" src="/src/main.tsx"></script>
        </body>
        </html>
    """)
    return files


# Function: _backend_manifest_files
def _dotnet_tfm(backend_tech: str) -> str:
    """Extract the .NET target-framework moniker from a backend_tech string
    like ".NET 10" — shared by every deterministic generator that needs to
    agree on the same TFM (csproj, Dockerfile) rather than each re-deriving
    it and risking drift."""
    m = re.search(r"(\d+)", backend_tech or "")
    return f"net{m.group(1)}.0" if m else "net8.0"


# Function: _backend_manifest_files
def _backend_manifest_files(lang: str, project_name: str, backend_tech: str,
                             is_dapper: bool, is_azure_auth: bool,
                             db_target: str = "mssql") -> Dict[str, str]:
    """Deterministic backend dependency manifest. The review's #1 blocker was
    that no .csproj/.sln existed anywhere in the delivered output, so nothing
    could compile before a single line of business logic was even read.

    `db_target` must agree with whatever ADO.NET/EF provider the generated
    data-access code actually calls — defaulting this to SQL Server packages
    unconditionally left a postgres-targeted Dapper repository referencing
    Npgsql with no Npgsql package in the .csproj at all (and vice versa)."""
    if lang == "csharp":
        tfm = _dotnet_tfm(backend_tech)
        framework_major = tfm.removeprefix("net").split(".", 1)[0]
        ef_version = f"{framework_major}.0.0"
        is_postgres = (db_target or "").strip().lower() == "postgres"
        pkgs = (
            (
                ['<PackageReference Include="Dapper" Version="2.1.35" />',
                 '<PackageReference Include="Npgsql" Version="8.0.3" />']
                if is_postgres else
                ['<PackageReference Include="Dapper" Version="2.1.35" />',
                 '<PackageReference Include="Microsoft.Data.SqlClient" Version="5.2.0" />']
            )
            if is_dapper else
            (
                [f'<PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="{ef_version}" />',
                 f'<PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="{ef_version}" />']
                if is_postgres else
                [f'<PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="{ef_version}" />',
                 f'<PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="{ef_version}" />']
            )
        )
        if is_azure_auth:
            pkgs.append('<PackageReference Include="Microsoft.Identity.Web" Version="3.3.1" />')
        pkgs.append('<PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />')
        pkg_xml = "\n                ".join(pkgs)
        return {f"backend/{project_name}.csproj": textwrap.dedent(f"""\
            <Project Sdk="Microsoft.NET.Sdk.Web">
              <PropertyGroup>
                <TargetFramework>{tfm}</TargetFramework>
                <Nullable>enable</Nullable>
                <ImplicitUsings>enable</ImplicitUsings>
              </PropertyGroup>
              <ItemGroup>
                {pkg_xml}
              </ItemGroup>
            </Project>
        """)}
    if lang == "python":
        reqs = ["fastapi", "uvicorn[standard]", "pydantic"]
        reqs.append("sqlalchemy" if not is_dapper else "databases[postgresql]")
        if is_azure_auth:
            reqs.append("msal")
        return {"requirements.txt": "\n".join(reqs) + "\n"}
    if lang == "go":
        return {"go.mod": _go_mod(project_name, backend_tech)}
    if lang == "java":
        return {"backend/pom.xml": _java_backend_pom(project_name, backend_tech)}
    return {}


# Function: _java_backend_pom
_JAVA_IMPORT_DEPENDENCIES = {
    "org.springframework.web.reactive.": (
        "org.springframework.boot", "spring-boot-starter-webflux", None,
    ),
    "org.springframework.data.redis.": (
        "org.springframework.boot", "spring-boot-starter-data-redis", None,
    ),
    "org.springframework.amqp.": (
        "org.springframework.boot", "spring-boot-starter-amqp", None,
    ),
    "org.springframework.batch.": (
        "org.springframework.boot", "spring-boot-starter-batch", None,
    ),
    "org.springframework.integration.": (
        "org.springframework.integration", "spring-integration-core", None,
    ),
    "org.springframework.cloud.gateway.": (
        "org.springframework.cloud", "spring-cloud-starter-gateway", None,
    ),
    "io.github.resilience4j.": (
        "io.github.resilience4j", "resilience4j-spring-boot3", "2.2.0",
    ),
    "io.jsonwebtoken.": ("io.jsonwebtoken", "jjwt-api", "0.12.6"),
    "org.mapstruct.": ("org.mapstruct", "mapstruct", "1.6.3"),
    "com.google.protobuf.": ("com.google.protobuf", "protobuf-java", "4.28.3"),
    "org.apache.avro.": ("org.apache.avro", "avro", "1.12.0"),
}


def _java_inferred_dependencies(output: Optional[Dict[str, str]]) -> List[tuple[str, str, Optional[str]]]:
    """Resolve Maven dependencies from imports emitted by the Java generator.

    The canonical POM remains service-owned, but it is no longer a closed,
    hard-coded list: supported framework imports deterministically extend it
    before every build/repair pass.
    """
    if not output:
        return []
    java_sources = "\n".join(
        content for path, content in output.items()
        if path.casefold().endswith(".java") and isinstance(content, str)
    )
    dependencies = {
        coordinates
        for package, coordinates in _JAVA_IMPORT_DEPENDENCIES.items()
        if package in java_sources
    }
    for module in re.findall(
        r"\bimport\s+software\.amazon\.awssdk\.services\.([a-z0-9_]+)\.",
        java_sources,
    ):
        dependencies.add(("software.amazon.awssdk", module.replace("_", "-"), None))
    if "io.jsonwebtoken." in java_sources:
        dependencies.update({
            ("io.jsonwebtoken", "jjwt-impl", "0.12.6"),
            ("io.jsonwebtoken", "jjwt-jackson", "0.12.6"),
        })
    dependencies.discard(("software.amazon.awssdk", "sqs", None))
    return sorted(dependencies)


def _java_dependency_xml(
    dependencies: List[tuple[str, str, Optional[str]]],
) -> str:
    rows = []
    for group_id, artifact_id, version in dependencies:
        version_xml = f"<version>{version}</version>" if version else ""
        runtime_scope = (
            "<scope>runtime</scope>"
            if artifact_id in {"jjwt-impl", "jjwt-jackson"}
            else ""
        )
        rows.append(
            "            <dependency>"
            f"<groupId>{group_id}</groupId><artifactId>{artifact_id}</artifactId>"
            f"{version_xml}{runtime_scope}</dependency>"
        )
    return "\n".join(rows)


def _java_backend_pom(
    project_name: str, backend_tech: str,
    inferred_dependencies: Optional[List[tuple[str, str, Optional[str]]]] = None,
) -> str:
    """Return the canonical single-module Maven contract for generated Java services."""
    java_match = re.search(r"\bjava\s*(\d+)", backend_tech or "", re.IGNORECASE)
    java_version = java_match.group(1) if java_match else "21"
    artifact_id = re.sub(r"[^a-z0-9]+", "-", project_name.casefold()).strip("-") or "modernized-app"
    inferred_xml = _java_dependency_xml(inferred_dependencies or [])
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <parent>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-parent</artifactId>
            <version>3.3.5</version>
            <relativePath/>
          </parent>
          <groupId>com.modernize</groupId>
          <artifactId>{artifact_id}</artifactId>
          <version>1.0.0-SNAPSHOT</version>
          <name>{artifact_id}</name>
          <properties><java.version>{java_version}</java.version></properties>
          <dependencyManagement>
            <dependencies>
              <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>2023.0.3</version>
                <type>pom</type>
                <scope>import</scope>
              </dependency>
              <dependency>
                <groupId>software.amazon.awssdk</groupId>
                <artifactId>bom</artifactId>
                <version>2.29.29</version>
                <type>pom</type>
                <scope>import</scope>
              </dependency>
            </dependencies>
          </dependencyManagement>
          <dependencies>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-oauth2-resource-server</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-aop</artifactId></dependency>
            <dependency><groupId>org.springframework.retry</groupId><artifactId>spring-retry</artifactId></dependency>
            <dependency><groupId>org.springframework.kafka</groupId><artifactId>spring-kafka</artifactId></dependency>
            <dependency><groupId>org.springframework.cloud</groupId><artifactId>spring-cloud-starter-openfeign</artifactId></dependency>
            <dependency><groupId>org.springframework.cloud</groupId><artifactId>spring-cloud-starter-loadbalancer</artifactId></dependency>
            <dependency><groupId>software.amazon.awssdk</groupId><artifactId>sqs</artifactId></dependency>
            <dependency><groupId>org.springdoc</groupId><artifactId>springdoc-openapi-starter-webmvc-ui</artifactId><version>2.6.0</version></dependency>
            <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-core</artifactId></dependency>
            <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-database-postgresql</artifactId></dependency>
            <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>
            <dependency><groupId>io.micrometer</groupId><artifactId>micrometer-tracing-bridge-otel</artifactId></dependency>
            <dependency><groupId>io.opentelemetry</groupId><artifactId>opentelemetry-exporter-otlp</artifactId></dependency>
            <dependency><groupId>io.opentelemetry.instrumentation</groupId><artifactId>opentelemetry-instrumentation-annotations</artifactId><version>2.10.0</version></dependency>
            <dependency><groupId>net.logstash.logback</groupId><artifactId>logstash-logback-encoder</artifactId><version>7.4</version></dependency>
            <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>
            <dependency><groupId>org.springframework.security</groupId><artifactId>spring-security-test</artifactId><scope>test</scope></dependency>
            <dependency><groupId>org.springframework.kafka</groupId><artifactId>spring-kafka-test</artifactId><scope>test</scope></dependency>
            <dependency><groupId>org.testcontainers</groupId><artifactId>junit-jupiter</artifactId><scope>test</scope></dependency>
            <dependency><groupId>org.testcontainers</groupId><artifactId>postgresql</artifactId><scope>test</scope></dependency>
            <dependency><groupId>org.testcontainers</groupId><artifactId>kafka</artifactId><scope>test</scope></dependency>
            <dependency><groupId>io.rest-assured</groupId><artifactId>rest-assured</artifactId><scope>test</scope></dependency>
{inferred_xml}
          </dependencies>
          <build>
            <plugins>
              <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
              </plugin>
            </plugins>
          </build>
        </project>
    """)


def _java_reactor_pom(project_name: str, modules: List[str], java_version: str) -> str:
    """Return an aggregator POM for an explicitly requested Maven reactor."""
    artifact_id = re.sub(r"[^a-z0-9]+", "-", project_name.casefold()).strip("-") or "modernized-app"
    module_xml = "\n".join(f"    <module>{module}</module>" for module in modules)
    template = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <groupId>com.modernize</groupId>
          <artifactId>{artifact_id}-reactor</artifactId>
          <version>1.0.0-SNAPSHOT</version>
          <packaging>pom</packaging>
          <properties><java.version>{java_version}</java.version></properties>
          <modules>
        __REACTOR_MODULES__
          </modules>
        </project>
    """)
    return template.replace("__REACTOR_MODULES__", module_xml)


def _java_module_roots(output: Dict[str, str], project_name: str) -> List[str]:
    """Discover real Maven modules from backend/<module>/src source roots."""
    marker = f"{project_name}/backend/"
    modules = set()
    for path in output:
        if not path.startswith(marker):
            continue
        relative = path[len(marker):]
        module, separator, remainder = relative.partition("/")
        if separator and remainder.startswith("src/") and module != "src":
            modules.add(module)
    return sorted(modules)


_FRONTEND_IMPORT_DEPENDENCIES = {
    "axios": "^1.7.9",
    "clsx": "^2.1.1",
    "date-fns": "^4.1.0",
    "lucide-react": "^0.468.0",
    "react-hook-form": "^7.54.0",
    "react-router-dom": "^6.28.0",
    "recharts": "^2.15.0",
    "tailwind-merge": "^2.6.0",
    "zod": "^3.24.0",
    "@hookform/resolvers": "^3.9.1",
    "@tanstack/react-query": "^5.62.0",
    "@tanstack/react-query-devtools": "^5.62.0",
    "@angular/cdk": "^17.3.10",
    "@angular/material": "^17.3.10",
    "@ngrx/effects": "^17.2.0",
    "@ngrx/store": "^17.2.0",
    "web-vitals": "^3.5.2",
}


# Function: _imported_package_name
def _imported_package_name(specifier: str) -> str:
    if not specifier or specifier.startswith((".", "/", "src/", "@/")):
        return ""
    parts = specifier.split("/")
    return "/".join(parts[:2]) if specifier.startswith("@") and len(parts) > 1 else parts[0]


# Function: _reconcile_java_frontend_dependencies
def _reconcile_java_frontend_dependencies(output: Dict[str, str]) -> None:
    """Close known frontend import dependencies before Java full-stack acceptance."""
    package_paths = [
        path for path in output
        if path.casefold().endswith("/frontend/package.json")
    ]
    for package_path in package_paths:
        try:
            package_data = json.loads(output[package_path])
        except (TypeError, ValueError):
            continue
        frontend_root = package_path.rsplit("/", 1)[0] + "/"
        imported = set()
        for source_path, content in output.items():
            if (
                source_path.startswith(frontend_root)
                and source_path.endswith((".js", ".jsx", ".ts", ".tsx"))
                and isinstance(content, str)
            ):
                specifiers = re.findall(
                    r"""(?:\bfrom\s*|\bimport\s*\(\s*|\bimport\s+)["']([^"']+)""",
                    content,
                )
                imported.update(filter(None, map(_imported_package_name, specifiers)))
        dependencies = package_data.setdefault("dependencies", {})
        changed = False
        for package in sorted(imported):
            if package in _FRONTEND_IMPORT_DEPENDENCIES and package not in dependencies:
                dependencies[package] = _FRONTEND_IMPORT_DEPENDENCIES[package]
                changed = True
        if changed:
            output[package_path] = json.dumps(package_data, indent=2) + "\n"


# Function: _reconcile_java_generation_output
def _reconcile_java_generation_output(output: Dict[str, str], project_name: str) -> None:
    """Enforce the canonical Java build boundary and frontend dependency closure."""
    # Normalize source APIs before inferring Maven dependencies. Otherwise a
    # repair that introduces the canonical JJWT/WebFlux/etc. import leaves the
    # POM one pass behind and guarantees a needless failed build round.
    _migrate_spring_boot3_javax_imports(output)
    _migrate_spring_filter_contracts(output)
    _migrate_java_record_factories(output)
    _migrate_java_record_getter_calls(output)
    _reconcile_java_entity_read_accessors(output)
    _synthesize_java_entity_dto_factories(output)
    _migrate_java_identity_pageable_lambda(output)
    _promote_privately_referenced_java_nested_types(output)
    _migrate_java_decimal_min_literals(output)
    _reconcile_java_stray_test_tree_duplicates(output)
    _repair_java_chained_assertj_extracting(output)
    _reconcile_java_repository_contracts(output)
    _strip_invalid_java_control_characters(output)
    canonical_pom = f"{project_name}/backend/pom.xml"
    module_roots = _java_module_roots(output, project_name)
    is_multi_module = len(module_roots) >= 2
    if canonical_pom in output:
        version_match = re.search(
            r"<java\.version>\s*(\d+)\s*</java\.version>",
            output[canonical_pom],
            re.IGNORECASE,
        )
        java_version = version_match.group(1) if version_match else "21"
    else:
        java_version = "21"
    if is_multi_module:
        output[canonical_pom] = _java_reactor_pom(project_name, module_roots, java_version)
        backend_root = f"{project_name}/backend/"
        expected_poms = {canonical_pom}
        for module in module_roots:
            module_prefix = f"{backend_root}{module}/"
            module_output = {
                path: content for path, content in output.items()
                if path.startswith(module_prefix)
            }
            module_pom = f"{module_prefix}pom.xml"
            output[module_pom] = _java_backend_pom(
                module,
                f"Java {java_version} Spring Boot 3",
                _java_inferred_dependencies(module_output),
            )
            expected_poms.add(module_pom)
            output.setdefault(
                f"{module_prefix}Dockerfile",
                _java_service_dockerfile(module),
            )
            output.setdefault(
                f"{module_prefix}src/main/resources/application.yml",
                _java_service_application_yml(module),
            )
        for path in list(output):
            if path.casefold().endswith("/pom.xml") and path not in expected_poms:
                del output[path]
    else:
        output[canonical_pom] = _java_backend_pom(
            project_name,
            f"Java {java_version} Spring Boot 3",
            _java_inferred_dependencies(output),
        )
        for path in list(output):
            if path != canonical_pom and path.casefold().endswith("/pom.xml"):
                del output[path]
        _flatten_java_module_paths(output)
        backend_root = f"{project_name}/backend/"
        output.setdefault(f"{backend_root}Dockerfile", _java_service_dockerfile(project_name))
        output.setdefault(
            f"{backend_root}src/main/resources/application.yml",
            _java_service_application_yml(project_name),
        )
    _align_java_public_type_paths(output)
    _migrate_spring_security_authorities_claim_api(output)
    _reconcile_java_type_imports(output, module_scoped=is_multi_module)
    _reconcile_java_frontend_dependencies(output)
    _reconcile_java_frontend_local_assets(output)
    _reconcile_java_frontend_exports(output)
    _reconcile_java_frontend_entry_point(output)


def _java_service_dockerfile(module: str) -> str:
    """Canonical Maven/JRE 21 image contract for every reactor service."""
    artifact = re.sub(r"[^a-z0-9]+", "-", module.casefold()).strip("-")
    return textwrap.dedent(f"""\
        FROM maven:3.9.9-eclipse-temurin-21 AS build
        WORKDIR /workspace
        COPY pom.xml .
        COPY src src
        RUN mvn -B -q -DskipTests package

        FROM eclipse-temurin:21-jre
        WORKDIR /app
        COPY --from=build /workspace/target/{artifact}-*.jar app.jar
        EXPOSE 8080
        ENTRYPOINT ["java", "-jar", "/app/app.jar"]
    """)


def _java_service_application_yml(module: str) -> str:
    """Minimal environment-driven configuration when planning omitted one."""
    return textwrap.dedent(f"""\
        spring:
          application:
            name: {module}
        server:
          port: ${{SERVER_PORT:8080}}
        management:
          endpoints:
            web:
              exposure:
                include: health,info
    """)


def _strip_invalid_java_control_characters(output: Dict[str, str]) -> None:
    """Remove C0/C1 response artifacts that Windows javac cannot decode."""
    for path, content in list(output.items()):
        if path.casefold().endswith(".java") and isinstance(content, str):
            output[path] = "".join(
                char for char in content
                if char in "\n\r\t" or ord(char) >= 160 or ord(char) >= 32 and ord(char) < 127
            )


def _migrate_spring_filter_contracts(output: Dict[str, str]) -> None:
    """Repair the common annotation-as-base-class servlet filter hallucination."""
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or "doFilterInternal(" not in content:
            continue
        if re.search(r"\bextends\s+Component\b", content):
            content = re.sub(
                r"\bextends\s+Component\b", "extends OncePerRequestFilter", content,
            )
            if "org.springframework.web.filter.OncePerRequestFilter" not in content:
                package = re.search(r"\bpackage\s+[^;]+;", content)
                if package:
                    content = (
                        content[:package.end()] +
                        "\n\nimport org.springframework.web.filter.OncePerRequestFilter;" +
                        content[package.end():]
                    )
        content = content.replace(
            'EnvironmentVariables.getSecret("JWT_SECRET")',
            'System.getenv("JWT_SECRET")',
        )
        content = content.replace("Base64Utils.decode(", "Base64.getDecoder().decode(")
        output[path] = _add_known_java_imports(content)


def _migrate_java_record_factories(output: Dict[str, str]) -> None:
    """Use canonical constructors when a record declares no ``of`` factory."""
    records: Dict[tuple[str, str], bool] = {}
    for path, content in output.items():
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        module = _java_source_module(path)
        for name in re.findall(r"\brecord\s+([A-Za-z_]\w*)\s*\(", content):
            has_factory = bool(re.search(
                rf"\bstatic\s+{re.escape(name)}\s+of\s*\(", content,
            ))
            records[(module, name)] = has_factory
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        module = _java_source_module(path)
        for (owner, name), has_factory in records.items():
            if owner != module or has_factory:
                continue
            content = re.sub(
                rf"\b{re.escape(name)}\.of\(([^;\n]*)\)",
                rf"new {name}(\1)",
                content,
            )
        output[path] = content


def _java_record_components(output: Dict[str, str]) -> Dict[tuple[str, str], List[str]]:
    """Component name lists for every declared record, keyed by (module,
    record name) — the record's own declaration is authoritative for its
    real accessor shape, the same source of truth `_migrate_java_record_factories`
    already trusts for constructor calls."""
    components: Dict[tuple[str, str], List[str]] = {}
    for path, content in output.items():
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        module = _java_source_module(path)
        for match in re.finditer(r"\brecord\s+([A-Za-z_]\w*)\s*\(", content):
            name = match.group(1)
            open_paren = match.end() - 1
            depth = 0
            close_paren = None
            # Bean Validation component annotations routinely carry their
            # own parens — `@NotBlank(message = "...")`, `@Min(value = 0L,
            # message = "...")` — so a naive `[^)]*` capture for the
            # component list stops at the *annotation's* closing paren, not
            # the record's, and silently mis-parses every annotated field.
            for index in range(open_paren, len(content)):
                if content[index] == "(":
                    depth += 1
                elif content[index] == ")":
                    depth -= 1
                    if depth == 0:
                        close_paren = index
                        break
            if close_paren is None:
                continue
            params = content[open_paren + 1:close_paren]
            names = [tokens[-1] for tokens in (p.split() for p in _split_java_arguments(params)) if tokens]
            components[(module, name)] = names
    return components


def _java_top_level_method_spans(content: str) -> List[tuple[int, int]]:
    """(start, end) character spans of each depth-2 brace block in a
    single-top-level-type file — i.e. each method/constructor body.

    Used to scope a `TypeName varName` binding to the method it is actually
    declared in: the same parameter name (`request`, `product`, ...) is
    routinely reused across sibling methods with a *different* declared
    type in generated Spring code, so a file-wide "this name means this
    type everywhere" binding silently mis-attributes accessor calls in
    every method except the last one scanned.
    """
    spans: List[tuple[int, int]] = []
    depth = 0
    start: Optional[int] = None
    for index, char in enumerate(content):
        if char == "{":
            depth += 1
            if depth == 2:
                start = index
        elif char == "}":
            if depth == 2 and start is not None:
                spans.append((start, index + 1))
                start = None
            depth = max(0, depth - 1)
    return spans


def _java_scope_variable_bindings(
    content: str, type_names,
) -> List[tuple[int, int, str, str]]:
    """Find `TypeName varName` declarations (parameter or local) for each
    name in `type_names`, each attributed to its enclosing method/constructor
    body span (see `_java_top_level_method_spans`)."""
    spans = _java_top_level_method_spans(content)
    bindings: List[tuple[int, int, str, str]] = []
    for type_name in type_names:
        for match in re.finditer(
            rf"\b{re.escape(type_name)}\s+([a-zA-Z_]\w*)\s*(?=[=;,)])", content,
        ):
            pos = match.start()
            # Local declarations sit inside their own body — "containing"
            # span. Parameter declarations sit in the method *signature*,
            # entirely before that method's own opening brace — the nearest
            # *following* span is unambiguously the body that parameter is
            # live in, since nothing else opens a depth-2 block between a
            # parameter list and its own method body.
            span = next(((s, e) for s, e in spans if s <= pos < e), None)
            if span is None:
                span = next(((s, e) for s, e in spans if s >= pos), None)
            if span is None:
                continue
            bindings.append((span[0], span[1], match.group(1), type_name))
    return bindings


def _apply_scoped_java_rewrites(
    content: str,
    bindings: List[tuple[int, int, str, str]],
    rewrite_fn: Callable[[str, str, str], str],
) -> str:
    """Apply `rewrite_fn(segment, var_name, type_name)` once per distinct
    method-body span, then reassemble — spans from
    `_java_top_level_method_spans` are non-overlapping, so this stays
    correct regardless of how much a rewrite changes each segment's length."""
    by_span: Dict[tuple[int, int], List[tuple[str, str]]] = {}
    for start, end, var_name, type_name in bindings:
        by_span.setdefault((start, end), []).append((var_name, type_name))
    if not by_span:
        return content
    pieces: List[str] = []
    cursor = 0
    for start, end in sorted(by_span):
        pieces.append(content[cursor:start])
        segment = content[start:end]
        for var_name, type_name in by_span[(start, end)]:
            segment = rewrite_fn(segment, var_name, type_name)
        pieces.append(segment)
        cursor = end
    pieces.append(content[cursor:])
    return "".join(pieces)


def _migrate_java_record_getter_calls(output: Dict[str, str]) -> None:
    """Rewrite JavaBean-style `.getX()`/`.isX()` calls made against a value
    declared (as a parameter or local) with a known record type back to
    that record's own canonical `.x()` accessor.

    This is the single most common per-file-generation drift for
    request/response DTOs: the DTO itself gets generated as a record, but a
    *consumer* file (a controller calling into a service's request type, or
    vice versa) is generated independently assuming JavaBean getters —
    e.g. `ProductCreateRequest` is a record but `ProductController` calls
    `request.getSku()`, or `OrderService`'s own nested `CreateOrderRequest`
    record is read via `request.getProductId()`/`request.getQuantity()`.
    """
    components = _java_record_components(output)
    if not components:
        return
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        module = _java_source_module(path)
        module_records = {name: fields for (mod, name), fields in components.items() if mod == module}
        if not module_records:
            continue
        bindings = _java_scope_variable_bindings(content, module_records)
        if not bindings:
            continue

        def rewrite(segment: str, var_name: str, record_name: str) -> str:
            for field in module_records[record_name]:
                cap = field[0].upper() + field[1:]
                for accessor in (f"get{cap}", f"is{cap}"):
                    pattern = rf"\b{re.escape(var_name)}\.{accessor}\(\)"
                    segment = re.sub(pattern, f"{var_name}.{field}()", segment)
            return segment

        output[path] = _apply_scoped_java_rewrites(content, bindings, rewrite)


def _java_entity_shapes(output: Dict[str, str]) -> Dict[tuple[str, str], dict]:
    """Real accessor surface of every plain (non-record) `@Entity` class —
    the authoritative shape a per-file-generated service/DTO must actually
    call against, instead of the record-style accessors or Lombok-builder
    API a *different* generation pass may have assumed for the same type."""
    shapes: Dict[tuple[str, str], dict] = {}
    for path, content in output.items():
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        if "@Entity" not in content or "toBuilder" in content:
            continue
        class_match = re.search(r"\bclass\s+([A-Za-z_]\w*)\b", content)
        if not class_match:
            continue
        name = class_match.group(1)
        getters: Dict[str, str] = {}
        for match in re.finditer(
            r"\bpublic\s+[\w<>\[\],.?]+\s+(get|is)([A-Za-z_]\w*)\s*\(\s*\)", content,
        ):
            prefix, rest = match.groups()
            getters[rest[0].lower() + rest[1:]] = prefix + rest
        if not getters:
            continue
        shapes[(_java_source_module(path), name)] = {"path": path, "getters": getters}
    return shapes


def _java_repository_entity_map(output: Dict[str, str]) -> Dict[tuple[str, str], str]:
    """Entity type each Spring Data repository interface is declared over."""
    mapping: Dict[tuple[str, str], str] = {}
    for path, content in output.items():
        if not path.casefold().endswith("repository.java") or not isinstance(content, str):
            continue
        match = re.search(
            r"\binterface\s+([A-Za-z_]\w*)\s+extends\s+[\w.]*"
            r"(?:JpaRepository|CrudRepository|PagingAndSortingRepository)\s*<\s*([A-Za-z_]\w*)\s*,",
            content,
        )
        if match:
            mapping[(_java_source_module(path), match.group(1))] = match.group(2)
    return mapping


def _reconcile_java_entity_read_accessors(output: Dict[str, str]) -> None:
    """Rewrite record-style bareword calls (`.id()`, `.name()`, ...) made
    against a value that resolves to a plain JPA entity back to that
    entity's real getter. This is the inverse drift of
    `_migrate_java_record_getter_calls`: a service method gets generated
    assuming its repository returns an immutable record when the entity is
    actually a mutable JavaBean-style `@Entity` class."""
    entities = _java_entity_shapes(output)
    if not entities:
        return
    repo_entity = _java_repository_entity_map(output)
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        module = _java_source_module(path)
        module_entities = {name: shape for (mod, name), shape in entities.items() if mod == module}
        if not module_entities:
            continue
        module_repos = {
            repo: entity for (mod, repo), entity in repo_entity.items()
            if mod == module and entity in module_entities
        }

        spans = _java_top_level_method_spans(content)
        bindings = _java_scope_variable_bindings(content, module_entities)

        repo_fields: Dict[str, str] = {}
        for repo_name, entity_name in module_repos.items():
            for match in re.finditer(rf"\b{re.escape(repo_name)}\s+(\w+)\s*[;)]", content):
                repo_fields[match.group(1)] = entity_name
        for repo_field, entity_name in repo_fields.items():
            chain = (
                rf"\bvar\s+(\w+)\s*=\s*{re.escape(repo_field)}\."
                rf"(?:findById|findByIdOrThrow)\([^;]*?\)\s*\.(?:orElseThrow\([^;]*\)|get\(\))\s*;"
            )
            for match in re.finditer(chain, content):
                span = next(((s, e) for s, e in spans if s <= match.start() < e), None)
                if span:
                    bindings.append((span[0], span[1], match.group(1), entity_name))
            for match in re.finditer(
                rf"\bvar\s+(\w+)\s*=\s*{re.escape(repo_field)}\.save\([^;]*\)\s*;", content,
            ):
                span = next(((s, e) for s, e in spans if s <= match.start() < e), None)
                if span:
                    bindings.append((span[0], span[1], match.group(1), entity_name))

        if not bindings:
            continue

        def rewrite(segment: str, var_name: str, entity_name: str) -> str:
            shape = module_entities[entity_name]
            for field, getter in shape["getters"].items():
                pattern = rf"\b{re.escape(var_name)}\.{re.escape(field)}\(\)"
                segment = re.sub(pattern, f"{var_name}.{getter}()", segment)
            return segment

        output[path] = _apply_scoped_java_rewrites(content, bindings, rewrite)


_ENTITY_DTO_SUFFIXES = ("Response", "Dto", "DTO")


def _synthesize_java_entity_dto_factories(output: Dict[str, str]) -> None:
    """Synthesize a missing `X.from(Entity)` static factory for an
    `<Entity><Suffix>` record whose components are all satisfied by the
    entity's real getters.

    `<Response>.from(<entity>)` is a convention several generated
    controllers/services call by name without the DTO itself ever defining
    it — a missing-method gap, not a wrong-call-site gap, so no amount of
    call-site rewriting fixes it; the method has to actually exist.
    """
    components = _java_record_components(output)
    entities = _java_entity_shapes(output)
    if not components or not entities:
        return
    for (module, record_name), fields in components.items():
        record_path = next(
            (
                path for path, content in output.items()
                if path.casefold().endswith(".java") and isinstance(content, str)
                and _java_source_module(path) == module
                and re.search(rf"\brecord\s+{re.escape(record_name)}\s*\(", content)
            ),
            None,
        )
        if not record_path:
            continue
        record_content = output[record_path]
        if re.search(rf"\bstatic\s+{re.escape(record_name)}\s+from\s*\(", record_content):
            continue
        entity_name = next(
            (
                record_name[:-len(suffix)] for suffix in _ENTITY_DTO_SUFFIXES
                if record_name.endswith(suffix) and (module, record_name[:-len(suffix)]) in entities
            ),
            None,
        )
        if not entity_name:
            continue
        getters = entities[(module, entity_name)]["getters"]
        accessors: List[str] = []
        for field in fields:
            getter = getters.get(field)
            if not getter:
                accessors = []
                break
            accessors.append(f"source.{getter}()")
        if not accessors:
            continue
        factory = (
            f"\n\n    public static {record_name} from({entity_name} source) {{\n"
            f"        return new {record_name}({', '.join(accessors)});\n"
            f"    }}\n"
        )
        insertion = record_content.rfind("}")
        if insertion == -1:
            continue
        output[record_path] = record_content[:insertion] + factory + record_content[insertion:]


def _migrate_java_identity_pageable_lambda(output: Dict[str, str]) -> None:
    """`.findAll(x -> x)` is never valid — no JpaRepository overload accepts
    a same-typed identity function — and is a recurring hallucinated
    stand-in for "no paging requested"."""
    pattern = re.compile(r"\.findAll\(\s*(\w+)\s*->\s*\1\s*\)")
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        if pattern.search(content):
            output[path] = pattern.sub(".findAll(Pageable.unpaged())", content)


def _promote_privately_referenced_java_nested_types(output: Dict[str, str]) -> None:
    """A DTO/record declared `private` inside one class but imported or
    referenced by a *different* top-level class cannot compile — Java's
    private access is scoped to the enclosing top-level class/file, and a
    controller generated independently of its service routinely imports
    `Service.RequestType` without knowing (or being able to know) that the
    service generated that type as a private nested member. Promote the
    declaration to `public` rather than guess at extracting it into its own
    top-level file, since other generated files may already reference it
    exactly as `Owner.Nested`."""
    private_nested: Dict[tuple[str, str], tuple[str, str]] = {}
    for path, content in output.items():
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        owner_match = re.search(
            r"\b(?:public\s+)?(?:class|interface|record|enum)\s+([A-Za-z_]\w*)", content,
        )
        if not owner_match:
            continue
        owner = owner_match.group(1)
        for nested_match in re.finditer(
            r"(?m)^[ \t]*private\s+((?:static\s+)?(?:final\s+)?record\s+([A-Za-z_]\w*)\s*\([^)]*\)\s*\{)",
            content,
        ):
            private_nested[(owner, nested_match.group(2))] = (path, nested_match.group(0))
        for nested_match in re.finditer(
            r"(?m)^[ \t]*private\s+((?:static\s+)?(?:final\s+)?class\s+([A-Za-z_]\w*)\b)",
            content,
        ):
            private_nested[(owner, nested_match.group(2))] = (path, nested_match.group(0))

    if not private_nested:
        return

    referenced: set[tuple[str, str]] = set()
    for path, content in output.items():
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        for (owner, name), (source_path, _declaration) in private_nested.items():
            if path == source_path:
                continue
            if re.search(rf"\b{re.escape(owner)}\.{re.escape(name)}\b", content):
                referenced.add((owner, name))

    for owner, name in referenced:
        source_path, declaration = private_nested[(owner, name)]
        promoted = declaration.replace("private ", "public ", 1)
        output[source_path] = output[source_path].replace(declaration, promoted, 1)


def _migrate_java_decimal_min_literals(output: Dict[str, str]) -> None:
    """Repair `@Min` applied to a fractional literal. `@Min.value()` is a
    `long`, so `@Min(value = 0.01, ...)` on a BigDecimal/Double field is a
    lossy-conversion compile error, not a validation-logic bug — the
    generator meant `@DecimalMin`, the Bean Validation annotation for
    exactly this case, whose bound is a `String`."""
    pattern = re.compile(r"@Min\((\s*(?:value\s*=\s*)?)(\d+\.\d+)")
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        if pattern.search(content):
            output[path] = pattern.sub(
                lambda m: f'@DecimalMin({m.group(1)}"{m.group(2)}"', content,
            )


_REACT_APP_SHELL = textwrap.dedent("""\
    export default function App() {
      return (
        <div>
          <h1>Application is running</h1>
        </div>
      );
    }
""")


def _react_entry_point_source(is_typescript: bool) -> str:
    cast = " as HTMLElement" if is_typescript else ""
    return textwrap.dedent(f"""\
        import React from 'react';
        import ReactDOM from 'react-dom/client';
        import App from './App';

        ReactDOM.createRoot(document.getElementById('root'){cast}).render(
          <React.StrictMode>
            <App />
          </React.StrictMode>,
        );
    """)


def _reconcile_java_frontend_entry_point(output: Dict[str, str]) -> None:
    """Guarantee the module index.html's `<script src="/src/main.tsx">`
    points to actually exists. `_frontend_scaffold_files`'s React branch
    always wires index.html to that entry point deterministically, but the
    module itself is normally the LLM's responsibility; if planning or
    generation dropped the entire frontend/src tree, ship a minimal — but
    real — mount point rather than fail npm's bundler on an unresolvable
    local import that this same pipeline guaranteed would be referenced."""
    for html_path, html in list(output.items()):
        if not html_path.casefold().endswith("index.html") or not isinstance(html, str):
            continue
        match = re.search(r'<script[^>]+src=["\']/?(src/main\.tsx)["\']', html)
        if not match:
            continue
        root = html_path.rsplit("/", 1)[0] if "/" in html_path else ""
        entry_path = f"{root}/{match.group(1)}" if root else match.group(1)
        if entry_path in output:
            continue
        app_path = next(
            (f"{root}/src/App.{ext}" for ext in ("tsx", "jsx") if f"{root}/src/App.{ext}" in output),
            None,
        )
        if app_path is None:
            app_path = f"{root}/src/App.tsx"
            output[app_path] = _REACT_APP_SHELL
        output[entry_path] = _react_entry_point_source(app_path.endswith(".tsx"))


def _reconcile_java_stray_test_tree_duplicates(output: Dict[str, str]) -> None:
    """A production-shaped class (no `@Test` methods, no JUnit imports)
    generated under `src/test/java` with the same package + simple name as a
    `src/main/java` class in the same module is always a duplicate-class
    compile error waiting to happen: javac's test-compile phase sees the
    identical FQCN already on the classpath (compiled from main) and again
    as a fresh test source, and refuses to proceed.

    This is a per-file-generation/repair mixup — a corrected class body
    written to the wrong tree — not a legitimate test double, so the stray
    copy is removed and whichever version looks the least like a stub
    (fewest "Placeholder"/TODO markers, then longest) is kept as the single
    `src/main/java` source of truth. The real `*Test.java` sitting right
    next to it is untouched.
    """
    placeholder_pattern = re.compile(r"//\s*Placeholder|\bTODO\b", re.IGNORECASE)

    def completeness_key(text: str) -> tuple[int, int]:
        return (len(placeholder_pattern.findall(text)), -len(text))

    marker = "/src/test/java/"
    for path in list(output.keys()):
        if not path.casefold().endswith(".java") or marker not in path:
            continue
        stem = Path(path).stem
        if stem.endswith(("Test", "Tests", "IT")):
            continue
        content = output.get(path)
        if not isinstance(content, str) or "@Test" in content or re.search(r"\borg\.junit\b", content):
            continue
        main_path = path.replace(marker, "/src/main/java/", 1)
        main_content = output.get(main_path)
        if not isinstance(main_content, str):
            continue
        output[main_path] = content if completeness_key(content) < completeness_key(main_content) else main_content
        del output[path]


def _split_java_fluent_chain(text: str) -> List[tuple[str, str]]:
    """Split `.a(x).b(y).c()` into `[("a", "x"), ("b", "y"), ("c", "")]`,
    respecting one level of nested parens inside each call's arguments."""
    calls: List[tuple[str, str]] = []
    index = 0
    length = len(text)
    while index < length:
        if text[index] != ".":
            index += 1
            continue
        match = re.match(r"\.([A-Za-z_]\w*)\(", text[index:])
        if not match:
            index += 1
            continue
        name = match.group(1)
        args_start = index + match.end()
        depth = 1
        cursor = args_start
        while cursor < length and depth > 0:
            if text[cursor] == "(":
                depth += 1
            elif text[cursor] == ")":
                depth -= 1
            cursor += 1
        calls.append((name, text[args_start:cursor - 1]))
        index = cursor
    return calls


_ASSERTJ_CHAIN_STATEMENT = re.compile(
    r"assertThat\(((?:[^()]|\([^()]*\))*)\)((?:\s*\.[A-Za-z_]\w*\((?:[^()]|\([^()]*\))*\))+)\s*;"
)


def _repair_java_chained_assertj_extracting(output: Dict[str, str]) -> None:
    """Split `assertThat(x)....extracting(A::f).isEqualTo(v1).extracting(B::g)...`
    chains into one `assertThat(...)` per extraction.

    AssertJ's `.isEqualTo(...)` returns `self` on the *extracted* assert
    (now typed to the extracted value, e.g. `ObjectAssert<String>`), not the
    original subject's assert — a second `.extracting(...)` further down the
    same chain has no matching overload against that narrowed type. This is
    a recurring per-file-generation anti-pattern in JUnit/AssertJ tests, not
    a one-off; splitting the chain (assert each extracted value against the
    *original* subject, independently) preserves exactly the same
    assertions the test intended without guessing at new ones.
    """
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue

        def repair(match: re.Match) -> str:
            subject, chain_text = match.groups()
            calls = _split_java_fluent_chain(chain_text)
            if sum(1 for name, _ in calls if name == "extracting") < 2:
                return match.group(0)
            statements: List[str] = []
            current_subject = subject
            pending: List[str] = []
            for name, args in calls:
                if name == "extracting":
                    if pending:
                        statements.append(f"assertThat({current_subject}){''.join(pending)};")
                        pending = []
                    reference = re.match(r"\s*([A-Za-z_][\w.]*)\s*::\s*([A-Za-z_]\w*)\s*$", args)
                    if not reference:
                        return match.group(0)
                    current_subject = f"{subject}.{reference.group(2)}()"
                else:
                    pending.append(f".{name}({args})")
            if pending:
                statements.append(f"assertThat({current_subject}){''.join(pending)};")
            return "\n        ".join(statements) if statements else match.group(0)

        new_content = _ASSERTJ_CHAIN_STATEMENT.sub(repair, content)
        if new_content != content:
            output[path] = new_content


def _split_java_arguments(value: str) -> List[str]:
    """Split a Java argument/parameter list without splitting nested calls."""
    parts: List[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(value):
        if char in "(<[{":
            depth += 1
        elif char in ")>]}":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    tail = value[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def _reconcile_java_repository_contracts(output: Dict[str, str]) -> None:
    """Align generated repository call sites with their declared return/arity."""
    contracts: Dict[tuple[str, str], List[tuple[str, List[str]]]] = {}
    for path, content in output.items():
        if (
            not path.casefold().endswith("repository.java")
            or not isinstance(content, str)
            or "interface " not in content
        ):
            continue
        module = _java_source_module(path)
        for match in re.finditer(
            r"(?m)^\s*((?:java\.util\.)?List\s*<[^;]+?>|"
            r"(?:org\.springframework\.data\.domain\.)?Page\s*<[^;]+?>|"
            r"[A-Za-z_][\w<>?, .]*)\s+([A-Za-z_]\w*)\s*\(([^;]*)\)\s*;",
            content,
        ):
            return_type, method, parameters = match.groups()
            contracts.setdefault((module, method), []).append(
                (return_type.strip(), _split_java_arguments(parameters))
            )
    unique = {
        key: values[0] for key, values in contracts.items() if len(values) == 1
    }
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        module = _java_source_module(path)
        for (owner, method), (return_type, parameters) in unique.items():
            if owner != module:
                continue
            call = rf"\b[A-Za-z_]\w*\.{re.escape(method)}\(([^;\n]*)\)"
            if re.search(r"(?:^|\.)List\s*<", return_type):
                content = re.sub(rf"({call})\.getContent\(\)", r"\1", content)
            if parameters and "Pageable" in parameters[-1]:
                def add_pageable(match: re.Match) -> str:
                    arguments = _split_java_arguments(match.group(1))
                    if len(arguments) != len(parameters) - 1:
                        return match.group(0)
                    joined = match.group(1).rstrip()
                    separator = ", " if joined else ""
                    return match.group(0)[:-1] + separator + "Pageable.unpaged())"
                content = re.sub(call, add_pageable, content)
        output[path] = content


def _migrate_spring_security_authorities_claim_api(output: Dict[str, str]) -> None:
    """Repair a common hallucinated Spring Security JWT converter method."""
    for path, content in list(output.items()):
        if (
            path.casefold().endswith(".java")
            and isinstance(content, str)
            and "JwtGrantedAuthoritiesConverter" in content
            and ".setClaimName(" in content
        ):
            output[path] = content.replace(
                ".setClaimName(",
                ".setAuthoritiesClaimName(",
            )


# Function: _java_single_module_path
def _java_single_module_path(path: str) -> str:
    """Flatten pseudo-module source roots into the canonical backend module."""
    normalized = path.replace("\\", "/")
    return re.sub(
        r"(^|/)backend/[^/]+/(src/(?:main|test)/(?:java|resources)/)",
        r"\1backend/\2",
        normalized,
        count=1,
    )


# Function: _flatten_java_module_paths
def _flatten_java_module_paths(output: Dict[str, str]) -> None:
    for path in list(output):
        flattened = _java_single_module_path(path)
        if flattened == path:
            continue
        output.setdefault(flattened, output[path])
        del output[path]


def _align_java_public_type_paths(output: Dict[str, str]) -> None:
    """Make Maven's source filename contract deterministic for public types."""
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        public_type = re.search(
            r"\bpublic\s+(?:(?:abstract|final|sealed|non-sealed)\s+)*"
            r"(?:class|interface|record|enum)\s+([A-Za-z_]\w*)",
            content,
        )
        if not public_type or Path(path).stem == public_type.group(1):
            continue
        renamed = path.rsplit("/", 1)[0] + "/" + public_type.group(1) + ".java"
        if renamed not in output:
            output[renamed] = content
            del output[path]


_SPRING_BOOT3_JAVAX_PACKAGES = {
    "javax.annotation": "jakarta.annotation",
    "javax.persistence": "jakarta.persistence",
    "javax.servlet": "jakarta.servlet",
    "javax.transaction": "jakarta.transaction",
    "javax.validation": "jakarta.validation",
    "javax.ws.rs": "jakarta.ws.rs",
}


def _migrate_spring_boot3_javax_imports(output: Dict[str, str]) -> None:
    """Normalize Java EE imports that were renamed for Spring Boot 3."""
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        for legacy, jakarta in _SPRING_BOOT3_JAVAX_PACKAGES.items():
            content = re.sub(
                rf"(?m)^(\s*import\s+){re.escape(legacy)}(?=[.;])",
                rf"\1{jakarta}",
                content,
            )
        content = content.replace(
            "jakarta.validation.DecimalMin",
            "jakarta.validation.constraints.DecimalMin",
        )
        output[path] = content


# Function: _reconcile_java_type_imports
def _java_source_module(path: str) -> str:
    """Return the Maven source-root owner for a generated Java path."""
    normalized = path.replace("\\", "/")
    marker = "/src/"
    return normalized.split(marker, 1)[0] if marker in normalized else ""


def _reconcile_java_type_imports(
    output: Dict[str, str], module_scoped: bool = False,
) -> None:
    """Align project-local imports with the package that actually owns each type."""
    owners: Dict[tuple[str, str], set[str]] = {}
    for path, content in output.items():
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue
        package_match = re.search(r"(?m)^\s*package\s+([^;]+);", content)
        if not package_match:
            continue
        package = package_match.group(1).strip()
        primary_type = Path(path).stem
        for declaration_match in re.finditer(
            r"\b(?:class|interface|record|enum)\s+([A-Za-z_]\w*)",
            content,
        ):
            declaration = declaration_match.group(1)
            prefix = content[:declaration_match.start()]
            brace_depth = prefix.count("{") - prefix.count("}")
            owner = (
                f"{package}.{primary_type}.{declaration}"
                if declaration != primary_type and brace_depth > 0
                else f"{package}.{declaration}"
            )
            scope = _java_source_module(path) if module_scoped else ""
            owners.setdefault((scope, declaration), set()).add(owner)
    unique_owners = {
        key: next(iter(values))
        for key, values in owners.items()
        if len(values) == 1
    }
    for path, content in list(output.items()):
        if not path.casefold().endswith(".java") or not isinstance(content, str):
            continue

        scope = _java_source_module(path) if module_scoped else ""

        def replace_import(match: re.Match) -> str:
            imported = match.group(1)
            simple_name = imported.rsplit(".", 1)[-1]
            owner = unique_owners.get((scope, simple_name))
            if owner and imported.startswith("com.") and owner != imported:
                return f"import {owner};"
            return match.group(0)

        reconciled = re.sub(
            r"\bimport\s+(?!static\s)([A-Za-z_][\w.]*)\s*;",
            replace_import,
            content,
        )
        for (owner_scope, simple_name), owner in unique_owners.items():
            if owner_scope != scope:
                continue
            reconciled = re.sub(
                rf"\bcom(?:\.[A-Za-z_]\w*)+\.{re.escape(simple_name)}\b",
                owner,
                reconciled,
            )
        body = re.sub(
            r"(?m)^\s*(?:package|import)\s+[^;]+;\s*$",
            "",
            reconciled,
        )
        existing_imports = set(re.findall(
            r"\bimport\s+(?!static\s)([A-Za-z_][\w.]*)\s*;", reconciled,
        ))
        current_package_match = re.search(r"(?m)^\s*package\s+([\w.]+)\s*;", reconciled)
        current_package = current_package_match.group(1) if current_package_match else ""
        additions = []
        for (owner_scope, simple_name), owner in unique_owners.items():
            owner_package = owner.rsplit(".", 1)[0]
            if (
                owner_scope == scope
                and owner not in existing_imports
                and owner_package != current_package
                and re.search(rf"\b{re.escape(simple_name)}\b", body)
            ):
                additions.append(f"import {owner};")
        if additions and current_package_match:
            insertion = current_package_match.end()
            reconciled = (
                reconciled[:insertion] + "\n\n"
                + "\n".join(sorted(set(additions)))
                + reconciled[insertion:]
            )

        def remove_unused_import(match: re.Match) -> str:
            simple_name = match.group(1).rsplit(".", 1)[-1]
            return match.group(0) if re.search(rf"\b{re.escape(simple_name)}\b", body) else ""

        output[path] = re.sub(
            r"\bimport\s+(?!static\s)([A-Za-z_][\w.]*)\s*;",
            remove_unused_import,
            reconciled,
        )
        output[path] = _add_known_java_imports(output[path])


_KNOWN_JAVA_SYMBOL_IMPORTS = {
    "BigDecimal": "java.math.BigDecimal",
    "Instant": "java.time.Instant",
    "LocalDate": "java.time.LocalDate",
    "LocalDateTime": "java.time.LocalDateTime",
    "List": "java.util.List",
    "Map": "java.util.Map",
    "Optional": "java.util.Optional",
    "Pageable": "org.springframework.data.domain.Pageable",
    "Set": "java.util.Set",
    "UUID": "java.util.UUID",
    "Base64": "java.util.Base64",
    "Claims": "io.jsonwebtoken.Claims",
    "Jwts": "io.jsonwebtoken.Jwts",
    "EntityNotFoundException": "jakarta.persistence.EntityNotFoundException",
    "RestTemplate": "org.springframework.web.client.RestTemplate",
    "Transactional": "org.springframework.transaction.annotation.Transactional",
    # Logger/LoggerFactory boilerplate appears in nearly every generated
    # service/controller ("private static final Logger logger =
    # LoggerFactory.getLogger(X.class)"), but per-file generation frequently
    # imports only one of the pair — LoggerFactory is the symbol actually
    # invoked, so its omission is the single most common "cannot find
    # symbol: variable LoggerFactory" failure in the real build.
    "Logger": "org.slf4j.Logger",
    "LoggerFactory": "org.slf4j.LoggerFactory",
    "DecimalMin": "jakarta.validation.constraints.DecimalMin",
}


# Function: _add_known_java_imports
def _add_known_java_imports(content: str) -> str:
    """Add narrowly unambiguous framework imports omitted by per-file generation."""
    existing = set(re.findall(r"\bimport\s+([A-Za-z_][\w.]*)\s*;", content))
    declared = set(re.findall(
        r"\b(?:class|interface|record|enum)\s+([A-Za-z_]\w*)",
        content,
    ))
    additions = []
    for symbol, import_name in _KNOWN_JAVA_SYMBOL_IMPORTS.items():
        if (
            symbol not in declared
            and import_name not in existing
            and re.search(rf"\b{re.escape(symbol)}\b", content)
        ):
            additions.append(f"import {import_name};")
    if not additions:
        return content
    package_match = re.search(r"\bpackage\s+[^;]+;", content)
    if not package_match:
        return "\n".join(additions) + "\n" + content
    insertion = package_match.end()
    return content[:insertion] + "\n\n" + "\n".join(additions) + content[insertion:]


# Function: _reconcile_java_frontend_local_assets
def _reconcile_java_frontend_local_assets(output: Dict[str, str]) -> None:
    """Create harmless missing relative stylesheet assets imported by Java SPAs."""
    for path, content in list(output.items()):
        if (
            "/frontend/" not in path
            or not path.endswith((".js", ".jsx", ".ts", ".tsx"))
            or not isinstance(content, str)
        ):
            continue
        parent = path.rsplit("/", 1)[0]
        specifiers = re.findall(
            r"""(?:\bfrom\s*|\bimport\s*\(\s*|\bimport\s+)["'](\.[^"']+)["']""",
            content,
        )
        for specifier in specifiers:
            target = posixpath.normpath(posixpath.join(parent, specifier))
            if target in output:
                continue
            if target.endswith((".css", ".scss", ".sass", ".less")):
                output[target] = "/* Generated stylesheet entry point. */\n"


def _reconcile_java_frontend_exports(output: Dict[str, str]) -> None:
    """Align local default imports with an already-declared named export.

    Vite reports these only during Rollup bundling, after TypeScript has
    completed, so a missing default export otherwise arrives as a synthetic
    project error that the per-file repair loop cannot attach to a source file.
    """
    source_suffixes = (".ts", ".tsx", ".js", ".jsx")
    for consumer_path, consumer in list(output.items()):
        if (
            "/frontend/" not in consumer_path
            or not consumer_path.endswith(source_suffixes)
            or not isinstance(consumer, str)
        ):
            continue
        parent = posixpath.dirname(consumer_path)
        for imported_name, specifier in re.findall(
            r"(?m)^\s*import\s+([A-Za-z_$][\w$]*)\s+from\s+['\"](\.[^'\"]+)['\"]\s*;?",
            consumer,
        ):
            unresolved = posixpath.normpath(posixpath.join(parent, specifier))
            candidates = [unresolved] if unresolved.endswith(source_suffixes) else [
                unresolved + suffix for suffix in source_suffixes
            ] + [
                posixpath.join(unresolved, "index" + suffix) for suffix in source_suffixes
            ]
            target_path = next((path for path in candidates if path in output), "")
            if not target_path or target_path == consumer_path:
                continue
            target = output[target_path]
            if not isinstance(target, str) or re.search(r"\bexport\s+default\b", target):
                continue
            declared_export = re.search(
                rf"\bexport\s+(?:async\s+)?(?:function|class|const|let|var)\s+{re.escape(imported_name)}\b",
                target,
            )
            listed_export = re.search(
                rf"\bexport\s*\{{[^}}]*\b{re.escape(imported_name)}\b[^}}]*\}}",
                target,
            )
            if declared_export or listed_export:
                output[target_path] = target.rstrip() + f"\n\nexport default {imported_name};\n"


# Function: _dotnet_backend_dockerfile
def _dotnet_backend_dockerfile(project_name: str, tfm: str) -> str:
    """Deterministic multi-stage .NET Dockerfile. An LLM-generated one drifted
    from the actual port everywhere else agreed on (compose/k8s use 8080) and
    has no reliable way to know the real .csproj filename in advance — this
    generator shares _dotnet_tfm with _backend_manifest_files so the SDK/
    runtime image tags can never disagree with the csproj's TargetFramework."""
    dotnet_version = tfm.removeprefix("net")
    return textwrap.dedent(f"""\
        FROM mcr.microsoft.com/dotnet/sdk:{dotnet_version} AS build
        WORKDIR /src
        COPY *.csproj ./
        RUN dotnet restore
        COPY . .
        RUN dotnet publish -c Release -o /app

        FROM mcr.microsoft.com/dotnet/aspnet:{dotnet_version} AS runtime
        WORKDIR /app
        COPY --from=build /app .
        ENV ASPNETCORE_URLS=http://+:8080
        EXPOSE 8080
        ENTRYPOINT ["dotnet", "{project_name}.dll"]
    """)


# Function: _angular_frontend_dockerfile
def _angular_frontend_dockerfile() -> str:
    """Deterministic multi-stage Angular Dockerfile — Node 20, `ng build
    --configuration production` (`--prod` was removed in Angular 12), then
    served via nginx (never `ng serve`, a dev server, in a production image).
    The dist path (`/app/dist`, no nested "browser/" folder) matches the
    "@angular-devkit/build-angular:browser" builder + outputPath "dist" set
    in _frontend_scaffold_files's angular.json — the newer "application"
    builder nests output under dist/<project>/browser instead, which would
    silently 404 everything if these two generators ever disagreed."""
    return textwrap.dedent("""\
        FROM node:20-alpine AS build
        WORKDIR /app
        COPY package*.json ./
        RUN npm ci
        COPY . .
        RUN npx ng build --configuration production

        FROM nginx:alpine AS runtime
        COPY --from=build /app/dist /usr/share/nginx/html
        COPY nginx.conf /etc/nginx/conf.d/default.conf
        EXPOSE 80
        CMD ["nginx", "-g", "daemon off;"]
    """)


# Function: _nginx_conf
def _nginx_conf() -> str:
    """Deterministic nginx config with SPA fallback — a missing
    try_files .../index.html rule 404s every deep-linked Angular route."""
    return textwrap.dedent("""\
        server {
            listen       80;
            server_name  localhost;
            root   /usr/share/nginx/html;
            index  index.html;

            location / {
                try_files $uri $uri/ /index.html;
            }
        }
    """)


# Function: _default_frontend_file_list
def _default_frontend_file_list(frontend_tech: str, project_name: str) -> List[str]:
    """Fallback frontend skeleton used only if the LLM planning step fails.
    Nests under "frontend/" — must match _ensure_modular_path's convention
    for the LLM-planned-successfully case, and _k8s_manifests_prompt's/
    _docker_compose_prompt's build-context assumptions ("./frontend")."""
    fw = (frontend_tech or "").lower()
    if "angular" in fw:
        return [
            "frontend/src/app/app.module.ts",
            "frontend/src/app/app-routing.module.ts",
            "frontend/src/app/core/auth/auth.service.ts",
            "frontend/src/app/core/auth/auth.guard.ts",
            "frontend/src/app/core/api/api.service.ts",
            "frontend/src/environments/environment.ts",
            "frontend/angular.json",
            "frontend/package.json",
            "frontend/Dockerfile",
        ]
    if "vue" in fw:
        return [
            "frontend/src/App.vue",
            "frontend/src/auth/auth.ts",
            "frontend/src/api/client.ts",
            "frontend/package.json",
            "frontend/Dockerfile",
        ]
    return [  # React / default SPA
        "frontend/src/App.tsx",
        "frontend/src/auth/AuthProvider.tsx",
        "frontend/src/api/client.ts",
        "frontend/package.json",
        "frontend/Dockerfile",
    ]


# Function: _docker_compose_java
def _docker_compose_java(root_ns: str, domains: List[str]) -> str:
    services = {"postgres": textwrap.dedent("""\
      postgres:
        image: postgres:16
        environment:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: changeme
        ports: ["5432:5432"]
        volumes: [postgres_data:/var/lib/postgresql/data]""")}
    for i, d in enumerate(domains):
        port = 8080 + i
        services[f"{d.lower()}-service"] = textwrap.dedent(f"""\
      {d.lower()}-service:
        build: ./services/{d.lower()}-service
        ports: ["{port}:{port}"]
        environment:
          DB_USER: postgres
          DB_PASSWORD: changeme
        depends_on: [postgres]""")
    svc_block = "\n".join(services.values())
    return f"version: '3.9'\nservices:\n{svc_block}\nvolumes:\n  postgres_data:\n"


# Function: _k8s_manifests
def _k8s_manifests(root_ns: str, domains: List[str], lang: str) -> Dict[str, str]:
    """Deterministic Kubernetes manifests for the folder-analysis pipeline's
    per-domain microservice topology — one Deployment/Service per domain plus
    a shared gateway, routed entirely through the gateway."""
    ns = root_ns.lower()
    services = [f"{d.lower()}-service" for d in domains]
    if lang == "csharp":
        # Only C# gets a real deployable ApiGateway (Program.cs + csproj) in
        # this pipeline — other languages' "gateway" is config-only.
        services = ["gateway"] + services
    entry_svc = "gateway" if lang == "csharp" else (services[0] if services else "app")
    return _k8s_manifests_core(ns, services, [("/", entry_svc)])


# Function: _k8s_manifests_prompt
def _k8s_manifests_prompt(project_name: str, has_backend: bool, has_frontend: bool) -> Dict[str, str]:
    """Deterministic Kubernetes manifests for the prompt-driven pipeline's
    two-tier topology (backend API and/or frontend SPA) — "/api" routes to
    the backend, everything else to the frontend, when both are present.
    This is the one thing the LLM cannot be trusted to keep consistent across
    the Deployment/Service/Ingress/ConfigMap/Secret files it would otherwise
    generate independently of each other (see _contract_digest's docstring;
    infra manifests aren't code files an interface can pin down)."""
    ns = re.sub(r"[^a-z0-9-]", "-", project_name.lower()).strip("-") or "app"
    services = [s for s, present in (("backend", has_backend), ("frontend", has_frontend)) if present]
    if has_backend and has_frontend:
        routes = [("/api", "backend"), ("/", "frontend")]
    elif has_backend:
        routes = [("/", "backend")]
    else:
        routes = [("/", "frontend")]
    return _k8s_manifests_core(ns, services, routes)


# Function: _docker_compose_prompt
def _docker_compose_prompt(project_name: str, has_backend: bool, has_frontend: bool, lang: str) -> str:
    """Deterministic docker-compose.yml for the prompt-driven pipeline's
    two-tier topology, placed at the project root with build contexts that
    actually match where _ensure_modular_path puts things (backend at root,
    frontend under "frontend/") — an LLM-generated compose file has no way
    to know that layout in advance, and got it wrong in practice (found
    inside frontend/ using "./backend" and "./frontend" contexts, which only
    resolve from the repo root)."""
    services: Dict[str, dict] = {}
    if has_backend:
        services["backend"] = {
            "build": "./backend",
            "ports": ["8080:8080"],
            "environment": {
                "ASPNETCORE_ENVIRONMENT": "Development",
                "ASPNETCORE_URLS": "http://+:8080",
            } if lang == "csharp" else {},
            "depends_on": ["db"] if lang == "csharp" else [],
        }
    if has_frontend:
        services["frontend"] = {
            "build": "./frontend",
            "ports": ["4200:80"],
            "depends_on": ["backend"] if has_backend else [],
        }
    if lang == "csharp":
        services["db"] = {
            "image": "mcr.microsoft.com/mssql/server:2022-latest",
            "environment": {"ACCEPT_EULA": "Y", "SA_PASSWORD": "YourStrong!Passw0rd"},
            "ports": ["1433:1433"],
        }
    import yaml as _yaml  # type: ignore
    try:
        return _yaml.dump({"version": "3.9", "services": services}, default_flow_style=False, sort_keys=False)
    except ImportError:
        import json as _json
        return "# yaml module not installed — raw JSON:\n" + _json.dumps(
            {"version": "3.9", "services": services}, indent=2)


# Function: _k8s_manifests_core
def _k8s_manifests_core(ns: str, services: List[str], ingress_routes: List[tuple]) -> Dict[str, str]:
    """Shared manifest builder. `ingress_routes` is an ordered list of
    (path, service_name) pairs — more specific paths (e.g. "/api") must come
    before "/" since Kubernetes Ingress matches paths in list order.
    Not LLM-dependent — these are boilerplate that must always be present and
    correct, not something worth risking on model output."""
    import yaml as _yaml  # type: ignore

    # Function: _dump
    def _dump(docs: List[dict]) -> str:
        try:
            return _yaml.dump_all(docs, default_flow_style=False, sort_keys=False)
        except ImportError:
            import json as _json
            return "# yaml module not installed — raw JSON documents:\n" + "\n---\n".join(
                _json.dumps(d, indent=2) for d in docs
            )

    deployments, cluster_services = [], []
    for svc in services:
        container_port = 8080 if svc == "backend" or svc.endswith("-backend") else 80
        probe_path = "/health" if container_port == 8080 else "/"
        deployments.append({
            "apiVersion": "apps/v1", "kind": "Deployment",
            "metadata": {"name": svc, "namespace": ns, "labels": {"app": svc}},
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": svc}},
                "template": {
                    "metadata": {"labels": {"app": svc}},
                    "spec": {
                        "containers": [{
                            "name": svc,
                            # Placeholder — replace with your ACR/registry image before deploying.
                            "image": f"<ACR_NAME>.azurecr.io/{ns}/{svc}:v1",
                            "ports": [{"containerPort": container_port}],
                            "envFrom": [
                                {"configMapRef": {"name": f"{ns}-config"}},
                                {"secretRef": {"name": f"{ns}-secrets"}},
                            ],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits":   {"cpu": "500m", "memory": "512Mi"},
                            },
                            "readinessProbe": {
                                "httpGet": {"path": probe_path, "port": container_port},
                                "initialDelaySeconds": 10, "periodSeconds": 10,
                            },
                            "livenessProbe": {
                                "httpGet": {"path": probe_path, "port": container_port},
                                "initialDelaySeconds": 20, "periodSeconds": 20,
                            },
                        }],
                    },
                },
            },
        })
        cluster_services.append({
            "apiVersion": "v1", "kind": "Service",
            "metadata": {"name": svc, "namespace": ns},
            "spec": {
                "selector": {"app": svc},
                "ports": [{"port": 80, "targetPort": container_port}],
                "type": "ClusterIP",
            },
        })

    ingress = {
        "apiVersion": "networking.k8s.io/v1", "kind": "Ingress",
        "metadata": {
            "name": f"{ns}-ingress", "namespace": ns,
            "annotations": {"kubernetes.io/ingress.class": "azure/application-gateway"},
        },
        "spec": {
            "tls": [{
                "hosts": [f"{ns}.example.com"],
                "secretName": f"{ns}-tls",
            }],
            "rules": [{
                "host": f"{ns}.example.com",
                "http": {
                    "paths": [
                        {
                            "path": path, "pathType": "Prefix",
                            "backend": {"service": {"name": svc, "port": {"number": 80}}},
                        }
                        for path, svc in ingress_routes
                    ],
                },
            }],
        },
    }
    configmap = {
        "apiVersion": "v1", "kind": "ConfigMap",
        "metadata": {"name": f"{ns}-config", "namespace": ns},
        "data": {"ASPNETCORE_ENVIRONMENT": "Production", "ASPNETCORE_URLS": "http://+:8080"},
    }
    secret_example = {
        "apiVersion": "v1", "kind": "Secret",
        "metadata": {"name": f"{ns}-secrets", "namespace": ns},
        "type": "Opaque",
        "stringData": {
            "ConnectionStrings__DefaultConnection": "<SET-VIA-AZURE-KEY-VAULT-OR-CI-CD-SECRET>",
            "AzureAd__ClientSecret": "<SET-VIA-AZURE-KEY-VAULT-OR-CI-CD-SECRET>",
        },
    }

    return {
        "k8s/deployment.yaml": _dump(deployments),
        "k8s/service.yaml": _dump(cluster_services),
        "k8s/ingress.yaml": _dump([ingress]),
        "k8s/configmap.yaml": _dump([configmap]),
        "k8s/secret.example.yaml": (
            "# Copy to secret.yaml, fill in real values, and apply with kubectl.\n"
            "# NEVER commit secret.yaml (only this .example file) — see README for the\n"
            "# recommended Azure Key Vault + CSI driver setup for AKS.\n"
        ) + _dump([secret_example]),
    }


# Function: _docker_compose
def _docker_compose(root_ns: str, domains: List[str]) -> str:
    services = {"gateway": {
        "build": "./ApiGateway",
        "ports": ["5000:80"],
        "depends_on": [f"{d.lower()}-service" for d in domains],
    }}
    port = 7001
    for d in domains:
        services[f"{d.lower()}-service"] = {
            "build": f"./Services/{d.capitalize()}Service",
            "expose": [str(port)],
            "environment": {
                "ASPNETCORE_URLS": f"http://+:{port}",
                "ConnectionStrings__DefaultConnection":
                    f"Server=sqlserver;Database=Modernized_{d.capitalize()}DB;Trusted_Connection=True;",
            },
            "depends_on": ["sqlserver"],
        }
        port += 1

    services["sqlserver"] = {
        "image": "mcr.microsoft.com/mssql/server:2022-latest",
        "environment": {
            "ACCEPT_EULA": "Y",
            "SA_PASSWORD": "YourStrong!Passw0rd",
        },
        "ports": ["1433:1433"],
    }

    import yaml as _yaml  # type: ignore
    try:
        return _yaml.dump({"version": "3.9", "services": services}, default_flow_style=False)
    except ImportError:
        import json as _json
        return "# yaml module not installed — raw JSON:\n" + _json.dumps(
            {"version": "3.9", "services": services}, indent=2)


# ─── Go build files ─────────────────────────────────────────────────────────
# Function: _go_mod
def _go_mod(root_ns: str, backend_tech: str) -> str:
    """Real go.mod for the generated project. Dependency selected by a
    substring match on backend_tech ("Go + Gin" -> Gin, else plain net/http),
    same signal TARGET_STACKS' go_rest/go_gin_react entries already carry."""
    module = f"github.com/{root_ns.lower()}/modernizedapp"
    deps = ['\tgithub.com/jackc/pgx/v5 v5.6.0']
    if "gin" in (backend_tech or "").lower():
        deps.append("\tgithub.com/gin-gonic/gin v1.10.0")
    if "fiber" in (backend_tech or "").lower():
        deps.append("\tgithub.com/gofiber/fiber/v2 v2.52.5")
    deps_block = "\n".join(deps)
    return f"module {module}\n\ngo 1.22\n\nrequire (\n{deps_block}\n)\n"


# Function: _docker_compose_go
def _docker_compose_go(root_ns: str, domains: List[str]) -> str:
    services = {"postgres": textwrap.dedent("""\
      postgres:
        image: postgres:16
        environment:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: changeme
        ports: ["5432:5432"]
        volumes: [postgres_data:/var/lib/postgresql/data]""")}
    for i, d in enumerate(domains):
        port = 8080 + i
        services[f"{d.lower()}-service"] = textwrap.dedent(f"""\
      {d.lower()}-service:
        build: ./services/{d.lower()}-service
        ports: ["{port}:{port}"]
        environment:
          DATABASE_URL: postgres://postgres:changeme@postgres:5432/{root_ns.lower()}?sslmode=disable
        depends_on: [postgres]""")
    svc_block = "\n".join(services.values())
    return f"version: '3.9'\nservices:\n{svc_block}\nvolumes:\n  postgres_data:\n"
