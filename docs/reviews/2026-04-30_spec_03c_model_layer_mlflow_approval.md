# Engineering Specification Section 3c — Model Layer and MLflow: Approval Note

**Section:** Engineering Specification — Section 3c: Model Layer and MLflow
**Section path:** `docs/engineering_spec/03c_model_layer_mlflow.md`
**Locked version:** v1.0 LOCKED / APPROVED
**Approval date:** 2026-04-30
**Approver:** Jeremy
**Builder:** Claude
**QA Reviewer:** ChatGPT

The section was iterated under direct Approver review across drafts v0.1 → v0.2 → v0.3, with each round producing an explicit revision list (fifteen revisions for v0.2, nine cleanup revisions for v0.3, plus minor editorial cleanup at locking). The Approver's final review serves as the QA pass per EW §3.4 item 9.

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
- Section 3c traceability updates (`docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_traceability_updates.md`)
- `docs/traceability_matrix.md` (post-merge state, after the Section 3c lock merge applies the companion traceability updates)

---

## 1. What this approval covers

Approval of Section 3c v1.0 LOCKED / APPROVED locks the following at the model-layer level. All decisions below were the subject of explicit Approver direction during the v0.1 → v0.2 → v0.3 → v1.0 process trail in §2 below.

### 1.1 Write contract

1. **03c writes only to `models.*` and to the MLflow tracking server.** The ten tables under the `models` schema are: `models.model_definitions`, `models.model_runs`, `models.model_predictions`, `models.model_run_issues`, `models.scoring_runs`, `models.scoring_run_models`, `models.combined_scores`, `models.scoring_run_issues`, `models.model_versions`, `models.model_state_history`. MLflow writes are a one-to-one mapping per model run (one MLflow run per `models.model_runs` row) and a one-to-one mapping per registered model version (one MLflow registered model + version per `models.model_versions` row).
2. **03c does not write to `ops.data_quality_exceptions` or any `ops.*` table.** Per Section 2 v1.0 LOCKED, `ingestion/` is the only emitter of `ops.data_quality_exceptions` rows in Phase 1; the framework remains ingestion-owned and unmodified by 03c. 03c does not write to `universe.*`, `prices.*`, `features.*` (Section 3a), `targets.*` (Section 3b), or any provider table.
3. **`models.model_run_issues` and `models.scoring_run_issues` are the Phase 1 model-layer issue logs.** They have **disjoint** closed `issue_type` enumerations defined in §6.6 — a `models.model_run_issues` row references exactly one `models.model_runs` row; a `models.scoring_run_issues` row references exactly one `models.scoring_runs` row. The two tables are deliberately separate to keep FK semantics clean (a scoring run typically aggregates several model runs).
4. **`models.model_run_issues` and `models.scoring_run_issues` are separate from Section 2's ingestion-owned `ops.data_quality_exceptions` framework**, parallel to the analogous separation in 03a (`features.feature_run_issues`) and 03b (`targets.target_run_issues`).

### 1.2 Lifecycle

5. **Open-run-before-validation lifecycle, parallel to 03a §6.3 and 03b §6.3.** Configuration validation is two-phase. Phase 0 (pre-run-open): if `config/model.yaml` is unreadable, malformed, encoding-broken, or missing the keys the orchestrator needs to construct a run context (minimally `model_set_version` and the `mlflow` block), the orchestrator treats this as a pre-run fatal parse error, logs to stderr only, and does **not** open a `models.model_runs` row; no `models.model_run_issues` row is written (no `model_run_id` exists yet to FK against). Phase 1 (post-run-open semantic validation): once the file is parseable enough to identify `model_set_version`, the orchestrator opens the `models.model_runs` row with `status='running'` and validates the selected `feature_run_id`, the selected `target_run_id`, the `data_snapshot_id` chain, the snapshot's `status`, the model config semantics, and MLflow connectivity. Any failure marks the run `status='failed'`, populates `error_message` and `completed_at_utc`, writes the appropriate `severity='fail'` `models.model_run_issues` row (FK satisfied), and writes **no** `models.model_predictions` rows. Front-edge horizon truncation is **not** a run-level blocking condition — it is row-level absence per 03b §6.5 Bucket 1 and the per-row `prediction_context` tagging discipline in 03c §6.2.
6. **Atomicity contract is split across two 03c-owned run types.** Model-run execution writes `models.model_predictions` (transactional batches keyed by (model_kind, signal-date-window)); scoring-run execution writes `models.combined_scores` (transactional batches keyed by (signal-date-window, sleeve_id)). A model run never writes to `models.combined_scores`, and a scoring run never writes to `models.model_predictions`. Both run types share the same closed three-value `status` enum `('running', 'succeeded', 'failed')` and the same open-run-before-validation lifecycle. Failed runs may retain partial rows; the schema deliberately does not delete partial rows on failure. Downstream consumers must filter on the appropriate run-status `'succeeded'` filter.
7. **Predictions are emitted for the entire `(etf_id, as_of_date)` set in the succeeded feature run, with `prediction_context` tagged per the rules in §6.2.** The closed `prediction_context` enumeration is `('in_sample_diagnostic', 'walk_forward_oos', 'current_scoring')`. 03c owns the storage column on `models.model_predictions`; **Section 4 owns fold construction, purge / embargo width selection, and the rule for which rows qualify as `walk_forward_oos`**. When Section 4 invokes the 03c-owned model-run contract through an approved seam, Section 4 is responsible for tagging each emitted row with the correct `prediction_context`. Outside a Section 4 invocation, the orchestrator emits `'current_scoring'` for rows at `T_now`-side dates and `'in_sample_diagnostic'` for rows at training-window dates; it never emits `'walk_forward_oos'` without Section 4 fold metadata.

### 1.3 `feature_set_version` / `target_set_version` integrity (database-level)

8. **Composite-FK integrity is enforced at the database level.** `models.model_runs` carries composite FKs `(feature_run_id, feature_set_version) → features.feature_runs(feature_run_id, feature_set_version)` and `(target_run_id, target_set_version) → targets.target_runs(target_run_id, target_set_version)`, mirroring the 03a/03b composite-FK discipline. The orchestrator's pre-write invariant check is retained as a clearer-error layer above the database constraints.
9. **Snapshot-chain reproducibility:** `models.model_runs.data_snapshot_id` is a redundant FK for query convenience; the orchestrator asserts at run-open that the linked `feature_run_id` and `target_run_id` reference the same `data_snapshot_id`. A mismatch is a fail-severity `models.model_run_issues` row with the canonical `issue_type` per §6.6 and a run-level abort. 03c does **not** carry an independent `data_snapshot_id` reference; the chain is single-sourced through 03a and 03b, then recorded redundantly on the model run row.

### 1.4 Phase 1 strategy-affecting model choices (Approver-resolved at lock; some retained as Proposed defaults requiring approval at first build)

10. **Two baseline model implementations matching SDR Decision 6's dual-target framework**, classified as **Proposed defaults requiring Approver approval** at first build per §11.6: (a) ridge regression on standardized features for the regression target (`excess_return_h63` and `excess_return_h126`, two independent fits); (b) logistic regression with a held-out calibration step (Platt by Proposed default, with isotonic and `logistic_on_folds` available behind config) for the classification target (`outperformance_h63` and `outperformance_h126`, two independent fits). Both baselines are deliberately simple to satisfy the "first testable" bar and to anchor the dual-target framework before any later complexity (gradient-boosted machines, ensembles, Danelfin-class signals — out of Phase 1 scope).
11. **First testable combined-score formula** under SDR Decision 6: a **2-component combined score** = `w_reg * z(predicted_excess_return_h) + w_cls * z(calibrated_probability_outperformance_h)` computed per `(etf, signal_date, horizon)`, with weights summing to `1.0 ± 1e-6` and Proposed defaults `w_reg = 0.5`, `w_cls = 0.5`. Per §6.8, the component z-scores are computed over the rank-method-defined ranking cross-section at signal date `T`: pooled across all rank-eligible ETFs for `benchmark_relative`, within sleeve for `peer_relative`, and not enabled for `absolute_with_context` under the current formula. Ranking is then materialized within sleeve. Hooks for the 4-component variant (adding a risk score and a trend / relative-strength confirmation per Decision 6) are reserved in `config/model.yaml` (`combined_score.formula_version` enum reserves a 4-component variant) but are not enabled in current 03c scope. Activation requires an Approver-approved 03c amendment.
12. **Calibration pipeline** under SDR Decision 7: held-out calibration over Section 4 fold structure, with the closed enumeration `('platt', 'isotonic', 'logistic_on_folds')` on `models.model_definitions.calibration_method`. The fold structure consumed by calibration is supplied by Section 4 through an approved seam; 03c owns the writer side of calibrated probabilities only. The calibration method choice itself is a Proposed default requiring Approver approval at first build per §11.6.
13. **`rank_method` closed enumeration and per-sleeve mapping** under SDR Decision 5, closing the Section 2 `pending_section_3` sentinel obligation. Closed enumeration: `('benchmark_relative', 'peer_relative', 'absolute_with_context')`. Per-sleeve mapping per §6.7 / §10.5: `BroadEquity → benchmark_relative`, `Sector → benchmark_relative`, `Thematic → benchmark_relative`, `BondTreasury → benchmark_relative`, `DiversifierHedge → absolute_with_context`, `REITRealAsset → peer_relative`. The orchestrator validates that every `universe.etfs.rank_method` value is in the enumeration and that no sleeve in `universe.sleeves` is missing from `sleeve_rank_methods`; any sentinel `pending_section_3` value still present is a `severity='fail'` `models.model_run_issues` row with `issue_type='pending_section_3_sentinel'`.
14. **`DiversifierHedge` under the current first-testable formula:** the current 2-component combined-score formula is benchmark-relative by 03b construction (excess return and outperformance both consume 03b's locked classification threshold `θ = 0.0` against `primary_benchmark_id`) and therefore does not produce a meaningful ranking signal for ETFs whose `rank_method = 'absolute_with_context'`. **Phase 1 disposition (locked):** `DiversifierHedge` ETFs produce **no `models.combined_scores` rows** under the current formula; one `severity='warning'` row is written to `models.scoring_run_issues` per scoring run with `issue_type='rank_method_unsupported_in_phase1'` listing the affected sleeve(s) and ETF count. Activation requires an Approver-approved 03c amendment that adds absolute-trend / absolute-gain `model_kind` values **and** the absolute / risk inputs needed by an extended combined-score formula. **The Builder is not silently re-mapping `DiversifierHedge` to `'benchmark_relative'`.** The Approver retains three resolution paths in §10.6 (Path X — proposed default; Path Y — de-scope DiversifierHedge from Phase 1 ranking entirely; Path Z — authorize a 03b target amendment to add absolute target families); the Path X disposition stands at lock.
15. **Model-state lifecycle schema and audit** under SDR Decision 12: `models.model_versions.state` is a closed enumeration `('Active', 'Warning', 'Paused', 'Retired')` (the four states are Approver-resolved by SDR Decision 12); `models.model_state_history` is an append-only audit table recording every state transition. The defaults `initial_state_on_register: Paused`, `approver_only_transitions: true`, and `retired_is_terminal: true` are **Proposed defaults requiring Approver approval** at first build per §11.5 (SDR Decision 12 names the four states but does not specify initial state, terminality of `Retired`, or whether all transitions are Approver-only in Phase 1). The Active → Warning trigger definition is an Open Question (§10.9), not resolved by this approval.
16. **Schema-level partial unique active-version index**: a partial unique index `(model_kind) WHERE state='Active'` on `models.model_versions` ensures at most one Active version per `model_kind` at any time. State-transition writes go through `models.model_state_history` and update `models.model_versions.state` atomically; consumers query the live state from `models.model_versions` and the audit history from `models.model_state_history`.

### 1.5 Configuration

17. **`config/model.yaml` is owned by 03c** as a strategy-affecting config file. Approved within the 03c spec approval path, mirroring the precedents Section 3a (`config/features.yaml`) and Section 3b (`config/targets.yaml`) set. **No Section 1 amendment is proposed by 03c**; the Section 1 *Config dependencies* table already enumerates `config/model.yaml`. 03c may *read* feature and target metadata at consumption time (`config/features.yaml`, `config/targets.yaml`, and the `features.feature_definitions` / `targets.target_definitions` catalogs) but does not own those files. 03c owns the `model_set_version` discipline on `config/model.yaml` parallel to 03a's `feature_set_version` and 03b's `target_set_version`.

### 1.6 Test surface

18. **Required Tests §8 are exhaustive at the spec level** and cover: training-data-assembly correctness; calibration correctness; combined-score formation (CS-01..CS-03 — including CS-01's filter that a scoring run consumes only `status='succeeded'` model runs, validated by the orchestrator before writing combined-score rows; FKs enforce existence and version integrity); sleeve-aware ranking; MLflow writer-side integration; model-state lifecycle; configuration discipline; reproducibility; error-path coverage; static-check tests (no `models/` import from `providers/`; no provider-table read; adjusted-close-only via `prices.etf_prices_daily`; no write to `ops.*` / `features.*` / `targets.*` / `universe.*` / `prices.*`; no `secondary_benchmark_id` fallback). Data-contract tests DC-01..DC-09 cover composite FKs; closed `models.model_run_issues.issue_type` enum (per §6.6); closed `models.scoring_run_issues.issue_type` enum (per §6.6); closed `models.scoring_run_models.role` enum; closed `models.model_predictions.prediction_context` enum; mlflow_model_uri-on-Active enforcement; per-run prediction-row count parity with feature-row count; combined-score uniqueness on `(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)`. Severity-enum closure tests for both issue tables. Deferred Section 4 / Section 5 / Section 6 tests are called out explicitly in §8.4 (walk-forward harness, purge / embargo, paper-portfolio replay, UI smoke).

### 1.7 Boundaries with Sections 4, 5, and 6

19. **Section 4 owns walk-forward fold structure, purge / embargo width selection, backtest, attribution, and OOS validation.** Section 4 does **not** write to `models.model_runs`, `models.model_predictions`, `models.scoring_runs`, or `models.combined_scores`. Section 4 invokes 03c-owned model-run and scoring-run contracts through approved seams (the §12.1 invocation seam); 03c owns the writer side throughout. The closed `prediction_context` enumeration in §6.2 is the contract by which Section 4 communicates fold-aware OOS-vs-in-sample to downstream consumers.
20. **Section 5 owns portfolio rules, paper portfolio state, the second promotion gate, and broker-neutral order intent.** Section 5 reads from the `models.combined_scores` surface (filtered on `models.scoring_runs.status='succeeded'`) and from `models.model_versions` (filtered on `state='Active'`); Section 5 does not write to `models.*`. 03c's first promotion gate is the registration of a `models.model_versions` row with `state='Paused'` (the Proposed default initial state); the second promotion gate (Section 5) controls when an Active version is consumed by the paper portfolio.
21. **Section 6 owns the UI and read-only surfaces**, including the Model Registry / Run Browser screens. Section 6 reads from `models.model_versions`, `models.model_state_history`, `models.model_runs`, `models.model_predictions`, `models.scoring_runs`, `models.combined_scores`, `models.model_run_issues`, `models.scoring_run_issues`, and the corresponding MLflow runs / artifacts. Section 6 enforces read-only access at the database role level (no INSERT / UPDATE / DELETE / DDL from `ui/`).

### 1.8 Approval Matrix items satisfied (per EW §2.3)

The following Approval Matrix items are satisfied by this approval:

- **Engineering Specification section finalization** (per EW §3.4): all eleven template fields populated; section committed to `docs/engineering_spec/`; QA review per EW §3.4 item 9 satisfied via Approver-direct iterative review across v0.1 → v0.2 → v0.3 with explicit revision lists at each step (fifteen revisions for v0.2, nine cleanup revisions for v0.3).
- **Database schema changes** at the spec level (the `models.*` schema: ten tables, indexes, FK and UNIQUE constraints, partial-unique active-version index).
- **Strategy-affecting YAML config changes** at the spec level (`config/model.yaml` shape and validation rules).
- **Changes to model definitions, calibration methods, combined-score formula, and ranking semantics** — the Phase 1 model layer per §1.4 above.
- **MLflow writer-side integration** under SDR Decision 11.
- **`rank_method` closed enumeration** closing the Section 2 `pending_section_3` sentinel obligation (per §1.4 item 13).
- **Model-state lifecycle schema and audit** under SDR Decision 12 (per §1.4 item 15).

The following Approval Matrix items are **explicitly not** satisfied by this approval and remain pending later sections:

- Walk-forward harness, purge / embargo enforcement, transaction-cost application, attribution storage, OOS leakage tests, regime reporting — Section 4.
- Portfolio rules, paper portfolio state, second promotion gate, kill switch, broker-neutral order intent — Section 5.
- UI screens and read-only enforcement — Section 6.
- DiversifierHedge `absolute_with_context` ranking activation — out of current 03c scope; requires a future 03c amendment that adds absolute-trend / absolute-gain `model_kind` values and the absolute / risk inputs to an extended combined-score formula (per §1.4 item 14).
- Active → Warning trigger definition — Open Question §10.9 carried forward.
- `risk_score` / `trend_relative_strength` definitions for the reserved 4-component formula variant — Open Questions §10.10 / §10.11 carried forward.
- Danelfin and any external-signal integrations — out of Phase 1 scope per SDR Decision 14.

---

## 2. Process trail

1. **Section 3 handoff packet** (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`) authorized Section 3 drafting after Section 2 lock, naming SDR v1.0 LOCKED, EW v1.5 LOCKED, Section 1 v1.0 LOCKED, and Section 2 v1.0 LOCKED as controlling documents. The same packet authorized the 3a / 3b / 3c split with sequencing 3a → 3b → 3c.
2. **Lightweight 03c handoff packet basis.** Per Approver direction, no separate Section 3c handoff packet was issued; 03c drafting and revision were authorized to proceed from four sources taken together as the de facto scope statement: (a) the current general project handoff (`docs/current_claude_context_handoff.md`); (b) Section 3a §12 and Section 3b §12 forward references to 03c; (c) Section 3a approval note §5.1 and Section 3b approval note §5.1 *"Open items handed forward to 03c"*; (d) the targeted v0.2 revision instruction issued by the Approver on 2026-04-30 (the QA-driven revision list applied in the v0.2 pass) and the targeted v0.3 cleanup instruction issued on 2026-04-30 (the nine-revision cleanup applied in the v0.3 pass). The 03c spec's front matter records this scope-basis language explicitly so this approval note can cite it without further amendment (introduced in v0.1, retained through v1.0).
3. **v0.1 drafted** by the Builder. Eleven EW §3.2 template fields populated in order. SDR Decisions 1, 2, 5, 6, 7, 11, 12, 16 cited as directly implemented or respected. Open Questions and Proposed defaults visibly classified per EW §3.3.
4. **v0.1 → v0.2 revision pass** by the Approver against v0.1 produced fifteen targeted revisions plus preservation of accepted v0.1 strengths: (R1) sleeve names corrected to the locked Section 2 closed enumeration `{BroadEquity, Sector, Thematic, BondTreasury, DiversifierHedge, REITRealAsset}`; (R2) removed the v0.1 fabricated `outperformance_threshold_bps_per_year=100` assumption (03c consumes 03b's locked `θ = 0.0`); (R3) DiversifierHedge mapped to `absolute_with_context` with explicit acknowledgement that the current 2-component formula does not rank such ETFs; (R4) run-status enum normalized to `('running', 'succeeded', 'failed')`; (R5) open-run-before-validation lifecycle reconfirmed parallel to 03a/03b; (R6) issue-type enumeration reconciled to the canonical §6.6 closed sets; (R7) `prediction_context` closed enum introduced; (R8) Section 4 ownership corrected (Section 4 does not write to `models.*`); (R9) `models.model_versions` schema contradiction fixed; (R10) new `models.scoring_run_issues` table introduced; (R11) schema inventory corrected to ten tables; (R12) model-state defaults reclassified (only the four-state closed enumeration is Approver-resolved; initial state, terminality, Approver-only transitions are Proposed defaults); (R13) Section 5 / Section 6 handoffs corrected; (R14) traceability sketch language softened; (R15) v0.1 strengths preserved per Approver direction.
5. **v0.2 → v0.3 revision pass** by the Approver produced nine cleanup revisions: (R1) config-validation lifecycle made consistent across §6.3, §7.3, §9.4 (semantic validation runs after run-open with `status='running'`); (R2) `model_state` YAML comments corrected to flag Proposed-default classifications; (R3) §5.2 outputs list extended to all ten `models.*` tables; (R4) DiversifierHedge YAML comment routing corrected to `models.scoring_run_issues`; (R5) test CS-01 wording rewritten to use only the closed three-value status enum and accurate enforcement language; (R6) test DC-02 stale "17-value enum" count removed and DC-07/08/09 added; (R7) final stale upstream-status wording in §5.1 removed; (R8) eight remaining current-body references to "v0.1 first-testable formula" replaced with "current first-testable formula"; (R9) `.env` wording cleaned (03c directly reads only `MLFLOW_TRACKING_URI`).
6. **v0.3 → v1.0 lock authorization** by the Approver. v0.3 promoted to v1.0 LOCKED / APPROVED with **no substantive change** to behavior, schema, tests, scope, or ownership; locking metadata flipped (status header, end-of-document marker); final editorial cleanup applied at lock: (a) current-body references to v0.1 / v0.2 that were not historical changelog entries replaced with neutral lock wording such as "current first-testable formula," "current disposition," "current scope," or "this section"; (b) §5.1 `config/model.yaml` consumer wording aligned with the final two-phase lifecycle; (c) §6.3 atomicity contract restated with model-run writes and scoring-run writes separated as different 03c-owned run types; (d) §13.5 "03c v0.2 does not perform any of these steps" wording replaced with lock-appropriate language deferring matrix-merge execution to the Approver. Historical v0.1 → v0.3 changelog entries preserved verbatim. The Approver exercised final-decision authority per EW §2.1 and approved without an additional QA cycle on v0.3.

---

## 3. Companion artifacts

- **Approved spec section:** `docs/engineering_spec/03c_model_layer_mlflow.md` (v1.0 LOCKED / APPROVED).
- **This approval note:** `docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_approval.md`.
- **Section 3c traceability updates:** `docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_traceability_updates.md`. Proposes replacement rows for SDR Decisions 1, 2, 3, 4, 5, 6, 7, 11, 12, 16, and 17 in `docs/traceability_matrix.md`, in the same shape as the Section 2 / Section 3a / Section 3b traceability-updates companion files. Application of the proposed replacement rows to `docs/traceability_matrix.md` is performed by the Approver as part of the Section 3c lock merge, bumping the matrix version from v0.5 to v0.6.
- **Section 3 handoff packet** (received pre-drafting for the broader Section 3 split): stored under `docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md` per EW §2.2.

---

## 4. Conditions on subsequent sections

Section 3c v1.0 LOCKED / APPROVED imposes the following constraints on Sections 4, 5, and 6. Any change to these requires a Section 3c amendment with Approver approval per EW §3.3 (no assumption drift) and EW §2.3 (Approval Matrix), not silent override:

1. **The §6.2 `prediction_context` closed enumeration `('in_sample_diagnostic', 'walk_forward_oos', 'current_scoring')`** is canonical for `models.model_predictions`. No Section 4, 5, or 6 module may add a fourth value or reframe an existing value without a 03c amendment. Section 4 owns the rules for which rows qualify as `walk_forward_oos`; 03c owns the storage column.
2. **The §6.3 atomicity contract** stands. Section 4 does **not** write to `models.model_runs`, `models.model_predictions`, `models.scoring_runs`, or `models.combined_scores`. Section 4 invokes the 03c-owned writer through the §12.1 invocation seam. Section 5 and Section 6 are read-only consumers of the model and scoring surfaces.
3. **Walk-forward fold structure, purge / embargo width selection, and the rule for what qualifies as `'walk_forward_oos'` are Section 4's**. 03c stores the per-row `prediction_context` value but does not construct folds, does not select embargo width, and does not enforce purge boundaries at emission time. Section 4 supplies the fold metadata through the §12.1 invocation seam.
4. **The failed-run consumption-side discipline** stands. Downstream consumers — Section 4 backtest, Section 5 portfolio, Section 6 UI — must filter `models.model_predictions` rows on `models.model_runs.status='succeeded'` and `models.combined_scores` rows on `models.scoring_runs.status='succeeded'`. Tests in Sections 4, 5, and 6 must verify these filters on every model / scoring consumption path.
5. **The composite-FK integrity contract** (`(feature_run_id, feature_set_version)` and `(target_run_id, target_set_version)` on `models.model_runs`; `data_snapshot_id` chain via the linked feature and target runs) stands. Any later model-set-version evolution must respect the FK chain.
6. **The MLflow reproducibility contract** stands. One MLflow run per `models.model_runs` row; one MLflow registered model + version per `models.model_versions` row; MLflow tags include the closed required tag set defined in 03c §6.10. Sections 4 / 5 / 6 may not bypass this chain.
7. **The `models.model_run_issues` and `models.scoring_run_issues` schemas** stand, including their **disjoint** closed `issue_type` enumerations and the closed two-value `severity` enumeration `('warning', 'fail')`. New types require an 03c amendment, not a Section 4 / 5 / 6 ad-hoc string.
8. **The `ops.data_quality_exceptions` framework remains ingestion-owned and unmodified by 03c.** No later section may reframe 03c as a writer to this table without a Section 2 amendment.
9. **The `rank_method` closed enumeration** `('benchmark_relative', 'peer_relative', 'absolute_with_context')` and its per-sleeve mapping in §6.7 / §10.5 stand. Sections 4 / 5 / 6 must consume this enumeration without redefining it. Adding a fourth value, changing a sleeve's mapping, or relaxing the validator's rejection of the `pending_section_3` sentinel requires a 03c amendment.
10. **The `DiversifierHedge` disposition** stands at lock: ETFs flagged `'absolute_with_context'` produce **no `models.combined_scores` rows** under the current 2-component formula; one `severity='warning'` `models.scoring_run_issues` row is written per scoring run with `issue_type='rank_method_unsupported_in_phase1'`. Section 5 portfolio rules and Section 6 UI must handle the absence-of-rows case gracefully (the eligible-but-not-ranked surface is non-empty for `DiversifierHedge` ETFs while the `combined_scores` surface for those ETFs is empty). The Builder is **not** silently re-mapping `DiversifierHedge` to `'benchmark_relative'`. Activation requires an Approver-approved 03c amendment that adds absolute-trend / absolute-gain `model_kind` values **and** the absolute / risk inputs to an extended combined-score formula.
11. **The model-state closed enumeration** `('Active', 'Warning', 'Paused', 'Retired')`, the `models.model_state_history` audit discipline, and the partial unique active-version index `(model_kind) WHERE state='Active'` stand. Section 5 owns the second promotion gate (when an Active version is consumed by the paper portfolio); 03c owns the first promotion gate (registration of a `models.model_versions` row at the Proposed-default initial state `Paused`). The Active → Warning trigger definition is an Open Question (§10.9); Section 5 may propose a definition, but adoption requires a 03c amendment.
12. **Convention B trading-day semantics and the 03b classification threshold `θ = 0.0`** stand on the model-consumption side. 03c reads target rows directly from `targets.target_values` and never recomputes excess return, outperformance, or window arithmetic; Sections 4 / 5 / 6 inherit this discipline.
13. **The benchmark-resolution interim constraint** stands at the model layer. 03c does **not** introduce a fallback-to-`secondary_benchmark_id` mechanism; the no-silent-benchmark-substitution rule is global to the feature, target, and model surfaces. Sections 4 / 5 / 6 may not introduce one without Approver approval and a coordinated Section 2 / 3a / 3b / 3c amendment.
14. **`config/model.yaml` is the only YAML file 03c owns.** Section 4 owns its own YAML (`config/backtest.yaml` or equivalent — Section 4 will name); Section 5 owns `config/portfolio.yaml` (per Section 1 *Config dependencies*); Section 6 may add UI-only config. Cross-file coupling (e.g., Section 5 reading `model_set_version` from `config/model.yaml` to choose a model variant) is permitted on the read side only.
15. **No implementation begins until 03c is committed and traceability is updated.** The matrix bump from v0.5 to v0.6 (per the companion artifact) and the addition of this approval note to the matrix changelog are prerequisites to any code under `models/`, any migration file creating `models.*` tables, and any `config/model.yaml` commit. The constraints in this §4 bind both the spec phase (no Section 4 / 5 / 6 spec content may contradict them) and the implementation phase (no code may bypass them).

---

## 5. Open items handed forward

### 5.1 Open items handed forward to Section 4

- **Walk-forward fold structure, purge / embargo width selection, and OOS-vs-in-sample fold rules** consuming the 03c-owned `prediction_context` storage column. 03c stores the value; Section 4 supplies the fold metadata through the §12.1 invocation seam.
- **Backtest harness** consuming `models.model_predictions` (filtered on `models.model_runs.status='succeeded'`) and `models.combined_scores` (filtered on `models.scoring_runs.status='succeeded'`).
- **Attribution storage and reporting** anchored on the `data_snapshot_id` / `feature_run_id` / `target_run_id` / `model_run_id` / `scoring_run_id` reproducibility chain.
- **OOS leakage tests** at the train / test boundary using the per-row window metadata 03b records and the `prediction_context` tagging 03c records.
- **Regime reporting** under SDR Decision 9, consuming whatever regime computation lands in Section 3 / Section 4 (currently `pending`; out of 03c scope).

### 5.2 Open items handed forward to Section 5

- **Portfolio rules, paper portfolio state, and the second promotion gate** consuming `models.combined_scores` (filtered on `models.scoring_runs.status='succeeded'`) and `models.model_versions` (filtered on `state='Active'`).
- **Broker-neutral order intent** under SDR Decision 15. Phase 1 is paper-only; the order-intent surface is broker-neutral and does not call any broker SDK.
- **Kill switch** under SDR Decision 12, integrated with the `models.model_versions` lifecycle (Section 5 may transition Active → Paused under defined conditions, subject to the Approver-only-Phase-1 transition default).
- **Replacement-ETF semantics** under SDR Decision 4 at the portfolio level. 03c does not consult `replacement_etf_id`; this remains a Section 5 portfolio concern.
- **Active → Warning trigger definition** (an Open Question §10.9 in 03c). Section 5 may propose a definition; adoption requires a 03c amendment.

### 5.3 Open items handed forward to Section 6

- **Model Registry / Run Browser screens** reading from `models.model_versions`, `models.model_state_history`, `models.model_runs`, `models.model_predictions`, `models.scoring_runs`, `models.combined_scores`, `models.model_run_issues`, `models.scoring_run_issues`, and the corresponding MLflow runs and registered models.
- **Read-only enforcement at the database role level** — no INSERT / UPDATE / DELETE / DDL from `ui/` against any `models.*` table.
- **Bias-control disclosure surfacing** under SDR Decision 16 (the survivorship label and the `prediction_context` value displayed in the UI alongside model outputs).
- **Surfacing of the DiversifierHedge unranked-ETFs case** — Section 6 UI must handle the eligible-but-not-ranked rendering for ETFs whose `rank_method='absolute_with_context'` per §1.4 item 14.

### 5.4 Open items handed forward as Approver Open Questions (still open after this approval)

- **Active → Warning trigger definition** (03c §10.9). The orchestrator may propose a default trigger definition (e.g., a calibration-degradation threshold), but adoption requires Approver direction. Section 5 may propose a definition during Section 5 drafting.
- **DiversifierHedge long-term path** (03c §10.6). The Path X disposition (no `combined_scores` rows; warning issue per scoring run) stands at lock. The Approver retains discretion to authorize Path Y (de-scope DiversifierHedge from Phase 1 ranking entirely) or Path Z (a coordinated 03b target amendment to add absolute target families plus a 03c amendment for the corresponding model_kind values).
- **`risk_score` definition** for the reserved 4-component formula variant (03c §10.10). Out of current 03c scope; activation requires a coordinated 03b / 03c amendment.
- **`trend_relative_strength` definition** for the reserved 4-component formula variant (03c §10.11). Same status.

---

## 6. Implementation status

**No implementation or code has started for Section 3c.** The locked spec is a specification, not a build. The migration script that creates the `models.*` schema, the calculator and orchestrator modules under `models/`, the `config/model.yaml` file, and the test files under `tests/unit/models/` and `tests/integration/models/` will be authored under the standard EW §3 → §10 build workflow after Section 3c is committed and traceability is updated, or earlier if the Approver authorizes a partial build.

The constraints in §4 above bind both the spec phase (no Section 4 / 5 / 6 spec content may contradict them) and the implementation phase (no code may bypass them).

---

## 7. Approval

The Approver has reviewed Section 3c v1.0 LOCKED / APPROVED at `docs/engineering_spec/03c_model_layer_mlflow.md`, the companion traceability updates at `docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_traceability_updates.md`, and the post-merge state of `docs/traceability_matrix.md` (v0.6), and approves the section as locked. Subsequent changes follow EW amendment discipline.

**Signed:** Jeremy (Approver), 2026-04-30.

---

**End of approval note.**
