# Engineering Specification Section 3a — Feature Engineering: Approval Note

**Section:** Engineering Specification — Section 3a: Feature Engineering
**Section path:** `docs/engineering_spec/03a_feature_engineering.md`
**Locked version:** v1.0 LOCKED / APPROVED
**Approval date:** 2026-04-29
**Approver:** Jeremy
**Builder:** Claude
**QA Reviewer:** ChatGPT

**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Section 1 approval note (`docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`)
- Section 2 approval note (`docs/reviews/2026-04-27_spec_02_data_layer_approval.md`)
- Section 2 traceability updates (`docs/reviews/2026-04-27_spec_02_data_layer_traceability_updates.md`)
- Section 3 handoff packet (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`)
- Section 3a traceability updates (`docs/reviews/2026-04-29_spec_03a_feature_engineering_traceability_updates.md`)
- `docs/traceability_matrix.md` (post-merge state, after the Section 3a lock merge applies the companion traceability updates)

---

## 1. What this approval covers

Approval of Section 3a v1.0 LOCKED / APPROVED locks the following at the feature-engineering level. All decisions below were the subject of explicit Approver direction during the v0.1 → v0.2 → v0.3 → v0.4 → v1.0 process trail in §2 below.

### 1.1 Write contract

1. **03a writes only to `features.*`.** The four tables under the `features` schema are: `features.feature_runs`, `features.feature_definitions`, `features.feature_values`, `features.feature_run_issues`.
2. **03a does not write to `ops.data_quality_exceptions` or any `ops.*` table.** Per Section 2 v1.0 LOCKED, `ingestion/` is the only emitter of `ops.data_quality_exceptions` rows in Phase 1; the framework remains ingestion-owned and unmodified by 03a. 03a does not write to `universe.*`, `prices.*`, `targets.*` (03b), `models.*` (03c), MLflow, or any provider table.
3. **`features.feature_run_issues` is the Phase 1 feature-layer issue log.** It records data-quality and operational issues that arise during a feature run (index-only-benchmark inability, blocked invalidated snapshot, blocked failed/partial ingestion-run dependency, failed feature run).
4. **`features.feature_run_issues` is separate from Section 2's ingestion-owned `ops.data_quality_exceptions` framework.** The two are deliberately separate: `ops.data_quality_exceptions` is the cross-cutting nine-field SDR Decision 11 report owned by `ingestion/`; `features.feature_run_issues` is a narrower, feature-run-scoped log used by 03a (and read by Section 6 UI surfaces and by 03c / Section 4 consumers as needed).

### 1.2 Blocked-run lifecycle

5. **Blocked feature runs use the open-run-before-validation lifecycle.** The orchestrator opens the `features.feature_runs` row (with `status='running'`) **before** validating the selected `data_snapshot_id`, the snapshot's `status`, and the ingestion-run dependencies covering the snapshot's price data. If any of those validations fail — invalidated snapshot, failed ingestion run, or (Phase 1 default) partial ingestion run — the orchestrator (a) marks the run row `status='failed'`, (b) populates `error_message` and `completed_at_utc`, (c) writes the appropriate `features.feature_run_issues` row (FK satisfied because the run row is already open), and (d) writes **no** `features.feature_values` rows for that run.
6. **`features.feature_run_issues.feature_run_id` remains NOT NULL and FK-protected** to `features.feature_runs(feature_run_id)`. The FK is never relaxed. There is no scenario in 03a in which a `feature_run_issues` row exists without a corresponding `feature_runs` row.

### 1.3 `feature_set_version` integrity (database-level)

7. **`feature_set_version` integrity is enforced at the database level**, not only at the orchestrator level, via three constraints:
   - `UNIQUE (feature_run_id, feature_set_version)` on `features.feature_runs` (so the pair can be the target of a foreign key);
   - composite FK `(feature_run_id, feature_set_version) → features.feature_runs(feature_run_id, feature_set_version)` on `features.feature_values` (rejects a `feature_values` row whose `feature_set_version` does not match its linked run's `feature_set_version`);
   - composite FK `(feature_set_version, feature_name) → features.feature_definitions(feature_set_version, feature_name)` on `features.feature_values` (rejects a `feature_values` row whose `feature_name` is not catalogued for the active `feature_set_version`).
   The orchestrator's pre-write invariant check is retained as a clearer-error layer above the database constraints.

### 1.4 Index-only benchmark behavior (interim)

8. **Index-only benchmark behavior remains:**
   - Family 4 (benchmark-relative excess return) is **null/unavailable** for an ETF/date when the primary benchmark resolves index-only (`universe.benchmarks.index_symbol` set, `etf_id IS NULL`).
   - **No silent benchmark substitution.**
   - **No fallback to `secondary_benchmark_id`** in Phase 1 03a. The benchmark-relative calculator reads only `primary_benchmark_id`.
   - A `severity='warning'` row with `issue_type='index_only_benchmark'` is recorded in `features.feature_run_issues`, with per-ETF / per-date / per-feature scoping.
   - The structural gap (no benchmark price storage for index-only benchmarks) remains an Open Question for the Approver and a possible future Section 2 amendment for benchmark price storage. **This approval does not propose that amendment.**

### 1.5 Feature surface, alignment, and lifecycle gating

9. **Eligibility-row omission contract remains approved.** 03a does not write `features.feature_values` rows for ETF/date pairs that are not rank-eligible per `universe.etf_eligibility_history` as of signal date `T`. Lifecycle bounds (`T < first_traded_date(e)` or `T >= delisted_date(e)`) likewise produce no row. Feature-row existence does not imply portfolio action or model promotion — those gates remain Section 4 / Section 5 / 03c concerns — but rank-ineligible ETF/date pairs do not appear in `features.feature_values`.
10. **T-1 trading-day semantics remain approved.** `T` is the signal date; `T-1` is the most recent valid trading day strictly before `T` for the relevant ETF (and benchmark, evaluated independently against its own trading-day index per `prices.etf_prices_daily`). `T-1` is **not** a calendar date minus one day. Weekend, holiday, and cross-series alignment are tested per family.
11. **Regime primitive remains default off.** The SPY-vs-200-day-moving-average primitive (`regime_spy_above_sma_200`) is disabled by default in `config/features.yaml`. Activation requires explicit Approver direction and, per §6.2.5 of the section, materialization as repeated rows for each eligible ETF/date using real `etf_id` values (no synthetic placeholders). The full `regime/` subpackage, `regime.*` schema, and SDR Decision 9 reporting layer remain outside 03a.

### 1.6 Ownership boundaries with 03b and 03c

12. **03b owns target generation.** Regression and classification target generation, forward excess-return labels over 63 and 126 trading days, label alignment to the `(etf_id, as_of_date)` axis 03a establishes, overlapping-label handling per SDR Decision 7 and Decision 16, and target tests remain entirely 03b's responsibility.
13. **03c owns the model layer, MLflow writer-side integration, `rank_method` semantics, and `config/model.yaml`.** Specifically: baseline model implementations per SDR Decision 6, the calibration pipeline per SDR Decision 7, MLflow client-side integration per SDR Decision 11, the model registry schema (`models.*`), the model state lifecycle per SDR Decision 12, the allowed values and semantics for `rank_method` (closing the Section 2 `pending_section_3` sentinel obligation), the combined-score formula per SDR Decision 6, and the linkage from MLflow runs back to `features.feature_runs.feature_run_id`.

### 1.7 Approval Matrix items satisfied (per EW §2.3)

The following Approval Matrix items are satisfied by this approval:

- **Engineering Specification section finalization** (per EW §3.4): all eleven template fields populated; section committed to `docs/engineering_spec/`; QA review per EW §3.4 item 9 satisfied via Approver-direct iterative review across v0.1 → v0.2 → v0.3 → v0.4 with explicit revision lists at each step.
- **Database schema changes** at the spec level (the `features.*` schema: four tables, indexes, FK and UNIQUE constraints).
- **Strategy-affecting YAML config changes** at the spec level (`config/features.yaml` shape and validation rules; this is the "feature parameters" file named in EW §7).

The following Approval Matrix items are **explicitly not** satisfied by this approval and remain pending later sections:

- Target labels, ranking math, and combined-score formula — 03b and 03c.
- Allowed `rank_method` values — 03c (closing the Section 2 `pending_section_3` sentinel obligation).
- Model promotion gates per SDR Decision 12 — 03c (state column) and Section 4 / Section 5 (gate evaluation).
- Risk rules, transaction-cost assumptions, portfolio rules — Sections 4 and 5.
- Any broker / order-intent behavior, any code path enabling live trading — Section 5 and the project's Phase 1 closure.

---

## 2. Process trail

1. **Section 3 handoff packet** authorized Section 3 drafting after Section 2 lock, naming SDR v1.0 LOCKED, EW v1.5 LOCKED, Section 1 v1.0 LOCKED, and Section 2 v1.0 LOCKED as controlling documents (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`).
2. **03a-specific drafting direction** issued by the Approver authorizing the 3a / 3b / 3c split with sequencing 3a → 3b → 3c, the canonical filename `03c_model_layer_mlflow.md` for the model-layer subsection, and the index-only-benchmark interim behavior (no silent substitution, no Section 2 amendment in 03a).
3. **v0.1 drafted** by the Builder. Eleven EW §3.2 template fields populated in order. SDR Decisions 1, 2, 3, 4, 5, 6, 7, 9, 11, 16 cited as directly implemented or respected. Open Questions and Proposed defaults visibly classified per EW §3.3.
4. **v0.1 → v0.2 revision pass** by the Approver against v0.1 produced seven targeted revisions: eligibility-row omission contract resolved (replacing v0.1 §10.9 incorrect Implementation-default classification with an Approver-resolved default); `ops.data_quality_exceptions` write contract clarified via the `common/` data-quality framework (subsequently superseded in v0.3); regime-primitive storage ambiguity removed (no synthetic `etf_id`); feature-run atomicity contract clarified (transactional batches; failed-run consumption discipline); referential integrity between `feature_values` and `feature_definitions` made explicit (Option A composite FK); T-1 trading-day semantics defined explicitly with weekend / holiday / cross-series tests; and accepted v0.1 defaults preserved.
5. **v0.2 → v0.3 revision pass** by the Approver produced two targeted revisions plus a preservation note: `ops.data_quality_exceptions` write path withdrawn entirely (per Section 2 v1.0 LOCKED, the framework remains ingestion-owned), with a new `features.feature_run_issues` table (Option A) introduced inside the `features` schema as the feature-layer issue log; `feature_set_version` integrity strengthened to database-level enforcement via `UNIQUE (feature_run_id, feature_set_version)` on `features.feature_runs` plus composite FK from `features.feature_values`; v0.2 accepted improvements preserved.
6. **v0.3 → v0.4 revision pass** by the Approver produced four targeted revisions: blocked-run lifecycle ambiguity resolved (open-run-before-validation lifecycle adopted as the single rule, ensuring `features.feature_run_issues.feature_run_id` FK is never relaxed); §12 handoff inventory updated to enumerate all four `features.*` tables; §13 Decision 11 traceability text updated to mention `feature_run_issues` and the explicit ingestion-owned status of `ops.data_quality_exceptions`; v0.2 changelog superseded note added.
7. **v0.4 → v1.0 lock authorization** by the Approver. v0.4 promoted to v1.0 LOCKED / APPROVED with no substantive change to behavior, schema, tests, scope, or ownership; locking metadata flipped (status header, end-of-document marker); minor wording cleanup applied to remove stale "v0.X scope" references from current spec body where not in historical changelog entries (replaced with "v1.0" or "current 03a scope" as appropriate). Historical v0.1 → v0.4 changelog entries are preserved verbatim. The Approver exercised final-decision authority per EW §2.1 and approved without an additional QA cycle on v0.4.

---

## 3. Companion artifacts

- **Approved spec section:** `docs/engineering_spec/03a_feature_engineering.md` (v1.0 LOCKED / APPROVED).
- **This approval note:** `docs/reviews/2026-04-29_spec_03a_feature_engineering_approval.md`.
- **Section 3a traceability updates:** `docs/reviews/2026-04-29_spec_03a_feature_engineering_traceability_updates.md`. Proposes replacement rows for SDR Decisions 1, 2, 3, 4, 5, 6, 7, 9, 11, 16 in `docs/traceability_matrix.md`, in the same shape as the Section 2 traceability-updates companion file. Application of the proposed replacement rows to `docs/traceability_matrix.md` is performed by the Approver as part of the Section 3a lock merge.
- **Section 3 handoff packet** (received pre-drafting): stored under `docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md` per EW §2.2.

---

## 4. Conditions on subsequent sections

Section 3a v1.0 LOCKED / APPROVED imposes the following constraints on Sections 3b, 3c, 4, 5, and 6. Any change to these requires a Section 3a amendment with Approver approval per EW §3.3 (no assumption drift) and EW §2.3 (Approval Matrix), not silent override:

1. **The eligibility-row omission contract** (rank-ineligible ETF/date pairs absent from `features.feature_values`) stands. Downstream consumers do **not** filter by re-deriving eligibility from `universe.etf_eligibility_history`; absence in `features.feature_values` is the consumption-side signal, alongside the run-status filter from constraint #4 below. Downstream consumers may still re-consult `universe.etf_eligibility_history` for as-of-date ETF lifecycle queries unrelated to feature consumption.
2. **The adjusted-close convention as canonical research price** stands at the feature level. Any 03b target, 03c model, or Section 4 backtest computation that uses a non-adjusted price is forbidden without explicit Approver approval and a Section 2 amendment.
3. **The provider-abstraction boundary** stands at the feature level. No 03b, 03c, Section 4, or Section 6 module imports from `quant_research_platform.providers` or any provider-specific library; data flows exclusively from Postgres.
4. **The failed-run consumption-side discipline** stands. Downstream consumers — 03b, 03c, Section 4 — must filter `features.feature_values` rows on `features.feature_runs.status='succeeded'`; partial rows from failed runs are retained in the table but must not enter consumable surfaces. Tests in 03b, 03c, and Section 4 must verify this filter on every feature consumption path.
5. **The `feature_set_version` integrity contract** (the three database-level constraints in §1.3 above) stands. Any later feature-set-version evolution must respect the FK chain.
6. **The `data_snapshot_id` reproducibility chain** stands. 03c MLflow runs must link back to `features.feature_runs.feature_run_id`, which transitively links to `ops.data_snapshots.data_snapshot_id` for the EW §7 reproducibility list. 03c may not bypass this chain.
7. **The `features.feature_run_issues` schema** stands. The closed enumeration on `issue_type` (`'index_only_benchmark'`, `'invalidated_snapshot_blocked'`, `'failed_ingestion_run_blocked'`, `'partial_ingestion_run_blocked'`, `'feature_run_failed'`) is closed; new types require an 03a amendment, not a 03b / 03c / Section 4 / Section 6 ad-hoc string. The two-severity enumeration (`'warning'`, `'fail'`) is likewise closed.
8. **The `ops.data_quality_exceptions` framework remains ingestion-owned and unmodified by 03a.** No later section may reframe 03a as a writer to this table without a Section 2 amendment. Any future amendment that opens the framework to feature-level emitters is a separate Approver decision.
9. **The T-1 trading-day semantics** stand. 03b target alignment, 03c model training data assembly, and Section 4 walk-forward harness must consume features without redefining `T-1` (e.g., must not silently switch to calendar-day semantics for any column).
10. **The benchmark-resolution interim constraint** stands. 03b, 03c, Section 4, and Section 6 may not introduce a fallback-to-secondary-benchmark mechanism without Approver approval; the no-silent-benchmark-substitution rule is global to the feature surface.
11. **`config/features.yaml`** is the only YAML file 03a owns. 03b owns target-related YAML (if any), 03c owns `config/model.yaml`. Cross-file coupling (e.g., 03c reading `feature_set_version` to choose a model variant) is permitted on the read side only.

---

## 5. Open items handed forward

### 5.1 Open items handed forward to 03b

- **Target generation against the same `(etf_id, as_of_date)` axis 03a establishes.** 03b will define the regression and classification target schemas, the 63/126-day forward-horizon labels, the overlapping-label handling discipline, and the label alignment tests. 03b consumes `features.feature_values` filtered on `features.feature_runs.status='succeeded'` and respects the eligibility-row omission contract.
- **Persistence vs. on-the-fly target computation** (Builder default proposal in the Section 3 handoff packet: persist with `data_snapshot_id` linkage). 03b will land this decision under EW §3.3 classification.

### 5.2 Open items handed forward to 03c

- **Allowed `rank_method` values and semantics** (closing the Section 2 `pending_section_3` sentinel obligation). 03c will define the closed enumeration, the per-sleeve semantics, and the validation that every `universe.etfs.rank_method` is one of the allowed values before any ranking runs.
- **Combined-score formula per SDR Decision 6** (first testable formula; explicit Approver direction at 03c handoff time).
- **Phase 1 baseline model forms** under SDR Decision 6's dual-target framework.
- **Calibration method choice** per SDR Decision 7 (Platt, isotonic, logistic-on-folds, or a combination).
- **Combined-score × sleeve-aware ranking interaction** — whether the combined score is computed before or after sleeve-aware ranking, and whether an ETF eligible across multiple sleeves is ranked once or once per sleeve.
- **`models.*` schema, model state lifecycle (Active/Warning/Paused/Retired) per SDR Decision 12, MLflow writer-side integration linked back to `features.feature_runs.feature_run_id`, and `config/model.yaml`.**

### 5.3 Open items handed forward to Section 4

- **Walk-forward validation harness** consuming the Section 3a feature surface (filtered on `feature_runs.status='succeeded'`) and the 03b targets, with purge/embargo enforcement per SDR Decision 7 and Decision 16.
- **Backtest reproducibility** anchored on the `data_snapshot_id` chain established by 03a.
- **Regime reporting layer** per SDR Decision 9 (the full reporting layer; 03a's feature-side primitive remains a feature input only).

### 5.4 Open items handed forward as Approver Open Questions (still open after this approval)

- **Index-only benchmark structural gap** (03a §10.1). The Approver may at any time direct (a) acceptance of the interim constraint as the durable Phase 1 behavior, (b) a Section 2 amendment to add benchmark price storage (e.g., a `prices.benchmark_prices_daily` table for index-backed benchmarks), or (c) a different resolution. **No such amendment is proposed by Section 3a v1.0.**
- **Phase 1 feature families and lookback windows** (03a §10.2), **long-form vs wide feature storage** (§10.3), **`data_snapshot_id` linkage granularity** (§10.4), **cross-sectional feature treatments** (§10.5), **regime primitive activation** (§10.6), **liquidity feature inclusion** (§10.7), **missing-data rule within a feature window** (§10.8). These remain Builder Proposed defaults the Approver may revise via 03a amendment at any time without disturbing the locked structural contracts in §1 above.

---

## 6. Implementation status

**No implementation or code has started for Section 3a.** The locked spec is a specification, not a build. The migration script that creates the `features.*` schema, the calculator modules under `features/`, the `config/features.yaml` file, and the test files under `tests/unit/features/` and `tests/integration/features/` will be authored under the standard EW §3 → §10 build workflow after 03b and 03c are also locked, or earlier if the Approver authorizes a partial build.

The constraints in §4 above bind both the spec phase (no 03b / 03c / Section 4 / Section 6 spec content may contradict them) and the implementation phase (no code may bypass them).

---

## 7. Approval

The Approver has reviewed Section 3a v1.0 LOCKED / APPROVED at `docs/engineering_spec/03a_feature_engineering.md`, the companion traceability updates at `docs/reviews/2026-04-29_spec_03a_feature_engineering_traceability_updates.md`, and the post-merge state of `docs/traceability_matrix.md`, and approves the section as locked. Subsequent changes follow EW amendment discipline.

**Signed:** Jeremy (Approver), 2026-04-29.

---

**End of approval note.**
