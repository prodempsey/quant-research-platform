# Section 4 — Backtest, Attribution, and Validation — Approval Note

**Source section:** Engineering Specification — Section 4: Backtest, Attribution, and Validation
**Status:** v1.0 LOCKED / APPROVED
**Date:** 2026-04-30
**Spec file:** `docs/engineering_spec/04_backtest_attribution_validation.md`
**Approver:** Jeremy
**Builder:** Claude
**QA Reviewer:** ChatGPT
**Process reference:** Engineering Workflow v1.5 LOCKED, §3 (drafting), §4 (review), §3.5 (lock), §3.6 (matrix update)
**Companion artifacts:**
- This approval note: `docs/reviews/2026-04-30_spec_04_backtest_attribution_validation_approval.md`
- Traceability updates: `docs/reviews/2026-04-30_spec_04_backtest_attribution_validation_traceability_updates.md`
- Matrix file (post-merge): `docs/traceability_matrix.md` v0.7

---

## 1. Approval scope

Section 4 is approved as v1.0 LOCKED / APPROVED. The approval covers the eleven-field EW §3.2 spec content as drafted, including:

- The `backtest.*` schema (`backtest_runs`, `backtest_folds`, `simulated_fills`, `fold_metrics`, `aggregate_metrics`, `regime_metrics`, `backtest_run_issues`).
- The `attribution.*` schema (`attribution_runs`, `signal_attribution`, `trade_attribution`, `attribution_run_issues`).
- The §6.1 / 03c §12.1 invocation seam shape; Section 4 supplies fold metadata and OOS qualification rules; 03c writes.
- Walk-forward fold construction with Option C non-partition geometry; SDR Decision 7 embargo width 126 trading days as Builder Proposed default.
- The OOS qualification rule with the v0.3 R2 correction: purge / embargo applies to training candidates only; never to test-window OOS rows.
- The §6.4.1 backtest-only simulated allocation contract — explicitly not Section 5 portfolio behavior; not paper portfolio state; not order intent.
- The §6.7 cost-application consumption seam over SDR Decision 8's locked four-value bucket enumeration (`ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`).
- The §6.10 financial metric definitions table with formulas, units, annualization conventions, null behavior, and benchmark-relative behavior.
- The reproducibility chain through `data_snapshot_id` per EW §7.
- The `current_survivor_disclosure_label` NOT NULL column on `backtest.backtest_runs` per SDR Decision 4 / Decision 16.
- The `is_pipeline_validation_only` + `pipeline_validation_only_reason` columns on `backtest.backtest_runs` per v0.3 Revision 5.
- Surrogate primary keys (`fold_metric_id`, `aggregate_metric_id`, `regime_metric_id`) on the three metric tables with logical `UNIQUE NULLS NOT DISTINCT` constraints over the dimensioned tuples per v0.4 Revision 1.
- The full §8 test set across WF-*, PE-*, OOS-*, LK-*, SF-*, CC-*, REP-*, RG-*, AT-*, CFG-*, FM-*, ALC-*, and UNI-* groups.

The approval is conditional on the four lock-package corrections being folded directly into the v1.0 spec, which they are.

## 2. What was approved that was not silently resolved

The following items remain explicitly unresolved at lock and are carried forward to the Approver for separate direction; they do not block Section 4 lock because the spec specifies the structural surface around them:

- **A-OQ-04-07** — Regime classifier (labeler) ownership. Option A: Section 4 owns a minimal SDR Decision 9 labeler in `regime/` (Builder recommended). Option B: a future approved amendment / sub-section owns the labeler; Section 4 consumes only. Approver direction required before any labeler implementation begins.
- **A-OQ-04-14** — Active → Warning automated trigger. Builder does not propose a trigger in current Section 4 scope. Adoption requires a 03c amendment.
- **A-OQ-04-18** — Backtest confidence-level outputs sufficiency. Builder does not propose additional fields in current Section 4 scope. Approver may direct.

The following items are Builder Proposed defaults (A-PRP-04-01 through A-PRP-04-37, with A-PRP-04-28 retired in v0.3) and are accepted as part of this lock:

- Schemas, config shape, fold geometry (Option C), embargo 126, OOS qualification rule with v0.3 R2 correction, long-only-corrected cost formula, metric set, attribution components, residual bound 0.0001, MLflow backtest-experiments off-by-default, regime-classifier-unavailable behavior `emit_partial_with_warning`, cost-config-missing behavior `warn_proceed_zero_cost`, per-fold failure containment skip-and-continue, empty-test-window severity warning, calibrated-unavailable handling skip-the-fold, disjoint issue_type enums, action enum disjoint from Section 5, 1:1 attribution-runs-per-backtest-runs, no Section 2 amendment, no Section 1 amendment, independent lock from `config/costs.yaml` and regime-classifier resolution, top-N-per-sleeve-per-horizon allocation contract, annualization 252, risk-free rate 0.0, weighted-by-sleeve-weight benchmark-relative rollup, per-horizon keying on `simulated_fills`, regime ownership Option A recommended (subject to A-OQ-04-07), current-survivor disclosure persistence, fold geometry Option C, explicit simulated weights, first-class horizon and sleeve dimensions on metrics tables, `is_pipeline_validation_only` flag, `pipeline_validation_only_reason` closed enum, surrogate metric-table PKs with logical `UNIQUE NULLS NOT DISTINCT`.

## 3. Process discipline observed

1. **Eleven-field EW §3.2 template** populated in order in §1 through §11.
2. **EW §3.3 assumption classification** applied throughout: A-DRV-* (Derived from SDR), A-INH-* (Inherited from prior locked section), A-IMP-* (Implementation default with no strategy impact), A-PRP-04-* (Proposed default requiring approval), A-OQ-04-* (Open question for Approver).
3. **Source-of-truth hierarchy** preserved: SDR > EW > prior locked sections > traceability matrix > approval notes > current draft. No locked decision was reinterpreted, optimized, relaxed, or replaced.
4. **Surgical revisions only** through v0.1 → v0.2 → v0.3 → v0.4 → v1.0; no whole-document rewrites; historical changelog entries preserved verbatim across all version transitions.
5. **Conditions on subsequent sections** documented in §12.1 (Section 5 handoff) and §12.2 (Section 6 handoff).

## 4. Conditions on subsequent sections

Section 4 v1.0 LOCKED / APPROVED imposes the following constraints on Sections 5 and 6. Any change to these requires a Section 4 amendment per EW §3.3 / §2.3:

1. **Section 4 owns** `backtest.*` and `attribution.*` schemas. Section 5 and Section 6 read from them; neither writes.
2. **Section 4 invokes 03c** through the §6.1 / 03c §12.1 seam only. No Section 4 module imports 03c writer-side internals.
3. **Section 4 does not write** to `models.*`, `ops.*`, `features.*`, `targets.*`, `universe.*`, or `prices.*`. Verified by §8.6 CC-01 through CC-04 + ALC-08.
4. **The `backtest.simulated_fills.action` closed enum** (`'enter_long'`, `'exit_long'`, `'rebalance_in'`, `'rebalance_out'`) is intentionally disjoint from Section 5's BUY / HOLD / TRIM / SELL / REPLACE / WATCH portfolio-action vocabulary.
5. **Section 5's promotion-gate logic must filter on `is_pipeline_validation_only = false`** when reading `backtest.aggregate_metrics` for promotion-eligibility evaluation. Verified by REP-07 (cross-section static check, runs after Section 5 lands).
6. **Section 5 does not consume `backtest.simulated_fills` as authoritative paper-portfolio state.** Verified by CC-09 + ALC-08.
7. **Section 6 surfaces the current-survivor disclosure label** read-only from `backtest.backtest_runs.current_survivor_disclosure_label` and `disclosures.current_survivor_label`.
8. **No fallback to `secondary_benchmark_id`.** `benchmark_relative_return` and `cost_drag` resolve against `primary_benchmark_id` only; index-only resolution propagates NULL. Verified by FM-09 + CC-08.
9. **Regime classifier ownership remains an Open Question (A-OQ-04-07).** Section 4 owns the consumption-side reporting surface unconditionally; the labeler may be Section 4 (Option A) or a future approved amendment (Option B). Either way, the §6.5 `backtest.regime_metrics` schema and §7.1 `regime_reporting` block apply.

## 5. Lock-package corrections folded into v1.0

- **C1** — A-PRP-04-34 stale wording fixed (dimensions are first-class nullable columns in logical uniqueness, not the PK; PK mechanics governed by A-PRP-04-37).
- **C2** — Stale `simulated_fills` keying prose fixed at two sites (§6.4 ledger bullet, §6.5 schema header) to include `horizon_trading_days`.
- **C3** — Attribution failure lifecycle reframed as open-run-before-validation (parallel to REP-02): open with `status='running'`, validate, mark `'failed'`, write one `'fail'` `attribution_run_issues` row with valid `attribution_run_id`, zero `signal_attribution` and `trade_attribution` rows. §9 #4a (f) and AT-04 updated.
- **C4** — §10 and §11.5 intro wording softened: "These are unresolved Approver decisions. Some include a Builder recommendation, but none are locked until the Approver accepts them."

## 6. Approval discipline

The Approver exercised final-decision authority per EW §2.1. Section 4 is locked. Implementation under §10 of EW does not begin until the Approver authorizes a build cycle.

---

**End of approval note.**
