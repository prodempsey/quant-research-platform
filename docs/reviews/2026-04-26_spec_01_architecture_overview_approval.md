# Approval Note — Engineering Specification Section 1 v1.0 LOCKED

**Artifact approved:** Engineering Specification Section 1 — Architecture Overview and Module Structure (`docs/engineering_spec/01_architecture_overview.md`)
**Final version:** v1.0 LOCKED
**Approval date:** 2026-04-26
**Approver:** Jeremy
**Builder:** Claude (Anthropic) acting as Builder per Engineering Workflow Section 2.1
**QA Reviewer:** ChatGPT acting as Reviewer per Engineering Workflow Section 2.1

---

## Approval scope

The Approver approved Section 1 v1.0 in full, including the eleven template fields required by Engineering Workflow Section 3.2 (Purpose, Relevant SDR decisions, In scope, Out of scope, Inputs and outputs, Data contracts, Config dependencies, Required tests, Edge cases and failure behavior, Open questions, Explicit assumptions) and the section-1-handoff section to Sections 2–6.

The Approver also confirmed and locked the ten Approver-resolved defaults under *Explicit assumptions → Approver-resolved defaults (Section 1)*:

| Item | Approved decision |
|---|---|
| Python version | Python 3.12 |
| Repository layout | `src/quant_research_platform/` |
| Dependency manager | `pyproject.toml` + pinned `requirements.txt` for the Dockerfile |
| Test framework | pytest |
| Linter / formatter | ruff (lint and format) |
| nginx in initial Phase 1 stack | Omit initially; add later only if controlled UI exposure is needed |
| `python-dotenv` scope | Local development only; not a runtime dependency of the deployed stack |
| MLflow web UI exposure | Internal-only; access via SSH tunnel during development |
| Scheduled-job tooling | cron-in-container, invoking thin command-line entry points |
| Container logging destination | stdout/stderr captured by Docker, rotated via Docker's default log driver |

Any change to these defaults is treated as an architectural change and goes through the Engineering Workflow change process.

---

## Process trail

1. **Handoff packet provided** by the Approver authorizing Section 1 drafting; SDR v1.0 LOCKED and Engineering Workflow v1.5 LOCKED named as controlling documents; Section 1 scope, in/out scope, SDR decision references, and stop conditions specified per Engineering Workflow Section 2.2.
2. **v0.1 drafted** by the Builder. Eleven template fields populated. Five SDR decisions cited as directly implemented (Decisions 1, 2, 11, 17, 18). Ten open questions raised and recorded under *Explicit assumptions → Proposed default requiring approval*.
3. **v0.1 QA review** by the Reviewer against the Engineering Workflow Section 9 spec section checklist. QA verdict: "Revise before approval." Three blocking issues (single dependency graph mixing Python imports and data-at-rest coupling; provider/ingestion write-responsibility contradiction; ten unresolved open questions) and four major gaps (bias-control architectural reservation absent; app container Dash + cron startup contract absent; UI read-only constraint not extended to database-access paths; Decision 16 missing from traceability matrix). Specific recommended edits and proposed defaults included.
4. **Approver-resolved defaults confirmed** by the Approver. The ten v0.1 open questions were resolved at the values listed above. The Approver also tightened the QA reviewer's proposed bias-control text to require only architectural reservation in Section 1, with implementation explicitly handed to Sections 2, 3, and 4.
5. **v0.2 drafted** by the Builder, incorporating the six QA-driven edits, the four minor improvements (three-container stack wording, multi-part no-live-broker check, `.env.example` parity test, manual-to-automated test conversion expectation), the ten Approver-resolved defaults, and the Approver-tightened bias-control invariant verbatim.
6. **v0.2 reviewed and approved by the Approver** based on direct review of v0.2 against the Engineering Workflow Section 9 spec section checklist and the v0.1 QA report's specific edits. The Approver exercised final-decision authority per Engineering Workflow Section 2.1 and approved without a second QA cycle. v0.2 promoted to v1.0 LOCKED with no substantive content change; only the section-status metadata was flipped from draft to locked, and a v1.0 entry was added to the changelog.

---

## Companion artifacts

- Approved spec section: `docs/engineering_spec/01_architecture_overview.md` (v1.0 LOCKED).
- Updated traceability matrix: `docs/traceability_matrix.md` (v0.2; replacement rows applied for Decisions 1, 2, 11, 16, 17, 18; remaining decisions remain `pending` until their owning section is drafted).
- Original handoff packet for Section 1 drafting: stored alongside this approval note under `docs/reviews/` per Engineering Workflow Section 2.2.
- v0.1 QA report from the Reviewer: stored alongside this approval note under `docs/reviews/` per Engineering Workflow Section 9.

---

## Open items handed forward to Section 2

Section 1 v1.0 leaves no Section-1-level open questions. The following Section-1 invariants are inherited by Section 2 as primary implementation responsibilities and should be reflected in the Section 2 handoff packet when it is authorized:

- **Time-aware research auditability (Architectural invariant 7).** Section 2 defines the universe and ingestion-side schema fields supporting point-in-time reconstruction; Sections 3 and 4 extend the fields for features, targets, model runs, backtest results, and attribution.
- **Provider abstraction boundary (Architectural invariant 1).** Section 2 specifies the provider interface and the EODHD provider implementation, which `providers/` returns as provider-tagged DTOs; `ingestion/` is the only persistence path.
- **EODHD 30-day purge mechanism.** Section 2 specifies the deletion routine that filters by `provider_name = 'eodhd'`, and the test that exercises it on subscription cancellation.
- **App container Dash + cron startup contract.** Section 2 selects the specific entrypoint mechanism (process supervisor, shell entrypoint, or other approach) consistent with the Section 1 contract that a healthy Dash signal must not mask a failed cron.

---

## Status

Section 1 is approved and committed. Implementation has not begun. Section 2 drafting is not yet authorized — the Approver will provide a Section 2 handoff packet in a separate fresh conversation when ready, per Engineering Workflow Section 3.1.

---

**End of approval note.**
