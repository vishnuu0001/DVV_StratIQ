# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Java source files using regular-expression and heuristic techniques.
# Date: 2026-03-10
# ---------------------------------------------------------------------------
"""
java_analyzer.py
----------------
Analyses Java source files using regular-expression and heuristic techniques.

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch counting)
- Class & method counts
- Long methods, deep nesting, magic numbers, TODO markers
- Bad-practice detection: empty catch blocks, System.out usage, raw types,
  god classes, public field exposure
- Dependency extraction from pom.xml / build.gradle
- Enterprise framework detection:
    * Spring MVC / Spring Boot annotations
    * Struts 1 / Struts 2 action classes and config
    * REST endpoints (JAX-RS, Spring @*Mapping)
    * SOAP web services (JAX-WS, @WebService, @WebMethod)
    * Servlet API (HttpServlet, @WebServlet, doGet/doPost)
    * EJB 3.x annotations (@Stateless, @Stateful, @Singleton, @MessageDriven)
    * IBM WAS proprietary API usage (com.ibm.*, javax.ejb.*)
    * JMS / messaging (@JmsListener, javax.jms.*)
    * JSF (javax.faces.*, @ManagedBean)
    * Hibernate / JPA persistence annotations
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class JavaAnalyzer(BaseAnalyzer):
    """Analyser for Java (.java) source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS["java"]

    # Patterns that increase cyclomatic complexity
    _BRANCH_PATTERNS = re.compile(
        r'\b(if|else\s+if|for|while|case|catch|&&|\|\||\?)\b'
    )
    _METHOD_PATTERN = re.compile(
        r'(?:public|private|protected|static|final|synchronized|abstract|native)'
        r'(?:\s+\w+)*\s+\w+\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{',
        re.MULTILINE
    )
    _CLASS_PATTERN = re.compile(
        r'\b(?:class|interface|enum|record)\s+\w+'
    )
    _EMPTY_CATCH = re.compile(
        r'catch\s*\([^)]*\)\s*\{[\s]*\}'
    )
    _SYSOUT = re.compile(r'System\.(out|err)\.(print|println|printf)\s*\(')
    _RAW_TYPE = re.compile(r'\b(List|Map|Set|Collection|Iterator)\s+\w+\s*[=;,)]')

    # ── Spring MVC / Spring Boot ─────────────────────────────────────────────
    _SPRING_CTRL    = re.compile(
        r'@(Controller|RestController|RequestMapping|GetMapping|PostMapping|'
        r'PutMapping|DeleteMapping|PatchMapping|ResponseBody|PathVariable|'
        r'RequestParam|RequestBody|CrossOrigin)\b',
        re.IGNORECASE
    )
    _SPRING_BEAN    = re.compile(
        r'@(Service|Repository|Component|Autowired|Inject|Bean|Configuration|'
        r'SpringBootApplication|EnableAutoConfiguration|'
        r'EnableWebMvc|ControllerAdvice|ExceptionHandler)\b',
        re.IGNORECASE
    )
    _SPRING_SECURITY= re.compile(
        r'@(PreAuthorize|PostAuthorize|Secured|EnableMethodSecurity|'
        r'EnableWebSecurity|WithMockUser)\b',
        re.IGNORECASE
    )

    # ── Struts 1 / Struts 2 ──────────────────────────────────────────────────
    _STRUTS1_ACTION = re.compile(
        r'(extends\s+Action\b|extends\s+DispatchAction|extends\s+MappingDispatchAction|'
        r'implements\s+Action\b|ActionForm\b|ActionMapping\b|ActionForward\b)',
        re.IGNORECASE
    )
    _STRUTS2_ACTION = re.compile(
        r'(@Action\b|@Result\b|@Results\b|extends\s+ActionSupport\b|'
        r'implements\s+ModelDriven\b)',
        re.IGNORECASE
    )

    # ── Servlets ─────────────────────────────────────────────────────────────
    _SERVLET        = re.compile(
        r'(extends\s+HttpServlet\b|extends\s+GenericServlet\b|'
        r'implements\s+Servlet\b|@WebServlet\b|'
        r'void\s+doGet\s*\(|void\s+doPost\s*\(|void\s+doPut\s*\(|void\s+doDelete\s*\()',
        re.IGNORECASE
    )
    _SERVLET_FILTER = re.compile(
        r'(implements\s+Filter\b|@WebFilter\b|doFilter\s*\()', re.IGNORECASE
    )

    # ── SOAP / JAX-WS ────────────────────────────────────────────────────────
    _SOAP_SERVICE   = re.compile(
        r'(@WebService\b|@WebMethod\b|@SOAPBinding\b|@WebParam\b|@WebResult\b|'
        r'javax\.xml\.ws\.|javax\.jws\.|'
        r'SOAPMessage\b|SOAPFault\b|SOAPBody\b|SOAPEnvelope\b|'
        r'Service\.create\s*\(|Dispatch<)',
        re.IGNORECASE
    )
    _WSDL_IMPORT    = re.compile(r'import\s+.*\.wsdl\b|WSDL_LOCATION', re.IGNORECASE)

    # ── REST (JAX-RS / Spring) ───────────────────────────────────────────────
    _REST_JAXRS     = re.compile(
        r'@(javax\.ws\.rs\.|jakarta\.ws\.rs\.|Path\b|GET\b|POST\b|PUT\b|DELETE\b|'
        r'PATCH\b|Produces\b|Consumes\b|QueryParam\b|PathParam\b|'
        r'FormParam\b|HeaderParam\b|BeanParam\b)',
        re.IGNORECASE
    )
    _REST_OPENAPI   = re.compile(
        r'@(Operation\b|ApiResponse\b|Tag\b|Schema\b|Parameter\b|'
        r'io\.swagger\.|springdoc\.)',
        re.IGNORECASE
    )

    # ── EJB 3.x ─────────────────────────────────────────────────────────────
    _EJB            = re.compile(
        r'@(Stateless\b|Stateful\b|Singleton\b|MessageDriven\b|EJB\b|'
        r'Remote\b|Local\b|LocalBean\b|TransactionManagement\b|'
        r'TransactionAttribute\b|Schedule\b|Schedules\b)',
        re.IGNORECASE
    )

    # ── IBM WAS / WebSphere ──────────────────────────────────────────────────
    _IBM_WAS        = re.compile(
        r'import\s+com\.ibm\.(websphere|wsspi|ws|ejs|bbo|connector)\.',
        re.IGNORECASE
    )

    # ── JMS / Messaging ──────────────────────────────────────────────────────
    _JMS            = re.compile(
        r'(import\s+javax\.jms\.|@JmsListener\b|@RabbitListener\b|'
        r'@KafkaListener\b|JmsTemplate\b|MessageProducer\b|MessageConsumer\b)',
        re.IGNORECASE
    )

    # ── JPA / Hibernate ──────────────────────────────────────────────────────
    _JPA            = re.compile(
        r'@(Entity\b|Table\b|Column\b|Id\b|GeneratedValue\b|OneToMany\b|'
        r'ManyToOne\b|ManyToMany\b|OneToOne\b|JoinColumn\b|NamedQuery\b|'
        r'Query\b|TypedQuery\b)',
        re.IGNORECASE
    )

    # ── JSF ──────────────────────────────────────────────────────────────────
    _JSF            = re.compile(
        r'(import\s+javax\.faces\.|@ManagedBean\b|@ViewScoped\b|'
        r'@SessionScoped\b|@RequestScoped\b|@ApplicationScoped\b|FacesContext\b)',
        re.IGNORECASE
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Java"

    # ──────────────────────────────────────────────────────────────────────────
    # Single-file analysis
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm = FileMetrics(path=path, language="Java", total_lines=len(lines))
        source = "\n".join(lines)

        # Strip block comments for some counts
        stripped_source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)

        # Line classification
        in_block = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            if '/*' in stripped:
                in_block = True
            if in_block:
                fm.comment_lines += 1
                if '*/' in stripped:
                    in_block = False
                continue
            if stripped.startswith('//') or stripped.startswith('*'):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        fm.todo_comments = self._count_todo(lines)
        fm.magic_numbers = self._count_magic_numbers(lines)
        fm.commented_out_lines = self._count_commented_out_code(lines)
        fm.max_depth     = self._max_nesting_depth(lines)
        fm.deep_nesting  = self._deep_nesting_count(lines, threshold=4)

        # Structure counts (compute before complexity so we can normalize)
        fm.functions = len(self._METHOD_PATTERN.findall(source))
        fm.classes   = len(self._CLASS_PATTERN.findall(source))

        # Cyclomatic complexity — per-method average (branch count / method count)
        raw_branches = len(self._BRANCH_PATTERNS.findall(stripped_source))
        method_count = max(fm.functions, 1)
        fm.cyclomatic = max(1, round((1 + raw_branches) / method_count))

        # Long methods estimated via line count between opening braces
        fm.long_methods = self._count_long_methods(source)

        # Java-specific bad practices (stored as fm attributes for aggregation)
        fm.duplicate_blocks += (
            len(self._EMPTY_CATCH.findall(source))
            + len(self._SYSOUT.findall(source))
            + len(self._RAW_TYPE.findall(source))
        )

        # ── Enterprise framework signals ────────────────────────────────────
        # Store per-file counts as extra attrs (accessed in analyse())
        fm._spring_ctrl    = len(self._SPRING_CTRL.findall(source))
        fm._spring_bean    = len(self._SPRING_BEAN.findall(source))
        fm._struts1        = len(self._STRUTS1_ACTION.findall(source))
        fm._struts2        = len(self._STRUTS2_ACTION.findall(source))
        fm._servlet        = len(self._SERVLET.findall(source))
        fm._soap           = len(self._SOAP_SERVICE.findall(source))
        fm._rest           = len(self._REST_JAXRS.findall(source)) + \
                             len(self._REST_OPENAPI.findall(source)) + \
                             len(self._SPRING_CTRL.findall(source))
        fm._ejb            = len(self._EJB.findall(source))
        fm._ibm_was        = len(self._IBM_WAS.findall(source))
        fm._jms            = len(self._JMS.findall(source))
        fm._jpa            = len(self._JPA.findall(source))
        fm._jsf            = len(self._JSF.findall(source))

        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Repository-level augments
    # ──────────────────────────────────────────────────────────────────────────

    # Function: analyse
    def analyse(self) -> LanguageReport:
        report = super().analyse()
        report = self._detect_java_bad_practices(report)
        report = self._detect_enterprise_frameworks(report)
        return report

    # Function: _detect_java_bad_practices
    def _detect_java_bad_practices(self, report: LanguageReport) -> LanguageReport:
        empty_catch = sysout = raw_types = 0
        for fm in report.files:
            empty_catch += fm.duplicate_blocks   # reused field for Java-specific count
        if empty_catch:
            report.bad_practices.append(f"Empty catch blocks / sysout / raw types: {empty_catch}")

        # God class detection (class with > 20 methods)
        god_classes = sum(
            1 for fm in report.files
            if fm.classes > 0
            and fm.functions / max(fm.classes, 1) > 20
        )
        if god_classes:
            report.bad_practices.append(f"Potential God Classes (>20 methods): {god_classes}")
        return report

    # Function: _detect_enterprise_frameworks
    def _detect_enterprise_frameworks(self, report: LanguageReport) -> LanguageReport:
        """Aggregate enterprise framework usage across all Java files."""
        totals = {
            "spring_ctrl": 0, "spring_bean": 0,
            "struts1": 0, "struts2": 0,
            "servlet": 0, "soap": 0, "rest": 0,
            "ejb": 0, "ibm_was": 0, "jms": 0,
            "jpa": 0, "jsf": 0,
        }
        for fm in report.files:
            for key in totals:
                totals[key] += getattr(fm, f"_{key}", 0)

        # Spring MVC / Spring Boot
        if totals["spring_ctrl"] + totals["spring_bean"] > 0:
            report.dependencies.add(
                f"Spring MVC/Boot ({totals['spring_ctrl']} controller + "
                f"{totals['spring_bean']} bean annotations)"
            )

        # Struts
        if totals["struts1"] > 0:
            report.dependencies.add(f"Apache Struts 1 ({totals['struts1']} action pattern(s))")
            report.bad_practices.append(
                f"Struts 1 patterns detected ({totals['struts1']}) — "
                f"EOL framework, migrate to Spring MVC or Quarkus."
            )
        if totals["struts2"] > 0:
            report.dependencies.add(f"Apache Struts 2 ({totals['struts2']} action pattern(s))")

        # Check for struts config files
        for cfg in self.repo_path.rglob("struts*.xml"):
            report.dependencies.add("Apache Struts (XML config)")
            break

        # Servlets
        if totals["servlet"] > 0:
            report.dependencies.add(f"Java Servlets ({totals['servlet']} pattern(s))")

        # SOAP
        if totals["soap"] > 0:
            report.dependencies.add(f"SOAP/JAX-WS ({totals['soap']} web service annotation(s))")
            report.bad_practices.append(
                f"SOAP web services detected ({totals['soap']}) — "
                f"consider REST/gRPC migration for modern interoperability."
            )

        # REST
        if totals["rest"] > 0:
            report.dependencies.add(f"REST API ({totals['rest']} endpoint annotation(s))")

        # EJB
        if totals["ejb"] > 0:
            report.dependencies.add(f"EJB 3.x ({totals['ejb']} annotation(s))")
            report.bad_practices.append(
                f"EJB annotations detected ({totals['ejb']}) — "
                f"EJBs are tightly coupled to app server; consider CDI/Spring beans."
            )

        # IBM WAS
        if totals["ibm_was"] > 0:
            report.dependencies.add(f"IBM WebSphere API ({totals['ibm_was']} import(s))")
            report.bad_practices.append(
                f"IBM WAS proprietary API usage ({totals['ibm_was']}) — "
                f"creates vendor lock-in; abstract behind interfaces for portability."
            )

        # JMS
        if totals["jms"] > 0:
            report.dependencies.add(f"JMS/Messaging ({totals['jms']} usage(s))")

        # JPA / Hibernate
        if totals["jpa"] > 0:
            report.dependencies.add(f"JPA/Hibernate ({totals['jpa']} annotation(s))")

        # JSF
        if totals["jsf"] > 0:
            report.dependencies.add(f"JavaServer Faces ({totals['jsf']} usage(s))")

        return report

    # ──────────────────────────────────────────────────────────────────────────
    # Dependency extraction
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()

        # Maven pom.xml
        for pom in self.repo_path.rglob("pom.xml"):
            src = pom.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(
                r'<artifactId>([\w\-\.]+)</artifactId>', src
            ):
                deps.add(m.group(1))

        # Gradle build.gradle / build.gradle.kts
        for gradle in self.repo_path.rglob("build.gradle*"):
            src = gradle.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(
                r'(?:implementation|compile|api|testImplementation)'
                r'\s*["\']([^:]+:[^:]+:[^"\']+)["\']', src
            ):
                parts = m.group(1).split(":")
                if len(parts) >= 2:
                    deps.add(parts[1])

        return deps

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _count_long_methods
    @staticmethod
    def _count_long_methods(source: str, threshold: int = 40) -> int:
        """Heuristically count methods whose body spans more than threshold lines."""
        count  = 0
        depth  = 0
        start  = None
        lines  = source.splitlines()
        for i, line in enumerate(lines):
            opens  = line.count("{")
            closes = line.count("}")
            if depth == 0 and opens > 0:
                start = i
            depth += opens - closes
            if depth <= 0 and start is not None:
                if (i - start) > threshold:
                    count += 1
                depth = 0
                start = None
        return count
