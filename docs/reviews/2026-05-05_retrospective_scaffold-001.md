# SCAFFOLD-001 / PR #2 — Retrospective

**Document type:** Retrospective
**Status:** v0.1 DRAFT
**Date:** 2026-05-05
**Owner:** Jeremy Dempsey
**Canonical path:** `docs/reviews/2026-05-05_retrospective_scaffold-001.md`
**Companion documents:**

- `docs/strategy_decision_record.md` (v1.0 LOCKED)
- `docs/engineering_workflow.md` (v1.5 LOCKED)
- `docs/implementation_context_governance.md` (v1.0 APPROVED)
- `docs/runbooks/governor_gated_github_pr_agent_loop.md` (v1.0 APPROVED)
- `docs/runbooks/vps_development_environment.md`
- `docs/traceability_matrix.md` (v0.9)
- Engineering Specification sections under `docs/engineering_spec/` (Sections 01–06, all v1.0 LOCKED / APPROVED)
- Possible companion: `docs/reviews/2026-05-05_autonomous_loop_proposal.md` — deferred; created only if §10 of this retrospective grows beyond a condensed summary.

**Scope statement.** This retrospective records observations, lessons, and recommended forward directions arising from SCAFFOLD-001 (Issue #1) and its merge via PR #2. Its scope is process and governance, not strategy. It is the retrospective companion to the closed loop on PR #2, and it is the operator-imposed precondition for drafting the SCAFFOLD-002 task packet, per the post-PR-#2 handoff.

**Non-authorization statement.** This document does not authorize anything. It is not an Engineering Specification section. It does not amend the SDR, the EW, the implementation context governance policy, the runbook, the VPS development environment runbook, or any locked Engineering Specification section. Its recommendations identify amendments that *would be* required and decisions that *would need to be made*; the actual amendments and decisions remain governed by each named document's own change process. Where this retrospective tags a recommendation as `amendment-required: <doc>`, the operative meaning is "requires a change to the named document via that document's standard change process," not "this retrospective changes the named document."

---

## 1. Purpose, scope, and non-goals

### 1.1 Purpose

This retrospective exists for three reasons:

1. **Record the actual experience** of running the Governor-Gated GitHub PR Agent Loop for the first time end-to-end, on a real implementation task, with a real branch-protection ruleset.
2. **Surface gaps** in the runbook, the policy layer, and the operating practice that a reading of those documents alone would not have surfaced.
3. **Recommend forward directions** before SCAFFOLD-002 work begins, including the architectural direction proposed for an autonomous-loop replacement of the current chat-Governor + operator-relay model.

### 1.2 In scope

- Process observations from the SCAFFOLD-001 / PR #2 loop, including the relay-cost-driven operator-effort burden.
- Builder, QA Reviewer, Project Governor / Context Auditor, and Approver-side observations, with concrete failures and concrete near-misses.
- Solo-operator branch-protection procedure, including the PR #2 ruleset relax / merge / restore window.
- Terminal label / loop-closure record gap.
- Cursor cleanup-pass experiment outcome (skipped on PR #2 per Approver decision).
- Cosmetic / rendering artifacts that affected the operator's day-to-day, even where they did not affect correctness.
- Session-boundary discipline for Builder and QA agent CLIs (`--continue` vs fresh context).
- Recommended forward direction for an autonomous-loop architecture, condensed; deeper architecture material may live in `docs/reviews/2026-05-05_autonomous_loop_proposal.md` if drafted.

### 1.3 Out of scope (non-goals)

- Drafting amendment text for the EW, the runbook, the implementation context governance policy, the VPS development environment runbook, or any locked Engineering Specification section. Each amendment, if approved, is its own follow-on artifact under the named document's standard change process.
- Drafting the SCAFFOLD-002 task packet.
- Drafting an autonomous-loop SCAFFOLD-class task packet.
- Implementing or building any autonomous-loop infrastructure.
- Reopening Engineering Specification Sections 01–06; they are LOCKED / APPROVED and the retrospective is not the place to reopen them.
- Approving anything. This document records observations and recommendations; approval authority remains with the Approver per EW §2.3.

### 1.4 Terminology and source-of-truth posture

The retrospective is subordinate to the source-of-truth hierarchy. Where a retrospective observation appears to conflict with a locked document, the locked document controls and the observation is recorded as a candidate amendment, not as a working interpretation.

The retrospective uses ICG §20's canonical wording — **"latest PR commit SHA"** and **"latest-commit SHA validation"** — for what was referred to in PR #2 chat as the "anchored review SHA." The two terms refer to the same concept; the canonical term is preferred in this document and in any subsequent governance amendment.

The retrospective uses runbook §3 / ICG §6 canonical role names — **Project Governor / Context Auditor**, **Builder**, **QA Reviewer**, **Approver** — for the present-day four-role model. The five-role expansion proposed in §10 is treated as an expansion of these roles, not a replacement.

The retrospective treats the per-PR chat shorthand "Step 13," "Step 14," and "Step 15" as session shorthand, *not* as references to runbook §6's numbered procedure. Runbook §6 has 24 numbered steps and includes the full governed / fix-loop path; clean-pass PRs may skip or collapse some practical actions. The drift between the per-PR session numbering and the canonical runbook §6 numbering is a separate finding under §4.8.

---

## 2. Outcome summary

### 2.1 Closure facts

The following facts are the durable state-of-the-record on GitHub at retrospective time:

- **Issue #1 (SCAFFOLD-001).** Closed. Reason: completed. Stale labels stripped. URL: `https://github.com/prodempsey/quant-research-platform/issues/1`.
- **PR #2.** Merged. Merged-at: `2026-05-04T05:39:07Z`. Stale labels stripped. URL: `https://github.com/prodempsey/quant-research-platform/pull/2`.
- **Merge commit on `main`.** `1aa31689a922dc074ecf49100a439210f528cb93`.
- **Latest PR commit SHA at final gate** (chat shorthand: "anchored review SHA"). `f13e926ade498c1ae97182587365f297f2bbfa21`. Preserved as parent of the merge commit; reachable from `main` indefinitely.
- **Branch.** `scaffold/scaffold-001-repo-skeleton`. Retained on `origin`. Deletion deferred to this retrospective; see §13.
- **Branch protection.** Ruleset `main protection`, Active enforcement, restored to its pre-merge configuration after the relaxation window. Restoration verified active via `gh api .../rulesets`.
- **Loop trace** (PR #2 comments):
  - Post-fix drift check (pass): `pull/2#issuecomment-4368233682`
  - Final PR approval brief: `pull/2#issuecomment-4368499035`
  - Post-merge completion confirmation: `pull/2#issuecomment-4368632762`
- **Repository visibility.** Public, intentional, post-secret-scan-audit-clean. Deliberate change to enable Ruleset enforcement on GitHub Free tier. Out of scope for this retrospective; recorded in the project's prior governance trail.
- **Cursor cleanup pass on PR #2.** Skipped per Approver decision under Precondition D option (b). Recorded as a deliberate experimental datapoint. See §7.

*Verification note.* The GitHub-derived facts in this section (merge timestamp, ruleset restore verification, repository visibility flip, pre-flip secret-scan audit outcome) are reproduced from the post-PR-#2 handoff and are plausible and consistent with the chat record, but are not all independently proven by the markdown files in this repository. They are subject to a verification pass against GitHub comments, `gh` output, and the final approval brief before this retrospective is promoted to v1.0. See §13.3.

### 2.2 What worked

The loop closed cleanly. The following observations are reported as positives because each one tested a previously untested invariant or held a deliberate governance choice under operating pressure for the first time. They are not "the loop did not catastrophically fail"; that bar is too low for a project at this stage.

- **The loop's latest-commit SHA discipline held across GitHub Actions, QA re-review, and post-fix Governor drift review.** No "fix slipped past a stale review" near-miss occurred. The latest-commit SHA at the final gate (`f13e926…`) is preserved as the parent of the merge commit, which keeps the review's commit basis reachable from `main` indefinitely.
- **Branch-protection ruleset relax / restore window worked end-to-end.** The relaxation (Required approvals 1 → 0; Require approval of most recent reviewable push unchecked) and the immediate post-merge restore both took effect as documented, and the restore was verified via `gh api`. The structural protection caught the case it was meant to catch: the Approver could not self-approve the PR they had also authored — that is the intended outcome of the ruleset, not a defect, and is the structural cause discussed under §5.
- **VPS-vs-client-crash recovery was untested before PR #2 and passed.** Cockpit-side disruption during the loop did not corrupt server-side state because the durable record-of-record (Issue body, PR comments, labels, GHA runs, branch state) lives on GitHub, not on the cockpit. This was an architectural assumption of the loop; PR #2 was the first real test of it.
- **Pre-flip secret-scan audit was clean.** The deliberate flip from private to public was preceded by an audit; no committed credentials, no credential-pattern files, `.gitignore` correctly excluded `.env`. The flip was a deliberate governance change and the prerequisite audit was performed.
- **Loop trace lives on GitHub as durable comments.** The post-fix drift check, the final approval brief, and the completion confirmation are PR comments, not chat-only artifacts. A future fresh-context Project Governor / Context Auditor session reading PR #2 can find the gates' verdicts and reasoning without needing a chat transcript.
- **Stale-label cleanup was performed.** Issue #1 and PR #2 were stripped of stale labels at closure; the post-merge label state is consistent with closure, modulo the missing terminal label discussed in §6.
- **Phase 1 boundary held inside SCAFFOLD-001's scope.** No live broker integration, no individual stocks, no fundamentals, no holdings, no news, no autonomous research agents, no commercial features were added. The Builder did not attempt scope expansion; the QA Reviewer did not surface scope drift. This is what the SDR-locked scope is meant to produce, and PR #2 produced it.

These positives are real but narrow. The dominant retrospective signal is in §3 onward.

---

## 3. Operator-experience cost — the dominant pain point

This is the single largest signal from PR #2 and the architectural driver for the autonomous-loop direction in §10. The retrospective records it as a first-class finding rather than as scattered annotations under §4.

### 3.1 What the relay model actually was on PR #2

The PR #2 loop ran under a chat-Governor + operator-relay model. In practice, this meant the Approver was the literal communication channel between every other party: chat-Governor outputs were copy-pasted into terminal panes for the Builder; Builder outputs were screenshotted, pasted, or transcribed back into chat for the Project Governor / Context Auditor; QA outputs were posted as PR comments and then re-summarized into chat; ruleset relax/restore, label changes, and PR/Issue comment posting were operator-issued `gh` commands; and every CLI prompt for tool-permission ("y/n," "always allow this command," "option 2") was an operator click-through.

A small number of relay events would have been negligible. PR #2 produced many of them, and the cumulative effect dominated the run.

### 3.2 Why it dominated

The dominance is not a single mechanic; it is the compounding of several:

- **Channel multiplication.** Every gate that reads from chat and writes to GitHub (or vice versa) doubles as a relay event.
- **Prompt-permission interruptions.** Both Builder (Claude Code) and QA (Codex CLI) interrupt for tool-permission decisions on commands the operator could plausibly have pre-authorized. PR #2's ruff-format fix loop alone burned more than four operator prompts on Builder-side toolchain discovery. See §4.3 and §4.4.
- **No structured-output boundary.** Builder narrative, plan content, blocker text, and verification claims arrived in free-form prose, which forced the Project Governor / Context Auditor to re-extract structure on every cycle. See §4.5.
- **Mid-flight prompt iteration.** The Approver hardened the Codex QA prompt through approximately five review iterations on PR #2. The iterations were correct work; their volume was a relay-cost amplifier. See §4.7.
- **Heredoc / pane truncation.** Two PR #2 comments hit the >50-line paste limit and required nano + `--body-file` workarounds. See §4.6.

The shape that emerges is: the loop's *governance* is sound, but its *plumbing* relies on a human relay. The relay is the cost.

### 3.3 Highest-leverage near-term mitigations (before SCAFFOLD-002)

Two changes can be made under existing governance, without waiting for any autonomous-loop infrastructure:

1. **Pre-approved-commands cheat sheet, by tool.** Document the safe-by-default and never-safe command sets for Codex CLI per-pattern `p`-mode and for Claude Code "option 2" mode, broken out by tool. Candidate command list for a future runbook amendment, not approved policy until amended. The handoff already enumerates a working candidate list:
   - **Codex CLI `p` is safe for:** `gh pr view`, `gh pr diff`, `gh run view`, `gh run list`, `gh pr checks`, `git status`, `git rev-parse`, `git log`, `git diff`, `git show`, `cat`, `head`, `tail`, `wc`, `grep`, `find`, `sort`.
   - **Codex CLI `p` is never safe for:** `gh api` (general HTTP), `gh pr comment`, `gh pr edit`, `gh issue comment`, `gh issue edit`, `gh pr create`, `gh pr merge`, `rm`, `mv`, `mkdir`, any file write, `git add` / `commit` / `push`, `pip install`, `pytest`, `ruff`, heredoc-into-file.

   *Scope guard for any preauthorized read-only command.* Preauthorization applies only inside the intended repo / PR context and never to secrets files, `.env`, production paths, backup paths, or arbitrary system inspection. This guard applies to all read-only commands listed above and to any incidental sanity commands pre-authorized under §4.4.

   - **Claude Code option 2 is broader than Codex `p` and needs careful guidance. Default: do not press option 2.**

   `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (add as a runbook subsection — operating procedure, not policy). The policy layer at `docs/implementation_context_governance.md` already governs forbidden file writes; the cheat sheet is a *recognition* of which read-only commands the operator is willing to pre-authorize, not a relaxation of any forbidden-action rule.

2. **Bounded fix prompts pre-authorize incidental sanity commands.** When the Project Governor / Context Auditor issues a bounded fix prompt to the Builder, the prompt should pre-authorize commonly-needed read-only sanity commands (e.g., `which`, `--version`, `ls`, `cat`) so the Builder does not interrupt for permission on each one. Discussed further as a Governor checklist refinement in §4.4. `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md`.

These two mitigations do not eliminate the relay; they reduce its volume. The architectural reduction is in §10.

### 3.4 Mid-loop request to spawn a Governor agent

During the PR #2 run, the Approver proposed spawning a Governor agent to absorb relay load mid-loop. The chat-Governor declined as a rules-mid-flight change and deferred the decision to this retrospective. That decision was correct under the loop's existing governance — changing the role model mid-PR is itself a category of drift the loop is meant to prevent — but it is also evidence that the operator-effort cost was high enough mid-run to warrant a structural change. The structural change is the §10 autonomous-loop direction. `informational`; the underlying decision is captured in §10.

---

## 4. Process gaps observed during PR #2

§4 records concrete gaps, each with the observation, why it matters, the recommendation, and an amendment tag where applicable. Findings are ordered roughly by where they hit the loop, not by severity. Severity ordering is implicit in §11.

### 4.1 Governor plan-validation checklist gaps

The Project Governor / Context Auditor's plan-validation pass on PR #2 missed four checks that, in retrospect, should have been part of the checklist. None of the four caused a merge defect; all four caused avoidable rework.

- **Pre-existing-files-vs-create check.** The Builder's plan described `.gitignore` and `README.md` as files to create; both already existed. The plan-validation pass did not catch this. The Builder's blocker comment claiming "all 11 `.gitignore` entries already present" was the symptom; the underlying gap was that the plan was not validated against repo state.
- **Packet → plan wording-drift check.** v2 §4 of the plan said "covering at minimum" where the packet said "exactly… No additions." The wording divergence relaxed a constraint; plan-validation did not flag it.
- **Ruff rule vs selected ruleset check.** The Builder's planned code patterns included a construct that failed the selected ruff ruleset (UP038) under GHA. Plan-validation could have caught this against the project's `pyproject.toml` rule set rather than treating ruff as a runtime discovery.
- **Formatter-step omission.** The plan / fix checklist did not explicitly require a formatting step before GHA or final review. Once code exists, the Builder should apply the project-pinned formatter as a deterministic transform before pushing, while GHA remains the verdict source.

**Recommendation.** Add four explicit items to the Project Governor / Context Auditor plan-validation checklist before SCAFFOLD-002: pre-existing-files-vs-create, packet → plan wording-drift, ruff-rule-vs-selected-ruleset, formatter-step omission. The first two are deterministic checks (file-existence, string-diff); the latter two are deterministic checks against the project's `pyproject.toml` configuration. None requires LLM judgment.

`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (plan-validation step in §6); `amendment-required: docs/implementation_context_governance.md` (deterministic-checks-before-LLM-judgment list in §9 / §24).

### 4.2 Builder verification failures — claimed without evidence

Two concrete failures occurred during PR #2. Both were caught, both were resolved, and neither merged. They share a pattern.

- **v2 §1 fixture non-enumeration.** The Builder claimed v2 §1 enumerated all fixtures; it did not enumerate them until pushed during the revise-verdict cycle (recorded as Finding 4 in that revise verdict).
- **`.gitignore` 11-of-11 claim.** The Builder's blocker comment claimed all 11 `.gitignore` entries were already present. A Project Governor / Context Auditor `grep` confirmed only 9 of 11. The discrepancy drove the R-1 resolution.

The shared pattern is *claim without supporting evidence in the same comment*. Both claims would have survived a less rigorous Governor pass.

**Recommendation.** For SCAFFOLD-002 and onward, the Builder must include verification output (e.g., `grep -nE '...' file`, `diff`, `wc -l`, `gh api` excerpts) inline in any blocker comment, plan section, or fix-applied claim that asserts a state-of-the-world fact. "Verified" without showing the verification is the failure mode. The Builder should provide supporting output with state-of-the-world claims. The Project Governor / Context Auditor should reject unsupported claims and may independently spot-check critical claims as part of deterministic guardrail review.

`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (Builder-side expectations under §3 Roles and §6 Step 7 / Step 17); `amendment-required: docs/implementation_context_governance.md` (Builder responsibilities, complementary to ICG §11 / §19).

### 4.3 Cockpit discipline — "no local verification as source-of-truth," not "no local execution"

PR #2 surfaced a wording problem in how the cockpit's "no local execution" principle was being interpreted. The original intent — that local execution must not be the source of truth for whether a change is correct — was being read as "the Builder may not run anything locally." Under the strict reading, the Builder spent more than four operator prompts discovering that ruff was not installed in the cockpit's Python environment, when ruff is a deterministic auto-formatter declared in the project's `pyproject.toml` dev extras.

The distinction matters: a deterministic auto-formatter is a *transform*, not a *verdict*. Running `ruff format` locally does not produce evidence about correctness; it produces a deterministic textual transform. GHA remains the authoritative verdict, and local formatting is acceptable only when using the project-pinned formatter/configuration or the approved dev/container toolchain. Treating the formatter as forbidden inflated relay cost without buying any governance.

**Recommendation.** Refine the cockpit principle to **"no local *verification* runs as source-of-truth"** (rather than "no local execution"). Builder-side use of deterministic auto-formatters declared in `pyproject.toml` dev extras (notably `ruff format` and equivalent) is permitted as a transform; the *verdict* on conformance still belongs to GHA. `pytest`, `ruff check` results, and any other gate that produces a pass/fail verdict remain GHA-owned and may not be cited locally.

`amendment-required: docs/implementation_context_governance.md` (the principle's wording lives there); `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (Builder-side operating procedure should reflect the refined wording).

### 4.4 Prompt completeness — bounded fix prompts must pre-authorize incidental sanity commands

When the Project Governor / Context Auditor issues a bounded fix prompt to the Builder, the prompt names the fix scope but does not currently pre-authorize the incidental read-only sanity commands the Builder will run to apply the fix. PR #2's ruff-format fix loop is the canonical example: the Builder needed to run `which ruff`, `ruff --version`, `ls` against the venv, and a few related read-only commands to discover the toolchain state. Each interrupted for permission. Each was a relay event.

**Recommendation.** A bounded fix prompt template should include an "Incidental commands pre-authorized" line listing the read-only sanity commands the Builder may run without re-prompting (e.g., `which`, `--version`, `ls`, `cat`, `head`, `grep`, `find`, `git status`, `git rev-parse`). The list is bounded and read-only; pre-authorizing it does not relax any forbidden-action rule. This finding is the per-prompt corollary of §3.3 #1's pre-approved-commands cheat sheet.

`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (fix-loop instruction template in §19).

### 4.5 Mid-flight failures — structured blocker template, not free-form narrative

When the Builder hit unexpected state during PR #2 (notably the `.gitignore` 11-of-11 case), the resulting blocker comment was free-form narrative. The narrative form forced the Project Governor / Context Auditor to re-extract structure (claim, evidence, scope, requested decision) before the gate could continue, which both slowed the cycle and introduced an interpretation step that should not exist between Builder claim and Governor audit.

**Recommendation.** A bounded blocker template — fields for *what was attempted*, *what state was found*, *the verification output* (per §4.2), *whether the blocker is in-scope-fixable or requires Approver decision*, and *requested next step* — should be added to the runbook. The template is the Builder's exit hatch from the fix-loop, analogous to the Failure Escalation Packet (ICG §25), but for in-PR mid-flight blockers rather than for repeated-failure escalations.

`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (Builder-side blocker template under §6 Step 7 / Step 17 and §19 fix-loop instruction).

### 4.6 Heredoc / Cursor terminal-pane truncation

During PR #2, heredocs over approximately 50 lines were observed to truncate in Cursor terminal panes. PR #2 hit the limit twice (the post-fix drift check and the post-merge completion confirmation referenced in §2.1, in chat shorthand — see §4.8 on numbering). Both were resolved successfully using a `nano` + `/tmp` transit-file + `gh ... --body-file <path>` workaround.

The truncation is a Cursor terminal renderer behavior, not a GitHub or `gh` behavior. The fix lives in the operator's tooling, not in the loop architecture. See §8 for the cluster of Cursor-rendering observations.

**Recommendation.** Document the >50-line paste rule and the `--body-file` workaround as a runbook operating note. For comments expected to exceed the limit (final approval briefs, retrospectives in PR comments, large fix-packet contents), default to the `--body-file` path. The recommendation does not require a tooling change; it requires an operating-procedure note.

`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (operating note alongside the comment-posting step).

### 4.7 Approver-QAs-Governor-prompt micro-gate (pre-issuance review)

The Approver hardened the Codex QA prompt for PR #2 through approximately five review iterations before it was issued to the QA Reviewer. The iterations were correct — the issued prompt was materially stronger than the first draft — but the iteration loop ran on the Approver's foreground time. The pattern is itself a governance signal: an Approver-QAs-Governor's-prompt-before-issuance step is *already happening informally* at every gate where the Project Governor / Context Auditor produces a prompt for an external party (Builder, QA Reviewer).

**Recommendation.** Create reusable Governor prompt templates and require Approver pre-issuance review only for first-use templates, high-risk prompts, approval-sensitive tasks, or prompts where the Governor flags ambiguity. Routine prompts that use already-approved templates should not require a separate manual micro-gate. This intentionally avoids adding a per-prompt manual gate that would compound the §3 relay burden.

`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (micro-gate added before each prompt-emission step in §6).

### 4.8 Session-step numbering vs runbook §6 numbering

The PR #2 chat record uses session shorthand "Step 13," "Step 14," "Step 15" for the post-fix drift check, the final approval brief, and the post-merge completion confirmation respectively. Runbook §6's canonical numbering is different: §6 has 24 numbered steps, post-QA drift check is Step 15, post-fix drift check is Step 20, and `ai:ready-for-human-approval` is Step 23. There is no canonical Step 14 named "final approval brief"; the final PR approval brief is the *output* of Step 23, not a step in its own right. There is no canonical Step 15 named "post-merge completion confirmation"; post-merge is implicit after Step 24 and currently has no labeled state (see §6 of this retrospective).

The drift between session shorthand and canonical numbering is a documentation gap, not a defect in PR #2's run. It became visible only when this retrospective tried to reconcile the chat record with `docs/runbooks/governor_gated_github_pr_agent_loop.md`.

**Recommendation.** Use canonical runbook §6 step numbers in chat, PR comments, and retrospective records. Avoid separate session-step numbering. A second shorthand sequence would create another mapping artifact to maintain; canonical numbering is less convenient but single-source.

`decision-required: numbering convention reconciliation` is therefore *resolved as a recommendation in this retrospective*; the actual change is `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` to add a one-line operating note that PR comments and chat references use §6 step numbers.

---

## 5. Solo-operator branch-protection procedure

### 5.1 The structural problem

The Approver and the PR author were the same person on PR #2. Branch protection's "Require a pull request before merging" rule with one approval, combined with "Require approval of most recent reviewable push" and "Dismiss stale approvals on new commits," produces a structural deadlock for a solo operator:

- The Approver cannot self-approve their own PR (PR-author-approves-PR is what the rule is built to prevent).
- AI / bot reviewers are explicitly disqualified per `docs/runbooks/vps_development_environment.md` §14 and EW §2.3.
- A second human maintainer with `write` access does not currently exist on this repository.

GitHub branch-protection approving review is a repository-control mechanism, not the same thing as EW Approver authority; however, using an AI/bot account as the approving reviewer would still violate the project's no-agent-approval boundary.

The result is that every PR authored by the sole operator requires either a second human maintainer or a temporary ruleset relaxation to merge. PR #2 used the second path.

### 5.2 What PR #2 actually did

PR #2 used a relax / merge / restore window:

- **Relax (per the PR #2 final approval / merge-relaxation brief).** Required approvals lowered from `1` to `0`. Require-approval-of-most-recent-reviewable-push unchecked. Other rules (Restrict deletions, Block force pushes, Require pull request, Require conversation resolution) retained.
- **Merge.** Performed under the relaxed ruleset.
- **Restore (immediately post-merge).** Required approvals reset to `1`. Require-approval-of-most-recent-reviewable-push re-enabled. Restoration verified active via `gh api`.

The window was bounded, documented, and verified. It was also a manual sequence under operator time pressure, performed at the moment the loop was already at maximum cognitive load, and the procedure included no automated tripwire that would have caught a missed restoration.

### 5.3 Three options

The retrospective records three viable directions; the choice is the Approver's and is not made here.

- **A — Formalize the relax / merge / restore window as Phase 1 standard.** Document the procedure in the runbook with an explicit pre-flight checklist, a post-merge verification command, and an explicit "ruleset restore confirmed" gate before the PR is considered closed. Cost: per-PR operator time on every solo-authored merge, plus the governance risk that a missed restoration leaves the repo unprotected. Mitigation: a deterministic post-merge tripwire that compares current ruleset state against a recorded baseline and posts a PR comment if they diverge.
- **B — Add a real second human maintainer with write access.** Cost: trust footprint and onboarding overhead, plus the question of whether the second maintainer's role is defined narrowly (PR-approval gate only) or broadly (full Approver-equivalent). The narrow definition is preferable; it preserves EW §2.3's reservation of approval-matrix items to the Approver while moving only the structural-PR-approval gate.
- **C — Accept per-PR cost.** Continue using the relax / merge / restore window without formalization, treating it as an unavoidable Phase 1 cost of the solo-operator constraint. Cost: governance fragility (the procedure depends on operator memory and the loop's maximum-cognitive-load moment).

The retrospective recommends **A** as the Phase 1 default. **Recommended Phase 1 default: A — formalize the relax / merge / restore window, with a deterministic restore-verification tripwire. Revisit B only if the project adds a trusted second human maintainer.** A matches what actually worked on PR #2 while reducing its fragility through the tripwire; B remains the cleanest long-term governance posture but depends on a trusted second human existing; C is too fragile for a recurring path.

*Standing rule, regardless of A/B/C.* **Any temporary branch-protection or ruleset relaxation must have a documented restore step and a verification record before the loop is considered closed.** This invariant applies whenever the ruleset is relaxed, including under option B (which would relax less often, not never) and under option C (which would relax under similar circumstances to A but without formalization).

`decision-required: solo-operator branch-protection procedure` (the retrospective recommends A; the decision remains the Approver's).
`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` once the decision is made.
`amendment-required: docs/runbooks/vps_development_environment.md` only if option B is selected.

### 5.4 What the retrospective will not propose

- *AI / bot approvers as a second maintainer.* Forbidden per `docs/runbooks/vps_development_environment.md` §14 and EW §2.3. Reaffirmed.
- *Auto-merge under any architecture.* Forbidden per `docs/runbooks/vps_development_environment.md` §14 and EW §2.3. Reaffirmed; see §10.8.
- *Ruleset relaxation without a documented restore.* The PR #2 final approval / merge-relaxation brief already required immediate post-merge restoration; the standing rule under §5.3 generalizes that requirement to any relaxation, not just the PR #2 case.

---

## 6. Loop-closure / terminal-label record gap

### 6.1 The gap

Runbook §4 enumerates 15 progression labels and 5 blocking labels. The progression labels run through `ai:ready-for-human-approval` (the pre-merge terminal state). There is no progression label for the post-merge state. After PR #2 was merged:

- `ai:ready-for-human-approval` was the last label in the loop and was removed at closure.
- No label remained on PR #2 to indicate that the loop had completed successfully (as opposed to closed without merging, abandoned, or stale).
- The post-merge completion confirmation lives as a PR comment (referenced in §2.1) but not as a labeled state.

The loop-state label state of a closed-and-merged PR after stale-label cleanup is therefore no `ai:*` or `blocked:*` labels, which is the same loop-state as a PR that was never labeled at all. The current runbook does not distinguish "loop ran to clean closure" from "PR was opened and closed without going through the loop."

### 6.2 Why this matters

Three downstream effects:

- **Retrospective discoverability.** The post-PR retrospective (this document) had to reconstruct loop completion from comment URLs rather than from a labeled state. A future Project Governor / Context Auditor session reading the closed PR list cannot tell at a glance which closed PRs went through the loop and which did not.
- **Autonomous-loop dispatcher state-machine completeness.** The §10 autonomous-loop direction depends on GitHub labels as the durable state-of-record. A state machine without an explicit terminal state is incomplete; the dispatcher cannot tell the difference between "dispatch already completed and was successful" and "dispatch never happened."
- **Human-readable audit trail.** A reviewer scanning the project's PR history cannot tell which PRs are loop-completed without opening each PR and reading its comments.

### 6.3 Three options

- **A — No new label.** Treat the absence of any `ai:*` or `blocked:*` label on a closed PR as the implicit terminal state. Cost: ambiguity between loop-completed and never-loop-routed.
- **B — Add `ai:loop-complete` (or `ai:merged`) as a sixteenth progression label.** Applied at the post-merge completion confirmation step. Cost: one more label to maintain; benefit: explicit terminal state.
- **C — Use a final Project Governor / Context Auditor PR comment as the terminal record, with no new label.** The completion comment already exists (PR #2's `pull/2#issuecomment-4368632762`); formalize its content and require its presence as the terminal artifact. Cost: human reviewers must read the comment; benefit: no new label and the comment carries reasoning that a label cannot.

A combination of B + C is also viable: the label provides discoverability; the comment provides reasoning. The label and the comment together would be the terminal artifact.

### 6.4 Recommendation

The retrospective recommends **B + C**: a single new progression label `ai:loop-complete` applied at post-merge, paired with a structured Project Governor / Context Auditor completion-confirmation comment as the durable narrative record. The label addresses the autonomous-loop state-machine completeness requirement (a dispatcher reading GitHub state can tell that the loop terminated cleanly) and the discoverability requirement (a reviewer scanning closed PRs sees the terminal state at a glance). The comment addresses the audit-trail requirement.

The label naming choice between `ai:loop-complete` and `ai:merged` is non-trivial. `ai:merged` reads accurately for clean-merge cases but does not cover the case where the loop completes by closing the PR without merging (e.g., the work was correctly abandoned through a Failure Escalation Packet decision). `ai:loop-complete` covers both. The retrospective prefers `ai:loop-complete` for that reason.

`decision-required: terminal-label model` (B+C as recommendation; alternatives A and C-only remain available); `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (label list in §4 and Step 24 in §6 once decided).

### 6.5 Out of scope here

The label naming convention for *closed-without-merge* terminal states (e.g., `ai:loop-complete-no-merge`, `ai:loop-abandoned`, or reuse of an existing `blocked:*` label as the terminal state for unresolved escalations) is a finer-grained decision that belongs to the runbook amendment, not to this retrospective. The retrospective only flags that the closed-without-merge case exists and must be considered when the label set is amended.

---

## 7. Cursor cleanup-pass experiment outcome

### 7.1 What the experiment was

PR #2 was the first PR run in the loop where Cursor (the IDE / agent) was a candidate for the cleanup-pass role. Under the prior preconditions, the operator faced a binary choice for PR #2: include a Cursor cleanup pass on the Builder's diff before QA review (option (a)), or skip the Cursor pass on PR #2 and treat the skip as an experimental datapoint (option (b)). The Approver selected option (b) per Precondition D.

The decision was deliberate. It was not a fallback because Cursor was unavailable. Cursor CLI / Cursor Agent is installed and authenticated on the VPS as `quantdev`, runs from `/srv/quant/dev/quant-research-platform`, and was operationally ready. *This operational-readiness claim is reproduced from the PR #2 / operator handoff and should be verified against the VPS or setup notes before v1.0.* The skip was an experimental design choice to produce a clean comparison datapoint for the retrospective.

### 7.2 What the datapoint says

The work that a Cursor cleanup pass would plausibly have done on PR #2 is dominated by two categories: `ruff format` application across Builder-edited files, and minor lint-level cleanup that `ruff check --fix` would resolve. Both categories of work were done anyway during the GHA fix loop, because GHA's lint and format checks failed and the Builder applied the formatter as part of the bounded fix.

The argument for skipping Cursor on PR #2 was: Cursor likely would have caught or applied some of the same cleanup pre-QA, but the GHA fix loop did the same work post-QA, and the GHA path produced an explicit verdict from the authoritative source of truth. Skipping Cursor cost approximately one fix-loop iteration in clock time. No correctness defect is known to have survived because of the skip.

The argument for including Cursor on a future PR is: a fix-loop iteration includes operator-relay overhead per §3, and a pre-QA cleanup pass would shorten that path. The operator-relay cost on PR #2 was non-trivial. A pre-QA Cursor pass would have moved the formatter work off the operator's foreground time, even though it would not have changed the merge outcome.

### 7.3 Tension this surfaces

The choice between "let GHA produce the verdict on the unformatted diff and fix in the loop" and "pre-format with Cursor, push a formatted diff, and have GHA confirm" is a tradeoff between *governance simplicity* (one source of truth: GHA) and *operator-effort efficiency* (less relay work). On PR #2 with the relay model, governance simplicity won by the Approver's choice. Under the §10 autonomous-loop direction, the same pre-QA cleanup pass becomes a candidate for an automated stage that does not consume operator time, which changes the tradeoff materially.

### 7.4 Recommendation for SCAFFOLD-002

Skip Cursor as a cleanup-pass agent on SCAFFOLD-002 unless one of the following is true:

- the autonomous-loop direction in §10 has progressed far enough that the cleanup pass can run without operator relay (i.e., headless / non-interactive invocation is verified per Phase-0 — see §10.6);
- the §3.3 pre-approved-commands cheat sheet has been adopted into the runbook in a form that explicitly authorizes Cursor's cleanup-pass commands, removing the per-prompt operator interruption that was a relay cost on PR #2;
- the SCAFFOLD-002 scope contains a category of cleanup that GHA cannot easily diagnose in a single fix loop (e.g., large reformatting of pre-existing files outside the Builder's diff scope), making a pre-QA pass materially more efficient.

If none of those is true, default to the GHA-authoritative path used on PR #2 and keep Cursor available as a manual operator tool, not as a loop stage. `decision-required: Cursor cleanup-pass status for SCAFFOLD-002`.

### 7.5 Independence from the autonomous-loop direction

The §10 autonomous-loop direction does not depend on Cursor and does not introduce Cursor as one of the five proposed roles. Cursor is an operator-side IDE / cleanup tool; the §10 loop is a Builder + QA Reviewer + Project Governor / Context Auditor + Governor Auditor + Approver model running on Claude Code and Codex CLIs. The two decisions are orthogonal: Cursor's status as a cleanup-pass agent can change without affecting §10, and §10 can be adopted without affecting Cursor's status.

`informational` for this retrospective; the substantive decision is the `decision-required:` in §7.4.

---

## 8. Cosmetic / rendering artifacts

§8 collects four observations about how content rendered in the operator's tooling and on GitHub during PR #2. None affected correctness; all affected operator experience or readability. The retrospective records them so the runbook's operating notes can warn future sessions, not because any of them is a defect to fix.

### 8.1 Cursor terminal renderer auto-linkifies dotted filenames

During PR #2, the Cursor terminal renderer was observed to auto-linkify dotted filenames (e.g., `.md`, `.py`, `.toml`) inside diff and `gh` output, displaying them as if they were URLs. The behavior is display-only; the underlying text is unchanged, and `gh` and `git` operations were unaffected. The artifact does affect operator scanning of diff output (a filename that looks like a clickable URL is harder to read as a filename) and persists in any setup where Cursor is the operator's terminal client.

The §10 autonomous-loop direction does not solve this. The fix, if pursued, is a different terminal client (or a Cursor configuration change), not a different agent architecture. `informational`; no governance amendment recommended; optional runbook operating note.

### 8.2 Diff renderer occasionally duplicates lines in long file-create previews

During PR #2, the cockpit diff renderer was observed to occasionally display duplicate lines in long file-create previews. The actual file content (verifiable via `git show` and `gh pr diff` against the latest PR commit SHA) did not contain the duplicates. The artifact is display-only, but the operator-relay model is sensitive to it: a duplicate in the rendered diff produces a moment of "is the diff actually wrong" before verification confirms it is not.

`informational`. The mitigation is operator awareness, plus the standing rule that artifact / diff wins over rendering (consistent with EW §9: "review the artifact, not the summary"). No governance amendment recommended; optional runbook operating note.

### 8.3 Heredoc previews compress blank lines visually but preserve them in actual file content

During PR #2, heredoc previews shown in the cockpit were observed to visually compress blank lines while preserving them in the underlying file content. The artifact is display-only and was not the cause of any defect on PR #2; it is recorded because it can produce false-positive concern during plan or fix review ("the plan claims to add a blank line that the preview does not show").

`informational`. Same mitigation as §8.2: artifact / diff wins. No governance amendment recommended; optional runbook operating note.

### 8.4 GitHub renders setext-style H1 (`========`) as huge headers

GitHub Markdown renders setext-style H1 (a line followed by `========` separators) as visually large headers. PR #2 hit this when comments used `========` lines as visual separators rather than as section headers; GitHub's rendering treated them as section headers. This is GitHub-correct Markdown rendering, not a GitHub bug; the convention to follow inside PR comments is to use ATX-style (`# Heading`) for headers and to use a simple line of dashes or other character for visual separators if separators are needed.

`informational`; no governance amendment recommended; optional runbook operating note. The recommendation is operating-procedure: prefer ATX-style headers in PR comments authored by Project Governor / Context Auditor or QA Reviewer.

### 8.5 Why §8 is recorded at all

These artifacts are individually trivial. Collectively, they account for a non-trivial portion of "Did the loop actually do what the diff says?" verification overhead during PR #2. The retrospective records them so the runbook can note them, so future sessions are not surprised, and so the §10 autonomous-loop direction is not credited with solving display-layer problems it does not solve.
## 9. Session-boundary discipline for agent CLIs

### 9.1 The discipline

The current operator tooling used for Builder / QA work has or may expose continue/resume semantics that preserve session context. Where a CLI supports `--continue` or an equivalent resume mode, the discipline is:

- **Default to fresh context per task packet.** A new task packet starts a new session. Cross-packet `--continue` (or equivalent resume) is forbidden.
- **`--continue` is permitted only within a single task packet's lifetime.** Within one packet's run — for example, between the Builder's plan-emission step and the Builder's implementation step, or between an initial fix-application and a re-pushed fix-application after GHA failure — `--continue` is acceptable to preserve in-task context. Within-packet `--continue` is permitted only when the resumed session is still operating from the same approved packet, same PR, and same latest PR commit context; if any of those changed materially, start fresh.
- **A fix loop counts as the same task packet.** A bounded fix prompt issued under §4.4 is part of the originating task packet's lifetime, not a new packet, so `--continue` may be used (subject to the latest-PR-commit qualifier above).
- **A new PR is a new task packet.** Even if the new PR is closely related to the previous one, the agent invocation starts fresh.

### 9.2 Why this matters

Cross-packet `--continue` accumulates context that is no longer authoritative. The risk is silent: the agent's session retains plan content, prior decisions, prior verification claims, and prior error states from the earlier packet, and reapplies them against the new packet's task. This is exactly the "telephone game drift between coding sessions" failure mode that ICG §1 lists as a thing the policy layer is built to prevent.

PR #2 did not fail this discipline (it was the loop's first task packet, so no cross-packet `--continue` was possible by construction), but the discipline was not documented anywhere before this retrospective. SCAFFOLD-002 is the first task packet where cross-packet `--continue` becomes a possibility, and the discipline must be documented before that work begins.

### 9.3 Practical operating notes

- **At the start of each new task packet, the operator confirms the agent CLI starts with a fresh session.** For Claude Code, this is the absence of a `--continue` flag and / or an explicit fresh-session start. For Codex CLI, the analogous fresh-session start.
- **At the end of a task packet (after PR merge or after closure), the operator does not preserve the agent CLI session for cross-packet reuse.** The session is closed; the next task packet starts new.
- **Within a task packet, `--continue` is permitted but not required.** If the operator chooses to start a fresh session mid-packet (for example, after a long break, or to clear out accumulated noise), that is acceptable; the loss is convenience, not governance.
- **Before using within-packet `--continue` after any push, the operator confirms the prompt/session is updated to the latest PR commit SHA.** This is the operating-procedure corollary of ICG §20's latest-commit SHA validation: a resumed session that references a stale SHA must not be used to drive a gate.

### 9.4 Interaction with the autonomous-loop direction

The §10 autonomous-loop direction proposes role-bounded, fresh-session agent invocations as boundary C. Under that model, the dispatcher invokes a new agent process per stage, and the question of `--continue` does not arise — every dispatch is a fresh session by construction. The discipline in §9.1 is the manual / chat-Governor-era equivalent of that boundary, applicable to PR #2's chat-Governor + operator-relay model and to any task packet (including SCAFFOLD-002) that runs before the §10 direction is implemented.

`amendment-required: docs/implementation_context_governance.md` (the discipline aligns with ICG §1 and ICG §11 — fresh-context session discipline — but the per-task-packet rule is not currently spelled out at this resolution).

`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (operating note on the operator's start-of-packet and end-of-packet behavior).

---

## 10. Recommended forward direction — autonomous-loop architecture (condensed)

§10 records the operator-developed autonomous-loop direction as the recommended forward architecture for replacing the chat-Governor + operator-relay plumbing of the loop. The retrospective records this direction at a condensed level: the loop's *governance* (role boundaries, gate sequencing, source-of-truth hierarchy, approval-matrix items) is unchanged; only the loop's *plumbing* (how state transitions are coordinated, how prompts are dispatched, how outputs are captured) is the subject of the autonomous direction.

If the §10 material grows past the condensed scope of this retrospective during drafting or review, the deeper architecture content moves to a separate companion at `docs/reviews/2026-05-05_autonomous_loop_proposal.md`. That companion would itself be observation-and-recommendation only; it would not authorize implementation. Until and unless that companion is created, §10 is the authoritative retrospective record of the recommended direction.

§10 is recorded as a recommendation, not as approved architecture. Every substantive item in §10 is `amendment-required:` or `decision-required:`. Nothing in §10 is decided by this retrospective.

### 10.1 Bias disclosure

The chat-Governor that drafted prior sessions on PR #2 — and that is drafting this retrospective — is the role being partially replaced under the autonomous direction. The retrospective treats critiques of the autonomous direction with appropriate skepticism for that structural conflict of interest. Codex (in the proposed Auditor role, or as adversarial reviewer in the absence of an Auditor) is the appropriate check on chat-Governor critiques of its own replacement. The Approver remains the final authority over both the architecture decision and any specific gate's verdict.

This disclosure is recorded once at the head of §10 and is not repeated in subsequent sub-sections. Readers should apply the disclosure to the entire §10 material, including the recommended directions and the design-risk flags in §10.7 and §10.9.

### 10.2 Why the autonomous direction is being recommended

The §3 operator-effort cost is the architectural driver. The PR #2 loop completed correctly but consumed enough operator foreground time that a second SCAFFOLD-class task running under the same plumbing would compound the cost. The §3 / §4 mitigations (pre-approved-commands cheat sheet, bounded-fix-prompt incidental-command pre-authorization, Builder verification discipline, structured blocker template, prompt-template reuse) reduce the relay volume but do not change the relay model.

The autonomous direction is recommended because it changes the *model*, not just the volume. Under the chat-Governor + operator-relay model, every channel transition between agents is an operator relay event by construction. Under a dispatcher model, channel transitions are deterministic plumbing; the operator's foreground time is consumed by the items that actually require Approver judgment (final PR approval, blocked-state escalation, ambiguous-state resolution), not by every relay between Builder and Project Governor / Context Auditor and QA Reviewer.

The autonomous direction does not promise faster wall-clock cycles than the current model — see §10.5 on the polling-overhead tradeoff. It promises lower operator-foreground cost. Those are different axes; the recommendation is grounded in the operator-foreground axis.

### 10.3 Architecture summary

Four named components, with one role and one boundary each:

- **GitHub** — durable state-of-record and message bus. PR comments are the human-readable audit trail. Labels are the current loop-state. Checks and statuses are gate pass/fail records. Fenced JSON blocks inside PR comments are the machine-readable handoffs (MVP format; a richer artifact-store format is deferred). GitHub Actions logs and poller logs are part of the execution trace. The Issue body is the task packet / scope source.
- **VPS poller / dispatcher** — runtime coordinator. Reads PR/Issue labels, comments, and checks. Determines the next allowed state transition from a fixed state machine. Invokes the correct agent prompt. Captures structured output. Posts comments, artifacts, labels, and checks. Does not interpret strategy, rewrite specs, approve PRs, or decide merge readiness beyond mechanical routing. The poller / dispatcher boundary is recorded in §10.5; its preservation under operational pressure is recorded as a design risk in §10.7.
- **GitHub Actions** — deterministic CI / check runner. Authoritative verdict source for tests, lint, format, and any other CI-defined gate. Unchanged from the current model.
- **Agent CLIs (Claude Code, Codex CLI)** — fresh-session role-bounded invocations dispatched by the poller. No persistent agent process; no agent-to-agent direct communication; no agent-resident state across stages. The fresh-session-by-construction property is the autonomous direction's equivalent of §9's manual session-boundary discipline.

The Approver remains the final authority and the only authority that merges PRs. This is unchanged from the current model and is reaffirmed under §10.5 and §10.8.

### 10.4 Five-role model

The current four-role model (Builder, QA Reviewer, Project Governor / Context Auditor, Approver) expands to five under the autonomous direction. The role boundaries are unchanged from existing governance; the addition is a Governor Auditor role that audits the Project Governor / Context Auditor's gate output rather than the Builder's diff.

- **Builder.** Builds only from approved task packet or fix packet. Implementation only. No self-certification. No merge, no approval. Implemented initially through Claude Code if the Phase-0 spike validates headless operation. Role boundary unchanged from runbook §3 / ICG §6.
- **QA Reviewer.** Audits the PR diff against the task packet, relevant approved spec sections, relevant SDR decisions, GitHub Actions output, traceability matrix, allowed/forbidden-files boundary. Implemented initially through Codex CLI if the Phase-0 spike validates headless operation. Role boundary unchanged from runbook §3 / ICG §21.
- **Project Governor / Context Auditor.** Orchestrates state, performs deterministic guardrail checks, validates plan against source-of-truth hierarchy, performs post-QA and post-fix drift reviews, prepares fix packets or final PR approval brief, routes to Approver on approval-matrix items. Implemented initially through Claude CLI if the Phase-0 spike validates headless operation. Role boundary unchanged from runbook §3 / ICG §6.
- **Governor Auditor (new role).** Audits the Project Governor / Context Auditor's gate output and routing decision. Does not orchestrate. Does not re-do QA (QA was already performed by the QA Reviewer; Auditor scope explicitly excludes Builder-output review). The Auditor may inspect the Governor gate output, cited PR state, labels, checks, comments, and referenced diff/QA evidence as needed to audit the routing decision, but must not re-perform full PR QA or issue implementation/fix instructions. Implemented initially through Codex CLI as the adversarial counterpart to a Claude-CLI-implemented Project Governor / Context Auditor. The disagreement protocol is bounded: Auditor either passes or challenges; Project Governor / Context Auditor gets one response cycle; Auditor gets one re-check; if disagreement remains, the loop stops and escalates to the Approver. No endless debate.
- **Approver.** Final approver, merger, escalation decision-maker. Unchanged from EW §2.3 and from the current model.

The Governor Auditor role is the principal new boundary introduced by the autonomous direction. It exists because the proposed dispatcher's correctness depends on the Project Governor / Context Auditor's gate output being trustworthy, and a single LLM agent producing the gate output and the routing decision is an obvious single-point-of-failure under adversarial-review standards. The Auditor is the adversarial review.

The role-naming distinction matters: this retrospective uses **Project Governor / Context Auditor** as the canonical governance role name, consistent with runbook §3 and ICG §6, and parenthetically notes that the autonomous direction proposes implementing that role through Claude CLI under the Phase-0 spike. The retrospective does not rename the governance role to "Claude Governor." Tool identity is secondary to role boundary; the role survives a CLI change.

### 10.5 Runtime coordination — polling, not webhooks, for β.1 MVP

The autonomous direction's β.1 MVP coordinates state transitions through a VPS-resident poller against the GitHub API. Webhooks are explicitly *not* the β.1 mechanism; they are recorded as the likely long-term evolution, requiring a separate approved task with its own deployment / security review.

**Why polling, not webhooks, for β.1.** Webhooks require a public ingress endpoint. The VPS posture is intentionally private: no public application service ports, loopback-only bindings, explicit approval required for any reverse-proxy / public-exposure change (per `docs/runbooks/vps_development_environment.md` §14). A webhook receiver introduces a public-ingress decision the project is not ready to make at MVP time, and the security review for that decision (HMAC validation, HTTPS termination, endpoint exposure choice, firewall / reverse-proxy / TLS / tunnel choice, service-user model, logging, abuse handling) is itself substantial. Polling avoids the public-ingress decision entirely; the VPS reaches out to GitHub, GitHub never reaches in.

**Rate-limit-aware polling required from day 1, not deferred.** The β.1 poller cannot treat rate-limit handling as a follow-up; it is part of the MVP. Required mechanics:

- *Targeted queries only.* No broad `gh api` sweeps. Each poll cycle queries a known set of active PRs, not the entire repo.
- *ETags and conditional requests.* On every endpoint that supports them. 304 behavior and rate-limit accounting must be verified per endpoint during Phase-0.
- *Active-PR filtering.* Poll only PRs carrying `ai:*` loop-state labels. Closed and merged PRs are not polled.
- *Last-seen-ID tracking.* Avoid re-fetching unchanged comment streams.
- *Rate-limit header monitoring.* `X-RateLimit-Remaining` and `X-RateLimit-Reset` logged per cycle. Warn at 80% of hourly budget consumed; back off at 95%; on 429, stop and wait for reset.
- *Polling cycle interval.* Default 60 seconds. Adaptive intervals (faster during active invocations, slower when idle) are acceptable and preferred.
- *Exponential backoff on 429 / secondary rate limits.* Standard mechanic; not a research item.

**Operator-perceived latency tradeoff.** The poller introduces clock-time overhead the operator-relay model does not. Worst-case end-to-end latency of a four-stage β.1 loop with 60-second polling is roughly four minutes of polling overhead on top of agent invocation time. This is acceptable for MVP because clock time runs in the background while the operator is doing other work; operator effort runs in the foreground and is the cost the autonomous direction is built to reduce. If clock-time overhead becomes painful before webhooks land, adaptive polling intervals are the near-term mitigation. Other GitHub-API-based mechanisms (e.g., `repository_dispatch`) are recorded as open engineering options under §10.9 rather than as near-term operational mitigations. Webhooks are the long-term answer, not the MVP answer.

**Poller / dispatcher boundary.** The poller / dispatcher executes deterministic state-machine transitions only. It must not:

- interpret ambiguous PR state;
- invent fixes;
- decide scope;
- approve PRs;
- merge PRs;
- resolve governance conflicts.

When the state machine encounters an input it cannot route deterministically, the dispatcher stops and escalates to the Approver. This is the boundary that distinguishes "dumb plumbing" from "reasoning agent," and its preservation under operational pressure is recorded as a design risk under §10.7. The autonomous direction's correctness depends on this boundary holding; if the boundary erodes incrementally — for example, by allowing the dispatcher's "next allowed state transition" logic to absorb special-case handling for ambiguous PR states — the dispatcher silently becomes a reasoning agent, and the Auditor / Approver gates are no longer protecting what they were built to protect.

**Auto-merge prohibition reaffirmed.** Under the autonomous direction, agents may produce checks, comments, and labels. The Approver remains the only authority that merges PRs. This is reaffirming existing governance from `docs/runbooks/vps_development_environment.md` §14 and EW §2.3, not introducing a new rule. The autonomous direction's correctness depends on the prohibition holding under all phases (Phase-0, β.1, β.2, and any future evolution including webhooks).

`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (autonomous-loop architecture as a runbook section under the same governance umbrella, drafted only after the Phase-0 spike resolves the make-or-break headless-invocation questions in §10.6).
`amendment-required: docs/implementation_context_governance.md` (policy-layer recognition of the dispatcher boundary and the Auditor role; ICG already governs Builder / QA / Project Governor / Context Auditor / Approver, but does not yet recognize a deterministic-dispatcher coordination layer or an Auditor role).
`decision-required: autonomous-loop architecture acceptance` (the architecture itself is a Phase-1 governance decision; this retrospective recommends, the Approver decides).

### 10.6 Phasing — Phase-0 spike, β.1, β.2; SCAFFOLD-002 independent

The autonomous direction is phased into three steps. The phasing is recorded as the recommended sequence; the actual phase boundaries are decisions reserved to the Approver and require the SCAFFOLD-class autonomous-loop task packet that this retrospective does not draft.

**Autonomous-loop implementation track:** Phase-0 spike → β.1 → β.2.

**SCAFFOLD-002 implementation workstream:** independent. SCAFFOLD-002 is not gated on the autonomous-loop architecture existing. If the autonomous loop is not ready, SCAFFOLD-002 proceeds under the current chat-Governor + operator-relay model, with the §3 / §4 mitigations applied where approved. The two tracks may run in parallel; the §1 non-authorization statement applies equally to both.

**Phase-0 spike — make-or-break.** The autonomous direction has two questions whose answers determine whether the architecture is viable at all:

1. **Claude Code non-interactive / headless invocation.** Exact command, exact output behavior, exact structured-output behavior. The Builder and Project Governor / Context Auditor roles depend on it.
2. **Codex CLI non-interactive / headless invocation.** Exact command, exact output behavior, exact structured-output behavior. The QA Reviewer and Governor Auditor roles depend on it.

If either CLI cannot be invoked headlessly with reliable structured output, the architecture changes — either by substituting a different agent runtime, by accepting an interactive component (which removes much of the autonomous direction's value), or by deferring the entire direction. The Phase-0 spike is therefore a hard gate on the SCAFFOLD-class autonomous-loop task packet. The retrospective recommends that the Phase-0 spike be authorized as its own deliverable, scoped narrowly to verifying these two CLIs and recording the verified commands and behaviors, *before* any β.1 task packet is drafted.

The Phase-0 spike's deliverable is documentation, not code. Specifically: a Phase-0 verification note recording, for each CLI, the verified headless invocation command, the verified output format, the verified exit-code behavior on the success and failure paths, the verified prompt-input mechanism (stdin, file, argument), and any operational caveats discovered during verification. The Phase-0 verification note belongs under `docs/reviews/`. Suggested path pattern: `docs/reviews/2026-05-05_phase0_autonomous_loop_headless_cli_verification.md` (or the equivalent date-stamped path on the day the spike is performed). It is not a runbook amendment by itself; it is the input to the SCAFFOLD-class autonomous-loop task packet.

**β.1 — dispatcher with four roles.** β.1 implements the hybrid GitHub-state + VPS-poller dispatcher with Builder, QA Reviewer, and Project Governor / Context Auditor roles. The Governor Auditor is not part of β.1; during the β.1 window, the Approver manually performs any Auditor-like challenge/review needed before final approval. The β.1 scope includes pause / resume / restart / idempotency mechanics from the start (per §10.7), the rate-limit-aware polling mechanics from day 1 (per §10.5), and the disagreement-protocol mechanics scoped down to a single Governor-without-Auditor configuration. β.1 is the proof point that the dispatcher works at all; it is not the final architecture.

**β.2 — add Governor Auditor.** β.2 layers the Codex-CLI-implemented Governor Auditor on top of working β.1 dispatcher mechanics. β.2 introduces the bounded disagreement protocol described in §10.4 between Project Governor / Context Auditor and Governor Auditor. β.2 is the autonomous direction's full five-role configuration.

**Why β.1 and β.2 are split.** Restart correctness, slash-command authorization, headless CLI behavior, and idempotent state transitions are make-or-break. The retrospective recommends a reliable autonomous-loop MVP with Approver-as-substitute-Auditor first, then layering the Auditor on top, rather than a single-step rollout that combines new dispatcher mechanics with new role mechanics simultaneously. A combined rollout doubles the surface area for failure-mode discovery; a phased rollout isolates the dispatcher's failure modes from the Auditor's failure modes.

**Recommended sequencing summary.** Phase-0 spike → SCAFFOLD-class autonomous-loop task packet draft → β.1 task packet → β.1 build under the current loop → β.2 task packet → β.2 build under β.1. SCAFFOLD-002 runs independently under whichever loop architecture is active at the time it is authorized.

`decision-required: Phase-0 spike authorization` (separate from the autonomous-loop architecture acceptance; the Phase-0 spike can be authorized without committing to β.1 or β.2).
`decision-required: β.1 / β.2 phasing acceptance` (only after the Phase-0 spike resolves the make-or-break questions; the Approver may revise the phasing based on Phase-0 findings).

### 10.7 Primary design concerns — restart correctness, slash-command authorization, dispatcher-boundary erosion

These three concerns are recorded as primary design concerns for the SCAFFOLD-class autonomous-loop task packet, not as objections to the architecture. The retrospective's posture is that each is solvable, and that each is most likely to fail if rushed or under-specified at the SCAFFOLD-class packet stage. They are recorded here so that the SCAFFOLD-class packet treats them as first-class scope items rather than as implementation details discovered during build.

**Restart correctness (operator-elevated, primary design concern).** Every dispatched agent run gets a unique invocation_id. Before dispatching, the poller records the active invocation_id, the agent role, the PR number, the latest PR commit SHA, the stage, the started-at timestamp, and the expected output type in GitHub-visible state. Every agent output comment includes the same invocation_id in its structured block. On restart, the poller reads current labels / checks / comments, finds the active invocation_id, and determines exactly one of:

- *matching completion output exists* → advance state idempotently;
- *no completion output and timeout not reached* → wait;
- *no completion output and timeout reached* → retry if read-only stage, or escalate / recovery-check if Builder stage (Builder interruption is more conservative because partial local file edits may exist);
- *ambiguous state* → stop and escalate to Approver.

The poller is idempotent: no duplicate dispatch, no duplicate state advancement, retry only with a new invocation_id. The handoff from PR #2 elevated this concern explicitly, and the retrospective records it as elevated. A dispatcher that cannot recover correctly from a restart is a dispatcher that silently corrupts state under operational disruption; that failure mode is exactly the class of failure the loop is built to prevent.

**Slash-command authorization (operator-elevated, primary design concern).** The poller honors slash-commands (`/loop pause`, `/loop resume`, `/loop stop`, `/governor rerun`, `/codex-qa rerun`, `/auditor rerun`) only from authorized users — write / maintain / admin permission at minimum. Commands are honored only as the first non-whitespace content on the first line of a standalone comment, not as embedded text inside Builder or QA outputs. Stop / resume / override commands may require confirmation syntax (e.g., `/loop stop confirm`). A slash-command authorization failure mode that the SCAFFOLD-class packet must explicitly handle: a Builder agent that quotes a slash-command in its own output as part of explanatory text must not trigger the dispatcher to act on the quoted command. Quoting and dispatch must be cleanly separated by parser design, not by hope.

**Dispatcher-boundary erosion (design risk).** The poller / dispatcher boundary in §10.5 — deterministic state-machine transitions only, never reasoning — is the boundary the autonomous direction's correctness depends on. The boundary is at risk under operational pressure: when the dispatcher encounters ambiguous PR state, the path of least resistance is to add special-case handling to the "next allowed state transition" logic rather than to escalate to the Approver. Each special case looks small in isolation; the cumulative effect is a dispatcher that has silently absorbed reasoning. The SCAFFOLD-class autonomous-loop task packet must specify (a) the explicit set of state-machine transitions the dispatcher is allowed to perform, (b) the explicit escalation behavior for any input outside that set, and (c) a periodic review mechanism that re-checks whether the dispatcher's logic has drifted past the deterministic boundary. The Auditor role provides one layer of protection against this drift, but the Auditor audits gate output, not dispatcher logic; the dispatcher's boundary is its own audit responsibility.

The handoff from PR #2 elevated restart correctness and slash-command authorization as primary design concerns. The dispatcher-boundary erosion risk is recorded by this retrospective as a third primary concern at the same severity level, because the autonomous direction is structurally exposed to it and existing governance does not yet cover it.

`amendment-required: docs/implementation_context_governance.md` (policy-layer recognition of the dispatcher boundary, the restart-correctness invariants, and the slash-command authorization rules; these are implementation-context-governance concerns, not just runbook concerns, because they govern how the Project Governor / Context Auditor function is mechanized).
`amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (operating procedure for the dispatcher's intervention controls — pause / resume / stop / rerun — and the slash-command syntax).

### 10.8 Explicit non-goals

The autonomous direction explicitly excludes the following. Each is reaffirming existing governance where it already exists, not introducing a new prohibition.

- **No auto-merge under any architecture.** Reaffirms `docs/runbooks/vps_development_environment.md` §14 and EW §2.3. Agents may produce checks, comments, and labels; the Approver remains the only authority that merges PRs. The prohibition holds under Phase-0, β.1, β.2, and any future webhook-based evolution.
- **No AI / bot account as GitHub PR approver.** Reaffirms `docs/runbooks/vps_development_environment.md` §14 and EW §2.3. The structural branch-protection problem under §5 is *not* solved by giving an AI the approver role.
- **No agent-to-agent direct communication.** Agents do not call other agents. State transitions are mediated by the dispatcher reading and writing GitHub state. The fresh-session-by-construction property in §10.3 depends on this.
- **No webhook-driven dispatch in β.1 MVP.** Webhooks are deferred to long-term evolution. The β.1 dispatcher uses polling per §10.5. Adopting webhooks at any later phase requires a separate approved task with its own deployment / security review (HMAC validation, HTTPS termination, endpoint exposure decision, firewall / reverse-proxy / TLS / tunnel choice, service-user model, logging, abuse handling).
- **No Approver as relay operator.** The autonomous direction's purpose is to remove the Approver from the per-channel relay path. The Approver remains in the loop for approval-matrix items (final PR approval, blocked-state escalation, ambiguous-state resolution per §10.7); the Approver is not a step in routine state transitions.
- **No poller-as-reasoning-agent.** The dispatcher's deterministic-only boundary in §10.5 holds. The dispatcher-boundary-erosion risk in §10.7 names this explicitly.
- **No pane-driven inter-agent communication.** Agent invocations are dispatched processes, not terminal-pane content piped between operator-controlled panes. The cockpit four-pane model (A — Operator, B — Builder, C — Cleanup, D — QA) remains operator-side for visibility, not as an inter-agent channel.

The non-goals are recorded explicitly because the autonomous direction's design space is large and each excluded option has surface plausibility. Recording the exclusions makes the SCAFFOLD-class autonomous-loop task packet's scope review tractable.

### 10.9 Open engineering questions deferred to the SCAFFOLD-class packet

The following questions are recorded for the SCAFFOLD-class autonomous-loop task packet to resolve. They are *not* answered in this retrospective. Items 1 and 2 are make-or-break per §10.6 and are the Phase-0 spike's deliverable. Items 3 through 12 are scope items the SCAFFOLD-class packet must address.

1. Exact Claude Code non-interactive / headless invocation command and output behavior. *(Phase-0 spike deliverable.)*
2. Exact Codex CLI non-interactive / headless invocation command and output behavior. *(Phase-0 spike deliverable.)*
3. Whether the poller authenticates to GitHub as `quantdev`, a dedicated machine user, or another approved identity. The decision interacts with the slash-command authorization rules in §10.7.
4. Minimum viable poller runtime: bash + `gh`, Python script, cron / systemd timer, or long-running service. Each option has different restart-correctness implications per §10.7.
5. How GitHub checks / statuses are created from poller results. Native `gh api` checks-API usage, statuses-API usage, or a combination.
6. How structured JSON blocks are parsed reliably from PR comment bodies. Fenced-block delimiter convention, parser robustness against agent-produced quoting and escaping, and behavior under partial / truncated comment content.
7. How the poller prevents duplicate invocation and handles restart in detail (high-level invariants in §10.7; concrete mechanism deferred).
8. How operator override comments are parsed and authorized in detail (high-level invariants in §10.7; concrete mechanism deferred).
9. What labels are added or revised for autonomous stages, including pause-state labels and the §6 terminal-state label. The autonomous direction's label set is a superset of the current 15-progression / 5-blocking model; the actual delta is for the SCAFFOLD-class packet to specify.
10. Whether this requires amendments to `docs/runbooks/governor_gated_github_pr_agent_loop.md`, `docs/implementation_context_governance.md`, or both. The retrospective tags both throughout §10; the SCAFFOLD-class packet finalizes the split.
11. **GitHub comment-size / evidence-storage boundary (design risk).** GitHub comment bodies have practical size limits, and Builder verification outputs, large diff excerpts, multi-megabyte logs, and structured artifacts may exceed those limits. The β.1 dispatcher's reliance on PR comments as the durable handoff format is correct for state but may be insufficient for some categories of evidence. The SCAFFOLD-class packet must specify (a) what Builder / QA / Governor / Auditor outputs are expected to fit in a single comment, (b) what outputs require an alternative durable store (committed file under `docs/reviews/`, attached artifact, repository-dispatch event payload, or external object store), and (c) the boundary criteria for choosing between in-comment and out-of-comment evidence. The retrospective records this as an open engineering question rather than as a near-term mitigation; the answer is design work, not an operational tweak.
12. **GitHub `repository_dispatch` events as a clock-time-overhead mitigation.** Recorded here per §10.5's redirection. `repository_dispatch` is GitHub-API-based and avoids the public-ingress decision that webhooks require, but introduces its own design / security / authorization questions: who can fire dispatch events, how are they authorized, how are they scoped to the autonomous-loop dispatcher rather than to other consumers, and how are they reconciled with the polling-based state machine. Evaluation belongs in the SCAFFOLD-class packet, not in this retrospective.

The list is not promised to be exhaustive. It is the set of open questions the retrospective surfaces; the SCAFFOLD-class packet may identify others during its own scope review.

`artifact-required: SCAFFOLD-class autonomous-loop task packet` (a new artifact, drafted under EW §2.2 task-packet discipline, ICG governance, and the approved runbook workflow; not authored by this retrospective).

---

## 11. Recommendations register

§11 is the actionable index for this retrospective. Every observation in §3–§10 that produces a follow-on action appears here once, in summary form, with its tag.

**Tag semantics.** Tags below have the following operative meanings:

- `amendment-required: <doc>` — the recommended action requires a change to the named document, performed via that document's standard change process. EW changes follow EW §13. ICG / runbook changes follow each document's own change process. Locked Engineering Specification sections are not in scope for this retrospective and are not tagged here.
- `artifact-required: <artifact>` — the recommended action requires a new artifact (task packet, verification note, companion proposal). The new artifact is drafted under the governance regime appropriate to its type (EW §2.2 task-packet discipline for task packets; runbook / ICG governance for operating notes; EW §3 for Engineering Specification sections, none of which appear in this retrospective).
- `decision-required: <topic>` — the recommended action requires an Approver decision before any amendment or artifact is drafted. Tags this severity are precondition gates on the corresponding `amendment-required:` or `artifact-required:` items.
- `informational` — recorded for the retrospective's narrative integrity; no follow-on action.

The retrospective does not draft amendment text, does not draft task packets, and does not approve any item below.

### 11.1 Operator-experience cost mitigations (§3)

| Item | Source | Tag(s) |
|---|---|---|
| Pre-approved-commands cheat sheet, by tool (Codex CLI `p` safe / never-safe sets; Claude Code option-2 guidance; scope guard limiting preauthorization to repo / PR context only) | §3.3 #1 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| Bounded fix prompts pre-authorize incidental sanity commands (`which`, `--version`, `ls`, `cat`, etc., subject to the §3.3 scope guard) | §3.3 #2 / §4.4 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| Mid-loop request to spawn a Governor agent — declined as rules-mid-flight; structural change deferred to §10 | §3.4 | `informational` |

### 11.2 Process gaps observed during PR #2 (§4)

| Item | Source | Tag(s) |
|---|---|---|
| Project Governor / Context Auditor plan-validation checklist gains four items: pre-existing-files-vs-create, packet → plan wording-drift, ruff-rule-vs-selected-ruleset, formatter-step-omission | §4.1 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md`; `amendment-required: docs/implementation_context_governance.md` |
| Builder must include verification output inline with state-of-the-world claims; Project Governor / Context Auditor rejects unsupported claims and may spot-check critical claims under deterministic guardrail review | §4.2 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md`; `amendment-required: docs/implementation_context_governance.md` |
| Cockpit principle refined to "no local *verification* runs as source-of-truth"; Builder-side use of project-pinned formatter / dev-toolchain transforms permitted; GHA remains the authoritative verdict | §4.3 | `amendment-required: docs/implementation_context_governance.md`; `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| Bounded fix-prompt template gains an "incidental commands pre-authorized" line (per §3.3 scope guard) | §4.4 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| Bounded mid-flight blocker template (Builder's exit hatch from the fix-loop) added | §4.5 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| Heredoc / Cursor terminal-pane truncation operating note (>50-line paste threshold; nano + `/tmp` transit-file + `gh ... --body-file` workaround for large comments) | §4.6 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| Approver pre-issuance prompt review formalized only for first-use templates, high-risk prompts, approval-sensitive tasks, or ambiguity-flagged prompts; reusable Governor prompt templates established | §4.7 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| Adopt canonical runbook §6 step numbers in chat, PR comments, and retrospective records; avoid separate session-step shorthand | §4.8 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |

### 11.3 Solo-operator branch-protection procedure (§5)

| Item | Source | Tag(s) |
|---|---|---|
| Solo-operator branch-protection procedure: recommended Phase 1 default A — formalize relax / merge / restore window with deterministic restore-verification tripwire; revisit B if a trusted second human maintainer exists | §5.3 | `decision-required: solo-operator branch-protection procedure`; `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (after decision); `amendment-required: docs/runbooks/vps_development_environment.md` (only if option B selected) |
| Standing rule (regardless of A/B/C): any temporary branch-protection or ruleset relaxation must have a documented restore step and a verification record before the loop is considered closed | §5.3 | `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |

### 11.4 Loop-closure / terminal-label record gap (§6)

| Item | Source | Tag(s) |
|---|---|---|
| Add `ai:loop-complete` as a sixteenth progression label, applied at post-merge; pair with a structured Project Governor / Context Auditor completion-confirmation comment as the durable narrative record (B + C combination); closed-without-merge label sub-question scoped into the runbook amendment, not into this retrospective | §6.4 | `decision-required: terminal-label model`; `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` (label list in §4 and Step 24 in §6 once decided) |

### 11.5 Cursor cleanup-pass status (§7)

| Item | Source | Tag(s) |
|---|---|---|
| Skip Cursor as a cleanup-pass agent on SCAFFOLD-002 by default; retry only if (a) autonomous-loop direction has progressed far enough that the cleanup pass runs without operator relay, (b) §3.3 cheat sheet adopted in a form that explicitly authorizes Cursor's cleanup-pass commands, or (c) SCAFFOLD-002 scope contains cleanup that GHA cannot easily diagnose in a single fix loop | §7.4 | `decision-required: Cursor cleanup-pass status for SCAFFOLD-002` |
| Cursor and the autonomous-loop direction are orthogonal; Cursor's status can change without affecting §10, and §10 can be adopted without affecting Cursor's status | §7.5 | `informational` |

### 11.6 Cosmetic / rendering artifacts (§8)

| Item | Source | Tag(s) |
|---|---|---|
| Cursor terminal renderer auto-linkifies dotted filenames; mitigation is operator awareness or a different terminal client | §8.1 | `informational`; optional runbook operating note |
| Cockpit diff renderer occasionally displays duplicate lines in long file-create previews; artifact / diff wins per EW §9 | §8.2 | `informational`; optional runbook operating note |
| Heredoc previews compress blank lines visually but preserve them in actual file content | §8.3 | `informational`; optional runbook operating note |
| GitHub renders setext-style H1 (`========`) as huge headers; prefer ATX-style (`# Heading`) in PR comments authored by Project Governor / Context Auditor or QA Reviewer | §8.4 | `informational`; optional runbook operating note |

### 11.7 Session-boundary discipline for agent CLIs (§9)

| Item | Source | Tag(s) |
|---|---|---|
| Default to fresh context per task packet; cross-packet `--continue` or equivalent forbidden; within-packet `--continue` permitted only when same approved packet, same PR, and same latest PR commit context; before within-packet `--continue` after any push, operator confirms the prompt/session is updated to the latest PR commit SHA | §9.1, §9.3 | `amendment-required: docs/implementation_context_governance.md`; `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |

### 11.8 Autonomous-loop architecture (§10)

| Item | Source | Tag(s) |
|---|---|---|
| Autonomous-loop architecture acceptance (GitHub state-of-record + VPS poller dispatcher + fresh-session agent CLIs + Approver final authority) | §10.5 | `decision-required: autonomous-loop architecture acceptance` |
| Autonomous-loop architecture acceptance, if approved, requires runbook and ICG amendments recognizing the dispatcher boundary, GitHub-state/poller architecture, fresh-session CLI dispatch model, and Governor Auditor role | §10.5 | `decision-required: autonomous-loop architecture acceptance`; `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md`; `amendment-required: docs/implementation_context_governance.md` |
| Phase-0 spike authorization (separate from architecture acceptance; can be authorized without committing to β.1 / β.2; deliverable is a verification note at `docs/reviews/2026-05-05_phase0_autonomous_loop_headless_cli_verification.md` or the equivalent date-stamped path) | §10.6 | `decision-required: Phase-0 spike authorization`; `artifact-required: Phase-0 verification note under docs/reviews/` |
| β.1 / β.2 phasing acceptance (only after Phase-0 resolves the make-or-break questions; phasing may be revised based on Phase-0 findings) | §10.6 | `decision-required: β.1 / β.2 phasing acceptance` |
| Primary design concerns recognized in policy: restart correctness, slash-command authorization, dispatcher-boundary erosion (deterministic-state-machine boundary preservation under operational pressure) | §10.7 | `amendment-required: docs/implementation_context_governance.md`; `amendment-required: docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| SCAFFOLD-class autonomous-loop task packet drafted (under EW §2.2 task-packet discipline, ICG governance, and the approved runbook workflow); not authored by this retrospective | §10.9 | `artifact-required: SCAFFOLD-class autonomous-loop task packet` |
| Open engineering questions deferred to the SCAFFOLD-class packet (12 items, including the Phase-0 deliverables and the §10.9 design risks: GitHub comment-size / evidence-storage boundary; `repository_dispatch` evaluation as a clock-time-overhead mitigation) | §10.9 | `informational` here; concrete items are scope inputs to the `artifact-required:` SCAFFOLD-class packet above |

### 11.9 Cross-cutting and meta items

| Item | Source | Tag(s) |
|---|---|---|
| GitHub-derived facts in §2.1 (merge timestamp, ruleset restore verification, repository visibility flip, pre-flip secret-scan audit outcome) are reproduced from the post-PR-#2 handoff and pending independent verification before v1.0 promotion | §2.1, §13 | `informational`; verification pass is a v0.1 → v1.0 precondition |
| §7.1 Cursor operational-readiness claim is reproduced from the post-PR-#2 handoff and pending verification against the VPS or setup notes before v1.0 promotion | §7.1, §13 | `informational`; verification pass is a v0.1 → v1.0 precondition |
| EW §13 re-read trigger applies before SCAFFOLD-002 work begins: operator re-reads EW, ICG, and runbook | §12 (precondition list) | `informational`; precondition |

### 11.10 Index of `decision-required:` and `amendment-required:` items

For Approver scanning convenience, the items requiring a decision or a document change are concentrated below. This index is derived from §11.1–§11.9 and adds no new items.

**Decisions required (Approver):**

1. Solo-operator branch-protection procedure — A / B / C (§5.3; recommendation: A).
2. Terminal-label model — A / B / C / B+C (§6.4; recommendation: B+C, label `ai:loop-complete`).
3. Cursor cleanup-pass status for SCAFFOLD-002 (§7.4; recommendation: skip by default, retry under three named conditions).
4. Numbering convention reconciliation (§4.8; recommendation: canonical runbook §6 step numbers).
5. Autonomous-loop architecture acceptance (§10.5; recommendation: accept with phasing).
6. Phase-0 spike authorization (§10.6; recommendation: authorize as a separate deliverable scoped to headless-CLI verification).
7. β.1 / β.2 phasing acceptance (§10.6; recommendation: phased, β.1 first, β.2 only after β.1 proves out).

**Amendments required (named document; standard change process applies):**

- `docs/runbooks/governor_gated_github_pr_agent_loop.md` — accumulated runbook amendments from §4.1, §4.2, §4.3, §4.4, §4.5, §4.6, §4.7, §4.8, §5.3, §6.4, §9, §10.5, §10.7. Drafted as a single amendment package or as a sequenced series; the amendment process determines the split.
- `docs/implementation_context_governance.md` — accumulated ICG amendments from §4.1, §4.2, §4.3, §9, §10.5, §10.7. Same drafting-package consideration as the runbook.
- `docs/runbooks/vps_development_environment.md` — only if option B is selected for §5.3 (second human maintainer convention).

**Artifacts required (new):**

- Phase-0 verification note at `docs/reviews/2026-05-05_phase0_autonomous_loop_headless_cli_verification.md` (or equivalent date-stamped path).
- SCAFFOLD-class autonomous-loop task packet (drafted under EW §2.2 + ICG + runbook governance; not authored by this retrospective).
- Optional companion at `docs/reviews/2026-05-05_autonomous_loop_proposal.md` if §10's recommended-direction material grows past the condensed scope of this retrospective.

The retrospective stops here on amendments and artifacts. Drafting any of them is out of scope per §1.3.

---

## 12. Pre-SCAFFOLD-002 gates

§12 lists the items that must close before the SCAFFOLD-002 task packet drafting begins. The list is the operational expression of the operator's gating direction in the post-PR-#2 handoff: SCAFFOLD-002 work is gated on this retrospective's completion or explicit Approver waiver. §12 makes that gating concrete.

The Phase-0 spike (§10.6) is *not* among these gates. The autonomous-loop architecture is a separate implementation track per §10.6's phasing summary; SCAFFOLD-002 is independent of autonomous-loop existence.

### 12.1 Hard gates — must close before SCAFFOLD-002 task packet drafting

1. **This retrospective at v1.0.** v0.1 DRAFT promotes to v1.0 only after the §13 verification pass closes the GitHub-derived facts in §2.1 and the Cursor operational-readiness claim in §7.1. Either v1.0 promotion or an explicit Approver waiver of the gate satisfies this item.
2. **Operator re-read of EW, ICG, and runbook.** EW §13 re-read trigger applies. SCAFFOLD-002 is a new module-type context (it is implementation under the loop, where SCAFFOLD-001 was the loop's first run); the re-read is required by EW §13 and is recorded here as a precondition rather than as a recommendation.
3. **§11.10 decisions 1–4 (the four non-autonomous-loop decisions).** Specifically: solo-operator branch-protection procedure (§5.3 / §11.10 item 1); terminal-label model (§6.4 / §11.10 item 2); Cursor cleanup-pass status for SCAFFOLD-002 (§7.4 / §11.10 item 3); numbering convention reconciliation (§4.8 / §11.10 item 4). Each is a precondition for SCAFFOLD-002's task packet because the packet's structure depends on the answers (e.g., the packet must specify branch-protection procedure under the chosen option; the packet must specify whether Cursor is a stage; the packet must use the chosen numbering convention).

§11.10 decisions 5–7 (autonomous-loop architecture acceptance; Phase-0 spike authorization; β.1 / β.2 phasing) are *not* hard gates on SCAFFOLD-002. They gate the autonomous-loop track only.

### 12.2 Soft gates — recommended but not blocking

1. **§11.1 / §11.2 highest-leverage runbook amendments adopted.** The pre-approved-commands cheat sheet (§3.3 / §11.1) and the §4.1 / §4.2 / §4.4 / §4.5 amendments materially reduce SCAFFOLD-002's relay cost. Their adoption before SCAFFOLD-002 is not strictly blocking, but the operator-effort cost of running SCAFFOLD-002 without them is the same cost §3 records as the dominant pain point. The retrospective recommends adopting them before SCAFFOLD-002 begins.
2. **§9 session-boundary discipline documented.** The discipline is currently captured only in this retrospective and in the post-PR-#2 handoff. Before SCAFFOLD-002 begins, the discipline should be written into the runbook's operating notes at minimum, even if the policy-layer ICG amendment is deferred.
3. **§5.3 standing rule documented.** The "any temporary branch-protection or ruleset relaxation must have a documented restore step and a verification record before the loop is considered closed" invariant is the smallest concrete deliverable the §5 decision can produce; it can be added to the runbook independently of the larger A/B/C decision and removes a known governance fragility.

### 12.3 Out of scope for §12

- **The SCAFFOLD-002 task packet itself.** Drafting the packet is a separate activity under EW §2.2 / runbook §16 once the §12.1 hard gates close. The retrospective does not draft it.
- **The autonomous-loop track gates.** Recorded under §11.8 / §11.10 items 5–7. Independent of SCAFFOLD-002 per §10.6.
- **Cleanup of branch `scaffold/scaffold-001-repo-skeleton`.** Recorded under §13 as a deferred decision, not as a SCAFFOLD-002 gate.

---

## 13. Deferred items, open questions, and v1.0 verification gates

§13 collects items the retrospective records but does not act on. Three categories.

### 13.1 Deferred operational items

1. **Branch `scaffold/scaffold-001-repo-skeleton` deletion.** Retained on `origin` per the post-PR-#2 handoff, with deletion deferred to this retrospective. The retrospective recommends **deletion**, on the basis that the merge commit on `main` (`1aa31689a922dc074ecf49100a439210f528cb93`) and the latest PR commit SHA at the final gate (`f13e926ade498c1ae97182587365f297f2bbfa21`, preserved as the parent of the merge commit) together preserve all SCAFFOLD-001 history reachable from `main`. The branch's continued existence on `origin` adds discoverability noise without governance value. `decision-required: scaffold/scaffold-001-repo-skeleton deletion`. The decision is small and can be executed at v1.0 promotion time.
2. **Whether the post-PR-#2 retrospective convention itself becomes a runbook step.** This retrospective exists because the operator handoff requested it after PR #2; the runbook §6 has no canonical retrospective step. Adopting the retrospective as a permanent runbook step would itself be a runbook amendment. The retrospective records this as an open governance question for the runbook's maintainers; it does not recommend adoption as a permanent step yet. One PR's evidence is insufficient to establish whether the retrospective convention should become standing practice or remain a one-off post-SCAFFOLD-001 artifact. `decision-required: retrospective as standing runbook convention` (deferred; revisit after SCAFFOLD-002 closes).

### 13.2 Open questions for future amendments and packets

The substantive open questions are concentrated in §10.9 (autonomous-loop) and in §11.10's `decision-required:` index. §13.2 collects open questions that did not fit either bucket and that the retrospective does not own.

1. **Closed-without-merge label sub-question.** The terminal-label model (§6) needs a label naming for the closed-without-merge case (e.g., `ai:loop-complete-no-merge`, `ai:loop-abandoned`, or reuse of a `blocked:*` label as the terminal state for unresolved escalations). Belongs to the runbook amendment, not to the retrospective. `informational` here.
2. **Long-term webhook adoption.** §10.5 / §10.8 records webhooks as the long-term evolution of the autonomous-loop coordination mechanism, requiring a separate approved task with its own deployment / security review. The retrospective does not list specific webhook design questions; they belong to the post-MVP autonomous-loop work, after β.1 has produced operating evidence. `informational`.
3. **Whether `ops.provider_raw_payloads` and other governed Section 2 / Section 6 surfaces produce evidence categories that hit §10.9 #11's GitHub comment-size boundary during implementation.** Recorded as a potential design risk for any future autonomous-loop SCAFFOLD-class packet that touches Section 2 / Section 6 implementation; not a SCAFFOLD-001 / SCAFFOLD-002 concern. `informational`.

### 13.3 v1.0 verification gates

This retrospective is v0.1 DRAFT. The §1 non-authorization statement and the §2.1 / §7.1 verification notes flag specific facts that are reproduced from the post-PR-#2 handoff but are not all independently proven by the markdown files in this repository at v0.1 time. v1.0 promotion is conditional on the following verification pass.

| Fact | Source | Verification mechanism |
|---|---|---|
| PR #2 merged-at timestamp `2026-05-04T05:39:07Z` | §2.1 | `gh pr view 2 --json mergedAt`; cross-reference against the merge commit on `main` |
| Merge commit on `main` `1aa31689a922dc074ecf49100a439210f528cb93` | §2.1 | `git rev-parse main`; cross-reference against `gh pr view 2 --json mergeCommit` |
| Latest PR commit SHA at final gate `f13e926ade498c1ae97182587365f297f2bbfa21` (preserved as parent of merge commit) | §2.1, §2.2 | `git log --first-parent main`; verify the named SHA is parent of the merge commit |
| Ruleset `main protection` Active enforcement and configuration restored to pre-merge state | §2.1, §5.2 | `gh api repos/prodempsey/quant-research-platform/rulesets`; compare against the recorded baseline |
| Repository visibility public, post-secret-scan-audit-clean | §2.1 | `gh api repos/prodempsey/quant-research-platform --jq .visibility`; cross-reference against the prior governance trail recording the secret-scan audit |
| Issue #1 closed; reason `completed`; stale labels stripped | §2.1 | `gh issue view 1 --json state,stateReason,labels` |
| PR #2 stale labels stripped; branch `scaffold/scaffold-001-repo-skeleton` retained on `origin` | §2.1 | `gh pr view 2 --json labels`; `git ls-remote origin scaffold/scaffold-001-repo-skeleton` |
| Loop-trace comment IDs (`pull/2#issuecomment-4368233682`, `pull/2#issuecomment-4368499035`, `pull/2#issuecomment-4368632762`) exist and have the post-fix-drift-check / final approval brief / post-merge completion confirmation content | §2.1 | `gh api repos/prodempsey/quant-research-platform/issues/comments/<id> --jq .body`; review content for each |
| Cursor CLI / Cursor Agent installed and authenticated on the VPS as `quantdev`, runs from `/srv/quant/dev/quant-research-platform`, no production-secret access | §7.1 | VPS-side check by the operator; cross-reference against `docs/runbooks/vps_development_environment.md` |

The verification pass is performed by the operator. The retrospective does not perform it; the retrospective records the gates the pass must close. v1.0 promotion may include a brief verification-results note added to §13.3 itself or kept as a separate v0.1 → v1.0 changelog entry.

A failed verification on any single row above does not invalidate the retrospective's substantive content; it only invalidates the specific factual claim that failed. The retrospective's recommendations and amendment / decision tags are independent of these verification gates and remain valid at v0.1.

### 13.4 What is intentionally not in §13

- **Items already actioned in §11.** §13 does not duplicate the recommendations register; it captures only items that did not fit §11's per-source tables and §11.10's flat index.
- **The SCAFFOLD-002 task packet's own open questions.** Those are not retrospective material; they belong to the SCAFFOLD-002 packet drafting activity that this retrospective does not perform.
- **Post-MVP autonomous-loop questions beyond §10.9.** The autonomous-loop SCAFFOLD-class packet's own open questions (when that packet is drafted) will introduce a fresh set; those are not retrospective material either.

---

## 14. Changelog

- **v0.1 DRAFT (2026-05-05).** Initial retrospective draft. Authored as the post-PR-#2 / SCAFFOLD-001 retrospective per the operator handoff. Records observations and recommended forward directions only; does not authorize any amendment, task packet, or implementation work. Subject to the §13.3 verification pass before v1.0 promotion. Builder: Claude (chat-Governor session). QA Reviewer: Approver, in iterative section-by-section review. Approver: Jeremy Dempsey (review-in-progress at v0.1).

The v1.0 entry is added when the §13.3 verification pass closes and the Approver promotes the document. Until then the retrospective remains v0.1 DRAFT.

---

**End of document.**
