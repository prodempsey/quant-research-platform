# Engineering Specification — Section 5: Portfolio Rules, Paper Portfolio State, Broker-Neutral Order Intent, Promotion Gates, and Kill Switch

**Phase 1 scope:** ETF tactical research platform  
**Document status:** v1.0 LOCKED / APPROVED  
**Date:** 2026-04-30  
**Builder:** ChatGPT  
**QA Reviewer:** Claude  
**Approver:** Jeremy  
**Section:** Engineering Specification — Section 5: Portfolio Rules, Paper Portfolio State, Broker-Neutral Order Intent, Promotion Gates, and Kill Switch  
**Canonical path:** `docs/engineering_spec/05_portfolio_paper_order_intent.md`

**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED / APPROVED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Engineering Specification — Section 3a v1.0 LOCKED / APPROVED (`docs/engineering_spec/03a_feature_engineering.md`)
- Engineering Specification — Section 3b v1.0 LOCKED / APPROVED (`docs/engineering_spec/03b_target_generation.md`)
- Engineering Specification — Section 3c v1.0 LOCKED / APPROVED (`docs/engineering_spec/03c_model_layer_mlflow.md`)
- Engineering Specification — Section 4 v1.0 LOCKED / APPROVED (`docs/engineering_spec/04_backtest_attribution_validation.md`)
- Section approval notes and traceability companion files through Section 4
- Section 5 approval note (`docs/reviews/2026-04-30_spec_05_portfolio_paper_order_intent_approval.md`)
- Section 5 traceability updates (`docs/reviews/2026-04-30_spec_05_portfolio_paper_order_intent_traceability_updates.md`)
- `docs/traceability_matrix.md` v0.9

**Scope-statement basis.** Section 5 drafting is authorized from the Approver-provided Section 5 handoff prompt for working session `05_portfolio_paper_order_intent`, plus the locked documents listed above. The handoff explicitly assigns ChatGPT as Builder / spec drafter for this Section 5 drafting cycle only; Claude may later act as QA reviewer / stress tester; Jeremy remains final Approver. This draft does not globally modify the locked Engineering Workflow role assignment.

**Changelog**

- **v1.0 LOCKED / APPROVED (2026-04-30).** Section 5 v1.0 candidate promoted to v1.0 LOCKED / APPROVED with no substantive change to behavior, schema, tests, scope, or ownership. Locking metadata flipped to match the existing approval note, traceability companion, and traceability matrix lock merge. Lock package: `docs/reviews/2026-04-30_spec_05_portfolio_paper_order_intent_approval.md`; `docs/reviews/2026-04-30_spec_05_portfolio_paper_order_intent_traceability_updates.md`. Matrix merge: `docs/traceability_matrix.md` v0.8, later carried forward by v0.9.

- **v1.0 candidate (2026-04-30).** Section 5 candidate v1.0: Approver dispositions applied to v0.3; lock-package commit (approval note, traceability companion, traceability_matrix.md v0.8) pending. No implementation code is started. No approval note is created by this candidate. No traceability companion file is created by this candidate. `docs/traceability_matrix.md` is not updated by this candidate. Approver dispositions are applied surgically: A-PRP-05-01 through A-PRP-05-17 are accepted as Phase 1 defaults; Builder recommendations for A-OQ-05-01 through A-OQ-05-14 and A-OQ-05-16 are accepted; A-OQ-05-15 is resolved by approving existing Section 4 v1.0 evidence surfaces as sufficient for the Phase 1 Section 5 consumption gate, with no Section 4 amendment required before Section 5 lock; A-OQ-05-09 is resolved by allowing Section 5 to record model-state recommendations only in Section-5-owned tables, with no automated `models.*` writes; the gate terminology reconciliation is approved (`consumption` gate = 03c second promotion gate; `paper_to_real_recommendation` gate = Section 5 paper-evidence recommendation layer); and A-OQ-04-07 regime-classifier ownership remains unresolved outside Section 5.

  ID-space note: between v0.3 and v1.0, A-PRP-05-15 and A-PRP-05-16 swapped substantive meanings; v0.3 A-PRP-05-17, kill-switch limited behavior, was absorbed into A-PRP-05-05 because it duplicated that default; new v1.0 A-PRP-05-17 is Section 4 evidence sufficiency; v0.3 A-OQ-05-16, kill-switch-driven SELL/TRIM/REPLACE enablement, is deferred to future amendment and will be tracked as A-OQ-05-17. The Approver acceptance of A-PRP-05-01 through A-PRP-05-17 refers to the v1.0 ID-space.

- **v0.3 DRAFT (2026-04-30).** Targeted cleanup revision after QA residual review. Restored the no-UI-import boundary test for `portfolio/`, `paper/`, and `order_intent/`; added `data_snapshot_id` to `paper.portfolio_snapshots`; clarified REPLACE output cardinality; removed `portfolio.kill_switch_triggers` from the issue-log list because it is an evaluation-decomposition table, not an issue table; clarified the common Section-5 issue-table field shape; and added the Section 4 regime-classifier ownership carryover to Out of scope. Historical v0.1 and v0.2 changelog entries are preserved.

- **v0.2 DRAFT (2026-04-30).** Targeted QA-driven revision. Reconciled Section 5 gate terminology with the 03c approval note by relabeling the Section 5 consumption gate as the 03c second promotion gate and the paper-tracking gate as the paper-to-real-decisions recommendation layer; added explicit handling for sleeves / rank methods that do not emit `models.combined_scores` rows under 03c's first-testable formula; added cadence-independence test coverage against Section 4's ALC-09 reservation; carried forward A-OQ-04-18 as A-OQ-05-15; corrected kill-switch SELL wording to avoid contradiction with pause-new-intents scope; added formal field tables for `portfolio.kill_switch_evaluations`, `portfolio.kill_switch_triggers`, and `portfolio.promotion_evaluations`; added `gate_kind` to promotion evaluations; tied action conversion to evidence filtering and rank-method semantics; verified Section-4-owned schema names and locked terms including `backtest.backtest_runs.is_pipeline_validation_only`, `pipeline_validation_only_reason='cost_config_zero_fallback'`, `backtest.aggregate_metrics`, `backtest.fold_metrics`, `backtest.regime_metrics`, `backtest.backtest_run_issues`, `attribution.attribution_runs`, `attribution.signal_attribution`, `attribution.trade_attribution`, and `attribution.attribution_run_issues`; and applied minor cleanup items including explicit Open Question / Proposed Default cross-indexing. Builder remains ChatGPT for this Section 5 cycle.

- **v0.1 DRAFT (2026-04-30).** Initial Section 5 draft. Eleven EW §3.2 template fields populated in order. Every visible assumption is classified under EW §3.3. No implementation code is started. No approval note is created. No traceability companion file is created. `docs/traceability_matrix.md` is not updated by this draft. Section 5 remains pending until QA review, Approver review, any directed revisions, approval note creation, traceability companion creation, and matrix merge occur under the normal EW process.

---

## 1. Purpose

Section 5 defines the Phase 1 **portfolio-control and paper-portfolio layer** for the ETF tactical research platform. It converts approved model and validation evidence into paper-only portfolio decisions, maintains paper portfolio state, records broker-neutral non-executable order intents, evaluates the second SDR Decision 12 promotion gate, evaluates kill-switch conditions, and preserves a clear audit trail for paper-only lifecycle behavior.

Section 5 consumes outputs from prior locked sections:

- `models.combined_scores`, `models.scoring_runs`, and `models.model_versions` from Section 3c;
- `backtest.aggregate_metrics`, `backtest.regime_metrics`, `backtest.backtest_runs`, and related validation evidence surfaces from Section 4;
- `attribution.signal_attribution` and `attribution.trade_attribution` from Section 4 for explanation and review support;
- ETF identity, lifecycle, eligibility, sleeve, benchmark, and replacement metadata from Section 2;
- adjusted-close price data from Section 2 for paper valuation and paper-only reference prices.

Section 5 produces Section-5-owned records only:

- portfolio decision runs and portfolio action records under a Section-5-owned `portfolio.*` schema;
- paper portfolio state, paper position state, paper rebalance cycles, paper position events, and paper portfolio snapshots under a Section-5-owned `paper.*` schema;
- broker-neutral non-executable order-intent records under a Section-5-owned `order_intent.*` schema;
- promotion-gate evaluation records and kill-switch evaluation records under Section-5-owned schemas.

Section 5 is the first layer where model scores become paper portfolio actions, but it is still **not live trading**. Phase 1 remains a personal research and internal paper-portfolio platform. Section 5 must not connect to a broker, must not import broker SDKs, must not place orders, must not create executable broker instructions, and must not define UI behavior.

Section 5 deliberately keeps three concepts separate:

1. **Backtest simulated fills** from Section 4 — historical validation artifacts used to evaluate strategy behavior; not paper state; not order intent.
2. **Paper portfolio state** from Section 5 — current and historical internal paper-tracking state; not broker-facing.
3. **Broker-neutral order intent** from Section 5 — non-executable paper recommendation records; not routed to any broker and not sufficient to place an order.

---

## 2. Relevant SDR decisions

Section 5 directly implements or respects the following SDR decisions.

### Decision 1 — Project Scope and Phase 1 Boundaries

Section 5 implements the paper-portfolio and order-intent portions of Phase 1 while preserving the no-live-trading boundary. It introduces no real broker API adapter, live order placement, individual stocks, fundamentals, ETF holdings, news/events, earnings transcripts, options data, Danelfin, autonomous research agents, or commercial/customer-facing behavior.

### Decision 2 — Data Provider and Provider-Switching Strategy

No module under `portfolio/`, `paper/`, or `order_intent/` may call EODHD or any provider-specific API directly. Section 5 reads provider-normalized data from Postgres only. Provider-specific logic remains owned by `providers/` and `ingestion/` under Section 2.

### Decision 3 — ETF Universe and Eligibility Rules

Section 5 may create BUY, REPLACE, or WATCH actions only for ETFs that are rank-eligible at the relevant paper decision date. Section 5 does not re-derive universe eligibility. It reads `universe.etf_eligibility_history`, `universe.etfs`, and the Section 3c / Section 4 outputs that already respect upstream eligibility surfaces.

### Decision 4 — Universe Survivorship and ETF Launch-Date Handling

Section 5 owns portfolio-level behavior for optional replacement ETF semantics. Replacement metadata may be read from `universe.etfs.replacement_etf_id` or equivalent Section 2-owned lifecycle fields, but Section 5 may not rewrite ETF identity, ticker history, eligibility history, or provider mappings. If an ETF is delisted or exits lifecycle eligibility during paper tracking, Section 5 records paper actions against the existing `etf_id` and may generate a REPLACE or SELL action according to the approved portfolio rules.

### Decision 5 — Benchmark, Sleeve, and Diversifier Treatment

Section 5 respects the sleeve assignments and rank-method semantics established upstream. It does not silently substitute benchmarks, does not fall back to `secondary_benchmark_id`, and does not rank ETFs against an unauthorized sleeve or benchmark. Portfolio diversification rules operate over Section 2 sleeves and Section 3c combined-score ranks.

Per 03c §12.2 and the 03c approval note §1.4 item 14, `DiversifierHedge` ETFs with `rank_method = 'absolute_with_context'` produce no `models.combined_scores` rows under 03c's current first-testable formula. Section 5 v1.0 therefore treats those ETFs as eligible-but-unranked: they are excluded from BUY / HOLD / TRIM / SELL / REPLACE / WATCH action evaluation and an explanatory Section-5 issue row is emitted. Section 5 does not silently remap `DiversifierHedge` to `benchmark_relative`.

### Decision 6 — Target Design and Ranking Objective

Section 5 consumes model rankings and combined scores produced by Section 3c. It does not define targets, change target horizons, modify combined-score formulas, or reinterpret model outputs. Portfolio rules translate scores and ranks into paper actions.

### Decision 7 — Validation, Calibration, and Backtest Confidence Level

Section 5 reads Section 4 validation evidence to determine whether model outputs are eligible for paper tracking and whether a model should remain trusted for ongoing paper decisions. Section 5 does not implement walk-forward validation, purge / embargo logic, fold construction, OOS tagging, or validation metric formulas.

### Decision 8 — Transaction Cost and Account-Type Assumptions

Section 5 respects the cost evidence surfaced by Section 4. Section 5 does not directly compute transaction costs or read `config/costs.yaml` in Phase 1 v1.0; it consumes Section 4 validation evidence that already reflects the approved cost treatment. Direct Section 5 consumption of `config/costs.yaml` requires a future approved amendment.

### Decision 9 — Regime Taxonomy and Reporting

Section 5 consumes regime-conditioned performance evidence from Section 4. It does not own the unresolved regime classifier / labeler question from Section 4 (`A-OQ-04-07`) and does not silently resolve it. Regime evidence is used only as one gate / warning input in promotion and kill-switch evaluation.

### Decision 10 — Portfolio Management and Risk Rules

Section 5 is the primary cash-out of SDR Decision 10. It defines the Phase 1 paper-only portfolio rules engine that converts model output into the action vocabulary BUY, HOLD, TRIM, SELL, REPLACE, and WATCH. It specifies monthly rebalance, weekly risk review, top-5 initial positions, equal-weight initial sizing, configurable thresholds, ATR-style stop logic as a future or proposed rule surface, and no tight fixed stops or fixed take-profit rules by default.

### Decision 11 — Model Tracking, Attribution, Data Quality, and Lightweight MLOps

Section 5 records portfolio decisions, paper state, promotion evaluations, kill-switch evaluations, and order-intent records in Postgres, preserving Postgres as the system of record. Section 5 reads model-quality, data-quality, attribution, and backtest evidence but does not write to `ops.data_quality_exceptions`, MLflow, `models.*`, `backtest.*`, or `attribution.*`.

### Decision 12 — Model Promotion, Warning, Pause, and Retirement Rules

Section 5 owns:

- the **consumption gate** that determines when an Active model version may be consumed by paper portfolio tracking; this is the **03c second promotion gate** per the 03c approval note §1.7 item 20;
- the **paper-tracking → real-decisions recommendation gate**, which records evidence that paper tracking may influence real decisions but does not enable live trading;
- kill-switch evaluation over paper behavior and validation evidence;
- Section-5-owned recommendations for Warning / Paused / review outcomes.

This reconciles two compatible framings: the SDR describes Research → paper tracking and Paper tracking → real decisions, while the 03c approval note defines 03c's model-version registration as the first promotion gate and Section 5's paper-consumption decision as the second promotion gate. Section 5 uses explicit `gate_kind` values to avoid hidden gate-counting ambiguity.

Section 5 does not create an unapproved direct writer to `models.model_versions` or `models.model_state_history`. Section 5 may record model-state recommendations only in Section-5-owned tables. Any mechanical model-state transition must respect 03c's approved lifecycle and audit contract and requires a future 03c amendment.

### Decision 13 — LLM Advisory Use

No special Section 5 runtime feature is introduced. LLMs may assist in drafting, QA, and future review under the EW, but no autonomous trading or autonomous portfolio modification is allowed.

### Decision 14 — Danelfin Deferred

Danelfin and other external commercial signal providers remain out of Phase 1. Section 5 does not introduce them.

### Decision 15 — Broker-Neutral, No Live Trading, No Broker SDK

Section 5 implements broker-neutral order-intent records as paper-only, non-executable recommendation records. It must not import broker SDKs, store broker account identifiers, route orders, place orders, or create records that can be executed without a separate future approved live-trading architecture.

### Decision 16 — Phase 1 Success Criteria and Bias Controls

Section 5 contributes to Phase 1 success criteria by ensuring that paper decisions are traceable to approved model versions, scoring runs, data snapshots, backtest evidence, attribution evidence, and portfolio-rule configuration. Section 5 must not use Section 4 pipeline-validation-only backtests as serious promotion evidence and must preserve current-survivor / pipeline-validation disclosures for downstream Section 6 surfacing.

### Decision 17 — Operator UI Architecture

Section 5 produces read-side records that Section 6 may display. It does not define screens, filters, dashboard behavior, UI actions, or UI write permissions.

### Decision 18 — Deployment and Container Architecture

Section 5 introduces no new container. It runs inside the existing application container as scheduled or manually invoked command-line entry points after Section 5 is implemented. Configuration is stored in YAML under `config/portfolio.yaml`, mounted according to the existing container convention.

---

## 3. In scope

Section 5 covers the following.

1. **Portfolio rules engine for Phase 1 paper tracking.** Rules that convert approved model scores and ranks into paper-only BUY / HOLD / TRIM / SELL / REPLACE / WATCH actions.
2. **Paper-only decision lifecycle.** A lifecycle for generating, reviewing, recording, superseding, and auditing portfolio decisions without enabling live trading.
3. **Paper portfolio state schema.** Section-5-owned Postgres schema for paper portfolios, rebalance cycles, positions, position events, and paper portfolio snapshots.
4. **Broker-neutral order-intent schema.** Section-5-owned records that document paper-only intended portfolio actions without broker-specific fields, broker account identifiers, executable order types, routing instructions, or broker API linkage.
5. **Signal-to-paper-action conversion.** Deterministic conversion from `models.combined_scores` and existing paper position state to the Section 5 action vocabulary.
6. **Position selection and sizing rules.** Initial Phase 1 rule surface for top-5 ETF positions and equal-weight sizing, with thresholds stored in `config/portfolio.yaml`.
7. **Replacement logic.** Rules for REPLACE actions when a current paper holding materially weakens and a replacement candidate is clearly stronger.
8. **WATCH logic.** Rules for attractive candidates that should be monitored but not bought because of portfolio size, sleeve concentration, insufficient evidence, stale data, unresolved gate status, or risk blocks.
9. **Promotion-gate evaluation records.** Section-5-owned records documenting whether evidence supports consuming a model in paper tracking and whether paper tracking may influence real decisions.
10. **Kill-switch evaluation records.** Section-5-owned records documenting warnings, pauses, paper-intent suppression, and manual-review requirements triggered by defined conditions.
11. **Read-side evidence consumption.** Section 5 reads `models.*`, `backtest.*`, `attribution.*`, `universe.*`, and `prices.*` only as allowed inputs. It writes only to Section-5-owned schemas.
12. **Config ownership.** Section 5 owns `config/portfolio.yaml` at the spec level.
13. **Required tests.** Tests covering paper-only enforcement, no broker imports, no executable order fields, promotion-evidence filtering, action enum separation from Section 4, kill-switch behavior, paper state transitions, and write-boundary enforcement.

---

## 4. Out of scope

Section 5 explicitly does not cover the following.

1. Implementation code.
2. Live trading.
3. Broker API integration.
4. Broker SDK dependencies.
5. Real order placement.
6. Executable order objects.
7. Broker-specific order types, time-in-force values, account IDs, broker order IDs, routing venues, or broker credentials.
8. UI implementation, screens, filters, charts, callbacks, or UI behavior.
9. Section 6 read-only enforcement.
10. Feature formulas, feature alignment, or `features.*` writes.
11. Target formulas, target alignment, or `targets.*` writes.
12. Model fitting, prediction, ranking, calibration, combined-score formula, MLflow integration, or `models.*` schema changes.
13. Direct model-state writes unless a future approved 03c-compatible transition mechanism is explicitly authorized.
14. Backtest fold construction, purge / embargo logic, simulated fills, validation metric formulas, attribution formulas, or `backtest.*` / `attribution.*` writes.
15. Data ingestion, provider abstraction, raw provider payloads, data snapshots, or `ops.data_quality_exceptions` writes.
16. ETF universe mutation, benchmark substitution, sleeve assignment changes, ticker-history mutation, provider-mapping mutation, or `universe.*` writes.
17. Changes to adjusted-price convention or `prices.*` writes.
18. Danelfin, fundamentals, ETF holdings, news/events, earnings transcripts, options data, individual stocks, autonomous research agents, or commercial/customer-facing behavior.
19. Account-type tax treatment or live retirement-account trading constraints beyond paper-rule placeholders and approved deferrals.
20. `docs/traceability_matrix.md` updates; those belong to the eventual lock package after Section 5 is approved.
21. Regime classifier / labeler ownership (`A-OQ-04-07`) carried forward from Section 4. Section 5 does not own or resolve it; Section 5 only consumes regime evidence as a gate / kill-switch input subject to availability.

---

## 5. Inputs and outputs

### 5.1 Inputs read by Section 5

Section 5 may read the following inputs.

**Model and scoring inputs from Section 3c**

- `models.model_versions`, filtered to approved lifecycle states according to §6.3 below.
- `models.model_state_history`, read-only, for lifecycle audit context.
- `models.scoring_runs`, filtered to `status='succeeded'`.
- `models.scoring_run_models`, read-only, for model composition / source-model linkage.
- `models.combined_scores`, filtered through succeeded scoring runs.
- `models.scoring_run_issues`, read-only, for warning / failure context.

**Backtest and validation evidence from Section 4**

- `backtest.backtest_runs`, filtered to `status='succeeded'` and `is_pipeline_validation_only = false` for promotion evidence.
- `backtest.aggregate_metrics`, read-only, as aggregate validation evidence.
- `backtest.regime_metrics`, read-only, as regime-conditioned validation evidence.
- `backtest.fold_metrics`, read-only, for diagnostic review if the gate requires fold-level evidence.
- `backtest.backtest_run_issues`, read-only, for warning / failure context.
- `backtest.simulated_fills`, read-only, for offline review only. Section 5 must not treat it as paper portfolio state.

**Attribution evidence from Section 4**

- `attribution.attribution_runs`, filtered to `status='succeeded'` when used as required promotion evidence.
- `attribution.signal_attribution`, read-only, for explanation and quality review.
- `attribution.trade_attribution`, read-only, for explanation and quality review.
- `attribution.attribution_run_issues`, read-only, for warning / failure context.

**Universe and price inputs from Section 2**

- `universe.etfs`, read-only, for ETF identity, lifecycle, sleeve, benchmark, active, and optional replacement ETF metadata.
- `universe.etf_eligibility_history`, read-only, for rank-eligibility checks at the paper decision date.
- `universe.sleeves` and `universe.benchmarks`, read-only, for grouping and audit context.
- `prices.etf_prices_daily`, read-only, using `adjusted_close` as the paper valuation and paper reference-price input.
- `ops.data_snapshots`, read-only, for reproducibility linkage and invalidated-snapshot rejection.

**Configuration inputs**

- `config/portfolio.yaml`, Section-5-owned.
- `config/universe.yaml`, read-only through common config loaders for universe labels / disclosure context.
- `config/model.yaml`, read-only only if needed to validate that a consumed model/scoring run matches the expected model-set version; Section 5 does not own or mutate it.
- `config/backtest.yaml`, read-only only if needed to interpret validation evidence labels; Section 5 does not own or mutate it.

### 5.2 Outputs written by Section 5

Section 5 writes only to Section-5-owned schemas. Section 5 schemas:

- `portfolio.*` — decision runs, portfolio decisions, promotion evaluations, kill-switch evaluations, issue logs.
- `paper.*` — paper portfolios, rebalance cycles, positions, position events, portfolio snapshots, paper performance observations.
- `order_intent.*` — broker-neutral non-executable order-intent records and order-intent audit / supersession records.

No Section 5 process writes to `models.*`, `backtest.*`, `attribution.*`, `features.*`, `targets.*`, `universe.*`, `prices.*`, `ops.*`, or MLflow.

### 5.3 Output purpose

Section 5 outputs are designed to answer these questions:

- Which model version and scoring run produced the current paper recommendation?
- Which ETFs are currently held in the internal paper portfolio?
- Why did the rules generate BUY / HOLD / TRIM / SELL / REPLACE / WATCH?
- Which Section 4 evidence was used to permit or block paper tracking?
- Was any promotion evidence excluded because the source backtest was pipeline-validation-only?
- Did any kill-switch condition fire?
- Which paper-only non-executable order intents were generated, acknowledged, superseded, or cancelled?
- Can every paper action be traced back to a data snapshot, model version, scoring run, backtest run, attribution run, and portfolio config version?

---

## 6. Data contracts

### 6.1 Ownership and schema split

Section 5 owns three Postgres schemas.

1. **`portfolio` schema** — portfolio rule runs, decisions, promotion evaluations, kill-switch evaluations, and issue logs.
2. **`paper` schema** — paper portfolio state, paper positions, paper rebalance cycles, paper events, and paper snapshots.
3. **`order_intent` schema** — broker-neutral non-executable order intent records.

This split is an Approver-accepted Phase 1 default. It follows the Section 1 architectural package split (`portfolio/`, `paper/`, `order_intent/`) and keeps rule evaluation, state management, and order-intent audit logically separate.

### 6.2 Closed enums

Section 5 introduces the following proposed closed enums.

**Portfolio action enum**

`('BUY', 'HOLD', 'TRIM', 'SELL', 'REPLACE', 'WATCH')`

This enum is intentionally separate from Section 4's `backtest.simulated_fills.action` enum `('enter_long', 'exit_long', 'rebalance_in', 'rebalance_out')`. Section 5 must not write Section 4's enum, and Section 4 must not write Section 5's enum.

**Decision-run status enum**

`('running', 'succeeded', 'failed')`

This mirrors the status style of prior sections without adding a cross-schema dependency.

**Paper portfolio status enum**

`('active_paper', 'paused_by_kill_switch', 'paused_by_approver', 'retired_paper')`

`paused_by_kill_switch` suppresses new BUY / REPLACE order intents but does not delete positions or rewrite history.

**Paper position status enum**

`('open', 'trimmed', 'closed', 'replaced')`

A replaced position is closed from the perspective of active holdings but remains audit-visible as the source leg of a REPLACE action.

**Order-intent status enum**

`('generated', 'paper_acknowledged', 'superseded', 'cancelled_by_approver')`

These statuses are paper-only. None is equivalent to broker-submitted, broker-accepted, broker-filled, or broker-cancelled.

**Promotion-evaluation gate-kind enum**

`('consumption', 'paper_to_real_recommendation')`

`consumption` means the Section 5 consumption gate: an Active model version may be consumed by paper portfolio tracking. This is the 03c second promotion gate per the 03c approval note §1.7 item 20. `paper_to_real_recommendation` means the paper-tracking → real-decisions recommendation gate; it records evidence only and never enables live trading.

**Promotion-evaluation status enum**

`('not_evaluated', 'blocked', 'eligible_for_paper_tracking', 'paper_tracking_active', 'eligible_for_real_decision_influence_recommendation')`

Valid status values by `gate_kind`:

| `gate_kind` | Valid status values |
|---|---|
| `consumption` | `not_evaluated`, `blocked`, `eligible_for_paper_tracking`, `paper_tracking_active` |
| `paper_to_real_recommendation` | `not_evaluated`, `blocked`, `eligible_for_real_decision_influence_recommendation` |

The final status is a recommendation / evidence status only. It does not enable live trading and does not bypass Jeremy approval.

**Kill-switch result enum**

`('pass', 'warning_recommended', 'pause_new_intents', 'manual_review_required')`

`pause_new_intents` suppresses new BUY / REPLACE order intents in paper tracking. It does not place sell orders, does not modify live assets, and does not write to `models.*`.

### 6.3 Promotion-gate contracts

Section 5 records two gate categories.

#### Consumption gate (= 03c second promotion gate per 03c approval note §1.7 item 20)

The 03c approval note frames Section 5 as owning the second promotion gate: an Active model version may be consumed by the paper portfolio only after Section 5 verifies the supporting evidence. Section 5 therefore uses the label `consumption` for this gate. This reconciles SDR Decision 12's gate language with 03c's approved lifecycle framing without changing 03c ownership.

A model version is eligible for Section 5 paper tracking only when all of the following hold:

1. The model version is in `models.model_versions.state = 'Active'`.
2. The consumed scoring run has `models.scoring_runs.status = 'succeeded'`.
3. The scoring run's associated model runs and upstream feature / target chains are traceable through approved 03c metadata.
4. At least one supporting Section 4 backtest run has `backtest.backtest_runs.status = 'succeeded'`.
5. Every supporting promotion-evidence backtest run used by the gate has `backtest.backtest_runs.is_pipeline_validation_only = false`.
6. No zero-cost fallback / pipeline-validation-only evidence is used for promotion; the locked Section 4 reason value is `pipeline_validation_only_reason='cost_config_zero_fallback'`.
7. Required validation metrics are present in `backtest.aggregate_metrics` and, when the gate requires fold-level support, `backtest.fold_metrics`.
8. Required regime metrics are present when regime evidence is enabled; if regime evidence is unavailable due to unresolved `A-OQ-04-07`, the evaluation records this explicitly and applies the configured gate behavior.
9. Attribution evidence is present through a succeeded attribution run when attribution is required by the gate.
10. The evidence bundle is reproducible through `data_snapshot_id`, scoring-run, and model-version linkage.
11. No fail-severity Section 4 issue invalidates the evidence bundle.
12. Jeremy approval is recorded outside this spec's automated authority. Section 5 may record the approval reference but may not infer approval.

The existing Section 4 v1.0 evidence surfaces are approved as sufficient for this Phase 1 consumption gate. If implementation later proves that Section 4 lacks a field required to verify the evidence bundle above, that discovery triggers a future Section 4 amendment rather than a silent Section 5 workaround.

#### Paper-tracking → real-decisions recommendation gate

The SDR describes a Paper tracking → influence on real decisions gate. Section 5 records evidence for this gate using `gate_kind='paper_to_real_recommendation'`, but it does not enable live trading and does not bypass Jeremy approval.

A paper-to-real recommendation evaluation may become `eligible_for_real_decision_influence_recommendation` only when all configured requirements are satisfied, including:

1. Minimum paper observation window satisfied.
2. Minimum number of paper rebalance cycles completed.
3. Paper drawdown is within configured tolerance.
4. Paper turnover is within configured tolerance.
5. Paper behavior is explainable through decision records and attribution evidence.
6. No active kill-switch block exists.
7. Model output has behaved as expected under current regime evidence when regime evidence is available.
8. Jeremy approval remains required before real decisions are influenced.

All paper-to-real recommendation thresholds are accepted Phase 1 defaults in `config/portfolio.yaml` subject to future Approver amendment.

#### `portfolio.promotion_evaluations`

| Field | Purpose |
|---|---|
| `promotion_evaluation_id` | Surrogate primary key. |
| `gate_kind` | Closed enum `('consumption', 'paper_to_real_recommendation')`. |
| `portfolio_id` | FK to `paper.paper_portfolios`. |
| `model_version_id` | Read-side reference to `models.model_versions`. |
| `scoring_run_id` | Read-side reference to `models.scoring_runs`. |
| `backtest_run_id` | Read-side reference to `backtest.backtest_runs` when validation evidence is used. |
| `attribution_run_id` | Read-side reference to `attribution.attribution_runs` when attribution evidence is required. |
| `data_snapshot_id` | Read-side reference to the reproducibility chain used by the evidence bundle. |
| `as_of_date` | Evaluation date. |
| `status` | Promotion-evaluation status enum constrained by `gate_kind`. |
| `evidence_summary_json` | Redacted summary of required evidence and pass/fail details. |
| `approver_reference` | Optional manual approval reference; never inferred by automation. |
| `created_at_utc` | Audit timestamp. |

### 6.4 Kill-switch contract

Section 5 owns kill-switch evaluation, but v1.0 does not authorize direct unreviewed model-state writes to `models.*`.

Kill-switch evaluation reads:

- current paper portfolio drawdown and paper performance;
- recent paper decisions and order intents;
- latest Active model version and scoring run status;
- Section 4 aggregate / regime metrics;
- Section 4 issue logs;
- data snapshot status;
- configured thresholds in `config/portfolio.yaml`.

Kill-switch evaluation writes:

- `portfolio.kill_switch_evaluations` rows;
- `portfolio.kill_switch_triggers` rows as evaluation-decomposition records;
- optional Section-5-owned paper portfolio status update to `paused_by_kill_switch` when the result is `pause_new_intents`.

Kill-switch evaluation does not write to `models.model_versions` or `models.model_state_history`. Section 5 may record Warning / Paused / manual-review recommendations only in Section-5-owned tables. If the Approver later wants Section 5 to automate Active → Warning or Active → Paused transitions, the implementation must first be reconciled with 03c's lifecycle/audit contract and requires a 03c amendment.

#### `portfolio.kill_switch_evaluations`

| Field | Purpose |
|---|---|
| `kill_switch_evaluation_id` | Surrogate primary key. |
| `portfolio_id` | FK to `paper.paper_portfolios`. |
| `as_of_date` | Evaluation date. |
| `model_version_id` | Read-side reference to `models.model_versions`. |
| `scoring_run_id` | Read-side reference to `models.scoring_runs`. |
| `paper_snapshot_id` | FK to `paper.portfolio_snapshots` when paper performance is evaluated. |
| `data_snapshot_id` | Read-side reference to the reproducibility chain used by the scoring/evidence bundle. |
| `result` | Kill-switch result enum. |
| `should_pause_new_intents` | Boolean derived from `result='pause_new_intents'`. |
| `model_state_recommendation` | Optional recommendation such as Warning / Paused / manual review; Section 5-owned only. |
| `created_at_utc` | Audit timestamp. |
| `notes` | Redacted rationale. |

#### `portfolio.kill_switch_triggers`

`portfolio.kill_switch_triggers` decomposes a kill-switch evaluation into one or more trigger findings. It is not an issue-log table.

| Field | Purpose |
|---|---|
| `kill_switch_trigger_id` | Surrogate primary key. |
| `kill_switch_evaluation_id` | FK to `portfolio.kill_switch_evaluations`. |
| `trigger_type` | Closed trigger type such as `paper_drawdown`, `stale_scoring_run`, `invalidated_snapshot`, `validation_deterioration`, `regime_deterioration`, or `section4_fail_issue`. |
| `severity` | Closed enum `('warning', 'fail')`. |
| `threshold_value` | Configured threshold when numeric. |
| `observed_value` | Observed value when numeric. |
| `plain_english_explanation` | Redacted explanation. |
| `created_at_utc` | Audit timestamp. |

### 6.5 Portfolio decision run contract

A portfolio decision run evaluates one portfolio at one decision date using one active model version and one scoring run.

`portfolio.decision_runs` fields:

| Field | Purpose |
|---|---|
| `decision_run_id` | Surrogate primary key. |
| `portfolio_id` | FK to `paper.paper_portfolios`. |
| `as_of_date` | Paper decision date. |
| `model_version_id` | Read-side reference to `models.model_versions`. |
| `scoring_run_id` | Read-side reference to `models.scoring_runs`. |
| `data_snapshot_id` | Read-side reference to the snapshot chain used by the scoring run. |
| `portfolio_config_version` | Version label from `config/portfolio.yaml`. |
| `portfolio_config_hash` | Hash of the effective portfolio config. |
| `status` | Closed enum `('running', 'succeeded', 'failed')`. |
| `started_at_utc` / `completed_at_utc` | Run lifecycle timestamps. |
| `error_message` | Redacted failure summary. |
| `notes` | Optional redacted notes. |

A decision run opens before semantic validation after config parse succeeds. If validation fails after open, the run is marked `failed`, a `portfolio.decision_run_issues` row is written, and no `portfolio.decisions` rows are written.

### 6.6 Portfolio decision record contract

`portfolio.decisions` fields:

| Field | Purpose |
|---|---|
| `decision_id` | Surrogate primary key. |
| `decision_run_id` | FK to `portfolio.decision_runs`. |
| `portfolio_id` | FK to `paper.paper_portfolios`. |
| `as_of_date` | Decision date. |
| `etf_id` | ETF receiving the action. |
| `replacement_etf_id` | Optional ETF replacing `etf_id` for REPLACE actions. |
| `action` | Closed enum BUY / HOLD / TRIM / SELL / REPLACE / WATCH. |
| `current_weight` | Paper weight before action. |
| `target_weight` | Paper target weight after action. |
| `target_weight_delta` | `target_weight - current_weight`. |
| `score_rank` | Rank value read from `models.combined_scores`. |
| `combined_score` | Combined score read from `models.combined_scores`. |
| `sleeve_id` | Sleeve reference used for selection / concentration rules. |
| `horizon_trading_days` | Horizon associated with the score used. |
| `decision_reason_code` | Closed reason code from config. |
| `plain_english_reason` | Redacted human-readable rationale. |
| `blocked_by_gate` | Boolean, true if the action would otherwise qualify but is blocked by gate status. |
| `blocked_by_kill_switch` | Boolean, true if suppressed by kill switch. |
| `created_at_utc` | Audit timestamp. |

No decision row is executable. Decisions are the semantic layer; order intents are the paper-intent audit layer.

### 6.7 Paper portfolio state contract

`paper.*` tables:

#### `paper.paper_portfolios`

Tracks each paper portfolio.

Key fields:

- `portfolio_id`
- `portfolio_name`
- `base_currency`
- `status`
- `created_at_utc`
- `retired_at_utc`
- `notes`

Phase 1 default: one internal paper portfolio. Multiple portfolios are structurally supported but not required.

#### `paper.rebalance_cycles`

Tracks each monthly rebalance or weekly risk review cycle.

Key fields:

- `rebalance_cycle_id`
- `portfolio_id`
- `cycle_type` — proposed enum `('monthly_rebalance', 'weekly_risk_review', 'manual_review')`
- `as_of_date`
- `decision_run_id`
- `status` — proposed enum `('opened', 'completed', 'failed', 'superseded')`
- `started_at_utc`
- `completed_at_utc`

#### `paper.positions`

Tracks current and historical paper positions.

Key fields:

- `paper_position_id`
- `portfolio_id`
- `etf_id`
- `status`
- `opened_as_of_date`
- `closed_as_of_date`
- `opening_decision_id`
- `closing_decision_id`
- `target_weight_current`
- `paper_quantity_current`
- `paper_cost_basis`
- `last_valuation_price`
- `last_valuation_date`

`paper_quantity_current` is a paper-only quantity used for internal performance measurement. It is not a broker quantity and cannot be submitted to a broker.

#### `paper.position_events`

Tracks immutable paper state changes.

Key fields:

- `paper_event_id`
- `paper_position_id`
- `rebalance_cycle_id`
- `decision_id`
- `order_intent_id`
- `event_type` — proposed enum `('paper_open', 'paper_add', 'paper_trim', 'paper_close', 'paper_replace_out', 'paper_replace_in', 'paper_hold_review')`
- `event_as_of_date`
- `paper_quantity_before`
- `paper_quantity_after`
- `target_weight_before`
- `target_weight_after`
- `paper_reference_price`
- `created_at_utc`

#### `paper.portfolio_snapshots`

Tracks paper portfolio valuation and risk-review evidence.

Key fields:

- `paper_snapshot_id`
- `portfolio_id`
- `as_of_date`
- `total_paper_value`
- `cash_placeholder_value`
- `gross_exposure`
- `net_exposure`
- `paper_return_since_prior_snapshot`
- `paper_drawdown_from_peak`
- `position_count`
- `active_model_version_id`
- `scoring_run_id`
- `data_snapshot_id` — Read-side reference to the snapshot chain used by the scoring run for this snapshot's evidence; denormalized for direct reproducibility.
- `created_at_utc`

Paper snapshots are Section 5's paper-performance source. They are separate from Section 4 metrics and Section 4 simulated fills.

### 6.8 Broker-neutral order-intent contract

`order_intent.order_intents` fields:

| Field | Purpose |
|---|---|
| `order_intent_id` | Surrogate primary key. |
| `portfolio_id` | FK to `paper.paper_portfolios`. |
| `decision_id` | FK to `portfolio.decisions`. |
| `rebalance_cycle_id` | FK to `paper.rebalance_cycles`. |
| `as_of_date` | Paper intent date. |
| `action` | BUY / HOLD / TRIM / SELL / REPLACE / WATCH. |
| `etf_id` | ETF for the intent. |
| `replacement_etf_id` | Optional replacement ETF for REPLACE. |
| `target_weight_before` | Paper target weight before intent. |
| `target_weight_after` | Paper target weight after intent. |
| `target_weight_delta` | Target weight change. |
| `paper_reference_price` | Adjusted-close reference price used for paper calculation. |
| `paper_notional_delta` | Paper-only notional change. |
| `is_executable` | Must be `false`; enforced by CHECK. |
| `broker_name` | Must be NULL in Phase 1. |
| `broker_account_id` | Must be NULL in Phase 1. |
| `broker_order_id` | Must be NULL in Phase 1. |
| `order_type` | Must be NULL in Phase 1. |
| `time_in_force` | Must be NULL in Phase 1. |
| `status` | Paper-only status enum. |
| `plain_english_intent` | Redacted explanation. |
| `created_at_utc` | Audit timestamp. |
| `superseded_by_order_intent_id` | Optional self-reference. |

The non-executable constraint is central. If any future live-trading phase wants executable orders, it must create a new approved architecture and must not silently reinterpret these Phase 1 records as broker orders.

### 6.9 Action conversion rules

The following are Approver-accepted Phase 1 defaults. Exact numeric thresholds live in `config/portfolio.yaml`.

Action conversion applies only to ETFs whose sleeve and `rank_method` produce a `models.combined_scores` row under the active 03c first-testable formula. Under the locked 03c first-testable formula, `DiversifierHedge` / `absolute_with_context` ETFs produce no `models.combined_scores` rows. Section 5 therefore excludes those ETFs from BUY / HOLD / TRIM / SELL / REPLACE / WATCH evaluation in v1.0 and records an explanatory Section-5 issue row when such an ETF would otherwise be considered. This preserves 03c's first-testable formula boundary and prevents Section 5 from inventing a ranking path.

Every action conversion reads evidence through §6.10 filtering rules before it emits a decision. No action conversion may bypass the consumption gate, use pipeline-validation-only evidence, consume zero-cost-fallback evidence as promotion-grade evidence, or infer model-state approval.

#### BUY

Generate BUY when:

- ETF is rank-eligible at decision date;
- ETF is not already held;
- ETF's sleeve and `rank_method` emit a `models.combined_scores` row under the active 03c formula;
- model version is Active and `gate_kind='consumption'` is eligible;
- scoring run succeeded;
- ETF is within the configured top-rank threshold;
- combined score clears the configured score threshold;
- portfolio has open capacity under top-position and sleeve-concentration limits;
- kill switch does not block new intents.

#### HOLD

Generate HOLD when:

- ETF is already held;
- ETF remains rank-eligible and within lifecycle bounds;
- ETF's sleeve and `rank_method` emit a current `models.combined_scores` row under the active 03c formula;
- rank / score remain within configured hold tolerance;
- no SELL / TRIM / REPLACE condition dominates;
- kill switch does not require suppression or manual review.

#### TRIM

Generate TRIM when:

- ETF is already held;
- ETF's sleeve and `rank_method` emit a current `models.combined_scores` row under the active 03c formula;
- target weight declines but does not fall to zero;
- rank / score deteriorate within a configured trim band;
- sleeve concentration or position drift requires reducing weight;
- no stronger replacement threshold is met.

#### SELL

Generate SELL when:

- ETF is already held;
- ETF is no longer rank-eligible, no longer active, past lifecycle bounds, or lacks required price data;
- rank / score deteriorate beyond configured sell threshold;
- risk-review rule requires exit.

Kill-switch-driven SELL is out of v1.0 scope and requires a future amendment. The v1.0 kill switch only suppresses new BUY / REPLACE intents and records review / warning recommendations in Section-5-owned tables.

#### REPLACE

Generate REPLACE when:

- existing held ETF qualifies for SELL or severe TRIM;
- candidate ETF qualifies for BUY;
- both the existing ETF and the candidate are supported by sleeve / `rank_method` semantics that emit `models.combined_scores` rows under the active 03c formula;
- candidate ETF is materially stronger by configured rank / score / sleeve-relative margin;
- replacement does not violate position count or concentration rules;
- replacement ETF metadata is valid and no silent benchmark substitution is introduced.

REPLACE is recorded as a single portfolio decision with both `etf_id` and `replacement_etf_id`, and as two paper events: `paper_replace_out` and `paper_replace_in`. REPLACE produces one `portfolio.decisions` row, one `order_intent.order_intents` row (with both `etf_id` and `replacement_etf_id` populated), and two `paper.position_events` rows (`paper_replace_out` and `paper_replace_in`).

#### WATCH

Generate WATCH when:

- candidate ETF appears attractive but portfolio capacity, sleeve concentration, gate status, evidence sufficiency, or kill-switch status prevents BUY;
- model evidence is promising but not yet enough for paper action;
- an ETF is a potential replacement but does not clear the material-strength threshold.

WATCH records are useful for review but do not alter paper positions and do not create executable intent.

### 6.10 Required evidence filtering rules

Promotion-gate and kill-switch evaluation must enforce these read-side rules:

1. Use only succeeded scoring runs.
2. Use only Active model versions for routine paper actions.
3. Use only succeeded Section 4 validation evidence.
4. Exclude every backtest run where `backtest.backtest_runs.is_pipeline_validation_only = true` from serious promotion evidence.
5. Do not treat zero-cost fallback / pipeline-validation-only evidence as promotion-grade evidence; the locked Section 4 reason value is `pipeline_validation_only_reason='cost_config_zero_fallback'`.
6. Require `backtest.aggregate_metrics` evidence, and `backtest.fold_metrics` evidence when the gate configuration requires fold-level support, for the relevant sleeve and horizon.
7. Require succeeded attribution evidence where attribution is required by the gate.
8. Do not use failed attribution runs as required attribution evidence.
9. Do not use invalidated data snapshots.
10. Require reproducible linkage through `data_snapshot_id`, scoring run, and model version.
11. Reject evidence bundles with fail-severity Section 4 issues that invalidate the evidence.
12. Preserve current-survivor disclosure context when evidence traces to Core Test Universe / current-survivor results.

The existing Section 4 v1.0 evidence surfaces are sufficient for the Phase 1 Section 5 consumption gate. If implementation later proves Section 4 lacks a required field to verify this evidence bundle, that discovery triggers a future Section 4 amendment.

### 6.11 Issue logs

Section 5 issue logs are separate from `ops.data_quality_exceptions`.

All Section-5 issue tables share the common field shape enumerated below, plus the table-specific FK columns named earlier in §6 (for example, `decision_run_id` on `portfolio.decision_run_issues`, `promotion_evaluation_id` on `portfolio.promotion_evaluation_issues`, `paper_snapshot_id` or `portfolio_id` on `paper.paper_state_issues`, and `order_intent_id` on `order_intent.order_intent_issues`).

Issue tables:

- `portfolio.decision_run_issues`
- `portfolio.promotion_evaluation_issues`
- `paper.paper_state_issues`
- `order_intent.order_intent_issues`

Issue records include:

- issue type;
- severity `('warning', 'fail')`;
- plain-English explanation;
- why it matters;
- likely cause;
- suggested resolution;
- whether auto-resolution is allowed;
- what was auto-resolved;
- what Jeremy must approve;
- redacted technical context JSON.

Section 5 may not write to `ops.data_quality_exceptions`; the Section 5 issue logs are local to Section 5 schemas.

---

## 7. Config dependencies

### 7.1 Section-5-owned config

Section 5 owns `config/portfolio.yaml`.

Top-level sections:

| Config section | Purpose |
|---|---|
| `portfolio_config_version` | Human-readable config version label. |
| `portfolio_id` | Default paper portfolio identifier / name. |
| `cadence` | Monthly rebalance and weekly risk-review schedule labels. |
| `position_limits` | Top-5 initial position limit, sleeve concentration, max position count. |
| `sizing` | Equal-weight initial sizing and later volatility-adjusted sizing placeholder. |
| `action_thresholds` | BUY / HOLD / TRIM / SELL / REPLACE / WATCH thresholds. |
| `replacement_rules` | Required material-strength margin for REPLACE. |
| `risk_rules` | ATR-style stop surface, drawdown warning/pause thresholds, no tight fixed stops. |
| `promotion_gates` | Gate 1 consumption check and Gate 2 paper-to-real-decision recommendation thresholds. |
| `kill_switch` | Kill-switch conditions and result mapping. |
| `order_intent` | Non-executable order-intent enforcement settings. |
| `paper_account` | Paper-only starting value, base currency, cash placeholder behavior. |
| `evidence_requirements` | Required Section 4 validation / attribution evidence. |
| `disclosures` | Paper-only / non-executable labels to carry forward to UI. |

### 7.2 Config values derived from SDR

The following are derived from SDR Decision 10 unless the Approver directs otherwise:

- `cadence.monthly_rebalance = true`
- `cadence.weekly_risk_review = true`
- `position_limits.max_positions_initial = 5`
- `sizing.initial_method = equal_weight`
- action enum includes BUY, HOLD, TRIM, SELL, REPLACE, WATCH
- fixed take-profit disabled by default
- tight fixed stops disabled by default
- ATR-style stop support reserved or enabled by configuration

### 7.3 Phase 1 defaults accepted by Approver

The following numeric or behavioral thresholds are accepted as Phase 1 defaults at the spec level and live in `config/portfolio.yaml`. Future changes are strategy-affecting and require Approver review:

- BUY rank threshold.
- BUY combined-score threshold.
- HOLD rank tolerance.
- TRIM rank / score deterioration threshold.
- SELL rank / score deterioration threshold.
- REPLACE material-strength margin.
- Maximum sleeve concentration.
- Minimum supporting backtest count for the consumption gate.
- Required validation metric thresholds for the consumption gate.
- Required paper observation period for the paper-to-real recommendation gate.
- Required number of paper rebalance cycles for the paper-to-real recommendation gate.
- Maximum paper drawdown for the paper-to-real recommendation gate.
- Kill-switch paper drawdown warning and pause thresholds.
- Kill-switch stale-scoring-run threshold.
- Kill-switch regime-deterioration threshold.

### 7.4 Config files read but not owned

Section 5 may read, but does not own:

- `config/universe.yaml` — disclosure labels and universe context.
- `config/model.yaml` — model-set version context only, if needed.
- `config/backtest.yaml` — validation evidence labels only, if needed.

Section 5 does not read `config/costs.yaml` directly in Phase 1 v1.0 except through Section 4 validation evidence. Direct Section 5 consumption of `config/costs.yaml` requires a future approved amendment.

### 7.5 Config validation

Required validation rules include:

- all enum values must be closed-set;
- position counts must be positive integers;
- weights must be non-negative and must not exceed 1.0 where applicable;
- threshold ordering must be coherent, e.g. BUY threshold must be stricter than WATCH threshold where both apply;
- REPLACE material-strength margin must be positive;
- kill-switch pause threshold must be at least as severe as warning threshold;
- fixed take-profit rules must be disabled unless a future approved amendment enables them;
- broker / account / executable-order settings must be absent or explicitly null in Phase 1.

---

## 8. Required tests

The following tests are required before Section 5 implementation can be considered complete. Test names are descriptive placeholders; final file names and exact test names are implementation details.

### 8.1 Boundary and import tests

1. **No broker SDK imports.** Static test confirms `portfolio/`, `paper/`, and `order_intent/` do not import Schwab, IBKR, Alpaca, broker SDKs, broker API clients, or any broker-routing package.
2. **No provider imports.** Static test confirms Section 5 modules do not import `providers/` or provider-specific libraries.
3. **No direct EODHD / provider credential access.** Static test confirms Section 5 modules do not require provider credentials or provider-specific environment variables.
4. **No writes to prior-section schemas.** Static / integration test confirms Section 5 writes only to `portfolio.*`, `paper.*`, and `order_intent.*`.
5. **No writes to `ops.data_quality_exceptions`.** Integration test confirms Section 5 issue paths write only to Section-5-owned issue tables.
6. **No `backtest.simulated_fills` as paper state.** Static / integration test confirms Section 5 does not consume `backtest.simulated_fills` as authoritative paper portfolio state.
7. **No UI imports.** Static test confirms no module under `portfolio/`, `paper/`, or `order_intent/` imports any `ui/` module.
8. **No executable order objects.** Static test confirms no Phase 1 order-intent record contains broker-specific executable-order fields beyond the required NULL / false fields.
9. **No `models.*` writes.** Static / integration test confirms Section 5 records model-state recommendations only in Section-5-owned tables.
10. **No Section 4 rewrite.** Static check confirms Section 5 does not import Section 4 internals in a way that reimplements fold construction, simulated fills, attribution, or validation metrics.
11. **No secondary-benchmark fallback.** Static / fixture test confirms Section 5 does not silently substitute `secondary_benchmark_id`.
12. **No out-of-scope data sources.** Static test confirms no fundamentals, holdings, news/events, earnings transcripts, options data, Danelfin, individual stocks, autonomous agents, or commercial/customer-facing modules are introduced.
13. **Config ownership boundary.** Static test confirms `config/portfolio.yaml` is Section-5-owned and that Section 5 reads other config files only through approved read-only seams.
14. **Cadence independence / ALC-09.** Static / integration test confirms `config/portfolio.yaml` rebalance / risk-review cadence does not read from or share schema with `config/backtest.yaml` rebalance cadence, and that no module under `portfolio/`, `paper/`, or `order_intent/` couples cadence to `config/backtest.yaml`.

### 8.2 Config validation tests

15. **Pipeline-validation-only exclusion.** Gate evaluation rejects or excludes `backtest.backtest_runs.is_pipeline_validation_only = true` from serious promotion evidence.
16. **Zero-cost fallback exclusion.** Gate evaluation does not treat `pipeline_validation_only_reason='cost_config_zero_fallback'` evidence as promotion-grade evidence.
17. **`config/portfolio.yaml` closed enum validation.** Unknown action, status, cycle, gate-kind, promotion-status, and kill-switch result values are rejected.
18. **Threshold ordering validation.** Incoherent action thresholds are rejected.
19. **Position-limit validation.** Non-positive max position count is rejected.
20. **Gate-kind / status matrix.** `portfolio.promotion_evaluations.status` values are validated against `gate_kind`.
21. **Sizing validation.** Equal-weight configuration produces total target weights that do not exceed 1.0.
22. **Kill-switch threshold validation.** Pause thresholds cannot be less severe than warning thresholds.
23. **Broker-field rejection.** Config containing broker name, account number, routing, or executable-order settings is rejected.
24. **Direct `config/costs.yaml` rejection.** Phase 1 Section 5 config validation rejects direct paper-cost modeling unless a future amendment enables it.
25. **Unranked-sleeve behavior config.** Config explicitly documents that `DiversifierHedge` / `absolute_with_context` ETFs are excluded from action conversion unless a future 03c formula emits combined scores for them.
26. **Paper starting-value validation.** Paper starting value and cash-placeholder settings are positive / coherent.

### 8.3 Promotion-gate tests

27. **Succeeded-backtest-only evidence.** Failed or running backtests cannot satisfy gate evidence requirements.
28. **Succeeded-attribution-only evidence.** Failed or running attribution runs cannot satisfy required attribution evidence.
29. **Active-model-version requirement.** Routine paper action generation requires `models.model_versions.state = 'Active'` unless the run is explicitly a diagnostic dry-run that writes no paper actions.
30. **Succeeded-scoring-run requirement.** Decision run fails cleanly if scoring run status is not `succeeded`.
31. **Invalidated snapshot block.** Gate evaluation fails when the evidence chain points to an invalidated data snapshot.
32. **Consumption-gate evidence bundle.** Consumption gate requires the approved evidence bundle from §6.10.
33. **Action enum separation.** Section 5 never emits Section 4 simulated-fill actions.
34. **Paper-to-real observation requirement.** Paper-to-real recommendation gate cannot recommend influence on real decisions before configured paper observation period and rebalance-cycle count are met.
35. **Gate recommendation only.** `eligible_for_real_decision_influence_recommendation` remains a recommendation status and does not enable live trading or broker connectivity.

### 8.4 Action conversion tests

36. **BUY conversion.** Known input where an unheld ETF clears rank, score, eligibility, gate, and risk thresholds produces BUY.
37. **HOLD conversion.** Known input where held ETF remains inside hold tolerance produces HOLD.
38. **TRIM conversion.** Known input where held ETF deteriorates into trim band produces TRIM and target weight reduction.
39. **SELL conversion.** Known input where held ETF fails eligibility or sell threshold produces SELL, without relying on kill-switch-driven SELL.
40. **REPLACE conversion.** Known input where held ETF weakens and candidate is materially stronger produces one decision row, one order-intent row, and two paper position events.
41. **No simulated-fill dependency.** Paper state and action conversion can be reconstructed without reading `backtest.simulated_fills`.
42. **WATCH conversion.** Known input where candidate is attractive but blocked by capacity or gate produces WATCH and no paper position change.
43. **Non-executable CHECK.** `order_intent.order_intents.is_executable` must be false.
44. **Broker fields NULL.** Broker name, broker account ID, broker order ID, order type, and time in force must be NULL in Phase 1.
45. **No broker account identifiers.** Schema and fixtures reject broker account identifiers or routing venues.
46. **Order intent created for BUY / TRIM / SELL / REPLACE.** Eligible paper actions create non-executable order-intent records.
47. **WATCH creates no executable-like intent.** WATCH may create a review intent only, with zero target-weight delta and non-executable status.
48. **Unranked-sleeve handling.** ETFs whose sleeve / `rank_method` produces no `models.combined_scores` row under the active 03c formula receive no BUY / HOLD / TRIM / SELL / REPLACE / WATCH action and produce an explanatory Section-5 issue row.
49. **Rank-method semantics.** BUY / HOLD / TRIM / SELL / REPLACE rules are evaluated only within the rank-method-defined cross-section represented by `models.combined_scores`.

### 8.5 Paper portfolio state tests

50. **Paper position open event.** BUY creates an open paper position and paper_open event.
51. **Paper hold event.** HOLD creates review evidence but does not alter paper quantity or target weight.
52. **No direct model-state write.** Kill-switch evaluation does not write to `models.model_versions` or `models.model_state_history`.
53. **Paper trim event.** TRIM reduces target weight and writes immutable event history.
54. **Paper sell event.** SELL closes the paper position without deleting history.
55. **Paper replace event pair.** REPLACE writes both replace-out and replace-in events and preserves linkage.
56. **Snapshot valuation.** Paper portfolio snapshot computes paper value from adjusted-close reference prices and records `data_snapshot_id`.
57. **Idempotent rebalance cycle.** Re-running the same approved decision run does not duplicate paper events unless an explicit supersession path is used.
58. **Decision-to-evidence traceability.** Every portfolio decision links to model version, scoring run, data snapshot chain, supporting backtest / attribution evidence where required, portfolio config version, and portfolio config hash.


## 9. Edge cases and failure behavior

1. **No Active model version.** Decision run opens, fails semantic validation, writes a `portfolio.decision_run_issues` fail row, and writes no decisions or order intents.
2. **Scoring run not succeeded.** Decision run fails and writes no decisions.
3. **No eligible combined-score rows.** Decision run succeeds with zero BUY / REPLACE candidates only if existing holdings can be evaluated; otherwise it fails or writes WATCH / manual-review records depending on config.
4. **Candidate ETF not rank-eligible.** No BUY / REPLACE action is generated for that ETF. If it otherwise looked attractive, a WATCH record may explain the eligibility block.
5. **Held ETF becomes ineligible or delisted.** Section 5 records a SELL or REPLACE recommendation according to portfolio rules; it does not mutate `universe.*`.
6. **Replacement ETF metadata exists but candidate evidence is weak.** Section 5 may WATCH the candidate but must not REPLACE unless material-strength threshold is satisfied.
7. **Backtest evidence is pipeline-validation-only.** Gate evaluation excludes it from serious evidence and records a warning / block.
8. **Zero-cost fallback evidence.** Gate evaluation excludes `pipeline_validation_only_reason='cost_config_zero_fallback'` from promotion-grade evidence.
9. **Attribution evidence missing.** Gate evaluation blocks or marks attribution-pending depending on config; no silent pass.
10. **Regime classifier unresolved.** Section 5 does not resolve A-OQ-04-07; if regime evidence is unavailable, behavior follows `config/portfolio.yaml` gate setting and records explicit issue context.
11. **Unranked sleeve / rank-method.** If an ETF's sleeve / `rank_method` produces no `models.combined_scores` row under the active 03c formula, Section 5 emits no portfolio action for that ETF and records an explanatory issue row.
12. **Active → Warning trigger requested.** Section 5 records kill-switch evaluation and may recommend Warning, but no automated `models.*` transition occurs unless a 03c-compatible amendment is approved.
13. **Kill switch fires during monthly rebalance.** New BUY / REPLACE intents are suppressed. Existing paper positions remain intact until configured review / SELL logic is applied.
14. **Kill switch fires during weekly risk review.** A kill-switch evaluation is written; optional paper portfolio status changes to `paused_by_kill_switch`; no broker action occurs.
15. **Paper valuation price missing.** Decision run records an issue; affected ETF cannot generate BUY / REPLACE; existing position may be marked manual review.
16. **Order-intent creation fails after decisions are written.** Decision run is marked failed unless the transaction boundary can roll back decisions and intents together. Accepted default: decisions and order intents for a single decision run commit atomically.
17. **Partially superseded intents.** Supersession records retain old intent history and point to the replacement intent. No destructive overwrite.
18. **Config parse failure before run context.** If `config/portfolio.yaml` is unreadable or lacks the keys required to construct a run context, no run row is opened; error goes to stderr / scheduler logs only.
19. **Config semantic failure after run opens.** Run is marked failed and a Section-5 issue row is written.
20. **Duplicate decision run for same portfolio / date / model / scoring run.** Accepted default: enforce natural uniqueness and require explicit supersession to rerun.
21. **User attempts to treat order intent as executable.** Schema CHECK constraints and static tests prevent executable fields in Phase 1; future live trading requires a separate approved architecture.
22. **Section 4 evidence appears insufficient during implementation.** The implementation must stop and request a future Section 4 amendment; Section 5 may not invent missing Section 4 evidence semantics.


## 10. Open questions

No Section-5-level Open Questions remain unresolved for the v1.0 candidate disposition set. The Approver resolved A-OQ-05-01 through A-OQ-05-17 as follows. Future changes to these dispositions require the normal EW amendment / Approval Matrix process.

### A-OQ-05-01 — Exact Section-5 schema split

Resolved: use the three-schema split `portfolio.*`, `paper.*`, and `order_intent.*`.

### A-OQ-05-02 — Exact paper portfolio state shape

Resolved: include position-level, rebalance-cycle-level, portfolio-snapshot-level, and order-intent / recommendation-level state so paper behavior is replayable and understandable before any real-decision influence.

### A-OQ-05-03 — Exact order-intent schema location

Resolved: use `order_intent.*` to keep the broker-neutral paper-intent surface visibly separate from paper position state.

### A-OQ-05-04 — Exact portfolio action enum

Resolved: keep the SDR enum as the closed Section 5 action enum: BUY, HOLD, TRIM, SELL, REPLACE, WATCH. Represent no-action / review through decision-run outcomes or issue records, not as portfolio actions.

### A-OQ-05-05 — Numeric action thresholds

Resolved: keep numeric thresholds in `config/portfolio.yaml`; do not hard-code them. Threshold changes remain strategy-affecting config changes.

### A-OQ-05-06 — Promotion-gate evidence thresholds

Resolved: require the minimum evidence bundle in §6.10 for the consumption gate. Exact numeric values live in `config/portfolio.yaml` and require Approver review when changed.

### A-OQ-05-07 — Minimum paper observation period for paper-to-real recommendation gate

Resolved: require both a minimum calendar duration and a minimum number of completed rebalance cycles.

### A-OQ-05-08 — Kill-switch conditions and thresholds

Resolved: include paper drawdown, stale scoring evidence, invalidated snapshot chain, unacceptable validation evidence, and serious Section 4 issue flags as kill-switch trigger categories; exact thresholds live in `config/portfolio.yaml`.

### A-OQ-05-09 — Active → Warning automation

Resolved: Section 5 may record model-state recommendations only in Section-5-owned tables. It must not write to `models.*` and must not automate Active → Warning. Any mechanical model-state transition requires a future 03c amendment.

### A-OQ-05-10 — Direct `config/costs.yaml` consumption

Resolved: consume costs only through Section 4 validation evidence in Phase 1; defer direct paper-cost modeling unless a future amendment enables it.

### A-OQ-05-11 — Account-type handling

Resolved: defer account-type execution constraints because Phase 1 order intents are non-executable; store only paper-only placeholders and do not model tax/account restrictions in v1.0.

### A-OQ-05-12 — Should order intent be stored without broker integration?

Resolved: yes. Store non-executable order intents to create an audit trail of what the system would have recommended without enabling trading.

### A-OQ-05-13 — Paper starting value and cash placeholder

Resolved: store paper starting value and cash-placeholder behavior in `config/portfolio.yaml`.

### A-OQ-05-14 — ATR stop implementation depth

Resolved: reserve ATR-style stop support in config but defer exact ATR formula unless a future approved amendment adds it.

### A-OQ-05-15 — Backtest confidence-level output sufficiency

Resolved: the existing Section 4 v1.0 evidence surfaces are sufficient for the Phase 1 Section 5 consumption gate. No Section 4 amendment is required before Section 5 lock. Section 5 treats promotion-grade evidence as requiring, at minimum, succeeded Section 4 validation evidence; `backtest.backtest_runs.is_pipeline_validation_only = false`; no zero-cost fallback / pipeline-validation-only evidence; required `backtest.aggregate_metrics` / `backtest.fold_metrics` evidence for the relevant sleeve and horizon; succeeded attribution evidence where attribution is required by the gate; reproducible `data_snapshot_id` / scoring-run / model-version linkage; and no fail-severity Section 4 issue that invalidates the evidence bundle. If implementation later proves Section 4 lacks a required field to verify this bundle, that will trigger a future Section 4 amendment.

### A-OQ-05-16 — Gate terminology reconciliation

Resolved: `consumption` gate means the 03c second promotion gate as framed by the 03c approval note. `paper_to_real_recommendation` gate means the Section 5 paper-evidence recommendation layer. This terminology is approved for Section 5 v1.0.

### A-OQ-05-17 — Kill-switch-driven SELL / TRIM / REPLACE enablement

Resolved: deferred. v1.0 kill switch suppresses new BUY / REPLACE intents and records review / warning / manual-review outcomes; it does not automatically generate SELL, TRIM, or REPLACE actions. Any future enablement of kill-switch-driven risk-reduction actions requires a Section 5 amendment with explicit tests and audit rules.

External carryover: A-OQ-04-07 regime classifier / labeler ownership remains unresolved outside Section 5. Section 5 consumes regime evidence only when available and does not own or resolve the labeler.


## 11. Explicit assumptions

### 11.1 Derived from SDR or EW

| ID | Assumption | Source / rationale |
|---|---|---|
| A-DRV-05-01 | Phase 1 remains paper-only and not live trading. | SDR Decision 1 and Decision 15. |
| A-DRV-05-02 | Section 5 action vocabulary includes BUY, HOLD, TRIM, SELL, REPLACE, WATCH. | SDR Decision 10. |
| A-DRV-05-03 | Initial portfolio concept uses monthly rebalance, weekly risk review, top 5 positions, and equal weight. | SDR Decision 10. |
| A-DRV-05-04 | Portfolio thresholds must be configurable, not hard-coded. | SDR Decision 10. |
| A-DRV-05-05 | Tight fixed stops and fixed take-profit rules are not default Phase 1 behavior. | SDR Decision 10. |
| A-DRV-05-06 | Two promotion gates exist, and Jeremy approval is required. | SDR Decision 12. |
| A-DRV-05-07 | Model states are Active, Warning, Paused, Retired. | SDR Decision 12. |
| A-DRV-05-08 | Broker-neutral order-intent records are in Phase 1 scope, but live broker integration is out of scope. | SDR Decisions 1 and 15. |
| A-DRV-05-09 | Postgres remains system of record for paper portfolio state, order-intent records, approvals, and audit-relevant tables. | SDR Decision 11. |
| A-DRV-05-10 | Tests are required and must verify financial meaning for portfolio rules and order-intent behavior. | EW testing requirements and module DoD. |

### 11.2 Derived from locked prior sections

| ID | Assumption | Source / rationale |
|---|---|---|
| A-LKD-05-01 | Section 5 fills `portfolio/`, `paper/`, and `order_intent/` and owns `config/portfolio.yaml`. | Section 1. |
| A-LKD-05-02 | Section 5 may not call providers directly. | Section 1 / Section 2 provider boundary. |
| A-LKD-05-03 | Section 5 must not write to `ops.data_quality_exceptions`. | Section 2 and prior section issue-log pattern. |
| A-LKD-05-04 | Section 5 reads `models.combined_scores` only through succeeded scoring runs. | Section 3c. |
| A-LKD-05-05 | Section 5 consumes `models.model_versions` state but does not own the 03c model-state schema. | Section 3c. |
| A-LKD-05-06 | Section 5 must not introduce fallback to `secondary_benchmark_id`. | 03a / 03b / 03c constraints. |
| A-LKD-05-07 | Section 4 simulated fills are not paper portfolio state and are not order intent. | Section 4 handoff. |
| A-LKD-05-08 | Section 5 must exclude `is_pipeline_validation_only = true` backtests from serious promotion evidence. | Section 4 v1.0. |
| A-LKD-05-09 | Section 5 may read but not write `backtest.*` and `attribution.*`. | Section 4 handoff. |
| A-LKD-05-10 | Section 5 may record model-state recommendations only in Section-5-owned tables; mechanical model-state transitions require a future 03c amendment. | 03c / Section 4 handoff and Approver disposition A-OQ-05-09. |
| A-LKD-05-11 | `DiversifierHedge` / `absolute_with_context` ETFs produce no `models.combined_scores` rows under 03c's current first-testable formula. | 03c §12.2 and 03c approval note §1.4 item 14. |
| A-LKD-05-12 | Section 5 review cadence must remain independent of Section 4 backtest rebalance cadence. | Section 4 ALC-09 reservation. |
| A-LKD-05-13 | Existing Section 4 v1.0 evidence surfaces are sufficient for the Phase 1 Section 5 consumption gate; future implementation-discovered gaps trigger a Section 4 amendment. | Approver disposition A-OQ-05-15. |

### 11.3 Implementation defaults with no strategy impact

| ID | Assumption | Rationale |
|---|---|---|
| A-IMP-05-01 | Use surrogate primary keys on Section-5-owned tables plus natural uniqueness constraints where needed. | Consistent with prior schema patterns; no strategy impact. |
| A-IMP-05-02 | Use UTC timestamps for run and audit fields. | Consistent operational audit practice. |
| A-IMP-05-03 | Use redacted text / JSON context for issue rows. | Consistent with prior secret-redaction discipline. |
| A-IMP-05-04 | Use `status='running' → 'succeeded'/'failed'` run lifecycle for decision runs. | Mirrors prior sections; no new strategy behavior. |
| A-IMP-05-05 | Store `portfolio_config_hash` and `portfolio_config_version` on decision runs. | Reproducibility support; no strategy impact. |
| A-IMP-05-06 | Store paper-only quantities for paper valuation. | Needed for paper performance; explicitly non-broker. |
| A-IMP-05-07 | Use immutable event rows for paper position changes. | Auditability pattern; no strategy impact. |

### 11.4 Proposed defaults accepted by Approver for Phase 1

| ID | Accepted Phase 1 default | Rationale |
|---|---|---|
| A-PRP-05-01 | Use three schemas: `portfolio.*`, `paper.*`, `order_intent.*`. | Matches Section 1 packages and keeps concerns separated. |
| A-PRP-05-02 | Include position-level, rebalance-cycle-level, and recommendation/order-intent-level paper state in Phase 1. | Makes paper behavior auditable. |
| A-PRP-05-03 | Keep the Section 5 action enum exactly `BUY / HOLD / TRIM / SELL / REPLACE / WATCH`. | Matches SDR Decision 10 without adding new action semantics. |
| A-PRP-05-04 | Do not allow Section 5 to write `models.*`; record Warning / Paused recommendations in Section-5-owned tables only. | Avoids conflict with 03c lifecycle ownership. |
| A-PRP-05-05 | Kill switch may pause new paper BUY / REPLACE intents but does not delete positions or place sell orders automatically. | Conservative paper-only behavior. |
| A-PRP-05-06 | Section 5 consumes transaction-cost assumptions only through Section 4 validation evidence in v1.0. | Avoids duplicate cost logic. |
| A-PRP-05-07 | Paper-to-real recommendation gate requires both calendar observation time and completed rebalance-cycle count. | Prevents overreacting to a small paper sample. |
| A-PRP-05-08 | Order intents are stored even without broker integration. | Provides audit trail of what the system would have recommended. |
| A-PRP-05-09 | Decision run, portfolio decisions, and order intents for one run commit atomically. | Prevents orphaned paper recommendations. |
| A-PRP-05-10 | WATCH records do not alter paper positions. | Keeps watchlist separate from holdings. |
| A-PRP-05-11 | REPLACE records both old ETF and replacement ETF on one portfolio decision, one order intent, and two paper events. | Preserves semantic clarity and auditability. |
| A-PRP-05-12 | Paper portfolio supports one default portfolio initially but allows multiple portfolios structurally. | Low cost and future flexibility. |
| A-PRP-05-13 | Direct account-type execution constraints are deferred in Phase 1. | No executable orders exist. |
| A-PRP-05-14 | ATR-style stop surface is reserved in config, but exact ATR formula remains pending unless a future amendment enables it. | SDR names ATR-based stops but not formula details. |
| A-PRP-05-15 | `portfolio.promotion_evaluations.gate_kind` uses closed enum `('consumption', 'paper_to_real_recommendation')`. | Reconciles SDR Decision 12 language with 03c's approved gate framing. |
| A-PRP-05-16 | ETFs whose sleeve / `rank_method` produces no `models.combined_scores` row under the active 03c formula receive no Section-5 action and produce an explanatory issue row. | Prevents Section 5 from inventing a ranking path for unranked sleeves. |
| A-PRP-05-17 | Existing Section 4 v1.0 evidence surfaces are sufficient for the Phase 1 Section 5 consumption gate. | Avoids unnecessary Section 4 amendment before implementation while preserving future amendment trigger if a real gap appears. |

### 11.5 Open Questions cross-index

| Open Question | v1.0 disposition |
|---|---|
| A-OQ-05-01 | Resolved by A-PRP-05-01. |
| A-OQ-05-02 | Resolved by A-PRP-05-02. |
| A-OQ-05-03 | Resolved by A-PRP-05-01 and A-PRP-05-08. |
| A-OQ-05-04 | Resolved by A-PRP-05-03. |
| A-OQ-05-05 | Resolved through `config/portfolio.yaml`; strategy-affecting threshold changes require Approver review. |
| A-OQ-05-06 | Resolved by §6.10 evidence bundle and A-PRP-05-17. |
| A-OQ-05-07 | Resolved by A-PRP-05-07. |
| A-OQ-05-08 | Resolved by §6.4 and `config/portfolio.yaml` kill-switch settings. |
| A-OQ-05-09 | Resolved: Section 5 recommendations only; no `models.*` writes; future 03c amendment required for mechanical transitions. |
| A-OQ-05-10 | Resolved by A-PRP-05-06. |
| A-OQ-05-11 | Resolved by A-PRP-05-13. |
| A-OQ-05-12 | Resolved by A-PRP-05-08. |
| A-OQ-05-13 | Resolved through `config/portfolio.yaml`. |
| A-OQ-05-14 | Resolved by A-PRP-05-14. |
| A-OQ-05-15 | Resolved by A-PRP-05-17 and §6.10; no Section 4 amendment required before Section 5 lock. |
| A-OQ-05-16 | Resolved by A-PRP-05-15. |
| A-OQ-05-17 | Resolved by deferral; future enablement requires Section 5 amendment per §6.4 and §6.9 SELL note. |

No Section-5 Open Question remains unresolved for the v1.0 candidate disposition set. External A-OQ-04-07 remains unresolved outside Section 5.

---

**End of Section 5 v1.0 LOCKED / APPROVED.**
