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
