# Engineering Specification — Section 3a: Feature Engineering

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v1.0 LOCKED / APPROVED
**Date:** 2026-04-29
**Builder:** Claude
**Section:** Engineering Specification — Section 3a: Feature Engineering
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Section 1 approval note (`docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`)
- Section 2 approval note (`docs/reviews/2026-04-27_spec_02_data_layer_approval.md`)
- Section 2 traceability updates (`docs/reviews/2026-04-27_spec_02_data_layer_traceability_updates.md`)
- Section 3 handoff packet (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`)
- `docs/traceability_matrix.md` v0.3 (Sections 1 and 2 merged)

---

## Changelog

- **v1.0 LOCKED / APPROVED (2026-04-29):** v0.4 DRAFT promoted to v1.0 LOCKED / APPROVED with **no substantive change** to behavior, schema, tests, scope, or ownership. Locking metadata flipped (status header, end-of-document marker) and minor wording cleanup applied to remove stale "v0.X scope" / "v0.X draft" references in current spec body where they are not historical changelog entries — replaced with "v1.0" or "current 03a scope" as appropriate. The historical v0.1 → v0.4 changelog entries are preserved verbatim (only entries already marked as superseded carry the existing supersession notes; nothing else is altered). Approver: Jeremy. Builder: Claude. QA Reviewer: ChatGPT.

- **v0.4 (2026-04-29):** Targeted revisions per Approver-issued QA-driven revision list (third pass). Four changes plus an explicit-non-action; no scope expansion; no Section 2 amendment proposed; no 03b or 03c drafting; no implementation started. v0.3 accepted improvements preserved unless directly affected:
  - **Revision 1 — `feature_run_issues` / blocked-run lifecycle ambiguity resolved.** v0.3 had a contradiction: blocked-run prose said the orchestrator raises "before any row is written" while also requiring a `features.feature_run_issues` row whose `feature_run_id` is a NOT-NULL FK to `features.feature_runs`. The contradiction is resolved by adopting a single lifecycle rule: **the orchestrator opens the `features.feature_runs` row first, *then* validates the snapshot and ingestion-run dependencies; if blocked, the orchestrator marks the run `status='failed'`, populates `error_message` and `completed_at_utc`, writes the appropriate `features.feature_run_issues` row (FK satisfied), and writes no `features.feature_values` rows.** `features.feature_run_issues.feature_run_id` remains NOT NULL and FK-protected. 03a still does not write to `ops.data_quality_exceptions` or any `ops.*` table. Affected sections: §6.3 (lifecycle paragraph rewritten); §6.6 (lifecycle integration note added); §8.2 #21 (test rewritten to verify the open-then-fail lifecycle); §8.2 #22 (text tightened — the run is opened before the block detection); §8.2 #35 (write test now exercises the real lifecycle for the four `*_blocked` and `feature_run_failed` types, not synthetic `feature_run_id` values); §9 edge cases 8, 9, 10 (lifecycle clarified to "no `features.feature_values` rows are written" rather than "before any row is written").
  - **Revision 2 — §12 handoff inventory updated.** The features.* schema bullet now enumerates all four tables: `features.feature_runs`, `features.feature_definitions`, `features.feature_values`, `features.feature_run_issues`. Inventory cleanup only; no behavior change.
  - **Revision 3 — §13 Decision 11 traceability text updated.** The proposed Decision 11 contribution now mentions: `features.feature_runs.data_snapshot_id` linkage; `features.feature_values.feature_run_id` row-level traceability; `features.feature_run_issues` as the feature-layer issue log; explicit note that `ops.data_quality_exceptions` remains ingestion-owned and unmodified by 03a.
  - **Revision 4 — v0.2 changelog clarity note added.** The historical v0.2 changelog bullet describing `ops.data_quality_exceptions` writes via the framework gets a short note that v0.3 Revision 1 superseded that approach. The historical entry itself is **not** deleted (the changelog is a record).
  - **Revision 5 — v0.3 accepted improvements preserved** unless directly affected by Revisions 1–4: 03a writes only to `features.*`; 03a does not write to `ops.data_quality_exceptions` or any `ops.*` table; `features.feature_run_issues` lives inside the `features` schema; `features.feature_run_issues.feature_run_id` is NOT NULL and FK-protected; v0.3 database-level `feature_set_version` integrity (UNIQUE on `feature_runs(feature_run_id, feature_set_version)` plus composite FK from `feature_values`); index-only benchmark behavior (no silent substitution, no secondary-benchmark fallback); eligibility-row omission contract; T-1 trading-day semantics; weekend / holiday / cross-series tests; regime primitive default off; long-form storage; failed-run partial-row consumption discipline.

- **v0.3 (2026-04-29):** Targeted revisions per Approver-issued QA-driven revision list (second pass). Two changes plus an explicit-non-action; no scope expansion; v0.2 accepted improvements preserved unless directly affected:
  - **Revision 1 — `ops.data_quality_exceptions` write path withdrawn; new `features.feature_run_issues` table introduced (Option A).** Per Section 2 v1.0 LOCKED: `ingestion/` is the only emitter of `ops.data_quality_exceptions` rows in Phase 1; the framework remains ingestion-owned. **03a does not write to `ops.data_quality_exceptions` and does not write to any `ops.*` table.** Feature-level data-quality issues (index-only-benchmark inability, blocked invalidated snapshot, blocked failed/partial ingestion-run dependency, failed feature run) are recorded in a new `features.feature_run_issues` table inside the `features` schema. This is a feature-layer issue log, **not** the Section 2 `ops.data_quality_exceptions` framework. v0.2 §8.2 test #34 (no-direct-DQ-write) is removed; replaced by §8.2 tests verifying `features.feature_run_issues` writes and queries. The index-only-benchmark Open Question (§10.1) is preserved as a possible future Section 2 amendment for benchmark price storage only — **no Section 2 amendment is proposed in 03a v0.3**. Affected sections: §1 Purpose; §5.2, §5.3 (write contract); §6 (new §6.6 introducing `features.feature_run_issues`; §6.6 sleeve-aware renumbered to §6.7; §6.7 `data_snapshot_id` linkage renumbered to §6.8); §6.2.4 Family 4 emission language; §8.1 Family 4 test #11(b); §8.2 (#22 ingestion blocking text; old #34 removed; new #34 no-write-to-`ops.*` static check, #35 `feature_run_issues` write test, #36 `feature_run_issues` query test); §9 edge cases 7, 8, 9, 10, 12; §10.1 (replace DQ-framework reference with `feature_run_issues`).
  - **Revision 2 — `feature_set_version` integrity made enforceable at the database level.** A `UNIQUE (feature_run_id, feature_set_version)` constraint is added to `features.feature_runs` so that the pair can be the target of a foreign key. A composite FK `(feature_run_id, feature_set_version) → features.feature_runs(feature_run_id, feature_set_version)` is added to `features.feature_values`. The composite FK to `features.feature_definitions(feature_set_version, feature_name)` from v0.2 is preserved. §6.4 `feature_runs` schema gets the UNIQUE constraint; §6.5 `feature_values` schema gets the second composite FK; §8.2 test #29 (`feature_set_version` consistency) is updated so the *database* (not just the orchestrator) rejects mismatches; §11.4 Implementation defaults updated.
  - **Revision 3 — v0.2 accepted improvements preserved** unless directly affected by Revisions 1–2: eligibility-row omission contract; adjusted-close-only feature inputs; no-provider-import rule; no synthetic `etf_id` for regime primitive; regime primitive default off; long-form feature storage; run-level `data_snapshot_id` linkage with row-level traceability; failed feature runs may retain partial rows with `feature_runs.status='succeeded'` consumption discipline; T-1 trading-day semantics; weekend / holiday / cross-series alignment tests; index-only-benchmark behavior (no silent substitution, no secondary-benchmark fallback).

- **v0.2 (2026-04-29):** Targeted revisions per Approver-issued QA-driven revision list. Seven changes; no scope expansion; v0.1 accepted defaults preserved unless directly affected:
  - **Revision 1 — Eligibility-row omission contract resolved.** 03a does **not** write `features.feature_values` rows for ETF/date pairs that are not rank-eligible per `universe.etf_eligibility_history` as of signal date `T`. The eligibility history is the canonical as-of-date gate. v0.1 §10.9 is removed from Open Questions and added to Approver-resolved defaults (§11.5). Affected sections updated consistently: §2 (Decisions 3, 4, 16), §3, §5.3, §6.5 (nullable explanation), §8.1 Family 1 test 3(c), §9 edge cases 1–2, §10, §11.5.
  - **Revision 2 — Write contract clarified for `ops.data_quality_exceptions`.** 03a writes primary outputs to `features.*` and may also write warning/fail records to `ops.data_quality_exceptions` **only via the approved `common/` data-quality framework** when feature-level data-quality issues occur (e.g., index-only benchmark). 03a does not write to `universe.*`, `prices.*`, `targets.*`, `models.*`, MLflow, or any provider table. §5.2, §5.3, §8.1 Family 4 test #11 updated. *(Superseded by v0.3 Revision 1: per Section 2 v1.0 LOCKED, `ingestion/` is the only emitter of `ops.data_quality_exceptions` rows in Phase 1, so 03a does not write to that table at all; feature-layer issues are recorded in the new `features.feature_run_issues` table inside the `features` schema. This historical bullet is retained as a record of the v0.2 state.)*
  - **Revision 3 — Regime primitive storage ambiguity removed.** v0.1's reference to a synthetic `etf_id` or a separate small table for the SPY-vs-200dma primitive is removed. The primitive remains default off. If later activated within 03a, it must be materialized as repeated rows for each eligible ETF/date using real `etf_id` values; otherwise it defers to a future `regime/` package and a future schema amendment. **No new table is introduced in 03a v0.2.** §6.2.5, §10.6 updated.
  - **Revision 4 — Feature-run atomicity contract clarified.** Feature runs may write in transactional batches; failed runs may retain partial `features.feature_values` rows; downstream consumers must filter on `features.feature_runs.status='succeeded'`. §6.5 (atomicity contract), §9 edge case 12 updated. New cross-cutting test added in §8.2 verifying failed-run rows are excluded from downstream-consumable surfaces.
  - **Revision 5 — Referential integrity between `feature_values` and `feature_definitions` made explicit (Option A, Implementation default).** A `feature_set_version` column is added to `features.feature_values` with a composite FK `(feature_set_version, feature_name) → features.feature_definitions(feature_set_version, feature_name)`. New consistency test added in §8.2 verifying `feature_values.feature_set_version` matches the linked `feature_runs.feature_set_version`. §6.5, §11.4 updated.
  - **Revision 6 — T-1 trading-day semantics defined explicitly.** `T` is the signal date. `T-1` means the most recent valid trading day strictly before `T` for the relevant ETF (and, where applicable, its benchmark) per `prices.etf_prices_daily`, **not** calendar date minus one. All feature windows count valid trading days. §6.1 updated. New tests added in §8.2 covering weekend/holiday alignment for ETF and benchmark.
  - **Revision 7 — v0.1 accepted defaults preserved** unless directly affected by Revisions 1–6: feature families and windows; long-form storage; run-level `data_snapshot_id` linkage with row-level traceability; raw values only (no cross-sectional transforms in 03a); regime primitive default off; liquidity feature omitted; `missing_data.rule = "null_on_any_missing_input_in_window"`; index-only benchmark Open Question (§10.1) and interim 03a behavior preserved.

- **v0.1 (2026-04-29):** Initial draft per Approver-confirmed Section 3 handoff packet (2026-04-28) and the Approver-issued 03a-specific drafting direction (2026-04-29). Eleven-field EW §3.2 template populated. Approver direction visibly applied:
  - The 3a / 3b / 3c split is authorized; 03c canonical filename is `03c_model_layer_mlflow.md`.
  - Regime scope narrowed: 03a may define feature-side primitives only where genuinely needed; the full `regime/` subpackage, `regime.*` schema, and SDR Decision 9 reporting layer remain outside 03a.
  - Index-only benchmark issue: benchmark-relative features require an ETF-backed benchmark with `etf_id` and adjusted-close history; index-only benchmarks render benchmark-relative features unavailable for that ETF/date; flagged as Open Question for Approver / possible future Section 2 amendment; **no silent benchmark substitution** is permitted.

---

## 1. Purpose

`features/` computes ETF features from data already in the application database, producing a per-ETF, per-as-of-date feature surface that downstream sections consume:

- **03b — Target generation** aligns regression and classification targets to the same `(etf_id, as_of_date)` axis 03a establishes.
- **03c — Model layer + MLflow** consumes features and targets to fit baseline models, calibrate probabilities, register runs to MLflow, and produce rankings.
- **04 — Backtest / Attribution / Validation** consumes the same feature surface inside the walk-forward harness.

Section 3a is responsible for what features are computed, how they are aligned in time, what they consume, what they produce, and how they tie back to a reproducible data snapshot. Section 3a is **not** responsible for what to do with the features (target generation, model fitting, ranking, calibration, model promotion).

The principal architectural cash-out points 03a inherits are:

- **SDR Decision 16 / Section 1 invariant 7 — time-aware research auditability.** Every feature row supports point-in-time reconstruction. T-1 alignment is enforced and tested.
- **SDR Decision 2 / Section 1 invariant 1 — provider-abstraction boundary.** No module under `features/` imports from `providers/` or any provider-specific library.
- **Section 2 v1.0 — adjusted-price convention.** `adjusted_close` is the canonical research price for every feature. Any use of unadjusted prices in research calculations requires explicit Approver approval and a Section 2 amendment.
- **Section 2 v1.0 — `data_snapshot_id` reproducibility anchor.** Feature outputs are linked to `ops.data_snapshots` so that any feature row is traceable to a specific snapshot of provider data, universe configuration, code commit, and config commit.

---

## 2. Relevant SDR decisions

03a directly implements or respects:

- **Decision 1 — Project Scope and Phase 1 Boundaries.** ETF-only; no fundamentals, holdings, news, earnings, options, individual stocks, or autonomous research agents in any 03a feature.
- **Decision 2 — Data Provider and Provider-Switching Strategy.** No `features/` module calls EODHD or any provider-specific library directly. All inputs flow through Postgres, populated by `ingestion/` per Section 2.
- **Decision 3 — ETF Universe and Eligibility Rules.** Features are computed only for ETFs in the loaded universe; the 2-year eligibility floor is enforced via `etf_eligibility_history` (no signal-date feature on a date earlier than the canonical `effective_start_date` with `is_rank_eligible=true`). **03a does not write `features.feature_values` rows for ETF/date pairs that are not rank-eligible per `universe.etf_eligibility_history` as of signal date `T`** — the eligibility history is the canonical as-of-date gate, and ineligible rows are absent from the feature surface, not stored with a flag.
- **Decision 4 — Universe Survivorship and ETF Launch-Date Handling.** **No `features.feature_values` row is written** for an ETF/date pair where `T < first_traded_date(e)` or `T >= delisted_date(e)`. No ranking before `eligible_start_date` (the floor); the `etf_eligibility_history` row with `is_rank_eligible=true` is the canonical as-of-date gate. ETF lifecycle fields on `universe.etfs` are the authoritative once-set bounds.
- **Decision 5 — Benchmark, Sleeve, and Diversifier Treatment.** Each ETF's `primary_benchmark_id` is the source of the ETF's primary benchmark for benchmark-relative features. Sleeve assignments are read from `universe.etfs.sleeve_id` but are not modified by 03a. The allowed values and semantics for `rank_method` are owned by 03c (forward reference); 03a does not read or interpret `rank_method`.
- **Decision 6 — Target Design and Ranking Objective.** 03a does **not** define targets. Lookback windows and feature horizons are chosen to support the 63-day and 126-day forward target horizons that 03b will define, but 03a does not generate labels.
- **Decision 7 — Validation, Calibration, and Backtest Confidence Level.** 03a does **not** implement walk-forward validation or calibration. Feature alignment supports later walk-forward harness construction in Section 4 by maintaining T-1 signal-date semantics on every feature row.
- **Decision 9 — Regime Taxonomy and Reporting.** Per Approver direction, 03a may define **feature-side primitives only where genuinely needed for feature engineering** (e.g., an SPY-above-200-day-moving-average primitive used as a feature input). The full `regime/` subpackage, `regime.*` schema, and Decision 9 reporting layer remain outside 03a (Sections 3 and 4 own those per Section 1's *Architectural areas*). Phase 1 default for the regime feature primitive is **off** in `config/features.yaml`; activation requires explicit Approver direction.
- **Decision 11 — Model Tracking, Attribution, Data Quality, and Lightweight MLOps.** Feature-run metadata is anchored to `ops.data_snapshots` per Section 2's reproducibility contract. The MLflow client-side integration on the writer side is owned by 03c (forward reference); 03a does **not** write to MLflow.
- **Decision 16 — Phase 1 Success Criteria and Bias Controls.** Section 1 invariant 7 (time-aware research auditability) is principally cashed out at the feature level by 03a. Look-ahead bias is controlled by T-1 alignment on every feature; survivorship bias is controlled by gating feature generation on `etf_eligibility_history` and ETF lifecycle fields, with **ineligible ETF/date pairs absent from `features.feature_values` rather than stored with a flag**; reproducibility is controlled by `data_snapshot_id` linkage at the feature-run level.

03a does **not** implement the following SDR decisions in any form: Decisions 8 (transaction costs — Section 4), 10 (portfolio rules — Section 5), 12 (model promotion gates — Section 4 and Section 5 for the gate mechanics; 03c for the model state column), 13 (LLM advisory — process), 14 (Danelfin — deferred), 15 (broker strategy — Section 5), 17 (UI — Section 6), 18 (deployment — Section 1).

---

## 3. In scope

03a covers the following at the specification level:

- **Feature families** for Phase 1, defined as named feature primitives with formula-level descriptions, lookback windows, and inputs (the formal list is in *Data contracts → Feature families* below).
- **Feature alignment rules** ensuring every feature on signal date `T` uses only `prices.etf_prices_daily` rows where `as_of_date <= T - 1` (T-1 alignment, with T-1 defined as the most recent valid trading day strictly before `T` per §6.1).
- **Eligibility-row omission contract** ensuring `features.feature_values` rows are written **only** for ETF/date pairs that are rank-eligible per `universe.etf_eligibility_history` as of signal date `T` and that lie within the ETF's lifecycle bounds (`first_traded_date <= T < delisted_date`, where `delisted_date` is open-ended `NULL` for active ETFs).
- **Adjusted-close usage** as the canonical research price across all feature computations; raw OHLCV is not used in any 03a feature.
- **Benchmark-relative feature inputs** sourced from each ETF's `primary_benchmark_id` per Section 2's `universe.etfs` schema, with the ETF-backed-benchmark interim constraint per Approver direction (see *Open questions*).
- **Sleeve-aware feature considerations** at the read-only level: sleeve assignments influence which benchmark each ETF's benchmark-relative feature uses (because the benchmark assignment is per-ETF and per-sleeve), but 03a does not modify `universe.etfs.sleeve_id` or any sleeve assignment.
- **`features.*` schema requirements** at the spec level (table shapes, key columns, constraints, indexes). Concrete migration filenames continuing from Section 2's `0001_initial_setup.sql` are assigned at module-build time, not in this spec.
- **`config/features.yaml`** structure, validation rules, and version-tracking convention.
- **`data_snapshot_id` linkage** at the feature-run level, with row-level traceability via `feature_run_id`.
- **Feature-side regime primitive** (limited): an SPY-above/below-200-day-moving-average flag may be defined as a feature primitive when genuinely required as a feature input; default off in `config/features.yaml`.
- **Required tests** for each feature family, including known-input / known-output tests, T-1 look-ahead tests, no-provider-import tests, survivorship and lifecycle tests, and `data_snapshot_id` linkage tests.
- **Edge cases and failure behavior** at the feature level (missing data, insufficient history, benchmark gaps, non-overlapping trading history, stale data, invalidated snapshots, partial/failed ingestion runs).

---

## 4. Out of scope

The following are **not** owned by 03a; they are owned by the sections and phases noted:

- **Target generation** (regression and classification targets, forward excess return labels, overlapping-label handling, label alignment to 63/126-day horizons) — **03b**.
- **Baseline model implementations, calibration pipeline, MLflow writer-side integration, model registry schema (`models.*`), model state lifecycle (Active/Warning/Paused/Retired), allowed values for `rank_method`, `config/model.yaml`** — **03c**.
- **Walk-forward harness, purge/embargo enforcement, transaction-cost application, backtest result evaluation, attribution storage tables** — **Section 4**.
- **Full `regime/` subpackage, `regime.*` schema, SDR Decision 9 reporting layer, regime consumption by the backtester or portfolio rules** — **Sections 3 (regime computation outside 03a) and 4 (regime consumption)**.
- **Portfolio rules, BUY/HOLD/TRIM/SELL/REPLACE/WATCH actions, paper portfolio state, broker-neutral order intent** — **Section 5**.
- **Dash UI screens, including any UI surface that visualizes features** — **Section 6**.
- **New data providers** beyond the EODHD adapter Section 2 implements — out of scope per Approver direction (Section 2 v1.0 LOCKED).
- **Live trading or broker integration** — out of scope per SDR Decisions 1, 15, 18 and Section 1 invariant 2.
- **Fundamentals, ETF holdings, news, earnings transcripts, options data, Danelfin, individual stocks, autonomous research agents, commercial / customer-facing features** — out of scope per SDR Decision 1.
- **Modifications to Section 1 v1.0 LOCKED architectural invariants or to Section 2 v1.0 LOCKED constraints** — any such modification requires a Section 1 or Section 2 amendment with Approver approval per EW §3.3 and §2.3.
- **Modifications to sleeve assignments, benchmark assignments, ETF universe membership, or eligibility rules** — locked in Section 2 schema and `config/universe.yaml`; changes require the Approval Matrix path.
- **Use of unadjusted prices in any 03a feature calculation** — forbidden by the Section 2 v1.0 adjusted-price convention without explicit Approver approval and a Section 2 amendment.

---

## 5. Inputs and outputs

### 5.1 System inputs to `features/`

- **`prices.etf_prices_daily`** — `adjusted_close` is the canonical research price; `(etf_id, as_of_date)` is the primary research key. `provider_name`, `provider_symbol`, and `ingestion_run_id` are read where needed for lineage and for filtering against partial / failed runs.
- **`universe.etfs`** — `etf_id`, `current_ticker`, `primary_benchmark_id`, `secondary_benchmark_id` (read-only — not used by Phase 1 03a features unless explicitly added), `sleeve_id`, `inception_date`, `first_traded_date`, `eligible_start_date`, `active`, `delisted_date`, `replacement_etf_id`.
- **`universe.etf_eligibility_history`** — canonical for the actual eligibility timeline; consulted via the Section 2 as-of-date SQL view to determine whether an ETF is rank-eligible on a given signal date.
- **`universe.benchmarks`** — `benchmark_id`, `etf_id` (the benchmark's backing ETF, when present), `index_symbol` (when the benchmark is index-only), `display_name`. Used to resolve each ETF's `primary_benchmark_id` to a price series for benchmark-relative features.
- **`ops.data_snapshots`** — pinned, reproducible data set for a feature run. The reproducibility anchor.
- **`ops.ingestion_runs`** — read by 03a only to verify that the ingestion runs covering the snapshot's price data are not `failed` and (Phase 1 default) not `partial`. Per-symbol-aware partial handling via `chunk_results` is explicitly **not** in 03a scope.
- **`config/features.yaml`** — feature parameters. Version-tracked via `feature_set_version`.
- **`config/universe.yaml`** — read only via Section 2's loaded universe structures (not directly by 03a). 03a does not modify or interpret the `pending_section_3` `rank_method` sentinels left by Section 2 — 03c owns that closure.

### 5.2 System outputs from `features/`

- **`features.feature_runs`** — one row per feature run; the reproducibility anchor on the writer side.
- **`features.feature_definitions`** — one row per feature for the active `feature_set_version`; the catalog of what features exist, their formula descriptions, lookbacks, and inputs.
- **`features.feature_values`** — long-form `(etf_id, as_of_date, feature_name, feature_set_version, feature_run_id, feature_value)` rows; the actual feature surface consumed by 03b, 03c, and Section 4.
- **`ops.data_quality_exceptions`** *(read-only from 03a's perspective; not written by 03a)* — per Section 2 v1.0 LOCKED, `ingestion/` is the only emitter of `ops.data_quality_exceptions` rows in Phase 1. **03a does not write to `ops.data_quality_exceptions`.** Feature-level data-quality issues are recorded in `features.feature_run_issues` (see below) instead.
- **`features.feature_run_issues`** — feature-layer issue log. One row per feature-run-level data-quality event (index-only-benchmark inability, blocked invalidated snapshot, blocked failed/partial ingestion-run dependency, failed feature run). Schema and semantics defined in §6.6. **This is a feature-layer issue log, not the Section 2 `ops.data_quality_exceptions` framework.** Activation of a future Section 2 amendment that opens `ops.data_quality_exceptions` to feature-level emitters is out of current 03a scope.

03a writes **only** to the `features` schema (`feature_runs`, `feature_definitions`, `feature_values`, `feature_run_issues`). 03a does **not** write to `universe.*`, `prices.*`, **any `ops.*` table** (read-only), `targets.*` (03b), `models.*` (03c), MLflow, or any provider table. 03a does **not** write to MLflow. 03a does **not** write to `ops.data_quality_exceptions` under any circumstance.

### 5.3 Module-level input/output summary

| Module (within `features/`) | Reads | Writes |
|---|---|---|
| Configuration loader | `config/features.yaml` (via `common/`) | (none) |
| Snapshot validator | `ops.data_snapshots`, `ops.ingestion_runs` | `features.feature_run_issues` on invalidated/failed/partial-run conditions |
| Feature catalog initializer | `config/features.yaml`, `features.feature_runs` | `features.feature_definitions` |
| Returns / momentum calculator | `prices.etf_prices_daily`, `universe.etfs`, `universe.etf_eligibility_history` | `features.feature_values` |
| Volatility calculator | `prices.etf_prices_daily`, `universe.etfs`, `universe.etf_eligibility_history` | `features.feature_values` |
| Trend-strength calculator | `prices.etf_prices_daily`, `universe.etfs`, `universe.etf_eligibility_history` | `features.feature_values` |
| Benchmark-relative calculator | `prices.etf_prices_daily`, `universe.etfs`, `universe.etf_eligibility_history`, `universe.benchmarks` | `features.feature_values`; `features.feature_run_issues` on index-only-benchmark conditions per §6.2.4 |
| Regime-primitive calculator (default off) | `prices.etf_prices_daily` (SPY series), `universe.etfs` | `features.feature_values` (only when activated and only with real `etf_id` values per §6.2.5) |
| Feature-run orchestrator | All of the above | `features.feature_runs` (open / close), `features.feature_values` (in transactional batches per §6.5 atomicity contract); `features.feature_run_issues` for run-level conditions |

No 03a module writes to `ops.data_quality_exceptions` or any other `ops.*` table. All feature-layer data-quality issues land in `features.feature_run_issues` per §6.6.

---

## 6. Data contracts

### 6.1 Feature alignment rule (T-1)

**Definition of `T` and `T-1`.** `T` is the **signal date** — the calendar date for which a feature row is produced and stamped (`features.feature_values.as_of_date = T`). For any feature input series referencing an ETF `e` (or, where applicable, a benchmark ETF `b`), `T-1` denotes the **most recent valid trading day strictly before `T`** for that series — that is, the maximum `prices.etf_prices_daily.as_of_date < T` for the relevant ETF. **`T-1` is not a calendar date minus one day**; it skips weekends, holidays, and any other days on which the relevant ETF has no price row in `prices.etf_prices_daily`.

**Consequences:**

- For any signal date `T` and any feature, the inputs to that feature are bounded by `prices.etf_prices_daily.as_of_date <= T - 1` for the relevant ETF (and, for benchmark-relative features, also for the benchmark ETF, with `T-1` evaluated independently against each series' own trading calendar).
- All feature window counts in §6.2 (`w` trading days) are **trading-day** counts, not calendar-day counts, and they walk backwards through `prices.etf_prices_daily` rows for the relevant ETF.
- The feature row is stamped with `as_of_date = T` (the signal date), but its computation uses only data available through that ETF's `T-1`.
- The trading-calendar semantics themselves are owned by Section 2 (the set of dates with rows in `prices.etf_prices_daily` is the operative trading calendar).

This is the principal cash-out of SDR Decision 16's look-ahead-bias control at the feature level. The trading-day semantics are tested for weekend and holiday boundaries (per §8.2) so that "T-1 = calendar T - 1" is never silently assumed.

**Cross-series alignment.** When a feature uses two or more series (e.g., Family 4 uses an ETF and its benchmark ETF), each series' `T-1` is resolved independently against its own trading-day index, and the feature is null on signal dates where the two series do not both have valid trading-day rows within the lookback window (per `missing_data.rule = "null_on_any_missing_input_in_window"` and per §6.2.4 / §9 edge case 5 for non-overlapping history).

### 6.2 Feature families (Phase 1)

The Phase 1 feature set is defined here at the formula and lookback level. Concrete window choices are the Builder's *Proposed default requiring Approver approval* (see *Open questions*).

For all formulas below, `adj_close(e, d)` denotes `prices.etf_prices_daily.adjusted_close` for `etf_id = e` on `as_of_date = d`. Trading days are calendar days on which `prices.etf_prices_daily` has rows for the relevant ETF (Section 2 owns the trading-calendar semantics).

#### Family 1 — Returns / momentum

**Feature names (Phase 1 proposed):** `return_21d`, `return_63d`, `return_126d`, `return_252d`.

**Formula (window `w`, signal date `T`):**

```
return_w(e, T) = adj_close(e, T-1) / adj_close(e, T-1-w) - 1
```

The window `w` counts trading days. Both endpoints are bounded by `T - 1`.

**Inputs:** `prices.etf_prices_daily.adjusted_close`.

**Notes:** The 63-day and 126-day windows align with the SDR Decision 6 forward-target horizons that 03b will define. 252-day momentum is included as a longer-horizon signal commonly used in tactical ETF research; activation is a Builder Proposed default.

#### Family 2 — Realized volatility

**Feature names (Phase 1 proposed):** `vol_realized_21d`, `vol_realized_63d`, `vol_realized_126d`.

**Formula (window `w`, signal date `T`):** standard deviation of daily log-returns of `adj_close` over the `w` trading days ending at `T - 1`. Whether the feature is annualized (e.g., multiplied by `sqrt(252)`) is the Builder's *Proposed default requiring Approver approval*; the proposal is **annualized by `sqrt(252)`** for ease of cross-feature interpretation, with the annualization factor recorded in `features.feature_definitions`.

**Inputs:** `prices.etf_prices_daily.adjusted_close`.

#### Family 3 — Trend strength (distance from moving average)

**Feature names (Phase 1 proposed):** `trend_dist_sma_50`, `trend_dist_sma_200`.

**Formula (SMA window `w`, signal date `T`):**

```
trend_dist_sma_w(e, T) = adj_close(e, T-1) / SMA_w(adj_close(e), ending T-1) - 1
```

where `SMA_w(...)` is the simple moving average over the `w` trading days ending at `T - 1`.

**Inputs:** `prices.etf_prices_daily.adjusted_close`.

#### Family 4 — Benchmark-relative excess return

**Feature names (Phase 1 proposed):** `excess_return_vs_primary_benchmark_63d`, `excess_return_vs_primary_benchmark_126d`.

**Formula (window `w`, signal date `T`, ETF `e` with primary benchmark backed by ETF `b`):**

```
excess_return_vs_primary_benchmark_w(e, T) = return_w(e, T) - return_w(b, T)
```

where `return_w(...)` is computed identically per Family 1, and `b` is resolved by joining `universe.etfs.primary_benchmark_id` to `universe.benchmarks.benchmark_id` and reading `universe.benchmarks.etf_id`.

**Inputs:** `prices.etf_prices_daily.adjusted_close` for both `e` and `b`; `universe.etfs.primary_benchmark_id`; `universe.benchmarks.etf_id`.

**Interim constraint (per Approver direction in 03a handoff):** This feature family is computed **only** when the primary benchmark resolves to an ETF-backed benchmark with a non-null `etf_id` and adjusted-close history covering the required window. When the primary benchmark is index-only (`universe.benchmarks.index_symbol` set, `etf_id` null), the feature is **null/absent** for that ETF/date and a `severity='warning'` row is recorded in `features.feature_run_issues` (the feature-layer issue log defined in §6.6) — **not** in `ops.data_quality_exceptions`, which is ingestion-owned per Section 2 v1.0 LOCKED. **No silent benchmark substitution is permitted.** This is flagged as an Open Question for Approver / possible future Section 2 amendment in *Open questions*.

The 63-day and 126-day windows align with SDR Decision 6's forward-target horizons.

#### Family 5 — Regime-side feature primitive (limited; default off)

**Feature names (Phase 1 proposed):** `regime_spy_above_sma_200`.

**Formula (signal date `T`):**

```
regime_spy_above_sma_200(T) = 1 if adj_close('SPY', T-1) > SMA_200(adj_close('SPY'), ending T-1) else 0
```

**Storage shape (only relevant when activated).** This primitive is **default off** in `config/features.yaml`. While disabled, no rows are written and no SPY data is read by the regime calculator. **No new table is introduced in 03a v1.0.** If the primitive is later activated within 03a's scope, it must be materialized in `features.feature_values` as **repeated rows for each eligible ETF/date using real `etf_id` values** (the value is identical across ETFs on a given signal date because the primitive is market-wide; the storage repetition is the cost of preserving FK integrity to `universe.etfs`). Alternatively, activation may be deferred to the future `regime/` package and a future schema amendment owned by Section 3 (regime computation outside 03a) and Section 4 (regime consumption / reporting); that path requires a Section 1 / Section 2 amendment for the `regime.*` schema and is out of current 03a scope. **A synthetic `etf_id` is not used** — `features.feature_values.etf_id` is FK to `universe.etfs.etf_id` and may not carry placeholder values.

**Inputs:** `prices.etf_prices_daily.adjusted_close` for the SPY ETF.

**Scope note.** This primitive is a *feature input* for downstream models that may benefit from a market-trend regime input. It is **not** the SDR Decision 9 regime-reporting layer; that lives in `regime/` and is owned by Sections 3 (computation, outside 03a) and 4 (consumption / reporting). 03a defines this primitive only because the Approver-confirmed handoff allows feature-side regime primitives "where genuinely needed." Activation in Phase 1 requires explicit Approver approval per EW §3.3 (this entry is a Proposed default; default is off).

### 6.3 `features.feature_runs`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `feature_run_id` | `bigserial` | PK | surrogate key |
| `data_snapshot_id` | `bigint` | not null, FK → `ops.data_snapshots` | reproducibility anchor |
| `feature_set_version` | `text` | not null | matches `config/features.yaml` `feature_set_version` |
| `commit_hash` | `text` | not null | code commit at run start |
| `config_hash` | `text` | not null | hash of `config/features.yaml` at run start |
| `started_at_utc` | `timestamptz` | not null default `now()` | |
| `completed_at_utc` | `timestamptz` | nullable | |
| `status` | `text` | not null, CHECK in (`'running'`, `'succeeded'`, `'failed'`) | |
| `error_message` | `text` | nullable | populated on `'failed'` |
| `created_by` | `text` | not null | container or user identifier |
| `notes` | `text` | nullable | free-form |
| | | **UNIQUE (`feature_run_id`, `feature_set_version`)** | per Revision 2 (v0.3); enables the composite FK from `features.feature_values` defined in §6.5 |

Index on `data_snapshot_id` to support reproducibility queries.

The `UNIQUE (feature_run_id, feature_set_version)` constraint is functionally redundant with the PK on `feature_run_id` (because `feature_run_id` alone is unique, the pair is also unique), but is required as a constraint object so that PostgreSQL accepts the composite foreign key from `features.feature_values(feature_run_id, feature_set_version)` referencing it. This is a standard pattern for enforcing cross-table integrity on a derived attribute (`feature_set_version` is set once at run open and is immutable for the life of the row).

**Blocked-run lifecycle (v0.4 Revision 1).** The feature-run orchestrator opens the `features.feature_runs` row (with `status='running'`) **before** validating the selected `data_snapshot_id`, the snapshot's `status`, and the ingestion-run dependencies covering the snapshot's price data. If any of those validations fail — i.e., the snapshot's `status='invalidated'`, or the snapshot depends on `ops.ingestion_runs` rows with `status='failed'` or (Phase 1 default) `status='partial'` — the orchestrator (a) marks the run row `status='failed'`, (b) populates `error_message` and `completed_at_utc`, (c) writes the appropriate `features.feature_run_issues` row (FK to `features.feature_runs(feature_run_id)` is satisfied because the run row is already open), and (d) writes **no** `features.feature_values` rows for that run. This sequence resolves the v0.3 lifecycle ambiguity: the run row exists for FK purposes; no value rows leak into the consumable surface (downstream consumers filter on `status='succeeded'` per §6.5); and feature-layer issues land in `features.feature_run_issues` per §6.6 — never in `ops.data_quality_exceptions`.

### 6.4 `features.feature_definitions`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `feature_set_version` | `text` | not null | |
| `feature_name` | `text` | not null | e.g., `return_63d` |
| `family` | `text` | not null | one of `returns_momentum`, `volatility`, `trend_strength`, `benchmark_relative`, `regime_primitives` |
| `formula_description` | `text` | not null | plain-English formula reference |
| `lookback_days` | `integer` | not null | trading-day lookback |
| `inputs_described` | `text` | not null | summary of which columns / tables are read |
| `parameters` | `jsonb` | nullable | family-specific parameters (e.g., annualization factor, SMA window) |
| | | PK (`feature_set_version`, `feature_name`) | |

Populated at orchestrator startup by reading `config/features.yaml` for the active version. Existing rows for prior `feature_set_version` values are retained for audit; only the active version is consulted by feature-value writes.

### 6.5 `features.feature_values`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `etf_id` | `bigint` | not null, FK → `universe.etfs` | |
| `as_of_date` | `date` | not null | signal date `T` |
| `feature_name` | `text` | not null | matches `features.feature_definitions.feature_name` |
| `feature_set_version` | `text` | not null | matches `features.feature_runs.feature_set_version` for the linked run; participates in both composite FKs below |
| `feature_run_id` | `bigint` | not null | participates in the composite FK to `features.feature_runs` below; the legacy single-column FK on `feature_run_id` alone is **not** declared, because the composite FK already enforces existence of the referenced run |
| `feature_value` | `numeric(24,12)` | nullable | null permitted for missing-data, insufficient-history, non-overlapping benchmark history, and index-only-benchmark cases (see *Nullable-value semantics* below) |
| | | PK (`etf_id`, `as_of_date`, `feature_name`, `feature_run_id`) | `feature_set_version` is determined by `feature_run_id` and so does not enter the PK |
| | | Composite FK (`feature_run_id`, `feature_set_version`) → `features.feature_runs(feature_run_id, feature_set_version)` | per Revision 2 (v0.3, Implementation default); enforces at the database level that `feature_values.feature_set_version` matches the linked run's `feature_set_version` (any mismatch is rejected by the database, not only by the orchestrator) |
| | | Composite FK (`feature_set_version`, `feature_name`) → `features.feature_definitions(feature_set_version, feature_name)` | per v0.2 Revision 5 (Implementation default — Option A); ensures every value row corresponds to a catalogued feature in the active version |

Indexes:
- `(feature_run_id)` for run-scoped queries (e.g., audit, idempotency checks, exclusion of failed-run rows).
- `(etf_id, as_of_date)` for primary research queries.
- `(feature_name, as_of_date)` for cross-sectional research queries.
- `(as_of_date)` for time-slice queries.

**Nullable-value semantics.** A null `feature_value` indicates that the feature was attempted but could not be computed for that ETF/date due to one of: missing input bar within the lookback window per `missing_data.rule = "null_on_any_missing_input_in_window"`; insufficient history (fewer than `w + 1` trading days available on `as_of_date <= T - 1`); non-overlapping trading-day history between the ETF and its benchmark for Family 4; or the index-only-benchmark interim constraint per §6.2.4 / §10.1. **Ineligibility on signal date `T` does not produce a null value — it produces no row at all** (per Revision 1 / §11.5). Lifecycle bounds (`T < first_traded_date(e)` or `T >= delisted_date(e)`) likewise produce no row.

**Atomicity contract (Revision 4).** Feature runs may write `features.feature_values` **in transactional batches** rather than in one massive transaction; the natural batch unit is a (calculator, ETF, signal-date-window) tuple, with the exact batching strategy a module-build-time choice. **Failed feature runs may retain partial `features.feature_values` rows** (rows from batches that committed before the failure). Downstream consumers — 03b, 03c, Section 4 — must **only consume `features.feature_values` rows whose `feature_run_id` links to a `features.feature_runs.status='succeeded'` row**. Consumption discipline is enforced by §8.2 cross-cutting tests; the schema deliberately does not delete partial rows on failure (the run row carries the truth via `status`).

The PK includes `feature_run_id` so that successive runs against the same snapshot are append-only and distinguishable; idempotency is verified by comparing values across two `'succeeded'` runs sharing the same `data_snapshot_id`, `feature_set_version`, `commit_hash`, and `config_hash` — see *Required tests*.

### 6.6 `features.feature_run_issues`

This is the **feature-layer issue log**, introduced in v0.3 per Revision 1. It records data-quality and operational issues that arise during a feature run. **It is not the Section 2 `ops.data_quality_exceptions` framework**; that framework remains ingestion-owned per Section 2 v1.0 LOCKED. The two are deliberately separate: `ops.data_quality_exceptions` is the cross-cutting nine-field SDR Decision 11 report owned by `ingestion/`; `features.feature_run_issues` is a narrower, feature-run-scoped log used by 03a (and read by Section 6 UI surfaces and by 03c / Section 4 consumers as needed).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `feature_run_issue_id` | `bigserial` | PK | surrogate key |
| `feature_run_id` | `bigint` | not null, FK → `features.feature_runs(feature_run_id)` | which run produced the issue |
| `issue_type` | `text` | not null, CHECK in (`'index_only_benchmark'`, `'invalidated_snapshot_blocked'`, `'failed_ingestion_run_blocked'`, `'partial_ingestion_run_blocked'`, `'feature_run_failed'`) | closed enumeration; new types require an 03a amendment |
| `severity` | `text` | not null, CHECK in (`'warning'`, `'fail'`) | `'warning'` for index-only-benchmark; `'fail'` for the four blocking conditions |
| `etf_id` | `bigint` | nullable, FK → `universe.etfs` | populated when the issue is per-ETF (e.g., index-only benchmark for that ETF); null for run-level issues |
| `as_of_date` | `date` | nullable | signal date the issue applies to, when applicable; null for run-level issues |
| `affected_feature_name` | `text` | nullable | feature name the issue applies to, when applicable (e.g., `excess_return_vs_primary_benchmark_63d`); null for run-level issues |
| `summary` | `text` | not null | short, structured summary suitable for UI display |
| `detail` | `jsonb` | nullable | structured detail (e.g., the offending `benchmark_id`, the `ingestion_run_id` that blocked the run, the failure exception message); free-form within the closed `issue_type` |
| `created_at_utc` | `timestamptz` | not null default `now()` | |

Indexes:
- `(feature_run_id)` for run-scoped issue queries.
- `(issue_type)` for type-scoped queries.
- `(etf_id, as_of_date)` for ETF/date-scoped queries (sparse — many rows have null in these columns).

**Scope and write discipline.**

- **Lifecycle integration with `features.feature_runs` (v0.4 Revision 1).** Every `features.feature_run_issues` row references a real `features.feature_runs` row through the NOT NULL FK on `feature_run_id`. Per the §6.3 blocked-run lifecycle, the orchestrator opens the `features.feature_runs` row (status `'running'`) **before** validating the snapshot and ingestion-run dependencies, so that on a block detection the orchestrator can mark the run `'failed'` and write the `feature_run_issues` row in the same transactional sequence. There is no scenario in 03a in which a `feature_run_issues` row exists without a corresponding `feature_runs` row. The FK is never relaxed.
- 03a writes to `features.feature_run_issues` directly via `common/` database helpers, **not** through the `common.redact_secrets()` utility's exception path (that utility is reserved for `ops.data_quality_exceptions` and `ops.provider_raw_payloads` per Section 2). 03a's `summary` and `detail` fields are written by 03a code from already-internal feature-layer state (snapshot IDs, ingestion run IDs, benchmark IDs, exception messages produced inside `features/`); they do not embed provider-derived text or response fragments, so the Section 2 redaction utility does not apply.
- The closed enumeration on `issue_type` ensures that adding a new issue type is a deliberate spec change, not an ad-hoc string. New types are added under 03a amendments.
- No 03a code path writes to `ops.data_quality_exceptions` under any circumstance (verified by §8.2 test #34).
- A future Section 2 amendment that opens `ops.data_quality_exceptions` to feature-level emitters would be a separate decision out of 03a scope; if that amendment is later approved, a follow-on 03a amendment may migrate (or mirror) some of these issue types into the broader framework. 03a v0.4 does not propose such a migration.

**Consumption.**

- Section 6 UI Model Registry / Run Browser surfaces (read-only) display these issues alongside the `feature_runs` they belong to.
- 03c may read `feature_run_issues` to filter or annotate model runs.
- Section 4 backtest harness may surface these issues in run reports.

### 6.7 Sleeve-aware feature treatment

Sleeve assignments live on `universe.etfs.sleeve_id` (Section 2). 03a reads sleeve assignments where they are needed for feature computation but does not modify them.

In the Phase 1 feature set proposed above, sleeve enters feature computation only via the per-ETF `primary_benchmark_id` assignment (which is itself sleeve-aware per SDR Decision 5). All other Phase 1 feature families (returns/momentum, volatility, trend strength, regime primitive) are sleeve-neutral at the per-ETF level — their formulas do not change based on sleeve. Future feature families that are explicitly sleeve-conditional (e.g., a "diversifier-only" hedge feature) would be added under Approver-approved 03a amendments.

### 6.8 `data_snapshot_id` linkage

Per the Approver-confirmed handoff direction ("data_snapshot_id is the downstream reproducibility anchor and must be part of feature-set outputs or feature-run metadata"), 03a uses **run-level linkage** with **row-level traceability**:

- **Run-level:** `features.feature_runs.data_snapshot_id` is the canonical anchor.
- **Row-level:** `features.feature_values.feature_run_id` is the foreign key that traces every feature row to its run, and via the run to its `data_snapshot_id`.

This satisfies the EW §7 reproducibility list (code commit, config commit, data snapshot, provider, universe version, adjusted-price convention, MLflow run ID) at the schema-shape level: the run row carries `commit_hash`, `config_hash`, and `data_snapshot_id`; the snapshot carries `provider_name`, `provider_dataset_label`, `universe_config_hash`, `universe_version_label`, and `adjusted_price_convention` per Section 2 v0.3. The MLflow run ID itself is owned by 03c and is not stored in `features.*`; 03c links its MLflow runs back to a `feature_run_id` (forward reference).

The granularity choice (run-level + row-level traceability rather than `data_snapshot_id` denormalized onto every `feature_values` row) is classified as a *Proposed default requiring Approver approval* — see *Open questions*.

---

## 7. Config dependencies

### 7.1 `config/features.yaml`

03a owns this file. It is a **Strategy-affecting** config per EW §7 (it defines feature parameters that change what a model sees, and therefore what the platform recommends). Any change requires Approver review per the Approval Matrix.

Proposed Phase 1 shape (classified as *Proposed default requiring Approver approval*):

```yaml
feature_set_version: "0.1"

families:
  returns_momentum:
    enabled: true
    windows_trading_days: [21, 63, 126, 252]

  volatility:
    enabled: true
    windows_trading_days: [21, 63, 126]
    annualization_factor: 15.874507866387544   # sqrt(252)
    annualize: true

  trend_strength:
    enabled: true
    sma_windows_trading_days: [50, 200]

  benchmark_relative:
    enabled: true
    windows_trading_days: [63, 126]
    benchmark_field: primary_benchmark_id      # references universe.etfs
    require_etf_backed_benchmark: true         # interim per Approver direction

  regime_primitives:
    spy_vs_200dma:
      enabled: false                            # Phase 1 default off
      market_etf: "SPY"
      sma_window_trading_days: 200

missing_data:
  rule: "null_on_any_missing_input_in_window"   # Proposed default; alternatives flagged in Open Questions
```

### 7.2 `config/features.yaml` validation rules

Validated at orchestrator startup. Failure raises a structured error and the run does not start (no silent defaulting per EW §7 / Section 1's "no silent default for any field that originates in YAML"):

- `feature_set_version` is a non-empty string.
- Every family key is one of the known closed set: `returns_momentum`, `volatility`, `trend_strength`, `benchmark_relative`, `regime_primitives`. Unknown family keys raise an error (no silent ignore).
- For each enabled family, family-specific required parameters are present and well-typed.
- All window values are positive integers.
- For `volatility`, if `annualize: true`, `annualization_factor` is a positive number.
- For `benchmark_relative`, if `enabled: true`, `require_etf_backed_benchmark: true` is required (interim per Approver direction; flipping this requires resolution of the Open Question and a corresponding Section 2 amendment).
- For `regime_primitives.spy_vs_200dma`, if `enabled: true`, `market_etf` must be the `current_ticker` of an active Phase 1 universe ETF.
- `missing_data.rule` is one of the documented allowed values; Phase 1 default is `"null_on_any_missing_input_in_window"`.

### 7.3 Other config dependencies

- **`config/universe.yaml`** — read indirectly via Section 2's loaded universe structures only. 03a does not read this YAML directly and does not modify it. The `pending_section_3` `rank_method` sentinels are not interpreted by 03a (forward reference: 03c closes them).
- **`.env`** — 03a introduces no new environment variables in this draft. Database credentials and connection parameters are inherited from Section 1 / Section 2's `.env` discipline.

### 7.4 Config commit discipline

Per EW §7, `config/features.yaml` changes use commit messages of the form:

```
config(features): [strategy-affecting] <change summary> per <SDR decision or 03a amendment reference>
```

The `config_hash` recorded on each `features.feature_runs` row is computed over `config/features.yaml` only (for change-detection on the family/window parameters that drive feature computation); the broader `config_hash` on `ops.data_snapshots` is hashed across all config files per Section 2.

---

## 8. Required tests

Tests live under `tests/unit/features/` and `tests/integration/features/`. All tests must run inside the application container per EW §5 (`docker compose exec app pytest tests/unit/features/` and the integration path).

### 8.1 Per-family tests

#### Family 1 — Returns / momentum

1. **Known-input / known-output** — for each window `w in {21, 63, 126, 252}`, a fixture price series produces a hand-computed `return_w` value matching to a documented tolerance.
2. **T-1 alignment** — the feature on signal date `T` does not change when `prices.etf_prices_daily` rows on `as_of_date >= T` are mutated. A mutation test that injects an obviously-wrong price on `as_of_date = T` must not change `return_w(e, T)` for any `w`.
3. **Survivorship and lifecycle (no row written for ineligible / out-of-lifecycle pairs)** —
   (a) **No `features.feature_values` row** is written for `(e, T)` where `T < first_traded_date(e)`.
   (b) **No `features.feature_values` row** is written for `(e, T)` where `T >= delisted_date(e)`.
   (c) **No `features.feature_values` row** is written for `(e, T)` where `etf_eligibility_history` (resolved via Section 2's as-of-date SQL view) does not return a row with `is_rank_eligible=true` covering signal date `T`. Verified by a fixture in which an ETF's eligibility window opens partway through the test period; rows before the window opens must be absent, rows after must be present.
4. **Insufficient history** — for `(e, T)` where fewer than `w + 1` trading days of history exist on `as_of_date <= T - 1`, `return_w(e, T)` is null.
5. **Idempotency** — same `data_snapshot_id`, same `feature_set_version`, same `commit_hash`, same `config_hash` produces the same `feature_value` on re-run (PK distinguishes runs but values are identical).

#### Family 2 — Realized volatility

Tests parallel Family 1, plus:

6. **Annualization correctness** — with `annualize: true` and `annualization_factor: sqrt(252)`, the test on a known-input series produces the expected annualized standard deviation.
7. **Sub-window NaN handling** — if any input bar within the window is missing, the feature is null (per `missing_data.rule = "null_on_any_missing_input_in_window"` Proposed default).

#### Family 3 — Trend strength

Tests parallel Family 1, plus:

8. **SMA correctness** — `SMA_w` on a known input matches a hand-computed value.
9. **Distance-from-SMA correctness** — full feature on a known input matches a hand-computed value.

#### Family 4 — Benchmark-relative excess return

Tests parallel Family 1, plus:

10. **ETF-backed-benchmark resolution** — `excess_return_vs_primary_benchmark_w(e, T)` resolves the benchmark via `universe.etfs.primary_benchmark_id → universe.benchmarks.etf_id` and computes the difference correctly on synthetic series.
11. **Index-only benchmark behavior (two-part test).**
    (a) **No silent benchmark substitution.** When the primary benchmark has `index_symbol` set and `etf_id IS NULL`, `feature_value` for Family 4 is null and `secondary_benchmark_id` is **not** consulted. The test injects a fixture ETF whose primary benchmark is index-only and whose `secondary_benchmark_id` is set to a valid ETF-backed benchmark; the feature must be null, not a value computed against the secondary.
    (b) **Warning row recorded in `features.feature_run_issues`.** A row is written to `features.feature_run_issues` with `issue_type='index_only_benchmark'`, `severity='warning'`, `etf_id` set to the affected ETF, `as_of_date` set to the affected signal date, `affected_feature_name` set to the Family 4 feature, `summary` populated, and `detail` populated with the offending `benchmark_id` and `index_symbol`. The test asserts the row landed with the expected `issue_type`, `severity`, and per-ETF / per-date / per-feature scoping. **No row is written to `ops.data_quality_exceptions`** — verified by asserting that table is unchanged across the test run. The Section 2 framework remains ingestion-owned per Section 2 v1.0 LOCKED.
12. **T-1 alignment for both ETF and benchmark** — the feature does not change when `as_of_date >= T` rows are mutated for either the ETF or its benchmark.
13. **Non-overlapping trading history** — when ETF `e` has price rows on a date that the benchmark does not (or vice versa), the feature is null on that signal date.
14. **Secondary benchmark not consulted in Phase 1 03a (architectural).** A static check or runtime assertion that the benchmark-relative calculator code path under `features/` reads only `primary_benchmark_id` and never `secondary_benchmark_id` from `universe.etfs`. The behavioral consequence (no fallback) is verified by test #11(a); this test backstops the contract at the code-shape level.

#### Family 5 — Regime-side feature primitive (default off)

Tests apply only when `regime_primitives.spy_vs_200dma.enabled: true`:

15. **Known-input / known-output** — synthetic SPY series with hand-computed SMA(200) produces the expected 0/1 flag.
16. **T-1 alignment** — the flag on signal date `T` does not change when `as_of_date >= T` SPY rows are mutated.
17. **Disabled-by-default test** — with the default `enabled: false`, no `regime_spy_above_sma_200` rows are written and no SPY data is read by the regime calculator.

### 8.2 Cross-cutting tests

18. **No-provider-import test** — static check verifying that no module under `quant_research_platform.features` imports from `quant_research_platform.providers`, from `quant_research_platform.ingestion`, or from any provider-specific library (e.g., EODHD client). Failing this is a defect against SDR Decision 2 and Section 1 invariant 1.
19. **Adjusted-close-only test** — a static / source-scan check verifying that no module under `features/` references the columns `raw_open`, `raw_high`, `raw_low`, `raw_close`, or `volume` from `prices.etf_prices_daily` in any feature-computation code path. Phase 1 03a does not use raw OHLCV in any feature; this test backstops the Section 2 adjusted-price convention.
20. **`data_snapshot_id` linkage test** — every `features.feature_values` row is reachable to a non-`'invalidated'` `ops.data_snapshots` row via `feature_run_id`. A mutation test that flips the snapshot's `status` to `'invalidated'` raises a clear error on the next attempted run referencing it.
21. **Invalidated-snapshot rejection test (v0.4 Revision 1).** Starting a feature run with `data_snapshot_id` referencing a snapshot whose `status='invalidated'` produces this lifecycle: (a) the `features.feature_runs` row is opened with `status='running'`; (b) the orchestrator's snapshot validation detects the invalidated status; (c) the run row is updated to `status='failed'` with `error_message` populated and `completed_at_utc` set; (d) a `severity='fail'` row with `issue_type='invalidated_snapshot_blocked'` is written to `features.feature_run_issues` with `feature_run_id` set to the now-failed run and `detail` naming the offending `data_snapshot_id`; (e) **no `features.feature_values` rows are written for that run**. The test asserts each of (a)–(e) and asserts that `ops.data_quality_exceptions` is unchanged.
22. **Ingestion-run consumption test (v0.4 Revision 1 lifecycle).** Starting a feature run when the ingestion runs covering the snapshot's price data include any with `status='failed'` produces this lifecycle: (a) the `features.feature_runs` row is opened with `status='running'`; (b) the orchestrator's ingestion-run validation detects the failed dependency; (c) the run row is updated to `status='failed'` with `error_message` populated and `completed_at_utc` set; (d) a `severity='fail'` row with `issue_type='failed_ingestion_run_blocked'` is written to `features.feature_run_issues` with `feature_run_id` set to the now-failed run and `detail` naming the offending `ingestion_run_id`(s); (e) **no `features.feature_values` rows are written for that run**. The same lifecycle and assertions apply for `'partial'` ingestion runs with `issue_type='partial_ingestion_run_blocked'` (Phase 1 default; per-symbol-aware partial handling is explicitly out of scope). **No row is written to `ops.data_quality_exceptions`.**
23. **Cross-run idempotency** — same `data_snapshot_id`, same `feature_set_version`, same `commit_hash`, same `config_hash` across two `'succeeded'` runs produces identical `feature_value` for every `(etf_id, as_of_date, feature_name)` (modulo PK).
24. **`config/features.yaml` validation tests** — every validation rule in §7.2 is exercised by a passing test for a valid config and a failing test for an invalid config. Unknown family keys raise. Missing required parameters raise. Out-of-type values raise. The test for `require_etf_backed_benchmark: false` raises (interim constraint).
25. **Container-test parity** — every test passes both at host pytest invocation and inside the container via `docker compose exec app pytest tests/unit/features/`. EW §5 treats divergence as a defect.
26. **Feature-catalog initialization test** — at orchestrator startup, `features.feature_definitions` rows for the active `feature_set_version` match the enabled families and parameters in `config/features.yaml` exactly. Disabling a family in YAML and re-running results in the active-version catalog reflecting only the enabled families on the next run; rows for prior versions are retained.
27. **No-secrets-in-features test** — a diff scan over `features/` source, fixtures, and tests confirms no API keys, tokens, passwords, or `.env` contents are committed (Section 1 invariant 6 backstop).
28. **Failed-run exclusion test (Revision 4).** A fixture run is forced to fail mid-execution after some `features.feature_values` rows have been committed in transactional batches. The test asserts:
    (a) the `features.feature_runs` row's `status` is `'failed'` and `error_message` is populated;
    (b) the partial `features.feature_values` rows from that run are still present in the table (no auto-deletion);
    (c) any downstream-consumable query helper exposed by `common/` (or its equivalent canonical query pattern documented in 03a) returns **zero rows** from the failed run when filtering on `features.feature_runs.status='succeeded'`. The test fails if a partial-failed-run row leaks into the consumable surface.
29. **`feature_set_version` consistency test (v0.2 Revision 5; v0.3 Revision 2 strengthens to database-level enforcement).** A fixture attempts to write a `features.feature_values` row whose `feature_set_version` does not match the `feature_set_version` of the linked `features.feature_runs` row (i.e., the pair `(feature_run_id, feature_set_version)` does not exist in `features.feature_runs`). The composite FK `(feature_run_id, feature_set_version) → features.feature_runs(feature_run_id, feature_set_version)` rejects the write **at the database level** (PostgreSQL raises a foreign-key violation). The test asserts:
    (a) the database itself rejects the write (the orchestrator's own pre-write invariant check is bypassed in this test fixture to prove the database constraint stands on its own);
    (b) when the orchestrator's invariant check is in place, it raises a structured error before the database constraint is reached, providing a clearer error message;
    (c) on the success path, every `feature_values` row's `feature_set_version` equals the `feature_runs.feature_set_version` for its `feature_run_id`. The double layer (orchestrator check + database constraint) is intentional: the orchestrator gives clearer messages; the database constraint is the backstop.
30. **Composite FK to `feature_definitions` test (Revision 5).** A fixture attempts to write a `features.feature_values` row with a `feature_name` that does not exist in `features.feature_definitions` for the active `feature_set_version`. The composite FK rejects the write at the database level. Verified for both unknown `feature_name` and mismatched `feature_set_version`.
31. **T-1 trading-day alignment — weekend boundary (Revision 6).** A fixture price series spans a Friday through the following Monday, with no rows on Saturday or Sunday. For signal date `T = Monday`, the feature on `T` uses Friday's `adjusted_close` as `T-1`, **not** Sunday's calendar date. The test fails if the calculator treats `T-1` as `Monday minus one calendar day` (Sunday). Verified for every feature family.
32. **T-1 trading-day alignment — holiday boundary (Revision 6).** A fixture price series spans a trading day, then a market holiday (no `prices.etf_prices_daily` row), then the next trading day. For signal date `T` equal to the post-holiday trading day, `T-1` is the pre-holiday trading day. The test fails if the calculator treats `T-1` as the calendar day before `T` (the holiday). Verified for every feature family.
33. **T-1 cross-series alignment for benchmark-relative features (Revision 6).** A fixture in which the ETF and its benchmark have **different missing days within the lookback window** (e.g., the ETF is missing day `D` while the benchmark is not, and vice versa). Family 4 is null on signal dates where either series cannot resolve a valid `T-1` and a full lookback window of valid trading-day rows. The test fails if the calculator silently uses different effective dates for the two series within the same feature row.
34. **No-write-to-`ops.*` static check (v0.3 Revision 1, replaces v0.2 test #34).** A static check confirming that no module under `quant_research_platform.features` writes to **any** `ops.*` table — neither `ops.data_quality_exceptions`, nor `ops.ingestion_runs`, nor `ops.provider_raw_payloads`, nor `ops.data_snapshots`, nor `ops.schema_migrations`. Implemented as a source / SQL scan looking for `INSERT INTO ops.`, `UPDATE ops.`, `DELETE FROM ops.` patterns and equivalent ORM operations. Failing this is a defect against Section 2 v1.0 LOCKED (the framework remains ingestion-owned).
35. **`features.feature_run_issues` write test (v0.3 Revision 1; v0.4 Revision 1 lifecycle integration).** A fixture exercises each of the five closed-enumeration `issue_type` values via a real lifecycle path — **not** via synthetic `feature_run_id` values that would bypass the orchestrator:
    - `'invalidated_snapshot_blocked'`, `'failed_ingestion_run_blocked'`, `'partial_ingestion_run_blocked'`: produced by starting a feature run with the corresponding adverse snapshot / ingestion-run state, per the §6.3 blocked-run lifecycle. The orchestrator opens the `features.feature_runs` row, marks it `'failed'`, and writes the issue row in the same sequence.
    - `'feature_run_failed'`: produced by forcing a feature run to fail mid-execution (after the `features.feature_runs` row is open and some `features.feature_values` rows have committed in transactional batches), per §9 edge case 12.
    - `'index_only_benchmark'`: produced by a normal `'succeeded'` feature run that includes an ETF whose primary benchmark resolves index-only on signal date `T`; in this case the run row is `'succeeded'` and a per-ETF / per-date / per-feature `severity='warning'` issue row is written for the affected combinations.
    The test asserts:
    (a) the row is written to `features.feature_run_issues` with the correct `feature_run_id` (referencing a real `features.feature_runs` row), `issue_type`, `severity`, scoping fields (`etf_id`, `as_of_date`, `affected_feature_name` populated where applicable), and `summary` and `detail` populated;
    (b) the database `CHECK` constraint on `issue_type` rejects an unknown value (e.g., `'spurious_type'`);
    (c) the database `CHECK` constraint on `severity` rejects values outside `{'warning', 'fail'}`;
    (d) the FK on `feature_run_id` rejects a row referencing a non-existent run (the test inserts a synthetic row with a fabricated `feature_run_id` to verify the FK constraint, separate from the lifecycle-driven cases above);
    (e) for the four `*_blocked` and `feature_run_failed` cases, the linked `features.feature_runs.status` is `'failed'`; for `'index_only_benchmark'`, the linked status is `'succeeded'`;
    (f) for the three `*_blocked` cases, **no `features.feature_values` rows are written for the failed run**.
36. **`features.feature_run_issues` query test (v0.3 Revision 1).** A fixture populates several runs with mixed issues and asserts that the canonical query patterns (per-run issues, per-`issue_type` issues, per-`(etf_id, as_of_date)` issues) return the expected rows. Verifies the index choices in §6.6 support these query patterns.

### 8.3 Test data discipline

- Fixtures live under `tests/fixtures/features/`. Synthetic price series for known-input / known-output tests are checked into the repo per EW §5.
- No 03a test depends on a live API call (Section 2 already enforces this for ingestion; 03a tests use Postgres fixtures).
- The integration test path (`tests/integration/features/`) exercises the orchestrator end-to-end on a small fixture universe with a fixture `ops.data_snapshots` row, producing fixture-comparable `features.feature_values` content.

---

## 9. Edge cases and failure behavior

1. **New ETFs (added to universe but not yet rank-eligible).** **No `features.feature_values` row is written** for `(e, T)` when `T < eligible_start_date(e)` or when `etf_eligibility_history` does not return a row with `is_rank_eligible=true` covering signal date `T` (resolved via Section 2's as-of-date SQL view). The principal gate is the eligibility history (canonical for the actual timeline); the `eligible_start_date` floor is the secondary check. Rows are absent from `features.feature_values`, not stored with a flag.
2. **Delisted ETFs.** **No `features.feature_values` row is written** for `(e, T)` where `T >= delisted_date(e)`. Replacement-ETF semantics (`replacement_etf_id` on `universe.etfs`) are not consulted by 03a; replacement is a Section 5 portfolio concern.
3. **Insufficient history for a window.** The feature is null when fewer than `w + 1` trading days of `prices.etf_prices_daily` rows exist on `as_of_date <= T - 1`. No imputation, no extrapolation.
4. **Benchmark gaps.** When the benchmark ETF `b` has missing days within the lookback window, the feature is null on the affected signal dates per `missing_data.rule = "null_on_any_missing_input_in_window"`. This applies to Family 4.
5. **Non-overlapping trading history (ETF vs benchmark).** When `e` has a price row on `T - 1` but `b` does not (or vice versa), Family 4 is null on that signal date.
6. **Stale data per Section 2 thresholds.** Section 2's `data_freshness:` block defines `stale_warning_business_days: 5` and `stale_fail_business_days: 10`. 03a respects the data-layer signal: when `prices.etf_prices_daily.as_of_date` for an ETF lags by more than `stale_fail_business_days`, no new feature rows are written for that ETF until the staleness clears. 03a does not override or relax the data-layer signal.
7. **Index-only benchmark.** Per Approver direction, Family 4 is unavailable for that ETF/date; the feature row is null and a `severity='warning'` row is recorded in `features.feature_run_issues` with `issue_type='index_only_benchmark'` (per §6.6). **No silent benchmark substitution. No row is written to `ops.data_quality_exceptions`.** This is flagged as Open Question §10.1.
8. **Invalidated `ops.data_snapshots`.** Per the §6.3 blocked-run lifecycle: the orchestrator opens the `features.feature_runs` row with `status='running'` first, then validates the snapshot. Detecting `status='invalidated'` causes the orchestrator to mark the run row `status='failed'`, populate `error_message` and `completed_at_utc`, and write a `severity='fail'` row to `features.feature_run_issues` with `issue_type='invalidated_snapshot_blocked'` and `detail` naming the offending `data_snapshot_id`. **No `features.feature_values` rows are written for that run.** Per Section 2 contract.
9. **Failed ingestion runs covering the snapshot's price data.** Per Section 2 LOCKED constraint #8, 03a may not silently consume `failed` runs. Per the §6.3 blocked-run lifecycle: the orchestrator opens the `features.feature_runs` row with `status='running'` first, then validates ingestion-run dependencies. Detecting any `status='failed'` ingestion run covering the snapshot causes the orchestrator to mark the run row `status='failed'`, populate `error_message` and `completed_at_utc`, and write a `severity='fail'` row to `features.feature_run_issues` with `issue_type='failed_ingestion_run_blocked'` and `detail` naming the offending `ingestion_run_id`(s). **No `features.feature_values` rows are written for that run.**
10. **Partial ingestion runs covering the snapshot's price data.** Per Section 2 LOCKED constraint #5 and #7, partial runs are blocking by default. Per-symbol-aware partial handling via `chunk_results` JSONB is explicitly out of 03a scope. Per the §6.3 blocked-run lifecycle: the orchestrator opens the `features.feature_runs` row with `status='running'` first, then validates ingestion-run dependencies. Detecting any `status='partial'` ingestion run covering the snapshot causes the orchestrator to mark the run row `status='failed'`, populate `error_message` and `completed_at_utc`, and write a `severity='fail'` row to `features.feature_run_issues` with `issue_type='partial_ingestion_run_blocked'` and `detail` naming the offending `ingestion_run_id`(s). **No `features.feature_values` rows are written for that run.** A future amendment could introduce per-symbol-aware feature computation.
11. **Missing data within a window (single bar gap).** Per `missing_data.rule = "null_on_any_missing_input_in_window"`, the feature is null on any signal date where the lookback window contains a missing input bar. No interpolation, no forward-fill, no backward-fill (backward-fill would also constitute look-ahead).
12. **Feature run failure mid-execution.** Feature runs write in transactional batches (per §6.5 atomicity contract); a failure during execution leaves the `features.feature_runs` row updated to `status='failed'` with `error_message` populated and `completed_at_utc` set, while any `features.feature_values` rows from already-committed batches **are retained** (no auto-deletion) and remain distinguishable by `feature_run_id`. **Downstream consumers — 03b, 03c, Section 4 — must filter on `features.feature_runs.status='succeeded'`** when reading from `features.feature_values`; 03a does not require a single massive transaction for the entire run, but it does require this consumption-side discipline. The feature run is **not** auto-retried by 03a; the next scheduled run picks up. A `severity='fail'` row with `issue_type='feature_run_failed'` is recorded in `features.feature_run_issues` (per §6.6). **No row is written to `ops.data_quality_exceptions`** — the Section 2 framework remains ingestion-owned.
13. **Universe expansion (ETF added between snapshots).** The feature run is bound to a single `data_snapshot_id`; the universe at snapshot time is the universe used for the run. ETFs added after snapshot creation are not retroactively added to the run. Re-creating the snapshot is a Section 2 / operational concern.
14. **YAML config malformed or missing.** Per EW §7 and Section 1 invariant 6, the orchestrator fails at startup with a clear, structured error. There is no silent default for any field originating in YAML.
15. **Database connectivity loss mid-run.** The run status transitions to `'failed'` on the next reconnection attempt (or via the orchestrator's structured exception handling); partial writes within the failed transaction are rolled back per standard Postgres semantics. 03a does not implement custom retry/resume — that is a future enhancement requiring Approver-approved scope expansion.

---

## 10. Open questions

These items are not silently resolved per EW §3.3. Each requires explicit Approver direction before 03a is locked.

### 10.1 Index-only benchmarks (Open question for Approver)

**Status:** *Open question for Approver / possible future Section 2 amendment.*

**Per Approver direction in 03a handoff:** benchmark-relative features require the primary benchmark to resolve to an ETF-backed benchmark with `etf_id` and adjusted-close history. When the benchmark is index-only via `universe.benchmarks.index_symbol`, benchmark-relative features are unavailable for that ETF/date; a `severity='warning'` row with `issue_type='index_only_benchmark'` is recorded in `features.feature_run_issues` (per §6.6); no silent benchmark substitution is permitted; no row is written to `ops.data_quality_exceptions`.

**Resolution path:** A future Section 2 amendment could introduce benchmark price storage (e.g., a `prices.benchmark_prices_daily` table for index-backed benchmarks) and a corresponding ingestion path. That amendment is not proposed here; this Open Question records the gap and the interim behavior. The Approver may at any time direct (a) acceptance of the interim constraint as the durable Phase 1 behavior, (b) a Section 2 amendment to add benchmark price storage, or (c) a different resolution.

### 10.2 Phase 1 feature families and lookback windows (Proposed default requiring Approver approval)

**Builder proposal:** five families as in §6.2 (returns/momentum, volatility, trend strength, benchmark-relative, regime primitive default off), with the specific window choices noted per family.

**Trade-offs:** the proposed windows align with SDR Decision 6's 63/126-day target horizons. Adding more families or windows expands feature surface (and downstream compute and storage); removing them constrains downstream model expressiveness.

**Approver options:** accept; modify family list; modify window list per family; remove a family; defer regime primitive entirely (would simplify §6.2.5 and §8.1 Family 5 tests).

### 10.3 Feature storage convention — long-form vs wide (Proposed default requiring Approver approval)

**Builder proposal:** long-form `features.feature_values(etf_id, as_of_date, feature_name, feature_run_id, feature_value)` per §6.5.

**Trade-offs:**
- *Long-form* (proposed): adding a feature requires no schema migration; query patterns are joins / pivots; row count grows with `etfs × dates × features`.
- *Wide*: one column per feature; faster read for typical model training; schema migration required when adding or removing a feature.

**Approver options:** accept long-form; direct wide; direct hybrid (e.g., a small wide cache table materialized from the long-form for typical training queries).

### 10.4 `data_snapshot_id` linkage granularity (Proposed default requiring Approver approval)

**Builder proposal:** run-level linkage on `features.feature_runs.data_snapshot_id`, with row-level traceability via `features.feature_values.feature_run_id` per §6.8.

**Trade-offs:**
- *Run-level* (proposed): cheaper storage; one canonical anchor per run; row-level traceability via FK; snapshot lookup requires a one-row join.
- *Row-level* (denormalized `data_snapshot_id` on every `feature_values` row): row count × bigint cost; redundant given the FK chain; simpler ad-hoc queries.

**Approver options:** accept run-level; direct row-level; direct both (run-level + denormalized).

### 10.5 Cross-sectional feature treatments (Proposed default requiring Approver approval)

**Builder proposal:** 03a stores raw per-ETF feature values. Any cross-sectional transforms (winsorization, z-score, cross-sectional rank within sleeve) are computed at consumption time in 03c, not stored in `features.*`.

**Trade-offs:**
- *Raw-only* (proposed): cleaner separation; transforms are model-side choices that 03c may iterate on without re-running 03a; storage is smaller.
- *Pre-transformed*: transforms are reproducible at the snapshot level; consumption is faster; but a transform change forces a feature re-run.

**Approver options:** accept raw-only; direct that 03a stores both raw and a Phase 1 transformed variant (e.g., cross-sectional z-score within sleeve); direct a different split.

### 10.6 Regime-side feature primitive activation (Proposed default requiring Approver approval)

**Builder proposal:** `regime_primitives.spy_vs_200dma.enabled: false` by default in `config/features.yaml`. Activation requires explicit Approver direction. Per the revised §6.2.5, activation within 03a's scope must materialize the primitive as repeated rows for each eligible ETF/date in `features.feature_values` using real `etf_id` values; alternatively, activation may be deferred to a future `regime/` package and a future Section 1 / Section 2 amendment.

**Trade-offs:** activating the primitive expands feature surface and adds a market-trend regime input that may improve model conditioning; leaving it off keeps Phase 1 lean. Whether the primitive helps Phase 1 ranking is an empirical question that 03c (model side) is positioned to answer. Materializing as repeated rows is storage-redundant (the value is identical across ETFs on a given signal date) but preserves FK integrity to `universe.etfs` without a schema amendment.

**Approver options:** accept default off; direct on for Phase 1 (with the repeated-row materialization per §6.2.5); defer the entire primitive to the future `regime/` package (which simplifies §6.2.5 and §8.1 Family 5 tests).

### 10.7 Liquidity feature inclusion (Proposed default requiring Approver approval)

**Status:** Phase 1 03a v1.0 **does not** include a liquidity feature family. Liquidity is currently used in Phase 1 only as a universe eligibility filter (`min_avg_daily_dollar_volume_usd: 25000000` per Section 2's `config/universe.yaml`).

**Rationale for omission:** dollar volume computed from `raw_close × volume` would constitute a research use of unadjusted prices, which Section 2's adjusted-price convention forbids without explicit Approver approval. An alternative (`adjusted_close × volume`) is defensible as a research-canonical liquidity proxy but differs semantically from "true dollar volume."

**Approver options:** accept omission; direct inclusion via the `adjusted_close × volume` proxy (no Section 2 amendment needed); direct inclusion via `raw_close × volume` (requires Section 2 amendment); direct deferral pending 03c's view of whether liquidity adds model value.

### 10.8 Missing-data rule within a feature window (Proposed default requiring Approver approval)

**Builder proposal:** `missing_data.rule = "null_on_any_missing_input_in_window"` — any missing input bar within the lookback window yields a null feature on that signal date.

**Trade-offs:**
- *Null-on-any-missing* (proposed): conservative; no imputation; a single missing bar nullifies the feature. May reduce feature coverage for noisy histories.
- *Tolerant rule* (e.g., null only if more than `k` bars are missing): more coverage; introduces a tolerance parameter per family.
- *Forward-fill*: more coverage; imputation introduces a small look-ahead-like bias if the fill direction is not strictly past-only; **backward-fill is forbidden** as it constitutes look-ahead.

**Approver options:** accept null-on-any-missing; direct a tolerance-based rule; direct strict past-only forward-fill with documented bounds.

### 10.9 `features.*` migration filenames (forward reference to module-build time)

**Status:** *Implementation default with no strategy impact.*

03a v1.0 references `features.feature_runs`, `features.feature_definitions`, `features.feature_values`, and `features.feature_run_issues` at the spec level. Concrete migration filenames continuing from Section 2's `0001_initial_setup.sql` (e.g., `0002_add_features_schema.sql`) are assigned at module-build time per EW §8 conventions, not in this spec. The exact filename and number are at Builder discretion within the convention.

---

## 11. Explicit assumptions

Classified per EW §3.3. Items already classified in §10 above (Open Questions and Proposed defaults) are not duplicated here.

### 11.1 Derived from SDR or EW

- **Adjusted-close is canonical research price.** Section 2 v1.0 LOCKED Approver-directed convention; SDR Decision 11 (data-quality auditability).
- **No `features/` module imports from `providers/` or provider-specific libraries.** SDR Decision 2; Section 1 invariant 1.
- **No ranking before `eligible_start_date`.** SDR Decision 3 (eligibility rules); SDR Decision 4 (universe survivorship).
- **Each ETF has a `primary_benchmark_id` and a `sleeve_id`.** SDR Decision 5; Section 2 v1.0 LOCKED schema.
- **Forward-target horizons of 63 and 126 trading days exist downstream.** SDR Decision 6. 03a does not generate targets but aligns lookback windows to support these horizons.
- **T-1 alignment for signal-date features.** SDR Decision 16 (look-ahead-bias control); Section 1 invariant 7.
- **Survivorship-aware feature generation gated on `etf_eligibility_history` and ETF lifecycle fields.** SDR Decision 16; Section 2 v1.0 LOCKED schema.
- **`data_snapshot_id` is the reproducibility anchor on the writer side.** SDR Decision 11; Section 2 v1.0 LOCKED `ops.data_snapshots`; EW §7 reproducibility list.
- **Tests must run inside the application container.** EW §5.
- **All paths via `pathlib.Path`; container-local paths only.** EW §7; Section 1 invariant 5.
- **No secrets in code, config, fixtures, logs, or docs.** EW §7, §9, §10; Section 1 invariant 6.
- **No new auto-resolution classes beyond the four allowed by SDR Decision 11.** Section 2 v1.0 LOCKED constraint #1. 03a does not write to `ops.data_quality_exceptions` at all (per v0.3 Revision 1) — feature-layer issues land in `features.feature_run_issues` per §6.6 — so the question of adding auto-resolution classes to the Section 2 framework does not arise from 03a. The Section 2 framework remains ingestion-owned and unmodified.
- **Phase 1 excludes fundamentals, holdings, news, earnings, options, individual stocks, autonomous research agents.** SDR Decision 1; SDR Decision 14.

### 11.2 Derived from Section 1

- **`features/` imports only from `common/`.** Section 1 *Python import dependency graph*.
- **`features/` does not import from any other business area** (`providers/`, `ingestion/`, `targets/`, `regime/`, `models/`, `backtest/`, `attribution/`, `portfolio/`, `paper/`, `order_intent/`, `ui/`). Section 1 import discipline; cross-area sharing is via `common/` or via Postgres data-at-rest coupling.
- **Time-aware research auditability invariant 7 cashes out at the feature level in 03a.** Section 1 reservation; 03a is the principal cash-out point alongside Section 2 (data-layer side) and Section 4 (backtest side).

### 11.3 Derived from Section 2

- **`prices.etf_prices_daily.adjusted_close` is the canonical price input** for all 03a features.
- **`universe.etfs` is the source of identity, lifecycle, sleeve, and benchmark assignment fields** for 03a.
- **`universe.etf_eligibility_history` is canonical for the actual eligibility timeline**, with half-open effective-date semantics.
- **`ops.data_snapshots` is the reproducibility anchor**; `'invalidated'` snapshots raise clear errors on attempted use.
- **Partial ingestion runs are blocking by default; failed runs may not be silently consumed.** Section 2 v1.0 LOCKED constraints #5, #7, #8.
- **The interim `pending_section_3` `rank_method` sentinels in `config/universe.yaml` are closed by 03c**, not by 03a.
- **The secrets redaction utility (`common.redact_secrets()`) is the only allowed path for persisting any provider-derived text or JSON.** Section 2 v1.0 LOCKED constraint #8. 03a does not persist provider-derived content (features are derivative computations); the constraint is respected by absence.

### 11.4 Implementation default (no strategy impact)

- **`features.feature_values` carries `feature_set_version` with composite FK to `features.feature_definitions(feature_set_version, feature_name)`** (v0.2 Revision 5, Option A). Chosen over Option B (validation-only at write time) because the database-enforced FK is more strict, is testable at the schema level, and survives any future bypass of the orchestrator's pre-write validation. No strategy impact: feature semantics are unchanged.
- **`features.feature_runs` carries a `UNIQUE (feature_run_id, feature_set_version)` constraint, and `features.feature_values` carries a composite FK `(feature_run_id, feature_set_version) → features.feature_runs(feature_run_id, feature_set_version)`** (v0.3 Revision 2). Strengthens the v0.2 referential integrity by enforcing at the database level (not only at the orchestrator level) that `feature_values.feature_set_version` matches the linked run's `feature_set_version`. The UNIQUE constraint is the standard PostgreSQL pattern for making a non-PK column pair the target of a foreign key. No strategy impact.
- **`features.feature_run_issues` is a feature-layer issue log inside the `features` schema, not in `ops.*`** (v0.3 Revision 1, Option A). Chosen over Option B (warning metadata on `feature_runs` only) because a separate table accommodates per-ETF / per-date / per-feature scoping for index-only-benchmark issues, supports indexed query patterns, and keeps `feature_runs` a clean run-state table. The closed enumeration on `issue_type` keeps the schema disciplined. No strategy impact: feature semantics are unchanged. Section 2 v1.0 LOCKED is fully respected — the `ops.data_quality_exceptions` framework remains ingestion-owned.
- **Long-form `features.feature_values` PK includes `feature_run_id`** to support append-only writes across runs while distinguishing successive runs against the same snapshot.
- **`numeric(24,12)` for `feature_value`** — generous precision for ratios, returns, and standardized values without committing to a specific transform's range.
- **`feature_definitions` populated at orchestrator startup** by reading `config/features.yaml`. Existing rows for prior `feature_set_version` values are retained for audit; only the active version is consulted by feature-value writes.
- **Feature names use lowercase snake_case** with windowed names suffixed by the trading-day window (e.g., `return_63d`). Matches the snake_case discipline established in Section 1 *Naming conventions*.
- **Indexes on `features.feature_values`** match Section 2's index style: PK + the small set of indexes named in §6.5. Additional indexes are added at module-build time only when query patterns demonstrate need.
- **Tests directory layout** under `tests/unit/features/` and `tests/integration/features/`, mirroring Section 1's convention.
- **Trading-calendar source.** Per §6.1 / v0.2 Revision 6, the operative trading calendar is the set of `prices.etf_prices_daily` rows for the relevant ETF (per Section 2 ownership of trading-calendar semantics). 03a does not maintain its own calendar table or load an external calendar.

### 11.5 Approver-resolved defaults (Section 3a)

Direction received pre-drafting v0.1 (2026-04-29), during the v0.1 → v0.2 revision pass (2026-04-29), the v0.2 → v0.3 revision pass (2026-04-29), the v0.3 → v0.4 revision pass (2026-04-29), and at the v0.4 → v1.0 lock authorization (2026-04-29):

| Item | Decision |
|---|---|
| Section 3 split | **3a / 3b / 3c** with sequencing 3a → 3b → 3c |
| 03c canonical filename | **`03c_model_layer_mlflow.md`** (not `03c_model_layer.md`) |
| Regime scope in 03a | **Feature-side primitives only where genuinely needed** for feature engineering. The full `regime/` subpackage, `regime.*` schema, and SDR Decision 9 reporting layer remain outside 03a. |
| Index-only benchmark behavior in 03a | **Benchmark-relative features unavailable** for that ETF/date when the primary benchmark is index-only. **No silent benchmark substitution.** Flagged as Open Question (§10.1) for possible future Section 2 amendment. |
| Eligibility-row treatment in 03a (Revision 1, 2026-04-29) | **03a does not write `features.feature_values` rows for ETF/date pairs that are not rank-eligible per `universe.etf_eligibility_history` as of signal date `T`.** The eligibility history is the canonical as-of-date gate; ineligible rows are absent from the feature surface, not stored with a flag. The feature-row existence does **not** imply portfolio action or model promotion — those gates remain Section 4 / Section 5 / 03c concerns — but rank-ineligible ETF/date pairs do not appear in `features.feature_values`. Lifecycle bounds (`T < first_traded_date(e)` or `T >= delisted_date(e)`) likewise produce no row. Replaces v0.1 §10.9 (which was incorrectly classified as an Implementation default with no strategy impact). |

Any change to these defaults goes through the EW change process.

### 11.6 Proposed default requiring Approver approval

(See §10. Items §10.2 through §10.8 are Proposed defaults; §10.9 is an Implementation default with no strategy impact, retained in §10 for visibility.)

### 11.7 Open question for Approver

(See §10.1 — index-only benchmark / possible future Section 2 amendment.)

---

## 12. Section 3a → 03b / 03c handoff (forward references only)

03a leaves the platform with:

- A specified feature-engineering surface (five Phase 1 families, one default off) computing values from `prices.etf_prices_daily.adjusted_close`, `universe.etfs`, `universe.etf_eligibility_history`, and `universe.benchmarks` per the Section 2 contracts.
- A specified `features.*` schema comprising four tables — `features.feature_runs`, `features.feature_definitions`, `features.feature_values`, and `features.feature_run_issues` — anchored to `ops.data_snapshots` for reproducibility, with the feature-layer issue log (`feature_run_issues`) deliberately separate from the Section 2 ingestion-owned `ops.data_quality_exceptions` framework.
- A specified `config/features.yaml` shape with closed-set family validation.
- T-1 alignment, look-ahead-bias controls, and survivorship gating tested at the feature level.
- An interim ETF-backed-benchmark constraint for benchmark-relative features, flagged as Open Question §10.1.

The handoff to subsequent subsections:

- **`docs/engineering_spec/03b_target_generation.md`** will own regression and classification target generation per SDR Decision 6 (forward excess-return labels over 63 and 126 trading days; outperformance flags), label alignment to the same `(etf_id, as_of_date)` axis 03a establishes, overlapping-label handling per SDR Decision 7 and Decision 16, and target tests including survivorship and horizon-correctness checks. 03b will also specify whether targets are persisted (Builder default proposal in the Section 3 handoff packet: persist with `data_snapshot_id` linkage) or computed on the fly.
- **`docs/engineering_spec/03c_model_layer_mlflow.md`** will own baseline model implementations (per SDR Decision 6 dual-target framework; baseline forms per Approver direction at 03c handoff time), the calibration pipeline per SDR Decision 7, MLflow client-side integration on the writer side per SDR Decision 11, the model registry schema (`models.*`), the model state lifecycle per SDR Decision 12 (Active/Warning/Paused/Retired), the allowed values and semantics for `rank_method` (closing the Section 2 `pending_section_3` sentinel obligation), the combined-score formula per SDR Decision 6 (first testable formula; explicit Approver direction at 03c handoff time), and `config/model.yaml`. 03c also owns the linkage from MLflow runs back to the `feature_run_id` referenced in 03a's `features.feature_runs`.

Each subsection follows the full EW §3 workflow (handoff packet, drafting, QA review, Approver approval, commit, traceability matrix update).

---

## 13. Proposed traceability matrix updates (draft only)

This section sketches the matrix updates 03a contributes at lock time. **The matrix update itself is not applied within this spec.** Items owned by 03b or 03c are marked pending. The fuller proposed-replacement-rows companion file (matching the Section 2 traceability-updates companion file shape) is produced as a separate artifact at 03a lock: `docs/reviews/2026-04-29_spec_03a_feature_engineering_traceability_updates.md`. The matrix is updated by the Approver as part of the Section 3a lock merge.

| SDR Decision | Proposed 03a contribution | Status after 03a lock |
|---|---|---|
| Decision 1 — Project Scope and Phase 1 Boundaries | Affirmed by 03a's exclusion of fundamentals, holdings, news, earnings, options, individual stocks, autonomous agents at the feature level. | unchanged (already `in spec` via Section 1) |
| Decision 2 — Data Provider and Provider-Switching Strategy | Extended to record 03a's no-provider-import contract for `features/` (test 8.2 #18) and the adjusted-close-only contract (test 8.2 #19). | unchanged status (`in spec`); row text extended |
| Decision 3 — ETF Universe and Eligibility Rules | Extended to record 03a's eligibility gating on `etf_eligibility_history` and `eligible_start_date` floor. | unchanged status (`in spec`); row text extended |
| Decision 4 — Universe Survivorship and ETF Launch-Date Handling | Extended to record 03a's `first_traded_date` / `delisted_date` gating at the feature level. | unchanged status (`in spec`); row text extended |
| Decision 5 — Benchmark, Sleeve, and Diversifier Treatment | Extended to record 03a's benchmark-relative feature family (Family 4) using `primary_benchmark_id`. The interim ETF-backed-benchmark constraint is recorded with a forward reference to Open Question §10.1. The allowed `rank_method` values remain pending (03c). | `in spec (universe-side and benchmark-relative feature side)`; `pending (ranking math, rank_method values)` |
| Decision 6 — Target Design and Ranking Objective | 03a does not generate targets but aligns 63/126-day windows to support the target horizons. | pending (03b and 03c) |
| Decision 7 — Validation, Calibration, and Backtest Confidence Level | 03a's T-1 alignment supports walk-forward; calibration is 03c; the harness is Section 4. | pending (03c and Section 4) |
| Decision 9 — Regime Taxonomy and Reporting | 03a defines a feature-side primitive (Family 5, default off) only; the full regime subpackage, schema, and reporting layer remain pending. | pending (Sections 3 and 4) |
| Decision 11 — Model Tracking, Attribution, Data Quality, and Lightweight MLOps | Extended to record 03a's `features.feature_runs.data_snapshot_id` linkage; `features.feature_values.feature_run_id` row-level traceability; `features.feature_run_issues` as the feature-layer issue log (introduced in v0.3, integrated with the open-then-validate run lifecycle in v0.4). **`ops.data_quality_exceptions` remains ingestion-owned and unmodified by 03a** per Section 2 v1.0 LOCKED. MLflow writer-side integration remains pending (03c). | unchanged status (`in spec`); row text extended |
| Decision 16 — Phase 1 Success Criteria and Bias Controls | Extended to record 03a's feature-side time-aware auditability: T-1 alignment tests (per family), survivorship tests, look-ahead boundary tests, idempotency tests, `data_snapshot_id` linkage tests. | unchanged status (`in spec`); row text extended |

The companion artifact named above contains the full proposed replacement rows in the Section 2 traceability-updates companion file shape.

---

**End of Section 3a v1.0 LOCKED / APPROVED.**
