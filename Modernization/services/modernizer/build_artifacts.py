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
                "@types/node": "20.11.30",
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
                "lib": ["ES2022", "dom"], "baseUrl": ".",
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
    return {}  # Java's pom.xml is left to the LLM — not the reported failure mode


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
