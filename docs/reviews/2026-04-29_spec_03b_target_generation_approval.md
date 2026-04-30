# Engineering Specification Section 3b — Target Generation: Approval Note

**Section:** Engineering Specification — Section 3b: Target Generation
**Section path:** `docs/engineering_spec/03b_target_generation.md`
**Locked version:** v1.0 LOCKED / APPROVED
**Approval date:** 2026-04-29
**Approver:** Jeremy
**Builder:** Claude
**QA Reviewer:** ChatGPT

The section was iterated under direct Approver review across drafts v0.1 → v0.2 → v0.3, with each round producing an explicit revision list (six revisions for v0.2, one cleanup for v0.3, plus minor wording cleanup at locking). The Approver's final review serves as the QA pass per EW §3.4 item 9.

**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Engineering Specification — Section 3a v1.0 LOCKED / APPROVED (`docs/engineering_spec/03a_feature_engineering.md`)
- Section 1 approval note (`docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`)
- Section 2 approval note (`docs/reviews/2026-04-27_spec_02_data_layer_approval.md`)
- Section 2 traceability updates (`docs/reviews/2026-04-27_spec_02_data_layer_traceability_updates.md`)
- Section 3 handoff packet (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`)
- Section 3a approval note (`docs/reviews/2026-04-29_spec_03a_feature_engineering_approval.md`)
- Section 3a traceability updates (`docs/reviews/2026-04-29_spec_03a_feature_engineering_traceability_updates.md`)
- Section 3b traceability updates (`docs/reviews/2026-04-29_spec_03b_target_generation_traceability_updates.md`)
- `docs/traceability_matrix.md` (post-merge state, after the Section 3b lock merge applies the companion traceability updates)

---

## 1. What this approval covers

Approval of Section 3b v1.0 LOCKED / APPROVED locks the following at the target-generation level. All decisions below were the subject of explicit Approver direction during the v0.1 → v0.2 → v0.3 → v1.0 process trail in §2 below.

### 1.1 Write contract

1. **03b writes only to `targets.*`.** The four tables under the `targets` schema are: `targets.target_runs`, `targets.target_definitions`, `targets.target_values`, `targets.target_run_issues`.
2. **03b does not write to `ops.data_quality_exceptions` or any `ops.*` table.** Per Section 2 v1.0 LOCKED, `ingestion/` is the only emitter of `ops.data_quality_exceptions` rows in Phase 1; the framework remains ingestion-owned and unmodified by 03b. 03b does not write to `universe.*`, `prices.*`, `features.*` (03a), `models.*` (03c), MLflow, or any provider table.
3. **`targets.target_run_issues` is the Phase 1 target-layer issue log.** It records data-quality and operational issues that arise during a target run (index-only-benchmark inability, blocked invalidated snapshot, blocked failed/partial ingestion-run dependency, failed target run).
4. **`targets.target_run_issues` is separate from Section 2's ingestion-owned `ops.data_quality_exceptions` framework.** The two are deliberately separate, parallel to the analogous separation between `features.feature_run_issues` and `ops.data_quality_exceptions` in 03a: `ops.data_quality_exceptions` is the cross-cutting nine-field SDR Decision 11 report owned by `ingestion/`; `targets.target_run_issues` is a narrower, target-run-scoped log used by 03b (and read by Section 6 UI surfaces and by 03c / Section 4 consumers as needed).

### 1.2 Blocked-run lifecycle

5. **Blocked target runs use the open-run-before-validation lifecycle.** The orchestrator opens the `targets.target_runs` row (with `status='running'`) **before** validating the selected `data_snapshot_id`, the snapshot's `status`, and the ingestion-run dependencies covering the snapshot's actual price data. The closed list of run-level blocking conditions is: (i) snapshot `status='invalidated'`; (ii) any covering ingestion run with `status='failed'`; (iii) (Phase 1 default) any covering ingestion run with `status='partial'`. If any is detected, the orchestrator marks the run `status='failed'`, populates `error_message` and `completed_at_utc`, writes the appropriate `targets.target_run_issues` row (FK satisfied), and writes **no** `targets.target_values` rows for that run. **Front-edge truncation is NOT a run-level blocking condition** — it is row-level absence per §6.5 Bucket 1.
6. **`targets.target_run_issues.target_run_id` remains NOT NULL and FK-protected** to `targets.target_runs(target_run_id)`. The FK is never relaxed. There is no scenario in 03b in which a `target_run_issues` row exists without a corresponding `target_runs` row.

### 1.3 `target_set_version` integrity (database-level)

7. **`target_set_version` integrity is enforced at the database level**, not only at the orchestrator level, via three constraints (parallel to 03a's `feature_set_version` discipline):
   - `UNIQUE (target_run_id, target_set_version)` on `targets.target_runs` (so the pair can be the target of a foreign key);
   - composite FK `(target_run_id, target_set_version) → targets.target_runs(target_run_id, target_set_version)` on `targets.target_values` (rejects a `target_values` row whose `target_set_version` does not match its linked run's `target_set_version`);
   - composite FK `(target_set_version, target_name) → targets.target_definitions(target_set_version, target_name)` on `targets.target_values` (rejects a `target_values` row whose `target_name` is not catalogued for the active `target_set_version`).
   The orchestrator's pre-write invariant check is retained as a clearer-error layer above the database constraints.

### 1.4 Phase 1 strategy-affecting target choices (Approver-resolved defaults)

8. **Entry/exit convention is Convention B: entry at `T+1` close, exit at `T+1+h` close** (per ETF's own trading-day index). The schema's `entry_offset_trading_days` and `exit_offset_trading_days` columns on `targets.target_definitions` record the convention explicitly per row; a future amendment is required to enable any other convention (Convention A is reserved as a future amendment path; current 03b scope does not enable it and the YAML validator refuses any value other than `"B"`).
9. **Classification threshold is `θ = 0.0`** — strict positive excess return defines outperformance.
10. **Missing-forward-data rule is `missing_data.rule = "null_on_any_missing_input_in_window"`** — any missing input bar in `[entry_date, exit_date]` produces a row with `target_value = NULL` (Bucket 2 of §6.5). Aligns with 03a's parallel rule.
11. **ETF-delisted-within-window rule is `forward_window.delisted_within_window_rule = "no_row"`** — when `delisted_date(e) <= exit_date(e, T, h)`, no row is written (Bucket 1 of §6.5). The alternative `"null_with_partial_flag"` is not enabled in current 03b scope; the YAML validator refuses any other value.
12. **Front-edge truncation is absence-only and not a failed run.** Signal dates whose required forward window exceeds the snapshot's `price_table_max_as_of_date` produce no rows (Bucket 1 of §6.5). The run still completes `'succeeded'` provided no run-level blocking condition (§6.3 closed list) is hit and at least some eligible rows are produced. **No `targets.target_run_issues` row** is written for front-edge truncation in current 03b scope; the closed `issue_type` enumeration does not include any `forward_window`-related value.
13. **Index-only benchmark behavior:** when the primary benchmark resolves index-only on signal date `T`, the regression target row is written with `target_value = NULL` (Bucket 2 of §6.5); the classification target row is also written with `target_value = NULL` by null propagation; a `severity='warning'` row with `issue_type='index_only_benchmark'` is recorded in `targets.target_run_issues`. **No silent benchmark substitution. No fallback to `secondary_benchmark_id`.** The structural gap (whether to ever pursue benchmark price storage via a Section 2 amendment) is preserved as the residual Open Question §10.1.

### 1.5 Configuration

14. **`config/targets.yaml` is owned by 03b** as a new strategy-affecting config file. Approved within the 03b spec approval path. **No Section 1 amendment is proposed by 03b**; targets config is not moved into `config/model.yaml`; 03c continues to own `config/model.yaml`; 03c may *read* target metadata at consumption time but does not own target config.

### 1.6 Target surface

15. **Target families are regression excess return and classification outperformance only.** No additional families in current 03b scope (no volatility-adjusted excess return, no drawdown-magnitude target, no sleeve-relative target, etc.). Additions require a future 03b amendment.
16. **Target horizons are exactly 63 and 126 trading days** per SDR Decision 6. No additions or removals. Any change requires explicit Approver direction since horizons are an SDR Decision 6 commitment.

### 1.7 Boundaries with 03a, 03c, and Section 4

17. **03b does not consume `features.feature_values` for target generation.** The forward-direction price computations 03b performs read directly from `prices.etf_prices_daily.adjusted_close`. The 03a-side filter on `features.feature_runs.status='succeeded'` therefore applies vacuously to 03b's target-generation paths.
18. **03c owns joining successful feature runs and successful target runs for model training.** Specifically: 03c is responsible for joining `features.feature_values` (filtered on `features.feature_runs.status='succeeded'`) and `targets.target_values` (filtered on `targets.target_runs.status='succeeded'`) on `(etf_id, as_of_date)` to assemble training data. 03c training-data-assembly tests must verify both filters are applied and that front-edge horizon truncation is correctly handled. 03c MLflow runs link back to both `feature_run_id` and `target_run_id` to satisfy the EW §7 reproducibility list.
19. **Section 4 owns purge/embargo enforcement.** 03b records the per-row window metadata (`signal_date`, `horizon_trading_days`, `entry_date`, `exit_date`) Section 4's walk-forward harness needs to apply purge/embargo at the train/test boundary; 03b does not apply purge/embargo at the target-emission level itself.

### 1.8 Approval Matrix items satisfied (per EW §2.3)

The following Approval Matrix items are satisfied by this approval:

- **Engineering Specification section finalization** (per EW §3.4): all eleven template fields populated; section committed to `docs/engineering_spec/`; QA review per EW §3.4 item 9 satisfied via Approver-direct iterative review across v0.1 → v0.2 → v0.3 with explicit revision lists at each step.
- **Database schema changes** at the spec level (the `targets.*` schema: four tables, indexes, FK and UNIQUE constraints).
- **Strategy-affecting YAML config changes** at the spec level (`config/targets.yaml` shape and validation rules; this is the new "target parameters" file owned by 03b).
- **Changes to feature, target, or label definitions** — the Phase 1 target families, horizons, alignment convention, and classification threshold per §1.4 and §1.6 above.

The following Approval Matrix items are **explicitly not** satisfied by this approval and remain pending later sections:

- Allowed `rank_method` values, combined-score formula, baseline model implementations, calibration pipeline, MLflow writer-side integration, model promotion gates per SDR Decision 12 — 03c.
- Walk-forward harness, purge/embargo enforcement, transaction-cost application, attribution storage — Section 4.
- Risk rules, portfolio rules — Section 5.
- Any broker / order-intent behavior, any code path enabling live trading — Section 5 and the project's Phase 1 closure.

---

## 2. Process trail

1. **Section 3 handoff packet** (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`) authorized Section 3 drafting after Section 2 lock, naming SDR v1.0 LOCKED, EW v1.5 LOCKED, Section 1 v1.0 LOCKED, and Section 2 v1.0 LOCKED as controlling documents. The same packet authorized the 3a / 3b / 3c split with sequencing 3a → 3b → 3c.
2. **Lightweight 03b handoff packet basis.** Per Approver direction, no separate Section 3b handoff packet was issued; 03b drafting and revision were authorized to proceed from four sources taken together as the de facto scope statement: (a) the current general project handoff (`docs/current_claude_context_handoff.md`); (b) Section 3a §12 forward references to 03b; (c) Section 3a approval note §5.1 *"Open items handed forward to 03b"*; (d) the targeted v0.2 revision instruction issued by the Approver on 2026-04-29 (the QA-driven revision list applied in the v0.2 pass). The 03b spec's front matter records this scope-basis language explicitly so this approval note can cite it without further amendment (Revision 6 in v0.2).
3. **v0.1 drafted** by the Builder. Eleven EW §3.2 template fields populated in order. SDR Decisions 1, 2, 3, 4, 5, 6, 7, 11, 16 cited as directly implemented or respected. Open Questions and Proposed defaults visibly classified per EW §3.3.
4. **v0.1 → v0.2 revision pass** by the Approver against v0.1 produced six targeted revisions plus preservation of accepted v0.1 strengths: (R1) snapshot forward-coverage blocking contradiction resolved; (R2) null-vs-no-row taxonomy clarified as the canonical two-bucket taxonomy in §6.5; (R3) `config/targets.yaml` file-location issue resolved without reopening Section 1; (R4) ten Approver decisions recorded as accepted defaults (entry/exit convention, classification threshold, missing-forward-data rule, ETF-delisted-within-window rule, target persistence, index-only benchmark interim behavior, config file ownership, target families, target horizons, snapshot front-edge truncation absence-only); (R5) accepted v0.1 strengths preserved; (R6) lightweight 03b handoff packet note formalized in the front matter.
5. **v0.2 → v0.3 revision pass** by the Approver produced one targeted cleanup pass: residual ambiguity around "insufficient-forward-history" and "fully observable forward window" phrasings was removed so that every reference to forward-window-coverage outcomes defers unambiguously to the §6.5 Bucket 1 / Bucket 2 taxonomy. The canonical §6.5 taxonomy itself was preserved exactly. Front-edge truncation remains absence-only and not a failed run; index-only benchmark behavior is unchanged.
6. **v0.3 → v1.0 lock authorization** by the Approver. v0.3 promoted to v1.0 LOCKED / APPROVED with **no substantive change** to behavior, schema, tests, scope, or ownership; locking metadata flipped (status header, end-of-document marker); minor wording cleanup applied to remove stale "v0.2 Revision N" / "v0.3 makes" / "in v0.2" / "in v0.2/v0.3" version markers in the current spec body where they were not historical changelog entries — replaced with "current 03b scope" or removed where they read as noise. Historical v0.1 → v0.3 changelog entries are preserved verbatim. The Approver exercised final-decision authority per EW §2.1 and approved without an additional QA cycle on v0.3.

---

## 3. Companion artifacts

- **Approved spec section:** `docs/engineering_spec/03b_target_generation.md` (v1.0 LOCKED / APPROVED).
- **This approval note:** `docs/reviews/2026-04-29_spec_03b_target_generation_approval.md`.
- **Section 3b traceability updates:** `docs/reviews/2026-04-29_spec_03b_target_generation_traceability_updates.md`. Proposes replacement rows for SDR Decisions 1, 2, 3, 4, 5, 6, 7, 11, 16 in `docs/traceability_matrix.md`, in the same shape as the Section 2 / Section 3a traceability-updates companion files. Application of the proposed replacement rows to `docs/traceability_matrix.md` is performed by the Approver as part of the Section 3b lock merge.
- **Section 3 handoff packet** (received pre-drafting for the broader Section 3 split): stored under `docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md` per EW §2.2.

---

## 4. Conditions on subsequent sections

Section 3b v1.0 LOCKED / APPROVED imposes the following constraints on Sections 3c, 4, 5, and 6. Any change to these requires a Section 3b amendment with Approver approval per EW §3.3 (no assumption drift) and EW §2.3 (Approval Matrix), not silent override:

1. **The §6.5 null-vs-no-row taxonomy** is canonical for `targets.target_values`. No 03c, Section 4, or Section 6 module may reframe Bucket 1 cases as `target_value = NULL` rows or Bucket 2 cases as row absences without an 03b amendment.
2. **The eligibility-row omission contract** (rank-ineligible ETF/date pairs absent from the surface; lifecycle-bound pairs absent; pairs whose forward window exceeds snapshot coverage absent) stands. Downstream consumers do **not** filter by re-deriving any of these conditions; absence in `targets.target_values` is the consumption-side signal, alongside the run-status filter from constraint #4 below.
3. **The adjusted-close convention as canonical research price** stands at the target level. Any 03c model or Section 4 backtest computation that uses a non-adjusted price is forbidden without explicit Approver approval and a Section 2 amendment.
4. **The failed-run consumption-side discipline** stands. Downstream consumers — 03c, Section 4 — must filter `targets.target_values` rows on `targets.target_runs.status='succeeded'`; partial rows from failed runs are retained in the table but must not enter consumable surfaces. Tests in 03c and Section 4 must verify this filter on every target consumption path. 03c must apply the equivalent filter on `features.feature_runs.status='succeeded'` simultaneously when joining feature and target rows for training data assembly.
5. **The `target_set_version` integrity contract** (the three database-level constraints in §1.3 above) stands. Any later target-set-version evolution must respect the FK chain.
6. **The `data_snapshot_id` reproducibility chain** stands. 03c MLflow runs must link back to both `targets.target_runs.target_run_id` and `features.feature_runs.feature_run_id`, which transitively link to `ops.data_snapshots.data_snapshot_id` for the EW §7 reproducibility list. 03c may not bypass this chain.
7. **The `targets.target_run_issues` schema** stands. The closed enumeration on `issue_type` (`'index_only_benchmark'`, `'invalidated_snapshot_blocked'`, `'failed_ingestion_run_blocked'`, `'partial_ingestion_run_blocked'`, `'target_run_failed'`) is closed; new types require an 03b amendment, not a 03c / Section 4 / Section 6 ad-hoc string. The two-severity enumeration (`'warning'`, `'fail'`) is likewise closed. The closed `issue_type` enumeration deliberately does not include any `forward_window`-related value (per §11.6 #10).
8. **The `ops.data_quality_exceptions` framework remains ingestion-owned and unmodified by 03b.** No later section may reframe 03b as a writer to this table without a Section 2 amendment. Any future amendment that opens the framework to feature-level or target-level emitters is a separate Approver decision.
9. **Convention B trading-day semantics** stand. 03c model training data assembly and Section 4 walk-forward harness must consume targets without redefining `entry_date` / `exit_date` (e.g., must not silently switch to calendar-day arithmetic for any target row).
10. **The benchmark-resolution interim constraint** stands. 03c, Section 4, and Section 6 may not introduce a fallback-to-secondary-benchmark mechanism without Approver approval; the no-silent-benchmark-substitution rule is global to the target surface as it is to the feature surface.
11. **`config/targets.yaml`** is the only YAML file 03b owns. 03c owns `config/model.yaml`. Cross-file coupling (e.g., 03c reading `target_set_version` from `config/targets.yaml` to choose a model variant) is permitted on the read side only.

---

## 5. Open items handed forward

### 5.1 Open items handed forward to 03c

- **Allowed `rank_method` values and semantics** (closing the Section 2 `pending_section_3` sentinel obligation). 03c will define the closed enumeration, the per-sleeve semantics, and the validation that every `universe.etfs.rank_method` is one of the allowed values before any ranking runs. 03b does not interpret `rank_method`.
- **Combined-score formula per SDR Decision 6** (first testable formula; explicit Approver direction at 03c handoff time).
- **Phase 1 baseline model forms** under SDR Decision 6's dual-target framework.
- **Calibration method choice** per SDR Decision 7 (Platt, isotonic, logistic-on-folds, or a combination).
- **Combined-score × sleeve-aware ranking interaction.**
- **`models.*` schema, model state lifecycle (Active/Warning/Paused/Retired) per SDR Decision 12, MLflow writer-side integration linked back to both `features.feature_runs.feature_run_id` and `targets.target_runs.target_run_id`, and `config/model.yaml`.**
- **Training-data assembly contract** — the join discipline on `(etf_id, as_of_date)` between feature and target rows, both filtered on `status='succeeded'`, with explicit handling of front-edge horizon truncation and the eligibility-row omission contract.

### 5.2 Open items handed forward to Section 4

- **Walk-forward validation harness** consuming the Section 3b target surface (filtered on `target_runs.status='succeeded'`) and the Section 3a feature surface (filtered analogously), with purge/embargo enforcement per SDR Decision 7 and Decision 16. Section 4 owns purge/embargo; 03b records the per-row window metadata Section 4 needs (`signal_date`, `horizon_trading_days`, `entry_date`, `exit_date`).
- **Backtest reproducibility** anchored on the `data_snapshot_id` chain established jointly by 03a and 03b.

### 5.3 Open items handed forward as Approver Open Questions (still open after this approval)

- **Index-only benchmark structural gap** (03b §10.1, inherited from 03a §10.1). The Approver may at any time direct (a) acceptance of the interim constraint as the durable Phase 1 behavior, (b) a Section 2 amendment to add benchmark price storage (e.g., a `prices.benchmark_prices_daily` table for index-backed benchmarks) — which would resolve the gap for both 03a and 03b simultaneously, or (c) a different resolution. **No such amendment is proposed by Section 3b v1.0.**

---

## 6. Implementation status

**No implementation or code has started for Section 3b.** The locked spec is a specification, not a build. The migration script that creates the `targets.*` schema, the calculator modules under `targets/`, the `config/targets.yaml` file, and the test files under `tests/unit/targets/` and `tests/integration/targets/` will be authored under the standard EW §3 → §10 build workflow after 03c is also locked, or earlier if the Approver authorizes a partial build.

The constraints in §4 above bind both the spec phase (no 03c / Section 4 / Section 6 spec content may contradict them) and the implementation phase (no code may bypass them).

---

## 7. Approval

The Approver has reviewed Section 3b v1.0 LOCKED / APPROVED at `docs/engineering_spec/03b_target_generation.md`, the companion traceability updates at `docs/reviews/2026-04-29_spec_03b_target_generation_traceability_updates.md`, and the post-merge state of `docs/traceability_matrix.md`, and approves the section as locked. Subsequent changes follow EW amendment discipline.

**Signed:** Jeremy (Approver), 2026-04-29.

---

**End of approval note.**
