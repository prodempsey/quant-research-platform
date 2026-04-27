# Quant Research Platform — Strategy Decision Record

**Phase 1 scope:** ETF tactical research platform.

**Document status:** v1.0 LOCKED / APPROVED
**Approval date:** 2026-04-26
**Final Approval:** Jeremy
**Repository:** `quant-research-platform`
**Companion document:** Quant Research Platform — Engineering Workflow v1.5 LOCKED

This Strategy Decision Record is the approved source of truth for Phase 1 strategy direction. The Engineering Workflow controls process. The Engineering Specification must be created from this SDR and the locked Engineering Workflow.

The repository name `quant-research-platform` reflects long-term scope, but Phase 1 is strictly limited to the ETF tactical research platform defined in this SDR. The broader name is not approval to expand scope.

---

## Purpose

This document captures the strategic decisions that should guide the Phase 1 Engineering Specification. It is not the engineering spec. Its purpose is to prevent coding agents from making hidden assumptions about data, targets, validation, portfolio rules, model promotion, broker execution, or agentic AI boundaries.

Official framing:

> The platform estimates relative ETF opportunity and risk under tested conditions. It does not predict the future with certainty.

---

## Decision 1 — Project Scope and Phase 1 Boundaries

### Decision

Phase 1 is a **personal ETF tactical research and internal paper-portfolio platform**, not a live trading bot.

Phase 1 includes EODHD historical price ingestion, a Core Test Universe, benchmark/sleeve mapping, feature engineering, target generation, baseline ranking, walk-forward backtesting, portfolio management rules, internal paper portfolio, broker-neutral order-intent records, manual/mock broker adapters only, lightweight MLflow tracking, and bias-control reporting.

Phase 1 excludes real broker API adapters (Schwab, IBKR, Alpaca, or any other live broker integration), live broker order placement, individual stocks, fundamentals, ETF holdings, news/events, earnings transcripts, options data, Danelfin, autonomous research agents, and commercial/customer-facing features.

### Rationale

The first priority is to prove that the ETF research and paper-portfolio engine is clean, reproducible, and understandable before adding richer data or execution complexity.

### Final Approval

Jeremy

### Revisit Trigger

Revisit after Phase 1 produces reproducible backtests, paper portfolio output, documented model runs, and understandable QA reports.

---

## Decision 2 — Data Provider and Provider-Switching Strategy

### Decision

Use **EODHD EOD Historical Data All World** as the starting Phase 1 provider.

The code must use a **provider abstraction layer** so the system is not tightly coupled to EODHD. The goal is to make it easier to replace or supplement EODHD later if needed without rewriting feature engineering, backtesting, modeling, or portfolio modules.

Future providers are not selected yet. Possible examples could include another market-data API, a survivorship-bias-free data provider, broker-provided data, or manually loaded CSV files.

No feature, model, backtest, or portfolio module may call EODHD directly. Provider-specific API logic must live only in the data provider layer.

### EODHD Storage Constraint

EODHD data may be stored internally during the active subscription period. Upon termination or expiration, stored EODHD data must be deleted within one month.

Implications:

- stored rows should include `provider_name` and `provider_symbol`
- raw and normalized EODHD-sourced data must be identifiable
- if the subscription is cancelled, EODHD-sourced raw and normalized data must be purged within 30 days
- continuing the project after cancellation requires renewing EODHD or re-sourcing data from another provider

### Rationale

EODHD's lower-cost EOD plan is enough for Phase 1. Provider abstraction preserves flexibility without implying that any future provider is already selected.

### Final Approval

Jeremy

### Revisit Trigger

Revisit provider choice if adjusted-close validation fails, ETF/benchmark coverage is insufficient, dividend/split adjustment reliability fails, licensing/storage constraints become incompatible, operational reliability is poor, or another provider becomes clearly better.

Validation failures should produce plain-English exception reports with likely cause, impact, suggested resolution, whether auto-resolution is allowed, and whether Jeremy approval is required.

---

## Decision 3 — ETF Universe and Eligibility Rules

### Decision

Phase 1 starts with a manually defined **Core Test Universe** of liquid, non-leveraged ETFs.

This initial list is not the final investable universe. It is a controlled seed universe used to validate the pipeline, features, targets, backtesting, and portfolio rules.

After the pipeline is working, the platform should expand to a broader **Candidate Universe** of approximately **150–300 liquid, non-leveraged U.S.-listed ETFs** before serious model evaluation.

Universe layers:

1. **Core Test Universe** — about 40–75 manually selected ETFs for pipeline validation and first backtests.
2. **Expanded Candidate Universe** — about 150–300 liquid, non-leveraged ETFs for more serious ranking/backtesting.
3. **Future Full Eligible Universe** — broader ETF universe filtered by eligibility rules after category, liquidity, and benchmark logic mature.

Core Test Universe examples include broad market ETFs, sectors, themes, bonds/Treasuries, commodities/currency/alternatives, international ETFs, and REITs.

Eligibility rules:

- at least 2 years of price history before becoming rank-eligible
- passes minimum liquidity and average daily dollar volume filters
- not leveraged or inverse
- reliable adjusted close data
- valid benchmark or sleeve classification
- may exist in the database before becoming rank-eligible

### Rationale

A small curated ETF universe is useful for debugging but too small for serious ETF ranking. The Core Test Universe gets the system working; the Expanded Candidate Universe makes evaluation more realistic.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if too few ETFs qualify, the model over-concentrates, liquidity assumptions fail, thematic ETF behavior is unreliable, or expanded ETF discovery is needed.

---

## Decision 4 — Universe Survivorship and ETF Launch-Date Handling

### Decision

Phase 1 begins with a manually selected Core Test Universe, which is a current-survivor ETF list. This is acceptable for validating mechanics but should not be treated as a fully realistic historical ETF universe.

Before serious model evaluation, the platform should expand to a broader Candidate Universe and apply time-aware eligibility rules.

Each ETF record should support:

- inception date or first available price date
- eligible start date
- active flag
- optional delisted date
- optional replacement ticker
- universe layer, such as Core Test Universe or Candidate Universe
- rank eligibility flag

An ETF may only be included in model ranking after its eligible start date.

Early Phase 1 results must be labeled:

> Core Test Universe / current-survivor results. Useful for pipeline validation and directional learning, not statistical proof.

### Rationale

Some ETFs in the starter list did not exist in earlier backtest years, and some historical ETFs that closed are not included. This is acceptable only if documented and improved before stronger performance claims.

### Final Approval

Jeremy

### Revisit Trigger

Revisit before using real capital, expanding into stocks, expanding the candidate universe materially, or making stronger performance claims.

---

## Decision 5 — Benchmark, Sleeve, and Diversifier Treatment

### Decision

Each ETF should be assigned to a portfolio sleeve before ranking. The platform should not force every ETF to compete against SPY in the same way.

Sleeves:

1. **Broad Equity ETFs** — compare broad equity ETFs to SPY/VTI, small caps to IWM/IJR, growth/Nasdaq to QQQ.
2. **Sector ETFs** — primary comparison to SPY, optional peer comparison to other sectors.
3. **Thematic ETFs** — benchmark depends on theme; technology/growth may compare to QQQ, defense/industrial to SPY or XLI, energy/commodity themes to XLE or relevant commodity benchmark where appropriate.
4. **Bond / Treasury ETFs** — compare to bond-category benchmarks; evaluate absolute trend, volatility, drawdown, and rate regime; do not judge primarily by beating SPY.
5. **Diversifier / Hedge ETFs** — examples include GLD, SLV, DBC, USO, UUP; evaluate primarily by absolute opportunity/risk and hedge value; SPY-relative return may be shown as context, not primary ranking target.
6. **REIT / Real Asset ETFs** — compare against REIT/real-estate peers; optionally compare to SPY as opportunity-cost context.

Each ETF should have fields for ticker, sleeve, category, primary benchmark, secondary benchmark, portfolio role, rank method, equity-rotation eligibility, and diversifier-sleeve eligibility.

### Rationale

Different ETFs have different jobs. XLK can reasonably be judged against SPY. GLD should not be judged primarily by whether it beats SPY; it may be valuable because it improves portfolio defense, inflation protection, or risk-off exposure.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if diversifiers are unfairly penalized, bond/Treasury ETFs are ranked poorly despite reducing drawdown, thematic ETFs are benchmarked poorly, or portfolio construction needs separate sleeve allocation rules.

---

## Decision 6 — Target Design and Ranking Objective

### Decision

Use a dual-target approach:

1. **Regression target** — forward excess return versus benchmark over 63 and 126 trading days.
2. **Classification target** — whether the ETF outperformed benchmark over 63 and 126 trading days.

The ranking should eventually combine expected excess return, calibrated probability of outperformance, risk score, and trend/relative-strength confirmation.

Do not hard-code the final combined score formula in this decision document. The engineering spec should define a first testable formula, and the backtester should compare alternatives.

### Rationale

A pure binary target loses magnitude information. A pure regression target may not directly support threshold-based portfolio rules. Using both provides a richer model framework.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if regression outputs are unstable, probabilities are poorly calibrated, expected excess return does not improve ranking quality, or portfolio rules become too dependent on noisy thresholds.

---

## Decision 7 — Validation, Calibration, and Backtest Confidence Level

### Decision

Use walk-forward validation as the primary validation framework.

Phase 1 should support:

- primary backtest: 2010–2025 where ETF data exists
- longer robustness test: 2005–2025 where ETF history supports it
- recent-regime test: 2020–2025
- monthly rebalance testing
- clear separation between training and test periods

Because 63-day and 126-day forward windows overlap, Phase 1 results should be treated as directional unless validation includes purge/embargo handling.

Probability outputs must be calibrated before hard thresholds such as 60% are treated as meaningful. Calibration methods may include Platt scaling, isotonic regression, or logistic calibration on held-out walk-forward folds.

Validation must explicitly address look-ahead bias, overlapping-label risk, selection/data-snooping bias, current-survivor universe limitations, backfill/proxy-history bias, market impact/liquidity bias, and time-zone/synchronization bias where relevant.

### Rationale

Simple backtests can create false confidence. Overlapping forward-return windows reduce sample independence. Scores should not be treated as reliable probabilities unless calibrated.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if early results look too good, confidence is unstable, probabilities are poorly calibrated, walk-forward results differ materially from paper tracking, or research moves into stocks.

---

## Decision 8 — Transaction Cost and Account-Type Assumptions

### Decision

Every backtest should include transaction-cost assumptions.

Use simple cost buckets in Phase 1: ultra-liquid ETF, liquid sector ETF, thematic/niche ETF, and commodity/specialty ETF.

The system should support account type tags, including internal paper account, retirement/Solo 401(k), taxable account later if needed, and non-retirement API testing account later if needed.

Phase 1 should default to conservative long-only ETF rules, but no live execution.

### Rationale

Even commission-free ETF trading has spreads and slippage. Tax drag is less relevant in retirement accounts but may matter later for taxable accounts.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if turnover is high, niche/thematic ETFs dominate trades, real fills differ from assumptions, taxable support is added, or non-retirement API execution testing begins.

---

## Decision 9 — Regime Taxonomy and Reporting

### Decision

Phase 1 should include a simple regime-reporting layer, not a complex macro regime model.

Start with two dimensions:

1. **Market trend regime** — SPY above/below 200-day moving average.
2. **Volatility regime** — VIX high/low using rolling percentile if VIX data is available; otherwise defer volatility regime reporting.

This creates up to four basic regimes: risk-on/low-vol, risk-on/high-vol, risk-off/low-vol, risk-off/high-vol.

Later additions may include rates, QQQ vs SPY, IWM vs SPY, RSP vs SPY, dollar trend, and oil trend.

### Rationale

Too many dimensions create too many small buckets. Phase 1 only needs enough regime reporting to see whether the strategy works in only one type of market.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if performance differs sharply across regimes, strategy fails in a specific environment, macro features are added, or richer data becomes available.

---

## Decision 10 — Portfolio Management and Risk Rules

### Decision

The system should convert model output into actions: BUY, HOLD, TRIM, SELL, REPLACE, WATCH.

Initial portfolio concept:

- model-driven ETF rotation
- monthly rebalance
- weekly risk review
- top 5 ETF positions initially
- equal weight initially
- volatility-adjusted sizing later

Rules should be configurable, not hard-coded. Early concepts include buy if rank and score confirm, hold while rank remains acceptable, sell when rank/trend/relative strength deteriorate, replace only when current ETF materially weakens and replacement is clearly stronger, use ATR-based stops, avoid tight fixed stops, and avoid fixed take-profit rules by default.

Store thresholds in YAML during early development.

### Rationale

The ranking model only says what looks attractive. Portfolio rules determine how the system acts.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if turnover is too high, whipsaws are frequent, drawdowns are too large, profit-taking cuts winners too early, replacement rules chase small changes, or paper behavior is hard to follow.

---

## Decision 11 — Model Tracking, Attribution, Data Quality, and Lightweight MLOps

### Decision

Phase 1 should include lightweight MLOps practices, but not enterprise MLOps infrastructure.

Start with Postgres as the system of record and MLflow as the lightweight experiment/model-run tracking layer for Phase 1.

MLflow will track:

- model runs
- training windows
- validation method
- feature sets
- target type
- hyperparameters
- performance metrics
- artifact references
- model comparison metadata

Postgres remains the system of record for platform state, ETF data, features, targets, rankings, paper portfolio state, order-intent records, approvals, and audit-relevant tables.

MLflow metadata will be stored in Postgres, and MLflow artifacts will be stored in a Docker named volume as defined by the deployment architecture.

The system should produce plain-English data-quality and model-quality reports with pass/warning/fail statuses.

Do not implement full production MLOps, automated retraining, or live model deployment in Phase 1.

### Data Quality Exception Report Standard

Each exception should include issue, plain-English explanation, why it matters, likely cause, severity, suggested resolution, whether agent auto-resolution is allowed, what was auto-resolved, and what Jeremy must approve.

Agents may auto-resolve mechanical issues such as retrying failed API calls, re-pulling affected date ranges, removing exact duplicate rows, and marking ETFs as not-yet-eligible due to insufficient history.

Agents may not silently change benchmarks, replace ETFs, alter historical prices, ignore bad benchmark data, switch providers, change model/portfolio rules, or place trades.

### Rationale

Postgres and local artifacts alone may be hard to analyze as model runs grow. MLflow makes experiment comparison easier while Postgres remains the source of truth.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if experiments become hard to compare, MLflow local tracking becomes disorganized, drift monitoring needs exceed custom reports, multiple models are active, or the platform moves from paper tracking to real decision support.

---

## Decision 12 — Model Promotion, Warning, Pause, and Retirement Rules

### Decision

Use two promotion gates:

1. **Research model → internal paper tracking** — requires backtest requirements, passing data quality checks, attribution, cost assumptions, regime report, model registration, and Jeremy approval.
2. **Paper tracking → influence on real decisions** — requires enough live observation to understand behavior, reasonable paper results, explainable output, tolerable drawdowns, expected behavior, and Jeremy approval.

Use model states: Active, Warning, Paused, Retired.

A simple bad month should not automatically retire a model. Pause/retirement should require multiple conditions or sustained failure.

### Rationale

There must be a process for deciding when a model is trusted, watched, paused, or retired. This prevents emotional decision-making during drawdowns.

### Final Approval

Jeremy

### Revisit Trigger

Revisit after the first 3–6 months of paper tracking.

---

## Decision 13 — LLM Guidance, Agentic Coding, Research Agents, and QA Workflow

### Decision

Use LLMs heavily as guidance, education, coding, research-support, and QA tools.

Jeremy is not expected to personally know quantitative finance, machine learning, or algorithmic trading at an expert level before building the platform. The LLM should act as a teacher and decision-support assistant.

Allowed early:

- explain concepts in plain English
- explain backtest results and model metrics
- identify risks, flaws, and suspicious results
- suggest reasonable next tests
- help design research questions and compare modeling approaches
- interpret data-quality and model-quality reports
- write code through Claude Code
- review code through Codex/ChatGPT
- produce recommendations for Jeremy to approve

Allowed coding workflow:

- Claude Code implements one well-defined module at a time
- Codex/ChatGPT reviews code as QA
- LLMs may run scoped test/fix/refactor loops
- financial logic, risk rules, model rules, or broker logic require review before acceptance

Not allowed in Phase 1:

- autonomous live trading
- autonomous broker order placement
- autonomous promotion to real-money use
- autonomous strategy optimization without review
- silent changes to risk rules, benchmarks, ETF universe, or target definitions
- optimizing backtests until they look good
- ignoring or overriding failed data-quality checks without approval

Research-agent loops should wait until the baseline platform is working and Jeremy has seen enough outputs to understand normal versus suspicious behavior.

LLM-guided research is allowed from the beginning if it remains advisory and produces explanations, options, and recommendations rather than automatic decisions.

### Rationale

The risk is not LLM assistance. The risk is unsupervised LLM control over strategy, model promotion, risk assumptions, or trade execution.

### Final Approval

Jeremy

### Revisit Trigger

Revisit after the baseline pipeline has been run repeatedly and outputs are understood.

---

## Decision 14 — Danelfin Timing and Evaluation Rule

### Decision

Do not subscribe to or integrate Danelfin during Phase 1.

Evaluate Danelfin only after baseline model, backtest framework, score/probability outputs, and attribution exist.

Danelfin's value should be judged by whether it adds information beyond the baseline model.

Later test variants: baseline only, Danelfin only, baseline + Danelfin scores, baseline + Danelfin score changes, baseline + Danelfin disagreement flags.

### Rationale

Danelfin cannot be evaluated properly until there is a baseline system to compare it against.

### Final Approval

Jeremy

### Revisit Trigger

Revisit after Phase 1 is complete and the baseline model has been tested.

---

## Decision 15 — Broker and Account Strategy

### Decision

Phase 1 will not include live broker execution.

The platform should remain broker-neutral and account-type-neutral so Jeremy can test execution through whichever broker/account combination is safest and easiest at the time.

Possible future execution paths include manual execution, mock/internal paper execution, Schwab brokerage account, Schwab Solo 401(k), IBKR Pro taxable/non-retirement account, IBKR Pro with third-party Solo 401(k) trust setup, or another broker.

The system should use broker-neutral order-intent records and broker adapters. The first live or paper broker-connected test should not be assumed to be the Solo 401(k).

### Account Safety Rules

The platform should support account-specific restrictions.

Retirement/Solo 401(k)-style rules: no margin, no shorting, no uncovered options, no leveraged/inverse ETFs in Version 1, no MLPs or UBTI-prone assets unless approved, no day-trading logic, no automated live orders without human approval.

Taxable/non-retirement testing rules: long ETF trades only in Phase 1. Stock trades may be considered only in a later approved phase. No margin unless enabled later, no shorting unless approved later, no options in early testing, and no automated live orders without human approval.

### Rationale

The best broker/account path is unknown. A non-retirement account may be easier and safer for API testing. Broker-neutral design prevents lock-in.

### Final Approval

Jeremy

### Revisit Trigger

Revisit after internal paper portfolio and broker-neutral order intents are working, Jeremy chooses an account for testing, Schwab API access is confirmed/denied, IBKR Pro testing becomes desirable, or manual-approved broker testing becomes worth evaluating.

---

## Decision 16 — Phase 1 Success Criteria and Bias Controls

### Decision

Phase 1 is successful only if the platform produces a reliable, auditable ETF research pipeline with explicit controls or disclosures for major backtesting biases.

Phase 1 is successful when:

1. ETF universe is loaded.
2. EODHD provider abstraction works.
3. Historical adjusted ETF prices are ingested.
4. Data quality checks run.
5. Features are calculated without look-ahead bias.
6. Signals are generated using data available at T-1 or earlier.
7. Simulated trades execute after the signal date, not on the same close used to generate the signal.
8. 63-day and 126-day targets are generated.
9. Baseline ranking model runs.
10. Walk-forward backtest runs.
11. Transaction costs/slippage assumptions are included.
12. ETF eligibility rules prevent ranking ETFs before eligible_start_date.
13. Current-survivor universe limitation is disclosed.
14. Backfilled/proxy history is not treated as actual tradable ETF history.
15. Experiments are tracked so failed tests are not lost.
16. Regime report is available.
17. Portfolio rules generate paper actions.
18. Internal paper portfolio works.
19. Model registry captures runs.
20. Attribution exists for trades/signals.
21. No live broker orders are possible.
22. Outputs are understandable and reviewable.

Phase 1 is not judged only by profitability.

### Bias Controls Required in Phase 1

**Survivorship Bias:** store inception/first price date, eligible_start_date, avoid ranking before eligible start, disclose current-survivor universe limitation.

**Look-Ahead Bias:** features and signals use only data available as of signal date; use T-1 data; execute simulated trades at T or later; target creation may use future data only for labels.

**Selection Bias / Data Snooping:** track all experiments, log failed tests, use walk-forward validation, compare against baseline, avoid unlimited parameter searching, require review before promotion.

**Backfill Bias:** use actual ETF traded prices, do not allow ETF data before first valid trading date, tag proxy/index data separately if ever used, exclude proxy history from standard performance claims.

**Market Impact / Liquidity Bias:** apply liquidity and average daily dollar volume filters; include transaction cost and slippage assumptions; avoid illiquid ETFs in Phase 1.

**Time-Zone / Synchronization Bias:** use U.S.-traded ETF price data only in Phase 1; do not use same-day foreign underlying data or NAV data for trade signals; add timestamp/calendar rules later if NAV, holdings, or international data are introduced.

### Rationale

Backtests can look profitable for the wrong reasons. Phase 1 should prove that the research pipeline is clean, auditable, and bias-aware before any model is trusted.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if a new data source is added, the ETF universe expands materially, stocks are added, NAV/holdings/fundamentals/news are added, or paper tracking begins to influence real decisions.

---

## Decision 17 — Operator UI

### Decision

Phase 1 will include a Dash-based operator UI for visibility, review, and controlled operation of the ETF tactical research platform.

The Phase 1 UI will include the following screens:

1. Universe & Eligibility
2. Data Quality
3. Current Rankings
4. Backtest Explorer
5. Paper Portfolio
6. Model Registry Browser
7. Regime View

The UI is read-only with respect to model promotion, broker execution, and live trading. No UI action may promote a model, place a live broker order, bypass approval gates, or modify SDR-governed strategy behavior without Jeremy's explicit approval.

The UI will be deployed as part of the application container on the Linux Hostinger VPS environment defined in Decision 18.

### Rationale

The UI should make the system understandable and reviewable without weakening the approval and safety controls. Phase 1 is a research and paper-trading platform, not an autonomous live-trading system.

### Approval Requirement

Any change that allows the UI to alter strategy-affecting state, promote models, submit broker orders, or enable live trading requires Jeremy's approval.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if UI requirements outgrow Dash, if mobile or remote-team access becomes a need, if read-only constraints become operationally limiting, or if a different visualization stack becomes clearly better-suited to Phase 2+ work.

---

## Decision 18 — Deployment and Container Architecture

### Decision

Phase 1 will be deployed on a Linux Hostinger VPS using Ubuntu 24.04 LTS, Docker, and `docker compose`.

The Phase 1 deployment architecture will use a multi-container stack:

1. Postgres container — system of record
2. MLflow tracking container — experiment and model-run tracking
3. Application container — Dash UI and scheduled research jobs
4. Optional nginx reverse proxy container — only if needed later for controlled UI access

Configuration will be handled through YAML files committed under `config/`. Credentials will live in a gitignored host `.env` file and will not be copied into container images or committed to the repository.

Deployment files such as `Dockerfile`, `docker-compose.yml`, `.env.example`, `.dockerignore`, backup scripts, restore scripts, and migration scripts are controlled project artifacts and must follow the Engineering Workflow review process.

### Rationale

Containerizing from day one improves reproducibility, portability, backup discipline, and separation between application code, configuration, database state, and credentials.

### Out of Scope for Phase 1

- Kubernetes
- Multi-host deployment
- Public TLS exposure of the Dash UI
- Container registry hosting
- CI/CD automation
- Live trading automation

### Approval Requirement

Any change to deployment exposure, live trading capability, broker connectivity, production credentials, database schema, or container architecture requires Jeremy's approval.

### Final Approval

Jeremy

### Revisit Trigger

Revisit if VPS resources become constraining, multi-host or cloud deployment becomes desirable, container registry hosting becomes useful, CI/CD automation becomes worth the operational cost, or the platform moves toward live trading.

---

## Known Phase 1 Limitations

Phase 1 limitations must be documented in backtest/report output:

- current-survivor ETF universe
- no delisted ETF universe reconstruction
- no fundamentals
- no ETF holdings
- no news/events
- no earnings transcripts
- no Danelfin
- no live broker API
- no individual stock model
- simple regime taxonomy
- early backtests are directional indicators, not statistical proof unless validation is upgraded
- probability thresholds should not be trusted until calibration is verified

---

## Language Discipline

Preferred wording: estimates, ranks, scores, flags, suggests, supports, under tested conditions, based on historical evidence.

Avoid: guarantees, proves, predicts with certainty, knows, sure thing, high probability without calibration, beats the market without context.

Official framing:

> The platform estimates relative ETF opportunity and risk under tested conditions. It does not predict the future with certainty.

---

## Immediate Next Step

With this SDR locked at v1.0 and the Engineering Workflow locked at v1.5, the next step is to create the Engineering Specification, section by section, governed by the Engineering Workflow. The Engineering Specification must cite this SDR for every decision it implements, and must update `docs/traceability_matrix.md` as each section is finalized.

---

## Final Approval

Approved by: Jeremy
Approval date: 2026-04-26
Approved version: v1.0

This SDR is approved as the controlling strategy document for Phase 1 of the `quant-research-platform` project. The Engineering Workflow v1.5 LOCKED controls process. The Engineering Specification must be created from this SDR and the locked Engineering Workflow.

Future SDR changes must be proposed, reviewed, approved, and documented as a new SDR revision.
