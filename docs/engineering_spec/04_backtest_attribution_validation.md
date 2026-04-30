# Engineering Specification — Section 4: Backtest, Attribution, and Validation

**Phase 1 scope:** ETF tactical research platform.
**Section status:** v1.0 LOCKED / APPROVED
**Date:** 2026-04-30
**Author:** Builder (Claude)
**QA Reviewer:** ChatGPT (post-draft)
**Approver:** Jeremy
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Engineering Specification — Section 3a v1.0 LOCKED / APPROVED (`docs/engineering_spec/03a_feature_engineering.md`)
- Engineering Specification — Section 3b v1.0 LOCKED / APPROVED (`docs/engineering_spec/03b_target_generation.md`)
- Engineering Specification — Section 3c v1.0 LOCKED / APPROVED (`docs/engineering_spec/03c_model_layer_mlflow.md`)
- `docs/traceability_matrix.md` v0.6

**Scope-statement basis (per Approver direction; lightweight handoff packet pattern mirroring 03b / 03c):** Section 4 drafting and revision are authorized to proceed from five sources taken together as the de facto scope statement: (a) the current general project handoff (`docs/current_claude_context_handoff.md`); (b) Section 3a §12 forward references and Section 3a approval note §5 *Open items handed forward*; (c) Section 3b §12 forward references and Section 3b approval note §4 / §5 *Conditions on subsequent sections / Open items handed forward to Section 4*; (d) Section 3c §12.1 *Handoff to Section 4*, Section 3c approval note §4 / §5.1 *Conditions on subsequent sections / Open items handed forward to Section 4*; (e) the Section 4 handoff packet issued 2026-04-30 with the Approver's amendments.

---

## Changelog

- **v1.0 (2026-04-30) — LOCKED / APPROVED.** Section 4 promoted from v0.4 DRAFT to v1.0 LOCKED / APPROVED by the Approver, subject to four small lock-package corrections folded directly into this version. No scope expansion; no Section 1 / Section 2 amendment; no Section 5 / Section 6 drafting; no implementation started. Companion artifacts produced at lock: approval note `docs/reviews/2026-04-30_spec_04_backtest_attribution_validation_approval.md`, traceability companion `docs/reviews/2026-04-30_spec_04_backtest_attribution_validation_traceability_updates.md`, and matrix update `docs/traceability_matrix.md` v0.6 → v0.7. Historical v0.4 / v0.3 / v0.2 / v0.1 changelog entries preserved verbatim below.
  - **Correction 1 — Stale A-PRP-04-34 wording fixed.** v0.3 wording said `horizon_trading_days` and `sleeve_id` are both included in the PK; that conflicted with v0.4's surrogate-PK design. v1.0 says the dimensions remain first-class nullable columns participating in **logical uniqueness**, not the primary key; PK mechanics are governed by A-PRP-04-37.
  - **Correction 2 — Stale `simulated_fills` keying prose fixed.** Two sites (§6.4 ledger-keying bullet at line 263; §6.5 schema header prose at line 348) said `(backtest_run_id, fold_id, etf_id, signal_date, action)` without `horizon_trading_days`. The actual table PK already includes `horizon_trading_days` (per v0.2 Revision 3 / A-PRP-04-29); the prose now matches.
  - **Correction 3 — Attribution-failure lifecycle reframed as open-run-before-validation.** v0.4 said attribution-run creation is refused with an `attribution.attribution_run_issues` row, which was internally awkward because attribution issues attach to an `attribution_run_id`. v1.0 uses the same open-run-before-validation pattern that REP-02 uses for invalidated-snapshot rejection: the decomposer (i) opens an `attribution.attribution_runs` row with `status='running'`; (ii) validates the referenced `backtest.backtest_runs.status='succeeded'`; (iii) on failure, marks the attribution run `'failed'`; (iv) writes one `'fail'` `attribution.attribution_run_issues` row with the now-valid `attribution_run_id`; (v) writes zero `attribution.signal_attribution` rows; (vi) writes zero `attribution.trade_attribution` rows. §9 #4a (f) and AT-04 updated. Issue-type closed enum on `attribution.attribution_run_issues` retains `'backtest_run_not_succeeded'` from v0.4.
  - **Correction 4 — Open-question intros softened.** §10 and §11.5 no longer claim the Builder does not recommend defaults for the §10 items. A-OQ-04-07 includes a Builder recommendation for Option A. New wording: "These are unresolved Approver decisions. Some include a Builder recommendation, but none are locked until the Approver accepts them."

- **v0.4 (2026-04-30):** Small targeted cleanup per Approver-issued QA review. Three revisions; no scope expansion; no Section 1 amendment proposed; no Section 2 amendment proposed; no Section 5 / Section 6 drafting added; no implementation started; no approval note or traceability companion file produced; no traceability matrix update.
  - **Revision 1 — Nullable metric dimensions in primary keys fixed.** v0.3 R3 added nullable `horizon_trading_days` and `sleeve_id` columns to the three metric tables (`backtest.fold_metrics`, `backtest.aggregate_metrics`, `backtest.regime_metrics`) and put them inside the primary key with `NULLS NOT DISTINCT`. Primary key columns cannot be nullable — that was a structural error. v0.4 fixes by introducing surrogate primary keys (`fold_metric_id`, `aggregate_metric_id`, `regime_metric_id`, all `bigserial`) and declaring logical uniqueness as a separate `UNIQUE NULLS NOT DISTINCT (...)` constraint over the dimensioned tuple, with a `COALESCE`-based UNIQUE index fallback for Postgres < 15. The v0.3 design principle is preserved: `metric_name` remains a clean closed enum, and horizon / sleeve remain first-class columns. Affected sections: §6.5 three metric-table schemas; A-IMP-06 rewritten; FM-15 wording updated to point at logical-uniqueness instead of PK NULL-handling; new A-PRP-04-37 in §11.4; new §8.14 UNI-* test group with UNI-01 (fold_metrics, six cases including all-NULL duplicate rejected, single non-NULL duplicate rejected, both-non-NULL duplicate rejected, distinct horizons allowed, distinct sleeves allowed, distinct metric_name at same dimension tuple allowed, plus inline metric_name purity), UNI-02 (aggregate_metrics, omits fold_id), UNI-03 (regime_metrics, includes regime_label).
  - **Revision 2 — Failed-backtest attribution rejection wording corrected.** v0.3 §9 #4a clause (f) said an `attribution.attribution_runs` row referring to a `'failed'` backtest run is rejected by the FK at `attribution_runs.backtest_run_id`. A foreign key validates row existence only — it does not validate `status`. v0.4 corrects to: Section 4's `attribution/` decomposer enforces the `status='succeeded'` precondition via pre-write validation, and refuses with a `'fail'` `attribution.attribution_run_issues` row of `issue_type='backtest_run_not_succeeded'` when the precondition fails. New issue-type value added to the closed enum on `attribution.attribution_run_issues`. New AT-04 test verifies the pre-write validation lifecycle and explicitly verifies the FK does not enforce status (defensive against future regressions to "the FK protects us" thinking).
  - **Revision 3 — Stale version labels in current spec body cleaned.** Four sites updated: §10 intro ("explicitly unresolved at v0.2" → "current Section 4 scope"); §11.5 first sentence ("As of v0.2" → "As of the current Section 4 scope"); A-OQ-04-14 ("Builder does not propose a trigger at v0.1" → "in current Section 4 scope"); final line ("End of Section 4 v0.2 DRAFT" → "v0.4 DRAFT"). Historical v0.1, v0.2, v0.3 changelog entries preserved verbatim.
  - **v0.3 strengths preserved** unless directly affected by Revisions 1–3: Option C fold geometry; purge / embargo applies to training candidates only; horizon and sleeve metric dimensions remain first-class (R1 changes only the PK mechanism around them, not their first-class status or `metric_name` purity); explicit simulated weights on `backtest.simulated_fills`; pipeline-validation-only labeling for zero-cost fallback; neutral regime ownership wording (A-OQ-04-07 framing); all-folds-failed terminal case (R2 strengthens the wording, does not remove the case); SDR Decision 8 bucket names locked and carried as a closed enum; long-only-corrected cost formula; current-survivor disclosure structurally persisted; no writes to `models.*`, `ops.*`, `features.*`, `targets.*`, `universe.*`, or `prices.*`; no Section 5 portfolio behavior; no fallback to `secondary_benchmark_id`; no silent benchmark substitution; no live broker integration; no implementation code.

- **v0.3 (2026-04-30):** Targeted revisions per Approver-issued QA-driven revision list. Eight revisions plus preservation of accepted v0.2 strengths; no scope expansion; no Section 1 amendment proposed; no Section 2 amendment proposed; no Section 5 / Section 6 drafting added; no implementation started; no approval note or traceability companion file produced.
  - **Revision 1 — Fold geometry inconsistency resolved (Option C).** v0.2 had `fold_count: 8` and `fold_size_trading_days: 252` with WF-02 saying folds partition `[signal_date_min, signal_date_max]`; for the primary 2010–2025 window (≈4032 trading days), 8×252=2016 trading days cannot partition the full window. v0.3 adopts Option C — **test windows partition `[earliest_test_signal_date, latest_test_signal_date]` only**, not the full window. The pre-fold-1 portion is initial training; any post-fold-N portion is unused. `fold_count` and `fold_size_trading_days` are independent knobs, bounded only by `signal_date_max - max(horizon)`. Affected sections: §6.2 prose, §7.1 YAML (added `initial_train_trading_days`), WF-02 rewritten, A-PRP-04-03 reformulated, new A-PRP-04-32 added in §11.4.
  - **Revision 2 — OOS / purge contradiction fixed.** v0.2 §6.1 condition (c) and OOS-03 said purge ranges disqualify test rows from `'walk_forward_oos'` tagging — wrong. **Purge / embargo applies to training candidates only, never to test-window OOS rows.** v0.3 §6.1 OOS qualification rule rewritten (condition (c) removed; (d) reformulated as the canonical "training rows whose forward-label window overlaps any test row's forward-label window are purged" rule). OOS-03 rewritten to assert that test-window rows ARE tagged OOS even when purge ranges adjoin or overlap; the purge effect is on the training set only. Affected: §6.1 rule, OOS-03 test, A-PRP-04-05 reformulated, §6.5 simulated_fills no-row-written rule clarified to remove "as_of_date falls in a purge / embargo window" as an exclusion criterion for test-window dates.
  - **Revision 3 — Horizon and sleeve dimensions added to metrics tables.** v0.2 metrics tables had only `(backtest_run_id, fold_id, metric_name)` keying, forcing sleeve / horizon to be encoded into `metric_name` strings (the retired A-PRP-04-28 pattern). v0.3 adds first-class nullable columns `horizon_trading_days` and `sleeve_id` to `backtest.fold_metrics`, `backtest.aggregate_metrics`, and `backtest.regime_metrics`; both columns participate in the PK; **`metric_name` remains a clean closed enum that does not encode horizon or sleeve**. NULL-handling discipline classified as new A-IMP-06. A-PRP-04-28 retired; new A-PRP-04-34 added. FM-10 rewritten; new FM-15 (horizon-dimensioned) and FM-16 (`metric_name` purity) tests added.
  - **Revision 4 — Explicit simulated weights persisted on every fill row.** v0.2 said weights could be reconstructed from row counts — too fragile for turnover, attribution, and portfolio-value reconstruction. v0.3 adds three columns to `backtest.simulated_fills`: `simulated_weight_before`, `simulated_weight_after`, `simulated_weight_delta`, with a CHECK constraint enforcing `delta = after - before`. Turnover formula in §6.10 rewritten to use `simulated_weight_delta` directly. §6.4.1 weighting language updated. ALC-02 split into ALC-02 (explicit weight read) and ALC-02b (delta consistency). New A-PRP-04-33.
  - **Revision 5 — Pipeline-validation-only labeling on backtest runs.** Zero-cost-fallback runs (per A-PRP-04-14) must not be confused with serious validation evidence. v0.3 adds two columns to `backtest.backtest_runs`: `is_pipeline_validation_only` (boolean, default `false`) and `pipeline_validation_only_reason` (closed enum, currently `('cost_config_zero_fallback')`, NULL when the flag is `false`). CHECK constraint enforces the conditional NULL. §6.7 cost-config-fallback path now sets the flag and reason. Section 5's promotion-gate logic must filter on `is_pipeline_validation_only = false`. New REP-06 test verifies flag setting; new REP-07 reserves a cross-section test slot for Section 5 enforcement. New A-PRP-04-35 and A-PRP-04-36.
  - **Revision 6 — Stale regime ownership wording removed.** v0.2 retained two stale statements assuming a Section 3 sub-section owned regime computation. v0.3 replaces with neutral A-OQ-04-07 framing across §1 (regime mention), §2 SDR Decision 9 entry, and §7.2 `config/regime.yaml` read entry. **Until A-OQ-04-07 is resolved, Section 4 specifies the reporting / consumption surface only and does not assume an unauthorized future sub-section exists.**
  - **Revision 7 — All-folds-failed terminal case defined.** v0.2 skip-and-continue was correct as a per-fold default but did not address the terminal case where every fold is skipped or failed. v0.3 §9 #4a defines: when all folds are skipped/failed, the backtest run is marked `'failed'`, no aggregate or regime metrics are written, and a single `'fail'` `backtest.backtest_run_issues` row with `issue_type='all_folds_failed'` (added to the closed enum) is written. Partial-skip remains `'succeeded'`; entire-skip is `'failed'`. New WF-05 test verifies the boundary.
  - **Revision 8 — Minor cleanup.** Replaced "Section 4 v0.1" with "this section" / "current Section 4 scope" in current spec body where the references were not historical changelog entries (six sites: §4 deferral statement, §4 implementation bullet, §6.10 metric-set canonical statement, §7.1 YAML comment, §8 CC-09, §10 Option A regime labeler, §11.4 A-PRP-04-12). Historical v0.1 / v0.2 changelog entries preserved verbatim. CFG-02 wording corrected from "non-negative" to "positive" (v0.2 said negative-or-zero raises but called it non-negative — internally inconsistent).
  - **v0.2 strengths preserved** unless directly affected by Revisions 1–8: SDR Decision 8 bucket names locked and carried as a closed enum; long-only-corrected cost formula; `horizon_trading_days` in `backtest.simulated_fills` PK and `attribution.trade_attribution` composite FK; backtest-only simulated allocation contract explicitly not Section 5 portfolio behavior; financial metrics formula-defined; current-survivor disclosure structurally persisted on every backtest run; Section 4 does not write to `models.*`, `ops.*`, `features.*`, `targets.*`, `universe.*`, or `prices.*`; no fallback to `secondary_benchmark_id`; no silent benchmark substitution; no live broker integration; no implementation code.

- **v0.2 (2026-04-30):** Targeted revisions per Approver-issued QA-driven revision list. Twelve revisions plus preservation of accepted v0.1 strengths; no scope expansion; no Section 1 amendment proposed; no Section 2 amendment proposed; no Section 5 / Section 6 drafting added; no implementation started.
  - **Revision 1 — SDR Decision 8 bucket-name handling corrected.** v0.1 incorrectly treated transaction-cost bucket *definitions* as fully pending. SDR Decision 8 already locks the four Phase 1 cost-bucket names: ultra-liquid ETF, liquid sector ETF, thematic/niche ETF, commodity/specialty ETF. v0.2 carries those as a closed enum (snake_case for SQL: `ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`). Per-bucket basis-point values and account-type handling remain Proposed defaults / Open Questions. Affected sections: §1, §2 Decision 8, §3 #15, §4 *Out of scope*, §5.1 / §5.2, §6.5 `backtest.simulated_fills.cost_bucket` CHECK constraint added, §6.7, §7.1 (`config/backtest.yaml` snippet), §7.2 (`config/costs.yaml` consumption note), §8 (test wording), §10 (`A-OQ-04-08` retired; replaced with `A-PRP-04-23` clarification), §11.1 `A-DRV-07` extended, §11.4 entries reorganized, §13 Decision 8 row.
  - **Revision 2 — Cost formula corrected.** v0.1 had the cost direction backwards for long-only simulated fills. v0.2 uses: entry after-cost = pre-cost × (1 + cost_bps / 10000); exit after-cost = pre-cost × (1 - cost_bps / 10000). Round-trip cost ≈ 2 × cost_bps / 10000 of position size. Affected sections: §6.7 (formula prose), §7.1 (`cost_application` YAML keys: entry `multiply_by_one_plus_bps`, exit `multiply_by_one_minus_bps`), §8.5 SF-06, §11.4 A-PRP-04-06.
  - **Revision 3 — `backtest.simulated_fills` keying corrected (Option A).** v0.1's PK omitted `horizon_trading_days` despite the column being present. v0.2 adopts Option A: `horizon_trading_days` is added to the PK on `backtest.simulated_fills` and to all downstream composite FKs (specifically `attribution.trade_attribution` PK and the composite FK to `backtest.simulated_fills`). Option B (one-horizon-per-run) is rejected because both 63d and 126d horizons are SDR-locked Phase 1 horizons (03b §11.6 #9; SDR Decisions 4 / 6) and a backtest must be able to evaluate both in one run. Affected sections: §6.5 (`backtest.simulated_fills` PK), §6.6 (`attribution.trade_attribution` PK and composite FK), §8.9 AT-02.
  - **Revision 4 — Backtest-only simulated allocation contract added.** v0.1 named simulated fills and metrics without specifying the per-rebalance allocation that produces them. v0.2 adds §6.4.1 *Backtest-only simulated allocation contract*: top-N per `(sleeve_id, horizon_trading_days)` ranked by `combined_score`, equal-weight simulated exposure within each `(sleeve_id, horizon_trading_days)` bucket, monthly rebalance cadence per the SDR Decision 7 named cadence. Builder Proposed defaults; explicitly **not** paper portfolio state, **not** BUY/HOLD/TRIM/SELL/REPLACE/WATCH logic, **not** order intent, **not** broker-facing, **not** Section 5 portfolio behavior. Required tests added under §8.13 (ALC-* group).
  - **Revision 5 — Financial metric formulas defined.** v0.1 named metrics without defining formulas. v0.2 adds §6.10 *Financial metric definitions* — a metric definition table covering total return, CAGR, volatility (annualized), max drawdown, Sharpe-like ratio, hit rate, turnover, cost drag, benchmark-relative return, sleeve-level performance, regime-conditioned performance — each with formula, units, annualization convention, null behavior, and benchmark-relative behavior. The §7.1 metric enum expanded accordingly. New §8.12 (FM-* group) tests verify financial meaning, not row existence (per EW §5).
  - **Revision 6 — Purge / leakage test wording corrected.** v0.1 LK-01 wording compared training forward-window endpoints to test signal dates; the financially correct invariant is that no training row's forward label window overlaps any test row's forward label window. v0.2 LK-01 rewritten on that basis. Purge / embargo clarified to operate on training candidates only; OOS test-window rows are never purged or embargoed (they are the OOS evaluation set). §6.3 wording tightened correspondingly. PE-01 / PE-04 retain 03b-recorded `entry_date` / `exit_date` as the canonical source.
  - **Revision 7 — Current-survivor disclosure persistence added.** Per SDR Decision 4 / Section 2 disclosure contract, early Phase 1 results must be labeled as Core Test Universe / current-survivor directional-learning results. v0.2 adds `backtest.backtest_runs.current_survivor_disclosure_label` (NOT NULL; sourced from Section 2 `disclosures.current_survivor_label` at run-open time) and propagates the label to attribution and regime-metrics surfaces by transitive FK. New required test §8.7 REP-05 verifies the label is attached to every backtest run output.
  - **Revision 8 — `snapshot_mismatch` added to closed `issue_type` enum.** v0.1 referenced this value in §6.8 and REP-01 but omitted it from the `backtest.backtest_run_issues.issue_type` closed enum. v0.2 adds it. Enum remains closed.
  - **Revision 9 — Regime ownership reframed as Open Question.** v0.1 asserted the regime classifier was "owned by an unauthorized future Section 3 sub-section". That over-committed an unauthorized section. v0.2 reframes A-OQ-04-07 as a binary choice: **Option A** Section 4 owns a minimal SDR Decision 9 regime labeler (SPY-200dma + VIX-percentile, with the SDR-named volatility-deferral fallback) for reporting purposes; **Option B** a future approved amendment / sub-section owns the labeler and Section 4 consumes only. Builder recommends Option A on grounds of reducing cross-section blocking and matching Section 1's reservation of `regime/` (consumption) to Section 4. Approver resolves. Affected sections: §1, §2 Decision 9, §3 #16, §4 *Out of scope*, §5.1, §6.5 `backtest.regime_metrics`, §10 A-OQ-04-07, §13 Decision 9.
  - **Revision 10 — Open Question vs Proposed Default duplication cleaned up.** v0.1 cross-listed every §10 Open Question in §11.5 and parallel-listed several with Builder Proposed defaults in §11.4. v0.2 applies the discipline that an item with a specific Builder default is classified as A-PRP only; an item where the Approver must choose without a recommended default is A-OQ only. Items reclassified A-OQ → A-PRP only: A-OQ-04-01, -02, -04, -05, -08 (retired in favor of -23), -09, -10, -11, -12, -13, -17, -19. Items remaining A-OQ (no strong Builder default): A-OQ-04-03, -06, -07 (Builder recommends Option A but the binary choice is genuinely open), -14, -15, -16, -18. §11.5 cross-listing clarified to remove duplicate flagging.
  - **Revision 11 — Decision 8 traceability sketch (§13) updated.** Decision 8 row text now reflects that bucket *names* are SDR-locked (the four Phase 1 buckets) and Section 4 carries them as a closed enum on `backtest.simulated_fills.cost_bucket` and in `config/backtest.yaml`. Per-bucket basis-point values and account-type handling remain pending / Proposed defaults.
  - **Revision 12 — Accepted v0.1 strengths preserved** unless directly affected by Revisions 1–11: Section 4 does not write to `models.*`; Section 4 invokes 03c only through the §6.1 invocation seam; Section 4 does not write to `ops.data_quality_exceptions` or any `ops.*` table; Section 4 does not write to `features.*`, `targets.*`, `universe.*`, or `prices.*`; Section 4 does not define Section 5 portfolio rules, paper portfolio state, order intent, the second promotion gate, or kill-switch enforcement; no fallback to `secondary_benchmark_id`; no silent benchmark substitution; no live broker integration; no implementation code.

- **v0.1 (2026-04-30):** Initial draft. Eleven EW §3.2 template fields populated in order. Every assumption classified per EW §3.3. Honors the seven Section 1 invariants, the ten Section 2 v1.0 LOCKED constraints, the eleven Section 3a v1.0 LOCKED conditions on subsequent sections, the fourteen Section 3b v1.0 LOCKED conditions on subsequent sections, and the constraints documented in the Section 3c approval note §4. SDR Decisions 1, 7, 8 (consumption seam only), 9 (consumption / reporting only), 11 (attribution-storage half), 16 cited as directly implemented or respected. The principal Phase 1 scope choices for Section 4 — fold geometry, purge/embargo width, cost-application seam, MLflow experiment policy, regime sequencing, attribution decomposition shape, `backtest.*` / `attribution.*` schema introduction, and `config/backtest.yaml` introduction — are visibly classified and flagged as Open Questions or Builder Proposed defaults requiring Approver approval. None are silently resolved. No `models.*` write contract is added. No fallback to `secondary_benchmark_id` is introduced. No live-broker code path is introduced. No transaction-cost bucket definitions are pinned (those await SDR Decision 8 / `config/costs.yaml` drafting). No portfolio promotion gate, kill-switch enforcement, paper-portfolio state, or order-intent surface is introduced — all remain Section 5's. No implementation code is started.

---

## 1. Purpose

`backtest/`, `attribution/`, and `regime/` (consumption side) implement the **validation, backtest, and attribution** layer for the Phase 1 ETF tactical research platform. The layer consumes:

- the Section 3a feature surface (`features.feature_values` filtered on `features.feature_runs.status='succeeded'`);
- the Section 3b target surface (`targets.target_values` filtered on `targets.target_runs.status='succeeded'`), including the per-row window metadata Section 4 needs for purge / embargo (`signal_date` (= `as_of_date`), `horizon_trading_days`, `entry_date`, `exit_date`);
- the Section 3c model layer (`models.model_predictions` filtered on `models.model_runs.status='succeeded'`; `models.combined_scores` filtered on `models.scoring_runs.status='succeeded'`), invoked through the 03c §12.1 seam for fold-aware OOS evaluation;
- the Section 2 reproducibility anchor (`ops.data_snapshots`);
- the Section 1 architectural reservation for `regime/` consumption-side reporting.

Section 4 produces:

- **walk-forward folds** with explicit train / test / purge / embargo bounds, recorded in a Section-4-owned schema;
- **a simulated backtest ledger** (also called the **simulated fills ledger** to make the read clear): per-signal-date simulated trades and simulated fills with cost-bucket-applied prices, anchored to a `data_snapshot_id`. **The simulated fills ledger is not paper portfolio state, not order intent, and not broker-facing in any form.** Section 5 owns paper portfolio state and broker-neutral order intent and is the writer there; Section 4 produces only the per-backtest-run simulated fills used to compute backtest performance and attribution;
- **per-fold, aggregate, and regime-conditioned performance metrics** consumed as **validation evidence surfaces** — that is, evidence that later sections (specifically Section 5's paper-portfolio promotion gate and Section 5's kill-switch evaluation) read. Section 4 does not define those gates or the kill-switch enforcement logic. Section 4 produces evidence; Section 5 evaluates it;
- **attribution decomposition** of the simulated backtest results, stored in a Section-4-owned schema for Section 6 to surface read-only;
- **regime reporting** at the consumption side per SDR Decision 9, conditioning the metrics above on the regime taxonomy. **Whether the regime classifier (labeler) itself is owned by Section 4 (a minimal SDR Decision 9 implementation in `regime/`) or by a future approved amendment / sub-section consumed by Section 4 is an Open Question carried forward to the Approver (A-OQ-04-07).** Section 4 does not assume an unauthorized future sub-section exists.
- **reproducibility metadata** linking every backtest run to a `data_snapshot_id`, the consumed `feature_run_id` / `target_run_id` chain via the model runs invoked, and (if introduced) MLflow experiment / run identifiers for backtest tracking.

Section 4 is responsible for **what backtest is run, on what folds, with what purge / embargo, against what model outputs, with what cost-application contract, and what evidence surfaces are produced**. Section 4 is **not** responsible for:

- the model-layer write contracts (03c owns `models.*`);
- portfolio rules, position sizing, paper portfolio state, or order intent (Section 5);
- the second SDR Decision 12 promotion gate (Paper tracking → influence on real decisions) — Section 5;
- multi-condition kill-switch enforcement — Section 5 (Section 4 may surface conditions Section 5 evaluates);
- live-trading code paths or broker integration (out of Phase 1 entirely per SDR Decision 1);
- the regime-classifier *computation* itself **when** ownership is resolved to Option B (a future approved amendment / sub-section); under Option A (Section 4 owns a minimal SDR Decision 9 labeler in `regime/`), this falls inside Section 4 scope. The question is open per A-OQ-04-07 in §10;
- transaction-cost bucket definitions: SDR Decision 8 locks the four Phase 1 cost-bucket *names* (`ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf` — snake_case for SQL); Section 4 consumes those names as a closed enum on `backtest.simulated_fills.cost_bucket` and in `config/backtest.yaml`. Section 4 does **not** pin per-bucket basis-point values or account-type rules — those remain Proposed defaults / Open Questions and may be cashed out independently by `config/costs.yaml` or by a future SDR Decision 8 amendment.

The principal architectural cash-out points Section 4 inherits are:

- **SDR Decision 7 — Validation, Calibration, and Backtest Confidence Level.** Walk-forward validation is Section 4's. The Phase 1 backtest support windows ("primary backtest 2010–2025", "longer robustness test 2005–2025", "recent-regime test 2020–2025", "monthly rebalance testing"), the explicit treatment of overlapping forward labels, and the explicit treatment of the seven biases (look-ahead, overlapping-label, selection / data-snooping, current-survivor universe, backfill / proxy-history, market-impact / liquidity, time-zone / synchronization) all anchor here. Section 4 owns fold geometry, purge / embargo width, OOS qualification, and the leakage tests. The calibration pipeline is 03c's; Section 4 only supplies the held-out fold structure to 03c via the §12.1 seam.
- **SDR Decision 16 / Section 1 invariant 7 — Time-aware research auditability.** Section 4 cashes the invariant out at the backtest layer via reproducibility metadata, leakage tests at fold boundaries, no-look-ahead in fold construction, and `data_snapshot_id` linkage on every backtest run.
- **SDR Decision 11 — Model Tracking, Attribution, Data Quality, and Lightweight MLOps (attribution half).** 03c owns the MLflow writer-side integration on the model side. Section 4 owns the **attribution storage and reporting side** — the per-trade and per-signal attribution tables, anchored to the same `data_snapshot_id` chain.
- **SDR Decision 9 — Regime Taxonomy and Reporting (consumption / reporting side).** Section 4 owns reporting. Ownership of the regime classifier (labeler) itself is unresolved per A-OQ-04-07 — Option A: Section 4 owns a minimal SDR Decision 9 labeler in `regime/`; Option B: a future approved amendment / sub-section owns it. **Until the Approver resolves A-OQ-04-07, Section 4 specifies the reporting / consumption surface only.** Section 4 does not assume an unauthorized future sub-section exists.
- **SDR Decision 8 — Transaction Cost and Account-Type Assumptions.** SDR Decision 8 locks the four Phase 1 cost-bucket names: `ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`. Section 4 inherits the locked bucket enumeration and specifies how the backtest harness consumes a per-ETF cost-bucket assignment plus a per-bucket basis-point value. The basis-point values themselves and the account-type rules SDR Decision 8 also names (internal paper account, retirement / Solo 401(k), taxable account later, non-retirement API testing later) are not pinned by this section — basis-points are Builder Proposed defaults requiring Approver approval (or Open Questions where no default is recommended); account-type handling is deferred to a later cash-out and is read-only-consumed via `config/costs.yaml` when populated.
- **SDR Decision 1 — Phase 1 scope.** Section 4 introduces no live-broker code, no individual stocks, no fundamentals, no holdings, no news, no options, no Danelfin.

---

## 2. Relevant SDR decisions

Section 4 directly implements or respects:

- **SDR Decision 1** — Phase 1 scope and boundaries. Backtest and attribution are pure-research surfaces; no module under `backtest/`, `attribution/`, or `regime/` (consumption) imports a broker SDK, makes order-placement HTTP calls, or persists records that constitute paper portfolio state or order intent. The architectural defenses inherited from Section 1 invariant 2 apply unchanged.
- **SDR Decision 7** — Validation, Calibration, and Backtest Confidence Level. Section 4 is the principal owner of the validation framework. Walk-forward folds, purge / embargo at train / test boundaries, OOS qualification, the seven-bias-control test surface, and the four backtest support windows enumerated in the SDR all originate here. The calibration *pipeline* is 03c's; Section 4 only supplies the held-out fold structure 03c needs.
- **SDR Decision 8** — Transaction Cost and Account-Type Assumptions. SDR Decision 8 locks the four Phase 1 cost-bucket names: `ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`. Section 4 specifies the **consumption seam** by which a backtest run reads a cost-bucket-per-ETF assignment and applies a per-bucket cost adjustment to simulated fills, using the locked bucket enumeration. Section 4 does **not** pin per-bucket basis-point values or account-type rules — those remain Builder Proposed defaults or Open Questions in §10 / §11 and are surfaced through `config/costs.yaml` (Section 4 owned at the file level per Section 1).
- **SDR Decision 9** — Regime Taxonomy and Reporting. Section 4 owns the consumption-side reporting layer. SDR Decision 9 names two dimensions for Phase 1 (SPY above/below 200-day moving average; VIX high/low using rolling percentile with a deferred fallback when VIX data is absent), creating up to four regimes. Section 4 specifies the reporting surface that conditions backtest metrics on the regime label per signal date. **Ownership of the regime classifier (labeler) that produces the regime label per `(as_of_date)` is an Open Question — A-OQ-04-07 in §10.** Two options are visible: Option A — Section 4 owns a minimal SDR Decision 9 labeler in `regime/` (Builder recommended); Option B — a future approved amendment / sub-section owns the labeler, and Section 4 consumes its output. Section 4 does **not** assume an unauthorized future sub-section exists.
- **SDR Decision 11** — Model Tracking, Attribution, Data Quality, and Lightweight MLOps. Section 4 owns the **attribution storage and reporting half**. 03c owns the model-tracking and MLflow-writer half. Section 4 inherits Section 2 / 3a / 3b / 3c constraint that `ops.data_quality_exceptions` is ingestion-owned and remains unmodified by Section 4.
- **SDR Decision 16** — Phase 1 Success Criteria and Bias Controls. Section 4 contributes the OOS validation backbone, leakage tests at fold boundaries, the reproducibility-chain extension at the backtest-run level, the regime-reporting surface (#16 *Regime report is available*), the attribution surface (#20 *Attribution exists for trades / signals*), the simulated-fills surface (#10 *Walk-forward backtest runs*; #11 *Transaction costs / slippage assumptions are included*), and the seven enumerated bias controls.

Section 4 also reads (without modifying) decisions implemented by other locked sections:

- **SDR Decision 3 / 4** — universe, eligibility, lifecycle, ETF launch-date handling. Section 4 respects the Section 2 eligibility-row and effective-date conventions on the read side; Section 4 does not re-derive eligibility windows.
- **SDR Decision 5** — Benchmark, sleeve, and diversifier treatment. Section 4 reads sleeve assignments where attribution is sleeve-conditioned and respects the closed `rank_method` enumeration 03c §6.7 / §10.5 establishes. Section 4 does not redefine the enumeration. The `DiversifierHedge` "no `models.combined_scores` rows under the current first-testable formula" contract from 03c §10.6 / A-PRP-29 (Path X) is preserved on the read side: a backtest run encounters absence of combined-score rows for `DiversifierHedge` ETFs as the documented and intended contract, not as a failure.
- **SDR Decision 6** — Target design and ranking objective. Section 4 consumes the dual-target (regression + calibrated classification) outputs through the `models.combined_scores` surface 03c §6.8 specifies; Section 4 does not redefine the combined-score formula.
- **SDR Decision 12** — Model promotion, warning, pause, and retirement rules. The first promotion gate (Research → Internal paper tracking) is owned by 03c at write time. The second gate (Paper tracking → influence on real decisions) is owned by Section 5. Section 4 produces validation evidence surfaces consumed by both gates; Section 4 does not evaluate either gate. Section 4 may surface candidate kill-switch conditions but does not enforce kill-switch transitions on `models.model_versions.state` (Section 5 owns enforcement; 03c owns the schema).
- **SDR Decision 13** — LLM advisory use. Process commitment governed by the EW; no architectural footprint in Section 4.
- **SDR Decision 14** — Danelfin deferred. Not introduced by Section 4.
- **SDR Decision 15** — Broker-neutral order-intent strategy. Not introduced by Section 4. Section 5 owns the order-intent surface.
- **SDR Decision 17** — Operator UI is read-only. Section 4's `backtest.*` and `attribution.*` schemas are designed for read-only consumption from `ui/`; Section 4 does not rely on UI behavior and does not permit UI writes.
- **SDR Decision 18** — Deployment and container architecture. Section 4 introduces no new container, no new named volume, and no new service in the Phase 1 stack.

---

## 3. In scope

Section 4 covers the following at the specification level:

1. **Walk-forward harness** — fold construction over the per-row window metadata 03b §6.5 records on every `targets.target_values` row, with explicit train / test / purge / embargo bounds per fold. The harness is the orchestrator that drives 03c model fitting and 03c scoring on each fold via the §12.1 invocation seam.
2. **Purge / embargo enforcement at train / test boundaries**, using the per-row window metadata 03b records. Section 4 does **not** re-derive `entry_date` / `exit_date` from horizon arithmetic; it reads them off `targets.target_values` and computes the fold-boundary purge / embargo from the recorded values. Per SDR Decision 7 Phase 1 uses a 126-trading-day embargo as the SDR-named width; Section 4 confirms or proposes alternatives at Approver direction (see §10 Open Questions).
3. **OOS qualification rule** — Section 4 owns the rule that determines which `(etf_id, as_of_date, model_kind, model_run_id)` rows produced through the §12.1 seam are tagged `prediction_context='walk_forward_oos'` by 03c at write time. 03c stores; Section 4 supplies via the seam.
4. **The §12.1 invocation seam** — function signature, parameterization, and fold-metadata payload that Section 4's harness uses to invoke 03c-owned model-run and scoring-run contracts. Section 4 specifies the seam shape; 03c is the writer to `models.*` and MLflow.
5. **OOS leakage tests at the train / test boundary** — parallel to Section 2's data-layer look-ahead checks and 3a / 3b's per-family alignment tests, this is the model-layer / backtest-layer half of the bias-control backbone.
6. **Simulated backtest ledger (simulated fills ledger)** — per-signal-date simulated trades and simulated fills with cost-bucket-applied prices, recorded in a Section-4-owned table inside the proposed `backtest.*` schema. **The simulated fills ledger is not paper portfolio state, not order intent, and not broker-facing.** Section 5 owns paper portfolio state and broker-neutral order intent; Section 4 produces only the per-backtest-run simulated fills.
7. **Per-fold, aggregate, and regime-conditioned performance metrics** computed from the simulated fills ledger and stored in `backtest.*`. Specific metric set is a Proposed default (see §10).
8. **Attribution decomposition and storage** in a Section-4-owned `attribution.*` schema. Per-signal and per-trade attribution rows are anchored to a `backtest_run_id` (Section 4) and transitively to the `data_snapshot_id` chain.
9. **Regime reporting (consumption side)** — the surface that conditions backtest metrics on the regime label per `(as_of_date)`. Section 4 specifies the reporting consumer. **Ownership of the regime classifier (labeler) is an Open Question per A-OQ-04-07 in §10**: either Section 4 owns a minimal SDR Decision 9 labeler in `regime/` (Option A, Builder recommended) or a future approved amendment / sub-section owns it (Option B). Section 4 does not assume an unauthorized future sub-section exists.
10. **Phase 1 backtest confidence-level outputs** per SDR Decision 7 — the "what does a successful backtest look like" surface consumed by Section 5's promotion gate and by Section 6 UI.
11. **Validation evidence surfaces consumed by later promotion / paper-portfolio gates.** Section 4 defines the *evidence* (metrics, leakage tests, reproducibility metadata, regime conditioning, attribution coverage) and the schema in which it is stored. Section 4 does **not** define the gate, the kill-switch threshold, or the portfolio-state behavior.
12. **Reproducibility chain extension** — every `backtest.backtest_runs` row links to a single `data_snapshot_id` and (transitively, through the `models.model_runs` / `models.scoring_runs` rows it consumed) to the `feature_run_id` and `target_run_id`. EW §7 reproducibility metadata (commit hash, config hash, `data_snapshot_id`, provider / dataset, universe version, adjusted-price convention, MLflow run ID) is recorded on every backtest run.
13. **Section-4-owned schemas (proposed): `backtest.*` and `attribution.*`.** Whether introducing these schemas requires a Section 2 amendment to register them with the application database is a Section 4 Open Question (Section 2 v1.0 LOCKED enumerates `universe`, `prices`, `ops`, plus the later `features`, `targets`, `models` schemas; `backtest` and `attribution` are not currently listed). Schema names and contents are Builder Proposed defaults requiring Approver approval per EW §3.3.
14. **Section-4-owned config: `config/backtest.yaml` (proposed).** Section 1's `config/` directory listing enumerates `config/backtest.yaml`'s nearest neighbors (`config/costs.yaml` Section 4, `config/regime.yaml` Sections 3 and 4) but does **not** explicitly enumerate `config/backtest.yaml`. Whether introducing the file requires a Section 1 amendment is a Section 4 Open Question (the §10 list classifies it). The file's shape and validation rules are specified at the spec level here, in `config/backtest.yaml` form, but not committed to disk.
15. **Section 4 reads of `config/costs.yaml`** (consumption seam). SDR Decision 8 locks the four Phase 1 cost-bucket names — `ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`. Section 4 reads a per-ETF or per-bucket cost basis-point value the harness applies to simulated fills using this locked bucket enumeration. Section 4 does **not** pin per-bucket basis-point values; those remain Builder Proposed defaults (or Open Questions where no default is recommended) and are populated in `config/costs.yaml` under Approver direction. Account-type handling per SDR Decision 8 is read-only-consumed when populated and not re-defined here.
16. **Section 4 reads of `config/regime.yaml`** (consumption seam). Section 4 specifies what the regime-reporting consumer expects from a regime-classification surface (per-`(as_of_date)` regime labels from a closed enumeration; per-regime aggregations) without pre-committing where that classifier lives. Per A-OQ-04-07, the classifier may live in `regime/` under Section 4 ownership (Option A, Builder recommended) or in a future approved amendment / sub-section (Option B). Under either option, `config/regime.yaml` is jointly read per Section 1's config-dependencies table.
17. **Required tests** — walk-forward harness correctness, purge / embargo enforcement, OOS qualification correctness, leakage tests, attribution decomposition correctness, reproducibility under shared `data_snapshot_id`, regime reporting correctness, `prediction_context` filter discipline, no-write-to-`models.*` / `ops.*` / `features.*` / `targets.*` / `universe.*` / `prices.*` static checks, no-broker-import / no-broker-SDK checks at the Section 4 module level (parallel to 03c §8.2 CC-05 and Section 1 invariant 2).

---

## 4. Out of scope

Current Section 4 scope explicitly defers the following:

- **Portfolio rules, position sizing, paper portfolio state, signal-to-trade conversion, broker-neutral order intent, second promotion gate, kill-switch enforcement** — Section 5. Section 4 produces backtest outputs that Section 5 consumes; Section 4 does not generate orders, does not transition `models.model_versions.state`, and does not write paper portfolio state.
- **Live trading code paths, broker integration, broker SDK, broker HTTP client** — out of Phase 1 entirely per SDR Decision 1 / 15.
- **Modifying `features.*`, `targets.*`, `models.*`, `universe.*`, `prices.*`, or `ops.*` schemas** — owned by 3a, 3b, 3c, 2 respectively. Section 4 is read-only against all of them.
- **Writing to `models.*`** — exclusively 03c per Section 3c §6.6 / §6.3 and the writer-side ownership boundary clarified in 03c §12.1 (R-8). Section 4 invokes 03c-owned model-run contracts through the §12.1 invocation seam but does not write directly. The closed three-value run-status enum `('running', 'succeeded', 'failed')` on `models.model_runs` and `models.scoring_runs` is consumed by Section 4 with the `'succeeded'` filter on every join; Section 4 does not introduce a fourth value.
- **Writing to `ops.data_quality_exceptions`** — ingestion-owned per Section 2 v1.0 LOCKED. Section 4 may write to its own issue log (`backtest.backtest_run_issues` / `attribution.attribution_run_issues` are proposed in §6) but does not write to `ops.*`.
- **MLflow as the model-run writer** — that is 03c per Section 3c §6.10. The 1:1 mapping between `models.model_runs` rows and MLflow runs and the closed required-tag set on those MLflow runs belong to 03c. Whether Section 4 introduces its own MLflow experiments for backtest tracking, separate from 03c's per-`model_kind` experiments, is a Builder Proposed default per A-PRP-04-12 (default off until Approver-resolved) — answered in either direction, the 03c writer-side contract is unchanged.
- **Active → Warning automated trigger** — carried forward from 03c §10.9 / A-OQ-01 as an Open Question. Section 4 may **propose** a mechanical trigger; **adoption requires a 03c amendment**, not a Section 4 unilateral decision.
- **Per-bucket transaction-cost basis-point values and account-type rule cash-out** — the four Phase 1 bucket *names* are locked by SDR Decision 8 (`ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`); Section 4 inherits and consumes them. The per-bucket basis-point values are Builder Proposed defaults — not pinned in this section. Account-type handling (internal paper account, retirement / Solo 401(k), taxable account later, non-retirement API testing later) is deferred to a later cash-out under `config/costs.yaml` and is not specified here. Whether Section 4 lock blocks on `config/costs.yaml` lock or proceeds with a documented "cost values pending" gap is a Builder Proposed default per A-PRP-04-23 (Builder recommends proceeding; runtime behavior controlled by A-PRP-04-14).
- **Regime classifier computation** — under Option B of A-OQ-04-07, this falls outside Section 4. Under Option A (Builder recommended), Section 4 owns a minimal SDR Decision 9 labeler in `regime/`. Whether Section 4 lock blocks on regime-classifier resolution or proceeds with a documented "regime classifier unavailable" runtime fallback (per A-PRP-04-13) is itself an Open Question (A-OQ-04-07).
- **UI surfaces** — Section 6. Section 4 specifies the schema Section 6 reads from; Section 4 does not specify Dash screens, layouts, or filters.
- **Implementation / code / migrations** — this section is a specification, not a build. The migration script that creates the `backtest.*` and `attribution.*` schemas (if they survive review), the harness modules under `backtest/`, the attribution modules under `attribution/`, the regime reporter under `regime/` (consumption), and the test files under `tests/unit/` and `tests/integration/` will be authored under the standard EW §3 → §10 build workflow after Sections 4, 5, and (if needed) 6 are also locked, or earlier if the Approver authorizes a partial build.

---

## 5. Inputs and outputs

### 5.1 Inputs

Section 4 consumes the following at run time, all read-only:

- **`features.feature_values`** filtered on `features.feature_runs.status='succeeded'` per the Section 3a v1.0 LOCKED filter discipline (constraint #4 in 03a approval note §4). Required only when Section 4's harness invokes 03c through the §12.1 seam for fold-specific re-fits; Section 4 does not consume features for fold-construction itself (folds are constructed over signal-date ranges, not over feature rows).
- **`targets.target_values`** filtered on `targets.target_runs.status='succeeded'` per the Section 3b v1.0 LOCKED filter discipline (constraint #4 in 03b approval note §4). Section 4 reads `signal_date` (via `as_of_date`), `horizon_trading_days`, `entry_date`, and `exit_date` off every consumed row to construct purge / embargo bounds. **Section 4 does NOT re-derive these from horizon arithmetic.** Section 4 inherits the §6.5 null-vs-no-row taxonomy without reframing: Bucket 1 absences are absences in Section 4's harness too; Bucket 2 `target_value = NULL` rows produce `predicted_value = NULL` propagation in the model layer per 03c §6.4 / §6.2.
- **`models.model_predictions`** filtered on `models.model_runs.status='succeeded'` per 03c constraint #4. For backtest performance evaluation (the simulated fills ledger and per-fold metrics), Section 4 reads only rows with `prediction_context='walk_forward_oos'` per 03c §6.2 and 03c §12.1 R-8. For other evidence surfaces (e.g., in-sample diagnostics surfaced read-only to Section 6) Section 4 may read other `prediction_context` values, with the closed three-value enum `('in_sample_diagnostic', 'walk_forward_oos', 'current_scoring')` from 03c §6.2 unmodified.
- **`models.combined_scores`** filtered on `models.scoring_runs.status='succeeded'` per 03c constraint #4. Keyed `(etf_id, as_of_date, sleeve_id, horizon_trading_days, scoring_run_id)` per 03c §6.6. Used to drive the simulated-fills construction (which ETFs the simulated trade ledger trades on each rebalance date is derived from `combined_score` and `rank_within_sleeve`). The `DiversifierHedge` zero-rows contract from 03c §10.6 / A-PRP-29 is preserved on the read side: absence of combined-score rows for `DiversifierHedge` ETFs is the documented contract, not a failure.
- **`models.scoring_runs`**, **`models.scoring_run_models`**, **`models.model_runs`**, **`models.model_versions`**, **`models.model_state_history`** — read for run-id lookup, version-id lookup, and lifecycle-state inspection (e.g., "this backtest evaluated `model_version_id` X whose state at the backtest-run-start time was `'Active'`"). Section 4 does **not** transition `model_versions.state`. Section 5 owns transitions; 03c owns the schema.
- **`models.model_run_issues`** and **`models.scoring_run_issues`** — read at run report time to surface upstream issues per backtest run.
- **`ops.data_snapshots`** — read for the snapshot pinning. Section 4 refuses to start a backtest run against an `'invalidated'` snapshot, mirroring the open-run-before-validation lifecycle 03a §6.3 / 03b §6.3 / 03c §6.3 establish.
- **`universe.etfs`**, **`universe.etf_eligibility_history`**, **`universe.benchmarks`**, **`universe.sleeves`** — read for sleeve-conditioned attribution, eligibility-as-of-date queries (only for sleeve / lifecycle context — Section 4 does **not** re-derive feature- or target-side eligibility filters; absence in `features.feature_values` and `targets.target_values` is the consumption-side signal per 03a constraint #1 and 03b §4 / approval note §4 #2).
- **Regime classifier outputs** (per A-OQ-04-07 ownership choice) — read when the classifier exists. Under Option A (Section 4 owns the classifier in `regime/`), the outputs are produced inside Section 4. Under Option B (a future approved amendment / sub-section), Section 4 consumes the output surface that amendment specifies. Until ownership is resolved, the regime-reporting consumer surfaces a documented "regime classifier unavailable" state per A-PRP-04-13 without failing the backtest run (per §9 Edge cases).
- **`config/backtest.yaml`** — Section 4 owned (proposed; see §7.1).
- **`config/costs.yaml`** — Section 4 owned at the file level per Section 1 config-dependencies table. SDR Decision 8 locks the four Phase 1 cost-bucket names (`ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`). Per-bucket basis-point values await Approver direction. Read-only by Section 4 modules.
- **`config/regime.yaml`** — Sections 3 and 4 jointly per Section 1 config-dependencies table. Read-only by Section 4 modules.

### 5.2 Outputs

Section 4 writes only to its own `backtest.*` and `attribution.*` schemas (proposed; see §6.5 / §6.6) and (optionally, if §10 approves it) MLflow experiments dedicated to backtest tracking. Specifically:

- `backtest.backtest_runs` — one row per backtest run (the harness invocation).
- `backtest.backtest_folds` — one row per fold within a backtest run.
- `backtest.simulated_fills` — the simulated fills ledger (per-signal-date simulated trades after cost application).
- `backtest.fold_metrics` — per-fold metrics.
- `backtest.aggregate_metrics` — aggregate-across-folds metrics per backtest run.
- `backtest.regime_metrics` — regime-conditioned metrics per backtest run.
- `backtest.backtest_run_issues` — backtest-layer issue log.
- `attribution.attribution_runs` — one row per attribution run (an attribution run consumes a `backtest_run_id`).
- `attribution.signal_attribution` — per-signal attribution rows.
- `attribution.trade_attribution` — per-trade attribution rows.
- `attribution.attribution_run_issues` — attribution-layer issue log.

Section 4 does **not** write to `models.*`, `features.*`, `targets.*`, `universe.*`, `prices.*`, or `ops.*`. Static checks at the test layer enforce this (§8).

### 5.3 Module-level input / output summary

- **`backtest/` harness** (the entry point for a walk-forward backtest run): `config/backtest.yaml` + selected `feature_run_id` + selected `target_run_id` + selected `data_snapshot_id` + (optionally) selected `model_set_version` → fold construction → repeated invocations of the 03c §12.1 seam → `backtest.backtest_runs` row + `backtest.backtest_folds` rows + `backtest.simulated_fills` rows + `backtest.fold_metrics` rows + `backtest.aggregate_metrics` rows + (on warning or failure) `backtest.backtest_run_issues` rows.
- **`backtest/` simulated-fill module**: per-signal-date simulated trades from `models.combined_scores` filtered on `'succeeded'` scoring runs and OOS-tagged predictions + cost adjustments from `config/costs.yaml` → `backtest.simulated_fills` rows.
- **`backtest/` metrics module**: simulated fills + fold metadata → `backtest.fold_metrics` and `backtest.aggregate_metrics` rows.
- **`regime/` (consumption) reporter**: per-`(as_of_date)` regime label from the regime classifier (when available) + `backtest.fold_metrics` / `backtest.aggregate_metrics` → `backtest.regime_metrics` rows.
- **`attribution/` decomposer**: `backtest.simulated_fills` + `backtest.aggregate_metrics` + universe / sleeve metadata → `attribution.attribution_runs` row + `attribution.signal_attribution` rows + `attribution.trade_attribution` rows + (on warning or failure) `attribution.attribution_run_issues` rows.

---

## 6. Data contracts

### 6.1 The §12.1 invocation seam (Section 4 → 03c)

Section 4's walk-forward harness invokes 03c-owned model-run and scoring-run contracts through the seam 03c §12.1 reserves to Section 4 design. The seam is a function-shaped contract; concrete signatures land at implementation time. The shape Section 4 specifies at the spec level:

- **Inputs to the seam** (Section 4 supplies):
  - `feature_run_id`, `feature_set_version` (for the snapshot's succeeded feature run).
  - `target_run_id`, `target_set_version` (for the snapshot's succeeded target run).
  - `model_set_version` (the active 03c version per `config/model.yaml`).
  - `data_snapshot_id` (Section 4 asserts it equals the snapshot anchored by both `feature_run_id` and `target_run_id`).
  - `fold_metadata` payload — a closed structure carrying:
    - `fold_id` (Section-4-issued; recorded on `backtest.backtest_folds`);
    - `fold_index` and `fold_count` (cardinal positions);
    - `train_signal_date_min` / `train_signal_date_max` (inclusive trading-day bounds for the training window of this fold);
    - `test_signal_date_min` / `test_signal_date_max` (inclusive trading-day bounds for the test / OOS window of this fold);
    - `purge_signal_date_ranges` (closed list of `(min, max)` purge ranges around the test window, derived from 03b's per-row `entry_date` / `exit_date` metadata so that no training row's forward window overlaps the test window);
    - `embargo_signal_date_min` / `embargo_signal_date_max` (the embargo region between train and test per SDR Decision 7's named 126-trading-day width — Proposed default; see §10 Open Questions);
    - `prediction_context_to_emit` (closed-set value per row produced through the seam — `'walk_forward_oos'` for predictions whose `as_of_date` falls in `[test_signal_date_min, test_signal_date_max]`; `'in_sample_diagnostic'` if the seam is invoked in a diagnostic mode; the seam refuses to emit `'current_scoring'` because that context is reserved to 03c orchestrator outside Section 4).
- **Outputs from the seam** (03c writes; Section 4 reads):
  - One or more `models.model_runs` rows (one per `model_kind`), each `status='succeeded'` if the fit and prediction emission succeeded; `models.model_predictions` rows tagged with the supplied `prediction_context`; on failure, `models.model_run_issues` per 03c §6.6.
  - Optionally a `models.scoring_runs` row that consumes the per-fold model runs, with `models.combined_scores` rows tagged through the score / rank chain. Whether scoring-run invocation is in-band with the §12.1 seam or a separate Section-4-driven invocation is an Implementation default (§11). The scoring-run write contract is 03c's either way.

**Writer-side ownership boundary.** Per 03c §12.1 R-8, Section 4 does **not** write to `models.model_runs`, `models.model_predictions`, `models.scoring_runs`, `models.combined_scores`, `models.model_versions`, `models.model_state_history`, `models.model_run_issues`, or `models.scoring_run_issues`. The seam is the only sanctioned path. Static checks at §8 verify the no-write rule.

**OOS qualification rule (Section-4-owned).** A `(etf_id, as_of_date, model_kind, model_run_id)` row is qualified `'walk_forward_oos'` for fold `f` if and only if (a) `as_of_date` falls in `[test_signal_date_min(f), test_signal_date_max(f)]`; (b) the model run that produced the row was fit on a training-row set from which **every** row whose recorded `[entry_date, exit_date]` overlaps any test row's `[entry_date, exit_date]` for fold `f` has been purged, and from which the additional `embargo_trading_days` margin has been excluded on both sides of the test window. **Purge and embargo apply to training candidates only — they do not exclude test-window rows from being tagged `'walk_forward_oos'`.** A test-window row is qualified OOS even when a purge range extends across, adjoins, or overlaps the test window; that is the structurally correct behavior because purge / embargo serves to clean the training set, not to shrink the test set. Section 4 supplies fold metadata and tag value; 03c stores. The leakage tests at §8 verify the rule on a fixture.

### 6.2 Walk-forward fold construction

Fold construction is over the signal-date axis derived from `targets.target_values.as_of_date` for the active snapshot, intersected with the eligible signal-date range from the rate-limit-aware perspective (Section 4 reads, does not redefine, the snapshot's `price_table_max_as_of_date` per Section 2 v1.0 LOCKED). The concrete fold geometry (number of folds, fold size in trading days, expanding vs. rolling window, gap structure) is **a Builder Proposed default requiring approval per EW §3.3** — see §10 / §11. SDR Decision 7 names walk-forward but does not pin geometry.

**Test windows do not partition the full window** (Builder Proposed default — Option C in v0.3 Revision 1; classified as A-PRP-04-32 in §11.4). Walk-forward folds march forward at stride `fold_size_trading_days + embargo_trading_days` from `signal_date_min + initial_train_trading_days`, producing `fold_count` non-overlapping test windows whose union covers `[earliest_test_signal_date, latest_test_signal_date]` only. The pre-fold-1 portion `[signal_date_min, earliest_test_signal_date)` is the initial training period; any post-fold-N portion `(latest_test_signal_date, signal_date_max]` is unused and not silently consumed for any other purpose. **`fold_count` and `fold_size_trading_days` are independent knobs** — neither is derived from the other or from window length. The harness validates `latest_test_signal_date <= signal_date_max - max(horizon_trading_days)` (in trading days) at config-load time and raises `'fold_construction_failed'` otherwise.

The harness exposes the four backtest support windows SDR Decision 7 names — primary 2010–2025, longer robustness 2005–2025, recent-regime 2020–2025, monthly rebalance testing — as `backtest_window_label` values on `backtest.backtest_runs`. Adding a fifth label requires a Section 4 amendment.

### 6.3 Purge and embargo

Per SDR Decision 7, Phase 1 uses a 126-trading-day purge / embargo width as the SDR-named value. The exact arithmetic Section 4 applies:

- For each training row at `as_of_date = T_train` with horizon `h`, the row's forward window is `[entry_date(T_train, h), exit_date(T_train, h)]` per 03b §6.5.
- For each test row at `as_of_date = T_test`, Section 4's harness ensures **no training row's forward window overlaps the test window** by purging training rows whose `[entry_date, exit_date]` overlaps any `[entry_date(T_test, h), exit_date(T_test, h)]` for any active horizon. The harness reads the recorded `entry_date` and `exit_date` directly off `targets.target_values` and does not re-derive them.
- Embargo extends the purge by an additional `embargo_trading_days` value (Proposed default: 126 — SDR-named) on both sides of the test window's signal-date range, expressed in trading days per the relevant ETF's trading-day index.

Whether 126 trading days is the Phase 1 final value, or whether Section 4 should propose an alternative, is an Open Question for the Approver (see §10).

### 6.4 The simulated backtest ledger (`backtest.simulated_fills`)

The simulated fills ledger is a **per-signal-date, per-`(etf_id, simulated_action)` record of simulated trades** within a backtest run. **It is not paper portfolio state, not order intent, and not broker-facing.**

- The ledger's keying anchors to `(backtest_run_id, fold_id, etf_id, signal_date, horizon_trading_days, action)` where `action` is from a closed enum Section 4 introduces (`'enter_long'`, `'exit_long'`, `'rebalance_in'`, `'rebalance_out'`). **The action enum is intentionally distinct from Section 5's BUY / HOLD / TRIM / SELL / REPLACE / WATCH portfolio actions** to make the read-only / non-broker-facing nature of the ledger structurally explicit. Section 5's portfolio rules engine consumes neither this enum nor this ledger as authoritative state.
- The ledger records simulated entry / exit prices using `prices.etf_prices_daily.adjusted_close` per the Section 2 canonical convention (Section 4 does not redefine the adjusted-price convention).
- Cost adjustment is applied per ETF per simulated fill from `config/costs.yaml` per the consumption seam in §6.7. Buckets and basis-point values await SDR Decision 8 lock; the ledger's column shape supports a `cost_bucket`, `applied_cost_bps`, and `simulated_fill_price_after_cost` triple regardless of what those values eventually become.
- The ledger does not produce, write, or imply any `paper.*` table, any `order_intent.*` table, or any broker-routing record.

### 6.4.1 Backtest-only simulated allocation contract

To compute simulated fills, returns, turnover, drawdown, and attribution from `models.combined_scores`, Section 4 needs a minimal **hypothetical allocation rule** mapping per-`(signal_date, sleeve_id, horizon_trading_days)` ranked combined scores to a set of simulated long positions. **This rule is strictly internal to the backtest harness's validation purpose. It is not portfolio rules, not paper portfolio state, not order intent, not BUY / HOLD / TRIM / SELL / REPLACE / WATCH logic, and not broker-facing in any form.** Section 5 owns all real portfolio behavior and may use a completely different rule set; Section 4's allocation rule exists only to produce the simulated fills ledger required to evaluate model-layer signal quality.

**Builder Proposed default (subject to Approver approval; classified as A-PRP-04-24 in §11.4):**

- **Selection.** On each rebalance signal date `T`, for each `(sleeve_id, horizon_trading_days)` cross-section, select the top `N_per_sleeve_per_horizon` ETFs by `rank_within_sleeve` ascending (i.e., the highest combined-score ETFs). `N_per_sleeve_per_horizon` is configurable in `config/backtest.yaml` under `simulated_allocation.top_n_per_sleeve_per_horizon`; Builder Proposed default `N = 5` (mirrors the SDR Decision 10 *top 5 ETF positions initially* directional value, **but** Section 4 does not import or reuse Section 5's portfolio-rule top-N — it borrows the value as a research convenience and Section 5 may set its own independently).
- **Weighting.** Equal weight across the selected ETFs within a `(sleeve_id, horizon_trading_days)` cross-section: each selected ETF receives a hypothetical weight `1 / N_per_sleeve_per_horizon`. Cross-sleeve aggregation is equal weight across active sleeves; cross-horizon aggregation is equal weight across active horizons. **Per v0.3 Revision 4, weights are explicitly persisted on every `backtest.simulated_fills` row** via `simulated_weight_before`, `simulated_weight_after`, and `simulated_weight_delta` columns (see §6.5). Reconstruction from row counts is not used — explicit weights are the source of truth for turnover, attribution, and portfolio-value reconstruction. An `'enter_long'` row has `simulated_weight_before = 0.0` and `simulated_weight_after = 1 / N_per_sleeve_per_horizon`; an `'exit_long'` row has `simulated_weight_before = 1 / N_per_sleeve_per_horizon` and `simulated_weight_after = 0.0`; a `'rebalance_in'` / `'rebalance_out'` row records the actual before/after weights for that ETF at that rebalance, even when both are positive (e.g., a partial trim or add). `simulated_weight_delta = simulated_weight_after - simulated_weight_before` is denormalized for query convenience; a CHECK constraint enforces consistency.
- **Rebalance cadence.** Configurable per `backtest_window_label` under `windows.<label>.rebalance_cadence` in `config/backtest.yaml`. Builder Proposed default `'monthly'` (matching SDR Decision 7 *monthly rebalance testing*). Other values from a closed enum `('weekly', 'biweekly', 'monthly', 'quarterly')`; values outside the enum rejected at config-load time. **The rebalance cadence is a backtest-internal pacing parameter; it is not Section 5 review cadence.**
- **Position-exit triggers.** A simulated long position is exited at the next rebalance date when (a) the ETF falls out of the top `N_per_sleeve_per_horizon` for its `(sleeve_id, horizon_trading_days)` cross-section, or (b) the ETF's `combined_score` row is absent at the rebalance date (e.g., transitioned out of rank-eligibility — `'rebalance_out'` row written), or (c) the ETF transitions to ineligible per `universe.etf_eligibility_history` between rebalances (`'exit_long'` row written at the next rebalance date, not at the eligibility-change date — current Section 4 scope does not implement intra-rebalance exits). **No SDR Decision 10 ATR-based stop, take-profit rule, or replacement-vs-trim logic is applied here**; those belong to Section 5.
- **DiversifierHedge sleeves** under 03c A-PRP-29 Path X produce no `models.combined_scores` rows; the allocation rule produces no simulated fills for `DiversifierHedge` ETFs and no warning issue (the absence is the documented contract per §9 #8).
- **Cash / unallocated weight.** When fewer than `N_per_sleeve_per_horizon` rank-eligible ETFs exist in a sleeve cross-section, the unallocated weight is recorded as a synthetic non-traded "cash" position with zero return. No `backtest.simulated_fills` row is written for the cash slot in current Section 4 scope; the cash slot is reconstructed at metric-computation time from `1 - sum(actual ETF weights)`.

**Boundary clarifications (binding, not Proposed):**

- The simulated allocation contract produces only `backtest.simulated_fills` rows. **No `paper.*` row is produced. No `order_intent.*` row is produced. No `models.model_versions.state` transition is produced.** Static checks at §8.6 (CC-09, CC-10) and §8.12 (new ALC-* group below) verify.
- The closed `action` enum on `backtest.simulated_fills` (`'enter_long'`, `'exit_long'`, `'rebalance_in'`, `'rebalance_out'`) is the only enum the allocation rule writes. It does **not** map to BUY / HOLD / TRIM / SELL / REPLACE / WATCH. Any future Section 5 portfolio-action enum is a separate disjoint vocabulary.
- The allocation rule is long-only in Phase 1 per SDR Decision 8 / Section 1 invariant 2. No short-side simulated fill is permitted; the closed `action` enum has no short-side values.
- The rebalance cadence in `config/backtest.yaml` is independent of Section 5 review cadence in `config/portfolio.yaml`. The two are not coupled at the spec level; Section 5 defines its own.

### 6.5 Proposed `backtest.*` schema

**Whether introducing a new `backtest` schema requires a Section 2 amendment to register it with the application database is a Builder Proposed default per A-PRP-04-21.** Section 2 v1.0 LOCKED enumerates `universe`, `prices`, `ops`. Section 3a / 3b / 3c later added `features`, `targets`, `models` without explicit Section 2 amendments because the 03b / 03c approval notes treat the schema introduction as part of the section-finalization Approval Matrix item rather than a Section 2 amendment. Section 4 mirrors that handling unless the Approver directs otherwise.

The proposed tables (all Builder Proposed defaults requiring approval per EW §3.3):

#### `backtest.backtest_runs`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `backtest_run_id` | `bigserial` | PK | |
| `data_snapshot_id` | `bigint` | not null, FK → `ops.data_snapshots` | run is rejected if snapshot status is `'invalidated'` |
| `feature_run_id` | `bigint` | not null, FK → `features.feature_runs(feature_run_id)` | the snapshot's selected succeeded feature run |
| `feature_set_version` | `text` | not null | participates in the composite FK to `features.feature_runs(feature_run_id, feature_set_version)` |
| `target_run_id` | `bigint` | not null, FK → `targets.target_runs(target_run_id)` | the snapshot's selected succeeded target run |
| `target_set_version` | `text` | not null | participates in the composite FK to `targets.target_runs(target_run_id, target_set_version)` |
| `model_set_version` | `text` | not null | matches the 03c-active version at run start; recorded for audit |
| `backtest_window_label` | `text` | not null, CHECK in (`'primary_2010_2025'`, `'robustness_2005_2025'`, `'recent_regime_2020_2025'`, `'monthly_rebalance_test'`) | closed enum; new labels require Section 4 amendment |
| `signal_date_min` | `date` | not null | inclusive lower trading-day bound applied across all folds |
| `signal_date_max` | `date` | not null | inclusive upper trading-day bound; constrained `≤ ops.data_snapshots.price_table_max_as_of_date` |
| `fold_geometry_label` | `text` | not null | Builder Proposed default; closed-set values configured in `config/backtest.yaml` |
| `embargo_trading_days` | `integer` | not null | Proposed default 126 per SDR Decision 7 |
| `random_seed` | `bigint` | not null | for deterministic fold construction (separate from 03c training seed) |
| `commit_hash` | `text` | not null | code commit at run start |
| `config_hash` | `text` | not null | hash of `config/backtest.yaml` at run start |
| `mlflow_experiment_id` | `text` | nullable | populated only if backtest MLflow experiments are enabled per §10 / §11 |
| `mlflow_run_id` | `text` | nullable, unique when not null | populated only if backtest MLflow tracking is enabled |
| `current_survivor_disclosure_label` | `text` | not null | populated at run-open time from `common.get_current_survivor_label()` (Section 2 retrieval function, sourced from `config/universe.yaml` `disclosures.current_survivor_label` per Section 2 v1.0 LOCKED). NOT NULL enforces SDR Decision 4's directional-learning-not-statistical-proof labeling on every backtest run. The label string is recorded on every backtest run for downstream UI surfacing per Section 6 and for any external reporting; it is **not** consulted by Section 4's metric or attribution logic. |
| `is_pipeline_validation_only` | `boolean` | not null default `false` | when `true`, this backtest run was executed under a pipeline-validation-only condition (currently: `cost_config_zero_fallback` per A-PRP-04-14 + A-PRP-04-35) and **must not** be used as serious model validation evidence or promotion evidence. Section 5's promotion-gate logic must filter on `is_pipeline_validation_only = false` for any promotion-eligibility evaluation. Per v0.3 Revision 5. |
| `pipeline_validation_only_reason` | `text` | nullable, CHECK ((`is_pipeline_validation_only = true AND pipeline_validation_only_reason IS NOT NULL AND pipeline_validation_only_reason IN ('cost_config_zero_fallback')`) OR (`is_pipeline_validation_only = false AND pipeline_validation_only_reason IS NULL`)) | closed enum populated only when the flag is `true`; the conditional NULL is enforced by CHECK. v0.3 Phase 1 enum: `'cost_config_zero_fallback'`. New reason codes require a Section 4 amendment per A-PRP-04-36. |
| `started_at_utc` | `timestamptz` | not null default `now()` | |
| `completed_at_utc` | `timestamptz` | nullable | |
| `status` | `text` | not null, CHECK in (`'running'`, `'succeeded'`, `'failed'`) | parallel to 3a / 3b / 3c three-value enum; no `'blocked'` or `'partial'` value |
| `error_message` | `text` | nullable | populated on `'failed'` |
| `created_by` | `text` | not null | container or user identifier |
| `notes` | `text` | nullable | |

Indexes: `(data_snapshot_id)`, `(feature_run_id)`, `(target_run_id)`, `(backtest_window_label, started_at_utc)`.

#### `backtest.backtest_folds`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `backtest_run_id` | `bigint` | not null, FK → `backtest.backtest_runs` | |
| `fold_id` | `text` | not null | Section-4-issued within a run; PK component |
| `fold_index` | `integer` | not null | ordinal position |
| `train_signal_date_min` | `date` | not null | |
| `train_signal_date_max` | `date` | not null | |
| `test_signal_date_min` | `date` | not null | |
| `test_signal_date_max` | `date` | not null | |
| `embargo_signal_date_min` | `date` | not null | |
| `embargo_signal_date_max` | `date` | not null | |
| `purge_signal_date_ranges` | `jsonb` | not null | array of `[min, max]` ranges; computed from 03b per-row metadata |
| | | PK (`backtest_run_id`, `fold_id`) | |
| | | UNIQUE (`backtest_run_id`, `fold_index`) | |

Indexes: `(backtest_run_id)`, `(test_signal_date_min, test_signal_date_max)`.

#### `backtest.simulated_fills`

The simulated fills ledger. Keyed by `(backtest_run_id, fold_id, etf_id, signal_date, horizon_trading_days, action)`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `backtest_run_id` | `bigint` | not null, FK → `backtest.backtest_runs` | |
| `fold_id` | `text` | not null | participates in composite FK to `backtest.backtest_folds(backtest_run_id, fold_id)` |
| `etf_id` | `bigint` | not null, FK → `universe.etfs` | |
| `signal_date` | `date` | not null | OOS test signal date |
| `simulated_entry_date` | `date` | not null | per Convention B inherited from 03b: `signal_date + 1` trading day on the relevant ETF's trading-day index |
| `simulated_exit_date` | `date` | nullable | populated for closed simulated trades |
| `horizon_trading_days` | `integer` | not null, CHECK in (63, 126) | per 03b active horizons |
| `action` | `text` | not null, CHECK in (`'enter_long'`, `'exit_long'`, `'rebalance_in'`, `'rebalance_out'`) | closed enum; intentionally disjoint from Section 5 portfolio actions |
| `sleeve_id` | `bigint` | not null, FK → `universe.sleeves` | from `models.combined_scores` row |
| `combined_score` | `numeric(24,12)` | nullable | from `models.combined_scores`; nullable to handle `DiversifierHedge` zero-rows under A-PRP-29 |
| `rank_within_sleeve` | `integer` | nullable | from `models.combined_scores` |
| `simulated_fill_price_pre_cost` | `numeric(24,12)` | not null | adjusted-close per Section 2 canonical convention |
| `cost_bucket` | `text` | nullable, CHECK in (`'ultra_liquid_etf'`, `'liquid_sector_etf'`, `'thematic_niche_etf'`, `'commodity_specialty_etf'`) when not null | per SDR Decision 8 locked four-value enum; nullable when no per-ETF mapping is resolved (e.g., pre-cost-config rows under A-PRP-04-14) |
| `applied_cost_bps` | `numeric(10,4)` | nullable | per `config/costs.yaml`; per-bucket basis-point values are Builder Proposed defaults / Open Questions per §10 / §11 |
| `simulated_fill_price_after_cost` | `numeric(24,12)` | not null | post-cost simulated price |
| `simulated_weight_before` | `numeric(12,8)` | not null, CHECK (`simulated_weight_before >= 0 AND simulated_weight_before <= 1`) | the simulated portfolio weight on this ETF immediately before this fill action; `'enter_long'` rows have `0.0` |
| `simulated_weight_after` | `numeric(12,8)` | not null, CHECK (`simulated_weight_after >= 0 AND simulated_weight_after <= 1`) | the simulated portfolio weight on this ETF immediately after this fill action; `'exit_long'` rows have `0.0` |
| `simulated_weight_delta` | `numeric(13,8)` | not null, CHECK (`simulated_weight_delta = simulated_weight_after - simulated_weight_before`) | denormalized for query convenience; consistency enforced by CHECK; turnover is computed from the absolute value summed over rebalance events |
| `prediction_context_consumed` | `text` | not null, CHECK in (`'walk_forward_oos'`) | Section 4 reads only OOS rows for fills |
| `model_run_id` | `bigint` | not null, FK → `models.model_runs` | the model run that produced the underlying prediction |
| `scoring_run_id` | `bigint` | not null, FK → `models.scoring_runs` | the scoring run that produced the underlying combined score |
| | | PK (`backtest_run_id`, `fold_id`, `etf_id`, `signal_date`, `horizon_trading_days`, `action`) | per-horizon keying — see *Per-horizon keying note* below |
| | | Composite FK (`backtest_run_id`, `fold_id`) → `backtest.backtest_folds(backtest_run_id, fold_id)` | |

Indexes: `(backtest_run_id, signal_date)`, `(etf_id, signal_date)`, `(model_run_id)`, `(scoring_run_id)`, `(horizon_trading_days)`.

**Per-horizon keying note (Builder Proposed default — Option A).** A backtest run may produce simulated fills for both Phase 1 active horizons (63d, 126d) within the same fold and signal date, since Section 4 inherits 03b's horizon set `{63, 126}` and 03c's six-value `model_kind` enumeration covering both horizons. To avoid PK collisions when both horizons emit a fill for the same `(etf_id, signal_date, action)` tuple, `horizon_trading_days` is part of the primary key and propagates into all downstream composite FKs that reference `backtest.simulated_fills` (specifically `attribution.trade_attribution`; see §6.6). The alternative (Option B — defining a backtest run as evaluating one selected horizon only, requiring a `horizon_trading_days` column on `backtest.backtest_runs` and rejecting cross-horizon fills) is **not** the Builder Proposed default because it precludes Phase 1 backtest runs that compare 63d-vs-126d horizon performance within a single reproducible run, which the SDR Decision 7 robustness-window discipline plausibly wants.

**Null-vs-no-row taxonomy for `backtest.simulated_fills`:**

- **No row is written for `(etf_id, signal_date)` when:** the ETF is rank-ineligible at that signal date (absence in `features.feature_values` and `targets.target_values`), the ETF is sleeve-mapped to a `rank_method` that produces no `models.combined_scores` rows (currently `DiversifierHedge` per A-PRP-29 Path X), the rebalance schedule does not hit that signal date for the active fold geometry, or the `signal_date` is not a test-window date for any fold (i.e., the date falls in the initial-training period or in a purge / embargo region around test windows where no fold's test set covers it). These cases are absences in the simulated fills ledger; they do not produce rows with NULL columns. **Purge / embargo regions never disqualify simulated fills for dates that ARE in some fold's test window** (per v0.3 R2 OOS-purge correction).
- **A row IS written with `combined_score = NULL` and `rank_within_sleeve = NULL` only if** Section 4 explicitly chooses (Builder Proposed default) to record a `'rebalance_out'` row for an ETF that was previously simulated long and is being exited because its combined score row is absent at the rebalance date (e.g., the ETF transitioned out of rank-eligibility). The `simulated_fill_price_pre_cost` and `simulated_fill_price_after_cost` are not null for any row.

#### `backtest.fold_metrics`

Per-`(backtest_run_id, fold_id, horizon_trading_days, sleeve_id, metric_name)` metric values. The exact metric set is a Builder Proposed default (§10). **`metric_name` is a clean closed enum and does not encode horizon or sleeve;** those are first-class columns instead per v0.3 Revision 3.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `fold_metric_id` | `bigserial` | primary key | surrogate PK per v0.4 Revision 1 / A-PRP-04-37; required because the logical-uniqueness columns include nullable `horizon_trading_days` and `sleeve_id`, which cannot participate in a primary key |
| `backtest_run_id` | `bigint` | not null, FK → `backtest.backtest_runs` | |
| `fold_id` | `text` | not null | participates in composite FK |
| `horizon_trading_days` | `integer` | nullable, CHECK in (63, 126) when not null | NULL when the metric is horizon-agnostic (e.g., `turnover` aggregated across horizons); set to 63 or 126 when the metric is computed within a single-horizon cross-section |
| `sleeve_id` | `bigint` | nullable, FK → `universe.sleeves` | NULL when the metric is sleeve-agnostic; set when the metric is `sleeve_level_performance` or any other sleeve-cross-sectioned metric |
| `metric_name` | `text` | not null | from a closed enum Section 4 specifies in `config/backtest.yaml`; specific names are Proposed defaults; **does not encode horizon or sleeve** |
| `metric_value` | `numeric(24,12)` | nullable | NULL permitted when the metric is undefined for the fold (e.g., zero trades) |
| | | UNIQUE NULLS NOT DISTINCT (`backtest_run_id`, `fold_id`, `horizon_trading_days`, `sleeve_id`, `metric_name`) | logical uniqueness; treats NULL values as equal so that a single `(backtest_run_id, fold_id, NULL, NULL, 'turnover')` row is unique. Postgres 15+. For Postgres < 15, the equivalent constraint is a UNIQUE index on `(backtest_run_id, fold_id, COALESCE(horizon_trading_days, -1), COALESCE(sleeve_id, -1), metric_name)`. Implementation choice per A-IMP-06. |
| | | Composite FK (`backtest_run_id`, `fold_id`) → `backtest.backtest_folds` | |

Indexes: `(backtest_run_id, fold_id, metric_name)`, `(metric_name, horizon_trading_days)`, `(sleeve_id, metric_name)`.

#### `backtest.aggregate_metrics`

Per-`(backtest_run_id, horizon_trading_days, sleeve_id, metric_name)` aggregate metric values across folds. Same dimensioning discipline as `backtest.fold_metrics`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `aggregate_metric_id` | `bigserial` | primary key | surrogate PK per v0.4 Revision 1 / A-PRP-04-37 |
| `backtest_run_id` | `bigint` | not null, FK → `backtest.backtest_runs` | |
| `horizon_trading_days` | `integer` | nullable, CHECK in (63, 126) when not null | as in `fold_metrics` |
| `sleeve_id` | `bigint` | nullable, FK → `universe.sleeves` | as in `fold_metrics` |
| `metric_name` | `text` | not null | closed enum from `config/backtest.yaml`; Proposed default |
| `metric_value` | `numeric(24,12)` | nullable | |
| | | UNIQUE NULLS NOT DISTINCT (`backtest_run_id`, `horizon_trading_days`, `sleeve_id`, `metric_name`) | logical uniqueness per A-IMP-06; Postgres 15+ syntax; older-version COALESCE fallback applies |

#### `backtest.regime_metrics`

Per-`(backtest_run_id, regime_label, horizon_trading_days, sleeve_id, metric_name)` regime-conditioned metric values. Populated only when the regime classifier is available (per A-OQ-04-07 ownership choice).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `regime_metric_id` | `bigserial` | primary key | surrogate PK per v0.4 Revision 1 / A-PRP-04-37 |
| `backtest_run_id` | `bigint` | not null, FK → `backtest.backtest_runs` | |
| `regime_label` | `text` | not null | closed enum specified in `config/regime.yaml`; the Phase 1 SDR Decision 9 default produces up to four labels (`risk_on_low_vol`, `risk_on_high_vol`, `risk_off_low_vol`, `risk_off_high_vol`); Proposed default |
| `horizon_trading_days` | `integer` | nullable, CHECK in (63, 126) when not null | as in `fold_metrics` |
| `sleeve_id` | `bigint` | nullable, FK → `universe.sleeves` | as in `fold_metrics` |
| `metric_name` | `text` | not null | |
| `metric_value` | `numeric(24,12)` | nullable | |
| | | UNIQUE NULLS NOT DISTINCT (`backtest_run_id`, `regime_label`, `horizon_trading_days`, `sleeve_id`, `metric_name`) | logical uniqueness per A-IMP-06 |

When the VIX-based volatility dimension is unavailable (per SDR Decision 9 deferral rule), only the trend dimension is reported and `regime_label` values are limited to `risk_on` / `risk_off`. Section 4 adopts the partial-dimension fallback by default per A-PRP-04-13 (`regime_reporting.classifier_unavailable_behavior: 'emit_partial_with_warning'`); alternative runtime behaviors (`'skip_with_warning'`, `'fail'`) are configurable.

#### `backtest.backtest_run_issues`

Section-4-layer issue log. Disjoint from `models.model_run_issues` and `models.scoring_run_issues` per the disjoint-issue-log discipline 3a / 3b / 3c establish.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `backtest_run_issue_id` | `bigserial` | PK | |
| `backtest_run_id` | `bigint` | not null, FK → `backtest.backtest_runs` | |
| `issue_type` | `text` | not null, CHECK in closed enum (Proposed default; see below) | |
| `severity` | `text` | not null, CHECK in (`'warning'`, `'fail'`) | parallel to 3a / 3b / 3c |
| `summary` | `text` | not null | |
| `detail` | `text` | nullable | |
| `etf_id` | `bigint` | nullable, FK → `universe.etfs` | sparse |
| `fold_id` | `text` | nullable | sparse |
| `created_at_utc` | `timestamptz` | not null default `now()` | |

**Proposed closed `issue_type` enum** (Builder Proposed default; subject to Approver approval and disjoint from the 03c enum):

- `'invalidated_snapshot_blocked'`
- `'snapshot_mismatch'`
- `'all_folds_failed'`
- `'failed_feature_run_blocked'`
- `'failed_target_run_blocked'`
- `'failed_model_run_blocked'`
- `'failed_scoring_run_blocked'`
- `'fold_construction_failed'`
- `'purge_embargo_violation'`
- `'oos_qualification_violation'`
- `'cost_config_unavailable'`
- `'regime_classifier_unavailable'`
- `'simulated_fill_pricing_failed'`
- `'metric_computation_failed'`
- `'mlflow_unreachable'`

### 6.6 Proposed `attribution.*` schema

#### `attribution.attribution_runs`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `attribution_run_id` | `bigserial` | PK | |
| `backtest_run_id` | `bigint` | not null, FK → `backtest.backtest_runs` | one attribution run per backtest run; future amendments may relax |
| `attribution_set_version` | `text` | not null | matches `config/backtest.yaml` `attribution.set_version` |
| `commit_hash` | `text` | not null | |
| `config_hash` | `text` | not null | |
| `started_at_utc` | `timestamptz` | not null default `now()` | |
| `completed_at_utc` | `timestamptz` | nullable | |
| `status` | `text` | not null, CHECK in (`'running'`, `'succeeded'`, `'failed'`) | |
| `error_message` | `text` | nullable | |
| `created_by` | `text` | not null | |

Indexes: `(backtest_run_id)`.

#### `attribution.signal_attribution`

Per-`(attribution_run_id, etf_id, signal_date, horizon_trading_days)` decomposition of how each signal contributed to fold-level performance.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `attribution_run_id` | `bigint` | not null, FK → `attribution.attribution_runs` | |
| `etf_id` | `bigint` | not null, FK → `universe.etfs` | |
| `signal_date` | `date` | not null | |
| `horizon_trading_days` | `integer` | not null, CHECK in (63, 126) | |
| `sleeve_id` | `bigint` | not null, FK → `universe.sleeves` | |
| `attribution_components` | `jsonb` | not null | component-name → component-value; component closed-set named in `config/backtest.yaml` (Proposed default) |
| `total_attribution` | `numeric(24,12)` | not null | sum-equal-or-residual relationship to `attribution_components` per a Builder Proposed default (§10) |
| | | PK (`attribution_run_id`, `etf_id`, `signal_date`, `horizon_trading_days`) | |

Indexes: `(attribution_run_id)`, `(etf_id, signal_date)`.

#### `attribution.trade_attribution`

Per-`(attribution_run_id, backtest_run_id, fold_id, etf_id, signal_date, horizon_trading_days, action)` decomposition of how each simulated fill contributed.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `attribution_run_id` | `bigint` | not null, FK → `attribution.attribution_runs` | |
| `backtest_run_id` | `bigint` | not null | participates in composite FK to `backtest.simulated_fills` |
| `fold_id` | `text` | not null | participates in composite FK |
| `etf_id` | `bigint` | not null, FK → `universe.etfs` | |
| `signal_date` | `date` | not null | |
| `horizon_trading_days` | `integer` | not null, CHECK in (63, 126) | participates in composite FK to `backtest.simulated_fills` per §6.5 per-horizon keying note |
| `action` | `text` | not null | |
| `attribution_components` | `jsonb` | not null | component closed-set in `config/backtest.yaml` |
| `total_attribution` | `numeric(24,12)` | not null | |
| | | PK (`attribution_run_id`, `backtest_run_id`, `fold_id`, `etf_id`, `signal_date`, `horizon_trading_days`, `action`) | |
| | | Composite FK (`backtest_run_id`, `fold_id`, `etf_id`, `signal_date`, `horizon_trading_days`, `action`) → `backtest.simulated_fills` | |

#### `attribution.attribution_run_issues`

Parallel to `backtest.backtest_run_issues`. Closed `issue_type` enum (Proposed default): `'failed_backtest_run_blocked'`, `'backtest_run_not_succeeded'`, `'attribution_decomposition_failed'`, `'component_set_unrecognized'`, `'mlflow_unreachable'`.

### 6.7 Cost-application consumption seam

**SDR Decision 8 locks the four Phase 1 cost-bucket names:** `ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`. Section 4 inherits the locked enumeration and consumes it without re-defining or re-naming.

Section 4 reads from `config/costs.yaml` two pieces of information per simulated fill: a `cost_bucket` for the `etf_id` (one of the four locked SDR Decision 8 values) and a per-bucket `cost_bps` value. The seam:

- accepts a per-ETF cost-bucket lookup (the bucket-per-ETF mapping itself is upstream — typically held in `universe.etfs.cost_bucket` per a future Section 2 amendment, or in `config/costs.yaml` directly; Section 4 does not pin where the per-ETF mapping lives);
- accepts a per-bucket basis-point value from `config/costs.yaml`;
- applies cost to `simulated_fill_price_pre_cost` to produce `simulated_fill_price_after_cost` per the **long-only-corrected** formula:
  - **Entry (long buy):** `simulated_fill_price_after_cost = simulated_fill_price_pre_cost * (1 + cost_bps / 10000)` — the simulated buyer pays *above* mid by the bucket's bps.
  - **Exit (long sell):** `simulated_fill_price_after_cost = simulated_fill_price_pre_cost * (1 - cost_bps / 10000)` — the simulated seller receives *below* mid by the bucket's bps.

  This is the directionally correct round-trip cost for long-only Phase 1 simulated fills. (No short-side cost is applied because Phase 1 is long-only per SDR Decision 8.)

- writes `cost_bucket` (one of the four locked enum values), `applied_cost_bps`, and `simulated_fill_price_after_cost` to `backtest.simulated_fills` for audit. The `cost_bucket` column on `backtest.simulated_fills` (§6.5) carries a `CHECK` constraint enforcing the four-value closed enum so any future bucket-name drift is caught at write time.

If `config/costs.yaml` is absent or its bucket-to-bps section is empty (e.g., before Approver populates per-bucket values), Section 4's harness has two Builder-proposed runtime options: (a) record `cost_bucket` (still resolved if the per-ETF mapping exists), `applied_cost_bps = 0`, `simulated_fill_price_after_cost = simulated_fill_price_pre_cost`, **set `backtest.backtest_runs.is_pipeline_validation_only = true` and `pipeline_validation_only_reason = 'cost_config_zero_fallback'` (per v0.3 Revision 5 / A-PRP-04-35 / A-PRP-04-36)**, and emit a `'warning'` `backtest.backtest_run_issues` row with `issue_type='cost_config_unavailable'` (proceed-with-zero-cost behavior, but the run is structurally labeled pipeline-validation-only); or (b) refuse to start the backtest run with `'fail'` severity and the same `issue_type`. Option (a) is the Builder Proposed default per A-PRP-04-14; the runtime choice between (a) and (b) is configurable in `config/backtest.yaml`. **Under option (a), Section 5's promotion-gate logic must reject the run as promotion evidence by filtering on `is_pipeline_validation_only = false`.** Section 4's contract is to set the flag correctly and surface the reason; Section 5 owns the gate enforcement.

### 6.8 Reproducibility chain

Mirroring 03c §6.12, Section 4 uses **transitive linkage** to `data_snapshot_id`:

- **Run-level (denormalized):** `backtest.backtest_runs.data_snapshot_id` is recorded redundantly for query convenience.
- **Run-level (canonical):** the canonical `data_snapshot_id` for a backtest run is reachable via `backtest.backtest_runs.feature_run_id → features.feature_runs.data_snapshot_id` AND via `backtest.backtest_runs.target_run_id → targets.target_runs.data_snapshot_id`. The two must equal each other and equal the denormalized field; the harness validates this at run-open time and writes `'fail'` `issue_type='snapshot_mismatch'` (per the §6.5 closed enum) on violation.
- **Row-level traceability:** every `backtest.simulated_fills` row links to a `backtest.backtest_runs` row and (via `model_run_id` / `scoring_run_id`) to the upstream model and scoring runs, transitively to the feature and target runs and to the snapshot. Every `attribution.signal_attribution` and `attribution.trade_attribution` row links to an `attribution_runs` row and (via `backtest_run_id`) to the same chain.

**Single-source-of-truth invariant.** Section 4 does not store a separate `data_snapshot_id` on `backtest.simulated_fills`, `backtest.fold_metrics`, `backtest.aggregate_metrics`, `backtest.regime_metrics`, `attribution.signal_attribution`, or `attribution.trade_attribution`. The chain is `simulated_fills → backtest_runs → ops.data_snapshots`.

### 6.9 The validation evidence surface

**Section 4 produces validation evidence; Section 5 evaluates promotion gates and the kill switch.**

The evidence surface comprises:

- the `backtest.fold_metrics` and `backtest.aggregate_metrics` rows for one or more `backtest.backtest_runs` rows;
- the `backtest.regime_metrics` rows when the regime classifier is available;
- the `attribution.signal_attribution` and `attribution.trade_attribution` rows for the corresponding `attribution.attribution_runs` rows;
- the leakage-test outcome on the harness's own test suite (test rows do not write to the schemas above; test outcomes are reported by the test runner, not stored in `backtest.*`);
- the reproducibility metadata on every `backtest.backtest_runs` row (commit hash, config hash, `data_snapshot_id`, MLflow run ID when present);
- the `backtest.backtest_run_issues` and `attribution.attribution_run_issues` rows for any warnings or failures.

The surface is read-only-consumed by:

- Section 5's promotion-gate logic (which Section 5 owns);
- Section 5's kill-switch evaluation (which Section 5 owns);
- Section 6's UI (read-only display).

Section 4's contract is that the surface is correct and reproducible. Section 4's contract is **not** to evaluate gates.

### 6.10 Financial metric definitions

The metric names referenced in §7.1 (`config/backtest.yaml`) and §6.5 (`backtest.fold_metrics`, `backtest.aggregate_metrics`, `backtest.regime_metrics`) carry the formulas, units, annualization conventions, null behavior, and benchmark-relative behavior defined here. **Test wording in §8 verifies the financial meaning of each metric, not just row existence.**

All return values used in the formulas below are **simulated** returns derived from `backtest.simulated_fills` rows (post-cost prices). All daily values are on the trading-day index of the relevant ETF / portfolio per Convention B inherited from 03b. The annualization factor for trading days is `252` (Builder Proposed default; A-PRP-04-25).

| Metric name | Formula | Unit | Annualization | Null behavior | Benchmark-relative? |
|---|---|---|---|---|---|
| `total_return` | `(V_end / V_start) - 1`, where `V_t` is the simulated portfolio value time series reconstructed from `backtest.simulated_fills` post-cost prices and the §6.4.1 equal-weight allocation | dimensionless (decimal; 0.10 = 10%) | none (period-cumulative) | NULL when fewer than two valid `V_t` points exist for the period | absolute; `benchmark_relative_return` is computed separately |
| `cagr` | `(V_end / V_start) ^ (252 / N_trading_days) - 1`, where `N_trading_days` is the count of trading days in the period | dimensionless (decimal annual) | annualized by definition | NULL when `N_trading_days < 21` (Builder Proposed default minimum sample) | absolute |
| `volatility` | `stdev(daily_returns) * sqrt(252)`, where `daily_returns_t = V_t / V_{t-1} - 1` | dimensionless (decimal annual) | annualized via `sqrt(252)` | NULL when fewer than 21 daily-return points | absolute |
| `max_drawdown` | `min_t( V_t / max_{s <= t}(V_s) - 1 )` over the period | dimensionless (decimal; negative or zero) | none | NULL when fewer than two valid `V_t` points | absolute |
| `risk_adjusted_return` (Sharpe-like) | `(cagr - risk_free_rate_annual) / volatility`; `risk_free_rate_annual` is configurable in `config/backtest.yaml` under `metrics.risk_free_rate_annual` (Builder Proposed default `0.0` for Phase 1 simplicity per A-PRP-04-26) | dimensionless | annualized by construction (cagr and vol both annual) | NULL when `volatility = 0` or `volatility IS NULL` | absolute. **Named explicitly as "risk-adjusted return" rather than "Sharpe ratio"** because Phase 1 uses a fixed configurable risk-free rate rather than a true T-bill series; the metric is Sharpe-shaped but not strictly the textbook Sharpe ratio. |
| `hit_rate` | Per fold: `(count of `'exit_long'` and `'rebalance_out'` rows where the round-trip simulated post-cost return is strictly positive) / (count of all such closing rows)`. A "round-trip" pairs each closing row with its prior `'enter_long'` or `'rebalance_in'` for the same `(etf_id, horizon_trading_days)` | dimensionless (decimal in `[0, 1]`) | none | NULL when zero closing rows exist for the period | absolute |
| `turnover` | Per fold: `(sum of |simulated_weight_delta| across all `backtest.simulated_fills` rows in the fold) / (count of distinct rebalance events in the fold)`. The explicit `simulated_weight_delta` column on each fill row makes this deterministic without reconstruction from row counts. | dimensionless (decimal per rebalance) | none | NULL when zero rebalance events | absolute |
| `cost_drag` | `total_return_pre_cost - total_return_post_cost`; both are computed identically except `total_return_pre_cost` substitutes `simulated_fill_price_pre_cost` for `simulated_fill_price_after_cost` in the value-series reconstruction | dimensionless (decimal) | none | NULL when `total_return` is NULL | absolute; quantifies how much SDR Decision 8 cost application reduces returns |
| `benchmark_relative_return` | `total_return - benchmark_total_return`, where `benchmark_total_return` is computed from `prices.etf_prices_daily.adjusted_close` for the per-ETF `primary_benchmark_id` (or, for portfolio-level rollup, a Builder-Proposed weighted-average of per-ETF benchmark returns; A-PRP-04-27) | dimensionless (decimal) | none (period-cumulative) | NULL when any constituent benchmark series is missing inside the period | **benchmark-relative**. **No fallback to `secondary_benchmark_id`** per the global rule. |
| `sleeve_level_performance` | `total_return` and `cagr` computed within a single `sleeve_id` cross-section using only that sleeve's simulated fills | dimensionless (decimal) | as per `total_return` and `cagr` | NULL when zero sleeve simulated fills | absolute (per sleeve) |
| `regime_conditioned_performance` | `total_return`, `cagr`, `volatility`, `max_drawdown`, `risk_adjusted_return`, and `hit_rate` recomputed using only the subset of trading days whose regime label per the regime classifier (when available, per A-OQ-04-07) equals a given `regime_label` | dimensionless | as per the underlying metric | NULL when the regime classifier is unavailable for the period or zero trading days carry the label | absolute (per regime) |
| `fold_consistency` | At the aggregate level only: `1 - (stdev(per_fold_total_return) / abs(mean(per_fold_total_return)))` — a coefficient-of-variation-style measure of how stable per-fold returns are across folds | dimensionless | none | NULL when `mean(per_fold_total_return) = 0` or fewer than two folds | absolute (across-fold) |

**The metric set above is canonical for the current Section 4 scope.** Adding a metric requires a Section 4 amendment. The closed list is enforced by `validation.reject_unknown_metric_name: true` in `config/backtest.yaml` (§7.1).

**Null-vs-no-row semantics for metric tables.** A metric whose formula returns NULL is written as a row with `metric_value IS NULL` to `backtest.fold_metrics` / `backtest.aggregate_metrics` / `backtest.regime_metrics`; the row is **not** absent. This makes "the metric was attempted but undefined for this period" distinguishable from "the metric was not configured for this run." A metric not configured in `config/backtest.yaml` produces no row at all.

**Benchmark resolution for `benchmark_relative_return`.** The per-ETF benchmark is `universe.etfs.primary_benchmark_id` per Section 2 v1.0 LOCKED. **No fallback to `secondary_benchmark_id`** (Section 4 inherits the global no-silent-benchmark-substitution rule). When the per-ETF primary benchmark resolves index-only on the trading-day index (per 03a §10.1 / 03b §11.6 #6 interim constraint), `benchmark_relative_return` for that ETF's contribution is NULL and the portfolio-level rollup propagates NULL or excludes the ETF per A-PRP-04-27.

---

## 7. Config dependencies

### 7.1 File Section 4 owns: `config/backtest.yaml` (proposed)

**Ownership note.** Section 1 v1.0 LOCKED's *Config dependencies* table enumerates `config/universe.yaml`, `config/features.yaml`, `config/model.yaml`, `config/portfolio.yaml`, `config/costs.yaml`, `config/regime.yaml` — six files. The table assigns *walk-forward window and embargo configuration per SDR Decisions 5, 6, 7* to `config/model.yaml`. 03c v1.0 LOCKED carves `config/model.yaml` as **exclusively 03c-owned** (constraint #14 in the 03c approval note §4: "`config/model.yaml` is the only YAML file 03c owns. Section 4 owns its own YAML (`config/backtest.yaml` or equivalent — Section 4 will name)"). Section 4 cannot put walk-forward window and embargo configuration in `config/model.yaml` without violating 03c's lock. Two options are visible to the Builder:

- **Option A (Builder Proposed default):** Introduce a new `config/backtest.yaml` file. This requires verifying whether the introduction triggers a Section 1 amendment (the table currently lists six files; adding a seventh is a config-dependencies-table edit). The 03b / 03c handling pattern was that the Section 1 table already enumerated the file (`config/targets.yaml` for 03b is *not* in the table — 03b nonetheless proceeded without a Section 1 amendment per 03b §11.6 #7; `config/model.yaml` for 03c *is* in the table). For Section 4, `config/backtest.yaml` is *not* in the table. Whether a Section 1 amendment is required is **an Open Question** (§10).
- **Option B:** Place walk-forward and embargo configuration in `config/regime.yaml` (already enumerated and already shared between Sections 3 and 4). This conflates regime and backtest scope; not Builder-recommended.

Builder proposes Option A and flags the Section 1 amendment question.

The proposed `config/backtest.yaml` shape (Builder Proposed default; subject to Approver approval):

```yaml
# config/backtest.yaml — Section 4 owned (proposed)
# All backtest-harness, validation, attribution, and regime-reporting
# parameters consumed by Section 4 modules.

backtest_set_version: "backtest_v1"

walk_forward:
  fold_geometry: "rolling"  # closed enum: ('rolling', 'expanding'); Proposed default 'rolling'
  fold_count: 8             # Proposed default; independent knob (per v0.3 R1 Option C — folds do not partition the full window)
  fold_size_trading_days: 252  # Proposed default; one trading year per fold; independent knob
  expanding_initial_train_trading_days: 1260  # used only when fold_geometry='expanding'
  initial_train_trading_days: 1260  # rolling-mode initial training window before fold 1's test window starts; Proposed default
  embargo_trading_days: 126  # SDR Decision 7 named width; Proposed default

windows:
  primary_2010_2025:
    signal_date_min: "2010-01-04"
    signal_date_max: "2025-12-31"
    rebalance_cadence: "monthly"
  robustness_2005_2025:
    signal_date_min: "2005-01-03"
    signal_date_max: "2025-12-31"
    rebalance_cadence: "monthly"
  recent_regime_2020_2025:
    signal_date_min: "2020-01-02"
    signal_date_max: "2025-12-31"
    rebalance_cadence: "monthly"
  monthly_rebalance_test:
    signal_date_min: null  # caller-supplied
    signal_date_max: null  # caller-supplied
    rebalance_cadence: "monthly"

oos_qualification:
  prediction_context_value: "walk_forward_oos"  # Section 4 supplies; 03c stores
  reject_in_sample_for_performance_eval: true
  reject_current_scoring_for_performance_eval: true

simulated_fills:
  action_enum: ["enter_long", "exit_long", "rebalance_in", "rebalance_out"]
  pricing_basis: "adjusted_close"  # Section 2 canonical convention; not configurable
  cost_application:
    # Long-only Phase 1 per SDR Decision 8: simulated buyer pays above mid; simulated seller receives below mid.
    on_entry: "multiply_by_one_plus_bps"   # entry: pre_cost_price * (1 + cost_bps / 10000)
    on_exit:  "multiply_by_one_minus_bps"  # exit:  pre_cost_price * (1 - cost_bps / 10000)
  cost_bucket_enum: ["ultra_liquid_etf", "liquid_sector_etf", "thematic_niche_etf", "commodity_specialty_etf"]  # locked by SDR Decision 8
  cost_config_missing_behavior: "warn_proceed_zero_cost"  # closed enum ('warn_proceed_zero_cost', 'fail'); Builder Proposed default per A-PRP-04-14

simulated_allocation:
  # Backtest-only allocation rule per §6.4.1. NOT Section 5 portfolio rules.
  top_n_per_sleeve_per_horizon: 5  # Builder Proposed default per A-PRP-04-24
  weighting: "equal_weight"        # closed enum ('equal_weight'); future amendments may add more
  long_only: true                  # not configurable; Phase 1 long-only per SDR Decision 8

metrics:
  # Closed metric set per §6.10. Canonical for current Section 4 scope; new names require a Section 4 amendment.
  per_fold:
    enabled: ["total_return", "cagr", "volatility", "max_drawdown", "risk_adjusted_return", "hit_rate", "turnover", "cost_drag", "benchmark_relative_return", "sleeve_level_performance"]
  aggregate:
    enabled: ["total_return", "cagr", "volatility", "max_drawdown", "risk_adjusted_return", "hit_rate", "turnover", "cost_drag", "benchmark_relative_return", "sleeve_level_performance", "fold_consistency"]
  trading_days_per_year: 252                # annualization factor; A-PRP-04-25
  risk_free_rate_annual: 0.0                # used in risk_adjusted_return; A-PRP-04-26
  benchmark_relative_rollup: "weighted_by_sleeve_weight"  # closed enum; A-PRP-04-27

regime_reporting:
  enabled: true
  # Regime classifier (labeler) ownership is an Open Question — A-OQ-04-07 in §10:
  #   Option A — Section 4 owns a minimal SDR Decision 9 regime labeler in regime/ (Builder recommended)
  #   Option B — a future approved amendment / sub-section owns the labeler; Section 4 consumes it
  classifier_unavailable_behavior: "emit_partial_with_warning"  # closed enum ('emit_partial_with_warning', 'skip_with_warning', 'fail'); Builder Proposed default per A-PRP-04-13
  partial_dimensions_allowed: true  # SDR Decision 9 deferral rule for VIX
  regime_label_enum: ["risk_on_low_vol", "risk_on_high_vol", "risk_off_low_vol", "risk_off_high_vol", "risk_on", "risk_off"]  # full four-regime set plus the trend-only fallback labels per SDR Decision 9 partial-dimensions rule

attribution:
  set_version: "attribution_v1"
  signal_components: ["benchmark_relative_excess_return", "calibrated_outperformance_probability", "rank_within_sleeve_position"]  # Proposed default
  trade_components: ["entry_price_skill", "exit_price_skill", "holding_period_return", "cost_drag"]  # Proposed default
  total_attribution_residual_bound: 0.0001  # Proposed default; sum-of-components must approximate total within this bound

mlflow:
  backtest_experiment_enabled: false  # Open Question per §10; default to off until Approver-resolved
  required_tags: []  # populated only if backtest_experiment_enabled: true

reproducibility:
  random_seed: 4242  # Implementation default; deterministic fold construction
  refuse_invalidated_snapshot: true  # not configurable; structural

validation:
  reject_unknown_fold_geometry: true
  reject_unknown_action_value: true
  reject_unknown_metric_name: true
  reject_unknown_attribution_component: true
  reject_unknown_regime_label: true
  reject_unknown_window_label: true
```

**Validation rules** (closed-set discipline parallel to 03b §7.2 / 03c §7.2):

- `walk_forward.fold_geometry` must be one of `('rolling', 'expanding')`; unknown values are rejected at config-load time.
- `walk_forward.embargo_trading_days` must be a positive integer; default 126 per SDR Decision 7.
- `simulated_fills.action_enum` is a closed list; unknown values in `backtest.simulated_fills.action` are rejected at write time by the table CHECK constraint and at config-load time by `validation.reject_unknown_action_value`.
- `metrics.per_fold.enabled` and `metrics.aggregate.enabled` are closed lists Section 4 maintains; new metric names require a Section 4 amendment.
- `attribution.signal_components` and `attribution.trade_components` are closed lists; new components require a Section 4 amendment.
- `regime_reporting.partial_dimensions_allowed` controls the SDR Decision 9 VIX-deferral fallback; if `false`, Section 4 refuses to emit `backtest.regime_metrics` rows when the volatility dimension is unavailable.
- `mlflow.backtest_experiment_enabled` defaults `false` until Approver-resolved (§10). If `true`, `mlflow.required_tags` must be a closed list and Section 4 propagates them parallel to 03c §6.10.

### 7.2 Files Section 4 reads

Section 4 reads, but does not modify, the following config files:

- `config/features.yaml` (owned by 03a) — read for `feature_set_version` discipline at run-open time.
- `config/targets.yaml` (owned by 03b) — read for `target_set_version` discipline and the active horizon list (Phase 1 locked: `{63, 126}`).
- `config/model.yaml` (owned by 03c) — read for `model_set_version` discipline and the active `model_kind` enumeration. Section 4 does **not** read or modify any other 03c-owned key.
- `config/universe.yaml` (owned by 02) — read for sleeve assignments and ETF metadata; Section 4 does not modify.
- `config/costs.yaml` (Section-4-owned at the file level per Section 1) — read for the per-bucket basis-point values per the §6.7 consumption seam. SDR Decision 8 locks the four Phase 1 cost-bucket names (`ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`); Section 4 consumes the locked enumeration. Per-bucket basis-point values await Approver direction (Builder Proposed defaults in §11.4 if and when populated).
- `config/regime.yaml` (Sections 3 and 4 jointly per Section 1) — read for the regime-label closed enumeration. Computation thresholds are populated by whichever owner the Approver resolves under A-OQ-04-07 (Option A: Section 4; Option B: a future approved amendment / sub-section). **Until A-OQ-04-07 is resolved, Section 4 reads the file's enumeration only and does not write to it.**
- `.env` (not committed) — Section 4 directly reads only `MLFLOW_TRACKING_URI` (when `mlflow.backtest_experiment_enabled: true`). Application database access is configured by Section 2.

Section 4 does **not** read provider credentials (`backtest/`, `attribution/`, `regime/` (consumption) modules never import from `quant_research_platform.providers`; verified by §8 static check).

### 7.3 Commit discipline

Per EW §7, `config/backtest.yaml` is **strategy-affecting** at the spec level (fold geometry, embargo width, metric set, attribution component set, regime-classifier-unavailable behavior, cost-config-missing behavior, MLflow-experiment-enabled flag — all are strategy-affecting choices). Modifications follow EW §7 strategy-affecting commit discipline and require Approver review.

`config/costs.yaml` and `config/regime.yaml` are likewise strategy-affecting; their commit discipline is anchored to SDR Decision 8 and SDR Decision 9 cash-outs respectively, and Section 4 inherits the EW §7 process.

---

## 8. Required tests

The minimum test coverage Section 4 must produce. Specific parameter values within tests inherit from the §7.1 `config/backtest.yaml` Proposed defaults; an Approver-issued change to those defaults flows through to the corresponding test fixtures.

### 8.1 Walk-forward harness correctness (WF-*)

1. **WF-01: Fold construction respects signal-date bounds.** Given `signal_date_min` and `signal_date_max` on a fixture snapshot, every fold's `train_signal_date_min`, `train_signal_date_max`, `test_signal_date_min`, `test_signal_date_max` falls within the bounds.
2. **WF-02: Fold geometry — rolling test windows do not partition the full window.** Given `fold_geometry: 'rolling'`, `fold_count: N`, `fold_size_trading_days: K`, and `embargo_trading_days: E`, the harness produces exactly `N` folds whose **test windows** are non-overlapping and march forward at stride `K + E` trading days each, starting at `signal_date_min + initial_train_trading_days` and ending at `signal_date_min + initial_train_trading_days + N*(K+E) - E`. The test-window union covers `[earliest_test_signal_date, latest_test_signal_date]` only — **not** `[signal_date_min, signal_date_max]`. The pre-fold-1 portion `[signal_date_min, earliest_test_signal_date)` is the initial training period; any post-fold-N portion `(latest_test_signal_date, signal_date_max]` is unused by walk-forward evaluation under this geometry and is not silently consumed for any other purpose. The harness validates `latest_test_signal_date <= signal_date_max` at config-load time and raises `'fold_construction_failed'` otherwise. **`fold_count` and `fold_size_trading_days` are independent knobs**; the relationship between window length and the product `N*(K+E)` is bounded by the signal-date upper limit per `ops.data_snapshots.price_table_max_as_of_date - max(horizon_trading_days)` (per WF-04), not by an exact-partition requirement.
3. **WF-03: Fold geometry — expanding.** Given `fold_geometry: 'expanding'` and `expanding_initial_train_trading_days: K`, fold 0 has train window of size `K`, and fold `i+1`'s train window strictly contains fold `i`'s train window.
4. **WF-04: Snapshot upper bound respected.** No fold's `test_signal_date_max` exceeds `ops.data_snapshots.price_table_max_as_of_date - max(horizon_trading_days)`.
4a. **WF-05: All-folds-failed terminal case (v0.3 Revision 7).** A fixture in which every fold's 03c invocation returns a `'failed'` `models.model_runs` row produces this lifecycle: (a) `backtest.backtest_runs.status = 'failed'`; (b) `error_message` populated with the per-fold outcome count; (c) zero rows in `backtest.aggregate_metrics`; (d) zero rows in `backtest.regime_metrics`; (e) per-fold `backtest.backtest_run_issues` rows with `issue_type='failed_model_run_blocked'` plus exactly one summary row with `issue_type='all_folds_failed'`, `fold_id IS NULL`. A parallel fixture in which one fold succeeds and the rest fail produces `status='succeeded'` and aggregate metrics computed over the surviving fold (no `'all_folds_failed'` row). The boundary between partial-skip-OK and all-skip-fail is verified.

### 8.2 Purge / embargo enforcement (PE-*)

5. **PE-01: Purge consumes 03b-recorded forward-label windows on both sides.** Given a training row at `(T_train, h)` with recorded forward-label window `[entry_date(T_train, h), exit_date(T_train, h)]` and a test row at `(T_test, h)` with recorded forward-label window `[entry_date(T_test, h), exit_date(T_test, h)]`, the harness purges the **training row from the training set** if the two windows overlap. Both sides of the comparison read `entry_date` and `exit_date` directly off `targets.target_values`; the harness does not re-derive either side from horizon arithmetic. The test verifies (a) overlap detection on a fixture where windows overlap by at least one trading day and (b) the test-window row itself is **not** disqualified — purge / embargo excludes training candidates around test windows; it must never disqualify valid OOS test-window rows.
6. **PE-02: Embargo width is configurable; default 126.** Setting `embargo_trading_days: 126` produces the SDR-named behavior; setting any other positive integer produces the configured behavior.
7. **PE-03: Purge does not re-derive windows from horizon arithmetic.** A fixture is constructed in which `targets.target_values.exit_date` differs from `signal_date + 1 + horizon_trading_days` calendar days (e.g., due to weekend / holiday boundaries; per 03b §6.5). The harness reads the recorded `exit_date` and applies purge per the recorded value, not per calendar arithmetic.
8. **PE-04: Purge handles overlapping-label arithmetic per 03b §8.2 #40.** For two adjacent signal dates `T` and `T+1` with horizon `h`, the recorded `[entry_date(T), exit_date(T)]` and `[entry_date(T+1), exit_date(T+1)]` overlap by exactly `h - 1` trading days under Convention B; the harness's purge correctly removes both rows from the training set when either is in the test window.

### 8.3 OOS qualification (OOS-*)

9. **OOS-01: Section 4 supplies fold metadata to 03c via the §6.1 seam.** The harness invokes the 03c-owned model-run contract with a `fold_metadata` payload conforming to §6.1; 03c writes `models.model_predictions` rows tagged with `prediction_context='walk_forward_oos'` for the test-window rows.
10. **OOS-02: `prediction_context` filter on backtest performance evaluation.** The harness reads only rows with `prediction_context='walk_forward_oos'` for `backtest.simulated_fills` writes. A fixture with `'in_sample_diagnostic'` and `'current_scoring'` rows verifies they are excluded.
11. **OOS-03: Purge ranges remove training candidates, not OOS test rows.** A test-window row at `as_of_date` is tagged `'walk_forward_oos'` even when a `purge_signal_date_ranges` entry extends across, adjoins, or overlaps the test window. The fixture: construct a fold whose `purge_signal_date_ranges` overlaps the test window's leading edge by 30 trading days; the test-window rows in that overlapping range are still tagged `'walk_forward_oos'`. Separately, the **training set** for that fold has the corresponding training candidates purged — verified jointly with PE-01.

### 8.4 Leakage tests at fold boundaries (LK-*)

12. **LK-01: No training forward-label window overlaps any test forward-label window.** For every fold, the harness verifies (and the test asserts) that the set `{[entry_date(T_train, h), exit_date(T_train, h)] : T_train in training set, h in horizons}` is pairwise disjoint from the set `{[entry_date(T_test, h), exit_date(T_test, h)] : T_test in test set, h in horizons}`. Both windows are read off the recorded 03b per-row metadata; neither side is re-derived from horizon arithmetic. The earlier (weaker) "training forward window vs test signal date" formulation is **not** sufficient because two overlapping forward-label windows can cause label leakage even when neither covers the other's signal date.
13. **LK-02: No T-1 leakage at fold boundaries.** Inherits 03a's T-1 contract — no training row consumed feature values with `as_of_date >= T_train`. The test reads the fixture feature surface and asserts the contract on each fold.
14. **LK-03: No future-data leakage on attribution.** Attribution rows for `signal_date = T` use only data rows with `as_of_date <= T - 1` (via the feature side) and `entry_date / exit_date <= price_table_max_as_of_date` (via the target side). A fixture verifies the boundary.
15. **LK-04: Calibration-fold disjointness preserved through the seam.** The held-out fold supplied by Section 4 to 03c's calibration pipeline (per 03c §6.5) does not overlap the classifier-fit fold; verified end-to-end with 03c's CAL-02 test consuming Section 4's harness output.

### 8.5 Simulated fills correctness (SF-*)

16. **SF-01: Simulated fills only consume succeeded upstream runs.** Given a `'failed'` `models.model_runs` row, the harness writes zero `backtest.simulated_fills` rows from it and emits `'fail'` `backtest.backtest_run_issues` with `issue_type='failed_model_run_blocked'`.
17. **SF-02: Simulated fills only consume succeeded scoring runs.** Symmetric to SF-01 for `models.scoring_runs`.
18. **SF-03: Adjusted-close pricing is canonical.** Every `simulated_fill_price_pre_cost` value comes from `prices.etf_prices_daily.adjusted_close`; raw OHLCV is never used.
19. **SF-04: Convention B applied to entry / exit dates.** `simulated_entry_date = signal_date + 1` trading day on the relevant ETF's trading-day index; the test reads `targets.target_values.entry_date` for the same `(etf_id, signal_date)` and asserts equality.
20. **SF-05: DiversifierHedge zero-rows handled without failure.** A fixture in which one ETF is sleeve-mapped to `DiversifierHedge` produces no `models.combined_scores` rows for that ETF (per 03c A-PRP-29 Path X); the harness does not write `backtest.simulated_fills` rows for that ETF and does not raise. A `'warning'` `backtest.backtest_run_issues` row is *not* written for this case (the absence is documented and intended).
21. **SF-06: Cost application on entries and exits — long-only direction.** Given `cost_bps = X`, an entry simulated fill (`'enter_long'` or `'rebalance_in'`) has `simulated_fill_price_after_cost = simulated_fill_price_pre_cost * (1 + X / 10000)` (simulated buyer pays above mid); an exit simulated fill (`'exit_long'` or `'rebalance_out'`) has `simulated_fill_price_after_cost = simulated_fill_price_pre_cost * (1 - X / 10000)` (simulated seller receives below mid). The fixture asserts the directionally correct round-trip cost for long-only Phase 1 simulated fills per SDR Decision 8.

### 8.6 Schema / write-discipline static checks (CC-*)

22. **CC-01: Section 4 modules write to no `models.*` table.** Static check: search `backtest/`, `attribution/`, `regime/` (consumption) for any DB write call targeting `models.*`. None permitted. Any match fails the check.
23. **CC-02: Section 4 modules write to no `ops.*` table.** Same shape.
24. **CC-03: Section 4 modules write to no `features.*`, `targets.*`, `universe.*`, or `prices.*` table.** Same shape.
25. **CC-04: Section 4 modules import no provider modules.** Search for `quant_research_platform.providers` imports inside `backtest/`, `attribution/`, `regime/` (consumption). None permitted.
26. **CC-05: Section 4 modules import no broker SDK and declare none in dependency manifests.** Parallel to Section 1 invariant 2.
27. **CC-06: Section 4 reads `models.model_predictions` only with the `'walk_forward_oos'` filter for backtest performance evaluation.** Static or fixture-level check that every read path in `backtest/`'s metrics module applies the filter.
28. **CC-07: Section 4 reads `models.model_runs` and `models.scoring_runs` only with `status='succeeded'` filter on every join.** Inherits the 03c constraint #4 discipline.
29. **CC-08: No `secondary_benchmark_id` fallback in Section 4 modules.** Inherits the global no-silent-benchmark-substitution rule. A fixture with `primary_benchmark_id` resolved index-only and `secondary_benchmark_id` populated must not produce a different attribution decomposition than a fixture with the same `primary_benchmark_id` and no `secondary_benchmark_id`.
30. **CC-09: `backtest.simulated_fills` is not paper portfolio state.** Static check: no module under `paper/` reads from `backtest.simulated_fills` as authoritative state, and no module under `order_intent/` reads from it. (Cross-section check; runs after Section 5 implementation lands; this section reserves the test slot.)
31. **CC-10: `backtest.simulated_fills.action` enum disjoint from any future Section 5 portfolio-action enum.** Static check: the closed list `{'enter_long', 'exit_long', 'rebalance_in', 'rebalance_out'}` and any future Section 5 enum (BUY / HOLD / TRIM / SELL / REPLACE / WATCH per SDR Decision 10) share no element.

### 8.7 Reproducibility (REP-*)

32. **REP-01: `data_snapshot_id` chain consistency.** The `data_snapshot_id` reachable via `feature_run_id` and the one reachable via `target_run_id` and the denormalized one on `backtest.backtest_runs` must equal each other; mismatch raises `'fail'` `issue_type='snapshot_mismatch'`.
33. **REP-02: Invalidated-snapshot rejection (open-run-before-validation lifecycle).** Starting a backtest run with a `data_snapshot_id` referencing a snapshot whose `status='invalidated'` produces this lifecycle: (a) `backtest.backtest_runs` row opened with `status='running'`; (b) snapshot validation detects `'invalidated'`; (c) row updated to `'failed'`; (d) `'fail'` `issue_type='invalidated_snapshot_blocked'` written to `backtest.backtest_run_issues`; (e) **no** rows written to `backtest.simulated_fills`, `backtest.fold_metrics`, `backtest.aggregate_metrics`, or `backtest.regime_metrics`. Asserted; `ops.data_quality_exceptions` asserted unchanged.
34. **REP-03: Cross-run idempotency.** Same `data_snapshot_id`, same `feature_run_id`, same `target_run_id`, same `model_set_version`, same `commit_hash`, same `config_hash`, same `random_seed` across two `'succeeded'` backtest runs produces identical `backtest.simulated_fills`, identical `backtest.fold_metrics`, identical `backtest.aggregate_metrics`, identical `backtest.regime_metrics`, and identical `attribution.*` rows (modulo PK and `backtest_run_id`).
35. **REP-04: EW §7 reproducibility list satisfied.** Every `backtest.backtest_runs` row carries non-null `commit_hash`, `config_hash`, `data_snapshot_id`, and (transitively) the EW §7 fields from `ops.data_snapshots`.
36. **REP-05: Current-survivor disclosure label persisted on every backtest run.** Every `backtest.backtest_runs` row carries non-null `current_survivor_disclosure_label`. The value equals the string returned by `common.get_current_survivor_label()` (Section 2 retrieval function sourced from `config/universe.yaml` `disclosures.current_survivor_label`), modulo whitespace. The test injects a fixture `config/universe.yaml` with a known disclosure string, runs the harness, and asserts the value is present verbatim on the resulting `backtest.backtest_runs` row. A `NULL` insertion attempt is rejected by the schema's NOT NULL constraint. Per SDR Decision 4 / Decision 16 bias-control labeling, this attaches the directional-learning-not-statistical-proof disclosure to every backtest output for downstream UI surfacing per Section 6.
36a. **REP-06: Pipeline-validation-only flag set under cost-config zero-fallback.** A backtest run executed with `cost_config_missing_behavior: 'warn_proceed_zero_cost'` and an absent or empty `config/costs.yaml` produces a `backtest.backtest_runs` row with `is_pipeline_validation_only = true` and `pipeline_validation_only_reason = 'cost_config_zero_fallback'`. A backtest run with cost values populated produces `is_pipeline_validation_only = false` and `pipeline_validation_only_reason IS NULL`. A run with `is_pipeline_validation_only = true` and `pipeline_validation_only_reason IS NULL` is rejected by the CHECK constraint. A run with `is_pipeline_validation_only = false` and a non-null reason is also rejected. Per v0.3 Revision 5 / A-PRP-04-35 / A-PRP-04-36.
36b. **REP-07: `is_pipeline_validation_only = true` runs are not consumable as promotion evidence (cross-section).** Static check across Section 5 modules (when they land) asserts no Section 5 promotion-gate query reads `backtest.aggregate_metrics` without applying the `is_pipeline_validation_only = false` filter on the corresponding `backtest.backtest_runs` row. Section 4 v0.3 reserves the test slot; the assertion runs after Section 5 implementation begins.

### 8.8 Regime reporting (RG-*)

36. **RG-01: `backtest.regime_metrics` rows written only when classifier outputs are available.** Given a fixture without regime-classifier outputs, the test asserts no `backtest.regime_metrics` rows are written and a `'warning'` `issue_type='regime_classifier_unavailable'` is logged (or, if `regime_reporting.classifier_unavailable_behavior: 'fail'` is configured, the run fails — runtime choice per A-PRP-04-13).
37. **RG-02: SDR Decision 9 partial-dimension fallback.** With trend dimension available and volatility dimension absent, given `partial_dimensions_allowed: true`, only `risk_on` / `risk_off` regime labels are emitted; given `false`, no regime rows are emitted and a warning is logged.

### 8.9 Attribution correctness (AT-*)

38. **AT-01: Attribution components sum to total within `total_attribution_residual_bound`.** For every `attribution.signal_attribution` and `attribution.trade_attribution` row, `abs(sum(attribution_components.values()) - total_attribution) <= total_attribution_residual_bound`.
39. **AT-02: Attribution rows match the simulated fills they decompose.** For every `attribution.trade_attribution` row, the composite FK `(backtest_run_id, fold_id, etf_id, signal_date, horizon_trading_days, action)` resolves to exactly one `backtest.simulated_fills` row.
40. **AT-03: Attribution closed-set component enumeration.** Unknown component names in `attribution_components` JSONB raise at write time per `validation.reject_unknown_attribution_component`.
40a. **AT-04: Attribution-run open-run-before-validation rejects non-`'succeeded'` backtest runs (v0.4 Revision 2; lifecycle refined in v1.0 Correction 3).** A fixture in which the referenced `backtest.backtest_runs.status = 'failed'` (e.g., the all-folds-failed terminal case from §9 #4a) produces this lifecycle when the `attribution/` decomposer is invoked: (a) the decomposer **opens** an `attribution.attribution_runs` row with `status='running'`, populated `backtest_run_id`, `attribution_set_version`, `commit_hash`, `config_hash`, `started_at_utc`, and `created_by`; (b) the decomposer reads the referenced backtest run's `status`; (c) on `status != 'succeeded'`, the attribution run's `status` is updated to `'failed'`, `completed_at_utc` is set, and `error_message` is populated; (d) a single `'fail'` `attribution.attribution_run_issues` row is written with the (now-valid) `attribution_run_id`, `issue_type='backtest_run_not_succeeded'`, and `detail` summarizing the referenced backtest run's status; (e) zero rows are written to `attribution.signal_attribution` and `attribution.trade_attribution` for that attribution run. A parallel fixture with `status = 'succeeded'` allows the attribution run to proceed normally to `status='succeeded'` with non-zero `signal_attribution` and `trade_attribution` rows. The test verifies that the FK on `attribution_runs.backtest_run_id` validates row existence only — it does not enforce status — by attempting a direct DB insertion that bypasses the application-side check: the FK accepts the insertion (the parent row exists), confirming that status discipline is enforced application-side and the §9 #4a (f) open-run-before-validation lifecycle is the canonical mechanism.

### 8.10 `config/backtest.yaml` validation (CFG-*)

41. **CFG-01: Closed-set validation.** Every closed-set field (fold geometry, action enum, cost-bucket enum, metric names, attribution components, regime labels, window labels) raises on unknown values at config load.
42. **CFG-02: `embargo_trading_days` positive.** Negative or zero values raise at config-load time. (Wording corrected in v0.3 R8: "non-negative" was incorrect since zero is rejected.)
43. **CFG-03: `mlflow.backtest_experiment_enabled: true` requires non-empty `mlflow.required_tags`.** Validator enforces; raises otherwise.
44. **CFG-04: `cost_application.cost_bucket_enum` matches the SDR Decision 8 locked enumeration.** The four-value set `('ultra_liquid_etf', 'liquid_sector_etf', 'thematic_niche_etf', 'commodity_specialty_etf')` is hard-coded as the expected closed enum; any deviation in `config/backtest.yaml` raises at config-load time. This is structural, not configurable.

### 8.11 Test data discipline

- Fixtures live under `tests/fixtures/backtest/` and `tests/fixtures/attribution/`. Synthetic price / feature / target / model-prediction / combined-score fixtures for known-input / known-output tests are checked into the repo per EW §5.
- No Section 4 test depends on a live API call.
- Integration tests (`tests/integration/backtest/`, `tests/integration/attribution/`) exercise the harness end-to-end on a small fixture universe with fixture `ops.data_snapshots`, fixture `features.feature_runs` / `targets.target_runs` / `models.model_runs` / `models.scoring_runs`, producing fixture-comparable `backtest.*` and `attribution.*` content.

### 8.12 Financial-meaning metric tests (FM-*)

These tests verify the **financial meaning** of each §6.10 metric on synthetic fixtures with hand-computed expected values, not just that rows exist. Each test injects a synthetic post-cost price / fill series and asserts the recorded `metric_value` against an externally-computed expected value within a small numerical tolerance (Builder Proposed default `1e-9`).

45. **FM-01: `total_return` known-input / known-output.** A synthetic fixture with `V_start = 100`, `V_end = 110` produces `total_return = 0.10` to within tolerance.
46. **FM-02: `cagr` annualization correctness.** A synthetic fixture spanning exactly `252` trading days with `total_return = 0.10` produces `cagr ≈ 0.10` to within tolerance; spanning `504` trading days with `total_return = 0.21` produces `cagr ≈ 0.10`.
47. **FM-03: `volatility` annualization correctness.** A synthetic daily-return series with constant daily standard deviation `s_d = 0.01` produces `volatility ≈ 0.01 * sqrt(252) ≈ 0.1587` to within tolerance.
48. **FM-04: `max_drawdown` peak-to-trough correctness.** A synthetic value series `[100, 110, 99, 121, 90]` produces `max_drawdown ≈ -0.2562` (the 121→90 trough), to within tolerance.
49. **FM-05: `risk_adjusted_return` sign and scale.** A synthetic fixture with `cagr = 0.10`, `volatility = 0.20`, `risk_free_rate_annual = 0.0` produces `risk_adjusted_return = 0.5` to within tolerance. A fixture with `volatility = 0` produces `risk_adjusted_return IS NULL` (row written, value null).
50. **FM-06: `hit_rate` correctness.** A synthetic fixture with 4 closing rows whose round-trip simulated post-cost returns are `[+0.05, -0.02, +0.01, -0.03]` produces `hit_rate = 0.5`.
51. **FM-07: `turnover` correctness.** A synthetic fixture with 3 rebalance events and weight-change sums `[1.0, 0.4, 0.6]` produces `turnover = (1.0 + 0.4 + 0.6) / 3 ≈ 0.6667`.
52. **FM-08: `cost_drag` correctness.** A synthetic fixture with `total_return_pre_cost = 0.10` and `total_return_post_cost = 0.085` produces `cost_drag = 0.015` to within tolerance.
53. **FM-09: `benchmark_relative_return` correctness.** A synthetic fixture with portfolio `total_return = 0.10` and per-ETF benchmark series producing portfolio-level benchmark `total_return = 0.07` produces `benchmark_relative_return = 0.03` to within tolerance. **A parallel fixture in which `secondary_benchmark_id` is populated and `primary_benchmark_id` resolves index-only must produce `NULL` propagation, not silent substitution; verified jointly with CC-08.**
54. **FM-10: `sleeve_level_performance` correctness with sleeve_id dimension.** A synthetic fixture with two sleeves (`sector`, `bond`) producing per-sleeve `total_return` `[0.12, 0.04]` records both values in `backtest.fold_metrics` / `backtest.aggregate_metrics` as two rows: `(metric_name='sleeve_level_performance', sleeve_id=<sector_id>, metric_value=0.12)` and `(metric_name='sleeve_level_performance', sleeve_id=<bond_id>, metric_value=0.04)`. **`metric_name` is `'sleeve_level_performance'` for both rows; the sleeve is disambiguated by the `sleeve_id` column, not by an encoded suffix on `metric_name`** (per v0.3 Revision 3). The test verifies both rows are written and that `metric_name` carries no sleeve suffix.
55. **FM-11: `regime_conditioned_performance` correctness.** A synthetic fixture with regime labels covering 60% of trading days as `risk_on_low_vol` and 40% as `risk_off_high_vol` produces per-regime `total_return` values matching the within-regime sub-period returns to within tolerance; verifies that the regime conditioning subsets the trading-day index correctly.
56. **FM-12: `fold_consistency` correctness.** A synthetic 4-fold fixture with per-fold `total_return = [0.10, 0.10, 0.10, 0.10]` produces `fold_consistency = 1.0` (zero variation); a fixture with `[0.10, -0.10, 0.10, -0.10]` produces `fold_consistency` close to `0.0` or strictly less than `1.0` per the §6.10 formula.
57. **FM-13: Null-vs-no-row distinction.** A metric configured but undefined for a period (e.g., `volatility` with fewer than 21 daily-return points) produces a `backtest.fold_metrics` row with `metric_value IS NULL`; a metric **not** configured produces no row at all. The test asserts both behaviors on the same fixture.
58. **FM-14: Annualization factor configurability.** Setting `metrics.trading_days_per_year: 252` produces the §6.10 default annualization; setting `260` (calendar-day-style) produces a different `cagr` and `volatility` per the formula; setting `0` raises at config-load time.
58a. **FM-15: Horizon-dimensioned metrics correctness.** A synthetic fixture with simulated fills at both 63d and 126d horizons producing per-horizon `total_return = [0.08, 0.12]` records two rows in `backtest.fold_metrics`: `(metric_name='total_return', horizon_trading_days=63, sleeve_id=NULL, metric_value=0.08)` and `(metric_name='total_return', horizon_trading_days=126, sleeve_id=NULL, metric_value=0.12)`. A horizon-agnostic metric (e.g., aggregated `turnover`) writes a single row with `horizon_trading_days IS NULL`. The test verifies both behaviors. (Logical-uniqueness NULL-handling under the surrogate-PK + `UNIQUE NULLS NOT DISTINCT` design per A-IMP-06 is verified separately under §8.14 UNI-* — see UNI-01.)
58b. **FM-16: `metric_name` purity.** No `metric_name` value contains a sleeve identifier suffix, a horizon suffix, or any other encoded dimension. The test scans every row written to `backtest.fold_metrics`, `backtest.aggregate_metrics`, and `backtest.regime_metrics` and asserts `metric_name` is one of the closed-enum values from `config/backtest.yaml` `metrics.per_fold.enabled` / `metrics.aggregate.enabled` exactly — no suffixes, no colons, no string composition. (Defensive against accidental regression to the retired A-PRP-04-28 pattern.)

### 8.13 Backtest-only simulated allocation contract (ALC-*)

These tests verify the §6.4.1 backtest-only simulated allocation contract and verify that the contract does **not** leak into Section 5 portfolio-rule territory.

59. **ALC-01: Top-N selection per `(sleeve_id, horizon_trading_days)` cross-section.** Given `top_n_per_sleeve_per_horizon: 5` and a fixture in which sleeve `S` has 8 ETFs with `combined_score` rows at signal date `T`, the harness selects exactly the 5 highest `combined_score` rows (lowest `rank_within_sleeve`) and writes 5 `'enter_long'` rows in `backtest.simulated_fills` for that `(sleeve_id, horizon_trading_days, signal_date)` triple. ETFs ranked 6–8 produce no fills.
60. **ALC-02: Explicit equal-weight assertion.** Every selected ETF in a `(sleeve_id, horizon_trading_days)` cross-section is written with `simulated_weight_after = 1 / N_per_sleeve_per_horizon` on its `'enter_long'` or `'rebalance_in'` row. The test reads `simulated_weight_after` directly from `backtest.simulated_fills` (not reconstructed from row count) and asserts the equality across all selected fills.
60a. **ALC-02b: Weight-delta consistency.** For every `backtest.simulated_fills` row, `simulated_weight_delta = simulated_weight_after - simulated_weight_before` exactly (CHECK constraint enforces; the test asserts the constraint is active by attempting to insert an inconsistent row, which is rejected at the database level).
61. **ALC-03: Rebalance cadence — monthly.** With `rebalance_cadence: 'monthly'` over a one-year fixture, the harness produces simulated fills only on the first valid trading day of each month; mid-month dates produce no fills even when combined-score rows exist.
62. **ALC-04: Position-exit on rank fall.** A fixture in which ETF `E` is in the top 5 at rebalance `R_i` and rank 7 at rebalance `R_{i+1}` produces a `'rebalance_out'` row at `R_{i+1}` for `E`. The exit is at `R_{i+1}` — **not** intra-rebalance.
63. **ALC-05: Position-exit on combined-score row absence.** A fixture in which ETF `E` has a combined-score row at `R_i` and no row at `R_{i+1}` produces a `'rebalance_out'` row at `R_{i+1}` for `E` with `combined_score IS NULL` and `rank_within_sleeve IS NULL`.
64. **ALC-06: DiversifierHedge sleeves produce no fills.** A fixture with one ETF sleeve-mapped to `DiversifierHedge` (no `models.combined_scores` rows per 03c A-PRP-29 Path X) produces zero `backtest.simulated_fills` rows for that ETF and zero `backtest.backtest_run_issues` rows of any severity for it (the absence is the documented contract).
65. **ALC-07: Long-only enforcement.** No `backtest.simulated_fills.action` value outside `('enter_long', 'exit_long', 'rebalance_in', 'rebalance_out')` is ever written; the schema CHECK constraint and the `simulated_allocation.long_only: true` validator both reject any short-side action at write time and at config-load time respectively.
66. **ALC-08: No write to `paper.*` / `order_intent.*` / `models.model_versions` (cross-section static check).** Static check across the full Section 4 module set asserts no DB write call targeting any `paper.*` table, any `order_intent.*` table, or any `models.model_versions` row. (When Section 5 implementation lands, the check extends to also assert no Section 5 module reads from `backtest.simulated_fills` as authoritative state — see CC-09.)
67. **ALC-09: Rebalance cadence is independent of Section 5 review cadence.** The test reads `simulated_allocation.rebalance_cadence` from a fixture `config/backtest.yaml` and a separate review-cadence value from a fixture `config/portfolio.yaml`; the harness consumes only the former and ignores the latter. (Defensive against accidental coupling; runs after Section 5 lock.)

### 8.14 Logical uniqueness on metric tables (UNI-*)

These tests exercise the surrogate-PK + `UNIQUE NULLS NOT DISTINCT` design on `backtest.fold_metrics`, `backtest.aggregate_metrics`, and `backtest.regime_metrics` per v0.4 Revision 1 / A-PRP-04-37 / A-IMP-06. They run against the actual database (or a Postgres 15+ test container, with a parallel Postgres-<15 test container running the COALESCE-based fallback). The test asserts both deployment paths.

68. **UNI-01: Logical uniqueness on `backtest.fold_metrics` across NULL and non-NULL dimension combinations.** The test inserts a sequence of rows into `backtest.fold_metrics` and asserts each insertion outcome:
    1. **All-NULL dimensions, duplicate logical row rejected.** Insert two rows with `(backtest_run_id, fold_id, horizon_trading_days=NULL, sleeve_id=NULL, metric_name='turnover')`. The second insertion is rejected by `UNIQUE NULLS NOT DISTINCT` (or by the COALESCE-based UNIQUE index on Postgres < 15). The surrogate `fold_metric_id` differs between attempts but does not save the second insertion.
    2. **One non-NULL dimension, duplicate logical row rejected.** Insert two rows with `(backtest_run_id, fold_id, horizon_trading_days=63, sleeve_id=NULL, metric_name='total_return')`. The second insertion is rejected.
    3. **Both non-NULL dimensions, duplicate logical row rejected.** Insert two rows with `(backtest_run_id, fold_id, horizon_trading_days=63, sleeve_id=<sector_id>, metric_name='sleeve_level_performance')`. The second insertion is rejected.
    4. **Distinct horizons allowed.** Insert `(backtest_run_id, fold_id, horizon_trading_days=63, sleeve_id=NULL, metric_name='total_return')` and `(backtest_run_id, fold_id, horizon_trading_days=126, sleeve_id=NULL, metric_name='total_return')`. Both succeed.
    5. **Distinct sleeves allowed.** Insert `(backtest_run_id, fold_id, horizon_trading_days=NULL, sleeve_id=<sector_id>, metric_name='sleeve_level_performance')` and `(backtest_run_id, fold_id, horizon_trading_days=NULL, sleeve_id=<bond_id>, metric_name='sleeve_level_performance')`. Both succeed.
    6. **Distinct metric_name allowed at same dimension tuple.** Insert `(backtest_run_id, fold_id, horizon_trading_days=63, sleeve_id=NULL, metric_name='total_return')` and `(backtest_run_id, fold_id, horizon_trading_days=63, sleeve_id=NULL, metric_name='cagr')`. Both succeed.
    7. **`metric_name` purity holds inline.** Every `metric_name` value inserted across cases (1)–(6) is one of the closed-enum values from `config/backtest.yaml` `metrics.per_fold.enabled`. No suffix, colon, or composed string is permitted (cross-asserted with FM-16 for defensiveness against the retired A-PRP-04-28 pattern).
69. **UNI-02: Logical uniqueness on `backtest.aggregate_metrics`.** Repeats UNI-01 cases (1)–(6) against `backtest.aggregate_metrics` over the tuple `(backtest_run_id, horizon_trading_days, sleeve_id, metric_name)`. `fold_id` is omitted from the logical key on this table.
70. **UNI-03: Logical uniqueness on `backtest.regime_metrics`.** Repeats UNI-01 cases (1)–(6) against `backtest.regime_metrics` over the tuple `(backtest_run_id, regime_label, horizon_trading_days, sleeve_id, metric_name)`. `regime_label` is non-nullable; the test additionally asserts that two rows with the same `(backtest_run_id, regime_label, horizon_trading_days, sleeve_id, metric_name)` tuple but distinct `regime_label` values are accepted.

---

## 9. Edge cases and failure behavior

1. **Invalidated `ops.data_snapshots`.** Per the §6.5 / §8.7 lifecycle: orchestrator opens the `backtest.backtest_runs` row first, then validates the snapshot. Detecting `status='invalidated'` causes the run row to be marked `'failed'` and a `'fail'` row written to `backtest.backtest_run_issues` with `issue_type='invalidated_snapshot_blocked'`. **No `backtest.simulated_fills` / `backtest.fold_metrics` / `backtest.aggregate_metrics` / `backtest.regime_metrics` rows are written.**
2. **Failed upstream feature run.** A `'failed'` `features.feature_runs` row referenced in `config/backtest.yaml`'s harness invocation produces `'fail'` `issue_type='failed_feature_run_blocked'`; **no** `backtest.simulated_fills` rows are written.
3. **Failed upstream target run.** Symmetric to #2 for `targets.target_runs`.
4. **Failed model run encountered during fold execution.** Even after the harness opens its run row, an individual fold's 03c invocation may produce a `'failed'` `models.model_runs` row. Section 4 records `'fail'` `issue_type='failed_model_run_blocked'` with `fold_id` populated, and skips the affected fold and continues per the Builder Proposed default A-PRP-04-15 (alternative: fail the entire backtest run — Approver-resolvable).
4a. **All folds skipped or failed (terminal case, v0.3 Revision 7; lifecycle refined in v1.0 Correction 3).** When **every** fold in a backtest run is skipped or failed (per the per-fold containment rules in #4 and in §9 #11 / #13), the backtest run as a whole is marked `'failed'`: (a) `backtest.backtest_runs.status` set to `'failed'`; (b) `error_message` populated with the count of skipped vs. failed folds; (c) `completed_at_utc` set; (d) **no rows are written to `backtest.aggregate_metrics` or `backtest.regime_metrics`** (per-fold rows that were written before the terminal condition are retained for audit but are not aggregated); (e) a single `'fail'` `backtest.backtest_run_issues` row is written with `issue_type='all_folds_failed'`, `fold_id IS NULL`, and `detail` summarizing the per-fold outcomes; (f) **attribution-run creation against this backtest run uses the open-run-before-validation lifecycle** (parallel to REP-02's invalidated-snapshot rejection): the `attribution/` decomposer (i) opens an `attribution.attribution_runs` row with `status='running'`; (ii) validates `backtest.backtest_runs.status = 'succeeded'` for the referenced `backtest_run_id`; (iii) on `status != 'succeeded'`, updates the attribution run's `status` to `'failed'`, sets `completed_at_utc`, and populates `error_message`; (iv) writes a single `'fail'` `attribution.attribution_run_issues` row with `attribution_run_id` set, `issue_type='backtest_run_not_succeeded'`, and `detail` summarizing the referenced backtest run's status; (v) writes zero rows to `attribution.signal_attribution`; (vi) writes zero rows to `attribution.trade_attribution`. The FK on `attribution_runs.backtest_run_id` validates row existence only; status discipline is enforced application-side. The harness contract: **a partially-skipped run is `'succeeded'`; an entirely-skipped run is `'failed'`.**
5. **Failed scoring run encountered during fold execution.** Same as #4 for `models.scoring_runs`.
6. **Cost config unavailable.** Per §6.7: proceed-with-zero-cost-and-warning per the Builder Proposed default A-PRP-04-14 (alternative: fail; runtime choice configurable in `config/backtest.yaml`).
7. **Regime classifier unavailable.** Per §6.5 and §7.1 `regime_reporting.classifier_unavailable_behavior`: `emit_partial_with_warning` per the Builder Proposed default A-PRP-04-13. Alternatives `'skip_with_warning'` and `'fail'` are configurable in `config/backtest.yaml`.
8. **DiversifierHedge ETFs.** Per 03c A-PRP-29 Path X, no `models.combined_scores` rows are emitted for `DiversifierHedge` ETFs under the current first-testable formula. Section 4 produces no `backtest.simulated_fills` rows for these ETFs. **This is the documented contract; no warning issue is written.** The `backtest.aggregate_metrics` and `backtest.regime_metrics` are computed over the rows that exist, exclusive of `DiversifierHedge` ETFs.
9. **Index-only benchmarks.** Inherited from 03b §6.5 / §11.6 #6: target rows for ETFs whose `primary_benchmark_id` is index-only are written with `target_value = NULL` (Bucket 2), the model layer propagates NULL through `predicted_value`, and `models.combined_scores` may have null components for those ETFs. Section 4's simulated fills for such ETFs are written with `combined_score = NULL` and `rank_within_sleeve = NULL` only if the rebalance schedule selects them — under the rank-driven simulated-fill rule, ETFs with `combined_score IS NULL` typically do not enter the simulated fill set. **No silent benchmark substitution. No fallback to `secondary_benchmark_id`.**
10. **Snapshot front-edge truncation.** Per 03b §6.5 Bucket 1 and 03b §6.9 coverage parity: target rows for `(etf, T)` whose `exit_date(T, h) > price_table_max_as_of_date` do not exist. Section 4 inherits this absence: the harness's signal-date upper bound is `price_table_max_as_of_date - max(horizon_trading_days)` (with trading-day adjustment); fold construction respects this bound. Models trained per fold use only rows present in `targets.target_values`.
11. **Calibration failure at the model layer.** Per 03c §6.5: a calibrator fit failure produces `'fail'` `issue_type='calibration_failed'` on the calibrated model run; the parent uncalibrated classifier run remains `'succeeded'`. Section 4 reads only `'succeeded'` runs and so the calibrated `model_kind` for that fold is unavailable. Per the Builder Proposed default A-PRP-04-17, Section 4 skips the affected fold and continues. Falling back to the uncalibrated `model_kind` is **explicitly forbidden** at the model layer per 03c §6.5 ("the uncalibrated classifier outputs are not used as a substitute"); the only Approver-available alternative to skip-the-fold is failing the entire run.
12. **Fold boundary at year-end / market close.** When a fold boundary falls on a market holiday or year-end, the harness uses the next valid trading day per the relevant ETF's trading-day index; tested under PE-03.
13. **Empty test window.** A configuration in which a fold has zero eligible signal dates in its test window produces `'warning'` `issue_type='fold_construction_failed'` with `fold_id` populated per the Builder Proposed default A-PRP-04-16; the fold's metric rows are not written; the backtest run continues with the remaining folds. Alternative: `'fail'` (Approver-resolvable).
14. **MLflow unreachable (when enabled).** When `mlflow.backtest_experiment_enabled: true` and the tracking server is unreachable, the run fails with `'fail'` `issue_type='mlflow_unreachable'` parallel to 03c §6.3.
15. **Concurrent backtest runs against the same snapshot.** Idempotency holds per REP-03; concurrent runs produce identical row content and only differ in `backtest_run_id`. The schema does not prevent parallel runs.
16. **Adjacent-fold metadata overlap.** When fold `i`'s test window is `[A, B]` and fold `i+1`'s test window is `[B+1, C]`, the embargo of width 126 trading days produces a non-empty `embargo_signal_date_min(i+1) > B` strictly. The harness asserts the strict inequality at fold-construction time.

---

## 10. Open questions

These are unresolved Approver decisions. Some include a Builder recommendation (e.g., A-OQ-04-07 carries a Builder recommendation for Option A), but none are locked until the Approver accepts them. Items where the Builder has both a recommended Proposed default *and* a clean strategy reading are listed under §11.4 instead; items here either lack a recommendation entirely or surface a structural choice the Approver must affirmatively make.

- **A-OQ-04-07: Regime classifier (labeler) ownership.** SDR Decision 9 names the regime taxonomy but does not say which spec section owns the classifier that emits per-`(as_of_date)` regime labels. Two options:
  - **Option A — Section 4 owns a minimal SDR Decision 9 regime labeler** in `regime/`, computing SPY-above-200d-SMA (trend dimension) and VIX rolling-percentile (volatility dimension, with the SDR-named deferred-fallback rule) per signal date. Current Section 4 scope reads this as the Builder's recommendation because it (i) avoids a dependency on an unauthorized future sub-section, (ii) keeps Phase 1 simple per SDR Decision 9's "simple regime-reporting layer, not a complex macro regime model" framing, and (iii) allows Section 4 lock without external precondition.
  - **Option B — A future approved amendment / sub-section owns the labeler**, and Section 4 consumes its output. This requires authorizing a separate spec deliverable before Section 4 can be exercised end-to-end against real regime labels; the §6.5 `backtest.regime_metrics` table and §7.1 `regime_reporting` block still apply.

  Approver chooses. The choice does not change `backtest.regime_metrics` schema or `config/regime.yaml` consumption seam — only the location of the labeler module.

- **A-OQ-04-14: Active → Warning automated trigger** (carried forward from 03c §10.9 / A-OQ-01). Section 4 *may* propose a mechanical trigger expressed as a threshold over `backtest.aggregate_metrics` (e.g., a drop in `risk_adjusted_return` below a configured floor flips a registered model version `Active → Warning`). **Builder does not propose a trigger in current Section 4 scope** because (i) the SDR explicitly leaves the trigger Approver-directed, (ii) any mechanical trigger requires a 03c amendment to integrate with the `models.model_versions.state` lifecycle, and (iii) Section 5 owns the kill-switch enforcement layer that would consume any such trigger. Approver directs whether to draft.

- **A-OQ-04-18: Backtest confidence-level outputs sufficiency.** SDR Decision 7 requires Phase 1 to support directional results and to address overlapping-label, look-ahead, selection / data-snooping, current-survivor, backfill / proxy, market-impact, and time-zone biases. The §6.9 validation evidence surface and §6.10 metric definitions enumerate what Section 4 produces. **Whether the surface as proposed is sufficient or needs additional fields** (e.g., explicit per-bias disclosure rows; an explicit "selection-bias score" derived from the count of leakage tests passed; a synthesized "directional-confidence label" combining `risk_adjusted_return`, `fold_consistency`, and bias-test pass-rate) is an Open Question. Builder does not propose additional fields in current Section 4 scope; Approver may direct.

---

## 11. Explicit assumptions

All assumptions are classified per EW §3.3.

### 11.1 Derived from SDR

- **A-DRV-01:** Walk-forward validation is the Phase 1 validation framework. Derived from SDR Decision 7 (named).
- **A-DRV-02:** Phase 1 uses a 126-trading-day purge / embargo width as the SDR-named value. Derived from SDR Decision 7. Adoption confirmed at the structural level; the *width* is also surfaced as A-PRP-04-04 because SDR Decision 7 leaves room for refinement.
- **A-DRV-03:** Phase 1 backtest support windows are `2010–2025` (primary), `2005–2025` (longer robustness), `2020–2025` (recent regime), and monthly rebalance testing. Derived from SDR Decision 7 (named).
- **A-DRV-04:** Probability outputs must be calibrated before hard thresholds are interpretable. Derived from SDR Decision 7. Section 4 enforces the consumption-side discipline by reading calibrated `model_kind` predictions for backtest evaluation (per 03c §6.5 Section 4 dependency note).
- **A-DRV-05:** Bias controls cover look-ahead, overlapping-label, selection / data-snooping, current-survivor universe, backfill / proxy-history, market-impact / liquidity, and time-zone / synchronization. Derived from SDR Decision 7 / Decision 16 (enumerated). Section 4 contributes the model-/backtest-layer half.
- **A-DRV-06:** Phase 1 simulates trades; no live execution. Derived from SDR Decision 1 / Decision 8.
- **A-DRV-07:** Transaction costs are applied per simulated fill against the SDR-locked four-value cost-bucket enumeration (`ultra_liquid_etf`, `liquid_sector_etf`, `thematic_niche_etf`, `commodity_specialty_etf`). Derived from SDR Decision 8 (named). Per-bucket basis-point values await Approver direction (§11.4 / §10).
- **A-DRV-08:** Phase 1 includes a regime-reporting layer with up to four regimes. Derived from SDR Decision 9 (named).
- **A-DRV-09:** When VIX data is unavailable, the volatility regime dimension is deferred. Derived from SDR Decision 9 (named).
- **A-DRV-10:** Attribution exists for trades / signals (SDR Decision 16 success criterion #20). Derived from SDR Decision 11 (attribution storage half) and SDR Decision 16.
- **A-DRV-11:** The `data_snapshot_id` chain anchors backtest reproducibility. Derived from SDR Decision 11 / Decision 16 / Section 1 invariant 7.
- **A-DRV-12:** No Section 4 module reads or writes broker-facing state. Derived from SDR Decision 1 / Decision 15 / Section 1 invariant 2.

### 11.2 Inherited from prior locked sections (A-INH-*)

- **A-INH-01:** Provider abstraction boundary. Inherited from Section 1 invariant 1; no Section 4 module imports from `providers/` or any provider-specific library.
- **A-INH-02:** No live broker code paths. Inherited from Section 1 invariant 2 / SDR Decisions 1, 15, 18.
- **A-INH-03:** Postgres-as-system-of-record. Inherited from Section 1 invariant 4 / SDR Decision 11; MLflow is tracking, not system of record.
- **A-INH-04:** All paths via `pathlib.Path`. Inherited from Section 1 invariant 5.
- **A-INH-05:** No secrets in code, config, fixtures, logs, or docs. Inherited from Section 1 invariant 6.
- **A-INH-06:** Time-aware research auditability. Inherited from Section 1 invariant 7.
- **A-INH-07:** UI is read-only, both at the import boundary and the database-access path. Inherited from Section 1 invariant 3 / SDR Decision 17.
- **A-INH-08:** `ops.data_quality_exceptions` is ingestion-owned. Inherited from Section 2 v1.0 LOCKED constraint #1; Section 4 does not write to this table.
- **A-INH-09:** Effective-date and EXCLUDE-constraint semantics on the three Section 2 effective-dated tables stand. Inherited from Section 2 v1.0 LOCKED.
- **A-INH-10:** `ops.data_snapshots` is read-only for Section 4. Inherited from Section 2 v1.0 LOCKED.
- **A-INH-11:** T-1 trading-day alignment on every feature row is structural and not redefined. Inherited from Section 3a v1.0 LOCKED.
- **A-INH-12:** Eligibility-row omission contract on `features.feature_values` stands. Inherited from Section 3a constraint #1.
- **A-INH-13:** Failed-run consumption discipline: only `features.feature_runs.status='succeeded'` is consumable. Inherited from Section 3a constraint #4. Section 4 applies this filter on every join.
- **A-INH-14:** Forward Convention B alignment on every target row (entry `T+1` close, exit `T+1+h` close) is structural and not redefined. Inherited from Section 3b v1.0 LOCKED.
- **A-INH-15:** Per-row window metadata (`signal_date`, `horizon_trading_days`, `entry_date`, `exit_date`) on every `targets.target_values` row is the canonical source for purge / embargo. Section 4 does NOT re-derive windows. Inherited from Section 3b v1.0 LOCKED.
- **A-INH-16:** The §6.5 null-vs-no-row taxonomy on `targets.target_values` is canonical. Bucket 1 (no row) and Bucket 2 (`target_value = NULL` row) are not reframed by Section 4. Inherited from Section 3b v1.0 LOCKED.
- **A-INH-17:** Failed-run consumption discipline: only `targets.target_runs.status='succeeded'` is consumable. Inherited from Section 3b v1.0 LOCKED.
- **A-INH-18:** Classification threshold `θ = 0.0` is locked. Section 4 does not redefine. Inherited from Section 3b v1.0 LOCKED.
- **A-INH-19:** No fallback to `secondary_benchmark_id` is permitted at any layer Section 4 touches. Inherited globally.
- **A-INH-20:** 03c is the writer for `models.*`. Section 4 does not write directly. Inherited from Section 3c constraint #2.
- **A-INH-21:** The closed three-value run-status enum `('running', 'succeeded', 'failed')` on `models.model_runs` and `models.scoring_runs` is consumed by Section 4 with the `'succeeded'` filter on every join. Inherited from Section 3c constraint #4.
- **A-INH-22:** The `models.model_predictions.prediction_context` closed three-value enum `('in_sample_diagnostic', 'walk_forward_oos', 'current_scoring')` is canonical. Section 4 owns the rule for which rows qualify as `'walk_forward_oos'`; 03c stores the value. Inherited from Section 3c constraint #1.
- **A-INH-23:** The closed `rank_method` enumeration `('benchmark_relative', 'peer_relative', 'absolute_with_context')` and the per-sleeve mapping are canonical. Inherited from Section 3c constraint #9.
- **A-INH-24:** `DiversifierHedge` produces no `models.combined_scores` rows under the current first-testable formula. Section 4 handles absence as the documented contract. Inherited from Section 3c §10.6 / A-PRP-29.
- **A-INH-25:** The `models.*` ten-table schema, the disjoint `models.model_run_issues` / `models.scoring_run_issues` enumerations, and the open-run-before-validation lifecycle are read-only invariants. Inherited from Section 3c v1.0 LOCKED.
- **A-INH-26:** The MLflow writer-side contract (one MLflow run per `models.model_runs` row; closed required-tag set per 03c §6.10) is 03c's. Section 4 does not modify it. Inherited from Section 3c constraint #6.

### 11.3 Implementation default (no strategy impact)

- **A-IMP-01:** Migration filenames for `backtest.*` and `attribution.*` schemas continue from the running sequence (e.g., `0007_create_backtest_schema.sql`, `0008_create_attribution_schema.sql`). No strategy impact.
- **A-IMP-02:** Module file structure under `backtest/` (e.g., `harness.py`, `folds.py`, `simulated_fills.py`, `metrics.py`, `cost_application.py`), under `attribution/` (e.g., `decomposer.py`, `signal_attribution.py`, `trade_attribution.py`), and under `regime/` (consumption side: e.g., `reporter.py`). No strategy impact.
- **A-IMP-03:** Test directory layout (`tests/unit/backtest/`, `tests/unit/attribution/`, `tests/unit/regime/`, `tests/integration/backtest/`, `tests/integration/attribution/`, `tests/fixtures/backtest/`, `tests/fixtures/attribution/`). Standard pytest layout per Section 1.
- **A-IMP-04:** `created_by` column populated from container or user identifier; format unspecified at spec level.
- **A-IMP-05:** Whether 03c scoring-run invocation is in-band with the §6.1 fold-metadata seam or driven by a separate Section-4-owned scoring orchestrator. No strategy impact; 03c writes either way.
- **A-IMP-06:** NULL-handling discipline for the `horizon_trading_days` and `sleeve_id` nullable logical-uniqueness columns on `backtest.fold_metrics`, `backtest.aggregate_metrics`, and `backtest.regime_metrics`. **Per v0.4 Revision 1 / A-PRP-04-37**, primary keys on these tables are surrogate (`fold_metric_id`, `aggregate_metric_id`, `regime_metric_id` — all `bigserial`) because primary-key columns cannot be nullable. Logical uniqueness over the dimensioned tuple is declared as a separate constraint. On Postgres 15+, `UNIQUE NULLS NOT DISTINCT (backtest_run_id, fold_id, horizon_trading_days, sleeve_id, metric_name)` (and the analogous tuples on the other two tables) treats NULL as equal so that a single `(backtest_run_id, fold_id, NULL, NULL, 'turnover')` row is unique. On Postgres < 15, the equivalent constraint is a UNIQUE index on `(backtest_run_id, fold_id, COALESCE(horizon_trading_days, -1), COALESCE(sleeve_id, -1), metric_name)` (and analogous on the other two tables); the `-1` sentinel is safe because `horizon_trading_days` is constrained to `(63, 126)` and `sleeve_id` is `bigserial`-positive. The Phase 1 deployment Postgres version is selected by Section 2 / Section 1 deployment defaults; this is a no-strategy-impact mechanical choice tied to whichever version is current.

### 11.4 Proposed default requiring approval

Each item below is a Builder-proposed strategy-affecting choice. The Approver explicitly accepts or rejects each. Items that lack a Builder recommendation are in §10 instead.

- **A-PRP-04-01:** `backtest.*` and `attribution.*` schemas, ten tables total (seven `backtest.*`, three `attribution.*`) per §6.5 / §6.6 schema sketches.
- **A-PRP-04-02:** `config/backtest.yaml` shape per §7.1.
- **A-PRP-04-03: Walk-forward fold geometry** per §6.2 / §7.1: `fold_geometry: 'rolling'`, `fold_count: 8`, `fold_size_trading_days: 252`, `initial_train_trading_days: 1260` (rolling mode), `expanding_initial_train_trading_days: 1260` (expanding mode). **Test windows do not partition the full window (Option C from v0.3 Revision 1).** `fold_count` and `fold_size_trading_days` are independent knobs; the bound is `signal_date_min + initial_train_trading_days + N*(fold_size + embargo) - embargo <= signal_date_max - max(horizon)`, validated at config-load time. SDR Decision 7 names walk-forward but does not pin geometry; this is the Builder's first proposal.
- **A-PRP-04-04:** `embargo_trading_days: 126` per SDR Decision 7 (Builder confirms named value as the Phase 1 default).
- **A-PRP-04-05: OOS qualification rule** per §6.1: a `(etf_id, as_of_date, model_kind, model_run_id)` row is `'walk_forward_oos'` for fold `f` iff (a) `as_of_date ∈ [test_signal_date_min(f), test_signal_date_max(f)]`; (b) the model run was fit on a training set from which every row whose recorded `[entry_date, exit_date]` overlaps any test row's `[entry_date, exit_date]` has been purged, with the additional `embargo_trading_days` margin excluded from training on both sides of the test window. **Purge / embargo applies to training candidates only — never to test-window rows.** Edge-case sub-rule: rows whose underlying training rows had `target_value = NULL` (Bucket 2 from 03b §6.5) are **not** specially excluded; NULL propagation through 03c naturally yields NULL `predicted_value` and the row is excluded from metric computation that requires non-null `predicted_value`.
- **A-PRP-04-06: Long-only-corrected cost-application formula** per §6.7: entry `simulated_fill_price_after_cost = simulated_fill_price_pre_cost * (1 + cost_bps / 10000)`; exit `simulated_fill_price_after_cost = simulated_fill_price_pre_cost * (1 - cost_bps / 10000)`. Replaces the v0.1 inverted formula. Directionally correct round-trip cost for long-only Phase 1 simulated fills per SDR Decision 8.
- **A-PRP-04-07: Per-fold metric set** per §6.10 / §7.1: `total_return`, `cagr`, `volatility`, `max_drawdown`, `risk_adjusted_return`, `hit_rate`, `turnover`, `cost_drag`, `benchmark_relative_return`, `sleeve_level_performance`. Adding a metric requires a Section 4 amendment.
- **A-PRP-04-08: Aggregate metric set** per §6.10 / §7.1: per-fold set plus `fold_consistency`.
- **A-PRP-04-09: Signal attribution component set** per §7.1: `benchmark_relative_excess_return`, `calibrated_outperformance_probability`, `rank_within_sleeve_position`.
- **A-PRP-04-10: Trade attribution component set** per §7.1: `entry_price_skill`, `exit_price_skill`, `holding_period_return`, `cost_drag`.
- **A-PRP-04-11:** `total_attribution_residual_bound: 0.0001` per §7.1.
- **A-PRP-04-12:** `mlflow.backtest_experiment_enabled: false` default. Whether Section 4 introduces its own MLflow experiments for backtest tracking, separate from 03c's per-`model_kind` experiments, is opt-in: enabling requires the Approver to populate `mlflow.required_tags` with a closed required-tag set; current Section 4 scope does not draft that set because the question is upstream.
- **A-PRP-04-13:** `regime_reporting.classifier_unavailable_behavior: 'emit_partial_with_warning'` per §7.1. Closed enum `('emit_partial_with_warning', 'skip_with_warning', 'fail')`. Per SDR Decision 9 partial-dimension fallback (trend-only when VIX is absent), Builder recommends emit-partial.
- **A-PRP-04-14:** `cost_config_missing_behavior: 'warn_proceed_zero_cost'` per §7.1. Closed enum `('warn_proceed_zero_cost', 'fail')`. Builder recommends warn-proceed for Phase 1 research convenience; Approver may direct `'fail'` to make cost-config a hard prerequisite.
- **A-PRP-04-15: Per-fold failure containment — skip-and-continue.** When an individual fold's 03c invocation fails (`'failed'` `models.model_runs`), the harness records the issue and skips the affected fold; the backtest run continues with remaining folds. Alternative: fail the entire backtest run.
- **A-PRP-04-16: Empty-test-window severity — `'warning'`.** When a fold's test window contains zero eligible signal dates, the harness emits a `'warning'` `backtest.backtest_run_issues` row and skips the fold. Alternative: `'fail'`.
- **A-PRP-04-17: Calibrated-`model_kind`-unavailable handling per fold — skip the fold.** When a fold's calibrated classifier run is `'failed'` but the uncalibrated parent is `'succeeded'`, Section 4 skips the affected fold. **Falling back to the uncalibrated `model_kind` is forbidden** at the model layer per 03c §6.5 ("the uncalibrated classifier outputs are not used as a substitute"); the only Approver-available alternative is failing the entire run.
- **A-PRP-04-18:** Disjoint closed `issue_type` enumerations on `backtest.backtest_run_issues` and `attribution.attribution_run_issues` per §6.5 / §6.6. Includes `'snapshot_mismatch'` (added in v0.2 per Revision 8).
- **A-PRP-04-19:** `backtest.simulated_fills.action` closed enum (`'enter_long'`, `'exit_long'`, `'rebalance_in'`, `'rebalance_out'`) intentionally disjoint from any future Section 5 portfolio-action enum per §6.4.
- **A-PRP-04-20:** `attribution.attribution_runs` is 1:1 with `backtest.backtest_runs` per §6.6 — FK uniqueness by behavior, not by hard constraint, to allow future amendment to 1:many. Alternative: add a UNIQUE constraint on `attribution_runs.backtest_run_id` to enforce 1:1 at the schema level.
- **A-PRP-04-21:** `backtest.*` and `attribution.*` schemas introduced without explicit Section 2 amendment, mirroring the 03a / 03b / 03c precedent (those sections introduced `features.*` / `targets.*` / `models.*` schemas under their own section approvals rather than via Section 2 amendments). Approver may direct a Section 2 amendment instead.
- **A-PRP-04-22:** `config/backtest.yaml` introduced without explicit Section 1 amendment, mirroring the 03b `config/targets.yaml` precedent (Section 1 LOCKED's config-dependencies table did not enumerate `config/targets.yaml` either; 03b proceeded without amendment per 03b §11.6 #7). Section 1 LOCKED's table assigns walk-forward / embargo to `config/model.yaml`, but 03c LOCKED carved `config/model.yaml` as 03c-exclusive (constraint #14), making `config/model.yaml` unavailable for Section 4 walk-forward / embargo content. Approver may direct a Section 1 amendment instead.
- **A-PRP-04-23:** Section 4 lock proceeds independently of `config/costs.yaml` per-bucket basis-point population and independently of regime-classifier ownership resolution (A-OQ-04-07); runtime behaviors A-PRP-04-13 and A-PRP-04-14 control the gap. Alternative: block Section 4 lock on either dependency.
- **A-PRP-04-24: Backtest-only simulated allocation contract** per §6.4.1: top-N selection (`top_n_per_sleeve_per_horizon: 5`), equal-weight within sleeve cross-section, monthly default rebalance cadence, exit at next rebalance on rank fall or combined-score absence, long-only, no SDR Decision 10 ATR / take-profit / replacement logic. **The contract is strictly internal to backtest validation; it is not portfolio rules, paper portfolio state, order intent, or Section 5 behavior.**
- **A-PRP-04-25: Annualization factor `metrics.trading_days_per_year: 252`** per §6.10. Used in `cagr` (`^ (252 / N)`) and `volatility` (`* sqrt(252)`).
- **A-PRP-04-26:** `metrics.risk_free_rate_annual: 0.0` per §6.10 / §7.1. Used only in `risk_adjusted_return`. Phase 1 research-simplicity choice; Approver may direct a non-zero rate or a T-bill-series-based alternative.
- **A-PRP-04-27:** `metrics.benchmark_relative_rollup: 'weighted_by_sleeve_weight'` per §7.1. Closed enum (`'weighted_by_sleeve_weight'`, `'equal_weighted_etf'`, `'sleeve_aggregate_then_equal_weighted'`). Used to roll per-ETF benchmark-relative returns into a portfolio-level `benchmark_relative_return` metric.
- **A-PRP-04-28:** *Retired in v0.3.* In v0.2 this proposed encoding sleeve identifiers in `metric_name` strings (e.g., `'sleeve_level_performance:sector'`). v0.3 Revision 3 supersedes this with first-class `horizon_trading_days` and `sleeve_id` columns on `backtest.fold_metrics`, `backtest.aggregate_metrics`, and `backtest.regime_metrics`; `metric_name` remains a clean closed enum and does not encode horizon or sleeve. The cleaner schema replaces the v0.2 string-encoding workaround.
- **A-PRP-04-29: Per-horizon keying on `backtest.simulated_fills`** per §6.5 (Option A in v0.2 Revision 3). Adds `horizon_trading_days` to the PK and propagates into `attribution.trade_attribution`'s composite FK and PK. Alternative (Option B): define a backtest run as evaluating one selected horizon only and add a single `horizon_trading_days` column to `backtest.backtest_runs`.
- **A-PRP-04-30: Regime classifier ownership — Option A (Section 4 owns a minimal SDR Decision 9 labeler in `regime/`)** as the Builder recommendation under A-OQ-04-07. Cross-listed; the structural choice itself remains an Open Question because it implicates Section 1's `regime/` (computation side) reservation language. Builder recommends Option A; Approver may direct Option B.
- **A-PRP-04-31: Current-survivor disclosure label storage on `backtest.backtest_runs`** per §6.5 (NOT NULL `current_survivor_disclosure_label` column populated from `common.get_current_survivor_label()`). Per SDR Decision 4 / Decision 16 bias-control labeling, every backtest output carries the disclosure for downstream UI surfacing. Alternative: store the label in `backtest.backtest_run_issues` as a `'warning'` row instead of as schema metadata. Builder recommends the schema-metadata approach because it makes the disclosure structural rather than incidental.
- **A-PRP-04-32: Walk-forward test windows do not partition the full signal-date window (Option C, v0.3 Revision 1).** Test windows partition `[earliest_test_signal_date, latest_test_signal_date]` only; `[signal_date_min, earliest_test_signal_date)` is initial training; `(latest_test_signal_date, signal_date_max]` is unused. `fold_count` and `fold_size_trading_days` are independent knobs. Alternative options: (A) derive `fold_count` from window and fold-size; (B) derive fold-size from window and `fold_count`. Builder rejects both A and B because neither matches walk-forward semantics — the early portion of the signal-date window is structurally the initial training period, not part of any test fold.
- **A-PRP-04-33: Explicit simulated weights on every `backtest.simulated_fills` row (v0.3 Revision 4).** Three columns added: `simulated_weight_before`, `simulated_weight_after`, `simulated_weight_delta` with CHECK consistency. Replaces v0.2's implicit weight reconstruction from row counts. Alternative: a single `simulated_weight` column (Builder rejected because it loses the before/after pair needed for partial-trim and partial-add semantics on `'rebalance_in'` / `'rebalance_out'` rows).
- **A-PRP-04-34: First-class `horizon_trading_days` and `sleeve_id` dimension columns on `backtest.fold_metrics`, `backtest.aggregate_metrics`, `backtest.regime_metrics` (v0.3 Revision 3, refined in v0.4 Revision 1).** Both columns nullable (NULL = horizon-agnostic / sleeve-agnostic); both participate in the **logical uniqueness constraint** over the dimensioned tuple, not in the primary key (primary-key mechanics are governed by A-PRP-04-37 — surrogate `bigserial` PKs on each table). `metric_name` remains a clean closed enum that does not encode horizon or sleeve. Replaces and retires v0.2's A-PRP-04-28 (string-encoded sleeve identifier in `metric_name`).
- **A-PRP-04-35: `is_pipeline_validation_only` boolean on `backtest.backtest_runs` (v0.3 Revision 5).** A backtest run executed under any zero-cost-fallback or other pipeline-validation-only condition is labeled with `is_pipeline_validation_only = true`; runs labeled true cannot be used as serious model validation evidence or promotion evidence. Section 5's promotion gate must reject promotion evidence drawn from `is_pipeline_validation_only = true` rows. Section 4's contract is to set the flag correctly and surface the reason; Section 5 owns gate enforcement. Alternative: store the flag in `backtest.backtest_run_issues` as a `'warning'` row instead of as schema metadata. Builder recommends the schema-metadata approach because the flag is consulted on every read of `backtest.aggregate_metrics` for promotion-eligibility filtering.
- **A-PRP-04-36: Closed `pipeline_validation_only_reason` enum on `backtest.backtest_runs` (v0.3 Revision 5).** When `is_pipeline_validation_only = true`, the `pipeline_validation_only_reason` column carries one of the closed-set reason codes: `'cost_config_zero_fallback'` (the v0.3 R5 case), with future Approver-approved additions possible. NULL when `is_pipeline_validation_only = false`; CHECK constraint enforces the conditional NULL. Alternative: a free-text reason field. Builder recommends the closed enum so reason filtering is mechanical.
- **A-PRP-04-37: Surrogate primary keys + logical UNIQUE NULLS NOT DISTINCT on the three metric tables (v0.4 Revision 1).** `backtest.fold_metrics`, `backtest.aggregate_metrics`, and `backtest.regime_metrics` use surrogate `bigserial` primary keys (`fold_metric_id`, `aggregate_metric_id`, `regime_metric_id`) because primary-key columns cannot be nullable, and the dimensioning columns `horizon_trading_days` and `sleeve_id` introduced in v0.3 Revision 3 are deliberately nullable (NULL = horizon-agnostic / sleeve-agnostic). Logical uniqueness over the dimensioned tuple is declared as a separate `UNIQUE NULLS NOT DISTINCT` constraint on Postgres 15+, with a `COALESCE`-based UNIQUE index fallback on Postgres < 15 (sentinel `-1` is safe because `horizon_trading_days ∈ {63, 126}` and `sleeve_id` is `bigserial`-positive). The v0.3 design principle is preserved: `metric_name` remains a clean closed enum, and horizon / sleeve remain first-class columns rather than `metric_name`-suffix encodings (the retired A-PRP-04-28 pattern). Implementation discipline classified per A-IMP-06; logical-uniqueness enforcement verified per §8.14 UNI-01 / UNI-02 / UNI-03. **Alternative considered and rejected:** declaring the dimensioning columns NOT NULL with sentinel values (e.g., `horizon_trading_days = 0` for horizon-agnostic). Rejected because it conflates "horizon-agnostic" with a real horizon value, breaks the CHECK constraint `(63, 126)`, and silently changes the semantic of "this metric is not horizon-conditioned" to "this metric is conditioned on horizon=0", which is wrong.

### 11.5 Open questions for Approver

Cross-references §10 for the §3.3 classification audit. As of the current Section 4 scope, three items remain unresolved Approver decisions; some include a Builder recommendation, but none are locked until the Approver accepts them:

- **A-OQ-04-07** — Regime classifier ownership (Option A vs Option B; Builder recommends Option A but the structural choice is Approver's).
- **A-OQ-04-14** — Active → Warning automated trigger definition (Builder does not propose a trigger).
- **A-OQ-04-18** — Backtest confidence-level outputs sufficiency (Builder does not propose additional fields).

---

## 12. Section 4 → Section 5 / Section 6 handoff (forward references)

This section catalogues forward references the next downstream sections will need so Section 4 lock provides clean seams. **Nothing in this section commits the next section's design.**

### 12.1 Handoff to Section 5 (Portfolio rules, paper portfolio state, broker-neutral order intent, kill switch)

Section 5 will need:

- **The `backtest.aggregate_metrics` and `backtest.regime_metrics` table contracts (§6.5)** — Section 5's promotion-gate logic and kill-switch evaluation read these as **validation evidence surfaces** (§6.9). Section 5 does not write to `backtest.*`.
- **The `attribution.signal_attribution` and `attribution.trade_attribution` table contracts (§6.6)** — Section 5 may surface attribution alongside portfolio decisions for review. Section 5 does not write to `attribution.*`.
- **The `backtest.simulated_fills` ledger (§6.4)** — Section 5 reads it for offline review and gate evaluation but **does not consume it as paper portfolio state**. The simulated fills ledger is not paper portfolio state, not order intent, and not broker-facing. Section 5 owns paper portfolio state in a separate `paper.*` schema (Section 5 design).
- **The closed `action` enum on `backtest.simulated_fills` (`'enter_long'`, `'exit_long'`, `'rebalance_in'`, `'rebalance_out'`)** is intentionally disjoint from any Section 5 portfolio-action enum (BUY / HOLD / TRIM / SELL / REPLACE / WATCH per SDR Decision 10). Section 5 must not consume Section 4's enum; Section 5 must not produce Section 4's enum.
- **The validation evidence surface (§6.9)** — Section 5 evaluates gates and the kill switch over this surface; Section 4 does not evaluate either.

**Writer-side ownership boundary.** Section 5 does **not** write to `backtest.*` or `attribution.*`. Section 5's portfolio rules engine, paper portfolio state, and order-intent surfaces are owned by Section 5; Section 4 does not specify them.

### 12.2 Handoff to Section 6 (Operator UI)

Section 6 will need:

- **Read-only access to `backtest.*` and `attribution.*`** for the seven Phase 1 screens (per SDR Decision 17). The schemas are designed for read-only consumption; Section 6 selects the database-access enforcement mechanism for Section 1 invariant 3.
- **The reproducibility chain** — every backtest run, every attribution run, every simulated fill is reachable to a `data_snapshot_id` per §6.8. Section 6 surfaces the chain for audit.
- **The Phase 1 backtest confidence-level outputs (§6.9)** — Section 6's UI displays them with the bias-control disclosures Section 1 / Section 2 / Section 6 contribute to.

---

## 13. Proposed traceability matrix updates — draft only

**This section is a sketch. It does NOT modify `docs/traceability_matrix.md`. No row in this section should be read as implying any Section 4 contribution is "complete" before Section 4 v1.0 LOCKED / APPROVED. All status language is conditional and pending.**

`docs/traceability_matrix.md` is currently at v0.6 with status entries reflecting Sections 1, 2, 3a, 3b, 3c v1.0 LOCKED. The rows below are sketches of what would be merged into the traceability matrix **after** Section 4 is approved and locked. They are not pre-merge claims of completion.

### 13.1 Rows where Section 4 is the responsible section (status pending until Section 4 approval and matrix merge)

| SDR Decision | Topic | Proposed Section 4 contribution at lock | Status after Section 4 lock, if approved |
|---|---|---|---|
| Decision 7 | Walk-forward harness, purge / embargo, OOS qualification, leakage tests | Section 4 §6.1 (§12.1 invocation seam shape; OOS qualification rule with v0.3 R2 correction — purge applies to training candidates only), §6.2 (fold construction over 03b per-row metadata, with v0.3 R1 Option C: test windows do not partition the full window), §6.3 (purge / embargo arithmetic over recorded `entry_date` / `exit_date`), §8.1 WF-02 (rewritten in v0.3 R1) and WF-05 (all-folds-failed terminal case), §8.3 / §8.4 (OOS-03 rewritten in v0.3 R2; LK-01 window-vs-window per v0.2 R6) | Pending until Section 4 approval and matrix merge. Embargo width 126 is SDR-named; fold geometry per A-PRP-04-03 / A-PRP-04-32 (Option C — independent `fold_count` and `fold_size_trading_days` knobs); OOS qualification rule per A-PRP-04-05 (purge applies to training only); leakage-test fixtures are Proposed defaults. |
| Decision 8 | Transaction-cost consumption seam (locked bucket names; pending basis-points and account-type rules) | Section 4 §6.7 (consumption seam over the SDR-locked four-value bucket enumeration `ultra_liquid_etf` / `liquid_sector_etf` / `thematic_niche_etf` / `commodity_specialty_etf`), §6.4 (cost-applied simulated fills with long-only-corrected formula), §7.2 (`config/costs.yaml` read), §6.10 `cost_drag` metric | Pending until Section 4 approval and matrix merge. **SDR Decision 8 already locks the four Phase 1 cost-bucket names; Section 4 inherits and consumes them.** Per-bucket basis-point values and account-type handling (internal paper / retirement / taxable / non-retirement-API-testing) remain pending — basis-points are Builder Proposed defaults / Open Questions; account-type handling is deferred to a later cash-out under `config/costs.yaml`. |
| Decision 9 | Regime reporting (consumption side) | Section 4 §6.5 `backtest.regime_metrics`, §7.2 (`config/regime.yaml` read), §8.8 (RG-* tests) | Pending until Section 4 approval and matrix merge. Regime classifier (labeler) ownership is an Open Question (A-OQ-04-07) — Option A: Section 4 owns a minimal SDR Decision 9 labeler in `regime/` (Builder recommended); Option B: a future approved amendment / sub-section owns the labeler. The §6.5 schema and §7.2 consumption seam are unaffected by the choice. |
| Decision 11 | Attribution storage and reporting half | Section 4 §6.5 (metrics tables now dimensioned by `horizon_trading_days` and `sleeve_id` per v0.3 R3 / A-PRP-04-34; A-PRP-04-28 retired; `metric_name` remains a clean closed enum), §6.5 `backtest.simulated_fills` with explicit `simulated_weight_before` / `_after` / `_delta` columns per v0.3 R4 / A-PRP-04-33 (drives turnover, attribution, and portfolio-value reconstruction without row-count inference), §6.6 (`attribution.*` schema), §6.8 (reproducibility chain extension), §8.9 (AT-* tests), §8.12 FM-15 / FM-16 (horizon-dimension correctness; `metric_name` purity) | Pending until Section 4 approval and matrix merge. Model-tracking / MLflow writer half is 03c's. |
| Decision 16 | Bias controls — backtest layer | Section 4 §6.1 (OOS qualification with v0.3 R2 purge-applies-to-training-only correction), §6.2 / §6.3 (purge / embargo using 03b-recorded forward-label windows on both sides per v0.2 R6; v0.3 R1 Option C non-partition rule), §6.4.1 (backtest-only simulated allocation contract — explicitly not Section 5 portfolio behavior; explicit weights per v0.3 R4), §6.5 (`backtest.backtest_runs.is_pipeline_validation_only` + `pipeline_validation_only_reason` per v0.3 R5 / A-PRP-04-35 / A-PRP-04-36 — zero-cost-fallback runs structurally labeled non-promotion-evidence), §6.5 (metrics tables dimensioned by `horizon_trading_days` and `sleeve_id` per v0.3 R3), §6.5 `backtest.backtest_run_issues.issue_type='all_folds_failed'` per v0.3 R7 (terminal-case bias control: zero-fold runs cannot masquerade as evidence), §6.8 (reproducibility chain), §6.10 (financial metric definitions with formulas), §8.4 LK-01 (window-vs-window leakage test), §8.7 REP-05 (current-survivor disclosure persisted), REP-06 (pipeline-validation-only flag wired to cost-fallback per v0.3 R5), REP-07 (cross-section enforcement reservation for Section 5), §8.1 WF-05 (all-folds-failed terminal-case test), §6.9 (validation evidence surface) | Pending until Section 4 approval and matrix merge. UI disclosure surfacing half remains Section 6's. Section 5's promotion gate must filter on `is_pipeline_validation_only = false`. |

### 13.2 Rows where Section 4 is a downstream consumer (matrix entry stays pinned to the owning section; Section 4 references are read-only)

| SDR Decision | Topic | Section 4 relationship | Note |
|---|---|---|---|
| Decision 1 | Phase 1 ETF universe | Section 4 reads `universe.*` and target / model surfaces; no Section 4 module reads or writes individual stocks, fundamentals, holdings, news, options, or Danelfin | Owned by Section 2; Section 4 reads, does not redefine. |
| Decision 2 | Open architecture / open data layer | No Section 4 module imports from `providers/`; verified by §8 CC-04 | Architecture coherence; Section 4 respects but does not redefine. |
| Decision 3 / 4 | Universe survivorship / ETF launch-date handling | Section 4 inherits eligibility-row omission and lifecycle-bound absence transitively | Owned by Section 2; Section 4 does not redefine. |
| Decision 5 | Sleeve / benchmark / diversifier treatment | Section 4 reads `rank_method` per sleeve and respects `DiversifierHedge` zero-rows contract | Owned by 03c; Section 4 does not redefine. |
| Decision 6 | Combined-score formula | Section 4 reads `models.combined_scores` produced under the 03c first-testable formula | Owned by 03c; Section 4 does not redefine. |
| Decision 12 | Model promotion gates / kill switch | Section 4 produces validation evidence; Section 5 evaluates the gates and the kill switch | Owned by 03c (schema) + Section 5 (gates / enforcement); Section 4 contributes evidence only. |
| Decision 17 | UI is read-only | `backtest.*` / `attribution.*` designed for read-only consumption | Owned by Section 6; Section 4 reserves the read-only contract. |

### 13.3 Rows untouched by Section 4

The following decisions are not within Section 4 scope and the traceability matrix entries should remain as currently set (or as updated by future sections):

- Decision 10 (portfolio management and risk rules) — Section 5.
- Decision 13 (LLM workflow / agentic coding / QA) — process discipline; no spec-section ownership.
- Decision 14 (Danelfin deferred) — out of Phase 1.
- Decision 15 (paper portfolio state / broker-neutral order intent) — Section 5.
- Decision 18 (deployment) — Section 1.

### 13.4 New traceability rows that Section 4 may motivate

Section 4 does not propose new SDR decisions.

---

**End of Section 4 v1.0 LOCKED / APPROVED.**
