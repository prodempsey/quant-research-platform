# Engineering Specification — Section 1: Architecture Overview and Module Structure

**Phase 1 scope:** ETF tactical research platform.
**Section status:** v1.0 LOCKED / APPROVED
**Approval date:** 2026-04-26
**Final Approval:** Jeremy
**Author:** Builder (Claude Code)
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- `docs/traceability_matrix.md`

---

## Changelog

**v1.0 LOCKED (2026-04-26).** Approved by the Approver (Jeremy). v0.2 promoted to v1.0 with no substantive content changes; only the section-status metadata is flipped from draft to locked, and this v1.0 entry is added to the changelog. The Approver-resolved defaults under *Explicit assumptions* are confirmed and locked at this approval. Approval record and process trail are stored under `docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`.

**v0.2 (2026-04-26).** QA-driven revision of v0.1, incorporating the six edits flagged by the QA review and the Approver's resolution of v0.1's open questions. Six substantive changes:

1. The single dependency graph in *Data contracts* is split into two: a strict **Python import dependency graph** (every business area imports `common/` only) and a separate **data-at-rest dependency graph** (Postgres- and MLflow-mediated coupling).
2. The provider/ingestion responsibility split is corrected: `providers/` returns provider-tagged DTOs; `ingestion/` is the only area that persists provider-sourced records to Postgres. v0.1 had `providers/` writing rows, which conflicted with `ingestion/` owning persistence.
3. A new architectural invariant — **Time-aware research auditability** (Decision 16) — is added under *Architectural invariants*, requiring later sections to design for point-in-time reconstruction. Section 1 does not define schema or implementation; Sections 2, 3, and 4 do.
4. The UI read-only invariant is extended beyond the import-boundary to include a database-access constraint: `ui/` must not execute INSERT, UPDATE, DELETE, DDL, or any SDR-governed state writes through `common/` DB helpers. Section 6 defines the enforcement mechanism.
5. The application container's responsibilities are clarified with an explicit Dash + cron startup contract: a healthy Dash process must not mask failed scheduled jobs.
6. The ten v0.1 open questions are resolved by Approver decision and recorded under *Approver-resolved defaults*; the "Proposed default requiring approval" classification in *Explicit assumptions* is closed out.

Minor wording fixes: the stack is described as "three-container Phase 1 with a reserved optional fourth (nginx)" rather than "four-container stack"; the no-live-broker invariant explicitly includes a dependency-manifest scan; an `.env.example` parity test is added to *Required tests*; "manual or scripted" disciplines are scoped with a conversion-to-automation expectation.

**v0.1 (2026-04-26).** Initial draft.

---

## Purpose

Section 1 establishes the structural foundation of the Phase 1 platform. It defines the top-level repository layout, the major architectural areas and how they are allowed to depend on one another, the Phase 1 deployment stack, the technology choices already implied by the SDR and EW, and the naming conventions and environment-setup expectations that subsequent sections build on.

This section is deliberately structural. It does not define database schemas, the provider abstraction interface, feature formulas, target generation logic, model training, walk-forward harness internals, portfolio rule transitions, paper-state management, or the contents of the Dash screens. Those belong to Sections 2–6 and are listed under *Out of scope*.

The intent is that, after Section 1 is approved, a reader can stand up an empty version of the repository — directory layout, container scaffolding, configuration filenames, the import-boundary discipline — without yet having any business logic. Sections 2–6 then fill that scaffolding in.

---

## Relevant SDR decisions

Section 1 directly implements:

- **SDR Decision 1** — Phase 1 scope and boundaries (ETF tactical research + internal paper portfolio; no live broker integration).
- **SDR Decision 2** — Data provider and provider-switching strategy (EODHD as Phase 1 provider; mandatory provider abstraction; no module outside the provider layer may call EODHD directly; 30-day deletion obligation on subscription cancellation).
- **SDR Decision 11** — MLOps architecture (Postgres as system of record; MLflow as lightweight tracking layer; MLflow metadata stored in Postgres; MLflow artifacts stored in a Docker named volume).
- **SDR Decision 16** — Phase 1 success criteria and bias controls — at the architectural reservation level only. Section 1 reserves the time-aware research auditability invariant; Sections 2, 3, and 4 implement the data contracts, alignment rules, purge/embargo logic, and tests that enforce it.
- **SDR Decision 17** — Operator UI architecture (Dash; seven Phase 1 screens; UI is read-only with respect to model promotion, broker execution, and live trading; deployed inside the application container).
- **SDR Decision 18** — Deployment and container architecture (Linux Hostinger VPS, Ubuntu 24.04 LTS, Docker, `docker compose`; multi-container stack; YAML config under `config/`; gitignored host `.env` for credentials; deployment files are versioned project artifacts).

Section 1 also accommodates the architectural footprint of the following decisions without implementing them in detail (each is implemented by a later section, as indicated):

- Decisions 3, 4 — universe layers, eligibility, survivorship — accommodated by reserving a Postgres-backed universe registry and a `config/universe.yaml`. Detail in Section 2.
- Decisions 5, 6, 7 — sleeves/benchmarks, target design, validation — accommodated by reserving feature/target/model packages and `config/features.yaml`, `config/model.yaml`. Detail in Section 3 and Section 4.
- Decision 8 — transaction costs — accommodated by reserving `config/costs.yaml` and a cost-application boundary inside the backtest area. Detail in Section 4.
- Decision 9 — regime taxonomy — accommodated by reserving a `regime/` package and `config/regime.yaml`. Detail in Sections 3 and 4.
- Decision 10 — portfolio rules and YAML config — accommodated by reserving `portfolio/`, `paper/`, and `order_intent/` packages and `config/portfolio.yaml`. Detail in Section 5.
- Decision 12 — model promotion gates and kill-switch — accommodated by reserving model-state fields in Postgres and a portfolio-side gate boundary. Detail in Sections 3 and 5.
- Decision 13 — LLM advisory use — non-architectural; governed by the EW.
- Decision 14 — Danelfin deferred — no architectural footprint in Phase 1.
- Decision 15 — broker-neutral order intents, paper-only — accommodated by reserving an `order_intent/` package with no live-broker code paths and a strict architectural boundary against broker SDKs and broker manifests. Detail in Section 5.

---

## In scope

Section 1 covers:

1. The top-level repository folder layout, including the Python package structure, `config/`, `migrations/`, `scripts/`, `tests/`, `docs/`, and the deployment files specified in EW Section 8.
2. The architectural module boundaries — provider layer, ingestion, features, targets, regime, models, backtest, attribution, portfolio, paper trading, order intent, UI, and shared/common utilities — at the level of which area is allowed to import from which, without specifying internal module details.
3. Two distinct dependency graphs: an allowed Python import graph (strict — every business area imports `common/` only) and an allowed data-at-rest dependency graph through Postgres and MLflow.
4. Architectural invariants the rest of the platform must respect, including the provider boundary, the no-live-broker rule, the UI read-only rule (both import-boundary and database-access), Postgres-as-system-of-record, path-handling discipline, secrets discipline, and the time-aware research auditability reservation for Decision 16.
5. The Phase 1 technology choices already implied by the SDR or EW: Python; Postgres; MLflow; Dash; Docker and `docker compose`; Ubuntu 24.04 LTS on a Linux Hostinger VPS; `pathlib` for all path manipulation; YAML configuration in git; the host-`.env` credential pattern from EW Section 7.
6. The Phase 1 deployment stack (three containers initially, with nginx reserved as an optional fourth) per SDR Decision 18, together with each container's responsibilities, the named volumes, and the application container's startup contract for running both Dash and scheduled jobs.
7. Environment setup expectations: which Python version the project targets, which categories of libraries are expected, how containers communicate, and how YAML config and the host `.env` flow into the application container.
8. Naming conventions for Python packages and modules, file naming, and the application image tag prefix (`quant-research-platform` per EW Section 8 v1.4).
9. How Section 1 hands off to Sections 2–6 — what Section 1 establishes versus what each later section will define.

---

## Out of scope

Section 1 deliberately defers the following:

- **Postgres schemas, table designs, DDL, migrations content, and adjusted-price conventions** — Section 2.
- **Provider abstraction interface details and EODHD-specific implementation** (method signatures, pagination, rate-limit handling, response normalization, and the exact shape of the provider-tagged DTOs returned to ingestion) — Section 2.
- **Data quality framework details** (exception report contents, severity rules, auto-resolution scope) — Section 2.
- **30-day EODHD deletion mechanism implementation** — Section 2.
- **Time-aware schema fields** (as-of/effective dates, eligibility windows, label alignment fields, snapshot identifiers) — Sections 2, 3, and 4. Section 1 reserves the architectural requirement; the schema is not designed here.
- **Feature calculation formulas, lookback windows, smoothing constants** — Section 3.
- **Target generation logic** (regression and classification labels, alignment, embargo at the label level) — Section 3.
- **Model training, calibration, and MLflow integration details** — Section 3.
- **Walk-forward harness internals, purge/embargo specifics, attribution storage schema, kill-switch monitoring rules, leakage tests** — Section 4.
- **Portfolio rule logic** (BUY/HOLD/TRIM/SELL/REPLACE/WATCH transitions, threshold semantics) — Section 5.
- **Paper portfolio state management details, broker-neutral order-intent schema, account-type rule enforcement** — Section 5.
- **Dash screen contents, UI component breakdown, and the database-side enforcement mechanism for the UI read-only constraint** — Section 6.
- **CI/CD automation, container registry hosting, public TLS, multi-host deployment** — explicitly out of scope for Phase 1 per SDR Decision 18 and EW Section 8.

Section 1 must leave each of these deferrable without holes that prevent the architecture from being understood. Where a deferral has architectural consequences (for example, the requirement to support a 30-day EODHD purge dictates that storage rows carry `provider_name` and `provider_symbol`, or the time-aware auditability requirement dictates that all relevant tables have to be designed for point-in-time reconstruction), Section 1 records the consequence as an invariant and points to the section that will fill in the detail.

---

## Inputs and outputs

At the architectural level — the system as a whole, not module-by-module:

### System inputs

1. **End-of-day historical and current adjusted ETF price data** sourced via the provider abstraction layer. Phase 1 binds this to EODHD All World per SDR Decision 2. No other source of ETF price data is permitted in Phase 1.
2. **Configuration** as YAML files under `config/`, version-controlled with the codebase, mounted read-only into the application container. The set of YAML files is enumerated under *Config dependencies* below. SDR Decision 10 and EW Section 7.
3. **Credentials and environment variables** from a gitignored `.env` file on the host VPS, injected into containers by `docker compose` per EW Section 7. The application code never reads `.env` directly. A committed `.env.example` documents required variables with placeholder values.
4. **Approver decisions** captured in handoff packets, QA reports, and approval annotations under `docs/reviews/`. These are inputs to the build process rather than to the running system, but Section 1 reserves the documentation directories that hold them.

### System outputs

1. **Postgres state** — the system of record per SDR Decision 11. Holds ETF universe, eligibility, prices, features, targets, model rankings, paper portfolio state, broker-neutral order-intent records, regime classifications, model registry entries, and audit-relevant tables. Schema content is defined in Section 2 and extended by Sections 3–5. The schemas must satisfy the time-aware research auditability invariant (see *Architectural invariants*).
2. **MLflow tracking state** — model runs, training windows, validation methods, feature sets, target types, hyperparameters, performance metrics, and artifact references per SDR Decision 11. MLflow metadata is stored in a separate database inside the same Postgres container; MLflow artifacts are stored in the `mlflow-artifacts` Docker named volume. Detail in Section 3.
3. **Dash operator UI** — seven read-only screens served from inside the application container per SDR Decision 17. Screen contents are defined in Section 6.
4. **Plain-English data-quality and model-quality reports** with pass/warning/fail statuses per SDR Decisions 11 and 16. Storage location and format are defined in Section 2 (data quality) and Section 4 (model quality).
5. **No live broker orders.** Any code path that could place a live broker order is forbidden in Phase 1 per SDR Decisions 1, 15, and 18 and the EW Approval Matrix (Section 2.3). Order-intent records are produced; order placement is not.

### Container-level shape of these inputs and outputs

The Phase 1 deployment stack from SDR Decision 18 is a **three-container stack** initially, with a fourth container (nginx) reserved as an optional addition. Each container's internals are defined in subsequent sections; Section 1 establishes only the container-level architecture.

- **Postgres container.** Official `postgres` image. Holds two logical databases: the application database (system of record) and the MLflow metadata database. Backed by the `pgdata` Docker named volume. Reachable on the internal Docker network only; not exposed to the host except for tooling access via SSH-tunneled connections during development. The application container and the MLflow container both connect to it.
- **MLflow tracking container.** Runs the MLflow tracking server. Stores experiment metadata in its dedicated Postgres database and artifacts in the `mlflow-artifacts` Docker named volume. Reachable on the internal Docker network by the application container. The MLflow web UI is reachable via SSH tunnel during development; it is not exposed beyond the internal network in Phase 1.
- **Application container.** Built from the project `Dockerfile`. Hosts the long-running Dash UI and runs scheduled research jobs (data ingestion, model runs, backtests, regime classification) via cron-in-container per EW Section 8. The application container reads YAML config from a read-only mount at `/app/config`, reads credentials via injected environment variables, writes to Postgres, writes to MLflow, and serves the Dash UI. It is the only container that imports project Python code.

  **App container startup contract.** The container's entrypoint must start the cron daemon and the Dash process deterministically, log both to container stdout/stderr, and surface failures of either through the container's Docker health check. A healthy Dash process must not mask failed scheduled jobs: scheduled-job failures must be visible through container logs and through the data-quality and model-quality status surfaces defined in Sections 2 and 4. Section 1 does not pick the specific entrypoint mechanism (a process supervisor such as `supervisord`, a shell entrypoint, or another approach is an implementation choice for Section 2 / the initial container scaffolding); Section 1 requires only that the contract above be met.
- **Optional nginx reverse proxy container.** Not part of the initial Phase 1 stack. Reserved by SDR Decision 18 and EW Section 8 for later addition if controlled UI exposure beyond SSH tunnel becomes desirable. Phase 1 access to the Dash UI is via SSH tunnel only (EW Section 8 confirms this is sufficient for Phase 1).

Volumes used by the stack: `pgdata` (Postgres data), `mlflow-artifacts` (MLflow artifacts). The `config/` directory and the host `.env` file are mounted from the host filesystem rather than living in named volumes — they are version-controlled artifacts (or, in `.env`'s case, gitignored host state), not Docker-managed runtime state.

---

## Data contracts

This section establishes contracts at the *architectural* level — boundaries between major areas of the codebase and the repository layout that enforces them. Module-internal data contracts (table schemas, column types, function signatures, DTO shapes) belong to Sections 2–6.

### Top-level repository folder layout

The repository is named `quant-research-platform`. Phase 1 work is strictly the ETF tactical research platform per SDR Decision 1; the broader repository name reflects future-phase scope and is not authority to widen Phase 1 scope.

The Phase 1 layout is:

```
quant-research-platform/
├── Dockerfile                    # application container image
├── docker-compose.yml            # services, volumes, networks, dependencies
├── .env.example                  # documents required env vars (placeholders only)
├── .dockerignore
├── .gitignore
├── README.md
├── pyproject.toml                # project metadata + dependency manifest
├── requirements.txt              # pinned runtime dependencies, generated from pyproject.toml
├── src/
│   └── quant_research_platform/  # the importable Python package
│       ├── __init__.py
│       ├── common/               # shared utilities: config loader, db helpers, mlflow helpers, logging, paths
│       ├── providers/            # data provider abstraction + EODHD implementation (Section 2)
│       ├── ingestion/            # provider-DTO → Postgres persistence (Section 2)
│       ├── features/             # feature calculation (Section 3)
│       ├── targets/              # target generation (Section 3)
│       ├── regime/               # regime classification (Sections 3 and 4)
│       ├── models/               # baseline models, calibration, model registry interface (Section 3)
│       ├── backtest/             # walk-forward harness, cost application (Section 4)
│       ├── attribution/          # backtest attribution storage and reporting (Section 4)
│       ├── portfolio/            # portfolio rules engine (Section 5)
│       ├── paper/                # paper portfolio state management (Section 5)
│       ├── order_intent/         # broker-neutral order intent records (Section 5)
│       └── ui/                   # Dash app and screens (Section 6)
├── config/
│   ├── universe.yaml
│   ├── features.yaml
│   ├── model.yaml
│   ├── portfolio.yaml
│   ├── costs.yaml
│   └── regime.yaml
├── migrations/                   # database migration scripts (Section 2 onward)
├── scripts/
│   ├── backup.sh                 # pg_dump + rotation against the Postgres container (EW Section 8)
│   └── restore.sh
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/                 # small CSVs / pickled responses; no live API calls in tests
└── docs/
    ├── engineering_spec/         # this file lives here as 01_architecture_overview.md
    ├── reviews/                  # approved handoff packets and QA reports (EW Sections 2.2 and 9)
    └── traceability_matrix.md    # SDR-to-implementation map (EW Section 3.6)
```

### Architectural areas and their responsibilities

Each top-level subpackage of `quant_research_platform/` is one *architectural area*. Section 1 defines what each area is responsible for at a high level; later sections define how each area is structured internally.

- **`common/`** — Shared utilities used by all other areas: configuration loading from `config/`, database connection helpers, MLflow helpers, logging setup, path helpers (all paths via `pathlib`). Contains no business logic, no provider-specific code, and no UI code. Importable by every other area; imports from no other project area.
- **`providers/`** — Data provider abstraction. Defines a provider-neutral interface and houses provider-specific subpackages (`providers/eodhd/` for Phase 1). Implements SDR Decision 2: only this area may contain code that knows how to talk to EODHD. **`providers/` returns provider-tagged DTOs containing `provider_name` and `provider_symbol`. It does not persist to Postgres.** The persistence boundary is owned by `ingestion/`. Detail in Section 2.
- **`ingestion/`** — The only area that persists provider-sourced records to Postgres. Orchestrates the full flow from provider call to durable storage: invokes the provider adapter, validates the returned DTOs against the data quality framework, and writes raw and normalized rows in transactions. Owns the 30-day EODHD purge mechanism per SDR Decision 2. The only area outside `providers/` that imports from `providers/`. Detail in Section 2.
- **`features/`** — Computes ETF and benchmark features from data already in Postgres. Reads via `common/` database helpers. Does not import from `providers/` or `ingestion/`. Detail in Section 3.
- **`targets/`** — Generates regression and classification labels per SDR Decision 6. Same import discipline as `features/`. Detail in Section 3.
- **`regime/`** — Computes the SPY/200dma trend regime and the VIX-percentile (or realized-vol fallback) volatility regime per SDR Decision 9. Same import discipline as `features/`. Detail in Sections 3 and 4.
- **`models/`** — Baseline models per SDR Decision 5 (no-ML factor model and calibrated logistic regression), calibration pipeline per SDR Decision 7, and model registry integration per SDR Decision 11. Reads features and targets from Postgres; writes runs to MLflow and registry rows to Postgres. Detail in Section 3.
- **`backtest/`** — Walk-forward harness with purge/embargo per SDR Decision 7, transaction-cost application per SDR Decision 8, eligibility filtering per SDR Decisions 3 and 4. Reads model outputs from Postgres/MLflow, features and targets from Postgres, and regime state from Postgres. Detail in Section 4.
- **`attribution/`** — Stores per-trade and per-signal attribution from backtest runs and produces attribution reports. Reads from `backtest/` outputs in Postgres; produces additional Postgres rows and reports. Detail in Section 4.
- **`portfolio/`** — Portfolio rules engine: converts model output into BUY/HOLD/TRIM/SELL/REPLACE/WATCH actions per SDR Decision 10. Reads model rankings and regime state from Postgres; reads thresholds from `config/portfolio.yaml`. Produces action records. Detail in Section 5.
- **`paper/`** — Paper portfolio state: positions, cash, history. Consumes portfolio actions from Postgres; persists state in Postgres. Detail in Section 5.
- **`order_intent/`** — Broker-neutral order-intent records per SDR Decisions 8 and 15. Consumes paper-state from Postgres; produces order-intent rows in Postgres with no live broker code path. The architectural rule is: no broker SDK or broker HTTP client is permitted in this area or anywhere else in Phase 1, and no broker SDK may appear in dependency manifests or container build files. Detail in Section 5.
- **`ui/`** — Dash application hosting the seven Phase 1 screens per SDR Decision 17. Reads from Postgres and MLflow only via read-only access paths. Imports no business logic from any other business area. Detail in Section 6.

### Python import dependency graph

Every business area imports `common/` only. Inter-business-area Python imports are forbidden. The two exceptions are the data layer's own seam (`ingestion/` imports `providers/`) and `common/` itself (which has no project-area imports).

```
common/         ← no project-area imports

providers/      → common/
ingestion/      → providers/, common/
features/       → common/
targets/        → common/
regime/         → common/
models/         → common/
backtest/       → common/
attribution/    → common/
portfolio/      → common/
paper/          → common/
order_intent/   → common/
ui/             → common/
```

A business area that needs a type, enum, or helper from another business area must promote it to `common/` (or accept that the coupling is data-driven, not import-driven). No business area may import another business area's modules to share behavior.

A subsequent section that needs to relax this rule must propose the relaxation as a Section 1 boundary amendment and obtain Approver approval per EW Section 3.3 (no assumption drift) and Section 2.3 (Approval Matrix).

### Data-at-rest dependency graph

Computational coupling between business areas flows through Postgres (the system of record) and MLflow (model run metadata and artifacts), not through Python imports. The allowed data dependencies are:

- **`models/`** reads feature tables and target tables produced by `features/` and `targets/`.
- **`backtest/`** reads features, targets, model outputs (from Postgres and MLflow), regime state, cost-bucket assignments, and eligibility/universe records.
- **`attribution/`** reads backtest outputs.
- **`portfolio/`** reads approved model rankings and regime state.
- **`paper/`** reads portfolio action records.
- **`order_intent/`** reads paper-state and writes broker-neutral order-intent records.
- **`ui/`** reads reporting/query outputs from Postgres and MLflow only, via read-only access paths. It does not write SDR-governed state; see *Architectural invariants*.

Section 2 specifies the application database schema that supports these data dependencies. Sections 3, 4, and 5 extend the schema for their respective domains. Each schema addition is subject to Approver approval per the Approval Matrix (EW Section 2.3, "Database schema changes").

### Architectural invariants

These invariants are testable at the boundary level and are required by the SDR or EW. Section 1 reserves the test scaffolding for them; the tests themselves are built incrementally as later sections add code.

1. **Provider abstraction boundary (SDR Decision 2).** No module outside `quant_research_platform.providers` may import from EODHD-specific submodules or use EODHD client libraries. An import-boundary test enforces this.
2. **No live broker code paths (SDR Decisions 1, 15, 18).** No module anywhere in the project may import a broker SDK (Schwab, IBKR, Alpaca, or any other), declare one as a dependency, or make HTTP calls to broker order-placement endpoints. The architectural defenses are: (a) an import-boundary test against project Python code; (b) a dependency-manifest scan over `pyproject.toml`, the generated `requirements.txt`, the `Dockerfile`, and `docker-compose.yml` for known broker SDK package names; and (c) a string scan of code, config, fixtures, and docs for broker order-placement endpoint patterns.
3. **UI read-only (SDR Decision 17).** The `ui/` area must not import from `portfolio/`, `paper/`, `order_intent/`, `models/` (training-side), `backtest/`, `attribution/`, or `ingestion/`. The `ui/` area must also use only read-only database access paths — no INSERT, UPDATE, DELETE, DDL, model-promotion writes, portfolio-state writes, paper-state writes, or order-intent writes. An import-boundary test enforces the import side at the architectural level. Section 6 defines the database-access enforcement mechanism (for example, a separate read-only Postgres user, restricted query helpers, or static checks against UI database calls).
4. **Postgres is the system of record (SDR Decision 11).** Business logic does not read application state from MLflow. MLflow is read by `models/` for run metadata and by `ui/` for the Model Registry Browser screen — neither uses MLflow as a state store for portfolio, paper, or order-intent data. An import/usage check confirms `portfolio/`, `paper/`, and `order_intent/` do not read application state from MLflow.
5. **No hardcoded paths or host-specific assumptions (EW Section 7).** All filesystem paths are constructed via `pathlib.Path` and reference container-local paths only (for example, `/app/config`, `/app/data`). Host-to-container path mappings live in `docker-compose.yml`.
6. **No secrets or credentials in code, config, fixtures, logs, or docs (EW Sections 7, 9, 10).** A diff scan check enforces this on every change.
7. **Time-aware research auditability (SDR Decision 16).** The architecture must support point-in-time reconstruction and auditability for look-ahead bias, survivorship bias, overlapping labels, and backtest leakage. Section 1 does not define the schema fields or implementation details. Sections 2, 3, and 4 must define the data contracts, alignment rules, purge/embargo logic, and tests that enforce this requirement.

### Naming conventions

- **Python package name.** `quant_research_platform` (lowercase, underscores) — the importable package name. The repository name `quant-research-platform` (lowercase, hyphens) follows packaging convention and matches the EW Section 8 image tag prefix. The mismatch between the repository name and the package name is conventional in Python.
- **Subpackage names.** Lowercase, single word where possible (`features`, `targets`, `models`, `backtest`, `paper`, `regime`, `ui`). Two-word names use underscores (`order_intent`).
- **Module file names.** Lowercase, underscores, descriptive (`config_loader.py`, `walk_forward.py`). Test files mirror module names with a `test_` prefix.
- **Test discovery.** All tests live under `tests/`; pytest discovery is rooted there. Subdirectories `tests/unit/`, `tests/integration/`, and `tests/fixtures/` follow EW Section 5.
- **Application image tag prefix.** `quant-research-platform` per EW Section 8 v1.4. Image tags include the git commit hash; milestone tags additionally apply a semantic suffix (for example, `quant-research-platform:0.1.0-data-layer`). The `latest` tag is not used in production runs (EW Section 8).
- **Docker Compose service names.** Lowercase, hyphenated, role-based: `postgres`, `mlflow`, `app`, optionally `nginx`.
- **Named volumes.** Lowercase, hyphenated, role-based: `pgdata`, `mlflow-artifacts`. Confirmed by EW Section 8.
- **Migration file names.** A monotonic numeric prefix and short description (for example, `0001_initial_universe_tables.sql`, `0002_add_provider_columns.sql`). Detail of the migration tooling is in Section 2.
- **YAML config file names.** Already enumerated under *Config dependencies* — these are the canonical filenames; sections that introduce new config keys do so within these files unless a new file is approved by the Approver as a Strategy-affecting config change per EW Section 7.

### Environment and config flow

At runtime, configuration and credentials reach the application code as follows:

1. **YAML config.** Files under `config/` are mounted into the application container read-only at `/app/config`. The `common/` config loader reads them at process startup and caches them. Container restart picks up YAML changes; image rebuild is not required (EW Section 7). The Dash app and scheduled jobs share the same loader.
2. **Credentials.** `docker compose` reads the host `.env` file and injects environment variables into the application and MLflow containers via `env_file:` / `environment:` directives. The `common/` credential helper reads `os.environ`. No module reads `.env` directly from inside the container. `python-dotenv` is permitted as a developer-side convenience for running scripts outside the container during local development; it is not a runtime dependency of the deployed stack.
3. **Database connectivity.** Postgres connection parameters reach the application via injected environment variables. The `common/` database helper constructs the connection from these. The MLflow container connects to the same Postgres instance using its own injected credentials and a separate database name.
4. **MLflow tracking URI.** The application container reaches the MLflow tracking server via the internal Docker network; the URI is provided as an injected environment variable.

---

## Config dependencies

The following YAML files exist under `config/` and are governed by EW Section 7. Section 1 enumerates them and describes what each governs at the architectural level. Detailed schemas are defined in the section that owns the corresponding domain.

| Config file | Architectural purpose | Detailed schema in |
|---|---|---|
| `config/universe.yaml` | ETF universe layers (Core Test, Candidate, Future Full Eligible), eligibility rules, sleeve mappings, primary/secondary benchmark assignments, ETF lifecycle fields per SDR Decisions 3, 4, 5 | Section 2 |
| `config/features.yaml` | Feature parameters (lookback windows, smoothing constants, etc.) per SDR Decisions 5, 6 | Section 3 |
| `config/model.yaml` | Model hyperparameters, calibration settings, target horizons (63 / 126 days), walk-forward window and embargo configuration per SDR Decisions 5, 6, 7 | Section 3 |
| `config/portfolio.yaml` | Portfolio-rule thresholds, position limits, ATR multiples, rebalance cadence, model-promotion gate parameters per SDR Decisions 10, 12, 15 | Section 5 |
| `config/costs.yaml` | Transaction-cost buckets and basis-point assumptions per SDR Decision 8 | Section 4 |
| `config/regime.yaml` | Regime classification thresholds and the realized-vol fallback rule per SDR Decision 9 | Sections 3 and 4 |

Section 1 does not specify the contents of any of these files. Section 1 reserves their existence and their architectural role.

The host `.env` file (gitignored) and `.env.example` (committed) are governed by EW Section 7 and SDR Decision 18. Section 1 reserves the convention; the variable list is grown by later sections as new credentials are introduced and is reflected in `.env.example` at each step.

Config-change classification (EW Section 7) — Operational, Research, Strategy-affecting, Production runtime, Credential/environment — is a process concern, not an architectural one, and is governed entirely by the EW.

---

## Required tests

Section 1's tests are *architectural* — they verify the structural invariants established here. Module-level tests are defined in the section that introduces the module. The time-aware research auditability invariant (Architectural invariant 7) is *not* tested at Section 1; per Approver direction, the data contracts, alignment rules, purge/embargo logic, and the tests that enforce them are defined in Sections 2, 3, and 4.

Tests live under `tests/unit/architecture/` and `tests/integration/architecture/` (final paths confirmed when Section 2 begins).

1. **Provider-abstraction import-boundary test.** Statically verify that no module under `quant_research_platform` outside `providers/` imports from `providers.eodhd` or from EODHD-specific client libraries. Failing this test is a defect against SDR Decision 2.
2. **No-live-broker boundary test (multi-part).**
   (a) Static import-boundary check: no module imports a broker SDK.
   (b) Dependency-manifest scan: `pyproject.toml`, `requirements.txt`, `Dockerfile`, and `docker-compose.yml` are scanned for known broker SDK package names (Schwab, IBKR, Alpaca, and similar) on every change.
   (c) String scan over code, config, fixtures, and docs for broker order-placement endpoint patterns.
   Failing any part is a defect against SDR Decisions 1, 15, and 18.
3. **UI read-only import-boundary test.** Statically verify that `ui/` does not import from `portfolio/`, `paper/`, `order_intent/`, `backtest/`, `attribution/`, `ingestion/`, or training-side `models/` modules. Failing this test is a defect against SDR Decision 17. The database-access enforcement mechanism for the UI read-only constraint is defined and tested in Section 6.
4. **Postgres-as-system-of-record import test.** Statically verify that `portfolio/`, `paper/`, and `order_intent/` do not read application state from MLflow. Failing this test is a defect against SDR Decision 11.
5. **Container startup smoke test.** With `docker compose up -d`, the three Phase 1 containers reach a healthy state within a defined timeout. Postgres accepts connections; the MLflow tracking server responds; the Dash app responds on its configured port. The health check additionally confirms the cron daemon is running inside the application container, so a Dash-only health signal cannot mask a failed cron.
6. **Cross-container connectivity smoke tests.** From inside the `app` container, a connection to the `postgres` service succeeds; a connection to the MLflow tracking URI succeeds; a query of `pg_catalog` returns the application database and the MLflow metadata database.
7. **Config loader smoke test.** Each of the six YAML files under `config/` loads without error via the `common/` config loader. Schema validation per file is a Section 2–6 concern; Section 1 only requires that the files exist, are parseable YAML, and are reachable at the expected container path.
8. **`.env.example` parity check.** Every environment variable referenced by `docker-compose.yml` (via `env_file:` / `environment:`) or by the `common/` credential helper is present in `.env.example` with a placeholder value. New variables introduced in later sections trigger a `.env.example` update at the same merge.
9. **Path-handling lint.** A static check that no module contains a hardcoded absolute path or a Windows drive letter, and that all path manipulation goes through `pathlib.Path`.
10. **Secrets-in-diff check.** A static check that no committed file (code, config, fixture, log sample, doc, notebook) contains anything matching credential patterns (API keys, tokens, passwords, broker account numbers, the literal contents of `.env`).
11. **Image rebuild test.** The application image rebuilds successfully from a clean cache. Required at every change to `Dockerfile`, `docker-compose.yml`, `requirements.txt` / `pyproject.toml`, or `.dockerignore` per EW Sections 8 and 10.
12. **Portability test.** Per EW Section 8, before any milestone tag, spin up the stack on a fresh test environment from the repository plus a backup; confirm the system runs and reports the same state. Validates that no hidden host state has accumulated.

Tests 1–4 require no business logic to run — they are static checks and can be implemented as soon as the empty package skeleton exists. Tests 5–8 require the container scaffolding from Section 1 plus a minimal `app` entrypoint. Tests 9–12 are continuous discipline checks rather than one-shot tests.

**Manual checks and conversion to automation.** Tests 2(b), 2(c), 8, 9, and 10 may be performed manually until a working test harness exists; manual execution is acceptable only when paired with a documented checklist stored under `docs/reviews/` for each Approver-gate change, and the check is converted to an automated test (running in `docker compose exec app pytest`) when practical. EW Section 5 ("tests must verify financial meaning, not just mechanics") and Section 9 ("review the artifact, not the summary") apply equally to architectural tests.

Module-internal tests (data-quality tests, feature look-ahead tests, target alignment tests, model fit/predict tests, backtest embargo tests, portfolio transition tests, order-intent paper-only tests, UI smoke tests) are defined in their owning sections per EW Section 5. The bias-control tests required by Architectural invariant 7 are defined in Sections 2, 3, and 4.

---

## Edge cases and failure behavior

At the architectural level, the failure modes Section 1 must account for are container-and-cross-container in nature. Module-level failure handling is defined in Sections 2–6.

1. **A container fails to start.** Each service in `docker-compose.yml` declares a Docker health check (EW Section 8); dependent services wait for prerequisites before starting. If the `postgres` container fails health checks, the `mlflow` and `app` containers do not enter their normal state — `app` either blocks or surfaces a clear startup error rather than degrading silently. The architectural requirement is: the application surfaces the failure rather than appearing healthy with no data.
2. **A container is OOM-killed mid-job.** Each service declares explicit memory and CPU limits (EW Section 8). Docker OOM-kills the offending container and restarts it via `restart: unless-stopped`. Scheduled jobs that were mid-run when the kill occurred are not auto-resumed; the next scheduled run picks up. Whether a partially-completed job leaves Postgres in an inconsistent state is a Section 2 concern (transactional ingestion) and a Section 3/4 concern (idempotent runs).
3. **Cron fails or scheduled job fails inside the app container.** The application container's health check covers both Dash and cron, so a Dash-only healthy signal does not mask cron failure. Failed scheduled-job runs surface through container logs and through the data-quality and model-quality status surfaces defined in Sections 2 and 4. There is no architectural state in which scheduled jobs silently stop running while the system reports healthy.
4. **The data provider is unreachable.** The provider abstraction layer (Section 2) wraps EODHD calls. When EODHD is unreachable, the provider adapter raises a structured exception that ingestion converts into a data-quality exception report per SDR Decision 2 and the Data Quality Exception Report Standard in SDR Decision 11. No downstream module proceeds with stale data silently. Auto-retry of failed API calls is allowed per SDR Decision 11 ("Agents may auto-resolve mechanical issues such as retrying failed API calls"); silent fallback to a different provider is forbidden.
5. **Postgres is reachable but a migration applied partially.** EW Section 7 requires that database schema changes have a migration script and a rollback plan; manual production database changes are not permitted. If a migration is found to have applied partially, the architectural response is to stop scheduled jobs, run the rollback, and surface the failure as a data-quality-and-deployment exception. Section 2 specifies the migration tooling.
6. **MLflow is unreachable.** Modules that write to MLflow (training-side `models/`, `backtest/`) fail their run rather than silently dropping tracking. Modules that read from MLflow (`ui/` Model Registry Browser screen) surface the unavailability with a clear UI message rather than an empty list that resembles "no models."
7. **A YAML config file is missing or malformed.** The `common/` config loader fails at startup with a clear, structured error naming the file and the parse error. The Dash app and scheduled jobs do not start with partial config. There is no silent default for any field that originates in YAML.
8. **`.env` is missing or incomplete on the host.** `docker compose up` fails with a clear error from the missing `env_file:` reference, or the application container fails its health check at startup because a required environment variable is unset. There is no fallback to hardcoded credentials. `.env.example` documents what is required, and the `.env.example` parity check (test 8) catches drift.
9. **Disk fills.** Postgres stops accepting writes; MLflow artifact writes fail; the application container surfaces the failure as a deployment-level exception. Backups (EW Section 8) and named-volume sizing are operational concerns reviewed before each milestone.
10. **EODHD subscription cancelled.** Per SDR Decision 2, raw and normalized EODHD-sourced data must be purged within 30 days. The architectural support for this is the `provider_name` and `provider_symbol` columns recorded by `ingestion/` on every provider-sourced row (Section 2 detail) plus a deletion routine that filters by `provider_name = 'eodhd'`. Section 1 reserves this requirement; Section 2 implements the routine and tests it.
11. **An unintended live-broker call path is introduced.** This is a critical defect. The architectural defense is the multi-part no-live-broker test (test 2 above), the QA review item in EW Section 9 ("can this module cause a live broker order? It must not"), and the secrets-in-diff check ensuring no broker credentials are accidentally committed. Detection at QA review is preferred; detection in the boundary tests is a backstop.
12. **The UI attempts a write.** Test 3 catches the import-side path for some classes of accidental write; the database-access enforcement mechanism Section 6 defines (for example, a read-only Postgres role for the UI) catches the database-side path. Section 1 requires that one or both of these enforcement layers exist before the UI ships any screen that could plausibly issue a write.

---

## Open questions

All ten open questions raised in v0.1 have been resolved by Approver decision and are recorded under *Approver-resolved defaults* in the next section. No new open questions remain at v0.2.

If implementation surfaces a new open question that Section 1 should resolve rather than leaving to a later section, the Builder pauses per EW Section 3.5 and escalates to the Approver before continuing.

---

## Explicit assumptions

Every architectural choice in this section is classified per EW Section 3.3 as one of: Derived from SDR or EW, Implementation default, Approver-resolved default, or Open question for Approver. The classifications below cover the choices Section 1 makes that are not directly stated by an SDR decision.

### Derived from SDR or EW

- **Three-container Phase 1 stack with reserved optional fourth (nginx).** Direct from SDR Decision 18 and EW Section 8.
- **Named volumes `pgdata` and `mlflow-artifacts`.** Direct from EW Section 8.
- **MLflow metadata in Postgres, artifacts in named volume.** Direct from SDR Decision 11.
- **Application container hosts both the Dash UI and the scheduled jobs.** Direct from SDR Decision 17 (UI in app container) and EW Section 8 (scheduled jobs in app container via cron-in-container).
- **Provider abstraction boundary; no module outside `providers/` may call EODHD.** Direct from SDR Decision 2.
- **`provider_name` and `provider_symbol` on provider-sourced records.** Derived from SDR Decision 2 (EODHD storage constraint requires identifiability for the 30-day purge). Carried on DTOs returned by `providers/` and persisted by `ingestion/`.
- **Time-aware research auditability invariant.** Derived from SDR Decision 16. Section 1 reserves the requirement at the architectural level only; Sections 2, 3, and 4 implement.
- **UI read-only invariant including database-access prohibition.** Derived from SDR Decision 17 (the UI is read-only with respect to model promotion, broker execution, and live trading). v0.2 makes the database-access dimension explicit as an architectural invariant; Section 6 selects the enforcement mechanism.
- **Image tag prefix `quant-research-platform`.** Direct from EW Section 8 v1.4.
- **YAML config in git under `config/`; gitignored host `.env`; `.env.example` committed.** Direct from SDR Decision 18 and EW Section 7.
- **All paths via `pathlib`; no hardcoded paths.** Direct from EW Section 7.
- **Tests must run inside the application container via `docker compose exec app pytest`.** Direct from EW Section 5.
- **Repository file inventory** (`Dockerfile`, `docker-compose.yml`, `.env.example`, `.dockerignore`, `config/`, `migrations/`, `scripts/backup.sh`, `scripts/restore.sh`, `docs/engineering_spec/`, `docs/reviews/`, `docs/traceability_matrix.md`). Direct from EW Section 8.
- **Six YAML config files.** Direct from EW Section 7.
- **No live broker code paths anywhere in Phase 1, including in dependency manifests.** Direct from SDR Decisions 1, 15, and 18 and EW Approval Matrix (Section 2.3).

### Implementation default (no strategy impact)

- **Twelve top-level subpackages of `quant_research_platform/`.** The SDR/EW name most of these architectural areas; making each one a separate top-level subpackage (rather than nesting, e.g., `attribution/` inside `backtest/`) is an implementation choice with no strategy impact.
- **Strict "every business area imports `common/` only" rule.** Slightly stricter than v0.1's wording. Adopted because it makes each business area independently testable and makes the platform's coupling fully data-driven through Postgres/MLflow, matching the system-of-record architecture of SDR Decision 11.
- **Naming conventions.** Lowercase package names, underscores in two-word names, `test_` prefix for test files, hyphenated Compose service names. Standard Python and Docker conventions.
- **Test directory structure.** `tests/unit/`, `tests/integration/`, `tests/fixtures/`. Standard pytest layout.
- **Container service names.** `postgres`, `mlflow`, `app`, optionally `nginx`. Standard role-based naming.
- **Migration filename convention.** `0001_short_description.sql`. Standard.
- **Read-only mount of `config/` at `/app/config`.** EW Section 7 says "mounted read-only into the application container at a known path (e.g., `/app/config`)"; using exactly `/app/config` is an implementation default.

### Approver-resolved defaults (Section 1)

These were the ten open questions in v0.1. The Approver resolved each on 2026-04-26:

| Item | Decision |
|---|---|
| Python version | **Python 3.12** |
| Repository layout | **`src/quant_research_platform/`** |
| Dependency manager | **`pyproject.toml` + pinned `requirements.txt` for the Dockerfile** |
| Test framework | **pytest** |
| Linter / formatter | **ruff** (lint and format) |
| nginx in initial Phase 1 stack | **Omit initially**; add later only if controlled UI exposure is needed |
| `python-dotenv` scope | **Local development only**; not a runtime dependency of the deployed stack |
| MLflow web UI exposure | **Internal-only**; access via SSH tunnel during development |
| Scheduled-job tooling | **cron-in-container**, invoking thin command-line entry points |
| Container logging destination | **stdout/stderr captured by Docker**, rotated via Docker's default log driver |

Any change to these defaults is treated as an architectural change and goes through the EW change process.

### Open question for Approver

None remaining at v0.2.

---

## Section 1 → Sections 2–6 handoff

Section 1 leaves the platform with a folder skeleton, a three-container stack scaffold (with nginx reserved), configuration filenames, an enforced import discipline, a data-at-rest dependency contract, and the architectural invariants the rest of the platform must respect, including the time-aware research auditability invariant. It does not specify any business logic. The handoff to subsequent sections is:

- **Section 2 — Data layer.** Fills `providers/` (provider abstraction interface and EODHD implementation, returning provider-tagged DTOs), `ingestion/` (the only persistence path for provider-sourced records), the application database schema in Postgres, the data quality framework, the migrations, and the 30-day EODHD purge mechanism. Owns `config/universe.yaml`. Implements SDR Decisions 2, 3, 4, 5 (universe-side), 11 (data-quality reporting standard), and the Section 1 invariant 7 reservation for time-aware data at the universe and ingestion level. Section 2 also defines the initial Postgres schema fields that support point-in-time reconstruction.
- **Section 3 — Features, targets, models.** Fills `features/`, `targets/`, `regime/` (computation side), `models/`. Owns `config/features.yaml` and `config/model.yaml`. Implements SDR Decisions 5, 6, 7 (calibration side), 9 (computation side), 11 (MLflow integration), 12 (model state field side), and the Section 1 invariant 7 reservation for feature/target alignment and overlapping-label handling.
- **Section 4 — Backtest, attribution, validation.** Fills `backtest/`, `attribution/`, `regime/` (consumption side). Owns `config/costs.yaml` and `config/regime.yaml`. Implements SDR Decisions 7 (validation harness, purge/embargo), 8, 9 (consumption side), 11 (attribution storage), 12 (kill-switch monitoring), 16 (bias controls and reporting), and the Section 1 invariant 7 reservation for backtest leakage prevention and reproducibility metadata.
- **Section 5 — Portfolio, paper, order intent.** Fills `portfolio/`, `paper/`, `order_intent/`. Owns `config/portfolio.yaml`. Implements SDR Decisions 10, 12 (gate side), 15.
- **Section 6 — UI.** Fills `ui/`. Implements SDR Decision 17 (the seven screens, their read-only enforcement on both the import side and the database-access side), and selects the database-access enforcement mechanism for Section 1 invariant 3.

Each subsequent section operates within the architectural boundaries Section 1 establishes. A subsequent section that needs to expand or modify a Section 1 boundary (for example, a new architectural area, a new YAML file, a relaxed import rule, a relaxation of the UI database-access constraint) must propose the change as a Section 1 amendment and obtain Approver approval before proceeding, per EW Section 3.3 (no assumption drift) and Section 2.3 (Approval Matrix).

---

**End of Section 1 v0.2 draft.**
