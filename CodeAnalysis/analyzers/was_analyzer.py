# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses IBM WebSphere Application Server (WAS / Liberty) artifacts.
# Date: 2026-03-22
# ---------------------------------------------------------------------------
"""
was_analyzer.py
---------------
Analyses IBM WebSphere Application Server (WAS / Liberty) artifacts.

Detects and metrics:
  - IBM WAS deployment descriptors (ibm-web-bnd.xml, ibm-ejb-jar-bnd.xml,
    ibm-application-bnd.xml, ibm-web-ext.xml, server.xml [Liberty])
  - EJB descriptors (ejb-jar.xml, ibm-ejb-jar-bnd.xml)
  - Proprietary IBM API usage in Java source (com.ibm.*, javax.ejb.*,
    javax.naming.InitialContext, DataSource JNDI lookups)
  - WAS-specific JNDI patterns (java:comp/env, eis/, jms/)
  - IBM MQ / JMS usage (com.ibm.mq.*, javax.jms.*)
  - IBM security APIs (com.ibm.websphere.security.*)
  - WAS Runtime configuration complexity score
  - Liberty feature detection (featureManager in server.xml)
  - Migration readiness assessment:
      * WAS Traditional → Liberty migration blockers
      * WAS → OpenLiberty / Quarkus / Spring Boot migration effort

Metrics produced
~~~~~~~~~~~~~~~~
  - was_descriptor_count    : number of ibm-*.xml files found
  - ejb_count               : EJB declarations
  - ibm_api_usage_count     : com.ibm.* package references
  - jndi_lookup_count       : JNDI lookup calls
  - jms_usage_count         : JMS / MQ usage
  - proprietary_api_score   : 0-100 portability risk (100 = max vendor lock-in)
  - liberty_features         : list of enabled Liberty features
  - migration_complexity     : low / medium / high / very_high
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, List, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class WASAnalyzer(BaseAnalyzer):
    """
    IBM WebSphere Application Server (WAS / Liberty) artifact analyzer.
    Processes both Java source files AND WAS XML descriptor files.
    """

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("was", {
        # WAS / Liberty descriptors
        ".xml",        # ibm-*.xml, ejb-jar.xml, server.xml
        # Java source (we restrict by path heuristics below)
        ".java",
        # Properties / resource files
        ".properties",
    })

    # ── IBM API detection patterns ────────────────────────────────────────────
    _IBM_API_PKG    = re.compile(r'import\s+(com\.ibm\.[a-zA-Z\.]+)\s*;')
    _IBM_WAS_PKG    = re.compile(r'import\s+(com\.ibm\.websphere\.[a-zA-Z\.]+)\s*;')
    _IBM_MQ_PKG     = re.compile(r'import\s+(com\.ibm\.mq\.[a-zA-Z\.]+)\s*;')
    _EJB_PKG        = re.compile(r'import\s+(javax\.ejb\.[a-zA-Z\.]+)\s*;')
    _JNDI_LOOKUP    = re.compile(r'InitialContext\(\)|ctx\.lookup\s*\(|context\.lookup\s*\(', re.IGNORECASE)
    _JNDI_STRING    = re.compile(r'"(java:comp/env/|eis/|jms/|jdbc/)[^"]*"')
    _JMS_USAGE      = re.compile(r'import\s+javax\.jms\.|QueueConnectionFactory|TopicConnectionFactory', re.IGNORECASE)
    _WAS_SECURITY   = re.compile(r'com\.ibm\.websphere\.security\.|WSSubject\.|WSLoginHelper\.')
    _WAS_TXMGR      = re.compile(r'com\.ibm\.websphere\.uow\.|UserTransaction|TransactionManager\b')
    _SERVLET_CTX    = re.compile(r'@WebServlet|@Stateless|@Stateful|@Singleton|@MessageDriven', re.IGNORECASE)
    _WSADMIN_CMD    = re.compile(r'\bwsadmin\b|\bAdminConfig\b|\bAdminApp\b|\bAdminControl\b')
    _ADMIN_SCRIPT   = re.compile(r'\.py$')               # wsadmin Jython scripts

    # ── Descriptor XML patterns ───────────────────────────────────────────────
    _EJB_DECL       = re.compile(r'<enterprise-beans>|<session>|<entity>|<message-driven>', re.IGNORECASE)
    _LIBERTY_FEATURE= re.compile(r'<feature>([^<]+)</feature>', re.IGNORECASE)
    _BINDING_JNDI   = re.compile(r'jndi-name\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    _RESOURCE_REF   = re.compile(r'<resource-ref>|<resource-env-ref>|<ejb-ref>', re.IGNORECASE)
    _SECURITY_ROLE  = re.compile(r'<security-role>|<security-constraint>', re.IGNORECASE)
    _WAS_VERSION    = re.compile(r'was\.version\s*=\s*(\d[\d\.]+)', re.IGNORECASE)

    # ── Files to analyse (restrict XML to WAS-specific names) ────────────────
    _WAS_XML_NAMES  = {
        "ibm-web-bnd.xml", "ibm-web-ext.xml",
        "ibm-ejb-jar-bnd.xml", "ibm-ejb-jar-ext.xml",
        "ibm-application-bnd.xml", "ibm-application-ext.xml",
        "ibm-application.xml",
        "ejb-jar.xml",
        "server.xml",              # Liberty server config
        "ibm-ws-bnd.xml",
        "was.policy",
    }

    # Function: language_name
    def language_name(self) -> str:
        return "IBM WAS"

    # Cheap plain-substring tokens checked before the full regex suite runs (see
    # _analyse_java) — a lowercase `in` scan over the raw text is far cheaper than
    # running 7 compiled regexes (4 findall + 3 search) against every single
    # .java file in the repo, which previously happened unconditionally even for
    # the (typically large) majority of files with no WAS/IBM signal at all.
    # MUST cover every alternative in every regex referenced by the early-return
    # gate in _analyse_java (ibm/was/mq imports, ejb imports, _JNDI_LOOKUP,
    # _JMS_USAGE, _SERVLET_CTX) — note _JNDI_LOOKUP also matches bare
    # "ctx.lookup("/"context.lookup(" (no "jndi" substring), and _JMS_USAGE also
    # matches "QueueConnectionFactory"/"TopicConnectionFactory" (no "jms"
    # substring), so "lookup" and "connectionfactory" are required, not optional.
    _CHEAP_PREFILTER_TOKENS = (
        "ibm", "ejb", "jms", "jndi", "initialcontext", "lookup", "connectionfactory",
        "@webservlet", "@stateless", "@stateful", "@singleton", "@messagedriven",
    )

    # Function: _should_analyse
    def _should_analyse(self, path: Path) -> bool:
        name = path.name.lower()
        # Always analyse WAS XML descriptors
        if name in self._WAS_XML_NAMES:
            return True
        # Only analyse .java files if they contain IBM-specific imports
        if path.suffix == ".java":
            return True
        # wsadmin scripts
        if name.startswith("wsadmin") and path.suffix == ".py":
            return True
        return False

    # ──────────────────────────────────────────────────────────────────────────
    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None
        name_lower = path.name.lower()
        if path.suffix == ".java":
            return self._analyse_java(path, lines)
        if name_lower in self._WAS_XML_NAMES or name_lower.startswith("ibm-"):
            return self._analyse_descriptor(path, lines)
        return None

    # ──────────────────────────────────────────────────────────────────────────
    # Function: _analyse_java
    def _analyse_java(self, path: Path, lines: list) -> Optional[FileMetrics]:
        source = "\n".join(lines)

        # Cheap reject: skip the full regex suite entirely if none of the
        # plain-substring tokens are present at all (case-insensitive). Every
        # one of the 7 regexes below requires at least one of these tokens to
        # ever match, so this is a pure fast-path with no change in results.
        lowered = source.lower()
        if not any(tok in lowered for tok in self._CHEAP_PREFILTER_TOKENS):
            return None

        ibm_apis   = self._IBM_API_PKG.findall(source)
        ibm_was    = self._IBM_WAS_PKG.findall(source)
        ibm_mq     = self._IBM_MQ_PKG.findall(source)
        ejb_pkgs   = self._EJB_PKG.findall(source)

        if not (ibm_apis or ibm_was or ibm_mq or ejb_pkgs or
                self._JNDI_LOOKUP.search(source) or
                self._JMS_USAGE.search(source) or
                self._SERVLET_CTX.search(source)):
            return None   # Not WAS-related Java

        fm = FileMetrics(path=path, language="IBM WAS", total_lines=len(lines))
        for line in lines:
            s = line.strip()
            if not s:
                fm.blank_lines += 1
            elif s.startswith("//") or s.startswith("*") or "/*" in s:
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        # Count vendor lock-in signals
        lock_in = (
            len(ibm_was) * 3 +    # WAS-specific APIs = highest lock-in
            len(ibm_mq)  * 2 +    # MQ APIs = medium lock-in
            len(ibm_apis)     +
            len(ejb_pkgs)     +
            len(self._JNDI_LOOKUP.findall(source)) * 2 +
            len(self._JNDI_STRING.findall(source)) +
            len(self._JMS_USAGE.findall(source)) +
            (3 if self._WAS_SECURITY.search(source) else 0) +
            (2 if self._WAS_TXMGR.search(source) else 0)
        )
        fm.duplicate_blocks = lock_in    # reuse for lock-in score

        # EJB type detection
        ejb_types = len(self._SERVLET_CTX.findall(source))
        fm.functions = ejb_types
        fm.classes   = len(re.findall(r'\bclass\s+\w+', source))

        fm.todo_comments = self._count_todo(lines)
        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Function: _analyse_descriptor
    def _analyse_descriptor(self, path: Path, lines: list) -> FileMetrics:
        fm = FileMetrics(path=path, language="IBM WAS:Descriptor", total_lines=len(lines))
        source = "\n".join(lines)

        fm.code_lines    = sum(1 for l in lines if l.strip() and not l.strip().startswith("<!--"))
        fm.comment_lines = sum(1 for l in lines if l.strip().startswith("<!--"))

        # Liberty features
        features = self._LIBERTY_FEATURE.findall(source)
        fm.functions = len(features)  # features as "functions"

        # EJB declarations
        fm.classes = len(self._EJB_DECL.findall(source))

        # JNDI bindings
        jndi_bindings = len(self._BINDING_JNDI.findall(source))
        resource_refs = len(self._RESOURCE_REF.findall(source))
        fm.duplicate_blocks = jndi_bindings + resource_refs

        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Function: _scan_java_files
    def _scan_java_files(self, report: LanguageReport) -> int:
        """Scan Java files for IBM API usage; returns total lock-in score."""
        total_lock_in = 0
        for java_path in self.repo_path.rglob("*.java"):
            try:
                fm = self._analyse_java(java_path, self._read_lines(java_path))
                if fm:
                    report.file_count   += 1
                    report.total_sloc   += fm.code_lines
                    report.total_functions = getattr(report, "total_functions", 0) + fm.functions
                    report.total_classes   = getattr(report, "total_classes", 0) + fm.classes
                    total_lock_in          += fm.duplicate_blocks
                    report.files.append(fm)
            except Exception:
                pass
        return total_lock_in

    # Function: _scan_was_descriptors
    def _scan_was_descriptors(self, report: LanguageReport) -> "tuple[List[str], Set[str], int]":
        was_xml_found: List[str] = []
        liberty_features: Set[str] = set()
        ejb_count = 0
        for xml_name in self._WAS_XML_NAMES:
            for xml_path in self.repo_path.rglob(xml_name):
                try:
                    lines = self._read_lines(xml_path)
                    source = "\n".join(lines)
                    fm = self._analyse_descriptor(xml_path, lines)
                    if fm:
                        was_xml_found.append(xml_name)
                        report.file_count += 1
                        report.total_sloc += fm.code_lines
                        ejb_count += fm.classes
                        # Extract Liberty features for dependency tracking
                        feats = self._LIBERTY_FEATURE.findall(source)
                        liberty_features.update(feats)
                        report.files.append(fm)
                except Exception:
                    pass
        return was_xml_found, liberty_features, ejb_count

    # Function: _scan_wsadmin_scripts
    def _scan_wsadmin_scripts(self, report: LanguageReport) -> None:
        for py_path in self.repo_path.rglob("wsadmin*.py"):
            try:
                fm = self._analyse_java(py_path, self._read_lines(py_path))
                if fm:
                    report.file_count += 1
                    report.total_sloc += fm.code_lines
                    report.files.append(fm)
            except Exception:
                pass

    # Function: _append_was_bad_practices
    @staticmethod
    def _append_was_bad_practices(
        report: LanguageReport, prop_score: int, migration_complexity: str,
        ejb_count: int, liberty_features: Set[str],
    ) -> None:
        if prop_score >= 50:
            report.bad_practices.append(
                f"High IBM WAS vendor lock-in score ({prop_score}/100) — "
                f"heavy com.ibm.*/javax.ejb.* API usage detected. "
                f"Migration to Liberty/Quarkus/Spring Boot requires significant effort."
            )
        if ejb_count > 0:
            report.bad_practices.append(
                f"{ejb_count} EJB declaration(s) found — EJBs are hard to containerize; "
                f"consider migration to CDI beans or Spring components."
            )
        if any("jca-1" in f or "rar-" in f for f in liberty_features):
            report.bad_practices.append(
                "JCA/RAR connector detected — requires IBM-specific connector bridge for cloud migration."
            )

        report.bad_practices.append(
            f"WAS Migration Complexity: {migration_complexity.upper()} "
            f"({prop_score}/100 lock-in score, {ejb_count} EJBs, "
            f"{len(liberty_features)} Liberty features)"
        )

    # Function: analyse
    def analyse(self) -> LanguageReport:
        """Walk repo and analyse only WAS-relevant files."""
        report = LanguageReport(language=self.language_name())

        total_lock_in = self._scan_java_files(report)
        was_xml_found, liberty_features, ejb_count = self._scan_was_descriptors(report)
        self._scan_wsadmin_scripts(report)

        if report.file_count == 0:
            return report

        # Populate report fields
        total_files = max(report.file_count, 1)
        all_cc = [f.cyclomatic for f in report.files]
        report.avg_complexity = sum(all_cc) / len(all_cc) if all_cc else 1.0
        report.max_complexity = max(all_cc) if all_cc else 0

        # Proprietary API score: higher = more lock-in = harder to migrate
        # Normalize to 0-100
        prop_score = min(100, int(total_lock_in / max(total_files, 1) * 5))
        migration_complexity = (
            "very_high" if prop_score >= 75 else
            "high"      if prop_score >= 50 else
            "medium"    if prop_score >= 25 else
            "low"
        )

        # Dependencies = detected packages and features
        report.dependencies.update(liberty_features)
        if was_xml_found:
            report.dependencies.add(f"IBM WAS descriptors: {', '.join(set(was_xml_found))}")

        self._append_was_bad_practices(report, prop_score, migration_complexity, ejb_count, liberty_features)

        return report
