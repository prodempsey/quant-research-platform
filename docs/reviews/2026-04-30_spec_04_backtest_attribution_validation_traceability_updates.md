# Section 4 — Proposed Traceability Matrix Updates (v0.7)

**Source section:** Engineering Specification — Section 4: Backtest, Attribution, and Validation (approved as v1.0 LOCKED / APPROVED, 2026-04-30)
**Target file:** `docs/traceability_matrix.md`
**Action:** Replace the rows for SDR Decisions 7, 8, 9, 11, and 16 with the rows below; transition statuses where indicated. Decisions 1, 2, 3, 4, 5, 6, 12, and 17 retain their existing rows with row text extended to record Section 4's downstream-consumer references where relevant. No new SDR decisions are introduced.

The format and column headers match the existing `docs/traceability_matrix.md` table after the Section 3c lock merge (matrix v0.6).

**v0.7 of the matrix** corresponds to the v1.0 LOCKED / APPROVED version of Section 4. There is one version of this companion artifact; the "v0.7" suffix follows the Section 2 / 3a / 3b / 3c companion convention of versioning the matrix file independently of the companion file.

---

## Replacement rows

### Decision 7 — Validation method (walk-forward with 126-day purge/embargo)

| SDR Decision | Spec Section(s) | Module(s) | Config File(s) | Required Tests | Approval Gate | Status |
|---|---|---|---|---|---|---|
| Decision 7 — Validation method (walk-forward with 126-day purge/embargo) | 03c (calibration pipeline, held-out fold consumption); **04 — Backtest, Attribution, and Validation (walk-forward harness, fold construction with Option C non-partition geometry, purge / embargo arithmetic over 03b-recorded `entry_date` / `exit_date`, OOS qualification with v0.3 R2 correction — purge applies to training candidates only, leakage tests, all-folds-failed terminal case, snapshot-upper-bound respect)** | 03c calibration; **04 `backtest/` harness, `backtest/` metrics module, `backtest/` issue logger** | `config/model.yaml` (calibration); **`config/backtest.yaml` (fold geometry, embargo width, allocation contract, metric set, attribution components, regime-classifier-unavailable behavior, cost-config-missing behavior, MLflow backtest-experiment flag, validation rejections)** | 03c calibration tests; **04 §8.1 WF-* (WF-01 through WF-05 including all-folds-failed terminal case), §8.2 PE-*, §8.3 OOS-* (OOS-03 rewritten in v0.3 R2), §8.4 LK-* (LK-01 window-vs-window per v0.2 R6)** | Approver per Approval Matrix | in spec (calibration; walk-forward harness, fold construction, purge / embargo arithmetic, OOS qualification, leakage tests, all-folds-failed terminal case) |

### Decision 8 — Transaction cost and account-type assumptions

| SDR Decision | Spec Section(s) | Module(s) | Config File(s) | Required Tests | Approval Gate | Status |
|---|---|---|---|---|---|---|
| Decision 8 — Transaction cost and account-type assumptions | **04 — Backtest, Attribution, and Validation (consumption seam over the SDR-locked four-value bucket enumeration `ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`; long-only-corrected cost formula on entries and exits; cost_bucket CHECK constraint on `backtest.simulated_fills`; pipeline-validation-only labeling on zero-cost-fallback runs per A-PRP-04-35 / A-PRP-04-36)** | **04 `backtest/` cost-application module** | **`config/costs.yaml` (Section 4 owned at file level per Section 1; per-bucket basis-point values await Approver direction); `config/backtest.yaml` `cost_application` and `simulated_fills.cost_bucket_enum`** | **04 §8.5 SF-06 (long-only-corrected cost formula), §8.10 CFG-04 (locked-bucket-enum validator), §8.7 REP-06 (pipeline-validation-only flag wired to cost-config zero-fallback)** | Approver per Approval Matrix | in spec (consumption seam, locked bucket names, long-only cost formula, pipeline-validation-only labeling); pending (per-bucket basis-point values, account-type rule cash-out) |

### Decision 9 — Regime taxonomy and reporting

| SDR Decision | Spec Section(s) | Module(s) | Config File(s) | Required Tests | Approval Gate | Status |
|---|---|---|---|---|---|---|
| Decision 9 — Regime taxonomy and reporting | **04 — Backtest, Attribution, and Validation (consumption / reporting side: `backtest.regime_metrics` schema with surrogate PK and logical UNIQUE constraint per A-PRP-04-37; partial-dimension fallback per SDR Decision 9 deferral rule; `regime_reporting` block in `config/backtest.yaml`)** | **04 `regime/` reporter (consumption side); regime classifier (labeler) ownership unresolved per A-OQ-04-07 — Option A (Section 4 owns) Builder recommended; Option B (future approved amendment / sub-section)** | **`config/regime.yaml` (Sections 3 and 4 jointly per Section 1; computation thresholds populated by whichever owner the Approver resolves under A-OQ-04-07)** | **04 §8.8 RG-01, §8.12 FM-11 (regime-conditioned performance correctness), §8.14 UNI-03 (logical uniqueness on `backtest.regime_metrics`)** | Approver per Approval Matrix | in spec (reporting / consumption side); pending (regime classifier / labeler ownership — A-OQ-04-07) |

### Decision 11 — MLOps storage and tracking

| SDR Decision | Spec Section(s) | Module(s) | Config File(s) | Required Tests | Approval Gate | Status |
|---|---|---|---|---|---|---|
| Decision 11 — MLOps storage and tracking | 03c (Postgres SOR for model layer, MLflow tracking, model-tracking writer-side discipline); **04 — Backtest, Attribution, and Validation (`backtest.*` schema, `attribution.*` schema, attribution-storage half of MLOps storage, reproducibility chain extension through `data_snapshot_id`, attribution-failure open-run-before-validation lifecycle per v1.0 Correction 3, surrogate-PK + logical-UNIQUE design on metric tables per A-PRP-04-37, explicit `simulated_weight_before` / `_after` / `_delta` columns on `backtest.simulated_fills` per A-PRP-04-33, first-class `horizon_trading_days` and `sleeve_id` dimensions on metric tables per A-PRP-04-34, optional Section 4 MLflow backtest experiments per A-PRP-04-12)** | 03c `models/` writer; **04 `backtest/` harness, `attribution/` decomposer** | 03c `config/model.yaml`; **04 `config/backtest.yaml` (closed-set field enumerations including `metric_name`, `attribution_components`, MLflow backtest-experiment flag, required-tag set when enabled)** | 03c CC-* / SQL contract tests; **04 §8.6 CC-* (write-discipline static checks), §8.7 REP-* (REP-01 through REP-07 reproducibility, snapshot-id chain, idempotency, current-survivor disclosure persistence, pipeline-validation-only flag wiring, cross-section enforcement reservation), §8.9 AT-* (AT-01 through AT-04 attribution correctness including AT-04 attribution-run open-run-before-validation), §8.12 FM-15 / FM-16 (horizon-dimensioned correctness; `metric_name` purity), §8.14 UNI-01 / UNI-02 / UNI-03 (logical uniqueness on metric tables)** | Approver per Approval Matrix | in spec (Postgres SOR, MLflow tracking, model-tracking writer-side, `backtest.*` schema, `attribution.*` schema, attribution-storage half, reproducibility chain extension) |

### Decision 16 — Phase 1 success criteria and bias controls

| SDR Decision | Spec Section(s) | Module(s) | Config File(s) | Required Tests | Approval Gate | Status |
|---|---|---|---|---|---|---|
| Decision 16 — Phase 1 success criteria and bias controls | 01 (time-aware research auditability invariant); 02 (data snapshot lifecycle, current-survivor disclosure storage and `common.get_current_survivor_label()` retrieval, ingestion-owned data-quality exception logging); 03a (T-1 contract, feature-target alignment, no-fundamentals/holdings/news/earnings/options at the feature layer); 03b (per-row forward-label window metadata, target-side T-1 contract, no-fundamentals/holdings/news/earnings/options at the target layer); 03c (calibration pipeline, prediction context closed enumeration, no-fundamentals/holdings/news/earnings/options at the model layer); **04 — Backtest, Attribution, and Validation (OOS qualification rule with v0.3 R2 purge-applies-to-training-only correction; purge / embargo arithmetic using 03b-recorded forward-label windows on both sides per v0.2 R6; v0.3 R1 Option C non-partition fold geometry; backtest-only simulated allocation contract per §6.4.1 explicitly not Section 5 portfolio behavior; explicit simulated weights per A-PRP-04-33; `backtest.backtest_runs.is_pipeline_validation_only` + `pipeline_validation_only_reason` per A-PRP-04-35 / A-PRP-04-36 — zero-cost-fallback runs structurally labeled non-promotion-evidence; metrics tables dimensioned by `horizon_trading_days` and `sleeve_id` per A-PRP-04-34 with surrogate PKs per A-PRP-04-37; `backtest.backtest_run_issues.issue_type='all_folds_failed'` per v0.3 R7 — terminal-case bias control; reproducibility chain through `data_snapshot_id`; financial metric definitions with formulas per §6.10; current-survivor disclosure persistence per A-PRP-04-31; validation evidence surface per §6.9)** | 02 ingestion + disclosure modules; 03a `features/`; 03b `targets/`; 03c `models/`; **04 `backtest/`, `attribution/`, `regime/` (consumption)** | 02 `config/universe.yaml` `disclosures.current_survivor_label`; 03a `config/features.yaml`; 03b `config/targets.yaml`; 03c `config/model.yaml`; **04 `config/backtest.yaml`** | 02 disclosure tests; 03a / 03b / 03c bias-control tests; **04 §8.1 WF-05 (all-folds-failed terminal-case test), §8.2 PE-* (purge / embargo enforcement using 03b-recorded forward-label windows), §8.4 LK-01 (window-vs-window leakage test), §8.7 REP-05 (current-survivor disclosure persistence), REP-06 (pipeline-validation-only flag wiring), REP-07 (cross-section enforcement reservation for Section 5), §8.9 AT-04 (attribution-run open-run-before-validation), §8.12 FM-* (financial-meaning metric tests), §8.13 ALC-* (allocation-contract not-Section-5-portfolio-behavior tests), §8.14 UNI-* (logical uniqueness on metric tables)** | Approver per Approval Matrix | in spec (data-layer auditability, feature/target/model auditability, backtest/attribution auditability); pending (UI disclosure surfacing — Section 6) |

---

## Rows extended with Section 4 downstream-consumer references (no status change)

### Decision 1 — Phase 1 scope (ETF tactical research, no live trading)

Row text extended to record Section 4's contribution: **Section 4 modules under `backtest/`, `attribution/`, and `regime/` (consumption) do not import from `providers/` and do not read from any provider table; the `backtest.simulated_fills.action` closed enum is intentionally disjoint from any future Section 5 portfolio-action vocabulary; no live-broker code path; CC-04 and CC-05 verify.** Status remains `in spec`.

### Decision 2 — Open architecture / open data layer

No change.

### Decision 3 — Universe survivorship (no historical proxies for delisted ETFs)

Row text extended to record Section 4's contribution: **Section 4 inherits eligibility-row omission and lifecycle-bound absence transitively; current-survivor disclosure label persisted on every `backtest.backtest_runs` row per A-PRP-04-31, sourced from Section 2 `common.get_current_survivor_label()`.** Status remains `in spec`.

### Decision 4 — Universe survivorship and ETF launch-date handling

Row text extended to record Section 4's contribution: **`backtest.backtest_runs.current_survivor_disclosure_label` NOT NULL column populated at run-open time from `common.get_current_survivor_label()`; REP-05 verifies disclosure attachment on every backtest output for downstream UI surfacing per Section 6.** Status remains `in spec`.

### Decision 5 — Benchmark, sleeve, and diversifier treatment

Row text extended to record Section 4's contribution: **Section 4 reads `rank_method` per sleeve and respects `DiversifierHedge` zero-rows contract; `backtest.fold_metrics`, `backtest.aggregate_metrics`, `backtest.regime_metrics` carry first-class `sleeve_id` dimension (nullable; participates in logical uniqueness, not PK) per A-PRP-04-34; `sleeve_level_performance` metric and `benchmark_relative_return` rollup per A-PRP-04-27.** Status remains `in spec`.

### Decision 6 — Target design and combined score philosophy

Row text extended to record Section 4's contribution: **Section 4 reads `models.combined_scores` produced under the 03c first-testable formula; the §6.4.1 backtest-only simulated allocation contract uses combined-score ranking per `(sleeve_id, horizon_trading_days)` cross-section; `metric_name` purity verified by FM-16 / UNI-01.** Status remains `in spec` (first testable variant; activation of the reserved 4-component variant remains pending).

### Decision 12 — Model promotion gates and kill switch

Row text extended to record Section 4's contribution: **Section 4 produces validation evidence consumed by Section 5's promotion gate; `is_pipeline_validation_only = false` filter is required for promotion-eligibility evaluation per A-PRP-04-35 (REP-07 reserves the cross-section static check that runs after Section 5 implementation lands); A-OQ-04-14 Active → Warning trigger remains an Open Question and requires a 03c amendment to integrate with `models.model_versions.state` lifecycle.** Status remains split: model-state lifecycle schema and audit `in spec` (03c, including the first promotion gate); second promotion gate, kill switch, and Active → Warning trigger remain `pending` (Section 5 plus an Open Question for the trigger definition).

### Decision 17 — UI is read-only

Row text extended to record Section 4's contribution: **`backtest.*` and `attribution.*` schemas are read-only-consumable by Section 6; `current_survivor_disclosure_label` and `is_pipeline_validation_only` flag are read-only surfaces for Section 6 disclosure rendering.** Status remains `in spec` (read-only contract reserved; Section 6 owns the rendering).

---

## Audit findings

No label findings. Decisions 7, 8, 9, 11, 16 labels in matrix v0.6 align acceptably with the locked SDR v1.0 labels.

---

## Notes for the matrix maintainer (Approver)

- **Decision 7 status form** uses an extended in-line list to preserve the single-row-per-decision convention while making the post-Section-4 coverage explicit. Decision 7 is now fully `in spec` for Phase 1 scope; what remains `pending` is the build under §10 of EW after the Approver authorizes a build cycle.
- **Decision 8 status form** uses the split form `in spec (consumption seam, locked bucket names, long-only cost formula, pipeline-validation-only labeling); pending (per-bucket basis-point values, account-type rule cash-out)`. This makes the gap between "Section 4 specifies the seam" and "the bucket-to-bps values exist" explicit.
- **Decision 9 status form** uses the split form `in spec (reporting / consumption side); pending (regime classifier / labeler ownership — A-OQ-04-07)`. This preserves Section 4's contribution while flagging the unresolved labeler ownership.
- **Decision 16 row** was already long; with Section 4 added it is now the longest row in the matrix. A row split into 16a (data-layer auditability), 16b (feature/target/model auditability), 16c (backtest/attribution auditability), 16d (UI disclosure surfacing) was deferred at Section 2 lock and remains deferred — Section 5 / Section 6 lock is a more natural moment if the row continues to grow.
- **Decisions 10, 13, 14, 15, 18** remain untouched by Section 4 and retain their post-Section-3c-lock rows.
- **`A-OQ-04-07` regime classifier ownership** is the only Open Question that touches a matrix-row status (Decision 9). The row's `pending` portion will be retired only when the Approver resolves A-OQ-04-07 either way.
- **Approval Gate column** stays `Approver per Approval Matrix` for every row; no new gate introduced.

---

**End of proposed updates.**
