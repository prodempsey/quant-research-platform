"""Test 4 — Postgres-as-system-of-record (no MLflow imports in stateful areas).

Maps to: Section 1 Required Tests #4; SDR Decision 11; traceability row Decision 11.

The scanner walks every .py under src/quant_research_platform/portfolio/,
src/quant_research_platform/paper/, and src/quant_research_platform/order_intent/
and reports a Violation when any imported module's canonical dotted token
matches `mlflow` or starts with `mlflow.`. Per IN-2 (gate_result #4365423458)
the match policy is prefix-match: T == F or T.startswith(F + ".").

Per IN-1 (gate_result #4365423458), canonical-token construction:
- For Import nodes: token = alias.name
- For ImportFrom nodes (level == 0): token = node.module + "." + alias.name

The Violation.offending_token field holds the matched forbidden prefix F.

The negative case uses an `overlay_root` parameter (same mechanism as Test 3)
to point the scanner at a fixture file outside the three stateful-area roots.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PORTFOLIO_ROOT = REPO_ROOT / "src" / "quant_research_platform" / "portfolio"
PAPER_ROOT = REPO_ROOT / "src" / "quant_research_platform" / "paper"
ORDER_INTENT_ROOT = REPO_ROOT / "src" / "quant_research_platform" / "order_intent"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "synthetic_bad_imports"

FORBIDDEN_PREFIXES: tuple[str, ...] = ("mlflow",)


@dataclass(frozen=True)
class Violation:
    file_path: Path
    lineno: int
    kind: str
    offending_token: str
    message: str


def _canonical_tokens_from_node(node: ast.AST) -> list[tuple[str, int]]:
    tokens: list[tuple[str, int]] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            tokens.append((alias.name, node.lineno))
    elif isinstance(node, ast.ImportFrom):
        if node.level and node.level > 0:
            raise ValueError(
                "relative import not supported by SCAFFOLD-001 scanner "
                f"(lineno {node.lineno}, level={node.level})"
            )
        module = node.module or ""
        for alias in node.names:
            tokens.append((f"{module}.{alias.name}", node.lineno))
    return tokens


def _matches_forbidden(token: str) -> str | None:
    for forbidden in FORBIDDEN_PREFIXES:
        if token == forbidden or token.startswith(forbidden + "."):
            return forbidden
    return None


def _iter_py_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix == ".py":
            yield root
        return
    yield from root.rglob("*.py")


def scan(roots: Iterable[Path], *, overlay_root: Path | None = None) -> list[Violation]:
    violations: list[Violation] = []
    effective_roots: list[Path] = [overlay_root] if overlay_root is not None else list(roots)
    for root in effective_roots:
        for path in _iter_py_files(root):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Import | ast.ImportFrom):
                    continue
                for token, lineno in _canonical_tokens_from_node(node):
                    matched = _matches_forbidden(token)
                    if matched is not None:
                        violations.append(
                            Violation(
                                file_path=path,
                                lineno=lineno,
                                kind="postgres_system_of_record_import",
                                offending_token=matched,
                                message=(
                                    "stateful area imports forbidden MLflow prefix "
                                    f"{matched!r} (canonical: {token!r})"
                                ),
                            )
                        )
    return violations


def test_postgres_system_of_record_production_case_is_clean() -> None:
    violations = scan([PORTFOLIO_ROOT, PAPER_ROOT, ORDER_INTENT_ROOT])
    assert violations == [], (
        "portfolio/paper/order_intent import forbidden MLflow prefix(es): "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )


def test_postgres_system_of_record_negative_case_catches_planted_violation() -> None:
    fixture = FIXTURE_ROOT / "bad_mlflow_import.py"
    violations = scan(
        [PORTFOLIO_ROOT, PAPER_ROOT, ORDER_INTENT_ROOT],
        overlay_root=fixture,
    )
    assert len(violations) == 1, (
        f"expected exactly one violation for fixture {fixture.name}; "
        f"got {len(violations)}: "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )
    v = violations[0]
    assert v.offending_token == "mlflow", (
        f"expected offending_token 'mlflow'; got {v.offending_token!r}"
    )
    assert v.file_path.name == "bad_mlflow_import.py", (
        f"expected file_path to end with 'bad_mlflow_import.py'; got {v.file_path}"
    )
