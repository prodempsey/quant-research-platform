# Quant Research Platform — Traceability Matrix

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v0.1 stub (placeholder rows pending Engineering Specification work)
**Date:** 2026-04-26
**Companion documents:**
- Quant Research Platform — Strategy Decision Record (Phase 1)
- Quant Research Platform — Engineering Workflow v1.5 (locked)

**Purpose:** Map each SDR decision to its downstream artifacts — Engineering Specification section, implementing modules, configuration files, required tests, and approval gates. This is the single place to verify that every strategic decision has corresponding implementation, configuration, test coverage, and approval discipline.

**Maintenance:** Per Engineering Workflow Section 3.6, this matrix is updated as part of finalizing each Engineering Specification section. A spec section cannot be finalized while its matrix entry is missing or stale. When the SDR is revised, this matrix is the entry point for the impact assessment described in Engineering Workflow Section 6.

**Status legend:**
- `pending` — Not yet covered by an approved spec section
- `in spec` — Spec section drafted but not yet approved
- `in build` — Spec section approved, modules being implemented
- `live` — Modules merged and integrated
- `n/a` — Decision does not require module-level implementation (e.g., a strategy commitment that constrains future work but generates no code)

---

## Matrix

| SDR Decision | Spec Section(s) | Module(s) | Config File(s) | Required Tests | Approval Gate | Status |
|---|---|---|---|---|---|---|
| Decision 1 — Phase 1 scope (ETF tactical research, no live trading) | TBD | TBD | TBD | TBD | Approver per Approval Matrix | pending |
| Decision 2 — Data provider (EODHD All World Phase 1) | TBD | TBD | TBD | TBD | Approver per Approval Matrix | pending |
| Decision 3 — ETF universe (layered: Core Test / Candidate / Full Eligible) | TBD | TBD | `config/universe.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 4 — Survivorship and benchmark inception handling | TBD | TBD | `config/universe.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 5 — Phase 1 baseline models (no-ML factor + calibrated logistic regression) | TBD | TBD | `config/model.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 6 — Target design (regression + calibrated probability) and combined score philosophy | TBD | TBD | `config/model.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 7 — Validation method (walk-forward with 126-day purge/embargo) | TBD | TBD | `config/model.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 8 — Transaction cost model (4-bucket bps defaults) | TBD | TBD | `config/costs.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 9 — Regime taxonomy (SPY-vs-200dma, VIX percentile + realized-vol fallback) | TBD | TBD | `config/regime.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 10 — Configuration storage (YAML in git) and rebalance/review cadence | TBD | TBD | All `config/*.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 11 — MLOps (Postgres + MLflow), performance attribution requirements | TBD | TBD | TBD | TBD | Approver per Approval Matrix | pending |
| Decision 12 — Two-gate model promotion + multi-condition kill switch | TBD | TBD | `config/model.yaml`, `config/portfolio.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 13 — LLM advisory use during build | n/a | n/a | n/a | n/a | n/a (governed by Engineering Workflow) | n/a |
| Decision 14 — Danelfin timing (deferred until baseline exists) | TBD | TBD | TBD | TBD | Approver per Approval Matrix | pending |
| Decision 15 — Account/broker strategy (paper-only Phase 1, broker-neutral) | TBD | TBD | `config/portfolio.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 16 — Phase 1 success criteria and bias controls | TBD | TBD | TBD | TBD | Approver per Approval Matrix | pending |
| Decision 17 — Phase 1 operator UI (Dash) on Linux/Hostinger VPS *(pending SDR rev)* | TBD | TBD | TBD | TBD | Approver per Approval Matrix | pending |
| Decision 18 — Container architecture (Docker, multi-container stack) *(pending SDR rev)* | TBD | TBD | TBD | TBD | Approver per Approval Matrix | pending |

---

## Notes

**Decision numbers in this stub.** The decision numbers above reflect the working set of SDR decisions discussed during planning. The actual numbering will lock when the SDR itself is finalized; if the final SDR reorders or consolidates decisions, the matrix is updated accordingly during the SDR revision pass. Decisions 17 and 18 in particular are flagged as pending because they were identified during Engineering Workflow drafting but may need to be added to or merged with existing SDR decisions.

**Decision 13 (LLM advisory use).** This is a process commitment, not a strategy commitment that generates code. It is governed by the Engineering Workflow rather than implemented as modules, so it is marked `n/a` for spec section, modules, config, and tests. Listed in the matrix for completeness.

**TBD entries.** Entries marked `TBD` will be filled in as each Engineering Specification section is drafted and approved. The "Spec Section(s)" column is filled first (when the relevant section is started), followed by Module(s), Config File(s), and Required Tests as the section is fleshed out. Status moves from `pending` to `in spec` to `in build` to `live` over time.

**One row per decision is the default.** If a single SDR decision requires implementation across multiple spec sections or many modules, expand the row's Spec Section(s) and Module(s) columns to comma-separated lists, or split the row into sub-rows with shared decision number (e.g., "Decision 11 — MLOps storage" and "Decision 11 — MLOps attribution").

**Approval Gate column.** For Phase 1, every entry routes through the Approver via the Engineering Workflow Approval Matrix (Section 2.3). The column exists to make the gate explicit per row and to support future phases that may introduce additional approval gates (e.g., a separate broker compliance gate if live trading is ever introduced).

---

**End of document.**
