# Claude Context Handoff — Quant Research Platform

**Document path in repo:** `docs/current_claude_context_handoff.md`
**Last updated:** 2026-04-29
**Maintainer:** Jeremy
**Purpose:** Bring a fresh Claude chat session up to date on the project state without making the human re-paste files.

---

## How to use this document

This handoff is the first thing a new Claude chat session should read when working on the **Quant Research Platform** project. It is not a substitute for the canonical files — it is a map that points to them and a snapshot of "where things stand right now."

### Source of truth: GitHub, not uploads

**Use the GitHub connector to read project files. Do not ask the human to upload files.** All canonical project documents live in the repository below. The human is the Approver, not a file-upload service; reading from GitHub is faster, less error-prone, and ensures Claude works against the actual current state of the repo rather than a possibly stale local copy.

- **Repository:** `prodempsey/quant-research-platform`
- **Branch:** `main`
- **Connector:** GitHub (search the MCP registry for "github" if it isn't already connected; suggest the connector to the human if so).

If for any reason the GitHub connector is unavailable, ask the human before falling back to file uploads — do not silently proceed against stale assumptions.

### Files to read first, in order

When a fresh Claude session begins, read these in order before responding to any new task:

1. **This document** (`docs/current_claude_context_handoff.md`) — the map.
2. **`docs/strategy_decision_record.md`** — the canonical SDR. v1.0 LOCKED. 18 numbered decisions.
3. **`docs/engineering_workflow.md`** — the canonical EW. v1.5 LOCKED. Defines the Approver/Builder/Reviewer roles, the section-drafting workflow, the Approval Matrix (§2.3), the spec-section template (§3.2), the assumption classification rules (§3.3), the QA review checklist (§9), and the configuration-management discipline (§7).
4. **`docs/traceability_matrix.md`** — the canonical traceability matrix. Currently **v0.4** (Sections 1, 2, 3a v1.0 LOCKED merged; Sections 3b, 3c, 4, 5, 6 still pending).
5. **`docs/engineering_spec/`** — directory of locked Engineering Specification sections. Currently:
   - `01_architecture_overview.md` (v1.0 LOCKED)
   - `02_data_layer.md` (v1.0 LOCKED)
   - `03a_feature_engineering.md` (v1.0 LOCKED / APPROVED)
6. **`docs/reviews/`** — directory of approval notes, traceability companion artifacts, and Section-level handoff packets. Read whichever ones are relevant to the task at hand. Notable files:
   - `2026-04-26_spec_01_architecture_overview_approval.md`
   - `2026-04-27_spec_02_data_layer_approval.md`
   - `2026-04-27_spec_02_data_layer_traceability_updates.md`
   - `2026-04-28_spec_03_features_targets_models_handoff_packet.md`
   - `2026-04-29_spec_03a_feature_engineering_approval.md`
   - `2026-04-29_spec_03a_feature_engineering_traceability_updates.md`

---

## Project at a glance

**What it is:** A personal quant research platform for ETF tactical research. Phase 1 is research-only — no live trading, no broker integration, paper portfolio tracking only.

**Maintainer / Approver:** Jeremy.

**Builder for spec work:** Claude (Anthropic).

**QA Reviewer for spec work:** ChatGPT.

**Hosting:** Linux VPS (Hostinger), multi-container Docker stack.

**Stack at a glance:**
- Postgres as system of record (universe, prices, ops, features schemas).
- MLflow for experiment tracking, with metadata in a separate Postgres database and artifacts in a named volume.
- Dash app as the operator UI (read-only).
- cron-in-container for scheduled jobs (ingestion, feature runs, model runs, backtests).
- EODHD as the Phase 1 data provider, accessed only through the provider-abstraction boundary.
- Python 3.12, `pyproject.toml` + pinned `requirements.txt`, ruff, pytest.

**Phase 1 hard exclusions** (do not propose, do not silently introduce): live trading, broker SDKs, fundamentals, ETF holdings data, news, earnings transcripts, options data, Danelfin (deferred), individual stocks, autonomous research agents, commercial / customer-facing features.

---

## Roles (from EW §2.1)

- **Approver (Jeremy)** has final decision authority on every section, every default, every strategy-affecting choice, and every Approval Matrix item. Claude does not silently resolve strategy-affecting questions — they are flagged as Open Questions for the Approver per EW §3.3.
- **Builder (Claude)** drafts spec sections, applies targeted revisions, and produces lock-package artifacts (approval notes, traceability companion files). The Builder follows the EW §3.2 eleven-field template, classifies assumptions per EW §3.3, and respects the EW §3.5 stop conditions.
- **QA Reviewer (ChatGPT)** reviews drafts against the EW §9 checklist and produces revision lists. Claude applies QA-driven revisions surgically (via `str_replace`) rather than rewriting whole documents.

---

## Where things stand (as of 2026-04-29)

### Locked artifacts

| Artifact | Status | Path |
|---|---|---|
| Strategy Decision Record | v1.0 LOCKED | `docs/strategy_decision_record.md` |
| Engineering Workflow | v1.5 LOCKED | `docs/engineering_workflow.md` |
| Engineering Spec — Section 1 (Architecture Overview) | v1.0 LOCKED | `docs/engineering_spec/01_architecture_overview.md` |
| Engineering Spec — Section 2 (Data Layer) | v1.0 LOCKED | `docs/engineering_spec/02_data_layer.md` |
| Engineering Spec — Section 3a (Feature Engineering) | v1.0 LOCKED / APPROVED | `docs/engineering_spec/03a_feature_engineering.md` |
| Traceability Matrix | v0.4 | `docs/traceability_matrix.md` |

### Pending — drafting not yet authorized

- **Section 3b — Target Generation** (`docs/engineering_spec/03b_target_generation.md`)
- **Section 3c — Model Layer + MLflow** (`docs/engineering_spec/03c_model_layer_mlflow.md`)
- **Section 4 — Backtest, Attribution, Validation**
- **Section 5 — Portfolio Management, Paper Trading, Order Intent**
- **Section 6 — UI Layer**

The Approver will issue a fresh handoff packet under `docs/reviews/` (similar in shape to `2026-04-28_spec_03_features_targets_models_handoff_packet.md`) when authorizing each next section.

### Implementation status

**No code has been written. No migrations have been run. No containers have been built.** The locked spec sections are specifications, not builds. Implementation begins under the EW §3 → §10 build workflow once the Approver authorizes it, after enough sections are locked for a meaningful build slice.

---

## Section 3a quick-reference (most recent lock)

Because Section 3a is the most recent lock and any Section 3b / 3c handoff will reference it heavily, here is a compact summary of what 3a does and does not own. The full text is in `docs/engineering_spec/03a_feature_engineering.md`.

### What 03a owns

- **Feature families** (Phase 1, in `config/features.yaml`):
  - Family 1: returns / momentum (`return_21d`, `return_63d`, `return_126d`, `return_252d`)
  - Family 2: realized volatility (`vol_realized_21d`, `vol_realized_63d`, `vol_realized_126d`)
  - Family 3: trend strength — distance from SMA (`trend_dist_sma_50`, `trend_dist_sma_200`)
  - Family 4: benchmark-relative excess return (`excess_return_vs_primary_benchmark_63d`, `excess_return_vs_primary_benchmark_126d`)
  - Family 5: regime-side feature primitive (`regime_spy_above_sma_200`) — **default off**
- **`features.*` schema** (four tables, all in the `features` schema):
  - `features.feature_runs`
  - `features.feature_definitions`
  - `features.feature_values`
  - `features.feature_run_issues`
- **`config/features.yaml`** — strategy-affecting config; closed-set family validation.
- **T-1 trading-day alignment** on every feature row (T-1 = most recent valid trading day strictly before signal date `T` per the relevant ETF's `prices.etf_prices_daily` rows; not calendar minus one).
- **Eligibility-row omission contract** — no `features.feature_values` row is written for ETF/date pairs that are not rank-eligible per `universe.etf_eligibility_history`, or where `T < first_traded_date(e)` or `T >= delisted_date(e)`. Ineligible rows are absent, not stored with a flag.
- **`data_snapshot_id` reproducibility chain** — run-level linkage on `features.feature_runs.data_snapshot_id`, row-level traceability via composite FK from `features.feature_values(feature_run_id, feature_set_version)` to `features.feature_runs(feature_run_id, feature_set_version)`.
- **Database-level `feature_set_version` integrity** — `UNIQUE (feature_run_id, feature_set_version)` on `features.feature_runs`, plus two composite FKs from `features.feature_values` (one to `feature_runs`, one to `feature_definitions`).
- **Open-run-before-validation lifecycle for blocked runs** — orchestrator opens the `features.feature_runs` row first, then validates snapshot and ingestion-run dependencies; on a block, it marks the run `'failed'` and writes a `features.feature_run_issues` row (FK satisfied); no `features.feature_values` rows are written for blocked runs.
- **36 numbered required tests** (17 per-family in §8.1, 19 cross-cutting in §8.2).

### What 03a does NOT own (forward references)

- **Target generation** (regression, classification, forward excess-return labels at 63/126-day horizons, overlapping-label handling) — **03b**.
- **Baseline models, calibration, MLflow writer-side integration, `models.*` schema, model state lifecycle, allowed `rank_method` values (closing the Section 2 `pending_section_3` sentinel), combined-score formula, `config/model.yaml`** — **03c**.
- **Walk-forward harness, purge/embargo, transaction costs, attribution storage, regime reporting layer** — **Section 4**.
- **Portfolio rules, BUY/HOLD/TRIM/SELL/REPLACE/WATCH actions, paper portfolio state, broker-neutral order intent** — **Section 5**.
- **Dash UI screens** — **Section 6**.
- **Full `regime/` subpackage and `regime.*` schema** — Sections 3 (computation) and 4 (consumption).

### What 03a does NOT write to

- `ops.data_quality_exceptions` — **ingestion-owned per Section 2 v1.0 LOCKED**. 03a does not write to this table or any `ops.*` table. Feature-layer data-quality issues land in `features.feature_run_issues` instead.
- `universe.*`, `prices.*`, `targets.*`, `models.*`, MLflow, any provider table.

### Open Questions still open after Section 3a lock (Approver's call)

- **Index-only benchmarks** (§10.1 in 03a). Family 4 is unavailable for an ETF whose primary benchmark resolves index-only via `universe.benchmarks.index_symbol`; no silent substitution; no fallback to `secondary_benchmark_id`. Whether to pursue a Section 2 amendment for benchmark price storage remains the Approver's decision. **No such amendment is proposed by 03a.**
- Plus seven Builder Proposed defaults (§10.2–§10.8) the Approver may revise via 03a amendment without disturbing the locked structural contracts.

---

## Working norms for fresh Claude sessions

These norms come from the EW and from the established working pattern across Sections 1, 2, and 3a. Following them avoids re-litigating ground covered.

### Always

- **Read from GitHub, not uploads.** Repository `prodempsey/quant-research-platform`, branch `main`. If the GitHub connector isn't available, ask the human before doing anything else.
- **Acknowledge the task and read the canonical files before drafting.** For any spec-related task, read the SDR, EW, the relevant locked sections, and the relevant approval notes. State what was read.
- **Honor the EW §3.2 eleven-field template** when drafting a new section: Purpose, Relevant SDR decisions, In scope, Out of scope, Inputs and outputs, Data contracts, Config dependencies, Required tests, Edge cases and failure behavior, Open questions, Explicit assumptions.
- **Classify every assumption per EW §3.3.** The seven categories are: *Derived from SDR/EW*, *Derived from Section 1*, *Derived from Section 2* (extend per locked predecessor section), *Implementation default (no strategy impact)*, *Approver-resolved default*, *Proposed default requiring Approver approval*, *Open question for Approver*. Strategy-affecting items are the last two — never the third or fourth.
- **Use Approver-issued handoff packets** as the authoritative scope statement for a new section. If the human starts a section without one, ask for one before drafting v0.1.
- **Apply targeted revisions surgically** via `str_replace` on the existing draft. Do not rewrite whole documents in response to QA feedback.
- **Produce lock packages in the established three-artifact shape** (when locking a section): the section itself promoted to v1.0 LOCKED / APPROVED, a separate approval note under `docs/reviews/`, and a separate traceability matrix update companion under `docs/reviews/`.
- **Match canonical file names exactly.** No spaces, no hyphens-instead-of-underscores, no title casing. Examples: `03a_feature_engineering.md` (not `03a feature engineering.md`), `03c_model_layer_mlflow.md` (not `03c_model_layer.md`).

### Never

- **Never silently resolve strategy-affecting questions.** Flag them as Open Questions for the Approver per EW §3.3.
- **Never propose modifications to the SDR.** The SDR is v1.0 LOCKED. SDR revisions follow EW §6 impact assessment and are the Approver's call, not the Builder's.
- **Never propose modifications to Section 1 or Section 2 within a later section's draft.** If a Section 2 amendment is genuinely needed, flag it as an Open Question; do not draft the amendment within the current section.
- **Never start implementation, write code, run migrations, or build containers** unless the Approver has explicitly authorized the implementation phase for the relevant section.
- **Never expand scope beyond Phase 1.** No fundamentals, holdings, news, earnings, options, individual stocks, autonomous research agents, commercial features, or live broker integration.
- **Never reframe locked decisions** ("I think Decision N actually means…"). Locked decisions are locked. If a locked decision seems wrong or incomplete in light of new information, raise the concern explicitly and let the Approver decide.
- **Never bypass the eligibility, T-1, adjusted-close, or `data_snapshot_id` contracts** in any later-section draft. These are the principal Section 3a / Section 2 / Section 1 invariants.

### Process tells (working pattern across the locked sections)

- A typical section moves v0.1 → v0.2 → v0.3 → v0.4 → v1.0 LOCKED / APPROVED, with QA-driven revisions at each step. Section 3a took four revision passes; Section 2 took three; Section 1 took two.
- Each revision pass produces a numbered revisions list with a "Revision N — short title — locations affected" structure. Builder applies edits surgically and confirms each revision lands.
- Lock package = three artifacts: locked spec, approval note, traceability matrix update companion. The approval note lists every explicit Approver decision; the traceability update companion proposes replacement rows for affected SDR decisions.
- After each lock, the Approver applies the traceability companion's proposed rows to `docs/traceability_matrix.md` as a separate task.

---

## Repository layout (for orientation)

```
prodempsey/quant-research-platform
├── docs/
│   ├── current_claude_context_handoff.md      # this file
│   ├── strategy_decision_record.md            # SDR v1.0 LOCKED
│   ├── engineering_workflow.md                # EW v1.5 LOCKED
│   ├── traceability_matrix.md                 # v0.4
│   ├── engineering_spec/
│   │   ├── 01_architecture_overview.md        # v1.0 LOCKED
│   │   ├── 02_data_layer.md                   # v1.0 LOCKED
│   │   └── 03a_feature_engineering.md         # v1.0 LOCKED / APPROVED
│   └── reviews/
│       ├── 2026-04-26_spec_01_architecture_overview_approval.md
│       ├── 2026-04-27_spec_02_data_layer_approval.md
│       ├── 2026-04-27_spec_02_data_layer_traceability_updates.md
│       ├── 2026-04-28_spec_03_features_targets_models_handoff_packet.md
│       ├── 2026-04-29_spec_03a_feature_engineering_approval.md
│       └── 2026-04-29_spec_03a_feature_engineering_traceability_updates.md
└── (no code yet — Phase 1 implementation has not been authorized)
```

When the next section is authorized, expect new files under `docs/engineering_spec/` and `docs/reviews/`. When implementation begins, expect a `src/quant_research_platform/`, `tests/`, `migrations/`, `config/`, `Dockerfile`, `docker-compose.yml`, etc., per the Section 1 layout.

---

## Common task patterns and how to handle them

### "Draft Section 3X v0.1"

1. Read this handoff, then read the SDR, EW, all locked sections (1, 2, 3a), and the section-specific handoff packet under `docs/reviews/`.
2. Confirm receipt of the handoff packet and acknowledge any Open Questions in it before producing v0.1.
3. Use the EW §3.2 eleven-field template in order. Classify every assumption per EW §3.3.
4. Output the draft as a markdown artifact with the exact canonical filename (e.g., `03b_target_generation.md`).

### "Apply QA revisions to v0.X"

1. Read the QA revision list carefully. Each revision typically names affected sections.
2. Apply each revision via targeted `str_replace` edits, one at a time. Do not rewrite the whole document.
3. After each revision, verify with `grep` or by viewing the affected region.
4. Add a new changelog entry summarizing the revisions; preserve historical changelog entries verbatim.
5. Output the revised draft (e.g., promoted from v0.X to v0.X+1).

### "Promote v0.X to v1.0 LOCKED"

1. Produce three artifacts in the established shape:
   - The section itself, with status flipped to v1.0 LOCKED / APPROVED, a v1.0 changelog entry added, and minor wording cleanup applied (stale "v0.X scope" references in current spec body, not in changelog entries).
   - The approval note: `docs/reviews/YYYY-MM-DD_spec_03X_<name>_approval.md`. Mirror the Section 1 / 2 / 3a approval-note structure: what approval covers, process trail, companion artifacts, conditions on subsequent sections, open items handed forward, implementation status, signed approval.
   - The traceability matrix update companion: `docs/reviews/YYYY-MM-DD_spec_03X_<name>_traceability_updates.md`. Mirror the Section 2 / 3a companion-file structure: replacement rows in 7-column format, audit findings, maintainer notes.
2. Do not apply the traceability companion's rows to `docs/traceability_matrix.md` unless explicitly instructed.

### "Apply Section 3X traceability matrix updates"

1. Read the Section 3X traceability companion under `docs/reviews/`.
2. Read the current `docs/traceability_matrix.md`.
3. Apply replacement rows surgically. Preserve verbatim the rows for decisions not affected.
4. Add a version-history entry to the matrix's Notes section.
5. Update the document status header and the in-spec interpretation note.

### "Something else"

If the task isn't one of the above patterns — e.g., a Section 2 amendment is genuinely needed, an SDR revision is being considered, an implementation phase is being authorized, or the Approver wants to discuss a strategic question — read the relevant files and ask for clarification before producing artifacts. Do not improvise on patterns the project hasn't established.

---

## What this handoff is not

- **Not a substitute for the canonical files.** Always read the SDR, EW, and locked sections directly. This handoff summarizes; the canonical files specify.
- **Not authoritative on locked content.** If this handoff and a locked file disagree, the locked file wins. The maintainer (Jeremy) updates this handoff manually after each lock; lag between this file and the actual repo state is possible.
- **Not a place to store decisions.** Decisions live in the SDR (strategy), EW (process), spec sections (engineering), and approval notes (Approver-resolved defaults). This handoff is a navigation aid only.

---

## Quick start checklist for a fresh Claude session

When a new chat begins, run through this once:

- [ ] Confirm GitHub connector is available; if not, ask the human.
- [ ] Read `docs/current_claude_context_handoff.md` (this file) end to end.
- [ ] Read `docs/strategy_decision_record.md` (the SDR).
- [ ] Read `docs/engineering_workflow.md` (the EW).
- [ ] Read `docs/traceability_matrix.md` (current state).
- [ ] List `docs/engineering_spec/` and `docs/reviews/` to confirm what's locked and what handoff packets exist.
- [ ] Read the locked Engineering Spec sections relevant to the current task (1, 2, 3a as of this writing).
- [ ] Read any Section-level handoff packet relevant to the current task.
- [ ] Acknowledge what was read, what state the project is in, and what the current task appears to be. Then ask for the explicit task statement if it isn't already in the user's first message.

---

**End of handoff.**
