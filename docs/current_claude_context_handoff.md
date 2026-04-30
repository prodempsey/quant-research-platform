# Claude Context Handoff — Quant Research Platform

# Section 3c — Model Layer + MLflow: Handoff Packet

**Section to be drafted:** `docs/engineering_spec/03c_model_layer_mlflow.md`
**Date issued:** 2026-04-29
**Approver:** Jeremy
**Builder:** Claude (fresh chat; new context window)
**QA Reviewer:** ChatGPT

This packet authorizes Section 3c drafting per Engineering Workflow §2.2 (handoff packet) and §3 (engineering specification workflow). Section 3c is the third sub-section of the broader Section 3 split (3a Feature Engineering → 3b Target Generation → 3c Model Layer + MLflow) authorized by the Section 3 handoff packet (`docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`); this packet narrows that earlier broad authorization to 3c specifically and makes the per-decision constraints inherited from 3a and 3b explicit.

---

## 1. Authorization basis

03c drafting is authorized to proceed from **five** explicit Approver-authorized sources, taken together as the de facto scope statement (mirroring the lightweight handoff pattern Section 3b used):

(a) The general project handoff: `docs/current_claude_context_handoff.md`
(b) Section 3 handoff packet (broader Section 3 split authorization): `docs/reviews/2026-04-28_spec_03_features_targets_models_handoff_packet.md`
(c) Section 3a §12 forward references and Section 3a approval note §5.1 *"Open items handed forward to 03c"*
(d) Section 3b §12 forward references and Section 3b approval note §5.1 *"Open items handed forward to 03c"*
(e) This Section 3c handoff packet

The eventual 03c approval note can cite this language directly, mirroring the 03b approval note's scope-basis citation.

---

## 2. Controlling documents (Builder consults all of them)

- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Engineering Specification — Section 2 v1.0 LOCKED (`docs/engineering_spec/02_data_layer.md`)
- Engineering Specification — Section 3a v1.0 LOCKED / APPROVED (`docs/engineering_spec/03a_feature_engineering.md`)
- Engineering Specification — Section 3b v1.0 LOCKED / APPROVED (`docs/engineering_spec/03b_target_generation.md`)
- Section 1 approval note (`docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`)
- Section 2 approval note (`docs/reviews/2026-04-27_spec_02_data_layer_approval.md`)
- Section 3a approval note (`docs/reviews/2026-04-29_spec_03a_feature_engineering_approval.md`)
- Section 3b approval note (`docs/reviews/2026-04-29_spec_03b_target_generation_approval.md`)
- `docs/traceability_matrix.md` v0.5 (post-3b lock state)

---

## 3. Scope (in scope for 03c v0.1)

03c owns the model layer at the spec level. v0.1 covers all of:

1. **`models.*` database schema** (writer-owned by 03c). At minimum: `models.model_runs`, `models.model_definitions` (or equivalent catalog), `models.predictions` (the per-`(etf_id, as_of_date)` model output surface), and a model-layer issue log (the `*.run_issues` pattern parallel to `features.feature_run_issues` and `targets.target_run_issues` — see Open Question §7.6 below). Run-level reproducibility anchored on `data_snapshot_id`. Row-level traceability via `model_run_id`. Database-level integrity for any model-set-version analogue.

2. **Phase 1 baseline model forms.** The dual-target framework per SDR Decision 6: a regression model trained on the `targets.target_values` regression family (excess return at 63 and 126 trading-day horizons) and a classification model trained on the `targets.target_values` classification family (outperformance at the same horizons). The specific baseline algorithm class (e.g., gradient boosted trees, regularized linear, etc.) is an Open Question for the Approver — see §7.

3. **Calibration pipeline** per SDR Decision 7. SDR Decision 7 names the candidates (Platt / isotonic / logistic-on-folds); 03c picks the Phase 1 default and exposes the choice in `config/model.yaml` (Open Question §7).

4. **Combined-score formula** per SDR Decision 6's first testable formulation, integrating regression and classification model outputs into a single per-`(etf_id, as_of_date)` ranking score. The exact functional form is an Open Question — SDR Decision 6 names the framework but does not fix the formula. 03c proposes the first testable formula; Approver resolves.

5. **Allowed values and semantics for `rank_method`** (closing the Section 2 `pending_section_3` sentinel obligation). 03c defines the closed enumeration of allowed `rank_method` values, the per-sleeve semantics, and the validation that every `universe.etfs.rank_method` is one of the allowed values before any ranking runs. 03b does not interpret `rank_method`; 03c does.

6. **Combined-score × sleeve-aware ranking interaction.** Per SDR Decision 5, ranking is sleeve-aware. 03c specifies how the combined score per `(etf_id, as_of_date)` interacts with the sleeve assignment to produce the final ranking output consumed by Section 5 (portfolio).

7. **Model state lifecycle** per SDR Decision 12: the four states (Active / Warning / Paused / Retired), the transitions between them, and the schema fields recording state. 03c does NOT implement the multi-condition kill switch itself (Section 5 owns kill-switch enforcement) but defines the state machine and the conditions Section 5 will check.

8. **MLflow writer-side integration.** Per SDR Decision 11 and Section 1's MLflow-as-tracking architecture: 03c is the only Phase 1 module that writes to MLflow. Every MLflow run links back to BOTH `features.feature_runs.feature_run_id` AND `targets.target_runs.target_run_id` to satisfy the EW §7 reproducibility list (per Section 3a approval note §4.6 and Section 3b approval note §4.6). MLflow tags / params / metrics conventions are 03c's to specify.

9. **`config/model.yaml`** — the model-layer config file owned by 03c. Strategy-affecting per EW §7. 03c specifies the YAML shape (model algorithm choice, hyperparameter ranges, calibration method, combined-score formula parameters, target-set-version / feature-set-version pinning, etc.) and the validation rules. **`config/targets.yaml` is NOT owned by 03c** — Section 3b owns it per Section 3b §11.6 #7. 03c may *read* target metadata at consumption time but does not modify the target-config file.

10. **Training-data assembly contract.** 03c is responsible for joining `features.feature_values` (filtered on `features.feature_runs.status='succeeded'`) and `targets.target_values` (filtered on `targets.target_runs.status='succeeded'`) on `(etf_id, as_of_date)` to assemble training data. Both filters must be applied; the failed-run consumption discipline is binding. Front-edge horizon truncation must be handled correctly (the target side is missing for the most recent `max_horizon` trading days that have feature rows). 03c training-data-assembly tests verify both filters are applied and the front-edge truncation is handled correctly.

11. **Tests** for all of the above, per EW §3.2 template field 9. Per-family tests, schema tests, MLflow integration tests, training-data-assembly tests, model state lifecycle tests, calibration tests, combined-score tests.

---

## 4. Out of scope (explicitly NOT in 03c v0.1)

- **Walk-forward validation harness, purge/embargo enforcement, leakage tests, regime reporting, attribution storage** — Section 4 owns these. 03c records the per-row metadata Section 4 needs (`data_snapshot_id`, `feature_run_id`, `target_run_id`, `model_run_id`) on every prediction row but does not run walk-forward itself.
- **Multi-condition kill switch enforcement and live promotion gates** — Section 5 owns these. 03c defines the model state lifecycle; Section 5 acts on it.
- **Portfolio construction, risk rules, position sizing, paper-only enforcement** — Section 5.
- **UI surfaces** (Model Registry / Run Browser, leaderboards, Model Cards) — Section 6. 03c specifies the schema Section 6 reads from.
- **Modifying `targets.*`, `features.*`, `universe.*`, `prices.*`, `ops.*` schemas** — these are owned by Section 3b, 3a, and 2 respectively. 03c is read-only against all of them. 03c does NOT write to `ops.data_quality_exceptions` (per Section 2 v1.0 LOCKED, ingestion-owned in Phase 1).
- **Live trading code paths or broker integration** — out of Phase 1 entirely per SDR Decision 1.
- **Sleeve-conditional model variants** (a separate model per sleeve, etc.) — out of scope unless the Approver explicitly directs otherwise. Phase 1 default is one model per family across all sleeves, with sleeve-aware ranking applied downstream of model output.
- **Autonomous research agents, Danelfin integration, fundamentals/holdings/news/earnings/options inputs** — out of Phase 1 per SDR Decisions 1 and 14.
- **Implementation / code / migrations** — 03c v0.1 is a specification, not a build. Migration filenames and module file names are at Builder discretion within the EW §8 conventions; the spec references the schema names but does not prescribe filenames.

---

## 5. Constraints inherited from prior locked sections

The Builder must respect ALL of the following without re-litigating. Any divergence requires an explicit amendment to the section that owns the constraint, not a silent override.

### 5.1 From Section 1 (v1.0 LOCKED) — architectural invariants

- Provider-abstraction boundary: no `models/` module imports from `providers/`, `ingestion/`, or any provider-specific library.
- Postgres-as-system-of-record: 03c's authoritative state is in Postgres (`models.*`); MLflow is the tracking surface, not the system of record.
- No-live-broker boundary: 03c writes no code that could enable live trading.
- All paths via `pathlib.Path`; container-local paths only.
- No secrets in code, config, fixtures, logs, or docs.
- Time-aware research auditability invariant 7: 03c's contribution is honoring the upstream T-1 / forward-Convention-B alignment from 3a/3b (not redefining it) and adding model-side reproducibility metadata (`model_run_id` linkage to `feature_run_id`, `target_run_id`, `data_snapshot_id`).
- UI is read-only: `models.*` schema design supports read-only consumption from `ui/`.

### 5.2 From Section 2 (v1.0 LOCKED) — data-layer constraints

- 03c is read-only against `prices.*`, `universe.*`, `ops.*`, `features.*`, `targets.*`. The only schema 03c writes to is `models.*`.
- 03c does NOT write to `ops.data_quality_exceptions`. The data-quality framework remains ingestion-owned per Section 2 v1.0 LOCKED constraint #1.
- `data_snapshot_id` is the reproducibility anchor on the writer side. Every `models.model_runs` row carries one.
- Adjusted-close is canonical research price. Any model that uses raw OHLCV is forbidden without an explicit Section 2 amendment.
- Provider raw payloads, ingestion runs, and corporate actions are read-only from 03c's perspective.

### 5.3 From Section 3a (v1.0 LOCKED / APPROVED) — feature-side constraints

- **Failed-run consumption discipline:** 03c reads `features.feature_values` ONLY filtered on `features.feature_runs.status='succeeded'`. Tests must verify this filter on every feature consumption path.
- **`feature_set_version` integrity:** 03c reads features at a pinned `feature_set_version` recorded in `config/model.yaml`; the database-level UNIQUE / composite-FK constraints are already enforced by 3a's schema.
- **Eligibility-row omission contract:** 03c does NOT filter feature rows by re-deriving eligibility — absence in `features.feature_values` is the consumption signal. 03c likewise does NOT add rows for ineligible pairs.
- **T-1 trading-day alignment:** 03c does NOT re-align features. The `as_of_date` on a feature row is the signal date `T`; the values themselves are bounded by `as_of_date <= T-1`. 03c consumes them as-is.
- **Index-only benchmark interim constraint:** 03c may not introduce a fallback-to-secondary-benchmark mechanism. Any feature row with `feature_value = NULL` due to index-only-benchmark conditions is consumed as a NULL by the model (handling is a model-level concern: imputation, exclusion, or model-class-specific NULL semantics — Builder Open Question §7).

### 5.4 From Section 3b (v1.0 LOCKED / APPROVED) — target-side constraints

- **Failed-run consumption discipline (parallel to 5.3):** 03c reads `targets.target_values` ONLY filtered on `targets.target_runs.status='succeeded'`.
- **`target_set_version` integrity:** 03c reads targets at a pinned `target_set_version` recorded in `config/model.yaml`. Database-level UNIQUE / composite-FK constraints are already enforced by 3b's schema.
- **§6.5 null-vs-no-row taxonomy is canonical:** 03c does NOT reframe Bucket 1 (no-row) cases as `target_value = NULL` rows or Bucket 2 (row-with-NULL) cases as row absences. 03c training-data-assembly logic respects the existing taxonomy.
- **Convention B trading-day semantics:** 03c does NOT redefine `entry_date` / `exit_date` (e.g., does not silently switch to calendar-day arithmetic). The 03b-recorded window metadata is the canonical source.
- **No purge/embargo at target emission:** Section 4 owns purge/embargo. 03c records `model_run_id` linkage to `target_run_id` so Section 4 has the per-row window metadata it needs; 03c does NOT apply purge/embargo at training-data-assembly time. (03c MAY apply in-fold cross-validation discipline at training time, but the walk-forward train/test boundary is Section 4's responsibility.)
- **Index-only benchmark interim constraint (parallel to 5.3):** Same rule on the target side.
- **`targets.target_run_issues` is read-only from 03c.** 03c may filter or annotate model runs that depend on target runs with issues, but does not write to `target_run_issues`.

### 5.5 Additional constraints inherited from the 3a/3b approval notes' "conditions on subsequent sections"

- The two issue-log tables (`features.feature_run_issues`, `targets.target_run_issues`) are deliberately separate from `ops.data_quality_exceptions`. If 03c introduces a model-layer issue log (Open Question §7.6), it follows the same pattern: a closed `issue_type` enumeration, a `severity` enumeration, an open-run-before-validation lifecycle, NOT NULL FK on `model_run_id`, and writes to `models.*` only.
- The benchmark-resolution interim constraint applies on the model side too: no silent benchmark substitution, no fallback to `secondary_benchmark_id`, anywhere in 03c's code paths.
- The reproducibility chain is `ops.data_snapshots → features.feature_runs (and targets.target_runs) → models.model_runs → MLflow`. 03c MAY NOT bypass this chain.

---

## 6. EW §3.2 template fields the spec must populate

Per EW §3.2, Section 3c v0.1 must populate the following eleven fields **in this order**:

1. Purpose
2. Relevant SDR decisions
3. In scope
4. Out of scope
5. Inputs and outputs
6. Data contracts (covering `models.*` schema in detail)
7. Config dependencies (covering `config/model.yaml` and read dependencies on `config/features.yaml`, `config/targets.yaml`, `config/universe.yaml`)
8. Required tests (per-family + cross-cutting)
9. Edge cases and failure behavior
10. Open questions
11. Explicit assumptions (classified per EW §3.3 — Approver-resolved defaults, Builder Proposed defaults requiring Approver approval, Open Questions for Approver, Implementation defaults with no strategy impact)
12. Section 3c → Section 4 handoff (forward references only)
13. Proposed traceability matrix updates (draft only — full companion artifact produced as a separate review file at lock time)

Every Open Question and Builder Proposed default is **visibly classified** per EW §3.3. **Nothing is silently resolved.**

---

## 7. Non-exhaustive list of Open Questions the Builder will surface

These are the Open Questions the prior session identified as belonging to 03c. The Builder will likely identify more during drafting; this list is a starting point, not a closed set.

### 7.1 Combined-score formula (SDR Decision 6's first testable formulation)
Functional form combining regression and classification model outputs. Candidates: linear weight (`w * regression_score + (1-w) * classification_probability`); product (`regression_score * classification_probability`); rank-then-combine. **Builder proposes; Approver resolves.**

### 7.2 Phase 1 baseline model class
SDR Decision 6 names the dual-target framework but not the model class. Candidates: gradient boosted trees (XGBoost / LightGBM), regularized linear (ridge, lasso, elastic net), or simple baselines (e.g., past-return-as-prediction). **Builder proposes; Approver resolves.**

### 7.3 Calibration method
SDR Decision 7 names Platt / isotonic / logistic-on-folds as candidates. Phase 1 default? **Builder proposes; Approver resolves.**

### 7.4 `rank_method` allowed values and semantics
The closed enumeration that closes Section 2's `pending_section_3` sentinel obligation. Candidates likely include: `combined_score_descending`, `regression_score_descending`, `classification_probability_descending`, possibly sleeve-conditional variants. **Builder proposes; Approver resolves.**

### 7.5 NULL-feature handling at model train/predict time
Features carrying `feature_value = NULL` (per the Bucket 2 cases in 3a) reach the model. Phase 1 strategy: imputation (mean / median / sentinel), exclusion (drop the row), or model-class-specific (XGBoost handles NULLs natively). **Builder proposes; Approver resolves.**

### 7.6 Model-layer issue log
Should 03c introduce `models.model_run_issues` parallel to `feature_run_issues` and `target_run_issues`? **Builder Proposed default: yes**, for consistency with the established pattern, with a closed `issue_type` enumeration covering at minimum: `'invalidated_snapshot_blocked'`, `'failed_feature_run_blocked'`, `'failed_target_run_blocked'`, `'partial_*` analogues, `'model_run_failed'`. **Approver resolves.**

### 7.7 Model state lifecycle transitions and gating conditions
SDR Decision 12 names the four states. 03c specifies the state machine (allowed transitions, conditions, who can trigger). **Builder proposes; Approver resolves.**

### 7.8 MLflow tags / params / metrics conventions
What gets recorded as tags vs. params vs. metrics. **Builder proposes; mostly Implementation default with no strategy impact unless the Approver wants to override.**

### 7.9 `models.*` migration filename
**Implementation default with no strategy impact** — assigned at module-build time per EW §8 conventions, mirroring 3a's `features.*` and 3b's `targets.*` deferrals.

### 7.10 Sleeve-conditional model variants
Phase 1 default: one model per family across all sleeves; sleeve-aware ranking is applied downstream of model output. Approver may direct sleeve-conditional models if desired. **Builder Proposed default: cross-sleeve.**

### 7.11 Cross-validation strategy at training time
03c may apply in-fold CV during training (separate from Section 4's walk-forward harness). **Builder proposes; Approver resolves.**

### 7.12 Whether to introduce model versioning beyond MLflow's run-id
A `model_set_version` analogue to `feature_set_version` / `target_set_version`? **Builder Proposed default: yes**, for consistency. **Approver resolves.**

This list is not exhaustive. The Builder will identify additional Open Questions during drafting and classify them per EW §3.3.

---

## 8. Approval gate

Per EW §2.3 Approval Matrix, Section 3c v0.1 falls under the following items requiring Approver approval:

- Engineering Specification section finalization (per EW §3.4)
- Database schema changes at the spec level (the `models.*` schema)
- Strategy-affecting YAML config changes at the spec level (`config/model.yaml`)
- Changes to feature, target, or label definitions (the dual-target framework's model-side cash-out, the combined-score formula, the calibration method)
- Changes to ranking math (`rank_method` allowed values and semantics)
- Model registry schema and model state lifecycle (per SDR Decisions 11 and 12)

The eventual 03c approval note will enumerate exactly which Approval Matrix items the section satisfies, mirroring the Section 3a and 3b approval notes' §1 *What approval covers* sections.

---

## 9. Workflow expectation (EW §3)

The Builder follows the standard EW §3 cycle:

1. **v0.1 DRAFT.** Builder produces the initial draft in /home/claude (or equivalent workspace), populating all eleven §3.2 template fields in order. Every assumption classified per EW §3.3. Honors all constraints in §5 of this packet. Surfaces Open Questions visibly per §7 and any additions found during drafting.
2. **Approver reviews v0.1.** Issues a targeted revision instruction (typically a numbered list of specific revisions, plus preservation of accepted v0.1 strengths). 03c is the largest section so far — expect more revisions than 3a (5) or 3b (6).
3. **v0.1 → v0.2 revision pass.** Builder applies the Approver's revisions surgically (str_replace edits, not whole-doc rewrites). Each revision is recorded in a v0.2 changelog entry preserving v0.1 verbatim.
4. **(Optional) v0.2 → v0.3 cleanup pass** if the Approver issues a follow-up cleanup instruction (mirroring the 03b v0.3 pattern).
5. **Lock package.** Approver authorizes promotion to v1.0 LOCKED / APPROVED. Builder produces three artifacts:
   - `docs/engineering_spec/03c_model_layer_mlflow.md` v1.0 LOCKED / APPROVED
   - `docs/reviews/<DATE>_spec_03c_model_layer_mlflow_approval.md` (the approval note)
   - `docs/reviews/<DATE>_spec_03c_model_layer_mlflow_traceability_updates.md` (the traceability companion)
6. **Approver applies the traceability merge** to `docs/traceability_matrix.md` per the runbook (`HOW_TO_apply_traceability_matrix_update.md`); matrix v0.5 → v0.6.
7. **Section 4 handoff packet** is issued separately, after 03c lock.

---

## 10. Output format

03c v0.1 is a single markdown file. No code. No migrations. No images. No fancy formatting beyond the EW conventions established by 3a and 3b. Tables for schema definitions are fine. YAML blocks are fine for `config/model.yaml` shape. Everything else is prose.

The Builder uses str_replace edits (surgical) once the v0.1 baseline is in place — not whole-doc rewrites — to preserve EW revision discipline.

The Builder DOES NOT:

- Write code.
- Run migrations.
- Build containers.
- Modify any other spec section.
- Modify the SDR or EW.
- Propose Section 1 amendments without explicit Approver direction (the same discipline 3a and 3b followed).
- Silently resolve any Open Question.

---

## 11. Notes on the fresh-context-window handoff

Section 3c is being drafted in a fresh chat window with no prior session memory. The Builder should:

1. Read this handoff packet first.
2. Read `docs/current_claude_context_handoff.md` for the project map.
3. Read SDR v1.0 and EW v1.5 in their entirety.
4. Read Sections 1, 2, 3a, and 3b in their entirety.
5. Read all four prior approval notes (Section 1, 2, 3a, 3b).
6. Read `docs/traceability_matrix.md` v0.5 (post-3b lock state).
7. Confirm understanding back to the Approver before producing v0.1.

The Approver may direct the Builder to skip step 7 and proceed directly to v0.1 if context is clear; default is to confirm.

---

**Signed:** Jeremy (Approver), 2026-04-29.

**End of Section 3c handoff packet.**
2. Confirm receipt of the handoff packet and acknowledge any Open Questions in it before producing v0.1.
3. Use the EW §3.2 eleven-field template in order. Classify every assumption per EW §3.3.
