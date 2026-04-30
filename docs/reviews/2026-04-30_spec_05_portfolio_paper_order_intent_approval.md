# Engineering Specification Section 5 — Portfolio Rules, Paper Portfolio State, Broker-Neutral Order Intent, Promotion Gates, and Kill Switch: Approval Note

**Section:** Engineering Specification — Section 5: Portfolio Rules, Paper Portfolio State, Broker-Neutral Order Intent, Promotion Gates, and Kill Switch
**Section path:** `docs/engineering_spec/05_portfolio_paper_order_intent.md`
**Locked version:** v1.0 LOCKED / APPROVED
**Approval date:** 2026-04-30
**Approver:** Jeremy
**Builder:** ChatGPT (Section 5 cycle only; per Approver-issued Section 5 handoff prompt)
**QA Reviewer:** Claude (Section 5 cycle only; same handoff prompt)

**Role-assignment note.** The Builder/QA assignment for the Section 5 drafting cycle was a temporary swap from the standing assignment (Builder = Claude, QA = ChatGPT). This swap was authorized only for the Section 5 cycle and does not modify the locked Engineering Workflow role assignment for subsequent sections; Section 6 reverts to the standing assignment unless the Approver re-authorizes the swap.

The section was iterated under direct Approver review across drafts v0.1 → v0.2 → v0.3 → v1.0 candidate → v1.0 LOCKED. Each transition produced an explicit revision list. Claude performed QA passes against v0.1 (four blockers, five majors, nine minors), v0.2 (six residuals), v0.3 (clean), and the v1.0 candidate (three blockers, one filename concern). Builder applied each revision list surgically. The Approver's final review serves as the QA pass per EW §3.4 item 9.

**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Engineering Specification — Section 3a v1.0 LOCKED / APPROVED (`docs/engineering_spec/03a_feature_engineering.md`)
- Engineering Specification — Section 3b v1.0 LOCKED / APPROVED (`docs/engineering_spec/03b_target_generation.md`)
- Engineering Specification — Section 3c v1.0 LOCKED / APPROVED (`docs/engineering_spec/03c_model_layer_mlflow.md`)
- Engineering Specification — Section 4 v1.0 LOCKED / APPROVED (`docs/engineering_spec/04_backtest_attribution_validation.md`)
- Section 1 approval note (`docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`)
- Section 2 approval note (`docs/reviews/2026-04-27_spec_02_data_layer_approval.md`)
- Section 2 traceability updates (`docs/reviews/2026-04-27_spec_02_data_layer_traceability_updates.md`)
- Section 3 handoff packet (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`)
- Section 3a approval note (`docs/reviews/2026-04-29_spec_03a_feature_engineering_approval.md`)
- Section 3a traceability updates (`docs/reviews/2026-04-29_spec_03a_feature_engineering_traceability_updates.md`)
- Section 3b approval note (`docs/reviews/2026-04-29_spec_03b_target_generation_approval.md`)
- Section 3b traceability updates (`docs/reviews/2026-04-29_spec_03b_target_generation_traceability_updates.md`)
- Section 3c approval note (`docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_approval.md`)
- Section 3c traceability updates (`docs/reviews/2026-04-30_spec_03c_model_layer_mlflow_traceability_updates.md`)
- Section 4 approval note (per Section 4 lock package, 2026-04-30)
- Section 4 traceability updates (per Section 4 lock package, 2026-04-30)
- Section 5 traceability updates (`docs/reviews/2026-04-30_spec_05_portfolio_paper_order_intent_traceability_updates.md`)
- `docs/traceability_matrix.md` (post-merge state, after the Section 5 lock merge applies the companion traceability updates and bumps the matrix from v0.7 to v0.8)

---

## 1. What this approval covers

Approval of Section 5 v1.0 LOCKED / APPROVED locks the following at the portfolio-and-paper-portfolio level. All decisions below were the subject of explicit Approver direction during the v0.1 → v0.2 → v0.3 → v1.0 candidate → v1.0 process trail in §2 below.

### 1.1 Schema and write contract

1. **Section 5 owns three new schemas: `portfolio.*`, `paper.*`, and `order_intent.*`.** No prior section writes to any of these. The proposed table set per the locked spec §6.5 through §6.11 is:
   - `portfolio.decision_runs`, `portfolio.decisions`, `portfolio.decision_run_issues`, `portfolio.promotion_evaluations`, `portfolio.promotion_evaluation_issues`, `portfolio.kill_switch_evaluations`, `portfolio.kill_switch_triggers`;
   - `paper.paper_portfolios`, `paper.rebalance_cycles`, `paper.positions`, `paper.position_events`, `paper.portfolio_snapshots`, `paper.paper_state_issues`;
   - `order_intent.order_intents`, `order_intent.order_intent_issues`.
2. **Section 5 writes only to `portfolio.*`, `paper.*`, and `order_intent.*`.** Section 5 does not write to `models.*`, `backtest.*`, `attribution.*`, `features.*`, `targets.*`, `universe.*`, `prices.*`, or `ops.*`. The Section 5 issue-log surface is local to Section-5-owned schemas; `ops.data_quality_exceptions` remains Section 2's.
3. **`portfolio.kill_switch_triggers` is an evaluation-decomposition table, not an issue-log table.** It records the per-trigger decomposition of a `portfolio.kill_switch_evaluations` parent row. It is not enumerated in the §6.11 issue-log list.
4. **All Section-5-owned issue tables share a common field shape** plus table-specific FK columns, per the locked spec §6.11. Issue rows include type, severity, plain-English explanation, why it matters, likely cause, suggested resolution, auto-resolution flags, and redacted technical context.
5. **`data_snapshot_id` is denormalized onto `paper.portfolio_snapshots` for direct reproducibility** in addition to the indirect chain via `scoring_run_id`.

### 1.2 Portfolio action vocabulary and structural disjointness

6. **The Section 5 action enum is closed: `BUY`, `HOLD`, `TRIM`, `SELL`, `REPLACE`, `WATCH`.** No additional values, no `NO_ACTION`, no `REVIEW`. No-action / review semantics are represented through decision-run outcomes or issue records, not through the action enum.
7. **The Section 5 action enum is structurally disjoint from Section 4's `backtest.simulated_fills.action` enum** (`enter_long`, `exit_long`, `rebalance_in`, `rebalance_out`). A Section 5 module never emits a Section 4 simulated-fill action and a Section 4 module never emits a Section 5 portfolio action. This disjointness is enforced at the test layer (locked spec test 33; CC-09 verification per Section 4's reservation).
8. **REPLACE produces one `portfolio.decisions` row, one `order_intent.order_intents` row** (with both `etf_id` and `replacement_etf_id` populated), **and two `paper.position_events` rows** (`paper_replace_out` + `paper_replace_in`). This output cardinality is canonical and tested.

### 1.3 Promotion-gate contracts

9. **Section 5 records two gate kinds via the `portfolio.promotion_evaluations.gate_kind` discriminator.** The closed enum is `('consumption', 'paper_to_real_recommendation')`.
10. **`gate_kind = 'consumption'`** is the 03c second promotion gate per the 03c approval note §1.7 item 20, restated in Section 5 terminology. It evaluates whether an Active model version may be consumed by Section 5 paper portfolio rules. This locks the Section 5 second-gate ownership clause from SDR Decision 12.
11. **`gate_kind = 'paper_to_real_recommendation'`** is the Section 5 paper-evidence recommendation layer. It records evidence only and does not enable live trading. Real-decision influence remains Approver-gated and out of any automated promotion path.
12. **The valid-status-by-gate_kind table in the locked spec §6.2 is canonical.** A `consumption` evaluation may carry `not_evaluated`, `blocked`, `eligible_for_paper_tracking`, or `paper_tracking_active`; it must never carry `eligible_for_real_decision_influence_recommendation`. A `paper_to_real_recommendation` evaluation may carry `not_evaluated`, `blocked`, or `eligible_for_real_decision_influence_recommendation`; it must never carry `eligible_for_paper_tracking` or `paper_tracking_active`. Test 21 enforces.
13. **Promotion-gate evidence filtering is canonical per the locked spec §6.10.** Promotion-grade evidence requires succeeded scoring runs, Active model versions, succeeded backtest runs, exclusion of `backtest.backtest_runs.is_pipeline_validation_only = true` rows, exclusion of zero-cost-fallback evidence including `backtest.backtest_runs.pipeline_validation_only_reason = 'cost_config_zero_fallback'`, succeeded attribution runs where required, exclusion of invalidated data snapshots, and preservation of current-survivor disclosure context. Tests 15 and 16 enforce the exclusions; the filter implements Section 4's REP-07 reservation on the Section 5 consumption side.

### 1.4 Kill-switch contract

14. **The v1.0 kill switch suppresses new BUY / REPLACE intents and records review / warning / pause / manual-review outcomes.** It does not automatically generate SELL, TRIM, or REPLACE actions; it does not delete or rewrite existing paper positions; it does not write to `models.*` or `models.model_state_history`. Tests 28, 52, and 53 enforce.
15. **The kill-switch result enum is closed: `('pass', 'warning_recommended', 'pause_new_intents', 'manual_review_required')`.** The `pause_new_intents` outcome may transition the paper portfolio status to `paused_by_kill_switch`, a Section-5-owned status value.
16. **`portfolio.kill_switch_evaluations` and `portfolio.kill_switch_triggers` field tables in the locked spec §6.4 are canonical.** Each `kill_switch_evaluation` row decomposes into zero or more `kill_switch_trigger` rows recording the underlying conditions met.

### 1.5 Config ownership

17. **Section 5 owns `config/portfolio.yaml` and only `config/portfolio.yaml`.** The proposed top-level structure per the locked spec §7.1 is canonical: `portfolio_config_version`, `portfolio_id`, `cadence`, `position_limits`, `sizing`, `action_thresholds`, `replacement_rules`, `risk_rules`, `promotion_gates`, `kill_switch`, `order_intent`, `paper_account`, `evidence_requirements`, `disclosures`.
18. **`config/portfolio.yaml` rebalance / risk-review cadence is structurally independent of `config/backtest.yaml` rebalance cadence.** No Section 5 module under `portfolio/`, `paper/`, or `order_intent/` may couple Section 5 cadence to `config/backtest.yaml`. Test 14 enforces; this satisfies Section 4's ALC-09 reservation on the Section 5 consumer side.
19. **Section 5 reads `config/universe.yaml`, `config/model.yaml`, and `config/backtest.yaml` for label / metadata context only.** Section 5 does not read `config/costs.yaml` directly in v1.0; cost assumptions are consumed only through Section 4 validation evidence (per A-PRP-05-06).

### 1.6 Test coverage

20. **Locked spec §8 tests 1 through 58 are the canonical Section 5 test surface.** Boundary tests (1–7) include the no-broker-import, no-provider-import, write-boundary, no-`models.*`-write, no-Section 4-write, no-`simulated_fills`-as-state, and no-`ui/`-import static checks. The simulated-fills-non-consumption test pair (test 6 and test 41) implements Section 4's ALC-08 reservation on the Section 5 consumer side; the action-disjointness test (test 33) implements CC-09 on the Section 5 side; the cadence-independence test (test 14) implements ALC-09 on the Section 5 side; the pipeline-validation-only-exclusion test (test 15) implements REP-07 on the Section 5 side.
21. **Test 24 (backtest confidence-level sufficiency placeholder) reserves a failing / skipped test until A-OQ-05-15 is closed.** A-OQ-05-15 is dispositioned as resolved (see §1.7 item 28) using existing Section 4 v1.0 evidence surfaces; the placeholder remains in the locked test list because the implementation phase must verify per-bundle sufficiency at integration time and trigger a Section 4 amendment if a real gap appears.

### 1.7 Approver dispositions on Section 5 Open Questions

The Approver resolved sixteen Open Questions enumerated as A-OQ-05-01 through A-OQ-05-17 in the v1.0 candidate ID-space (note: ID-space mutation between v0.3 and v1.0 was recorded explicitly in the v1.0 changelog). The dispositions below are reproduced from the locked spec §10 and are binding on subsequent sections.

22. **A-OQ-05-01 (schema split).** Resolved: three-schema split `portfolio.*`, `paper.*`, `order_intent.*`.
23. **A-OQ-05-02 (paper portfolio state shape).** Resolved: include position-level, rebalance-cycle-level, portfolio-snapshot-level, and order-intent / recommendation-level state.
24. **A-OQ-05-03 (order-intent schema location).** Resolved: `order_intent.*` separate from `paper.*` and `portfolio.*`.
25. **A-OQ-05-04 (action enum).** Resolved: SDR Decision 10 enum exactly; no `NO_ACTION` or `REVIEW`.
26. **A-OQ-05-05 (numeric action thresholds).** Resolved: thresholds live in `config/portfolio.yaml`; threshold changes remain strategy-affecting.
27. **A-OQ-05-06 (promotion-gate evidence thresholds).** Resolved: §6.10 evidence bundle is the minimum; numeric values live in `config/portfolio.yaml`.
28. **A-OQ-05-07 (paper observation period for paper-to-real recommendation gate).** Resolved: require both calendar duration and minimum completed rebalance cycles.
29. **A-OQ-05-08 (kill-switch conditions).** Resolved: paper drawdown, stale scoring evidence, invalidated snapshot, validation deterioration, serious Section 4 issue flags. Numeric thresholds in `config/portfolio.yaml`.
30. **A-OQ-05-09 (Active → Warning automation).** Resolved: Section 5 records recommendations only in Section-5-owned tables. No `models.*` writes. No automated Active → Warning transition. Any mechanical model-state transition requires a future 03c amendment. This carries forward A-OQ-04-14 from the Section 4 handoff.
31. **A-OQ-05-10 (direct `config/costs.yaml` consumption).** Resolved: consume costs only through Section 4 validation evidence in v1.0.
32. **A-OQ-05-11 (account-type handling).** Resolved: defer account-type execution constraints; Phase 1 paper-only placeholders only.
33. **A-OQ-05-12 (order-intent storage without broker integration).** Resolved: yes; non-executable order intents are stored as audit trail.
34. **A-OQ-05-13 (paper starting value and cash placeholder).** Resolved: parameters live in `config/portfolio.yaml`.
35. **A-OQ-05-14 (ATR stop implementation depth).** Resolved: reserve ATR-style stop support in config; defer exact ATR formula until a future approved amendment.
36. **A-OQ-05-15 (backtest confidence-level output sufficiency).** Resolved: existing Section 4 v1.0 evidence surfaces are sufficient for the Phase 1 Section 5 consumption gate. No Section 4 amendment required before Section 5 lock. The minimum promotion-grade bundle is enumerated in §6.10 plus the locked spec A-OQ-05-15 disposition text. If implementation later proves Section 4 lacks a required field to verify the bundle, that triggers a future Section 4 amendment under EW §6 impact assessment. This carries forward and resolves A-OQ-04-18 from the Section 4 handoff.
37. **A-OQ-05-16 (gate terminology reconciliation).** Resolved: `consumption` gate = 03c second promotion gate; `paper_to_real_recommendation` gate = Section 5 paper-evidence recommendation layer.
38. **A-OQ-05-17 (kill-switch-driven SELL / TRIM / REPLACE enablement).** Resolved: deferred. v1.0 kill switch only suppresses new BUY / REPLACE intents and records review / warning / manual-review outcomes. Future enablement requires a Section 5 amendment with explicit tests and audit rules.

### 1.8 Approver acceptance of Proposed defaults

The Approver accepted the seventeen Proposed defaults A-PRP-05-01 through A-PRP-05-17 enumerated in the locked spec §11.4 (v1.0 ID-space). These defaults are binding on Section 5 implementation and on subsequent sections to the extent they create cross-section invariants. Notable items:

39. **A-PRP-05-04 (no `models.*` writes).** Section 5 may not write `models.*`. Warning / Paused recommendations are recorded in Section-5-owned tables only.
40. **A-PRP-05-05 / A-PRP-05-17-equivalent kill-switch conservatism.** Kill switch may pause new paper BUY / REPLACE intents but does not delete positions or place sell orders automatically. (Note: the v0.3 A-PRP-05-17 was absorbed into A-PRP-05-05 at v1.0 because the two were duplicative; the current A-PRP-05-17 is the new Section 4 evidence sufficiency item.)
41. **A-PRP-05-08 (order-intent storage).** Order intents are stored even without broker integration as audit trail.
42. **A-PRP-05-09 (atomic commit).** Decision run, portfolio decisions, and order intents for one run commit atomically.
43. **A-PRP-05-11 (REPLACE cardinality).** REPLACE records both old and replacement ETF on one decision, one order intent, and two paper events.
44. **A-PRP-05-15 (`gate_kind` enum).** `portfolio.promotion_evaluations.gate_kind` uses the closed enum `('consumption', 'paper_to_real_recommendation')`.
45. **A-PRP-05-16 (unranked-sleeve handling).** ETFs whose sleeve / `rank_method` produces no `models.combined_scores` row under the active 03c first-testable formula receive no Section-5 action and produce an explanatory issue row. This honors the 03c §12.2 / 03c approval note §1.4 item 14 disposition without silent remapping.
46. **A-PRP-05-17 (Section 4 evidence sufficiency).** Existing Section 4 v1.0 evidence surfaces are sufficient for the Phase 1 Section 5 consumption gate.

### 1.9 Approval Matrix items satisfied (per EW §2.3)

The following Approval Matrix items are satisfied by this approval:

- **Engineering Specification section finalization** (per EW §3.4): all eleven §3.2 template fields populated; section committed to `docs/engineering_spec/05_portfolio_paper_order_intent.md`; QA review per EW §3.4 item 9 satisfied via direct Approver-iterated review across v0.1 → v0.2 → v0.3 → v1.0 candidate → v1.0 with explicit Builder/QA revision lists at each step.
- **Database schema changes** at the spec level: three new schemas (`portfolio.*`, `paper.*`, `order_intent.*`) and their fifteen-plus tables, indexes, FK relationships, and CHECK / NOT-NULL constraints (notably the `order_intent.order_intents.is_executable = false` CHECK and the broker-field NULL constraints).
- **Strategy-affecting YAML config changes** at the spec level (`config/portfolio.yaml` shape, validation rules, and ownership).
- **Portfolio-rules and risk-rules definition** per SDR Decision 10 (action vocabulary, monthly rebalance + weekly risk review, top-5 equal-weight initial sizing, no fixed take-profit default, no tight fixed stops, ATR-style stop reservation).
- **Second promotion gate definition and kill-switch enforcement layer** per SDR Decision 12 (gate scope and disposition; kill-switch result enum; v1.0 conservative behavior; audit tables).
- **Paper portfolio state and broker-neutral order-intent contract** per SDR Decision 15 (`paper.*`, `order_intent.*` schemas; non-executable CHECK; broker-field NULL constraints; no broker SDK imports under `portfolio/`, `paper/`, `order_intent/`). SDR Decision 14 (Danelfin deferred) has no architectural footprint in Phase 1 and is not implemented by Section 5.
- **Any code path that could enable live trading** (EW Approval Matrix item): Section 5 explicitly enforces this at the spec level via §6.8 schema constraints and tests 1, 7, 43, 44.

The following Approval Matrix items are **explicitly not** satisfied by this approval and remain pending later sections or external resolution:

- **UI screens, read-only enforcement, and disclosure surfacing** — Section 6.
- **Kill-switch-driven SELL / TRIM / REPLACE behavior** — A-OQ-05-17 deferred; future Section 5 amendment.
- **Active → Warning automated trigger** — A-OQ-05-09 deferred; future 03c amendment.
- **Direct `config/costs.yaml` consumption for paper-state cost drag** — A-OQ-05-10 deferred; future amendment.
- **Account-type tax / execution constraints** — A-OQ-05-11 deferred; future phase.
- **ATR formula details** — A-PRP-05-14 / A-OQ-05-14 deferred; future amendment.
- **Regime classifier / labeler ownership** — A-OQ-04-07 remains external; not resolved within Section 5.
- **DiversifierHedge `absolute_with_context` ranking activation** — out of current Section 5 scope; depends on the future 03c amendment that adds absolute-trend / absolute-gain `model_kind` values per 03c approval note §1.4 item 14.
- **Live trading / broker SDK integration** — out of Phase 1 entirely per SDR Decision 1, 15, 18.

### 1.10 Carryovers from prior sections

The following Open Questions from prior sections are dispositioned by Section 5 lock:

47. **A-OQ-04-18 (backtest confidence-level outputs sufficiency)** — carried forward as A-OQ-05-15 and resolved as `existing Section 4 v1.0 evidence surfaces are sufficient` (see §1.7 item 36). No Section 4 amendment required before Section 5 lock; future Section 4 amendment may be triggered at implementation time if a real gap appears.
48. **A-OQ-04-14 (Active → Warning automated trigger definition)** — carried forward as A-OQ-05-09 and resolved as `Section 5 records recommendations only; no `models.*` writes; future 03c amendment required for mechanical transitions` (see §1.7 item 30).
49. **A-OQ-04-07 (regime classifier / labeler ownership)** — remains unresolved outside Section 5. Section 5 consumes regime evidence only when available and does not own or resolve the labeler. Section 6 inherits the same external carryover.

---

## 2. Process trail

1. **Section 4 lock as predecessor.** Section 4 v1.0 LOCKED / APPROVED on 2026-04-30 produced the Section 4 lock package (approval note, traceability companion, traceability_matrix.md v0.7) and explicit binding conditions on Section 5: read-only contract against `backtest.*` and `attribution.*`; the `is_pipeline_validation_only = false` filter (REP-07); non-consumption of `backtest.simulated_fills` as paper state (CC-09 + ALC-08); action-enum disjointness (CC-09); cadence independence (ALC-09); paper-only enforcement under SDR Decision 1 / Decision 15.
2. **Section 5 handoff prompt** (Approver-issued, lightweight, recorded in the v0.1 spec front matter as scope-statement basis). Per Approver direction, no separate Section 5 handoff packet file was issued; Section 5 drafting and revision were authorized to proceed from four sources taken together as the de facto scope statement: (a) the locked SDR, EW, and Sections 1–4; (b) the Section 4 approval note §5.1 *Open items handed forward to Section 5* and the Section 4-imposed conditions on Section 5; (c) the carryover Open Questions A-OQ-04-07, A-OQ-04-14, A-OQ-04-18; (d) the Approver-issued Section 5 prompt assigning ChatGPT as Builder / spec drafter and Claude as QA reviewer / stress tester for the Section 5 cycle only.
3. **v0.1 drafted** by the Builder (ChatGPT). Eleven EW §3.2 template fields populated in order. SDR Decisions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18 cited as directly implemented or respected. Open Questions and Proposed defaults visibly classified per EW §3.3.
4. **v0.1 → v0.2 revision pass** driven by the Claude QA report against v0.1 produced four blocking revisions plus five major and nine minor revisions: (B-01) gate terminology reconciled to 03c approval-note framing; (B-02) DiversifierHedge / `absolute_with_context` unranked-sleeve handling defined explicitly with no silent remapping; (B-03) ALC-09 cadence-independence test reservation added; (B-04) A-OQ-04-18 carried forward as A-OQ-05-15; (M-01) §6.9 SELL kill-switch contradiction removed; (M-02) formal field tables for `portfolio.kill_switch_evaluations`, `portfolio.kill_switch_triggers`, and `portfolio.promotion_evaluations` added; (M-03) action conversion rules tied to evidence filtering and per-sleeve `rank_method` semantics; (M-04) Section-4-owned schema names and locked terms verified including `pipeline_validation_only_reason='cost_config_zero_fallback'`; (M-05) `gate_kind` discriminator added to `portfolio.promotion_evaluations`. Builder applied all revisions surgically.
5. **v0.2 → v0.3 revision pass** driven by the Claude QA report against v0.2 produced six residual cleanups: restored the no-UI-import boundary test as test 7 with §8 renumbering; added `data_snapshot_id` to `paper.portfolio_snapshots`; clarified REPLACE output cardinality as one decision + one order intent + two paper events; removed `portfolio.kill_switch_triggers` from the issue-log list (it is an evaluation-decomposition table); clarified the common Section-5 issue-table field shape; added the regime-classifier ownership carryover (A-OQ-04-07) to Section 5 Out of scope.
6. **v0.3 → v1.0 candidate Approver dispositions.** The Approver resolved A-OQ-05-01 through A-OQ-05-16 (v0.3 ID-space) and accepted A-PRP-05-01 through A-PRP-05-17 (v0.3 ID-space) as Phase 1 defaults. Two Section-4-handoff carryovers were resolved at Section 5 level: A-OQ-04-18 → A-OQ-05-15 (Section 4 evidence sufficient); A-OQ-04-14 → A-OQ-05-09 (recommendations-only; no `models.*` writes). The gate terminology reconciliation was approved (`consumption` gate = 03c second promotion gate; `paper_to_real_recommendation` gate = Section 5 paper-evidence layer). A-OQ-04-07 regime-classifier ownership remains external.
7. **v1.0 candidate → v1.0 LOCKED revisions** driven by the Claude QA report against the v1 candidate produced four corrections: (R1) front-matter status label changed from `v1.0 LOCKED / APPROVED` to `v1.0 candidate (Approver dispositions applied; lock package pending)` to remove the contradiction with the changelog body that disclaimed the lock package; (R2) explicit ID-space mutation note added to the v1.0 changelog row enumerating the v0.3 → v1.0 A-PRP-05-15 / -16 swap, the absorption of v0.3 A-PRP-05-17 into A-PRP-05-05, the new v1.0 A-PRP-05-17, and the deferral of v0.3 A-OQ-05-16 to a new tracked A-OQ-05-17; (R3) A-OQ-05-17 (kill-switch-driven SELL/TRIM/REPLACE enablement) reinstated in §10 with deferral disposition; §11.5 cross-index updated; (R4) canonical filename restored to `05_portfolio_paper_order_intent.md` (no working-copy suffix).
8. **v1.0 candidate → v1.0 LOCKED / APPROVED authorization** by the Approver. v1.0 candidate (post-R-edit) promoted to v1.0 LOCKED / APPROVED with no substantive change to behavior, schema, tests, scope, or ownership; locking metadata flipped (status header, end-of-document marker); a final v1.0 changelog row appended recording the lock-merge step. Historical v0.1 → v0.3 → v1.0 candidate changelog entries preserved verbatim. The Approver exercised final-decision authority per EW §2.1 and approved without an additional QA cycle on the post-R-edit candidate.

---

## 3. Companion artifacts

- **Approved spec section:** `docs/engineering_spec/05_portfolio_paper_order_intent.md` (v1.0 LOCKED / APPROVED).
- **This approval note:** `docs/reviews/2026-04-30_spec_05_portfolio_paper_order_intent_approval.md`.
- **Section 5 traceability updates:** `docs/reviews/2026-04-30_spec_05_portfolio_paper_order_intent_traceability_updates.md`. Proposes replacement rows for SDR Decisions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, and 18 in `docs/traceability_matrix.md`, in the same shape as the Section 2 / Section 3a / Section 3b / Section 3c / Section 4 traceability-updates companion files. Application of the proposed replacement rows to `docs/traceability_matrix.md` is performed by the Approver as part of the Section 5 lock merge, bumping the matrix version from v0.7 to v0.8.
- **Section 4 handoff conditions** (reproduced in the Section 5 system-prompt scope-statement basis): the binding conditions imposed by Section 4's lock on Section 5, including the `is_pipeline_validation_only = false` filter, simulated-fills non-consumption, action-enum disjointness, cadence independence, and paper-only enforcement.

---

## 4. Conditions on subsequent sections

Section 5 v1.0 LOCKED / APPROVED imposes the following constraints on Section 6 (the only remaining Phase 1 section). Any change to these requires a Section 5 amendment with Approver approval per EW §3.3 (no assumption drift) and EW §2.3 (Approval Matrix), not silent override:

1. **UI is read-only with respect to `portfolio.*`, `paper.*`, `order_intent.*`** (and to `models.*`, `backtest.*`, `attribution.*`, `universe.*`, `prices.*`, `features.*`, `targets.*`, `ops.*` per prior sections). UI does not place orders, does not promote model states, does not trigger kill-switch evaluations, does not modify `config/portfolio.yaml`, does not write to any database table. The Section 5 §8.1 test 7 reserves the no-UI-import boundary check; the Section 6 implementation must additionally reserve a no-Section-5-write-from-`ui/` static check on the database-access side.
2. **Paper-only / non-executable disclosures must be surfaced on every UI view that displays an `order_intent.order_intents` row, a `portfolio.decisions` row, or a `paper.*` state row.** The `disclosures` section of `config/portfolio.yaml` ships the labels; UI surfaces them prominently and may not suppress them.
3. **The `gate_kind` discriminator and the kill-switch state must be displayed wherever portfolio decisions, promotion evaluations, or order intents are surfaced.** UI may not collapse `consumption` and `paper_to_real_recommendation` evaluations into a single visual representation in a way that loses the discriminator semantics. The `paused_by_kill_switch` paper portfolio status must be visually distinct from `active`.
4. **UI may not act on promotion-gate state.** Display only. Gate transitions remain entirely Section 5's responsibility through the `portfolio.promotion_evaluations` write path.
5. **UI may not act on kill-switch state.** Display only. Kill-switch evaluation and any resulting suppression of new BUY / REPLACE intents remain entirely Section 5's responsibility.
6. **UI may not enable any path that could constitute live trading.** No "place order" affordance, no broker-account selection, no broker-connection screen, no API key entry surface. The EW Approval Matrix item *"Any code path that could enable live trading"* binds Section 6 the same as it binds Section 5.
7. **UI may not own or resolve the regime classifier (A-OQ-04-07).** It may surface regime evidence when present (read-only) and must surface its absence honestly when not present.
8. **The Section 5 action enum (BUY / HOLD / TRIM / SELL / REPLACE / WATCH) is canonical for UI display.** UI may not introduce alternate action labels; UI may not display Section 4 simulated-fill actions (`enter_long`, `exit_long`, `rebalance_in`, `rebalance_out`) in any view that purports to show paper portfolio actions.
9. **REPLACE display semantics.** UI views over `order_intent.order_intents` must visually pair the `etf_id` and `replacement_etf_id` fields on REPLACE rows; the corresponding `paper.position_events` `paper_replace_out` and `paper_replace_in` rows must visually link as a pair.
10. **Account-type tax / execution constraints (A-OQ-05-11) are deferred.** UI may surface account-type placeholders but may not present them as enforcing real account constraints.
11. **No Section 5 amendment is proposed by Section 6 within Section 6's draft.** If a Section 5 amendment is genuinely needed, Section 6 flags it as an Open Question per EW §3.3 and the Approver decides.

---

## 5. Open items handed forward

### 5.1 Open items handed forward to Section 6

- **Read-only UI enforcement mechanism** (database-access side) for `portfolio.*`, `paper.*`, `order_intent.*` and the prior-section schemas. Section 1 reserved the choice of mechanism (per Section 1 §10.4 / EW Approval Matrix); Section 6 selects.
- **Disclosure surfacing patterns** for paper-only / non-executable labels, `gate_kind` semantics, kill-switch state, regime-evidence availability, and survivorship-disclosure context.
- **The seven UI screens** per SDR Decision 17 (UI is read-only): data quality dashboard, universe and eligibility, model and validation, paper portfolio, order intent log, attribution, system health. Section 6 owns scope; Section 5 imposes the read-only and disclosure-surfacing conditions in §4 above. SDR Decision 18 (Container architecture) is owned by Section 1 and is not in Section 5's footprint.
- **The UI test surface** including a static no-write test against every Section 5 schema, a disclosure-presence test on every paper-portfolio and order-intent view, and visual regression / snapshot tests on REPLACE rendering and kill-switch state rendering.

### 5.2 External carryovers and future amendments

- **A-OQ-04-07 — Regime classifier / labeler ownership.** Remains unresolved outside Section 5. Section 5 consumes regime evidence only when available and does not own or resolve the labeler. Section 6 inherits the same external carryover. Resolution path: a future strategy decision or Section 4 amendment, at Approver direction.
- **A-OQ-05-09 — Active → Warning automation.** Resolved as deferred. Section 5 records recommendations only. Mechanical transitions require a future 03c amendment under EW §6 impact assessment.
- **A-OQ-05-17 — Kill-switch-driven SELL / TRIM / REPLACE enablement.** Resolved as deferred. v1.0 kill switch only suppresses new BUY / REPLACE intents. Future enablement requires a Section 5 amendment with explicit tests and audit rules.
- **A-OQ-05-10 — Direct `config/costs.yaml` consumption.** Resolved as deferred for v1.0. Future enablement requires a Section 5 amendment.
- **A-OQ-05-11 — Account-type handling.** Resolved as deferred. Real-account execution constraints out of Phase 1.
- **A-OQ-05-14 / A-PRP-05-14 — ATR formula details.** Resolved as reserved-in-config / deferred. Future enablement requires a Section 5 amendment.
- **DiversifierHedge `absolute_with_context` ranking activation.** Out of Section 5 v1.0 scope. Section 5 honors the no-`combined_scores`-row disposition with no silent remapping. Activation requires a future 03c amendment that adds absolute-trend / absolute-gain `model_kind` values per 03c approval note §1.4 item 14.
- **Implementation-time Section 4 amendment trigger.** Per A-OQ-05-15 disposition, if implementation reveals that Section 4 v1.0 evidence surfaces lack a required field for the consumption-gate evidence bundle, a future Section 4 amendment is triggered under EW §6.

---

## 6. No-implementation discipline

No implementation begins until Section 5 is committed and traceability is updated. The matrix bump from v0.7 to v0.8 (per the companion artifact) and the addition of this approval note to the matrix changelog are prerequisites to any code under `portfolio/`, `paper/`, `order_intent/`, any migration file creating `portfolio.*`, `paper.*`, or `order_intent.*` tables, and any `config/portfolio.yaml` commit. The constraints in §1 and §4 above bind both the spec phase (no Section 6 spec content may contradict them) and the implementation phase (no code may bypass them).

---

**End of Section 5 approval note.**
