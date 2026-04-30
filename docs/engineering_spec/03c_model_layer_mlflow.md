# Engineering Specification — Section 3c: Model Layer and MLflow

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v1.0 LOCKED / APPROVED
**Date:** 2026-04-30
**Builder:** Claude
**Section:** Engineering Specification — Section 3c: Model Layer and MLflow
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Engineering Specification — Section 3a v1.0 LOCKED / APPROVED (`docs/engineering_spec/03a_feature_engineering.md`)
- Engineering Specification — Section 3b v1.0 LOCKED / APPROVED (`docs/engineering_spec/03b_target_generation.md`)
- Section 1 approval note (`docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`)
- Section 2 approval note (`docs/reviews/2026-04-27_spec_02_data_layer_approval.md`)
- Section 2 traceability updates (`docs/reviews/2026-04-27_spec_02_data_layer_traceability_updates.md`)
- Section 3 handoff packet (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`)
- Section 3a approval note (`docs/reviews/2026-04-29_spec_03a_feature_engineering_approval.md`)
- Section 3a traceability updates (`docs/reviews/2026-04-29_spec_03a_feature_engineering_traceability_updates.md`)
- Section 3b approval note (`docs/reviews/2026-04-29_spec_03b_target_generation_approval.md`)
- Section 3b traceability updates (`docs/reviews/2026-04-29_spec_03b_target_generation_traceability_updates.md`)
- `docs/traceability_matrix.md` v0.5 (Sections 1, 2, 3a, 3b v1.0 LOCKED merged)

**Scope statement basis (in lieu of a separate Section 3c handoff packet at the time of v0.1).** Mirroring the pattern Section 3b adopted in v0.2 (Revision 6), no separate Section 3c handoff packet appears under `docs/reviews/` at the time of v0.1 drafting. 03c drafting was authorized to proceed from the following four sources, taken together as the de facto scope statement:

(a) the Approver's drafting prompt of 2026-04-29 (which itself names scope, controlling documents, inherited constraints, items requiring explicit classification, and required tests);
(b) the Section 3a approval note §5.2 *"Open items handed forward to 03c"* (`docs/reviews/2026-04-29_spec_03a_feature_engineering_approval.md`);
(c) the Section 3b approval note §5.1 *"Open items handed forward to 03c"* (`docs/reviews/2026-04-29_spec_03b_target_generation_approval.md`);
(d) the Section 3 handoff packet (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`), to the extent it covers the broader Section 3 split that 03a / 03b / 03c implement.

If a fresh Section 3c handoff packet is later issued, any divergence between this draft and the packet is resolved in favor of the packet via standard EW §3 revision discipline. This scope-basis language is intentionally written so a future 03c approval note can cite it directly.

---

## Changelog

- **v1.0 LOCKED / APPROVED (2026-04-30):** Approver promoted v0.3 to v1.0 LOCKED / APPROVED with **no substantive change** to behavior, schema, tests, scope, or ownership. Locking metadata flipped (status header, end-of-document marker). Final editorial cleanup applied per Approver direction at lock time: (a) current-body references to `v0.1` / `v0.2` that are not historical changelog entries replaced with neutral lock wording such as "current first-testable formula," "current disposition," "current scope," or "this section"; (b) `§5.1` `config/model.yaml` consumer wording aligned with the final lifecycle (unreadable / malformed / pre-run-fatal YAML means no `models.model_runs` row; semantic config failures detected after parse open a `models.model_runs` row, mark it failed, and write `models.model_run_issues`); (c) `§6.3` atomicity contract restated with model-run writes (`models.model_predictions`) and scoring-run writes (`models.combined_scores`) separated as different 03c-owned run types; (d) `§13.5` "03c v0.2 does not perform any of these steps" wording replaced with lock-appropriate language deferring matrix-merge execution to the Approver; (e) `§3` item 7 summary description of the first testable combined-score formula aligned with the controlling `§6.8` standardization semantics — the prior summary phrase "computed cross-sectionally within sleeve at each rebalance signal date" matched only the `peer_relative` semantics of `§6.8` and was inconsistent with `§6.8`'s `benchmark_relative` semantics (pooled across all rank-eligible ETFs at signal date `T`); the summary now states the per-rank-method standardization explicitly and notes that ranking is materialized within sleeve in a separate step. This is an editorial consistency fix only; `§6.8` itself is unchanged. Historical changelog entries for v0.1, v0.2, and v0.3 are preserved verbatim. The Approver exercised final-decision authority per EW §2.1 and approved the section as locked. Companion files: `docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_approval.md`; `docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_traceability_updates.md`. Matrix merge: `docs/traceability_matrix.md` v0.6.

- **v0.3 (2026-04-30):** Targeted cleanup pass per Approver QA feedback (no full rewrite). Nine-revision packet applied surgically to internal consistency defects in v0.2. (1) Config-validation lifecycle made consistent: `§7.3` rewritten so semantic validation runs *after* opening the `models.model_runs` row with `status='running'` (matching `§6.3`); only pre-run YAML parse / encoding / missing-`model_set_version` errors abort to stderr without opening a run row; semantic validation failures now mark the run failed and write `models.model_run_issues`. `§9.4` rewritten in parallel; "Process aborts" wording removed. (2) `config/model.yaml` `model_state` block YAML comments corrected — `initial_state_on_register: Paused`, `approver_only_transitions: true`, and `retired_is_terminal: true` are all flagged as Proposed defaults requiring approval (per §11.5 A-PRP-08, A-PRP-10, A-PRP-09 respectively); the v0.2 stale comment claiming `initial_state_on_register: Paused` was Approver-resolved per SDR Decision 12 is removed (SDR Decision 12 names the four states but does not specify the initial state). (3) `§5.2` outputs list now enumerates all ten `models.*` tables matching `§6.6` and `§3` item 5 — added the missing `models.scoring_run_models` and `models.scoring_run_issues` rows; module-level scoring orchestrator I/O summary updated to include `models.scoring_run_issues`. (4) DiversifierHedge YAML comment in `§7.2` corrected: warning row now routes to `models.scoring_run_issues` (was incorrectly `models.model_run_issues` in v0.2 YAML). (5) Test CS-01 rewritten to use only the closed three-value status enum `('running', 'succeeded', 'failed')` — removed the v0.2 reference to `'pending'` model runs (not in the 03c enum) and replaced the inaccurate "rejected by FK + CHECK constraint" wording with the orchestrator-validation-plus-FK-existence-and-version-integrity wording the Approver requested. (6) Test DC-02 stale "17-value enum" count removed; replaced with "closed enum defined in §6.6" wording; new tests DC-07, DC-08, DC-09 added for `models.scoring_run_issues.issue_type`, `models.scoring_run_issues.severity`, and `models.model_predictions.prediction_context` closed enums. (7) Final stale upstream-status wording in `§5.1` removed: "asserting the run is non-blocked" replaced with `status='succeeded'` filter language explicitly citing the 03a closed three-value enum. (8) Eight remaining current-body references to "v0.1 first-testable formula" replaced with "current first-testable formula" — historical changelog wording in v0.2 entry preserved. (9) `.env` wording in `§7.1` cleaned — 03c directly reads only `MLFLOW_TRACKING_URI`; application DB access inherits from Section 2; no `POSTGRES_*` or provider-credential variables introduced by 03c (the v0.2 wording incorrectly suggested 03c reads them). (10) v0.2 strengths preserved: locked Section 2 sleeve names; 03b θ = 0.0; DiversifierHedge → `absolute_with_context` with no `combined_scores` rows under the current formula; `prediction_context` closed enum; Section 4 does not own `models.*` writes; `models.scoring_run_issues` for scoring-run-level issues; 03c writes only to `models.*` and MLflow; no writes to `ops.*`/`features.*`/`targets.*`/`universe.*`/`prices.*`; MLflow runs link to both `feature_run_id` and `target_run_id`; no `secondary_benchmark_id` fallback.

- **v0.2 (2026-04-30):** Targeted revision pass per Approver QA feedback (no full rewrite). Fifteen-revision packet applied surgically. (1) Sleeve names corrected to the locked Section 2 closed enumeration `{BroadEquity, Sector, Thematic, BondTreasury, DiversifierHedge, REITRealAsset}`; the v0.1 invented names `{CoreEquityBeta, TacticalEquityTilt, StyleFactor, YieldCarry, Cash}` are removed. (2) Removed the v0.1 fabricated assumption A-SDR-02 claiming `outperformance_threshold_bps_per_year=100`; 03c consumes 03b's locked classification threshold `θ = 0.0` (strict positive excess return) without modification. (3) DiversifierHedge mapped to `absolute_with_context` per SDR Decision 5; explicit acknowledgement that the v0.1 first-testable two-component formula does not rank `absolute_with_context` ETFs, so DiversifierHedge produces no `models.combined_scores` rows under current 03c scope unless and until an Approver-approved amendment adds the absolute / risk inputs; recorded as Open Question / Proposed Default, not silently resolved. (4) Run-status enum normalized to `('running', 'succeeded', 'failed')` matching 03a/03b LOCKED schemas; references to `status='blocked'` and `status='pending'` removed from all upstream-status discussion (replaced with `status != 'succeeded'`). (5) Open-run-before-validation lifecycle in §6.3 reconfirmed parallel to 03a/03b; pre-run fatal YAML parse errors isolated to stderr only, never mixed with `models.model_run_issues`. (6) Issue-type enumeration reconciled: every `issue_type` value referenced in §6.3, §6.6, §8, §9, §10, §11 is now in the canonical §6.6 closed enumeration; v0.1 strays (`upstream_run_not_succeeded`, `snapshot_chain_broken`, `insufficient_training_rows`, `all_null_target`, `all_null_feature`, `single_class_training_set`, `calibration_fold_degenerate`, `shape_mismatch`, `mlflow_logging_partial`, `cross_model_snapshot_mismatch`, `degenerate_cross_section`, `rank_method_unsupported_in_phase1_v1`) are renamed or routed to the new `models.scoring_run_issues` table. (7) §6.2 prediction-emission contract revised with explicit `prediction_context` enum (`in_sample_diagnostic`, `walk_forward_oos`, `current_scoring`); Section 4 may consume only out-of-sample predictions per Section 4 fold approval; 03c owns the storage field, Section 4 owns fold construction and OOS-consumption validation. (8) Section 4 ownership corrected: Section 4 does not write to `models.model_runs` or `models.model_predictions`; Section 4 invokes 03c-owned model-run contracts through approved seams; 03c owns the writer side. (9) `models.model_versions` schema contradiction fixed: removed the v0.1 `model_definition_id` reference in §9.6 edge case; the partial unique active-version index is on `(model_kind) WHERE state='Active'` using columns the schema actually defines. (10) Scoring-run issue ownership resolved: new separate `models.scoring_run_issues` table parallel to `models.model_run_issues`; updates propagated to §6.6, §8, §9, §11. (11) Schema inventory corrected to nine tables (the v0.1 "eight tables" wording miscounted; `models.scoring_run_models` was always in scope). With Revision 10 adding `models.scoring_run_issues`, the total is ten tables; references updated. (12) Model-state defaults reclassified: only "the four states `Active`/`Warning`/`Paused`/`Retired` exist" is Approver-resolved by SDR Decision 12; initial-state-Paused, Retired-is-terminal, and Approver-only-Phase-1 transitions are Proposed defaults requiring approval. (13) Section 5 / Section 6 handoffs corrected: paper portfolio state, portfolio rules, and order intent belong to Section 5; UI belongs to Section 6; §12.2 / §12.3 / §12.4 and `§8.4` deferred-test labels updated. (14) Traceability sketch language softened: "Implementation complete in 03c" replaced with "Proposed 03c contribution at lock" / "Status after 03c lock, if approved" / "Pending until 03c approval and matrix merge". (15) v0.1 strengths preserved per Approver direction: 03c writes only to `models.*` and MLflow; no writes to `ops.*`; MLflow runs link to both `feature_run_id` and `target_run_id`; `feature_runs.status='succeeded'` and `targets.target_runs.status='succeeded'` filters intact; T-1 not redefined; Convention B not redefined; no `secondary_benchmark_id` fallback; `config/model.yaml` exclusively 03c-owned; baseline model forms, calibration method, combined-score formula, `rank_method` semantics, model-state lifecycle, and `config/model.yaml` structure remain explicitly classified under EW §3.3.

- **v0.1 (2026-04-29):** Initial draft. Eleven EW §3.2 template fields populated in order. Every assumption classified per EW §3.3. SDR Decisions 1, 2, 5, 6, 7, 11, 12, 16 cited as directly implemented or respected. Open Questions and Proposed defaults visibly enumerated in §10 and §11.

---

## 1. Purpose

Section 3c establishes the **model layer** for the Phase 1 ETF tactical research platform: training-data assembly from the Section 3a feature surface and the Section 3b target surface, baseline model implementations under SDR Decision 6's dual-target framework, the calibration pipeline under SDR Decision 7, the MLflow client-side (writer-side) integration under SDR Decision 11, the `models.*` Postgres schema, the `config/model.yaml` file, the closed enumeration and per-sleeve semantics for the `rank_method` field on `universe.etfs` (closing the Section 2 `pending_section_3` sentinel obligation), the first testable combined-score formula under SDR Decision 6, and the model-state lifecycle fields on registered model versions under SDR Decision 12 (Active / Warning / Paused / Retired).

This section is the model-layer cash-out of:
- **SDR Decision 6's** dual-target framework — the regression-and-classification pair already cashed out in Section 3b becomes a *fitted* pair plus a calibrated probability output, which together feed the first testable combined-score formula;
- **SDR Decision 7's** calibration requirement — calibrated probabilities are produced before any threshold is treated as meaningful;
- **SDR Decision 11's** lightweight MLOps architecture — every model run is recorded as one MLflow run, with metadata fields aligned to the EW §7 reproducibility list and tags linking back to the upstream `feature_run_id` and `target_run_id`;
- **SDR Decision 12's** model-state model — registered model versions carry an Active/Warning/Paused/Retired state field that downstream Sections 4 and 5 consume for promotion-gate evaluation;
- **SDR Decision 5's** sleeve / benchmark structure — `rank_method` allowed values and per-sleeve semantics are defined here; no module ranks ETFs against a sleeve they are not eligible for, and no module silently substitutes the secondary benchmark.

Section 3c does **not** define feature formulas (03a), target formulas (03b), the walk-forward harness (Section 4), purge/embargo enforcement (Section 4), transaction costs (Section 4), attribution (Section 4), the regime reporting layer (Section 4), portfolio rules (Section 5), paper portfolio state (Section 5), broker-neutral order intents (Section 5), the UI (Section 6), or live trading (out of Phase 1 entirely). Forward references to those owners are used where the reader needs to know which section closes what.

---

## 2. Relevant SDR decisions

Section 3c directly implements:

- **SDR Decision 1** — Phase 1 scope and boundaries. 03c reads ETF features and targets only; introduces no fundamentals, holdings, news, earnings, options, individual stocks, autonomous research agents, or commercial features into any model, calibration, or combined-score formula. No live broker dependency or broker SDK reference appears anywhere in `models/`.
- **SDR Decision 2** — Data Provider and Provider-Switching Strategy. No `models/` module imports from `quant_research_platform.providers` or from any provider-specific library; all model inputs flow through Postgres.
- **SDR Decision 5** — Benchmark, Sleeve, and Diversifier Treatment. 03c defines the **closed enumeration of allowed `rank_method` values** and the **per-sleeve semantics** for each. The Section 2 `pending_section_3` sentinel obligation in `config/universe.yaml` is closed by 03c. No module under `models/` introduces a fallback to `secondary_benchmark_id`; the no-silent-benchmark-substitution rule established in 03a §10.1 / §11.6 #6 and 03b §11.6 #6 is preserved at the model layer.
- **SDR Decision 6** — Target Design and Ranking Objective. 03c fits the dual-target pair (regression excess return + classification outperformance) at the 63 and 126 trading-day horizons 03b cashed out, and produces the **first testable combined-score formula**. The combined-score formula does not hard-code into the SDR; 03c proposes a formula at the spec level and exposes its weights in `config/model.yaml` for explicit Approver-controlled tuning.
- **SDR Decision 7** — Validation, Calibration, and Backtest Confidence Level. 03c implements the **calibration pipeline** that turns raw classification probabilities into calibrated probabilities. The calibration *method* (Platt, isotonic, logistic-on-folds) is a Proposed default requiring Approver approval. The walk-forward harness, purge/embargo enforcement, and the actual fold construction belong to Section 4; 03c integrates with whatever fold structure Section 4 provides via a thin contract.
- **SDR Decision 11** — Model Tracking, Attribution, Data Quality, and Lightweight MLOps. 03c is the **MLflow writer-side integration** for Phase 1. Every successful model training run produces one MLflow run; every MLflow run records the EW §7 reproducibility metadata and links back to `features.feature_runs.feature_run_id`, `targets.target_runs.target_run_id`, and (transitively) `ops.data_snapshots.data_snapshot_id`. The attribution-storage side of Decision 11 belongs to Section 4 and is not implemented by 03c.
- **SDR Decision 12** — Model Promotion, Warning, Pause, and Retirement Rules. 03c defines the **schema fields** that record a registered model version's state (Active / Warning / Paused / Retired) and the **state-transition audit log**. The **gate evaluation logic** (when a model moves from Active to Warning, when paper-tracking results are sufficient to graduate to influence-on-real-decisions, etc.) is a downstream concern: the first promotion gate (Research → Internal paper tracking) is owned by 03c at the write side (a registered version's state can only transition to `Active` upon Approver approval), and the second gate (Paper tracking → influence on real decisions) is owned by Section 5 and the broader portfolio review process. 03c does **not** implement automated state transitions.
- **SDR Decision 16** — Phase 1 Success Criteria and Bias Controls. 03c contributes at the model level: (a) reproducibility via the `data_snapshot_id` / `feature_run_id` / `target_run_id` linkage chain and the EW §7 metadata recorded on every MLflow run; (b) idempotency of model runs given the same inputs and seed; (c) absence of look-ahead bias in training-data assembly via the Section 3a T-1 contract and the Section 3b Convention B contract, neither of which 03c redefines; (d) absence of provider leakage via the no-provider-import rule; (e) calibration of probability outputs before any threshold is interpretable.

Section 3c also reads (without modifying) decisions implemented by other locked sections:

- **SDR Decision 3 / 4** — universe / eligibility / lifecycle. 03c respects the eligibility-row omission contract on the read side: rows absent from `features.feature_values` or `targets.target_values` are not training rows and are not re-derived. ETFs not rank-eligible at signal date `T` per `universe.etf_eligibility_history` do not appear in combined scores at `T`.
- **SDR Decision 9** — regime taxonomy. 03c does not own the regime reporting layer (Section 4) and does not own the regime classifier (deferred). The regime-side feature primitive (`regime_spy_above_sma_200`, default off in `config/features.yaml`) may be consumed as a feature input if activated; it is not given special treatment by 03c.
- **SDR Decision 13** — LLM advisory use. Process commitment governed by the EW; no architectural footprint in 03c.
- **SDR Decision 14** — Danelfin deferred. Not introduced by 03c.
- **SDR Decision 15** — broker-neutral, no live-trading, no broker SDK in dependency manifests. Backstopped at the model layer by the no-broker-import / no-broker-SDK static checks Section 1 invariant 2 establishes.
- **SDR Decision 17** — UI is read-only. Section 6 reads `models.*` and MLflow run metadata read-only; 03c neither relies on UI behavior nor permits UI writes.

---

## 3. In scope

Section 3c covers:

1. **Training-data assembly contract.** The canonical join discipline for assembling training rows from Section 3a feature outputs and Section 3b target outputs:
   - `features.feature_values` filtered through `features.feature_runs.status='succeeded'`;
   - `targets.target_values` filtered through `targets.target_runs.status='succeeded'`;
   - inner join on `(etf_id, as_of_date)` with both filters applied;
   - explicit handling of front-edge horizon truncation (rows present in `features.feature_values` but absent in `targets.target_values` are not training-eligible because the target side is missing — they are absent from the training set, not silently treated as `NULL` labels);
   - explicit handling of Bucket 2 NULL targets (rows present in `targets.target_values` with `target_value IS NULL` are not training-eligible either; they are filtered out from training and their absence is recorded in run metadata);
   - explicit feature-side missing-value handling (rows with one or more `feature_value IS NULL` in the requested feature set are not training-eligible at Phase 1; they are filtered out, and their absence is recorded).
2. **Baseline model implementations** under SDR Decision 6's dual-target framework, with the specific algorithmic choices classified as Proposed defaults requiring Approver approval (see §6.4 and §11.6).
3. **Calibration pipeline** under SDR Decision 7. Calibration produces a calibrated probability output for the classification family; the calibration method is a Proposed default requiring Approver approval (see §6.5 and §11.6).
4. **MLflow writer-side integration** per SDR Decision 11. Per Approver direction, MLflow is the experiment tracker; Postgres remains system of record. Each model training run produces one MLflow run; the MLflow run records training/validation metrics, hyperparameters, calibration parameters, fitted-model artifacts (binary), feature/target schema snapshots, and the EW §7 reproducibility metadata. **Linkage back to `feature_run_id` and `target_run_id`** is recorded both as MLflow tags and as Postgres FKs on `models.model_runs`.
5. **`models.*` Postgres schema at the spec level**, comprising ten tables (see §6.6). Migration filenames are an Implementation default with no strategy impact (see §11.5).
6. **Closed enumeration of allowed `rank_method` values** and per-sleeve semantics for each, replacing the Section 2 `pending_section_3` sentinel in `config/universe.yaml`. The closed enumeration and the proposed per-sleeve mapping are Proposed defaults requiring Approver approval (see §6.7 and §11.6).
7. **First testable combined-score formula** under SDR Decision 6. Phase 1 03c proposes a **2-component combined score** (expected excess return from the regression baseline + calibrated probability of outperformance from the classification baseline). The first testable combined score is computed per `(etf, signal_date, horizon)` using component z-scores over the rank-method-defined ranking cross-section: pooled across all rank-eligible ETFs for `benchmark_relative`, within sleeve for `peer_relative`, and not enabled for `absolute_with_context` under the current formula. Ranking is then materialized within sleeve. The formula is classified as Proposed default requiring Approver approval. Hooks for the 4-component variant (adding a risk score and a trend/relative-strength confirmation per Decision 6) are reserved in `config/model.yaml` but are not enabled in current 03c scope.
8. **Combined-score-and-rank materialization** in `models.combined_scores` keyed on `(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)` with score components retained as JSONB for transparency.
9. **Sleeve-aware ranking semantics** — proposing that combined score is computed *first* per `(etf, signal_date, horizon)` and then ranked *second* within sleeve at each rebalance signal date, with an ETF eligible across multiple sleeves ranked once *per sleeve* (i.e., it appears in each sleeve's ranking with the same combined score). Both choices are Proposed defaults requiring Approver approval (see §6.7 and §11.6); the alternative resolutions are flagged in §10 as Open Questions.
10. **Model state lifecycle fields and audit** per SDR Decision 12. Schema fields for Active / Warning / Paused / Retired; an audit table (`models.model_state_history`) recording every state transition; the rule that state transitions are Approver-only in Phase 1 (no automated transitions). The semantics of when each state should be entered are partly Open Questions for the Approver (see §10) and partly handed forward to Section 5 (the second promotion gate).
11. **`config/model.yaml`** ownership. 03c owns this strategy-affecting config file. May read `config/features.yaml` and `config/targets.yaml` metadata but does not own them.
12. **`models.model_run_issues`** — model-layer issue log inside the `models` schema, parallel to 03a's `features.feature_run_issues` and 03b's `targets.target_run_issues`, with a closed `issue_type` enumeration disjoint from the upstream sections' enumerations.

## 4. Out of scope

Section 3c does **not** cover:

1. **Feature formulas.** 03a owns. 03c reads `features.feature_values` and `features.feature_definitions` only.
2. **Target formulas.** 03b owns. 03c reads `targets.target_values` and `targets.target_definitions` only.
3. **`config/features.yaml`** ownership. 03a owns. 03c may read for metadata (e.g., active `feature_set_version`, family enumeration) but does not modify.
4. **`config/targets.yaml`** ownership. 03b owns. 03c may read for metadata (e.g., active `target_set_version`, horizon enumeration, `alignment.convention`) but does not modify.
5. **Walk-forward harness construction**, **fold layout**, **purge/embargo enforcement**, **transaction-cost application**, and **leakage tests across folds**. Section 4 owns. 03c integrates with whatever fold contract Section 4 supplies but does not construct folds.
6. **Attribution storage and reporting.** Section 4 owns. 03c records training/validation metrics on the MLflow run for the model itself; per-trade and per-signal attribution at the backtest level is Section 4's.
7. **Regime classification computation** beyond reading the (default-off) regime feature primitive. Sections 3 (computation, beyond 03a's primitive) and 4 (consumption / reporting layer) own.
8. **Portfolio rules engine.** Section 5 owns. 03c emits combined scores and ranks; the BUY/HOLD/TRIM/SELL/REPLACE/WATCH transitions and the second promotion gate (paper-tracking → influence-on-real-decisions) are Section 5's.
9. **Paper portfolio state.** Section 5 owns.
10. **Broker-neutral order intents.** Section 5 owns. 03c emits no order intents and depends on no broker SDK.
11. **UI.** Section 6 owns. UI reads `models.*` and MLflow read-only.
12. **Live trading and any code path that could enable it.** Out of Phase 1 entirely per SDR Decision 1, 15, 18 and the Section 1 invariants.
13. **Automated promotion / pause / retirement transitions.** Per SDR Decision 12 and the EW Approval Matrix, model promotion and state changes are Approver-gated. 03c records the schema fields and the audit log; the transition logic is manual / Approver-driven in Phase 1.
14. **A new auto-resolution class on `ops.data_quality_exceptions`.** Per Section 2 v1.0 LOCKED, the framework is ingestion-owned and 03c does not write to `ops.data_quality_exceptions` or any `ops.*` table. Model-layer issues land in the new `models.model_run_issues` table inside the `models` schema (parallel to 03a and 03b).
15. **A change to `features.feature_run_issues` or `targets.target_run_issues` enumerations.** Per the Approver's drafting prompt and per 03a / 03b approval-note §4 conditions, 03c does not modify either upstream enumeration.
16. **A Section 1 amendment** for the introduction of the `models.*` schema, the `models/` package internals, or `config/model.yaml`. 03c is approved within its own spec approval path, mirroring the pattern Section 3b adopted for `config/targets.yaml`. The Section 1 *Config dependencies* table already enumerates `config/model.yaml`; 03c populates the file's structure.
17. **A Section 2 amendment** for benchmark price storage that would close the index-only-benchmark structural gap (03a §10.1, 03b §10.1). The interim behavior (no silent substitution, no fallback to secondary benchmark, regression target row written with `target_value = NULL`, `target_run_issues` warning row) is inherited; 03c does not propose the structural amendment.
18. **A change to the Section 3a / Section 3b null-vs-no-row taxonomies.** Inherited verbatim. 03c reads features and targets through these taxonomies and does not reinterpret them.


---

## 5. Inputs and outputs

### 5.1 Inputs

03c reads from the following Postgres tables and config files. **All reads are filtered on the appropriate `status='succeeded'` filter where applicable.**

**From Section 2 (read-only):**

- `universe.etfs` — ETF identity, sleeve, primary benchmark, lifecycle bounds (`first_traded_date`, `delisted_date`, `replacement_etf_id`), `equity_rotation_eligible`, `diversifier_sleeve_eligible`, `cost_bucket`, `rank_method`. **`rank_method` is read with the closed enumeration 03c defines (§6.7); any value outside the enumeration raises a structured error at orchestrator startup.**
- `universe.sleeves` — sleeve catalog (six SDR Decision 5 sleeves).
- `universe.benchmarks` — benchmark catalog (`etf_id` for ETF-backed benchmarks; `index_symbol` for index-only).
- `universe.etf_eligibility_history` — for as-of-date eligibility queries via the Section 2 SQL view (used to filter combined-score / ranking outputs to rank-eligible ETFs at the relevant signal date).
- `prices.etf_prices_daily` — **read access path is restricted in 03c**. The fitted models do not read prices directly; prices are reached only through the feature surface 03a produces. The one exception is the optional regime-feature primitive `regime_spy_above_sma_200` which 03a (not 03c) computes from SPY prices. 03c-side static checks (§8.2) enforce that no module under `models/` reads from `prices.*`.
- `ops.data_snapshots` — the snapshot anchor for reproducibility. Read at orchestrator startup to validate `status='active'` and to retrieve `price_table_max_as_of_date`, `provider_name`, `provider_dataset_label`, `universe_config_hash`, `universe_version_label`, and `adjusted_price_convention` for inclusion in MLflow tags.
- `ops.ingestion_runs` — **not directly consulted by 03c** in current scope. 03a and 03b already validate the `data_snapshot_id` against ingestion-run dependencies before producing `feature_run_id` / `target_run_id`. 03c relies on the upstream blocking discipline: a feature run or target run will not have `status='succeeded'` if its ingestion-run dependencies failed, so 03c's `status='succeeded'` filter is sufficient.

**From Section 3a (read-only):**

- `features.feature_values` — ETF feature values; **filter through `features.feature_runs.status='succeeded'`** (constraint inherited from 03a §6.5 atomicity contract and 03a approval note §4 condition #4).
- `features.feature_runs` — for the status filter (every read enforces `status='succeeded'`), for retrieving `data_snapshot_id`, `feature_set_version`, `commit_hash`, `config_hash` (recorded as MLflow tags). The 03a closed status enum is `('running', 'succeeded', 'failed')`; 03c consumes only the succeeded subset.
- `features.feature_definitions` — for retrieving the feature catalog (`feature_name`, `family`, `parameters`) corresponding to the active `feature_set_version`.
- `features.feature_run_issues` — read-only for 03c's optional annotation of model runs in MLflow tags or `models.model_run_issues` (e.g., propagating an `index_only_benchmark` warning). 03c does **not** write to `features.feature_run_issues`.

**From Section 3b (read-only):**

- `targets.target_values` — ETF target values; **filter through `targets.target_runs.status='succeeded'`** (constraint inherited from 03b §6.5 atomicity contract and 03b approval note §4 condition #4).
- `targets.target_runs` — for the status filter and for retrieving `data_snapshot_id`, `target_set_version`, `commit_hash`, `config_hash`.
- `targets.target_definitions` — for the active target catalog (`target_name`, `family`, `horizon_trading_days`, `entry_offset_trading_days`, `exit_offset_trading_days`, `parameters`).
- `targets.target_run_issues` — read-only for 03c's optional annotation. 03c does **not** write to `targets.target_run_issues`.

**Reproducibility constraint (Approver-bound):** 03c respects the `data_snapshot_id` chain by reading it through the linked `feature_run_id` and `target_run_id`, asserting at orchestrator startup that the two IDs reference the same `data_snapshot_id` (a mismatch is a fail-severity model-run issue and a run-level abort). 03c does **not** carry an independent `data_snapshot_id` reference; the chain is single-sourced through 03a and 03b.

**From config:**

- `config/model.yaml` — owned by 03c. **Two-phase consumption per the §6.3 / §7.3 lifecycle:** if the file is unreadable, malformed, or missing required top-level keys the orchestrator needs to construct a run context (minimally `model_set_version` and the `mlflow` block), this is a **pre-run fatal parse error**: the orchestrator does **not** open a `models.model_runs` row, logs to stderr only, and writes no `models.model_run_issues` row. Once the file is parseable enough to identify `model_set_version`, the orchestrator opens a `models.model_runs` row with `status='running'` and runs semantic validation (§7.3); any semantic failure marks the run `status='failed'`, populates `error_message` and `completed_at_utc`, and writes a `severity='fail'` `models.model_run_issues` row with the appropriate canonical `issue_type` per §6.6.
- `config/features.yaml` — read-only metadata. 03c reads `feature_set_version` and the active family / parameter table to enumerate which features are available to the model. 03c does not interpret feature semantics beyond what `features.feature_definitions` already records.
- `config/targets.yaml` — read-only metadata. 03c reads `target_set_version`, the active family / horizon table, and the `alignment.convention` field. 03c does not interpret target semantics beyond what `targets.target_definitions` already records and does not redefine `entry_date` / `exit_date`.
- `config/universe.yaml` — read-only metadata. 03c reads each ETF's `rank_method` value and validates it against the closed enumeration 03c defines (§6.7). The Section 2 sentinel `pending_section_3` is rejected at orchestrator startup once 03c's enumeration is approved; before approval, 03c is not authorized to start ranking runs.

**From `.env`:**

- `MLFLOW_TRACKING_URI` (already declared by Section 2). 03c writes to MLflow via this URI.
- No new environment variables introduced by 03c.

### 5.2 Outputs

03c writes to the following Postgres tables and the MLflow tracking server. **03c writes only to `models.*` and to MLflow.** Specifically: 03c does **not** write to `universe.*`, `prices.*`, `features.*`, `targets.*`, `ops.*` (per the no-write-to-`ops.*` discipline inherited from 03a and 03b), or any provider table.

**To `models.*` (owned by 03c; see §6.6 for the schema):**

- `models.model_definitions` — closed catalog of `model_kind` values per active `model_set_version`.
- `models.model_runs` — every model training+prediction run (one row per (model_kind, training+prediction execution)). Carries FKs to `features.feature_runs(feature_run_id, feature_set_version)` and `targets.target_runs(target_run_id, target_set_version)`, plus FK to `ops.data_snapshots(data_snapshot_id)` redundantly for query convenience.
- `models.model_predictions` — per-`(etf_id, as_of_date, model_kind, model_run_id)` model outputs (predicted excess return, predicted raw probability, calibrated probability, `prediction_context`).
- `models.model_run_issues` — model-run-layer issue log; closed `issue_type` enumeration; closed `severity` enumeration. Parallel to `features.feature_run_issues` and `targets.target_run_issues`, with the same lifecycle integration discipline.
- `models.scoring_runs` — every combined-score / ranking run (one row per (set-of-model-runs-consumed, signal-date-window, scoring execution)). Records the FKs to consumed model runs and the scoring formula version.
- `models.scoring_run_models` — junction table linking a `scoring_run_id` to the `model_run_id` rows it consumes, with a closed `role` enum (regression-h63, regression-h126, classification-h63, classification-h126).
- `models.combined_scores` — per-`(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)` combined score, rank within sleeve, and score components (JSONB).
- `models.scoring_run_issues` — scoring-run-layer issue log; disjoint closed `issue_type` enumeration from `models.model_run_issues`; FK'd to `models.scoring_runs(scoring_run_id)`. Per §6.6.
- `models.model_versions` — registered model versions. Each row links to a `model_run_id` and carries the lifecycle `state` field (Active / Warning / Paused / Retired) plus registration / approval audit fields.
- `models.model_state_history` — append-only audit of every state transition on `models.model_versions`.

(Total: ten tables, matching §6.6 and §3 item 5.)

**To MLflow (writer-side):**

- One MLflow run per `models.model_runs` row (1:1 mapping). The MLflow run's tags, params, metrics, and artifacts include the EW §7 reproducibility metadata, the upstream `feature_run_id` and `target_run_id`, the active `feature_set_version` and `target_set_version`, the `model_kind`, the calibration method (when applicable), the fitted-model binary (e.g., `joblib` pickle or equivalent — Implementation default), and the feature/target schema snapshots used at fit time.
- One MLflow registered model + version per `models.model_versions` row (1:1 mapping). The registered model URI is recorded on `models.model_versions.mlflow_model_uri` for downstream lookup.
- **MLflow metadata is in Postgres** (per Section 2 — separate `mlflow` database in the same Postgres cluster). **MLflow artifacts are in the `mlflow-artifacts` Docker named volume** (per Section 1 / Section 2).

**Module-level input/output summary:**

- **`models/` orchestrator** (the entry point for a model training+prediction run): config + active feature/target metadata + selected `feature_run_id` / `target_run_id` → `models.model_runs` row + `models.model_predictions` rows + an MLflow run + (on failure) `models.model_run_issues` rows.
- **`models/` baseline regression module**: assembled training rows + hyperparameters → fitted regression model + per-row predicted excess return.
- **`models/` baseline classification module**: assembled training rows + hyperparameters → fitted classification model + per-row predicted raw probability + calibrated probability.
- **`models/` calibration module**: held-out fold structure + raw probabilities + observed labels → calibrated probabilities for both held-out and prediction-time rows.
- **`models/` scoring module**: per-`(etf, as_of_date, horizon)` predicted excess return + calibrated probability → combined score → per-sleeve rank → `models.scoring_runs` row + `models.scoring_run_models` rows + `models.combined_scores` rows + (on warning or failure) `models.scoring_run_issues` rows + an MLflow run (if the scoring run is treated as an MLflow run) or as artifacts on the parent model runs (Implementation default; see §11.5).


---

## 6. Data contracts

### 6.1 Training-data assembly contract

The canonical SQL for a Phase 1 training run, given a selected `feature_run_id = F` (status `'succeeded'`) and a selected `target_run_id = T` (status `'succeeded'`) referencing the same `data_snapshot_id`:

```sql
WITH succeeded_features AS (
  SELECT fv.etf_id, fv.as_of_date, fv.feature_name, fv.feature_value,
         fv.feature_set_version, fv.feature_run_id
  FROM features.feature_values fv
  INNER JOIN features.feature_runs fr
    ON fv.feature_run_id = fr.feature_run_id
   AND fv.feature_set_version = fr.feature_set_version
  WHERE fr.feature_run_id = :selected_feature_run_id
    AND fr.status = 'succeeded'
),
succeeded_targets AS (
  SELECT tv.etf_id, tv.as_of_date, tv.target_name, tv.target_value,
         tv.horizon_trading_days, tv.entry_date, tv.exit_date,
         tv.target_set_version, tv.target_run_id
  FROM targets.target_values tv
  INNER JOIN targets.target_runs tr
    ON tv.target_run_id = tr.target_run_id
   AND tv.target_set_version = tr.target_set_version
  WHERE tr.target_run_id = :selected_target_run_id
    AND tr.status = 'succeeded'
)
SELECT f.etf_id, f.as_of_date,
       /* feature columns reshaped wide for fitting */
       /* target columns reshaped wide for fitting per horizon */
       f.feature_set_version, t.target_set_version,
       f.feature_run_id, t.target_run_id
FROM succeeded_features f
INNER JOIN succeeded_targets t
  ON f.etf_id = t.etf_id
 AND f.as_of_date = t.as_of_date;
```

**Contract semantics:**

- The **inner join on `(etf_id, as_of_date)`** is the canonical pattern; it naturally excludes:
  - rows present in features but absent in targets (front-edge horizon truncation per 03b §6.5 Bucket 1; 03b's coverage-parity guarantee per 03b §6.9 ensures these are the only "in features but not in targets" rows for the same snapshot);
  - rows present in targets but absent in features (theoretically impossible under coverage parity, but the join discipline is robust).
- **Front-edge horizon truncation produces missing training labels, not failed model runs.** The training set is simply smaller at the front edge by approximately `max(horizon)` trading days. The model run completes `'succeeded'` provided enough training rows remain (see §6.4 minimum-training-rows threshold and §9 edge cases).
- **Bucket 2 NULL targets are filtered from training.** A row with `target_value IS NULL` (per 03b §6.5 Bucket 2: missing forward bar inside an otherwise coverable window, non-overlapping benchmark forward history, index-only-benchmark, or null-propagated classification) is **not training-eligible**. It is dropped from the training set; its absence is recorded in `models.model_runs.training_dataset_summary` (a JSONB field) for auditability. A high count of dropped Bucket 2 rows may produce a `severity='warning'` row in `models.model_run_issues` with `issue_type='high_null_target_rate'` (Proposed default; see §6.6 and §11.6).
- **Feature-side NULL handling for training is filter-out.** A row with any required feature `feature_value IS NULL` for the active feature set is not training-eligible. Phase 1 03c does not impute. The dropped count is recorded; alternative handling (mean imputation, zero imputation, indicator features) is a Proposed default explicitly classified in §11.6 / §10.
- **Both runs must reference the same `data_snapshot_id`.** Asserted at orchestrator startup; mismatch produces `severity='fail'` model-run issue with `issue_type='snapshot_mismatch'` and aborts the run before fitting.
- **Both runs must be `status='succeeded'`** at orchestrator startup. Asserted explicitly; either run in `status='running'`, `'failed'`, or with no row at all aborts the model run.

### 6.2 Prediction emission contract (separate from training)

Every emitted prediction row in `models.model_predictions` carries an explicit **prediction_context** field that records the operational regime in which the prediction was produced. The Phase 1 closed enumeration is:

| `prediction_context` | Meaning | Permissible downstream consumption |
|---|---|---|
| `'in_sample_diagnostic'` | Prediction produced over rows used (in whole or in part) to fit the model. Useful for diagnostic checks (residual analysis, training-set sanity), **not** for backtest performance evaluation. | UI / diagnostics only. **Section 4 backtest harness MUST NOT consume `in_sample_diagnostic` rows for performance evaluation**; doing so would constitute look-ahead leakage. |
| `'walk_forward_oos'` | Prediction produced over rows that were strictly out-of-sample relative to the model's training fold per Section 4's purge / embargo / fold-boundary rules. The fold structure is owned by Section 4; 03c records the `prediction_context` value supplied by Section 4 (or by Section-4-equivalent fixture machinery during testing) but does not itself construct folds. | Section 4 backtest performance evaluation. Section 5 portfolio simulation when reading historical predictions. |
| `'current_scoring'` | Prediction at the most recent signal date `T_now` for which feature rows exist but target rows for `horizon = h` cannot exist (i.e., `T_now > price_table_max_as_of_date - h`). These are the most actionable predictions for the next paper rebalance. | Section 5 portfolio rules at `T_now`. UI display. **Not** consumable by Section 4 for backtest-period performance evaluation (no realized label exists yet). |

**Ownership boundary.** 03c owns the `prediction_context` column on `models.model_predictions` and the writer-side rule that every emitted row must carry exactly one of the three closed values. **03c does not own fold construction, purge / embargo width selection, or the rule for which rows qualify as `walk_forward_oos`.** Those are Section 4's. When Section 4 invokes the 03c-owned model-run contract through an approved seam (see §12.1), Section 4 is responsible for tagging each emitted row with the correct `prediction_context`. Outside a Section 4 invocation, the orchestrator emits `'current_scoring'` for rows at `T_now`-side dates and `'in_sample_diagnostic'` for rows at training-window dates; it never emits `'walk_forward_oos'` without Section 4 fold metadata.

**Emission rule.** For every rank-eligible `(etf, as_of_date)` row in the succeeded feature run, the orchestrator emits one `models.model_predictions` row per fitted `model_kind` with the appropriate `prediction_context`. Predictions are **not** withheld merely because the matching target row is absent (front-edge truncation per 03b §6.5 Bucket 1) — the absence-of-target ≠ absence-of-prediction principle applies, with the contextual safety supplied by `prediction_context` rather than by row suppression.

The canonical prediction-emission SQL (with the model already fitted via §6.1):

```sql
SELECT f.etf_id, f.as_of_date, f.feature_value /* reshaped wide */
FROM features.feature_values f
INNER JOIN features.feature_runs fr
  ON f.feature_run_id = fr.feature_run_id
WHERE fr.feature_run_id = :selected_feature_run_id
  AND fr.status = 'succeeded';
```

**Predictions are emitted for the entire `(etf_id, as_of_date)` set in the succeeded feature run, with `prediction_context` tagged per the rules above.** Rows with `feature_value IS NULL` produce `predicted_value IS NULL` (no imputation; no error) and are recorded as such in `models.model_predictions`. This preserves the eligibility-row omission contract (rank-ineligible ETF/date pairs are absent from `features.feature_values` and so absent from predictions) while keeping the predictability surface complete on the feature side.

### 6.3 Failed-run lifecycle (parallel to 03a §6.3 and 03b §6.3)

**Pre-run fatal parse errors.** If `config/model.yaml` cannot be parsed at all (malformed YAML, missing required top-level keys per §7.2 / §7.3, file unreadable, encoding error), the orchestrator **does not open a `models.model_runs` row**. The fatal error is logged to stderr only. No `models.model_run_issues` row is written for this case (no `model_run_id` exists yet to FK against, parallel to 03a §6.3 / 03b §6.3 lifecycle).

**Open-run-before-validation lifecycle.** Once `config/model.yaml` parses, the model-run orchestrator opens the `models.model_runs` row (with `status='running'`) **before** validating the selected `feature_run_id`, the selected `target_run_id`, the `data_snapshot_id` chain, the snapshot's `status`, the model config semantics, and MLflow connectivity. The closed list of run-level blocking conditions is:

1. The selected `feature_run_id` does not exist or has `status != 'succeeded'`.
2. The selected `target_run_id` does not exist or has `status != 'succeeded'`.
3. The two runs reference different `data_snapshot_id` values.
4. The shared `data_snapshot_id` references a snapshot with `status='invalidated'`.
5. The active `feature_set_version` recorded on the feature run is not present in `features.feature_definitions` for the run's reported version (defensive check; the upstream composite FK already enforces this at the row level, but the orchestrator surfaces the clearer error).
6. The active `target_set_version` recorded on the target run is not present in `targets.target_definitions` for the run's reported version (analogous defensive check).
7. `config/model.yaml` semantic validation (§7.3) fails (e.g., unknown `rank_method` value, unknown `model_kind`, unknown calibration method, weights not summing to one, sleeve missing from `sleeve_rank_methods`).
8. The configured combined-score formula references a `model_kind` not enabled in `config/model.yaml`.
9. The MLflow tracking server is unreachable at orchestrator startup (`MLFLOW_TRACKING_URI` cannot be contacted within a bounded timeout).

If any of these is detected, the orchestrator (a) marks the run row `status='failed'`, (b) populates `error_message` and `completed_at_utc`, (c) writes the appropriate `models.model_run_issues` row (FK satisfied because the run row is already open), and (d) writes **no** `models.model_predictions` rows for that run.

The `models.model_runs.status` enumeration is the same closed three-value set used by 03a `features.feature_runs.status` and 03b `targets.target_runs.status`: `('running', 'succeeded', 'failed')`. There is no `'blocked'`, `'pending'`, `'queued'`, `'partial'`, or other value in 03c's run-status enum. Upstream-blocking conditions are expressed via the predicate `status != 'succeeded'`, not via a distinct status value.

**Front-edge horizon truncation is NOT a run-level blocking condition.** It is row-level absence on the training-set side per §6.1 and row-level absence on the target-row side per 03b §6.5 Bucket 1. The model run completes `status='succeeded'` provided the training set has at least `min_training_rows` rows (Proposed default in `config/model.yaml`; see §6.4) and the prediction-emission step succeeds.

**Atomicity contract (parallel to 03a §6.5 and 03b §6.5).** 03c writes are split across **two different 03c-owned run types**, each with its own atomicity contract:

- **Model-run execution writes `models.model_predictions`.** A model run (one row in `models.model_runs`) may write `models.model_predictions` rows **in transactional batches** rather than in one massive transaction; the natural batch unit is a (model_kind, signal-date-window) tuple. Failed model runs may retain partial `models.model_predictions` rows (rows from batches that committed before the failure). Downstream consumers — Section 4 backtest, Section 5 portfolio, Section 6 UI — must **only consume `models.model_predictions` rows whose `model_run_id` links to a `models.model_runs.status='succeeded'` row**.
- **Scoring-run execution writes `models.combined_scores`.** A scoring run (one row in `models.scoring_runs`) is a separate 03c-owned run type that consumes one or more already-`status='succeeded'` `models.model_runs` rows (via `models.scoring_run_models`) and emits combined-score / rank rows. A scoring run may write `models.combined_scores` rows in transactional batches as well; the natural batch unit is a (signal-date-window, sleeve_id) tuple. Failed scoring runs may retain partial `models.combined_scores` rows. Downstream consumers must **only consume `models.combined_scores` rows whose `scoring_run_id` links to a `models.scoring_runs.status='succeeded'` row**.

Both run types share the same closed three-value `status` enum `('running', 'succeeded', 'failed')` and the same open-run-before-validation lifecycle, but they are distinct executions: a model run never writes to `models.combined_scores`, and a scoring run never writes to `models.model_predictions`. The schema deliberately does not delete partial rows on failure for either run type; the run-status filter is the consumption-side signal in both cases.

### 6.4 Baseline model implementations (Proposed defaults requiring approval)

03c proposes two baseline implementations matching SDR Decision 6's dual-target framework. The specific algorithmic choices are **Proposed defaults requiring Approver approval** per §11.6.

#### 6.4.1 Regression baseline — forward excess return

**Proposed model form:** Ridge regression of the per-row regression target value (`excess_return_h`) on the standardized feature vector for that ETF/signal-date.

- **Standardization**: per-feature z-score over the training set's full pooled distribution (no per-ETF or per-sleeve standardization in Phase 1 to keep the baseline simple); the fitted means and standard deviations are stored in the MLflow artifact for reproducibility.
- **Hyperparameters**: regularization strength `alpha` (default proposal: chosen via Section 4 walk-forward grid search; for the first testable formula, fixed `alpha = 1.0` is proposed). Other hyperparameters at scikit-learn-style defaults; configurable via `config/model.yaml`.
- **One model per horizon**: one fit for `excess_return_63d` and one fit for `excess_return_126d`. The two fits are independent.
- **No sleeve-specific or per-ETF fits in Phase 1**: a single pooled fit across the entire training set per horizon. Sleeve-specific fits are flagged as a possible future amendment (see §10).

**Output:**
- `models.model_predictions.predicted_value` — predicted excess return for the (etf, as_of_date, model_kind = `regression_excess_return_h63` or `regression_excess_return_h126`).
- `models.model_predictions.calibrated_probability` — NULL (calibration applies only to classification models).
- MLflow run records the fitted coefficients, the `alpha`, the standardization parameters, training-set summary, and held-out validation metrics (RMSE, MAE, R^2 on validation folds; Section 4 supplies the fold structure).

#### 6.4.2 Classification baseline — outperformance

**Proposed model form:** Logistic regression of the per-row classification target value (`outperformance_h ∈ {0, 1}`) on the standardized feature vector for that ETF/signal-date, with calibration applied on held-out walk-forward folds (per §6.5).

- **Standardization**: same as the regression baseline.
- **Hyperparameters**: regularization strength `C` (default proposal: chosen via Section 4 walk-forward grid search; for the first testable formula, fixed `C = 1.0` is proposed). Other hyperparameters at scikit-learn-style defaults; configurable via `config/model.yaml`.
- **One model per horizon**: one fit for `outperformance_63d` and one fit for `outperformance_126d`. The two fits are independent.
- **No sleeve-specific or per-ETF fits in Phase 1.**

**Output:**
- `models.model_predictions.predicted_value` — raw (uncalibrated) probability of outperformance for the (etf, as_of_date, model_kind = `classification_outperformance_h63_uncalibrated` or `_h126_uncalibrated`).
- `models.model_predictions.calibrated_probability` — calibrated probability for the corresponding calibrated `model_kind` (e.g., `classification_outperformance_h63_platt`). The calibrated and uncalibrated outputs may share a `model_run_id` (one run produces both) or live on separate `model_run_id` values (one run for the uncalibrated logistic, another for the calibrator on top); the choice is an Implementation default classified in §11.5.

**Closed enumeration of `model_kind` values for Phase 1 03c (Proposed default requiring approval):**

- `regression_excess_return_h63`
- `regression_excess_return_h126`
- `classification_outperformance_h63_uncalibrated`
- `classification_outperformance_h63_calibrated`
- `classification_outperformance_h126_uncalibrated`
- `classification_outperformance_h126_calibrated`

Six entries. Adding a new `model_kind` requires a 03c amendment with Approver approval. The closed enumeration is enforced by a `CHECK` constraint on `models.model_definitions.model_kind` and a composite FK from `models.model_predictions(model_set_version, model_kind)` to `models.model_definitions(model_set_version, model_kind)` (parallel to the 03a / 03b composite-FK pattern).

**Minimum training rows.** A Proposed default `min_training_rows = 1000` is set in `config/model.yaml`. A model run with fewer training rows after the §6.1 filtering produces `severity='fail'` `models.model_run_issues` row with `issue_type='insufficient_training_data'` and aborts. The threshold itself is a Proposed default requiring approval.

### 6.5 Calibration pipeline (Proposed default requiring approval)

Per SDR Decision 7: "Probability outputs must be calibrated before hard thresholds such as 60% are treated as meaningful. Calibration methods may include Platt scaling, isotonic regression, or logistic calibration on held-out walk-forward folds."

**Proposed Phase 1 default:** **Platt scaling** (sigmoid calibration) applied on **held-out walk-forward fold predictions** supplied by Section 4. Alternatives (isotonic regression; logistic calibration) are reserved as `calibration_method` values in `config/model.yaml`; only the Approver-resolved value is enabled at any time.

**Pipeline contract:**

1. The classification baseline is fit on the in-fold training rows.
2. The fitted classifier produces raw (uncalibrated) probabilities on the held-out fold rows.
3. The calibrator is fit on (raw probability, observed label) pairs from the held-out folds. This requires Section 4's fold structure; 03c integrates with it via a thin `CalibrationFoldData` contract (see §6.6 below).
4. The calibrator is applied to all prediction-emission rows (training, held-out, and front-edge prediction-only rows).
5. Calibrated probabilities are stored in `models.model_predictions.calibrated_probability` with non-null values constrained to `[0, 1]`.

**Output contract:**
- Calibrated probability ∈ `[0, 1]` (asserted by a `CHECK` constraint on `models.model_predictions.calibrated_probability` and verified by §8 tests).
- `NULL` permitted on rows where the underlying prediction is `NULL` (e.g., feature-side missing data).
- The calibrator's parameters are stored as an MLflow artifact alongside the fitted classifier.

**Calibration failure handling.** If the calibrator's fit fails (e.g., insufficient held-out rows, degenerate label distribution), the orchestrator emits `severity='fail'` `models.model_run_issues` with `issue_type='calibration_failed'` and the model run aborts. The uncalibrated classifier outputs are not used as a substitute (no silent fallback to uncalibrated probabilities for ranking).

**Section 4 dependency.** Phase 1 03c assumes Section 4 supplies the held-out fold layout. Until Section 4 is locked, the calibration pipeline is structurally specified but not buildable end-to-end — the calibrator's fold-data input shape is recorded in §6.6 below for forward use, and the integration test path in §8 includes a fixture fold structure that simulates Section 4. This ordering is consistent with the EW §3 section-by-section approach.

### 6.6 `models.*` schema

Ten tables in the `models` schema. Migration filenames continuing from `0001_initial_setup.sql` (Section 2) and the eventual 03a / 03b migrations are an Implementation default (§11.5).

#### `models.model_definitions`

Closed catalog of `model_kind` values for an active `model_set_version`. Parallel to `features.feature_definitions` and `targets.target_definitions`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `model_set_version` | `text` | not null | matches `config/model.yaml` `model_set_version` |
| `model_kind` | `text` | not null, CHECK in the closed enumeration above | |
| `family` | `text` | not null, CHECK in (`'regression_excess_return'`, `'classification_outperformance_uncalibrated'`, `'classification_outperformance_calibrated'`) | |
| `horizon_trading_days` | `integer` | not null, CHECK in (63, 126) | matches the 03b horizon enumeration |
| `algorithm` | `text` | not null | e.g., `'ridge_regression'`, `'logistic_regression'`, `'platt_scaling'` |
| `calibration_method` | `text` | nullable, CHECK in (`'platt'`, `'isotonic'`, `'logistic_on_folds'`) when not null | populated only for calibrated classification kinds |
| `inputs_described` | `text` | not null | summary of which feature names and target names are read |
| `parameters` | `jsonb` | nullable | algorithm-specific parameters (e.g., `alpha`, `C`, calibration parameters) |
| | | PK (`model_set_version`, `model_kind`) | |

Populated at orchestrator startup by reading `config/model.yaml` for the active version. Existing rows for prior `model_set_version` values are retained for audit; only the active version is consulted by run / prediction writes.

#### `models.model_runs`

Every model training+prediction run. One row = one MLflow run.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `model_run_id` | `bigserial` | PK | surrogate key |
| `data_snapshot_id` | `bigint` | not null, FK → `ops.data_snapshots` | redundantly stored for query convenience; transitively reachable through the feature/target run FKs |
| `feature_run_id` | `bigint` | not null, FK → `features.feature_runs(feature_run_id)` | per Approver constraint: every model run links back to a feature run |
| `feature_set_version` | `text` | not null | participates in the composite FK below |
| `target_run_id` | `bigint` | not null, FK → `targets.target_runs(target_run_id)` | per Approver constraint: every model run links back to a target run |
| `target_set_version` | `text` | not null | participates in the composite FK below |
| `model_set_version` | `text` | not null | matches `config/model.yaml` `model_set_version`; participates in composite FKs from `model_predictions` |
| `model_kind` | `text` | not null | matches `models.model_definitions.model_kind` for the active `model_set_version` |
| `mlflow_experiment_id` | `text` | not null | identifies the MLflow experiment |
| `mlflow_run_id` | `text` | not null, unique | identifies the MLflow run; 1:1 with this Postgres row |
| `commit_hash` | `text` | not null | code commit at run start |
| `config_hash` | `text` | not null | hash of `config/model.yaml` at run start |
| `started_at_utc` | `timestamptz` | not null default `now()` | |
| `completed_at_utc` | `timestamptz` | nullable | |
| `status` | `text` | not null, CHECK in (`'running'`, `'succeeded'`, `'failed'`) | |
| `error_message` | `text` | nullable | populated on `'failed'` |
| `random_seed` | `bigint` | not null | for deterministic reproducibility (see §8.2) |
| `training_dataset_summary` | `jsonb` | nullable | row counts, unique-ETF count, signal-date min/max, drop counts by reason (`feature_null`, `target_null`, `target_absent`, `eligibility_filter`) |
| `validation_metrics` | `jsonb` | nullable | metric name → metric value (e.g., `{"rmse_validation": 0.024, "auc_validation": 0.61}`); the metric set is `model_kind`-specific |
| `created_by` | `text` | not null | container or user identifier |
| `notes` | `text` | nullable | free-form |
| | | UNIQUE (`model_run_id`, `model_set_version`) | enables composite FK from `models.model_predictions` (parallel to 03a / 03b pattern) |
| | | Composite FK (`feature_run_id`, `feature_set_version`) → `features.feature_runs(feature_run_id, feature_set_version)` | enforces at the database level that the `feature_set_version` recorded on this row matches the linked feature run's |
| | | Composite FK (`target_run_id`, `target_set_version`) → `targets.target_runs(target_run_id, target_set_version)` | analogous for targets |
| | | Composite FK (`model_set_version`, `model_kind`) → `models.model_definitions(model_set_version, model_kind)` | enforces every `model_run` corresponds to a catalogued `model_kind` in the active version |

Indexes: `(data_snapshot_id)`, `(feature_run_id)`, `(target_run_id)`, `(mlflow_run_id)`, `(model_kind, started_at_utc)`.

#### `models.model_predictions`

Per-`(etf_id, as_of_date, model_kind, model_run_id)` model output.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `etf_id` | `bigint` | not null, FK → `universe.etfs` | |
| `as_of_date` | `date` | not null | signal date `T` |
| `model_kind` | `text` | not null | |
| `model_set_version` | `text` | not null | participates in composite FK below |
| `model_run_id` | `bigint` | not null | participates in composite FK below; the legacy single-column FK on `model_run_id` alone is **not** declared (composite FK already enforces existence) |
| `horizon_trading_days` | `integer` | not null, CHECK in (63, 126) | denormalized from `model_definitions` for query convenience |
| `predicted_value` | `numeric(24,12)` | nullable | predicted excess return (regression family) or raw probability (uncalibrated classification family); NULL when feature-side inputs are missing |
| `calibrated_probability` | `numeric(24,12)` | nullable, CHECK (`calibrated_probability IS NULL OR (calibrated_probability >= 0 AND calibrated_probability <= 1)`) | populated only for calibrated classification rows; NULL otherwise |
| `prediction_context` | `text` | not null, CHECK in (`'in_sample_diagnostic'`, `'walk_forward_oos'`, `'current_scoring'`) | per §6.2 closed enum; identifies the operational regime in which the prediction was produced; consumed by Section 4 to enforce out-of-sample-only backtest evaluation |
| | | PK (`etf_id`, `as_of_date`, `model_kind`, `model_run_id`) | |
| | | Composite FK (`model_run_id`, `model_set_version`) → `models.model_runs(model_run_id, model_set_version)` | |
| | | Composite FK (`model_set_version`, `model_kind`) → `models.model_definitions(model_set_version, model_kind)` | |

Indexes:
- `(model_run_id)` for run-scoped queries.
- `(etf_id, as_of_date)` for primary lookups.
- `(model_kind, as_of_date)` for cross-sectional queries.
- `(as_of_date)` for time-slice queries.

**Nullable-value semantics.** `predicted_value IS NULL` indicates a feature-side missing-input case at prediction time (not an error). `calibrated_probability IS NULL` is the correct value for non-calibrated `model_kind` rows and for rows whose underlying raw probability is NULL (null propagation).

#### `models.scoring_runs`

A combined-score / ranking run consumes one or more `model_runs` and produces `combined_scores` rows.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `scoring_run_id` | `bigserial` | PK | |
| `data_snapshot_id` | `bigint` | not null, FK → `ops.data_snapshots` | must equal the snapshot anchored by all consumed model runs |
| `feature_run_id` | `bigint` | not null, FK → `features.feature_runs(feature_run_id)` | must equal the feature run consumed by the model runs (single-feature-run discipline in current 03c scope; multi-feature-run scoring is a future amendment) |
| `target_run_id` | `bigint` | not null, FK → `targets.target_runs(target_run_id)` | likewise for targets |
| `combined_score_formula_version` | `text` | not null | matches `config/model.yaml` `combined_score.formula_version` |
| `scoring_set_version` | `text` | not null | matches `config/model.yaml` `scoring_set_version` |
| `commit_hash` | `text` | not null | |
| `config_hash` | `text` | not null | hash of `config/model.yaml` at run start |
| `started_at_utc` | `timestamptz` | not null default `now()` | |
| `completed_at_utc` | `timestamptz` | nullable | |
| `status` | `text` | not null, CHECK in (`'running'`, `'succeeded'`, `'failed'`) | |
| `error_message` | `text` | nullable | |
| `created_by` | `text` | not null | |
| `notes` | `text` | nullable | |

Index: `(data_snapshot_id)`, `(combined_score_formula_version, started_at_utc)`.

#### `models.scoring_run_models`

Junction table recording which `model_run_id` values were consumed by a given `scoring_run_id` and in what role.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `scoring_run_id` | `bigint` | not null, FK → `models.scoring_runs` | |
| `model_run_id` | `bigint` | not null, FK → `models.model_runs` | |
| `role` | `text` | not null, CHECK in (`'regression_h63'`, `'regression_h126'`, `'classification_h63'`, `'classification_h126'`) | which role this model run plays in the combined-score formula |
| | | PK (`scoring_run_id`, `model_run_id`) | |
| | | UNIQUE (`scoring_run_id`, `role`) | exactly one model run per role per scoring run |

Indexes: `(model_run_id)`.

The closed `role` enumeration matches the four `model_kind` values that participate in the Phase 1 first testable combined-score formula: two horizons × {regression, calibrated classification}. Adding a fifth role (e.g., a risk score model) requires a 03c amendment.

#### `models.combined_scores`

Per-`(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)` combined score and rank.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `etf_id` | `bigint` | not null, FK → `universe.etfs` | |
| `as_of_date` | `date` | not null | signal date `T` |
| `sleeve_id` | `bigint` | not null, FK → `universe.sleeves` | per the once-per-sleeve Proposed default; an ETF eligible across multiple sleeves appears in each |
| `horizon_trading_days` | `integer` | not null, CHECK in (63, 126) | one combined score row per horizon |
| `scoring_run_id` | `bigint` | not null, FK → `models.scoring_runs` | |
| `rank_method` | `text` | not null, CHECK in the closed enumeration of §6.7 | denormalized from `universe.etfs.rank_method` at scoring time; recorded for audit |
| `combined_score` | `numeric(24,12)` | nullable | result of the combined-score formula at signal date for ETF; NULL when one of the input components is NULL (no imputation) |
| `rank_within_sleeve` | `integer` | nullable | rank within `sleeve_id` at `as_of_date`; NULL when `combined_score IS NULL` |
| `score_components` | `jsonb` | nullable | structured detail: per-component pre-standardization values, post-standardization z-scores, weights, and the formula version; for transparency and audit |
| `created_at_utc` | `timestamptz` | not null default `now()` | |
| | | PK (`etf_id`, `as_of_date`, `sleeve_id`, `horizon_trading_days`, `scoring_run_id`) | |

Indexes:
- `(scoring_run_id)` for run-scoped queries.
- `(etf_id, as_of_date)` for primary lookups.
- `(as_of_date, sleeve_id, horizon_trading_days)` for "give me the ranking at signal date `T` for sleeve `S` and horizon `h`" queries (the principal portfolio-side query).

**Eligibility filter at scoring time.** Only `(etf, as_of_date)` pairs that are rank-eligible per `universe.etf_eligibility_history` (resolved via the Section 2 SQL view) at signal date `T` produce `combined_scores` rows. Pairs not rank-eligible are **absent** from `combined_scores` (parallel to 03a / 03b eligibility-row omission).

**Sleeve duplication semantics.** Per the Proposed default, an ETF eligible in `n` sleeves at signal date `T` produces `n` rows in `combined_scores` for each horizon — one per sleeve, all sharing the same `combined_score` value but with potentially different `rank_within_sleeve` because the within-sleeve cross-section differs. The alternative (rank once across all eligible sleeves combined) is flagged in §10 as an Open Question.

#### `models.model_versions`

Registered model versions. Each version corresponds to a specific `model_run_id` that has been promoted past SDR Decision 12's first promotion gate (Research model → Internal paper tracking).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `model_version_id` | `bigserial` | PK | |
| `model_kind` | `text` | not null | |
| `model_run_id` | `bigint` | not null, FK → `models.model_runs` | the run this version was promoted from |
| `version_label` | `text` | not null | unique within `model_kind`; e.g., `"baseline_v1"` |
| `mlflow_model_uri` | `text` | not null | URI to the MLflow registered model + version |
| `state` | `text` | not null, CHECK in (`'Active'`, `'Warning'`, `'Paused'`, `'Retired'`) | per SDR Decision 12 |
| `state_entered_at_utc` | `timestamptz` | not null default `now()` | when the current state was entered |
| `registered_at_utc` | `timestamptz` | not null default `now()` | when the row was created |
| `registered_by` | `text` | not null | |
| `approved_at_utc` | `timestamptz` | nullable | when the Approver approved this version (the first promotion gate); MUST be non-null before `state` may be `'Active'` (CHECK constraint) |
| `approved_by` | `text` | nullable | |
| `notes` | `text` | nullable | |
| | | UNIQUE (`model_kind`, `version_label`) | |
| | | CHECK (`(state = 'Active' AND approved_at_utc IS NOT NULL AND approved_by IS NOT NULL) OR state IN ('Warning', 'Paused', 'Retired') OR (state = 'Active' AND approved_at_utc IS NULL AND approved_by IS NULL AND FALSE)`) | enforced; cannot be `'Active'` without approval audit fields populated |

The CHECK constraint above is written in a verbose form to make the intent explicit: `state = 'Active'` requires both `approved_at_utc` and `approved_by` to be non-null. Other states do not require approval audit (a model can be created in `'Paused'` state for evaluation, for example).

Indexes: `(model_run_id)`, `(model_kind, state)`.

**Partial unique index for at-most-one-Active-per-model_kind.** A partial unique index on `(model_kind) WHERE state = 'Active'` is declared on `models.model_versions`. The index uses only columns the schema actually defines (`model_kind` and `state`) and enforces the SDR-Decision-12-aligned invariant that there is at most one Active version per `model_kind` at any time. Inserting (or updating to) a second `state='Active'` row for the same `model_kind` is rejected at the database level. (See §9.6.)

#### `models.model_state_history`

Append-only audit log of every state transition on `models.model_versions`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `transition_id` | `bigserial` | PK | |
| `model_version_id` | `bigint` | not null, FK → `models.model_versions` | |
| `from_state` | `text` | nullable, CHECK in the four states or NULL | NULL on the initial state insertion |
| `to_state` | `text` | not null, CHECK in the four states | |
| `changed_at_utc` | `timestamptz` | not null default `now()` | |
| `changed_by` | `text` | not null | identifier of the human/Approver who made the change (Phase 1: Approver-only) |
| `reason` | `text` | not null | human-readable rationale |
| `mlflow_run_id_at_transition` | `text` | nullable | optional snapshot of the linked MLflow run at the time of the transition |

Indexes: `(model_version_id, changed_at_utc)`.

**Phase 1 transition discipline.** All state transitions are written by Approver-initiated procedures only. There are no automated triggers in Phase 1. The audit log is append-only — no `UPDATE` or `DELETE` paths are exposed in `common/` helpers for this table.

#### `models.model_run_issues`

Model-layer issue log. Parallel to `features.feature_run_issues` and `targets.target_run_issues`. **Disjoint from the upstream issue logs**; the closed `issue_type` enumeration is independent.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `model_run_issue_id` | `bigserial` | PK | |
| `model_run_id` | `bigint` | not null, FK → `models.model_runs(model_run_id)` | |
| `issue_type` | `text` | not null, CHECK in the closed enumeration below | |
| `severity` | `text` | not null, CHECK in (`'warning'`, `'fail'`) | |
| `etf_id` | `bigint` | nullable, FK → `universe.etfs` | populated when per-ETF; null for run-level issues |
| `as_of_date` | `date` | nullable | signal date when applicable; null for run-level issues |
| `affected_model_kind` | `text` | nullable | model kind when applicable; null for run-level issues |
| `summary` | `text` | not null | short, structured summary suitable for UI display |
| `detail` | `jsonb` | nullable | structured detail (e.g., naming the offending `feature_run_id`, the conflicting snapshot ID, the calibration exception message) |
| `created_at_utc` | `timestamptz` | not null default `now()` | |

**Closed `issue_type` enumeration for 03c (Proposed default requiring approval; new types require an 03c amendment):**

| Issue type | Severity | Run-level / row-level | Trigger |
|---|---|---|---|
| `'invalidated_snapshot_blocked'` | `'fail'` | run-level | the data snapshot the model run resolved is `'invalidated'` |
| `'failed_feature_run_blocked'` | `'fail'` | run-level | the linked `feature_run_id` is not in `status='succeeded'` |
| `'failed_target_run_blocked'` | `'fail'` | run-level | the linked `target_run_id` is not in `status='succeeded'` |
| `'partial_feature_run_blocked'` | `'fail'` | run-level | (Phase 1 default) the linked `feature_run_id` resolves to a partial upstream ingestion dependency that 03a treated as blocking; backstop in case 03a's filter discipline ever loosens |
| `'partial_target_run_blocked'` | `'fail'` | run-level | analogous for targets |
| `'snapshot_mismatch'` | `'fail'` | run-level | the feature run and target run reference different `data_snapshot_id` values, OR the denormalized `models.model_runs.data_snapshot_id` does not equal both upstream values, OR a referenced snapshot is absent from `ops.data_snapshots`. Single canonical issue type for any snapshot-chain inconsistency |
| `'feature_set_version_mismatch'` | `'fail'` | run-level | active `feature_set_version` recorded on the feature run is not present in `features.feature_definitions` |
| `'target_set_version_mismatch'` | `'fail'` | run-level | analogous for targets |
| `'rank_method_unknown'` | `'fail'` | run-level | one or more `universe.etfs.rank_method` values fall outside the closed enumeration §6.7 defines |
| `'pending_section_3_sentinel'` | `'fail'` | run-level | one or more `rank_method` values still equal the Section 2 sentinel `pending_section_3`; 03c is not authorized to start a ranking run while sentinels exist |
| `'insufficient_training_data'` | `'fail'` | run-level | training set has fewer rows than `min_training_rows` after the §6.1 filtering |
| `'all_null_training_column'` | `'fail'` | run-level | a feature column or target column has zero non-null values across the entire assembled training set; covers both feature-side and target-side cases |
| `'single_class_training_set'` | `'fail'` | run-level | binary outperformance target is all-zeros or all-ones in the training set; classifier cannot be fit |
| `'calibration_failed'` | `'fail'` | run-level | calibrator fit failed for any reason (degenerate label distribution, insufficient held-out rows, fitter exception); consolidates all calibrator-fit failure causes (degenerate fold, insufficient held-out rows, fitter exception) |
| `'prediction_emission_failed'` | `'fail'` | run-level | shape mismatch between fit-time and predict-time feature columns, or other prediction-emission error after a successful fit |
| `'mlflow_unavailable'` | `'fail'` | run-level | the MLflow tracking server cannot be reached at orchestrator startup |
| `'mlflow_logging_partial'` | `'fail'` | run-level | MLflow tracking server became unreachable mid-run; metric/artifact logging incomplete after retry budget exhausted; fitted model is not persisted to MLflow; Postgres run row remains as audit anchor |
| `'high_null_target_rate'` | `'warning'` | run-level | percentage of training-eligible rows dropped due to `target_value IS NULL` exceeds a configurable threshold (Proposed default: 5%); informational only |
| `'high_null_feature_rate'` | `'warning'` | run-level | percentage of training-eligible rows dropped due to `feature_value IS NULL` exceeds the threshold; informational only |
| `'index_only_benchmark_propagated'` | `'warning'` | per-ETF or run-level | propagated from `targets.target_run_issues` via 03c's optional annotation; recorded for visibility (does not duplicate the upstream issue) |
| `'model_run_failed'` | `'fail'` | run-level | model run failed mid-execution from any cause not covered by a more specific issue type (parallel to `feature_run_failed` and `target_run_failed`) |

Indexes: `(model_run_id)`, `(issue_type)`, `(etf_id, as_of_date)`.

**Scope and write discipline (parallel to 03a §6.6 and 03b §6.6):**

- Lifecycle integration with `models.model_runs`: every row references a real `models.model_runs` row through the NOT NULL FK on `model_run_id`. The orchestrator opens the `models.model_runs` row first, then validates inputs; on a block detection it marks the run `'failed'` and writes the issue row in the same transactional sequence.
- 03c does **not** write to `ops.data_quality_exceptions` under any circumstance (verified by §8.2 static check, parallel to 03a / 03b).
- The closed enumeration on `issue_type` ensures adding a new issue type is a deliberate spec change, not an ad-hoc string. New types are added under 03c amendments.
- 03c does **not** modify `features.feature_run_issues` or `targets.target_run_issues` enumerations. The `'index_only_benchmark_propagated'` issue type above is a **new 03c entry** that records propagation; it does not redefine the upstream `'index_only_benchmark'` issue type.
- **Scoring-run-level issues (e.g., cross-model snapshot mismatch within a scoring run, degenerate cross-section at a signal date, `rank_method_unsupported_in_phase1` per §6.7) are written to the separate `models.scoring_run_issues` table below, not to `models.model_run_issues`.** The two tables are deliberately disjoint to keep FK semantics clean (a `models.model_run_issues` row references exactly one `models.model_runs` row; a scoring run typically aggregates several).

**Consumption.**

- Section 6 UI Model Registry / Run Browser surfaces (read-only) display these issues alongside the `model_runs` they belong to.
- Section 4 backtest harness may surface these issues in run reports.
- Section 5 portfolio rules engine reads `model_run_issues` for a model version's run history when evaluating the second promotion gate.

#### `models.scoring_run_issues`

Scoring-run-layer issue log. Parallel to `models.model_run_issues` but FK'd to `models.scoring_runs(scoring_run_id)`. **Disjoint enumeration** from `models.model_run_issues`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `scoring_run_issue_id` | `bigserial` | PK | |
| `scoring_run_id` | `bigint` | not null, FK → `models.scoring_runs(scoring_run_id)` | |
| `issue_type` | `text` | not null, CHECK in the closed enumeration below | |
| `severity` | `text` | not null, CHECK in (`'warning'`, `'fail'`) | |
| `sleeve_id` | `bigint` | nullable, FK → `universe.sleeves` | populated when sleeve-scoped (e.g., `'rank_method_unsupported_in_phase1'`); null otherwise |
| `as_of_date` | `date` | nullable | signal date when applicable; null for scoring-run-level issues |
| `summary` | `text` | not null | short, structured summary suitable for UI display |
| `detail` | `jsonb` | nullable | structured detail (e.g., affected ETF count, the conflicting `model_run_id` set, the offending sleeve list) |
| `created_at_utc` | `timestamptz` | not null default `now()` | |

**Closed `issue_type` enumeration for `models.scoring_run_issues` (Proposed default requiring approval):**

| Issue type | Severity | Trigger |
|---|---|---|
| `'cross_model_snapshot_mismatch'` | `'fail'` | the constituent model runs of a scoring run reference more than one distinct `data_snapshot_id` |
| `'cross_model_set_version_mismatch'` | `'fail'` | the constituent model runs reference more than one distinct `model_set_version` |
| `'degenerate_cross_section'` | `'warning'` | at a `(signal_date, horizon)`, the cross-sectional standardization input has variance ≤ 1e-12 (effectively a single-ETF cross-section); the combined-score row for the lone ETF is recorded as `combined_score = 0.0`, `rank_within_sleeve = 1`; downstream consumers may filter |
| `'rank_method_unsupported_in_phase1'` | `'warning'` | one or more sleeves resolve to `rank_method='absolute_with_context'`; the current first-testable formula does not produce combined-score rows for those ETFs (per §6.7 / §10.6); the affected sleeve(s) and ETF count are recorded for audit |
| `'scoring_run_failed'` | `'fail'` | scoring run failed mid-execution from any cause not covered by a more specific issue type |

Indexes: `(scoring_run_id)`, `(issue_type)`, `(sleeve_id, as_of_date)`.

**Scope and write discipline.**

- Every row references a real `models.scoring_runs` row through the NOT NULL FK. Lifecycle parallels `models.model_runs`: the orchestrator opens the `models.scoring_runs` row first, validates inputs, then writes the issue row on detection.
- 03c does **not** route scoring-run-level issues to `ops.data_quality_exceptions` (Section 2 framework remains ingestion-owned).
- The two issue tables (`models.model_run_issues` and `models.scoring_run_issues`) have **disjoint** `issue_type` enumerations — there is no overlap, and consumers querying for a specific issue type query the correct table without ambiguity.


### 6.7 `rank_method` allowed values and per-sleeve semantics (Proposed default requiring approval)

The Section 2 sentinel `pending_section_3` in `config/universe.yaml` is closed by 03c with the following Proposed-default closed enumeration of allowed values for `universe.etfs.rank_method`:

**Closed enumeration (Proposed default requiring approval):**

| `rank_method` value | Semantics |
|---|---|
| `'benchmark_relative'` | Combined score is computed using the regression baseline's predicted excess return against the ETF's `primary_benchmark_id` and the calibrated probability of outperformance against the same primary benchmark. Both inputs are cross-sectionally standardized at signal date `T`. This is the standard treatment for sleeves where the SDR Decision 5 framing is "compare to a benchmark." |
| `'absolute_with_context'` | Per SDR Decision 5 #5, ETFs flagged with this `rank_method` are evaluated primarily by absolute opportunity / risk and hedge value; benchmark-relative views remain available as **context only** in Section 6 UI and Section 4 reports. The current first-testable two-component combined-score formula (§6.8) consumes only benchmark-relative inputs (regression excess return + calibrated probability of outperformance per 03b's locked target definitions) and therefore cannot honor `absolute_with_context` ranking. **Phase 1 current disposition:** ETFs flagged `'absolute_with_context'` produce **no `models.combined_scores` rows**; one `severity='warning'` row is written to `models.scoring_run_issues` per scoring run with `issue_type='rank_method_unsupported_in_phase1'` listing the affected sleeve(s) and ETF count. Activation requires an Approver-approved 03c amendment that adds absolute-trend / absolute-gain `model_kind` values **and** the absolute / risk inputs needed by an extended combined-score formula. See §10.6. |
| `'peer_relative'` | Combined score is computed as the standard 2-component formula but the cross-sectional standardization is performed within **the ETF's sleeve only** (not pooled across all sleeves) and the ranking is sleeve-cross-sectional only. This is the standard treatment for sleeves where SDR Decision 5 framing is "compare against peers" (e.g., REITs). |

**Per-sleeve default mapping (Proposed default requiring approval).** This mapping aligns with §10.5; the derivation column references the SDR Decision 5 sleeve description it draws from:

| Sleeve (locked Section 2 code) | Proposed default `rank_method` | SDR Decision 5 derivation |
|---|---|---|
| `BroadEquity` | `'benchmark_relative'` | "compare broad equity ETFs to SPY/VTI, small caps to IWM/IJR, growth/Nasdaq to QQQ" |
| `Sector` | `'benchmark_relative'` | "primary comparison to SPY, optional peer comparison to other sectors" |
| `Thematic` | `'benchmark_relative'` (subject to the index-only-benchmark interim constraint inherited from 03a §10.1 and 03b §10.1; an ETF whose primary benchmark is index-only inherits the Bucket 2 NULL behavior on the regression target side, which propagates to a NULL `combined_score` for that ETF/date) | "benchmark depends on theme" — handled via per-ETF `primary_benchmark_id` |
| `BondTreasury` | `'benchmark_relative'` (against bond-category benchmarks via `primary_benchmark_id`; the additional Decision 5 language about "absolute trend, volatility, drawdown, rate regime" is reserved for 4-component formula activation per §10.11 / §10.12, not Phase 1 current scope) | "compare to bond-category benchmarks" |
| `DiversifierHedge` | `'absolute_with_context'` per SDR Decision 5 | "evaluate primarily by absolute opportunity/risk and hedge value; SPY-relative return may be shown as context, not primary ranking target" — see §10.6 for the current row-emission consequence |
| `REITRealAsset` | `'peer_relative'` (REIT peers; SPY-relative is context per SDR Decision 5) | "compare against REIT/real-estate peers; optionally compare to SPY as opportunity-cost context" |

**Validation discipline.**

- `config/model.yaml` declares the closed enumeration of allowed `rank_method` values (above).
- Orchestrator startup, after opening the `models.model_runs` row with `status='running'` (per the §6.3 open-run-before-validation lifecycle), reads every `universe.etfs.rank_method` value and validates against the closed enumeration. Any value outside the enumeration produces `severity='fail'` `models.model_run_issues` with `issue_type='rank_method_unknown'`, marks the run `status='failed'`, populates `error_message` and `completed_at_utc`, and writes no `models.model_predictions` rows.
- The Section 2 sentinel `pending_section_3` is **not** an allowed value. Its presence at orchestrator startup produces `severity='fail'` with `issue_type='pending_section_3_sentinel'` under the same lifecycle. This satisfies the Section 2 obligation and prevents 03c from running on a config that has not been migrated to a real `rank_method` value.

**SDR-Decision-5 alignment under the current first-testable formula.** The current first-testable combined-score formula (§6.8) is benchmark-relative by 03b construction (excess return and outperformance are both benchmark-relative under 03b's locked threshold `θ = 0.0`). It honors SDR Decision 5 for the five sleeves whose Decision 5 framing involves comparison to a benchmark (broad equity, sector, thematic, bond-category, REIT peers). It does **not** honor SDR Decision 5 for the one sleeve Decision 5 explicitly removes from benchmark-relative ranking — `DiversifierHedge`. The current disposition for that sleeve is documented in §10.6: row-emission is suppressed and a warning issue is recorded, pending an Approver-approved amendment that adds absolute / risk inputs. **The Builder is not silently re-mapping `DiversifierHedge` to `'benchmark_relative'`.**

### 6.8 Combined-score formula (first testable; Proposed default requiring approval)

Per SDR Decision 6: "The ranking should eventually combine expected excess return, calibrated probability of outperformance, risk score, and trend/relative-strength confirmation. Do not hard-code the final combined score formula in this decision document. The engineering spec should define a first testable formula, and the backtester should compare alternatives."

**Proposed Phase 1 first testable formula (2-component):**

```
combined_score(e, T, h, sleeve) = w_r * z_r(predicted_excess_return_h(e, T))
                                + w_p * z_p(calibrated_probability_h(e, T))
```

where:
- `predicted_excess_return_h(e, T)` is `models.model_predictions.predicted_value` for `model_kind = 'regression_excess_return_h{h}'`;
- `calibrated_probability_h(e, T)` is `models.model_predictions.calibrated_probability` for `model_kind = 'classification_outperformance_h{h}_calibrated'`;
- `z_r(...)` and `z_p(...)` are cross-sectional z-scores computed at signal date `T` over the **ranking cross-section** for that ETF, where the ranking cross-section depends on `rank_method`:
  - for `'benchmark_relative'`: pool across all rank-eligible ETFs at `T` (single global cross-section, sleeve dimension preserved only for ranking, not for standardization);
  - for `'peer_relative'`: pool within the ETF's sleeve at `T` (per-sleeve standardization);
  - for `'absolute_with_context'`: not enabled in Phase 1 first testable scope (see §6.7 tension);
- weights `w_r` and `w_p` default to `0.5` each (equal weight) and live in `config/model.yaml`. **A Proposed default requiring approval.**
- if either input component is `NULL`, `combined_score` is `NULL` (no imputation); the corresponding `combined_scores.rank_within_sleeve` is also `NULL` and excluded from the ranking output.

**Order of operations: combined score before sleeve-aware ranking.** Per the Proposed default in §3 item 9: combined score is computed *first* per `(etf, signal_date, horizon)`, then ranking is computed *second* within sleeve. The alternative (rank within sleeve on each component first, then combine the ranks) is flagged in §10 as an Open Question for the Approver.

**ETF-eligible-in-multiple-sleeves: rank once per sleeve.** Per the Proposed default in §3 item 9: an ETF eligible across multiple sleeves (e.g., SPY simultaneously eligible in `BroadEquity` and used as a benchmark for `Sector`) produces one `combined_scores` row *per sleeve* it is eligible in, with the same `combined_score` value but potentially different `rank_within_sleeve`. The alternative (rank once across all eligible sleeves combined) is flagged in §10 as an Open Question.

**4-component formula reservation.** SDR Decision 6's full framing names four components: expected excess return, calibrated probability of outperformance, **risk score**, and **trend / relative-strength confirmation**. The first testable formula proposes only the first two. Hooks for the additional two are reserved in `config/model.yaml`:

```yaml
combined_score:
  formula_version: "v1_2component"
  components:
    expected_excess_return:
      enabled: true
      weight: 0.5
    calibrated_probability:
      enabled: true
      weight: 0.5
    risk_score:
      enabled: false                        # Phase 1 default off; awaiting Approver direction on definition
      weight: 0.0
    trend_relative_strength:
      enabled: false                        # Phase 1 default off; awaiting Approver direction on definition
      weight: 0.0
```

The 4-component variant requires Approver direction on (a) the operational definition of `risk_score` (proposed candidates: `-z(vol_realized_63d)` from 03a Family 2; or a downside-risk variant requiring a new 03a feature; or a backward-realized drawdown) and (b) the operational definition of `trend_relative_strength` (proposed candidates: a function of 03a Family 3 `trend_dist_sma_200` and 03a Family 4 `excess_return_vs_primary_benchmark_63d`; or another combination). Both definitions are **Open Questions for Approver** in §10.

**Combined-score formula version field.** `combined_score.formula_version` in `config/model.yaml` is recorded on every `models.scoring_runs` row. Changes to the formula bump this version; the `models.scoring_runs.combined_score_formula_version` is the canonical audit anchor. A future amendment that adds the 4-component variant uses `formula_version: "v2_4component"` (or similar; precise label assignment is at the Builder's discretion at amendment time).

### 6.9 Model-state lifecycle semantics (some Approver-resolved by SDR Decision 12; some Open Questions)

Per SDR Decision 12, models traverse the four states Active / Warning / Paused / Retired. Decision 12 also says: "A simple bad month should not automatically retire a model. Pause/retirement should require multiple conditions or sustained failure."

03c's contribution at the **schema level** is unambiguous: the four states are defined as a closed CHECK enumeration on `models.model_versions.state` (the four-state enumeration is Approver-resolved by SDR Decision 12; see §11.4 A-APP-01), and the audit log records every transition. The **Phase 1 Approver-only transitions** rule, the **initial-state-Paused** default, and the **Retired-is-terminal** rule are Proposed defaults requiring approval (§11.5 A-PRP-08, A-PRP-09, A-PRP-10) — SDR Decision 12 names the four states but does not specify these particulars.

03c's contribution at the **semantics level** is partial — what triggers each state, whether automated triggers ever exist in Phase 1 (proposed default: no), and what observability surfaces back into the audit log are partly Open Questions for the Approver.

**Proposed Phase 1 lifecycle semantics (Proposed default requiring approval):**

- **Initial state on registration:** `'Paused'` until the Approver explicitly approves via the first promotion gate. The CHECK constraint on `models.model_versions` enforces that `state='Active'` requires both `approved_at_utc` and `approved_by` to be non-null. This is more conservative than allowing a default `'Active'` state — a registered version sits in `'Paused'` (not used for ranking) until explicitly promoted.
- **Transition `'Paused' → 'Active'`:** Approver approval of the first promotion gate per SDR Decision 12 (Research model → Internal paper tracking). Records the timestamp and identity in `approved_at_utc` / `approved_by`; appends a `model_state_history` row with `from_state='Paused'`, `to_state='Active'`, and a `reason` populated by the Approver.
- **Transition `'Active' → 'Warning'`:** Approver direction. Phase 1 03c does **not** define automated triggers for the Active→Warning transition. Whether Phase 1 should support advisory automated triggers (e.g., "a calibration metric on the latest fold falls below threshold") is an Open Question.
- **Transition `'Warning' → 'Paused'`:** Approver direction. Same automation-status question.
- **Transition `'Paused' → 'Active'` (return)** or **`'Warning' → 'Active'`** (return): Approver direction.
- **Transition to `'Retired'`:** Approver direction; per SDR Decision 12, requires multiple conditions or sustained failure. Phase 1 03c does not define what "sustained" means quantitatively; that is an Open Question.
- **No `'Retired' → ...` transition is permitted.** Once retired, a version stays retired. A new version with a different `version_label` is the path forward. Enforced via a trigger or a `common/` helper that refuses such transitions.

**Section 5 forward dependency.** The second promotion gate (Paper tracking → influence on real decisions) is owned by Section 5 / portfolio review per SDR Decision 12. 03c provides the schema fields and the audit log; Section 5 reads them.

### 6.10 MLflow integration contract (writer side)

Per SDR Decision 11 and EW §7, every model training+prediction run produces one MLflow run that captures the EW §7 reproducibility metadata. The 1:1 mapping between `models.model_runs` rows and MLflow runs is enforced by the unique `mlflow_run_id` column on `models.model_runs`.

**MLflow experiment naming convention (Implementation default; see §11.5):**

- One MLflow experiment per `model_kind`. Experiment name pattern: `{model_kind}` (the `model_kind` string is unique and self-describing — e.g., `regression_excess_return_h63`).
- All runs for a given `model_kind` land in the same MLflow experiment.
- Adding a new `model_kind` (via 03c amendment) implies creating a new MLflow experiment; the orchestrator creates it on first use if it does not exist.

**MLflow run naming convention (Implementation default):**

- Run name pattern: `{model_set_version}--snapshot-{data_snapshot_id}--{started_at_utc:%Y%m%dT%H%M%SZ}`.

**MLflow tags (required on every run):**

| MLflow tag key | Source value |
|---|---|
| `data_snapshot_id` | from `ops.data_snapshots.data_snapshot_id` |
| `provider_name` | from `ops.data_snapshots.provider_name` |
| `provider_dataset_label` | from `ops.data_snapshots.provider_dataset_label` |
| `universe_config_hash` | from `ops.data_snapshots.universe_config_hash` |
| `universe_version_label` | from `ops.data_snapshots.universe_version_label` |
| `adjusted_price_convention` | from `ops.data_snapshots.adjusted_price_convention` |
| `commit_hash` | from `models.model_runs.commit_hash` |
| `config_hash` | from `models.model_runs.config_hash` |
| `feature_run_id` | from `models.model_runs.feature_run_id` |
| `feature_set_version` | from `models.model_runs.feature_set_version` |
| `target_run_id` | from `models.model_runs.target_run_id` |
| `target_set_version` | from `models.model_runs.target_set_version` |
| `model_set_version` | from `models.model_runs.model_set_version` |
| `model_kind` | from `models.model_runs.model_kind` |
| `random_seed` | from `models.model_runs.random_seed` |

The tag set is closed for Phase 1 03c. Adding a new tag (or removing one) requires an 03c amendment.

**MLflow params (required on every run):**

- All hyperparameters of the fitted model (e.g., `alpha`, `C`, calibration parameters).
- All cross-cutting orchestrator parameters from `config/model.yaml` that affect this run (`min_training_rows`, missing-data rule, etc.).

**MLflow metrics (required on every run, `model_kind`-specific):**

- For `regression_excess_return_h{h}`: validation RMSE, validation MAE, validation R^2, training RMSE, training MAE, training R^2.
- For `classification_outperformance_h{h}_uncalibrated`: validation log-loss, validation Brier score, validation AUC, training log-loss, training Brier score, training AUC.
- For `classification_outperformance_h{h}_calibrated`: same as the uncalibrated set, plus a calibration diagnostic (proposed: validation Brier-after-calibration, validation reliability-diagram bin counts).
- A `validation_metrics` JSONB on `models.model_runs` mirrors the MLflow metrics for queryability without a round-trip to MLflow.

**MLflow artifacts (required on every successful run):**

- The fitted model binary (per the algorithm's serialization convention — Implementation default: `joblib`).
- The standardization parameters (per-feature mean and standard deviation) as a separate artifact for inspection.
- The training-set summary as JSON: row counts, unique-ETF count, signal-date min/max, per-feature null counts, per-target null counts.
- The calibrator binary (when applicable) and calibration parameters as a separate artifact.

**MLflow registered model.** When a model run is promoted to a `models.model_versions` row, an MLflow registered model + version is created and the URI is recorded in `models.model_versions.mlflow_model_uri`. The MLflow registered model name pattern is `{model_kind}` (the same string as the experiment name); the version is auto-assigned by MLflow.

**MLflow connectivity-failure handling.** The orchestrator validates `MLFLOW_TRACKING_URI` connectivity at run startup (during the §6.3 lifecycle "after opening the run row, before fitting"). On failure, the run is marked `'failed'`, a `severity='fail'` `models.model_run_issues` row is written with `issue_type='mlflow_unavailable'`, and no fitting is attempted. The Postgres run row remains as the audit anchor.

### 6.11 Sleeve-aware ranking treatment

Sleeve assignments live on `universe.etfs.sleeve_id` (Section 2). 03c reads sleeve assignments where they are needed for ranking but does not modify them.

The two structural sleeve-aware questions handed forward by 03a §5.2 / 03b §5.1:

**Question A: Is combined score computed before or after sleeve-aware ranking?**

- Proposed default: **before** (combined score per `(etf, signal_date, horizon)` first; rank within sleeve second). See §6.8.
- Alternative: rank each component within sleeve first, then combine the within-sleeve ranks (e.g., sum of within-sleeve percentile ranks). The alternative produces different rankings in cross-sleeve comparisons.

**Question B: Is an ETF eligible across multiple sleeves ranked once or once per sleeve?**

- Proposed default: **once per sleeve** — appears in each eligible sleeve's ranking with the same `combined_score` but potentially different `rank_within_sleeve`. See §6.6 `models.combined_scores`.
- Alternative: rank once across the union of eligible sleeves combined (effectively a global rank with sleeve as a context label).

Both questions are **Open Questions for Approver** in §10. The Proposed defaults are not silent resolutions; they are the Builder's first proposal for the Approver to accept, modify, or replace.

### 6.12 `data_snapshot_id` linkage and reproducibility chain

Mirroring 03a §6.8 and 03b §6.7, 03c uses **transitive linkage** to `data_snapshot_id`:

- **Run-level (denormalized):** `models.model_runs.data_snapshot_id` is recorded redundantly for query convenience.
- **Run-level (canonical):** the canonical `data_snapshot_id` for a model run is reachable via `models.model_runs.feature_run_id → features.feature_runs.data_snapshot_id` AND via `models.model_runs.target_run_id → targets.target_runs.data_snapshot_id`. The two must equal each other and equal the denormalized field; the §6.3 orchestrator validation enforces this.
- **Row-level traceability:** every `models.model_predictions` row links to a `models.model_runs` row via composite FK (`model_run_id`, `model_set_version`); every `models.combined_scores` row links to a `models.scoring_runs` row, which itself links to `models.model_runs` rows via `models.scoring_run_models`.

**Single-source-of-truth invariant.** 03c does not store a separate `data_snapshot_id` on `models.model_predictions` or `models.combined_scores`. The chain is `model_predictions → model_runs → feature_runs / target_runs → ops.data_snapshots`. The denormalized `data_snapshot_id` on `models.model_runs` is asserted equal to the upstream values at run-open time and after that is read-only.

This satisfies the EW §7 reproducibility list at the schema-shape level: every model prediction is reachable to its data snapshot, code commit hash (via `models.model_runs.commit_hash`), config commit hash (via `models.model_runs.config_hash` for the model config plus the upstream feature/target run hashes for those configs), data snapshot/version identifier (via the chain), provider/dataset (via `ops.data_snapshots`), universe version (via `ops.data_snapshots.universe_version_label`), adjusted-price convention (via `ops.data_snapshots.adjusted_price_convention`), and MLflow run ID (via `models.model_runs.mlflow_run_id`).


---

## 7. Config dependencies

### 7.1 Files 03c reads

03c reads, but does not modify, the following config files:

- `config/features.yaml` (owned by 03a) — read for `feature_set_version` metadata and to validate that a feature run's set version is current/known.
- `config/targets.yaml` (owned by 03b) — read for `target_set_version` metadata, the active `horizons` list (Phase 1 locked: `{63, 126}`), and the locked classification threshold `θ = 0.0` (strict positive excess return; Approver-resolved per 03b §11.6 #2). 03c does **not** redefine `θ`; 03c consumes whatever target rows 03b emits under its own threshold contract.
- `config/universe.yaml` (owned by 02) — read for the active `benchmark_id` per ETF and for `sleeve_id` assignments. 03c does **not** read `universe.yaml` itself directly during model fitting; it reads the materialized join of `universe.etfs` (Section 2) and never bypasses the `feature_runs.status='succeeded'` chain.
- `.env` (not committed) — 03c directly reads only `MLFLOW_TRACKING_URI`. Application database access is configured by Section 2 and is consumed by 03c through the same connection settings — 03c introduces no new database environment variables. 03c does **not** need provider credentials at any point: the model-fitting orchestrator never imports from `quant_research_platform.providers` (verified by §8.2 CC-05) and never reads from any provider table directly.

### 7.2 File 03c owns: `config/model.yaml`

`config/model.yaml` is owned by 03c and is the single source of truth for model-fitting and combined-scoring parameters. The shape below is **Proposed default requiring approval**; all closed enumerations within it are also Proposed defaults requiring approval.

```yaml
# config/model.yaml — 03c-owned
# All model-layer parameters affecting training, prediction, calibration,
# combined-score formation, and sleeve-aware ranking.

model_set_version: "2026.04.0"          # bumped on any change to this file

# ---- Allowed model_kind values (closed enumeration; bumping requires 03c amendment) ----
allowed_model_kinds:
  - regression_excess_return_h63
  - regression_excess_return_h126
  - classification_outperformance_h63_uncalibrated
  - classification_outperformance_h63_calibrated
  - classification_outperformance_h126_uncalibrated
  - classification_outperformance_h126_calibrated

# ---- Allowed calibration_method values (closed enumeration) ----
allowed_calibration_methods:
  - none           # uncalibrated classifier
  - platt          # Platt scaling (Proposed Phase 1 default)
  - isotonic       # reserved; not enabled in Phase 1

# ---- Allowed rank_method values (closed enumeration; closes Section 2 pending_section_3 sentinel) ----
allowed_rank_methods:
  - benchmark_relative
  - absolute_with_context
  - peer_relative

# ---- Per-sleeve rank_method assignment (Proposed default requiring approval) ----
# Each entry must reference a sleeve_code present in universe.sleeves
# (locked Section 2 enumeration: BroadEquity, Sector, Thematic, BondTreasury,
# DiversifierHedge, REITRealAsset) AND a rank_method value present in
# allowed_rank_methods. See §6.7 / §10.5 / §10.6 for derivation from SDR Decision 5.
sleeve_rank_methods:
  BroadEquity:       benchmark_relative      # SDR Decision 5 #1: compare to SPY/VTI/IWM/IJR/QQQ
  Sector:            benchmark_relative      # SDR Decision 5 #2: primary comparison to SPY
  Thematic:          benchmark_relative      # SDR Decision 5 #3: theme-dependent benchmark via primary_benchmark_id
  BondTreasury:      benchmark_relative      # SDR Decision 5 #4: compare to bond-category benchmarks; absolute components reserved for 4-component formula activation
  DiversifierHedge:  absolute_with_context   # SDR Decision 5 #5: evaluate primarily by absolute opportunity/risk and hedge value;
                                             # SPY-relative return is context, not primary ranking target.
                                             # IMPORTANT: the current first-testable 2-component combined-score formula (§6.8) is
                                             # benchmark-relative and DOES NOT yet rank absolute_with_context ETFs. Until an
                                             # Approver-approved amendment adds the absolute / risk inputs (§10.6, §10.11),
                                             # DiversifierHedge ETFs produce NO models.combined_scores rows; one
                                             # severity='warning' row is written to models.scoring_run_issues per scoring run with
                                             # issue_type='rank_method_unsupported_in_phase1' listing the affected sleeve(s)
                                             # and ETF count.
  REITRealAsset:     peer_relative           # SDR Decision 5 #6: compare against REIT/real-estate peers

# ---- Training-data assembly parameters ----
training:
  min_training_rows: 1000               # Proposed default
  missing_data_rule: drop_row           # Proposed default; alternatives: 'mean_impute', 'reject'
  standardization: per_feature_zscore   # Proposed default; alternatives: 'none', 'robust_zscore'
  random_seed: 17                       # required; bumping requires model_set_version bump

# ---- Combined-score formula (first testable; Proposed default requiring approval) ----
combined_score:
  formula_version: "v0.1-2component"    # closed enum: 'v0.1-2component', 'v0.2-4component-reserved'
  components:
    predicted_excess_return:
      source_model_role: regression
      weight: 0.5                       # w_r
    calibrated_probability:
      source_model_role: classifier_calibrated
      weight: 0.5                       # w_p
    # 4-component reservation — disabled in Phase 1
    risk_score:
      enabled: false
      weight: 0.0
    trend_relative_strength:
      enabled: false
      weight: 0.0
  weight_constraint: must_sum_to_one    # validation: enabled weights must sum to 1.0 +/- 1e-6
  zscore_pool: per_signal_date_cross_section   # Proposed default
  rank_within_sleeve_method: dense_rank_descending  # Proposed default
  ranking_order: combined_score_then_rank_within_sleeve   # see §10 Open Question A

# ---- MLflow integration ----
mlflow:
  experiment_name_pattern: "{model_kind}"   # one experiment per model_kind
  run_name_pattern: "{model_set_version}--snapshot-{data_snapshot_id}--{started_at_utc}"
  required_tags:                            # closed set (matches §6.10)
    - data_snapshot_id
    - provider_name
    - provider_dataset_label
    - universe_config_hash
    - universe_version_label
    - adjusted_price_convention
    - commit_hash
    - config_hash
    - feature_run_id
    - feature_set_version
    - target_run_id
    - target_set_version
    - model_set_version
    - model_kind
    - random_seed
  serialization_format: joblib            # Implementation default

# ---- Model-state lifecycle (Phase 1) ----
model_state:
  initial_state_on_register: Paused        # Proposed default requiring approval (§11.5 A-PRP-08)
                                            # SDR Decision 12 names the four states but does not specify
                                            # the initial state on registration.
  approver_only_transitions: true          # Proposed default requiring approval (§11.5 A-PRP-10)
                                            # Phase 1 default; SDR Decision 12 does not explicitly forbid
                                            # all automated transitions in Phase 1.
  retired_is_terminal: true                # Proposed default requiring approval (§11.5 A-PRP-09)
                                            # SDR Decision 12 lists Retired as one of the four states
                                            # but does not specify terminality.
  active_warning_trigger_definition: open_question   # see §10.9 Open Question

# ---- Validation rules (enforced at orchestrator startup) ----
validation:
  reject_unknown_rank_method: true
  reject_unknown_model_kind: true
  reject_unknown_calibration_method: true
  reject_unknown_formula_version: true
  reject_sleeve_id_not_in_universe: true
  reject_weights_not_summing_to_one: true
  reject_min_training_rows_below_floor: 100   # absolute floor; below this is a config error
```

### 7.3 Validation rules (cross-cutting)

**Lifecycle alignment with §6.3.** Configuration validation follows the same two-phase pattern as 03a §6.3 / 03b §6.3 / 03c §6.3:

- **Phase 0 (pre-run-open).** If `config/model.yaml` is unreadable, malformed YAML, encoding-broken, or missing the keys the orchestrator needs to construct a run context — minimally `model_set_version` and the `mlflow` block — the orchestrator treats this as a pre-run fatal parse error, logs to stderr only, and does **not** open a `models.model_runs` row. No `models.model_run_issues` row is written (no `model_run_id` exists yet to FK against).
- **Phase 1 (post-run-open semantic validation).** Once `config/model.yaml` is parseable enough to identify `model_set_version` and the orchestrator can open a `models.model_runs` row with `status='running'`, every semantic validation rule below runs against the open run. Any failure marks the run `status='failed'`, populates `error_message` and `completed_at_utc`, and writes a `severity='fail'` row to `models.model_run_issues` with the appropriate canonical `issue_type` per §6.6. No `models.model_predictions` rows are written.

**Semantic validation rules (Phase 1; every failure is `severity='fail'`):**

1. `model_set_version` is present and is a non-empty string. *(In practice this is also Phase 0 because the orchestrator needs `model_set_version` to construct the run context; if it is missing or non-string the YAML cannot be used to open a run.)*
2. Every entry in `sleeve_rank_methods` keys a `sleeve_code` that exists in `universe.sleeves` (locked Section 2 closed enumeration). Failure → `issue_type='rank_method_unknown'` (sleeve-side variant, same canonical issue type since the failure mode is "the sleeve_rank_methods block references something the orchestrator cannot resolve to a closed-enum value").
3. Every entry in `sleeve_rank_methods` values a `rank_method` that exists in `allowed_rank_methods`. Failure → `issue_type='rank_method_unknown'`.
4. No `sleeve_code` present in `universe.sleeves` is missing from `sleeve_rank_methods` (forces explicit assignment for every active sleeve). Failure → `issue_type='rank_method_unknown'`.
5. No `universe.etfs.rank_method` value still equals the Section 2 sentinel `pending_section_3`. Failure → `issue_type='pending_section_3_sentinel'`.
6. `combined_score.formula_version` is in the closed enum. Failure → `issue_type='model_run_failed'` with `detail` naming the offending value.
7. Sum of `weight` over enabled components in `combined_score.components` is `1.0 +/- 1e-6`. Failure → `issue_type='model_run_failed'` with `detail` reporting the actual sum.
8. `training.min_training_rows >= validation.reject_min_training_rows_below_floor` (absolute floor; the proposed default 1000 is the recommended floor, but the absolute floor is 100 to catch degenerate configs). Failure → `issue_type='model_run_failed'`.
9. `training.random_seed` is present and is an integer. Failure → `issue_type='model_run_failed'`.
10. `mlflow.required_tags` matches the §6.10 closed set exactly (no additions, no omissions). Failure → `issue_type='model_run_failed'`.
11. No `model_kind` referenced in any registered `models.model_definitions` row is missing from `allowed_model_kinds`. Failure → `issue_type='feature_set_version_mismatch'` analogue (treated as a definition-vs-config mismatch; recorded as `issue_type='model_run_failed'` with the specific mismatch in `detail` because the canonical enum does not have a dedicated `model_kind_mismatch` entry — adding one would be a §6.6 enum amendment).
12. No `calibration_method` referenced in any registered `models.model_definitions` row is missing from `allowed_calibration_methods`. Failure → `issue_type='model_run_failed'` with `detail` analogous to rule 11.

Per the §6.3 closed list of run-level blocking conditions, rules 2 through 12 are the semantic-validation portion of condition 7 ("`config/model.yaml` semantic validation fails"). The orchestrator runs them sequentially after run-open and stops at the first failure.

### 7.4 Commit discipline

`config/model.yaml` is checked into version control. Every commit that modifies it must:

1. Bump `model_set_version` (an opaque string; convention is `YYYY.MM.PATCH` but the parser does not enforce it).
2. The `config_hash` recorded on `models.model_runs` is the SHA-256 of the canonicalized (ordered-key) YAML content; the orchestrator computes this at run-open.
3. Existing `models.model_runs` rows reference the historical `config_hash` they were fit under; this is immutable on the run row.

Bumping any of `random_seed`, `formula_version`, `sleeve_rank_methods`, `combined_score.components.*.weight`, `training.*` is a strategy-affecting change and per EW §3.3 requires Approver review. The Builder may not silently bump these.

### 7.5 Cross-config consistency

03c does **not** enforce that `config/features.yaml` and `config/targets.yaml` are mutually consistent — that is a 03a/03b responsibility and is enforced by their respective `*_run_issues` tables. 03c's only cross-config consistency obligation is:

- The `feature_set_version` recorded on `models.model_runs.feature_set_version` must match the `feature_set_version` recorded on the joined `features.feature_runs` row (composite FK enforces this).
- The `target_set_version` recorded on `models.model_runs.target_set_version` must match the `target_set_version` recorded on the joined `targets.target_runs` row (composite FK enforces this).
- Both `feature_runs.status` and `target_runs.status` must equal `'succeeded'` at training-data-assembly time (orchestrator validation, raises `issue_type='failed_feature_run_blocked'` or `issue_type='failed_target_run_blocked'` per the offending side and fails the run if not).


---

## 8. Required tests

03c required tests are specified at the **shape and intent** level (per EW §3.2, the spec does not contain test code). They are organized into per-component (§8.1), cross-cutting (§8.2), and data-contract (§8.3) groups.

### 8.1 Per-component tests

**Training-data assembly (§6.1):**

1. **TDA-01: Training-data assembly joins only successful feature and target runs.** Given two `features.feature_runs` rows for the same `feature_set_version` — one `'succeeded'` and one `'failed'` — and two `targets.target_runs` rows for the same `target_set_version` — one `'succeeded'` and one `'failed'` — the assembly query produces rows joined exclusively from the two `'succeeded'` runs.
2. **TDA-02: Failed feature runs are excluded.** Given only a `'failed'` feature run and a `'succeeded'` target run for matching versions, the assembly query produces zero rows and the orchestrator opens a `severity='fail'` `models.model_run_issues` row with `issue_type='failed_feature_run_blocked'`.
3. **TDA-03: Failed target runs are excluded.** Symmetric to TDA-02 with target run failed; orchestrator opens a `severity='fail'` `models.model_run_issues` row with `issue_type='failed_target_run_blocked'`.
4. **TDA-04: Non-succeeded upstream runs are not silently consumed.** Given an upstream `feature_runs` row with any value other than `'succeeded'` (i.e., `'running'` or `'failed'` per the locked 03a / 03b three-value status enum), the assembly query treats it as if it does not exist; the orchestrator raises `issue_type='failed_feature_run_blocked'` (or `'failed_target_run_blocked'` for the target side). The 03c canonical enum does not introduce a `'blocked'` status value of its own.
5. **TDA-05: Front-edge target truncation produces missing training labels without being treated as model failure.** Given a feature row at `as_of_date = T` for which the target table has no row at the same `as_of_date` for the active horizon (because `T + h` is beyond the snapshot's last available price date — see 03b §6.4 front-edge truncation), the assembly query produces zero training rows for `T` for that horizon, **and** the model run completes successfully with whatever training rows remain. No `models.model_run_issues` row is opened for this case.
6. **TDA-06: Feature/target version consistency is enforced.** The composite FKs on `models.model_runs` to `features.feature_runs(feature_run_id, feature_set_version)` and `targets.target_runs(target_run_id, target_set_version)` reject any insertion where the version recorded on `models.model_runs` does not match the version on the upstream run row.
7. **TDA-07: Snapshot consistency.** The `data_snapshot_id` reachable via `feature_run_id` and the `data_snapshot_id` reachable via `target_run_id` must equal each other and equal `models.model_runs.data_snapshot_id` (denormalized). The orchestrator verifies this at run-open and writes `issue_type='snapshot_mismatch'` `severity='fail'` if not.

**Baseline model fitting (§6.4):**

8. **MOD-01: Fit/predict shape consistency.** For every `model_kind`, given training input `X` of shape `(n_train, n_features)` and `y` of length `n_train`, the fitted model produces predictions of length `n_predict` for input of shape `(n_predict, n_features)`. Mismatched feature counts between fit and predict raise an error and write `issue_type='prediction_emission_failed'` per the canonical §6.6 enum.
9. **MOD-02: Deterministic reproducibility with same input and same seed.** Two runs of the same `model_kind` over the same training-data-assembly output, with the same `random_seed` and the same `config_hash`, produce identical fitted-model parameters bit-for-bit.
10. **MOD-03: Standardization parameters are recorded.** For every fitted model, the per-feature mean and standard-deviation parameters used for standardization (per the 03c default `per_feature_zscore`) are persisted as an MLflow artifact and are usable to standardize future prediction inputs.
11. **MOD-04: Fit fails gracefully on insufficient training data.** If the assembled training set has fewer than `training.min_training_rows` rows, the run is marked `'failed'` and a `severity='fail'` `models.model_run_issues` row with `issue_type='insufficient_training_data'` is written. No model artifact is persisted.

**Calibration pipeline (§6.5):**

12. **CAL-01: Calibration output probabilities are in [0, 1].** For every `classification_outperformance_*_calibrated` model run, every prediction emitted to `models.model_predictions.calibrated_probability` is in the closed interval `[0, 1]`.
13. **CAL-02: Calibrator is fit on a held-out fold.** The fold used to fit the calibrator does not overlap the fold used to fit the classifier. (Specific fold structure inherits from Section 4 once it locks; for current scope the test asserts the row-set inequality.)
14. **CAL-03: Uncalibrated and calibrated runs share the same upstream.** A `classification_outperformance_h{h}_calibrated` model run records a parent `classification_outperformance_h{h}_uncalibrated` `model_run_id`; the FK is non-null and points to a `'succeeded'` uncalibrated run.
15. **CAL-04: Calibration without a classifier fails.** Attempting to register a `*_calibrated` model definition without a corresponding `*_uncalibrated` model definition is rejected at config-validation time.

**MLflow integration (§6.10):**

16. **MLF-01: MLflow run metadata links to feature_run_id and target_run_id.** Every successful `models.model_runs` row has a non-null `mlflow_run_id`, and the MLflow run with that ID has both `feature_run_id` and `target_run_id` tags whose values match the corresponding columns on `models.model_runs`.
17. **MLF-02: MLflow tag completeness.** Every successful `models.model_runs` row's MLflow run has every tag in the §6.10 closed 15-tag set; missing or extra tags are rejected by the orchestrator.
18. **MLF-03: MLflow connectivity-failure handling.** Simulating an MLflow tracking-server outage at run-open causes the run to be marked `'failed'` with `issue_type='mlflow_unavailable'`; no fitting is attempted; the Postgres run row remains as the audit anchor.
19. **MLF-04: Joblib serialization round-trip.** A model fit, persisted as a joblib artifact, and reloaded from MLflow produces predictions identical to the in-memory model bit-for-bit on the same input.

**Combined-score formation (§6.8):**

20. **CS-01: Combined score uses only successful component model runs.** A `models.scoring_runs` row may consume only `models.model_runs` rows whose `status='succeeded'`. The scoring orchestrator validates this before writing any `models.combined_scores` rows: for every `model_run_id` referenced by `models.scoring_run_models` for the scoring run, the corresponding `models.model_runs.status` must equal `'succeeded'`. Failure causes the scoring run to be marked `status='failed'` with a `severity='fail'` `models.scoring_run_issues` row written (`issue_type='scoring_run_failed'`, `detail` naming the offending model_run_id and its actual status from the closed three-value enum `('running', 'succeeded', 'failed')`). FKs enforce existence of every referenced `model_run_id` and the composite `(model_run_id, model_set_version)` integrity; orchestrator validation enforces the terminal-success status (a future Approver-approved DB trigger could enforce this at the database level, but Phase 1 03c does not propose one).
21. **CS-02: Z-scoring is per-signal-date cross-section.** The standardization for each component happens within `(signal_date, horizon)`, not across horizons or across dates.
22. **CS-03: Weight sum constraint.** Loading a `config/model.yaml` whose enabled `combined_score.components` weights do not sum to `1.0 +/- 1e-6` is rejected at config-validation time.

**Sleeve-aware ranking (§6.7, §6.11):**

23. **RNK-01: `config/model.yaml` validation rejects unknown rank_method values.** Loading a `config/model.yaml` containing a `sleeve_rank_methods` entry whose value is not in `allowed_rank_methods` is rejected at config-validation time.
24. **RNK-02: Every active sleeve has an explicit rank_method.** Loading a `config/model.yaml` where any `sleeve_id` present in `universe.etfs` is missing from `sleeve_rank_methods` is rejected at config-validation time. (This closes the Section 2 `pending_section_3` sentinel obligation.)
25. **RNK-03: ETF in multiple sleeves is ranked according to the §10 Question B resolution.** Current default: ranked once per eligible sleeve (one row per `(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)` in `models.combined_scores`).
26. **RNK-04: Rank order is within sleeve.** `models.combined_scores.rank_within_sleeve` is dense-rank-descending of `combined_score` within `(scoring_run_id, signal_date, horizon, sleeve_id)`. Ties resolve deterministically (proposed default: by `etf_id` ascending).

**Model-state lifecycle (§6.9):**

27. **STA-01: Initial state on register is `Paused`.** Newly inserted `models.model_versions` rows have `state='Paused'`; the CHECK constraint allows this without requiring `approved_at_utc` / `approved_by`.
28. **STA-02: Active state requires approval metadata.** A row with `state='Active'` and either `approved_at_utc` or `approved_by` null is rejected by the CHECK constraint.
29. **STA-03: Retired is terminal.** A `models.model_state_history` row recording a transition from `Retired` to any other state is rejected.
30. **STA-04: All transitions in Phase 1 are Approver-only.** A `models.model_state_history` row whose `acting_user` does not match the `approved_by` on the resulting `models.model_versions` row is rejected. (Phase 1 only; relaxed in later sections per SDR Decision 12.)

### 8.2 Cross-cutting tests

31. **CC-01: T-1 inheritance.** All training-data assembly uses features at `as_of_date = T-1` per 03a §6.1; tests verify that no feature value emitted to a model from `as_of_date = T` is present in the training-data assembly for `signal_date = T`.
32. **CC-02: Convention B inheritance.** Targets joined to features carry `entry_date` and `exit_date` per 03b Convention B; 03c does not redefine these and tests verify that `models.model_runs` does not store its own copies of `entry_date` / `exit_date`.
33. **CC-03: No write to ops.data_quality_exceptions.** A static check (e.g., `grep` over the `models/` package and a database-trigger or role-grant test) verifies no insert/update statement targeting `ops.data_quality_exceptions` is present in 03c-owned code paths.
34. **CC-04: No write to features.\*, targets.\*, universe.\*, prices.\*, or ops.\*.** Static check: 03c-owned code paths contain no `INSERT`, `UPDATE`, `DELETE`, or `TRUNCATE` against these schemas. The `models` schema is the only schema 03c writes.
35. **CC-05: No provider imports from `models/`.** Static check: the `models/` Python package contains no `import` referencing `data.providers.*` or any external-data-provider SDK. (Provider code is owned by Section 2.)
36. **CC-06: No live broker dependency or broker SDK reference.** Static check: 03c-owned code contains no `import` of any broker SDK (`alpaca`, `ibkr`, `tradier`, etc.) and no reference to live-trading endpoints.
37. **CC-07: No fallback to secondary_benchmark_id.** Static check: 03c-owned code does not reference `secondary_benchmark_id` in any data path. (Secondary benchmark is read-only for context labels only, per SDR Decision 17.)
38. **CC-08: No modification to `features.feature_run_issues` or `targets.target_run_issues` enumerations.** Schema-level test: the closed enums for these tables match exactly what 03a and 03b specified at lock; 03c migrations do not ALTER them.
39. **CC-09: No secrets-in-models.** Static check: no API key, password, connection string, or `.env` content is committed under `models/` or `config/model.yaml`.
40. **CC-10: `feature_runs.status` and `target_runs.status` are read in every assembly query.** Code-grep / query-plan test: every SQL or ORM query that joins `features.feature_values` includes a `feature_runs.status='succeeded'` predicate; every join to `targets.target_values` includes `target_runs.status='succeeded'`.

### 8.3 Data-contract tests

41. **DC-01: Composite FKs reject mismatched run/version pairs.** Given a `models.model_runs` row attempting to reference `(feature_run_id=X, feature_set_version='A')` while the parent has `feature_set_version='B'`, the insert is rejected.
42. **DC-02: `models.model_run_issues.issue_type` enum is closed.** Inserting a value not in the closed enum defined in §6.6 is rejected at the CHECK constraint level.
43. **DC-03: `models.scoring_run_models.role` enum is closed.** Inserting a value not in the §6.6 closed enum is rejected.
44. **DC-04: `models.model_versions.mlflow_model_uri` is set on every `Active` row.** A row with `state='Active'` and `mlflow_model_uri` null is rejected by a CHECK constraint.
45. **DC-05: `models.model_predictions` row count equals feature-row count for the run.** For a successful run, the count of `models.model_predictions` rows for `(model_run_id)` equals the count of feature rows in the snapshot universe at the run's `signal_date` set, regardless of whether targets exist (front-edge predictions are emitted; only training is truncated). See §6.2.
46. **DC-06: `models.combined_scores` is unique on `(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)`.** Database-level UNIQUE constraint test.
47. **DC-07: `models.scoring_run_issues.issue_type` enum is closed.** Inserting a value not in the closed enum defined in §6.6 (the disjoint scoring-run enumeration) is rejected at the CHECK constraint level.
48. **DC-08: `models.scoring_run_issues.severity` enum is closed.** Inserting a value not in `('warning', 'fail')` is rejected at the CHECK constraint level. (Parallel to the analogous test for `models.model_run_issues.severity`, which DC-02 implicitly covers via the same constraint pattern.)
49. **DC-09: `models.model_predictions.prediction_context` enum is closed.** Inserting a value not in `('in_sample_diagnostic', 'walk_forward_oos', 'current_scoring')` per §6.2 is rejected at the CHECK constraint level.

### 8.4 Tests deferred to Section 4 / 5 / 6

The following tests are **not** owned by 03c and are listed here only to make the seam explicit. They will be specified by the section that owns them:

- Walk-forward fold structure correctness — Section 4.
- Purge / embargo enforcement around target horizons — Section 4.
- Backtest reproducibility under same `data_snapshot_id` — Section 4.
- Out-of-sample-only consumption rule for `prediction_context='walk_forward_oos'` rows — Section 4.
- Attribution decomposition correctness — Section 4.
- Combined-score downstream consumption tests (signal-to-portfolio mapping) — Section 5.
- Paper portfolio state correctness, P&L computation, position lifecycle — Section 5.
- Broker-neutral order intent generation — Section 5.
- Transaction-cost application — Section 5.
- UI rendering and read-only access patterns — Section 6.
- Live-trading guardrails — out of scope for Phase 1.


---

## 9. Edge cases and failure behavior

### 9.1 Upstream-run failures

**Failed feature run.** If the most recent `features.feature_runs` row for the active `feature_set_version` has `status='failed'`, training-data assembly produces zero rows. The orchestrator opens a `models.model_runs` row with `status='running'` (per the §6.3 open-run-before-validation lifecycle), then on detection writes a `severity='fail'` `models.model_run_issues` row with `issue_type='failed_feature_run_blocked'` and updates the `models.model_runs` row to `status='failed'`. No model artifact is fit or persisted.

**Failed target run.** Symmetric to failed feature run; `issue_type='failed_target_run_blocked'`.

**Failed run for a non-current set version.** If the most recent run for the active `feature_set_version` is `'succeeded'` but a stale run for an obsolete `feature_set_version` is `'failed'`, the orchestrator ignores the stale failure and proceeds. (The composite-FK and `feature_set_version` filter on the assembly query handle this.)

**Upstream run with `status != 'succeeded'` (any reason).** The 03c orchestrator only consumes feature/target runs whose `status='succeeded'`. Any other status — `'running'` (upstream still in flight), `'failed'`, or any future status value 03a / 03b might add via amendment — is treated as not-succeeded for consumption purposes, and the 03c run fails with `issue_type='failed_feature_run_blocked'` or `issue_type='failed_target_run_blocked'` accordingly. 03c does **not** wait on a `'running'` upstream run; it does **not** synthesize a `'pending'` or `'blocked'` status of its own. (The 03a §6.3 / 03b §6.3 closed status enum is `('running', 'succeeded', 'failed')`; 03c relies on that and does not introduce additional values.) **Implementation default:** when 03c starts and finds the upstream still running, the operator re-runs after upstream completes; no automatic wait.

**Partial upstream-ingestion dependency backstop.** Per 03a §6.3 and 03b §6.3, partial ingestion runs covering the snapshot's price data cause the upstream feature/target run to be marked `'failed'` with the appropriate `partial_*_blocked` issue type. 03c never sees a "succeeded but with a partial dependency" upstream run. As a defensive backstop in case 03a / 03b's filter discipline ever loosens, the 03c canonical enum (§6.6) reserves `issue_type='partial_feature_run_blocked'` and `issue_type='partial_target_run_blocked'`. These are not expected to fire under current 03a / 03b LOCKED behavior.

### 9.2 Snapshot-chain anomalies

**`data_snapshot_id` mismatch between feature_run and target_run.** At run-open, the orchestrator reads `features.feature_runs.data_snapshot_id` and `targets.target_runs.data_snapshot_id` for the chosen run pair. If they differ, the run is marked `'failed'` with `issue_type='snapshot_mismatch'` `severity='fail'`. The denormalized `models.model_runs.data_snapshot_id` is not written.

**Snapshot ID present on upstream but absent from `ops.data_snapshots`.** Treated as a referential-integrity violation; should be impossible if upstream FKs are intact, but if it occurs the run fails with `issue_type='snapshot_mismatch'` `severity='fail'` (the canonical enum entry covers any snapshot-chain inconsistency, not only feature/target snapshot disagreement; see §6.6 enum row).

**Snapshot version label change between fit-time and predict-time.** Predict-time always uses the snapshot recorded on the model run's parent `model_version` row, not the current snapshot. If a downstream consumer attempts to use a different snapshot for prediction, it must open a new `models.model_runs` row (i.e., refit) — there is no "predict using a different snapshot than fit" code path.

### 9.3 Training-data anomalies

**Insufficient training rows.** If the assembled training set has fewer than `training.min_training_rows` rows after the `INNER JOIN`, the run is marked `'failed'` with `issue_type='insufficient_training_data'` `severity='fail'`. No artifact is persisted. (See §8.1 MOD-04.)

**All-null training column.** If a feature column or the target column for the active horizon has zero non-null values across the entire assembled training set, the run is marked `'failed'` with `issue_type='all_null_training_column'` `severity='fail'`. The canonical enum entry covers both the target-side case (e.g., a 03b run that succeeded but emitted all-null target rows for a horizon) and the feature-side case (e.g., a 03a-side calculator bug that emitted a feature column with no non-null values).

**Front-edge target truncation.** Per 03b §6.4 and §6.5, target rows are simply absent for `signal_date > T_max - h` where `T_max` is the snapshot's last available price date. The `INNER JOIN` in §6.1 silently excludes those feature rows from the training set. This is **not** a failure case; the run completes normally with whatever rows remain. The two-bucket null-vs-no-row taxonomy is inherited from 03b and is **not** redefined here. See §8.1 TDA-05.

**ETF eligibility flips during training window.** If `universe.etfs.is_active` flipped between true and false during the training window, the snapshot used for training contains rows from the snapshot date only; 03c does not look up "current" `is_active`. Rows are eligible/ineligible per the snapshot's view. (Per Section 2 reproducibility chain.)

**Single-class training set for a classifier.** If the binary outperformance target is all-zeros or all-ones in the assembled training set, the classifier cannot be fit. The run is marked `'failed'` with `issue_type='single_class_training_set'` `severity='fail'`. (Distinct from the broader `all_null_training_column` case, which covers any column with no non-null values across all rows.)

**Calibrator degenerate.** If the held-out calibration fold has fewer than a minimum row count (Implementation default: 100) or only a single class, the calibrator cannot be fit. The run is marked `'failed'` with `issue_type='calibration_failed'` `severity='fail'` (the canonical enum entry covers any cause of calibrator-fit failure; the more granular `calibration_fold_degenerate` value considered during drafting is folded into `calibration_failed`). The parent uncalibrated classifier run remains `'succeeded'`.

### 9.4 Configuration anomalies

All configuration anomalies below assume `config/model.yaml` is parseable enough for the orchestrator to open a `models.model_runs` row with `status='running'`. Anomalies that prevent parse (malformed YAML, missing `model_set_version`, encoding-broken file) are pre-run fatal parse errors per §6.3 / §7.3 — they are logged to stderr only and no `models.model_runs` row is opened.

**Unknown `rank_method` in `config/model.yaml`.** Caught at semantic-validation time after run-open (§7.3 rules 2–4). The run is marked `status='failed'` and a `severity='fail'` `models.model_run_issues` row with `issue_type='rank_method_unknown'` is written. No `models.model_predictions` rows are written.

**Sleeve in `universe.sleeves` but missing from `sleeve_rank_methods`.** Caught at semantic-validation time (§7.3 rule 4). Same lifecycle as above; `issue_type='rank_method_unknown'`. (This is one of the `pending_section_3` sentinel-closure mechanisms.)

**Sentinel `pending_section_3` still present in `universe.yaml` at 03c run-time.** Caught at semantic-validation time (§7.3 rule 5). The run is marked `status='failed'` and a `severity='fail'` `models.model_run_issues` row with `issue_type='pending_section_3_sentinel'` is written, with `detail` naming the offending ETF tickers. The Approver is responsible for retiring the sentinel via a `universe.yaml` commit (Section 2 owns that file); 03c does not modify `universe.yaml`. (See §10.18.)

**Weight sum mismatch in combined-score components.** Caught at semantic-validation time (§7.3 rule 7). The run is marked `status='failed'` and a `severity='fail'` `models.model_run_issues` row with `issue_type='model_run_failed'` is written, `detail` reporting the actual sum.

**Bumped `random_seed` without `model_set_version` bump.** Caught by code review and EW §3.3 commit discipline; not enforced by the orchestrator at startup (the orchestrator records both, and a downstream auditor catches it). **Open Question:** whether to enforce this mechanically (proposed default: not enforced; rely on EW §3.3 review).

### 9.5 MLflow anomalies

**MLflow tracking server unreachable at run-open.** Run is marked `'failed'` with `issue_type='mlflow_unavailable'` `severity='fail'`. No fitting is attempted. Postgres run row is the audit anchor. (See §8.1 MLF-03.)

**MLflow tracking server unreachable mid-run.** If MLflow becomes unreachable after fitting has started but before metric/artifact logging completes, the orchestrator retries logging up to a fixed count (Implementation default: 3 retries with exponential backoff). On final failure, the run is marked `'failed'` with `issue_type='mlflow_logging_partial'` `severity='fail'`. The fitted-model artifact is **not** persisted to MLflow but the Postgres run row remains as the audit anchor. The failed-but-fit model is **not** loaded for any downstream prediction (a `'failed'` run is invisible to scoring per §6.6 FK constraint).

**MLflow registered-model promotion fails.** Promoting a `models.model_versions` row to MLflow's registered-model registry can fail (e.g., name already taken by a stale entry). The promotion writes to `models.model_versions.mlflow_model_uri` only after MLflow confirms registration; on failure, the `models.model_versions` row is not inserted. The Approver is informed via standard error logging. (No `models.model_run_issues` row is written for this case because no `models.model_runs` is in flight.)

### 9.6 Model-state lifecycle anomalies

**Attempt to register an `Active` model without approval metadata.** Rejected by the §6.6 CHECK constraint. (See §8.1 STA-02.)

**Attempt to transition out of `Retired`.** Rejected by application logic (the orchestrator's state-transition validator) and tested by STA-03. The CHECK constraint on `models.model_state_history` could enforce this, but the proposed default is application-level enforcement only — flagged in §10.

**Two `Active` versions for the same `model_kind` simultaneously.** Per §6.6, `models.model_versions` has a partial unique index on `(model_kind) WHERE state='Active'`. Insertion of a second Active row for the same `model_kind` is rejected at the database level.

**`Active` model whose underlying `model_run` is later marked `'failed'`.** Should be impossible because runs are immutable after terminal state, but if it occurs (e.g., manual data correction), the `models.model_versions` row is not auto-demoted. The Approver must explicitly transition the version. (Phase 1 lifecycle is Approver-only.)

### 9.7 Combined-score / scoring anomalies

**Scoring run references models with mismatched `data_snapshot_id`.** A `models.scoring_runs` row joins multiple `models.model_runs`; if those runs have different `data_snapshot_id` values, the scoring run is rejected with `issue_type='cross_model_snapshot_mismatch'` `severity='fail'` written to **`models.scoring_run_issues`** (the table per §6.6). The corresponding `models.scoring_runs.status` is updated to `'failed'`. No `models.combined_scores` rows are written for that scoring run.

**Cross-sectional z-scoring with a single eligible ETF.** If only one ETF is eligible at `(signal_date, horizon)`, z-scoring produces a degenerate value (mean=value, std=0). The orchestrator detects `n_eligible <= 1` per signal-date and writes a `severity='warning'` row to **`models.scoring_run_issues`** with `issue_type='degenerate_cross_section'`; the combined score for that single ETF is recorded as 0.0 and `rank_within_sleeve` is recorded as 1. The scoring run completes with `status='succeeded'`; downstream consumers (Section 5 portfolio rules) may apply their own filtering.

**Empty sleeve at signal date.** If a sleeve has zero eligible ETFs at `(signal_date, horizon)`, no `models.combined_scores` rows are emitted for that sleeve at that date. This is **not** a failure case; it is the natural absence pattern from 03b §6.5.

### 9.8 Sentinel-closure obligations from Section 2

**`universe.etfs.rank_method = 'pending_section_3'`.** Section 2 §6.6 introduced this sentinel as a placeholder pending 03c. The 03c-owned closure mechanism is:

1. `config/model.yaml` enumerates `allowed_rank_methods` as a closed 3-value set.
2. `config/model.yaml` enumerates `sleeve_rank_methods` requiring every active `sleeve_id` to map to a value in `allowed_rank_methods`.
3. The Section 2 sentinel `'pending_section_3'` is removed from any future `universe.yaml` migration that ships alongside 03c lock; this is a Section 2 / Section 7 concern (migration ordering) and is not implemented in 03c. 03c only declares the sentinel-replacement enumeration and rejects the sentinel at config-validation time.

This is the structural sense in which 03c "closes the obligation": after 03c lock, Section 2's pending sentinel becomes resolvable by an Approver-driven `universe.yaml` migration with no further engineering-spec ambiguity.


---

## 10. Open questions

The following items are explicitly raised for the Approver. Each has a Status (`Open` or `Open with Proposed Default`), a brief restatement, the Builder's proposal (if any), and the alternatives the Approver might choose. Per the prompt, no item below has been silently resolved; each Proposed Default is recorded in §11 as a "Proposed default requiring approval" assumption.

### 10.1 Phase 1 baseline model forms

**Status:** Open with Proposed Default.

**Question.** What model forms are the canonical Phase 1 baselines per SDR Decisions 6 and 11?

**Proposed default.** Two paired baselines: ridge regression for predicted excess return at horizons `h63` and `h126` (per SDR Decision 6 horizon list), and logistic regression for outperformance probability at the same horizons. Both use cross-sectionally z-scored features with per-feature mean/std persisted as MLflow artifacts. See §6.4.

**Alternatives.** Linear regression without ridge (no L2 penalty), Lasso, ElasticNet, gradient-boosted trees, neural network. Each alternative changes calibration behavior and reproducibility constraints. Phase 1 SDR explicitly de-scopes ML complexity beyond a calibrated linear baseline; the proposed default reflects that.

### 10.2 Calibration method choice

**Status:** Open with Proposed Default.

**Question.** Which calibration method is canonical per SDR Decision 7?

**Proposed default.** Platt scaling. Fit on a held-out fold disjoint from the classifier's training fold (specific fold structure inherits from Section 4 once it locks).

**Alternatives.** Isotonic regression (more flexible but requires more held-out data and is less stable on small samples); none (uncalibrated probabilities exposed directly). Isotonic is reserved in the `allowed_calibration_methods` enum but not enabled in Phase 1.

### 10.3 First testable combined-score formula

**Status:** Open with Proposed Default.

**Question.** What is the first testable combined-score formula per SDR Decision 6?

**Proposed default.** Two-component, equal-weighted:

```
combined_score = w_r * z(predicted_excess_return) + w_p * z(calibrated_probability)
                 with w_r = w_p = 0.5
```

Z-scoring is per `(signal_date, horizon)` cross-section. See §6.8.

**Alternatives.** Four-component formula (adding `risk_score` and `trend_relative_strength`); unequal weights (e.g., `w_r=0.7`, `w_p=0.3`); product instead of sum; rank-based (sum of percentile ranks instead of z-scores). The four-component variant is reserved in `config/model.yaml` but disabled. See also §10.11 and §10.12.

### 10.4 Allowed `rank_method` values

**Status:** Open with Proposed Default.

**Question.** What is the closed set of allowed `rank_method` values that closes the Section 2 `pending_section_3` sentinel?

**Proposed default.** Three values: `benchmark_relative`, `absolute_with_context`, `peer_relative`. See §6.7.

**Alternatives.** Two values (drop `absolute_with_context` and treat DiversifierHedge as `benchmark_relative` for now); five or more values (add `risk_adjusted`, `regime_conditional`, etc.); leave the enumeration extensible per-sleeve. The Builder recommends a small closed set for Phase 1 to make the validator definitive.

### 10.5 Per-sleeve `rank_method` assignment

**Status:** Open with Proposed Default.

**Question.** Which `rank_method` value applies to each Phase 1 sleeve from SDR Decision 5, as cashed out in the locked Section 2 closed enumeration `{BroadEquity, Sector, Thematic, BondTreasury, DiversifierHedge, REITRealAsset}`?

**Proposed default.**

| Sleeve (locked Section 2 code) | Proposed `rank_method` | SDR Decision 5 derivation |
|---|---|---|
| `BroadEquity` | `benchmark_relative` | "compare broad equity ETFs to SPY/VTI, small caps to IWM/IJR, growth/Nasdaq to QQQ" |
| `Sector` | `benchmark_relative` | "primary comparison to SPY, optional peer comparison to other sectors" |
| `Thematic` | `benchmark_relative` | "benchmark depends on theme" — handled via per-ETF `primary_benchmark_id` |
| `BondTreasury` | `benchmark_relative` | "compare to bond-category benchmarks" — bond benchmarks supply the comparison; the additional Decision 5 language ("evaluate absolute trend, volatility, drawdown, and rate regime") is reserved for 4-component formula activation (§10.11, §10.12), not Phase 1 current scope |
| `DiversifierHedge` | `absolute_with_context` | "evaluate primarily by absolute opportunity/risk and hedge value; SPY-relative return may be shown as context, not primary ranking target" — the only sleeve Decision 5 explicitly removes from benchmark-relative ranking. See §10.6 for the consequence under the current first-testable formula. |
| `REITRealAsset` | `peer_relative` | "compare against REIT/real-estate peers; optionally compare to SPY as opportunity-cost context" |

**Alternatives.** Several per-sleeve permutations are conceivable, but the proposed mapping is the direct read of SDR Decision 5's per-sleeve language. The most consequential question — the consequence for `DiversifierHedge` under the current first-testable formula — is broken out as §10.6.

### 10.6 DiversifierHedge under the current first-testable formula

**Status:** Open with Proposed Default. (Identifies the only structural gap between the SDR-consistent `rank_method` mapping in §10.5 and the current first-testable combined-score formula in §6.8 / §10.3.)

**Setup.** Per §10.5, `DiversifierHedge` is mapped to `absolute_with_context` because SDR Decision 5 explicitly says diversifier / hedge ETFs are evaluated "primarily by absolute opportunity / risk and hedge value; SPY-relative return may be shown as context, not primary ranking target." This is the only sleeve Decision 5 removes from benchmark-relative ranking.

**The gap.** The current first-testable two-component combined-score formula (§6.8) operates on (a) predicted excess return from `regression_excess_return_h{63,126}` and (b) calibrated probability of outperformance from `classification_outperformance_h{63,126}_calibrated`. Both are **benchmark-relative** by 03b's locked target definitions: `excess_return_h(e, T) = return_h(e, T) - return_h(b, T)` (03b §6.4) and `outperformance_h(e, T) = 1 if excess_return_h(e, T) > 0 else 0` (03b §6.4 with locked threshold `θ = 0.0` per 03b §11.6 #2). The formula has no absolute-return input and no risk input, so it does not produce a meaningful ranking signal for ETFs whose `rank_method` is `absolute_with_context`.

**Proposed default for current 03c scope.**

1. **Do not silently re-map `DiversifierHedge` to `benchmark_relative`.** That would contradict SDR Decision 5 and would put GLD, SLV, DBC, USO, UUP into a ranking treatment Decision 5 explicitly rejects.
2. **Do not propose a 03b target amendment in this section.** A new "absolute forward return" or "absolute risk" target family would be a strategy-affecting target change owned by 03b (and ultimately driven by Approver direction), not a 03c surgical revision in this section.
3. **For current 03c scope, ETFs whose effective `rank_method` resolves to `absolute_with_context` produce no `models.combined_scores` rows.** When a `models.scoring_runs` row is opened, the orchestrator (a) computes combined scores for ETFs whose `rank_method` is `benchmark_relative` or `peer_relative` exactly as §6.8 specifies, (b) skips ETFs whose `rank_method` is `absolute_with_context`, and (c) writes one `severity='warning'` row to `models.scoring_run_issues` with `issue_type='rank_method_unsupported_in_phase1'` listing the affected sleeve(s) and ETF count. The skipped ETFs are absent from `models.combined_scores`, parallel to the eligibility-row omission discipline 03a / 03b apply elsewhere.
4. **Activation requires an Approver-approved amendment** that (a) extends the `model_kind` enumeration with absolute-trend regression and absolute-gain classification baselines (or an equivalent absolute-return + risk decomposition), (b) extends the §6.8 combined-score formula to consume those new components when `rank_method = 'absolute_with_context'`, and (c) updates `config/model.yaml` accordingly. The amendment is itself open (no draft path proposed in this section).

**Alternatives the Approver may direct instead.**

- **Path X (Builder's proposed default — recorded above):** keep `absolute_with_context` SDR-aligned in this section; emit no rows for `DiversifierHedge`; record a warning per scoring run; defer activation to a future amendment.
- **Path Y:** explicitly de-scope `DiversifierHedge` from Phase 1 ranking until the absolute formula lands; sleeve membership remains in `universe.etfs` for portfolio-side context use only. (Cleaner than Path X but requires Approver direction; the §6.8 / §6.7 mechanics are otherwise identical.)
- **Path Z:** authorize a 03b target amendment to add the absolute-forward-return / absolute-risk family alongside excess-return / outperformance, then re-issue 03c to consume them. (Largest scope; not requested in current scope.)

**The Builder is not silently choosing among Path X / Y / Z.** Path X is the proposed default. The choice is Approver-resolvable; this section records the gap honestly without weakening SDR Decision 5.

### 10.7 Combined-score / sleeve-rank ordering

**Status:** Open with Proposed Default.

**Question.** Is the combined score computed first (over the cross-section of all eligible ETFs at a signal date) and then ranked within sleeve, or is each component first ranked within sleeve and the within-sleeve ranks combined?

**Proposed default.** **Compute combined score first (cross-sectional z-score across all eligible ETFs at a signal date), then rank within sleeve.** See §6.8 and §6.11 Question A.

**Alternatives.** Within-sleeve z-scoring of each component, then combine. The two methods produce different rankings whenever an ETF's cross-sectional z-score differs from its within-sleeve z-score (which is essentially always).

### 10.8 ETF eligible across multiple sleeves

**Status:** Open with Proposed Default.

**Question.** When an ETF is eligible in more than one sleeve, is it ranked once (with sleeve as a context label) or once per sleeve?

**Proposed default.** **Ranked once per sleeve** — appears in `models.combined_scores` with one row per `(etf_id, signal_date, horizon, sleeve_id)`, sharing `combined_score` across rows but with sleeve-specific `rank_within_sleeve`. See §6.11 Question B.

**Alternatives.** Single global ranking with sleeve as a join-time context label (no per-sleeve duplication). Resolution affects the unique-key shape of `models.combined_scores`.

### 10.9 Model-state lifecycle: Active → Warning trigger

**Status:** Open. (No proposed default.)

**Question.** What conditions cause a `models.model_versions.state` transition from `Active` to `Warning`? Per SDR Decision 12, Warning is a "concerning but not yet failed" state; the trigger conditions are not specified.

**Candidate triggers (illustrative, not exhaustive).**

- Realized prediction error exceeds a threshold over a rolling window.
- Calibration reliability drift detected by a held-out fold.
- A monitoring run scheduled via 03c's orchestration produces a regression in a tracked metric.

**Proposed paths.**

- **Path A:** Phase 1 leaves the trigger undefined and Approver-only; the Approver manually transitions a model to `Warning` based on judgment. (Simplest; defers to a later spec section.)
- **Path B:** Phase 1 defines a single mechanical trigger (e.g., out-of-sample R^2 below threshold) and 03c orchestration writes `Warning` automatically.

The Builder recommends Path A for current scope because mechanical triggers introduce dependencies on a monitoring layer not yet specified. Phase 1's SDR Decision 12 does not require automation.

### 10.10 Model-state lifecycle: Retired terminal enforcement

**Status:** Open with Proposed Default.

**Question.** Is the "Retired is terminal" rule enforced at the database CHECK-constraint level or only at the application level?

**Proposed default.** **Application level only** in Phase 1, via the orchestrator's state-transition validator. A CHECK constraint on `models.model_state_history` could enforce this but would require a stored procedure or trigger; the Builder proposes deferring database-level enforcement until a state-machine generalization in a later section.

**Alternatives.** Enforce at the database level via a trigger that rejects insertion of any `model_state_history` row whose `from_state='Retired'`. Stronger guarantee; more migration complexity.

### 10.11 `risk_score` definition (for 4-component combined-score reservation)

**Status:** Open. (Reserved in config; not active in Phase 1.)

**Question.** If the 4-component combined-score formula is later activated, what is the canonical `risk_score` definition? Candidates: realized volatility, downside deviation, max drawdown over a window, factor-loading-derived risk metric.

**Phase 1 disposition.** Disabled. The `risk_score` slot is present in `config/model.yaml` with `enabled: false` and `weight: 0.0`. Activation requires an explicit Approver decision and an 03c (or successor section) amendment.

### 10.12 `trend_relative_strength` definition (for 4-component combined-score reservation)

**Status:** Open. (Reserved in config; not active in Phase 1.)

**Question.** If the 4-component combined-score formula is later activated, what is the canonical `trend_relative_strength` definition? Candidates: 12-1 momentum, 6-month relative-strength rank, dual-moving-average crossover indicator.

**Phase 1 disposition.** Disabled. Same handling as `risk_score`.

### 10.13 MLflow experiment / run naming convention

**Status:** Open with Proposed Default.

**Question.** What is the canonical MLflow experiment and run naming convention?

**Proposed default.**

- Experiment per `model_kind`. Experiment name = `model_kind` string (e.g., `regression_excess_return_h63`).
- Run name = `{model_set_version}--snapshot-{data_snapshot_id}--{started_at_utc:%Y%m%dT%H%M%SZ}`.
- Registered-model name = `model_kind` string; version auto-assigned by MLflow.

See §6.10.

**Alternatives.** Experiment per `(model_kind, sleeve_id)` (would require per-sleeve fits, which Phase 1 does not do); experiment per Phase / project (single MLflow experiment with all runs); date-bucketed experiments (one per day or month). The proposed default keeps experiment cardinality bounded (one per `model_kind`, finite by enum) and run cardinality unbounded but timestamped.

### 10.14 `models.*` table design

**Status:** Open with Proposed Default.

**Question.** What is the Phase 1 `models.*` schema?

**Proposed default.** **Ten tables**: `models.model_definitions`, `models.model_runs`, `models.model_predictions`, `models.scoring_runs`, `models.scoring_run_models`, `models.combined_scores`, `models.model_versions`, `models.model_state_history`, `models.model_run_issues`, **`models.scoring_run_issues`** (per §6.6). Composite FKs to `features.feature_runs(feature_run_id, feature_set_version)` and `targets.target_runs(target_run_id, target_set_version)` mirror the 03a/03b composite-FK discipline. Detailed shape in §6.6.

**Alternatives.** Fewer tables with denormalized JSONB blobs (less schema enforcement; faster to migrate); more tables with normalized provenance audit (e.g., separate `model_run_provenance` table). The proposed default is the middle ground that keeps schema enforcement strong while staying within the 03a/03b stylistic precedent.

### 10.15 `config/model.yaml` structure

**Status:** Open with Proposed Default.

**Question.** What is the Phase 1 `config/model.yaml` structure?

**Proposed default.** See §7.2. Top-level keys: `model_set_version`, `allowed_model_kinds`, `allowed_calibration_methods`, `allowed_rank_methods`, `sleeve_rank_methods`, `training`, `combined_score`, `mlflow`, `model_state`, `validation`.

**Alternatives.** Splitting into multiple files (`config/model_kinds.yaml`, `config/scoring.yaml`, `config/ranking.yaml`); inlining `sleeve_rank_methods` into `config/universe.yaml` (but Section 2 owns `universe.yaml` and 03c does not modify it); using JSON instead of YAML.

### 10.16 Issue-table ownership for scoring-run anomalies — RESOLVED (Option B)

**Status:** Resolved (Option B); Approver-resolved at lock.

**Background.** §9.7 describes scoring-run-level anomalies (cross-model snapshot mismatch, degenerate cross-section, sleeves whose `rank_method='absolute_with_context'` are unsupported by the current first-testable formula). The `models.model_run_issues` table FKs to a single `models.model_runs(model_run_id)`; a scoring run aggregates several model runs and so does not fit cleanly under that FK.

**Candidates considered during drafting (now retired):**

- ~~Option A: Allow `models.model_run_issues.model_run_id` to be nullable and add a `scoring_run_id` nullable FK with an XOR CHECK.~~
- ~~Option C: Always generate scoring-run-level issues against one of the constituent `model_run_id` rows.~~

**Resolution (Option B): separate table `models.scoring_run_issues`.** This section introduces `models.scoring_run_issues` parallel to `models.model_run_issues`, with its own closed `issue_type` enumeration disjoint from `models.model_run_issues` and an FK to `models.scoring_runs(scoring_run_id)`. Detailed schema in §6.6. Affected sections: §6.6 (schema), §6.7 (`absolute_with_context` warning routing), §8 (tests), §9.7 (edge cases), §10.6 (DiversifierHedge disposition), §11.5 A-PRP-17. The polymorphic-FK alternative (Option A, considered during drafting) is not adopted.

### 10.17 Mechanical enforcement of `random_seed` ↔ `model_set_version` bump

**Status:** Open with Proposed Default.

**Question.** Should the orchestrator mechanically reject a `config/model.yaml` commit that bumps `training.random_seed` without bumping `model_set_version`?

**Proposed default.** **Not enforced mechanically** in Phase 1; rely on EW §3.3 review discipline. Mechanical enforcement would require comparing current YAML to git history at orchestrator startup, which couples runtime to git state.

**Alternatives.** Enforce via a pre-commit hook (lighter coupling); enforce at orchestrator startup by comparing `config_hash` of `config/model.yaml` against the `config_hash` recorded on the most recent `'succeeded'` run with a different `random_seed` (more complex; may produce false positives during legitimate seed-and-version bumps).

### 10.18 Sentinel-retirement migration ordering

**Status:** Open. (Cross-section concern; flagged for migration ordering at 03c lock.)

**Question.** When 03c locks, the Section 2 `pending_section_3` sentinel must be retired from `universe.yaml`. Is the sentinel-retirement migration shipped alongside 03c lock, or is it a separate operator-driven task?

**Proposed paths.**

- **Path A:** Ship a `universe.yaml` migration alongside 03c lock that replaces every `'pending_section_3'` value with the appropriate `rank_method` per `sleeve_rank_methods`. (Cleaner; single coordinated change.)
- **Path B:** Treat sentinel retirement as an Approver-driven `universe.yaml` commit decoupled from 03c lock. The 03c orchestrator's config-validation rejects the sentinel, so any run after 03c lock requires the Approver to have retired the sentinel first. (Looser coupling; small risk of brief unrunnable state between locks.)

The Builder recommends Path A but flags it as Approver-decidable.


---

## 11. Explicit assumptions

Per EW §3.3, every assumption in this draft is classified as one of:

- **Derived from SDR** — directly entailed by Strategy Decision Record v1.0 LOCKED.
- **Derived from EW or earlier locked spec section** — entailed by Engineering Workflow v1.5 or by Sections 1, 2, 3a, or 3b.
- **Implementation default** — engineering choice with no strategy implication; Builder authority per EW §3.3.
- **Approver-resolved default** — strategy-affecting but already resolved by the SDR or by an earlier section's approval note.
- **Proposed default requiring approval** — strategy-affecting, not previously resolved, surfaced for Approver review with this draft. All such items also appear in §10.
- **Open question for Approver** — strategy-affecting, not resolved, no proposal possible without Approver input. Cross-references §10.

### 11.1 Derived from SDR

- **A-SDR-01:** Phase 1 horizon set is `{63, 126}` trading days. (SDR Decision 6 / 03b §11.6 #9.)
- **A-SDR-02:** Phase 1 classification target is `outperformance_h(e, T) = 1 if excess_return_h(e, T) > 0 else 0` per 03b's locked threshold `θ = 0.0` (Approver-resolved per 03b §11.6 #2). 03c consumes this threshold; 03c does **not** redefine it.
- **A-SDR-03:** No fallback to `secondary_benchmark_id` in any data path; secondary benchmark is read-only context per SDR Decision 17.
- **A-SDR-04:** Phase 1 sleeves are the six locked Section 2 codes: `{BroadEquity, Sector, Thematic, BondTreasury, DiversifierHedge, REITRealAsset}`. (SDR Decision 5 as cashed out in `config/universe.yaml` per Section 2 v1.0 LOCKED.)
- **A-SDR-05:** Calibration is required for the classifier baseline. (SDR Decision 7.)
- **A-SDR-06:** Phase 1 model lifecycle has four states `{Active, Warning, Paused, Retired}` with all transitions Approver-only. (SDR Decision 12.)
- **A-SDR-07:** No live broker integration, no individual stocks, no fundamentals, no ETF holdings, no news/events, no earnings transcripts, no options data, no Danelfin, no autonomous research agents, no commercial features in Phase 1. (SDR multiple decisions.)

### 11.2 Derived from EW or earlier locked spec section

- **A-INH-01:** Reproducibility chain anchored on `data_snapshot_id`; transitively reachable from every `models.model_runs` row via `feature_run_id` and `target_run_id`. (Section 2 §6.7, EW §7.)
- **A-INH-02:** T-1 feature semantics inherited from 03a §6.1. Not redefined in 03c.
- **A-INH-03:** Convention B target metadata (`entry_date`, `exit_date`) inherited from 03b §6.5. Not redefined in 03c.
- **A-INH-04:** Two-bucket null-vs-no-row taxonomy for targets inherited from 03b §6.4. Front-edge truncation = absence, not failed run. Not redefined in 03c.
- **A-INH-05:** `features.feature_run_issues` and `targets.target_run_issues` enumerations are not modified by 03c.
- **A-INH-06:** `ops.data_quality_exceptions` is not written by 03c. Model-layer issues land in `models.model_run_issues`.
- **A-INH-07:** `features.feature_runs.status='succeeded'` and `targets.target_runs.status='succeeded'` filters are required on every assembly query.
- **A-INH-08:** Composite-FK discipline (`run_id`, `set_version`) is inherited from 03a/03b and applied to `models.*`.
- **A-INH-09:** Open-run-before-validation lifecycle pattern inherited from 03a §6.3 / 03b §6.3 and applied to `models.model_runs`.

### 11.3 Implementation defaults

These are engineering choices with no strategy implication and are within Builder authority per EW §3.3:

- **A-IMP-01:** MLflow serialization format is `joblib`. (See §6.10, §7.2.)
- **A-IMP-02:** MLflow connectivity is validated at run-open before fitting. (See §6.10.)
- **A-IMP-03:** MLflow connectivity-failure mid-run retries 3 times with exponential backoff. (See §9.5.)
- **A-IMP-04:** Calibrator-fold minimum row count is 100. (See §9.3.)
- **A-IMP-05:** Upstream feature/target runs whose `status != 'succeeded'` (per the locked 03a/03b three-value status enum) are not waited on; the 03c orchestrator opens its own run with `status='running'`, detects the upstream condition, and fails with the appropriate `failed_*_blocked` issue type. The operator re-runs after upstream completes. (See §9.1.)
- **A-IMP-06:** `commit_hash` and `config_hash` are SHA-256 of the canonicalized git commit and config YAML respectively, computed at run-open. (See §7.4.)
- **A-IMP-07:** Run-name-pattern timestamp uses UTC. (See §6.10.)
- **A-IMP-08:** Tie-breaking in `rank_within_sleeve` is by `etf_id` ascending. (See §6.6 `combined_scores` notes; flagged as default in §8.1 RNK-04.)

### 11.4 Approver-resolved defaults

These are strategy-affecting but already resolved by the SDR or by an earlier locked section. **This list is deliberately narrow:** an item appears here only when a locked source explicitly establishes it. Items that earlier drafts placed here without explicit locked-source backing have been moved to §11.5.

- **A-APP-01:** The model-state enumeration is the closed four-value set `{Active, Warning, Paused, Retired}`. (SDR Decision 12 explicit.)
- **A-APP-02:** Two SDR Decision 12 promotion gates exist: (i) Research model → Internal paper tracking and (ii) Paper tracking → influence on real decisions; both require Jeremy approval. 03c implements the schema fields supporting (i); (ii) is owned by Section 5. (SDR Decision 12 explicit.)
- **A-APP-03:** Phase 1 classification target uses threshold `θ = 0.0` (strict positive excess return) per 03b §11.6 #2 (Approver-resolved in 03b lock). 03c consumes this without modification.
- **A-APP-04:** Phase 1 horizon set is `{63, 126}` trading days per 03b §11.6 #9 (Approver-resolved in 03b lock).

### 11.5 Proposed defaults requiring approval

Each of these is strategy-affecting, not previously resolved, and is explicitly proposed in this draft for Approver review. All appear in §10 with full alternatives.

- **A-PRP-01:** Baseline model forms — ridge regression for excess return, logistic regression for outperformance probability. (§10.1.)
- **A-PRP-02:** Calibration method — Platt scaling. (§10.2.)
- **A-PRP-03:** First testable combined-score formula — two-component, equal-weighted z-scores of predicted excess return and calibrated probability. (§10.3.)
- **A-PRP-04:** `allowed_rank_methods` — closed three-value enum: `{benchmark_relative, absolute_with_context, peer_relative}`. (§10.4.)
- **A-PRP-05:** Per-sleeve `rank_method` mapping per the table in §10.5 (locked Section 2 sleeve codes only): `BroadEquity`, `Sector`, `Thematic`, `BondTreasury` → `benchmark_relative`; `DiversifierHedge` → `absolute_with_context`; `REITRealAsset` → `peer_relative`.
- **A-PRP-06:** Combined score is computed first (cross-sectional z-score across all eligible ETFs at signal date), then ranked within sleeve. (§10.7.)
- **A-PRP-07:** ETF eligible across multiple sleeves is ranked once per sleeve (one row per `(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)`). (§10.8.)
- **A-PRP-08:** Initial state on registering a `models.model_versions` row is `'Paused'`. (SDR Decision 12 names the four states but does not specify the initial state.) (§10.9, §6.9.)
- **A-PRP-09:** `Retired` is terminal in Phase 1. (SDR Decision 12 lists `Retired` as one of the four states but does not specify terminality.) (§10.10, §6.9.)
- **A-PRP-10:** All model-state transitions in Phase 1 are Approver-only; no automated transitions. (SDR Decision 12 says "Pause/retirement should require multiple conditions or sustained failure" and "Jeremy approval" gates both promotion gates, but does not explicitly forbid all automated transitions in Phase 1.) (§6.9.)
- **A-PRP-11:** A `models.model_versions` row with `state='Active'` requires both `approved_at_utc` and `approved_by` non-null; enforced by CHECK constraint. (The CHECK shape is a Builder design choice consistent with SDR Decision 12 but not specified by it.)
- **A-PRP-12:** Active → Warning trigger is Approver-only manual transition in Phase 1; no mechanical trigger. (§10.9.)
- **A-PRP-13:** Retired-is-terminal is enforced at the application level only; no DB CHECK or trigger. (§10.10.)
- **A-PRP-14:** MLflow naming — experiment per `model_kind`; run name `{model_set_version}--snapshot-{data_snapshot_id}--{started_at_utc}`; registered model = `model_kind`. (§10.13.)
- **A-PRP-15:** `models.*` schema — **ten-table** design per §6.6: `model_definitions`, `model_runs`, `model_predictions`, `scoring_runs`, `scoring_run_models`, `combined_scores`, `model_versions`, `model_state_history`, `model_run_issues`, **`scoring_run_issues`**. (§10.14.)
- **A-PRP-16:** `config/model.yaml` structure per §7.2.
- **A-PRP-17:** Scoring-run-level issues are routed to the `models.scoring_run_issues` table with its own closed `issue_type` enumeration; `models.model_run_issues` retains its own disjoint enumeration. (§6.6, §10.16.)
- **A-PRP-18:** `random_seed` ↔ `model_set_version` bump is not mechanically enforced; relies on EW §3.3 review. (§10.17.)
- **A-PRP-19:** `risk_score` slot in `combined_score.components` is reserved with `enabled: false`; activation requires amendment. (§10.11.)
- **A-PRP-20:** `trend_relative_strength` slot in `combined_score.components` is reserved with `enabled: false`; activation requires amendment. (§10.12.)
- **A-PRP-21:** `model_kind` enumeration is the closed six-value set in §6.4 / §7.2.
- **A-PRP-22:** `models.model_run_issues.issue_type` is the closed enumeration in §6.6 (see the §6.6 table). `models.scoring_run_issues.issue_type` is a separate closed five-value enumeration per §6.6.
- **A-PRP-23:** `models.scoring_run_models.role` is a closed enum (`'regression_h63'`, `'regression_h126'`, `'classification_h63'`, `'classification_h126'`).
- **A-PRP-24:** `models.model_predictions.prediction_context` is a closed three-value enum: `{'in_sample_diagnostic', 'walk_forward_oos', 'current_scoring'}`. (§6.2.)
- **A-PRP-25:** Standardization default is `per_feature_zscore` with mean and std persisted as MLflow artifacts.
- **A-PRP-26:** `training.missing_data_rule` default is `drop_row`.
- **A-PRP-27:** `training.min_training_rows` default is `1000`; absolute floor is `100`.
- **A-PRP-28:** Sentinel-retirement migration ordering — Path A (ship `universe.yaml` migration alongside 03c lock). (§10.18.)
- **A-PRP-29:** DiversifierHedge under the current first-testable formula — Path X per §10.6 (keep `absolute_with_context` SDR-aligned; emit no `models.combined_scores` rows for `DiversifierHedge` ETFs; record `severity='warning'` `models.scoring_run_issues` row with `issue_type='rank_method_unsupported_in_phase1'` per scoring run; defer activation to a future amendment). **The Builder is not silently re-mapping `DiversifierHedge` to `'benchmark_relative'`.**

### 11.6 Open questions for Approver

These are explicitly unresolved. The Builder is not proposing a default for these:

- **A-OQ-01:** Active → Warning automated trigger definition. (§10.9 Path A vs Path B.)
- **A-OQ-02:** DiversifierHedge under the current first-testable formula — the default A-PRP-29 (Path X) is SDR-Decision-5-aligned (`absolute_with_context`; no `models.combined_scores` rows; `severity='warning'` issue per scoring run) but still requires Approver acceptance of one of three resolution paths in §10.6: Path X (proposed default), Path Y (de-scope DiversifierHedge from Phase 1 ranking entirely), or Path Z (authorize a 03b target amendment to add absolute target families).
- **A-OQ-03:** `risk_score` definition for the 4-component formula. (§10.11.)
- **A-OQ-04:** `trend_relative_strength` definition for the 4-component formula. (§10.12.)

Items A-OQ-03 and A-OQ-04 do not block 03c current scope because their corresponding `combined_score.components` are disabled in the proposed `config/model.yaml`; activation is gated on Approver decision.


---

## 12. Section 3c → Section 4 / 5 / 6 handoff (forward references)

This section catalogues forward references the next downstream sections will need, so 03c lock provides clean seams. Nothing in this section commits the next section's design.

### 12.1 Handoff to Section 4 (Walk-forward backtest, attribution, validation)

Section 4 will need:

- The per-component model-fitting contract (§6.4) — specifically the `model_kind` enumeration and the fit/predict shape consistency guarantees.
- The training-data assembly canonical SQL (§6.1) — Section 4 will parameterize the assembly by fold-specific signal-date ranges.
- The calibration-fold disjointness contract (§6.5) — Section 4 will define the specific fold structure (purge/embargo, fold widths).
- The `prediction_context` enumeration on `models.model_predictions` (§6.2) — Section 4 is responsible for tagging fold-specific prediction rows as `'walk_forward_oos'` and is responsible for enforcing that backtest performance evaluation reads only `'walk_forward_oos'` rows. 03c stores the field; Section 4 enforces the consumption rule.
- The `data_snapshot_id` chain (§6.12) — Section 4 must produce reproducible backtest outputs by re-running against a frozen snapshot.

**Writer-side ownership boundary (R-8 clarification).** Section 4 does **not** write to `models.model_runs`, `models.model_predictions`, `models.scoring_runs`, `models.combined_scores`, `models.model_versions`, `models.model_state_history`, `models.model_run_issues`, or `models.scoring_run_issues`. The model-layer write contracts and MLflow writer-side integration are owned by 03c. When Section 4's walk-forward harness needs model outputs per fold, it does so by **invoking 03c-owned model-run contracts through an approved seam** (the seam shape — function signature, parameterization, fold-metadata payload — is Section 4's design responsibility and is recorded in the locked Section 4 spec, not pre-committed by 03c). Section 4 owns fold structure, purge/embargo widths, walk-forward validation logic, backtest performance computation, and attribution decomposition. 03c does **not** specify those.

### 12.2 Handoff to Section 5 (Signals → portfolio rules, paper portfolio state, order intent)

Section 5 will need:

- The `models.combined_scores` table contract (§6.6, §6.8) — every combined score row is keyed `(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)` with `combined_score` and `rank_within_sleeve`.
- The `models.scoring_runs` and `models.scoring_run_issues` table contracts (§6.6) — Section 5 reads scoring runs and their issue rows; Section 5 does **not** write to these tables; 03c writes them.
- The `models.model_versions` table and the model-state lifecycle (§6.6, §6.9) — Section 5 must respect `state` and reject portfolio decisions made against a `'Paused'` or `'Retired'` model version. The second SDR Decision 12 promotion gate (Paper tracking → influence on real decisions) is owned by Section 5.
- The sleeve-aware ranking semantics (§6.7, §6.11) — Section 5 must respect the `rank_method` choice per sleeve when forming portfolio holdings.
- The §10.6 disposition for `absolute_with_context` ETFs — Section 5 must accept that `DiversifierHedge` ETFs produce no `models.combined_scores` rows under the current first-testable formula and design portfolio rules accordingly until an Approver-approved amendment lands.
- The `data_snapshot_id` chain — Section 5 must produce portfolio holdings keyed to a specific snapshot.

03c does **not** specify portfolio rules, position sizing, signal-to-trade conversion, holding-period logic, paper portfolio state schema, P&L computation, or broker-neutral order intent generation. **All of those are Section 5's scope.**

### 12.3 Handoff to Section 6 (Operator UI)

Section 6 will need:

- Read-only access to `models.model_runs`, `models.model_predictions`, `models.combined_scores`, `models.model_versions`, `models.model_state_history`, `models.model_run_issues`, and `models.scoring_run_issues` for display in the Model Registry / Run Browser surfaces.
- Read-only access to MLflow run metadata via `models.model_runs.mlflow_run_id`.
- The `Active`-uniqueness invariant (§6.6 partial unique index) — UI surfaces displaying the "current Active model" per `model_kind` rely on this invariant.

03c does **not** specify UI layout, navigation, page structure, or interactive controls. UI ownership rests entirely with Section 6 per SDR Decision 17 (UI is read-only). Section 6 does **not** write to any `models.*` table.

### 12.4 Cross-section open seams

The following items are **not** owned by 03c and are listed only to make the seams explicit:

- Walk-forward fold structure, purge widths, embargo widths, attribution decomposition, backtest performance computation — Section 4.
- Portfolio rules, position sizing, paper portfolio state, P&L computation, broker-neutral order intent generation, transaction-cost application — Section 5.
- Operator UI surfaces, Model Registry / Run Browser layout — Section 6.
- Regime classification / regime-conditional combined-score variants — likely tied to 4-component formula activation (§10.11, §10.12); section ownership TBD.
- Live trading / broker integration — explicitly out of scope per SDR.


---

## 13. Proposed traceability matrix updates — draft only

**This section is a sketch. It does NOT modify `docs/traceability_matrix.md`. No row in this section should be read as implying any 03c contribution is "complete" before 03c v1.0 LOCKED / APPROVED. All status language is conditional and pending.**

`docs/traceability_matrix.md` is currently at v0.5 with status entries for SDR Decisions 1, 2, 3, 4, 5, 6, 7, 11, 12, 16, 17 and others. The rows below are sketches of what would be merged into the traceability matrix **after** 03c is approved and locked. They are not pre-merge claims of completion.

### 13.1 Rows where 03c is the responsible section (status pending until 03c approval and matrix merge)

| SDR Decision | Topic | Proposed 03c contribution at lock | Status after 03c lock, if approved |
|---|---|---|---|
| Decision 5 | Sleeve, benchmark, diversifier treatment | 03c §6.7, §6.11, §7.2 enumerate `sleeve_rank_methods` keying every active Section 2 sleeve to a closed `rank_method` value, closing the Section 2 `pending_section_3` sentinel obligation | Pending until 03c approval and matrix merge. `DiversifierHedge` SDR-Decision-5 alignment is recorded in §10.6 / A-PRP-29 (Path X proposed default); long-term resolution path remains an Open Question in A-OQ-02. |
| Decision 6 | Combined-score formula | 03c §6.8, §7.2 specifies first-testable two-component formula with hooks for 4-component reservation | Pending until 03c approval and matrix merge. 4-component activation (`risk_score`, `trend_relative_strength`) deferred per §10.11 / §10.12. |
| Decision 7 | Calibration pipeline | 03c §6.5, §6.6, §7.2 specifies Platt-scaling calibration pipeline integrated with §6.4 baseline classifiers; calibration-fold disjointness via Section 4's fold structure | Pending until 03c approval and matrix merge. Concrete fold structure handed to Section 4. |
| Decision 11 | Lightweight MLOps + MLflow writer side | 03c §6.4 specifies ridge regression + logistic regression as the paired Phase 1 baselines; §6.10 specifies the MLflow writer-side integration with closed 15-tag set linking back to `feature_run_id` and `target_run_id` | Pending until 03c approval and matrix merge. Attribution storage (Decision 11's other half) remains Section 4's. |
| Decision 12 | Model promotion / state lifecycle | 03c §6.6 (`model_versions`, `model_state_history`), §6.9, §7.2 specify the schema fields and the audit log; Phase 1 transitions and `Retired`-terminal are Proposed defaults requiring approval per A-PRP-08, A-PRP-09, A-PRP-10, A-PRP-11 | Pending until 03c approval and matrix merge. The first promotion gate is implementable at 03c lock; the second gate (paper tracking → influence on real decisions) remains Section 5's. Active→Warning automated trigger is A-OQ-01. |
| Decision 16 | Reproducibility chain (model-layer extension) | 03c §6.10, §6.12, §8 extend the chain through `models.*` to MLflow tags + `data_snapshot_id` transitive linkage via `feature_run_id` and `target_run_id` | Pending until 03c approval and matrix merge. The chain is otherwise already established by Section 2, 03a, and 03b. |

### 13.2 Rows where 03c is a downstream consumer (matrix entry stays pinned to the owning section; 03c references are read-only)

| SDR Decision | Topic | 03c relationship | Note |
|---|---|---|---|
| Decision 1 | ETF-only Phase 1 universe | 03c §6.1 INNER JOINs on `(etf_id, as_of_date)`; reads only ETF-keyed rows | Owned by Section 2; 03c reads, does not redefine. |
| Decision 2 | Open architecture / open data layer | 03c writes only to `models.*` and MLflow; no provider lock-in; no broker SDK reference | Architecture coherence; 03c respects but does not redefine. |
| Decision 3 | Phase 1 deliverables | 03c is the model-layer Phase 1 deliverable; matrix references to "Section 3c" become specific at 03c lock | Editorial only at lock. |
| Decision 4 | Phase 1 horizons (63d, 126d) | 03c §6.4 model_kind enum encodes both horizons; §6.8 z-scoring is per `(signal_date, horizon)` cross-section | Owned by 03b (`config/targets.yaml` ships the horizon list); 03c reads. |
| Decision 17 | Secondary benchmarks read-only | 03c §11 A-INH-* (no-fallback assumption); §8.2 CC-07 static check verifies | Owned by Section 2; 03c verifies via test. |

### 13.3 Rows untouched by 03c

The following decisions are not within 03c scope and the traceability matrix entries should remain as currently set (or as updated by future sections):

- Decision 8 (purge/embargo) — Section 4.
- Decision 9 (regime taxonomy / regime reporting) — Section 4 owns the reporting layer; 03a's feature-side regime primitive remains an input only.
- Decision 10 (portfolio management and risk rules) — Section 5.
- Decision 13 (LLM workflow / agentic coding / QA) — process discipline; no spec-section ownership.
- Decision 14 (paper portfolio state, broker-neutral order intent) — Section 5.
- Decision 15 (data-quality reporting cadence) — owned by Section 2 (ingestion-side).
- Decision 18 (operator UI / read-only surface) — Section 6.

### 13.4 New traceability rows that 03c may motivate

03c does not propose new SDR decisions. The traceability matrix structure is keyed on SDR decisions; no new rows are needed. (The new content surfaces as additional cells in existing rows, per §13.1 / §13.2.)

### 13.5 Update procedure (informational; not part of 03c)

When 03c is approved and locked, the Approver (or the Approver's delegate) is expected to:

1. Update `docs/traceability_matrix.md` to incorporate the rows in §13.1 / §13.2 with text the Approver finalizes at lock time. The sketches above are not to be treated as final wording.
2. Bump `docs/traceability_matrix.md` version (currently v0.5).
3. Reference the 03c approval note in the matrix changelog.

**The matrix merge is performed by the Approver as part of the Section 3c lock**, using the Section 3c traceability companion artifact (`docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_traceability_updates.md`) as the canonical source of replacement rows. This section §13 is a Builder-side sketch of which decision rows 03c expects to touch; it does not itself modify `docs/traceability_matrix.md`. Nothing in §13 implies any 03c contribution is finalized or merged ahead of v1.0 LOCKED / APPROVED and the corresponding matrix bump.

---

End of Section 3c v1.0 LOCKED / APPROVED.

