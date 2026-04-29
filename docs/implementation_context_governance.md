# Implementation Context Governance — Governor-Gated GitHub PR Agent Loop

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v1.0 APPROVED
**Approval:** Jeremy Dempsey, 2026-04-29
**Date:** 2026-04-29
**Document type:** Project-specific governance policy. Documentation only — no implementation, no scripts, no GitHub Actions workflow files, no separate repository.
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification sections under `docs/engineering_spec/`
- `docs/traceability_matrix.md`
- Approval notes and review artifacts under `docs/reviews/`
- Operating procedure: `docs/runbooks/governor_gated_github_pr_agent_loop.md`

---

## 1. Purpose

This document governs implementation-phase AI context management, token budgeting, task packet generation, drift prevention, Project Governor / Context Auditor review, QA review, post-fix validation, risk-tier routing, artifact handoffs, and final human approval for the Phase 1 implementation work that will follow approval of the remaining Engineering Specification sections.

It is the *policy layer*. The companion runbook at `docs/runbooks/governor_gated_github_pr_agent_loop.md` is the *operating procedure* — what Jeremy and the agents actually do, day to day.

The purpose of the policy layer is to prevent:

- context-window overload during long coding sessions;
- project scope drift;
- "telephone game" drift between coding sessions;
- silent assumptions baked into code;
- coding outside approved SDR / EW / engineering_spec contracts;
- Claude self-certifying its own fixes;
- implementation reaching Jeremy before independent QA and Project Governor / Context Auditor review have passed;
- overloading every small task with unnecessary bureaucracy;
- relying on another LLM as a rubber-stamp Governor.

This document is created now, *before* implementation begins, so that the workflow is in place when the first implementation task lands.

---

## 2. Non-scope-change statement

This document is documentation only. It does not change the project's strategy, scope, design, or workflow. Specifically:

- This document does not revise the SDR.
- This document does not revise the Engineering Workflow unless later promoted by Jeremy as a formal workflow amendment.
- This document does not revise any approved Engineering Specification section.
- This document does not expand Phase 1 scope.
- This document does not authorize implementation before the relevant approved spec section exists.
- This document does not authorize agents to approve or merge code.
- This document does not create a separate Governor tooling repository.
- This document does not select or implement Archon.
- This document does not introduce code, GitHub Actions workflow files, scripts, an `implementation_tasks.yaml`, a `drift_ledger.md`, or any `.archon/` directory.

Any change to the SDR, EW, or an approved engineering_spec section follows the existing change processes in those documents, not this one.

---

## 3. Relationship to existing Engineering Workflow

This document operationalizes the existing EW handoff-packet, QA-review, approval-matrix, and artifact-review discipline during the coding phase. The EW already establishes:

- the Builder / QA Reviewer / Approver role separation (EW §2.1);
- the LLM handoff packet contract and packet-storage discipline (EW §2.2);
- the Approval Matrix items reserved for the Approver (EW §2.3);
- the Engineering Specification section creation workflow (EW §3);
- the assumption-classification rules and stop conditions (EW §3.3, §3.5);
- the testing requirements (EW §5);
- the configuration management discipline (EW §7);
- the QA review checklist (EW §9);
- the module Definition of Done (EW §10);
- the "review the artifact, not the summary" principle (EW §9).

This document does not replace any of that. It adds a thin process layer on top of it for the implementation phase, so that when Claude Code, GitHub Actions, Codex/ChatGPT QA, and a Project Governor / Context Auditor review step are wired together over GitHub PRs, the resulting loop preserves the EW's controls rather than eroding them.

If at any point this document and the SDR or EW conflict, the SDR and EW control. A conflict that cannot be resolved by reading this document narrowly is escalated to Jeremy as a formal workflow amendment proposal.

---

## 4. Custom workflow statement

The Governor-Gated GitHub PR Agent Loop is a custom, GitHub-native, project-specific workflow for `quant-research-platform`. It is not a generic framework, and it is not a library.

The project may later extract generic tooling — token-budget checkers, allowed-files checkers, forbidden-import scanners, latest-commit SHA checkers, reusable GitHub Actions templates, reusable task packet templates — into a separate reusable repository. The current governance documents (this file and the runbook) remain inside `quant-research-platform` because they are tied to *this* project's source-of-truth hierarchy: this project's SDR, this project's EW, this project's engineering specifications, this project's traceability matrix, and this project's review artifacts.

The current design borrows general workflow-harness principles (see §5) but does not depend on Archon, LangGraph, CrewAI, or any external orchestration framework. It is built from primitives every team already has: GitHub Issues, GitHub PRs, GitHub Actions, Claude Code GitHub Actions, Codex/ChatGPT review prompts, and a Project Governor / Context Auditor LLM session that runs deterministic checks first and LLM-assisted semantic review second.

---

## 5. Archon-inspired principles adopted without Archon dependency

The project does not implement Archon and does not depend on Archon. No Archon code, dependencies, configuration files, command files, or workflow YAML are introduced by this document.

However, the workflow adopts these useful general design principles, which are widely applicable to AI-assisted coding regardless of any specific framework:

- explicit, repeatable workflow structure — every task moves through a known sequence of stages with known transitions;
- artifact-first handoffs — durable artifacts and GitHub records carry state between stages, not chat memory;
- fresh-context sessions — each Builder, QA, and Governor session starts from a clean packet rather than inheriting a prior chat;
- deterministic checks before LLM judgment — cheap, mechanical checks run before any model is asked to think;
- structured gate outputs — every gate produces a structured pass/revise/blocked result, not free-form prose;
- loop limits — fix loops have explicit caps and produce escalation packets when they hit;
- risk-tiered execution paths — trivial work and high-risk work do not follow the same path;
- independent QA review — the QA reviewer is a separate session that reads the artifact, not the Builder's summary;
- latest-commit validation — every gate decision references a specific commit SHA;
- failure escalation packets — repeated failure is an event that produces a structured packet, not silent retries;
- separation of Builder, QA Reviewer, Project Governor / Context Auditor, and Jeremy Approver roles — no single agent has end-to-end authority.

These principles inform the design of the workflow described below. They are not implemented as a framework; they are implemented as discipline encoded in this document and the runbook.

---

## 6. Terminology

The following terms appear throughout this document and the runbook. Definitions are project-local; if a term is also used in the EW, this document does not redefine it but uses it consistently.

- **Governor-Gated GitHub PR Agent Loop** — the end-to-end workflow that takes a GitHub Issue, runs it through Claude Code planning and implementation, GitHub Actions tests, Codex/ChatGPT QA review, and Project Governor / Context Auditor drift review, before reaching Jeremy for final approval and merge.
- **Project Governor / Context Auditor** — the control role that creates or verifies the task packet before Builder planning begins, manages the input-token budget, runs deterministic guardrail checks, validates Builder plans against the source-of-truth hierarchy, performs post-QA and post-fix drift reviews, and routes blocked items to Jeremy. The Project Governor / Context Auditor is a hybrid control layer combining deterministic checks, canonical-context retrieval, structured gate outputs, and LLM-assisted semantic review. It is not a rubber-stamp LLM. The full role name is used unless the role has already been introduced earlier in the same paragraph.
- **Builder** — Claude Code, acting as the implementation agent. Drafts plans, writes code, applies fixes. Does not approve, does not merge, does not self-certify fixes.
- **QA Reviewer** — Codex/ChatGPT, acting as an independent reviewer of the actual PR diff against the task packet, the relevant approved specs, the relevant SDR decisions, and the GitHub Actions test output.
- **Approver** — Jeremy. Final decision authority, per the EW Approval Matrix.
- **task packet** — the structured input given to the Builder before planning begins. Defines the task's scope, controlling specs, allowed and forbidden files, required tests, stop conditions, and context budget.
- **plan packet** — the Builder's draft implementation plan, produced before any code is written. Reviewed by the Project Governor / Context Auditor before code may begin.
- **fix packet** — the structured input given to the Builder when QA or tests have identified a safe, in-scope issue to address inside the existing PR.
- **post-fix QA re-review** — the QA Reviewer's review of the PR diff *after* a Builder fix, against the same task packet and specs.
- **post-fix drift check** — the Project Governor / Context Auditor's drift review *after* a Builder fix, against the source-of-truth hierarchy.
- **artifact handoff** — the durable record (a markdown file under `docs/reviews/`, a GitHub Issue/PR comment, a labeled state on a PR) by which one stage of the loop hands work to the next stage.
- **fresh-context session** — a Builder, QA Reviewer, or Project Governor / Context Auditor session that starts from a clean task packet or fix packet, not from a prior chat history.
- **drift ledger** — the future artifact at `docs/drift_ledger.md` that will record possible deviations between implementation and the source-of-truth hierarchy. Not created by this document.
- **implementation task manifest** — the future artifact at `docs/implementation_tasks.yaml` that will catalog implementation tasks. Not created by this document.
- **stop condition** — any condition under which the Project Governor / Context Auditor, Builder, or QA Reviewer must stop and escalate to Jeremy rather than proceed (see §29).
- **context budget** — the input-token cap on a Builder, QA Reviewer, or Project Governor / Context Auditor session packet (see §10).
- **allowed files** — the explicit list of files a Builder is authorized to edit for a given task.
- **forbidden files** — the explicit list of files (or file patterns) a Builder is forbidden to edit for a given task. Locked governance documents and approved spec sections are forbidden by default.
- **risk tier** — the classification (Tier 0, Tier 1, Tier 2, Tier 3) that determines which path a task follows through the loop (see §14).
- **failure escalation packet** — the structured packet generated when the loop hits a configured failure limit and stops AI retries in favor of a Jeremy decision (see §25).
- **final PR approval brief** — the Project Governor / Context Auditor's structured summary attached to a PR that has cleared all gates and is ready for Jeremy's final approval and merge.

---

## 7. Control-plane vs work-plane model

The workflow separates control from work. The control plane decides whether the work plane may proceed; the work plane performs the actual implementation and review activity.

**Control plane (Project Governor / Context Auditor)**

- canonical-context retrieval;
- task packet generation or verification;
- input-token-budget checks;
- deterministic guardrail checks (allowed files, forbidden files, forbidden imports, secrets, schema-migration detection, strategy-affecting config detection, latest commit SHA, test-result parsing, traceability row checks);
- plan validation (semantic);
- traceability checks;
- drift checks (post-QA and post-fix);
- stop-condition routing;
- structured gate outputs;
- no implementation authority;
- no merge authority;
- no approval authority.

**Work plane**

- Claude Code Builder — drafts plans, writes code, applies fixes;
- Codex/ChatGPT QA Reviewer — reviews the actual PR diff;
- GitHub Actions test runner — executes deterministic tests;
- one scoped GitHub Issue and one scoped PR per implementation task.

The Project Governor / Context Auditor does not write production code. The Builder does not approve plans, classify drift, or move PRs to human approval. The QA Reviewer does not implement fixes. Jeremy approves and merges. These role boundaries are not negotiable.

---

## 8. Project Governor / Context Auditor responsibilities

The Project Governor / Context Auditor must:

- retrieve relevant canonical context from the source-of-truth hierarchy (SDR, EW, approved engineering_spec sections, traceability matrix, approval notes);
- create or verify every task packet before Builder planning begins;
- estimate input-token size before the task is sent to the Builder or to the QA Reviewer;
- enforce the context-budget policy (see §10);
- split or reject oversized packets;
- validate Claude's plan *before code exists*;
- compare Claude's plan against the SDR, the Engineering Workflow, the relevant approved engineering_spec sections, the traceability matrix, the task packet, the allowed-files and forbidden-files lists, and the stop conditions;
- verify allowed and forbidden files;
- verify required tests are included in the plan;
- run or verify deterministic guardrail checks where available;
- detect possible project drift, including hidden assumptions and approval-gate items;
- route blocked items to Jeremy with appropriate labels (see runbook §4);
- perform the post-QA drift review after initial QA;
- perform the post-fix drift review after every Claude fix;
- compare the PR diff, QA findings, test output, task packet, approved specs, traceability matrix, allowed/forbidden file list, latest commit SHA, and stop conditions before final human approval, and produce the final PR approval brief.

The Project Governor / Context Auditor must not:

- write production code;
- approve SDR changes;
- approve Engineering Specification amendments;
- approve schema changes beyond approved specs;
- approve financial calculation changes;
- approve feature, target, or label definition changes;
- reinterpret SDR decisions;
- relax locked contracts;
- merge PRs;
- move a PR to human approval unless independent QA and post-fix drift checks have passed against the latest PR commit SHA.

---

## 9. Project Governor / Context Auditor toolbox

The Project Governor / Context Auditor is a hybrid control layer, not just another LLM. Wherever a check can be performed deterministically, it is performed deterministically *before* any LLM judgment is invoked.

**Deterministic checks** (used wherever available):

- input-token estimate check;
- changed-files check (PR diff scope);
- allowed-files / forbidden-files check;
- forbidden-import scan (e.g., broker SDKs, EODHD client libraries outside `providers/`);
- provider-boundary scan;
- live-trading / broker keyword scan;
- secrets scan (API keys, tokens, passwords, account numbers, `.env` literals);
- strategy-affecting config change detector (e.g., edits to `config/portfolio.yaml`, `config/model.yaml`, `config/features.yaml`, `config/universe.yaml`, `config/costs.yaml`, `config/regime.yaml`);
- schema migration detector (any change under `migrations/`);
- latest PR commit SHA check;
- pytest / ruff / migration test result parser;
- traceability matrix row check (does this task touch a row whose status would change?).

**LLM-assisted semantic judgment** (used after deterministic checks pass):

- plan drift review (does the plan match what the spec section actually requires?);
- hidden-assumption review (does the plan rely on something not stated in SDR / EW / approved specs?);
- semantic spec compliance review;
- QA finding classification (is this a defect, a Builder misunderstanding, or a spec ambiguity?);
- failure escalation summary;
- final PR approval brief generation.

The Project Governor / Context Auditor is not a rubber-stamp LLM. Deterministic checks are not optional preliminaries — they are the first line of defense, and an LLM's "looks fine to me" cannot override a deterministic failure.

---

## 10. Token budget policy

Long Builder, QA Reviewer, or Project Governor / Context Auditor sessions degrade in predictable ways: instructions earlier in the session get diluted by later content, deterministic constraints get treated as soft suggestions, and confident-but-wrong responses become more likely. The token budget policy exists to keep sessions inside the band where this degradation is manageable.

- Target maximum total session context: **100k tokens**.
- Preferred input packet ceiling: **60k–70k tokens**.
- No Builder, QA Reviewer, or Project Governor / Context Auditor session packet may exceed **70k input tokens** unless Jeremy manually approves the exception.
- Any packet above **70k input tokens** requires Jeremy approval.
- Any packet above **80k input tokens** should normally be split into smaller tasks unless Jeremy explicitly approves.
- Reserve **30k–40k tokens** for model reasoning, tool output, diffs, test logs, review comments, fix instructions, and final responses.
- No session should load all project documents verbatim unless Jeremy explicitly approves.
- The Project Governor / Context Auditor is responsible for estimating and enforcing the input-token budget before each Builder or QA Reviewer session.

A token-budget breach is a stop condition (see §29). The Project Governor / Context Auditor labels the issue/PR `blocked:token-budget` and routes to Jeremy.

---

## 11. Fresh-context discipline

Each Builder, QA Reviewer, and Project Governor / Context Auditor review cycle should operate from a fresh context packet. Prior chat or session history is not source of truth and is not assumed to be present.

Durable state lives in:

- canonical repo documents (SDR, EW, approved engineering_spec sections, traceability matrix);
- the GitHub Issue task packet;
- the PR diff;
- the latest commit SHA;
- GitHub Actions output;
- Codex/ChatGPT QA comments on the PR;
- Project Governor / Context Auditor comments on the PR;
- explicit review artifacts under `docs/reviews/`.

When a session ends, the durable artifacts above are sufficient to restart the loop in a new session without information loss. When a session begins, those artifacts are sufficient to bring the new session up to speed.

This discipline is not just a context-budget tactic. It is what makes the loop resumable across days, across agents, and across people.

---

## 12. Artifact-first handoffs

Every major loop stage produces or consumes explicit artifacts or durable GitHub records. No Builder, QA Reviewer, or Project Governor / Context Auditor session relies on prior chat memory as source of truth.

Examples of stage artifacts:

- `task_packet.md` — the input to Builder planning;
- `builder_plan.md` — the Builder's plan, produced before code;
- `governor_plan_review.md` — the Project Governor / Context Auditor's plan-review verdict;
- `test_results.md` — the GitHub Actions output;
- `codex_qa_review.md` — the QA Reviewer's PR review;
- `fix_packet.md` — the input to a Builder fix;
- `governor_post_fix_drift_check.md` — the Project Governor / Context Auditor's post-fix drift review;
- `final_pr_approval_brief.md` — the Project Governor / Context Auditor's pre-merge brief;
- `failure_escalation_packet.md` — the packet produced when the loop hits a failure limit.

In practice, several of these live as PR comments rather than as standalone files; the requirement is that they are durable, addressable, and copy-pasteable into a fresh session, not that they are necessarily separate markdown files. Artifacts that need to persist beyond the PR's life are stored under `docs/reviews/` per EW §2.2 and §9.

---

## 13. Structured gate outputs

Project Governor / Context Auditor decisions are structured, not vague. Every gate decision uses a structured pattern such as:

```
gate_result:               pass | revise | blocked
risk_tier:                 tier0 | tier1 | tier2 | tier3
requires_jeremy:           true | false
token_estimate:            <number>
latest_commit_sha_reviewed: <string>
blocking_reasons:          [<list of short structured reasons>]
required_next_step:        <one of: revise_plan | implement | rerun_tests |
                                    apply_fix | qa_recheck | governor_recheck |
                                    human_approval | escalate>
```

Free-form "looks fine to me" or "I have some concerns" responses are not gate decisions. The runbook (§17) provides example comments for the common gate verdicts.

---

## 14. Risk-tiered execution paths

Not every task carries the same risk. Forcing a typo fix and a feature-calculator implementation through the same heavyweight loop teaches the team to ignore the loop. The workflow defines four risk tiers; the Project Governor / Context Auditor classifies every task before the Builder plans it.

### Tier 0 — Trivial / mechanical

Examples:

- typo fixes;
- formatting-only changes;
- non-behavioral comments;
- documentation wording that does not affect requirements or process.

Allowed path:

- allowed-files check;
- no full Project Governor / Context Auditor loop required unless touching governed documents;
- no Codex/ChatGPT QA required unless requested.

Not allowed under Tier 0:

- no code behavior changes;
- no schema changes;
- no tests changed;
- no config changes;
- no financial / feature / target / model / backtest logic changes.

A task that touches any forbidden category is reclassified upward.

### Tier 1 — Low-risk implementation

Examples:

- adding tests for already-approved behavior;
- a small helper inside an approved module;
- fixture cleanup;
- logging improvement.

Required path:

- task packet verification;
- lightweight plan;
- GitHub Actions tests;
- Project Governor / Context Auditor post-check;
- Codex/ChatGPT QA optional based on file impact.

### Tier 2 — Standard governed implementation

Examples:

- implementing an approved schema;
- implementing approved config validation;
- implementing an approved feature calculator;
- implementing an approved provider abstraction method.

Required path:

- full task packet;
- Project Governor / Context Auditor plan validation;
- Claude implementation;
- GitHub Actions tests;
- Codex/ChatGPT QA;
- Project Governor / Context Auditor post-QA drift check;
- fix loop with QA re-review and Project Governor / Context Auditor post-fix check;
- Jeremy final PR approval.

### Tier 3 — High-risk / approval-sensitive

Examples:

- financial calculations;
- feature definitions;
- target labels;
- model logic;
- backtest logic;
- portfolio rules;
- schema changes beyond the exact approved spec;
- universe / benchmark / sleeve / eligibility logic;
- strategy-affecting YAML.

Required path:

- full Tier 2 path;
- independent QA test plan produced before reviewing Builder implementation;
- stricter Project Governor / Context Auditor drift review;
- Jeremy escalation if any ambiguity appears.

When in doubt, the Project Governor / Context Auditor classifies upward. A task wrongly classified as Tier 1 that turns out to be Tier 2 wastes a fix loop; a task wrongly classified as Tier 2 that turns out to be Tier 3 risks merging strategy-affecting change without the right review.

---

## 15. Global Phase 1 invariants

Every Builder and QA Reviewer packet — regardless of risk tier — includes the Phase 1 invariants. They are non-negotiable for the duration of Phase 1 and cannot be silently relaxed by any agent:

- Phase 1 is ETF tactical research only.
- No live trading.
- No real broker adapters.
- No individual stocks.
- No fundamentals, ETF holdings, news, earnings, options, Danelfin, autonomous research agents, or commercial / customer-facing features.
- EODHD access is provider-layer only.
- No feature, model, backtest, or portfolio module may call EODHD directly.
- Postgres is the system of record.
- MLflow is tracking only, not the system of record.
- `adjusted_close` is the canonical research price.
- `data_snapshot_id` is the reproducibility anchor.
- No strategy-affecting assumption may be made silently.
- If a requirement conflicts with the SDR, the Engineering Workflow, an approved engineering_spec section, or the traceability matrix, stop and escalate.

---

## 16. Task packet requirements

Every implementation task packet includes:

- task ID;
- task title;
- task type (e.g., implementation, test addition, refactor, fix);
- risk tier (Tier 0 / Tier 1 / Tier 2 / Tier 3);
- Builder or QA Reviewer role;
- canonical source-of-truth hierarchy (SDR → EW → approved engineering_spec sections → traceability matrix → approval notes);
- relevant SDR decision numbers;
- relevant Engineering Specification section excerpts;
- relevant traceability matrix rows;
- allowed files to edit;
- forbidden files to edit;
- in-scope behavior;
- out-of-scope behavior;
- required tests;
- expected commands (e.g., `docker compose exec app pytest tests/...`);
- stop conditions specific to the task;
- context budget estimate;
- prior QA comments, if this is a fix loop.

A packet missing any of the above is incomplete and is not authorized for use. The Project Governor / Context Auditor either fills the gaps or rejects the packet.

---

## 17. Plan validation

Claude Code Builder drafts a plan *before* coding. The Project Governor / Context Auditor validates the plan before code exists.

Human plan review is not required for routine tasks. Human review is required only if the Project Governor / Context Auditor detects:

- an approval-gate item;
- an unresolved assumption;
- an SDR conflict;
- an Engineering Specification conflict;
- a traceability conflict;
- a token-budget exception;
- repeated loop failure;
- scope drift;
- a schema, financial, feature, target, or label change requiring approval.

If the plan is wrong but fixable within scope, the Project Governor / Context Auditor requests a revised plan from the Builder rather than rejecting the task. Spec sections are inexpensive to fix in draft and expensive to fix after coding begins; plans are inexpensive to fix before code exists and expensive to fix after.

If the plan hits a stop condition, the issue/PR is labeled appropriately (see runbook §4) and routed to Jeremy.

---

## 18. Required loop order

The required loop order is:

1. Trigger GitHub Issue / task.
2. Project Governor / Context Auditor creates or verifies the task packet.
3. Project Governor / Context Auditor checks the input context budget.
4. Project Governor / Context Auditor classifies task risk tier.
5. Claude Code Builder drafts an implementation plan only.
6. Project Governor / Context Auditor validates the plan against the SDR, the Engineering Workflow, approved engineering_spec sections, the traceability matrix, the task packet, the allowed-files and forbidden-files lists, and the stop conditions.
7. If the plan fails but is fixable, Claude Code Builder revises the plan.
8. If the plan hits a stop condition, the task is blocked and routed to Jeremy.
9. If the plan passes, Claude Code Builder implements on a branch / PR.
10. GitHub Actions runs deterministic tests.
11. Codex/ChatGPT QA Reviewer reviews the actual PR diff against the task packet, relevant specs, relevant SDR decisions, and test output.
12. Project Governor / Context Auditor performs the post-QA drift review.
13. If tests or QA identify safe, in-scope issues, Claude Code Builder applies fixes in the same PR.
14. GitHub Actions rerun.
15. Codex/ChatGPT QA Reviewer re-reviews the updated PR diff.
16. Project Governor / Context Auditor performs the post-fix drift review.
17. Steps 13–16 repeat only within configured loop limits.
18. If the loop passes all gates, the PR is labeled `ai:ready-for-human-approval`.
19. Jeremy performs the final PR approval and merge.

The Project Governor / Context Auditor begins the loop, not the Builder. The Builder's first action in the loop is *plan*, not *code*.

---

## 19. Post-fix validation rule

Claude Code Builder fixes may not proceed directly to Jeremy final PR approval. Every Builder fix goes through the full post-fix validation chain:

1. Claude Code Builder applies the fix in the same PR.
2. GitHub Actions rerun deterministic checks.
3. Codex/ChatGPT QA Reviewer re-reviews the updated PR diff against the task packet, relevant specs, relevant SDR decisions, and the test output.
4. Project Governor / Context Auditor performs a post-fix drift check against full project controls.
5. Only if tests pass, QA has no unresolved blocking findings, and the Project Governor / Context Auditor finds no unresolved drift or approval-gate item may the PR be labeled `ai:ready-for-human-approval`.

Claude Code Builder may not self-certify a fix as safe.

Claude Code Builder may not move a PR directly to human approval after applying a fix.

This rule exists because the most likely time for a regression to slip through is *after* a fix that "looks small." Self-certified fixes are the most common cause of "the tests passed but the merge was wrong."

---

## 20. Latest-commit validation

A PR may not be labeled `ai:ready-for-human-approval` unless all required checks were performed against the **latest PR commit SHA**:

- GitHub Actions tests;
- Codex/ChatGPT QA review or re-review;
- Project Governor / Context Auditor post-QA or post-fix drift check.

If Claude pushes any new commit after QA or Project Governor / Context Auditor review, the PR returns to:

GitHub Actions → Codex/ChatGPT QA re-review → Project Governor / Context Auditor post-fix drift check.

The check chain is per-commit, not per-PR. A "near-miss" in which the gates passed against an earlier commit and a quick follow-up commit slipped through is exactly the failure mode this rule blocks.

---

## 21. Codex/ChatGPT QA Reviewer responsibilities

Codex/ChatGPT QA Reviewer reviews the actual PR diff against:

- the approved task packet;
- the relevant SDR decisions;
- the relevant Engineering Specification sections;
- the relevant traceability matrix rows;
- the GitHub Actions test output;
- the allowed-files and forbidden-files constraints.

Codex/ChatGPT reviews the artifact / diff, not Claude's summary. If Claude's summary conflicts with the diff, the diff controls (consistent with EW §9: "review the artifact, not the summary").

Codex/ChatGPT QA must check for:

- scope drift;
- missing tests;
- weak tests that only verify mechanics instead of financial meaning;
- forbidden file edits;
- provider-boundary violations;
- look-ahead bias;
- unapproved schema changes;
- unapproved strategy-affecting config changes;
- unapproved feature / target / label changes;
- hidden assumptions;
- live-trading or broker-integration risk;
- secrets or credentials committed to the repo;
- failure to update traceability when required.

A QA pass is *pass*, *pass-with-comments*, or *fail*, consistent with the EW QA checklist verdicts.

---

## 22. Independent QA test plan for Tier 2 and Tier 3

For Tier 2 and Tier 3 work, Codex/ChatGPT QA produces or validates an Independent Test Plan from the task packet and approved specs. The QA Reviewer answers:

- What tests should exist if this implementation is correct?
- Are those tests present?
- Do they test financial meaning, not just mechanics (consistent with EW §5)?
- Do they fail for the right wrong reasons?
- Are integration contracts tested where needed?

The Independent Test Plan is produced from the task packet and approved specs, *before* deeply inspecting the Builder's tests, so that the Plan is not biased by the Builder's choices. The QA Reviewer then compares the Plan to the Builder's actual tests and notes gaps.

---

## 23. Post-QA and post-fix drift checks

After Codex/ChatGPT QA completes, the Project Governor / Context Auditor compares:

- the PR diff;
- QA findings;
- test output;
- the task packet;
- approved specs;
- the traceability matrix;
- the allowed-files and forbidden-files list;
- the stop conditions.

The Project Governor / Context Auditor blocks the PR if there is unresolved drift, missing traceability, missing required tests, forbidden file changes, or any approval-gate issue.

This drift check occurs after initial QA and again after every Builder fix. The post-fix drift check is not optional — it is the rule in §20 (latest-commit validation) cashed out at the drift level.

---

## 24. Drift prevention controls

The workflow's drift-prevention controls are not one big check at the end. They are layered throughout the loop:

- canonical source paths only — the source-of-truth hierarchy is referenced by repo path, not paraphrased into a session;
- task IDs — every Builder, QA, and Project Governor / Context Auditor session is tied to a task ID and a PR;
- allowed-files / forbidden-files discipline — the diff scope is bounded explicitly, not by Builder discretion;
- no editing locked docs unless explicitly authorized — locked SDR, EW, and approved engineering_spec sections are forbidden by default;
- context-budget check before every Builder and QA Reviewer session;
- fresh-context session discipline (§11);
- artifact-first handoffs (§12);
- structured gate outputs (§13);
- deterministic checks before LLM judgment (§9);
- traceability check before and after implementation;
- QA reviews artifact / diff, not Builder summary;
- Project Governor / Context Auditor reviews plan before code exists;
- Codex/ChatGPT QA reviews PR diff before fixes;
- Codex/ChatGPT QA re-reviews PR diff after fixes;
- Project Governor / Context Auditor reviews PR before final Jeremy approval;
- latest-commit SHA validation;
- end-of-section reconciliation (the traceability matrix is updated as part of finalizing each spec section, per EW §3.6);
- drift ledger entry for possible deviations (when the drift ledger is later created — see §26).

---

## 25. Failure escalation packet

After repeated failure, the loop stops and produces a Failure Escalation Packet instead of continuing AI retries. Trigger conditions:

- the same failure repeats after 2 attempts;
- maximum Builder fix attempts reached;
- maximum QA / fix cycles reached;
- unresolved spec conflict;
- unresolved scope conflict;
- unclear financial / feature / target / schema behavior.

The Failure Escalation Packet includes:

- task ID;
- original goal;
- risk tier;
- files changed;
- reduced diff summary;
- tests failing;
- QA blocking findings;
- Project Governor / Context Auditor blocking findings;
- what Claude attempted;
- what changed between attempts;
- likely cause;
- decision needed from Jeremy.

The packet is the loop's exit hatch. Its existence is what prevents an AI fix loop from running forever.

---

## 26. Drift ledger policy

A future artifact at `docs/drift_ledger.md` will record possible deviations between implementation and the source-of-truth hierarchy. **This document does not create that file.**

When the drift ledger is later created, it will record:

- date;
- task ID;
- affected files;
- affected SDR decision;
- affected spec section;
- possible drift description;
- classification (rejected / deferred / approved / requires amendment);
- Jeremy approval status;
- resolution notes or links.

Until the drift ledger exists, drift events are recorded as comments on the relevant PR or Issue, and as approval notes under `docs/reviews/` if the drift is material enough to warrant a separate artifact.

---

## 27. Implementation task manifest policy

A future artifact at `docs/implementation_tasks.yaml` will catalog implementation tasks. **This document does not create that file.**

When the manifest is later created, it will contain:

- task IDs;
- module names;
- controlling spec sections;
- relevant SDR decisions;
- risk tier;
- allowed files;
- forbidden files;
- required tests;
- stop conditions;
- context budget estimate;
- status.

Until the manifest exists, tasks live as GitHub Issues with the task packet attached. A GitHub Issue *is* a task entry; the manifest, when added, is a structured index over the Issues, not a replacement for them.

---

## 28. Future reusable tooling extraction

After the Governor-Gated GitHub PR Agent Loop has been tested successfully inside `quant-research-platform`, generic tooling may later be extracted into a separate reusable repository. **This document does not create that repository.**

If such a repository is created later, it would contain generic scripts and templates only:

- token-budget checker;
- allowed-files checker;
- forbidden-import scanner;
- latest-commit SHA checker;
- reusable GitHub Actions templates;
- reusable task packet templates.

It would not contain:

- this project's SDR;
- this project's engineering specs;
- this project's traceability matrix;
- this project's project-specific decisions;
- this project's Phase 1 ETF constraints.

The clean separation is:

- *Reusable tooling repo, later:* how to run the loop.
- *`quant-research-platform` repo, now and ongoing:* what the loop must enforce.

The decision to extract reusable tooling is a future Jeremy decision, not implied by this document.

---

## 29. Stop conditions

The Project Governor / Context Auditor, the Builder, or the QA Reviewer must stop and escalate to Jeremy if any task:

- changes or conflicts with the SDR;
- changes or conflicts with a locked Engineering Specification section;
- changes financial calculations;
- changes feature, target, or label definitions;
- changes ETF universe, benchmark, sleeve, or eligibility rules;
- changes schema beyond the approved spec;
- changes model promotion logic;
- changes broker / order-intent behavior;
- introduces live-trading risk;
- modifies strategy-affecting YAML;
- exceeds the token budget;
- requires assumptions not already resolved;
- repeats the same failed loop more than the configured maximum attempt count;
- produces unresolved QA blocking findings;
- attempts to route Claude's self-certified fix directly to Jeremy.

A stop condition is not a defect in the workflow. It is the workflow doing its job. The right response to a stop condition is to label the issue/PR appropriately (see runbook §4) and hand the decision to Jeremy.

---

## 30. Authority model

Only Jeremy can approve:

- SDR changes;
- locked spec amendments;
- merges;
- strategy-affecting changes;
- schema changes beyond approved specs;
- financial calculation changes;
- feature, target, or label definition changes;
- model promotion;
- scope changes;
- token-budget exceptions above 70k input tokens.

The Project Governor / Context Auditor, the Builder, the QA Reviewer, and any future agentic loop have no authority over the items above. These are reserved for the Approver, consistent with the EW Approval Matrix (EW §2.3).

---

**End of document.**
