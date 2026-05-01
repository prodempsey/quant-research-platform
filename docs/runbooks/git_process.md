# Git Process Runbook — Quant Research Platform

**Phase 1 scope:** ETF tactical research platform  
**Runbook status:** v0.1 DRAFT  
**Recommended repo path:** `docs/runbooks/git_process.md`  
**Owner:** Jeremy / Approver  
**Purpose:** Define the practical Git and GitHub workflow for controlled documentation, specification, and implementation changes.

---

## 1. Purpose

This runbook defines the mechanical Git process for the `quant-research-platform` project.

It explains how branches, commits, pull requests, QA review, Governor review, fixes, and merges should work during Phase 1.

This runbook does **not** replace or amend:

- `docs/strategy_decision_record.md`
- `docs/engineering_workflow.md`
- approved files under `docs/engineering_spec/`
- `docs/traceability_matrix.md`
- any approved review / approval artifacts under `docs/reviews/`

If this runbook conflicts with the locked Strategy Decision Record, Engineering Workflow, approved Engineering Specification, approval notes, or traceability matrix, the locked project source controls and this runbook must be corrected.

---

## 2. Source-of-truth hierarchy

Use the following hierarchy when resolving conflicts:

1. Strategy Decision Record (`docs/strategy_decision_record.md`)
2. Engineering Workflow (`docs/engineering_workflow.md`)
3. Approved Engineering Specification sections under `docs/engineering_spec/`
4. Approval notes and QA artifacts under `docs/reviews/`
5. Traceability Matrix (`docs/traceability_matrix.md`)
6. Task handoff packet for the specific branch / PR
7. This Git Process Runbook
8. Agent summaries, chat transcripts, or informal notes

Agent summaries are never the source of truth. Review the actual artifact, branch, PR diff, test output, and controlling documents.

---

## 3. Role ownership

### 3.1 Jeremy / Approver

Jeremy owns final project authority.

Jeremy is responsible for:

- choosing and authorizing tasks;
- approving task scope when required;
- resolving SDR, Engineering Workflow, Engineering Specification, schema, financial logic, risk, broker/order-intent, deployment, and scope questions;
- approving or rejecting final PRs;
- merging PRs into `main`;
- deciding when repeated agent failure should stop rather than continue consuming time.

Jeremy is **not** expected to personally write every line of code or perform every technical QA review.

### 3.2 Claude Code / Primary Builder

Claude Code is the primary Builder for normal implementation work.

Claude Code may:

- draft implementation plans from approved task packets;
- write code, tests, migrations, documentation, and fixes within the allowed scope;
- run requested local checks;
- update the same PR branch in response to QA findings.

Claude Code may **not**:

- approve its own work;
- merge PRs;
- change strategy;
- modify locked source-of-truth docs unless explicitly authorized;
- expand scope without approval;
- bypass QA or Governor review;
- make live-trading or broker-enabling changes.

### 3.3 Cursor / Secondary Builder

Cursor may act as a limited secondary Builder for small, explicitly scoped PRs when the task packet names Cursor as Builder.

Cursor is best suited for:

- small unit-test additions;
- lint / formatting / typing cleanup;
- small helper functions;
- small UI component improvements;
- narrow bug fixes with clear expected behavior;
- small documentation or runbook changes.

Cursor should not be the primary Builder for high-risk work unless Jeremy explicitly authorizes it. High-risk work includes financial formulas, target generation, backtest logic, portfolio rules, database migrations, order-intent behavior, broker/live-trading boundaries, model promotion, locked spec changes, or strategy-affecting YAML config changes.

Only one Builder may be active on a branch / PR at a time.

### 3.4 ChatGPT / Codex / QA Reviewer

The QA Reviewer independently reviews the actual PR diff against the controlling documents and task packet.

The QA Reviewer is responsible for:

- checking scope compliance;
- checking implementation against the approved Engineering Specification;
- checking whether tests are meaningful and sufficient;
- checking for hidden assumptions and strategy drift;
- identifying forbidden file changes, forbidden imports, missing tests, schema drift, secret leakage, or live-trading risk;
- reviewing fixes after the Builder updates the same branch.

The QA Reviewer does **not** implement fixes directly and does not merge PRs.

### 3.5 Project Governor / Context Auditor

The Project Governor is the scope and drift-control layer.

The Governor is responsible for:

- creating or verifying task packets;
- checking that the Builder plan matches the packet before work begins;
- checking allowed and forbidden files;
- checking forbidden imports, dependency additions, secrets, schema/config changes, and traceability impact;
- performing post-QA and post-fix drift review;
- routing unresolved or strategy-affecting issues back to Jeremy;
- preparing the final PR approval brief for Jeremy.

The Governor does **not** write implementation code, perform the primary QA review, approve final scope changes, or merge PRs.

### 3.6 GitHub Actions / Automated Checks

GitHub Actions produces deterministic evidence.

It may run:

- tests;
- linting;
- formatting checks;
- type checks;
- migration checks;
- secret scans;
- forbidden import checks;
- forbidden file-change checks;
- Docker build checks where relevant.

GitHub Actions does not make judgment calls. Failed checks must be fixed or explicitly resolved by Jeremy.

---

## 4. Branch strategy

### 4.1 Main branch

`main` is the approved source of truth.

Do not commit directly to `main` except for rare repo housekeeping explicitly approved by Jeremy.

All normal work should happen through branches and pull requests.

### 4.2 Branch naming convention

Use short, descriptive branch names.

Recommended prefixes:

| Prefix | Use for |
|---|---|
| `docs/` | Documentation changes |
| `runbook/` | Operational runbooks |
| `spec/` | Engineering Specification or spec-supporting changes |
| `impl/` | Implementation work |
| `test/` | Test-only changes |
| `fix/` | Bug fixes |
| `cursor/` | Cursor-owned small tasks |
| `claude/` | Claude-owned implementation tasks when useful for clarity |

Examples:

```bash
git checkout main
git pull origin main
git checkout -b runbook/git-process
```

```text
impl/provider-dto-contracts
impl/ingestion-run-metadata
test/provider-dto-validation
fix/ui-readonly-role-test
cursor/test-provider-dtos
runbook/git-process
```

---

## 5. Task packet requirement

Every non-trivial Builder task should have a task packet before work begins.

The packet should include:

- task title;
- assigned Builder (`Claude Code` or `Cursor`);
- task type (`docs`, `spec`, `implementation`, `test`, `fix`, `migration`, `runbook`);
- controlling documents;
- SDR decision references, where applicable;
- approved Engineering Specification section references;
- in-scope work;
- out-of-scope work;
- allowed files / folders;
- forbidden files / folders;
- required tests or checks;
- known open questions;
- stop conditions;
- expected PR description requirements.

### 5.1 Minimal packet template

```markdown
# Task Packet — <Task Name>

## Builder
Claude Code | Cursor

## Task type
Implementation | Test | Docs | Runbook | Fix | Spec Support

## Controlling documents
- `docs/strategy_decision_record.md`
- `docs/engineering_workflow.md`
- `docs/engineering_spec/<section>.md`
- `docs/traceability_matrix.md`

## SDR decisions
- Decision <N> — <name>

## In scope
- <specific work allowed>

## Out of scope
- <specific work forbidden>

## Allowed files / folders
- `<path>`

## Forbidden files / folders
- `docs/strategy_decision_record.md`
- `docs/engineering_workflow.md`
- `docs/engineering_spec/*` unless explicitly authorized
- `docs/traceability_matrix.md` unless explicitly authorized
- any unrelated module

## Required checks
- <pytest command>
- <lint command>
- <other checks>

## Stop conditions
Pause and escalate if:
- the spec conflicts with implementation needs;
- a strategy-affecting choice is required;
- a schema/config decision is needed but not approved;
- a broker/live-trading boundary is unclear;
- repeated fixes fail to resolve the issue;
- the task requires editing forbidden files.
```

---

## 6. Local workflow

Start from a clean and updated `main`:

```bash
git checkout main
git pull origin main
git status
```

Create a branch:

```bash
git checkout -b <branch-name>
```

After changes:

```bash
git status
git diff
```

Run the required checks from the task packet.

Stage and commit:

```bash
git add <files>
git commit -m "<type-scope>: <short description>"
```

Push:

```bash
git push -u origin <branch-name>
```

Open a PR into `main`.

---

## 7. Commit message convention

Use clear, boring commit messages.

Recommended format:

```text
<type>-<scope>: <description>
```

Examples:

```text
docs: add git process runbook
runbook: add VPS development environment guide
impl-data: add provider DTO contracts
test-data: add provider DTO validation tests
impl-ingestion: add ingestion run metadata writer
fix-ui: correct readonly role permission test
spec-05: lock portfolio paper order intent package
```

For implementation commits, include SDR decision references in the PR description rather than trying to overload the commit message.

---

## 8. Pull request requirements

Every PR should clearly say what kind of change it is.

### 8.1 PR type labels

Use one of these PR types:

- `docs-only`
- `runbook-only`
- `spec-only`
- `implementation`
- `test-only`
- `migration`
- `fix`
- `mixed` — avoid unless explicitly approved

### 8.2 PR description template

```markdown
## Type
Implementation | Test-only | Docs-only | Runbook-only | Spec-only | Migration | Fix

## Builder
Claude Code | Cursor

## Scope
Briefly describe exactly what this PR does.

## Controlling documents
- `docs/strategy_decision_record.md`
- `docs/engineering_workflow.md`
- `docs/engineering_spec/<section>.md`
- `docs/traceability_matrix.md`

## SDR decisions
- Decision <N> — <name>

## Changed files
- `<path>`

## Tests / checks run
- `<command>` — pass/fail

## Out of scope confirmed
- No locked SDR changes
- No Engineering Workflow changes
- No approved Engineering Specification changes unless explicitly authorized
- No traceability matrix change unless explicitly authorized
- No schema migration unless explicitly authorized
- No strategy-affecting config change unless explicitly authorized
- No broker/live-trading code path
- No secrets or credentials

## Known limitations / follow-ups
- <item or "None">
```

---

## 9. Allowed and forbidden changes

### 9.1 Normal implementation PRs may edit

Only the files explicitly allowed by the task packet.

Common examples:

- `src/quant_research_platform/<module>/...`
- `tests/<module>/...`
- narrow module documentation where required
- migration files if explicitly authorized
- config files if explicitly authorized

### 9.2 Normal implementation PRs may not edit

Unless explicitly authorized, implementation PRs may not edit:

- `docs/strategy_decision_record.md`
- `docs/engineering_workflow.md`
- approved files under `docs/engineering_spec/`
- `docs/traceability_matrix.md`
- approval notes under `docs/reviews/`
- unrelated modules
- strategy-affecting YAML config
- database migrations
- dependency manifests
- deployment exposure files
- broker/order-intent behavior
- live-trading-related code paths

### 9.3 Locked document rule

Locked SDR, Engineering Workflow, and Engineering Specification documents are not ordinary editable files.

Changes to them require the existing project amendment / approval discipline. Do not modify them through a normal implementation PR.

---

## 10. QA review process

QA reviews the PR diff, not the Builder summary.

QA should check:

- Does the PR stay within the task packet?
- Does it follow the SDR?
- Does it follow the Engineering Workflow?
- Does it follow the approved Engineering Specification?
- Does it introduce hidden assumptions?
- Does it modify forbidden files?
- Does it add unapproved dependencies?
- Does it add unapproved schema changes?
- Does it add unapproved strategy config changes?
- Does it preserve no-live-trading and no-broker boundaries?
- Are tests present and meaningful?
- Do tests verify financial meaning where applicable, not just mechanics?
- Are secrets absent from code, logs, tests, and documentation?

QA result options:

| Result | Meaning |
|---|---|
| `Pass` | Ready for Governor drift check |
| `Pass with minor notes` | No blocker; notes may become follow-up issues |
| `Revise` | Builder fixes same branch and QA re-reviews |
| `Blocked` | Jeremy decision required before continuing |

---

## 11. Fix loop

If QA or Governor review finds issues, the Builder fixes the same branch.

The fix loop is:

1. QA or Governor identifies issue.
2. Builder updates the same branch.
3. Builder commits and pushes fix.
4. GitHub Actions rerun.
5. QA re-reviews the updated PR diff.
6. Governor performs drift check again if needed.

Do not open a new PR for the same fix unless the original PR has become too messy and Jeremy approves restarting.

Repeated failure should stop and escalate to Jeremy rather than continuing indefinitely.

---

## 12. Governor review process

Governor review checks whether the PR has drifted from approved context.

The Governor should check:

- task packet compliance;
- allowed / forbidden file list;
- hidden scope expansion;
- edits to locked documents;
- unapproved schema or migration changes;
- unapproved YAML strategy config changes;
- unapproved dependency additions;
- provider-boundary violations;
- feature / target / model / backtest / portfolio behavior drift;
- order-intent or live-trading boundary issues;
- secrets or credential exposure;
- traceability impact;
- whether unresolved open questions were silently decided.

Governor result options:

| Result | Meaning |
|---|---|
| `Pass` | Ready for Jeremy approval brief |
| `Revise` | Builder fixes same branch |
| `Blocked` | Jeremy decision required |

---

## 13. Final approval and merge

A PR is ready for Jeremy only when:

- Builder completed the scoped work;
- required checks passed or exceptions are explicitly documented;
- QA passed;
- Governor drift check passed;
- no unresolved blocker remains;
- the PR description is accurate;
- changed files match the allowed scope;
- no locked documents were modified without authorization;
- no secrets are present;
- no broker/live-trading boundary was crossed.

Jeremy then reviews the final PR approval brief and the PR as needed.

Only Jeremy approves and merges into `main`.

After merge:

```bash
git checkout main
git pull origin main
git branch -d <branch-name>
```

Remote branches may be deleted after merge.

---

## 14. Documentation-only PRs

Documentation-only PRs may use a lighter process if they do not change controlling project commitments.

Examples:

- runbooks;
- operational notes;
- development-environment documentation;
- Git process documentation;
- non-binding explanatory diagrams.

Documentation-only PRs must still avoid modifying locked source-of-truth documents unless explicitly authorized.

A docs-only PR should say:

```markdown
## Type
Docs-only

## Governance impact
No SDR change. No Engineering Workflow change. No Engineering Specification change. No traceability matrix change.
```

---

## 15. Specification and locked-document PRs

Spec and locked-document PRs are governed by the Engineering Workflow and the Approval Matrix.

Use a stricter process for:

- SDR revisions;
- Engineering Workflow revisions;
- Engineering Specification amendments;
- traceability matrix updates;
- approval notes;
- QA reports;
- scope changes;
- strategy-affecting config changes.

These PRs require explicit Jeremy approval and should not be mixed with implementation code unless specifically authorized.

---

## 16. Implementation PRs

Implementation PRs should be small and module-bounded.

Good implementation PR shape:

```text
One module or one narrow contract.
One clear task packet.
One Builder.
One PR.
Tests included.
No unrelated cleanup.
```

Avoid:

```text
Large multi-module PRs.
Spec edits plus implementation.
Refactors mixed with feature work.
Schema changes hidden inside code PRs.
Dependency additions without approval.
Financial logic changes without explicit approval.
```

---

## 17. Migration PRs

Database migration PRs are higher risk.

A migration PR must include:

- controlling spec section;
- migration file(s);
- reverse migration or rollback discipline if required by the approved spec;
- tests proving the schema behavior required by the spec;
- confirmation that no unrelated schema was changed;
- Governor review for schema drift.

Do not create migrations unless the task packet explicitly authorizes them.

---

## 18. Config PRs

YAML config changes may be strategy-affecting.

A config PR must state whether the change is:

- non-strategy operational metadata;
- implementation default;
- strategy-affecting;
- already approved by a locked spec;
- requiring Jeremy approval.

Do not change strategy-affecting YAML values without explicit approval.

---

## 19. Dependency PRs

Dependency changes require explicit review.

A dependency PR must explain:

- why the dependency is needed;
- which module uses it;
- whether it introduces broker/live-trading, provider, credential, network, or deployment risk;
- whether it changes Docker build behavior;
- whether tests cover it.

No broker SDKs or live-trading-capable dependencies are allowed in Phase 1 unless a future approved amendment changes the project scope.

---

## 20. Cursor-specific operating rules

Cursor may be used on small PRs, but only with clear boundaries.

Every Cursor task packet should include:

```markdown
## Cursor Builder Constraints

- Cursor is the sole active Builder on this branch.
- Cursor may edit only the allowed files listed in this packet.
- Cursor may not modify locked SDR, Engineering Workflow, approved Engineering Specification files, approval notes, or the traceability matrix unless explicitly authorized.
- Cursor may not introduce new dependencies unless explicitly authorized.
- Cursor may not change schemas, migrations, financial formulas, feature definitions, target definitions, portfolio rules, order-intent behavior, broker behavior, or YAML strategy config unless explicitly authorized.
- Cursor may not mark the PR ready for human approval.
- Cursor fixes must go through GitHub Actions, QA re-review, and Governor drift check.
```

Cursor-owned branches should use either `cursor/` or a normal prefix with the Builder named in the PR description.

Examples:

```text
cursor/test-provider-dtos
cursor/fix-ruff-providers
cursor/docs-git-process
```

---

## 21. Recommended PR size

Keep PRs small enough to review carefully.

Recommended maximums:

| PR type | Recommended size |
|---|---|
| Docs/runbook | one document or one tightly related set |
| Test-only | one module or one contract area |
| Implementation | one module contract or one small vertical slice |
| Migration | one schema area or one approved migration group |
| Fix | one defect or closely related defects |

Large PRs should be split unless Jeremy explicitly approves the larger scope.

---

## 22. Stop conditions

Stop and escalate to Jeremy if any of the following occur:

- the SDR and Engineering Specification appear to conflict;
- the implementation requires a strategy decision not already made;
- the task requires changing locked docs;
- a financial calculation, feature, target, risk rule, portfolio rule, model promotion rule, broker/order-intent behavior, or deployment exposure is ambiguous;
- an unapproved schema or config change appears necessary;
- an agent repeatedly fails to fix the same issue;
- tests cannot be written for the behavior;
- the PR is growing beyond the approved task scope;
- a live-trading or broker boundary question appears;
- secrets or credentials may have been exposed.

Escalation is preferred over guessing.

---

## 23. Final PR approval brief template

Before Jeremy merges, the Governor or QA Reviewer should prepare a concise final brief:

```markdown
# Final PR Approval Brief — <PR Title>

## PR
<link or PR number>

## Builder
Claude Code | Cursor

## Summary
<one paragraph>

## Scope result
In scope / minor deviation explained / blocked

## Controlling documents checked
- SDR Decision <N>
- Engineering Workflow v<version>
- Engineering Specification <section>
- Traceability Matrix
- Task packet

## Checks
- GitHub Actions: pass/fail
- Local checks: pass/fail/not applicable
- QA review: pass/fail
- Governor drift check: pass/fail

## Files changed
- <list>

## Confirmations
- No locked-doc edits unless authorized
- No unapproved schema changes
- No unapproved config changes
- No secrets
- No broker/live-trading path
- No unresolved open questions silently decided

## Recommendation
Merge / Do not merge / Jeremy decision required
```

---

## 24. Simple mental model

```text
main = approved truth
branch = controlled workspace
PR = review package
Builder = writes the change
QA Reviewer = checks correctness
Governor = checks scope and drift
GitHub Actions = runs deterministic checks
Jeremy = approves and merges
```

No single agent should plan, build, review, approve, and merge its own work.

---

## 25. End state after merge

After a PR is merged:

- `main` becomes the new source of truth;
- the branch can be deleted;
- follow-up tasks should be opened separately;
- any approved docs or specs must be referenced by their committed repo path, not by chat transcript;
- the next task packet should start from the updated `main` branch.

