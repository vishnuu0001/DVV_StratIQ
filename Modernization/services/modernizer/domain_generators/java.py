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
) -> None:
    """Add Java domain files to *files* (mutates in-place). Framework
    (Spring Boot / Quarkus / Micronaut) is selected from target['backend_tech']
    - see _gen_java_scaffold for the matching deterministic scaffold side."""
    from .._shared import _TOKENS_DEFAULT, _adaptive_num_ctx
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
            f"in package com.{root_ns.lower()}.{domain.lower()}.controller with ALL of the following:\n"
            f"- SLF4J logger: private static final Logger log = LoggerFactory.getLogger({domain}Controller.class)\n"
            f"- Constructor injection of I{domain}Service (no field injection)\n"
            f"- Full CRUD endpoints:\n"
            f"    GET  /api/{domain.lower()}?page=0&size=20  \u2192 Page<{domain}Response> (paginated)\n"
            f"    GET  /api/{domain.lower()}/{{id}}           \u2192 ResponseEntity<{domain}Response> (404 if missing)\n"
            f"    POST /api/{domain.lower()}                  \u2192 ResponseEntity<{domain}Response> (201 Created, Location header)\n"
            f"    PUT  /api/{domain.lower()}/{{id}}            \u2192 ResponseEntity<{domain}Response> (404 if missing)\n"
            f"    DELETE /api/{domain.lower()}/{{id}}          \u2192 ResponseEntity<Void> (204 or 404)\n"
            f"- Request/Response DTO records with validation: @NotNull, @NotBlank, @Size, @Positive as appropriate\n"
            f"- @Valid on all @RequestBody parameters\n"
            f"- @ExceptionHandler for ResourceNotFoundException returning ProblemDetail (RFC 7807)\n"
            f"- @ExceptionHandler for MethodArgumentNotValidException returning validation error details\n"
            f"- log.info for successful operations, log.warn for not-found, log.error for exceptions\n"
            f"- Tables being modernized: {', '.join(domain_tables)}\n"
            f"- Fix anti-patterns detected: {', '.join(antipatterns) or 'none'}\n"
            f"Output ONLY the complete Java file. No markdown fences."
        )
        _rel = f"{base}/controller/{domain}Controller.java"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="java",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Controller — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
    except Exception as exc:
        files[f"{base}/controller/{domain}Controller.java"] = f"// LLM generation failed: {exc}\n"

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
            f"Generate a COMPLETE Spring Boot 3 JPA entity + DTO in package com.{root_ns.lower()}.{domain.lower()}.model:\n"
            f"1. @Entity @Table(name = \"{domain_tables[0].lower() if domain_tables else domain.lower()}\") class {domain.rstrip('s')} with:\n"
            f"   - @Id @GeneratedValue(strategy = GenerationType.IDENTITY) Long id\n"
            f"   - ALL business fields with appropriate JPA @Column constraints (nullable, length, unique)\n"
            f"   - Boolean isActive = true with @Column(nullable=false)\n"
            f"   - LocalDateTime createdAt auto-set via @PrePersist\n"
            f"   - LocalDateTime updatedAt auto-set via @PreUpdate\n"
            f"   - Lombok @Data @Builder @NoArgsConstructor @AllArgsConstructor\n"
            f"   - @EqualsAndHashCode(of = \"id\")\n"
            f"   - Business-relevant fields inferred from domain '{domain}' and tables: {', '.join(domain_tables)}\n"
            f"2. {domain.rstrip('s')}CreateRequest record with full @NotNull/@NotBlank/@Size validation\n"
            f"3. {domain.rstrip('s')}UpdateRequest record with full validation\n"
            f"4. {domain.rstrip('s')}Response record (safe read model, no sensitive fields)\n"
            f"5. {domain}Mapper utility class with static toResponse(), toEntity() helper methods\n"
            f"Output ONLY the Java file with all 5 declarations. No markdown fences."
        )
        _rel = f"{base}/model/{domain}.java"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="java",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Entity + DTO — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
    except Exception as exc:
        files[f"{base}/model/{domain}.java"] = f"// LLM generation failed: {exc}\n"

    # Service interface + full implementation (LLM) — Spring Data JPA's
    # Pageable/Page<T> types used here don't exist in Quarkus/Micronaut, so for
    # those two frameworks the deterministic scaffold below (framework-correct
    # Panache/Micronaut-Data repository calls) is the sole Service artifact
    # rather than risking Spring vocabulary leaking into their projects.
    if is_quarkus or is_micronaut:
        _gen_java_scaffold(files, root_ns, domain, tables, backend_tech, target.get("db_target", "postgres"))
    else:
      try:
        if on_step:
            on_step(f"[{domain}] Generating Service interface + implementation…")
        prompt = (
            f"{context}\n{prod_rules}{source_sec}{guide_sec}\n\n"
            f"Generate TWO Java files in one output, separated by '// === FILE ===' sentinel:\n\n"
            f"FILE 1: I{domain}Service interface in package com.{root_ns.lower()}.{domain.lower()}.service\n"
            f"- findAll(Pageable pageable): Page<{domain.rstrip('s')}Response>\n"
            f"- findById(Long id): {domain.rstrip('s')}Response (throws ResourceNotFoundException)\n"
            f"- create({domain.rstrip('s')}CreateRequest request): {domain.rstrip('s')}Response\n"
            f"- update(Long id, {domain.rstrip('s')}UpdateRequest request): {domain.rstrip('s')}Response\n"
            f"- delete(Long id): void\n\n"
            f"FILE 2: {domain}ServiceImpl class implementing I{domain}Service:\n"
            f"- @Service @Transactional(readOnly=true) with @RequiredArgsConstructor\n"
            f"- SLF4J logger\n"
            f"- Constructor injection of {domain}Repository\n"
            f"- COMPLETE implementation of all methods including:\n"
            f"  * findAll: paged query using repository.findAll(pageable), map to response\n"
            f"  * findById: repository.findById(id).map(mapper::toResponse).orElseThrow ResourceNotFoundException\n"
            f"  * create: validate uniqueness if applicable, save, return mapped response\n"
            f"  * update: find existing, apply all fields from request, save, return response\n"
            f"  * delete: find existing, soft-delete (isActive=false), save (no hard delete)\n"
            f"- Custom ResourceNotFoundException(String message) inner class or separate class\n"
            f"Output ONLY the Java content. No markdown fences."
        )
        _rel = f"{base}/service/{domain}Service.java"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="java",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Service interface + implementation — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
      except Exception as exc:
        _gen_java_scaffold(files, root_ns, domain, tables, backend_tech, target.get("db_target", "postgres"))  # fallback

    # Boilerplate via templates (pom, Application.java/properties/yml, Repository)
    _gen_java_scaffold(files, root_ns, domain, tables, backend_tech, target.get("db_target", "postgres"))
