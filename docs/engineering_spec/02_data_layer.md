# Engineering Specification — Section 2: Data Layer

**Phase 1 scope:** ETF tactical research platform.
**Section status:** v1.0 LOCKED / APPROVED
**Draft date:** 2026-04-27
**Author:** Builder (Claude)
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- `docs/traceability_matrix.md`

---

## Changelog

**v1.0 LOCKED / APPROVED (2026-04-27).** Approver final approval. One cleanup edit applied at locking, with no other changes:

- *Explicit assumptions → Proposed default 4 (Provider DTO contract — Pydantic v2)* corrected to remove `as_of_date` from the required tagging fields on every DTO. The main DTO contracts subsection had already been updated in v0.3 to declare `as_of_date` per-DTO rather than on every DTO; the Item 4 wording was the last remaining inconsistency, now resolved. Date fields are DTO-specific: `ProviderEODBarDTO` carries `as_of_date`; `ProviderCorporateActionDTO` carries corporate-action date fields; `ProviderEtfMetadataDTO` carries no as-of-date.

Section now committed as v1.0 LOCKED at `docs/engineering_spec/02_data_layer.md`. Approval note: `docs/reviews/2026-04-27_spec_02_data_layer_approval.md`. Subsequent changes to this section follow EW Section 3 amendment discipline and the Approval Matrix in EW Section 2.3.

**v0.3 (2026-04-27).** Targeted Approver-directed revisions of v0.2 before approval. No scope expansion. Ten fixes applied:

1. **Effective-date range semantics fixed.** Effective-dated tables now use half-open ranges: `effective_start_date` is **inclusive**, `effective_end_date` is **exclusive**, `NULL` end-date means current/open-ended. EXCLUDE constraints use `daterange(..., '[)')`. Migration `0001_initial_setup.sql` enables the `btree_gist` Postgres extension required by these constraints.
2. **`ops.data_snapshots` strengthened.** Added six explicit reproducibility fields: `provider_name`, `provider_dataset_label`, `universe_config_hash`, `universe_version_label`, `adjusted_price_convention`, `price_table_max_as_of_date`. `data_snapshot_id` remains the downstream reference consumed by Sections 3 and 4.
3. **`rank_method` placeholder replaced.** YAML examples now use the temporary sentinel `pending_section_3` rather than `<Section-3-defined>`. Section 2 validates presence and type only; Section 3 must define allowed `rank_method` values and replace these sentinels before ranking or model implementation.
4. **`ProviderEtfMetadataDTO` date semantics clarified.** Removed `as_of_date` from the common-fields list because metadata is identity-level and does not carry an as-of-date semantics. `as_of_date` is now declared per DTO that uses it (only `ProviderEODBarDTO` in Phase 1). Metadata retrieval timing is captured by `pulled_at_utc`.
5. **Benchmark constraint tightened.** `universe.etfs.primary_benchmark_id` is now `NOT NULL`. Every Phase 1 ETF must have a primary benchmark assigned.
6. **DQ exception redaction added.** All text and JSON fields written to `ops.data_quality_exceptions` pass through the same secret-redaction utility used for raw payloads before persistence. Test added.
7. **EODHD purge treatment of `ops.ingestion_runs` clarified.** Purge does not delete `ops.ingestion_runs` rows — they are operational audit metadata. The `chunk_results` JSONB and `notes` columns on rows where `provider_name='eodhd'` are redacted during purge so the rows do not retain raw provider content; `status`, timestamps, hashes, and counts are preserved.
8. **Natural uniqueness for `prices.corporate_actions` added.** Unique index on the natural key `(etf_id, provider_name, action_type, ex_date, COALESCE(factor, 0), COALESCE(amount, 0))` prevents duplicate corporate-action rows on re-pull. Test added.
9. **Companion traceability file wording corrected.** Now describes three label findings, with Finding 3 explicitly framed as a label tightening rather than a mislabel.
10. **Decision 10 label correction applied now.** The companion file proposes correcting Decision 10's label to "Portfolio Management and Risk Rules" as part of the Section 2 approval merge, even though the row remains `pending` until Section 5.

**v0.2 (2026-04-27).** Targeted Approver-directed revisions of v0.1 before approval. No scope expansion. Thirteen fixes applied:

1. **Provider abstraction method signatures.** A new *Provider abstraction interface* subsection in *Data contracts* defines `fetch_eod_bars`, `fetch_eod_bars_batch`, `fetch_corporate_actions`, and `fetch_etf_metadata` with input/output types, empty-result semantics, structured-exception semantics, and batch behavior. A `ProviderBatchResult` envelope captures per-symbol successes and per-symbol failures.
2. **Ingestion transaction model resolved (chunk-level atomicity).** A new *Ingestion transaction model and partial-run semantics* subsection establishes that the atomic write unit is the *chunk* (one chunk = one provider-symbol pull for daily EOD). Chunks commit transactionally; runs may end as `partial` if some chunks succeed and others fail; `ops.ingestion_runs` carries a `chunk_results` JSONB column recording per-symbol outcomes; downstream compute blocks on `failed` and (by default) `partial` runs. Edge case 2 and the ingestion tests are aligned to this design.
3. **MLflow database bootstrap separated from application migrations.** Database creation, role creation, and grants now live in `scripts/postgres-init/` SQL files mounted into the Postgres container's `/docker-entrypoint-initdb.d/`. The transactional migration runner only manages schemas inside the application database; it does not run `CREATE DATABASE` or `CREATE ROLE`.
4. **Traceability matrix audit performed.** Decision labels in `docs/traceability_matrix.md` v0.2 were checked against the locked SDR v1.0. Two mislabels found: Decision 5 (existing label "Phase 1 baseline models" → correct label "Benchmark, Sleeve, and Diversifier Treatment") and Decision 10 (existing label "Configuration storage (YAML in git) and rebalance/review cadence" → correct label "Portfolio Management and Risk Rules"). Section 2's replacement rows use exact SDR labels. The Decision 10 mislabel is outside Section 2's scope but is flagged for Approver attention in the companion file. Decision 4's label is also tightened to match the SDR exactly.
5. **Placeholder config values removed.** `min_avg_daily_dollar_volume_usd` now has a proposed default of $25,000,000 (Proposed default requiring Approver approval). `rank_method` is required per ETF; Section 2 validates presence and string type only; allowed values and semantics are deferred to Section 3.
6. **Exact `.env` variable names listed.** `APP_DB_*` and `MLFLOW_DB_*` expanded to specific names; full list in *Config dependencies → Environment variables*.
7. **Stale-data thresholds moved to YAML.** `config/universe.yaml` adds a `data_freshness:` block with `stale_warning_business_days` and `stale_fail_business_days`. Defaults remain 5 and 10 (Proposed default requiring Approver approval).
8. **No-overlap constraints and tests added** for `universe.etf_provider_mapping`, `universe.etf_ticker_history`, and `universe.etf_eligibility_history`. Each table specifies a Postgres `EXCLUDE` constraint on the natural-key columns and a daterange built from the effective dates. Required tests verify constraint violation on overlapping inserts.
9. **`provider_run_id` persisted.** Added to `prices.etf_prices_daily`, `prices.corporate_actions`, and `ops.provider_raw_payloads`.
10. **Raw payload retention tightened.** Provider adapters strip secrets (Authorization headers, query parameters matching credential patterns, tokenized URL components) before persistence. `ops.data_quality_exceptions` adds a `provider_name` column for purge filtering; the EODHD 30-day purge extends to `data_quality_exceptions` rows where `provider_name='eodhd'`. A redaction test is required.
11. **Data snapshot concept added.** New `ops.data_snapshots` table records pinned data sets (label, as-of date, ingestion-run set, commit/config hashes, status). Sections 3 and 4 reference `data_snapshot_id` to satisfy EW Section 7 reproducibility. The EODHD purge invalidates affected snapshots rather than deleting them.
12. **Current-survivor disclosure storage clarified.** The label string lives in `config/universe.yaml` under `disclosures.current_survivor_label`. A `common/` retrieval function returns it. Applicability and surfacing are Sections 4 and 6 concerns.
13. **Canonical vs denormalized eligibility fields clarified.** `universe.etf_eligibility_history` is canonical for the actual eligibility timeline; `universe.etfs.eligible_start_date` is canonical for the *eligibility-rules-computed earliest possible eligibility* — a distinct semantic. A consistency rule prevents `is_rank_eligible=true` history rows with `effective_start_date < etfs.eligible_start_date`. `universe.etfs.active` is denormalized from `delisted_date` with a consistency rule. Both rules are tested.

**v0.1 (2026-04-27).** Initial draft. Approver direction received pre-drafting on the adjusted-price convention and the application-container entrypoint mechanism.

---

## Purpose

Section 2 establishes how data enters the system, where it is stored, how it is verified, and how the schema supports point-in-time reconstruction. It defines the provider abstraction interface, the EODHD provider implementation, the foundational Postgres application database schema, the MLflow metadata database at the Postgres level, the data-quality framework, ingestion orchestration, the migrations infrastructure, the EODHD 30-day deletion mechanism, the contents of `config/universe.yaml`, and the application-container entrypoint mechanism that Section 1's approval note handed forward.

This section is the schema-level cash-out of Section 1 invariant 7 (time-aware research auditability) for the universe and ingestion domains. Sections 3 and 4 extend the same invariant to features/targets and to backtest/attribution.

This section does not define feature formulas, target labels, model training, calibration pipelines, MLflow client-side integration, walk-forward harness internals, portfolio rules, paper-state management, or UI screens. Those belong to Sections 3-6.

---

## Relevant SDR decisions

Section 2 directly implements:

- **SDR Decision 2** — Data provider abstraction principle and the EODHD storage constraint (provider abstraction interface and methods, EODHD implementation, the 30-day deletion mechanism, `provider_name`/`provider_symbol`/`provider_run_id` tagging on every provider-sourced row).
- **SDR Decision 3** — ETF universe layered model (Core Test, Candidate, Future Full Eligible), eligibility rules, the universe registry schema, `config/universe.yaml`.
- **SDR Decision 4** — Universe Survivorship and ETF Launch-Date Handling (inception/first-traded date, eligible-start date, active flag, optional delisted date, optional replacement ETF, universe-layer membership, rank-eligibility flag, current-survivor disclosure label).
- **SDR Decision 5 (universe-side only)** — Benchmark, Sleeve, and Diversifier Treatment: sleeve and benchmark assignment fields on ETF records (sleeve, category, primary benchmark, secondary benchmark, portfolio role, rank method, equity-rotation eligibility, diversifier-sleeve eligibility). Sleeve-aware ranking math and benchmark-relative computations belong to Section 3.
- **SDR Decision 11** — Data quality reporting standard plus the Postgres setup that supports the application database and the MLflow metadata database. MLflow client-side integration on the writer side belongs to Section 3.
- **SDR Decision 16 (Section 2 contribution)** — universe-side and ingestion-side schema fields supporting point-in-time reconstruction; data-layer-level look-ahead and survivorship checks; data-snapshot foundation.

Section 2 also accommodates the architectural footprint of the following decisions without implementing them in detail:

- Decision 6 (target horizons), Decision 7 (walk-forward), Decision 8 (cost buckets — `universe.etfs.cost_bucket` reserved), Decision 9 (regime), Decision 10, Decision 12, Decision 15 — schema accommodates without implementing.

---

## In scope

1. The provider abstraction interface owned by `providers/`: method signatures, input/output semantics, empty-result behavior, structured-exception behavior, batch behavior, and the shape of provider-tagged DTOs returned to ingestion.
2. EODHD provider implementation in `providers/eodhd/`: subset of EODHD endpoints used in Phase 1, pagination and rate-limit handling, normalization into DTOs, and how the SDR Decision 2 storage tagging requirement is satisfied at the DTO level.
3. The Postgres application database foundational schema: universe registry, ETF identity and lifecycle, eligibility windows, sleeve and benchmark assignments, prices (raw OHLCV plus adjusted close), corporate actions, ingestion-run metadata with chunk-level result tracking, data-quality exceptions, raw provider payloads with secrets stripped, schema-migration tracking, and the data-snapshot foundation.
4. The MLflow metadata database setup at the Postgres level only: database creation, ownership, and isolation from the application database. MLflow client-side integration on the writer side belongs to Section 3.
5. The data-quality framework: exception report contents, severity rules, auto-resolution scope per SDR Decision 11.
6. Ingestion orchestration: chunk-level atomicity model, partial-run semantics, how `ingestion/` invokes `providers/`, validates DTOs, persists records in transactions, and emits data-quality exceptions.
7. Migrations infrastructure: tooling, file conventions, rollback discipline, fixture-update expectations. Migrations are application-database schema changes only; database/role bootstrap is separate.
8. Database/role bootstrap: how the application database, the MLflow metadata database, and their roles are created on Postgres first-init, separately from the application migration runner.
9. The EODHD 30-day deletion mechanism: implementation, scope, scheduling, the test that exercises it on subscription cancellation, and its interaction with `ops.data_snapshots` (invalidation, not deletion, of affected snapshots).
10. `config/universe.yaml`: contents and schema, including the layered universe model, eligibility rules, sleeve and benchmark definitions, per-ETF assignments, data-freshness thresholds, and disclosure labels.
11. Schema-level support for the time-aware research auditability invariant for the universe and ingestion domains, including no-overlap constraints on effective-dated tables and canonical/denormalized field semantics on `universe.etfs`.
12. The application-container entrypoint mechanism (handed forward by the Section 1 approval note).

---

## Out of scope

Section 2 deliberately defers the following:

- **Feature calculation formulas, lookback windows, smoothing constants** — Section 3.
- **Target generation logic, label alignment rules, overlapping-label handling** — Section 3.
- **Model training, calibration pipeline, MLflow client-side integration on the writer side, model registry tables, allowed values and semantics for `rank_method`** — Section 3.
- **Regime classification logic and regime tables** — Sections 3 (computation) and 4 (consumption).
- **Walk-forward harness, purge/embargo mechanics, transaction cost application, attribution storage tables** — Section 4.
- **Portfolio rule logic, paper portfolio state tables, broker-neutral order-intent tables** — Section 5.
- **Dash UI screens and the database-access enforcement mechanism for the UI read-only constraint** — Section 6.
- **Future provider selection** — out of scope per Approver direction; Phase 1 is EODHD only.
- **Live broker integration** — out of scope per SDR Decisions 1, 15, 18 and Section 1 invariant 2.
- **Per-section-aware partial-scope handling.** Section 2 establishes the chunk-level atomicity model and the default block-on-partial behavior; Sections 3 and 4 may opt into per-symbol-aware partial handling at their own scope.

Where a deferral has data-layer consequences, Section 2 records the convention and points to the section that will fill in the detail.

---

## Inputs and outputs

### System inputs to the data layer

1. **EODHD API responses** for the endpoints Phase 1 uses.
2. **`config/universe.yaml`**, mounted read-only at `/app/config` per Section 1.
3. **Trading-calendar data** — US market trading days; source proposed below.
4. **Ordered SQL migration files** under `migrations/forward/` and `migrations/reverse/` (application-database schema changes only).
5. **Ordered SQL bootstrap files** under `scripts/postgres-init/` (database/role creation; runs once on Postgres first-init).
6. **Credentials and connection parameters** from injected environment variables (per Section 1).

### System outputs from the data layer

1. **Postgres rows in the application database** in the `universe`, `prices`, and `ops` schemas.
2. **Provider-raw payload rows** in `ops.provider_raw_payloads` (with secrets stripped before persistence) for audit, reconciliation, and "likely cause" diagnostics on data-quality exceptions.
3. **Data-quality exception rows** in `ops.data_quality_exceptions` with the nine fields per SDR Decision 11 plus a `provider_name` column for purge filtering.
4. **Ingestion-run metadata rows** in `ops.ingestion_runs` capturing run lifecycle, status, code commit hash, config hash, and per-chunk results.
5. **Data-snapshot rows** in `ops.data_snapshots` capturing pinned data-set definitions consumed by Sections 3 and 4 for backtest reproducibility per EW Section 7.
6. **MLflow metadata database** created and isolated inside the same Postgres cluster; no Section 2 rows inside it.
7. **Plain-English data-quality exception reports** surfaced to container logs and to the Section 6 Data Quality screen.

### Module-level input/output summary

- **`providers/`**: configured provider parameters → provider-tagged Pydantic DTOs (success) or structured exceptions (failure); no Postgres writes.
- **`providers/eodhd/`**: EODHD API base URL, API token, per-call parameters → DTOs or structured exceptions; HTTP calls to EODHD only.
- **`ingestion/`**: a configured provider adapter and `config/universe.yaml` → durable Postgres rows in `universe`, `prices`, and `ops`; chunk-level transactional writes; data-quality exception rows; ingestion-run lifecycle rows; raw payloads with secrets stripped.
- **Migrations runner** (`common/db_migrations.py`): ordered SQL files in `migrations/forward/` and `migrations/reverse/` → applied schema state and `ops.schema_migrations` rows. Does not create databases or roles.
- **Application-container entrypoint**: container start signal → long-running supervisor process with Dash and cron both running and both health-check-observable.

---

## Data contracts

### Provider abstraction interface

`providers/` defines a Protocol-style interface that every concrete provider implements. Methods are stateless and idempotent given the same parameters. All methods return provider-tagged Pydantic v2 DTOs on success and raise structured exceptions on failure. No method writes to Postgres or reads Postgres state.

#### Methods

**`fetch_eod_bars(provider_symbol: str, start_date: date, end_date: date) -> Iterable[ProviderEODBarDTO]`**
Fetches end-of-day bars for one ETF over an inclusive date range.
- Returns: an iterable of `ProviderEODBarDTO`. **An empty iterable is normal** (the date range falls outside the ETF's trading history, or the range contains only non-trading days).
- Raises:
  - `ProviderTransportError` on network/HTTP failure
  - `ProviderAuthError` on 401/403
  - `ProviderRateLimitError` on quota exhaustion
  - `ProviderParseError` if the response cannot be parsed
  - `ProviderValidationError` if any returned row fails DTO validation, or if `start_date > end_date`, or if either date is invalid
  - `ProviderDataNotAvailableError` if `provider_symbol` is unknown to the provider

**`fetch_eod_bars_batch(provider_symbols: Sequence[str], start_date: date, end_date: date) -> ProviderBatchResult[ProviderEODBarDTO]`**
Batch variant for multiple ETFs over a date range.
- Returns: a `ProviderBatchResult` envelope:
  - `successes: dict[str, list[ProviderEODBarDTO]]` — `provider_symbol` → rows
  - `failures: dict[str, ProviderError]` — `provider_symbol` → structured exception
- **Per-symbol errors are collected, not raised** — a single-symbol failure does not abort the batch.
- Raises systemic errors that affect the whole batch only:
  - `ProviderTransportError`, `ProviderAuthError`, `ProviderRateLimitError` on whole-batch failure
  - `ProviderValidationError` on invalid date inputs

**`fetch_corporate_actions(provider_symbol: str, start_date: date, end_date: date) -> Iterable[ProviderCorporateActionDTO]`**
Fetches corporate actions for one ETF over an inclusive date range.
- Returns: an iterable of `ProviderCorporateActionDTO`. **An empty iterable is normal** (no actions in range).
- Raises: same as `fetch_eod_bars`.

**`fetch_etf_metadata(provider_symbol: str) -> ProviderEtfMetadataDTO`**
Fetches identity metadata for one ETF.
- Returns: a `ProviderEtfMetadataDTO`.
- Raises:
  - `ProviderTransportError`, `ProviderAuthError`, `ProviderRateLimitError`, `ProviderParseError`, `ProviderValidationError` as documented above
  - `ProviderDataNotAvailableError` if `provider_symbol` is unknown

#### Behavior contracts

- All methods are stateless and idempotent given the same parameters.
- "No data found" for date-range queries returns an empty iterable; "symbol unknown" raises `ProviderDataNotAvailableError`. Ingestion distinguishes these cases when emitting DQ exceptions.
- The EODHD adapter handles pagination internally for `fetch_eod_bars` and `fetch_corporate_actions`; callers see the assembled iterable, not pages.
- The EODHD adapter handles retry-on-rate-limit internally with bounded exponential backoff and jitter; on attempt-budget exhaustion it raises `ProviderRateLimitError`. Auto-retry of failed API calls is allowed per SDR Decision 11.
- Batch methods do not raise per-symbol errors; they collect them. Ingestion converts collected per-symbol errors into per-symbol fail-severity DQ exceptions while persisting the symbols that succeeded (chunk-level atomicity; see *Ingestion transaction model*).
- Every DTO returned carries `provider_name`, `provider_symbol`, `as_of_date` (where applicable), `pulled_at_utc`, and `provider_run_id`. `provider_run_id` is unique per provider call.

#### What the interface deliberately does not do

- It does not write to Postgres (Section 1 invariant 1).
- It does not read or accept Postgres state.
- It does not implement business logic about which symbols to fetch — ingestion supplies symbols from `config/universe.yaml`.

### Provider DTO contracts (Pydantic v2)

**Common fields on every DTO** returned by `providers/`:

| Field | Type | Notes |
|---|---|---|
| `provider_name` | `str` | e.g., `"eodhd"` |
| `provider_symbol` | `str` | provider's symbol for the ETF |
| `pulled_at_utc` | `datetime` | UTC timestamp the provider call completed |
| `provider_run_id` | `str (UUID)` | identifies the provider call |

Note: `as_of_date` is **not** a common field as of v0.3. It is declared per DTO that uses it. `ProviderEODBarDTO` carries `as_of_date` (the trading date the row represents). `ProviderCorporateActionDTO` carries explicit corporate-action date fields (`ex_date`, `record_date`, `pay_date`) instead. `ProviderEtfMetadataDTO` carries no as-of-date — metadata is identity-level; retrieval timing is `pulled_at_utc` only.

**`ProviderEODBarDTO`** — one DTO per ETF per trading day:

| Field | Type | Required | Notes |
|---|---|---|---|
| (common fields) | | | |
| `as_of_date` | `date` | required | trading date the row represents |
| `raw_open` | `Decimal \| None` | optional | raw/unadjusted; for audit only |
| `raw_high` | `Decimal \| None` | optional | for audit only |
| `raw_low` | `Decimal \| None` | optional | for audit only |
| `raw_close` | `Decimal \| None` | optional | for audit only |
| `volume` | `int \| None` | optional | |
| `adjusted_close` | `Decimal` | required | canonical research price |
| `currency` | `str \| None` | optional | |
| `exchange` | `str \| None` | optional | |

**`ProviderCorporateActionDTO`**:

| Field | Type | Required | Notes |
|---|---|---|---|
| (common fields) | | | |
| `action_type` | `Literal["split","dividend","spinoff","rights_issue"]` | required | |
| `factor` | `Decimal \| None` | one of `factor` or `amount` required | split ratio |
| `amount` | `Decimal \| None` | one of `factor` or `amount` required | cash amount for dividends |
| `currency` | `str \| None` | for dividends | |
| `ex_date` | `date` | required | |
| `record_date` | `date \| None` | optional | |
| `pay_date` | `date \| None` | optional | |

**`ProviderEtfMetadataDTO`** — identity-level only, *not* fundamentals:

| Field | Type | Notes |
|---|---|---|
| (common fields) | | |
| `name` | `str` | |
| `inception_date` | `date \| None` | per SDR Decision 4 |
| `first_traded_date` | `date \| None` | per SDR Decision 4 |
| `currency` | `str` | |
| `exchange` | `str` | |
| `country` | `str` | Phase 1: US-listed only per SDR Decision 1 |
| `isin` | `str \| None` | |

This DTO does not include ETF holdings, fundamentals, news, earnings, or options data — all explicitly out of Phase 1 per SDR Decision 1. It also carries no `as_of_date`; metadata is identity-level and retrieval timing is captured by `pulled_at_utc`.

### Provider error contract

Structured exceptions returned by `providers/`:

- `ProviderTransportError` — network or HTTP-level failure; transient.
- `ProviderAuthError` — credential or authorization failure; non-transient until refreshed.
- `ProviderRateLimitError` — quota exhausted; carries a retry-after hint.
- `ProviderParseError` — response could not be parsed into a DTO.
- `ProviderValidationError` — DTO failed Pydantic validation, or input arguments invalid.
- `ProviderDataNotAvailableError` — symbol unknown to the provider.

Ingestion converts each to a data-quality exception with appropriate severity.

### EODHD endpoint scope (Phase 1)

Phase 1 uses the following EODHD endpoint categories:

- **EOD historical price** — daily OHLCV plus adjusted close. Source for `ProviderEODBarDTO`.
- **Splits and dividends / corporate actions** — source for `ProviderCorporateActionDTO`.
- **ETF identity metadata** — name, inception/first-traded date, currency, exchange, country, ISIN. Source for `ProviderEtfMetadataDTO`. The "fundamentals" categories EODHD also offers are out of Phase 1 scope per SDR Decision 1 and are not used.

The EODHD adapter handles pagination via the provider's documented page/limit parameters and respects rate limits via exponential backoff with jitter on `429` responses; on quota exhaustion it raises `ProviderRateLimitError`. Authentication is API-key via injected environment variable.

### Application database — schema layout

Three schemas in Phase 1: `universe`, `prices`, `ops`. The remaining schemas (`features`, `targets`, `models`, `backtest`, `attribution`, `portfolio`, `paper`, `order_intent`) are reserved for later sections.

**Effective-date semantics on history tables.** All effective-dated tables in Section 2 (`universe.etf_provider_mapping`, `universe.etf_ticker_history`, `universe.etf_eligibility_history`) use **half-open ranges**:

- `effective_start_date` is **inclusive** — the state takes effect on this date.
- `effective_end_date` is **exclusive** — the state is no longer in effect on this date; the next state's `effective_start_date` equals the prior state's `effective_end_date`.
- `effective_end_date IS NULL` means **current/open-ended** — the state is in effect through "infinity".

EXCLUDE constraints on these tables are constructed as `daterange(effective_start_date, COALESCE(effective_end_date, 'infinity'::date), '[)') WITH &&` to enforce this consistently. Adjacent ranges where one ends and the next begins on the same date do **not** overlap under half-open semantics. Migration `0001_initial_setup.sql` enables the `btree_gist` Postgres extension, which is required for these EXCLUDE constraints (gist indexing on scalar `text`/`bigint` columns alongside the daterange).

#### `universe.etfs` — surrogate-keyed identity table

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `etf_id` | `bigserial` | PK | surrogate key |
| `current_ticker` | `text` | not null | denormalized; authoritative source is `etf_ticker_history` |
| `isin` | `text` | unique where not null | |
| `name` | `text` | not null | |
| `sleeve_id` | `bigint` | not null, FK → `universe.sleeves` | per SDR Decision 5 |
| `category` | `text` | not null | per SDR Decision 5 |
| `primary_benchmark_id` | `bigint` | not null, FK → `universe.benchmarks` | per SDR Decision 5; every Phase 1 ETF must have a primary benchmark |
| `secondary_benchmark_id` | `bigint` | FK → `universe.benchmarks`, nullable | per SDR Decision 5 |
| `portfolio_role` | `text` | | per SDR Decision 5 |
| `rank_method` | `text` | not null | per SDR Decision 5; allowed values defined in Section 3 |
| `equity_rotation_eligible` | `boolean` | not null default `false` | per SDR Decision 5 |
| `diversifier_sleeve_eligible` | `boolean` | not null default `false` | per SDR Decision 5 |
| `inception_date` | `date` | nullable | per SDR Decision 4; once-set |
| `first_traded_date` | `date` | nullable | per SDR Decision 4; once-set |
| `eligible_start_date` | `date` | nullable | per SDR Decision 4; canonical for *eligibility-rules-computed earliest possible eligibility* |
| `active` | `boolean` | not null default `true` | denormalized from `delisted_date` |
| `delisted_date` | `date` | nullable | per SDR Decision 4; once-set |
| `replacement_etf_id` | `bigint` | FK → `universe.etfs`, nullable | per SDR Decision 4 |
| `cost_bucket` | `text` | nullable | reserved for SDR Decision 8 (Section 4) |
| `created_at` | `timestamptz` | not null default `now()` | |
| `updated_at` | `timestamptz` | not null default `now()` | |

**Canonical vs denormalized field semantics:**

- `eligible_start_date` is **canonical for "the earliest date the ETF could be rank-eligible per the eligibility rules"** — typically `first_traded_date + 2 years` per SDR Decision 3. It is computed once when the ETF is added to the universe; it does not change unless eligibility rules change (an Approver-approved process).
- `etf_eligibility_history` (below) is **canonical for the actual eligibility timeline** — when rank-eligibility was granted or revoked. The two are related but distinct: `eligible_start_date` is the floor; the history records the reality. Consistency rule: no row in `etf_eligibility_history` with `is_rank_eligible=true` may have `effective_start_date < etfs.eligible_start_date` for the same `etf_id`. Tested.
- `active` is **denormalized from `delisted_date`**: `active=true` iff `delisted_date IS NULL` or `delisted_date > current_date`. Maintained at update time; consistency rule tested.
- `inception_date`, `first_traded_date`, `delisted_date`, `replacement_etf_id` are **once-set canonical fields** on `etfs`. Not effective-dated history.
- `current_ticker` is **denormalized from `etf_ticker_history`**: equal to the ticker on the `etf_ticker_history` row whose `effective_end_date IS NULL` (the open-ended row). Maintained at update time.

#### `universe.etf_provider_mapping` — `etf_id` to provider symbols over time

| Column | Type | Constraints |
|---|---|---|
| `etf_id` | `bigint` | not null, FK |
| `provider_name` | `text` | not null |
| `provider_symbol` | `text` | not null |
| `effective_start_date` | `date` | not null |
| `effective_end_date` | `date` | nullable |
| | | PK (`etf_id`, `provider_name`, `effective_start_date`) |
| | | EXCLUDE constraint preventing overlapping date ranges per `(etf_id, provider_name)`; uses half-open ranges per *Effective-date semantics* above |

The EXCLUDE constraint is constructed as `EXCLUDE USING gist (etf_id WITH =, provider_name WITH =, daterange(effective_start_date, COALESCE(effective_end_date, 'infinity'::date), '[)') WITH &&)`. Tested.

Index on `(provider_name)` to support the EODHD purge filter.

#### `universe.etf_ticker_history` — ticker change history

| Column | Type | Constraints |
|---|---|---|
| `etf_id` | `bigint` | not null, FK |
| `ticker` | `text` | not null |
| `effective_start_date` | `date` | not null |
| `effective_end_date` | `date` | nullable |
| `change_reason` | `text` | nullable |
| | | PK (`etf_id`, `effective_start_date`) |
| | | EXCLUDE constraint preventing overlapping date ranges per `etf_id`; uses half-open ranges per *Effective-date semantics* above |

#### `universe.etf_eligibility_history` — append-only eligibility history (point-in-time foundation, canonical)

| Column | Type | Constraints |
|---|---|---|
| `etf_id` | `bigint` | not null, FK |
| `effective_start_date` | `date` | not null |
| `effective_end_date` | `date` | nullable (`null` = current) |
| `is_rank_eligible` | `boolean` | not null |
| `universe_layer` | `text` | not null, CHECK in (`'CoreTest'`, `'Candidate'`, `'FutureFullEligible'`) |
| `reason_code` | `text` | not null |
| `recorded_at` | `timestamptz` | not null default `now()` |
| `recorded_by` | `text` | not null |
| | | PK (`etf_id`, `effective_start_date`) |
| | | EXCLUDE constraint preventing overlapping date ranges per `etf_id`; uses half-open ranges per *Effective-date semantics* above |

Universe-membership "as of date X" is derived at query time via a SQL view over this table. Pre-materialization of daily snapshots is deferred until query performance demands it.

This table is canonical for the actual eligibility timeline (see *Canonical vs denormalized field semantics* above).

#### `universe.sleeves`

| Column | Type | Constraints |
|---|---|---|
| `sleeve_id` | `bigserial` | PK |
| `sleeve_code` | `text` | not null, unique |
| `display_name` | `text` | not null |
| `description` | `text` | |

Seeded via migration `0001_*` with: `BroadEquity`, `Sector`, `Thematic`, `BondTreasury`, `DiversifierHedge`, `REITRealAsset` (per SDR Decision 5).

#### `universe.benchmarks`

| Column | Type | Constraints |
|---|---|---|
| `benchmark_id` | `bigserial` | PK |
| `benchmark_code` | `text` | not null, unique |
| `display_name` | `text` | not null |
| `etf_id` | `bigint` | FK, nullable | when benchmark is an ETF |
| `index_symbol` | `text` | nullable | when benchmark is an index |
| `description` | `text` | |

#### `prices.etf_prices_daily` — canonical daily price table

| Column | Type | Constraints |
|---|---|---|
| `etf_id` | `bigint` | not null, FK |
| `as_of_date` | `date` | not null |
| `provider_name` | `text` | not null |
| `provider_symbol` | `text` | not null |
| `provider_run_id` | `text` | not null |
| `raw_open` | `numeric(18,6)` | nullable |
| `raw_high` | `numeric(18,6)` | nullable |
| `raw_low` | `numeric(18,6)` | nullable |
| `raw_close` | `numeric(18,6)` | nullable |
| `volume` | `bigint` | nullable |
| `adjusted_close` | `numeric(18,6)` | not null |
| `currency` | `text` | nullable |
| `ingestion_run_id` | `bigint` | not null, FK → `ops.ingestion_runs` |
| `pulled_at_utc` | `timestamptz` | not null |
| | | PK (`etf_id`, `as_of_date`, `provider_name`) |

Indexes: `(provider_name, as_of_date)` for the 30-day purge; `(etf_id, as_of_date)` for primary research queries.

`adjusted_close` is the canonical research price per the Approver-directed adjusted-price convention. The raw OHLCV columns are retained for audit, reconciliation, provider validation, display, and diagnostics only; their use in research calculations requires explicit Approver approval. `provider_run_id` enables tracing each row back to the specific provider call that produced it.

#### `prices.corporate_actions`

| Column | Type | Constraints |
|---|---|---|
| `corporate_action_id` | `bigserial` | PK |
| `etf_id` | `bigint` | not null, FK |
| `provider_name` | `text` | not null |
| `provider_symbol` | `text` | not null |
| `provider_run_id` | `text` | not null |
| `action_type` | `text` | not null, CHECK in (`'split'`, `'dividend'`, `'spinoff'`, `'rights_issue'`) |
| `factor` | `numeric(18,6)` | nullable |
| `amount` | `numeric(18,6)` | nullable |
| `currency` | `text` | nullable |
| `ex_date` | `date` | not null |
| `record_date` | `date` | nullable |
| `pay_date` | `date` | nullable |
| `ingestion_run_id` | `bigint` | not null, FK |
| `pulled_at_utc` | `timestamptz` | not null |

Index on `(provider_name)` for the 30-day purge.

**Natural-key uniqueness.** A unique index prevents duplicate corporate-action rows on re-pull:

```sql
CREATE UNIQUE INDEX idx_corporate_actions_natural_key
ON prices.corporate_actions (
  etf_id, provider_name, action_type, ex_date,
  COALESCE(factor, 0), COALESCE(amount, 0)
);
```

The DTO contract requires exactly one of `factor` or `amount` to be populated per action, so the COALESCE-based key is well-defined for every row. For action types where both are NULL (e.g., a spinoff without a numeric component), the key collapses to `(etf_id, provider_name, action_type, ex_date, 0, 0)`, which uniquely identifies one such event per ETF per ex-date — sufficient for Phase 1. A future provider-event-id-based unique constraint can be added by a later migration if a stable provider identifier becomes available.

#### `ops.ingestion_runs` — every ingestion attempt tracked

| Column | Type | Constraints |
|---|---|---|
| `ingestion_run_id` | `bigserial` | PK |
| `run_kind` | `text` | not null (e.g., `daily_eod`, `backfill`, `metadata_refresh`, `corporate_actions_refresh`) |
| `provider_name` | `text` | not null |
| `started_at_utc` | `timestamptz` | not null |
| `completed_at_utc` | `timestamptz` | nullable |
| `status` | `text` | not null, CHECK in (`'pending'`, `'succeeded'`, `'failed'`, `'partial'`) |
| `chunk_results` | `jsonb` | nullable | per-chunk outcomes (see below) |
| `rows_processed` | `bigint` | nullable |
| `rows_upserted` | `bigint` | nullable |
| `exceptions_raised` | `int` | nullable |
| `commit_hash` | `text` | nullable | code commit hash at run time, per EW Section 7 |
| `config_hash` | `text` | nullable | hash of `config/universe.yaml` at run time |
| `notes` | `text` | nullable |

`chunk_results` JSONB shape:

```json
{
  "successes": ["SPY", "QQQ", "GLD"],
  "failures": [
    {"provider_symbol": "XYZ", "error_code": "ProviderTransportError", "exception_id": 123},
    {"provider_symbol": "ABC", "error_code": "ProviderDataNotAvailableError", "exception_id": 124}
  ]
}
```

Section 3 and 4 read this column when they opt into per-symbol-aware partial handling.

#### `ops.data_quality_exceptions` — SDR Decision 11 nine-field exception report plus purge filtering

| Column | Type | Constraints | SDR Decision 11 field |
|---|---|---|---|
| `exception_id` | `bigserial` | PK | |
| `ingestion_run_id` | `bigint` | nullable, FK | (cross-ref) |
| `provider_name` | `text` | nullable | added in v0.2 for purge filtering; NULL when exception is not provider-sourced |
| `issue` | `text` | not null | issue |
| `explanation` | `text` | not null | plain-English explanation |
| `why_it_matters` | `text` | not null | why it matters |
| `likely_cause` | `text` | not null | likely cause |
| `severity` | `text` | not null, CHECK in (`'warning'`, `'fail'`) | severity |
| `suggested_resolution` | `text` | not null | suggested resolution |
| `auto_resolution_allowed` | `boolean` | not null | whether agent auto-resolution is allowed |
| `auto_resolution_action` | `text` | nullable | what was auto-resolved |
| `approver_required` | `boolean` | not null | whether Approver must approve |
| `approver_action` | `text` | nullable | what Approver must approve (description) |
| `affected_scope` | `jsonb` | nullable | structured ref to affected ETFs/dates/runs |
| `created_at` | `timestamptz` | not null default `now()` | |
| `resolved_at` | `timestamptz` | nullable | |
| `resolution_notes` | `text` | nullable | |

There is no `'pass'` severity row — pass is the absence of an exception.

`provider_name` participates in the EODHD 30-day purge: rows where `provider_name='eodhd'` are deleted by the purge routine. Rows where `provider_name IS NULL` (e.g., a config-validation failure or a schema-migration alarm) are not affected by the purge.

#### `ops.provider_raw_payloads` — raw provider responses for audit (with secrets stripped)

| Column | Type | Constraints |
|---|---|---|
| `payload_id` | `bigserial` | PK |
| `ingestion_run_id` | `bigint` | not null, FK |
| `provider_name` | `text` | not null |
| `provider_run_id` | `text` | not null |
| `provider_symbol` | `text` | nullable |
| `as_of_date` | `date` | nullable |
| `endpoint` | `text` | not null |
| `response_payload` | `jsonb` | not null |
| `pulled_at_utc` | `timestamptz` | not null |

Index on `(provider_name)` for the 30-day purge.

The provider adapter strips secrets before persistence (see *Secrets redaction (raw payloads and DQ exceptions)* below).

#### `ops.data_snapshots` — pinned data sets for reproducibility

| Column | Type | Constraints |
|---|---|---|
| `data_snapshot_id` | `bigserial` | PK |
| `snapshot_label` | `text` | not null, unique |
| `created_at_utc` | `timestamptz` | not null default `now()` |
| `created_by` | `text` | not null |
| `description` | `text` | nullable |
| `as_of_date` | `date` | not null |
| `provider_name` | `text` | not null |
| `provider_dataset_label` | `text` | not null |
| `commit_hash` | `text` | not null |
| `config_hash` | `text` | not null |
| `universe_config_hash` | `text` | not null |
| `universe_version_label` | `text` | not null |
| `adjusted_price_convention` | `text` | not null |
| `price_table_max_as_of_date` | `date` | not null |
| `ingestion_run_ids` | `bigint[]` | not null |
| `status` | `text` | not null, CHECK in (`'active'`, `'invalidated'`), default `'active'` |
| `invalidated_at_utc` | `timestamptz` | nullable |
| `invalidation_reason` | `text` | nullable |

Field semantics (additions in v0.3 emphasized):

- `commit_hash` — code commit at snapshot creation.
- `config_hash` — hash of all config files at snapshot creation (broad).
- **`provider_name`** — provider that sourced the snapshot's data; e.g., `"eodhd"`. Enables purge filtering and explicit auditability.
- **`provider_dataset_label`** — human-readable provider/dataset identifier; e.g., `"EODHD All World 2026-04-27"`. Distinguishes one provider's dataset version from another.
- **`universe_config_hash`** — hash of `config/universe.yaml` specifically. Pinpoints which universe configuration was active at snapshot time, even if other config files changed.
- **`universe_version_label`** — human-readable universe identifier; e.g., `"CoreTest_v1"`. Enables semantic referencing in research write-ups.
- **`adjusted_price_convention`** — identifier of the adjusted-price convention used; e.g., `"adjusted_close_canonical_v1"` per the Section 2 v0.2 Approver-approved convention. Future changes to the convention are versioned and a new label is issued.
- **`price_table_max_as_of_date`** — the latest `prices.etf_prices_daily.as_of_date` covered by this snapshot. Sets the upper boundary for any backtest or research run referencing the snapshot.
- `ingestion_run_ids` — array of ingestion runs included.
- `status`, `invalidated_at_utc`, `invalidation_reason` — see purge interaction below.

Sections 3 and 4 reference `data_snapshot_id` in MLflow runs and backtest records to satisfy the EW Section 7 reproducibility requirement (Code commit hash, Config commit hash, Data snapshot/version identifier, Data provider/source, Universe version, Adjusted-price convention used, MLflow run ID). The v0.3 columns above are the schema-level cash-out of those EW Section 7 line items.

The EODHD 30-day purge marks affected snapshots `'invalidated'` with an `invalidation_reason`; it does not delete the snapshot rows (audit retention). Subsequent attempts to use an invalidated snapshot raise a clear error.

#### `ops.schema_migrations` — applied migrations record

| Column | Type | Constraints |
|---|---|---|
| `migration_id` | `text` | PK (the migration filename) |
| `applied_at_utc` | `timestamptz` | not null default `now()` |
| `applied_by` | `text` | not null |
| `forward_checksum` | `text` | not null |
| `reverse_filename` | `text` | nullable |

### Ingestion transaction model and partial-run semantics

**The atomic write unit is the *chunk*.** For daily EOD ingestion, a chunk is one provider-symbol pull (the price rows for one ETF over the requested date range). For corporate-actions and metadata refreshes, a chunk is similarly per-symbol. For backfills covering multiple date ranges per symbol, ingestion may further sub-chunk per (symbol, date-window) pair; the choice of sub-chunking is an implementation detail of the ingestion run kind.

**Within a chunk, writes are transactional.** All Postgres writes for a given chunk — `prices.etf_prices_daily` rows, `prices.corporate_actions` rows, the `ops.provider_raw_payloads` row, any per-chunk DQ exception — happen inside one Postgres transaction. If any write in the chunk fails, the entire chunk rolls back. There is no half-written chunk state visible to readers.

**Across chunks, writes are independent.** A run with 50 chunks may end in three terminal statuses:

- **`succeeded`** — all 50 chunks committed.
- **`partial`** — at least one chunk committed and at least one chunk failed. The committed chunks are persisted; the failed chunks rolled back; per-failed-chunk fail-severity DQ exceptions are emitted.
- **`failed`** — no chunks committed (typically because of a systemic error like provider auth failure that prevented every chunk from running).

`ops.ingestion_runs.chunk_results` records per-chunk outcomes for `partial` and `succeeded` runs.

**Downstream blocking behavior.** Section 2's default is conservative: downstream compute (features, targets, model runs, backtests, portfolio) blocks on `failed` runs and on `partial` runs. Sections 3 and 4 may opt into per-symbol-aware partial handling at their own scope (reading `chunk_results` to identify which symbols are usable); they may not silently accept a `failed` run.

### Contract between `ingestion/` and the data-quality framework

**Severity model (three levels):**

- **`pass`** — no exception emitted; the chunk completes normally.
- **`warning`** — exception emitted but does not block downstream compute. Auto-resolution allowed for the four mechanical issues SDR Decision 11 names: retried API calls; exact duplicate row removal; mark-not-yet-eligible due to insufficient history; re-pull of affected date ranges.
- **`fail`** — exception emitted; downstream compute blocks until resolved.

**Forbidden auto-resolutions per SDR Decision 11**, enforced at framework level:

1. Silent benchmark changes
2. ETF replacements
3. Historical price modifications
4. Provider switches

The framework rejects any auto-resolution attempt in these classes; each is a separate test case.

`ingestion/` is the only emitter of `ops.data_quality_exceptions` rows in Phase 1. Sections 3 and 4 may add data-quality emitters of their own; they will write to the same table.

### Migration file conventions (application-database schema only)

- Migrations are pairs of plain SQL files: `migrations/forward/0001_short_description.sql` and `migrations/reverse/0001_short_description.sql`.
- Each migration runs inside a single Postgres transaction managed by the runner. **The migration runner must not contain `CREATE DATABASE`, `CREATE ROLE`, or other commands Postgres forbids inside transactions.** Database/role bootstrap is separate (see below).
- A thin Python runner under `common/db_migrations.py` reads ordered files, applies each in a transaction, and records the application in `ops.schema_migrations`.
- The runner refuses to apply out-of-order migrations.
- Rollback applies the matching reverse file and removes the row from `ops.schema_migrations`.
- Fixtures under `tests/fixtures/` are updated whenever a migration changes the shape of a table referenced by tests, per EW Section 10 item 21.
- The first migration (`0001_initial_setup.sql`) enables the `btree_gist` Postgres extension (required by the EXCLUDE constraints on effective-dated tables; see *Effective-date semantics on history tables* under *Application database — schema layout*), creates the application schemas (`universe`, `prices`, `ops`), seeds `universe.sleeves`, and creates the foundational tables — but does not create databases or roles.

### Database / role bootstrap (separate from application migrations)

Database and role creation occurs in plain SQL files under `scripts/postgres-init/`. These files are mounted into the Postgres container's `/docker-entrypoint-initdb.d/` directory via `docker-compose.yml`. Postgres runs them once on first-init, before the migration runner ever executes.

Phase 1 bootstrap files:

- `scripts/postgres-init/01_create_app_database.sql` — creates the application database if not already created by the Postgres image's defaults.
- `scripts/postgres-init/02_create_mlflow_database.sql` — creates the `mlflow` database, the `mlflow` Postgres role, and grants. The `app` role does not have privileges on the `mlflow` database; the `mlflow` role does not have privileges on the application database.
- `scripts/postgres-init/03_grants.sql` — additional role grants required for the Phase 1 stack.

These bootstrap files are versioned project artifacts subject to Approver review per EW Section 7 (database schema migrations) and the Approval Matrix (Section 2.3). They are not part of the application migration history; their effect is captured by the existence of the databases and roles, not by a row in `ops.schema_migrations`.

### Application-container entrypoint contract

Per Approver direction, the application container's entrypoint is a **simple, explicit process supervisor** that:

1. Starts the cron daemon as a foreground-managed process, with the project crontab loaded.
2. Starts the Dash app as a foreground-managed process, listening on its configured port.
3. Routes both processes' `stdout`/`stderr` to container `stdout`/`stderr` (per Section 1 Approver-resolved default on container logging).
4. Reports container health to Docker via a health check that confirms (a) the supervisor is running, (b) Dash responds on its port, and (c) the cron daemon is active.

A failure of either Dash or cron causes the supervisor to attempt restart per a configured policy; if restart fails repeatedly, the container's health check fails. This satisfies the Section 1 contract that "a healthy Dash signal must not mask a failed cron."

The specific tool is `supervisord` (Implementation default within the Approver-resolved category-level decision).

### MLflow metadata database (Postgres-level)

Section 2 owns only the Postgres-level setup:

- The `mlflow` database, `mlflow` role, and grants are created by `scripts/postgres-init/02_create_mlflow_database.sql` on Postgres first-init. **Not** by the application migration runner.
- The application database role does not have privileges on the `mlflow` database, and vice versa.
- The MLflow tracking container connects with the `mlflow` role; the application container connects to the application database with its own role.
- MLflow's own internal schema inside the `mlflow` database is managed by MLflow itself.

Section 3 owns MLflow client-side integration on the writer side.

### Secrets redaction (raw payloads and DQ exceptions)

A single `common.redact_secrets()` utility handles redaction across both `ops.provider_raw_payloads` and `ops.data_quality_exceptions`. It strips the following:

- HTTP `Authorization` headers
- All request headers (the adapter persists only response data, not request data)
- Query parameters whose names match credential patterns: `api_key`, `apikey`, `token`, `access_token`, `secret`, `auth`
- URL components matching tokenized patterns (long alphanumeric strings in path positions known to carry tokens)

**Raw payloads.** Provider adapters strip the above from raw payloads **before** persisting them to `ops.provider_raw_payloads`. The persisted payload is the response body plus a small set of safe response headers (`Content-Type`, `Date`, `Last-Modified`). Request URLs are stored only as a method+endpoint label (e.g., `"GET /eod/SPY.US"`), not as full URLs with query strings.

**DQ exceptions (added v0.3).** All text and JSON fields written to `ops.data_quality_exceptions` — `issue`, `explanation`, `why_it_matters`, `likely_cause`, `suggested_resolution`, `auto_resolution_action`, `approver_action`, `affected_scope`, `resolution_notes` — pass through `common.redact_secrets()` before persistence. This is necessary because exception messages frequently quote response fragments, URLs, and stack traces while explaining what went wrong; without the same redaction, secrets could leak into the DQ audit trail through the back door. The redaction discipline is thus uniform across both persistence paths, not just raw payloads.

Both behaviors are strict guarantees enforced by unit tests: a synthetic provider call whose URL contains `?api_token=ABCDEFG` produces a payload row containing neither `ABCDEFG` nor any credential pattern, and a synthetic DQ exception whose `explanation` quotes a URL with `?api_token=ABCDEFG` produces a row whose `explanation` contains neither. See *Required tests*.

### Current-survivor disclosure label

Per SDR Decision 4, early Phase 1 results must be labeled with a disclosure such as "Core Test Universe / current-survivor results. Useful for pipeline validation and directional learning, not statistical proof."

Section 2 establishes:

- The label string lives in `config/universe.yaml` under `disclosures.current_survivor_label`. Validated as a non-empty string at app startup.
- A `common/` retrieval function `get_current_survivor_label() -> str` returns the configured string.
- Applicability (when to surface the label) and surfacing (how to display it) are Sections 4 and 6 concerns. Section 2 only establishes storage and retrieval.

---

## Config dependencies

`config/universe.yaml` is the single config file Section 2 owns. Its v0.3 shape:

```yaml
universe_layers:
  - name: CoreTest
    description: ~40-75 manually selected ETFs for pipeline validation per SDR Decision 3
  - name: Candidate
    description: ~150-300 liquid non-leveraged US ETFs for serious ranking per SDR Decision 3
  - name: FutureFullEligible
    description: broader ETF universe filtered by eligibility rules per SDR Decision 3

eligibility_rules:
  min_history_years: 2                     # per SDR Decision 3
  min_avg_daily_dollar_volume_usd: 25000000  # Proposed default requiring Approver approval; $25M USD
  exclude_leveraged: true                  # per SDR Decision 3
  exclude_inverse: true                    # per SDR Decision 3
  require_us_listing: true                 # per SDR Decision 1
  require_adjusted_close: true             # per SDR Decision 2

data_freshness:
  stale_warning_business_days: 5           # Proposed default requiring Approver approval
  stale_fail_business_days: 10             # Proposed default requiring Approver approval

disclosures:
  current_survivor_label: |
    Core Test Universe / current-survivor results. Useful for pipeline validation
    and directional learning, not statistical proof.

sleeves:
  - code: BroadEquity
    display_name: Broad Equity ETFs
    description: per SDR Decision 5 sleeve 1
  - code: Sector
    display_name: Sector ETFs
    description: per SDR Decision 5 sleeve 2
  - code: Thematic
    display_name: Thematic ETFs
    description: per SDR Decision 5 sleeve 3
  - code: BondTreasury
    display_name: Bond / Treasury ETFs
    description: per SDR Decision 5 sleeve 4
  - code: DiversifierHedge
    display_name: Diversifier / Hedge ETFs
    description: per SDR Decision 5 sleeve 5
  - code: REITRealAsset
    display_name: REIT / Real Asset ETFs
    description: per SDR Decision 5 sleeve 6

benchmarks:
  - code: SPY
    display_name: SPDR S&P 500 ETF Trust
    etf_ticker: SPY
    description: ...
  - code: QQQ
    display_name: Invesco QQQ Trust
    etf_ticker: QQQ
    description: ...
  # ... additional benchmarks

etfs:
  - ticker: SPY
    layer: CoreTest
    sleeve: BroadEquity
    category: BroadMarket
    primary_benchmark: SPY
    secondary_benchmark: VTI
    portfolio_role: core
    rank_method: pending_section_3        # required string; Section 2 validates presence and type only. Section 3 must replace this sentinel with an allowed rank_method value before ranking or model implementation.
    equity_rotation_eligible: true
    diversifier_sleeve_eligible: false
  - ticker: GLD
    layer: CoreTest
    sleeve: DiversifierHedge
    category: PreciousMetal
    primary_benchmark: GLD
    secondary_benchmark: ~
    portfolio_role: diversifier
    rank_method: pending_section_3
    equity_rotation_eligible: false
    diversifier_sleeve_eligible: true
  # ... full Core Test list
```

**Validations applied at app startup** (any failure prevents startup):

- `universe_layers` contains exactly the three names: `CoreTest`, `Candidate`, `FutureFullEligible`.
- `eligibility_rules` contains all required keys; `min_avg_daily_dollar_volume_usd` is a positive number; `min_history_years` is a positive integer.
- `data_freshness` contains both keys; both are positive integers; `stale_warning_business_days < stale_fail_business_days`.
- `disclosures.current_survivor_label` is a non-empty string.
- `sleeves` contains the six SDR Decision 5 codes.
- Every ETF references a `sleeve` that exists in the `sleeves` block.
- Every ETF references a `primary_benchmark` that exists in the `benchmarks` block.
- `secondary_benchmark`, if present, exists in the `benchmarks` block.
- Every ETF's `layer` is one of the three defined layers.
- Every ETF carries a non-empty `rank_method` string. Allowed values and semantics are defined in Section 3; Section 2 validates presence and type only. The Phase 1 sentinel `pending_section_3` is acceptable to Section 2 validation but must be replaced by Section 3 before any ranking or model implementation reads from this field.

### Environment variables (`.env`)

Section 2 introduces the following variables. Each is added to `.env.example` with a placeholder value at the same merge per Section 1 test 8 (`.env.example` parity).

**Application database:**

- `APP_DB_HOST`
- `APP_DB_PORT`
- `APP_DB_NAME`
- `APP_DB_USER`
- `APP_DB_PASSWORD`

**MLflow metadata database:**

- `MLFLOW_DB_HOST`
- `MLFLOW_DB_PORT`
- `MLFLOW_DB_NAME`
- `MLFLOW_DB_USER`
- `MLFLOW_DB_PASSWORD`

**MLflow tracking server (URI used by application code):**

- `MLFLOW_TRACKING_URI`

**EODHD provider:**

- `EODHD_API_KEY`
- `EODHD_API_BASE_URL`

The Postgres host is reachable on the internal Docker network; `APP_DB_HOST` and `MLFLOW_DB_HOST` will resolve to the `postgres` Compose service name. Section 2 does not own `docker-compose.yml`; the relevant `env_file:` / `environment:` wiring is in Section 1's deployment file inventory.

Section 2 does not own the contents of any other YAML file. Sections 3-5 own the remaining `config/*.yaml` files per Section 1.

---

## Required tests

Tests are organized by area. All tests must pass both locally and inside the application container per EW Section 5.

### Provider interface tests (`providers/`, `providers/eodhd/`)

- Each interface method conforms to its declared signature: returns the specified type or raises one of the specified exceptions on the specified inputs.
- DTO normalization tests: known fixture input → known DTO output, with `provider_name='eodhd'`, `provider_symbol`, and `provider_run_id` populated on every DTO.
- Pagination: multi-page fixture response → all pages assembled into the iterable.
- Rate-limit handling: simulated `429` → backoff and retry; exhaustion → `ProviderRateLimitError`.
- Auth failure: simulated `401` → `ProviderAuthError`.
- Malformed payload: garbage bytes → `ProviderParseError`.
- DTO validation: invalid field combinations (e.g., `adjusted_close` missing) → `ProviderValidationError`.
- Empty result for date-range query: provider responds successfully with no rows → empty iterable, *not* an exception.
- Symbol unknown to provider → `ProviderDataNotAvailableError`.
- Invalid date inputs (`start_date > end_date`, malformed dates) → `ProviderValidationError`.
- `ProviderBatchResult` shape: per-symbol failures collected in `failures`, per-symbol successes in `successes`; no per-symbol failure raises.
- Systemic failure inside a batch (auth, rate limit) → batch raises the systemic exception; `successes` and `failures` are not returned.

### Ingestion tests (`ingestion/`)

- **Idempotency**: re-running the same ingestion with the same fixture converges to the same DB state.
- **Chunk-level atomicity**: a chunk that fails mid-write rolls back its own writes; chunks that already committed remain persisted; no half-written chunk state visible.
- **Partial-run status**: simulated batch where 47 of 50 symbols succeed and 3 fail → `ops.ingestion_runs.status='partial'`; `chunk_results` JSONB lists the 47 successes and the 3 failures with `error_code` and `exception_id`; per-failed-symbol fail-severity DQ exceptions emitted.
- **Failed-run status**: simulated systemic auth failure preventing every chunk → `status='failed'`; no rows persisted in prices or corporate actions.
- **Conflicting provider data on re-pull**: different `adjusted_close` for an existing `(etf_id, as_of_date, provider_name)` → fail-severity DQ exception, no silent overwrite.
- **Auto-resolution scope (allowed)**: framework auto-resolves the four allowed mechanical issues.
- **Auto-resolution scope (forbidden)**: framework rejects each of the four forbidden classes (silent benchmark changes, ETF replacements, historical price modifications, provider switches). One assertion per class.
- **Partial-run recovery**: simulated OOM-kill mid-run → re-run of the same `run_kind` completes correctly.
- **Ingestion-run row produced**: every run produces an `ops.ingestion_runs` row with `status`, `commit_hash`, and `config_hash`.
- **Downstream block-on-partial**: a downstream consumer reading from `ingestion_runs` treats `partial` as blocking by default.

### Data-quality framework tests

- All nine SDR Decision 11 fields populated on every emitted exception.
- Severity rules: warning vs. fail per the framework (table-driven).
- Forbidden auto-resolutions blocked at framework level (one assertion per forbidden class).
- Exception report renders human-readably.
- `provider_name` populated on provider-sourced exceptions; NULL on non-provider exceptions (e.g., config validation failure).

### EODHD 30-day deletion test

- Seed DB with rows where `provider_name='eodhd'` and rows where `provider_name='__test_other_provider'` across `prices.etf_prices_daily`, `prices.corporate_actions`, `ops.provider_raw_payloads`, `universe.etf_provider_mapping`, `ops.data_quality_exceptions`, and `ops.ingestion_runs`.
- Seed `ops.ingestion_runs` rows for both providers with non-trivial `chunk_results` JSONB and `notes` content that includes provider symbols and example provider response fragments.
- Seed `ops.data_snapshots` rows referencing some of the EODHD ingestion runs.
- Trigger the deletion routine.
- Assert: all `eodhd` rows in `prices.etf_prices_daily`, `prices.corporate_actions`, `ops.provider_raw_payloads`, `ops.data_quality_exceptions`, and `universe.etf_provider_mapping` are removed; `__test_other_provider` rows in those tables untouched.
- Assert: `eodhd` rows in `ops.ingestion_runs` are **not deleted**; `chunk_results` and `notes` columns on those rows are redacted (no provider symbols, no provider response content); `status`, `started_at_utc`, `completed_at_utc`, `commit_hash`, `config_hash`, `rows_processed`, `rows_upserted`, `exceptions_raised` are preserved verbatim.
- Assert: snapshots referencing affected ingestion runs transition to `status='invalidated'` with an `invalidation_reason`; the snapshot rows themselves remain (audit retention).
- Assert: `universe.etfs`, `universe.sleeves`, `universe.benchmarks`, `universe.etf_eligibility_history`, `universe.etf_ticker_history` are not affected.

### Schema migration tests (application-database scope)

- Apply `0001..N` forward → schema matches expected snapshot.
- Apply `N..0001` reverse → schema returns to empty.
- Out-of-order application refused.
- Fixture updates accompany schema-changing migrations.
- Migration runner rejects any forward file containing `CREATE DATABASE` or `CREATE ROLE` (which Postgres forbids inside transactions).

### Database/role bootstrap tests

- On Postgres first-init, `scripts/postgres-init/` files run once and create the `mlflow` database, the `mlflow` role, and the expected grants.
- Subsequent container restarts do not re-run the bootstrap files.
- The `app` role lacks privileges on the `mlflow` database; the `mlflow` role lacks privileges on the application database.

### No-overlap constraint tests (effective-dated tables)

All three tests use half-open range semantics: ranges where one ends and the next begins on the same date are **not** overlapping and must be accepted.

- Insert overlapping range into `universe.etf_provider_mapping` for the same `(etf_id, provider_name)` → constraint violation.
- Insert overlapping range into `universe.etf_ticker_history` for the same `etf_id` → constraint violation.
- Insert overlapping range into `universe.etf_eligibility_history` for the same `etf_id` → constraint violation.
- For each table, valid non-overlapping inserts succeed.
- For each table, an insert where `effective_start_date` equals the prior row's `effective_end_date` (adjacent ranges, no overlap under half-open semantics) succeeds.

### Corporate-actions natural-key tests (added v0.3)

- Insert a corporate-action row, then attempt to insert a second row with identical `(etf_id, provider_name, action_type, ex_date)` and identical `factor`/`amount` → unique-index violation.
- Insert two corporate-action rows for the same ETF and ex_date but different `action_type` (e.g., split and dividend on the same day) → both succeed.
- Insert two dividend rows for the same ETF and ex_date but different `amount` → both succeed.
- Insert two action rows with both `factor` and `amount` NULL on the same `(etf_id, provider_name, action_type, ex_date)` (e.g., two spinoff records) → second insert fails (COALESCE collapses to `(0, 0)`).

### Point-in-time reconstruction tests

- Given an `etf_eligibility_history` with multiple rows per ETF over time, a query "as of date X" returns the eligibility state in effect on X. By construction (no-overlap constraint), at most one row matches.
- ETF launched after backtest start: as-of query correctly excludes it from periods before its `eligible_start_date`.
- ETF delisted before backtest end: as-of query correctly excludes it from periods after its `delisted_date`.
- Universe-membership "as of X" view returns the correct `universe_layer` for each `etf_id` at date X.
- Ticker change: prices rows are joined via `etf_id`, not ticker; queries return correct results across the change.

### Canonical/denormalized field consistency tests

- For every ETF, no row in `etf_eligibility_history` with `is_rank_eligible=true` has `effective_start_date < etfs.eligible_start_date`. (Computed assertion across the table.)
- For every ETF, `etfs.active=true` iff `etfs.delisted_date IS NULL OR etfs.delisted_date > current_date`.
- For every ETF, `etfs.current_ticker` equals the ticker on the `etf_ticker_history` row whose `effective_end_date IS NULL`.

### Look-ahead and survivorship checks (data-layer level)

- No row in `prices.etf_prices_daily` for an ETF before its `first_traded_date`.
- No row in `etf_eligibility_history` flags `is_rank_eligible=true` before the ETF's `eligible_start_date` (covered by the consistency test above; restated for traceability against SDR Decision 16).
- The current-survivor disclosure label is retrievable via `common.get_current_survivor_label()` and is a non-empty string per `config/universe.yaml`. Semantic verification of when to show it is Section 4/6.

### Secrets redaction tests

**Raw payloads.** Synthetic provider call whose URL contains `?api_token=ABCDEFG` and `Authorization: Bearer XYZ` header → resulting `ops.provider_raw_payloads.response_payload` contains neither `ABCDEFG` nor `XYZ` nor any credential-pattern key. The endpoint label captures `GET /eod/SPY.US` (or equivalent) without query string.

**DQ exceptions (added v0.3).** Synthetic ingestion failure whose internal exception text includes a URL with `?api_token=ABCDEFG` and an `Authorization: Bearer XYZ` header fragment → resulting `ops.data_quality_exceptions` row, across all text and JSON fields (`issue`, `explanation`, `why_it_matters`, `likely_cause`, `suggested_resolution`, `auto_resolution_action`, `approver_action`, `affected_scope`, `resolution_notes`), contains neither `ABCDEFG` nor `XYZ` nor any credential-pattern key.

Both tests exercise `common.redact_secrets()` directly to confirm the same utility is reachable from both persistence paths.

### Data snapshot tests

- Creating a snapshot referencing existing successful ingestion runs records the expected row with `status='active'`, the run IDs, the `as_of_date`, and the `commit_hash` / `config_hash`.
- The v0.3 reproducibility fields are populated and non-null on creation: `provider_name`, `provider_dataset_label`, `universe_config_hash`, `universe_version_label`, `adjusted_price_convention`, `price_table_max_as_of_date`. Attempting to create a snapshot with any of these missing or empty raises a clear error.
- `price_table_max_as_of_date` matches the actual `MAX(as_of_date)` across `prices.etf_prices_daily` for the rows belonging to the included ingestion runs.
- Attempting to create a snapshot referencing a non-existent or non-succeeded ingestion run raises an error.
- After EODHD purge, snapshots referencing affected ingestion runs transition to `status='invalidated'`.
- Reading an `'invalidated'` snapshot for use in a new compute job raises a clear error.

### App container startup contract test

- `docker compose up -d` produces a healthy application container.
- Both Dash and cron are running.
- Killing Dash → container health check fails within a defined timeout.
- Killing cron → container health check fails within a defined timeout.
- Both processes' stdout/stderr reach Docker logs.

### `config/universe.yaml` validation tests

- Valid config loads.
- ETF referencing a nonexistent sleeve fails validation.
- ETF referencing a nonexistent benchmark fails validation.
- Missing required `eligibility_rules` key fails validation.
- `data_freshness.stale_warning_business_days >= stale_fail_business_days` fails validation.
- Empty `disclosures.current_survivor_label` fails validation.
- ETF missing `rank_method` fails validation.
- ETF with non-string `rank_method` fails validation.
- ETF with `rank_method: pending_section_3` (the v0.3 temporary sentinel) **passes** Section 2 validation. Section 3's eventual ranking module will be responsible for rejecting any unreplaced sentinel before reading the field for ranking.
- ETF missing `primary_benchmark` fails validation (corresponds to the NOT NULL constraint on `universe.etfs.primary_benchmark_id`).
- App refuses to start with malformed config.

### Trading-calendar tests

- Known US holiday: ingestion does not flag missing prices for any ETF.
- Known weekend: same.
- Known trading day with missing prices for a ranked-eligible ETF: emits fail-severity DQ exception.
- Known trading day with missing prices for a not-yet-eligible ETF: emits warning-severity DQ exception (auto-resolvable).

---

## Edge cases and failure behavior

1. **Provider unreachable.** Provider raises `ProviderTransportError`; ingestion converts to fail-severity DQ exception; ingestion run marked `failed`; downstream blocked. Auto-retry of failed API calls is allowed per SDR Decision 11; silent fallback to a different provider is forbidden.
2. **Partial pull at the chunk level.** A multi-symbol batch where 47 of 50 symbols succeed and 3 fail. Each symbol's pull is one chunk. Chunks for the 47 successful symbols commit transactionally; chunks for the 3 failed symbols roll back entirely (no half-written chunk state). Per-failed-symbol fail-severity DQ exceptions emitted. The ingestion run is marked `partial`; `chunk_results` JSONB records per-symbol outcomes. Downstream compute reading from this run blocks by default; Sections 3 and 4 may opt into per-symbol-aware partial handling at their own scope by reading `chunk_results`.
3. **Malformed provider response.** DTO validation fails → fail-severity DQ exception with the parse error, the response payload (truncated and redacted), and a suggested resolution.
4. **Duplicate rows in provider response.** Upsert resolves them (allowed auto-resolution); a warning DQ exception logged for traceability.
5. **Conflicting provider data on re-pull.** Different `adjusted_close` for existing `(etf_id, as_of_date, provider_name)` → fail-severity DQ exception requiring Approver review; no silent overwrite.
6. **Schema migration partial application.** Rollback runs; if rollback also fails, scheduled jobs stop and the failure surfaces as a deployment-level exception per Section 1 edge case 5. Migration runner errors on any file containing `CREATE DATABASE` or `CREATE ROLE`.
7. **EODHD subscription cancellation.** Manual or scheduled trigger of the purge routine within 30 days. The routine **deletes** rows where `provider_name='eodhd'` from `prices.etf_prices_daily`, `prices.corporate_actions`, `ops.provider_raw_payloads`, `ops.data_quality_exceptions`, and `universe.etf_provider_mapping`. For `ops.ingestion_runs` rows where `provider_name='eodhd'`, the routine **does not delete** the rows (they are operational audit metadata necessary for reproducibility traceability) but **redacts** the `chunk_results` JSONB and `notes` columns to remove any provider-derived content; `status`, timestamps, `commit_hash`, `config_hash`, `rows_processed`, `rows_upserted`, and `exceptions_raised` are preserved. Affected `ops.data_snapshots` rows are marked `'invalidated'` (also not deleted). Per SDR Decision 2.
8. **ETF delisting.** `delisted_date` set on `etfs`; `active` denormalized to `false`; new `etf_eligibility_history` row with `is_rank_eligible=false`; historical `prices.etf_prices_daily` rows preserved. The consistency tests catch any divergence.
9. **Ticker change.** New row in `etf_ticker_history` with the new ticker and `effective_start_date`; the prior row's `effective_end_date` is set; `current_ticker` on `etfs` updated; the no-overlap constraint prevents accidental simultaneous tickers.
10. **Benchmark missing for an ETF that needs it.** Fail-severity DQ exception. Benchmark changes are a forbidden auto-resolution per SDR Decision 11.
11. **Trading day with no prices for some ETFs.** Distinguished by the trading calendar: weekend/holiday (no exception); ranked-eligible ETF missing data (fail); not-yet-eligible ETF missing data (warning, auto-resolvable).
12. **`adjusted_close` outside reasonable range.** Negative; > 100x prior close without a corporate-action match in `prices.corporate_actions` → fail-severity DQ exception.
13. **App container starts but Dash never reaches healthy state.** Container health check fails; Docker `restart: unless-stopped` attempts restart per Section 1.
14. **Cron crashes after Dash is healthy.** Container health check transitions to unhealthy because the supervisor's per-process health includes cron, satisfying the Section 1 contract.
15. **MLflow metadata database does not exist on first startup.** App fails fast with a clear error referencing the bootstrap files (`scripts/postgres-init/02_create_mlflow_database.sql`).
16. **`config/universe.yaml` references an ETF that has no provider mapping.** Ingestion run for that ETF logs a warning DQ exception; the ETF is not silently dropped from rank eligibility.
17. **Data snapshot referenced after purge.** A backtest in Section 4 references `data_snapshot_id=K`. The EODHD subscription is cancelled and the purge runs, marking K `'invalidated'`. Subsequent attempts to reuse K raise a clear error referencing the snapshot label and the invalidation reason; the snapshot row remains for audit but is not usable for new compute.
18. **Bootstrap files altered after first init.** Postgres only runs `/docker-entrypoint-initdb.d/` on first init. Subsequent edits to `scripts/postgres-init/` files have no automatic effect; an Approver-approved migration or manual operation is required to apply changes to an already-initialized cluster, with rollback discipline equivalent to schema migrations.
19. **Effective-dated insert with an overlapping range.** Postgres `EXCLUDE` constraint using half-open ranges (`'[)'`) rejects the insert; ingestion converts to a fail-severity DQ exception. Adjacent ranges where one row ends and another begins on the same date do **not** overlap under half-open semantics and are accepted.

---

## Open questions

After Approver direction received pre-drafting on the adjusted-price convention and the entrypoint mechanism, and after the v0.2 revisions, no top-level open questions remain at draft stage. All non-derived choices are visible under *Explicit assumptions* below.

If implementation surfaces a new open question that Section 2 should resolve rather than leaving to a later section, the Builder pauses per EW Section 3.5 and escalates to the Approver before continuing.

---

## Explicit assumptions

Every choice in this section is classified per EW Section 3.3 as one of: Derived from SDR or EW, Derived from approved Section 1, Implementation default, Approver-resolved default, or Proposed default requiring Approver approval.

### Derived from SDR or EW

- Provider abstraction with no persistence in `providers/`. **SDR Decision 2.**
- `ingestion/` is the only persistence path for provider-sourced records. **SDR Decision 2 + EW.**
- All provider-sourced rows tagged with `provider_name`, `provider_symbol`, and `provider_run_id`. **SDR Decision 2.**
- Data-quality exception report has nine fields. **SDR Decision 11.**
- Allowed auto-resolutions limited to the four mechanical issues; forbidden auto-resolutions enforced at framework level. **SDR Decision 11.**
- ETF lifecycle fields per **SDR Decision 4**.
- Sleeve and benchmark fields per **SDR Decision 5**.
- Universe layered model and eligibility rules baseline per **SDR Decision 3**.
- 30-day purge filter on `provider_name='eodhd'` for raw and normalized rows, including data-quality exceptions. **SDR Decision 2.**
- Migrations under `migrations/` with rollback and fixture updates. **EW Section 7 + EW Section 10 items 19-22.**
- Backtest reproducibility metadata captured at ingestion-run level (`commit_hash`, `config_hash`) plus `ops.data_snapshots`. **EW Section 7.**
- Approver review required on database schema changes. **EW Section 2.3.**
- Tests must pass inside the application container. **EW Section 5.**
- Raw provider payloads exclude secrets. **Section 1 invariant 6 (no secrets in code/config/fixtures/logs/docs) extended to runtime artifacts; EW Section 9 secrets-in-diff check.**

### Derived from approved Section 1

- Two logical Postgres databases in one cluster (application DB + MLflow metadata DB). **Section 1 *Container-level shape*.**
- Application code reads YAML from `/app/config` mount and credentials from injected env vars. **Section 1 *Environment and config flow*.**
- `pathlib.Path` everywhere; no host-specific paths. **Section 1 invariant 5.**
- No secrets in code, config, fixtures, logs, docs. **Section 1 invariant 6.**
- Schema-level support for time-aware research auditability at the universe and ingestion level. **Section 1 invariant 7.**
- Application container hosts both Dash and cron. **Section 1 + EW Section 8.**
- Migration filename convention `0001_short_description.sql`. **Section 1 *Naming conventions*.**

### Implementation default (no strategy impact)

- Three Postgres schemas in Phase 1 — `universe`, `prices`, `ops` (within the Approver-approved Postgres-layout proposed default).
- Surrogate `bigserial` keys for primary tables; natural-key uniqueness via additional unique constraints.
- `numeric(18,6)` for monetary/price fields; `bigint` for volume; `date` for trading dates; `timestamptz` for UTC timestamps.
- `supervisord` as the specific process supervisor (within the Approver-resolved category-level decision).
- `pandas-market-calendars` (NYSE calendar) as the trading-calendar source.
- Postgres `EXCLUDE` constraints using `gist` indexing for no-overlap on effective-dated tables. (These are correctness-of-history constraints, not strategy choices; they could equally be enforced by triggers, but `EXCLUDE` is the canonical Postgres pattern.)
- Bootstrap mechanism: `scripts/postgres-init/` files mounted into Postgres `/docker-entrypoint-initdb.d/` (within the Approver-resolved separation of bootstrap from migrations).
- `chunk_results` as JSONB on `ops.ingestion_runs` rather than a separate `ops.ingestion_run_chunks` table. (Can be promoted to a table in a later section if query needs grow; storage and indexing on JSONB are sufficient for Phase 1.)
- The `mlflow` Postgres role and database are created with conventional Postgres role/grant SQL; specific role naming is conventional.

### Approver-resolved default (direction received pre-drafting)

- **Application-container entrypoint mechanism.** Simple, explicit process supervision so Dash and cron are deterministic and both surface failures via the container health check.
- **Database/role bootstrap separated from application migrations.** Direction received in v0.2 review: do not put `CREATE DATABASE` inside the transactional application migration runner; bootstrap is separate.
- **Adjusted-price convention.** Direction received pre-drafting and incorporated in v0.1; classified visibly as a Proposed default requiring Approver approval per Approver direction.

### Proposed default requiring Approver approval

**1. Migration tooling.** Plain SQL up/down files in `migrations/forward/` and `migrations/reverse/`, applied by `common/db_migrations.py`. No Alembic auto-generation. Migration runner does not handle bootstrap.

**2. Adjusted-price convention.** Direction received pre-drafting and incorporated. Store raw OHLCV where available, store adjusted close, treat adjusted close as canonical research price for returns/features/targets/rankings/excess-return/backtesting, retain raw for audit/reconciliation/diagnostics only, store corporate actions separately, retain provider tagging and purge eligibility on every record, require explicit Approver approval for any later use of unadjusted prices in research calculations.

**3. Postgres layout — schemas inside the application database.** Three schemas in Phase 1 (`universe`, `prices`, `ops`); additional schemas reserved for later sections.

**4. Provider DTO contract — Pydantic v2.** Architecturally consequential. Required tagging fields on every DTO: `provider_name`, `provider_symbol`, `pulled_at_utc`, `provider_run_id`. Date fields are DTO-specific: `ProviderEODBarDTO` carries `as_of_date`; `ProviderCorporateActionDTO` carries corporate-action date fields; `ProviderEtfMetadataDTO` carries no as-of-date.

**5. Raw provider payload storage.** In `ops.provider_raw_payloads`; provider tagging participates in 30-day purge; secrets stripped before persistence.

**6. Data freshness / SLA rules.** Now in `config/universe.yaml` under `data_freshness:`. Defaults: 5 business days warning, 10 business days fail. Downstream blocks on fail; UI can display prior data.

**7. Data-quality severity framework — `pass` / `warning` / `fail` model.** With the SDR Decision 11 nine-field exception report, framework-level enforcement of forbidden auto-resolutions, and the `provider_name` column on `data_quality_exceptions` for purge filtering.

**8. Ingestion idempotency and chunk-level atomicity.** Chunks are atomic; runs may end as `succeeded`, `partial`, or `failed`; downstream compute blocks on `partial` and `failed` by default; per-chunk results captured in `ops.ingestion_runs.chunk_results` JSONB.

**9. ETF identity and symbol mapping — surrogate key with effective-dated history tables.** Surrogate `etf_id` on `universe.etfs`; `etf_provider_mapping`, `etf_ticker_history`, `etf_eligibility_history` carry effective dates with no-overlap constraints. v0.3: ranges are **half-open** (`effective_start_date` inclusive, `effective_end_date` exclusive, NULL = current); EXCLUDE constraints use `daterange(..., '[)')` and require the `btree_gist` extension.

**10. Time-aware eligibility model.** Append-only `etf_eligibility_history` (canonical for actual eligibility timeline); `etfs.eligible_start_date` (canonical for eligibility-rules-computed earliest possible eligibility); consistency rule between them. As-of-date queries via SQL view; pre-materialization deferred until performance demands it.

**11. Trading calendar source — `pandas-market-calendars` (NYSE).** Borderline classification; treated as Implementation default (see above) but visible here in case the Approver wants to require an alternative.

**12. Data snapshot foundation.** `ops.data_snapshots` table; snapshots reference ingestion-run sets; EODHD purge invalidates rather than deletes; downstream sections (3 and 4) reference `data_snapshot_id` for reproducibility. v0.3 adds explicit reproducibility fields directly to the table: `provider_name`, `provider_dataset_label`, `universe_config_hash`, `universe_version_label`, `adjusted_price_convention`, `price_table_max_as_of_date`. These are the schema-level cash-out of the EW Section 7 reproducibility metadata list.

**13. Canonical/denormalized field semantics on `universe.etfs`.** `eligible_start_date`, `active`, `current_ticker` are denormalized convenience fields with explicit consistency rules tested at the schema level. `etf_eligibility_history` and `etf_ticker_history` are the authoritative history tables; `inception_date`, `first_traded_date`, `delisted_date`, `replacement_etf_id` are once-set canonical fields.

**14. `min_avg_daily_dollar_volume_usd` default of $25,000,000.** Per SDR Decision 3 ("passes minimum liquidity and average daily dollar volume filters") without specifying a number. **Rationale:** $25M ADV is conservative for "liquid US-listed ETF" and matches commonly accepted thresholds for institutional-grade ETF liquidity. Lower (e.g., $10M) would broaden the universe; higher (e.g., $50M) would shrink it. Configurable in `config/universe.yaml`.

**15. Stale-data threshold defaults of 5 / 10 business days.** Now in YAML; values unchanged from v0.1. **Rationale:** 5-day window absorbs typical provider outages; 10-day window catches sustained provider failure before research outputs degrade silently.

**16. Corporate-actions natural-key uniqueness (added v0.3).** Unique index on `(etf_id, provider_name, action_type, ex_date, COALESCE(factor, 0), COALESCE(amount, 0))` on `prices.corporate_actions`. **Rationale:** EODHD does not expose a stable corporate-action event ID in the endpoints Phase 1 uses; the natural key prevents duplicate rows on re-pull while remaining provider-agnostic. A future provider-event-id-based unique constraint can be layered in via a later migration if a stable identifier becomes available.

**17. Primary-benchmark NOT NULL constraint on `universe.etfs` (added v0.3).** Every Phase 1 ETF must have a primary benchmark assigned. **Rationale:** SDR Decision 5 makes benchmark assignment a defining property of an ETF in this platform; making it NOT NULL at the schema level prevents an entire class of "what's the benchmark for this ETF?" defects from leaking downstream into Section 3 ranking and Section 4 attribution. The trade-off is that adding an ETF that genuinely has no clear benchmark requires a deliberate `config/universe.yaml` choice (assign one of the existing benchmarks, or add a new benchmark first). For Phase 1 this trade-off is accepted.

---

## Section 2 → Sections 3-6 handoff

Section 2 leaves the platform with:

- A working provider abstraction interface (with explicit method signatures) and the EODHD implementation.
- Three populated Postgres schemas (`universe`, `prices`, `ops`) supporting point-in-time reconstruction.
- An application database and an isolated MLflow metadata database, both in the same Postgres cluster, **bootstrapped via `scripts/postgres-init/`** (separately from application migrations).
- A working data-quality framework with the SDR Decision 11 exception report and framework-level enforcement of allowed/forbidden auto-resolution classes.
- A working migrations infrastructure handling application-database schema only (not databases or roles).
- A tested EODHD 30-day purge mechanism that removes provider-sourced rows across five tables and invalidates affected `ops.data_snapshots` rows.
- A populated `config/universe.yaml` with the Core Test Universe, sleeves, benchmarks, eligibility rules, data-freshness thresholds, disclosure label, and per-ETF assignments.
- An application container that starts Dash and cron deterministically with both surfacing failures via the container health check.
- A foundation for chunk-level atomicity in ingestion and per-chunk traceability through `ops.ingestion_runs.chunk_results`.
- A foundation for reproducible data snapshots via `ops.data_snapshots`.

Section 2 does not write feature, target, model, backtest, portfolio, paper, order-intent, or UI tables; those are added by their owning sections via additional migrations:

- **Section 3 — Features/Targets/Models** — adds `features`, `targets`, `models` schemas. Reads from `prices.etf_prices_daily`, `universe.etfs`, `universe.etf_eligibility_history`. Owns MLflow client-side integration on the writer side. Owns the allowed values and semantics for `rank_method` referenced in `config/universe.yaml`. References `data_snapshot_id` from `ops.data_snapshots` in MLflow runs to satisfy EW Section 7 reproducibility.
- **Section 4 — Backtest/Attribution/Validation** — adds `backtest`, `attribution` schemas. References `data_snapshot_id` in backtest records. May opt into per-symbol-aware partial-scope handling by reading `ops.ingestion_runs.chunk_results`. Owns `regime/` consumption side.
- **Section 5 — Portfolio/Paper/Order Intent** — adds `portfolio`, `paper`, `order_intent` schemas. Reads from approved model rankings.
- **Section 6 — UI** — reads from the above via read-only access paths; selects the database-access enforcement mechanism for Section 1 invariant 3; surfaces the current-survivor disclosure label retrieved via `common.get_current_survivor_label()`.

A subsequent section that needs to expand or modify a Section 2 boundary — for example, a new auto-resolution class beyond the four allowed; a relaxation of the 30-day purge; a different price-storage convention; the use of unadjusted prices in research calculations; a relaxation of the conflicting-data fail-severity rule; a relaxation of the chunk-level atomicity contract; a relaxation of the canonical/denormalized field consistency rules — must propose the change as a Section 2 amendment and obtain Approver approval per EW Section 3.3 and Section 2.3.

---

**End of Section 2 v1.0 LOCKED / APPROVED.**
