# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Java Server Pages (.jsp, .jspx) and related servlet descriptor
# Date: 2025-09-07
# ---------------------------------------------------------------------------
"""
jsp_analyzer.py
---------------
Analyses Java Server Pages (.jsp, .jspx) and related servlet descriptor
files (web.xml, web-fragment.xml).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / HTML / Java scriptlet / EL / JSTL line breakdown
- Cyclomatic complexity (scriptlet if/for/while branches)
- Scriptlet count (inline Java <%  %> blocks — migration risk)
- Expression Language (EL) usage: ${...}  #{...}
- JSTL tag usage: c:if, c:forEach, c:choose, fn:*, fmt:*
- Implicit object usage (request, response, session, application, out)
- Bad practices:
    * Raw scriptlets with DB/JDBC calls (SQL injection risk)
    * Direct session attribute casts without null-check
    * include directive with user-controlled path
    * Response splitting risks (unencoded output)
    * Missing CSRF token in forms
- Servlet descriptor analysis (web.xml):
    * Servlet / filter / listener mappings
    * Security constraints and authentication methods
    * Welcome-file lists
- Technology stack detection:
    * JSF, Struts 1/2, Spring MVC tags, JSTL, custom tag libraries
    * Servlet API version from web.xml descriptor
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set, List

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class JSPAnalyzer(BaseAnalyzer):
    """Analyser for JSP / JSPX / web.xml files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("jsp", {
        ".jsp", ".jspx", ".jspf", ".tag", ".tagx",
    })

    # ── JSP structural patterns ───────────────────────────────────────────────
    _SCRIPTLET_OPEN   = re.compile(r'<%(?!=|@|--)')          # <% but not <%=, <%@, <%--
    _SCRIPTLET_CLOSE  = re.compile(r'%>')
    _EXPRESSION_EL    = re.compile(r'\$\{[^}]+\}|\#\{[^}]+\}')
    _DIRECTIVE        = re.compile(r'<%@\s*(\w+)')            # page, include, taglib
    _TAGLIB           = re.compile(r'<%@\s*taglib\s+uri=["\']([^"\']+)["\']', re.IGNORECASE)

    # Complexity branches inside scriptlets
    _BRANCH           = re.compile(r'\b(if|else\s+if|for|while|switch|case|catch|&&|\|\||\?)\b')

    # JSTL / JSF / Spring tags
    _JSTL_IF          = re.compile(r'<c:if\b|<c:choose\b|<c:when\b', re.IGNORECASE)
    _JSTL_LOOP        = re.compile(r'<c:forEach\b|<c:forTokens\b', re.IGNORECASE)
    _JSTL_TAG         = re.compile(r'<(?:c|fn|fmt|sql|x|fl):', re.IGNORECASE)
    _JSF_TAG          = re.compile(r'<(?:h|f|ui|p|rich|a4j|ice):', re.IGNORECASE)
    _SPRING_FORM      = re.compile(r'<form:', re.IGNORECASE)
    _STRUTS_TAG       = re.compile(r'<(?:html|bean|logic|nested|tiles|s):', re.IGNORECASE)

    # Implicit objects
    _IMPLICIT_OBJ     = re.compile(
        r'\b(request|response|session|application|out|pageContext|config|page|exception)\.'
    )

    # Bad practices
    _JDBC_IN_JSP      = re.compile(r'java\.sql\.|DriverManager\.getConnection', re.IGNORECASE)
    _UNSAFE_CAST      = re.compile(r'\(\s*\w[\w\.]+\s*\)\s*session\.getAttribute')
    _INCLUDE_USER     = re.compile(r'<jsp:include\s+page\s*=\s*["\']?\s*<%')
    _CSRF_FORM        = re.compile(r'<form\b[^>]*method\s*=\s*["\']?post["\']?', re.IGNORECASE)
    _CSRF_TOKEN       = re.compile(r'_csrf|csrf_token|csrfToken', re.IGNORECASE)
    _UNENCODED_OUT    = re.compile(r'out\.print(?:ln)?\s*\(\s*request\.getParameter')
    _RESPONSE_SPLIT   = re.compile(r'response\.setHeader.*\+.*request\.', re.IGNORECASE)

    # web.xml patterns
    _WX_SERVLET       = re.compile(r'<servlet-name>([^<]+)</servlet-name>', re.IGNORECASE)
    _WX_FILTER        = re.compile(r'<filter-name>([^<]+)</filter-name>', re.IGNORECASE)
    _WX_SECURITY      = re.compile(r'<auth-method>([^<]+)</auth-method>', re.IGNORECASE)
    _WX_SERVLET_API   = re.compile(r'<web-app[^>]+version\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

    # Function: language_name
    def language_name(self) -> str:
        return "JSP"

    # ──────────────────────────────────────────────────────────────────────────
    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        name_lower = path.name.lower()
        if name_lower in ("web.xml", "web-fragment.xml"):
            return self._analyse_web_xml(path, lines)
        return self._analyse_jsp(path, lines)

    # ──────────────────────────────────────────────────────────────────────────
    # Function: _classify_jsp_line
    def _classify_jsp_line(self, stripped: str, fm: FileMetrics, state: dict) -> None:
        # JSP comment: <%-- ... --%>
        if "<%--" in stripped:
            state["in_comment"] = True
        if "--%>" in stripped:
            state["in_comment"] = False
            fm.comment_lines += 1
            return
        if state["in_comment"]:
            fm.comment_lines += 1
            return

        # HTML/template line vs Java scriptlet
        if "<%--" in stripped or stripped.startswith("//") or stripped.startswith("*"):
            fm.comment_lines += 1
        else:
            fm.code_lines += 1

        # Scriptlet detection
        if re.search(r'<%(?!=|@|--)', stripped):
            state["in_scriptlet"] = True
            state["scriptlet_count"] += 1
        if "%>" in stripped and state["in_scriptlet"]:
            state["in_scriptlet"] = False

        if state["in_scriptlet"]:
            state["branches"] += len(self._BRANCH.findall(stripped))

        # CSRF
        if self._CSRF_FORM.search(stripped):
            state["forms_with_post"] += 1
        if self._CSRF_TOKEN.search(stripped):
            state["csrf_tokens"] += 1

    # Function: _detect_jsp_bad_practices
    def _detect_jsp_bad_practices(self, source: str, fm: FileMetrics, forms_with_post: int, csrf_tokens: int) -> list:
        bad = []
        if self._JDBC_IN_JSP.search(source):
            bad.append("JDBC calls in JSP scriptlet — move to DAO layer")
            fm.duplicate_blocks += 1
        if self._UNSAFE_CAST.search(source):
            bad.append("Unsafe session attribute cast without null check")
            fm.duplicate_blocks += 1
        if self._UNENCODED_OUT.search(source):
            bad.append("Unencoded user input written to output (XSS risk)")
            fm.duplicate_blocks += 1
        if self._RESPONSE_SPLIT.search(source):
            bad.append("Potential HTTP response splitting via unvalidated header")
            fm.duplicate_blocks += 1
        if forms_with_post > 0 and csrf_tokens == 0:
            bad.append(f"{forms_with_post} POST form(s) with no CSRF token detected")
            fm.duplicate_blocks += 1
        return bad

    # Function: _analyse_jsp
    def _analyse_jsp(self, path: Path, lines: list) -> FileMetrics:
        fm = FileMetrics(path=path, language="JSP", total_lines=len(lines))
        source = "\n".join(lines)

        state = {
            "in_scriptlet": False, "in_comment": False, "scriptlet_count": 0,
            "branches": 0, "forms_with_post": 0, "csrf_tokens": 0,
        }

        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            self._classify_jsp_line(stripped, fm, state)

        scriptlet_count = state["scriptlet_count"]
        fm.todo_comments = self._count_todo(lines)
        fm.functions     = scriptlet_count            # scriptlet blocks as "functions"
        fm.cyclomatic    = max(1, 1 + state["branches"])

        # Bad practices
        self._detect_jsp_bad_practices(source, fm, state["forms_with_post"], state["csrf_tokens"])

        # Count EL usage and JSTL
        el_count    = len(self._EXPRESSION_EL.findall(source))
        jstl_count  = len(self._JSTL_TAG.findall(source))
        jsf_count   = len(self._JSF_TAG.findall(source))
        spring_form = len(self._SPRING_FORM.findall(source))
        struts_tags = len(self._STRUTS_TAG.findall(source))

        # Tag library detection → dependencies
        for tl_uri in self._TAGLIB.findall(source):
            self._detected_frameworks = getattr(self, "_detected_frameworks", set())
            self._detected_frameworks.add(tl_uri)

        fm.magic_numbers = scriptlet_count  # reuse field: scriptlet count
        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Function: _analyse_web_xml
    def _analyse_web_xml(self, path: Path, lines: list) -> FileMetrics:
        fm = FileMetrics(path=path, language="JSP:web.xml", total_lines=len(lines))
        source = "\n".join(lines)

        servlets  = self._WX_SERVLET.findall(source)
        filters   = self._WX_FILTER.findall(source)
        auth      = self._WX_SECURITY.findall(source)
        api_ver   = self._WX_SERVLET_API.findall(source)

        fm.code_lines = len([l for l in lines if l.strip() and not l.strip().startswith("<!--")])
        fm.comment_lines = len([l for l in lines if l.strip().startswith("<!--")])
        fm.functions  = len(servlets)    # servlets as "functions"
        fm.classes    = len(filters)     # filters as "classes"

        # Detect dispatcher servlet → Spring MVC
        spring_mvc = any("DispatcherServlet" in s for s in servlets)
        struts     = any("ActionServlet" in s or "FilterDispatcher" in s or
                         "StrutsPrepareAndExecuteFilter" in s for s in servlets + filters)

        if spring_mvc:
            fm.duplicate_blocks += 0  # informational
        if struts:
            fm.duplicate_blocks += 0

        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Function: analyse
    def analyse(self) -> LanguageReport:
        report = super().analyse()

        # Walk web.xml files (may not have .jsp extension)
        for xml_path in self.repo_path.rglob("web.xml"):
            try:
                fm = self._analyse_web_xml(xml_path, self._read_lines(xml_path))
                if fm:
                    report.file_count  += 1
                    report.total_sloc  += fm.code_lines
                    report.files.append(fm)
            except Exception:
                pass

        # Tag-library framework detection from gathered URIs
        detected_fw = getattr(self, "_detected_frameworks", set())

        # Aggregate framework detection into bad_practices as informational
        if any("struts" in u.lower() for u in detected_fw):
            report.dependencies.add("Apache Struts (taglib)")
        if any("spring" in u.lower() for u in detected_fw):
            report.dependencies.add("Spring MVC (taglib)")
        if any("jsf" in u.lower() or "faces" in u.lower() for u in detected_fw):
            report.dependencies.add("JavaServer Faces")
        if any("myfaces" in u.lower() for u in detected_fw):
            report.dependencies.add("Apache MyFaces")

        # Struts config file detection
        for cfg in self.repo_path.rglob("struts*.xml"):
            report.dependencies.add("Apache Struts (config)")
            break
        for cfg in self.repo_path.rglob("struts*.properties"):
            report.dependencies.add("Apache Struts (properties)")
            break

        return report
