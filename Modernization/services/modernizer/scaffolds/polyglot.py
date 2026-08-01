# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Deterministic, offline-safe project scaffolds for guided target languages.
# Date: 2026-04-01
# ---------------------------------------------------------------------------
"""Deterministic, offline-safe project scaffolds for guided target languages.

These are deliberately small vertical slices: an executable entry point, a
health endpoint or equivalent, dependency/build metadata, and a smoke test.
The LLM may replace domain files, but a generation job never falls back to a
different programming language when the model is unavailable.
"""
from __future__ import annotations

import json
import re
from typing import Dict


# Function: _slug
def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "app"


# Function: _spa_frontend
def _spa_frontend(framework: str, app: str, name: str) -> Dict[str, str]:
    """Small strict TypeScript SPA used by backend+frontend target presets."""
    is_vue = framework == "vue"
    dependency = (
        '"vue":"^3.5.0"' if is_vue
        else '"react":"^18.3.1","react-dom":"^18.3.1"'
    )
    dev_types = (
        "" if is_vue
        else ',"@types/react":"^18.3.0","@types/react-dom":"^18.3.0"'
    )
    extension = "ts" if is_vue else "tsx"
    source = (
        f'import {{ createApp }} from "vue";\n'
        f'createApp({{template:"<main><h1>{name}</h1><p>Service ready</p></main>"}}).mount("#app");\n'
        if is_vue else
        f'import React from "react";\nimport {{createRoot}} from "react-dom/client";\n'
        f'createRoot(document.getElementById("root")!).render(<main><h1>{name}</h1><p>Service ready</p></main>);\n'
    )
    return {
        "ModernizedApp/frontend/package.json": (
            '{"name":"' + app + '-frontend","private":true,'
            '"scripts":{"build":"tsc --noEmit"},'
            f'"dependencies":{{{dependency}}},'
            '"devDependencies":{"typescript":"^5.6.0"'
            + dev_types + '}}\n'
        ),
        "ModernizedApp/frontend/tsconfig.json": (
            '{"compilerOptions":{"target":"ES2022","module":"ESNext",'
            '"moduleResolution":"Bundler","strict":true,"jsx":"react-jsx",'
            '"lib":["ES2022","DOM"],"skipLibCheck":true},'
            f'"include":["src/**/*.{extension}"]}}\n'
        ),
        f"ModernizedApp/frontend/src/main.{extension}": source,
    }


# Function: generate_polyglot_project
def generate_polyglot_project(language: str, root_ns: str, domain: str, target: dict) -> Dict[str, str]:
    lang, app, name = language.casefold(), _slug(root_ns), domain.capitalize()
    base = f"ModernizedApp/services/{_slug(domain)}-service"
    stack = f"{target.get('name', '')} {target.get('backend_tech', '')} {target.get('frontend_tech', '')}".casefold()
    if lang == "c":
        return {
            f"{base}/CMakeLists.txt": 'cmake_minimum_required(VERSION 3.20)\nproject(modernized C)\nset(CMAKE_C_STANDARD 17)\nadd_executable(app src/main.c src/health.c)\nenable_testing()\nadd_test(NAME smoke COMMAND app --health)\n',
            f"{base}/src/health.c": 'const char *health_status(void) { return "ok"; }\n',
            f"{base}/src/main.c": '#include <stdio.h>\n#include <string.h>\nconst char *health_status(void);\nint main(int argc,char **argv){if(argc==2&&strcmp(argv[1],"--health")==0){puts(health_status());return 0;}return 0;}\n',
        }
    if lang == "cpp":
        return {
            f"{base}/CMakeLists.txt": 'cmake_minimum_required(VERSION 3.20)\nproject(modernized LANGUAGES CXX)\nset(CMAKE_CXX_STANDARD 23)\nadd_executable(app src/main.cpp src/health.cpp)\nenable_testing()\nadd_test(NAME smoke COMMAND app --health)\n',
            f"{base}/src/health.cpp": '#include <string_view>\nstd::string_view health_status() noexcept { return "ok"; }\n',
            f"{base}/src/main.cpp": '#include <iostream>\n#include <string_view>\nstd::string_view health_status() noexcept;\nint main(int argc,char **argv){if(argc==2&&std::string_view(argv[1])=="--health")std::cout<<health_status()<<"\\n";return 0;}\n',
        }
    if lang == "cobol":
        program = re.sub(r"[^A-Z0-9-]", "-", f"{app}-{_slug(domain)}".upper())[:28]
        return {
            f"{base}/src/{program}.cob": f"""       IDENTIFICATION DIVISION.
       PROGRAM-ID. {program}.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-STATUS PIC X(02) VALUE "OK".
       PROCEDURE DIVISION.
           DISPLAY "{name} SERVICE " WS-STATUS
           STOP RUN.
""",
            f"{base}/db/schema.sql": "CREATE TABLE HEALTH_STATUS (SERVICE_NAME VARCHAR(128) NOT NULL, STATUS CHAR(2) NOT NULL);\n",
            f"{base}/Makefile": f"build:\n\tcobc -x -std=ibm -o {app}.exe src/{program}.cob\n\ntest: build\n\t./{app}.exe\n",
        }
    if lang == "ruby":
        module = "".join(part.capitalize() for part in app.split("-")) or "Modernized"
        files = {
            f"{base}/Gemfile": "source 'https://rubygems.org'\ngem 'rails', '~> 7.2.0'\ngem 'pg', '~> 1.5'\ngem 'puma', '>= 6.4'\ngem 'rspec-rails', '~> 7.0', group: [:development, :test]\n",
            f"{base}/config/application.rb": f"require 'rails/all'\nBundler.require(*Rails.groups)\nmodule {module}\n  class Application < Rails::Application\n    config.load_defaults 7.2\n    config.api_only = true\n  end\nend\n",
            f"{base}/config/environment.rb": "require_relative 'application'\nRails.application.initialize!\n",
            f"{base}/config/routes.rb": "Rails.application.routes.draw do\n  get '/health', to: 'health#show'\nend\n",
            f"{base}/app/controllers/application_controller.rb": "class ApplicationController < ActionController::API\nend\n",
            f"{base}/app/controllers/health_controller.rb": "class HealthController < ApplicationController\n  def show\n    render json: { status: 'ok' }\n  end\nend\n",
            f"{base}/Rakefile": "require_relative 'config/application'\nRails.application.load_tasks\n",
        }
        if "react" in stack:
            files.update(_spa_frontend("react", app, name))
        return files
    if lang == "typescript" and any(token in stack for token in ("express", "graphql", "node.js")):
        is_graphql = "graphql" in stack
        db_target = str(target.get("db_target") or "").casefold()
        dependencies = {
            "dotenv": "^16.4.5",
            "graphql": "^16.9.0",
            "@apollo/server": "^4.11.0",
        } if is_graphql else {
            "dotenv": "^16.4.5", "express": "^4.21.0", "helmet": "^8.0.0",
        }
        if db_target == "mongodb":
            dependencies["mongoose"] = "^8.8.0"
        elif db_target:
            dependencies["pg"] = "^8.13.0"
        dev_dependencies = {
            "typescript": "^5.6.0", "@types/node": "^22.0.0",
        }
        if not is_graphql:
            dev_dependencies["@types/express"] = "^5.0.0"
        package = {
            "name": f"{app}-{_slug(domain)}-service", "private": True,
            "scripts": {"build": "tsc -p tsconfig.json", "start": "node dist/server.js"},
            "dependencies": dependencies, "devDependencies": dev_dependencies,
        }
        source = (
            "import 'dotenv/config';\nimport { ApolloServer } from '@apollo/server';\n"
            "import { startStandaloneServer } from '@apollo/server/standalone';\n"
            "const typeDefs=`type Query { health: String! }`;\n"
            "const resolvers={Query:{health:()=>\"ok\"}};\n"
            "const server=new ApolloServer({typeDefs,resolvers});\n"
            "void startStandaloneServer(server,{listen:{port:Number(process.env.PORT ?? 3000)}});\n"
            if is_graphql else
            "import 'dotenv/config';\nimport express from 'express';\nimport helmet from 'helmet';\n"
            "const app=express(); app.use(helmet()); app.use(express.json());\n"
            "app.get('/health',(_request,response)=>response.json({status:'ok'}));\n"
            "app.listen(Number(process.env.PORT ?? 3000));\n"
        )
        files = {
            f"{base}/package.json": json.dumps(package, indent=2) + "\n",
            f"{base}/tsconfig.json": json.dumps({"compilerOptions": {
                "target": "ES2022", "module": "NodeNext", "moduleResolution": "NodeNext",
                "strict": True, "esModuleInterop": True, "outDir": "dist",
                "skipLibCheck": True,
            }, "include": ["src/**/*.ts"]}, indent=2) + "\n",
            f"{base}/src/server.ts": source,
            f"{base}/.env.example": "PORT=3000\nDATABASE_URL=\n",
        }
        if "react" in stack:
            files.update(_spa_frontend("react", app, name))
        elif "vue" in stack:
            files.update(_spa_frontend("vue", app, name))
        return files
    if lang == "typescript" and "nestjs" in stack:
        files = {
            f"{base}/package.json": '{"name":"' + app + '-api","private":true,"scripts":{"build":"nest build","test":"jest --passWithNoTests"},"dependencies":{"@nestjs/common":"^11.1.28","@nestjs/core":"^11.1.28","reflect-metadata":"^0.2.2","rxjs":"^7.8.2"},"devDependencies":{"@nestjs/cli":"^11.0.0","@nestjs/testing":"^11.1.28","@types/node":"^24.0.0","jest":"^30.0.0","ts-jest":"^29.4.0","typescript":"^5.9.0"}}\n',
            f"{base}/nest-cli.json": '{"collection":"@nestjs/schematics","sourceRoot":"src"}\n',
            f"{base}/tsconfig.json": '{"compilerOptions":{"module":"commonjs","target":"ES2022","strict":true,"experimentalDecorators":true,"emitDecoratorMetadata":true,"outDir":"dist"},"include":["src/**/*.ts"]}\n',
            f"{base}/src/main.ts": "import 'reflect-metadata';\nimport { NestFactory } from '@nestjs/core';\nimport { Module, Controller, Get } from '@nestjs/common';\n@Controller() class HealthController { @Get('health') health(){ return {status:'ok'}; } }\n@Module({controllers:[HealthController]}) class AppModule {}\nNestFactory.create(AppModule).then(app=>app.listen(Number(process.env.PORT ?? 3000)));\n",
        }
        if "react native" in stack:
            files.update({
                "ModernizedApp/mobile/package.json": '{"name":"' + app + '-mobile","private":true,"scripts":{"build":"tsc --noEmit","test":"jest --passWithNoTests"},"dependencies":{"react":"19.2.8","react-native":"0.86.0"},"devDependencies":{"@react-native/babel-preset":"0.86.0","@react-native/metro-config":"0.86.0","@types/react":"^19.2.0","typescript":"^5.9.0","jest":"^30.0.0"}}\n',
                "ModernizedApp/mobile/tsconfig.json": '{"compilerOptions":{"target":"ES2022","module":"ESNext","moduleResolution":"Bundler","jsx":"react-jsx","strict":true,"noEmit":true,"esModuleInterop":true,"allowSyntheticDefaultImports":true,"skipLibCheck":true,"lib":["ES2022"],"types":["react","react-native"]},"include":["App.tsx","src/**/*.ts","src/**/*.tsx"]}\n',
                "ModernizedApp/mobile/app.json": '{"name":"ModernizedMobile","displayName":"Modernized Mobile"}\n',
                "ModernizedApp/mobile/index.js": "import {AppRegistry} from 'react-native';\nimport App from './App';\nimport {name as appName} from './app.json';\nAppRegistry.registerComponent(appName,()=>App);\n",
                "ModernizedApp/mobile/App.tsx": "import React from 'react';\nimport {SafeAreaView,Text} from 'react-native';\nexport default function App(){return <SafeAreaView><Text>Modernized application</Text></SafeAreaView>;}\n",
                "ModernizedApp/mobile/babel.config.js": "module.exports={presets:['module:@react-native/babel-preset']};\n",
                "ModernizedApp/mobile/metro.config.js": "const {getDefaultConfig,mergeConfig}=require('@react-native/metro-config');\nmodule.exports=mergeConfig(getDefaultConfig(__dirname),{});\n",
            })
        return files
    if lang == "javascript" and any(token in stack for token in ("node.js", "node ", "express")):
        dependencies = {"dotenv": "^16.4.5", "express": "^4.21.0", "helmet": "^8.0.0"}
        db_target = str(target.get("db_target") or "").casefold()
        if db_target == "mongodb":
            dependencies["mongoose"] = "^8.8.0"
        elif db_target:
            dependencies["pg"] = "^8.13.0"
        return {
            f"{base}/package.json": json.dumps({
                "name": f"{app}-{_slug(domain)}-service", "private": True, "type": "module",
                "scripts": {"build": "node --check src/server.js", "start": "node src/server.js"},
                "dependencies": dependencies,
            }, indent=2) + "\n",
            f"{base}/src/server.js": (
                "import 'dotenv/config';\nimport express from 'express';\nimport helmet from 'helmet';\n"
                "const app=express(); app.use(helmet()); app.use(express.json());\n"
                "app.get('/health',(_request,response)=>response.json({status:'ok'}));\n"
                "app.listen(Number(process.env.PORT ?? 3000));\n"
            ),
            f"{base}/.env.example": "PORT=3000\nDATABASE_URL=\n",
        }
    if lang == "python" and "django" in stack:
        package = app.replace("-", "_")
        return {
            f"{base}/requirements.txt": (
                "Django==5.1.3\ndjangorestframework==3.15.2\n"
                "dj-database-url==2.2.0\npsycopg[binary]==3.2.3\npytest-django==4.9.0\n"
            ),
            f"{base}/manage.py": (
                "#!/usr/bin/env python\nimport os\nfrom django.core.management import execute_from_command_line\n"
                f"os.environ.setdefault('DJANGO_SETTINGS_MODULE','{package}.settings')\n"
                "if __name__=='__main__': execute_from_command_line()\n"
            ),
            f"{base}/{package}/__init__.py": "",
            f"{base}/{package}/settings.py": (
                "import os\nfrom pathlib import Path\nimport dj_database_url\n"
                "BASE_DIR=Path(__file__).resolve().parent.parent\nSECRET_KEY=os.environ['SECRET_KEY']\n"
                "DEBUG=os.getenv('DEBUG','false').lower()=='true'\nALLOWED_HOSTS=os.getenv('ALLOWED_HOSTS','localhost').split(',')\n"
                f"ROOT_URLCONF='{package}.urls'\nINSTALLED_APPS=['django.contrib.contenttypes','django.contrib.auth','rest_framework']\n"
                "MIDDLEWARE=[]\nDATABASES={'default':dj_database_url.config(env='DATABASE_URL')}\nDEFAULT_AUTO_FIELD='django.db.models.BigAutoField'\n"
            ),
            f"{base}/{package}/urls.py": (
                "from django.http import JsonResponse\nfrom django.urls import path\n"
                "def health(_request): return JsonResponse({'status':'ok'})\n"
                "urlpatterns=[path('health',health)]\n"
            ),
            f"{base}/pytest.ini": f"[pytest]\nDJANGO_SETTINGS_MODULE={package}.settings\npython_files=test_*.py\n",
            f"{base}/tests/test_health.py": (
                "def test_health(client):\n    response=client.get('/health')\n    assert response.status_code==200\n"
            ),
        }
    if lang == "typescript" and "next.js" in stack:
        return {
            "ModernizedApp/package.json": '{"name":"' + app + '","private":true,"scripts":{"build":"next build","test":"tsc --noEmit"},"dependencies":{"next":"^14.2.0","react":"^18.3.1","react-dom":"^18.3.1","@prisma/client":"^5.20.0"},"devDependencies":{"@types/node":"^20.16.0","@types/react":"^18.3.0","prisma":"^5.20.0","typescript":"^5.6.0"}}\n',
            "ModernizedApp/tsconfig.json": '{"compilerOptions":{"target":"ES2022","lib":["dom","esnext"],"strict":true,"noEmit":true,"module":"esnext","moduleResolution":"bundler","jsx":"preserve","plugins":[{"name":"next"}]},"include":["next-env.d.ts","**/*.ts","**/*.tsx"]}\n',
            "ModernizedApp/next-env.d.ts": '/// <reference types="next" />\n/// <reference types="next/image-types/global" />\n',
            f"ModernizedApp/app/api/{_slug(domain)}/route.ts": "import { NextResponse } from 'next/server';\nexport async function GET(){ return NextResponse.json({items:[]}); }\n",
            "ModernizedApp/app/page.tsx": "export default function Page(){return <main><h1>Modernized application</h1></main>}\n",
            "ModernizedApp/app/layout.tsx": "export default function Layout({children}:{children:React.ReactNode}){return <html><body>{children}</body></html>}\n",
            "ModernizedApp/prisma/schema.prisma": 'generator client { provider = "prisma-client-js" }\ndatasource db { provider = "postgresql" url = env("DATABASE_URL") }\n',
        }
    if lang == "kotlin":
        framework = "ktor" if "ktor" in stack else "spring"
        dependency = (
            'implementation("io.ktor:ktor-server-netty:2.3.12")\n    implementation("io.ktor:ktor-server-core:2.3.12")'
            if framework == "ktor" else
            'implementation("org.springframework.boot:spring-boot-starter-web:3.3.4")'
        )
        plugins = (
            'kotlin("jvm") version "2.0.21"\n    application'
            if framework == "ktor" else
            'kotlin("jvm") version "2.0.21"\n    kotlin("plugin.spring") version "2.0.21"\n    id("org.springframework.boot") version "3.3.4"\n    id("io.spring.dependency-management") version "1.1.6"'
        )
        source = (
            'import io.ktor.server.application.*\nimport io.ktor.server.engine.*\nimport io.ktor.server.netty.*\nimport io.ktor.server.response.*\nimport io.ktor.server.routing.*\nfun main() { embeddedServer(Netty, port=8080) { routing { get("/health") { call.respondText("ok") } } }.start(wait=true) }\n'
            if framework == "ktor" else
            'import org.springframework.boot.autoconfigure.SpringBootApplication\nimport org.springframework.boot.runApplication\nimport org.springframework.web.bind.annotation.GetMapping\nimport org.springframework.web.bind.annotation.RestController\n@SpringBootApplication class App\n@RestController class HealthController { @GetMapping("/health") fun health()=mapOf("status" to "ok") }\nfun main(args:Array<String>){runApplication<App>(*args)}\n'
        )
        return {
            f"{base}/settings.gradle.kts": f'rootProject.name = "{app}-{_slug(domain)}"\n',
            f"{base}/build.gradle.kts": f'plugins {{\n    {plugins}\n}}\nrepositories {{ mavenCentral() }}\ndependencies {{\n    {dependency}\n    testImplementation(kotlin("test"))\n}}\napplication {{ mainClass.set("AppKt") }}\ntasks.test {{ useJUnitPlatform() }}\n',
            f"{base}/src/main/kotlin/App.kt": source,
            f"{base}/src/test/kotlin/AppTest.kt": 'import kotlin.test.Test\nimport kotlin.test.assertTrue\nclass AppTest { @Test fun health() = assertTrue(true) }\n',
        }
    if lang == "rust":
        files = {
            f"{base}/Cargo.toml": f'[package]\nname="{app}-{_slug(domain)}"\nversion="1.0.0"\nedition="2021"\n\n[dependencies]\naxum="0.7"\ntokio={{version="1",features=["full"]}}\n',
            f"{base}/src/main.rs": 'use axum::{routing::get,Router};\n#[tokio::main]\nasync fn main(){let app=Router::new().route("/health",get(||async{"ok"}));let listener=tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();axum::serve(listener,app).await.unwrap();}\n',
        }
        if "react" in stack:
            files.update(_spa_frontend("react", app, name))
        return files
    if lang == "php":
        files = {
            f"{base}/composer.json": '{"name":"modernized/app","require":{"php":"^8.2","laravel/framework":"^11.0"},"require-dev":{"phpunit/phpunit":"^11.0"},"autoload":{"psr-4":{"App\\\\":"app/"}},"scripts":{"test":"phpunit"}}\n',
            f"{base}/artisan": '#!/usr/bin/env php\n<?php\nrequire __DIR__."/vendor/autoload.php";\n',
            f"{base}/bootstrap/app.php": '<?php\nuse Illuminate\\Foundation\\Application;\nreturn Application::configure(basePath: dirname(__DIR__))->withRouting(api: __DIR__."/../routes/api.php")->create();\n',
            f"{base}/routes/api.php": '<?php\nuse Illuminate\\Support\\Facades\\Route;\nRoute::get("/health", fn()=>["status"=>"ok","service"=>"' + name + '"]);\n',
            f"{base}/public/index.php": '<?php\n$app=require_once __DIR__."/../bootstrap/app.php";\n$app->handleRequest(Illuminate\\Http\\Request::capture());\n',
            f"{base}/phpunit.xml": '<phpunit bootstrap="vendor/autoload.php"><testsuites><testsuite name="Application"><directory>tests</directory></testsuite></testsuites></phpunit>\n',
            f"{base}/tests/HealthTest.php": '<?php\ndeclare(strict_types=1);\nuse PHPUnit\\Framework\\TestCase;\nfinal class HealthTest extends TestCase { public function testHealth(): void { $this->assertTrue(true); } }\n',
        }
        if "vue" in stack:
            files.update(_spa_frontend("vue", app, name))
        return files
    if lang == "dart":
        if "shelf" in stack or "server" in stack:
            package = app.replace("-", "_")
            return {
                f"{base}/pubspec.yaml": f'name: {package}\nenvironment:\n  sdk: ">=3.12.0 <4.0.0"\ndependencies:\n  shelf: ^1.4.2\n  shelf_router: ^1.1.4\ndev_dependencies:\n  test: ^1.26.0\n  lints: ^6.0.0\n',
                f"{base}/analysis_options.yaml": "include: package:lints/recommended.yaml\nanalyzer:\n  language:\n    strict-casts: true\n    strict-inference: true\n",
                f"{base}/bin/server.dart": "import 'dart:io';\nimport 'package:shelf/shelf.dart';\nimport 'package:shelf/shelf_io.dart' as io;\nimport 'package:shelf_router/shelf_router.dart';\nRouter routes()=>Router()..get('/health',(Request _)=>Response.ok('{\"status\":\"ok\"}',headers:{'content-type':'application/json'}));\nFuture<void> main() async {final server=await io.serve(routes().call,InternetAddress.anyIPv4,8080);stdout.writeln('listening on ${server.port}');}\n",
                f"{base}/test/health_test.dart": "import 'package:test/test.dart';\nimport 'package:shelf/shelf.dart';\nimport '../bin/server.dart';\nvoid main(){test('health',() async {final response=await routes().call(Request('GET',Uri.parse('http://localhost/health')));expect(response.statusCode,200);});}\n",
            }
        return {
            "ModernizedApp/mobile/pubspec.yaml": f'name: {app.replace("-", "_")}\nenvironment:\n  sdk: ">=3.4.0 <4.0.0"\ndependencies:\n  flutter:\n    sdk: flutter\ndev_dependencies:\n  flutter_test:\n    sdk: flutter\nflutter:\n  uses-material-design: true\n',
            "ModernizedApp/mobile/lib/main.dart": "import 'package:flutter/material.dart';\nvoid main()=>runApp(const App());\nclass App extends StatelessWidget{const App({super.key});@override Widget build(BuildContext context)=>const MaterialApp(home:Scaffold(body:Center(child:Text('Modernized application'))));}\n",
            "ModernizedApp/mobile/test/widget_test.dart": "import 'package:flutter_test/flutter_test.dart';\nimport 'package:" + app.replace("-", "_") + "/main.dart';\nvoid main(){testWidgets('renders',(tester) async {await tester.pumpWidget(const App());expect(find.text('Modernized application'),findsOneWidget);});}\n",
            "ModernizedApp/backend/Backend.csproj": '<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net8.0</TargetFramework><Nullable>enable</Nullable><ImplicitUsings>enable</ImplicitUsings></PropertyGroup></Project>\n',
            "ModernizedApp/backend/Program.cs": 'var app=WebApplication.CreateBuilder(args).Build();\napp.MapGet("/health",()=>Results.Ok(new{status="ok"}));\napp.Run();\n',
        }
    if lang == "elixir":
        module = "".join(part.capitalize() for part in app.split("-")) or "Modernized"
        return {
            f"{base}/mix.exs": f'''defmodule {module}.MixProject do
  use Mix.Project
  def project, do: [app: :{app.replace("-", "_")}, version: "1.0.0", elixir: "~> 1.20", start_permanent: Mix.env() == :prod, deps: deps()]
  def application, do: [extra_applications: [:logger], mod: {{{module}.Application, []}}]
  defp deps, do: [{{:phoenix, "~> 1.8.9"}}, {{:plug_cowboy, "~> 2.9"}}]
end
''',
            f"{base}/lib/application.ex": f"defmodule {module}.Application do\n  use Application\n  def start(_type,_args), do: Supervisor.start_link([{{Plug.Cowboy, scheme: :http, plug: {module}.Router, options: [port: 4000]}}], strategy: :one_for_one, name: {module}.Supervisor)\nend\n",
            f"{base}/lib/router.ex": f"defmodule {module}.Router do\n  use Phoenix.Router\n  pipeline :api do\n    plug :accepts, [\"json\"]\n  end\n  scope \"/\" do\n    pipe_through :api\n    get \"/health\", {module}.HealthController, :show\n  end\nend\n",
            f"{base}/lib/health_controller.ex": f"defmodule {module}.HealthController do\n  use Phoenix.Controller, formats: [:json]\n  def show(conn,_params), do: json(conn,%{{status: \"ok\"}})\nend\n",
            f"{base}/test/test_helper.exs": "ExUnit.start()\n",
            f"{base}/test/health_test.exs": f"defmodule {module}.HealthTest do\n  use ExUnit.Case\n  test \"health payload\", do: assert(%{{status: \"ok\"}}.status == \"ok\")\nend\n",
        }
    if lang == "erlang":
        otp_app = app.replace("-", "_")
        return {
            f"{base}/rebar.config": "{erl_opts, [debug_info, warnings_as_errors]}.\n{eunit_opts, [verbose]}.\n",
            f"{base}/src/{otp_app}.app.src": f"{{application, {otp_app}, [{{description, \"Modernized OTP service\"}},{{vsn,\"1.0.0\"}},{{modules,[]}},{'{'}registered,[]{'}'},{{applications,[kernel,stdlib]}},{{mod,{{{otp_app}_app,[]}}}}]}}.\n",
            f"{base}/src/{otp_app}_app.erl": f"-module({otp_app}_app).\n-behaviour(application).\n-export([start/2,stop/1]).\nstart(_Type,_Args)->{otp_app}_sup:start_link().\nstop(_State)->ok.\n",
            f"{base}/src/{otp_app}_sup.erl": f"-module({otp_app}_sup).\n-behaviour(supervisor).\n-export([start_link/0,init/1]).\nstart_link()->supervisor:start_link({{local,?MODULE}},?MODULE,[]).\ninit([])->{{ok,{{{{one_for_one,1,5}},[]}}}}.\n",
            f"{base}/src/health_service.erl": "-module(health_service).\n-export([health/0]).\n-spec health() -> map().\nhealth()->#{status => ok}.\n",
            f"{base}/test/health_service_tests.erl": "-module(health_service_tests).\n-include_lib(\"eunit/include/eunit.hrl\").\nhealth_test()->?assertEqual(#{status => ok},health_service:health()).\n",
        }
    if lang == "swift":
        return {
            f"{base}/Package.swift": '// swift-tools-version: 5.10\nimport PackageDescription\nlet package=Package(name:"App",platforms:[.macOS(.v13)],dependencies:[.package(url:"https://github.com/vapor/vapor.git",from:"4.100.0")],targets:[.executableTarget(name:"App",dependencies:[.product(name:"Vapor",package:"vapor")]),.testTarget(name:"AppTests",dependencies:["App"])])\n',
            f"{base}/Sources/App/main.swift": 'import Vapor\nlet app = try await Application.make(.detect())\napp.get("health"){_ in ["status":"ok"]}\ntry await app.execute()\ntry await app.asyncShutdown()\n',
        }
    if lang == "scala":
        return {f"{base}/build.sbt": 'scalaVersion := "2.13.14"\nlazy val root=(project in file(".")).enablePlugins(PlayScala)\nlibraryDependencies += guice\n', f"{base}/project/plugins.sbt": 'addSbtPlugin("org.playframework" % "sbt-plugin" % "3.0.5")\n', f"{base}/conf/routes": 'GET /health controllers.HealthController.health\n', f"{base}/app/controllers/HealthController.scala": 'package controllers\nimport javax.inject._\nimport play.api.mvc._\n@Singleton class HealthController @Inject()(cc:ControllerComponents) extends AbstractController(cc){def health=Action{Ok("""{"status":"ok"}""").as("application/json")}}\n'}
    if lang == "clojure":
        return {
            f"{base}/deps.edn": '{:paths ["src"] :deps {ring/ring-core {:mvn/version "1.12.2"} ring/ring-jetty-adapter {:mvn/version "1.12.2"} metosin/reitit-ring {:mvn/version "0.7.2"}} :aliases {:run {:main-opts ["-m" "app.core"]}}}\n',
            f"{base}/pom.xml": '''<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>modernized</groupId><artifactId>ring-service</artifactId><version>1.0.0</version><repositories><repository><id>clojars</id><url>https://repo.clojars.org/</url></repository></repositories><dependencies><dependency><groupId>org.clojure</groupId><artifactId>clojure</artifactId><version>1.12.2</version></dependency><dependency><groupId>ring</groupId><artifactId>ring-core</artifactId><version>1.12.2</version></dependency><dependency><groupId>ring</groupId><artifactId>ring-jetty-adapter</artifactId><version>1.12.2</version></dependency><dependency><groupId>metosin</groupId><artifactId>reitit-ring</artifactId><version>0.7.2</version></dependency></dependencies><build><sourceDirectory>src</sourceDirectory><plugins><plugin><groupId>com.theoryinpractise</groupId><artifactId>clojure-maven-plugin</artifactId><version>1.9.3</version><extensions>true</extensions><executions><execution><id>compile-clojure</id><phase>compile</phase><goals><goal>compile</goal></goals></execution></executions></plugin></plugins></build></project>
''',
            f"{base}/src/app/core.clj": '(ns app.core (:gen-class) (:require [ring.adapter.jetty :as jetty] [reitit.ring :as ring]))\n(def app (ring/ring-handler (ring/router [["/health" {:get (fn [_] {:status 200 :body "ok"})}]])))\n(defn -main [& _] (jetty/run-jetty app {:port 8080 :join? true}))\n',
        }
    if lang == "shell":
        return {f"{base}/bin/app.sh": f'#!/usr/bin/env bash\nset -euo pipefail\nprintf "%s\\n" "{name} automation ready"\n', f"{base}/tests/smoke.sh": '#!/usr/bin/env bash\nset -euo pipefail\nbash -n bin/app.sh\n'}
    if lang == "r":
        return {f"{base}/DESCRIPTION": f'Package: {app.replace("-", "")}\nType: Package\nVersion: 1.0.0\nImports: shiny\nSuggests: testthat\n', f"{base}/app.R": f'library(shiny)\nui <- fluidPage(h1("{name} analytics"))\nserver <- function(input, output, session) {{}}\nshinyApp(ui, server)\n', f"{base}/tests/testthat.R": f'library(testthat)\ntest_check("{app.replace("-", "")}")\n'}
    if lang == "julia":
        return {f"{base}/Project.toml": f'name = "{name}Service"\nuuid = "12345678-1234-1234-1234-123456789abc"\nversion = "1.0.0"\n', f"{base}/src/{name}Service.jl": f'module {name}Service\nhealth() = (status="ok", service="{name}")\nend\n'}
    if lang == "haskell":
        package = f"{app}-{_slug(domain)}"
        return {f"{base}/app/Main.hs": '{-# LANGUAGE DataKinds #-}\n{-# LANGUAGE TypeOperators #-}\nimport Servant\nimport Network.Wai.Handler.Warp(run)\ntype API = "health" :> Get \'[JSON] String\nserver :: Server API\nserver = pure "ok"\nmain :: IO ()\nmain = run 8080 (serve (Proxy :: Proxy API) server)\n', f"{base}/stack.yaml": 'resolver: lts-22.26\npackages: [.]\n', f"{base}/package.yaml": f'name: {package}\nversion: 1.0.0\ndependencies: [base, servant-server, warp]\nexecutables:\n  app:\n    main: Main.hs\n    source-dirs: app\n', f"{base}/{package}.cabal": f'cabal-version: 2.4\nname: {package}\nversion: 1.0.0\nexecutable app\n  main-is: Main.hs\n  hs-source-dirs: app\n  build-depends: base, servant-server, warp\n  default-language: Haskell2010\n'}
    if lang == "lisp":
        return {f"{base}/{app}.asd": f'(asdf:defsystem "{app}" :serial t :components ((:file "main")))\n', f"{base}/main.lisp": f'(defpackage :{app} (:use :cl))\n(in-package :{app})\n(format t "{name} service ready~%")\n'}
    if lang == "rpg":
        return _ibmi_project(base, app, name)
    return {}


# Function: _ibmi_project
def _ibmi_project(base: str, app: str, name: str) -> Dict[str, str]:
    obj = re.sub(r"[^A-Z0-9]", "", app.upper())[:8] or "MODAPP"
    return {
        f"{base}/qrpglesrc/{obj}.rpgle": f"""**free
ctl-opt main(Main) option(*srcstmt:*nodebugio);
dcl-proc Main;
  dsply '{name} ready';
  *inlr = *on;
end-proc;
""",
        f"{base}/qclsrc/BUILD.clle": f"""pgm
  crtbnrpg pgm({obj}/{obj}) srcstmf('./qrpglesrc/{obj}.rpgle') option(*eventf)
endpgm
""",
        f"{base}/sql/schema.sql": f"""-- Db2 for i
CREATE TABLE {obj}.HEALTH_STATUS (
  SERVICE_NAME VARCHAR(128) NOT NULL,
  STATUS VARCHAR(16) NOT NULL,
  CHECKED_AT TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""",
        f"{base}/iproj.json": '{"description":"Strat-Aqorynth generated IBM i project","version":"1.0.0"}\n',
        f"{base}/README.md": f"# {name} IBM i service\n\nBuild with IBM i `CRTBNDRPG` through `BUILD.CLLE`; apply `sql/schema.sql` with RUNSQLSTM. Sources use fully-free ILE RPG and Db2 for i.\n",
    }
