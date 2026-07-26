# StratIQ Platform — Product Features & Invention Disclosure Source Document

**Purpose of this document:** StartIQ's `IDD.docx` (Invention Disclosure Document) is a blank template requiring, per feature/module: a title, keywords, the technical problem addressed, a description of the invention, the inventive step ("X-factor"), advantages over alternatives, and development status. This document surveys every module in the repository via full-codebase search and extracts the features that are **genuinely novel technical mechanisms** — custom algorithms, scoring models, pipelines, and architectural patterns — as opposed to generic, non-copyrightable web-application plumbing (login forms, CRUD tables, REST scaffolding, standard dashboards). Each module section below is written so it can be lifted directly into an IDD submission.

Generic elements deliberately **excluded** as non-distinctive: standard JWT-style session auth, React/Vite SPA scaffolding, Flask/FastAPI REST conventions, IIS reverse-proxy configuration, and CRUD database access — these are common patterns, not inventive contributions.

---

## Platform Overview

**StratIQ** is a multi-module enterprise AI platform for IT application/infrastructure rationalization, modernization, and operations intelligence. It is composed of 13 independently deployable full-stack modules sharing a central authentication system, unified behind IIS. A recurring platform-level design pattern — worth calling out as its own inventive thread — is the **"local-LLM-first with deterministic fallback"** architecture: nearly every module that uses an LLM (via local Ollama) pairs it with a rule-based/statistical fallback path so that scoring, classification, and recommendations remain available and reproducible even when the LLM is unreachable, and so that "countable" facts are computed deterministically while only genuinely fuzzy judgments are delegated to the model.

---

## 1. AppRationalization — Multi-Source Application Portfolio Rationalization Engine

**Keywords:** application rationalization, entity resolution, golden record, 4R disposition, fuzzy matching, hybrid rule/LLM scoring, data reconciliation

**Technical Problem Addressed:**
Enterprises hold fragmented, disconnected records of the same application across code-quality tools (CAST), infrastructure inventories, and industry classification sources, with no reliable key to join them. Manual reconciliation and disposition (Retire/Replace/Re-platform/Retain) is a 6–8 week analyst-driven exercise prone to inconsistency and bias.

**Description of the Invention:**
- A cascading multi-tier entity-resolution engine that reconciles records across CAST and infrastructure datasets using progressively looser match strategies: direct application-ID match → server-name match → exact application-name match → `SequenceMatcher`-based fuzzy name match with length-ratio pre-filtering and confidence scoring (`backend/app/services/correlation_service.py`).
- A "golden record" builder that coalesces values from multiple disagreeing sources (CORENT, CAST, Industry, workspace) into one authoritative record, tracking per-field provenance — which fields were sourced directly vs. AI/heuristically imputed (`backend/app/services/golden_data_service.py`).
- A hybrid disposition-scoring engine combining a deterministic weighted rule model (signals: cloud readiness, missing source code, coupling, COTS status, mainframe dependency) with batch LLM-based prediction and robust JSON-array extraction from model output (`backend/app/services/ollama_service.py`).

**Inventive Step (X-factor):**
The rule-based scorer and the LLM-based scorer are designed to produce equivalent-shape output and the system falls back to the rule engine transparently when the LLM is unavailable — disposition scoring never fails or blocks, only degrades in nuance. Combined with the cascading fuzzy-match resolver, this turns disconnected multi-source enterprise data into one reconciled, always-available "golden record" without manual spreadsheet work.

**Advantages Over Alternatives:**
Off-the-shelf ITAM/APM tools require clean, pre-joined data or manual mapping; this engine auto-resolves entities across heterogeneous sources with confidence scoring, and remains operational (with graceful quality degradation) without any external LLM API dependency or connectivity.

**Development Status:** In production use as the platform's central data-reconciliation and auth backend.

---

## 2. CodeAnalysis — Multi-Language Static Analysis & Modernization Scoring Engine

**Keywords:** technical debt costing, defect prediction, legacy migration complexity, CO2 estimation, AI grounding, knowledge graph, COCOMO II

**Technical Problem Addressed:**
There is no standardized, explainable way to quantify technical debt cost, defect risk, cloud-migration complexity, or environmental impact across a heterogeneous, 15+ language codebase spanning legacy mainframe (COBOL/JCL/PL-I) through modern stacks — and generic LLM code review tools hallucinate incompatible modernization suggestions (e.g., recommending Node.js for COBOL).

**Description of the Invention:**
- COCOMO II-derived technical-debt cost model: `Effort(PM) = 2.94 × KSLOC^0.91 × EM_complexity × EM_reliability`, translated into a USD debt figure via a debt-fraction curve (`metrics/technical_debt.py`).
- A logistic-regression-style defect predictor whose feature weights are explicitly sourced from published empirical software-engineering studies (Zimmermann 2008, Nagappan 2006, Menzies 2010), combining sigmoid-normalized complexity, size, duplication, and nesting signals (`services/ml_predictions.py`).
- A legacy-migration-complexity scorer combining keyword-detected legacy technology signals (COBOL/CICS, EJB/WAS, Struts, SOAP, Panvalet) with SLOC log-scaling and a language-diversity penalty (`services/ml_predictions.py`).
- A CO2/energy-reduction estimator that converts SLOC and cloud-maturity gap into estimated on-prem server count, kWh consumption, and CO2 tons saved by migrating to cloud, using EPA grid emission factors (`metrics/co2_reduction.py`).
- An **anti-hallucination grounding layer**: builds a ground-truth fact base from static analysis results and validates/rewrites LLM-generated modernization suggestions against an incompatible-technology-stack matrix before the report is emitted (`services/ai_grounding.py`).
- A language-agnostic knowledge/call-graph builder using per-language AST and regex extractors across 15+ languages to power dependency and architecture-layer analysis (`services/knowledge_graph.py`, `services/call_graph.py`).

**Inventive Step (X-factor):**
The combination of (a) academically-grounded, cited defect/complexity/debt formulas rather than arbitrary heuristics, and (b) a post-generation LLM output validator that mechanically blocks technology-incompatible modernization suggestions before they reach a report — giving statistically defensible, hallucination-resistant modernization guidance across a very wide (including mainframe) language surface.

**Advantages Over Alternatives:**
Generic static-analysis SaaS tools rarely support legacy mainframe languages or quantify debt in currency/CO2 terms tied to real cost models; adding an explicit incompatibility-matrix grounding pass is a targeted defense against a known LLM failure mode that competitors using raw LLM code review do not address.

**Development Status:** In production use; supports 15+ languages including COBOL/JCL/PL-I.

---

## 3. InfraRationalization — Multi-Protocol Infrastructure Discovery, DR Feasibility & IaC Generation

**Keywords:** agentless discovery, dependency graph, migration wave planning, RTO/RPO gap analysis, IaC generation, PDF asset extraction, hypervisor consolidation

**Technical Problem Addressed:**
Enterprises lack a unified, protocol-agnostic way to discover real (as opposed to documented) infrastructure topology, quantify disaster-recovery gaps against stated requirements, and produce ready-to-use migration artifacts — asset data is frequently locked in unstructured legacy CMDB PDF exports rather than a live system of record.

**Description of the Invention:**
- A multi-protocol agentless discovery engine unifying nmap/socket sweeps, ARP/SNMP walks (via pysnmp), and SSH-based OS/CPU/storage/virtualization fingerprinting into one normalized `DiscoveredServer` model (`scanner/onprem.py`).
- A PDF-based infrastructure extractor that parses unstructured legacy CMDB/asset PDFs (with OCR fallback via pdfplumber), auto-detects the cloud provider referenced, and segments free text into structured per-server records via regex block segmentation (`scanner/pdf_scanner.py`).
- A dependency-graph-driven migration wave planner: builds a directed server graph from ARP/route/LLDP neighbor data plus port-based role classification (database/middleware/web/app tiers), applies Kahn's topological sort, and assigns migration waves ordered by computed effort score (`services/dependency_migration.py`).
- An RTO/RPO feasibility engine that cross-references stated DR requirements against detected HA tier, replication configuration, and load-balancer presence to compute a gap list and a 0–100 recovery-readiness score (`services/bcdr_analysis.py`).
- Zombie/orphan/duplicate-service decommissioning detection and a hypervisor consolidation calculator (`services/decommission.py`, `services/hypervisor_consolidation.py`).
- Multi-cloud Infrastructure-as-Code auto-generation (Terraform / ARM / CloudFormation) directly from scan reports (`scanner/iac_generator.py`).

**Inventive Step (X-factor):**
Fusing three normally-separate data-collection modes — live agentless network scanning, SNMP topology walks, *and* OCR-based extraction from legacy PDF documentation — into a single discovery model, then feeding that unified topology directly into a dependency-ordered wave planner and DR-gap scorer, and finally into ready-to-apply IaC output, closes the loop from "unknown legacy estate" to "deployable migration plan" without manual re-entry at any stage.

**Advantages Over Alternatives:**
Most discovery tools require either agents on every host or a pre-existing, accurate CMDB; this engine works from network scanning alone and can additionally recover topology locked in static PDF documentation, then automatically sequences migration waves by real dependency order rather than manual guesswork.

**Development Status:** In production use.

---

## 4. Modernization — LLM-Driven Multi-Target Code Transpilation Platform (with IDE Integration)

**Keywords:** code transpilation, legacy modernization, LLM persona routing, adaptive context sizing, conversion caching, domain-driven decomposition, Copilot Chat extension

**Technical Problem Addressed:**
Rewriting legacy source code (Java, .NET, JSP, etc.) into a modern target stack is slow, language-pair-specific, and typically requires per-project custom tooling; no existing tool offers configurable multi-target transpilation spanning both conventional web stacks and industrial control-system targets, embedded directly into a developer's IDE workflow.

**Description of the Invention:**
- A configurable target-stack catalog of 12+ conversion targets — including an unusual industrial-manufacturing target (AVEVA MES), Spring Boot, Blazor, React, and Oracle→Postgres/Mongo/MSSQL database-dialect migration — each with a dedicated LLM persona and per-language-pair conversion hint library (`services/modernizer.py`).
- Adaptive LLM resource sizing: computes the minimal required Ollama context window from prompt character count, and estimates the output token budget from source LOC × target-language verbosity ratio, avoiding both truncation and over-allocation (`services/modernizer.py`).
- Content-hash-based conversion caching (SHA-256 over source + target stack + language) to skip redundant LLM calls on repeat conversions (`services/modernizer.py`).
- Domain-driven decomposition that combines keyword detection, Java/Kotlin package-structure analysis, and directory-based fallback heuristics to auto-suggest microservice boundaries when decomposing a monolith (`services/analyzer.py`).
- A bundled VS Code extension that registers a **native GitHub Copilot Chat participant** (`@modernizer`, with `/modernizeFile` and `/modernizeSelection` commands) alongside a custom sidebar, both calling the same backend conversion API — embedding legacy modernization directly into the developer's existing Copilot workflow rather than requiring a separate web tool (`vscode-extension/`).

**Inventive Step (X-factor):**
The combination of (a) a broad, persona-routed multi-target catalog spanning web frameworks *and* an industrial MES target, (b) adaptive prompt/context sizing driven by measured source complexity rather than fixed limits, and (c) surfacing the same conversion engine as a first-class Copilot Chat participant inside the IDE — collapsing "modernize this file" into a native chat command instead of a context switch to a browser tool.

**Advantages Over Alternatives:**
Competing "AI code migration" tools are typically single-target (e.g., only Java→Java-modern) and browser-only; this platform's persona-per-target design and adaptive sizing generalize across very different target ecosystems (including non-web industrial targets) while the Copilot integration keeps the workflow inside the tool developers already use daily.

**Development Status:** In production use.

---

## 5. Novastra-ITSM — Grounded RAG Incident-Resolution Assistant (11-Stage Anti-Hallucination Pipeline)

**Keywords:** retrieval-augmented generation, anti-hallucination, cross-encoder reranking, evidence gating, multi-backend vector store, ITSM knowledge retrieval

**Technical Problem Addressed:**
General-purpose LLMs fabricate plausible but false IT/SAP identifiers (incident numbers, transaction codes, error codes, SolMan IDs) when used to answer support/incident questions, making them unsafe for grounded enterprise knowledge retrieval without a verification layer.

**Description of the Invention — the 11-stage pipeline** (`backend/rag/pipeline.py`):
1. **Metadata lookup** — regex-extracts INC/SolMan/delivery identifiers from the query and exact-matches them against the store before any semantic search runs.
2. **Multi-angle vector search** — decomposes the query into short/description/symptom sub-queries run in parallel to counter embedding dilution from long ticket text.
3. **Keyword/regex-entity search** — a lexical fallback plus a dedicated regex signal search for error codes, stack tokens, T-codes, and job keys, used as a fast path for short queries.
4. **Solution-chunk sibling augmentation** — pulls linked resolution chunks for already-matched sources.
5. **Cross-encoder reranking** (FlashrankRerank, ms-marco-MiniLM-L-12-v2) reorders merged candidates by true relevance, capped to the top 6, with a "fast semantic mode" that skips reranking when the top score already exceeds a high-confidence threshold.
6. **Strict evidence gate** — blocks the LLM call entirely if the top/average rerank scores fall below configured thresholds, rather than letting a weak-evidence answer be generated.
7. **Regex-first solution extraction** — pulls verbatim resolution/close-notes text before the LLM is ever invoked.
8. **Direct-answer short-circuit** — when a chunk already contains an explicit solution, the LLM is instructed only to *format* it, not *discover* an answer.
9. **Rule-based post-generation validation** — every identifier (INC/delivery/SolManID/T-code/error code) cited in the LLM's answer must appear verbatim in the retrieved context, or the entire answer is discarded and replaced with a deterministic fallback.
10. **Context-only prompting** with banned generic hedge phrases ("typically", "in general") enforced by both the prompt and post-hoc string matching.
11. **Temperature = 0** decoding with tuned repeat-penalty for deterministic, non-creative output.

**Additional distinctive mechanisms:** a scenario-classification fallback engine that, instead of a generic "no answer found," produces a structured response tailored to the diagnostic pattern detected (file-lock, JDBC, integration-flow, job-execution); a pluggable multi-backend vector store (LanceDB / Qdrant / Postgres+pgvector / hybrid dual-write) letting retrieval route per backend; and an async job pattern for long-running automation analysis, polled via a job-status endpoint.

**Inventive Step (X-factor):**
Rather than relying on a single retrieval-then-generate step, the pipeline layers seven independent verification/gating mechanisms (metadata match, multi-angle retrieval, reranking, evidence-score gating, regex-verbatim extraction, direct-answer short-circuiting, and post-hoc citation validation) so that no fact can reach the user unless it is independently traceable to source text — a defense-in-depth approach to LLM grounding rather than a single-pass mitigation.

**Advantages Over Alternatives:**
Standard RAG implementations perform one retrieval pass and trust the LLM's synthesis; this pipeline mechanically rejects ungrounded answers post-generation (stage 9) even if earlier stages let a hallucination slip through, and runs entirely on local GPU inference (LanceDB + Ollama) with no external vector-DB or API dependency required.

**Development Status:** In production use; most architecturally complex module in the platform.

---

## 6. Dashboard — Executive ITSM Intelligence & Automation-ROI Scoring Engine

**Keywords:** automation opportunity scoring, ROI quantification, in-memory data cache, LLM enrichment, offline degradation

**Technical Problem Addressed:**
Leadership needs a defensible, quantified view of which recurring ITSM ticket categories are worth automating and the expected hours/cost saved — not just raw incident volume dashboards.

**Description of the Invention:**
- A multi-factor, 100-point automation-opportunity scoring model combining Volume (0–30, normalized against the global maximum), Repetition (0–20, from unique-description ratio), Cycle-time (0–20, inverted so short cycles score higher), Assignment-group load concentration (0–15), priority-derived complexity (0–10), and ticket ageing (0–5) into one ranked list, with `estimated_hours_saved_monthly` computed from ticket count × average cycle time × a 0.6 automation-yield factor (`backend/automation.py`).
- Local LLM enrichment layered on top of the deterministic score — a separate Ollama pass classifies automation type, risk, and rationale per candidate, with cache pre-warming after each data sync to eliminate first-request latency (`backend/ollama_service.py`).
- A thread-safe singleton in-memory data cache (double-checked locking) holding refreshable pandas DataFrames on a scheduled cycle, with graceful degradation to an offline XLSX fallback and Qdrant-backed persistence of critical alerts that survives backend restarts (`backend/data_cache.py`).

**Inventive Step (X-factor):**
Separating a fully deterministic, auditable 100-point scoring formula from an LLM enrichment layer that only adds qualitative rationale — so the ranked priority order is reproducible and defensible to leadership even though it is enriched with natural-language explanation.

**Advantages Over Alternatives:**
Generic ITSM analytics dashboards report volume/trend charts; this engine directly outputs a ranked, ROI-quantified automation backlog, and keeps all inference (Ollama, Qdrant) confined to localhost so ticket data and RCA notes never leave the on-premise boundary.

**Development Status:** In production use.

---

## 7. LabRobot — Physics-Based Digital-Twin Robot Fleet Simulator with Physical-Device Bridge

**Keywords:** digital twin, MQTT command bridge, inventory reconciliation, physics simulation, collision-aware path planning

**Technical Problem Addressed:**
Integrating industrial robot fleet software (welding, assembly, inspection, AMR) against real hardware early in a project is expensive and slow; teams need a simulated environment that can later bridge to physical devices without re-architecting the control/telemetry layer.

**Description of the Invention:**
- A digital-twin-to-physical command bridge over MQTT (`backend/robot_service.py`) featuring idempotent command enqueue keyed by command ID, priority/FIFO dispatch gated on robot idleness, and an acknowledgement state machine that maps device-reported statuses (e.g. `arrived_rack`, `scan_complete`, `placed_on_conveyor`) to command lifecycle transitions.
- Automatic inventory reconciliation on physical task completion — rack inventory is decremented and conveyor inventory incremented only once a real device acknowledgement confirms the item transfer, keeping the digital twin's state consistent with the physical world.
- A real-time physics engine with Newtonian kinematics, velocity clamping, friction decay, sphere-collision detection that triggers an immediate error state and event log entry, and battery drain/charge modeling tied to motion state (`backend/simulation_engine.py`).
- Point-to-segment collision-aware path interpolation for waypoint generation and obstacle-distance checking.

**Inventive Step (X-factor):**
The same command/ack/inventory data model drives both the simulated robot and a real physical device over MQTT, so the "digital twin" is not just a visualization layer but the actual control-and-inventory system of record — physical device acknowledgements are the only trigger that commits an inventory state change, preventing the twin from drifting out of sync with reality.

**Advantages Over Alternatives:**
Many robot simulators are purely visual/offline; this design lets the same command queue and inventory logic operate identically whether the target is a simulated or a physical robot, so integration testing done in simulation transfers directly to hardware deployment.

**Development Status:** In production use for simulation; physical-device bridge implemented via MQTT (hardware-dependent for full validation).

---

## 8. SSDLC_Process_Assessment — Weighted Maturity Scoring Engine + CSM Consolidation Savings Model

**Keywords:** secure SDLC maturity, weighted scoring, LLM output contract, formula audit trail, tower consolidation savings

**Technical Problem Addressed:**
Secure-SDLC maturity self-assessments are inherently subjective; converting them into defensible, weighted scores and prioritized gap-closure guidance without letting an LLM silently miscalculate arithmetic is an unsolved reliability problem for AI-assisted assessment tools. Separately, the bundled CSM ("Consolidation Savings Model") sub-application needs every IT tower-consolidation savings figure to be independently auditable for finance sign-off.

**Description of the Invention:**
- A weighted-maturity formula (dimension-category base weight × maturity-level multiplier: 0.50 / 0.65 / 0.82 / 1.00) enforced by constraining the LLM's output to a fixed `WEIGHT:` / `ACTIONS:` contract, parsed via regex and clamped to a 1–10 range rather than trusting free-form LLM arithmetic (`backend/app/ollama_client.py`).
- A "no heuristic fallback" policy: if the local LLM is unreachable, the weighted-prediction function returns null rather than fabricating a plausible-looking score (`backend/app/ollama_client.py`, `backend/app/service.py`).
- Streaming, structured CISO executive-briefing generation constrained to a fixed section template.
- Dual-source maturity-level resolution merging spreadsheet-driven templates with a legacy SQLite state table.
- **CSM engine** (`backend/app/csm/`): every savings calculation returns a formula-level audit object — the expression, its inputs, and the result — aggregated into a self-documenting financial calculation trail; all monetary math uses `Decimal` with explicit `ROUND_HALF_UP` rounding to avoid floating-point drift in financial output, and the engine is deployable both embedded and as a standalone microservice.

**Inventive Step (X-factor):**
Rather than trusting an LLM's numeric output directly, the system constrains the model to emit a structured, regex-parseable weight token that is then clamped and combined deterministically — and explicitly refuses to fabricate a score when the model is offline. The CSM's formula-audit-object pattern applies the same "never trust an opaque number" philosophy to financial calculations, returning full expression provenance alongside every result.

**Advantages Over Alternatives:**
Most AI-assisted maturity/assessment tools let the LLM produce the final score directly, which is neither reproducible nor auditable; here the LLM only supplies a bounded input to a deterministic formula, and every financial output is self-documenting for audit purposes.

**Development Status:** In production use; CSM available both embedded and as standalone service.

---

## 9. OpportunityTracker — Deterministic/LLM-Split Wave Planning Engine

**Keywords:** migration wave planning, deterministic classification, bin-packing, hallucination-resistant disposition, custom signed token

**Technical Problem Addressed:**
Automated application-portfolio wave planning tools that delegate classification and sequencing entirely to an LLM produce inconsistent, non-reproducible migration plans because LLMs are unreliable at "countable" tasks (grouping, counting, sequencing) even though they are useful for genuinely fuzzy judgment calls.

**Description of the Invention:**
- A deliberate deterministic/LLM split: migration-type classification, wave assignment, and department clustering are computed in pure, auditable Python (`backend/wave_deterministic.py`); only genuinely fuzzy calls — such as Harmonization-vs-Modernization disposition or archival-candidate detection — are routed to the LLM (`backend/wave_llm_service.py`). This split is documented in-repo as an empirical response to observed LLM hallucination on countable data.
- A regex-based eligibility pre-filter that hard-overrides the LLM's disposition output to "Harmonization" for ineligible applications regardless of what the model returns, preventing the LLM from contradicting a known-deterministic rule.
- A custom bin-packing wave-assignment algorithm: solo waves for large departments, greedy largest-remaining-first bundling toward a target wave size, closest-to-band pilot selection, and a remediation-rejoin step for flagged data — reverse-engineered and validated against a real historical worked example.
- Every wave-assignment decision emits a fact-cited rationale string generated by the deterministic code itself (not the LLM), giving a traceable "why" for each placement.
- A custom self-contained signed token format (`ot1.{body}.{HMAC-SHA256 signature}`) implemented without a JWT library, intentionally scoped independently from the platform's shared auth system.

**Inventive Step (X-factor):**
Architecturally separating "what an LLM is good at" (fuzzy disposition judgment) from "what it is bad at" (counting, grouping, sequencing) at the code level, with a hard regex override that can veto the LLM's fuzzy output when it conflicts with a known deterministic rule — producing wave plans that are both LLM-assisted and fully reproducible/auditable.

**Advantages Over Alternatives:**
Competing "AI migration planner" tools that ask an LLM to produce the whole wave plan in one pass are prone to silently drifting counts and inconsistent groupings across runs; this split-architecture guarantees the countable parts of the plan are identical on every run while still benefiting from LLM judgment on the genuinely ambiguous parts.

**Development Status:** In production use.

---

## 10. AI_Reman_Core — Remanufactured-Parts Inspection Scoring Schema

**Keywords:** remanufacturing, warranty tiering, defect-penalty scoring, life-expectancy prediction

**Technical Problem Addressed:**
Determining whether a used automotive/industrial core (e.g., starter motor, alternator) is salvage, limited-pass, or full-warranty-eligible after remanufacturing requires converting itemized defect findings into a single warranty decision with a defensible predicted service life.

**Description of the Invention:**
- A per-core-type specification table (`CORE_SPECS`: maximum life, base warranty period, confidence) combined with per-defect `life_penalty` values that are summed to compute a `predicted_life_years` figure, which is then tiered into Salvage / Pass-Limited-Warranty / Pass-Full-Warranty bands (`backend/main.py`).

**Inventive Step (X-factor):**
The calibrated per-core-type life curve combined with additive defect-penalty aggregation and threshold-based warranty tiering is a defined, reusable scoring schema — the inventive contribution is this schema itself (the structure of how defect findings compose into a life/warranty decision), independent of the detection method that feeds it.

**Development Status — important caveat for the IDD filing:** This module's defect *detection* is currently a placeholder — matching is done via filename-substring checks rather than trained computer-vision inference, and its `/api/stats` endpoint returns randomly generated placeholder values. **The scoring/tiering schema is the genuine inventive artifact; it is not yet paired with a working detection backend.** Any IDD claim on this module should be scoped to the scoring/tiering method, flagged as prototype-stage pending real CV/ML integration.

---

## 11. AI_Vehicle_Loan — Conversational Vehicle Loan Pre-Qualification Agent

**Keywords:** loan tiering, intent classification, conversational agent, token-overlap similarity

**Technical Problem Addressed:**
Combining rapid, explainable loan pre-qualification with natural-language vehicle discovery in a single conversational interface, without a full LLM round-trip on every conversational turn.

**Description of the Invention:**
- Deterministic tiered underwriting logic combining credit score and debt-to-income thresholds into named risk tiers (e.g. Platinum Prime / Gold / Silver), each driving an interest rate, approval status, and a maximum-loan-amount formula (`income × scope_factor`) computed in a single pass (`api/loan_engine.py`).
- An intent-routed conversational agent that uses regex-based intent classification (eligibility check vs. vehicle discovery vs. fallback) to decide the response path, rather than sending every user turn through the LLM (`api/agent_service.py`).
- A token-overlap similarity scorer that ranks vehicle matches by query/description token-set intersection, explicitly designed as a drop-in stand-in for a future embedding-based vector search (`api/vector_db_stub.py`).

**Inventive Step (X-factor):**
The regex-based intent router avoids invoking the LLM for structurally simple turns, reducing latency and cost while keeping the tiered underwriting fully deterministic and explainable.

**Advantages Over Alternatives:** Faster and cheaper than routing every conversational turn through an LLM, while keeping the loan decision itself fully auditable.

**Development Status:** Prototype/scaffold stage — the credit data source is a synthetic profile generator and the vector search is an explicit stub intended to be replaced with a real credit-bureau feed and embedding-based search; rule-based, not yet ML-trained. Limited standalone patentability until real data integrations replace the stubs.

---

## 12. Microsite_Data_Analysis — StratIQ Tower Consolidation Studio

**Keywords:** IT tower consolidation, spreadsheet-to-SPA migration, vendor rationalization heatmap, reinvestment allocation

**Technical Problem Addressed:**
IT spend/vendor "tower consolidation" financial models typically live in large, fragile Excel workbooks that are hard to scenario-test or share interactively; there is no direct path from a validated spreadsheet model to a reactive web tool without re-deriving the underlying formulas.

**Description of the Invention:**
- A faithful JavaScript reimplementation of a multi-factor savings decomposition chain — `addressableSpend → {efficiency, rate, vendor-management} savings → grossAnnualCapacity → netYear1Capacity` — explicitly cross-referenced line-by-line against the original spreadsheet blueprint (`src/calculations.js`).
- A weighted multi-criteria "Vendor Rationalization Heatmap" score blending spend, vendor count, strategic importance, and complexity via configurable weights into a single 0–100 priority index (`calculateHeatmapScore()`).
- A reinvestment allocation engine that redistributes the net savings capacity pool across strategic investment areas by configurable allocation percentage (`calculateReinvestment()`).

**Inventive Step (X-factor):**
The productization pattern itself — taking a finance-team-owned, formula-validated Excel model and mechanically porting it into a parameterized, scenario-testable web calculation engine while preserving exact blueprint semantics — is the reusable inventive pattern, more than the underlying financial math (which is standard consolidation-savings arithmetic).

**Development Status:** In production use.

---

## 13. Supply Chain Disruption Manager — Sense→Understand→Act Multi-Agent Governance Platform

**Keywords:** signal normalization, blast-radius graph traversal, multi-agent orchestration, human-in-the-loop approval, severity rule engine

**Technical Problem Addressed:**
Enterprises receive noisy, heterogeneous disruption signals from ERP/WMS/TMS/MES systems with no governed, explainable way to determine downstream impact and automatically dispatch the right remediation response while keeping high-risk actions under human control.

**Description of the Invention:**
- A six-stage signal normalizer pipeline (validate → dedupe → enrich → severity → retag → publish) that converts adapter-specific payloads into one canonical event envelope (`services/signal-inspector/src/inspector/normalizer/pipeline.py`).
- A YAML-driven declarative severity rule engine supporting gte/lte/gt/lt/eq/neq comparisons against arbitrary payload fields, hot-reloadable without a redeploy (`services/signal-inspector/src/inspector/normalizer/severity.py`).
- Idempotent event deduplication using Redis `SET NX` with a 24-hour TTL, keyed on `source_system:source_event_id` (`services/signal-inspector/src/inspector/normalizer/dedupe.py`).
- A Neo4j-backed "blast radius" traversal — variable-depth, direction-aware, edge-kind-filtered BFS via Cypher — plus transitive ownership resolution through chained FLOW/META relationship edges, to compute which systems/processes are impacted by a given disruption (`services/kg-service/src/kg/repositories/traversal_repo.py`).
- An orchestrator state machine (`NEW → CLASSIFIED → DISPATCHED → IN_PROGRESS → RESOLVED/BLOCKED/AWAITING_APPROVAL`) that fans out to up to 7 domain-specialist AI agents in parallel, each scope-checked against its allowed action set, with automatic detection of irreversible actions that force escalation to human approval (`services/agent-service/src/agents/orchestrator/agent.py`, `.../specialists/base.py`).
- A disruption-type-to-specialist dispatch map combined with a severity-threshold approval override and a rejection-triggered replanning loop (`services/agent-service/src/agents/orchestrator/planner.py`).

**Inventive Step (X-factor):**
The full pipeline — canonicalized signal ingestion → graph-based blast-radius computation → multi-agent parallel remediation dispatch → automatic irreversible-action detection with human-approval escalation — forms a closed-loop, governed autonomous response system. The irreversible-action auto-escalation check is the key safety mechanism: it inspects a specialist agent's proposed action against a defined "irreversible" classification before execution, rather than relying on the agent's own judgment about when to ask for permission.

**Advantages Over Alternatives:**
Most supply-chain "control tower" products are dashboards with manual triage; this platform closes the loop with autonomous multi-agent remediation while a structural (not prompt-based) safety gate — the irreversible-action detector — prevents runaway autonomous action, addressing the core trust barrier to autonomous supply-chain response. This is architecturally the platform's strongest overall patentability candidate: a true microservices design (separate signal-inspector, kg-service, and agent-service, each independently deployable) rather than a monolith, with an LLM-optional mode (`MOCK_AGENTS`) that swaps in deterministic mocks for local Ollama-backed reasoning without code changes.

**Development Status:** In production use; deployed via Docker Compose or native Windows/IIS.

---

## Summary Table — Development Status & Patentability Signal

| # | Module | Core Inventive Mechanism | Status | Patentability Signal |
|---|--------|--------------------------|--------|----------------------|
| 1 | AppRationalization | Cascading fuzzy entity resolution + golden record + hybrid rule/LLM disposition | Production | Strong |
| 2 | CodeAnalysis | Cited empirical defect/debt models + LLM output grounding against incompatibility matrix | Production | Strong |
| 3 | InfraRationalization | Tri-modal discovery (scan+SNMP+PDF/OCR) → dependency-ordered wave planning → IaC | Production | Strong |
| 4 | Modernization | Persona-routed multi-target transpilation + adaptive context sizing + native Copilot Chat integration | Production | Strong |
| 5 | Novastra-ITSM | 11-stage defense-in-depth RAG anti-hallucination pipeline | Production | Very strong |
| 6 | Dashboard | Deterministic 100-point automation-ROI scoring + LLM enrichment layer | Production | Moderate |
| 7 | LabRobot | MQTT digital-twin/physical bridge with ack-gated inventory reconciliation | Production | Moderate–Strong |
| 8 | SSDLC_Process_Assessment / CSM | Constrained LLM output contract for weighted scoring + formula-audit-trail savings engine | Production | Strong |
| 9 | OpportunityTracker | Deterministic/LLM-split wave planning with regex veto override | Production | Strong |
| 10 | AI_Reman_Core | Defect-penalty life/warranty tiering schema | **Prototype (scoring schema only, no real detection backend)** | Moderate, scope-limited |
| 11 | AI_Vehicle_Loan | Regex intent-routed conversational agent + deterministic loan tiering | **Prototype (stubbed data sources)** | Weak, scope-limited |
| 12 | Microsite_Data_Analysis | Spreadsheet-to-SPA formula migration pattern | Production | Moderate |
| 13 | Supply Chain Disruption Manager | Signal→graph→multi-agent governance loop with structural irreversible-action gate | Production | Very strong |

---

*Document generated via full-repository search across all 13 StratIQ modules on 2026-07-08. Findings are cited to specific source files; verify current line numbers against the working tree before filing, as source may have changed since this survey.*
