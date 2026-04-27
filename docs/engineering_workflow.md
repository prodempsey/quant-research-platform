# Quant Research Platform — Engineering Workflow

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v1.5 (locked)
**Date:** 2026-04-26
**Companion document:** Quant Research Platform — Strategy Decision Record (Phase 1: ETF Tactical Research)
**Purpose:** Define how the Engineering Specification is created, and how Phase 1 modules get built, reviewed, tested, and merged. This document covers process, not strategy.

**Changes in v1.5:** Added file location convention for Engineering Specification sections at `docs/engineering_spec/` (Section 3.1) — a spec section is not approved if it lives only in an LLM chat transcript. Added storage convention for handoff packets and QA reports at `docs/reviews/` (Section 2.2 and Section 9). Updated repository file inventory in Section 8 to include the `docs/` tree.

**Changes in v1.4:** Renamed document title from "ETF Tactical Platform — Engineering Workflow" to "Quant Research Platform — Engineering Workflow" to match the repository name (`quant-research-platform`). Added Phase 1 scope subtitle. Updated image tag prefix in Section 8 from `etf-platform` to `quant-research-platform`. Added Section 1 paragraph clarifying that the broader repo name is a vessel for future phases, not a license to expand current scope.

**Changes in v1.3:** Handoff packet ownership shifted to Approver (Section 2.2). Six-section spec outline now explicitly a default with split-if-needed rule (Section 3.1). Traceability matrix added as required artifact (Section 3.6). Integration test triggers extended to contract changes (Section 5). Research config tightened — Approver review required when results are reported or used for promotion (Section 7). Database schema migration discipline added (Section 7). Backtest reproducibility metadata expanded (Section 7). Secrets/credentials check added to QA checklist and Module DoD (Sections 9 and 10). "Review the artifact, not the summary" principle made explicit (Section 9).

**Changes in v1.2:** Added Section 3 (Engineering Specification Creation Workflow). Section 2 expanded into Roles, Handoffs, and Approval Matrix with explicit LLM handoff packet and approval categories. Sections 4–13 renumbered. Testing section sharpened to require tests verify financial meaning, not just mechanics. Configuration section adds change classification by impact category. QA checklist extended to cover spec section review. Stop-and-escalate triggers extended to spec drafting.

**Changes in v1.1:** Updated for Linux deployment on Hostinger VPS with Docker + `docker-compose` containerization from day one. Added deployment and container workflow section. Path-handling expectations clarified throughout.

---

## 1. Purpose and Scope

This document is the operating manual for *how* the project gets built. The Strategy Decision Record (SDR) defines *what* gets built and *why*. The Engineering Specification will define *which modules exist* and *what each module does*. This document defines *how the Engineering Specification is created*, and *how any given module moves from idea to merged code*.

The repository is named `quant-research-platform` to reflect long-term scope (multiple phases, possibly multiple asset classes), but Phase 1 work is strictly the ETF tactical research platform defined in the SDR. The broader name is a vessel for future phases, not a license to expand current scope.

If a workflow question arises that is not covered here, the default response is: pause, document the question, decide deliberately, and update this document.

---

## 2. Roles, Handoffs, and Approval Matrix

### 2.1 Roles

**Builder — Claude Code.** Primary implementer. Drafts Engineering Specification sections, writes module code, unit tests, and inline documentation. Operates from the Engineering Specification and the SDR. Does not promote models, change strategy commitments, or merge code.

**QA Reviewer — Codex (or ChatGPT).** Independent reviewer. Reads Engineering Specification sections (per Section 3) and completed module code, and validates each against the SDR and this workflow. Flags issues. Does not implement fixes directly — fixes return to the Builder with the QA report attached.

**Approver — Jeremy.** Final decision authority. Approves Engineering Specification sections, approves merges, owns all SDR decisions, resolves disagreements between Builder and Reviewer. Has the final word on whether a module or spec section meets its Definition of Done.

**Strategy interpretation rule.** LLMs may implement SDR decisions but may not reinterpret, optimize, relax, replace, or "improve" strategy decisions without explicit Approver authorization. If implementation reveals that an SDR decision is impractical or mistaken, the response is to escalate, not to silently adjust.

### 2.2 LLM Handoff Packet

Every spec-drafting task given to the Builder, every code implementation task given to the Builder, and every QA review task given to the Reviewer must operate from a standard handoff packet:

- Current SDR version
- Current Engineering Workflow version
- Relevant Engineering Specification section (or section being drafted)
- Specific SDR decision numbers being implemented or reviewed
- Module name and scope boundaries
- Out-of-scope items
- Required tests for this module type
- Known open questions and flagged assumptions
- Prior QA comments, if this is a fix iteration

**Packet ownership.** The Approver provides or approves the handoff packet before work begins. The Builder may draft the packet for efficiency, but the Approver confirms its contents — particularly the SDR decision references, scope boundaries, and flagged open questions — before the task is treated as authorized. The Reviewer receives the approved packet alongside the artifact under review.

This separation matters because the handoff packet defines what counts as in-scope and what counts as a defect. If the same agent that frames the work also delivers it, control is lost.

**Packet storage.** Approved handoff packets are saved under `docs/reviews/` alongside the corresponding QA report (per Section 9) when they cover Engineering Specification sections, module approvals, SDR changes, model promotions, broker / order-intent behavior changes, database migrations, or strategy-affecting configuration changes. Routine implementation tasks for low-risk infrastructure modules do not require a saved packet, but any task that touches the Approval Matrix items in Section 2.3 does.

### 2.3 Approval Matrix

The Approver's review and explicit approval is required before any of the following take effect:

- SDR revisions of any kind
- Engineering Specification section finalization (per Section 3.4)
- Changes to financial calculations (returns, excess returns, alphas, risk-adjusted metrics)
- Changes to feature, target, or label definitions
- Changes to risk rules (stops, position limits, drawdown thresholds, ATR multiples)
- Changes to ETF universe membership or eligibility rules
- Changes to benchmark or sleeve assignments
- Changes to transaction cost assumptions
- Model promotion between any two gates (per SDR Decision 12)
- Any broker / order-intent behavior change
- Any code path that could enable live trading
- Strategy-affecting YAML config changes (as classified in Section 7)
- Research config changes when results are reported or used for promotion (per Section 7)
- Deployment exposure changes (e.g., exposing the Dash UI beyond SSH tunnel)
- Database schema changes (per Section 7)
- Project scope changes beyond what the SDR commits to

No automated agent — Builder, Reviewer, or any future agentic loop — has authority over the items above. These are reserved for the Approver.

---

## 3. Engineering Specification Creation Workflow

The Engineering Specification is itself created in controlled sections, not in a single LLM prompt. This section governs how the spec is drafted, reviewed, and finalized.

### 3.1 Section-by-section creation

The Engineering Specification is created in approximately six sequential sections:

1. **Architecture overview and module structure** — folder layout, module boundaries, dependency graph, technology choices, environment setup
2. **Data layer** — provider abstraction interface, EODHD provider implementation, Postgres schema (DDL), data quality framework, ingestion orchestration, EODHD 30-day deletion mechanism
3. **Feature, target, and model layer** — feature calculation specs, target generation, baseline model implementations, calibration pipeline, MLflow integration, model registry schema
4. **Backtest, attribution, and validation layer** — walk-forward harness with purge/embargo, transaction cost application, regime classification, attribution storage, performance metrics, kill-switch monitoring
5. **Portfolio, paper trading, and order intent layer** — portfolio rules engine, BUY/HOLD/TRIM/SELL/REPLACE/WATCH logic, paper portfolio state management, broker-neutral order intent schema, account-type rule enforcement
6. **UI layer** — Dash app structure, the seven screens from SDR Decision 17, read-only enforcement, data flow from Postgres/MLflow to UI

Each section is drafted, reviewed by the QA Reviewer, and approved by the Approver before the next section is started. **No single prompt may request the full Engineering Specification.** Coding does not begin on any module until the spec section covering that module is approved.

**Section size control.** The six-section outline is the default, not a hard constraint. If any section becomes too large for focused review, the Builder proposes a split into smaller subsections before QA review begins. Sections 3 and 4 in particular bundle internally distinct concerns (feature engineering, target generation, and modeling each carry different risks; backtesting, attribution, and validation similarly), and may need to be split during drafting. Combining sections, expanding a section's scope materially, or reducing the number of sections requires Approver approval.

**File location and naming.** Engineering Specification sections are committed as markdown files under `docs/engineering_spec/`. A spec section is not considered approved if it exists only in an LLM chat transcript or scratch document — the committed markdown file in `docs/engineering_spec/` is the source of truth. Recommended file names:

- `docs/engineering_spec/01_architecture_overview.md`
- `docs/engineering_spec/02_data_layer.md`
- `docs/engineering_spec/03_features_targets_models.md`
- `docs/engineering_spec/04_backtest_attribution_validation.md`
- `docs/engineering_spec/05_portfolio_paper_trading_order_intent.md`
- `docs/engineering_spec/06_ui_layer.md`

If a section is split per the section-size-control rule, use suffix naming such as `03a_feature_engineering.md`, `03b_target_generation.md`, `03c_model_layer.md`. The numeric prefix preserves the original section order; suffixes preserve the split relationship.

### 3.2 Section template

Each Engineering Specification section must include the following fields, in this order:

- **Purpose** — what this part of the system is responsible for
- **Relevant SDR decisions** — explicit decision numbers this section implements
- **In scope** — modules, behaviors, and data covered by this section
- **Out of scope** — what is explicitly deferred to other sections or later phases
- **Inputs and outputs** — for each module, what it consumes and what it produces
- **Data contracts** — schemas, types, units, naming conventions
- **Config dependencies** — which YAML files this section reads or requires
- **Required tests** — minimum test coverage per module, including bias and look-ahead checks
- **Edge cases and failure behavior** — what happens when inputs are bad, missing, or unexpected
- **Open questions** — items not resolved by the SDR or by this section
- **Explicit assumptions** — anything the section assumes that is not in the SDR, classified per Section 3.3

A section that omits any of these fields is incomplete and is returned to the Builder.

### 3.3 No assumption drift

If the Engineering Specification requires a detail not explicitly decided in the SDR, the LLM drafting the section must classify and mark it as one of:

- **Derived from SDR** — a logical consequence of an existing SDR decision (cite which one)
- **Implementation default** — a reasonable engineering choice that does not change strategy behavior
- **Open question for Approver** — needs Jeremy's decision before the section is finalized
- **Proposed default requiring approval** — a strategy-affecting choice the LLM proposes, requiring explicit Jeremy accept/reject

Silent decisions are forbidden. If a spec section contains a strategy-affecting choice that does not trace to the SDR or appear in one of the categories above, the section is returned to the Builder. This rule applies during spec drafting and during implementation — at every stage, undeclared assumptions are defects.

### 3.4 Spec section Definition of Done

A spec section is Done when:

1. Every requirement maps to one or more SDR decisions, or to a flagged assumption per Section 3.3.
2. All template fields from Section 3.2 are populated.
3. Inputs, outputs, and data contracts are specified for each module described.
4. Required tests are defined for each module described.
5. Config impact is identified.
6. Open questions are either resolved by the Approver or explicitly deferred with a tracking note.
7. The traceability matrix (Section 3.6) is updated to cover the SDR decisions implemented in this section.
8. The section is committed to `docs/engineering_spec/` per Section 3.1.
9. QA Reviewer has reviewed the section against the spec review checklist (Section 9) and produced a report.
10. The Approver has reviewed and approved the section.

### 3.5 Stop conditions for spec drafting

The Builder pauses spec drafting and escalates to the Approver if:

- An SDR decision needed by this section is missing.
- An SDR decision conflicts with what the section would need to specify.
- A module boundary is unclear and cannot be resolved by reading the SDR.
- Testability of a requirement is unclear.
- Financial logic is implied by the SDR but not actually decided.
- A new research feature appears to be required that the SDR does not cover.
- Broker or live-trading behavior is ambiguous in the SDR.

Escalation is preferred over guessing. Spec sections are inexpensive to fix in draft and expensive to fix after coding begins.

### 3.6 Traceability matrix

Each finalized Engineering Specification section updates a project traceability matrix maintained at `docs/traceability_matrix.md`. The matrix maps each SDR decision to its downstream artifacts:

**SDR Decision → Spec Section(s) → Module(s) → Config File(s) → Required Tests → Approval Gate**

The matrix is the single place to verify that every SDR decision has corresponding implementation, configuration, test coverage, and approval discipline. It is a lightweight markdown table, not a separate process — maintaining it is part of finalizing each spec section.

QA review of a spec section confirms the matrix has been updated for that section. The Approver's section approval includes confirmation that the matrix entry is accurate. A spec section cannot be finalized while its traceability matrix entry is missing or stale.

When the SDR is revised, the matrix is the entry point for the impact assessment described in Section 6.

---

## 4. Module Implementation Workflow

The standard cycle for each module, after the relevant spec section is approved:

**Step 1 — Spec confirmation.** Builder re-reads the relevant Engineering Specification section and the SDR decisions it implements. If anything is ambiguous, the Builder pauses and asks the Approver. Coding does not start on ambiguous specs.

**Step 2 — Test scaffolding first.** Builder writes the unit test file before or alongside the implementation. Tests reflect what the module is *supposed to do*, not what the implementation happens to produce. Tests reference SDR decisions in their names or docstrings where applicable.

**Step 3 — Implementation.** Builder writes the module to make tests pass. Inline comments cite the SDR decision number that motivates non-obvious choices (e.g., `# SDR Decision 7: 126-day embargo around train/test boundaries`).

**Step 4 — Self-review and lint.** Builder runs tests, runs the project linter/formatter, checks for hardcoded values that should be in YAML config, confirms no provider-specific code has leaked outside the data provider layer, and confirms no hardcoded paths or host-specific assumptions have leaked into module code. If the change touches `requirements.txt`, the `Dockerfile`, or `docker-compose.yml`, Builder verifies the application image rebuilds and the stack starts cleanly. Builder also confirms no secrets, credentials, or sensitive values appear in the diff.

**Step 5 — QA review.** QA Reviewer receives the module code, the test file, the handoff packet, and a brief change summary. The Reviewer checks against the QA checklist in Section 9 and produces a QA report with status: pass / pass-with-comments / fail.

**Step 6 — Fixes if needed.** If QA returns fail or pass-with-comments, the Builder addresses the issues. Steps 5–6 repeat until QA passes.

**Step 7 — Approval and merge.** Approver reviews the QA report and the change summary, approves the merge, and the module enters the codebase. Commit message includes the module name and SDR decision references.

**QA scope by module type.** For modules touching financial calculations (returns, targets, costs, attribution, portfolio rules, order intents, model outputs), QA review is mandatory and thorough. For modules that are pure infrastructure (logging, config loading, database connection helpers), a lighter QA pass is acceptable, but the Approver still merges. For modules touching the Dockerfile, `docker-compose.yml`, or other deployment configuration, QA additionally confirms portability is preserved.

---

## 5. Testing Requirements

**Unit tests are required for every module.** Modules without tests do not merge.

**Tests must verify financial meaning, not just mechanics.** A test that confirms a function returns a DataFrame is not enough. A backtest test must verify that dates are aligned correctly, that the embargo is enforced, that transaction costs are applied to the correct sides of trades, and that no future information has leaked into past decisions. A feature test must verify the feature's value matches a hand-computed result on a known input. A target test must verify that labels use only forward data and align with the as-of date. The intent of the test should be clear from the test's name and assertions.

**Minimum coverage by module type:**

- *Data ingestion modules:* tests for happy path, missing data, duplicate data, malformed API responses, date-range edge cases, and the 30-day deletion mechanism for EODHD-sourced data on subscription cancellation.
- *Feature calculation modules:* tests for at least one known-input / known-output case per feature, plus look-ahead bias tests confirming the feature on day T uses only data up to day T-1.
- *Target generation modules:* tests confirming labels use only forward data and are correctly aligned with the as-of date.
- *Model modules:* tests for fit/predict shape consistency, calibration output range (probabilities in [0,1]), and reproducibility (same input + same seed = same output).
- *Backtest modules:* tests for walk-forward window correctness, purge/embargo enforcement, transaction cost application, eligibility filtering, and survivorship handling.
- *Portfolio rule modules:* tests for each BUY/HOLD/TRIM/SELL/REPLACE/WATCH transition, including edge cases at threshold boundaries.
- *Order intent modules:* tests confirming no live broker calls are possible, paper-only mode is enforced, and account-type restrictions are applied.
- *UI modules:* smoke tests confirming pages load, read-only enforcement is active, and no UI action can bypass approval gates.

**Integration tests are required for cross-module flows.** End-to-end ingest → feature → target → model → backtest → attribution should run on a small fixture dataset as a regression test. The integration test runs:

- At every model-module merge
- At every backtest-module merge
- Whenever a module changes a shared schema, data contract, provider interface, portfolio state contract, or order-intent contract
- Whenever a database migration is merged

**Test data discipline.** Tests must not depend on live API calls. All external data is fixtured (small CSVs or pickled responses checked into the repo under `tests/fixtures/`).

**Test execution environment.** Unit tests must pass both locally and inside the application container via `docker compose exec app pytest`. Integration tests run inside the container against the containerized Postgres instance, using a separate test database so they never touch production data. Tests that pass locally but fail in the container — or vice versa — are treated as a defect, not a quirk.

---

## 6. Code-to-Decision Traceability

Every module that implements an SDR decision should reference that decision in code, in addition to appearing in the project traceability matrix (Section 3.6).

**Module docstring header.** Each module file begins with a docstring naming the SDR decisions it implements. Example:

```python
"""Walk-forward backtest harness.

Implements SDR Decision 7 (validation method, 126-day embargo)
and SDR Decision 8 (transaction cost application).
"""
```

**Inline comments at non-obvious choices.** Where the code makes a choice that exists only because of an SDR decision, the comment cites the decision number. Example:

```python
# 126-day embargo per SDR Decision 7
embargo_days = 126
```

This is not bureaucracy. It is how future-you, or a coding agent picking up the project months later, understands why the code is shaped the way it is, and how SDR revisions translate into code changes.

**SDR revision protocol.** When the SDR is revised, the revision document must include a list of code modules potentially affected, identified by consulting the traceability matrix. Modules referencing the revised decision are reviewed for whether the change requires implementation updates. Revisions to the SDR are not silent — they trigger a code review pass and a traceability matrix update.

---

## 7. Configuration Management

**Configuration as data, in YAML, in git.** Per SDR Decision 10, all tunable parameters live in YAML files under `config/` in version control. Hardcoded thresholds in code are treated as bugs.

**Categories of config:**

- `config/universe.yaml` — ETF universe, eligibility rules, sleeve mappings, benchmark assignments
- `config/features.yaml` — feature parameters (windows, lookbacks, smoothing constants)
- `config/model.yaml` — model hyperparameters, calibration settings, target horizons
- `config/portfolio.yaml` — portfolio rule thresholds, position limits, ATR multiples, rebalance cadence
- `config/costs.yaml` — transaction cost buckets and basis points per SDR Decision 8
- `config/regime.yaml` — regime classification thresholds and fallback rules

**Config change classification.** Not all config changes are equal. Each change falls into one of five categories with different review requirements:

- *Operational* — logging levels, output verbosity, container-internal paths. Standard QA review only.
- *Research* — backtest windows, validation parameters, experiment settings, or analysis settings that affect research outputs but not deployed strategy behavior. Standard QA review is sufficient for exploratory runs. **If the result is used for reported performance, model comparison, strategy selection, or model promotion, Approver review is required and the config commit hash must be recorded with the result.**
- *Strategy-affecting* — thresholds, weights, ATR multiples, transaction costs, eligibility rules, anything that changes what the model recommends or how the portfolio behaves. **Approver review required.**
- *Production runtime* — anything affecting deployed behavior of the running system. **Approver review required.**
- *Credential / environment* — anything in `.env` or affecting authentication. **Approver review required, never auto-modified by any agent.**

The category is stated in the commit message for any config change. When in doubt, treat as Strategy-affecting and escalate.

**Commit conventions for config changes.** Config changes get descriptive commit messages stating what changed, why, the change category, and which SDR decision (if any) the change implements or revises.

Example: `config(portfolio): [strategy-affecting] raise replacement probability gap from 5pp to 7pp per SDR rev re Decision 10`

**Backtest reproducibility.** Every official backtest run records the following alongside the model run in MLflow:

- Code commit hash
- Config commit hash
- Data snapshot/version identifier
- Data provider/source (e.g., EODHD All World, snapshot date)
- Universe version (which Core Test Universe / Candidate Universe was active)
- Adjusted-price convention used
- MLflow run ID

A backtest result is not considered reproducible unless all of the above can be retrieved. Reported results, model comparison results, and any run used for a promotion decision must include the full reproducibility metadata.

**Database schema migrations.** Database schema changes require a migration script committed under `migrations/`, a documented rollback plan, fixture and test updates that exercise the new schema, and QA review. Manual production database changes are not permitted. If a schema change is discovered to be necessary mid-implementation, the Builder pauses and escalates rather than applying the change directly. Schema migrations are subject to Approver review per the Approval Matrix.

**Credential handling.** Credentials live in a `.env` file in the project root on the host VPS. The `.env` file is gitignored and is never copied into a container image. `docker-compose` reads the host `.env` file and injects environment variables into the appropriate containers via `env_file:` or `environment:` directives in `docker-compose.yml`. Modules access credentials via standard environment variable lookup or via a thin config helper — no module reads the `.env` file directly.

A `.env.example` file is committed to the repository documenting all required variables with placeholder values, so initial setup on a new host follows a reproducible pattern. Rotating credentials is a matter of editing the host `.env` file and running `docker compose up -d` to restart affected containers — no image rebuild required.

**YAML config in containers.** YAML config files in `config/` are mounted read-only into the application container at a known path (e.g., `/app/config`). Config changes on the host take effect on container restart, without rebuilding the image. This matches the "config as data" philosophy: the container code is stable; the configuration it reads is mutable.

**Path handling.** All file path manipulation uses `pathlib.Path`. No hardcoded forward or backslash paths in code. No drive letters, no host-specific absolute paths embedded in modules. Path values that need to be configurable reference container-local paths (e.g., `/app/data`), and host-to-container path mappings live in `docker-compose.yml`.

---

## 8. Deployment and Container Workflow

The platform runs as a multi-container stack orchestrated by `docker-compose` on a Linux host (Hostinger VPS for Phase 1). Container portability is a Phase 1 requirement: the entire system must be moveable between hosts by copying the project directory and the named Docker volumes.

**Phase 1 container layout:**

- *Postgres container* — system of record per SDR Decision 11, using the official `postgres` image with data persisted in a named volume (`pgdata`).
- *MLflow tracking container* — for experiment tracking per SDR Decision 11, with metadata in Postgres (separate database) and artifacts in a named volume (`mlflow-artifacts`).
- *Application container* — built from the project `Dockerfile`. Hosts the Dash operator UI as the long-running main process and runs scheduled jobs (data ingestion, model runs, backtests) via cron-in-container for Phase 1.
- *(Optional) nginx reverse proxy container* — single entry point for the Dash UI. Useful if the UI is ever exposed beyond SSH tunnel access. Optional for Phase 1.

**Repository file layout.** These directories and files are part of the codebase and are versioned, reviewed, and tested like any other module:

- `Dockerfile` — defines the application container image
- `docker-compose.yml` — defines all services, networks, volumes, inter-service dependencies
- `.env.example` — documents required environment variables (placeholders only)
- `.dockerignore` — excludes secrets, virtualenvs, fixtures, and host-only artifacts from the build context
- `config/` — YAML configuration files (see Section 7)
- `migrations/` — database migration scripts
- `scripts/backup.sh` — host-side backup script that runs `pg_dump` against the Postgres container and rotates dumps
- `scripts/restore.sh` — corresponding restore script
- `docs/engineering_spec/` — Engineering Specification sections (see Section 3.1)
- `docs/reviews/` — approved handoff packets and QA reports (see Section 2.2 and Section 9)
- `docs/traceability_matrix.md` — SDR-to-implementation traceability (see Section 3.6)

Changes to any of these files go through the same Builder → QA → Approver workflow as application code.

**When the application image must be rebuilt:**

- New Python dependencies added (changes to `requirements.txt` or equivalent)
- Changes to system-level dependencies in the `Dockerfile`
- Application code changes deployed via the baked image

**When the application image does not need to be rebuilt:**

- YAML config changes (mounted in, take effect on container restart)
- `.env` credential changes (read by `docker-compose`, take effect on container restart)
- Documentation changes under `docs/`
- Pure data updates

**Image tagging convention.** Application container images are tagged with the git commit hash. At meaningful milestones, an additional semantic tag is applied (e.g., `quant-research-platform:0.1.0-data-layer`). The `latest` tag is not used in production runs — every running container references a specific image tag, so rollback is a matter of changing `docker-compose.yml` to a prior tag and restarting.

**Resource limits.** Each service in `docker-compose.yml` declares explicit memory and CPU limits. This prevents a runaway process (memory leak, oversized backtest) from starving the host. With limits in place, Docker will OOM-kill the offending container and restart it via the `restart: unless-stopped` policy, rather than taking down the entire VPS.

**Health checks.** Each service defines a Docker health check. The application container's health check confirms the Dash app is responding on its port. The Postgres container's health check confirms the database accepts connections. Container state is observable via `docker ps`, and dependent services wait for prerequisites before starting.

**Backups.** A scheduled job on the host (cron) runs `scripts/backup.sh`, which executes `pg_dump` against the Postgres container, writes the dump to a host directory, and rotates older dumps. The host directory is captured by Hostinger's VPS-level backup. MLflow artifacts are backed up by archiving the MLflow named volume on a less frequent schedule.

**Portability test.** Before any milestone tag, the deployment is tested for portability: spin up the stack on a fresh test environment from the repo plus a backup, confirm the system runs and reports the same state. This validates that no hidden host state has accumulated.

**Out of scope for Phase 1:**

- Kubernetes orchestration
- Multi-host deployment
- Public TLS exposure of the Dash UI (SSH tunnel access is sufficient)
- Container registry hosting
- CI/CD automation (manual `docker compose up -d` after merge is sufficient)

---

## 9. QA Review Checklist

The QA Reviewer validates each Engineering Specification section and each module against the relevant items below.

**Reviewing the artifact, not the summary.** The Reviewer reviews the actual specification section, code diff, tests, and config changes — not only the Builder's summary. A polished summary that omits issues does not satisfy QA. If the artifact and summary disagree, the artifact wins.

**For Engineering Specification sections:**

- Are all template fields from Section 3.2 populated?
- Is the section committed under `docs/engineering_spec/` per Section 3.1?
- Does every requirement trace to an SDR decision or a flagged assumption per Section 3.3?
- Are inputs, outputs, and data contracts specified for each module?
- Are required tests defined for each module?
- Is config impact identified?
- Are open questions either answered or explicitly deferred?
- Are any strategy-affecting choices flagged correctly, not silently embedded?
- Is anything in the section out of scope per the SDR (a sign of scope creep)?
- Has the traceability matrix been updated for this section?

**For module code, specification compliance:**

- Does the code implement what the Engineering Specification asked for?
- Are inputs and outputs as specified?
- Are SDR decisions properly referenced in docstrings and inline comments?

**Test coverage:**

- Are the required tests for this module type present?
- Do tests verify financial meaning (Section 5), not just mechanics?
- Are edge cases tested (boundaries, empty inputs, malformed data)?
- Do tests pass both locally and in the application container?
- For changes to shared schemas or contracts: do integration tests run?

**Bias and correctness:**

- Any look-ahead bias in feature or target code?
- Any provider-specific logic outside the data provider layer?
- Any silent assumptions about data shape, units, or trading calendar?
- Any hardcoded values that should be in YAML config?
- For financial calculations: is the math verifiable against an externally computable answer?

**Safety:**

- For order-intent and portfolio modules: can this module cause a live broker order? It must not.
- For model modules: does this module respect the two-gate promotion process from SDR Decision 12?
- For UI modules: can any UI action change SDR-governed state without explicit Approver action?

**Container and deployment hygiene:**

- Are paths handled via `pathlib`, with no host-specific or hardcoded paths?
- Are credentials accessed via environment variables, not direct `.env` reads?
- If `requirements.txt`, `Dockerfile`, or `docker-compose.yml` changed, does the image rebuild and the stack start cleanly?
- Are any new YAML config files mounted into the container correctly?
- Does the diff contain any secrets, API keys, tokens, passwords, account numbers, broker credentials, or sensitive `.env` values? It must not.
- If the change includes a database migration: is there a rollback plan, fixture update, and successful migration test?
- For deployment-affecting changes: is portability preserved?

**Documentation:**

- Does the module have a docstring header citing relevant SDR decisions?
- Are non-obvious choices commented with decision references?

QA produces a brief written report: status (pass / pass-with-comments / fail), specific issues found, and recommended actions.

**Report storage.** QA reports are saved under `docs/reviews/` alongside the corresponding handoff packet (per Section 2.2) when they cover Engineering Specification sections, module approvals, SDR changes, model promotions, broker / order-intent behavior changes, database migrations, or strategy-affecting configuration changes. Routine implementation tasks for low-risk infrastructure modules do not require a saved report. Recommended naming convention: `docs/reviews/YYYY-MM-DD_<artifact-type>_<short-description>.md` (e.g., `docs/reviews/2026-05-01_spec_02_data_layer.md`, `docs/reviews/2026-05-15_module_eodhd_provider.md`).

---

## 10. Definition of Done

### 10.1 Spec section Definition of Done

See Section 3.4. A spec section is Done when its template is complete, all requirements trace to SDR or to flagged assumptions, the section is committed under `docs/engineering_spec/`, the traceability matrix is updated, the QA Reviewer has approved it, and the Approver has approved it.

### 10.2 Module Definition of Done

A module is Done when all of the following are true:

1. Code matches the approved Engineering Specification section.
2. All required unit tests pass, both locally and in the application container.
3. Linter and formatter checks pass.
4. Integration tests (where applicable) pass inside the container.
5. QA review status is pass or pass-with-comments-resolved.
6. Module docstring cites relevant SDR decisions.
7. No hardcoded values that should be in YAML config.
8. No hardcoded paths; all file paths use `pathlib`.
9. No provider-specific code outside the provider layer (for non-provider modules).
10. No secrets, credentials, tokens, account numbers, or sensitive environment values appear in code, config, fixtures, logs, notebooks, or documentation.
11. Approver has reviewed and approved the merge.

**For modules touching financial calculations, additionally:**

12. At least one known-input / known-output test case verifies the calculation against an externally computable answer.
13. QA review explicitly confirms no look-ahead bias and no provider leakage.

**For modules touching the broker / order-intent layer, additionally:**

14. QA review explicitly confirms paper-only mode is enforced and no live broker call paths exist.

**For modules touching deployment configuration, additionally:**

15. The application image rebuilds successfully from a clean cache.
16. The stack starts cleanly with `docker compose up -d` and all health checks pass.
17. Portability is preserved — no new host-specific dependencies are introduced.
18. `.env.example` is updated if new environment variables were added.

**For modules including a database migration, additionally:**

19. Migration script applies cleanly to a fresh database.
20. Rollback script reverses the migration cleanly.
21. Test fixtures are updated to reflect the new schema.
22. Integration tests pass against the migrated schema.

---

## 11. Branching and Versioning

**Branch naming.** Feature branches named `module/<module-name>` or `fix/<short-description>`. Spec drafting branches named `spec/<section-name>`. No work directly on `main`.

**Commit granularity.** Commits are small and topical. A single commit doing five unrelated things is rejected at QA review.

**Pull request equivalence.** Although this is a personal project, the merge step is treated as a pull request: Builder describes changes, QA Reviewer comments, Approver merges. The "PR" can be a local diff review — formality is not the point, the review gate is the point.

**Tagging.** Tag releases at meaningful milestones (e.g., `v0.1-data-layer-complete`, `v0.2-feature-engineering-complete`). Tags allow easy rollback. Application container images receive a corresponding image tag at each milestone.

**Rollback policy.** If a merged module is later found to have a serious defect, the response is to (a) revert to the last good tag and corresponding image tag, (b) document the defect and how it was missed, (c) update this document or the QA checklist if the gap was procedural, and (d) re-implement under the updated process.

---

## 12. When to Stop and Escalate

### 12.1 During spec drafting

See Section 3.5 for the full list. In summary: stop if SDR decisions are missing, conflicting, or ambiguous; if module boundaries or testability are unclear; if financial logic is implied but not decided; or if a new research feature is being proposed that isn't in the SDR.

### 12.2 During implementation

**Builder pauses and escalates to Approver if:**

- The Engineering Specification appears to conflict with the SDR.
- A test cannot be written for what the spec asks (this usually means the spec is ambiguous).
- An SDR decision turns out to be impractical or wrong in implementation.
- A data quality issue is discovered that affects downstream modules.
- The module's scope appears to be growing beyond what the spec described.
- Tests pass locally but fail inside the container, or vice versa, in ways not explained by trivial config differences.
- A schema change appears necessary that wasn't anticipated in the spec.

**QA Reviewer pauses and escalates to Approver if:**

- The same issue keeps recurring across modules (suggests a systemic problem).
- A safety-critical issue is found (live broker risk, look-ahead bias, promotion bypass, secret leak).
- A module appears to satisfy its tests but not the SDR's intent.
- The Builder and Reviewer disagree on whether something is a defect.
- Container behavior is inconsistent across environments in ways that suggest a deeper deployment defect.
- An undeclared assumption surfaces in code that wasn't flagged in the spec section.
- The artifact and the Builder's summary disagree.

**Approver pauses everything if:**

- A discovery in implementation invalidates an SDR decision.
- Backtest results begin looking suspicious in ways the bias controls don't explain.
- The pace of revisions to the SDR or this document suggests the foundations need revisiting.

The cost of escalation is small. The cost of pushing through ambiguity is large.

---

## 13. Document Maintenance

This document is versioned alongside the SDR. Changes require:

1. Identifying what process gap or problem prompted the change.
2. Updating the document with a version increment and date.
3. A brief note in the commit message about what changed and why.
4. A brief change-log line at the top of the document.

**Re-read trigger.** Re-read this document at the start of each new module type, and at the start of each Engineering Specification section. Process drift is harder to detect than code drift, and a periodic re-read keeps practice aligned with intent.

**Annual review.** At minimum, review this document once per year against actual practice. If practice has drifted from the document, decide whether to correct practice or update the document — either is acceptable, but the gap is not.

---

**End of document.**
