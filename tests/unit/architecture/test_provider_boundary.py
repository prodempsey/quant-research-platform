"""Test 1 — Provider-abstraction import-boundary.

Maps to: Section 1 Required Tests #1; SDR Decision 2; traceability row Decision 2.

The scanner walks every .py file under src/quant_research_platform/ whose path
is NOT under src/quant_research_platform/providers/, parses each with
ast.parse, and reports a Violation when any imported module's canonical
dotted token matches an EODHD-related forbidden entry. Per IN-2 (gate_result
#4365423458) the match policy is prefix-match: T == F or T.startswith(F + ".").

Per IN-1 (gate_result #4365423458), canonical-token construction:
- For Import nodes: token = alias.name
- For ImportFrom nodes (level == 0): token = node.module + "." + alias.name
- Relative imports (level > 0) raise; out of scope for SCAFFOLD-001 fixtures.

The Violation.offending_token field holds the matched forbidden entry F
(the policy entry that triggered), so that prefix matches over deep
sub-module imports report the rule that was violated rather than the
specific path observed.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_QRP_ROOT = REPO_ROOT / "src" / "quant_research_platform"
PROVIDERS_ROOT = SRC_QRP_ROOT / "providers"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "synthetic_bad_imports"

FORBIDDEN_TOKENS: tuple[str, ...] = (
    "quant_research_platform.providers.eodhd",
    "eodhd",
    "eodhd_data",
    "eod_historical_data",
    "eodhistoricaldata",
)


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
    for forbidden in FORBIDDEN_TOKENS:
        if token == forbidden or token.startswith(forbidden + "."):
            return forbidden
    return None


def _iter_py_files(root: Path, *, exclude_under: Path | None = None) -> Iterable[Path]:
    if root.is_file():
        if root.suffix == ".py":
            yield root
        return
    for p in root.rglob("*.py"):
        if exclude_under is not None:
            try:
                p.relative_to(exclude_under)
                continue
            except ValueError:
                pass
        yield p


def scan(roots: Iterable[Path], *, exclude_under: Path | None = None) -> list[Violation]:
    violations: list[Violation] = []
    for root in roots:
        for path in _iter_py_files(root, exclude_under=exclude_under):
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
                                kind="provider_boundary",
                                offending_token=matched,
                                message=(
                                    "non-providers module imported forbidden "
                                    f"EODHD-related token {matched!r} "
                                    f"(canonical: {token!r})"
                                ),
                            )
                        )
    return violations


def test_provider_boundary_production_case_is_clean() -> None:
    violations = scan([SRC_QRP_ROOT], exclude_under=PROVIDERS_ROOT)
    assert violations == [], (
        "non-providers code imports forbidden EODHD-related token(s): "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )


def test_provider_boundary_negative_case_catches_planted_violation() -> None:
    fixture = FIXTURE_ROOT / "bad_provider_import.py"
    violations = scan([fixture])
    assert len(violations) == 1, (
        f"expected exactly one violation for fixture {fixture.name}; "
        f"got {len(violations)}: "
        f"{[(str(v.file_path), v.lineno, v.offending_token) for v in violations]}"
    )
    v = violations[0]
    assert v.offending_token == "quant_research_platform.providers.eodhd", (
        "expected offending_token 'quant_research_platform.providers.eodhd'; "
        f"got {v.offending_token!r}"
    )
    assert v.file_path.name == "bad_provider_import.py", (
        "expected file_path to end with 'bad_provider_import.py'; "
        f"got {v.file_path}"
    )
