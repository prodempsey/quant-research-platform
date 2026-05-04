"""Test 2 — No-live-broker import-boundary (AST scan + dependency-manifest scan).

Maps to: Section 1 Required Tests #2(a) and #2(b)-partial; SDR Decisions 1, 15, 18;
traceability rows Decisions 1, 15, 18.

This module hosts both Test 2(a) (AST scan over src/) and Test 2(b)-partial
(manifest scan over pyproject.toml + requirements.txt) in the same file per
v2 plan §5; if Governor prefers separate files, Builder revises.

Per IN-2 (gate_result #4365423458), Test 2(a) uses an exact-match policy on
the PEP 503-normalized top-level distribution name. The construction rule
for the top-level segment is:
- For Import nodes: leftmost dotted segment of alias.name
- For ImportFrom nodes: leftmost dotted segment of node.module

The Violation.offending_token field for Test 2(a) holds the original
(un-normalized) top-level segment as observed in source, so QA can map the
violation back to the literal import statement. Normalization is applied
only at compare time.

For the manifest scan, distribution names are PEP 503-normalized at compare
time and reported in their original spellings.
"""

from __future__ import annotations

import ast
import re
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "synthetic_bad_imports"

# Broker SDK distribution names. Source: packet §"In-scope behavior" item 5
# minimum (17 names) plus 8 Builder additions per v2 plan §5 Test 2(a). Stored
# as their original spellings; PEP 503 normalization is applied at compare time.
BROKER_SDK_NAMES_RAW: tuple[str, ...] = (
    # Packet minimum (17)
    "schwab",
    "schwab_py",
    "schwab-py",
    "schwabapi",
    "ibapi",
    "ib_insync",
    "ibinsync",
    "ibkr",
    "alpaca",
    "alpaca_trade_api",
    "alpaca-py",
    "tda-api",
    "tda_api",
    "robinhood",
    "robin_stocks",
    "etrade",
    "fidelity",
    # Builder additions (8)
    "td-ameritrade",
    "tdameritrade",
    "ib-async",
    "ib_async",
    "tradier",
    "tradestation",
    "questrade",
    "webull",
)

# EODHD-client distribution names. The manifest scan covers them here (the
# in-source AST scan for the EODHD boundary lives in test_provider_boundary).
EODHD_CLIENT_NAMES_RAW: tuple[str, ...] = (
    "eodhd",
    "eodhd_data",
    "eod_historical_data",
    "eodhistoricaldata",
)


def _normalize_pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


BROKER_SDK_NAMES_NORMALIZED: frozenset[str] = frozenset(
    _normalize_pep503(n) for n in BROKER_SDK_NAMES_RAW
)
EODHD_CLIENT_NAMES_NORMALIZED: frozenset[str] = frozenset(
    _normalize_pep503(n) for n in EODHD_CLIENT_NAMES_RAW
)


@dataclass(frozen=True)
class Violation:
    file_path: Path
    lineno: int
    kind: str
    offending_token: str
    message: str


def _top_level_segment_from_node(node: ast.AST) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            top = alias.name.split(".", 1)[0]
            out.append((top, node.lineno))
    elif isinstance(node, ast.ImportFrom):
        if node.level and node.level > 0:
            raise ValueError(
                "relative import not supported by SCAFFOLD-001 scanner "
                f"(lineno {node.lineno}, level={node.level})"
            )
        module = node.module or ""
        if module:
            top = module.split(".", 1)[0]
            out.append((top, node.lineno))
    return out


def _iter_py_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix == ".py":
            yield root
        return
    yield from root.rglob("*.py")


def scan_python_imports(roots: Iterable[Path]) -> list[Violation]:
    violations: list[Violation] = []
    for root in roots:
        for path in _iter_py_files(root):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Import | ast.ImportFrom):
                    continue
                for top, lineno in _top_level_segment_from_node(node):
                    if _normalize_pep503(top) in BROKER_SDK_NAMES_NORMALIZED:
                        violations.append(
                            Violation(
                                file_path=path,
                                lineno=lineno,
                                kind="no_live_broker_python_import",
                                offending_token=top,
                                message=(
                                    "src/ imports broker-SDK top-level package "
                                    f"{top!r} (PEP 503 normalized: "
                                    f"{_normalize_pep503(top)!r})"
                                ),
                            )
                        )
    return violations


def _leading_distname(spec: str) -> str:
    end = len(spec)
    for ch in (" ", "=", "<", ">", "~", ";", "[", "@"):
        i = spec.find(ch)
        if i != -1 and i < end:
            end = i
    return spec[:end].strip()


def _collect_pyproject_dependency_names(path: Path) -> list[tuple[str, int]]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    names: list[tuple[str, int]] = []
    project = data.get("project") or {}
    for dep in project.get("dependencies") or []:
        names.append((_leading_distname(dep), 1))
    for _group, deps in (project.get("optional-dependencies") or {}).items():
        for dep in deps:
            names.append((_leading_distname(dep), 1))
    build = data.get("build-system") or {}
    for dep in build.get("requires") or []:
        names.append((_leading_distname(dep), 1))
    return names


def _collect_requirements_names(path: Path) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    text = path.read_text(encoding="utf-8")
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append((_leading_distname(line), lineno))
    return out


def scan_dependency_manifests(
    pyproject_path: Path | None = None,
    requirements_path: Path | None = None,
) -> list[Violation]:
    violations: list[Violation] = []
    forbidden = BROKER_SDK_NAMES_NORMALIZED | EODHD_CLIENT_NAMES_NORMALIZED

    if pyproject_path is not None and pyproject_path.exists():
        for raw_name, lineno in _collect_pyproject_dependency_names(pyproject_path):
            if _normalize_pep503(raw_name) in forbidden:
                violations.append(
                    Violation(
                        file_path=pyproject_path,
                        lineno=lineno,
                        kind="no_live_broker_pyproject_manifest",
                        offending_token=raw_name,
                        message=(
                            "pyproject.toml declares forbidden distribution "
                            f"{raw_name!r} (PEP 503 normalized: "
                            f"{_normalize_pep503(raw_name)!r})"
                        ),
                    )
                )
    if requirements_path is not None and requirements_path.exists():
        for raw_name, lineno in _collect_requirements_names(requirements_path):
            if _normalize_pep503(raw_name) in forbidden:
                violations.append(
                    Violation(
                        file_path=requirements_path,
                        lineno=lineno,
                        kind="no_live_broker_requirements_manifest",
                        offending_token=raw_name,
                        message=(
                            "requirements.txt declares forbidden distribution "
                            f"{raw_name!r} (PEP 503 normalized: "
                            f"{_normalize_pep503(raw_name)!r})"
                        ),
                    )
                )
    return violations


def test_no_live_broker_python_imports_production_case_is_clean() -> None:
    violations = scan_python_imports([SRC_ROOT])
    assert violations == [], (
        "src/ imports broker SDK package(s): "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )


def test_no_live_broker_python_imports_negative_case_catches_planted_violation() -> None:
    fixture = FIXTURE_ROOT / "bad_broker_import.py"
    violations = scan_python_imports([fixture])
    assert len(violations) == 1, (
        f"expected exactly one violation for fixture {fixture.name}; "
        f"got {len(violations)}: "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )
    v = violations[0]
    assert v.offending_token == "alpaca_trade_api", (
        f"expected offending_token 'alpaca_trade_api'; got {v.offending_token!r}"
    )
    assert v.file_path.name == "bad_broker_import.py", (
        f"expected file_path to end with 'bad_broker_import.py'; got {v.file_path}"
    )


def test_no_live_broker_dependency_manifests_production_case_is_clean() -> None:
    violations = scan_dependency_manifests(
        pyproject_path=PYPROJECT_PATH,
        requirements_path=REQUIREMENTS_PATH,
    )
    assert violations == [], (
        "manifest declares forbidden distribution(s): "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )


def test_no_live_broker_dependency_manifests_negative_case_pyproject() -> None:
    bad_pyproject = FIXTURE_ROOT / "bad_pyproject_fragment.toml"
    violations = scan_dependency_manifests(
        pyproject_path=bad_pyproject,
        requirements_path=None,
    )
    assert len(violations) == 1, (
        f"expected exactly one violation for fixture {bad_pyproject.name}; "
        f"got {len(violations)}: "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )
    v = violations[0]
    assert v.offending_token == "alpaca_trade_api", (
        f"expected offending_token 'alpaca_trade_api'; got {v.offending_token!r}"
    )
    assert v.file_path.name == "bad_pyproject_fragment.toml", (
        f"expected file_path to end with 'bad_pyproject_fragment.toml'; got {v.file_path}"
    )


def test_no_live_broker_dependency_manifests_negative_case_requirements() -> None:
    bad_requirements = FIXTURE_ROOT / "bad_requirements_fragment.txt"
    violations = scan_dependency_manifests(
        pyproject_path=None,
        requirements_path=bad_requirements,
    )
    assert len(violations) == 1, (
        f"expected exactly one violation for fixture {bad_requirements.name}; "
        f"got {len(violations)}: "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )
    v = violations[0]
    assert v.offending_token == "alpaca_trade_api", (
        f"expected offending_token 'alpaca_trade_api'; got {v.offending_token!r}"
    )
    assert v.file_path.name == "bad_requirements_fragment.txt", (
        f"expected file_path to end with 'bad_requirements_fragment.txt'; got {v.file_path}"
    )
