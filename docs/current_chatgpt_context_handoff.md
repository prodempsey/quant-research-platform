# Quant Research Platform — Current Context Handoff

## Project

Repository: prodempsey/quant-research-platform  
Branch: main  
Phase: Phase 1 ETF tactical research platform  
Status: Engineering Specification drafting, pre-implementation

## Source-of-truth hierarchy

1. Strategy Decision Record v1.0 LOCKED / APPROVED
2. Engineering Workflow v1.5 LOCKED
3. Locked Engineering Specification sections
4. Traceability Matrix
5. Approval notes and review artifacts
6. Current draft section under review

If any document conflicts with a higher-priority source, flag the conflict. Do not silently resolve it.

## Locked / approved sections

- docs/engineering_spec/01_architecture_overview.md — v1.0 LOCKED / APPROVED
- docs/engineering_spec/02_data_layer.md — v1.0 LOCKED / APPROVED
- docs/engineering_spec/03a_feature_engineering.md — v1.0 LOCKED / APPROVED
- docs/engineering_spec/03b_target_generation.md — v1.0 LOCKED / APPROVED

## Current active section

Next section:

docs/engineering_spec/03c_model_layer_mlflow.md

03c owns:
- baseline model layer;
- model training using successful feature runs and successful target runs;
- MLflow writer-side integration;
- models.* schema;
- rank_method allowed values and semantics;
- config/model.yaml;
- combined-score formula;
- calibration pipeline;
- model state lifecycle handoff to later sections.

03c does not own:
- feature engineering;
- target generation;
- walk-forward backtest harness;
- purge/embargo enforcement;
- portfolio rules;
- order intent;
- UI;
- live trading.

## Phase 1 hard boundaries

Phase 1 is strictly research and paper-trading only.

Do not introduce:
- live broker integration;
- individual stocks;
- fundamentals;
- ETF holdings;
- news/events;
- earnings transcripts;
- options data;
- Danelfin;
- autonomous research agents;
- commercial/customer-facing features.

## Current canonical status

traceability_matrix.md is at v0.5 after merging Sections 1, 2, 3a, and 3b.

Sections still pending:
- 03c_model_layer_mlflow.md
- 04_backtest_attribution_validation.md
- 05_portfolio_paper_order_intent.md
- 06_operator_ui.md

## Reviewer checklist

When reviewing Claude output, check for:

- scope drift;
- contradiction with locked sections;
- hidden strategy assumptions;
- missing approval gates;
- missing traceability matrix updates;
- data leakage or look-ahead bias;
- survivorship bias;
- incorrect null-vs-no-row behavior;
- incorrect ownership between sections;
- implementation/code appearing before approval;
- stale document paths or invented filenames.

## Process rule

Do not start code or implementation until the relevant Engineering Specification section is v1.0 LOCKED / APPROVED and traceability has been updated.

When a section is ready to lock, expected artifacts are:

- docs/engineering_spec/<section>.md
- docs/reviews/<date>_spec_<section>_approval.md
- docs/reviews/<date>_spec_<section>_traceability_updates.md
- docs/traceability_matrix.md updated after applying the companion artifact
