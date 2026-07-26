# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Classifies source files into four CAST-style architectural layers:
# Date: 2026-02-05
# ---------------------------------------------------------------------------
"""
architecture_layers.py
----------------------
Classifies source files into four CAST-style architectural layers:

    Presentation  – UI/controller/view code (HTTP handlers, templates, JSX)
    Coordination  – Business logic orchestrators (services, managers, workflows)
    Services      – Data-access, integrations, gateways, clients
    Persistence   – Database models, repositories, ORM entities, migrations

The detection uses package/class naming conventions and import/annotation
patterns common in Java, Python, .NET, and JavaScript projects.

Output
~~~~~~
  ArchitectureReport with per-layer file counts and a nodes list suitable
  for rendering a layered network diagram in the frontend.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ─── Layer definitions ────────────────────────────────────────────────────────

LAYER_PRESENTATION  = "Presentation"
LAYER_COORDINATION  = "Coordination"
LAYER_SERVICES      = "Services"
LAYER_PERSISTENCE   = "Persistence"
LAYER_UNKNOWN       = "Other"

_LAYERS = [
    LAYER_PRESENTATION,
    LAYER_COORDINATION,
    LAYER_SERVICES,
    LAYER_PERSISTENCE,
    LAYER_UNKNOWN,
]

# ─── Classification rules ──────────────────────────────────────────────────────

@dataclass
class _Rule:
    layer:   str
    path_re: Optional[re.Pattern]    # match against relative path
    code_re: Optional[re.Pattern]    # match against file content


_PATH_RULES: List[_Rule] = [
    # Presentation
    _Rule(LAYER_PRESENTATION,
          re.compile(r'(?i)[\\/](controller|controllers|views?|templates?|'
                     r'pages?|screens?|ui|frontend|webapp|web[\\/]|'
                     r'presenters?|forms?|routes?|handlers?)[\\/]'),
          None),
    _Rule(LAYER_PRESENTATION,
          re.compile(r'(?i)(Controller|View|Template|Presenter|Form|'
                     r'Screen|Page|Route|Handler)\.(java|cs|py|jsx?|tsx?)$'),
          None),
    # Coordination
    _Rule(LAYER_COORDINATION,
          re.compile(r'(?i)[\\/](service|services|managers?|processors?|'
                     r'orchestrators?|coordinators?|use_cases?|usecases?|'
                     r'interactors?|commands?|application)[\\/]'),
          None),
    _Rule(LAYER_COORDINATION,
          re.compile(r'(?i)(Service|Manager|Processor|Orchestrator|'
                     r'Coordinator|Interactor|UseCase|Command)'
                     r'\.(java|cs|py|ts|js)$'),
          None),
    # Services / Integration / Gateway
    _Rule(LAYER_SERVICES,
          re.compile(r'(?i)[\\/](api|clients?|gateways?|integration|'
                     r'adapters?|external|connectors?|proxies?|'
                     r'infrastructure)[\\/]'),
          None),
    _Rule(LAYER_SERVICES,
          re.compile(r'(?i)(Client|Gateway|Adapter|Integration|'
                     r'Connector|Proxy|Api)\.(java|cs|py|ts|js)$'),
          None),
    # Persistence
    _Rule(LAYER_PERSISTENCE,
          re.compile(r'(?i)[\\/](repositor|repositories|dao|daos|'
                     r'models?|entities|entity|migrations?|'
                     r'schemas?|orm|db|database|persistence)[\\/]'),
          None),
    _Rule(LAYER_PERSISTENCE,
          re.compile(r'(?i)(Repository|DAO|Entity|Model|Migration|'
                     r'Schema)\.(java|cs|py|ts|js)$'),
          None),
]

_CODE_RULES: List[_Rule] = [
    # Presentation – annotation / framework markers
    _Rule(LAYER_PRESENTATION, None,
          re.compile(r'@(Controller|RestController|GetMapping|PostMapping|'
                     r'RequestMapping|ViewController)|'
                     r'\[HttpGet\]|\[HttpPost\]|\[ApiController\]|'
                     r'@app\.route|@router\.(get|post)'
                     r'|export default function.*\breturn\b.*<[A-Z]',
                     re.MULTILINE)),
    # Coordination
    _Rule(LAYER_COORDINATION, None,
          re.compile(r'@Service|@Component|@ApplicationScoped|'
                     r'\[Service\]|class\s+\w+(Service|Manager|Orchestrator)',
                     re.MULTILINE)),
    # Services / Integration
    _Rule(LAYER_SERVICES, None,
          re.compile(r'RestTemplate|WebClient|HttpClient|requests\.get|'
                     r'axios\.|fetch\(|grpc|@FeignClient|@Gateway',
                     re.MULTILINE)),
    # Persistence
    _Rule(LAYER_PERSISTENCE, None,
          re.compile(r'@Entity|@Repository|@Table|@Column|'
                     r'\[Table\]|\[Column\]|DbContext|'
                     r'class\s+\w+(Repository|DAO|Entity|Model)\b|'
                     r'Base\.Model\b|db\.Model\b|'
                     r'SELECT\s+|INSERT\s+INTO|UPDATE\s+\w+\s+SET',
                     re.MULTILINE | re.IGNORECASE)),
]

# ─── Result types ──────────────────────────────────────────────────────────────

@dataclass
class ArchLayerNode:
    """Single file that has been classified."""
    name:     str    # short display name (last 2 path segments)
    layer:    str
    language: str
    sloc:     int = 0


@dataclass
class ArchitectureLayer:
    name:         str
    file_count:   int
    sloc:         int
    pct:          float       # % of total files
    technologies: List[str]   # languages found in this layer


@dataclass
class ArchitectureReport:
    layers:          List[ArchitectureLayer]
    nodes:           List[ArchLayerNode]     # for graph rendering
    total_files:     int
    layer_counts:    Dict[str, int]          # layer_name → file_count
    layer_sloc:      Dict[str, int]          # layer_name → sloc
    has_data:        bool


# ─── Classifier ───────────────────────────────────────────────────────────────

class ArchitectureLayerAnalyzer:
    """
    Walks a repository and classifies source files into architectural layers.
    """

    _SUPPORTED_EXTS = {
        ".java": "Java", ".py": "Python",
        ".cs": ".NET", ".vb": ".NET",
        ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "JavaScript", ".tsx": "TypeScript",
        ".cbl": "Mainframe", ".cob": "Mainframe",
    }

    _SKIP_DIRS = {
        ".git", "node_modules", "vendor", "venv", ".venv",
        "target", "bin", "obj", "__pycache__", "dist", "build",
    }

    # Function: analyse
    def analyse(self, repo_path: Path) -> ArchitectureReport:
        if repo_path is None or not repo_path.exists():
            return ArchitectureReport(
                layers=[], nodes=[], total_files=0,
                layer_counts={}, layer_sloc={}, has_data=False,
            )
        nodes: List[ArchLayerNode] = []
        layer_counts: Dict[str, int]   = {l: 0 for l in _LAYERS}
        layer_sloc:   Dict[str, int]   = {l: 0 for l in _LAYERS}
        layer_techs:  Dict[str, set]   = {l: set() for l in _LAYERS}

        for src in self._iter_files(repo_path):
            lang    = self._SUPPORTED_EXTS.get(src.suffix.lower(), "Other")
            rel     = src.relative_to(repo_path)
            rel_str = str(rel).replace("\\", "/")
            layer   = self._classify(rel_str, src)
            sloc    = self._count_sloc(src)

            parts   = rel_str.split("/")
            display = "/".join(parts[-2:]) if len(parts) >= 2 else rel_str

            nodes.append(ArchLayerNode(
                name=display, layer=layer, language=lang, sloc=sloc
            ))
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
            layer_sloc[layer]   = layer_sloc.get(layer, 0) + sloc
            layer_techs[layer].add(lang)

        total_files = len(nodes) or 1

        layers = [
            ArchitectureLayer(
                name=l,
                file_count=layer_counts[l],
                sloc=layer_sloc[l],
                pct=round(layer_counts[l] / total_files * 100, 1),
                technologies=sorted(layer_techs[l]),
            )
            for l in _LAYERS
            if layer_counts[l] > 0
        ]

        return ArchitectureReport(
            layers=layers,
            nodes=nodes[:500],        # cap for frontend
            total_files=total_files,
            layer_counts=layer_counts,
            layer_sloc=layer_sloc,
            has_data=total_files > 1,
        )

    # ── Internal ──────────────────────────────────────────────────────────────

    # Function: _classify
    def _classify(self, rel_path: str, src_file: Path) -> str:
        """Return the best-matching layer for this file."""
        # 1. Path-based rules (fast, no I/O)
        for rule in _PATH_RULES:
            if rule.path_re and rule.path_re.search(rel_path):
                return rule.layer

        # 2. Content-based rules
        try:
            text = src_file.read_text(encoding="utf-8", errors="ignore")[:8000]
        except Exception:
            return LAYER_UNKNOWN

        for rule in _CODE_RULES:
            if rule.code_re and rule.code_re.search(text):
                return rule.layer

        return LAYER_UNKNOWN

    # Function: _count_sloc
    def _count_sloc(self, src_file: Path) -> int:
        try:
            return sum(
                1 for ln in src_file.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines()
                if ln.strip() and not ln.strip().startswith(("#", "//", "/*", "*", "<!--"))
            )
        except Exception:
            return 0

    # Function: _iter_files
    def _iter_files(self, repo_path: Path, max_files: int = 2000):
        _MAX_BYTES = 500_000
        count = 0
        for dirpath, dirnames, filenames in os.walk(str(repo_path)):
            dirnames[:] = [d for d in dirnames if d not in self._SKIP_DIRS]
            dir_path = Path(dirpath)
            for fname in filenames:
                if count >= max_files:
                    return
                path = dir_path / fname
                if path.suffix.lower() not in self._SUPPORTED_EXTS:
                    continue
                try:
                    if path.stat().st_size > _MAX_BYTES:
                        continue
                except OSError:
                    continue
                count += 1
                yield path
