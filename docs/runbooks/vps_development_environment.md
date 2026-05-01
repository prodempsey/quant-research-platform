# VPS Development Environment — Runbook

**Phase 1 scope:** ETF tactical research platform.
**Document status:** v0.2 DRAFT — pending Approver review.
**Approval:** (not yet approved)
**Date:** 2026-04-30
**Document type:** Practical operating procedure. Documentation only — no implementation, no scripts, no `docker-compose.yml` changes, no application code changes, no new engineering specification section, no ADR, no new tool installs.
**Companion documents:**
- Quant Research Platform — Strategy Decision Record v1.0 LOCKED ("SDR")
- Quant Research Platform — Engineering Workflow v1.5 LOCKED ("EW")
- Engineering Specification sections under `docs/engineering_spec/`
- `docs/traceability_matrix.md`
- Approval notes and review artifacts under `docs/reviews/`
- Governance policy: `docs/implementation_context_governance.md`
- Operating procedure (PR loop): `docs/runbooks/governor_gated_github_pr_agent_loop.md`

---

## 1. Purpose and scope

This runbook defines the intended Ubuntu VPS layout for operating the `quant-research-platform` project across:

1. a development environment;
2. an optional staging/test environment;
3. a production environment;
4. an optional, future, *not-yet-approved* AI command-center tool ("AI Maestro").

Its purpose is to describe — at the host-and-filesystem level — how the existing approved Phase 1 stack (Postgres, MLflow, application container, optional nginx) is laid out on the VPS, how the three deployment lanes are kept separated, how operators reach internal services over SSH, and what is forbidden.

It does not change the project's strategy, scope, design, or workflow. It does not introduce a new architectural component, a new dependency, a new approval gate, or a new ticketing system. It does not authorize any implementation. The SDR, the EW, the locked engineering specification sections, and the traceability matrix remain the project's source of truth in that order.

If this runbook conflicts with the SDR or the EW, the SDR and EW control. If it conflicts with `docs/implementation_context_governance.md` or `docs/runbooks/governor_gated_github_pr_agent_loop.md`, those documents control. This runbook is downstream of all of them.

---

## 2. Definition of "runbook"

A runbook is a short, practical, operator-facing document that says how a thing is set up and operated, day to day. It is not a design document, not an architectural decision record, not an engineering specification, and not implementation code. It records conventions and procedures that already follow from approved decisions, in a form an operator can act on without re-reading the upstream specs.

---

## 3. Directory layout under `/srv/quant/`

The project occupies a single top-level tree on the VPS, with one subdirectory per deployment lane plus a backups area. The optional AI command-center tool lives in a sibling tree, fully outside `/srv/quant/`, so that a hypothetical future pilot cannot accidentally see project state.

```
/srv/quant/
  dev/
    quant-research-platform/        # development checkout
  stage/
    quant-research-platform/        # optional staging/test checkout
  prod/
    quant-research-platform/        # production checkout
  backups/
    dev/                            # dev backups (DB dumps, .env snapshots, MLflow artifact snapshots)
    stage/                          # stage backups
    prod/                           # production backups (authoritative; retention to be defined by a future
                                    # backup/restore runbook or owning deployment procedure)

/srv/ai-maestro/                    # reserved for an optional future AI Maestro pilot only
                                    # not created or populated by this runbook
```

Notes on the layout:

- Each lane (`dev/`, `stage/`, `prod/`) holds an independent checkout of the repository under its own working tree. Lanes do not share a working tree. Lanes do not share a Postgres data volume, a named MLflow artifacts volume, or a `.env` file.
- The `backups/` tree is *separate per lane*. Backups taken from the production stack go only under `/srv/quant/backups/prod/`. They are never restored into `dev/` or `stage/` without an explicit, manual review step that confirms no PII, customer data, or non-Phase-1 data is being introduced (Phase 1 has none of those, but the discipline stands).
- `/srv/ai-maestro/` is a placeholder. Nothing in this runbook authorizes its creation. It is named here only so that, if a future pilot is approved, there is one and only one location for it. That location is physically separated from the project environment lanes under `/srv/quant/`, and any access from `/srv/ai-maestro/` into the project tree must be granted deliberately, path by path.

---

## 4. Recommended Linux user separation

Each lane runs as a distinct, unprivileged Linux service user. The users are members of the `docker` group only to the extent each user must operate its own Compose stack. They are not members of each other's primary groups.

**Caution: `docker` group membership is powerful.** Membership in the host `docker` group is effectively close to root-equivalent — a member can mount any host path into a container, run privileged containers, and read or modify files outside their normal Linux permissions through the Docker daemon. `docker` group access is therefore granted only where it is actually needed to operate a lane's Compose stack, and it is not granted casually to additional accounts. Production Docker access in particular remains tightly controlled: only `quantprod` (and root, for OS-level maintenance) holds it on the production lane, and AI Maestro's user, if ever created, is not added to the `docker` group at all unless and until a separately authorized pilot specifically requires it.

Recommended user model:

| Lane | Service user | Home / working dir | Purpose |
|---|---|---|---|
| Development | `quantdev` | `/srv/quant/dev/` | Day-to-day development, branch checkouts, local pytest runs against the dev stack. |
| Staging (optional) | `quantstage` | `/srv/quant/stage/` | Promotion target before production. Runs the same compose stack as prod with stage `.env`. |
| Production | `quantprod` | `/srv/quant/prod/` | Production stack. Only used for production operation and authorized maintenance. |
| AI Maestro (optional, future) | `aimaestro` | `/srv/ai-maestro/` | Reserved. Not created until and unless a pilot is explicitly authorized by Jeremy. |

Operator access:

- Jeremy (Approver) is the only human with the ability to assume `quantprod`. Routine operator access to production is via `sudo -iu quantprod` from Jeremy's normal account, not via direct SSH-as-root and not via direct SSH-as-`quantprod`.
- Day-to-day work happens as `quantdev`. Any session that needs to touch the staging stack uses `sudo -iu quantstage` and exits back. The same pattern applies to `quantprod`.
- No service user has passwordless `sudo` to root. Root is reserved for OS-level maintenance (package updates, disk operations).
- The `aimaestro` user, if ever created, has *no* read or execute access to `/srv/quant/prod/` or `/srv/quant/stage/`. It has read access to `/srv/quant/dev/` only if a pilot is authorized.

This separation is operational hygiene; it does not replace the EW's role separation (Builder / QA Reviewer / Approver) or the Governor-Gated PR loop.

---

## 5. Docker Compose project-name conventions

Each lane runs its Compose stack with an explicit, distinct project name. Project name is set per `docker compose -p <name>` (or `COMPOSE_PROJECT_NAME` in the lane's `.env`), so that container names, network names, and named volumes are namespaced by lane.

| Lane | Compose project name |
|---|---|
| Development | `qrp_dev` |
| Staging (optional) | `qrp_stage` |
| Production | `qrp_prod` |
| AI Maestro (optional, future pilot only) | `ai_maestro` |

This means a dev Postgres container is named like `qrp_dev-postgres-1`, a prod Postgres container is named like `qrp_prod-postgres-1`, and the named volumes (`pgdata`, `mlflow-artifacts` per Section 1 of the spec) become `qrp_dev_pgdata`, `qrp_prod_pgdata`, and so on. Cross-lane name collisions are not possible at the Docker level.

The Compose service names *inside* each stack remain those defined by Section 1 of the engineering specification (`postgres`, `mlflow`, `app`, optionally `nginx`). This runbook does not change service names; it only namespaces the project that contains them.

---

## 6. `localhost`-only port conventions

All HTTP/UI services exposed by any lane are bound to `127.0.0.1` only. None of the application services bind to `0.0.0.0` and none are exposed to the public Internet. External reach is exclusively via SSH tunnel from an operator workstation (Section 7).

Fixed user-facing ports:

| Service | Bind |
|---|---|
| Production Dash UI | `127.0.0.1:8050` |
| Development Dash UI | `127.0.0.1:8051` |
| Optional staging Dash UI | `127.0.0.1:8052` |
| Optional future AI Maestro UI (pilot only, not currently authorized) | `127.0.0.1:23000` |

Ports for internal services (Postgres, MLflow tracking server, any future supporting service) are defined by `docker-compose.yml` per the engineering specification. They follow the same rule: bound to `127.0.0.1` only, reached over SSH tunnel when an operator needs direct access. This runbook does not pin those port numbers.

The convention "production = 8050, dev = 8051, stage = 8052" is deliberately ordered so that the production Dash retains the conventional Dash default port. If the operator forgets which environment they tunneled, this small detail is one extra safeguard against confusing dev and prod.

---

## 7. SSH tunnel access examples

Operators reach internal services from their workstation by opening a single-purpose SSH tunnel to the VPS. Examples below are illustrative; substitute the actual VPS hostname.

Dev Dash UI:
```
ssh -N -L 8051:127.0.0.1:8051 jeremy@<vps-host>
# then browse to http://127.0.0.1:8051 on the workstation
```

Optional stage Dash UI:
```
ssh -N -L 8052:127.0.0.1:8052 jeremy@<vps-host>
# then browse to http://127.0.0.1:8052 on the workstation
```

Production Dash UI:
```
ssh -N -L 8050:127.0.0.1:8050 jeremy@<vps-host>
# then browse to http://127.0.0.1:8050 on the workstation
```

Optional future AI Maestro UI (only if a pilot is later authorized):
```
ssh -N -L 23000:127.0.0.1:23000 jeremy@<vps-host>
# then browse to http://127.0.0.1:23000 on the workstation
```

For internal services like the MLflow tracking UI or a Postgres client connection, the same pattern applies: forward the lane-specific localhost port from the VPS to the workstation, and never bind those services on a public interface server-side.

---

## 8. Dev / stage / prod separation rules

Separation is enforced at four layers and a change in any one layer is *not* sufficient to merge state across lanes:

1. **Filesystem.** Each lane has its own working tree under `/srv/quant/<lane>/quant-research-platform/`. Symlinks across lanes are forbidden. Bind-mounting one lane's directory into another lane's container is forbidden.
2. **Linux user.** Each lane is operated by its own service user (`quantdev` / `quantstage` / `quantprod`). A user cannot read or write another lane's working tree.
3. **Compose project.** Each lane uses its own Compose project name (`qrp_dev` / `qrp_stage` / `qrp_prod`). Networks, named volumes, and container names are namespaced.
4. **`.env` and database.** Each lane has its own `.env` and its own Postgres data volume. Production credentials are never present on the dev or stage stack. Dev fixtures are never present in the prod database.

Operationally:

- Dev is the only lane that may run locally edited, uncommitted code in a container, and only in branches. Production never runs uncommitted code.
- Stage, when used, runs only commits that are merged to `main` and that are candidates for production deploy.
- Production runs only commits that have been promoted via the flow in Section 11.

---

## 9. Secret-handling rules

This runbook does not introduce or change the secrets contract — it just states the operational rules that follow from EW Sections 7, 9, and 10 and Section 1 of the engineering specification.

- Secrets live only in the lane's `.env` on the VPS host filesystem, owned by that lane's service user with mode `0600`.
- `.env` files are never checked into the repository, never copied between lanes, never logged, and never read into chat or PR comments. The EW prohibition on secrets in code, config, fixtures, logs, or docs applies here without modification.
- Production secrets are accessible only as `quantprod`. They are not visible to `quantdev` or `quantstage`. They are not visible to `aimaestro` under any circumstance.
- A new credential is rotated by editing the lane's `.env`, restarting only the affected lane's containers, and recording the rotation in the operator's own private notes (not in the repo).
- `.env.example` in the repository contains variable *names* only and never real values; this is the same rule as in the engineering specification.
- If a secret is suspected of being exposed, the affected credential is rotated immediately at the provider, the new value is placed in the lane's `.env`, and the lane's containers are restarted. This is operational; it is not a strategy change.

---

## 10. Production protection rules

Production is the most-restricted lane on the VPS. Beyond the separation rules in Section 8 and the secret-handling rules in Section 9:

- The production working tree is updated only by the promotion flow in Section 11 — never by ad-hoc `git pull` on a feature branch, never by `git checkout` of an arbitrary commit, never by uploading a tarball.
- No interactive write to the production database outside of an approved migration applied by the production stack. No `psql` `INSERT`/`UPDATE`/`DELETE`/`DDL` from an operator shell against the prod database. Read-only inspection is allowed.
- No edits to `docker-compose.yml`, `config/*.yaml`, or any application file *in place* on the production tree. Changes flow through the PR loop and arrive in production only via promotion.
- The production Compose stack is the only stack on the VPS authorized to run scheduled jobs (cron-in-container per Section 1 of the engineering specification). Dev and stage may run scheduled jobs only when explicitly testing them.
- The production lane has its own backup schedule, writing to `/srv/quant/backups/prod/`. Backups are not deleted as part of routine operation; retention is governed by the relevant engineering specification section that owns data lifecycle.
- The production lane is never used as a development environment. No code is edited under `/srv/quant/prod/` directly.
- AI Maestro, if ever piloted, has no read or write access to `/srv/quant/prod/`, `/srv/quant/backups/prod/`, or any production secret.

---

## 11. Promotion flow from dev to production

The promotion flow respects the existing Governor-Gated GitHub PR Agent Loop (`docs/runbooks/governor_gated_github_pr_agent_loop.md`) and adds nothing to it. It is summarized here as the operator-side procedure on the VPS.

1. **Develop.** Work happens on a feature branch in the `quantdev` working tree at `/srv/quant/dev/quant-research-platform/`. Pytest is run inside the dev `app` container.
2. **Open PR.** The feature branch is pushed to GitHub and a PR is opened. The Governor-Gated loop runs: GitHub Actions tests, Codex/ChatGPT QA review, Project Governor / Context Auditor drift review, then Jeremy's final approval.
3. **Merge to `main`.** Jeremy merges. `main` now contains the new commit.
4. **(Optional) promote to stage.** As `quantstage`, fetch `main` in `/srv/quant/stage/quant-research-platform/`, check out the candidate commit (or a release tag), apply migrations against the stage Postgres, restart the stage Compose stack, and run a defined smoke check against the stage Dash UI. If anything fails, do not promote. Fix on a feature branch and repeat from step 1.
5. **Promote to prod.** As `quantprod`, fetch the *exact* commit SHA or tag that passed stage (if stage is in use) — or the merged `main` SHA Jeremy approved (if stage is not in use). Apply migrations against the production Postgres, restart the production Compose stack, and confirm that the production Dash UI and any scheduled jobs come up cleanly via the localhost SSH tunnel.
6. **Record.** Jeremy records the promoted commit SHA in his own operator notes. The runbook does not require a per-promotion entry in `docs/reviews/`; the merged PR and the traceability matrix already record the change. Meaningful production milestones — initial production cut-over, schema-changing migrations, any change that materially alters scheduled-job behavior — should additionally be recorded with a Git tag or a GitHub Release at the merged commit, when appropriate, so that private operator notes are not the only durable record of production state.

**When the stage lane is required versus optional.** Step 4 above says "(Optional) promote to stage." The stage lane may be skipped for documentation-only changes and for low-risk dev-only changes (changes that do not affect production behavior, do not touch the database schema, do not change a scheduled job, and do not change deployment, environment, or configuration). The stage lane should be used before any change that affects production deployment, applies a database migration, alters scheduled-job behavior, or modifies environment or configuration values. When in doubt, use stage.

The flow is unidirectional: changes move dev → stage → prod, never the reverse. Production is never edited and then back-merged into a branch.

---

## 12. QA / testing expectations at a high level

This runbook does not redefine the testing strategy — that lives in EW §5 and in the relevant engineering specification sections. It states only how testing is exercised across lanes.

- **Dev lane** runs the full pytest suite (`tests/unit/` and `tests/integration/`) inside the dev `app` container. This is where new tests are written and where the Governor-Gated loop's required tests are exercised before PR.
- **Stage lane**, when used, runs a subset of integration tests against the stage Postgres and stage MLflow, plus a defined smoke check on the stage Dash UI and any scheduled job that's about to be promoted. The stage lane is for catching environment-coupled bugs that don't show up against dev fixtures.
- **Prod lane** does not run the test suite. The production stack runs the application and its scheduled jobs. The only testing in prod is post-deploy smoke verification — confirming containers came up, migrations applied, the Dash UI loads, and the next scheduled run starts on time. Anything more is a sign that the wrong code was promoted.
- AI agents may, in the future, assist with writing or running tests in the dev lane only. This is a development-time aid; it does not grant agents approval authority and it does not substitute for the QA Reviewer step in the Governor-Gated loop.

---

## 13. GitHub-only tracking convention for Phase 1

Phase 1 is a single-operator, personal research project. Its tracking needs are bounded. The following four GitHub primitives are sufficient and are the project's only authorized work-tracking surface for Phase 1:

- **GitHub Issues** — tasks, bugs, open questions, follow-ups.
- **GitHub Projects** — board view over Issues and PRs, if Jeremy chooses to use one.
- **GitHub Pull Requests** — the merge boundary, reviewed via the Governor-Gated loop.
- **GitHub Actions** — the CI surface that runs tests on PRs.

Approval artifacts continue to live under `docs/reviews/`. The traceability matrix continues to live at `docs/traceability_matrix.md`. Engineering specifications continue to live under `docs/engineering_spec/`.

Jira (or any equivalent external ticketing system) is *not* introduced for Phase 1. It would be introduced only if Jeremy later decides the project needs:

- external stakeholder reporting that GitHub doesn't expose well; or
- formal sprint management with multiple contributors; or
- cross-project portfolio tracking spanning more than this repository.

None of those conditions exists in Phase 1. Until they do, GitHub is the system of record for work tracking, and this runbook does not authorize anyone to introduce another one.

---

## 14. Forbidden actions

The following are forbidden as a matter of operating the VPS. They are listed because each one has plausibly come up at some point and the answer is no.

- Binding any application service on `0.0.0.0` or on a publicly routable interface. All services bind to `127.0.0.1` and are reached via SSH tunnel.
- Running the production Compose stack with the dev or stage `.env`, or vice versa.
- Copying `.env` files between lanes.
- Symlinking, bind-mounting, or `cp -r`-ing one lane's working tree into another lane.
- Editing files in `/srv/quant/prod/quant-research-platform/` directly. Production changes arrive only via the promotion flow.
- Running ad-hoc `psql` write statements or DDL against the production database outside of an approved migration applied by the production stack.
- Loading dev fixtures into the production database.
- Restoring a production backup into dev or stage without an explicit review step.
- Logging into the VPS as `root` for routine operator tasks. `root` is reserved for OS-level maintenance.
- Granting any service user passwordless `sudo` to root.
- Installing AI Maestro, treating AI Maestro as an approved Phase 1 dependency, or letting AI Maestro mount production folders or read production secrets.
- Letting any agent (Builder, QA Reviewer, Project Governor / Context Auditor, AI Maestro, or any other) merge a PR, approve a PR, or substitute its judgment for Jeremy's at the Approval Matrix items defined in EW §2.3.
- Introducing Jira, Linear, Asana, or any other external ticketing system for Phase 1 work tracking.
- Installing additional command-center, agent-orchestration, or workflow tools on the VPS without an explicit, approved decision in the project's source-of-truth hierarchy.

---

## 15. Future AI Maestro pilot conditions

AI Maestro is *not* an approved Phase 1 tool. It is named here only because, if Jeremy later wishes to pilot it, this runbook tells the operator the conditions under which a pilot may proceed. Until that decision is made, none of the following applies and `/srv/ai-maestro/` remains an empty placeholder.

If, and only if, Jeremy later authorizes a pilot:

- The pilot lives entirely under `/srv/ai-maestro/`, owned by an unprivileged `aimaestro` service user. It does not live under `/srv/quant/`.
- The pilot operates only against `/srv/quant/dev/quant-research-platform/`. Read access is granted on a per-path basis at pilot start. Read access to `/srv/quant/stage/` and `/srv/quant/prod/` is not granted.
- Production folders, production secrets, and `/srv/quant/backups/prod/` are never mounted into AI Maestro and never made readable to it.
- Agent-to-agent coordination features inside AI Maestro are disabled or, if not separately configurable, ignored. The pilot is treated strictly as a dashboard over terminal agents.
- The pilot does not alter, replace, or shortcut the existing workflow. The Governor-Gated GitHub PR Agent Loop remains the path from idea to merge. The GitHub PR remains the merge boundary.
- The pilot does not grant agents approval authority. Agents may assist with development tasks and QA testing in the dev lane; they do not approve PRs, they do not merge PRs, and they do not stand in for Jeremy at any Approval Matrix item.
- The pilot binds its UI on `127.0.0.1:23000` only. It is reached via SSH tunnel like every other internal service.
- The pilot is reversible. Ending the pilot means stopping its containers, removing `/srv/ai-maestro/` contents, and revoking the `aimaestro` user's access. Nothing the pilot did persists into production.
- Authorizing a pilot is a Jeremy decision. It is recorded as such, not assumed from this runbook. This runbook describes the conditions under which a pilot would operate; it does not authorize the pilot.

---

## 16. Closing statement

This runbook is documentation only. Specifically:

- It does not authorize implementation, in this repository or anywhere else.
- It does not install any tool on the VPS or anywhere else.
- It does not approve AI Maestro as a project tool, a Phase 1 dependency, or an approved future addition. AI Maestro remains tabled.
- It does not change the Strategy Decision Record, the Engineering Workflow, any approved Engineering Specification section, the traceability matrix, the implementation context governance policy, or the Governor-Gated GitHub PR Agent Loop.
- It does not change the human-gated project workflow. Jeremy remains the Approver. The PR remains the merge boundary. Agents do not have approval authority.

Any change to the layout, conventions, or rules in this runbook follows the existing change processes in the upstream documents — the SDR, the EW, the affected engineering specification sections, and the implementation context governance policy — not this runbook.

---

**End of document.**
