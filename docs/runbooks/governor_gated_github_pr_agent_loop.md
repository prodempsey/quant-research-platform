# Governor-Gated GitHub PR Agent Loop — Runbook

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v1.0 APPROVED
**Approval:** Jeremy Dempsey, 2026-04-29
**Date:** 2026-04-29
**Document type:** Practical operating procedure. Documentation only — no implementation, no scripts, no GitHub Actions workflow files, no separate repository.
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification sections under `docs/engineering_spec/`
- `docs/traceability_matrix.md`
- Approval notes and review artifacts under `docs/reviews/`
- Policy layer: `docs/implementation_context_governance.md`

---

## 1. Purpose

This runbook tells Jeremy how to use the Governor-Gated GitHub PR Agent Loop during implementation. The companion document `docs/implementation_context_governance.md` is the *policy layer* (what the workflow must enforce); this runbook is the *operating procedure* (how it's actually run, day to day).

If something here is unclear, the policy layer controls. If the policy layer and this runbook conflict, the policy layer controls. If either conflicts with the SDR or the Engineering Workflow, the SDR and EW control.

---

## 2. When to use this runbook

Use this runbook when **all** of the following are true:

- the relevant Engineering Specification section is approved and committed under `docs/engineering_spec/`;
- the traceability matrix has been updated to reflect that section;
- implementation has been authorized by Jeremy for the section in question;
- a GitHub Issue with a task packet exists for the specific task at hand.

Do **not** use this runbook for:

- spec drafting (use the EW §3 workflow instead);
- ad-hoc one-off scripts unrelated to the implementation phase;
- documentation-only changes that do not affect any approved spec section, locked governance document, traceability row, or Phase 1 invariant (those follow the lighter Tier 0 path described in §7).

---

## 3. Roles

- **Jeremy (Approver)** — final approver, merge authority, stop-condition decision-maker.
- **Project Governor / Context Auditor** — task packet creator / verifier, context-budget manager, deterministic guardrail checker, plan validator, drift checker, traceability checker, stop-condition router. Hybrid control layer (deterministic checks first, LLM-assisted semantic review second). No implementation, no merge, no approval authority.
- **Claude Code GitHub Actions (Builder)** — drafts plans, writes code, applies fixes inside the same PR. Does not self-certify fixes. Does not move PRs to human approval.
- **Codex/ChatGPT (QA Reviewer)** — independent reviewer of the actual PR diff against the task packet, relevant approved specs, relevant SDR decisions, and the GitHub Actions test output.
- **GitHub Actions (deterministic test runner)** — runs pytest, ruff, migration tests, and any other CI checks defined for the relevant module.

The role boundaries from the policy layer (§7) are not negotiable. No agent has end-to-end authority.

---

## 4. Label / state model

Recommended GitHub labels for tracking state. The labels are not magic — they are a shared vocabulary so a fresh session can read the issue/PR and know exactly where the loop stands.

**Loop progression:**

- `ai:ready-for-plan`
- `ai:plan-drafted`
- `ai:plan-approved-by-governor`
- `ai:build-in-progress`
- `ai:ready-for-tests`
- `ai:tests-failed`
- `ai:ready-for-qa`
- `ai:qa-failed`
- `ai:fix-requested`
- `ai:fix-applied`
- `ai:ready-for-qa-recheck`
- `ai:qa-recheck-passed`
- `ai:ready-for-governor-review`
- `ai:governor-recheck-passed`
- `ai:ready-for-human-approval`

**Blocking:**

- `blocked:jeremy-decision`
- `blocked:scope-conflict`
- `blocked:spec-conflict`
- `blocked:token-budget`
- `blocked:repeated-failure`

A PR carries at most one progression label and at most one blocking label at a time. Stale labels are removed when the state advances.

---

## 5. Standard loop

The standard loop, in compressed form:

```
Trigger
  → Project Governor / Context Auditor creates or verifies task packet
  → Project Governor / Context Auditor checks token budget
  → Project Governor / Context Auditor classifies risk tier
  → Claude drafts plan
  → Project Governor / Context Auditor validates plan
  → Claude implements (if plan passes)
  → GitHub Actions runs tests
  → Codex/ChatGPT reviews PR diff
  → Project Governor / Context Auditor performs post-QA drift review
  → Claude fixes only safe, in-scope issues (if any)
  → GitHub Actions rerun
  → Codex/ChatGPT re-reviews updated PR diff
  → Project Governor / Context Auditor performs post-fix drift review
  → repeat fix loop within configured limits
  → stop / escalate if approval gate triggered
  → Jeremy approves final PR
  → merge
```

This is the same loop in policy layer §18, presented procedurally. See §6 for the step-by-step procedure.

---

## 6. Step-by-step procedure

**Step 1 — Create GitHub Issue from task packet.** The task packet (see §9 and §16) is the Issue body. The Issue title carries the task ID and a short title.

**Step 2 — Project Governor / Context Auditor creates or verifies the task packet.** All required fields populated; canonical paths only; no paraphrased SDR or EW content.

**Step 3 — Project Governor / Context Auditor checks context budget.** Estimate input tokens. If above 70k, label `blocked:token-budget` and route to Jeremy. If above 80k, the task should normally be split.

**Step 4 — Project Governor / Context Auditor classifies risk tier.** Tier 0 / 1 / 2 / 3 per §7 (and policy layer §14). Classification is recorded in the Issue.

**Step 5 — Label issue `ai:ready-for-plan`.**

**Step 6 — Claude drafts implementation plan only.** No code yet. The plan references the approved spec section, the SDR decisions involved, the allowed files, the required tests, and the expected commands. Label moves to `ai:plan-drafted`.

**Step 7 — Project Governor / Context Auditor validates plan.** Against the SDR, the EW, the approved engineering_spec sections, the traceability matrix, the task packet, and the allowed/forbidden file lists. Structured gate output (policy layer §13).

**Step 8 — If plan fails but is fixable, Project Governor / Context Auditor requests revised plan.** Label remains `ai:plan-drafted`. Claude revises within the same Issue thread.

**Step 9 — If plan hits a stop condition, label appropriately.** `blocked:jeremy-decision`, `blocked:scope-conflict`, `blocked:spec-conflict`, `blocked:token-budget`, or `blocked:repeated-failure`. Routed to Jeremy.

**Step 10 — If plan passes, label `ai:plan-approved-by-governor`.**

**Step 11 — Claude implements on a branch / PR.** Single PR per task. Label moves to `ai:build-in-progress`.

**Step 12 — GitHub Actions runs tests.** Label moves to `ai:ready-for-tests`. On pass, label moves to `ai:ready-for-qa`. On fail, label moves to `ai:tests-failed`.

**Step 13 — If tests fail, Claude receives a fix packet.** Bounded to the failing tests and the safe, in-scope fix. No scope expansion. See §19 for the fix-loop instruction template.

**Step 14 — Codex/ChatGPT reviews PR diff.** Against the artifact, not Claude's summary. Findings are pass / pass-with-comments / fail. On clean pass, label moves to `ai:ready-for-governor-review`. On findings, label moves to `ai:qa-failed`.

**Step 15 — Project Governor / Context Auditor performs post-QA drift check.** Compares PR diff, QA findings, test output, task packet, approved specs, traceability matrix, allowed/forbidden file list, and stop conditions.

**Step 16 — If QA fails or tests fail but the issue is safe / in-scope, Claude receives fix packet.** Label moves to `ai:fix-requested`.

**Step 17 — Claude applies fix in the same PR.** No new PR per fix. Label moves to `ai:fix-applied`.

**Step 18 — GitHub Actions rerun.**

**Step 19 — Codex/ChatGPT re-reviews updated PR diff.** Against the latest commit SHA. Label moves to `ai:ready-for-qa-recheck` then `ai:qa-recheck-passed` on clean pass.

**Step 20 — Project Governor / Context Auditor performs post-fix drift check.** Against the latest commit SHA. Label moves to `ai:governor-recheck-passed` on clean pass.

**Step 21 — Repeat fix loop only within configured loop limits.** See §8.

**Step 22 — If repeated failure occurs, generate a Failure Escalation Packet.** Label `blocked:repeated-failure`. See §20 for the template.

**Step 23 — If clean, label `ai:ready-for-human-approval`.**

**Step 24 — Jeremy reviews and merges.** Final PR approval brief from the Project Governor / Context Auditor is attached. Jeremy's review is reading the brief and the diff, not redoing the loop.

---

## 7. Risk-tier quick reference

Mirror of policy layer §14, condensed.

**Tier 0 — Trivial / mechanical.** Typo fixes; formatting; non-behavioral comments; documentation wording that does not affect requirements or process. Allowed-files check; no full Project Governor / Context Auditor loop unless touching governed documents; no Codex/ChatGPT QA unless requested. Not allowed: code behavior changes, schema changes, test changes, config changes, financial / feature / target / model / backtest logic changes.

**Tier 1 — Low-risk implementation.** Adding tests for already-approved behavior; small helper inside an approved module; fixture cleanup; logging improvement. Required: task packet verification; lightweight plan; GitHub Actions tests; Project Governor / Context Auditor post-check. Codex/ChatGPT QA optional based on file impact.

**Tier 2 — Standard governed implementation.** Implementing an approved schema; implementing approved config validation; implementing an approved feature calculator; implementing an approved provider abstraction method. Required: full task packet; plan validation; Claude implementation; GitHub Actions tests; Codex/ChatGPT QA; Project Governor / Context Auditor post-QA drift check; fix loop with QA re-review and post-fix check; Jeremy final PR approval.

**Tier 3 — High-risk / approval-sensitive.** Financial calculations; feature definitions; target labels; model logic; backtest logic; portfolio rules; schema changes beyond exact approved spec; universe / benchmark / sleeve / eligibility logic; strategy-affecting YAML. Required: full Tier 2 path; independent QA test plan before reviewing Builder implementation; stricter drift review; Jeremy escalation if any ambiguity appears.

When in doubt, classify upward.

---

## 8. Loop limits

- Maximum Builder fix attempts: **3**.
- Maximum QA / fix cycles: **2**.
- Same failure repeats after **2** attempts → label `blocked:repeated-failure`.
- Token-budget breach → label `blocked:token-budget`.
- Approval-gate issue → label `blocked:jeremy-decision`.
- Unresolved SDR / spec conflict → label `blocked:spec-conflict`.
- Unresolved scope conflict → label `blocked:scope-conflict`.

When a loop limit fires, the loop *stops*. The next action is generating a Failure Escalation Packet (§20), not "one more retry."

---

## 9. Context packet requirements at loop start

Before Claude drafts a plan, the Project Governor / Context Auditor creates or verifies a task packet containing:

- task ID;
- task title;
- risk tier;
- relevant SDR decisions;
- relevant EW requirements;
- relevant engineering_spec excerpts;
- relevant traceability matrix rows;
- allowed files;
- forbidden files;
- required tests;
- stop conditions;
- token estimate;
- prior QA comments if applicable.

The packet must not exceed **70k input tokens** unless Jeremy manually approves.

If a section reads "see SDR" without specifying which decision, the packet is incomplete. If a section reads "see Section 3a" without specifying which subsection, the packet is incomplete. Canonical paths and decision numbers, not paraphrases.

---

## 10. What the Project Governor / Context Auditor checks before coding

Checklist applied at plan-validation time:

- task packet exists;
- task packet uses canonical repo paths;
- token estimate is ≤ 70k input tokens, unless Jeremy approved an exception;
- risk tier classification is present;
- plan matches task packet;
- plan references correct SDR decisions;
- plan references correct spec section;
- files to edit are allowed;
- forbidden files are untouched;
- required tests are included;
- no hidden assumptions;
- no scope expansion;
- no token-budget breach;
- no approval-gate item is being bypassed.

A failure on any item is a *revise plan* or *blocked* verdict, not a *pass with comments*.

---

## 11. What Codex/ChatGPT checks during QA

Checklist applied at PR-diff review time:

- diff implements the approved spec;
- diff matches the task packet;
- tests are present and meaningful;
- financial meaning is tested, not just mechanics;
- no provider logic outside the provider layer;
- no look-ahead bias;
- no unapproved schema change;
- no forbidden dependencies;
- no secrets;
- no live-trading path;
- no forbidden file edits;
- no hidden assumptions;
- no skipped traceability requirements.

Codex/ChatGPT reviews the diff, not Claude's PR summary. If the summary and the diff conflict, the diff wins.

---

## 12. Independent QA test plan

For Tier 2 and Tier 3 work, Codex/ChatGPT QA produces or validates an Independent Test Plan *before* finalizing QA. The plan answers:

- What tests should exist?
- Are they present?
- Do they test financial meaning?
- Do they test integration contracts?
- Do they fail for the correct wrong reasons?

The Plan is produced from the task packet and the approved spec, not from the Builder's tests. The QA Reviewer then compares the Plan to the Builder's tests and notes gaps. A Builder test suite that *only* matches the Builder's own assumptions is exactly what this plan exists to catch.

---

## 13. What the Project Governor / Context Auditor checks after QA

Checklist applied at post-QA drift-review time:

- GitHub Actions pass or failures are classified;
- QA blocking comments are captured;
- PR diff is compared against the task packet;
- allowed/forbidden file boundaries respected;
- no unresolved approval-gate item;
- no drift from the SDR, the EW, the approved specs, or the traceability matrix;
- the fix loop is allowed only if the issue is safe and in scope.

If anything fails, the PR does not advance. A safe, in-scope fix is requested via a fix packet (§19). An unsafe or scope-expanding finding is escalated.

---

## 14. What happens after Claude fixes

Every Claude fix follows this sequence:

1. Claude applies the fix in the same PR.
2. GitHub Actions rerun.
3. Codex/ChatGPT re-reviews the updated PR diff.
4. Project Governor / Context Auditor performs the post-fix drift check.
5. The PR may advance only if tests pass, QA has no blocking findings, and the Project Governor / Context Auditor confirms no unresolved drift or approval-gate issue.

Claude may not self-certify a fix. Claude may not move the PR directly to Jeremy. Claude may not bypass QA re-review.

This is policy layer §19 cashed out procedurally. The most common failure mode the policy is built to prevent — "small fix, no need to re-review" — is exactly what this checklist blocks.

---

## 15. What the Project Governor / Context Auditor checks before human approval

Final checklist applied before labeling `ai:ready-for-human-approval`:

- GitHub Actions pass;
- Codex/ChatGPT QA has no unresolved blocking comments;
- post-fix QA re-review completed after the most recent Claude fix;
- post-fix Project Governor / Context Auditor drift check completed after the most recent Claude fix;
- latest PR commit SHA was reviewed (per policy layer §20);
- allowed/forbidden file boundaries respected;
- traceability row status updated if required;
- no drift-ledger unresolved issues (when the drift ledger exists; until then, no unresolved drift comments on the PR);
- no approval-gate item bypassed;
- PR summary matches actual diff;
- artifact / diff wins over summary.

The output of this step is the *final PR approval brief* (policy layer §6, §13). The brief is what Jeremy actually reads at the merge gate.

---

## 16. Example task packet

A hypothetical Tier 2 task. The example assumes Section 2 is locked (it is) and that the Approver has authorized initial data-layer implementation (this remains a future authorization).

```
Task ID:        FEATURES-001
Task title:     Implement features schema migration
Task type:      Implementation
Risk tier:      Tier 2

Builder role:   Claude Code Builder
Reviewer role:  Codex/ChatGPT QA Reviewer

Source-of-truth hierarchy:
  1. docs/strategy_decision_record.md (v1.0 LOCKED)
  2. docs/engineering_workflow.md (v1.5 LOCKED)
  3. docs/engineering_spec/01_architecture_overview.md (v1.0 LOCKED)
  4. docs/engineering_spec/02_data_layer.md (v1.0 LOCKED)
  5. docs/engineering_spec/03a_feature_engineering.md (v1.0 LOCKED / APPROVED)
  6. docs/traceability_matrix.md (current state)

Relevant SDR decisions:
  - Decision 11 (data quality / MLOps storage)
  - Decision 16 (bias controls — reproducibility chain)
  - Decision 2 (provider boundary — features/ writes only to features.*,
    never to providers/* or ops.* outside the read paths Section 3a allows)

Relevant Engineering Specification excerpts:
  - 03a §6.3 features.feature_runs schema
  - 03a §6.4 features.feature_definitions schema
  - 03a §6.5 features.feature_values schema
  - 03a §6.6 features.feature_run_issues schema
  - 03a §6.8 data_snapshot_id linkage

Relevant traceability matrix rows:
  - Decision 2 (in spec; extended by 03a)
  - Decision 5 (in spec, universe-side and benchmark-relative feature side)
  - Decision 11 (in spec)
  - Decision 16 (in spec)

Allowed files to edit:
  - migrations/forward/0002_add_features_schema.sql
  - migrations/reverse/0002_add_features_schema.sql
  - tests/unit/architecture/test_features_schema_migration.py
  - tests/integration/architecture/test_features_schema_roundtrip.py
  - .env.example (only if a new variable is needed; otherwise no change)
  - docs/traceability_matrix.md (only if a row's status changes from
    "in spec" to "in build")

Forbidden files to edit:
  - docs/strategy_decision_record.md
  - docs/engineering_workflow.md
  - docs/engineering_spec/**  (all locked spec sections)
  - docs/reviews/**  (approval notes are immutable)
  - migrations/forward/0001_*.sql  (already applied)
  - migrations/reverse/0001_*.sql  (already applied)
  - any file outside the explicit allowed list

In-scope behavior:
  - Create the four features.* tables exactly as specified in 03a §6.3-§6.6.
  - Apply the UNIQUE (feature_run_id, feature_set_version) constraint on
    features.feature_runs.
  - Apply the two composite FKs on features.feature_values:
    (feature_run_id, feature_set_version) → features.feature_runs(...);
    (feature_set_version, feature_name) → features.feature_definitions(...).
  - Apply indexes per 03a §6.5 and §6.6.
  - Provide forward and reverse migration files; both must apply cleanly.

Out-of-scope behavior:
  - No calculator code. (Separate task.)
  - No config/features.yaml. (Separate task.)
  - No MLflow integration. (Section 3c.)
  - No targets.* tables. (Section 3b.)
  - No models.* tables. (Section 3c.)
  - No changes to ops.*, universe.*, prices.*.

Required tests:
  - Schema migration test: forward applies cleanly to fresh DB; reverse
    rolls back to empty features schema.
  - UNIQUE constraint test on features.feature_runs(feature_run_id,
    feature_set_version) — duplicate rejected.
  - Composite FK test (run linkage) on features.feature_values: insert
    with mismatched (feature_run_id, feature_set_version) → DB rejection.
  - Composite FK test (definition linkage) on features.feature_values:
    insert with feature_name not in features.feature_definitions for the
    active feature_set_version → DB rejection.
  - Index presence test (each index in §6.5 and §6.6).

Expected commands:
  - docker compose exec app pytest tests/unit/architecture/test_features_schema_migration.py
  - docker compose exec app pytest tests/integration/architecture/test_features_schema_roundtrip.py
  - ruff check .
  - ruff format --check .

Stop conditions specific to this task:
  - Any change to ops.*, universe.*, prices.* schema → stop.
  - Any change to a locked spec section → stop.
  - Any new feature calculator code → stop.
  - Any change to config/features.yaml shape beyond what 03a requires → stop.
  - Any change to the feature_run_issues issue_type or severity enumerations → stop.

Context budget estimate:
  ~38k input tokens
  (SDR full text ~22k, EW relevant sections ~6k, 03a §6 only ~5k,
   traceability matrix relevant rows ~2k, task packet itself ~3k)

Prior QA comments: (none — this is the initial loop)

Project Governor / Context Auditor plan-review checklist:
  [ ] Plan touches only the allowed files
  [ ] Plan does not touch any forbidden file
  [ ] Plan implements 03a §6.3-§6.6 exactly (no extra columns, no missing columns)
  [ ] Plan includes all required tests
  [ ] Plan includes both forward and reverse migration files
  [ ] Plan does not introduce CREATE DATABASE or CREATE ROLE in migrations
  [ ] Plan does not modify ops.*, universe.*, prices.* schema
  [ ] Plan does not introduce calculator code
  [ ] Plan does not modify any approved spec section
  [ ] Token estimate is ≤ 70k input tokens
```

The packet is long because this is a Tier 2 task. A Tier 1 packet is shorter; a Tier 0 packet may be just a few lines.

---

## 17. Example Project Governor / Context Auditor plan-review comments

The structured gate-output pattern from policy layer §13. Each example is a comment posted on the GitHub Issue or PR.

### Example 17.1 — Pass

```
gate_result:               pass
risk_tier:                 tier2
requires_jeremy:           false
token_estimate:            38000
latest_commit_sha_reviewed: (n/a — plan-review stage, no commits yet)
blocking_reasons:          []
required_next_step:        implement

Notes:
  Plan implements 03a §6.3-§6.6 exactly. Forward and reverse migrations
  both included. Required tests present. Allowed-files boundary respected.
  No drift from SDR / EW / approved specs / traceability matrix.
  Cleared to proceed to implementation. Label moved to
  ai:plan-approved-by-governor.
```

### Example 17.2 — Revise plan (fixable inside scope)

```
gate_result:               revise
risk_tier:                 tier2
requires_jeremy:           false
token_estimate:            38000
latest_commit_sha_reviewed: (n/a — plan-review stage, no commits yet)
blocking_reasons:
  - "Plan adds a column `notes text` to features.feature_values that is
     not in 03a §6.5; 03a §6.5 lists the exact columns and `notes` is not
     among them."
  - "Plan omits the index on features.feature_run_issues (etf_id, as_of_date)
     required by 03a §6.6."
required_next_step:        revise_plan

Notes:
  Both items are fixable inside the existing task scope and do not
  require a Jeremy decision. Builder, please revise the plan to (a)
  remove the unspecified column and (b) add the missing index, then
  re-post for re-validation.
```

### Example 17.3 — Blocked: jeremy-decision

```
gate_result:               blocked
risk_tier:                 tier3
requires_jeremy:           true
token_estimate:            45000
latest_commit_sha_reviewed: (n/a — plan-review stage, no commits yet)
blocking_reasons:
  - "Plan proposes a new auto-resolution class (auto-clear DQ exceptions
     of severity='warning' older than 90 days). Section 2 v1.0 LOCKED §1.3
     (Section 2 approval note) explicitly forbids new auto-resolution
     classes beyond the four allowed by SDR Decision 11. Adding this is
     a Section 2 amendment, not a feature task."
required_next_step:        escalate

Notes:
  Labeling blocked:jeremy-decision. This is an Approval Matrix item
  (EW §2.3) and cannot be resolved inside the current task. Please
  decide whether to (a) drop the auto-resolution from this task, (b)
  authorize a Section 2 amendment, or (c) defer.
```

### Example 17.4 — Blocked: token-budget

```
gate_result:               blocked
risk_tier:                 tier2
requires_jeremy:           true
token_estimate:            82000
latest_commit_sha_reviewed: (n/a — plan-review stage, no commits yet)
blocking_reasons:
  - "Task packet is 82k input tokens, exceeding the 70k cap and the 80k
     normal-split threshold. The packet pulls in the entire SDR (22k),
     EW (16k), and Sections 1, 2, and 3a verbatim (44k)."
required_next_step:        escalate

Notes:
  Labeling blocked:token-budget. Recommend splitting into:
    FEATURES-001a — features.feature_runs + features.feature_definitions only;
    FEATURES-001b — features.feature_values + composite FKs;
    FEATURES-001c — features.feature_run_issues + indexes.
  Each sub-task can reference the relevant 03a subsection rather than
  loading the full section. Estimated per-sub-task budget: ~25-30k.
  Awaiting Jeremy's call on the split or a 70k-cap exception.
```

### Example 17.5 — Blocked: repeated-failure

```
gate_result:               blocked
risk_tier:                 tier2
requires_jeremy:           true
token_estimate:            38000
latest_commit_sha_reviewed: 9a4b2c1...
blocking_reasons:
  - "This is the third Builder fix attempt. The same composite-FK
     creation failure (`pg_constraint duplicate key` on the named FK)
     has recurred after each fix attempt."
  - "Loop limit: maximum Builder fix attempts = 3."
required_next_step:        escalate

Notes:
  Labeling blocked:repeated-failure. Generating Failure Escalation Packet
  (see runbook §20). The likely cause is a name collision with an
  existing constraint left over from an earlier failed migration; the
  fix is probably one Jeremy-approved manual `DROP CONSTRAINT IF EXISTS`
  before the next migration attempt. Awaiting Jeremy's decision.
```

---

## 18. Example Codex/ChatGPT QA prompt

A reusable PR review prompt. It tells Codex/ChatGPT to review the artifact / diff against the task packet and specs, not Claude's summary.

```
You are the Codex/ChatGPT QA Reviewer for the quant-research-platform
project's Governor-Gated GitHub PR Agent Loop. You review the actual
PR diff against the task packet, the relevant approved specs, and the
GitHub Actions test output. You do not review Claude's PR summary;
the diff controls.

Your review covers, at minimum:

1. Diff implements the approved spec section exactly. No extra columns,
   missing columns, off-by-one window sizes, or silently introduced
   parameters.
2. Diff matches the task packet. Allowed files only. No forbidden file
   edits. No scope expansion.
3. Tests are present and meaningful. Tests verify financial meaning,
   not just mechanics (per EW §5).
4. No provider logic outside the provider layer.
5. No look-ahead bias in any feature, target, or backtest code.
6. No unapproved schema change.
7. No forbidden dependencies (broker SDKs; provider client libraries
   outside providers/).
8. No secrets in code, config, fixtures, logs, notebooks, or docs.
9. No live-trading path.
10. No hidden assumptions. Every choice in the diff traces to the
    SDR, the EW, an approved spec section, the traceability matrix,
    or the task packet's flagged assumptions.
11. Traceability matrix updated if a row's status changed.

For Tier 2 and Tier 3 work, additionally:

12. Produce or validate an Independent Test Plan from the task packet
    and approved specs, *before* deeply inspecting Claude's tests. The
    Plan answers:
      - What tests should exist if this is correct?
      - Are they present?
      - Do they test financial meaning?
      - Do they test integration contracts?
      - Do they fail for the correct wrong reasons?

Your verdict is one of: pass | pass-with-comments | fail.

Format your review as:

  Verdict: <pass | pass-with-comments | fail>
  Latest commit SHA reviewed: <sha>
  Independent Test Plan (Tier 2/3): <attached or "not required for Tier 0/1">
  Findings:
    - <one-line description per finding, severity-tagged>
  Recommended next step: <implement-fix | rerun-tests | escalate>

If Claude's PR summary contradicts the diff, note it explicitly. The
diff is what merges; the summary is not.

Your inputs are below:

  TASK PACKET:
    <task packet content>

  RELEVANT APPROVED SPEC EXCERPTS:
    <spec excerpts>

  RELEVANT SDR DECISIONS:
    <decision numbers and short text>

  PR DIFF:
    <full diff>

  GITHUB ACTIONS TEST OUTPUT:
    <test output>

  CLAUDE'S PR SUMMARY (for reference only — do not rely on it):
    <Claude's summary>
```

---

## 19. Example fix-loop instruction to Claude

Given to the Builder when QA or tests have identified a safe, in-scope issue. The instruction is bounded — Claude fixes only the named issue, does not expand scope, and does not move the PR forward without re-review.

```
Fix-loop instruction to Claude Code Builder.

Task ID: FEATURES-001
PR: <PR link>
Latest commit SHA: <sha>

Fix scope (apply ONLY these fixes; do not expand):
  - <issue 1, with file path and line range>
  - <issue 2, with file path and line range>

Out of scope for this fix:
  - any change beyond the issues above;
  - any new test beyond the ones the fix requires;
  - any refactor;
  - any change to allowed files unless directly required by the fix;
  - any change to forbidden files (always — these are still locked).

Required after applying the fix:
  1. Push the fix to the same PR (no new PR).
  2. Wait for GitHub Actions to rerun.
  3. The PR returns to:
       GitHub Actions
         → Codex/ChatGPT QA re-review (against the new latest commit SHA)
         → Project Governor / Context Auditor post-fix drift check
       BEFORE the PR may be labeled ai:ready-for-human-approval.
  4. Do NOT self-certify the fix as safe.
  5. Do NOT move the PR directly to human approval.
  6. Do NOT bypass QA re-review.

If during the fix you discover a problem outside the named scope:
  - stop;
  - leave a comment describing the discovery;
  - request a separate task or a Jeremy decision;
  - do not silently expand scope.

Stop conditions (any of these → stop and escalate, do not "fix through"):
  - the fix would change financial calculations;
  - the fix would change feature/target/label definitions;
  - the fix would change ETF universe / benchmark / sleeve / eligibility;
  - the fix would change schema beyond the approved spec;
  - the fix would touch a forbidden file;
  - the fix would expand scope;
  - the fix would require a context-budget exception above 70k.

Confirm in your response that you understand the bounded scope and the
post-fix validation chain, then apply the fix.
```

---

## 20. Example Failure Escalation Packet

Generated when the loop hits a configured failure limit (§8) or any stop condition that cannot be resolved without Jeremy.

```
FAILURE ESCALATION PACKET

Task ID:           FEATURES-001
Issue / PR:        <links>
Original goal:     Implement features schema migration per 03a §6.3-§6.6.
Risk tier:         Tier 2
Date:              2026-MM-DD
Latest commit SHA: 9a4b2c1...

Files changed (in the PR):
  - migrations/forward/0002_add_features_schema.sql
  - migrations/reverse/0002_add_features_schema.sql
  - tests/unit/architecture/test_features_schema_migration.py
  - tests/integration/architecture/test_features_schema_roundtrip.py

Reduced diff summary:
  - Added: 4 tables (features.feature_runs, feature_definitions,
    feature_values, feature_run_issues)
  - Added: 1 UNIQUE constraint on feature_runs(feature_run_id,
    feature_set_version)
  - Added: 2 composite FKs on feature_values
  - Added: 6 indexes per 03a §6.5 and §6.6
  - Added: schema migration runner test + integration roundtrip test

Tests failing:
  - tests/integration/architecture/test_features_schema_roundtrip.py
    - test_forward_then_reverse_returns_empty_features_schema
      Failure: pg_constraint "features_feature_values_run_link_fkey"
      already exists. Migration aborted on second forward apply attempt
      after a prior failed run.

QA blocking findings:
  - Codex/ChatGPT QA flagged that the constraint name collision
    indicates the previous failed migration left orphaned constraint
    metadata in the test database; QA recommends Jeremy review whether
    the migration runner should drop-if-exists the named constraint
    before applying, or whether the test database should be torn down
    between runs.

Project Governor / Context Auditor blocking findings:
  - Drift check passes against approved specs and the task packet.
  - However, the loop limit (max 3 Builder fix attempts) has been
    reached. The same failure has recurred after each fix.
  - Continuing AI retries is not appropriate; the underlying cause
    appears to be test-database state, not Builder logic.

What Claude attempted:
  - Attempt 1: corrected an unrelated typo in the FK column reference;
    test still failed with the same constraint-collision error.
  - Attempt 2: added IF NOT EXISTS to the table CREATE statements;
    test still failed (CREATE TABLE was not the failing statement).
  - Attempt 3: split the migration into two files; test still failed
    on the same constraint creation in the second file.

What changed between attempts:
  - Cosmetic and structural changes to the migration; no change to the
    constraint name or to the test fixture's database setup.

Likely cause:
  - The test fixture's database is not torn down between forward and
    reverse cycles; orphaned constraint metadata from earlier failed
    runs is colliding with the new migration. The fix is probably a
    one-line change to the test fixture (drop-and-recreate the schema
    before each test) or a small change to the migration runner
    (drop-if-exists named constraints). Either is plausibly correct;
    the choice has implications outside the current task's scope and
    should be made by Jeremy.

Decision needed from Jeremy:
  - Choose one of:
      (a) Patch the test fixture to drop-and-recreate the features
          schema before each test, and re-run the loop with a fresh
          fix attempt.
      (b) Modify the migration runner to drop-if-exists named
          constraints before recreating them. This touches the
          migration runner (a Section 2 component) and may itself be
          a Section 2 amendment.
      (c) Defer and split the task — apply only forward migration
          this iteration, defer the reverse roundtrip test to a
          follow-up task.
  - Awaiting Jeremy's decision before any further loop attempts on
    this task.
```

---

## 21. Human involvement model

- Jeremy does not review routine implementation plans.
- Jeremy is interrupted only for blocked / approval-gate items.
- Jeremy is interrupted for token-budget exceptions above 70k input tokens.
- Jeremy is interrupted for repeated loop failures (Failure Escalation Packets).
- Jeremy performs the final PR approval and merge.
- Jeremy remains the final authority.

The goal of the loop is to make Jeremy's involvement *high-leverage*: Jeremy reviews the things only Jeremy can decide, and the loop handles the rest. The goal is not to make Jeremy involved in every step.

The opposite failure mode — Jeremy never gets interrupted, and a strategy-affecting change merges silently — is exactly what the stop conditions (policy layer §29) and the blocking labels (§4) are built to prevent.

---

## 22. Future reusable tooling note

The Governor-Gated GitHub PR Agent Loop is documented inside `quant-research-platform` first. If the workflow proves useful, generic scripts and templates may later be extracted into a separate reusable tooling repository.

**This runbook does not create that repository.** The decision to extract is a future Jeremy decision, made after the loop has been exercised on real implementation tasks and has produced enough evidence about which parts are project-specific and which are genuinely reusable.

The clean separation is:

- *Reusable tooling repo, later:* how to run the loop.
- *`quant-research-platform` repo, now and ongoing:* what the loop must enforce.

Until the extraction happens, this runbook and the policy layer at `docs/implementation_context_governance.md` are the authoritative description of the workflow for this project.

---

**End of document.**
