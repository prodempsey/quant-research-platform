# Quant Research Platform — VPS Setup Procedure

**Phase 1 scope:** ETF tactical research platform  
**Document type:** Runbook / setup procedure  
**Canonical suggested path:** `docs/runbooks/vps_setup_procedure.md`  
**Document status:** v1.0 LOCKED / APPROVED 
**Approval:** Approved by Jeremy Dempsey May 1 2026
**Version:** 0.4  
**Created:** 2026-04-30  
**Last updated:** 2026-05-01  

**Source authority:**

- Quant Research Platform — Strategy Decision Record v1.0 LOCKED / APPROVED
- Quant Research Platform — Engineering Workflow v1.5 LOCKED
- Locked Engineering Specification sections 01–06
- `docs/traceability_matrix.md`

**Companion runbooks / governance documents:**

- `docs/runbooks/vps_security_baseline.md`
- `docs/runbooks/vps_development_environment.md`
- `docs/runbooks/governor_gated_github_pr_agent_loop.md`
- `docs/implementation_context_governance.md`, if present in the repository

---

## Changelog

### v0.4 DRAFT — targeted user-context cleanup after Claude review

Targeted cleanup after Claude QA of v0.3. No application code, `docker-compose.yml`, Engineering Specification sections, or traceability matrix changes are made by this runbook. Main changes:

1. Clarified that GitHub CLI authentication is per Linux user and should be run as the lane user that will use `gh` for PR work.
2. Added a user-context callout at the start of the Node/npm section because npm global prefix and AI CLI installs are per-user.
3. Split Appendix A verification commands into admin-context checks and lane-user checks so Docker checks are not accidentally run as `quantdev` with sudo assumptions.
4. Updated the readiness checklist to qualify Claude Code and Codex installs/authentication by lane user.
5. Replaced ambiguous "Section 1" provider wording with `docs/engineering_spec/01_architecture_overview.md`.

### v0.3 DRAFT — targeted QA follow-up after Claude review

Targeted cleanup after Claude QA of v0.2. No application code, `docker-compose.yml`, Engineering Specification sections, or traceability matrix changes are made by this runbook. Main changes:

1. Verified and clarified that lane-user names (`quantdev`, `quantstage`, `quantprod`) are inherited from `docs/runbooks/vps_development_environment.md`.
2. Added an explicit prerequisite before lane commands: lane users must be created per the development-environment runbook before lane-specific commands are run.
3. Verified that locked source documents currently reference Hostinger as the initial VPS provider assumption; provider-neutral operational wording is preserved until source-of-truth documents are amended.
4. Replaced ambiguous "Section 2" `.env` references with `docs/engineering_spec/02_data_layer.md` and clarified that variable names and values shown in this runbook are illustrative.
5. Clarified that AI CLI npm installs are per Linux user; for normal dev-lane work, install Claude Code and Codex under `quantdev` or the lane user that will run them.
6. Marked Appendix A as a human-readable checklist, not a single-shot script.
7. Softened references to the project Dockerfile before implementation and removed a duplicate `postgresql-client` install line.

### v0.2 DRAFT — targeted setup / procedure reconciliation

Targeted cleanup after QA review. No application code, `docker-compose.yml`, Engineering Specification sections, or traceability matrix changes are made by this runbook. Main changes:

1. Added source-authority, status, companion-document, changelog, open-questions, and closing-statement structure.
2. Removed duplicated security procedures and made `vps_security_baseline.md` the sole owner of SSH hardening, UFW, Fail2ban, unattended security updates, Docker exposure security, provider firewall, and off-host backup baseline.
3. Removed Docker group membership as a default setup step; initial setup uses `sudo docker` and `sudo docker compose`.
4. Kept Docker daemon log rotation, but classified it as Docker host hygiene rather than security-baseline ownership.
5. Added Docker port-binding standard: published ports bind to `127.0.0.1`; Docker-published ports are not treated as protected by UFW.
6. Reconciled project layout with `vps_development_environment.md`: `/srv/quant/<lane>/quant-research-platform/` is the VPS lane layout; no parallel `~/quant` clone is maintained on the VPS.
7. Reconciled user model: `deploy` is the SSH/admin user; `quantdev`, `quantstage`, and `quantprod` are lane users governed by the development-environment runbook.
8. Made SSH tunnel examples lane-aware and avoided inventing MLflow lane ports.
9. Trimmed Python library inventory to neutral dependency categories; package choices and pins belong to project manifests and locked specifications.
10. Cleaned Appendix A so it starts after the security baseline and does not run security-baseline commands.
11. Replaced duplicated AI-agent operating rules with references to the governance runbooks.
12. Added provider-neutral wording and an open question for final VPS provider selection.

### v0.1 DRAFT

Initial VPS setup procedure covering OS setup, security setup, Git/GitHub CLI, Docker, Python, Node, Claude Code, Codex, optional Cursor, `.env`, Postgres, MLflow, Dash/app container expectations, SSH tunnels, backups, health checks, and agent guardrails.

---

## 1. Purpose

This runbook defines the post-security setup procedure for preparing an Ubuntu VPS to operate the `quant-research-platform` project.

It is intentionally procedural. It is not an Engineering Specification section, not an ADR, and not implementation authorization. It does not change the approved project architecture, strategy, service topology, deployment exposure, no-live-trading boundary, or traceability matrix.

The goal is to make the VPS reproducible enough that the platform can be rebuilt from:

1. the GitHub repository;
2. the host `.env` file;
3. Docker named volumes or backups;
4. documented install steps;
5. approved project configuration under `config/`.

---

## 2. Source authority and status

This runbook is downstream of the locked project sources. If this runbook conflicts with the SDR, Engineering Workflow, locked Engineering Specification sections, traceability matrix, or companion runbooks, the locked / controlling source wins.

This runbook implements the approved Phase 1 operating pattern at the setup-procedure level:

- Ubuntu 24.04 LTS on a selected Linux VPS provider;
- Docker Engine and Docker Compose plugin on the host;
- Postgres, MLflow, and the application/Dash stack running in containers;
- credentials injected from host `.env` into containers;
- YAML config committed under `config/` and mounted read-only;
- Dash and MLflow reached through SSH tunnels, not public exposure;
- no live broker SDKs, broker credentials, or order-placement code paths;
- AI Maestro not installed and not approved as a Phase 1 tool.

Operational defaults in this runbook, such as Node.js LTS baseline, npm user-level prefix, host helper packages, and setup command examples, are setup-level defaults. They are subject to override by a future approved deployment specification or Approver-directed runbook amendment.

---

## 3. Security prerequisite

Before installing Docker, Postgres containers, MLflow containers, Dash/app containers, Claude Code, Codex, Cursor, or project secrets, complete:

```text

docs/runbooks/vps_security_baseline.md
```

Confirm `docs/runbooks/vps_security_baseline.md` has been completed end-to-end before continuing. SSH hardening, UFW, Fail2ban, `deploy` user setup, unattended security updates, Docker exposure security, provider firewall, and the off-host backup baseline are owned by the security baseline runbook and are not re-implemented here.

This setup procedure may still include reminders that Postgres, MLflow, Dash, and app service ports must not be publicly exposed. Those reminders do not replace the security baseline.

---

## 4. Companion-runbook ownership boundaries

| Area | Owning document |
|---|---|
| SSH hardening, UFW, Fail2ban, provider firewall, Docker exposure safety, off-host backup baseline | `docs/runbooks/vps_security_baseline.md` |
| `/srv/quant` lane layout, lane users, Compose project names, lane-specific port conventions, dev/stage/prod separation | `docs/runbooks/vps_development_environment.md` |
| Tool installation and general VPS setup after the security baseline | This runbook |
| Builder / QA / Approver workflow and PR loop | `docs/runbooks/governor_gated_github_pr_agent_loop.md` |
| Context-governance and agent-boundary policy | `docs/implementation_context_governance.md`, if present |
| Strategy, architecture, schema, model behavior, portfolio behavior, UI requirements | Locked SDR / EW / Engineering Specification sections |

---

## 5. Controlling project decisions reflected here

This runbook follows these locked Phase 1 decisions and constraints:

- VPS operating system: **Ubuntu 24.04 LTS**.
- Runtime architecture: **Docker Engine + Docker Compose plugin**, not Docker Desktop.
- Initial stack: **three containers**:
  - Postgres container;
  - MLflow tracking container;
  - application container running Dash plus scheduled jobs.
- Optional fourth container: **nginx**, only later if controlled UI exposure is explicitly approved.
- Python version: **Python 3.12**.
- Repository layout inside the codebase: `src/quant_research_platform/`.
- Dependency discipline: `pyproject.toml` plus pinned `requirements.txt` for the Dockerfile.
- Test framework: `pytest`.
- Linter / formatter: `ruff`.
- MLflow web UI: internal only, reached through SSH tunnel during development.
- Dash UI: internal only, reached through SSH tunnel during development.
- Credentials: gitignored host `.env`; never copied into images; never committed.
- YAML config: committed under `config/`, mounted read-only into the application container.
- No live broker SDKs, no broker credentials, no order-placement code paths.
- AI Maestro remains tabled as a possible future command-center only and is not installed as an official project tool in Phase 1.

---

## 6. What should be installed where

### 6.1 Install on the VPS host

Install these directly on Ubuntu after the security baseline is complete:

| Tool | Install on host? | Purpose |
|---|---:|---|
| Git | Yes | Clone repo, branch, commit, inspect diffs |
| GitHub CLI `gh` | Yes | Authenticate to GitHub, open PRs, inspect PRs |
| Docker Engine | Yes | Run all project services |
| Docker Compose plugin | Yes | Orchestrate project services |
| Python 3.12 host tooling | Yes | Lightweight host checks; container remains runtime source of truth |
| Node.js LTS + npm | Yes | Required for Claude Code, Codex CLI, and optional Cursor CLI |
| Claude Code CLI | Yes, user-level | Primary Builder tool when assigned by the project workflow |
| OpenAI Codex CLI | Yes, user-level | Independent QA/reviewer tool when assigned by the project workflow |
| Cursor CLI | Optional, user-level | Optional small-scope builder/editor-adjacent tool |
| PostgreSQL client tools | Optional but recommended | `psql`, diagnostics, backup verification |
| Host utility packages | Yes | `curl`, `jq`, `tmux`, `htop`, compression tools, etc. |

### 6.2 Do not install directly on the VPS host

Do **not** install these as host services for Phase 1:

| Tool | Why not |
|---|---|
| PostgreSQL server | Postgres runs in the official Docker container. Host may have `postgresql-client` only. |
| MLflow server | MLflow runs only in its container. Do not install MLflow as a host service. |
| Dash app runtime | Dash runs in the application container. |
| Python project dependencies globally | Dependencies live in the app image and project manifests, not system Python. |
| nginx | Omitted initially unless later approved for controlled UI exposure. |
| Kubernetes | Out of scope for Phase 1. |
| CI/CD runners | Out of scope for Phase 1. |
| Broker SDKs | Forbidden in Phase 1. |
| AI Maestro | Tabled for possible future command-center use only; not an official Phase 1 tool. |

---

## 7. Recommended version baseline

| Component | Recommended baseline | Notes |
|---|---|---|
| OS | Ubuntu 24.04 LTS | Locked project decision. |
| Python | Python 3.12.x | Locked project decision. Use the eventual project Dockerfile for runtime details once implementation files exist. |
| PostgreSQL container | Fixed major tag, not `latest` | Exact major version should be chosen deliberately during implementation. |
| Docker | Current Docker Engine from Docker apt repository | Install from Docker's official apt repo, not the legacy Ubuntu package if avoidable. |
| Node.js | One supported LTS version; Node 22 LTS remains an acceptable baseline unless tool docs require newer | One Node version is enough for Claude Code, Codex CLI, and optional Cursor CLI. |
| MLflow | Pin in project dependency manifest | MLflow server runs in container. Exact pin is implementation-owned. |
| Dash | Pin in project dependency manifest | Dash app runs in application container. Exact pin is implementation-owned. |
| scikit-learn / pandas / numpy | Pin in project dependency manifest | Used by model, data, and research layers. Exact pins are implementation-owned. |

**Node guidance:** Do not install multiple Node versions unless a tool later requires it. If Claude Code, Codex, or Cursor official requirements change, update this runbook deliberately.

---

## 8. Official download / documentation links

Use official sources first. Re-check official install commands before running them on the VPS.

### Core VPS / platform

- Ubuntu Server docs: https://ubuntu.com/server/docs/
- Ubuntu 24.04 LTS release notes: https://documentation.ubuntu.com/release-notes/24.04/
- Docker Engine on Ubuntu: https://docs.docker.com/engine/install/ubuntu/
- Docker Compose docs: https://docs.docker.com/compose/
- PostgreSQL official site: https://www.postgresql.org/
- PostgreSQL Docker official image: https://hub.docker.com/_/postgres
- Git: https://git-scm.com/download/linux
- GitHub CLI Linux install docs: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

### Python and Python project libraries

- Python downloads: https://www.python.org/downloads/
- Python Docker images: https://hub.docker.com/_/python
- pandas install docs: https://pandas.pydata.org/docs/getting_started/install.html
- scikit-learn install docs: https://scikit-learn.org/stable/install.html
- SQLAlchemy: https://www.sqlalchemy.org/
- Dash install docs: https://dash.plotly.com/installation
- MLflow docs: https://mlflow.org/docs/latest/
- MLflow tracking server architecture: https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/
- MLflow backend store docs: https://mlflow.org/docs/latest/self-hosting/architecture/backend-store/
- MLflow artifact store docs: https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/

### AI coding tools

- Claude Code setup: https://code.claude.com/docs/en/setup
- Claude Code npm package: https://www.npmjs.com/package/@anthropic-ai/claude-code
- OpenAI Codex CLI docs: https://developers.openai.com/codex/cli
- OpenAI Codex CLI GitHub: https://github.com/openai/codex
- Cursor: https://cursor.com/
- Cursor CLI installation: https://cursor.com/docs/cli/installation
- Cursor CLI overview: https://cursor.com/docs/cli/overview

### Market data

- EODHD homepage: https://eodhd.com/
- EODHD historical EOD API docs: https://eodhd.com/financial-apis/api-for-historical-data-and-volumes

This runbook does not decide whether the provider adapter uses direct HTTP, a third-party package, or an official client. Provider-adapter implementation choices belong to the locked Engineering Specification and implementation tasks.

---

## 9. Procedure overview

Perform setup in this order:

1. Complete `docs/runbooks/vps_security_baseline.md` end-to-end.
2. Confirm the selected VPS is Ubuntu 24.04 LTS.
3. Install post-security host utilities.
4. Install Git and GitHub CLI.
5. Install Docker Engine and Docker Compose plugin.
6. Configure Docker host hygiene, including daemon log rotation.
7. Verify Docker using `sudo docker ...` commands.
8. Install Python 3.12 host tooling.
9. Install Node.js LTS and npm.
10. Install Claude Code, Codex CLI, and optional Cursor CLI.
11. Use the `/srv/quant/<lane>/quant-research-platform/` lane layout defined by `vps_development_environment.md`.
12. Clone the repo into the appropriate lane working tree.
13. Create host `.env` from `.env.example` in the lane working tree.
14. Build and start the Docker stack when implementation files exist.
15. Verify Postgres, MLflow, and app container health.
16. Use SSH tunnels for Dash and MLflow.
17. Confirm lane-aware backup paths and off-host backup requirements.
18. Document what was installed.

---

## 10. VPS operating system checks and host utilities

### 10.1 Confirm OS version

```bash
lsb_release -a
uname -a
```

Expected: Ubuntu 24.04 LTS.

### 10.2 Update non-security host packages

Security-update policy and unattended upgrades are owned by `vps_security_baseline.md`. After that baseline is complete, it is still acceptable to update packages before installing tooling:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

If the system reports that a reboot is required, reboot during a quiet window and reconnect as `deploy`.

### 10.3 Install host utility packages

```bash
sudo apt install -y \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  software-properties-common \
  apt-transport-https \
  unzip \
  zip \
  tar \
  jq \
  htop \
  tree \
  nano \
  vim \
  tmux \
  build-essential \
  pkg-config
```

Do not install a host PostgreSQL server.

---

## 11. Git and GitHub CLI setup

### 11.1 Install Git

```bash
sudo apt install -y git
```

Configure identity:

```bash
git config --global user.name "<your-name>"
git config --global user.email "<your-github-email>"
git config --global init.defaultBranch main
```

### 11.2 Install GitHub CLI

Install GitHub CLI using the current official Linux instructions:

```text
https://github.com/cli/cli/blob/trunk/docs/install_linux.md
```

After installation, authenticate `gh` for the Linux user that will use it. For dev-lane work that creates or reviews PRs from `/srv/quant/dev/quant-research-platform`, this normally means `quantdev`, not `deploy`, because GitHub CLI authentication is stored under the current user's home directory.

Example for the dev lane:

```bash
sudo -iu quantdev
gh auth login
gh auth status
```

Do not paste GitHub tokens into docs, prompts, or shell transcripts.

---

## 12. Docker Engine and Docker Compose setup

### 12.1 Remove conflicting packages if present

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt remove -y "$pkg" || true
done
```

### 12.2 Install Docker from Docker's official apt repository

Check Docker's official Ubuntu instructions before running these commands:

```text
https://docs.docker.com/engine/install/ubuntu/
```

Current pattern:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 12.3 Docker access default: use sudo

Initial VPS setup uses:

```bash
sudo docker ...
sudo docker compose ...
```

Do not add `deploy` or the current user to the `docker` group by default. Docker group membership is root-equivalent and may only be granted later as an explicit lane-operator exception documented in `docs/runbooks/vps_development_environment.md`.

Verify with `sudo`:

```bash
sudo docker --version
sudo docker compose version
sudo docker run hello-world
```

### 12.4 Docker host hygiene: daemon log rotation

`vps_security_baseline.md` owns Docker exposure rules and security hardening. This setup runbook owns basic Docker installation and host hygiene such as log rotation.

Create or edit:

```bash
sudo nano /etc/docker/daemon.json
```

Suggested starter content:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
```

Restart Docker:

```bash
sudo systemctl restart docker
sudo systemctl status docker --no-pager
```

### 12.5 Port-binding standard

Every container port published to the host must bind to `127.0.0.1`, not `0.0.0.0`.

Important: UFW does not reliably filter Docker-published ports. The Docker Compose bind address is the primary enforcement point for container service exposure.

Rules:

1. Published host ports bind to `127.0.0.1` only.
2. Internal container-to-container traffic should use Docker internal networking or `expose`.
3. `0.0.0.0` bindings are not allowed in Phase 1 unless explicitly approved as a deployment-exposure change.
4. Public IPv6 bindings are not allowed in Phase 1 unless explicitly approved as a deployment-exposure change.
5. See `docs/runbooks/vps_security_baseline.md` for safe / unsafe examples and verification commands.

Verification command:

```bash
sudo ss -tulpen | grep -vE '127\.0\.0\.1|\[::1\]'
```

Passing condition:

```text
Only sshd should appear on non-loopback addresses unless a future deployment-exposure change is explicitly approved.
```

---

## 13. Python 3.12 host tooling

The application runtime belongs in Docker. The host Python install is for lightweight checks only.

### 13.1 Install Python support packages

Ubuntu 24.04 includes Python 3.12 by default. Install venv/pip support:

```bash
sudo apt install -y python3 python3.12-venv python3-pip
python3 --version
```

Expected major/minor: `Python 3.12.x`.

### 13.2 Optional host virtual environment

Use this only for local helper tools, not as the deployed runtime:

```bash
mkdir -p ~/venvs
python3 -m venv ~/venvs/quant-tools
source ~/venvs/quant-tools/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Optional host-only helper tools:

```bash
python -m pip install pytest ruff
```

Do not install the full project globally with `sudo pip`.

Open question OQ-VPS-SETUP-03 tracks whether this host venv convention should remain in the setup runbook or move to a separate local-development procedure.

---

## 14. Node.js and npm setup

Node is required for the AI CLI tools. The application itself is Python/Dash and does not require Node at runtime.

**User-context note:** Node itself is installed system-wide by the admin user, but npm global prefix configuration and AI CLI installs are per Linux user. For normal development-lane work, switch to `quantdev` before running the npm-global and AI CLI commands in this section and in Sections 15-17.

### 14.1 Install one Node.js LTS version

Recommended baseline: Node.js 22 LTS unless official tool requirements change.

Example using NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

If official Claude Code, Codex, or Cursor requirements later require a newer Node LTS, update this runbook deliberately.

### 14.2 npm global package directory without sudo

Avoid global npm installs that require `sudo`. npm global package configuration is **per Linux user**. Configure it for the user that will run the AI CLI tools. For normal development-lane work, that is usually `quantdev`, not `deploy`.

Example for the dev lane:

```bash
ssh deploy@<vps-host>
sudo -iu quantdev
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
```

Add to `~/.bashrc`:

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
```

Reload:

```bash
source ~/.bashrc
npm config get prefix
```

Expected: `/home/<user>/.npm-global`.

---

## 15. Claude Code setup

Claude Code is the primary Builder tool when assigned by the project workflow.

### 15.1 Install

Run as the Linux user that will use Claude Code, normally the dev-lane user `quantdev`:

```bash
npm install -g @anthropic-ai/claude-code
```

Verify:

```bash
claude --version
```

### 15.2 Authenticate

Run:

```bash
claude
```

Follow the browser or terminal authentication flow provided by Claude Code.

For headless/API-key usage, follow Anthropic's official docs. Do not paste API keys into chat, docs, code, shell history, or Git.

### 15.3 Project operating rules

This section covers installation only. Project operating rules for Claude Code are governed by:

```text

docs/runbooks/governor_gated_github_pr_agent_loop.md
docs/implementation_context_governance.md, if present
```

Minimum reminder: run agents from a feature branch on a clean working tree. Agents do not approve, merge, expose services publicly, edit real secrets casually, or bypass Jeremy's approval authority.

---

## 16. OpenAI Codex CLI setup

Codex is the independent QA/reviewer tool when assigned by the project workflow. It can also be used for small implementation tasks only when explicitly assigned.

### 16.1 Install

Run as the Linux user that will use Codex, normally the dev-lane user `quantdev`:

```bash
npm install -g @openai/codex
```

Verify:

```bash
codex --version
```

### 16.2 Authenticate

```bash
codex
```

Follow the sign-in flow. Use ChatGPT account authentication unless you deliberately choose API-key usage.

### 16.3 Project operating rules

This section covers installation only. Codex operating rules are governed by:

```text

docs/runbooks/governor_gated_github_pr_agent_loop.md
docs/implementation_context_governance.md, if present
```

Minimum reminder: run agents from a feature branch on a clean working tree. Agents do not approve, merge, expose services publicly, edit real secrets casually, or bypass Jeremy's approval authority.

---

## 17. Cursor setup

Cursor is optional. It may be useful as a smaller-scale editor/builder aid, but it does not replace the approved Builder → QA → Approver process.

### 17.1 Recommended use

Best default:

1. Install Cursor Desktop on your local computer.
2. Use it for small edits, file navigation, and targeted implementation tasks.
3. Push changes through the same Git branch / PR / QA process.
4. Use SSH into the VPS for terminal-based Claude Code and Codex when needed.

### 17.2 Optional Cursor CLI on VPS

Install Cursor CLI only if you want terminal agent support on the VPS. Run it as the Linux user that will use Cursor CLI, normally `quantdev` for dev-lane work:

```bash
curl https://cursor.com/install -fsS | bash
```

Then restart the shell and verify based on Cursor's current CLI docs.

Cursor tooling should not run inside the application container and should not be given production secrets beyond what the normal user shell already has access to.

### 17.3 Project operating rules

Cursor operating rules are governed by:

```text

docs/runbooks/governor_gated_github_pr_agent_loop.md
docs/implementation_context_governance.md, if present
```

Minimum reminder: run agents from a feature branch on a clean working tree. Agents do not approve, merge, expose services publicly, edit real secrets casually, or bypass Jeremy's approval authority.

---

## 18. VPS lane layout and user model

`docs/runbooks/vps_development_environment.md` owns the VPS lane layout, lane users, Compose project names, and lane-specific port conventions.

Use the lane-specific working tree defined there:

```text
/srv/quant/dev/quant-research-platform
/srv/quant/stage/quant-research-platform
/srv/quant/prod/quant-research-platform
```

Do not maintain a parallel home-directory clone on the VPS.

User model:

| User | Role |
|---|---|
| `deploy` | SSH/admin user created by the security baseline |
| `quantdev` | development lane user |
| `quantstage` | optional staging lane user |
| `quantprod` | production lane user |

Operator pattern:

```bash
ssh deploy@<vps-host>
sudo -iu quantdev
# or
sudo -iu quantstage
# or
sudo -iu quantprod
```

If you use a personalized admin username instead of `deploy`, document it as a replacement for `deploy`; do not mix both names in the same procedure.

Lane-user creation and lane permissions are governed by `vps_development_environment.md`. This setup runbook does not change that model.

---

## 19. Clone the repository into a lane working tree

Lane users (`quantdev`, `quantstage`, `quantprod`) must be created per `docs/runbooks/vps_development_environment.md` before this section is run. This runbook uses those exact names because the development-environment runbook defines them as the lane users.

Example for the dev lane:

```bash
ssh deploy@<vps-host>
sudo -iu quantdev
cd /srv/quant/dev
git clone https://github.com/prodempsey/quant-research-platform.git
cd /srv/quant/dev/quant-research-platform
git remote -v
git status
```

Example for production should follow the promotion flow in `vps_development_environment.md`, not ad-hoc branch work.

Do not clone a second working copy under `~/quant` on the VPS.

---

## 20. Host `.env` setup

### 20.1 Create `.env` in the lane working tree

From the lane repo root:

```bash
cd /srv/quant/dev/quant-research-platform
cp .env.example .env
chmod 600 .env
nano .env
```

For stage/prod, use the corresponding lane path and lane user. Do not copy `.env` files between lanes.

### 20.2 Environment variable illustration

`docs/engineering_spec/02_data_layer.md` defines the required data-layer environment-variable names, and `.env.example` is the implementation-facing template once it exists. Variable names and values shown below are illustrative in this runbook; if this block differs from `docs/engineering_spec/02_data_layer.md` or `.env.example`, the locked spec and `.env.example` control.

```bash
# Application database
APP_DB_HOST=postgres
APP_DB_PORT=5432
APP_DB_NAME=quant_app
APP_DB_USER=quant_app_user
APP_DB_PASSWORD=REPLACE_ME

# MLflow metadata database
MLFLOW_DB_HOST=postgres
MLFLOW_DB_PORT=5432
MLFLOW_DB_NAME=quant_mlflow
MLFLOW_DB_USER=quant_mlflow_user
MLFLOW_DB_PASSWORD=REPLACE_ME

# MLflow tracking server
MLFLOW_TRACKING_URI=http://mlflow:5000

# EODHD provider
EODHD_API_KEY=REPLACE_ME
EODHD_API_BASE_URL=https://eodhd.com/api
```

Do not commit `.env`.

Verify without printing secrets:

```bash
git status --ignored --short | grep .env || true
ls -l .env
```

Expected `.env` permission pattern:

```text
-rw-------
```

### 20.3 Credential handling rules

- Do not paste real credentials into prompts.
- Do not save real credentials in markdown files.
- Do not put credentials in `config/*.yaml`.
- Do not bake credentials into Docker images.
- Rotate credentials by editing the lane's host `.env` and restarting affected containers.

---

## 21. PostgreSQL setup

### 21.1 Host package

Install the client only if not already installed:

```bash
sudo apt install -y postgresql-client
psql --version
```

Do not install or enable a host PostgreSQL server for Phase 1.

### 21.2 Container role

Postgres runs as a Docker Compose service using the official `postgres` image.

Expected project behavior:

- one Postgres container per lane Compose stack;
- named volume for Postgres data, namespaced by Compose project name;
- two logical databases:
  - application database;
  - MLflow metadata database;
- bootstrap SQL under `scripts/postgres-init/` mounted to `/docker-entrypoint-initdb.d/`;
- application migrations under `migrations/` applied separately from database/role bootstrap.

### 21.3 Verify after Compose is available

From the lane repo root:

```bash
sudo docker compose ps
sudo docker compose exec postgres pg_isready -U "$APP_DB_USER" -d "$APP_DB_NAME"
```

If environment variables are not available in your shell, read service names and usernames from `.env` without printing passwords.

---

## 22. MLflow setup

### 22.1 Intended Phase 1 architecture

MLflow runs as a dedicated container, not as a host service.

Expected behavior:

- MLflow metadata database is in the same Postgres container but isolated from the app database.
- MLflow artifacts are stored in the `mlflow-artifacts` Docker named volume, namespaced by Compose project name.
- Application container writes MLflow run metadata through `MLFLOW_TRACKING_URI`.
- MLflow web UI is internal-only and reached by SSH tunnel.

### 22.2 Typical MLflow server command inside the MLflow container

The implementation may vary, but the expected shape is:

```bash
mlflow server \
  --backend-store-uri postgresql+psycopg://$MLFLOW_DB_USER:$MLFLOW_DB_PASSWORD@postgres:5432/$MLFLOW_DB_NAME \
  --default-artifact-root /mlflow/artifacts \
  --host 0.0.0.0 \
  --port 5000
```

Do not run this command directly on the host shell; credentials may appear in process listings. The actual command belongs in `docker-compose.yml`, the MLflow service image definition, or container configuration.

The container may listen on `0.0.0.0` **inside the Docker network**, but any host-published port must still bind to `127.0.0.1` only.

### 22.3 Verify MLflow after Compose is available

```bash
sudo docker compose ps mlflow
sudo docker compose logs --tail=100 mlflow
```

From the app container:

```bash
sudo docker compose exec app python - <<'PY'
import os
print(os.environ.get("MLFLOW_TRACKING_URI"))
PY
```

Do not expose MLflow publicly.

---

## 23. Application container setup

### 23.1 Expected container responsibilities

The application container is the only container that imports project Python code. It should eventually:

- serve the Dash UI;
- run cron-in-container;
- invoke thin CLI entry points for ingestion, features, targets, model runs, backtests, portfolio decisions, and reporting;
- read YAML config from `/app/config` read-only;
- read credentials from environment variables;
- write application state to Postgres;
- write model run tracking to MLflow.

### 23.2 Python dependencies belong in project manifests

Use:

- `pyproject.toml` for project metadata and dependency declarations;
- pinned `requirements.txt` generated from the approved dependency set for the Dockerfile;
- `pytest` and `ruff` for test/lint/format.

Avoid:

- global `sudo pip install`;
- notebook-only dependency installs;
- unpinned runtime dependencies in the Dockerfile;
- hidden host dependencies.

---

## 24. Python dependency categories

The exact package set and pins are owned by `pyproject.toml`, `requirements.txt`, and the locked Engineering Specification sections. This runbook only lists expected dependency categories for setup awareness.

### 24.1 Runtime dependency categories likely needed

| Category | Examples of purpose |
|---|---|
| Dataframes / numeric computation | ETL, feature/target/backtest calculations |
| Scientific / ML stack | Baseline regression/classification models and calibration |
| Experiment tracking | MLflow client integration |
| Database access | SQLAlchemy-style access and PostgreSQL driver |
| Validation / DTOs | Provider DTOs and config/data validation |
| YAML config parsing | Read approved `config/*.yaml` files |
| HTTP client | Provider adapter calls inside provider layer |
| Retry/backoff | Provider rate limits and transient failures |
| Date / market calendar support | Trading-day logic |
| Dash / Plotly UI | Operator UI |
| CLI entry points | Thin command wrappers |
| Logging | Standard or structured logging, as selected by implementation |

### 24.2 Dev/test dependency categories likely needed

| Category | Examples of purpose |
|---|---|
| Test runner | Unit and integration tests |
| Coverage | Coverage reporting |
| Linting / formatting | Ruff or approved equivalent |
| Type checking | Optional static type checks if adopted |
| HTTP mocks | Provider API tests |
| Time controls | Date/time boundary tests |

This runbook does not decide among competing packages. Package selection belongs to implementation under the approved specs.

---

## 25. Docker Compose startup procedure

After the repo contains the approved `Dockerfile`, `docker-compose.yml`, `.env.example`, and required bootstrap files, work from the appropriate lane repo root.

Example dev lane:

```bash
cd /srv/quant/dev/quant-research-platform
cp .env.example .env
chmod 600 .env
nano .env
```

Build:

```bash
sudo docker compose build --no-cache
```

Start:

```bash
sudo docker compose up -d
```

Check services:

```bash
sudo docker compose ps
sudo docker compose logs --tail=100 postgres
sudo docker compose logs --tail=100 mlflow
sudo docker compose logs --tail=100 app
```

Verify non-loopback listeners:

```bash
sudo ss -tulpen | grep -vE '127\.0\.0\.1|\[::1\]'
```

Passing condition:

```text
Only sshd should appear on non-loopback addresses unless a future deployment-exposure change is explicitly approved.
```

Run tests inside the app container when code exists:

```bash
sudo docker compose exec app pytest
```

Run lint/format checks when code exists:

```bash
sudo docker compose exec app ruff check .
sudo docker compose exec app ruff format --check .
```

---

## 26. SSH tunnels for Dash and MLflow

Do not expose Dash or MLflow publicly in Phase 1.

Lane-specific port conventions are owned by `docs/runbooks/vps_development_environment.md`.

Example dev lane Dash tunnel:

```bash
ssh -N -L 8051:127.0.0.1:8051 deploy@<vps-host>
```

Then browse locally to:

```text
http://127.0.0.1:8051
```

Example production lane Dash tunnel:

```bash
ssh -N -L 8050:127.0.0.1:8050 deploy@<vps-host>
```

Then browse locally to:

```text
http://127.0.0.1:8050
```

MLflow follows the same loopback-only tunnel pattern using the lane's configured localhost port. Do not invent or expose MLflow public ports in this setup runbook.

---

## 27. Backup setup pointer

Backup root is lane-aware and governed by `docs/runbooks/vps_development_environment.md`:

```text
/srv/quant/backups/dev/
/srv/quant/backups/stage/
/srv/quant/backups/prod/
```

The off-host backup requirement is owned by `docs/runbooks/vps_security_baseline.md`.

This setup runbook does not define the final backup/restore procedure. Suggested future runbook:

```text

docs/runbooks/vps_backup_restore.md
```

At setup time, verify that the lane backup directory exists and has restrictive permissions. Example for dev:

```bash
sudo mkdir -p /srv/quant/backups/dev
sudo chmod 700 /srv/quant/backups/dev
```

Do not treat on-host backup directories as sufficient by themselves. Off-host backups are required before the platform stores meaningful research data, MLflow artifacts, or secrets.

---

## 28. Health-check procedure

### 28.1 Host health

```bash
df -h
free -h
uptime
sudo systemctl status docker --no-pager
```

### 28.2 Container health

From the lane repo root:

```bash
sudo docker compose ps
sudo docker stats --no-stream
```

### 28.3 App health

```bash
sudo docker compose logs --tail=100 app
```

Expected once implementation exists:

- Dash process is running;
- cron process is running;
- scheduled-job failures are visible;
- app health check does not pass if cron is dead.

### 28.4 Database health

```bash
sudo docker compose exec postgres pg_isready
```

### 28.5 MLflow health

```bash
sudo docker compose logs --tail=100 mlflow
```

If MLflow is reachable by tunnel:

```bash
curl -I http://127.0.0.1:<lane-mlflow-local-port>
```

Use the lane's configured localhost port from `vps_development_environment.md` or the final Compose configuration.

---

## 29. AI agent governance on the VPS

Detailed agent operating rules are governed by:

```text

docs/runbooks/governor_gated_github_pr_agent_loop.md
docs/implementation_context_governance.md, if present
```

This setup runbook only records the cross-cutting reminder:

- Run agents from a feature branch on a clean working tree.
- Agents do not approve or merge their own work.
- Agents do not expose services publicly.
- Agents do not edit real secrets casually.
- Agents do not bypass Jeremy's approval authority.

---

## 30. Things not needed right now

Do not set these up unless a later approved change requires them:

- nginx reverse proxy;
- public TLS certificates;
- Docker registry;
- GitHub Actions / CI/CD runner;
- Kubernetes;
- Redis;
- Celery;
- Airflow;
- Prefect;
- local host PostgreSQL server;
- broker APIs / SDKs;
- AI Maestro;
- multiple Node versions;
- production secrets in agent tooling;
- VPN / Tailscale / WireGuard requirement;
- SIEM / Wazuh / CrowdSec.

---

## 31. Final VPS setup readiness checklist

The VPS is ready for implementation work when all are true:

- [ ] `docs/runbooks/vps_security_baseline.md` completed and signed off.
- [ ] Ubuntu 24.04 LTS confirmed.
- [ ] Git installed and configured with placeholder-correct user identity.
- [ ] GitHub CLI installed from official docs and authenticated for the lane user that will use it.
- [ ] Docker Engine installed from official Docker apt repository.
- [ ] Docker Compose plugin installed.
- [ ] Docker commands verified with `sudo docker ...`.
- [ ] `deploy` or current admin user has **not** been casually added to the Docker group.
- [ ] Docker daemon log rotation configured.
- [ ] Docker port-binding standard understood: host-published ports bind to `127.0.0.1` only.
- [ ] Non-loopback listener check shows only SSH unless an approved exposure change exists.
- [ ] Python 3.12 host tooling available.
- [ ] Node.js LTS and npm installed.
- [ ] npm global prefix configured without sudo for the lane user(s) that will use AI CLIs.
- [ ] Claude Code installed and authenticated for the lane user(s) that will use it.
- [ ] Codex CLI installed and authenticated for the lane user(s) that will use it.
- [ ] Cursor local desktop or optional CLI plan decided.
- [ ] Lane users from `vps_development_environment.md` exist before lane commands are run.
- [ ] `/srv/quant/<lane>/quant-research-platform/` lane layout followed.
- [ ] No parallel `~/quant` clone maintained on the VPS.
- [ ] Repository cloned into the selected lane.
- [ ] `.env` created from `.env.example` in the lane working tree and chmod `600`.
- [ ] `.env` is ignored by Git.
- [ ] Docker stack builds when implementation files exist.
- [ ] Docker stack starts when implementation files exist.
- [ ] Postgres container healthy.
- [ ] MLflow container healthy.
- [ ] App container healthy.
- [ ] Dash reachable by SSH tunnel only.
- [ ] MLflow reachable by SSH tunnel only.
- [ ] Lane-aware backup directory exists under `/srv/quant/backups/<lane>/`.
- [ ] Off-host backup destination selected before serious use.
- [ ] No public database/UI/MLflow ports exposed.
- [ ] No broker SDKs installed.
- [ ] No AI Maestro installed.

---

## 32. Appendix A — quick command sequence after security baseline

Run only after `docs/runbooks/vps_security_baseline.md` is complete.

This is a compact, human-readable checklist, not a single-shot shell script. Read the full procedure before running commands and run each block in the correct user context.

```bash
# Base non-security utilities
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
sudo apt install -y ca-certificates curl gnupg lsb-release software-properties-common apt-transport-https unzip zip tar jq htop tree nano vim tmux build-essential pkg-config git python3 python3.12-venv python3-pip postgresql-client

# Docker official repo
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker log rotation
sudo tee /etc/docker/daemon.json > /dev/null <<'JSON'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
JSON
sudo systemctl restart docker

# Node.js 22 LTS baseline (run as deploy/admin)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Switch to the dev-lane user before configuring npm globals and AI CLIs.
# Lane users must already exist per docs/runbooks/vps_development_environment.md.
ssh deploy@<vps-host>
sudo -iu quantdev
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# AI CLIs, installed for the lane user that will run them
npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex

# Example dev-lane repo clone
cd /srv/quant/dev
git clone https://github.com/prodempsey/quant-research-platform.git
cd /srv/quant/dev/quant-research-platform
cp .env.example .env
chmod 600 .env
```

Verify as the admin user (`deploy` or equivalent), before switching to a lane user:

```bash
sudo docker run hello-world
sudo docker compose version
python3 --version
sudo ss -tulpen | grep -vE '127\.0\.0\.1|\[::1\]'
```

The non-loopback listener check should show only SSH unless an approved exposure change exists.

Then verify as the lane user that will run the AI tools, for example `quantdev`:

```bash
sudo -iu quantdev
node --version
npm --version
claude --version
codex --version
gh auth status
```

If `gh auth status` fails under `quantdev`, authenticate GitHub CLI under `quantdev`; authentication under `deploy` does not automatically carry over to lane users.

---

## 33. Appendix B — first troubleshooting checks

### Docker permission denied

Do not immediately add the user to the Docker group.

First verify Docker works with sudo:

```bash
sudo docker ps
sudo docker compose version
```

If lane users later require direct Docker access, that must be handled as an explicit lane-operator exception in `docs/runbooks/vps_development_environment.md` with the root-equivalent Docker group warning preserved.

### Docker Compose cannot read `.env`

Check:

```bash
ls -la .env
chmod 600 .env
```

Make sure `.env` is in the lane repo root next to `docker-compose.yml`.

### Port already in use

Check:

```bash
sudo ss -tulpn | grep -E ':8050|:8051|:8052|:5000|:5432'
```

Dash, MLflow, and Postgres should not be publicly exposed. Host-mapped ports, if used, should bind to localhost.

### MLflow cannot connect to Postgres

Check:

```bash
sudo docker compose logs --tail=100 mlflow
sudo docker compose logs --tail=100 postgres
sudo docker compose exec postgres psql -U postgres -c '\l'
```

Most likely causes:

- MLflow database was not created during first-init bootstrap;
- `.env` has mismatched database credentials;
- Postgres named volume already existed before bootstrap files were added;
- MLflow backend URI uses the wrong service name.

### App cannot load config

Check that config is mounted and read-only:

```bash
sudo docker compose exec app ls -la /app/config
```

### EODHD authentication fails

Check only that the variable exists; do not print the key:

```bash
sudo docker compose exec app python - <<'PY'
import os
print("EODHD_API_KEY present:", bool(os.environ.get("EODHD_API_KEY")))
PY
```

---

## 34. Open questions

These do not block v0.4 review, but should be resolved before serious VPS use.

| ID | Open question | Current disposition |
|---|---|---|
| OQ-VPS-SETUP-01 | Final VPS provider selection remains pending. The locked SDR and `docs/engineering_spec/01_architecture_overview.md` currently reference Hostinger as the initial VPS provider assumption, but operational runbooks should remain provider-neutral unless and until source-of-truth documents are amended. | Open; selected VPS provider may be Hostinger, Contabo, or another Approver-selected provider if source documents are reconciled. |
| OQ-VPS-SETUP-02 | Exact Postgres major version tag for Phase 1 containers. | Open; use a fixed major tag, not `latest`, when implementation begins. |
| OQ-VPS-SETUP-03 | Whether the optional host virtualenv `~/venvs/quant-tools` should remain in this setup runbook or move to a local-development procedure. | Open; harmless as host helper default but not a deployed runtime pattern. |
| OQ-VPS-SETUP-04 | Exact MLflow, Dash, scikit-learn, pandas, numpy, and related library pins. | Open; owned by project dependency manifests during implementation. |
| OQ-VPS-SETUP-05 | Whether lane users should be granted Docker group membership or all Docker operations should remain `sudo docker` from the admin path. | Open; if granted, document as explicit operational exception in `vps_development_environment.md`. |
| OQ-VPS-SETUP-06 | Whether a dedicated `docs/runbooks/vps_backup_restore.md` should be created before first serious data accumulation. | Recommended; security baseline already requires off-host backup before serious use. |

---

## 35. Closing statement

This runbook does not authorize implementation. It does not install tools by itself. It does not change the SDR, the EW, the locked Engineering Specification sections, or the traceability matrix. If this runbook conflicts with a locked source-of-truth document, the locked document controls.

No public exposure of Postgres, MLflow, Dash, or application ports is introduced by this runbook. No broker SDKs, broker credentials, live trading paths, AI Maestro installation, public TLS, nginx, reverse proxy, VPN, Tailscale, WireGuard, Kubernetes, SIEM, Wazuh, CrowdSec, Redis, Celery, Airflow, Prefect, or CI/CD runners are introduced by this runbook.

---

End of `docs/runbooks/vps_setup_procedure.md` v0.4 DRAFT.
