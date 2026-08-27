# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/domain_generators (java.py)
# Date: 2026-04-06
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


def _normalize_spring_entity_contract(content: str) -> str:
    """Expose the Boolean accessor contract used by the Spring service scaffold.

    Lombok intentionally turns a primitive field named ``isActive`` into
    ``isActive()/setActive()``. The stable service API uses
    ``getIsActive()/setIsActive()`` so it also works for nullable ``Boolean``
    entities. Add explicit aliases only for that primitive edge case.
    """
    if not re.search(r"\bprivate\s+boolean\s+isActive\b", content):
        return content
    if " getIsActive(" in content and " setIsActive(" in content:
        return content
    closing_brace = content.rfind("}")
    if closing_brace < 0:
        return content
    accessors = (
        "\n    public Boolean getIsActive() {\n"
        "        return isActive;\n"
        "    }\n\n"
        "    public void setIsActive(Boolean active) {\n"
        "        this.isActive = Boolean.TRUE.equals(active);\n"
        "    }\n"
    )
    return content[:closing_brace] + accessors + content[closing_brace:]



# ─── LLM-powered domain generator ────────────────────────────────────────────

# ─── Per-language domain generation helpers ──────────────────────────────────

# Function: _llm_domain_java
# Function: _java_controller_prompt_quarkus
def _java_controller_prompt_quarkus(domain, root_ns, domain_tables, antipatterns, context, prod_rules, source_sec, guide_sec) -> str:
    return (
        f"{context}\n{prod_rules}{source_sec}{guide_sec}\n\n"
        f"Generate a COMPLETE, PRODUCTION-READY Quarkus JAX-RS resource named {domain}Controller "
        f"in package com.{root_ns.lower()}.{domain.lower()}.controller with ALL of the following:\n"
        f"- @Path(\"/api/{domain.lower()}\") @ApplicationScoped on the class\n"
        f"- @Produces(MediaType.APPLICATION_JSON) @Consumes(MediaType.APPLICATION_JSON) on the class\n"
        f"- org.jboss.logging.Logger: private static final Logger log = Logger.getLogger({domain}Controller.class)\n"
        f"- Constructor injection of I{domain}Service (CDI, no field injection)\n"
        f"- Full CRUD endpoints:\n"
        f"    @GET                    /api/{domain.lower()}?page=0&size=20  → paginated list\n"
        f"    @GET @Path(\"/{{id}}\")     /api/{domain.lower()}/{{id}}           → Response (404 if missing)\n"
        f"    @POST                   /api/{domain.lower()}                  → Response.status(201) with Location header\n"
        f"    @PUT @Path(\"/{{id}}\")     /api/{domain.lower()}/{{id}}            → Response (404 if missing)\n"
        f"    @DELETE @Path(\"/{{id}}\")  /api/{domain.lower()}/{{id}}            → Response.noContent() or 404\n"
        f"- Request/Response DTO records with Jakarta Bean Validation: @NotNull, @NotBlank, @Size, @Positive\n"
        f"- @Valid on all request-body parameters\n"
        f"- A jakarta.ws.rs.ext.ExceptionMapper<ResourceNotFoundException> returning a JSON problem body\n"
        f"- log.info for successful operations, log.warn for not-found, log.error for exceptions\n"
        f"- Never catch generic Exception or Throwable; let unexpected exceptions propagate to the "
        f"ExceptionMapper — catch only the specific typed exceptions this method can actually throw\n"
        f"- Tables being modernized: {', '.join(domain_tables)}\n"
        f"- Fix anti-patterns detected: {', '.join(antipatterns) or 'none'}\n"
        f"Output ONLY the complete Java file. No markdown fences."
    )


# Function: _java_controller_prompt_micronaut
def _java_controller_prompt_micronaut(domain, root_ns, domain_tables, antipatterns, context, prod_rules, source_sec, guide_sec) -> str:
    return (
        f"{context}\n{prod_rules}{source_sec}{guide_sec}\n\n"
        f"Generate a COMPLETE, PRODUCTION-READY Micronaut @Controller named {domain}Controller "
        f"in package com.{root_ns.lower()}.{domain.lower()}.controller with ALL of the following:\n"
        f"- @Controller(\"/api/{domain.lower()}\") on the class\n"
        f"- SLF4J logger: private static final Logger log = LoggerFactory.getLogger({domain}Controller.class)\n"
        f"- Constructor injection of I{domain}Service (no field injection)\n"
        f"- Full CRUD endpoints:\n"
        f"    @Get              /api/{domain.lower()}?page=0&size=20  → paginated list\n"
        f"    @Get(\"/{{id}}\")     /api/{domain.lower()}/{{id}}           → HttpResponse<{domain}Response> (404 if missing)\n"
        f"    @Post             /api/{domain.lower()}                  → HttpResponse.created(...) with Location header\n"
        f"    @Put(\"/{{id}}\")     /api/{domain.lower()}/{{id}}            → HttpResponse (404 if missing)\n"
        f"    @Delete(\"/{{id}}\")  /api/{domain.lower()}/{{id}}            → HttpResponse.noContent() or 404\n"
        f"- Request/Response DTOs as Java records with Jakarta Bean Validation (@NotNull, @NotBlank, @Size, @Positive)\n"
        f"- @Valid @Body on all request-body parameters\n"
        f"- An @Error handler method for ResourceNotFoundException returning a JSON error body\n"
        f"- log.info for successful operations, log.warn for not-found, log.error for exceptions\n"
        f"- Never catch generic Exception or Throwable; let unexpected exceptions propagate to the "
        f"@Error handler — catch only the specific typed exceptions this method can actually throw\n"
        f"- Tables being modernized: {', '.join(domain_tables)}\n"
        f"- Fix anti-patterns detected: {', '.join(antipatterns) or 'none'}\n"
        f"Output ONLY the complete Java file. No markdown fences."
    )


# Function: _java_entity_prompt_quarkus
def _java_entity_prompt_quarkus(domain, root_ns, domain_tables, context, prod_rules, source_sec, guide_sec) -> str:
    table = domain_tables[0].lower() if domain_tables else domain.lower()
    return (
        f"{context}\n{prod_rules}{source_sec}{guide_sec}\n\n"
        f"Generate a COMPLETE Quarkus Hibernate ORM entity + DTO in package com.{root_ns.lower()}.{domain.lower()}.model:\n"
        f"1. @Entity @Table(name = \"{table}\") class {domain.rstrip('s')} with:\n"
        f"   - @Id @GeneratedValue(strategy = GenerationType.IDENTITY) Long id\n"
        f"   - ALL business fields with appropriate JPA @Column constraints (nullable, length, unique)\n"
        f"   - Boolean isActive = true with @Column(nullable=false)\n"
        f"   - LocalDateTime createdAt auto-set via @PrePersist\n"
        f"   - LocalDateTime updatedAt auto-set via @PreUpdate\n"
        f"   - Plain getters/setters (no Lombok - it is not a default Quarkus dependency)\n"
        f"   - Business-relevant fields inferred from domain '{domain}' and tables: {', '.join(domain_tables)}\n"
        f"2. {domain.rstrip('s')}CreateRequest record with full Jakarta Bean Validation (@NotNull/@NotBlank/@Size)\n"
        f"3. {domain.rstrip('s')}UpdateRequest record with full validation\n"
        f"4. {domain.rstrip('s')}Response record (safe read model, no sensitive fields)\n"
        f"5. {domain}Mapper utility class with static toResponse(), toEntity() helper methods\n"
        f"Output ONLY the Java file with all 5 declarations. No markdown fences."
    )


# Function: _java_entity_prompt_micronaut
def _java_entity_prompt_micronaut(domain, root_ns, domain_tables, context, prod_rules, source_sec, guide_sec) -> str:
    table = domain_tables[0].lower() if domain_tables else domain.lower()
    return (
        f"{context}\n{prod_rules}{source_sec}{guide_sec}\n\n"
        f"Generate a COMPLETE Micronaut Data JDBC entity + DTO in package com.{root_ns.lower()}.{domain.lower()}.model:\n"
        f"1. @MappedEntity(\"{table}\") class {domain.rstrip('s')} with:\n"
        f"   - @Id @GeneratedValue(GeneratedValue.Type.IDENTITY) Long id\n"
        f"   - ALL business fields with appropriate types, matching the source columns\n"
        f"   - Boolean isActive = true\n"
        f"   - LocalDateTime createdAt, LocalDateTime updatedAt\n"
        f"   - Plain getters/setters and an all-args constructor (no Lombok - not a default Micronaut dependency)\n"
        f"   - Business-relevant fields inferred from domain '{domain}' and tables: {', '.join(domain_tables)}\n"
        f"2. {domain.rstrip('s')}CreateRequest record with full Jakarta Bean Validation (@NotNull/@NotBlank/@Size)\n"
        f"3. {domain.rstrip('s')}UpdateRequest record with full validation\n"
        f"4. {domain.rstrip('s')}Response record (safe read model, no sensitive fields)\n"
        f"5. {domain}Mapper utility class with static toResponse(), toEntity() helper methods\n"
        f"Output ONLY the Java file with all 5 declarations. No markdown fences."
    )


# Function: _llm_domain_java
def _llm_domain_java(
    files: "Dict[str, str]",
    domain: str,
    root_ns: str,
    domain_tables: "List[str]",
    antipatterns: "List[str]",
    context: str,
    prod_rules: str,
    source_sec: str,
    guide_sec: str,
    model: str,
    system: str,
    tables: "List[str]",
    target: dict,
    on_step: "Optional[Callable[[str], None]]",
    generate: "Callable[..., str]",
    on_validation: "Optional[Callable[[object, int], None]]" = None,
) -> set:
    """Add Java domain files to *files* (mutates in-place). Framework
    (Spring Boot / Quarkus / Micronaut) is selected from target['backend_tech']
    - see _gen_java_scaffold for the matching deterministic scaffold side."""
    from .._shared import _JAVA_FILE_GENERATION_MAX_SECONDS, _TOKENS_DEFAULT, _adaptive_num_ctx
    from ..scaffolds.java import _gen_java_scaffold
    from ..validation_orchestration import _generate_validated
    base = (
        f"ModernizedApp/services/{domain.lower()}-service/src/main/java"
        f"/com/{root_ns.lower()}/{domain.lower()}"
    )
    backend_tech = target.get("backend_tech", "") or ""
    bt = backend_tech.lower()
    is_quarkus = "quarkus" in bt
    is_micronaut = "micronaut" in bt
    generated_paths = set()

    # Controller
    try:
        if on_step:
            on_step(f"[{domain}] Generating Controller…")
        prompt = None
        if is_quarkus:
            prompt = _java_controller_prompt_quarkus(domain, root_ns, domain_tables, antipatterns, context, prod_rules, source_sec, guide_sec)
        elif is_micronaut:
            prompt = _java_controller_prompt_micronaut(domain, root_ns, domain_tables, antipatterns, context, prod_rules, source_sec, guide_sec)
        if prompt is None:
            prompt = (
            f"{context}\n{prod_rules}{source_sec}{guide_sec}\n\n"
            f"Generate a COMPLETE, PRODUCTION-READY Spring Boot 3 @RestController named {domain}Controller "
            f"in package com.{root_ns.lower()}.{domain.lower()}.controller. Compile against the exact "
            f"existing contracts com.{root_ns.lower()}.{domain.lower()}.service.I{domain}Service and "
            f"com.{root_ns.lower()}.{domain.lower()}.model.{domain}.\n"
            f"- SLF4J logger: private static final Logger log = LoggerFactory.getLogger({domain}Controller.class)\n"
            f"- Constructor injection of I{domain}Service (no field injection)\n"
            f"- Use only these service signatures: List<{domain}> findAll(), Optional<{domain}> findById(Long), "
            f"{domain} create({domain}), {domain} update(Long, {domain}), void delete(Long)\n"
            f"- Full CRUD endpoints:\n"
            f"    GET  /api/{domain.lower()}                  \u2192 ResponseEntity<List<{domain}>>\n"
            f"    GET  /api/{domain.lower()}/{{id}}           \u2192 ResponseEntity<{domain}> (404 if missing)\n"
            f"    POST /api/{domain.lower()}                  \u2192 ResponseEntity<{domain}> (201 Created)\n"
            f"    PUT  /api/{domain.lower()}/{{id}}            \u2192 ResponseEntity<{domain}> (404 if missing)\n"
            f"    DELETE /api/{domain.lower()}/{{id}}          \u2192 ResponseEntity<Void> (204 or 404)\n"
            f"- @Valid on all @RequestBody parameters, using jakarta.validation.Valid — this is Spring Boot 3 "
            f"on Jakarta EE 9+, never the legacy javax.validation/javax.persistence/javax.servlet namespace\n"
            f"- log.info for successful operations, log.warn for not-found, log.error for exceptions\n"
            f"- Never catch generic Exception or Throwable; let unexpected exceptions propagate to a "
            f"centralized @RestControllerAdvice — catch only the specific typed exceptions this method can "
            f"actually throw\n"
            f"- Do not invent DTOs, mappers, service methods, exceptions, or unlisted types\n"
            f"- Emit exactly one public top-level class\n"
            f"Output ONLY the complete Java file. No markdown fences."
        )
        _rel = f"{base}/controller/{domain}Controller.java"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="java",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Controller — attempt {a}/{m}…")) if on_step else None,
            generation_max_seconds=_JAVA_FILE_GENERATION_MAX_SECONDS,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
        if not _result.passed:
            raise RuntimeError(f"Java validation failed for {_rel}: {'; '.join(_result.diagnostics)}")
        generated_paths.add(_rel)
    except Exception as exc:
        logger.exception("Java controller generation failed for %s", domain)
        raise RuntimeError(f"Java controller generation failed for {domain}") from exc

    # Entity + DTO
    try:
        if on_step:
            on_step(f"[{domain}] Generating Entity + DTO…")
        prompt = None
        if is_quarkus:
            prompt = _java_entity_prompt_quarkus(domain, root_ns, domain_tables, context, prod_rules, source_sec, guide_sec)
        elif is_micronaut:
            prompt = _java_entity_prompt_micronaut(domain, root_ns, domain_tables, context, prod_rules, source_sec, guide_sec)
        if prompt is None:
            prompt = (
            f"{context}\n{prod_rules}{source_sec}{guide_sec}\n\n"
            f"Generate one COMPLETE Spring Boot 3 JPA entity in package com.{root_ns.lower()}.{domain.lower()}.model:\n"
            f"- The only public top-level class must be named {domain}\n"
            f"- @Entity @Table(name = \"{domain_tables[0].lower() if domain_tables else domain.lower()}\")\n"
            f"   - @Id @GeneratedValue(strategy = GenerationType.IDENTITY) Long id\n"
            f"   - String name with a non-null @Column constraint\n"
            f"   - Additional business fields grounded in the supplied source evidence\n"
            f"   - Boolean isActive = true with @Column(nullable=false)\n"
            f"   - LocalDateTime createdAt auto-set via @PrePersist\n"
            f"   - LocalDateTime updatedAt auto-set via @PreUpdate\n"
            f"   - Lombok @Data @NoArgsConstructor @AllArgsConstructor with every annotation imported\n"
            f"   - Business-relevant fields inferred from domain '{domain}' and tables: {', '.join(domain_tables)}\n"
            f"- Do not emit DTOs, records, mappers, nested types, or a second top-level declaration\n"
            f"Output ONLY the complete {domain}.java file. No markdown fences."
        )
        _rel = f"{base}/model/{domain}.java"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="java",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Entity + DTO — attempt {a}/{m}…")) if on_step else None,
            generation_max_seconds=_JAVA_FILE_GENERATION_MAX_SECONDS,
        )
        if not (is_quarkus or is_micronaut):
            _content = _normalize_spring_entity_contract(_content)
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
        if not _result.passed:
            raise RuntimeError(f"Java validation failed for {_rel}: {'; '.join(_result.diagnostics)}")
        generated_paths.add(_rel)
    except Exception as exc:
        logger.exception("Java entity generation failed for %s", domain)
        raise RuntimeError(f"Java entity generation failed for {domain}") from exc

    # Service interface and implementation must be separate Java compilation
    # units. The former prompt requested both in one response, then validated
    # the response as one *.java file—an unsatisfiable repair loop. The
    # framework-specific scaffold owns these complete files and the final
    # dependency-aware Maven build validates them.
    _gen_java_scaffold(files, root_ns, domain, tables, backend_tech, target.get("db_target", "postgres"))
    return generated_paths
