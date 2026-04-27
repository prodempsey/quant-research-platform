# Quant Research Platform — Traceability Matrix

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v0.2 (Section 1 v1.0 LOCKED merged; Sections 2–6 still pending)
**Date:** 2026-04-26
**Companion documents:**
- Quant Research Platform — Strategy Decision Record (Phase 1)
- Quant Research Platform — Engineering Workflow v1.5 (locked)
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)

**Purpose:** Map each SDR decision to its downstream artifacts — Engineering Specification section, implementing modules, configuration files, required tests, and approval gates. This is the single place to verify that every strategic decision has corresponding implementation, configuration, test coverage, and approval discipline.

**Maintenance:** Per Engineering Workflow Section 3.6, this matrix is updated as part of finalizing each Engineering Specification section. A spec section cannot be finalized while its matrix entry is missing or stale. When the SDR is revised, this matrix is the entry point for the impact assessment described in Engineering Workflow Section 6.

**Status legend:**
- `pending` — Not yet covered by an approved spec section
- `in spec` — Spec section drafted but not yet approved, or spec section approved and modules not yet started
- `in build` — Spec section approved, modules being implemented
- `live` — Modules merged and integrated
- `n/a` — Decision does not require module-level implementation (e.g., a strategy commitment that constrains future work but generates no code)

---

## Matrix

| SDR Decision | Spec Section(s) | Module(s) | Config File(s) | Required Tests | Approval Gate | Status |
|---|---|---|---|---|---|---|
| Decision 1 — Phase 1 scope (ETF tactical research, no live trading) | 01 — Architecture Overview (no-live-broker boundary, scope reservations); also touched by 05 (paper-only enforcement) and 06 (UI read-only) | Cross-cutting; enforced architecturally by the absence of broker SDKs in `pyproject.toml` / `requirements.txt` / `Dockerfile` / `docker-compose.yml` and the absence of broker imports in any module | n/a (scope is structural, not configurable) | No-live-broker boundary test (multi-part: import-boundary + dependency-manifest scan + endpoint-string scan); secrets-in-diff check (no broker credentials in any committed file) | Approver per Approval Matrix | in spec |
| Decision 2 — Data provider (EODHD All World Phase 1) | 01 — Architecture Overview (provider-abstraction boundary; `providers/` returns provider-tagged DTOs containing `provider_name`/`provider_symbol`; `ingestion/` is the sole persistence path; 30-day-purge consequence reserved); 02 — Data Layer (provider interface, EODHD implementation, ingestion persistence, 30-day purge mechanism) | `providers/`, `providers/eodhd/`, `ingestion/` | `config/universe.yaml` (Section 2 detail; provider-tagging fields TBD in Section 2) | Provider-abstraction import-boundary test (Section 1); EODHD provider integration tests (Section 2); 30-day deletion test on subscription cancellation (Section 2); ingestion failure-mode tests when provider is unreachable (Section 2) | Approver per Approval Matrix | in spec |
| Decision 3 — ETF universe (layered: Core Test / Candidate / Full Eligible) | TBD | TBD | `config/universe.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 4 — Survivorship and benchmark inception handling | TBD | TBD | `config/universe.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 5 — Phase 1 baseline models (no-ML factor + calibrated logistic regression) | TBD | TBD | `config/model.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 6 — Target design (regression + calibrated probability) and combined score philosophy | TBD | TBD | `config/model.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 7 — Validation method (walk-forward with 126-day purge/embargo) | TBD | TBD | `config/model.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 8 — Transaction cost model (4-bucket bps defaults) | TBD | TBD | `config/costs.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 9 — Regime taxonomy (SPY-vs-200dma, VIX percentile + realized-vol fallback) | TBD | TBD | `config/regime.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 10 — Configuration storage (YAML in git) and rebalance/review cadence | TBD | TBD | All `config/*.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 11 — MLOps (Postgres + MLflow), performance attribution requirements | 01 — Architecture Overview (Postgres-as-system-of-record boundary, MLflow-as-tracking architecture, MLflow metadata in Postgres, MLflow artifacts in `mlflow-artifacts` named volume); 02 — Data Layer (application DB schema, MLflow metadata DB); 03 — Features/Targets/Models (MLflow integration on the writer side); 04 — Backtest/Attribution (attribution storage) | `common/` (db helpers, mlflow helpers); `models/`, `backtest/`, `attribution/` (MLflow writers); `ui/` Model Registry Browser screen (MLflow reader) | n/a at the architectural level; downstream sections may add (e.g., MLflow connection settings live in `.env`, not YAML) | Postgres-as-system-of-record import test (Section 1); cross-container connectivity smoke tests (Section 1); application DB and MLflow metadata DB present in `pg_catalog` (Section 1) | Approver per Approval Matrix | in spec |
| Decision 12 — Two-gate model promotion + multi-condition kill switch | TBD | TBD | `config/model.yaml`, `config/portfolio.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 13 — LLM advisory use during build | n/a | n/a | n/a | n/a | n/a (governed by Engineering Workflow) | n/a |
| Decision 14 — Danelfin timing (deferred until baseline exists) | TBD | TBD | TBD | TBD | Approver per Approval Matrix | pending |
| Decision 15 — Account/broker strategy (paper-only Phase 1, broker-neutral) | TBD | TBD | `config/portfolio.yaml` | TBD | Approver per Approval Matrix | pending |
| Decision 16 — Phase 1 success criteria and bias controls | 01 — Architecture Overview (architectural reservation only: time-aware research auditability invariant; no schema or implementation defined here); 02 — Data Layer (universe time-awareness, eligibility/effective-date schema fields, current-survivor disclosure); 03 — Features/Targets/Models (feature/target alignment rules, overlapping-label handling, calibration discipline); 04 — Backtest/Attribution (purge/embargo enforcement, leakage tests, reproducibility metadata, regime reporting); 06 — UI (surface bias-control disclosures and labels in the relevant screens) | Cross-cutting; Section 1 introduces no module for this. Owning modules are defined in Sections 2–4. | Cross-cutting; Section 1 introduces no config. Owning config is defined in Sections 2–4. | Section 1 introduces no test for invariant 7; Sections 2, 3, and 4 define the data contracts, alignment rules, purge/embargo logic, and the tests that enforce point-in-time reconstruction and auditability for look-ahead bias, survivorship bias, overlapping labels, and backtest leakage | Approver per Approval Matrix | in spec |
| Decision 17 — Phase 1 operator UI (Dash) on Linux/Hostinger VPS | 01 — Architecture Overview (UI as read-only architectural area, hosted inside the application container; UI read-only invariant covers both Python imports and database-access paths); 06 — UI Layer (seven Phase 1 screens, content, and the database-access enforcement mechanism for the read-only constraint) | `ui/` | TBD (Section 6 will specify; UI screens read from existing `config/*.yaml` and may add UI-only config) | UI read-only import-boundary test (Section 1); UI database-access enforcement test — no INSERT/UPDATE/DELETE/DDL from `ui/` (Section 6); UI smoke tests confirming pages load (Section 6); UI cannot bypass approval gates or modify SDR-governed state (Section 6) | Approver per Approval Matrix | in spec |
| Decision 18 — Container architecture (Docker, multi-container stack) | 01 — Architecture Overview | `Dockerfile`, `docker-compose.yml`, `.env.example`, `.dockerignore`, `scripts/backup.sh`, `scripts/restore.sh` | n/a (these are deployment artifacts, not application config) | Container startup smoke test (three-container Phase 1 stack; cron daemon health-checked alongside Dash so a Dash-only signal cannot mask cron failure); cross-container connectivity smoke tests; image rebuild test from clean cache; portability test on a fresh test environment; `.env.example` parity check against `docker-compose.yml` env references and `common/` credential helper usage | Approver per Approval Matrix | in spec |

---

## Notes

**Document version history.**
- v0.1 stub (2026-04-26) — Initial placeholder rows; Decisions 17 and 18 marked as `*(pending SDR rev)*` because they were identified during Engineering Workflow drafting and had not yet been incorporated into the SDR.
- v0.2 (2026-04-26) — Section 1 v1.0 LOCKED merged. Replacement rows applied for Decisions 1, 2, 11, 16, 17, 18. The `*(pending SDR rev)*` parentheticals on 17 and 18 are removed because the SDR is locked at v1.0 with both decisions final. Decision 16 receives an architectural footprint for the first time, reflecting Section 1's time-aware research auditability invariant. Sections 2–6 remain to be drafted; their rows remain `pending` until their owning section is finalized.

**Decision 13 (LLM advisory use).** This is a process commitment, not a strategy commitment that generates code. It is governed by the Engineering Workflow rather than implemented as modules, so it is marked `n/a` for spec section, modules, config, and tests. Listed in the matrix for completeness.

**Decision 16 (Phase 1 success criteria and bias controls).** Cross-cutting. Section 1 establishes the architectural reservation (the time-aware research auditability invariant) without defining schema fields or implementation. Sections 2, 3, and 4 own the actual data contracts, alignment rules, purge/embargo logic, and tests. Sections 2 and 6 also carry disclosure-side responsibilities (current-survivor labels on early outputs and the UI surfacing of bias-control disclosures).

**`in spec` status interpretation.** A row marked `in spec` means the relevant spec section has been drafted and may be approved (Section 1 v1.0 LOCKED is approved; Sections 2–6 are not yet drafted). When the corresponding modules begin implementation, status moves to `in build`. When modules are merged and integrated, status moves to `live`.

**TBD entries.** Entries marked `TBD` will be filled in as each Engineering Specification section is drafted and approved. The "Spec Section(s)" column is filled first (when the relevant section is started), followed by Module(s), Config File(s), and Required Tests as the section is fleshed out. Status moves from `pending` to `in spec` to `in build` to `live` over time.

**One row per decision is the default.** If a single SDR decision requires implementation across multiple spec sections or many modules, expand the row's Spec Section(s) and Module(s) columns to comma-separated lists, or split the row into sub-rows with shared decision number (e.g., "Decision 11 — MLOps storage" and "Decision 11 — MLOps attribution").

**Approval Gate column.** For Phase 1, every entry routes through the Approver via the Engineering Workflow Approval Matrix (Section 2.3). The column exists to make the gate explicit per row and to support future phases that may introduce additional approval gates (e.g., a separate broker compliance gate if live trading is ever introduced).

---

**End of document.**
