# Section 6 — Operator UI, Read-Only Surfaces, Disclosure Surfacing, System Health, and Final Phase 1 Integration Boundaries — Approval Note

**Source section:** Engineering Specification — Section 6: Operator UI, Read-Only Surfaces, Disclosure Surfacing, System Health, and Final Phase 1 Integration Boundaries
**Status:** v1.0 LOCKED / APPROVED
**Date:** 2026-04-30
**Spec file:** `docs/engineering_spec/06_operator_ui.md`
**Approver:** Jeremy
**Builder:** ChatGPT (v0.1 first draft and v0.2 merge); Claude (v0.1 comparison draft and v0.3 surgical cleanup pass per Approver direction)
**QA Reviewer:** Claude (v0.2 review)
**Process reference:** Engineering Workflow v1.5 LOCKED, §3 (drafting), §4 (review), §3.5 (lock), §3.6 (matrix update)
**Companion artifacts:**
- This approval note: `docs/reviews/2026-04-30_spec_06_operator_ui_approval.md`
- Traceability updates: `docs/reviews/2026-04-30_spec_06_operator_ui_traceability_updates.md`
- Matrix file (post-merge): `docs/traceability_matrix.md` v0.9

---

## 1. Approval scope

Section 6 is approved as v1.0 LOCKED / APPROVED. The approval covers the eleven-field EW §3.2 spec content as drafted, including the scope/ownership boundaries, data contracts, configuration dependencies, required tests, edge cases, open-questions disposition, and explicit-assumptions classification. Section 6 is the final Phase 1 Engineering Specification section. After this lock, the project becomes eligible for implementation authorization under EW §3 → §10.

### 1.1 Canonical filename

The canonical Section 6 path is **`docs/engineering_spec/06_operator_ui.md`**, accepted by the Approver at the v0.2 → v0.3 transition and reaffirmed at v1.0 lock. This follows the Section 6 handoff packet. The EW §3.1 default suggestion `06_ui_layer.md` and the Section 6 working-session identifier `06_ui_dash.md` are treated as superseded naming variants of the same Section 6 scope, not separate files. EW §3.1 itself is not amended by this Section 6 lock; the §3.1 list of recommended file names is a default, not a binding contract. Any future cleanup of EW §3.1 is an EW maintenance concern outside Section 6 scope.

### 1.2 Read-only enforcement contract

1. **UI is read-only with respect to all application schemas and MLflow.** No `ui/` module writes to `portfolio.*`, `paper.*`, `order_intent.*`, `models.*`, `backtest.*`, `attribution.*`, `features.*`, `targets.*`, `universe.*`, `prices.*`, `ops.*`, or MLflow. UI does not modify any `config/*.yaml` file owned by a prior section.
2. **Database-access enforcement is dual** per A-PRP-06-01: a dedicated `ui_readonly` Postgres role with `USAGE` on display schemas and `SELECT` on display tables only — no `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, DDL, `GRANT`, ownership, role-management, or system-catalog write privileges — paired with `ui/`-side static checks against write-path call sites and writer-module imports. Section 1 reserved the choice of mechanism in invariant 3; Section 6 selects this dual mechanism.
3. **MLflow read-only enforcement** is performed by a UI-side wrapper that refuses MLflow write methods (run creation, metric/param/tag/artifact logging, registered-model creation, model-version creation, model-stage transition, model deletion). Static checks ensure no `ui/` module bypasses the wrapper.
4. **No live-trading affordance anywhere in `ui/`.** No "place order" affordance, no broker-account selection, no broker-connection screen, no API-key entry surface, no OAuth surface. Enforced at multiple layers per UI-DB-07, UI-ACT-01, UI-ACT-02, and §6.12 redaction discipline.
5. **No state-mutating affordances.** No promotion-state mutation, no kill-switch evaluation/override, no portfolio/paper/order-intent mutation, no run-triggering controls. Enforced by UI-ACT-01 through UI-ACT-06.

### 1.3 Seven-screen scope and screen-name reconciliation

6. **The seven canonical Phase 1 UI navigation surfaces are the SDR Decision 17 / Section 1 names**: Universe & Eligibility, Data Quality, Current Rankings, Backtest Explorer, Paper Portfolio, Model Registry Browser, Regime View.
7. **A-OQ-06-01 — Seven-screen list reconciliation — is RESOLVED** by Approver acceptance of the §6.7 coverage map (path iii). The operator-oriented seven-surface list circulating in the Section 5 approval note §4 and the Section 6 handoff (Data quality / ingestion health, Universe and eligibility, Model and validation, Paper portfolio, Order intent log, Attribution, System health) is satisfied through subpanels, tabs, or sub-routes inside the seven canonical screens, per the §6.7 coverage map (binding). No SDR Decision 17 amendment is required.
8. **The §6.7 coverage map is canonical** for which canonical screen covers which operator-oriented surface. The order-intent log is explicitly a Paper-Portfolio-subordinate surface (tab/subpanel or sub-route under Paper Portfolio); it is not an eighth navigation surface and does not appear in the primary navigation alongside the seven canonical screens.

### 1.4 Disclosure-surfacing contract

9. **Disclosures are non-suppressible** at the UI layer: filters, sorting, pagination, collapsed panels, column selection, and view toggles cannot hide required disclosures. Per UI-DISC-09 anti-suppression test.
10. **The §6.4 disclosure-rendering contract is canonical** and covers eleven disclosure contexts: global Phase 1 no-live-trading; paper-only / non-executable; current-survivor / directional-learning; pipeline-validation-only; prediction-context; regime-evidence availability; DiversifierHedge no-rank; kill-switch state; gate-kind discriminator; account-type deferred; null-vs-no-row.
11. **The current-survivor disclosure label** comes from `backtest.backtest_runs.current_survivor_disclosure_label` (sourced via Section 2's `common.get_current_survivor_label()` from `config/universe.yaml` `disclosures.current_survivor_label`) and is rendered per row and as a per-view banner. Per SDR Decision 4 / Section 2 / Section 4 REP-05.
12. **The pipeline-validation-only disclosure** uses `backtest.backtest_runs.is_pipeline_validation_only` paired with `backtest.backtest_runs.pipeline_validation_only_reason`. Promotion-grade evidence views must exclude `is_pipeline_validation_only=true` AND surface and exclude any row whose `pipeline_validation_only_reason='cost_config_zero_fallback'`. Mirrors Section 5 §6.10 and Section 4 REP-07.
13. **The prediction-context disclosure** uses the closed three-value enum `'in_sample_diagnostic'`, `'walk_forward_oos'`, `'current_scoring'` from 03c §6.2 / A-PRP-24, rendered with visual distinction between in-sample and walk-forward rows.
14. **The DiversifierHedge no-rank disclosure** surfaces the `'rank_method_unsupported_in_phase1'` `models.scoring_run_issues` row and renders affected ETFs as "no rank emitted under current formula." Per 03c §6.7 / §10.6 / approval note §1.4 item 14. UI does not invent ranks for unranked sleeves.

### 1.5 Canonical action / event / cost-bucket enum display contract

15. **The §6.5 canonical-enum table is binding** and covers five view scopes: Paper Portfolio decision panels (`BUY` / `HOLD` / `TRIM` / `SELL` / `REPLACE` / `WATCH` from `portfolio.decisions.action`); Paper Portfolio order-intent panels (same enum from `order_intent.order_intents.action`); Paper Portfolio position-event panels (`paper_open` / `paper_add` / `paper_trim` / `paper_close` / `paper_replace_out` / `paper_replace_in` / `paper_hold_review` from `paper.position_events.event_type`); Backtest Explorer simulated-fills panel (`enter_long` / `exit_long` / `rebalance_in` / `rebalance_out` from `backtest.simulated_fills.action`); cost panels (`ultra_liquid_etf` / `liquid_sector_etf` / `thematic_niche_etf` / `commodity_specialty_etf` from SDR Decision 8 LOCKED via Section 4 §6.7).
16. **The Section 5 portfolio action enum is structurally disjoint from the Section 4 simulated-fills enum** by view scope. UI-ENUM-01 / UI-ENUM-02 / UI-ENUM-03 enforce. The cost-bucket enum is the SDR Decision 8 LOCKED four-value set; UI may not introduce additional values. UI-ENUM-05 covers fail-closed on unknown values across every enum in the table.

### 1.6 Gate-kind, kill-switch, and REPLACE-pairing display contracts

17. **`gate_kind` is displayed verbatim** per §6.6 — `'consumption'` (the 03c second promotion gate) and `'paper_to_real_recommendation'` (Section 5 paper-evidence layer; advisory-only and never enables live trading) — never collapsed into a single visual element. UI-GATE-01 enforces.
18. **Valid status semantics by `gate_kind`** are preserved per §6.6. A promotion-evaluation row carrying a status invalid for its `gate_kind` (per Section 5 §6.2) renders a defect state rather than being silently normalized. UI-GATE-02 enforces.
19. **Kill-switch result enum is displayed verbatim** using Section 5's closed enum — `'pass'`, `'warning_recommended'`, `'pause_new_intents'`, `'manual_review_required'` — and `paper.paper_portfolios.status='paused_by_kill_switch'` is visually distinct from `'active_paper'`, `'paused_by_approver'`, and `'retired_paper'`. UI-KS-01 / UI-KS-02 enforce. The kill-switch panel is read-only; no clear / override / force-resume / re-evaluate / acknowledge affordances.
20. **REPLACE pairing is canonical**: on `order_intent.order_intents`, `etf_id` and `replacement_etf_id` render as a paired out-→-in unit; on `paper.position_events`, the `paper_replace_out` / `paper_replace_in` pair shares `(decision_id, order_intent_id)` per Section 5 §6.7 / A-PRP-05-11 and renders as a visually linked pair. Missing-side REPLACE renders a warning linked to the relevant `paper.paper_state_issues` row, not silently. UI-REPL-01 / UI-REPL-02 / UI-REPL-03 enforce.

### 1.7 Null-vs-no-row and reproducibility-chain contracts

21. **The §6.8 null-vs-no-row table is canonical** for `features.feature_values`, `targets.target_values` (Section 3b §6.5 Bucket 1 / Bucket 2 taxonomy), `models.model_predictions`, `models.combined_scores`, and `backtest.regime_metrics`. Section 6 never silently substitutes a generic dash / blank cell for both NULL-value and no-row states. UI-NULL-01 / UI-NULL-02 enforce.
22. **The §6.11 reproducibility chain is canonical**: `data_snapshot_id` → `features.feature_runs` → `targets.target_runs` → `models.model_runs` → `models.scoring_runs` (traversed to constituent `models.model_runs` via the `models.scoring_run_models` junction) → `backtest.backtest_runs` → `attribution.attribution_runs` → `portfolio.decision_runs` / `portfolio.decisions` → `paper.*` / `order_intent.order_intents`. UI-LINEAGE-01 / UI-LINEAGE-02 enforce. UI does not fabricate missing lineage.

### 1.8 Security, redaction, and sanitization contract

23. **The §6.12 redaction and sanitization contract is binding.** UI escapes / sanitizes issue text, JSON snippets, technical context, provider messages, exception messages, file paths, and Markdown-like content before rendering. UI never displays secrets, tokens, API keys, authorization headers, broker credentials, provider credentials, write-capable connection strings, environment-variable values, or unredacted raw payload content. UI-SEC-01 through UI-SEC-04 enforce.
24. **`ops.provider_raw_payloads` is read metadata-only** by the Data Quality screen — payload bodies are not displayed by default per UI-SEC-02 and the §3.5 / §5.3 read contract.

### 1.9 Defensive edge-case contract

25. **Multiple-Active-model fail-closed.** If more than one Active model version appears for a `model_kind` despite the 03c uniqueness invariant, the Model Registry Browser renders an upstream-invariant defect and does not choose a winner. UI-EDGE-01 enforces.
26. **Browser refresh / session loss.** UI restores authoritative content from read-only database / MLflow surfaces only and does not attempt to reconstruct state by writing session records. Per A-PRP-06-04 / UI-EDGE-02 / §6.13.
27. **Postgres / MLflow unavailable.** UI displays service-unavailable state and does not retry writes (it has no write paths). UI-EDGE-03 / UI-EDGE-04 enforce.
28. **Unknown enum values fail closed.** Action / event / status / gate / kill-switch result / cost-bucket / prediction-context values outside the closed sets render as defect states rather than being silently normalized. UI-ENUM-05 enforces.

### 1.10 Builder Proposed defaults accepted at lock

The Approver accepted the following Builder Proposed defaults as Phase 1 Section 6 defaults at v1.0 lock. Any change to these defaults is a strategy-affecting choice and goes through the EW amendment process.

| ID | Approved default |
|---|---|
| A-PRP-06-01 | UI read-only enforcement uses dedicated `ui_readonly` Postgres principal (USAGE / SELECT only; no DDL / GRANT / ownership / role-management / system-catalog write), read-only transaction posture where supported, static no-write SQL checks, static import-boundary checks, and integration permission-denial tests. |
| A-PRP-06-02 | Section 6 introduces no required `config/ui.yaml` in Phase 1 v1.0. UI display labels come from prior-section config files, schema enumerations, or non-strategy UI constants defined during implementation. |
| A-PRP-06-03 | UI is internal/operator-only in Phase 1 and does not introduce a multi-user authentication / authorization model. Section 1 owns deployment exposure. |
| A-PRP-06-04 | UI uses only non-persistent browser/session display state and optional transient in-memory caching; no UI-owned durable state. |
| A-PRP-06-05 | MLflow access from the UI is read-only metadata / artifact-reference display only. |
| A-PRP-06-06 | Raw provider payload bodies are not shown by default in the UI; only redacted metadata and issue summaries are displayed. |
| A-PRP-06-07 | UI disclosure banners / badges are non-dismissible on views where disclosures are required. |
| A-PRP-06-08 | Visual-regression baselines are produced during implementation, not committed as part of the Section 6 spec lock package. |
| A-PRP-06-09 | Nginx / public exposure remains out of scope for Section 6 v1.0. |

The earlier v0.2 A-PRP-06-08 (coverage-map resolution) was retired at v0.3 per QA item C5; the coverage-map resolution is the disposition of A-OQ-06-01 in §10.1, not a separate Proposed default. Subsequent v0.2 A-PRP-06-09 and A-PRP-06-10 were renumbered to v0.3 / v1.0 A-PRP-06-08 and A-PRP-06-09 respectively.

---

## 2. Process trail

1. **Section 6 handoff prompt** issued by the Approver authorizing Section 6 drafting; SDR v1.0 LOCKED, EW v1.5 LOCKED, Sections 1–5 v1.0 LOCKED named as controlling documents; Section 5 approval note §4 binding conditions on Section 6 named explicitly; Claude assigned QA reviewer / stress tester role; ChatGPT named as possible Builder / spec drafter; Jeremy as final Approver.
2. **v0.1 parallel drafts produced.** ChatGPT produced a v0.1 draft using the Section 6 handoff's operator-oriented seven-surface list (`06_operator_ui_v0_1_draft.md`). Claude produced a comparison v0.1 draft using the SDR Decision 17 LOCKED canonical seven-screen names (`06_ui_dash.md`) per Approver authorization to compare drafts. Both drafts populated the eleven EW §3.2 fields and classified assumptions per EW §3.3.
3. **v0.1 comparison QA review by Claude.** Claude produced a side-by-side comparison identifying ChatGPT's strengths (broad SDR coverage; deeper Section 5 contract specificity; more edge cases; security/redaction tests; cleaner table-based scannability) and weaknesses (silent adoption of the operator-oriented screen list, mis-attributed to SDR Decision 17 — a returnable EW §3.3 finding). Claude's strengths (correct flagging of A-OQ-06-01 with three resolution paths; concrete `ui_readonly` privilege specification; view-scope action-enum table; null-vs-no-row contract across all sections; cross-section binding constraints from Section 6 lock). Net judgment: stitch the two for a stronger v0.1.
4. **v0.2 merge by ChatGPT** (`06_operator_ui_v0_2_draft.md`) folded both v0.1 drafts: kept canonical path `06_operator_ui.md`; added A-OQ-06-01 with proposed coverage-map resolution; adopted Claude's `ui_readonly` role contract, action-enum view-scope table, null-vs-no-row rendering contract; preserved ChatGPT's broader SDR coverage and deeper Section 5 details (`gate_kind`, kill-switch result enum, valid-status handling, REPLACE pairing); added redaction/security tests, reproducibility-chain tests, multi-Active-model fail-closed behavior, browser-refresh handling, anti-suppression disclosure tests.
5. **v0.2 QA review by Claude.** Verdict: pass with comments. Two blocking items requiring Approver decision (B1: A-OQ-06-01 acceptance; B2: canonical filename confirmation) plus ten non-blocking cleanup items C1–C10.
6. **Approver dispositions issued at v0.2 → v0.3 transition.** A-OQ-06-01 resolved via path (iii) coverage-map; canonical filename confirmed as `06_operator_ui.md`; C1–C10 authorized as a single surgical pass.
7. **v0.3 surgical pass by Claude** applied C1–C10 plus the two Approver decisions: enumerated the four cost-bucket values in §6.5; named `pipeline_validation_only_reason='cost_config_zero_fallback'` in §6.10; named `decision_id` and `order_intent_id` as REPLACE-pairing linkage fields in §6.9; added the A-DRV ↔ EW §3.3 classification-mapping note in §11.1; retired the duplicate A-PRP-06-08 and renumbered (v0.2 -09 → v0.3 -08; v0.2 -10 → v0.3 -09); spelled out `ops.provider_raw_payloads` (metadata only) in §3.5 and §5.3; tightened order-intent log placement as a Paper-Portfolio-subordinate surface in §6.7; added `models.scoring_run_models` to the §6.11 reproducibility chain; added the Model Registry Browser promotion-evaluations linkage clause to UI-SMOKE-06; documented the canonical filename in front matter and scope-statement basis. Editorial cleanup of stale "v0.2" version markers in current spec body applied; obsolete §9 edge case #21 (rejected-coverage-map scenario) removed.
8. **v0.3 → v1.0 lock authorization by the Approver.** v0.3 DRAFT promoted to v1.0 LOCKED / APPROVED with no substantive change to behavior, schema, tests, scope, or ownership. Locking metadata flipped (status header, builder/QA-reviewer attribution, end-of-document marker) and minor wording cleanup applied to remove stale "v0.3" version markers in current spec body where they are not historical changelog entries. A-PRP-06-01 through A-PRP-06-09 dispositions updated from "Pending Approver review" to "Accepted as Phase 1 Section 6 default per v1.0 lock approval." A-OQ-06-01 marked closed (resolved). Historical v0.1 → v0.3 changelog entries preserved verbatim. The Approver exercised final-decision authority per EW §2.1 and approved without an additional QA cycle on the v0.3 → v1.0 transition.

---

## 3. Companion artifacts

- **Approved spec section:** `docs/engineering_spec/06_operator_ui.md` (v1.0 LOCKED / APPROVED).
- **This approval note:** `docs/reviews/2026-04-30_spec_06_operator_ui_approval.md`.
- **Section 6 traceability updates:** `docs/reviews/2026-04-30_spec_06_operator_ui_traceability_updates.md`. Proposes a replacement row for SDR Decision 17 and text-extension deltas for SDR Decisions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, and 18 in `docs/traceability_matrix.md`. Application of the proposed replacement row and extension deltas to `docs/traceability_matrix.md` is performed by the Approver as part of the Section 6 lock merge, bumping the matrix version from v0.8 to v0.9. Decisions 13, 14 unchanged from v0.8.
- **Working drafts (preserved for audit):** `06_ui_dash.md` (Claude v0.1 comparison draft), `06_operator_ui_v0_1_draft.md` (ChatGPT v0.1), `06_operator_ui_v0_2_draft.md` (ChatGPT v0.2 merge), `06_operator_ui_v0_3_draft.md` (Claude v0.3 surgical pass).

---

## 4. Conditions on the implementation phase

Section 6 is the final Phase 1 Engineering Specification section. There are no subsequent spec sections to bind. The constraints below bind the **implementation phase** under EW §3 → §10. Any change to these requires a Section 6 amendment with Approver approval per EW §3.3 (no assumption drift) and EW §2.3 (Approval Matrix), not silent override.

1. **No `ui/` module writes** to any application database schema or to MLflow. The dual enforcement mechanism (§6.2 `ui_readonly` role plus static checks) is binding. Implementation must not introduce a write helper, a write-capable connection string, an admin-mode toggle, or any other path that would bypass the dual mechanism. UI-DB-01 through UI-DB-10 backstop.
2. **No live-trading affordance, full stop.** Implementation must not introduce a place-order button, broker-account selector, broker-connection screen, API-key entry surface, OAuth surface, or any string in `ui/` matching known broker-action terminology. UI-ACT-01 / UI-ACT-02 / UI-LT-* tests backstop. The EW Approval Matrix item *"Any code path that could enable live trading"* binds Section 6 implementation the same as it binds prior sections.
3. **No state-mutation affordances.** No promotion-state transition (UI-ACT-03), no kill-switch actuation (UI-ACT-04), no portfolio/paper/order-intent mutation (UI-ACT-05), no run-triggering controls (UI-ACT-06).
4. **The seven canonical screen names are binding navigation labels.** Implementation may not rename them. The §6.7 coverage map is binding — operator-oriented surfaces are realized as subpanels / tabs / sub-routes inside the seven canonical screens; the order-intent log is specifically a Paper-Portfolio-subordinate surface and may not be promoted to an eighth navigation surface.
5. **Disclosures are non-suppressible.** The §6.4 disclosure-rendering contract and the UI-DISC-09 anti-suppression test are binding. Filters / sorting / pagination / collapsed panels / column selection / view toggles cannot hide required disclosures.
6. **The §6.5 canonical-enum table is binding.** UI may not introduce alternate action labels, alternate event-type labels, or alternate cost-bucket values. Section 5 portfolio actions never appear on Backtest Explorer simulated-fills panels; Section 4 simulated-fill actions never appear on Paper Portfolio panels.
7. **The §6.6 gate_kind, valid-status, kill-switch, and paper-status display contract is binding.** No collapsing of `consumption` and `paper_to_real_recommendation`; no advisory-qualifier suppression on Gate 2; no clear/override/force-resume affordances on the kill-switch panel.
8. **The §6.8 null-vs-no-row distinction is binding** across all five surfaces. Implementation may not silently substitute a generic dash / blank cell for both NULL-value and no-row states.
9. **The §6.9 REPLACE pairing is binding**. `order_intent.order_intents` REPLACE rows visually pair `etf_id` and `replacement_etf_id`; `paper.position_events` `paper_replace_out` and `paper_replace_in` rows pair on `(decision_id, order_intent_id)`.
10. **The §6.10 evidence-filtering contract is binding.** Promotion-grade evidence excludes `is_pipeline_validation_only=true` AND surfaces and excludes `pipeline_validation_only_reason='cost_config_zero_fallback'` rows.
11. **The §6.11 reproducibility-chain rendering is binding** through `models.scoring_run_models` for scoring-run composition and through every locked-section run table for full lineage.
12. **The §6.12 redaction and sanitization contract is binding.** No UI display of secrets, tokens, API keys, write-capable connection strings, environment-variable values, or unredacted raw payload content.
13. **External carryovers are honored as honest-absence / display-only / no-speculative-UI**: A-OQ-04-07 (regime classifier ownership), A-OQ-05-09 (Active → Warning automation deferred), A-OQ-05-10 (direct `config/costs.yaml` consumption deferred), A-OQ-05-11 (account-type handling deferred), A-OQ-05-14 / A-PRP-05-14 (ATR formula details deferred), A-OQ-05-17 (kill-switch-driven SELL/TRIM/REPLACE deferred), DiversifierHedge `absolute_with_context` activation deferred. UI surfaces each as absence/deferred/display-only, never inventing semantics.
14. **No prior-section amendment is proposed by Section 6.** If implementation reveals a needed prior-section amendment, the implementation phase must stop and flag the issue under EW §6 impact assessment; it must not work around the gap inside `ui/`.

---

## 5. Open items handed forward

### 5.1 Section-6-internal Open Questions

**None remain at v1.0 lock.** A-OQ-06-01 was resolved by Approver acceptance of the §6.7 coverage map prior to v1.0 lock. UI authentication, `config/ui.yaml`, nginx exposure, and visual-regression baselines were resolved as Phase 1 Section 6 defaults via A-PRP-06-03, A-PRP-06-02, A-PRP-06-09, and A-PRP-06-08 respectively, all accepted at v1.0 lock.

### 5.2 External carryovers (unchanged at Section 6 lock)

The following Open Questions / deferred items remain external to Section 6 and are not resolved by this lock:

- **A-OQ-04-07 — Regime classifier / labeler ownership.** Section 6 surfaces regime evidence when present and surfaces "regime classifier unavailable" honestly when not present. Resolution path: a future strategy decision or Section 4 amendment, at Approver direction.
- **A-OQ-05-09 — Active → Warning automation.** Section 5 records recommendations only; mechanical transitions require a future 03c amendment. Section 6 displays only Approver-driven model-state transitions reflected in `models.model_versions.state` and `models.model_state_history`.
- **A-OQ-05-10 — Direct `config/costs.yaml` consumption.** Deferred at Section 5 lock. Section 6 surfaces cost evidence only as it appears in Section 4 outputs.
- **A-OQ-05-11 — Account-type handling.** Deferred. Section 6 may surface account-type placeholders read-only but does not present them as enforcing real account constraints.
- **A-OQ-05-14 / A-PRP-05-14 — ATR formula details.** Reserved-in-config / deferred. Section 6 surfaces configured stop levels read-only without UI configurability.
- **A-OQ-05-17 — Kill-switch-driven SELL / TRIM / REPLACE enablement.** Deferred. Section 6 does not surface speculative kill-switch-driven action UIs.
- **DiversifierHedge `absolute_with_context` ranking activation.** Out of current Section 5 / Section 6 scope. Section 6 honors the no-`combined_scores`-row disposition by surfacing "no rank emitted under current formula"; activation requires a future 03c amendment that adds absolute-trend / absolute-gain `model_kind` values per 03c approval note §1.4 item 14.
- **Implementation-time Section 4 amendment trigger from A-OQ-05-15 disposition.** If implementation reveals Section 4 v1.0 evidence surfaces lack a required field for the consumption-gate evidence bundle, that is a future Section 4 amendment path under EW §6, not a Section 6 UI workaround.

### 5.3 Decision 16 row split — deferred again

The traceability-matrix Decision 16 row remains the longest in the matrix at v0.9 with the addition of Section 6's UI disclosure-surfacing contribution. A row split into 16a (data-layer auditability) / 16b (feature/target/model auditability) / 16c (backtest/attribution auditability) / 16d (portfolio/paper/order-intent auditability) / 16e (UI disclosure surfacing) was deferred at Section 2, Section 4, and Section 5 lock and is deferred again at Section 6 lock. Phase 1 spec coverage of Decision 16 is now complete, so the Decision 16 row will not grow further within Phase 1; the split decision can be deferred to a Phase 2 / matrix-restructuring task without further blocking effect. Recorded here for the matrix maintainer.

---

## 6. No-implementation discipline

No implementation begins until Section 6 is committed and traceability is updated. Once Section 6 v1.0 LOCKED / APPROVED and `docs/traceability_matrix.md` v0.9 are committed, the project becomes eligible for implementation authorization under EW §3 → §10. The Approver issues a separate implementation authorization. Implementation discipline:

- The `ui/` package skeleton, the `ui_readonly` Postgres role bootstrap (added to `scripts/postgres-init/` per Section 2's bootstrap convention; coordinated with Section 2 maintainer rather than duplicated under `ui/`), the seven Phase 1 screens, and the test files under `tests/unit/ui/`, `tests/unit/architecture/`, and `tests/integration/ui/` (including `tests/integration/ui/snapshots/` for visual-regression baselines per A-PRP-06-08) will be authored under the standard EW §3 → §10 build workflow after the Approver authorizes a build cycle.
- The constraints in §4 above bind the implementation phase. No code may bypass them.

---

## 7. Approval

The Approver has reviewed Section 6 v1.0 LOCKED / APPROVED at `docs/engineering_spec/06_operator_ui.md`, the companion traceability updates at `docs/reviews/2026-04-30_spec_06_operator_ui_traceability_updates.md`, and the post-merge state of `docs/traceability_matrix.md` v0.9, and approves the section as locked. Subsequent changes follow EW amendment discipline.

This is the final Phase 1 Engineering Specification section. Phase 1 spec drafting is complete.

**Signed:** Jeremy (Approver), 2026-04-30.

---

**End of approval note.**
