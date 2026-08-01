# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/scaffolds (java.py)
# Date: 2026-03-26
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



# ─── Java Spring Boot generation ──────────────────────────────────────────────
# Function: _gen_spring_service
def _gen_spring_service(
    output: Dict[str, str], root_ns: str, domain: str, tables: List[str],
    db_target: str = "postgres",
):
    pkg  = f"com.{root_ns.lower()}.{domain.lower()}"
    base = f"ModernizedApp/services/{domain.lower()}-service"
    src  = f"{base}/src/main/java/{pkg.replace('.', '/')}"

    output[f"{base}/pom.xml"]                         = _spring_service_pom(root_ns, domain)
    output[f"{src}/{domain}Application.java"]         = _spring_application(pkg, domain)
    output[f"{src}/repository/{domain}Repository.java"] = _spring_repository(pkg, domain, db_target)
    output[f"{src}/service/I{domain}Service.java"]    = _spring_service_iface(pkg, domain)
    output[f"{src}/service/{domain}ServiceImpl.java"] = _spring_service_impl(pkg, domain)
    output[f"{base}/src/main/resources/application.yml"] = _spring_application_yml(domain)


# Function: _spring_parent_pom
def _spring_parent_pom(root_ns: str, domains: List[str]) -> str:
    modules = "\n".join(f"        <module>services/{d.lower()}-service</module>" for d in domains)
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <groupId>com.{root_ns.lower()}</groupId>
          <artifactId>{root_ns.lower()}-parent</artifactId>
          <version>1.0.0-SNAPSHOT</version>
          <packaging>pom</packaging>
          <parent>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-parent</artifactId>
            <version>4.1.0</version>
          </parent>
          <modules>
        {modules}
          </modules>
          <properties>
            <java.version>21</java.version>
          </properties>
        </project>
    """)


# Function: _spring_service_pom
def _spring_service_pom(root_ns: str, domain: str) -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <parent>
            <groupId>com.{root_ns.lower()}</groupId>
            <artifactId>{root_ns.lower()}-parent</artifactId>
            <version>1.0.0-SNAPSHOT</version>
          </parent>
          <artifactId>{domain.lower()}-service</artifactId>
          <dependencies>
            <dependency><groupId>org.springframework.boot</groupId>
              <artifactId>spring-boot-starter-web</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId>
              <artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId>
              <artifactId>spring-boot-starter-validation</artifactId></dependency>
            <dependency><groupId>org.postgresql</groupId>
              <artifactId>postgresql</artifactId><scope>runtime</scope></dependency>
            <dependency><groupId>org.projectlombok</groupId>
              <artifactId>lombok</artifactId><optional>true</optional></dependency>
          </dependencies>
        </project>
    """)


# Function: _spring_application
def _spring_application(pkg: str, domain: str) -> str:
    return textwrap.dedent(f"""\
        package {pkg};

        import org.springframework.boot.SpringApplication;
        import org.springframework.boot.autoconfigure.SpringBootApplication;

        @SpringBootApplication
        public class {domain}Application {{
            public static void main(String[] args) {{
                SpringApplication.run({domain}Application.class, args);
            }}
        }}
    """)


# Function: _spring_repository
def _spring_repository(pkg: str, domain: str, db_target: str = "postgres") -> str:
    entity = domain.rstrip("s")
    repository_type = {
        "mongodb": "org.springframework.data.mongodb.repository.MongoRepository",
        "cassandra": "org.springframework.data.cassandra.repository.CassandraRepository",
        "neo4j": "org.springframework.data.neo4j.repository.Neo4jRepository",
        "redis": "org.springframework.data.repository.CrudRepository",
        "elasticsearch": "org.springframework.data.elasticsearch.repository.ElasticsearchRepository",
    }.get((db_target or "").casefold(), "org.springframework.data.jpa.repository.JpaRepository")
    repository_name = repository_type.rsplit(".", 1)[-1]
    return textwrap.dedent(f"""\
        package {pkg}.repository;

        import {pkg}.model.{entity};
        import {repository_type};
        import org.springframework.stereotype.Repository;
        import java.util.List;

        @Repository
        public interface {domain}Repository extends {repository_name}<{entity}, Long> {{
            List<{entity}> findByIsActiveTrue();
        }}
    """)


# Function: _spring_service_iface
def _spring_service_iface(pkg: str, domain: str) -> str:
    entity = domain.rstrip("s")
    return textwrap.dedent(f"""\
        package {pkg}.service;

        import {pkg}.model.{entity};
        import java.util.List;
        import java.util.Optional;

        public interface I{domain}Service {{
            List<{entity}> findAll();
            Optional<{entity}> findById(Long id);
            {entity} create({entity} entity);
            {entity} update(Long id, {entity} entity);
            void delete(Long id);
        }}
    """)


# Function: _spring_service_impl
def _spring_service_impl(pkg: str, domain: str) -> str:
    entity = domain.rstrip("s")
    return textwrap.dedent(f"""\
        package {pkg}.service;

        import {pkg}.model.{entity};
        import {pkg}.repository.{domain}Repository;
        import lombok.RequiredArgsConstructor;
        import org.springframework.stereotype.Service;
        import org.springframework.transaction.annotation.Transactional;
        import java.util.List;
        import java.util.Optional;

        @Service
        @RequiredArgsConstructor
        @Transactional(readOnly = true)
        public class {domain}ServiceImpl implements I{domain}Service {{

            private final {domain}Repository repository;

            @Override
            public List<{entity}> findAll() {{
                return repository.findByIsActiveTrue();
            }}

            @Override
            public Optional<{entity}> findById(Long id) {{
                return repository.findById(id);
            }}

            @Override
            @Transactional
            public {entity} create({entity} entity) {{
                return repository.save(entity);
            }}

            @Override
            @Transactional
            public {entity} update(Long id, {entity} updated) {{
                return repository.findById(id).map(existing -> {{
                    existing.setName(updated.getName());
                    existing.setIsActive(updated.getIsActive());
                    return repository.save(existing);
                }}).orElseThrow(() -> new RuntimeException("{entity} not found: " + id));
            }}

            @Override
            @Transactional
            public void delete(Long id) {{
                repository.findById(id).ifPresent(e -> {{
                    e.setIsActive(false);
                    repository.save(e);
                }});
            }}
        }}
    """)


# Function: _spring_application_yml
def _spring_application_yml(domain: str) -> str:
    return textwrap.dedent(f"""\
        spring:
          application:
            name: {domain.lower()}-service
          datasource:
            url: jdbc:postgresql://localhost:5432/modernized_{domain.lower()}
            username: ${{DB_USER:postgres}}
            password: ${{DB_PASSWORD:changeme}}
            driver-class-name: org.postgresql.Driver
          jpa:
            hibernate:
              ddl-auto: validate
            show-sql: false
            properties:
              hibernate:
                format_sql: true
                dialect: org.hibernate.dialect.PostgreSQLDialect
        server:
          port: 8080
    """)


# Function: _spring_gateway_config
def _spring_gateway_config(domains: List[str]) -> str:
    routes = []
    for i, d in enumerate(domains):
        port = 8080 + i
        routes.append(textwrap.dedent(f"""\
          - id: {d.lower()}-service
            uri: http://localhost:{port}
            predicates:
              - Path=/api/{d.lower()}/**"""))
    return textwrap.dedent(f"""\
        spring:
          cloud:
            gateway:
              routes:
        {chr(10).join('    ' + r for r in routes)}
        server:
          port: 8000
    """)


# ─── Java scaffold dispatch (framework-aware) ──────────────────────────────────
# Function: _gen_java_scaffold
def _gen_java_scaffold(
    output: Dict[str, str], root_ns: str, domain: str, tables: List[str],
    backend_tech: str, db_target: str = "postgres",
):
    """Picks the Spring/Quarkus/Micronaut deterministic scaffold family based
    on backend_tech. Same file-set shape (pom.xml, Repository, Service
    iface/impl, config) as _gen_spring_service, just framework-correct
    annotations/deps — see _mp_generate_build_files for the matching root
    pom.xml (parent POM) selection."""
    bt = (backend_tech or "").lower()
    if "quarkus" in bt:
        _gen_quarkus_service(output, root_ns, domain, tables)
    elif "micronaut" in bt:
        _gen_micronaut_service(output, root_ns, domain, tables, db_target)
    else:
        _gen_spring_service(output, root_ns, domain, tables, db_target)

    # All scaffold families share the production manifest resolver used by the
    # prompt-driven generator.  This prevents fallback generation from owning
    # a second, PostgreSQL-only dependency graph.
    from ..build_artifacts import _java_backend_pom
    base = f"ModernizedApp/services/{domain.lower()}-service"
    service_sources = {
        path: content for path, content in output.items() if path.startswith(f"{base}/")
    }
    from ..build_artifacts import _java_inferred_dependencies
    output[f"{base}/pom.xml"] = _java_backend_pom(
        f"{domain}-service", backend_tech,
        _java_inferred_dependencies(service_sources), db_target=db_target,
    )
    framework = (
        "quarkus" if "quarkus" in bt else "micronaut" if "micronaut" in bt else "spring"
    )
    config_name, config = _java_runtime_config(framework, db_target, domain)
    for path in list(output):
        if path.startswith(f"{base}/src/main/resources/application."):
            del output[path]
    output[f"{base}/src/main/resources/{config_name}"] = config


def _java_runtime_config(framework: str, db_target: str, domain: str) -> Tuple[str, str]:
    """Build environment-driven runtime configuration from database capability."""
    db = (db_target or "postgres").casefold().removesuffix("-vector")
    name = domain.lower()
    jdbc = {
        "postgres": ("postgresql", f"jdbc:postgresql://localhost:5432/modernized_{name}"),
        "pgvector": ("postgresql", f"jdbc:postgresql://localhost:5432/modernized_{name}"),
        "cockroachdb": ("postgresql", f"jdbc:postgresql://localhost:26257/modernized_{name}"),
        "mssql": ("mssql", f"jdbc:sqlserver://localhost:1433;databaseName=modernized_{name};encrypt=true"),
        "mysql": ("mysql", f"jdbc:mysql://localhost:3306/modernized_{name}"),
        "mariadb": ("mariadb", f"jdbc:mariadb://localhost:3306/modernized_{name}"),
        "oracle": ("oracle", "jdbc:oracle:thin:@//localhost:1521/FREEPDB1"),
        "db2": ("db2", f"jdbc:db2://localhost:50000/modernized_{name}"),
        "sqlite": ("sqlite", f"jdbc:sqlite:modernized_{name}.db"),
    }
    if framework == "spring":
        if db == "mongodb":
            return "application.yml", textwrap.dedent(f"""\
                spring:
                  application.name: {name}-service
                  data.mongodb.uri: ${{MONGODB_URI}}
                server.port: ${{SERVER_PORT:8080}}
            """)
        if db in {"redis", "cassandra", "neo4j", "elasticsearch", "opensearch", "dynamodb", "cosmosdb", "pinecone", "weaviate", "milvus", "vector"}:
            key = re.sub(r"[^A-Z0-9]+", "_", db.upper())
            return "application.yml", textwrap.dedent(f"""\
                spring:
                  application.name: {name}-service
                application:
                  datastore-uri: ${{{key}_URI}}
                server.port: ${{SERVER_PORT:8080}}
            """)
    if db in jdbc:
        kind, default_url = jdbc[db]
        if framework == "quarkus":
            return "application.properties", textwrap.dedent(f"""\
                quarkus.application.name={name}-service
                quarkus.datasource.db-kind={kind}
                quarkus.datasource.username=${{DB_USER}}
                quarkus.datasource.password=${{DB_PASSWORD}}
                quarkus.datasource.jdbc.url=${{DB_URL:{default_url}}}
                quarkus.hibernate-orm.database.generation=validate
                quarkus.http.port=${{SERVER_PORT:8080}}
            """)
        if framework == "micronaut":
            return "application.yml", (
                f"micronaut:\n  application:\n    name: {name}-service\n"
                "datasources:\n  default:\n"
                f"    url: ${{DB_URL:{default_url}}}\n"
                "    username: ${DB_USER}\n    password: ${DB_PASSWORD}\n"
            )
        return "application.yml", (
            f"spring:\n  application:\n    name: {name}-service\n  datasource:\n"
            f"    url: ${{DB_URL:{default_url}}}\n"
            "    username: ${DB_USER}\n    password: ${DB_PASSWORD}\n"
            "server:\n  port: ${SERVER_PORT:8080}\n"
        )
    key = re.sub(r"[^A-Z0-9]+", "_", db.upper())
    suffix = "properties" if framework == "quarkus" else "yml"
    separator = "=" if suffix == "properties" else ": "
    return f"application.{suffix}", f"application.datastore-uri{separator}${{{key}_URI}}\n"


# ─── Quarkus deterministic scaffold ─────────────────────────────────────────
# Function: _gen_quarkus_service
def _gen_quarkus_service(output: Dict[str, str], root_ns: str, domain: str, tables: List[str]):
    pkg  = f"com.{root_ns.lower()}.{domain.lower()}"
    base = f"ModernizedApp/services/{domain.lower()}-service"
    src  = f"{base}/src/main/java/{pkg.replace('.', '/')}"

    output[f"{base}/pom.xml"]                            = _quarkus_service_pom(root_ns, domain)
    output[f"{src}/repository/{domain}Repository.java"]  = _quarkus_repository(pkg, domain)
    output[f"{src}/service/I{domain}Service.java"]       = _spring_service_iface(pkg, domain)  # framework-agnostic
    output[f"{src}/service/{domain}ServiceImpl.java"]    = _quarkus_service_impl(pkg, domain)
    output[f"{base}/src/main/resources/application.properties"] = _quarkus_application_properties(domain)


# Function: _quarkus_parent_pom
def _quarkus_parent_pom(root_ns: str, domains: List[str]) -> str:
    modules = "\n".join(f"        <module>services/{d.lower()}-service</module>" for d in domains)
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <groupId>com.{root_ns.lower()}</groupId>
          <artifactId>{root_ns.lower()}-parent</artifactId>
          <version>1.0.0-SNAPSHOT</version>
          <packaging>pom</packaging>
          <properties>
            <quarkus.platform.group-id>io.quarkus.platform</quarkus.platform.group-id>
            <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
            <quarkus.platform.version>3.15.1</quarkus.platform.version>
            <maven.compiler.release>21</maven.compiler.release>
          </properties>
          <dependencyManagement>
            <dependencies>
              <dependency>
                <groupId>${{quarkus.platform.group-id}}</groupId>
                <artifactId>${{quarkus.platform.artifact-id}}</artifactId>
                <version>${{quarkus.platform.version}}</version>
                <type>pom</type>
                <scope>import</scope>
              </dependency>
            </dependencies>
          </dependencyManagement>
          <modules>
        {modules}
          </modules>
        </project>
    """)


# Function: _quarkus_service_pom
def _quarkus_service_pom(root_ns: str, domain: str) -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <parent>
            <groupId>com.{root_ns.lower()}</groupId>
            <artifactId>{root_ns.lower()}-parent</artifactId>
            <version>1.0.0-SNAPSHOT</version>
          </parent>
          <artifactId>{domain.lower()}-service</artifactId>
          <dependencies>
            <dependency><groupId>io.quarkus</groupId>
              <artifactId>quarkus-resteasy-reactive-jackson</artifactId></dependency>
            <dependency><groupId>io.quarkus</groupId>
              <artifactId>quarkus-hibernate-orm-panache</artifactId></dependency>
            <dependency><groupId>io.quarkus</groupId>
              <artifactId>quarkus-jdbc-postgresql</artifactId></dependency>
            <dependency><groupId>io.quarkus</groupId>
              <artifactId>quarkus-hibernate-validator</artifactId></dependency>
          </dependencies>
          <build>
            <plugins>
              <plugin>
                <groupId>io.quarkus</groupId>
                <artifactId>quarkus-maven-plugin</artifactId>
                <version>${{quarkus.platform.version}}</version>
                <extensions>true</extensions>
                <executions>
                  <execution><goals><goal>build</goal></goals></execution>
                </executions>
              </plugin>
            </plugins>
          </build>
        </project>
    """)


# Function: _quarkus_repository
def _quarkus_repository(pkg: str, domain: str) -> str:
    entity = domain.rstrip("s")
    return textwrap.dedent(f"""\
        package {pkg}.repository;

        import {pkg}.model.{entity};
        import io.quarkus.hibernate.orm.panache.PanacheRepository;
        import jakarta.enterprise.context.ApplicationScoped;
        import java.util.List;

        @ApplicationScoped
        public class {domain}Repository implements PanacheRepository<{entity}> {{
            public List<{entity}> findByIsActiveTrue() {{
                return list("isActive", true);
            }}
        }}
    """)


# Function: _quarkus_service_impl
def _quarkus_service_impl(pkg: str, domain: str) -> str:
    entity = domain.rstrip("s")
    return textwrap.dedent(f"""\
        package {pkg}.service;

        import {pkg}.model.{entity};
        import {pkg}.repository.{domain}Repository;
        import jakarta.enterprise.context.ApplicationScoped;
        import jakarta.transaction.Transactional;
        import java.util.List;
        import java.util.Optional;

        @ApplicationScoped
        public class {domain}ServiceImpl implements I{domain}Service {{

            private final {domain}Repository repository;

            public {domain}ServiceImpl({domain}Repository repository) {{
                this.repository = repository;
            }}

            @Override
            public List<{entity}> findAll() {{
                return repository.findByIsActiveTrue();
            }}

            @Override
            public Optional<{entity}> findById(Long id) {{
                return repository.findByIdOptional(id);
            }}

            @Override
            @Transactional
            public {entity} create({entity} entity) {{
                repository.persist(entity);
                return entity;
            }}

            @Override
            @Transactional
            public {entity} update(Long id, {entity} updated) {{
                return repository.findByIdOptional(id).map(existing -> {{
                    existing.setName(updated.getName());
                    existing.setIsActive(updated.getIsActive());
                    return existing;
                }}).orElseThrow(() -> new RuntimeException("{entity} not found: " + id));
            }}

            @Override
            @Transactional
            public void delete(Long id) {{
                repository.findByIdOptional(id).ifPresent(e -> e.setIsActive(false));
            }}
        }}
    """)


# Function: _quarkus_application_properties
def _quarkus_application_properties(domain: str) -> str:
    return textwrap.dedent(f"""\
        quarkus.application.name={domain.lower()}-service
        quarkus.datasource.db-kind=postgresql
        quarkus.datasource.username=${{DB_USER:postgres}}
        quarkus.datasource.password=${{DB_PASSWORD:changeme}}
        quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/modernized_{domain.lower()}
        quarkus.hibernate-orm.database.generation=validate
        quarkus.http.port=8080
    """)


# ─── Micronaut deterministic scaffold ───────────────────────────────────────
# Function: _gen_micronaut_service
def _gen_micronaut_service(
    output: Dict[str, str], root_ns: str, domain: str, tables: List[str],
    db_target: str = "postgres",
):
    pkg  = f"com.{root_ns.lower()}.{domain.lower()}"
    base = f"ModernizedApp/services/{domain.lower()}-service"
    src  = f"{base}/src/main/java/{pkg.replace('.', '/')}"

    output[f"{base}/pom.xml"]                            = _micronaut_service_pom(root_ns, domain)
    output[f"{src}/{domain}Application.java"]            = _micronaut_application(pkg, domain)
    output[f"{src}/repository/{domain}Repository.java"]  = _micronaut_repository(pkg, domain, db_target)
    output[f"{src}/service/I{domain}Service.java"]       = _spring_service_iface(pkg, domain)  # framework-agnostic
    output[f"{src}/service/{domain}ServiceImpl.java"]    = _micronaut_service_impl(pkg, domain)
    output[f"{base}/src/main/resources/application.yml"] = _micronaut_application_yml(domain)


# Function: _micronaut_parent_pom
def _micronaut_parent_pom(root_ns: str, domains: List[str]) -> str:
    modules = "\n".join(f"        <module>services/{d.lower()}-service</module>" for d in domains)
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <parent>
            <groupId>io.micronaut.platform</groupId>
            <artifactId>micronaut-parent</artifactId>
            <version>4.6.3</version>
          </parent>
          <groupId>com.{root_ns.lower()}</groupId>
          <artifactId>{root_ns.lower()}-parent</artifactId>
          <version>1.0.0-SNAPSHOT</version>
          <packaging>pom</packaging>
          <properties>
            <maven.compiler.release>21</maven.compiler.release>
          </properties>
          <modules>
        {modules}
          </modules>
        </project>
    """)


# Function: _micronaut_service_pom
def _micronaut_service_pom(root_ns: str, domain: str) -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <parent>
            <groupId>com.{root_ns.lower()}</groupId>
            <artifactId>{root_ns.lower()}-parent</artifactId>
            <version>1.0.0-SNAPSHOT</version>
          </parent>
          <artifactId>{domain.lower()}-service</artifactId>
          <dependencies>
            <dependency><groupId>io.micronaut</groupId>
              <artifactId>micronaut-http-server-netty</artifactId></dependency>
            <dependency><groupId>io.micronaut.data</groupId>
              <artifactId>micronaut-data-jdbc</artifactId></dependency>
            <dependency><groupId>io.micronaut.sql</groupId>
              <artifactId>micronaut-jdbc-hikari</artifactId></dependency>
            <dependency><groupId>org.postgresql</groupId>
              <artifactId>postgresql</artifactId><scope>runtime</scope></dependency>
            <dependency><groupId>io.micronaut.validation</groupId>
              <artifactId>micronaut-validation</artifactId></dependency>
            <dependency><groupId>io.micronaut</groupId>
              <artifactId>micronaut-jackson-databind</artifactId></dependency>
          </dependencies>
          <build>
            <plugins>
              <plugin>
                <groupId>io.micronaut.maven</groupId>
                <artifactId>micronaut-maven-plugin</artifactId>
              </plugin>
            </plugins>
          </build>
        </project>
    """)


# Function: _micronaut_application
def _micronaut_application(pkg: str, domain: str) -> str:
    return textwrap.dedent(f"""\
        package {pkg};

        import io.micronaut.runtime.Micronaut;

        public class {domain}Application {{
            public static void main(String[] args) {{
                Micronaut.run({domain}Application.class, args);
            }}
        }}
    """)


# Function: _micronaut_repository
def _micronaut_repository(pkg: str, domain: str, db_target: str = "postgres") -> str:
    entity = domain.rstrip("s")
    dialect = {
        "postgres": "POSTGRES", "pgvector": "POSTGRES", "cockroachdb": "POSTGRES",
        "mysql": "MYSQL", "mariadb": "MYSQL", "mssql": "SQL_SERVER",
        "oracle": "ORACLE",
    }.get((db_target or "").casefold(), "ANSI")
    return textwrap.dedent(f"""\
        package {pkg}.repository;

        import {pkg}.model.{entity};
        import io.micronaut.data.jdbc.annotation.JdbcRepository;
        import io.micronaut.data.model.query.builder.sql.Dialect;
        import io.micronaut.data.repository.CrudRepository;
        import java.util.List;

        @JdbcRepository(dialect = Dialect.{dialect})
        public interface {domain}Repository extends CrudRepository<{entity}, Long> {{
            List<{entity}> findByIsActiveTrue();
        }}
    """)


# Function: _micronaut_service_impl
def _micronaut_service_impl(pkg: str, domain: str) -> str:
    entity = domain.rstrip("s")
    return textwrap.dedent(f"""\
        package {pkg}.service;

        import {pkg}.model.{entity};
        import {pkg}.repository.{domain}Repository;
        import jakarta.inject.Singleton;
        import java.util.List;
        import java.util.Optional;

        @Singleton
        public class {domain}ServiceImpl implements I{domain}Service {{

            private final {domain}Repository repository;

            public {domain}ServiceImpl({domain}Repository repository) {{
                this.repository = repository;
            }}

            @Override
            public List<{entity}> findAll() {{
                return repository.findByIsActiveTrue();
            }}

            @Override
            public Optional<{entity}> findById(Long id) {{
                return repository.findById(id);
            }}

            @Override
            public {entity} create({entity} entity) {{
                return repository.save(entity);
            }}

            @Override
            public {entity} update(Long id, {entity} updated) {{
                return repository.findById(id).map(existing -> {{
                    existing.setName(updated.getName());
                    existing.setIsActive(updated.getIsActive());
                    return repository.update(existing);
                }}).orElseThrow(() -> new RuntimeException("{entity} not found: " + id));
            }}

            @Override
            public void delete(Long id) {{
                repository.findById(id).ifPresent(e -> {{
                    e.setIsActive(false);
                    repository.update(e);
                }});
            }}
        }}
    """)


# Function: _micronaut_application_yml
def _micronaut_application_yml(domain: str) -> str:
    return textwrap.dedent(f"""\
        micronaut:
          application:
            name: {domain.lower()}-service
        datasources:
          default:
            url: jdbc:postgresql://localhost:5432/modernized_{domain.lower()}
            username: ${{DB_USER:postgres}}
            password: ${{DB_PASSWORD:changeme}}
            driverClassName: org.postgresql.Driver
            dialect: POSTGRES
    """)
