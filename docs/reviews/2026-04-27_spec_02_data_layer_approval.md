# Engineering Specification Section 2 — Data Layer: Approval Note

**Section:** Engineering Specification — Section 2: Data Layer
**Section path:** `docs/engineering_spec/02_data_layer.md`
**Locked version:** v1.0 LOCKED / APPROVED
**Approval date:** 2026-04-27
**Approver:** Jeremy
**Builder:** Claude
**QA Reviewer status:** The section was iterated under direct Approver review across drafts v0.1 → v0.2 → v0.3, with each round producing an explicit revisions list (13 fixes for v0.2, 10 fixes for v0.3, plus one cleanup edit at locking). The Approver elected to lock at v1.0 on the basis of this iterative review rather than a separate ChatGPT QA pass on v0.3. The Approver's final review serves as the QA pass per EW Section 3.4 item 9.

**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification — Section 1 v1.0 LOCKED (`docs/engineering_spec/01_architecture_overview.md`)
- Section 1 approval note (`docs/reviews/2026-04-26_spec_01_architecture_overview_approval.md`)
- Section 2 traceability matrix updates (`docs/reviews/2026-04-27_spec_02_data_layer_traceability_updates.md`)
- `docs/traceability_matrix.md` (post-merge state)

---

## 1. What this approval covers

Approval of Section 2 v1.0 LOCKED locks the following at the data-layer level:

### 1.1 Provider abstraction interface and EODHD implementation

- The four-method provider abstraction (`fetch_eod_bars`, `fetch_eod_bars_batch`, `fetch_corporate_actions`, `fetch_etf_metadata`) with declared input/output types, structured-exception semantics, empty-iterable normal-case semantics for date-range queries, and `ProviderDataNotAvailableError` for unknown symbols.
- The `ProviderBatchResult` envelope shape: `successes` and `failures` keyed by `provider_symbol`; per-symbol failures collected, not raised; only systemic errors abort the batch.
- The Pydantic v2 DTO contracts: `ProviderEODBarDTO`, `ProviderCorporateActionDTO`, `ProviderEtfMetadataDTO`. Common tagging fields: `provider_name`, `provider_symbol`, `pulled_at_utc`, `provider_run_id`. Date fields are DTO-specific.
- The EODHD adapter scope: EOD historical price, splits/dividends/corporate actions, ETF identity metadata. Holdings, fundamentals, news, earnings, options data are out of scope per SDR Decision 1.

### 1.2 Postgres application database schema

- Three application schemas (`universe`, `prices`, `ops`) and the foundational tables they contain.
- `universe.etfs` lifecycle and assignment columns, with `primary_benchmark_id NOT NULL`, surrogate `etf_id` keys, and explicit canonical-vs-denormalized field semantics for `eligible_start_date`, `active`, `current_ticker`.
- The three effective-dated tables (`etf_provider_mapping`, `etf_ticker_history`, `etf_eligibility_history`) using **half-open range semantics** (`effective_start_date` inclusive, `effective_end_date` exclusive, NULL = current/open-ended), with EXCLUDE constraints constructed as `daterange(..., '[)')` and the `btree_gist` extension enabled in migration `0001`.
- `prices.etf_prices_daily` carrying both raw OHLCV and `adjusted_close`, with `adjusted_close` as the canonical research price.
- `prices.corporate_actions` with the natural-key unique index `(etf_id, provider_name, action_type, ex_date, COALESCE(factor, 0), COALESCE(amount, 0))`.
- `ops.ingestion_runs` with `chunk_results` JSONB recording per-symbol outcomes for `succeeded` and `partial` runs.
- `ops.data_quality_exceptions` with the SDR Decision 11 nine-field exception report plus a `provider_name` column for purge filtering.
- `ops.provider_raw_payloads` for audit, with secrets stripped before persistence.
- `ops.data_snapshots` with the six v0.3 reproducibility fields (`provider_name`, `provider_dataset_label`, `universe_config_hash`, `universe_version_label`, `adjusted_price_convention`, `price_table_max_as_of_date`) plus `data_snapshot_id` as the downstream reference for Sections 3 and 4.
- `ops.schema_migrations` for application-database migration tracking.

### 1.3 Operational and ingestion contracts

- **Chunk-level atomicity** as the ingestion transaction model: the chunk is the atomic write unit; runs end as `succeeded`, `partial`, or `failed`; downstream compute blocks on `failed` and (by default) `partial`.
- **Database/role bootstrap separated from application migrations**: bootstrap SQL files live under `scripts/postgres-init/` and are mounted into the Postgres container's `/docker-entrypoint-initdb.d/`. The application migration runner explicitly forbids `CREATE DATABASE` and `CREATE ROLE`.
- **EODHD 30-day deletion mechanism** covering `prices.etf_prices_daily`, `prices.corporate_actions`, `ops.provider_raw_payloads`, `ops.data_quality_exceptions`, `universe.etf_provider_mapping`. `ops.ingestion_runs` rows are not deleted (operational audit metadata), but `chunk_results` and `notes` columns are redacted on EODHD rows. Affected `ops.data_snapshots` are marked `'invalidated'`, not deleted.
- **Data quality framework** with the `pass`/`warning`/`fail` severity model, framework-level enforcement of the four forbidden auto-resolutions (silent benchmark changes, ETF replacements, historical price modifications, provider switches), and the four allowed mechanical auto-resolutions per SDR Decision 11.
- **Secrets redaction utility** (`common.redact_secrets()`) shared across raw payloads and data-quality exception fields; strips Authorization headers, all request headers, query parameters matching credential patterns, and tokenized URL components.
- **Application-container entrypoint mechanism** using `supervisord` to run Dash and cron deterministically, with both processes' stdout/stderr to container logs and the container health check covering both.

### 1.4 Configuration

- `config/universe.yaml` v0.3 shape, including the layered universe model, eligibility rules, sleeve and benchmark definitions, `data_freshness:` thresholds (5/10 business days), `disclosures.current_survivor_label`, and per-ETF assignments. The Phase 1 sentinel `rank_method: pending_section_3` is acceptable to Section 2 validation; Section 3 must replace these before reading the field.
- `.env` variables introduced by Section 2: `APP_DB_HOST/PORT/NAME/USER/PASSWORD`, `MLFLOW_DB_HOST/PORT/NAME/USER/PASSWORD`, `MLFLOW_TRACKING_URI`, `EODHD_API_KEY`, `EODHD_API_BASE_URL`, with `.env.example` parity per Section 1 test 8.

### 1.5 Approver-directed conventions and proposed defaults accepted

- **Adjusted-price convention** (Approver direction received pre-drafting v0.1, classified visibly as Proposed default and accepted at locking): store both raw OHLCV and adjusted close; adjusted close is canonical for returns/features/targets/rankings/excess-return/backtesting; raw retained for audit, reconciliation, provider validation, display, and diagnostics only; corporate actions stored separately; provider tagging and purge eligibility on every record; **explicit Approver approval required for any later use of unadjusted prices in research calculations**.
- **`min_avg_daily_dollar_volume_usd: 25000000`** as the eligibility default.
- **`stale_warning_business_days: 5` and `stale_fail_business_days: 10`** as the data-freshness thresholds.

---

## 2. Approval Matrix items satisfied (per EW Section 2.3)

The following Approval Matrix items are satisfied by this approval:

- **Engineering Specification section finalization** (per EW Section 3.4): all ten DoD criteria met; section committed to `docs/engineering_spec/`; QA review per Section 3.4 item 9 satisfied via Approver-direct iterative review across v0.1 → v0.2 → v0.3.
- **Database schema changes** (universe / prices / ops schemas, foundational tables, migrations infrastructure).
- **Strategy-affecting YAML config changes** (`config/universe.yaml` v0.3 shape and validations).
- **ETF universe membership and eligibility rules** at the schema and config level (Decision 3 schema, eligibility-rules block in YAML).
- **Benchmark and sleeve assignments** at the schema level (Decision 5 universe-side fields).

The following Approval Matrix items are **explicitly not** satisfied by this approval and remain pending later sections:

- Changes to financial calculations, feature/target/label definitions, model promotion gates — Section 3.
- Changes to risk rules, transaction cost assumptions, portfolio rules — Sections 4 and 5.
- Any broker / order-intent behavior, any code path enabling live trading — Section 5 and the project's Phase 1 closure.
- Deployment exposure changes — operational, not Section 2.

---

## 3. Traceability matrix updates merged

The following `docs/traceability_matrix.md` updates are applied as part of the Section 2 approval merge:

- **Replacement rows** for Decisions 2, 3, 4, 5, 11, and 16 per the companion file. Decisions 3, 4, and 5 transition from `pending` to `in spec` (Decision 5 noted "in spec (universe-side); pending (ranking math)"). Decisions 2, 11, and 16 are extended with Section 2's specific contributions.
- **Decision 10 label correction**: the SDR-Decision column for the existing Decision 10 row is corrected from "Configuration storage (YAML in git) and rebalance/review cadence" to "Portfolio Management and Risk Rules". All other cells in the Decision 10 row are unchanged; the row remains `pending` until Section 5 drafts its full replacement.

The `scripts/postgres-init/` directory is added to the matrix's project-artifacts cross-reference if such a cross-reference exists.

---

## 4. Conditions on subsequent sections

Section 2 v1.0 LOCKED imposes the following constraints on Sections 3, 4, 5, and 6. Any change to these requires a Section 2 amendment with Approver approval per EW Section 3.3 (no assumption drift) and EW Section 2.3 (Approval Matrix), not silent override:

1. **No new auto-resolution classes** beyond the four allowed by SDR Decision 11 may be added to the data-quality framework.
2. **The 30-day EODHD purge** may not be relaxed in scope or timing.
3. **The adjusted-price convention** is the canonical research price. Any use of unadjusted prices in research calculations requires explicit Approver approval and a new Section 2 amendment classification.
4. **The conflicting-provider-data fail-severity rule** stands: re-pulled rows that conflict with existing `(etf_id, as_of_date, provider_name)` rows must produce a fail-severity DQ exception, not a silent overwrite.
5. **The chunk-level atomicity contract** stands: ingestion writes within a chunk are transactional; `partial` runs are blocking by default; per-symbol-aware partial handling in Sections 3/4 reads `chunk_results` JSONB and may not silently accept a `failed` run.
6. **The canonical/denormalized field consistency rules** on `universe.etfs` (`eligible_start_date` vs `etf_eligibility_history`, `active` vs `delisted_date`, `current_ticker` vs `etf_ticker_history`) are enforced by tests; any new denormalized field must follow the same pattern.
7. **The half-open effective-date range semantics** on the three history tables stand. New effective-dated tables introduced by later sections follow the same convention.
8. **The secrets redaction utility** (`common.redact_secrets()`) is the only allowed path for persisting provider-derived text or JSON to either `ops.provider_raw_payloads` or `ops.data_quality_exceptions`.
9. **Section 3 must define allowed `rank_method` values** and replace every `pending_section_3` sentinel in `config/universe.yaml` before any ranking or model implementation reads from this field.
10. **Sections 3 and 4 must reference `data_snapshot_id`** in MLflow runs and backtest records, populating the v0.3 reproducibility fields, to satisfy the EW Section 7 reproducibility metadata list.

---

## 5. Forward references

- **Section 3** drafting may now begin under EW Section 3 discipline. Handoff packet preparation is the Approver's next action.
- The Section 2 → Sections 3-6 handoff at the end of `docs/engineering_spec/02_data_layer.md` enumerates the schemas, modules, and references each later section will extend or consume.

---

## 6. Approval

The Approver has reviewed Section 2 v1.0 LOCKED at `docs/engineering_spec/02_data_layer.md`, the companion traceability matrix updates at `docs/reviews/2026-04-27_spec_02_data_layer_traceability_updates.md`, and the post-merge state of `docs/traceability_matrix.md`, and approves the section as locked. Subsequent changes follow EW amendment discipline.

**Signed:** Jeremy (Approver), 2026-04-27.

---

**End of approval note.**
