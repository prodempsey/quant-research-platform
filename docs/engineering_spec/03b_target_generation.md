# Engineering Specification — Section 3b: Target Generation

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v1.0 LOCKED / APPROVED
**Date:** 2026-04-29
**Builder:** Claude
**Section:** Engineering Specification — Section 3b: Target Generation
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Engineering Specification — Section 3a v1.0 LOCKED / APPROVED (`docs/engineering_spec/03a_feature_engineering.md`)
- Section 1 approval note (`docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`)
- Section 2 approval note (`docs/reviews/2026-04-27_spec_02_data_layer_approval.md`)
- Section 2 traceability updates (`docs/reviews/2026-04-27_spec_02_data_layer_traceability_updates.md`)
- Section 3a approval note (`docs/reviews/2026-04-29_spec_03a_feature_engineering_approval.md`)
- Section 3a traceability updates (`docs/reviews/2026-04-29_spec_03a_feature_engineering_traceability_updates.md`)
- `docs/traceability_matrix.md` v0.4 (Sections 1, 2, 3a v1.0 LOCKED merged)

**Scope statement basis (in lieu of a separate Section 3b handoff packet).** The Approver explicitly authorized 03b drafting and revision from the following four sources, taken together as the de facto scope statement:

(a) the current general project handoff (`docs/current_claude_context_handoff.md`);
(b) Section 3a §12 forward references to 03b;
(c) Section 3a approval note §5.1 *"Open items handed forward to 03b"*;
(d) the targeted v0.2 revision instruction issued by the Approver on 2026-04-29 (the QA-driven revision list applied in this v0.2 pass).

The v0.1 draft was produced under (a)–(c); v0.2 incorporates (d). If a fresh Section 3b handoff packet is later issued, any divergence between this draft and the packet is resolved in favor of the packet via standard EW §3 revision discipline. This scope-basis language is intentionally written so the eventual 03b approval note can cite it directly without further amendment.

---

## Changelog

- **v1.0 LOCKED / APPROVED (2026-04-29):** v0.3 DRAFT promoted to v1.0 LOCKED / APPROVED with **no substantive change** to behavior, schema, tests, scope, or ownership. Locking metadata flipped (status header, end-of-document marker) and minor wording cleanup applied to remove stale "v0.2 Revision N" / "v0.3 makes" / "in v0.2" / "in v0.2/v0.3" version markers in the current spec body where they are not historical changelog entries — replaced with "current 03b scope" or removed where they read as noise. The historical v0.1 → v0.3 changelog entries are preserved verbatim. Approver: Jeremy. Builder: Claude. QA Reviewer: ChatGPT. Approval note: `docs/reviews/2026-04-29_spec_03b_target_generation_approval.md`. Traceability matrix update companion: `docs/reviews/2026-04-29_spec_03b_target_generation_traceability_updates.md`.

- **v0.3 (2026-04-29):** Targeted cleanup pass per Approver-issued instruction. **One revision; no scope expansion; no Section 1 amendment proposed; no Section 2 amendment proposed; no 03c drafting added; no implementation started.** v0.2 structural decisions are preserved unchanged.
  - **Cleanup 1 — Removed residual ambiguity around "insufficient-forward-history" and "fully observable forward window" phrasings.** v0.2 established the canonical null-vs-no-row taxonomy in §6.5, but a small set of phrases in earlier and later sections still used language ("insufficient-forward-history", "the target is null when either series cannot resolve a valid window", "fully observable forward window") that could be read as implying front-edge truncation produces a null row. v0.3 rewrites only those phrases so they defer unambiguously to the §6.5 taxonomy: if the required forward window exceeds snapshot coverage **no row is written** (Bucket 1); if the window is otherwise coverable but an input price bar is missing or benchmark history is non-overlapping inside the window, **a row is written with `target_value = NULL`** (Bucket 2). The canonical §6.5 taxonomy itself is preserved exactly; front-edge truncation remains absence-only and not a failed run; index-only benchmark behavior remains unchanged (regression row written with `target_value = NULL`, classification row written with `target_value = NULL`, `targets.target_run_issues` warning row, no silent benchmark substitution, no fallback to `secondary_benchmark_id`). Affected sections: §1 Purpose (one phrase tightened); §2 (Decision 4 row text tightened); §3 In scope (one phrase tightened); §6.1 (cross-series alignment statement split into the two §6.5 buckets); §6.2 regression family (cross-series statement split similarly); §6.2 classification family null-propagation list (the example "insufficient forward window" removed from the NULL-cause list because it belongs to the no-row list, which is enumerated separately in the same paragraph); §6.5 `target_value` column note ("insufficient-forward-history" removed from the parenthetical); §6.5 Bucket 2 description (parenthetical tightened to refer only to otherwise-coverable windows); §8.1 test #8 (Bucket 2 made explicit); §8.2 test #33 (Bucket 2 made explicit); §9 edge case 4 (descriptor "insufficient forward history" removed from the title because the body already states the precise Bucket 1 semantics).

- **v0.2 (2026-04-29):** Targeted revisions per Approver-issued QA-driven revision list. Six revisions plus preservation of accepted v0.1 strengths; no scope expansion; no Section 1 amendment proposed; no Section 2 amendment proposed; no 03c drafting added; no implementation started.
  - **Revision 1 — Snapshot forward-coverage blocking contradiction resolved.** v0.1 contained an internal contradiction between §6.3 (which listed "snapshot does not cover the maximum forward window" as a blocking condition) and §6.3's nuance paragraph + §6.5 + §10.9 (which treated the same condition as row-level absence). Resolved by the unambiguous rule below: invalidated snapshots block; failed ingestion runs block; partial ingestion runs block (Phase 1 default); **front-edge truncation does NOT block** — signal dates whose required forward window exceeds snapshot coverage simply produce no `targets.target_values` rows. The run may still succeed if at least some eligible rows are produced. **No warning issue is required for front-edge truncation in v0.2** unless the Approver later directs otherwise. Affected sections: §5.1 (`ops.data_snapshots` and `ops.ingestion_runs` input notes), §6.3 (lifecycle paragraph rewritten), §6.5 (nullable-value semantics rewritten — see Revision 2), §6.7 (`data_snapshot_id` linkage), §6.9 (coverage parity with 03a), §8 (tests #5, #9, #21, #22, #37, #40 reviewed and tightened where needed), §9 (edge case 4 clarified as row absence, not run failure), §10.9 (resolved — moved to §11.6), §11 (assumptions updated), §12 (handoff updated).
  - **Revision 2 — Null-vs-no-row taxonomy clarified.** v0.1 was inconsistent about whether target rows are absent or present-with-null on certain edge cases. v0.2 adopts an explicit two-bucket taxonomy. **No row** is written for: ETF/date not rank-eligible at signal date `T`; `T < first_traded_date(e)`; `T >= delisted_date(e)`; ETF delists before the required `exit_date`; forward window exceeds snapshot coverage. **Row with `target_value = NULL`** is written for: missing input price bar inside an otherwise coverable forward window; benchmark history missing or non-overlapping inside an otherwise coverable forward window; index-only benchmark condition; classification target whose underlying regression target is NULL. For index-only benchmark specifically: the regression target row is written with `target_value = NULL`; the classification target row is written with `target_value = NULL`; a `targets.target_run_issues` warning row with `issue_type='index_only_benchmark'` is recorded; **no silent substitution; no use of `secondary_benchmark_id`**. Affected sections: §6.2 (target families — index-only paragraph rewritten for both regression and classification), §6.5 (nullable-value semantics rewritten as the canonical taxonomy), §6.6 (target_run_issues consumption text aligned), §8 (per-family and cross-cutting tests aligned), §9 (edge cases aligned), §10.3 (resolved — moved to §11.6 as two Approver-resolved defaults), §10.5 (residual structural Open Question retained, interim behavior recorded as Approver-resolved in §11.6), §11 (assumptions updated).
  - **Revision 3 — `config/targets.yaml` file-location issue resolved without reopening Section 1.** Per Approver direction: 03b owns a new strategy-affecting config file `config/targets.yaml`; this is approved within the 03b spec approval path; **no Section 1 amendment is proposed by 03b**; targets config is **not** moved into `config/model.yaml`; 03c continues to own `config/model.yaml`; 03c may read target metadata but does not own target config. Affected sections: §7.1 (Open Question reference removed; file ownership stated directly), §7.2 (removed "subject to §10.6" nuance), §7.3 (cleanup), §7.4 (commit-discipline language unchanged but tightened), §10.6 (resolved — moved to §11.6), §11 (assumptions updated), §12 (handoff cleanup), §13 (traceability notes — Decision 6 row text updated; no Section 1 amendment cited).
  - **Revision 4 — Approver decisions recorded as accepted defaults.** The following ten items are now Approver-resolved defaults (not Open Questions, not Builder Proposed defaults): (1) entry/exit Convention B; (2) classification threshold `θ = 0.0`; (3) `missing_data.rule = "null_on_any_missing_input_in_window"`; (4) `forward_window.delisted_within_window_rule = "no_row"`; (5) target persistence with `data_snapshot_id` linkage; (6) index-only benchmark interim behavior (no Section 2 amendment proposed; no silent substitution; no fallback to `secondary_benchmark_id`; null target row plus `targets.target_run_issues` warning); (7) `config/targets.yaml` as the config file (no Section 1 amendment proposed); (8) target families: regression excess return and classification outperformance only; (9) target horizons: exactly 63 and 126 trading days; (10) snapshot coverage / front-edge truncation: absence-only, no run-level warning issue in v0.2. The corresponding Open Questions and Proposed defaults in §10 are removed; one residual Open Question (the structural index-only-benchmark gap, inherited from 03a §10.1) is preserved, and the Implementation default for `targets.*` migration filenames is preserved. The full table lands in §11.6.
  - **Revision 5 — Accepted v0.1 strengths preserved** unless directly affected by Revisions 1–4: 03b writes only to `targets.*`; 03b does not write to `ops.data_quality_exceptions` or any `ops.*` table; `targets.target_run_issues` is the target-layer issue log; `target_run_issues.target_run_id` is NOT NULL and FK-protected; database-level `target_set_version` integrity parallel to 03a; no provider imports from `targets/`; adjusted-close-only target calculations; no raw OHLCV in target calculations; no live broker, no MLflow writes, no model code; 03b does not consume `features.feature_values` for target generation; 03c owns joining features and targets for training data assembly; Section 4 owns purge/embargo enforcement; no implementation/code is started.
  - **Revision 6 — Lightweight 03b handoff packet note formalized.** The scope-statement-basis language at the top of this document now lists four explicit Approver-authorized sources for 03b drafting and revision, including this v0.2 revision instruction. The eventual 03b approval note can cite this language directly. No separate handoff packet file is created at this stage.

- **v0.1 (2026-04-29):** Initial draft. Eleven-field EW §3.2 template populated in order. Every assumption classified per EW §3.3. Honors the seven Section 1 invariants, the ten Section 2 v1.0 LOCKED constraints, and the eleven Section 3a v1.0 LOCKED conditions on subsequent sections (03a approval note §4). The principal Phase 1 scope choices — entry/exit convention, classification threshold, missing-forward-data rule, target-config file location, target persistence vs on-the-fly — are visibly classified and flagged as Open Questions or Builder Proposed defaults requiring Approver approval; none are silently resolved.

---

## 1. Purpose

`targets/` generates regression and classification labels for use by 03c (model layer) and Section 4 (backtest harness). It consumes adjusted-close price series from `prices.etf_prices_daily`, ETF identity / lifecycle / benchmark fields from `universe.etfs`, the as-of-date eligibility timeline from `universe.etf_eligibility_history`, and benchmark resolution from `universe.benchmarks`. It produces a per-ETF, per-signal-date target surface aligned to the same `(etf_id, as_of_date)` axis Section 3a established for features.

Section 3b is responsible for what targets are computed, how they are aligned in time relative to the signal date, what they consume, what they produce, and how they tie back to a reproducible data snapshot. Section 3b is **not** responsible for what to do with the targets (model fitting, calibration, ranking, walk-forward harness, purge/embargo enforcement, attribution, portfolio rules).

The principal architectural cash-out points 03b inherits are:

- **SDR Decision 6 — Target Design and Ranking Objective.** Dual-target framework: a regression target (forward excess return over 63 and 126 trading days) and a classification target (whether the ETF outperformed the benchmark over the same horizons).
- **SDR Decision 7 — Validation, Calibration, and Backtest Confidence Level.** Walk-forward validation is owned by Section 4. Section 3b records the per-target metadata (signal date, horizon, entry date, exit date) that Section 4's purge/embargo logic will consume to handle overlapping-label risk per Decision 7 and Decision 16. Section 3b does not implement purge/embargo itself.
- **SDR Decision 16 / Section 1 invariant 7 — time-aware research auditability.** Look-ahead-bias control on the *signal-formation* side (T-1 alignment of features) is enforced by 03a; Section 3b's role is the parallel control on the *label-formation* side: targets use forward data only, every target row records the precise window it measured, and the canonical null-vs-no-row taxonomy in §6.5 governs absence vs. row-with-NULL semantics. No target row is written for `(e, T)` pairs whose required forward window exceeds the snapshot's `price_table_max_as_of_date` or extends past the ETF's `delisted_date(e)` (both Bucket 1 absence cases per §6.5).
- **Section 2 v1.0 — adjusted-close convention.** `adjusted_close` is the canonical research price for every target. Any use of unadjusted prices in research calculations is forbidden without explicit Approver approval and a Section 2 amendment.
- **Section 2 v1.0 — `data_snapshot_id` reproducibility anchor.** Target outputs are linked to `ops.data_snapshots` so that any target row is traceable to a specific snapshot of provider data, universe configuration, code commit, and config commit.
- **Section 3a v1.0 — eligibility-row omission contract, T-1 trading-day semantics, no-fallback-to-secondary-benchmark, `data_snapshot_id` reproducibility chain, `feature_run_issues` issue-log pattern.** Section 3b adopts the parallel patterns for targets: rank-ineligible / out-of-lifecycle pairs are absent from `targets.target_values` (not stored with a flag); trading-day semantics are used everywhere a window is counted; the Family 4 index-only-benchmark rule is inherited for excess-return targets; the `data_snapshot_id → target_run_id → target_value` chain mirrors 03a's; `targets.target_run_issues` is the target-layer issue log inside the `targets` schema (deliberately separate from the ingestion-owned `ops.data_quality_exceptions` framework, exactly as 03a's `features.feature_run_issues` is).

---

## 2. Relevant SDR decisions

03b directly implements or respects:

- **Decision 1 — Project Scope and Phase 1 Boundaries.** ETF-only; no fundamentals, holdings, news, earnings, options, individual stocks, or autonomous research agents in any 03b target.
- **Decision 2 — Data Provider and Provider-Switching Strategy.** No `targets/` module calls EODHD or any provider-specific library directly. All inputs flow through Postgres, populated by `ingestion/` per Section 2. Adjusted-close is canonical; raw OHLCV is not used in any target.
- **Decision 3 — ETF Universe and Eligibility Rules.** Targets are computed only for ETFs that are rank-eligible per `universe.etf_eligibility_history` as of signal date `T`. The 2-year eligibility floor is enforced via the same eligibility-history view 03a uses. **03b does not write `targets.target_values` rows for ETF/date pairs that are not rank-eligible per `universe.etf_eligibility_history` as of signal date `T`** — ineligible rows are absent from the target surface, not stored with a flag.
- **Decision 4 — Universe Survivorship and ETF Launch-Date Handling.** **No `targets.target_values` row is written** for `(e, T)` where `T < first_traded_date(e)` or `T >= delisted_date(e)`. Additionally, no row is written when ETF `e` is delisted before the required `exit_date(e, T, h)` or when the required forward window exceeds the snapshot's `price_table_max_as_of_date` (both Bucket 1 absence cases per the canonical §6.5 taxonomy); see *Edge cases* below. Replacement-ETF semantics (`replacement_etf_id` on `universe.etfs`) are not consulted by 03b; replacement is a Section 5 portfolio concern.
- **Decision 5 — Benchmark, Sleeve, and Diversifier Treatment.** Excess-return targets resolve the benchmark via `universe.etfs.primary_benchmark_id → universe.benchmarks.etf_id`. The Section 3a interim ETF-backed-benchmark constraint applies: when the primary benchmark resolves index-only, excess-return targets are unavailable for that ETF/date and a `severity='warning'` row is recorded in `targets.target_run_issues`; **no silent benchmark substitution; no fallback to `secondary_benchmark_id`** in Phase 1 03b.
- **Decision 6 — Target Design and Ranking Objective.** Dual-target framework (regression + classification) at 63 and 126 trading-day horizons. The combined-score formula and the integration of expected excess return, calibrated probability, risk score, and trend confirmation are owned by 03c (forward reference); 03b produces the raw labels.
- **Decision 7 — Validation, Calibration, and Backtest Confidence Level.** 03b records per-target metadata (signal_date `T`, horizon, entry_date, exit_date) sufficient for Section 4's walk-forward harness to apply purge/embargo discipline at the overlapping-label boundary. 03b does **not** implement purge/embargo itself.
- **Decision 11 — Model Tracking, Attribution, Data Quality, and Lightweight MLOps.** Target-run metadata is anchored to `ops.data_snapshots` per Section 2's reproducibility contract. **`ops.data_quality_exceptions` remains ingestion-owned per Section 2 v1.0 LOCKED — 03b does not write to that table or any `ops.*` table.** Target-layer data-quality issues land in `targets.target_run_issues`.
- **Decision 16 — Phase 1 Success Criteria and Bias Controls.** Section 1 invariant 7 (time-aware research auditability) cashes out at the label level by 03b: forward-data-only labeling (no use of T-1 or earlier in the label itself); per-target window metadata (entry_date / exit_date) supporting Section 4's purge/embargo; data-snapshot reproducibility at the target-run level with row-level traceability; survivorship gating producing absence of rows for ineligible / out-of-lifecycle / forward-unobservable pairs.

03b does **not** implement the following SDR decisions in any form: Decisions 8 (transaction costs — Section 4), 9 (regime — Sections 3 (computation outside 03b) and 4 (consumption)), 10 (portfolio rules — Section 5), 12 (model promotion gates — 03c for the model state column; Sections 4 and 5 for the gate evaluation), 13 (LLM advisory — process), 14 (Danelfin — deferred), 15 (broker strategy — Section 5), 17 (UI — Section 6), 18 (deployment — Section 1).

---

## 3. In scope

03b covers the following at the specification level:

- **Target families** for Phase 1, defined as named target labels with formula-level descriptions, horizons, and inputs (the formal list is in *Data contracts → Target families* below):
  - Regression family: `excess_return_63d`, `excess_return_126d`.
  - Classification family: `outperformance_63d`, `outperformance_126d`.
- **Target alignment rules** ensuring every target on signal date `T` uses only forward-looking `prices.etf_prices_daily` rows for both the ETF and its primary benchmark; the precise entry/exit convention is **Convention B** (entry at `T+1` close, exit at `T+1+h` close), Approver-resolved per §11.6 #1.
- **Eligibility-row omission contract** (inherited from 03a) ensuring `targets.target_values` rows are written **only** for ETF/date pairs that are rank-eligible per `universe.etf_eligibility_history` as of signal date `T`, lie within ETF lifecycle bounds, are not delisted before the required `exit_date`, and whose required forward window does not exceed the snapshot's `price_table_max_as_of_date` (the full Bucket 1 absence-condition list is canonical in §6.5).
- **Adjusted-close usage** as the canonical research price across all target computations; raw OHLCV is not used in any 03b target.
- **Benchmark resolution for excess-return targets** sourced from each ETF's `primary_benchmark_id` per Section 2's `universe.etfs` schema, with the ETF-backed-benchmark interim constraint inherited from 03a.
- **`targets.*` schema requirements** at the spec level (table shapes, key columns, constraints, indexes). Concrete migration filenames continuing from Section 2's `0001_initial_setup.sql` and Section 3a's `features.*` migration are assigned at module-build time, not in this spec.
- **`config/targets.yaml`** structure, validation rules, and version-tracking convention (owned by 03b per §11.6 #7; no Section 1 amendment proposed).
- **`data_snapshot_id` linkage** at the target-run level, with row-level traceability via `target_run_id` (mirroring 03a).
- **Per-target-row window metadata** (signal_date, horizon_trading_days, entry_date, exit_date) sufficient for Section 4's purge/embargo logic to consume without re-deriving the windows.
- **Target persistence** (not on-the-fly computation) as the Phase 1 default per §11.6 #5 (Approver-resolved). Every target row is materialized in `targets.target_values`; downstream consumers (03c, Section 4) query the table.
- **Required tests** for each target family, including known-input / known-output tests, forward-data-only tests, no-T-1-leakage tests, eligibility / lifecycle / forward-observability tests, no-provider-import tests, `data_snapshot_id` linkage tests, classification-from-regression consistency tests, and `targets.target_run_issues` write/query tests.
- **Edge cases and failure behavior** at the target level (forward window not observable, ETF delisted within forward window, benchmark gaps in forward window, non-overlapping ETF/benchmark trading history in forward window, index-only benchmark, invalidated snapshot, partial/failed ingestion runs).

---

## 4. Out of scope

The following are **not** owned by 03b; they are owned by the sections and phases noted:

- **Feature engineering** (ETF features, regime-side feature primitives, the `features.*` schema, `config/features.yaml`) — **Section 3a** (locked).
- **Baseline model implementations, calibration pipeline, MLflow writer-side integration, model registry schema (`models.*`), model state lifecycle (Active/Warning/Paused/Retired), allowed values for `rank_method`, combined-score formula, dual-target integration into ranking, `config/model.yaml`** — **03c**.
- **Walk-forward harness, purge/embargo enforcement (the 126-day embargo per SDR Decision 7), transaction-cost application, backtest result evaluation, attribution storage tables, regime reporting layer** — **Section 4**.
- **Portfolio rules, BUY/HOLD/TRIM/SELL/REPLACE/WATCH actions, paper portfolio state, broker-neutral order intent** — **Section 5**.
- **Dash UI screens, including any UI surface that visualizes targets** — **Section 6**.
- **New data providers** beyond the EODHD adapter Section 2 implements — out of scope per Approver direction (Section 2 v1.0 LOCKED).
- **Live trading or broker integration** — out of scope per SDR Decisions 1, 15, 18 and Section 1 invariant 2.
- **Fundamentals, ETF holdings, news, earnings transcripts, options data, Danelfin, individual stocks, autonomous research agents, commercial / customer-facing features** — out of scope per SDR Decision 1.
- **Modifications to Section 1 v1.0 LOCKED architectural invariants, Section 2 v1.0 LOCKED constraints, or Section 3a v1.0 LOCKED conditions on subsequent sections** — any such modification requires the corresponding section's amendment with Approver approval per EW §3.3 and §2.3.
- **Use of unadjusted prices in any 03b target calculation** — forbidden by the Section 2 v1.0 adjusted-price convention without explicit Approver approval and a Section 2 amendment.
- **Walk-forward purge/embargo masks, train/test boundary masks, overlapping-label-aware sample weights** — Section 4. 03b *records the metadata Section 4 needs*; it does not compute the masks.
- **Cross-sectional target transforms** (e.g., cross-sectional rank of `excess_return_63d` within sleeve) — out of 03b scope per the same separation of concerns 03a applied to features (raw values stored; cross-sectional transforms are consumption-time choices in 03c if and when adopted).

---

## 5. Inputs and outputs

### 5.1 System inputs to `targets/`

- **`prices.etf_prices_daily`** — `adjusted_close` is the canonical price input; `(etf_id, as_of_date)` is the primary research key. `provider_name`, `provider_symbol`, and `ingestion_run_id` are read where needed for lineage and for filtering against partial / failed runs.
- **`universe.etfs`** — `etf_id`, `current_ticker`, `primary_benchmark_id`, `secondary_benchmark_id` (read-only — not used by Phase 1 03b unless explicitly added; the no-fallback rule applies), `sleeve_id` (read-only — not used by Phase 1 03b targets, but available for future sleeve-conditional targets under amendment), `inception_date`, `first_traded_date`, `eligible_start_date`, `active`, `delisted_date`, `replacement_etf_id` (read-only — not consulted by 03b for replacement semantics).
- **`universe.etf_eligibility_history`** — canonical for the actual eligibility timeline; consulted via the Section 2 as-of-date SQL view to determine whether an ETF is rank-eligible on a given signal date.
- **`universe.benchmarks`** — `benchmark_id`, `etf_id` (the benchmark's backing ETF, when present), `index_symbol` (when the benchmark is index-only), `display_name`. Used to resolve each ETF's `primary_benchmark_id` to a price series for excess-return targets.
- **`ops.data_snapshots`** — pinned, reproducible data set for a target run. The reproducibility anchor. The snapshot's `price_table_max_as_of_date` is the operative upper bound for forward-window observability **at the row level**: a target row for `(e, T, h)` is producible only when the required `exit_date` lies within `price_table_max_as_of_date`. Signal dates whose required forward window exceeds this bound produce **no rows** (row-level absence pattern); they do **not** cause the target run to fail. **Run-level blocking** is reserved for the snapshot's `status='invalidated'` (per Section 2 invalidation semantics) — see *Required tests* and §6.3 for the lifecycle.
- **`ops.ingestion_runs`** — read by 03b only to verify that the ingestion runs *covering the snapshot's actual price data* are not `status='failed'` and (Phase 1 default) not `status='partial'`. **Failed and partial ingestion runs covering the snapshot's price data are run-level blocking conditions.** The scope of the dependency check is the price data the snapshot actually contains, not a hypothetical extension out to `T_max + max_horizon`; the front-edge of the price data is governed by the row-level observability gate above (per §6.3). Per-symbol-aware partial handling via `chunk_results` is explicitly **not** in 03b scope (mirroring 03a).
- **`config/targets.yaml`** — target parameters, owned by 03b (per the Approver-resolved default in §11.6). Version-tracked via `target_set_version`.
- **`config/universe.yaml`** — read only via Section 2's loaded universe structures (not directly by 03b). 03b does not modify or interpret the `pending_section_3` `rank_method` sentinels — 03c owns that closure.
- **`features.feature_values` / `features.feature_runs`** — **not consumed by 03b for target generation.** Section 3b's targets are pure forward-return labels derived from prices and benchmark resolution; they do not depend on feature values. The Section 3a approval note §4.4 failed-run consumption discipline therefore applies *vacuously* to 03b's target-generation code paths and binds 03c when 03c joins features and targets for model training. See §11.3 *Derived from Section 3a*.

### 5.2 System outputs from `targets/`

- **`targets.target_runs`** — one row per target run; the reproducibility anchor on the writer side.
- **`targets.target_definitions`** — one row per target for the active `target_set_version`; the catalog of what targets exist, their formula descriptions, horizons, and inputs.
- **`targets.target_values`** — long-form `(etf_id, as_of_date, target_name, target_set_version, target_run_id, horizon_trading_days, entry_date, exit_date, target_value)` rows; the actual target surface consumed by 03c and Section 4.
- **`targets.target_run_issues`** — target-layer issue log. One row per target-run-level data-quality event (index-only-benchmark inability, blocked invalidated snapshot, blocked failed/partial ingestion-run dependency, failed target run). Schema and semantics defined in §6.6. **This is a target-layer issue log, not the Section 2 `ops.data_quality_exceptions` framework.**
- **`ops.data_quality_exceptions`** *(read-only from 03b's perspective; not written by 03b)* — per Section 2 v1.0 LOCKED, `ingestion/` is the only emitter. **03b does not write to `ops.data_quality_exceptions`.**

03b writes **only** to the `targets` schema (`target_runs`, `target_definitions`, `target_values`, `target_run_issues`). 03b does **not** write to `universe.*`, `prices.*`, **any `ops.*` table** (read-only), `features.*` (03a-owned), `models.*` (03c), MLflow, or any provider table. 03b does **not** write to MLflow.

### 5.3 Module-level input/output summary

| Module (within `targets/`) | Reads | Writes |
|---|---|---|
| Configuration loader | `config/targets.yaml` (via `common/`) | (none) |
| Snapshot validator | `ops.data_snapshots`, `ops.ingestion_runs` | `targets.target_run_issues` on invalidated/failed/partial-run conditions |
| Target catalog initializer | `config/targets.yaml`, `targets.target_runs` | `targets.target_definitions` |
| Excess-return calculator (regression) | `prices.etf_prices_daily`, `universe.etfs`, `universe.etf_eligibility_history`, `universe.benchmarks` | `targets.target_values` (regression family); `targets.target_run_issues` on index-only-benchmark conditions |
| Outperformance calculator (classification) | `targets.target_values` rows produced by the regression calculator within the same run, OR direct re-computation from `prices.etf_prices_daily` (implementation choice — see §11.4) | `targets.target_values` (classification family) |
| Target-run orchestrator | All of the above | `targets.target_runs` (open / close), `targets.target_values` (in transactional batches per §6.5 atomicity contract); `targets.target_run_issues` for run-level conditions |

No 03b module writes to `ops.data_quality_exceptions` or any other `ops.*` table. All target-layer data-quality issues land in `targets.target_run_issues` per §6.6.

---

## 6. Data contracts

### 6.1 Target alignment rule (forward-window semantics)

**Definition of `T`, `entry_date`, and `exit_date`.** `T` is the **signal date** — the calendar date for which a target row is produced and stamped (`targets.target_values.as_of_date = T`). `T` must be a valid trading day for the relevant ETF (and, where applicable, its benchmark): there must be a `prices.etf_prices_daily` row with `as_of_date = T` for both. The target's measurement window is bounded by the per-target `entry_date` and `exit_date`, which are recorded on every row.

**Per Convention B (Approver-resolved per §11.6 #1):** for signal date `T` and horizon `h` (counted in trading days), the entry date is **`T+1`** (the trading day immediately following the signal date for the relevant ETF, per the same trading-day index 03a's `T-1` uses), and the exit date is **`T+1+h`** (the trading day exactly `h` trading days after the entry date for the relevant ETF). Both endpoints are recorded explicitly in `targets.target_values.entry_date` and `targets.target_values.exit_date` so Section 4's purge/embargo logic does not have to re-derive them.

**Trading-day arithmetic, not calendar arithmetic.** All offsets (`T+1`, `T+1+h`) are counted by walking forward through `prices.etf_prices_daily` rows for the relevant ETF; weekends, holidays, and any other days on which the ETF has no price row are skipped. This is the parallel of 03a's T-1 trading-day semantics applied to the forward direction. Cross-series alignment (between an ETF and its benchmark, where applicable) is resolved independently against each series' own trading-day index. Per the canonical §6.5 taxonomy, the cross-series outcome splits into two cases: (i) if either series' required forward window exceeds the snapshot's `price_table_max_as_of_date`, **no row is written** (Bucket 1 — front-edge truncation); (ii) if both series' windows fall inside snapshot coverage but one or both series have missing or non-overlapping trading-day rows inside the window, **a row is written with `target_value = NULL`** (Bucket 2).

**No use of T-1 or earlier in the target value itself.** The label measures returns over `[entry_date, exit_date]` only. It does not consult prices on `T-1` or earlier (those are the feature side, owned by 03a). This is the parallel control to 03a's no-T-and-later look-ahead control: 03a's features are bounded by `as_of_date <= T-1`; 03b's targets are bounded by `as_of_date >= T+1` in their value calculation. Together they ensure no overlap between feature inputs and target inputs at the same signal date.

**Consequences:**

- For any signal date `T` and any target, the inputs to that target's value are bounded by `prices.etf_prices_daily.as_of_date >= T+1` for the relevant ETF (and, for excess-return targets, also for the benchmark ETF, with `entry_date` and `exit_date` evaluated independently against each series' own trading calendar).
- All horizon counts (`h` trading days) in §6.2 are **trading-day** counts walked forward through `prices.etf_prices_daily` rows for the relevant ETF.
- The target row is stamped with `as_of_date = T` (the signal date), but its value computation uses only data available on or after `entry_date`.
- The trading-calendar semantics themselves are owned by Section 2 (the set of dates with rows in `prices.etf_prices_daily` is the operative trading calendar), exactly as for 03a.

This is the principal cash-out of SDR Decision 16's look-ahead-bias control on the **label-formation side** at the target level. The trading-day semantics are tested for weekend and holiday boundaries (per §8.2) so that "T+1 = calendar T + 1" is never silently assumed.

### 6.2 Target families (Phase 1)

The Phase 1 target set is defined here at the formula and horizon level. All formulas use Convention B per §11.6 #1 (Approver-resolved). The schema's `entry_offset_trading_days` and `exit_offset_trading_days` columns on `targets.target_definitions` make the convention explicit at the row level so a future amendment that introduces an alternative convention (e.g., Convention A: entry at `T`, exit at `T+h`) can be absorbed without further schema modification; current 03b scope does not enable any other convention and the YAML validator (§7.2) refuses any value other than `"B"`.

For all formulas below, `adj_close(e, d)` denotes `prices.etf_prices_daily.adjusted_close` for `etf_id = e` on `as_of_date = d`. Trading days are calendar days on which `prices.etf_prices_daily` has rows for the relevant ETF (Section 2 owns the trading-calendar semantics).

#### Regression family — Forward excess return

**Target names (Phase 1):** `excess_return_63d`, `excess_return_126d`.

**Formula (horizon `h`, signal date `T`, ETF `e` with primary benchmark backed by ETF `b`, Convention B):**

```
return_h(e, T)        = adj_close(e, T+1+h) / adj_close(e, T+1) - 1
return_h(b, T)        = adj_close(b, T+1+h) / adj_close(b, T+1) - 1
excess_return_h(e, T) = return_h(e, T) - return_h(b, T)
```

**Inputs:** `prices.etf_prices_daily.adjusted_close` for both `e` and `b`; `universe.etfs.primary_benchmark_id`; `universe.benchmarks.etf_id`.

**Per-row window metadata recorded:**

- `signal_date = T`
- `horizon_trading_days = h`
- `entry_date = T+1` (per ETF `e`'s trading-day index)
- `exit_date = T+1+h` (per ETF `e`'s trading-day index)

The benchmark's own `T+1` and `T+1+h` may differ from the ETF's if the two series have different trading calendars (rare for US-listed ETFs but possible). Cross-series alignment per §6.1 applies, splitting per the §6.5 taxonomy: if either series' required forward window exceeds the snapshot's `price_table_max_as_of_date`, **no row is written** (Bucket 1); if both windows fall inside snapshot coverage but a series has missing or non-overlapping trading-day rows inside its window, **a row is written with `target_value = NULL`** (Bucket 2).

**Index-only benchmark behavior (inherited from 03a §6.2.4).** This family is computed **only** when the primary benchmark resolves to an ETF-backed benchmark with a non-null `etf_id` and adjusted-close history covering the required forward window. When the primary benchmark is index-only (`universe.benchmarks.index_symbol` set, `etf_id` null), a **row IS written** for that `(e, T, h)` with `target_value = NULL`, and a `severity='warning'` row is recorded in `targets.target_run_issues` with `issue_type='index_only_benchmark'`. **No silent benchmark substitution is permitted. No fallback to `secondary_benchmark_id`.** This is the row-with-NULL bucket of the canonical null-vs-no-row taxonomy in §6.5. The structural gap remains §10.1 (residual Open Question for Approver — possible future Section 2 amendment for benchmark price storage). The interim behavior itself is an Approver-resolved default (§11.6 #6).

#### Classification family — Outperformance flag

**Target names (Phase 1):** `outperformance_63d`, `outperformance_126d`.

**Formula (horizon `h`, signal date `T`, classification threshold `θ = 0.0` Approver-resolved per §11.6 #2):**

```
outperformance_h(e, T) = 1 if excess_return_h(e, T) > θ else 0
                       = NULL if excess_return_h(e, T) is NULL
```

**Inputs:** `excess_return_h(e, T)` from the regression family for the same `(e, T, h)`.

**Per-row window metadata recorded:** identical to the regression target with the same horizon (`signal_date`, `horizon_trading_days`, `entry_date`, `exit_date`), so the classification row carries the same window metadata Section 4 needs.

**Definition of "outperformed":** Phase 1 03b uses `θ = 0` (strict positive excess return); see §11.6 #2 (Approver-resolved default).

**Null propagation.** When the underlying regression target is `NULL` for any §6.5 Bucket 2 reason (missing input bar inside an otherwise coverable forward window, missing or non-overlapping benchmark trading-day history inside an otherwise coverable forward window, index-only benchmark, etc.), the classification target row is **also written with `target_value = NULL`** — it is **not** absent. The classification target is **not** re-derived independently from prices; it is computed from the regression target within the same run. This avoids divergence between the two families on edge cases. **No-row** cases on the regression side (Bucket 1: ineligibility, lifecycle bounds, ETF delisted before required `exit_date`, forward window exceeds snapshot coverage) likewise produce **no classification row** — the classification family inherits both buckets of the §6.5 taxonomy from the regression family.

### 6.3 `targets.target_runs`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `target_run_id` | `bigserial` | PK | surrogate key |
| `data_snapshot_id` | `bigint` | not null, FK → `ops.data_snapshots` | reproducibility anchor |
| `target_set_version` | `text` | not null | matches `config/targets.yaml` `target_set_version` |
| `commit_hash` | `text` | not null | code commit at run start |
| `config_hash` | `text` | not null | hash of `config/targets.yaml` at run start |
| `started_at_utc` | `timestamptz` | not null default `now()` | |
| `completed_at_utc` | `timestamptz` | nullable | |
| `status` | `text` | not null, CHECK in (`'running'`, `'succeeded'`, `'failed'`) | |
| `error_message` | `text` | nullable | populated on `'failed'` |
| `created_by` | `text` | not null | container or user identifier |
| `notes` | `text` | nullable | free-form |
| | | **UNIQUE (`target_run_id`, `target_set_version`)** | enables the composite FK from `targets.target_values` defined in §6.5 (parallel to 03a §6.3) |

Index on `data_snapshot_id` to support reproducibility queries.

The `UNIQUE (target_run_id, target_set_version)` constraint is functionally redundant with the PK on `target_run_id` but is required as a constraint object so PostgreSQL accepts the composite foreign key from `targets.target_values(target_run_id, target_set_version)` referencing it. This is the same standard pattern 03a established for `features.feature_runs`.

**Blocked-run lifecycle (parallel to 03a §6.3).** The target-run orchestrator opens the `targets.target_runs` row (with `status='running'`) **before** validating the selected `data_snapshot_id`, the snapshot's `status`, and the ingestion-run dependencies covering the snapshot's actual price data. The **closed list of run-level blocking conditions** is:

1. The selected snapshot has `status='invalidated'`.
2. Any ingestion run covering the snapshot's price data has `status='failed'`.
3. (Phase 1 default) Any ingestion run covering the snapshot's price data has `status='partial'`.

If any of these is detected, the orchestrator (a) marks the run row `status='failed'`, (b) populates `error_message` and `completed_at_utc`, (c) writes the appropriate `targets.target_run_issues` row (FK satisfied because the run row is already open), and (d) writes **no** `targets.target_values` rows for that run.

**Front-edge truncation is NOT a run-level blocking condition.** A snapshot whose `price_table_max_as_of_date` is *less than* the required `exit_date` for some signal dates `T` simply produces **no rows** for those `(e, T, h)` combinations (row-level absence pattern, parallel to the eligibility-row omission contract in 03a). The run may still complete with `status='succeeded'` provided no run-level blocking condition is hit and at least some eligible rows are produced. **No `targets.target_run_issues` warning row is required for front-edge truncation in current 03b scope** unless the Approver later directs otherwise (per §11.6 #10). The implicit "would have been labeled but weren't due to front-edge truncation" set is derivable by an operator from comparing the eligible signal-date set to the produced signal-date set; current 03b scope does not formalize this as an `issue_type`.

### 6.4 `targets.target_definitions`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `target_set_version` | `text` | not null | |
| `target_name` | `text` | not null | e.g., `excess_return_63d` |
| `family` | `text` | not null | one of `regression_excess_return`, `classification_outperformance` |
| `formula_description` | `text` | not null | plain-English formula reference |
| `horizon_trading_days` | `integer` | not null | trading-day forward horizon |
| `entry_offset_trading_days` | `integer` | not null | `1` for Convention B (Approver-resolved per §11.6 #1); reserved column to absorb any future Approver-approved alternative convention without schema migration |
| `exit_offset_trading_days` | `integer` | not null | `entry_offset + horizon` |
| `inputs_described` | `text` | not null | summary of which columns / tables are read |
| `parameters` | `jsonb` | nullable | family-specific parameters (e.g., classification threshold `θ`) |
| | | PK (`target_set_version`, `target_name`) | |

Populated at orchestrator startup by reading `config/targets.yaml` for the active version. Existing rows for prior `target_set_version` values are retained for audit; only the active version is consulted by target-value writes. The `entry_offset_trading_days` and `exit_offset_trading_days` columns make the convention explicit at the row level so future amendments that introduce mixed conventions are unambiguous.

### 6.5 `targets.target_values`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `etf_id` | `bigint` | not null, FK → `universe.etfs` | |
| `as_of_date` | `date` | not null | signal date `T` |
| `target_name` | `text` | not null | matches `targets.target_definitions.target_name` |
| `target_set_version` | `text` | not null | matches `targets.target_runs.target_set_version` for the linked run; participates in both composite FKs below |
| `target_run_id` | `bigint` | not null | participates in the composite FK to `targets.target_runs` below; the legacy single-column FK on `target_run_id` alone is **not** declared |
| `horizon_trading_days` | `integer` | not null | denormalized from `target_definitions` for query convenience and Section 4 consumption |
| `entry_date` | `date` | not null | actual trading day used as the entry per the relevant ETF's trading-day index |
| `exit_date` | `date` | not null | actual trading day used as the exit per the relevant ETF's trading-day index |
| `target_value` | `numeric(24,12)` | nullable | null permitted for the §6.5 Bucket 2 cases only: missing input bar inside an otherwise coverable forward window, non-overlapping benchmark forward history inside an otherwise coverable forward window, index-only-benchmark cases, and classification rows whose underlying regression value is NULL (see *Nullable-value semantics* below) |
| | | PK (`etf_id`, `as_of_date`, `target_name`, `target_run_id`) | `target_set_version` is determined by `target_run_id` |
| | | Composite FK (`target_run_id`, `target_set_version`) → `targets.target_runs(target_run_id, target_set_version)` | parallel to 03a §6.5; database-level enforcement of `target_set_version` consistency |
| | | Composite FK (`target_set_version`, `target_name`) → `targets.target_definitions(target_set_version, target_name)` | parallel to 03a §6.5; ensures every value row corresponds to a catalogued target in the active version |

Indexes:
- `(target_run_id)` for run-scoped queries (audit, idempotency checks, exclusion of failed-run rows).
- `(etf_id, as_of_date)` for primary research queries.
- `(target_name, as_of_date)` for cross-sectional research queries.
- `(as_of_date)` for time-slice queries.
- `(exit_date)` for Section 4's overlapping-label / purge-embargo queries (the maximum `exit_date` minus the minimum next-fold `entry_date` is the natural quantity the harness needs).

**Null-vs-no-row taxonomy (canonical).** The set of conditions on which `targets.target_values` does or does not produce a row, and whether the produced row carries a non-null `target_value` or `target_value = NULL`, is divided into two disjoint buckets. All other §6 / §8 / §9 / §11 references defer to this taxonomy.

**Bucket 1 — No row is written for `(e, T, h)` when:**

- `(e, T)` is not rank-eligible per `universe.etf_eligibility_history` resolved as of signal date `T` (Section 2 as-of-date SQL view);
- `T < first_traded_date(e)`;
- `T >= delisted_date(e)`;
- `delisted_date(e) <= exit_date(e, T, h)` — the ETF delists before the required forward exit date (the `forward_window.delisted_within_window_rule = "no_row"` Approver-resolved default per §11.6 #4);
- `exit_date(e, T, h)` (or, for excess-return targets, `exit_date(b, T, h)` for the benchmark ETF `b`) exceeds the snapshot's `price_table_max_as_of_date` — the forward window exceeds snapshot coverage (front-edge truncation).

These cases are **absences** in the target surface, parallel to 03a's eligibility-row omission contract. They do not produce a `target_value = NULL` row and do not produce a `targets.target_run_issues` row in current 03b scope.

**Bucket 2 — A row is written with `target_value = NULL` for `(e, T, h)` when:**

- a missing input price bar exists inside an otherwise coverable forward window for ETF `e` (`missing_data.rule = "null_on_any_missing_input_in_window"` Approver-resolved default per §11.6 #3);
- benchmark history is missing or non-overlapping inside an otherwise coverable forward window (excess-return family only; "otherwise coverable" means both the ETF's and the benchmark's required `entry_date` and `exit_date` fall inside the snapshot's `price_table_max_as_of_date` — the front-edge-truncation case where one or both series' window exceeds snapshot coverage is Bucket 1, not Bucket 2; see §6.1 for the split);
- the primary benchmark resolves index-only on signal date `T` (per §6.2 regression family; an additional `severity='warning'` row with `issue_type='index_only_benchmark'` is recorded in `targets.target_run_issues`; the classification family writes a row with `target_value = NULL` by null propagation per §6.2);
- the classification target's underlying regression target is `NULL` (null propagation per §6.2 — applies when the regression row is in Bucket 2 only; if the regression row is in Bucket 1, the classification row is also in Bucket 1).

**Atomicity contract (parallel to 03a §6.5).** Target runs may write `targets.target_values` **in transactional batches** rather than in one massive transaction; the natural batch unit is a (calculator, ETF, signal-date-window) tuple, with the exact batching strategy a module-build-time choice. **Failed target runs may retain partial `targets.target_values` rows** (rows from batches that committed before the failure). Downstream consumers — 03c, Section 4 — must **only consume `targets.target_values` rows whose `target_run_id` links to a `targets.target_runs.status='succeeded'` row**. Consumption discipline is enforced by §8.2 cross-cutting tests; the schema deliberately does not delete partial rows on failure (the run row carries the truth via `status`).

The PK includes `target_run_id` so successive runs against the same snapshot are append-only and distinguishable; idempotency is verified by comparing values across two `'succeeded'` runs sharing the same `data_snapshot_id`, `target_set_version`, `commit_hash`, and `config_hash` — see *Required tests*.

### 6.6 `targets.target_run_issues`

This is the **target-layer issue log**, parallel to 03a's `features.feature_run_issues` and introduced for the same reasons. **It is not the Section 2 `ops.data_quality_exceptions` framework**; that framework remains ingestion-owned per Section 2 v1.0 LOCKED. The two are deliberately separate.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `target_run_issue_id` | `bigserial` | PK | surrogate key |
| `target_run_id` | `bigint` | not null, FK → `targets.target_runs(target_run_id)` | which run produced the issue |
| `issue_type` | `text` | not null, CHECK in (`'index_only_benchmark'`, `'invalidated_snapshot_blocked'`, `'failed_ingestion_run_blocked'`, `'partial_ingestion_run_blocked'`, `'target_run_failed'`) | closed enumeration; new types require an 03b amendment |
| `severity` | `text` | not null, CHECK in (`'warning'`, `'fail'`) | `'warning'` for index-only-benchmark; `'fail'` for the four blocking conditions |
| `etf_id` | `bigint` | nullable, FK → `universe.etfs` | populated when the issue is per-ETF; null for run-level issues |
| `as_of_date` | `date` | nullable | signal date the issue applies to, when applicable; null for run-level issues |
| `affected_target_name` | `text` | nullable | target name the issue applies to, when applicable (e.g., `excess_return_63d`); null for run-level issues |
| `summary` | `text` | not null | short, structured summary suitable for UI display |
| `detail` | `jsonb` | nullable | structured detail (e.g., the offending `benchmark_id`, the `ingestion_run_id` that blocked the run, the failure exception message); free-form within the closed `issue_type` |
| `created_at_utc` | `timestamptz` | not null default `now()` | |

Indexes:
- `(target_run_id)` for run-scoped issue queries.
- `(issue_type)` for type-scoped queries.
- `(etf_id, as_of_date)` for ETF/date-scoped queries (sparse — many rows have null in these columns).

**Scope and write discipline.**

- **Lifecycle integration with `targets.target_runs`.** Every `targets.target_run_issues` row references a real `targets.target_runs` row through the NOT NULL FK on `target_run_id`. Per the §6.3 blocked-run lifecycle, the orchestrator opens the `targets.target_runs` row (status `'running'`) **before** validating the snapshot and ingestion-run dependencies, so on a block detection the orchestrator can mark the run `'failed'` and write the issue row in the same transactional sequence. There is no scenario in 03b in which a `target_run_issues` row exists without a corresponding `target_runs` row. The FK is never relaxed.
- 03b writes to `targets.target_run_issues` directly via `common/` database helpers, **not** through the `common.redact_secrets()` utility's exception path (that utility is reserved for `ops.data_quality_exceptions` and `ops.provider_raw_payloads` per Section 2). 03b's `summary` and `detail` fields are written by 03b code from already-internal target-layer state (snapshot IDs, ingestion run IDs, benchmark IDs, exception messages produced inside `targets/`); they do not embed provider-derived text or response fragments, so the Section 2 redaction utility does not apply.
- The closed enumeration on `issue_type` ensures adding a new issue type is a deliberate spec change, not an ad-hoc string. New types are added under 03b amendments.
- No 03b code path writes to `ops.data_quality_exceptions` under any circumstance (verified by §8.2 test #34, the parallel of 03a's no-write-to-`ops.*` static check).
- A future Section 2 amendment that opens `ops.data_quality_exceptions` to feature/target-level emitters would be a separate decision out of 03b scope.

**Consumption.**

- Section 6 UI Model Registry / Run Browser surfaces (read-only) display these issues alongside the `target_runs` they belong to.
- 03c may read `target_run_issues` to filter or annotate model runs that depend on a target run.
- Section 4 backtest harness may surface these issues in run reports.

### 6.7 `data_snapshot_id` linkage

Mirroring 03a §6.8, 03b uses **run-level linkage** with **row-level traceability**:

- **Run-level:** `targets.target_runs.data_snapshot_id` is the canonical anchor.
- **Row-level:** `targets.target_values.target_run_id` is the foreign key that traces every target row to its run, and via the run to its `data_snapshot_id`.

The snapshot's `price_table_max_as_of_date` field (per Section 2 v1.0 LOCKED) is the operative upper bound for **row-level** forward-window observability: a target row for `(e, T, h)` is producible only when the required `exit_date` for that `(e, T, h)` falls within `price_table_max_as_of_date` (Convention B refines this to `T + 1 + h <= price_table_max_as_of_date` for the relevant ETF, evaluated against its own trading-day index). Signal dates whose required forward window exceeds this bound produce **no rows** (Bucket 1 of §6.5). This is **row-level** absence, not a run-level blocking condition; the run may still succeed if at least some eligible rows are produced.

This satisfies the EW §7 reproducibility list at the schema-shape level: the run row carries `commit_hash`, `config_hash`, and `data_snapshot_id`; the snapshot carries provider, dataset, universe, adjusted-price-convention, and the price-table coverage bound per Section 2 v1.0 LOCKED. The MLflow run ID itself is owned by 03c and is not stored in `targets.*`; 03c links its MLflow runs back to a `target_run_id` (forward reference).

### 6.8 Sleeve-aware target treatment

03b does **not** apply sleeve-conditional target families in Phase 1. Excess-return and outperformance targets are computed identically across all sleeves, with the per-ETF `primary_benchmark_id` (which is itself sleeve-aware per SDR Decision 5) providing the per-ETF benchmark. Future sleeve-conditional targets (e.g., a "diversifier-only" hedge target measuring SPY-relative drawdown rather than excess return) would be added under Approver-approved 03b amendments.

### 6.9 Coverage parity with 03a

For a target run with `data_snapshot_id = S` and a feature run (03a) with `data_snapshot_id = S` and the same eligibility logic applied to the same universe at the same as-of dates, the set of `(etf_id, as_of_date)` pairs in `targets.target_values` is a **subset** of the set of `(etf_id, as_of_date)` pairs in `features.feature_values`. This is because:

- Both 03a and 03b consult the same authoritative sources (`universe.etf_eligibility_history` for eligibility; `universe.etfs` for lifecycle bounds) and arrive at the same eligibility/lifecycle-passing set on the read side.
- 03b additionally applies a **row-level** *forward-window observability* gate (the snapshot's `price_table_max_as_of_date` must cover the required `exit_date` for that `(e, T, h)`), which 03a does not require. This makes 03b's set strictly smaller at the front edge of the data window (the most recent signal dates) by approximately `max_horizon` trading days. This is row-level absence — it is not a run-level blocking condition; the run may still complete `'succeeded'` (per §6.3 / §11.6 #10).

03c (forward reference) is responsible for joining `features.feature_values` and `targets.target_values` on `(etf_id, as_of_date)` to assemble training data; rows present in features but not in targets are simply not training-eligible (the target side is missing). 03c's training data assembly tests must verify this join is correct, including the front-edge truncation.

---

## 7. Config dependencies

### 7.1 `config/targets.yaml`

03b owns a new file `config/targets.yaml`. This is **strategy-affecting** config per EW §7 (it defines target horizons and the classification threshold, which directly change what the model is trained against). Any change requires Approver review per the Approval Matrix.

**File location is Approver-resolved within the 03b spec approval path (§11.6 #7).** The Approver directed:

- 03b owns `config/targets.yaml` as a new strategy-affecting config file;
- this is approved within the 03b spec approval path — **no Section 1 amendment is proposed by 03b**;
- targets config is **not** moved into `config/model.yaml`;
- 03c continues to own `config/model.yaml`;
- 03c may *read* target metadata at consumption time but does not own target config.

The Section 1 list of YAML files (six in total, enumerated in Section 1's *Config dependencies*) is not modified by 03b. The 03b approval will record `config/targets.yaml` as an additional strategy-affecting config file owned by 03b at the spec level; integration with the Section 1 list is left to a future housekeeping pass that does not require reopening Section 1.

Phase 1 shape (Approver-resolved per §11.6):

```yaml
target_set_version: "0.1"

families:
  regression_excess_return:
    enabled: true
    horizons_trading_days: [63, 126]
    benchmark_field: primary_benchmark_id      # references universe.etfs
    require_etf_backed_benchmark: true         # interim per Section 3a §10.1; no fallback to secondary; see §11.6 #6

  classification_outperformance:
    enabled: true
    horizons_trading_days: [63, 126]
    threshold: 0.0                             # Approver-resolved per §11.6 #2
    derive_from: regression_excess_return      # classification target is computed from the regression target within the same run

alignment:
  convention: "B"                              # Approver-resolved per §11.6 #1
                                               # "B": entry T+1, exit T+1+h
                                               # (Convention "A" reserved as a future amendment path; not enabled in current 03b scope)
  trading_day_index: per_etf                   # follows the same per-ETF trading-day index 03a's T-1 uses

forward_window:
  delisted_within_window_rule: "no_row"        # Approver-resolved per §11.6 #4

missing_data:
  rule: "null_on_any_missing_input_in_window"  # Approver-resolved per §11.6 #3; aligns with 03a
                                               # any missing input bar in [entry_date, exit_date] yields a row with target_value = NULL
```

### 7.2 `config/targets.yaml` validation rules

Validated at orchestrator startup. Failure raises a structured error and the run does not start (no silent defaulting per EW §7 / Section 1's "no silent default for any field that originates in YAML"):

- `target_set_version` is a non-empty string.
- Every family key is one of the known closed set: `regression_excess_return`, `classification_outperformance`. Unknown family keys raise an error (no silent ignore).
- For each enabled family, family-specific required parameters are present and well-typed.
- All horizon values are positive integers.
- For `classification_outperformance`, `threshold` is a finite number (positive, negative, or zero) and `derive_from` is one of the enabled regression family names; if `derive_from` is set, the regression family it names is enabled and shares all required horizons.
- `alignment.convention` is `"B"` (Approver-resolved per §11.6 #1). Phase 1 03b validates that the configured value is exactly `"B"`; any other value (including `"A"`) raises a structured error. A future 03b amendment is required to enable additional conventions.
- `alignment.trading_day_index` is one of the documented allowed values; Phase 1 default is `per_etf`.
- `forward_window.delisted_within_window_rule` is `"no_row"` (Approver-resolved per §11.6 #4). Phase 1 03b validates that the configured value is exactly `"no_row"`; any other value (including `"null_with_partial_flag"`) raises a structured error. A future 03b amendment is required to enable an alternative rule.
- `missing_data.rule` is one of the documented allowed values; Phase 1 default is `"null_on_any_missing_input_in_window"`.

### 7.3 Other config dependencies

- **`config/universe.yaml`** — read indirectly via Section 2's loaded universe structures only. 03b does not read this YAML directly and does not modify it. The `pending_section_3` `rank_method` sentinels are not interpreted by 03b (forward reference: 03c closes them).
- **`config/features.yaml`** — read indirectly only if 03b wanted to align its target horizons with 03a's window choices at config-load time. Phase 1 03b does not read `config/features.yaml` directly; the alignment is documented (both sets of 63 and 126 trading-day windows align with SDR Decision 6) but not enforced via cross-file validation.
- **`.env`** — 03b introduces no new environment variables. Database credentials and connection parameters are inherited from Section 1 / Section 2's `.env` discipline.

### 7.4 Config commit discipline

Per EW §7, `config/targets.yaml` changes use commit messages of the form:

```
config(targets): [strategy-affecting] <change summary> per <SDR decision or 03b amendment reference>
```

The `config_hash` recorded on each `targets.target_runs` row is computed over `config/targets.yaml` only; the broader `config_hash` on `ops.data_snapshots` is hashed across all config files per Section 2.

---

## 8. Required tests

Tests live under `tests/unit/targets/` and `tests/integration/targets/`. All tests must run inside the application container per EW §5 (`docker compose exec app pytest tests/unit/targets/` and the integration path).

### 8.1 Per-family tests

#### Regression family — Forward excess return

1. **Known-input / known-output** — for each horizon `h in {63, 126}`, a fixture price series for ETF `e` and benchmark ETF `b` produces a hand-computed `excess_return_h` value matching to a documented tolerance, with the recorded `entry_date` and `exit_date` matching the trading-day-walk expectation under Convention B.
2. **Forward-data-only alignment** — the target on signal date `T` does not change when `prices.etf_prices_daily` rows on `as_of_date <= T` are mutated. A mutation test that injects an obviously-wrong price on `as_of_date = T-1` (or earlier) must not change `excess_return_h(e, T)` for any `h`. This is the parallel control to 03a's T-1 alignment test, applied to the label-formation side.
3. **No-T-1-leakage** — a static / source-scan check verifies that the regression calculator code path never references prices on `as_of_date <= T` for the value computation (under Convention B per §11.6 #1, the value formula reads only `T+1` and `T+1+h`). The recorded `as_of_date = T` is for indexing only, not for value computation.
4. **Survivorship and lifecycle (no row written for ineligible / out-of-lifecycle pairs)** —
   (a) **No `targets.target_values` row** is written for `(e, T)` where `T < first_traded_date(e)`.
   (b) **No `targets.target_values` row** is written for `(e, T)` where `T >= delisted_date(e)`.
   (c) **No `targets.target_values` row** is written for `(e, T)` where `etf_eligibility_history` (resolved via Section 2's as-of-date SQL view) does not return a row with `is_rank_eligible=true` covering signal date `T`.
5. **Forward-window observability gate (row-level absence).** For `(e, T)` where the required `exit_date(e, T, h)` exceeds the snapshot's `price_table_max_as_of_date`, **no `targets.target_values` row** is written for that `(e, T, h)` (Bucket 1 of §6.5). Verified by a fixture in which the snapshot's coverage ends mid-test-period; rows for signal dates whose forward window extends beyond coverage must be absent. The test additionally asserts that the run completes with `status='succeeded'` provided at least some eligible rows are produced — front-edge truncation is **not** a run-level blocking condition.
6. **ETF-delisted-within-forward-window behavior (`forward_window.delisted_within_window_rule = "no_row"`, Approver-resolved per §11.6 #4).** For `(e, T)` where `delisted_date(e)` falls within `[entry_date, exit_date]`, **no `targets.target_values` row** is written. This belongs to Bucket 1 of the §6.5 taxonomy. The alternative `null_with_partial_flag` is not enabled in current 03b scope; the YAML validator (§7.2) refuses any other value.
7. **Index-only benchmark behavior (two-part test, parallel to 03a Family 4 test #11).**
   (a) **Row written with `target_value = NULL`; no silent benchmark substitution.** When the primary benchmark has `index_symbol` set and `etf_id IS NULL`, a `targets.target_values` row IS written for `(e, T, h)` with `target_value = NULL` and `secondary_benchmark_id` is **not** consulted. The test injects a fixture ETF whose primary benchmark is index-only and whose `secondary_benchmark_id` is set to a valid ETF-backed benchmark; the assertion is that the row exists with `target_value = NULL` (Bucket 2 of §6.5), not that the row is absent, and that the value computation did not consult the secondary benchmark.
   (b) **Warning row recorded in `targets.target_run_issues`.** A row is written with `issue_type='index_only_benchmark'`, `severity='warning'`, `etf_id` set, `as_of_date` set, `affected_target_name` set, `summary` populated, and `detail` populated with the offending `benchmark_id` and `index_symbol`. **No row is written to `ops.data_quality_exceptions`** — verified by asserting that table is unchanged across the test run.
8. **Cross-series alignment (ETF vs benchmark forward windows).** When both ETF `e`'s and benchmark `b`'s required `entry_date` and `exit_date` fall inside the snapshot's `price_table_max_as_of_date` but ETF `e` has price rows on `entry_date` or `exit_date` (or any day inside the window) that the benchmark does not have (or vice versa), a `targets.target_values` row IS written for `(e, T, h)` with `target_value = NULL` (Bucket 2 of §6.5). Verified for both endpoints and for missing days within the window. The corresponding case where either series' required window exceeds snapshot coverage produces **no row** (Bucket 1) and is exercised by tests #5 and #9.
9. **Insufficient forward history — snapshot truncation (Bucket 1 — no row).** For `(e, T)` where the snapshot does not cover `exit_date(e)` or, for excess-return targets, `exit_date(b)`, **no `targets.target_values` row** is written. This consolidates with test #5 and is restated here for completeness against the §6.5 taxonomy. Verified for the ETF-only case (Family 1 not directly applicable; this test runs on the regression excess-return family, where benchmark coverage is also required). The target is **not** present with `target_value = NULL`; it is absent.
10. **Trading-day forward arithmetic — weekend / holiday boundaries** — fixture series spanning a Friday → Monday gap (no Saturday/Sunday rows) and a market-holiday gap. For signal date `T = Thursday` and horizon `h = 1`, `entry_date = Friday` and `exit_date = Monday` (skipping the weekend); the recorded `entry_date` and `exit_date` match these dates exactly. The test fails if the calculator treats `T+1` as `Friday` (calendar) when the ETF has no Friday price row.
11. **Idempotency** — same `data_snapshot_id`, same `target_set_version`, same `commit_hash`, same `config_hash` produces the same `target_value` on re-run (PK distinguishes runs but values are identical).

#### Classification family — Outperformance flag

12. **Known-input / known-output** — for each horizon `h in {63, 126}`, a fixture in which `excess_return_h(e, T)` is hand-computed to a specific positive value produces `outperformance_h(e, T) = 1`; a hand-computed negative value produces `0`; a hand-computed value of exactly `θ = 0.0` produces `0` (strict inequality `> θ`). The threshold semantics are documented and tested.
13. **Null propagation** — when the underlying `excess_return_h(e, T)` is null (any of the regression-family null cases above), `outperformance_h(e, T)` is also null and the row carries a null `target_value`.
14. **Classification-from-regression consistency** — for every `(e, T, h)` where both the regression and classification rows exist with non-null values within the same target run, the classification value equals the indicator computed from the regression value with the configured threshold. Verified across the full fixture universe.
15. **Window metadata parity** — for every `(e, T, h)`, the classification row's `signal_date`, `horizon_trading_days`, `entry_date`, `exit_date` match the corresponding regression row's exactly.
16. **Threshold sensitivity** — when `config/targets.yaml` is changed to set a non-zero threshold (e.g., `θ = 0.01`), the resulting classification values change at the boundary; values within `(0, 0.01]` flip from `1` to `0`.
17. **Survivorship, lifecycle, eligibility, forward-window, index-only-benchmark gates** — every gate that suppresses a regression row also suppresses the corresponding classification row. Verified via fixture cases that exercise each gate independently.

### 8.2 Cross-cutting tests

18. **No-provider-import test** — static check verifying that no module under `quant_research_platform.targets` imports from `quant_research_platform.providers`, from `quant_research_platform.ingestion`, or from any provider-specific library. Failing this is a defect against SDR Decision 2 and Section 1 invariant 1.
19. **Adjusted-close-only test** — a static / source-scan check verifying that no module under `targets/` references the columns `raw_open`, `raw_high`, `raw_low`, `raw_close`, or `volume` from `prices.etf_prices_daily` in any target-computation code path. Phase 1 03b does not use raw OHLCV in any target; this test backstops the Section 2 adjusted-price convention.
20. **`data_snapshot_id` linkage test** — every `targets.target_values` row is reachable to a non-`'invalidated'` `ops.data_snapshots` row via `target_run_id`. A mutation test that flips the snapshot's `status` to `'invalidated'` raises a clear error on the next attempted run referencing it.
21. **Invalidated-snapshot rejection test (open-run-before-validation lifecycle).** Starting a target run with `data_snapshot_id` referencing a snapshot whose `status='invalidated'` produces this lifecycle: (a) the `targets.target_runs` row is opened with `status='running'`; (b) the orchestrator's snapshot validation detects the invalidated status; (c) the run row is updated to `status='failed'` with `error_message` populated and `completed_at_utc` set; (d) a `severity='fail'` row with `issue_type='invalidated_snapshot_blocked'` is written to `targets.target_run_issues` with `target_run_id` set to the now-failed run and `detail` naming the offending `data_snapshot_id`; (e) **no `targets.target_values` rows are written for that run**. The test asserts each of (a)–(e) and asserts that `ops.data_quality_exceptions` is unchanged.
22. **Ingestion-run consumption test (open-run-before-validation lifecycle).** Starting a target run when the ingestion runs *covering the snapshot's actual price data* include any with `status='failed'` produces this lifecycle: (a) the `targets.target_runs` row is opened with `status='running'`; (b) the orchestrator's ingestion-run validation detects the failed dependency; (c) the run row is updated to `status='failed'` with `error_message` populated and `completed_at_utc` set; (d) a `severity='fail'` row with `issue_type='failed_ingestion_run_blocked'` is written; (e) **no `targets.target_values` rows are written for that run**. The same lifecycle and assertions apply for `'partial'` ingestion runs with `issue_type='partial_ingestion_run_blocked'`. **No row is written to `ops.data_quality_exceptions`.** The test additionally asserts that the dependency-check scope is the snapshot's actual price data (not a hypothetical extended range out to `T_max + max_horizon`); a fixture in which the snapshot's `price_table_max_as_of_date` is well below the eligible signal-date floor's `T_max + max_horizon` but all ingestion runs covering the snapshot's actual data are `'succeeded'` must produce a `'succeeded'` target run with the front-edge-truncated absence pattern (consistent with test #5 / test #37).
23. **Cross-run idempotency** — same `data_snapshot_id`, same `target_set_version`, same `commit_hash`, same `config_hash` across two `'succeeded'` runs produces identical `target_value`, `entry_date`, `exit_date`, and `horizon_trading_days` for every `(etf_id, as_of_date, target_name)` (modulo PK).
24. **`config/targets.yaml` validation tests** — every validation rule in §7.2 is exercised by a passing test for a valid config and a failing test for an invalid config. Unknown family keys raise. Missing required parameters raise. Out-of-type values raise. The test for `require_etf_backed_benchmark: false` raises (interim constraint inherited from 03a §10.1; §11.6 #6). The test for `convention: "A"` raises (Convention B is the only enabled value in current 03b scope per §11.6 #1; the test for any unknown convention also raises). The test for `forward_window.delisted_within_window_rule: "null_with_partial_flag"` raises (the only enabled value is `"no_row"` per §11.6 #4).
25. **Container-test parity** — every test passes both at host pytest invocation and inside the container via `docker compose exec app pytest tests/unit/targets/`. EW §5 treats divergence as a defect.
26. **Target-catalog initialization test** — at orchestrator startup, `targets.target_definitions` rows for the active `target_set_version` match the enabled families and parameters in `config/targets.yaml` exactly. Disabling a family in YAML and re-running results in the active-version catalog reflecting only the enabled families on the next run; rows for prior versions are retained.
27. **No-secrets-in-targets test** — a diff scan over `targets/` source, fixtures, and tests confirms no API keys, tokens, passwords, or `.env` contents are committed (Section 1 invariant 6 backstop, parallel to 03a).
28. **Failed-run exclusion test (parallel to 03a Revision 4).** A fixture run is forced to fail mid-execution after some `targets.target_values` rows have been committed in transactional batches. The test asserts:
    (a) the `targets.target_runs` row's `status` is `'failed'` and `error_message` is populated;
    (b) the partial `targets.target_values` rows from that run are still present in the table (no auto-deletion);
    (c) any downstream-consumable query helper exposed by `common/` (or its equivalent canonical query pattern documented in 03b) returns **zero rows** from the failed run when filtering on `targets.target_runs.status='succeeded'`. The test fails if a partial-failed-run row leaks into the consumable surface.
29. **`target_set_version` consistency test (database-level enforcement, parallel to 03a §8.2 #29).** A fixture attempts to write a `targets.target_values` row whose `target_set_version` does not match the `target_set_version` of the linked `targets.target_runs` row. The composite FK rejects the write at the database level. The test asserts (a) database-level rejection; (b) clearer-error orchestrator-side rejection when the orchestrator's invariant check is in place; (c) on the success path, every value row's `target_set_version` matches its linked run's.
30. **Composite FK to `target_definitions` test (parallel to 03a §8.2 #30).** A fixture attempts to write a `targets.target_values` row with a `target_name` that does not exist in `targets.target_definitions` for the active `target_set_version`. The composite FK rejects the write at the database level.
31. **Forward trading-day alignment — weekend boundary (parallel to 03a Revision 6, applied forward).** A fixture price series spans Friday → Monday with no rows on Saturday or Sunday. For signal date `T = Thursday` and horizon 1, `entry_date = Friday` (Convention B's `T+1`) and `exit_date = Monday` (one trading day after entry, skipping the weekend). The recorded `entry_date` and `exit_date` match these dates. The test fails if the calculator treats `T+1` as `Friday` (calendar Friday) on a fixture where the ETF has no Friday row, in which case `entry_date` would have to be the next available trading day.
32. **Forward trading-day alignment — holiday boundary (parallel to 03a Revision 6, applied forward).** A fixture price series spans a trading day, a market holiday (no row), and the next trading day. For signal date `T` equal to the pre-holiday trading day and horizon 1, `entry_date` is the post-holiday trading day. The test fails if the calculator treats `T+1` as the calendar day immediately after `T` when that day has no row.
33. **Forward cross-series alignment for excess-return targets.** A fixture in which both the ETF's and the benchmark's required `entry_date` and `exit_date` fall inside the snapshot's `price_table_max_as_of_date`, but the two series have **different missing days within the forward window** (e.g., the ETF is missing day `D` while the benchmark is not, and vice versa). A `targets.target_values` row IS written for `(e, T, h)` with `target_value = NULL` (Bucket 2 of §6.5); the row is **not** absent. The classification target row is also written with `target_value = NULL` by null propagation. The test fails if the calculator silently uses different effective dates for the two series within the same target row, or if it omits the row entirely (which would be the Bucket 1 outcome and would not match the fixture's coverable-window setup).
34. **No-write-to-`ops.*` static check (parallel to 03a §8.2 #34).** A static check confirming that no module under `quant_research_platform.targets` writes to **any** `ops.*` table. Implemented as a source / SQL scan looking for `INSERT INTO ops.`, `UPDATE ops.`, `DELETE FROM ops.` patterns and equivalent ORM operations. Failing this is a defect against Section 2 v1.0 LOCKED.
35. **`targets.target_run_issues` write test (lifecycle-driven, parallel to 03a §8.2 #35).** A fixture exercises each of the five closed-enumeration `issue_type` values via a real lifecycle path:
    - `'invalidated_snapshot_blocked'`, `'failed_ingestion_run_blocked'`, `'partial_ingestion_run_blocked'`: produced by starting a target run with the corresponding adverse snapshot / ingestion-run state, per the §6.3 blocked-run lifecycle.
    - `'target_run_failed'`: produced by forcing a target run to fail mid-execution (after the run row is open and some value rows have committed in transactional batches).
    - `'index_only_benchmark'`: produced by a normal `'succeeded'` target run that includes an ETF whose primary benchmark resolves index-only.
    The test asserts (a) row written with correct `target_run_id`, `issue_type`, `severity`, scoping fields, `summary`, `detail`; (b) CHECK constraint rejects unknown `issue_type`; (c) CHECK constraint rejects unknown `severity`; (d) FK rejects a row referencing a non-existent run; (e) for the four blocking / failed cases, the linked `target_runs.status` is `'failed'`; for `'index_only_benchmark'`, `'succeeded'`; (f) for the three `*_blocked` cases, **no `targets.target_values` rows are written for the failed run**.
36. **`targets.target_run_issues` query test (parallel to 03a §8.2 #36).** A fixture populates several runs with mixed issues; the canonical query patterns (per-run, per-`issue_type`, per-`(etf_id, as_of_date)`) return the expected rows.
37. **Coverage-parity-with-03a test (per §6.9).** A fixture target run with `data_snapshot_id = S` and a fixture feature run with `data_snapshot_id = S` over the same universe and as-of-date range. The `(etf_id, as_of_date)` set in `targets.target_values` is asserted to be a subset of the set in `features.feature_values` after both runs are filtered on `status='succeeded'`. The front-edge truncation (target rows missing for the most recent `max_horizon` trading days that have feature rows) is asserted explicitly: (a) the missing rows are simply absent in `targets.target_values`, **not** present with `target_value = NULL`; (b) the target run completes with `targets.target_runs.status='succeeded'` despite the front-edge truncation — front-edge truncation does **not** block the run; (c) **no `targets.target_run_issues` row** with any `forward_window`-related `issue_type` is written for these absences in current 03b scope (per §11.6 #10).
38. **Vacuous failed-run-feature-consumption discipline test (per §5.1 / 03a approval note §4.4).** A static / source-scan check confirming that no module under `quant_research_platform.targets` reads from `features.feature_values` or `features.feature_runs` for target generation. The §4.4 discipline applies vacuously to 03b's target-generation paths because there are no feature-consumption paths. (If the Approver later extends 03b to consume feature values, this test is replaced with the corresponding `status='succeeded'` filter test.)
39. **Window-metadata-on-every-row test.** Every `targets.target_values` row has non-null `signal_date`-equivalent (`as_of_date`), `horizon_trading_days`, `entry_date`, and `exit_date`. The schema's NOT NULL constraints enforce this; the test asserts the constraint by attempting to insert a row missing any of the four (rejected at the database level).
40. **Overlapping-label window arithmetic test (informational; Section 4 owns enforcement).** For a fixed horizon `h` and two adjacent signal dates `T` and `T+1` (trading-day-adjacent), the recorded `[entry_date(T), exit_date(T)]` and `[entry_date(T+1), exit_date(T+1)]` overlap by exactly `h - 1` trading days under Convention B. The test asserts the overlap arithmetic on a fixture; it does **not** assert that any purge/embargo is applied (Section 4 owns that). Verifies the schema metadata is sufficient for Section 4 to apply purge/embargo without re-deriving the windows.

### 8.3 Test data discipline

- Fixtures live under `tests/fixtures/targets/`. Synthetic price series for known-input / known-output tests are checked into the repo per EW §5.
- No 03b test depends on a live API call.
- The integration test path (`tests/integration/targets/`) exercises the orchestrator end-to-end on a small fixture universe with a fixture `ops.data_snapshots` row, producing fixture-comparable `targets.target_values` content.

---

## 9. Edge cases and failure behavior

1. **New ETFs (added to universe but not yet rank-eligible).** **No `targets.target_values` row is written** for `(e, T)` when `T < eligible_start_date(e)` or when `etf_eligibility_history` does not return a row with `is_rank_eligible=true` covering signal date `T`.
2. **Delisted ETFs (signal date on/after delisting).** **No `targets.target_values` row is written** for `(e, T)` where `T >= delisted_date(e)`.
3. **ETF delisted within the forward window.** Per the Approver-resolved `forward_window.delisted_within_window_rule = "no_row"` (§11.6 #4): when `delisted_date(e) <= exit_date(e, T, h)`, **no row** is written for that `(e, T, h)` (Bucket 1 of §6.5). The alternative `"null_with_partial_flag"` is not enabled in current 03b scope and the YAML validator (§7.2) refuses any other value.
4. **Snapshot front-edge truncation (Bucket 1 absence; NOT a run-level failure).** When the snapshot's `price_table_max_as_of_date` does not cover `exit_date(e, T, h)`, **no `targets.target_values` row** is written for that `(e, T, h)` (Bucket 1 of §6.5). The target run still completes with `status='succeeded'` provided no run-level blocking condition (§6.3 closed list) is hit and at least some eligible rows are produced. **No `targets.target_run_issues` row** is written for front-edge truncation in current 03b scope (per §11.6 #10). The operator can derive the implicit "would have been labeled but weren't" set by comparing the eligible signal-date set to the produced signal-date set.
5. **Benchmark gaps within the forward window.** When the benchmark ETF `b` has missing days within `[entry_date, exit_date]` per the missing-data rule (§6.1), a `targets.target_values` row IS written with `target_value = NULL` for the regression family (Bucket 2 of §6.5); the classification target row is also written with `target_value = NULL` by null propagation per §6.2.
6. **Non-overlapping trading history (ETF vs benchmark) within the forward window.** When `e` has a price row on `entry_date` or `exit_date` that `b` does not (or vice versa), a `targets.target_values` row IS written with `target_value = NULL` for the regression family (Bucket 2 of §6.5); the classification target row is also written with `target_value = NULL` by null propagation.
7. **Index-only benchmark (regression and classification both write rows with `target_value = NULL`).** Per Section 3a §10.1 inheritance: a `targets.target_values` row IS written for the regression family with `target_value = NULL`; the classification family row is also written with `target_value = NULL` by null propagation per §6.2 (Bucket 2 of §6.5). A `severity='warning'` row with `issue_type='index_only_benchmark'` is recorded in `targets.target_run_issues`. **No silent benchmark substitution. No fallback to `secondary_benchmark_id`. No row is written to `ops.data_quality_exceptions`.**
8. **Invalidated `ops.data_snapshots`.** Per the §6.3 blocked-run lifecycle: orchestrator opens the `targets.target_runs` row first, then validates the snapshot. Detecting `status='invalidated'` causes the run row to be marked `'failed'` and a `severity='fail'` row written to `targets.target_run_issues` with `issue_type='invalidated_snapshot_blocked'`. **No `targets.target_values` rows are written.**
9. **Failed ingestion runs covering the snapshot's price data.** Per Section 2 LOCKED constraint #8, 03b may not silently consume `failed` runs. The dependency-check scope is the ingestion runs that actually populated the snapshot's price data — **not** a hypothetical extended range out to `T_max + max_horizon` (front-edge of the price data is governed by the row-level observability gate, not by a run-level dependency check). Per the §6.3 blocked-run lifecycle: orchestrator opens the run row first; on detection of any covering ingestion run with `status='failed'`, marks run `'failed'`; writes `issue_type='failed_ingestion_run_blocked'`. **No `targets.target_values` rows are written.**
10. **Partial ingestion runs covering the snapshot's price data.** Per Section 2 LOCKED constraint #5 and #7, partial runs are blocking by default. The dependency-check scope is the same as edge case 9 — ingestion runs covering the snapshot's actual price data, not a hypothetical extended range. Per-symbol-aware partial handling via `chunk_results` JSONB is explicitly out of 03b scope (mirroring 03a). Per the §6.3 blocked-run lifecycle: orchestrator opens the run row first; on detection, marks run `'failed'`; writes `issue_type='partial_ingestion_run_blocked'`. **No `targets.target_values` rows are written.** A future amendment could introduce per-symbol-aware target computation.
11. **Missing data within the forward window (single bar gap).** Per `missing_data.rule = "null_on_any_missing_input_in_window"` (Approver-resolved per §11.6 #3), a `targets.target_values` row IS written for any signal date where `[entry_date, exit_date]` contains a missing input bar, with `target_value = NULL` (Bucket 2 of §6.5). No interpolation, no forward-fill, no extrapolation. Backward-fill is forbidden (it would constitute look-ahead within the forward window).
12. **Target run failure mid-execution.** Target runs write in transactional batches; a failure during execution leaves the `targets.target_runs` row updated to `status='failed'` with `error_message` populated and `completed_at_utc` set, while any `targets.target_values` rows from already-committed batches **are retained** (no auto-deletion) and remain distinguishable by `target_run_id`. **Downstream consumers — 03c, Section 4 — must filter on `targets.target_runs.status='succeeded'`** when reading from `targets.target_values`. The target run is **not** auto-retried by 03b; the next scheduled run picks up. A `severity='fail'` row with `issue_type='target_run_failed'` is recorded. **No row is written to `ops.data_quality_exceptions`.**
13. **Universe expansion (ETF added between snapshots).** The target run is bound to a single `data_snapshot_id`; the universe at snapshot time is the universe used for the run.
14. **YAML config malformed or missing.** Per EW §7 and Section 1 invariant 6, the orchestrator fails at startup with a clear, structured error.
15. **Database connectivity loss mid-run.** The run status transitions to `'failed'` on the next reconnection attempt (or via the orchestrator's structured exception handling); partial writes within the failed transaction are rolled back per standard Postgres semantics. 03b does not implement custom retry/resume.
16. **Adjacent target rows with overlapping forward windows.** Targets at signal dates `T` and `T+1` with horizon `h` have measurement windows `[entry(T), exit(T)]` and `[entry(T+1), exit(T+1)]` that overlap by `h - 1` trading days under Convention B. This is **expected** and recorded explicitly via the per-row `entry_date` / `exit_date` columns. 03b does **not** apply purge/embargo at the target-emission level — Section 4's walk-forward harness consumes the recorded windows and applies purge/embargo at the train/test boundary. This is the principal reason §11.6 #5 (Approver-resolved persistence default) materializes targets with row-level window metadata: Section 4's purge/embargo logic should not have to re-derive the windows from horizon arithmetic.
17. **Future target horizon extension via amendment.** If a future 03b amendment adds, say, a 252-day horizon, the new horizon's required snapshot coverage (`T_max + 252`) extends further forward; the snapshot validation would need to pass for the maximum enabled horizon across all enabled families.

---

## 10. Open questions

In current 03b scope, the items previously raised as Open Questions and Proposed defaults requiring Approver approval are now Approver-resolved defaults and live in §11.6. **Two items remain in §10:** one residual structural Open Question (inherited from 03a §10.1) and one Implementation default with no strategy impact, retained here for visibility per EW §3.3.

### 10.1 Index-only benchmark structural gap (inherited Open Question from 03a §10.1; residual)

**Status:** *Open Question for Approver / possible future Section 2 amendment.*

The interim *behavior* — when the primary benchmark resolves index-only, the regression and classification target rows are written with `target_value = NULL` and a `severity='warning'` row with `issue_type='index_only_benchmark'` is recorded in `targets.target_run_issues`; no silent benchmark substitution; no fallback to `secondary_benchmark_id` — is now an **Approver-resolved default** in §11.6 #6. **No Section 2 amendment is proposed by 03b.**

The **residual structural question** retained here is whether to ever pursue a Section 2 amendment that introduces benchmark price storage (e.g., a `prices.benchmark_prices_daily` table for index-backed benchmarks) and a corresponding ingestion path, which would resolve the structural gap for both 03a and 03b simultaneously. The Approver may at any time direct (a) acceptance of the interim constraint as the durable Phase 1 behavior, (b) a Section 2 amendment to add benchmark price storage, or (c) a different resolution. None of those is proposed by current 03b scope.

### 10.2 `targets.*` migration filenames (forward reference to module-build time)

**Status:** *Implementation default with no strategy impact.*

Current 03b scope references `targets.target_runs`, `targets.target_definitions`, `targets.target_values`, and `targets.target_run_issues` at the spec level. Concrete migration filenames continuing from Section 2's `0001_initial_setup.sql` and Section 3a's eventual `features.*` migration are assigned at module-build time per EW §8 conventions, not in this spec. The exact filename and number are at Builder discretion within the convention.

---

## 11. Explicit assumptions

Classified per EW §3.3. Items already classified in §10 above (the residual structural Open Question §10.1 and the Implementation default §10.2) and items recorded as Approver-resolved defaults in §11.6 are not duplicated under §11.1–§11.5.

### 11.1 Derived from SDR or EW

- **Adjusted-close is canonical research price.** Section 2 v1.0 LOCKED Approver-directed convention; SDR Decision 11.
- **No `targets/` module imports from `providers/` or provider-specific libraries.** SDR Decision 2; Section 1 invariant 1.
- **No target generation before `eligible_start_date` and the as-of-date eligibility-history `is_rank_eligible=true` row.** SDR Decision 3; SDR Decision 4.
- **Each ETF has a `primary_benchmark_id`.** SDR Decision 5; Section 2 v1.0 LOCKED schema (NOT NULL).
- **Forward-target horizons of 63 and 126 trading days.** SDR Decision 6.
- **Targets must support walk-forward validation in Section 4 with purge/embargo.** SDR Decision 7. 03b records the per-row window metadata (`signal_date`, `horizon_trading_days`, `entry_date`, `exit_date`) Section 4 needs without implementing purge/embargo itself.
- **Forward-data-only labeling at the target level.** SDR Decision 16 (look-ahead-bias control on the label-formation side); Section 1 invariant 7.
- **Survivorship-aware target generation gated on `etf_eligibility_history` and ETF lifecycle fields, with ineligible / out-of-lifecycle pairs absent from `targets.target_values`.** SDR Decision 16; Section 2 v1.0 LOCKED schema; Section 3a v1.0 LOCKED eligibility-row omission contract (parallel application).
- **`data_snapshot_id` is the reproducibility anchor on the writer side.** SDR Decision 11; Section 2 v1.0 LOCKED `ops.data_snapshots`; EW §7 reproducibility list.
- **Tests must run inside the application container.** EW §5.
- **All paths via `pathlib.Path`; container-local paths only.** EW §7; Section 1 invariant 5.
- **No secrets in code, config, fixtures, logs, or docs.** EW §7, §9, §10; Section 1 invariant 6.
- **No new auto-resolution classes beyond the four allowed by SDR Decision 11.** Section 2 v1.0 LOCKED constraint #1. 03b does not write to `ops.data_quality_exceptions` at all — target-layer issues land in `targets.target_run_issues` per §6.6. The Section 2 framework remains ingestion-owned and unmodified.
- **Phase 1 excludes fundamentals, holdings, news, earnings, options, individual stocks, autonomous research agents.** SDR Decision 1; SDR Decision 14.

### 11.2 Derived from Section 1

- **`targets/` imports only from `common/`.** Section 1 *Python import dependency graph*.
- **`targets/` does not import from any other business area.** Section 1 import discipline; cross-area sharing is via `common/` or via Postgres data-at-rest coupling.
- **Time-aware research auditability invariant 7 cashes out at the target level in 03b** alongside Section 2 (data-layer side), Section 3a (feature-formation side), and Section 4 (backtest side).

### 11.3 Derived from Section 2

- **`prices.etf_prices_daily.adjusted_close` is the canonical price input** for all 03b targets.
- **`universe.etfs` is the source of identity, lifecycle, sleeve, and benchmark assignment fields** for 03b.
- **`universe.etf_eligibility_history` is canonical for the actual eligibility timeline**, with half-open effective-date semantics.
- **`ops.data_snapshots` is the reproducibility anchor**; `'invalidated'` snapshots raise clear errors on attempted use; `price_table_max_as_of_date` is the operative upper bound for forward-window observability.
- **Partial ingestion runs are blocking by default; failed runs may not be silently consumed.** Section 2 v1.0 LOCKED constraints #5, #7, #8.
- **The interim `pending_section_3` `rank_method` sentinels in `config/universe.yaml` are closed by 03c**, not by 03b.
- **The secrets redaction utility (`common.redact_secrets()`) is the only allowed path for persisting any provider-derived text or JSON.** Section 2 v1.0 LOCKED constraint #8. 03b does not persist provider-derived content (targets are derivative computations); the constraint is respected by absence.

### 11.4 Derived from Section 3a

- **The eligibility-row omission contract** (rank-ineligible ETF/date pairs absent from the surface) is inherited verbatim and applied to `targets.target_values`.
- **T-1 trading-day semantics** at the signal date are inherited; 03b's parallel construction is forward trading-day arithmetic for `entry_date` and `exit_date`, walked through `prices.etf_prices_daily` rows for the relevant ETF.
- **The provider-abstraction boundary** is inherited; no `targets/` module imports from `providers/` or any provider-specific library.
- **The failed-run consumption-side discipline** (filtering on `status='succeeded'`) is inherited and applied to `targets.target_runs`. The 03a-equivalent filter on `features.feature_values` applies *vacuously* to 03b's target-generation paths because 03b does not consume feature values for target generation; 03c is bound by both filters when it joins features and targets for model training.
- **The `feature_set_version` integrity contract** is parallelled by 03b's `target_set_version` integrity contract (UNIQUE on `target_runs` plus composite FK from `target_values`).
- **The `data_snapshot_id` reproducibility chain** is inherited; 03c MLflow runs link back to `targets.target_runs.target_run_id` (and to `features.feature_runs.feature_run_id`) in parallel.
- **The closed-enumeration issue-log pattern** (`feature_run_issues` schema and lifecycle) is inherited by `targets.target_run_issues`; the five `issue_type` values mirror 03a's directly with target-context wording.
- **The benchmark-resolution interim constraint** (no fallback to secondary; warning row on index-only) is inherited verbatim for the regression family.
- **The `ops.data_quality_exceptions` framework remains ingestion-owned and unmodified by 03b.**
- **The classification-derived-from-regression design** (§6.2 classification family computed from the regression target within the same run, not re-derived from prices independently) is an Implementation default introduced by 03b that mirrors 03a's principle of uniform behavior on edge cases.

### 11.5 Implementation default (no strategy impact)

- **`targets.target_values` carries `target_set_version` with composite FKs to `targets.target_definitions(target_set_version, target_name)` and to `targets.target_runs(target_run_id, target_set_version)`** (parallel to 03a §11.4). Database-enforced FKs are more strict than orchestrator-only validation, are testable at the schema level, and survive any future bypass.
- **Long-form `targets.target_values` PK includes `target_run_id`** to support append-only writes across runs while distinguishing successive runs against the same snapshot.
- **`numeric(24,12)` for `target_value`** — generous precision for excess returns and outperformance flags (`0` / `1`). Matches 03a precision.
- **`target_definitions` populated at orchestrator startup** by reading `config/targets.yaml`. Existing rows for prior `target_set_version` values are retained for audit.
- **Target names use lowercase snake_case** with windowed names suffixed by the trading-day horizon (e.g., `excess_return_63d`). Matches 03a's convention.
- **Indexes on `targets.target_values`** match 03a's index style: PK + the small set of indexes named in §6.5, plus the `(exit_date)` index for Section 4 purge/embargo queries.
- **Tests directory layout** under `tests/unit/targets/` and `tests/integration/targets/`, mirroring 03a's convention.
- **Trading-calendar source.** Per §6.1, the operative trading calendar is the set of `prices.etf_prices_daily` rows for the relevant ETF (per Section 2 ownership). 03b does not maintain its own calendar table or load an external calendar.
- **Classification is computed within the same target run as the regression it derives from.** Avoids divergence between the two families on edge cases (a single null cause produces null in both families simultaneously). Alternative — separate runs per family — is implementation flexibility for future amendments but not Phase 1.

### 11.6 Approver-resolved defaults (Section 3b)

Direction received during the v0.1 → v0.2 revision pass (2026-04-29) per the established working pattern. The following ten items are Approver-resolved defaults:

| # | Item | Decision |
|---|---|---|
| 1 | Entry/exit convention | **Convention B**: entry at `T+1` close, exit at `T+1+h` close (per ETF `e`'s trading-day index). The schema's `entry_offset_trading_days` and `exit_offset_trading_days` columns record the convention explicitly per row; a future amendment is required to enable any other convention. |
| 2 | Classification threshold `θ` | **`θ = 0.0`** — strict positive excess return defines outperformance. |
| 3 | Missing-forward-data rule | **`missing_data.rule = "null_on_any_missing_input_in_window"`** — any missing input bar in `[entry_date, exit_date]` produces a row with `target_value = NULL` (Bucket 2 of §6.5). Aligns with 03a's parallel rule. |
| 4 | ETF-delisted-within-window rule | **`forward_window.delisted_within_window_rule = "no_row"`** — when `delisted_date(e) <= exit_date(e, T, h)`, no row is written (Bucket 1 of §6.5). The alternative `"null_with_partial_flag"` is not enabled in current 03b scope; the YAML validator (§7.2) refuses any other value. |
| 5 | Target persistence | **Persist `targets.*` with `data_snapshot_id` linkage.** The `targets.*` schema is materialized; downstream consumers (03c, Section 4) query the table. The on-the-fly alternative is not pursued; the persistence-side window-metadata columns (`signal_date`, `horizon_trading_days`, `entry_date`, `exit_date`) are what Section 4's purge/embargo logic consumes. |
| 6 | Index-only benchmark behavior | **Keep interim behavior; no Section 2 amendment proposed; no silent benchmark substitution; no fallback to `secondary_benchmark_id`.** When the primary benchmark resolves index-only on signal date `T`, the regression target row is written with `target_value = NULL` (Bucket 2 of §6.5); the classification target row is also written with `target_value = NULL` by null propagation; a `severity='warning'` row with `issue_type='index_only_benchmark'` is recorded in `targets.target_run_issues`. The residual structural question (whether to ever pursue benchmark price storage via a Section 2 amendment) remains §10.1. |
| 7 | Config file | **`config/targets.yaml`** — owned by 03b. Approved within the 03b spec approval path. **No Section 1 amendment is proposed by 03b**; targets config is **not** moved into `config/model.yaml`; 03c continues to own `config/model.yaml`; 03c may *read* target metadata at consumption time but does not own target config. |
| 8 | Target families | **Regression excess return and classification outperformance only** for Phase 1 03b. No additional families (no volatility-adjusted excess return, no drawdown-magnitude target, no sleeve-relative target, etc.). Additions require a future 03b amendment. |
| 9 | Target horizons | **Exactly 63 and 126 trading-day horizons** per SDR Decision 6. No additions or removals. Any change requires explicit Approver direction and an SDR-level review since horizons are an SDR Decision 6 commitment. |
| 10 | Snapshot coverage / front-edge truncation | **Absence-only** — signal dates whose required forward window exceeds the snapshot's `price_table_max_as_of_date` produce no rows (Bucket 1 of §6.5). **No run-level warning issue is required for front-edge truncation in current 03b scope** unless the Approver later directs otherwise. The closed `issue_type` enumeration on `targets.target_run_issues` (§6.6) does not include `'forward_window_horizon_truncated'` in current 03b scope. |

Any change to these defaults goes through the EW change process. Items #1, #2, #3, #4, #5, #8, #9, #10 are strategy-affecting; items #6 and #7 are structural / process-affecting.

### 11.7 Proposed default requiring Approver approval

In current 03b scope this category is empty. All Phase 1 03b strategy-affecting choices that would otherwise sit here have been promoted to Approver-resolved defaults (§11.6); the only structural item that did not resolve is preserved as a residual Open Question (§11.8 / §10.1).

### 11.8 Open question for Approver

(See §10.1 — the residual structural Open Question on the index-only benchmark gap, inherited from 03a §10.1. The interim behavior is Approver-resolved per §11.6 #6; what remains open is whether to ever pursue the Section 2 amendment that would close the structural gap.)

---

## 12. Section 3b → 03c handoff (forward references only)

03b leaves the platform with:

- A specified target-generation surface (regression and classification at 63 and 126 trading-day horizons) computing values from `prices.etf_prices_daily.adjusted_close`, `universe.etfs`, `universe.etf_eligibility_history`, and `universe.benchmarks` per the Section 2 contracts and the Section 3a eligibility/benchmark patterns.
- A specified `targets.*` schema comprising four tables — `targets.target_runs`, `targets.target_definitions`, `targets.target_values`, and `targets.target_run_issues` — anchored to `ops.data_snapshots` for reproducibility, with the target-layer issue log (`target_run_issues`) deliberately separate from the Section 2 ingestion-owned `ops.data_quality_exceptions` framework and parallel to 03a's `features.feature_run_issues`.
- A specified `config/targets.yaml` shape with closed-set family validation, owned by 03b (per §11.6 #7; no Section 1 amendment proposed).
- Forward-data-only labeling, per-row window metadata (`signal_date`, `horizon_trading_days`, `entry_date`, `exit_date`), survivorship gating, forward-window observability gating, and benchmark interim constraint inherited from 03a — all tested at the target level.
- A coverage-parity guarantee with 03a (target rows are a subset of feature rows over the same snapshot, modulo the front-edge horizon truncation).

The handoff to subsequent sections:

- **`docs/engineering_spec/03c_model_layer_mlflow.md`** (next in sequence) will own baseline model implementations under SDR Decision 6's dual-target framework, the calibration pipeline per SDR Decision 7, MLflow client-side integration on the writer side per SDR Decision 11, the model registry schema (`models.*`), the model state lifecycle per SDR Decision 12 (Active/Warning/Paused/Retired), the allowed values and semantics for `rank_method` (closing the Section 2 `pending_section_3` sentinel obligation), the combined-score formula per SDR Decision 6 (first testable formula), and `config/model.yaml`. 03c does **not** own `config/targets.yaml` (03b does, per §11.6 #7); 03c may *read* target metadata at consumption time. 03c is responsible for joining `features.feature_values` (filtered on `features.feature_runs.status='succeeded'`) and `targets.target_values` (filtered on `targets.target_runs.status='succeeded'`) on `(etf_id, as_of_date)` to assemble training data; 03c training data assembly tests must verify both filters are applied and the front-edge horizon truncation is correctly handled. 03c MLflow runs link back to both `feature_run_id` and `target_run_id` to satisfy the EW §7 reproducibility list.

- **`docs/engineering_spec/04_backtest_attribution_validation.md`** will own the walk-forward harness consuming the Section 3a feature surface and the Section 3b target surface (both filtered on `status='succeeded'`), with purge/embargo enforcement per SDR Decision 7 and Decision 16. The 126-day embargo per SDR Decision 7 is implemented at the train/test boundary using the `entry_date` / `exit_date` metadata Section 3b records on every target row — Section 4 does **not** re-derive the windows from horizon arithmetic. Backtest reproducibility is anchored on the `data_snapshot_id` chain established by 03a and 03b. The regime reporting layer per SDR Decision 9 (the full reporting layer; 03a's feature-side primitive remains a feature input only) is also Section 4's.

- **Section 5** (portfolio, paper, order intent) and **Section 6** (UI) consume target-derived rankings from 03c outputs and target-related metadata from `targets.target_run_issues` (UI surfacing only).

Each subsection follows the full EW §3 workflow (handoff packet, drafting, QA review, Approver approval, commit, traceability matrix update).

---

## 13. Proposed traceability matrix updates (draft only)

This section sketches the matrix updates 03b contributes at lock time. **The matrix update itself is not applied within this spec.** Items owned by 03c or Section 4 are marked pending. The fuller proposed-replacement-rows companion file (matching the Section 2 / 3a traceability-updates companion file shape) is produced as a separate artifact at 03b lock: `docs/reviews/<YYYY-MM-DD>_spec_03b_target_generation_traceability_updates.md`. The matrix is updated by the Approver as part of the Section 3b lock merge.

**Note on `config/targets.yaml` and Section 1.** Per §11.6 #7, `config/targets.yaml` is approved within the 03b spec approval path; **no Section 1 amendment is proposed by 03b**. The Section 1 *Config dependencies* table is not updated by this proposed traceability companion. Integration with the Section 1 list is left to a future housekeeping pass that does not require reopening Section 1.

| SDR Decision | Proposed 03b contribution | Status after 03b lock |
|---|---|---|
| Decision 1 — Project Scope and Phase 1 Boundaries | Affirmed by 03b's exclusion of fundamentals, holdings, news, earnings, options, individual stocks, autonomous agents at the target level. | unchanged (already `in spec`) |
| Decision 2 — Data Provider and Provider-Switching Strategy | Extended to record 03b's no-provider-import contract for `targets/` and the adjusted-close-only contract. | unchanged status (`in spec`); row text extended |
| Decision 3 — ETF Universe and Eligibility Rules | Extended to record 03b's eligibility-row omission contract on `targets.target_values` (Bucket 1 of §6.5). | unchanged status (`in spec`); row text extended |
| Decision 4 — Universe Survivorship and ETF Launch-Date Handling | Extended to record 03b's `first_traded_date` / `delisted_date` gating at the target level, including the Approver-resolved `forward_window.delisted_within_window_rule = "no_row"` (§11.6 #4) which makes ETF-delisted-within-the-forward-window a Bucket 1 absence case. | unchanged status (`in spec`); row text extended |
| Decision 5 — Benchmark, Sleeve, and Diversifier Treatment | Extended to record 03b's regression family using `primary_benchmark_id` and inheriting the index-only-benchmark interim constraint per §11.6 #6 (no silent substitution, no fallback to secondary, row written with `target_value = NULL`, warning row in `targets.target_run_issues`). | unchanged status (`in spec` (universe-side and feature side); `pending` (ranking math, rank_method values)); row text extended on the target-side contribution |
| Decision 6 — Target Design and Ranking Objective | **Status transition.** 03b cashes out the regression and classification families at 63 and 126 trading-day horizons (Approver-resolved per §11.6 #8 and §11.6 #9), the entry/exit Convention B (§11.6 #1), the classification threshold `θ = 0.0` (§11.6 #2), the missing-forward-data rule and ETF-delisted-within-window rule (§11.6 #3 and #4), the snapshot-coverage / front-edge-truncation absence pattern (§11.6 #10), the target persistence model (§11.6 #5), the forward-data-only labeling, and the per-row window metadata. The combined-score formula and the integration into ranking remain pending in 03c. | **`in spec` (regression and classification target generation, label alignment, per-row window metadata)**; `pending` (combined-score formula, ranking integration — 03c) |
| Decision 7 — Validation, Calibration, and Backtest Confidence Level | Extended to record 03b's per-row window metadata (`entry_date`, `exit_date`, `horizon_trading_days`) supporting Section 4's walk-forward harness with purge/embargo. 03b does not implement walk-forward or calibration. | `pending` (03c calibration, Section 4 harness); 03b row text extended on the metadata-supplied-to-Section-4 contribution |
| Decision 11 — Model Tracking, Attribution, Data Quality, and Lightweight MLOps | Extended to record 03b's `targets.target_runs.data_snapshot_id` linkage; `targets.target_values.target_run_id` row-level traceability via the composite FK to `targets.target_runs`; `targets.target_run_issues` as the target-layer issue log with closed `issue_type` and `severity` enumerations and the open-run-before-validation lifecycle (the closed `issue_type` enumeration does **not** include a `forward_window`-related value in current 03b scope per §11.6 #10). **`ops.data_quality_exceptions` remains ingestion-owned and unmodified by 03b** per Section 2 v1.0 LOCKED. MLflow writer-side integration remains pending (03c). | unchanged status (`in spec`); row text extended |
| Decision 16 — Phase 1 Success Criteria and Bias Controls | Extended to record 03b's target-side time-aware auditability: forward-data-only labeling tests; survivorship and lifecycle tests at the target level; row-level forward-window observability tests (Bucket 1 absence pattern, not a run-level failure, per §11.6 #10); idempotency tests; `data_snapshot_id` linkage tests; per-target-row window metadata supporting Section 4 purge/embargo. | unchanged status (`in spec`); row text extended |

The companion artifact named above contains the full proposed replacement rows in the Section 2 / 3a traceability-updates companion file shape.

---

**End of Section 3b v1.0 LOCKED / APPROVED.**
