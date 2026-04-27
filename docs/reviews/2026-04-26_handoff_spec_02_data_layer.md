Section 2 Handoff Prompt — Engineering Specification Section 2: Data Layer
Artifact type: Drafting handoff packet (Engineering Workflow Section 2.2)
Authorizes: Drafting of Engineering Specification Section 2 — Data Layer
Authorizes implementation: No. Spec drafting only.
Approver: Jeremy
Builder: Claude Code (in a fresh conversation)
QA Reviewer: ChatGPT (after Builder draft)
Storage path when used: docs/reviews/YYYY-MM-DD_handoff_spec_02_data_layer.md per EW Section 9 naming convention

Canonical project document manifest
The uploaded filenames in this chat may differ from the repository filenames. Treat the canonical repo paths below as authoritative. If an uploaded filename conflicts with a canonical path below, ignore the uploaded filename and use the canonical path for all references, traceability notes, and handoff language.
#DocumentCanonical repo path1Strategy Decision Record v1.0 LOCKED / APPROVEDdocs/strategy_decision_record.md2Engineering Workflow v1.5 LOCKEDdocs/engineering_workflow.md3Engineering Specification Section 1 v1.0 LOCKED / APPROVEDdocs/engineering_spec/01_architecture_overview.md4Traceability Matrix v0.2docs/traceability_matrix.md5Section 1 Approval Notedocs/reviews/2026-04-26_spec_01_architecture_overview_approval.md
When this prompt refers to "the SDR," it means document #1 above. "The EW" means #2. "Section 1" or "Section 1 v1.0" means #3. "The traceability matrix" or "the matrix" means #4. "The Section 1 approval note" means #5.

Task
Draft Engineering Specification Section 2 — Data Layer.
You are the Builder per the EW (Section 2.1). I am the Approver. ChatGPT will be the QA Reviewer for this section after you finish drafting.
This is a spec-drafting task, not an implementation task. The output is a single markdown file at docs/engineering_spec/02_data_layer.md (or, if a split is approved, the file pair noted under "Section size control" below). No code is written in this conversation.

Documents you must read before drafting
Read all five documents from the canonical manifest above, in this order:

The SDR — controlling strategy document. All decisions in this section must trace to specific SDR decisions or be flagged per EW Section 3.3.
The EW — process document governing how spec sections are drafted, reviewed, and finalized.
Section 1 v1.0 LOCKED — the approved architecture. Section 2 inherits its boundaries, invariants, and Approver-resolved defaults. Section 2 may not relax or contradict Section 1 without an Approver-approved Section 1 amendment.
The traceability matrix — partially populated. You will produce the matrix updates that should be merged in for the SDR decisions Section 2 implements.
The Section 1 approval note — process record for Section 1, including the "Open items handed forward to Section 2" list.

The EW takes precedence on process. The SDR takes precedence on strategy. Section 1 takes precedence on architecture. If they appear to conflict, stop and escalate to me before drafting.

Section scope
Section 2 is the data layer. It establishes how data enters the system, where it is stored, how it is verified, and how the system supports point-in-time reconstruction.
In scope for Section 2

The provider abstraction interface owned by providers/ — method signatures, error semantics, retry expectations, response normalization, and the shape of the provider-tagged DTOs returned to ingestion.
The EODHD provider implementation — what subset of EODHD endpoints Phase 1 uses, how pagination and rate-limiting are handled, how EODHD responses are normalized into DTOs, and how the EODHD-storage-tagging requirement (provider_name, provider_symbol) is satisfied at the DTO level.
The Postgres application database foundational schema — universe registry, ETF identity and lifecycle fields, eligibility windows, sleeve and benchmark assignments, prices (raw and adjusted as decided), ingestion-run metadata, data-quality exception records, and any other tables Section 2 needs as foundation for Sections 3–5 to extend.
The MLflow metadata database setup at the Postgres level — database creation, ownership, isolation from the application database. (MLflow client integration on the writer side belongs to Section 3.)
The data quality framework — exception report contents, severity rules, auto-resolution scope per SDR Decision 11.
Ingestion orchestration — how ingestion/ invokes providers/, validates DTOs, persists records in transactions, and emits data-quality exceptions.
Migrations infrastructure — migration tooling choice, migration file conventions, rollback discipline, fixture-update expectations.
The EODHD 30-day deletion mechanism — implementation, scope, scheduling, and the test that exercises it on subscription cancellation.
config/universe.yaml — the contents and schema of the universe configuration, including the layered universe model (Core Test, Candidate, Future Full Eligible) and eligibility rules from SDR Decisions 3 and 4.
The schema-level support for the time-aware research auditability invariant inherited from Section 1 — universe membership snapshots, eligibility effective dates, ETF launch and delisting handling, and any other foundational fields needed to prevent survivorship bias and support point-in-time reconstruction.

Out of scope for Section 2 (deferred to later sections)

Feature calculation formulas, lookback windows, smoothing constants → Section 3.
Target generation logic, label alignment rules, overlapping-label handling → Section 3.
Model training, calibration pipeline, MLflow client-side integration, model registry tables → Section 3.
Regime classification logic and regime tables → Sections 3 (computation) and 4 (consumption).
Walk-forward harness, purge/embargo mechanics, transaction cost application, attribution storage tables → Section 4.
Portfolio rule logic, paper portfolio state tables, broker-neutral order-intent tables → Section 5.
Dash UI screens and the database-access enforcement mechanism for the UI read-only constraint → Section 6.

Section 2 should make clear that these are deferred without leaving holes that prevent the data layer from being understood. Where a deferral has data-layer consequences (for example, that future sections will add tables to the application database via migrations), Section 2 records the convention and points to the section that will fill in the detail.

Section 1 v1.0 inherited requirements
Section 2 must satisfy all of the following requirements inherited from Section 1 v1.0 LOCKED. These are not open for renegotiation in Section 2; they are constraints. If the inheritance forces a Section 2 design choice that you believe is impractical or wrong, escalate per EW Section 12.2 — do not silently work around the inheritance.

providers/ returns provider-tagged DTOs. No persistence inside providers/.
ingestion/ is the only persistence path for provider-sourced records. Transactions, the data-quality framework, and the EODHD purge mechanism live here.
Postgres is the system of record. All application state lives in Postgres; MLflow is for run metadata and artifacts only.
MLflow is not application state. No business module (portfolio/, paper/, order_intent/) reads application state from MLflow. Section 2 must not introduce a pattern that contradicts this.
The system must support time-aware research auditability. Per Section 1 architectural invariant 7, the architecture must support point-in-time reconstruction and auditability for look-ahead bias, survivorship bias, overlapping labels, and backtest leakage.
Section 2 must establish the universe and ingestion foundation for point-in-time reconstruction. This is where the time-aware invariant cashes out at the schema level for universe membership, eligibility, ETF lifecycle, and ingestion-run metadata.
Section 2 must support survivorship-bias controls from day one. Per SDR Decision 4 and Section 1 invariant 7. The schema must support inception/first-price dates, eligible start dates, active flags, optional delisted dates, optional replacement tickers, universe-layer membership, and rank-eligibility flags. Section 2 designs these fields; Sections 3–5 use them.
Section 2 must support the EODHD 30-day purge obligation. Per SDR Decision 2. Every provider-sourced row carries provider_name and provider_symbol; the deletion routine filters by provider_name = 'eodhd' and runs within 30 days of subscription cancellation. Section 2 implements and tests this.
Section 2 must not design features, targets, models, backtests, portfolio rules, or UI screens beyond handoff contracts. Schema fields that future sections will use (e.g., a feature_id foreign key from a feature table to the universe table) may be reserved at the convention level, but the feature tables themselves are Section 3's responsibility.
No implementation should begin from this prompt. This is drafting only. Coding starts only after Section 2 is approved per EW Section 3.4 and you have an additional implementation-task handoff packet from me per EW Section 4.


SDR decisions Section 2 most directly implements
Cite these explicitly in the section's "Relevant SDR decisions" field, and reference them in inline commentary where they shape the data layer:

Decision 2 — Data provider abstraction principle and EODHD storage constraint (provider abstraction interface, EODHD implementation, the 30-day deletion mechanism, provider_name/provider_symbol tagging).
Decision 3 — ETF universe layered model (Core Test / Candidate / Future Full Eligible), eligibility rules, the universe registry schema, config/universe.yaml.
Decision 4 — Survivorship and ETF launch-date handling (inception/first-price date, eligible start date, active flag, optional delisted/replacement fields, universe-layer membership, rank-eligibility flag).
Decision 5 (universe-side only) — sleeve and benchmark assignment fields on ETF records (ticker, sleeve, category, primary benchmark, secondary benchmark, portfolio role, rank method, equity-rotation eligibility, diversifier-sleeve eligibility). The actual sleeve-aware ranking logic and benchmark math are Section 3.
Decision 11 — Data quality reporting standard (issue, plain-English explanation, why it matters, likely cause, severity, suggested resolution, agent auto-resolution scope, what was auto-resolved, what the Approver must approve). Postgres database setup that supports the application database and the MLflow metadata database. MLflow writer-side integration is Section 3, not Section 2.
Decision 16 (architecture-level reservation, inherited from Section 1 invariant 7) — Section 2 implements the universe and ingestion-side schema fields supporting point-in-time reconstruction. Sections 3 and 4 implement the rest.

Other SDR decisions are touched by Section 2 only in the sense that the schema must accommodate their later use (Decision 6 target horizons, Decision 7 walk-forward, etc.). Section 2 does not implement those decisions in detail.

Section template (required by EW Section 3.2)
The drafted section must include all of these fields, in this order:

Purpose
Relevant SDR decisions
In scope
Out of scope
Inputs and outputs (at the data layer level — what data the data layer consumes and produces)
Data contracts (DTO shapes between providers/ and ingestion/; foundational table schemas; the contract between ingestion and the data quality framework)
Config dependencies (what config/universe.yaml contains; how it is validated at startup)
Required tests (provider tests, ingestion tests, schema migration tests, data-quality framework tests, 30-day purge test, point-in-time reconstruction tests, look-ahead and survivorship checks where they apply at the data layer)
Edge cases and failure behavior (provider unreachable, partial pulls, malformed responses, duplicate rows, schema-migration partial application, EODHD subscription cancellation, conflicting provider data on re-pulls, etc.)
Open questions (items not resolved by the SDR, EW, or Section 1, classified per EW Section 3.3 and the proposed-default categories below)
Explicit assumptions (any data-layer choice not directly traced to the SDR/EW/Section 1, classified per EW Section 3.3)

A section that omits any of these fields is incomplete and is returned to the Builder.

Proposed-default flagging — explicit categories
Section 2 will need decisions in the following categories that are not pre-resolved by the SDR, the EW, or Section 1. For each category below, you must explicitly classify the choice using the EW Section 3.3 categories below and propose a default with rationale where appropriate. Do not bury these in the draft. Surface each one under Open questions or Explicit assumptions with the classification visible.
The classifications are:

Derived from SDR or EW — a logical consequence of an existing SDR decision or EW provision (cite which one).
Derived from approved Section 1 — a logical consequence of a Section 1 invariant, boundary, or Approver-resolved default (cite which one).
Implementation default with no strategy impact — a reasonable engineering choice that does not change strategy behavior.
Proposed default requiring Approver approval — a strategy-affecting or operationally consequential choice you propose, requiring explicit Approver accept/reject.
Open question for Approver — needs Approver decision before the section is finalized; you have not formed a confident default.

The categories Section 2 must address:

Migration tooling. Choose between Alembic, raw SQL migrations with a thin runner, yoyo-migrations, or plain SQL files with manual/scripted execution. Propose a default with rationale; flag classification per Section 3.3.
Adjusted-price convention. Which price fields are stored. Whether adjusted close is the canonical research price. How splits and dividends are represented. Whether raw OHLCV and adjusted OHLCV are both stored, or only one. Strategy-affecting per SDR Decision 2 ("reliable adjusted close data") and SDR Decision 7 (validation depends on consistent adjusted prices).
Postgres layout. One Postgres cluster with two logical databases (application DB plus MLflow metadata DB), versus another arrangement. Whether schemas are used inside the application database (e.g., a universe schema, a prices schema), or whether all tables live in the public schema. Operationally consequential.
Provider DTO contract. Exact DTO fields. Whether DTOs are dataclasses, Pydantic models, typed dictionaries, or another contract form. Required provider-tagging fields including provider_name and provider_symbol. Strategy-neutral but architecturally consequential — this is the seam between providers/ and ingestion/.
Raw provider payload storage. Whether raw provider responses are stored alongside the normalized rows, or only the normalized rows. If raw responses are stored, the retention policy. How this interacts with the EODHD 30-day purge obligation per SDR Decision 2 (raw EODHD-sourced data is also subject to the purge).
Data freshness / SLA rules. Expected daily refresh timing. Stale-data threshold (after how many missed business days a price series is treated as stale). Whether stale data triggers warning or fail in the data quality framework. Whether the system can continue to use prior data if the provider is unavailable, and for how long.
Data quality severity framework. Pass / warning / fail definitions consistent with SDR Decision 11. Exception report structure. Which issue classes block downstream modules from running, which are warnings, which are pass-with-note. Auto-resolution scope (which issues ingestion/ may auto-resolve per SDR Decision 11; recall that benchmark changes, ETF replacements, price modifications, and provider switches are explicitly forbidden as auto-resolution).
Ingestion idempotency. Whether ingestion uses upsert/merge semantics. How ingestion runs are tracked (run table, run id, run status). Duplicate-row handling. Partial-run recovery expectations after an OOM-kill or container restart.
ETF identity and symbol mapping. Internal ETF identifier. Provider symbol. Ticker changes (how a ticker change is represented and resolved). Exchange and country fields if needed. Launch date and delisting/inactive handling. The relationship between the internal identifier and the provider_symbol.
Time-aware eligibility model. Effective start and end dates. As-of dates. Universe membership snapshots. Fields needed to prevent survivorship bias and support point-in-time reconstruction per SDR Decision 4 and Section 1 invariant 7. This is where the time-aware research auditability invariant cashes out at the schema level for the universe and ingestion domains; Section 3 extends it to features and targets, and Section 4 extends it to backtest results.

For each of the ten categories above, the draft must produce one of: an Approver-resolved default (only after I confirm), a Proposed default requiring Approver approval (most likely outcome for several of these), an Implementation default classification, a Derived-from classification with citation, or an Open question.
If you find another category not listed above that needs Approver decision, raise it as an additional Open question — do not bury it.

Section size control (EW Section 3.1)
Section 2 is the largest single concentration of data-layer concerns in the project. The default is to keep it as one section; do not pre-split.
Authorization to propose a split. If during drafting you assess that Section 2 has become too large, too dense, or starts mixing concerns that would be safer to review separately, you are authorized to propose a split into:

02a_provider_and_ingestion.md — provider abstraction, EODHD implementation, ingestion orchestration, data quality framework, EODHD 30-day purge mechanism. Canonical repo path docs/engineering_spec/02a_provider_and_ingestion.md.
02b_data_layer_schema_and_quality.md — Postgres schema, migrations infrastructure, MLflow metadata DB setup, schema-level time-aware fields, config/universe.yaml. Canonical repo path docs/engineering_spec/02b_data_layer_schema_and_quality.md.

Builder discipline. You must not split automatically. Stop drafting at the point you propose the split, explain why (size, density, review safety), and wait for my approval before restructuring. If I approve, you produce two files; if I decline, you continue as a single section.
If size becomes an issue and you have not yet proposed a split, that itself is a defect at QA review.

Constraints

Length: Section 2 should be focused and readable. If you find yourself writing more than roughly 12–15 pages of markdown without proposing a split, you are probably specifying things that belong in later sections, or you are at the size where a split should be proposed. Stop and either escalate or propose a split.
No assumption drift (EW Section 3.3): Every data-layer choice must trace to an SDR decision, an EW provision, a Section 1 invariant, or be flagged per the Section 3.3 categories listed above. Silent decisions are forbidden. This rule is especially important for the ten proposed-default categories — each must be visibly classified.
No reinterpretation of strategy (EW Section 2.1): If an SDR decision seems impractical or wrong as you draft, escalate to me. Do not silently adjust.
No relaxation of Section 1: Section 1 v1.0 LOCKED is binding. If a Section 2 design choice would relax or contradict a Section 1 invariant or boundary, escalate — do not silently work around it.
Stop conditions (EW Section 3.5): If an SDR decision needed by this section is missing or conflicting, if a module boundary is unclear, if testability is unclear, if financial logic is implied but not actually decided, if broker behavior is ambiguous, or if a new research feature appears to be needed that the SDR does not cover, stop and escalate.
No code in this conversation: This is a spec-drafting task. No Python, no SQL DDL, no Alembic scripts, no Dockerfile content, no docker-compose.yml snippets. The spec describes what will exist; later modules implement it. Pseudocode-style schema sketches in tables (column name / type / constraints) are acceptable as part of the data contract; full DDL is not.


Output format
Produce the drafted section as a single markdown file. The canonical commit path is docs/engineering_spec/02_data_layer.md (or, if a split is approved, the two paths named under "Section size control"). Use the section template from EW Section 3.2 as the document structure.
Alongside the section, produce a proposed update for the traceability matrix (canonical path docs/traceability_matrix.md) covering the SDR decisions Section 2 implements (Decisions 2, 3, 4, 5 universe-side, 11, plus the Section 2 contribution to Decision 16). Provide the updated rows in the same markdown table format the matrix already uses. The Decision 2 row already exists at status in spec from Section 1; Section 2 will fill out its Module(s), Config File(s), and Required Tests fully.
If you have open questions or proposed defaults that I need to decide, list them at the end of your response separately from the drafted section, so I can address them before the section is taken to QA review. For each item, state the EW Section 3.3 classification.

Process reminder
After your draft:

I review it.
I take it to ChatGPT for QA review against EW Section 9 (spec section checklist), citing the SDR, the EW, and Section 1 v1.0.
ChatGPT produces a QA report.
If QA flags issues, the report comes back here and you address them.
Once QA passes (and any Approver-resolved defaults are confirmed), I approve, commit to docs/engineering_spec/02_data_layer.md, save the handoff packet and QA report to docs/reviews/, and update the traceability matrix.
Section 3 begins in a separate fresh conversation with its own handoff packet.

Section 2 is not approved until I commit it. Do not assume approval based on QA passing. Do not begin module implementation based on this prompt — implementation begins only after Section 2 is approved and I provide a separate implementation-task handoff packet per EW Section 4.

Begin
Read the five documents from the canonical manifest, in the order listed under "Documents you must read before drafting." When you have read them, confirm back to me what you understand the task scope to be, raise any open questions you see before drafting (especially any of the ten flagged categories where you would like guidance before proposing a default), confirm whether you intend to draft as a single section or anticipate proposing a split, and then produce the draft.
If anything in this prompt conflicts with the SDR, the EW, or Section 1 v1.0 LOCKED, the SDR / EW / Section 1 take precedence and you should flag the conflict.

End of Section 2 handoff prompt.
