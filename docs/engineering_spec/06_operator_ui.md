# Engineering Specification — Section 6: Operator UI, Read-Only Surfaces, Disclosure Surfacing, System Health, and Final Phase 1 Integration Boundaries

**Phase 1 scope:** ETF tactical research platform  
**Document status:** v1.0 LOCKED / APPROVED  
**Date:** 2026-04-30  
**Builder:** ChatGPT (v0.1 first draft and v0.2 merge); Claude (v0.1 comparison draft and v0.3 surgical cleanup pass per Approver direction)  
**QA Reviewer:** Claude (v0.2 review)  
**Approver:** Jeremy  
**Section:** Engineering Specification — Section 6: Operator UI, Read-Only Surfaces, Disclosure Surfacing, System Health, and Final Phase 1 Integration Boundaries  
**Canonical path:** `docs/engineering_spec/06_operator_ui.md`

**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED / APPROVED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED / APPROVED (`docs/engineering_spec/02_data_layer.md`)
- Engineering Specification — Section 3a v1.0 LOCKED / APPROVED (`docs/engineering_spec/03a_feature_engineering.md`)
- Engineering Specification — Section 3b v1.0 LOCKED / APPROVED (`docs/engineering_spec/03b_target_generation.md`)
- Engineering Specification — Section 3c v1.0 LOCKED / APPROVED (`docs/engineering_spec/03c_model_layer_mlflow.md`)
- Engineering Specification — Section 4 v1.0 LOCKED / APPROVED (`docs/engineering_spec/04_backtest_attribution_validation.md`)
- Engineering Specification — Section 5 v1.0 LOCKED / APPROVED (`docs/engineering_spec/05_portfolio_paper_order_intent.md`)
- Section approval notes and traceability companion files through Section 5
- `docs/traceability_matrix.md` v0.8

**Scope-statement basis.** Section 6 drafting is authorized from the Approver-provided Section 6 handoff prompt for working session `06_operator_ui`, plus the locked documents listed above.

**Canonical filename — Approver-accepted (v0.3).** The canonical Section 6 path is `docs/engineering_spec/06_operator_ui.md`. This follows the Section 6 handoff packet and was explicitly accepted by the Approver at the v0.2 → v0.3 transition. Earlier published references — the EW §3.1 default suggestion `06_ui_layer.md` and the Section 6 working-session identifier `06_ui_dash.md` — are treated as superseded naming variants of the same Section 6 scope, not separate files. The Section 6 lock package will record this naming decision in the approval note. EW §3.1 itself is not amended by Section 6; the §3.1 list of recommended file names is a default, not a binding contract, and any future cleanup of the §3.1 list is an EW maintenance concern outside Section 6 scope.

This v1.0 LOCKED Section 6 does not modify prior locked sections and does not start implementation. The v1.0 lock package consists of this spec, the approval note at `docs/reviews/2026-04-30_spec_06_operator_ui_approval.md`, and the traceability companion at `docs/reviews/2026-04-30_spec_06_operator_ui_traceability_updates.md`. The Approver applies the traceability companion to `docs/traceability_matrix.md` as a separate merge step bumping the matrix from v0.8 to v0.9.

**Changelog**

- **v1.0 LOCKED / APPROVED (2026-04-30).** v0.3 DRAFT promoted to v1.0 LOCKED / APPROVED with **no substantive change** to behavior, schema, tests, scope, or ownership. Locking metadata flipped (status header, builder/QA-reviewer attribution, end-of-document marker) and minor wording cleanup applied to remove stale "v0.3" version markers in current spec body where they are not historical changelog entries — replaced with "v1.0" or "current Section 6 scope" as appropriate. The historical v0.1 → v0.3 changelog entries are preserved verbatim. A-PRP table dispositions updated from "Pending Approver review" to "Accepted as Phase 1 default per v1.0 lock approval" for A-PRP-06-01 through A-PRP-06-09 per Approver direction at lock. A-OQ-06-01 marked closed (resolved at v0.3 by Approver acceptance of the §6.7 coverage map per path iii). Approver: Jeremy. Builder: ChatGPT (v0.1, v0.2); Claude (v0.1 comparison draft, v0.3 surgical pass). QA Reviewer: Claude (v0.2 review). Lock package: this v1.0 spec, the approval note at `docs/reviews/2026-04-30_spec_06_operator_ui_approval.md`, and the traceability companion at `docs/reviews/2026-04-30_spec_06_operator_ui_traceability_updates.md`. Matrix updated to v0.9 by the Approver as part of the Section 6 lock merge.

- **v0.3 DRAFT (2026-04-30).** Targeted surgical pass on v0.2 applying QA-driven cleanup items C1–C10 plus two Approver decisions issued at v0.2 → v0.3 transition. No scope expansion. No implementation code started. No approval note created. No traceability companion created. `docs/traceability_matrix.md` not updated.
  - **Approver decision A — A-OQ-06-01 resolved.** The Approver accepted path (iii): preserve the SDR Decision 17 / Section 1 seven canonical UI screen names as the canonical navigation labels and satisfy the operator-oriented seven-surface requirements through the §6.7 coverage map. No SDR amendment required. A-OQ-06-01 marked resolved in §10.1.
  - **Approver decision B — Canonical filename accepted.** `docs/engineering_spec/06_operator_ui.md` is the Approver-accepted canonical path for Section 6. Recorded in front matter and scope-statement basis.
  - **Revision C1 — Cost-bucket enum enumerated.** Added the four locked SDR Decision 8 cost-bucket values (`ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`) as a new row in the §6.5 canonical-enum display table.
  - **Revision C2 — Pipeline-validation-only reason exclusion explicit.** §6.10 #3 now names `pipeline_validation_only_reason='cost_config_zero_fallback'` as a paired filter alongside `is_pipeline_validation_only=true` for promotion-grade evidence exclusion, mirroring Section 5 §6.10 and Section 4 REP-07.
  - **Revision C3 — REPLACE-pairing linkage fields named.** §6.9 now names `decision_id` and `order_intent_id` as the Section 5 linkage fields shared by `paper_replace_out` and `paper_replace_in`, per Section 5 §6.7 / A-PRP-05-11.
  - **Revision C4 — A-DRV classification clarified.** §11.1 introductory note clarifies that the A-DRV ("Driving requirement") label maps to EW §3.3 "Derived from SDR / inherited from locked Engineering Specification section" and is a documentation convention, not a new EW §3.3 category.
  - **Revision C5 — A-PRP-06-08 / A-OQ-06-01 double classification removed.** A-PRP-06-08 retired; the coverage-map resolution is now the accepted disposition of A-OQ-06-01 in §10.1, not a separate Proposed default. Subsequent A-PRP IDs renumbered: v0.2 A-PRP-06-09 → v0.3 A-PRP-06-08; v0.2 A-PRP-06-10 → v0.3 A-PRP-06-09.
  - **Revision C6 — `ops.provider_raw_payloads` metadata-only spelled out.** §3.5 Data Quality screen and §5.3 module table both now name `ops.provider_raw_payloads` (metadata only; no payload bodies by default) explicitly, paired with the §6.12 redaction discipline and the UI-SEC-02 test.
  - **Revision C7 — Order-intent log placement tightened.** §6.7 coverage map and §3.9 Paper Portfolio screen now state explicitly that the order-intent log is a tab/subpanel within the Paper Portfolio screen (or a sub-route subordinate to it), not an eighth navigation surface.
  - **Revision C8 — `models.scoring_run_models` added to reproducibility chain.** §6.11 names `models.scoring_run_models` as the junction traversed when resolving a `models.scoring_runs` row to its constituent `models.model_runs` rows.
  - **Revision C9 — Model Registry promotion-evaluations linkage smoke test added.** UI-SMOKE-06 now includes a sub-clause asserting that the Model Registry Browser surfaces linked `portfolio.promotion_evaluations` rows for Active model versions where evaluations exist.
  - **Revision C10 — Filename decision documented.** Front matter and scope-statement basis carry an explicit note recording that `06_operator_ui.md` is the Approver-accepted canonical path. The Section 6 lock approval note will reproduce this.

- **v0.2 DRAFT (2026-04-30).** Targeted merge revision after comparing ChatGPT v0.1 and Claude v0.1. No implementation code is started. No Dash app code is written. No database migrations are created. No config file is created. No approval note is created. No traceability companion file is created. `docs/traceability_matrix.md` is not updated by this draft.
  - **Revision 1 — Screen-list conflict surfaced and proposed resolution added.** v0.1 silently used the operator-oriented seven-screen list from the Section 6 handoff. Claude's comparison correctly flagged that locked sources may reserve a different seven-screen set under SDR Decision 17 / Section 1. v0.2 introduces A-OQ-06-01 and a proposed coverage-map resolution: keep the SDR / Section 1 screen names as canonical navigation labels unless the Approver amends Decision 17, while requiring those screens to cover the newer operator-oriented list from the Section 6 handoff. The coverage map is now a first-class data contract in §6.7.
  - **Revision 2 — Read-only enforcement strengthened.** Adopted Claude's concrete dual mechanism: a dedicated `ui_readonly` Postgres role with `USAGE` / `SELECT` only, no write / DDL / GRANT / ownership privileges, plus static import and SQL-write checks. Retained ChatGPT's broader no-write, no-config-mutation, no-MLflow-write, no-broker, and callback non-actionability tests.
  - **Revision 3 — Action-enum and view-scope table added.** Adopted Claude's mapping table separating Section 5 portfolio actions, Section 5 paper position-event types, and Section 4 simulated-fill actions by view scope. This prevents implementation drift between paper state and historical backtest artifacts.
  - **Revision 4 — Null-vs-no-row rendering contract added.** Adopted Claude's unified rendering contract for `features.feature_values`, `targets.target_values`, `models.model_predictions`, `models.combined_scores`, and `backtest.regime_metrics`, with explicit prohibition against silently treating NULL values and row absence as the same UI state.
  - **Revision 5 — Section 5 contract specificity retained and expanded.** Preserved ChatGPT's deeper Section 5 details: `gate_kind` semantics, valid-status display by gate kind, kill-switch result enum (`pass`, `warning_recommended`, `pause_new_intents`, `manual_review_required`), `paused_by_kill_switch` visual distinction, REPLACE pairing, paper-only / non-executable disclosures, and no actionability from the UI.
  - **Revision 6 — Redaction, sanitization, reproducibility-chain, and defensive edge-case coverage added.** Added explicit tests for no-secret display, no raw-payload display, HTML / Markdown escaping, reproducibility-chain rendering, multiple-Active-model fail-closed behavior, browser refresh / session-loss behavior, and anti-suppression of disclosures by filters.
  - **Revision 7 — Open-question discipline tightened.** v0.2 keeps the screen-list conflict as A-OQ-06-01 until Approver acceptance. Lower-risk UI choices are classified as Builder Proposed defaults or Implementation defaults to avoid unnecessary process drag.
  - **Revision 8 — Draft-only traceability sketch retained.** The expected Section 6 matrix-update areas are included in §12 as a draft planning note only. The actual traceability companion and matrix update are deferred until lock.

- **v0.1 DRAFT (2026-04-30).** Initial Section 6 draft. Eleven EW §3.2 template fields populated in order. Every visible assumption classified under EW §3.3. No implementation code started. No approval note created. No traceability companion created. `docs/traceability_matrix.md` not updated.

---

## 1. Purpose

Section 6 defines the Phase 1 **operator UI layer** for the ETF tactical research platform. It specifies the read-only Dash UI surfaces, screen-level information architecture, data-read contracts, disclosure surfacing, UI-side enforcement of the no-write boundary, presentation of model / validation / portfolio / paper / order-intent state, system-health visibility, and final Phase 1 pre-implementation integration boundaries.

Section 6 is the final Engineering Specification section for Phase 1. It integrates the surfaces created by prior locked sections into an internal operator-facing UI, but it does not create new business logic and does not mutate state.

Section 6 consumes outputs from prior locked sections:

- `universe.*`, `prices.*`, and `ops.*` from Section 2;
- `features.*` from Section 3a;
- `targets.*` from Section 3b;
- `models.*` and MLflow metadata / artifact references from Section 3c;
- `backtest.*` and `attribution.*` from Section 4;
- `portfolio.*`, `paper.*`, and `order_intent.*` from Section 5;
- existing YAML configuration values and disclosure labels defined by prior sections.

Section 6 produces only rendered operator-facing UI surfaces. It produces no durable application database rows. It does not write to any schema. It does not place orders. It does not promote models. It does not trigger kill-switch evaluations. It does not write portfolio decisions. It does not create order intents. It does not alter YAML config. It does not introduce a broker workflow. It does not start implementation.

### 1.1 Seven-screen scope and screen-name reconciliation

Section 6 records the resolution of A-OQ-06-01 (screen-list reconciliation), accepted by the Approver prior to v1.0 lock.

The SDR Decision 17 / Section 1 screen names are the canonical navigation labels. They are not amended by Section 6:

1. Universe & Eligibility
2. Data Quality
3. Current Rankings
4. Backtest Explorer
5. Paper Portfolio
6. Model Registry Browser
7. Regime View

The Section 6 handoff and Section 5 forward-looking language describe an operator-oriented coverage set:

1. Data quality / ingestion health
2. Universe and eligibility
3. Model and validation
4. Paper portfolio
5. Order intent log
6. Attribution
7. System health

**Approver-accepted resolution (A-OQ-06-01, path iii).** The seven canonical SDR / Section 1 screen names stand as Section 6's navigation labels. The operator-oriented coverage requirements are satisfied through subpanels, tabs, or sub-routes inside those seven screens, per the §6.7 coverage map. No SDR amendment is required. The §6.7 coverage-map table is binding.

Section 6 also closes the UI-disclosure side of SDR Decision 16 by specifying where and how current-survivor, paper-only, non-executable, no-live-trading, pipeline-validation-only, stale / invalidated evidence, prediction-context, null-vs-no-row, regime-unavailable, and reproducibility-chain disclosures appear.

---

## 2. Relevant SDR decisions

Section 6 directly implements or respects the following SDR decisions.

### Decision 1 — Project Scope and Phase 1 Boundaries

Section 6 implements an internal read-only operator UI for the Phase 1 ETF tactical research and paper-portfolio platform. It introduces no live broker integration, no executable broker order workflow, no individual stocks, no fundamentals, no ETF holdings, no news/events, no earnings transcripts, no options data, no Danelfin, no autonomous research agents, and no commercial/customer-facing behavior.

### Decision 2 — Data Provider and Provider-Switching Strategy

The UI must not call EODHD or any future provider API directly. Provider-specific logic remains owned by `providers/` and `ingestion/`. Section 6 reads normalized, provider-tagged rows from Postgres and may display provider names, provider symbols, data snapshot metadata, and ingestion status. It must not require provider credentials.

### Decision 3 — ETF Universe and Eligibility Rules

The UI displays ETF universe membership, sleeve assignment, rank eligibility, eligibility history, and layer assignment as read-only state. It does not decide eligibility and does not rewrite universe configuration. Any rank-eligible / not-rank-eligible display must reflect Section 2's universe and eligibility contracts and upstream row-omission contracts from Sections 3a, 3b, and 3c.

### Decision 4 — Universe Survivorship and ETF Launch-Date Handling

The UI must surface current-survivor / directional-learning disclosures wherever early Phase 1 results, backtest outputs, validation evidence, model outputs, portfolio decisions, order intents, or paper portfolio state could otherwise be mistaken for statistically complete historical proof. It must display ETF lifecycle and replacement metadata read-only when relevant, but it does not own lifecycle semantics or replacement rules.

### Decision 5 — Benchmark, Sleeve, and Diversifier Treatment

The UI displays sleeve, benchmark, and `rank_method` semantics read-only. It must not silently substitute benchmarks, must not fall back to `secondary_benchmark_id`, and must not re-map `rank_method` values. The UI must handle the `DiversifierHedge` / `absolute_with_context` case where eligible ETFs may not have `models.combined_scores` rows under the current first-testable formula.

### Decision 6 — Target Design and Ranking Objective

The UI may display target-family metadata, horizons, combined scores, rankings, and model-scoring outputs, but it does not compute targets, fit models, or define ranking formulas. It must distinguish precomputed model/scoring outputs from UI-only formatting.

### Decision 7 — Validation, Calibration, and Backtest Confidence Level

The UI displays calibration, validation, walk-forward, backtest, attribution, OOS, and confidence-level evidence surfaces read-only. It must distinguish validation evidence from portfolio state and must not present pipeline-validation-only runs as promotion-grade evidence.

### Decision 8 — Transaction Cost and Account-Type Assumptions

The UI displays transaction-cost assumptions, cost buckets, and pipeline-validation-only / zero-cost fallback warnings when those surfaces are present. Account-type handling remains deferred. UI placeholders may note that account-type constraints are not enforced in Phase 1, but the UI must not present tax or real-account execution constraints as active enforcement.

### Decision 9 — Regime Taxonomy and Reporting

The UI may display regime evidence when present and must disclose when regime evidence or regime labels are unavailable. The UI does not define, own, or resolve the unresolved regime classifier / labeler ownership question A-OQ-04-07.

### Decision 10 — Portfolio Management and Risk Rules

The UI displays Section 5 portfolio decisions and paper-portfolio actions using the canonical closed action enum: `BUY`, `HOLD`, `TRIM`, `SELL`, `REPLACE`, `WATCH`. It does not create decisions, compute actions, rebalance portfolios, mutate paper state, or reinterpret Section 5 rules.

### Decision 11 — Model Tracking, Attribution, Data Quality, and Lightweight MLOps

The UI displays Postgres-backed system state, issue-log rows, MLflow run references, registered model references, attribution output, data-quality exceptions, and plain-English explanations. It must preserve redaction discipline and must not expose unredacted secrets or raw provider payloads.

### Decision 12 — Model Promotion, Warning, Pause, and Retirement Rules

The UI displays model state, model-state history, promotion evaluations, recommendations, kill-switch outcomes, and paper portfolio status read-only. It does not perform model-state transitions, does not trigger promotion evaluations, does not trigger kill-switch evaluations, and does not write `models.*`, `portfolio.*`, or `paper.*` rows.

The UI must display `gate_kind` semantics clearly and must not collapse `consumption` and `paper_to_real_recommendation` into one ambiguous visual concept.

### Decision 13 — LLM Advisory Use

Section 6 introduces no LLM advisory workflows, no autonomous agents, and no UI path for automated strategy changes. Any future LLM-assisted review remains governed by the EW and Approver control.

### Decision 14 — Danelfin Deferred

Section 6 must not introduce Danelfin displays, Danelfin placeholders implying planned Phase 1 support, or Danelfin-derived score surfaces.

### Decision 15 — Broker-Neutral Order Intent and Paper-Only Boundary

The UI displays broker-neutral non-executable order-intent records with paper-only and non-executable disclosures. It must not display any order intent as an executable broker instruction. It must not include place-order buttons, broker account selection, broker connection screens, API-key-entry surfaces, export-to-broker flows, or any executable-order workflow.

### Decision 16 — Phase 1 Success Criteria and Bias Controls

Section 6 implements the UI surfacing layer for Phase 1 bias controls and auditability. It displays reproducibility chains, data snapshots, current-survivor labels, prediction context, validation evidence status, pipeline-validation-only warnings, stale / invalidated evidence warnings, and issue-log explanations. It does not compute bias controls.

### Decision 17 — Operator UI Architecture

Section 6 is the owning section for the Dash operator UI screen scope, read-only data-read contracts, UI disclosure behavior, and database-access enforcement mechanism for the UI read-only invariant.

A-OQ-06-01 (seven-screen list reconciliation) was resolved by Approver acceptance of the §6.7 coverage map prior to v1.0 lock; the SDR Decision 17 screen names stand as canonical navigation labels.

### Decision 18 — Deployment and Container Architecture

Section 6 respects the Section 1 deployment architecture: Dash runs inside the application container. Section 6 does not alter container architecture, introduce nginx, expose the UI beyond the approved deployment boundary, or modify host / Docker deployment contracts.

---

## 3. In scope

Section 6 covers the following.

### 3.1 UI package and screen-level information architecture

1. The `ui/` package as the Dash UI area reserved by Section 1.
2. The canonical seven Phase 1 UI navigation surfaces (Approver-accepted per §1.1):
   - Universe & Eligibility
   - Data Quality
   - Current Rankings
   - Backtest Explorer
   - Paper Portfolio
   - Model Registry Browser
   - Regime View
3. Required operator-oriented coverage within those surfaces:
   - data quality / ingestion health;
   - universe and eligibility;
   - model and validation;
   - paper portfolio;
   - order intent log;
   - attribution;
   - system health.
4. Screen-level content requirements and ownership boundaries.
5. Read-only view-model / query-output contracts sufficient for later implementation.
6. Navigation-level separation between historical validation, model/scoring output, paper portfolio state, order-intent state, attribution, regime evidence, and system health.

### 3.2 Read-only enforcement mechanism

Section 6 selects the Phase 1 UI read-only enforcement mechanism, accepted by the Approver as A-PRP-06-01 at v1.0 lock:

1. A dedicated database principal named `ui_readonly` for `ui/` with read-only permissions only.
2. `USAGE` on approved application schemas and `SELECT` on approved tables / views required for UI display.
3. No `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, DDL, role-management, extension-management, copy-from, `GRANT`, ownership, trigger, or schema/table ownership privileges for the UI database principal.
4. No privilege on system-catalog write surfaces or role-management surfaces.
5. A default read-only transaction posture for UI database sessions where supported.
6. A single UI database-connection seam that refuses write-capable credentials.
7. A static test layer that fails if `ui/` contains SQL write statements or calls write-capable database helper functions.
8. A static import-boundary test that fails if `ui/` imports writer modules from any prior section.
9. An integration test layer that attempts representative writes against every Phase 1 schema using the UI database principal and verifies rejection.
10. UI route / callback tests that verify there are no state-mutating controls.

This mechanism is a Phase 1 spec commitment. It does not create the actual bootstrap SQL or migration files in this draft.

### 3.3 UI data-read contracts

Section 6 defines read-only UI consumption contracts for:

- `universe.*`
- `prices.*` where appropriate for charts, reference prices, and context
- `ops.*`
- `features.*`
- `targets.*`
- `models.*`
- MLflow metadata and artifact references, read-only
- `backtest.*`
- `attribution.*`
- `portfolio.*`
- `paper.*`
- `order_intent.*`

### 3.4 Disclosure surfacing

Section 6 defines UI placement rules for:

1. Current-survivor / directional-learning disclosure.
2. Paper-only disclosure.
3. Non-executable order-intent disclosure.
4. No-live-trading disclosure.
5. Pipeline-validation-only exclusion / warning where relevant.
6. Stale evidence warning where relevant.
7. Invalidated data-snapshot warning where relevant.
8. Regime-evidence unavailable warning where relevant.
9. Prediction-context disclosure where model predictions or validation evidence are displayed.
10. Account-type / real-account constraint deferred disclosure where relevant.
11. Null-vs-no-row distinction where relevant.
12. Reproducibility-chain display where relevant.

Required disclosures are non-dismissible and must not be hidden by filters, sorting, pagination, collapsed panels, or view-mode toggles.

### 3.5 Data Quality screen

The Data Quality screen displays:

1. Latest ingestion-run status by provider, universe layer, and dataset label where available.
2. Partial / failed ingestion-run summaries and plain-English issue explanations.
3. `ops.data_quality_exceptions` rows with severity, likely cause, impact, suggested resolution, whether auto-resolution is allowed, and whether Approver approval is required.
4. Data-snapshot status, including active, invalidated, stale, and provider-purge-related invalidation indicators.
5. Provider/source identifiers and snapshot metadata needed for audit, including `ops.provider_raw_payloads` **metadata only** (provider name, payload kind, ingestion-run linkage, redaction status, retention status); **payload bodies are not displayed by default** per §6.12 redaction discipline and UI-SEC-02.
6. Data freshness indicators using Section 2-owned freshness thresholds.
7. Cross-section issue-log summaries from Section 3a, 3b, 3c, Section 4, and Section 5 issue tables.
8. System-health subpanels for Postgres reachability, MLflow reachability, Dash process health, last successful run timestamps, and scheduled-job visibility where existing Section 1 container / cron health surfaces make that information available.

The screen does not expose raw provider payloads by default and must not expose secrets. It does not clear, acknowledge, retry, or resolve issues.

### 3.6 Universe & Eligibility screen

The Universe & Eligibility screen displays:

1. ETF identity, current ticker, provider symbol, sleeve, category, benchmark assignment, cost bucket, and universe layer.
2. Rank-eligibility status and effective-dated eligibility history.
3. ETF lifecycle fields such as first available price date, eligible start date, active flag, delisted date, and replacement ETF metadata where present.
4. `rank_method` display using the 03c closed enumeration: `benchmark_relative`, `peer_relative`, `absolute_with_context`.
5. Current-survivor / directional-learning disclosure.
6. Clear explanation when an ETF exists in the database but is not rank-eligible.

The screen does not edit universe membership, eligibility, benchmark assignment, sleeve assignment, cost buckets, provider mappings, or YAML config.

### 3.7 Current Rankings screen

The Current Rankings screen displays:

1. Succeeded scoring-run metadata and current scoring output.
2. `models.combined_scores`, including `combined_score`, `rank_within_sleeve`, score components, horizon, sleeve, and signal date.
3. Current model/scoring lineage sufficient to identify the upstream model run(s), scoring run, model-set version, feature run, target run, and data snapshot.
4. `DiversifierHedge` / `absolute_with_context` eligible-but-not-ranked cases, shown honestly as no current combined-score row under the first-testable formula.
5. Prediction-context, rank-method, current-survivor, stale-evidence, invalidated-snapshot, and no-row disclosures where relevant.

The screen does not override ranks, recompute ranks, score models, or mutate portfolio actions.

### 3.8 Backtest Explorer screen

The Backtest Explorer screen displays:

1. Backtest runs, folds, simulated fills, fold metrics, aggregate metrics, regime metrics, and backtest-run issues.
2. Validation evidence, including walk-forward, purge / embargo, OOS qualification, pipeline-validation-only status, and all-folds-failed terminal cases.
3. Section 4 simulated fills as historical validation artifacts only.
4. Section 4 simulated-fill actions using Section 4 labels only: `enter_long`, `exit_long`, `rebalance_in`, `rebalance_out`.
5. Attribution subpanels that display `attribution.attribution_runs`, `attribution.signal_attribution`, `attribution.trade_attribution`, and `attribution.attribution_run_issues`.
6. Links back to reproducibility metadata: `data_snapshot_id`, feature run, target run, model run, scoring run, backtest run, and attribution run where available.
7. Current-survivor, pipeline-validation-only, prediction-context, cost, regime-unavailable, and validation-evidence disclosures where relevant.

The screen does not trigger backtests, recompute attribution, create attribution rows, or use simulated fills as paper portfolio state.

### 3.9 Paper Portfolio screen

The Paper Portfolio screen displays:

1. Paper portfolios, paper portfolio status, positions, position events, rebalance cycles, portfolio snapshots, and paper-state issue rows.
2. Portfolio decisions and decision-run metadata.
3. Promotion evaluations, gate kinds, statuses, and evidence summaries.
4. Kill-switch evaluations and trigger summaries.
5. Paper portfolio status `paused_by_kill_switch` as visually distinct from `active_paper`, `paused_by_approver`, and `retired_paper`.
6. Paper-only / non-executable / no-live-trading disclosures anywhere `paper.*`, `portfolio.decisions`, or order-intent-linked state is displayed.
7. Current-survivor and evidence-quality disclosures where paper state is linked to model / validation evidence.
8. **An order-intent log surface as a tab or subpanel within the Paper Portfolio screen** (or, equivalently, as a sub-route subordinate to it such as `/paper-portfolio/order-intents/`). The order-intent log is **not an eighth navigation surface** and does not appear in the primary navigation alongside the seven canonical screens. It displays broker-neutral non-executable order intents tied to the paper portfolio with full paper-only / non-executable / no-live-trading disclosures, REPLACE pairing, and supersession history.

The screen does not rebalance portfolios, create paper positions, update positions, evaluate promotion gates, evaluate kill switches, create order intents, or write paper portfolio state.

### 3.10 Model Registry Browser screen

The Model Registry Browser displays:

1. Model runs, scoring runs, model definitions, model versions, model-state history, model-run issues, and scoring-run issues.
2. MLflow run identifiers, registered model references, and artifact references read-only.
3. Current Active model versions per model kind, relying on the 03c Active-uniqueness invariant but failing closed if the invariant is violated.
4. `models.model_predictions.prediction_context` values: `in_sample_diagnostic`, `walk_forward_oos`, `current_scoring`.
5. Calibration metadata and validation evidence as display-only context.
6. Linked `portfolio.promotion_evaluations` rows, including `gate_kind`, gate status, valid-status semantics by gate kind, and paper-to-real recommendation status.
7. Current-survivor, pipeline-validation-only, invalidated-snapshot, stale-evidence, and prediction-context disclosures.

The screen does not fit models, score models, register models, promote models, transition model state, trigger backtests, trigger attribution, or create validation evidence.

### 3.11 Regime View screen

The Regime View displays:

1. Regime metrics from `backtest.regime_metrics` where present.
2. Backtest-run linkage and evidence status.
3. Regime-evidence availability status.
4. Explicit unavailable-state messaging when A-OQ-04-07 remains unresolved or regime labels are unavailable.
5. Partial-dimension fallback states from Section 4 when relevant.

The screen does not define, compute, or own regime classifier logic.

### 3.12 Final Phase 1 integration boundaries

Section 6 records the final pre-implementation integration boundary:

1. After Section 6 is locked and its traceability update is approved, the Phase 1 Engineering Specification is complete.
2. Implementation must still not begin until the Section 6 lock package and `docs/traceability_matrix.md` v0.9 are approved.
3. Section 6 does not retroactively amend Sections 1–5.
4. If Section 6 reveals a needed prior-section amendment, it must flag an Open Question and amendment path for Approver decision.

---

## 4. Out of scope

The following are out of scope for Section 6:

1. Any implementation code.
2. Any Dash app source code.
3. Any database migrations or bootstrap scripts.
4. Any new application database schema.
5. Any writes to database tables.
6. Any model training, scoring, calibration, registration, promotion, or model-state transition logic.
7. Any model-state transition action from the UI.
8. Any kill-switch evaluation logic.
9. Any kill-switch action from the UI.
10. Any portfolio decision logic.
11. Any paper portfolio mutation logic.
12. Any order-intent creation logic.
13. Any executable broker order logic.
14. Any broker integration or broker SDK.
15. Any broker account selector, broker connection screen, API-key-entry screen, OAuth screen, or place-order workflow.
16. Any config mutation.
17. Any new financial calculations not already defined by prior locked sections.
18. Any changes to Section 1–5 contracts.
19. Any attempt to resolve A-OQ-04-07 regime classifier / labeler ownership.
20. Any attempt to enable Active → Warning automation.
21. Any attempt to enable kill-switch-driven SELL / TRIM / REPLACE behavior.
22. Any attempt to enforce account-type tax or execution constraints.
23. Any attempt to define ATR stop formulas.
24. Any live trading, real broker, or account-execution capability.
25. Any commercial/customer-facing behavior.
26. Any deployment exposure change, including nginx enablement or public UI exposure.
27. Any user-authentication / multi-user authorization model unless separately approved under deployment exposure discipline.
28. Any LLM advisory or autonomous agent workflow.
29. Any UI action that clears, acknowledges, resolves, retries, restarts, triggers, overrides, approves, rejects, promotes, demotes, pauses, resumes, retires, places, submits, routes, or exports state.

---

## 5. Inputs and outputs

### 5.1 System inputs to the UI layer

The UI layer reads from the following sources only:

1. The application Postgres database through the `ui_readonly` database principal.
2. MLflow tracking metadata and artifact references in read-only mode.
3. Existing configuration values defined by prior locked sections, mounted read-only.
4. Existing container / process health signals, if exposed by Section 1-approved deployment surfaces.
5. Static UI assets needed for Dash rendering.

The UI must not read provider APIs directly. The UI must not read broker APIs. The UI must not require EODHD credentials, broker credentials, or write-capable database credentials.

### 5.2 System outputs from the UI layer

The UI layer outputs:

1. Rendered Dash screens.
2. Read-only tables, charts, badges, warnings, and plain-English explanations.
3. Operator navigation across the seven Phase 1 screens.
4. Non-persistent UI interaction state such as filters, table sorting, pagination, selected rows, and chart controls.
5. Container stdout / stderr logs for UI errors and startup health.
6. Test artifacts created by the test suite during implementation, such as visual-regression snapshots, if accepted.

The UI layer does not output:

1. Application database rows.
2. MLflow runs, metrics, params, tags, registered models, or artifacts.
3. YAML config changes.
4. Broker orders.
5. Portfolio decisions.
6. Paper position events.
7. Order intents.
8. Data-quality exception rows.
9. Issue-log rows.
10. Model-state history rows.
11. Backtest runs or attribution runs.
12. Any durable UI-owned state.

### 5.3 Module-level input/output summary

| Module area within `ui/` | Reads | Writes |
|---|---|---|
| Application shell / navigation | Route definitions, read-only config constants, screen registry | No persistent writes |
| Read-only data-access layer | Approved schemas through `ui_readonly`; MLflow read-only wrapper | No database writes; no MLflow writes |
| Disclosure helpers | Prior-section disclosure labels, row flags, evidence status, issue context | No config writes; no new disclosure source of truth |
| Universe & Eligibility screen | `universe.*`, limited price recency summaries, current-survivor label | None |
| Data Quality screen | `ops.data_quality_exceptions`, `ops.ingestion_runs`, `ops.data_snapshots`, `ops.provider_raw_payloads` (metadata only — no payload bodies), `ops.schema_migrations`, all section-owned issue tables, latest-run metadata, system-health read surfaces | None |
| Current Rankings screen | `models.combined_scores`, `models.scoring_runs`, `models.scoring_run_models`, `models.scoring_run_issues`, `universe.*` joins | None |
| Backtest Explorer screen | `backtest.*`, `attribution.*`, linked `models.*`, `features.*`, `targets.*`, `ops.data_snapshots` | None |
| Paper Portfolio screen | `paper.*`, `portfolio.*`, `order_intent.*`, linked `models.*`, `backtest.*`, `attribution.*`, relevant prices | None |
| Model Registry Browser screen | `models.*`, MLflow read-only references, `portfolio.promotion_evaluations`, linked evidence | None |
| Regime View screen | `backtest.regime_metrics`, linked `backtest.backtest_runs`, regime issue context | None |
| UI test suite | `ui/` source tree, fixture database, fixture MLflow metadata | Test reports / snapshots only |

---

## 6. Data contracts

### 6.1 Ownership

Section 6 owns no application database schema. The UI read-only invariant is inconsistent with Section 6 owning a runtime write surface.

Section 6 owns:

- the `ui/` Python package layout and module boundaries;
- the Dash app structure and seven-screen scope;
- the UI read-only database-access contract;
- the disclosure-rendering and canonical-enum-display contracts;
- the UI test surface;
- no required `config/ui.yaml` in current Section 6 scope, unless the Approver later directs otherwise.

### 6.2 Read-only Postgres role contract

A new Postgres role, proposed name `ui_readonly`, is created during implementation through the project bootstrap / migration discipline approved by prior sections. Section 6 specifies the role's required privilege set; it does not create the actual bootstrap file in this draft.

**Privileges:**

- `USAGE` on schemas required for display: `universe`, `prices`, `ops`, `features`, `targets`, `models`, `backtest`, `attribution`, `portfolio`, `paper`, and `order_intent`.
- `SELECT` on approved tables and read views in the schemas above.
- Read-only access to MLflow metadata / references through an approved read-only seam.
- No `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, `REFERENCES`, or `TRIGGER` privileges.
- No DDL privileges (`CREATE`, `ALTER`, `DROP`).
- No `GRANT` privileges.
- No schema or table ownership.
- No role-management privileges.
- No privilege on system-catalog write surfaces.

**Connection contract:**

- `ui/` modules connect using credentials bound exclusively to `ui_readonly`.
- The UI database connection helper refuses to construct connections using write-capable application roles.
- A static check asserts no `ui/` module imports write-capable connection helpers from any prior section.
- The UI may use read-only transactions where supported by the database driver.

**Failure mode:**

- An attempted INSERT / UPDATE / DELETE / DDL from `ui/` raises a Postgres permission error at the database layer.
- The UI surfaces a clear "this view is read-only" or "operation unavailable" error; no row is written.
- The incident is logged to container stdout / stderr only and does not create an application issue row.

### 6.3 MLflow read-only contract

Section 6 reads MLflow metadata and artifact references only through a read-only wrapper or approved read-only seam. UI code must not call MLflow write methods, including run creation, metric logging, param logging, tag logging, artifact logging, registered-model creation, model-version creation, model-stage transition, or model deletion.

If MLflow cannot enforce read-only access at the server/protocol level, the UI wrapper must refuse write methods, and the static test suite must ensure no `ui/` module bypasses that wrapper.

### 6.4 Disclosure-rendering contract

Section 6 introduces a closed set of disclosure-render contexts. Each context has a label source, a render rule, and a non-suppression invariant.

| Context | Label / state source | Render rule | Suppression |
|---|---|---|---|
| Global Phase 1 no-live-trading | SDR Decisions 1, 15, 17; Section 5 disclosures | Persistent shell banner or equivalent global context | Forbidden |
| Paper-only / non-executable | Section 5 `config/portfolio.yaml` disclosure block and `order_intent.order_intents.is_executable=false` | Top-of-view banner on Paper Portfolio and order-intent displays; per-row badge on order intents | Forbidden |
| Current-survivor / directional-learning | `backtest.backtest_runs.current_survivor_disclosure_label`; Section 2 current-survivor label source | Per-row tag on backtest-result rows; banner on validation / evidence views | Forbidden |
| Pipeline-validation-only | `backtest.backtest_runs.is_pipeline_validation_only` + `pipeline_validation_only_reason` | Distinct row styling; warning that evidence is not promotion-grade | Forbidden |
| Prediction context | `models.model_predictions.prediction_context` | Per-row tag on prediction displays; explain `in_sample_diagnostic`, `walk_forward_oos`, `current_scoring` | Forbidden |
| Regime-evidence availability | `backtest.regime_metrics` presence / absence; relevant Section 4 issue rows | Explicit available / unavailable state on Regime View and Backtest Explorer regime panels | Forbidden |
| DiversifierHedge no-rank | `models.scoring_run_issues` with `rank_method_unsupported_in_phase1`; no `models.combined_scores` row | "No rank emitted under current formula" label | Forbidden |
| Kill-switch state | `paper.paper_portfolios.status`, `portfolio.kill_switch_evaluations`, `portfolio.kill_switch_triggers` | Distinct badge and linked read-only trigger panel | Forbidden |
| Gate-kind discriminator | `portfolio.promotion_evaluations.gate_kind` | First-class column / badge; values not collapsed | Forbidden |
| Account-type deferred | A-OQ-05-11 carryover | Placeholder-only / not enforced disclosure where account-type appears | Forbidden |
| Null vs no-row | Row presence, NULL values, upstream issue rows | Distinct display states | Forbidden |

Disclosure suppression at the UI layer is a defect, not a design choice. Filters, sorting, pagination, collapsed panels, selected columns, and empty-state layouts must preserve required disclosures.

### 6.5 Canonical action-enum display contract

| View scope | Action / event enum displayed | Source |
|---|---|---|
| Paper Portfolio screen, decision panels | `BUY`, `HOLD`, `TRIM`, `SELL`, `REPLACE`, `WATCH` | `portfolio.decisions.action` |
| Paper Portfolio screen, order-intent panels | `BUY`, `HOLD`, `TRIM`, `SELL`, `REPLACE`, `WATCH` | `order_intent.order_intents.action` |
| Paper Portfolio screen, position-event panels | `paper_open`, `paper_add`, `paper_trim`, `paper_close`, `paper_replace_out`, `paper_replace_in`, `paper_hold_review` | `paper.position_events.event_type` |
| Backtest Explorer simulated-fills panel | `enter_long`, `exit_long`, `rebalance_in`, `rebalance_out` | `backtest.simulated_fills.action` |
| Backtest Explorer cost panels; any UI surface displaying ETF cost-bucket assignment | `ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf` | SDR Decision 8 LOCKED four-value enum; consumed read-only via Section 4 §6.7 |

The Section 5 portfolio action enum is never displayed on a Backtest Explorer simulated-fills panel. The Section 4 simulated-fills enum is never displayed on any Paper Portfolio panel that purports to show paper-portfolio actions or order intents. The cost-bucket enum is the SDR Decision 8 LOCKED four-value set; the UI may not introduce additional bucket values. UI-ENUM-05 covers fail-closed behavior on unknown values for every enum in this table.

### 6.6 `gate_kind`, valid-status, and kill-switch display contract

`portfolio.promotion_evaluations.gate_kind` values:

- `consumption` — the 03c second promotion gate. The UI displays this as the gate controlling paper-consumption eligibility.
- `paper_to_real_recommendation` — the Section 5 paper-tracking → real-decisions recommendation layer. The UI displays this as advisory evidence only and must state that it does not enable live trading.

The two values are never collapsed into a single visual element.

The UI must preserve valid-status semantics by `gate_kind`. If a promotion-evaluation row contains a status that is invalid for its `gate_kind`, the UI must render a defect state rather than silently normalize or hide the row.

Kill-switch result values must be displayed using the Section 5 closed enum:

- `pass`
- `warning_recommended`
- `pause_new_intents`
- `manual_review_required`

`paper.paper_portfolios.status` values must render distinctly:

- `active_paper`
- `paused_by_kill_switch`
- `paused_by_approver`
- `retired_paper`

The kill-switch panel is read-only. No "clear", "override", "force resume", "re-evaluate", "resume", or "acknowledge" affordance is offered.

### 6.7 Seven-screen coverage map

A-OQ-06-01 was resolved by Approver acceptance of this coverage map prior to v1.0 lock (path iii). Section 6 uses the SDR / Section 1 seven-screen names as canonical navigation labels and maps the operator-oriented handoff requirements into those screens as follows.

| Canonical screen | Operator-oriented coverage satisfied | Main read surfaces | Key non-actionability rule |
|---|---|---|---|
| Universe & Eligibility | Universe and eligibility | `universe.*`, selected price recency summaries, `ops.data_snapshots` | No universe/config edits |
| Data Quality | Data quality / ingestion health; System health | `ops.data_quality_exceptions`, `ops.ingestion_runs`, `ops.data_snapshots`, `ops.provider_raw_payloads` (metadata only), `ops.schema_migrations`, all issue tables, latest-run summaries, MLflow/Postgres/Dash health indicators | No retry, clear, resolve, acknowledge, restart, or trigger |
| Current Rankings | Current model/scoring output portion of model and validation | `models.scoring_runs`, `models.combined_scores`, `models.scoring_run_issues`, `universe.*` joins | No rank override or portfolio action creation |
| Backtest Explorer | Validation evidence; Attribution | `backtest.*`, `attribution.*`, linked `models.*`, `features.*`, `targets.*` | No backtest or attribution execution |
| Paper Portfolio | Paper portfolio; Order intent log (as a tab/subpanel within Paper Portfolio or a sub-route subordinate to it — not an eighth navigation surface) | `paper.*`, `portfolio.*`, `order_intent.*` | No rebalance, gate, kill-switch, order-intent, or paper-state mutation |
| Model Registry Browser | Model registry, model state, promotion evidence portion of model and validation | `models.*`, MLflow read-only references, `portfolio.promotion_evaluations` | No model registration, promotion, pause, retire, or MLflow write |
| Regime View | Regime evidence / unavailable state | `backtest.regime_metrics`, linked `backtest.backtest_runs`, regime issues | No regime labeler ownership or regime computation |

The order-intent log is explicitly a Paper-Portfolio-subordinate surface (tab, subpanel, or sub-route under Paper Portfolio); it is not an eighth navigation surface and does not appear in the primary nav. Implementation must not promote it to a sibling-of-Paper-Portfolio route. UI-SMOKE-05 fixtures cover the order-intent log as a sub-surface of Paper Portfolio.

### 6.8 Null-vs-no-row display semantics

Section 6 inherits and surfaces the null-vs-no-row taxonomies established by prior sections, without redefining them.

| Surface | NULL value means | No row means | UI obligation |
|---|---|---|---|
| `features.feature_values` | Feature is defined but unavailable / unobservable for that eligible ETF/date under 03a rules | ETF/date was not rank-eligible or row was not emitted by a succeeded feature run | Render NULL and absence distinctly |
| `targets.target_values` | Bucket 2 condition under 03b taxonomy: otherwise-coverable window but missing input / benchmark / index-only condition; classification inherits NULL when regression target is NULL | Bucket 1 absence condition such as not rank-eligible, outside lifecycle, delisted before exit, or required forward window exceeds snapshot coverage | Render Bucket 1 absence and Bucket 2 NULL distinctly |
| `models.model_predictions` | Prediction output unavailable due to upstream NULL / model-kind semantics; calibrated probability may be NULL where not applicable | No prediction emitted for that row/run/context | Render unavailable prediction and row absence distinctly |
| `models.combined_scores` | One or more score components NULL; no imputation | ETF/date not rank-eligible, no succeeded scoring row, or rank method not supported under current formula such as DiversifierHedge `absolute_with_context` | Render score unavailable vs no rank emitted distinctly |
| `backtest.regime_metrics` | Dimension value may be NULL under allowed partial-dimension fallback | Regime metrics unavailable for the run / classifier unavailable | Render partial regime vs unavailable regime distinctly |

Section 6 never silently substitutes a generic dash / blank cell for both NULL-value and no-row states.

### 6.9 REPLACE-pairing display contract

For every `order_intent.order_intents` row with `action='REPLACE'`, the UI renders `etf_id` (the position being replaced) and `replacement_etf_id` (the incoming replacement) as a visually paired unit.

For every pair of `paper.position_events` rows representing a REPLACE — one `paper_replace_out` and one `paper_replace_in` — the UI renders the two events as a visually linked pair. The Section 5 linkage fields shared by the pair are `decision_id` and `order_intent_id` (per Section 5 §6.7 / A-PRP-05-11: REPLACE produces one `portfolio.decisions` row, one `order_intent.order_intents` row, and exactly two `paper.position_events` rows that share that decision and order-intent linkage). The UI uses `(decision_id, order_intent_id)` as the join key for visual pairing.

A REPLACE decision row missing either side of the paired event surface is rendered with a warning / defect indicator that surfaces the relevant Section 5 issue row, not silently hidden.

### 6.10 Evidence filtering and display contract

The UI has two distinct display modes:

1. **Audit / health mode:** may display all statuses, including failed, partial, invalidated, stale, pipeline-validation-only, and issue rows.
2. **Decision / recommendation context mode:** must display only the evidence surfaces that the upstream owner marks as eligible for that context, and must surface warnings where evidence is not eligible.

The UI does not define eligibility rules itself. It applies read-side filters already defined by the owning section and labels excluded records clearly.

At minimum:

1. Model predictions displayed as usable model evidence must be linked to `models.model_runs.status = 'succeeded'`.
2. Combined scores displayed as current scoring evidence must be linked to `models.scoring_runs.status = 'succeeded'`.
3. Backtest evidence displayed as promotion-grade must exclude `backtest.backtest_runs.is_pipeline_validation_only = true` and must additionally surface (and exclude from promotion-grade context) any row whose `backtest.backtest_runs.pipeline_validation_only_reason = 'cost_config_zero_fallback'`. The reason-field exclusion mirrors Section 5 §6.10 evidence-eligibility filtering and Section 4 REP-07. The two filters are paired: the boolean flag identifies pipeline-validation-only runs, and the reason field carries the closed-enum cause that Section 6 makes explicit on the UI side.
4. Portfolio / paper / order-intent displays must preserve Section 5's paper-only and non-executable context.
5. Simulated fills from Section 4 must never be displayed as paper portfolio actions.

### 6.11 Reproducibility-chain display contract

Where a UI view displays a downstream decision, order intent, paper state, backtest result, attribution row, or model/scoring output, it must provide a read-only path back through the applicable reproducibility chain.

The full chain, when available, is:

`data_snapshot_id` → `features.feature_runs` → `targets.target_runs` → `models.model_runs` → `models.scoring_runs` (traversed to constituent `models.model_runs` rows via the `models.scoring_run_models` junction, which the UI may surface as scoring-run composition for transparency) → `backtest.backtest_runs` → `attribution.attribution_runs` → `portfolio.decision_runs` / `portfolio.decisions` → `paper.*` / `order_intent.order_intents`

The UI may omit unavailable upstream links only when the row's owning section does not provide that relationship. It must not fabricate missing lineage. The `models.scoring_run_models` junction is read-only context: surfacing scoring-run-to-model-run composition does not constitute a separate write surface or a separate run-level entity.

### 6.12 Secret redaction and display sanitization contract

The UI must assume issue-log text and technical context could contain user-supplied or upstream-supplied strings. It must display only redacted fields from the database and must apply UI-safe escaping / sanitization before rendering text, JSON snippets, technical context, provider messages, exception messages, file paths, or Markdown-like content.

The UI must not display secrets, tokens, API keys, authorization headers, broker credentials, provider credentials, write-capable connection strings, environment-variable values, or unredacted raw payload content.

### 6.13 Browser/session behavior contract

Browser refresh, browser back/forward navigation, session loss, container restart, or Dash process restart may lose UI display state such as selected filters and expanded rows. That is acceptable because Section 6 owns no durable state. The UI must restore authoritative content from read-only database / MLflow surfaces only and must not attempt to reconstruct state by writing session records.

---

## 7. Config dependencies

### 7.1 Existing config files read by the UI

The UI may read the following config files in read-only mode where the display requires approved labels, thresholds, or metadata:

1. `config/universe.yaml` — current-survivor disclosure label, universe labels, data-freshness thresholds.
2. `config/features.yaml` — feature set names and display labels if needed.
3. `config/targets.yaml` — target set names, target horizons, and display labels if needed.
4. `config/model.yaml` — model set labels, rank-method display metadata, and MLflow reference context if needed.
5. `config/backtest.yaml` — validation display labels, backtest metric labels, and cost / pipeline-validation display context if needed.
6. `config/costs.yaml` — read-only display only through approved Section 4 evidence surfaces; no UI direct enforcement.
7. `config/regime.yaml` — regime label semantics if a labeler exists / when Section 4 exposes relevant surfaces.
8. `config/portfolio.yaml` — paper-only and non-executable disclosure labels, gate / kill-switch display labels, and portfolio action display metadata.

The UI must not mutate any config file.

### 7.2 No required `config/ui.yaml` in current Section 6 scope

Current Section 6 proposed default: Section 6 does **not** introduce a required `config/ui.yaml` file. UI display labels should come from prior-section config files, schema enumerations, or non-strategy UI constants defined during implementation.

If the Approver later wants operator-customizable UI preferences, a future UI-only config file may be introduced through a Section 6 revision. Such a file must not contain strategy-affecting values, portfolio thresholds, model thresholds, provider settings, broker settings, execution settings, or credentials.

### 7.3 Environment variables and secrets

The UI requires:

1. Read-only application database connectivity for the dedicated UI database principal.
2. Read-only MLflow tracking URI access if MLflow metadata is displayed.
3. Standard Dash runtime settings inside the application container.

The UI must not require:

1. EODHD API keys.
2. Broker API keys.
3. Write-capable application database credentials.
4. MLflow write credentials beyond read-only tracking access.
5. Secrets embedded in YAML.

If implementation requires new environment variable names for the read-only UI database principal, those names must be added through the implementation task or a targeted Section 6 revision before coding begins. Suggested names, if adopted, are `UI_DB_USER` and `UI_DB_PASSWORD`, paired with existing application database host / port / database settings. These names are not created by this draft.

### 7.4 Deployment configuration

Section 6 does not change the Section 1 deployment architecture. Dash remains inside the application container. Any future exposure beyond the internal / approved access pattern, including nginx enablement or public access, is a deployment exposure change under the EW Approval Matrix and is outside current Section 6 scope.

### 7.5 Authentication / access control

Current Section 6 scope does not introduce a multi-user authentication / authorization model. The UI remains internal/operator-only under the deployment exposure assumptions from Section 1 unless the Approver directs an amendment. If the Approver later requires authentication, that decision should be made as a deployment/security amendment rather than silently embedded in UI screen code.

---

## 8. Required tests

Tests below are specification requirements for later implementation. This draft does not create test files.

### 8.1 Read-only enforcement tests

1. **UI-DB-01: UI database principal no-write test.** Using `ui_readonly`, representative `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, and DDL attempts fail against every Phase 1 application schema: `universe`, `prices`, `ops`, `features`, `targets`, `models`, `backtest`, `attribution`, `portfolio`, `paper`, and `order_intent`.
2. **UI-DB-02: UI database principal select-only test.** `ui_readonly` can read only approved tables / views needed for display.
3. **UI-DB-03: Read-only transaction test.** UI database sessions use read-only transaction posture where supported.
4. **UI-DB-04: Static no-write SQL test.** `ui/` source contains no SQL write verbs or write-capable DB helper calls.
5. **UI-DB-05: No writer-module import test.** `ui/` does not import writer modules from `ingestion/`, `features/`, `targets/`, `models/`, `backtest/`, `attribution/`, `portfolio/`, `paper/`, or `order_intent/`.
6. **UI-DB-06: No provider import test.** `ui/` does not import `providers/`, EODHD adapter code, or provider-specific libraries.
7. **UI-DB-07: No broker import / dependency test.** `ui/` and dependency manifests contain no broker SDK import or broker workflow dependency.
8. **UI-DB-08: No config mutation test.** `ui/` never opens YAML config files in write mode and contains no config-save path.
9. **UI-DB-09: No MLflow write test.** UI can read MLflow metadata references but cannot create runs, log metrics, log params, upload artifacts, register models, or transition model versions.
10. **UI-DB-10: No authentication-library drift test.** If UI authentication is deferred, `ui/` must not import a UI authentication library or introduce login / role-based access code without Approver-authorized amendment.

### 8.2 Screen smoke tests

11. **UI-SMOKE-01: Universe & Eligibility loads** with active, inactive, delisted, replacement, rank-eligible, and not-rank-eligible fixtures.
12. **UI-SMOKE-02: Data Quality loads** with empty, succeeded, failed, partial, invalidated-snapshot, and issue-row fixtures.
13. **UI-SMOKE-03: Current Rankings loads** with succeeded scoring run, no-rank DiversifierHedge case, NULL combined-score case, and empty-state fixtures.
14. **UI-SMOKE-04: Backtest Explorer loads** with succeeded, failed, all-folds-failed, pipeline-validation-only, regime-unavailable, and attribution fixtures.
15. **UI-SMOKE-05: Paper Portfolio loads** with active, paused-by-kill-switch, paused-by-approver, retired, REPLACE, blocked-by-gate, and blocked-by-kill-switch fixtures.
16. **UI-SMOKE-06: Model Registry Browser loads** with Active, Warning, Paused, Retired, multiple-Active-defect, MLflow-unavailable, and promotion-evaluation fixtures. Sub-clause: for each Active model version with at least one corresponding `portfolio.promotion_evaluations` row, the Model Registry Browser surfaces the linked promotion-evaluation rows with `gate_kind` displayed verbatim and valid-status semantics preserved per §6.6. Fixtures cover both `gate_kind='consumption'` and `gate_kind='paper_to_real_recommendation'` linked to the same Active model version.
17. **UI-SMOKE-07: Regime View loads** with populated regime metrics, partial-dimension fallback, and unavailable-regime fixtures.
18. **UI-SMOKE-08: Empty database smoke.** Every screen renders an empty-state message rather than an unhandled exception when source tables are empty.
19. **UI-SMOKE-09: Container-startup smoke.** After `docker compose up -d`, the Dash component starts without masking failed scheduled jobs and all seven screens are reachable on the configured port.

### 8.3 Disclosure tests

20. **UI-DISC-01: Global no-live-trading disclosure present.** The UI shell or equivalent persistent context contains a Phase 1 research / paper-only disclosure.
21. **UI-DISC-02: Paper-only disclosure present** on every display of `portfolio.decisions`, `paper.*`, and `order_intent.order_intents`.
22. **UI-DISC-03: Non-executable order-intent disclosure present** on every order-intent row, including `is_executable=false` badge.
23. **UI-DISC-04: Current-survivor disclosure present** on every backtest / validation / model / portfolio evidence view where relevant.
24. **UI-DISC-05: Pipeline-validation-only warning present** wherever `is_pipeline_validation_only=true` appears.
25. **UI-DISC-06: Prediction-context label present** wherever model predictions are displayed.
26. **UI-DISC-07: Regime-unavailable display present** when regime evidence is absent.
27. **UI-DISC-08: DiversifierHedge no-rank display present** when no `combined_scores` row exists under `absolute_with_context`.
28. **UI-DISC-09: Disclosure anti-suppression test.** Filters, sorting, pagination, collapsed panels, column selection, and view toggles cannot hide required disclosures.

### 8.4 Canonical enum, gate, and state tests

29. **UI-ENUM-01: Section 5 action enum display test.** Paper portfolio decision and order-intent displays show only `BUY`, `HOLD`, `TRIM`, `SELL`, `REPLACE`, `WATCH`.
30. **UI-ENUM-02: Section 4 simulated-fill enum separation test.** Backtest Explorer simulated-fills panels show only `enter_long`, `exit_long`, `rebalance_in`, `rebalance_out`.
31. **UI-ENUM-03: Enum disjointness test.** Section 4 simulated-fill labels never appear as paper-portfolio actions; Section 5 action labels never appear as simulated-fill actions.
32. **UI-ENUM-04: Paper event-type display test.** Paper position-event panels display only the Section 5 paper event enum.
33. **UI-ENUM-05: Unknown enum fail-closed test.** Unknown action, event, status, gate, kill-switch result, cost-bucket, or prediction-context values render as defect states rather than silently displaying as valid values.
34. **UI-GATE-01: `gate_kind` visible test.** `consumption` and `paper_to_real_recommendation` appear as first-class labels and are visually distinct.
35. **UI-GATE-02: Valid-status-by-gate-kind test.** Invalid status values for a given `gate_kind` render as defects rather than being normalized.
36. **UI-KS-01: Kill-switch result enum display test.** Kill-switch results display only `pass`, `warning_recommended`, `pause_new_intents`, and `manual_review_required`.
37. **UI-KS-02: `paused_by_kill_switch` visual distinction test.** `paused_by_kill_switch` is visually distinct from `active_paper`, `paused_by_approver`, and `retired_paper`.

### 8.5 Non-actionability tests

38. **UI-ACT-01: No place-order affordance.** No UI control, route, callback, label, or string implies a broker-place-order workflow.
39. **UI-ACT-02: No broker account selector.** No UI screen contains broker account, broker connection, broker credential, broker API-key, OAuth, or route-to-broker controls.
40. **UI-ACT-03: No promotion action.** No UI control writes or attempts to write `models.model_versions`, `models.model_state_history`, or `portfolio.promotion_evaluations`.
41. **UI-ACT-04: No kill-switch action.** No UI control triggers, clears, reruns, overrides, or acknowledges kill-switch state.
42. **UI-ACT-05: No portfolio / paper / order-intent mutation.** No UI control creates, modifies, deletes, supersedes, approves, or exports `portfolio.*`, `paper.*`, or `order_intent.*` rows.
43. **UI-ACT-06: No run-triggering controls.** No UI control triggers ingestion, feature, target, model, scoring, backtest, attribution, portfolio, paper, or order-intent jobs.

### 8.6 REPLACE and order-intent tests

44. **UI-REPL-01: REPLACE order-intent pairing test.** `etf_id` and `replacement_etf_id` render as a paired out → in unit.
45. **UI-REPL-02: REPLACE paper-event pairing test.** `paper_replace_out` and `paper_replace_in` render as linked pair when both exist.
46. **UI-REPL-03: Missing REPLACE side test.** Missing `paper_replace_out` or `paper_replace_in` renders a warning linked to the relevant issue row, not silence.
47. **UI-OI-01: Non-executable invariant test.** Every order-intent row renders `is_executable=false` as a non-suppressible badge and does not display broker fields as executable instructions.

### 8.7 Null-vs-no-row and reproducibility-chain tests

48. **UI-NULL-01: NULL vs no-row distinction test.** Fixtures verify distinct rendering for NULL values vs row absence across `features.feature_values`, `targets.target_values`, `models.model_predictions`, `models.combined_scores`, and `backtest.regime_metrics`.
49. **UI-NULL-02: 03b Bucket 1 / Bucket 2 rendering test.** Target absence and target NULL conditions render distinctly according to Section 3b §6.5.
50. **UI-LINEAGE-01: Reproducibility-chain test.** The UI links the available chain from `data_snapshot_id` through feature run, target run, model run, scoring run, backtest run, attribution run, decision run, and order intent without writing rows.
51. **UI-LINEAGE-02: Missing-lineage fail-closed test.** If a required lineage link is missing where the owning section says it should exist, the UI renders a defect state rather than fabricating lineage.

### 8.8 Security, redaction, and sanitization tests

52. **UI-SEC-01: No secret display test.** UI fixtures containing API keys, tokens, authorization headers, connection strings, or passwords are redacted or blocked from display.
53. **UI-SEC-02: No raw provider payload display test.** Raw provider payload bodies do not render by default; only redacted metadata / issue summaries render.
54. **UI-SEC-03: HTML / Markdown escaping test.** Issue-log text, provider messages, exception text, JSON snippets, and file paths render as escaped text and cannot inject HTML or script.
55. **UI-SEC-04: No write-capable credential exposure test.** UI logs and browser-rendered content never display write-capable database credentials or environment-variable values.

### 8.9 Defensive edge-case tests

56. **UI-EDGE-01: Multiple Active model versions fail closed.** If more than one Active model version appears where 03c says uniqueness should hold, UI renders an upstream-invariant defect and does not choose a winner.
57. **UI-EDGE-02: Browser refresh / session loss test.** Refresh or session loss restores content only from read-only authoritative sources and does not create durable UI state.
58. **UI-EDGE-03: MLflow unavailable test.** Model Registry Browser degrades honestly when MLflow is unreachable and does not attempt writes.
59. **UI-EDGE-04: Postgres unavailable test.** Screens show data-layer unavailable state and no write retry behavior.
60. **UI-EDGE-05: Runtime config change test.** UI does not hot-write or persist config; config changes require process restart or approved implementation mechanism.

---

## 9. Edge cases and failure behavior

1. **Postgres unreachable.** Affected screens display "data layer unavailable" or equivalent. The UI does not attempt write retries and does not create issue rows.
2. **MLflow tracking server unreachable.** Model Registry Browser displays MLflow unavailable state; other screens degrade gracefully to model-id-only / metadata-only display when possible.
3. **`backtest.backtest_runs.current_survivor_disclosure_label` missing despite NOT NULL expectation.** UI renders a defect state and does not invent a replacement label.
4. **`backtest.backtest_runs.is_pipeline_validation_only=true`.** UI displays a distinct warning and does not present the run as promotion-grade evidence.
5. **A `models.combined_scores` row has `combined_score=NULL` and `rank_within_sleeve=NULL`.** UI renders "score unavailable" with score-component context, not a fake rank.
6. **No `models.combined_scores` rows for a DiversifierHedge ETF at signal date `T`.** UI renders "no rank emitted under current formula" and links the relevant `models.scoring_run_issues` row where available.
7. **No `backtest.regime_metrics` rows for a backtest run.** UI renders "regime evidence unavailable" rather than an empty chart that implies zero values.
8. **`paper.paper_portfolios.status='paused_by_kill_switch'`.** UI renders a visually distinct status badge and read-only trigger decomposition.
9. **`portfolio.decisions.blocked_by_gate=true` or `blocked_by_kill_switch=true`.** UI renders explicit blocked/suppressed state and does not imply an order intent should exist.
10. **`paper_replace_out` exists without `paper_replace_in`, or vice versa.** UI renders warning / defect linked to issue row, not silence.
11. **Unknown action / event / status / gate / kill-switch result / cost-bucket / prediction-context value.** UI renders a defect state rather than silently treating the value as valid.
12. **Multiple Active model versions appear for a model kind despite 03c uniqueness discipline.** UI fails closed: it renders an upstream-invariant violation and does not choose an Active winner.
13. **Attempted database write through UI connection.** Postgres permission error; UI displays read-only error; no row written.
14. **Attempted MLflow write through UI wrapper.** Wrapper rejects; no write performed.
15. **Filters or pagination would hide required disclosures.** UI preserves disclosures at the view or row level; if not possible, the filtered view is invalid.
16. **Browser refresh or session loss.** UI restores from read-only database / MLflow sources only; transient filters may reset.
17. **Runtime config file changes.** UI does not write or hot-save config. Any reload behavior must be explicitly implemented later under approved scope.
18. **Issue text contains HTML / script / Markdown injection.** UI escapes / sanitizes before rendering.
19. **Provider raw payload metadata references an unavailable or purged payload.** UI shows metadata / purged state only and does not treat missing payload body as a UI failure.
20. **External carryover remains unresolved.** For A-OQ-04-07, A-OQ-05-09, A-OQ-05-10, A-OQ-05-11, A-OQ-05-14, and A-OQ-05-17, UI shows honest unavailable / deferred / display-only state and does not implement the deferred behavior.

---

## 10. Open questions

### 10.1 A-OQ-06-01 — Seven-screen list reconciliation — RESOLVED

**Status: Resolved by Approver acceptance prior to v1.0 lock.** Disposition: path (iii) — coverage map.

Locked sources reserve the following seven UI screen names per SDR Decision 17 / Section 1:

1. Universe & Eligibility
2. Data Quality
3. Current Rankings
4. Backtest Explorer
5. Paper Portfolio
6. Model Registry Browser
7. Regime View

The Section 6 handoff and Section 5 forward-looking language describe an operator-oriented seven-surface list:

1. Data quality / ingestion health
2. Universe and eligibility
3. Model and validation
4. Paper portfolio
5. Order intent log
6. Attribution
7. System health

**Approver-accepted resolution:** the locked SDR / Section 1 names stand as Section 6's canonical navigation labels; the operator-oriented requirements are satisfied through subpanels, tabs, and sub-routes inside those screens per the §6.7 coverage map (binding):

- data quality / ingestion health and system health are surfaced inside Data Quality;
- universe and eligibility are surfaced inside Universe & Eligibility;
- model and validation are surfaced across Current Rankings, Model Registry Browser, and Backtest Explorer;
- paper portfolio is surfaced inside Paper Portfolio;
- the order-intent log is surfaced as a tab/subpanel within Paper Portfolio (or a sub-route subordinate to it), not an eighth navigation surface;
- attribution is surfaced inside Backtest Explorer;
- regime evidence is surfaced inside Regime View.

No SDR amendment is required. A-OQ-06-01 is closed.

### 10.2 External carryovers not resolved by Section 6

The following Open Questions / deferred items remain outside Section 6 and are not resolved here:

1. **A-OQ-04-07 — Regime classifier / labeler ownership.** Section 6 may display regime evidence when present and disclose absence honestly. It must not define or own the classifier.
2. **A-OQ-05-09 — Active → Warning automation.** Section 6 may display Section 5 recommendations only. It must not trigger model-state transitions.
3. **A-OQ-05-17 — Kill-switch-driven SELL / TRIM / REPLACE enablement.** Section 6 may display the deferred state only. It must not create or imply automatic risk-reduction actions.
4. **A-OQ-05-10 — Direct `config/costs.yaml` consumption by Section 5.** Section 6 consumes only approved read surfaces and display labels.
5. **A-OQ-05-11 — Account-type handling.** Section 6 may display placeholders only and must not present account-type constraints as enforced real-account constraints.
6. **A-OQ-05-14 / A-PRP-05-14 — ATR formula details.** Section 6 must not imply exact ATR stop enforcement unless a future Section 5 amendment defines it.
7. **Implementation-time Section 4 amendment trigger from A-OQ-05-15 disposition.** If later implementation reveals Section 4 v1.0 evidence surfaces lack a required field for the Section 5 consumption-gate evidence bundle, that is a future Section 4 amendment path, not a Section 6 UI workaround.

No Section-6-internal Open Questions remain. A-OQ-06-01 was resolved by Approver acceptance per §10.1. UI authentication, `config/ui.yaml`, nginx exposure, and visual-regression baselines are accepted as Phase 1 Section 6 defaults per A-PRP-06-03 / -02 / -09 / -08 respectively.

---

## 11. Explicit assumptions

### 11.1 Driving requirements inherited from locked sources

**Classification mapping note.** The `A-DRV` ("Driving requirement") label used in this table is a documentation convention introduced for clarity in Section 6; it maps to EW §3.3 "Derived from SDR / inherited from locked Engineering Specification section." It is not a fifth EW §3.3 category. Each A-DRV row below is a requirement that flows from a locked SDR decision or a locked prior-section binding condition, not a Section-6-introduced strategy choice. Section-6-introduced choices are classified under §11.2 (Builder Proposed defaults) or §11.3 (Implementation defaults); Section-6-introduced unresolved questions belong in §10.

| ID | Classification | Assumption / requirement | Source / disposition |
|---|---|---|---|
| A-DRV-06-01 | Driving requirement | UI is read-only with respect to all application schemas and all prior-section state. | Section 1, Section 5, SDR Decision 17. |
| A-DRV-06-02 | Driving requirement | UI must not write to any database table. | Section 1 and Section 5 condition on Section 6. |
| A-DRV-06-03 | Driving requirement | UI must not place orders, promote models, trigger kill switches, mutate config, or mutate portfolio / paper / order-intent state. | Section 5 condition on Section 6. |
| A-DRV-06-04 | Driving requirement | Seven-screen scope is required; the canonical navigation labels are the SDR Decision 17 / Section 1 names, with operator-oriented coverage satisfied through the §6.7 coverage map (A-OQ-06-01 resolved per §10.1). | SDR Decision 17 / Section 1 / Section 6 §6.7. |
| A-DRV-06-05 | Driving requirement | Paper-only and non-executable disclosures must appear anywhere `order_intent.order_intents`, `portfolio.decisions`, or `paper.*` state is displayed. | Section 5 condition on Section 6. |
| A-DRV-06-06 | Driving requirement | `gate_kind` semantics must remain visible and must preserve the distinction between `consumption` and `paper_to_real_recommendation`. | Section 5 condition on Section 6. |
| A-DRV-06-07 | Driving requirement | Kill-switch state, including `paused_by_kill_switch`, must be visually distinct. | Section 5 condition on Section 6. |
| A-DRV-06-08 | Driving requirement | UI must contain no live-trading affordance. | SDR Decisions 1, 15, 17; Section 5 condition on Section 6. |
| A-DRV-06-09 | Driving requirement | UI must display Section 5 actions exactly as `BUY`, `HOLD`, `TRIM`, `SELL`, `REPLACE`, `WATCH`. | Section 5. |
| A-DRV-06-10 | Driving requirement | Section 4 simulated-fill actions must not be displayed as paper portfolio actions. | Section 4 / Section 5 disjointness. |
| A-DRV-06-11 | Driving requirement | REPLACE rows must visually pair `etf_id`, `replacement_etf_id`, and related paper replacement events where available. | Section 5. |
| A-DRV-06-12 | Driving requirement | Section 6 does not resolve A-OQ-04-07, A-OQ-05-09, A-OQ-05-17, A-OQ-05-10, A-OQ-05-11, or A-OQ-05-14. | Section 5 carryovers. |
| A-DRV-06-13 | Driving requirement | UI must preserve the null-vs-no-row distinctions established by prior sections. | Sections 3a, 3b, 3c, 4. |
| A-DRV-06-14 | Driving requirement | UI must preserve redaction and sanitization discipline. | Section 2 data-quality / raw-payload redaction, Section 5 issue-log discipline, SDR Decision 11. |

### 11.2 Builder Proposed defaults requiring Approver approval

| ID | Classification | Proposed default | Rationale | Approval disposition |
|---|---|---|---|---|
| A-PRP-06-01 | Builder Proposed default requiring approval | UI read-only enforcement uses dedicated `ui_readonly` database principal, SELECT-only grants, read-only transaction posture, static no-write checks, and integration permission-denial tests. | Closes the Section 1 reserved enforcement mechanism without adding UI-side write paths. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |
| A-PRP-06-02 | Builder Proposed default requiring approval | Section 6 introduces no required `config/ui.yaml` in Phase 1 v1.0. | Avoids unnecessary config surface and prevents accidental strategy-affecting UI config. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |
| A-PRP-06-03 | Builder Proposed default requiring approval | UI is internal/operator-only in Phase 1 and does not introduce a multi-user authentication / authorization model. | Section 1 owns deployment exposure. UI auth would expand scope and may require deployment/security decisions. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |
| A-PRP-06-04 | Builder Proposed default requiring approval | UI may use only non-persistent browser/session display state and optional transient in-memory caching; no UI-owned durable state. | Preserves no-write boundary and avoids a UI schema. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |
| A-PRP-06-05 | Builder Proposed default requiring approval | MLflow access from the UI is read-only metadata / artifact-reference display only. No artifact upload, run creation, metric logging, model registration, or model-state transition. | Preserves 03c writer-side MLflow ownership. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |
| A-PRP-06-06 | Builder Proposed default requiring approval | Raw provider payload bodies are not shown by default in the UI; only redacted metadata and issue summaries are displayed. | Reduces accidental secret exposure and keeps the UI operator-focused. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |
| A-PRP-06-07 | Builder Proposed default requiring approval | UI disclosure banners / badges are non-dismissible on views where disclosures are required. | Prevents filters or UI controls from hiding paper-only / non-executable / current-survivor context. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |
| A-PRP-06-08 | Builder Proposed default requiring approval | Visual-regression baselines are produced during implementation, not committed as part of the Section 6 spec lock package. | Concrete baselines require running UI code; Section 6 reserves the tests only. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |
| A-PRP-06-09 | Builder Proposed default requiring approval | Nginx / public exposure remains out of scope for Section 6 v1.0. | Section 1 already reserves optional nginx; no Section 6 need to activate it. | Accepted as Phase 1 Section 6 default per v1.0 lock approval. |

### 11.3 Implementation defaults, not strategy assumptions

| ID | Classification | Implementation default | Notes |
|---|---|---|---|
| A-IMP-06-01 | Implementation default | Specific Dash route names and component layout are implementation details as long as the seven required screens / coverage areas exist and tests pass. | Does not affect strategy. |
| A-IMP-06-02 | Implementation default | Chart/table formatting may evolve during implementation if it preserves required disclosures and does not change data meaning. | Visual design flexibility only. |
| A-IMP-06-03 | Implementation default | UI empty-state copy may be refined during implementation if it preserves no-live-trading and evidence-quality meanings. | Content polish only. |
| A-IMP-06-04 | Implementation default | Time display should include timezone / UTC context where source timestamps are UTC. | Avoids operator confusion; not a strategy change. |
| A-IMP-06-05 | Implementation default | A single UI DB connection helper may be used to centralize read-only credential use. | Engineering choice; static tests enforce no bypass. |
| A-IMP-06-06 | Implementation default | MLflow read-only access may be wrapped in a small UI-side client wrapper. | Engineering choice; tests ensure no write methods are exposed. |

### 11.4 Explicit non-assumptions

1. This section does not assume a live broker will be added later.
2. This section does not assume a public UI exposure model.
3. This section does not assume user login, user-specific permissions, or role-based UI access in Phase 1.
4. This section does not assume a regime classifier exists.
5. This section does not assume `DiversifierHedge` ETFs are ranked under the current first-testable model formula.
6. This section does not assume account-type constraints are enforced.
7. This section does not assume kill-switch-driven SELL / TRIM / REPLACE behavior exists.
8. This section does not assume Active → Warning automation exists.
9. This section does not assume pipeline-validation-only evidence is promotion-grade.
10. This section does not assume UI filters can hide required disclosures.
11. This section does not assume MLflow provides server-side read-only enforcement.
12. This section does not assume any reinterpretation of the SDR Decision 17 screen list beyond the §6.7 coverage map accepted by the Approver.

---

## 12. Draft-only traceability expectations for Section 6 lock

This section is a draft planning note only. It does **not** modify `docs/traceability_matrix.md`.

At Section 6 lock, the traceability companion is expected to update at least:

1. **Decision 1** — Add Section 6 UI enforcement of no-live-trading affordances and no commercial/customer-facing behavior.
2. **Decision 2** — Add Section 6 no-provider-direct-call / normalized-data-read-only contribution.
3. **Decision 4** — Add Section 6 current-survivor / directional-learning disclosure surfacing.
4. **Decision 5** — Add Section 6 read-only display of sleeve / benchmark / `rank_method` semantics and `DiversifierHedge` no-current-combined-score display.
5. **Decision 7** — Add Section 6 validation evidence and pipeline-validation-only display / warning contribution.
6. **Decision 8** — Add Section 6 cost assumptions / account-type deferred display contribution.
7. **Decision 9** — Add Section 6 regime-evidence display and unavailable-disclosure contribution without resolving A-OQ-04-07.
8. **Decision 10** — Add Section 6 display of canonical Section 5 action enum and disjointness from Section 4 simulated-fill actions.
9. **Decision 11** — Add Section 6 read-only display of MLOps, issue logs, data quality, MLflow references, attribution, and redaction / sanitization behavior.
10. **Decision 12** — Add Section 6 display-only treatment of model state, gate_kind, recommendations, and kill-switch state.
11. **Decision 15** — Add Section 6 paper-only / non-executable order-intent display and no executable broker workflow.
12. **Decision 16** — Complete the previously pending UI disclosure surfacing contribution.
13. **Decision 17** — Replace pending UI-layer language with Section 6's approved screen scope, coverage map / screen list disposition, and read-only enforcement mechanism.
14. **Decision 18** — Confirm Section 6 does not change deployment/container architecture.

Expected matrix version after Section 6 lock: `docs/traceability_matrix.md` v0.9.

---

**End of Section 6 v1.0 LOCKED / APPROVED.**
