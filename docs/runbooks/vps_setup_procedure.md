# Quant Research Platform — VPS Setup Procedure

**Phase 1 scope:** ETF tactical research platform  
**Document type:** Runbook / procedure  
**Canonical suggested path:** `docs/runbooks/vps_setup_procedure.md`  
**Created:** 2026-04-30  
**Status:** Draft procedure for review before committing  

---

## Security prerequisite

Before installing the application stack, complete `docs/runbooks/vps_security_baseline.md`.

The VPS must have SSH key-based access, root/password SSH login disabled, UFW enabled, Fail2ban enabled for SSH, automatic security updates configured, Docker exposure reviewed, and no public exposure of Postgres, MLflow, Dash, or application service ports unless explicitly approved through the project deployment-exposure process.

Do not continue with Docker, Postgres, MLflow, Dash, Claude Code, Codex, Cursor, or project secrets until the security baseline checklist is complete.

---

## 1. Purpose

This runbook defines what to download, install, and configure on the Ubuntu VPS before Phase 1 implementation and deployment of the `quant-research-platform` project.

It is intentionally procedural. It is not an Engineering Specification section and does not change the approved project architecture.

The goal is to make the VPS reproducible enough that the platform can be rebuilt from:

1. the GitHub repository;
2. the host `.env` file;
3. Docker named volumes or backups;
4. documented install steps;
5. approved project configuration under `config/`.

---

## 2. Controlling project decisions

This runbook follows the locked project decisions already approved for Phase 1:

- VPS operating system: **Ubuntu 24.04 LTS**.
- Runtime architecture: **Docker Engine + Docker Compose plugin**, not Docker Desktop.
- Initial stack: **three containers**:
  - Postgres container;
  - MLflow tracking container;
  - application container running Dash plus scheduled jobs.
- Optional fourth container: **nginx**, only later if controlled UI exposure is needed.
- Python version: **Python 3.12**.
- Repository layout: `src/quant_research_platform/`.
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

## 3. What should be installed where

### 3.1 Install on the VPS host

Install these directly on Ubuntu:

| Tool | Install on host? | Purpose |
|---|---:|---|
| Ubuntu system packages | Yes | OS updates, firewall, SSH, build basics |
| Git | Yes | Clone repo, branch, commit, inspect diffs |
| GitHub CLI `gh` | Yes | Authenticate to GitHub, open PRs, inspect PRs |
| Docker Engine | Yes | Run all project services |
| Docker Compose plugin | Yes | Orchestrate project services |
| Python 3.12 host tooling | Yes | Lightweight local checks; container remains runtime source of truth |
| Node.js LTS + npm | Yes | Required for Claude Code, Codex CLI, and optional Cursor CLI |
| Claude Code CLI | Yes, user-level | Primary Builder agent from SSH terminal |
| OpenAI Codex CLI | Yes, user-level | Independent QA/reviewer agent from SSH terminal |
| Cursor CLI | Optional, user-level | Small-scope builder / editor-adjacent agent if desired |
| PostgreSQL client tools | Optional but recommended | `psql`, diagnostics, backup verification |
| Fail2ban / UFW | Yes | Basic VPS hardening |
| Host backup directory | Yes | Store rotated database dumps and MLflow artifact archives |

### 3.2 Do not install directly on the VPS host

Do **not** install these as host services for Phase 1:

| Tool | Why not |
|---|---|
| PostgreSQL server | Postgres runs in the official Docker container. Host may have `postgresql-client` only. |
| MLflow server | MLflow runs in its own container. Host may have MLflow only for ad-hoc client testing, but not as the service. |
| Dash app runtime | Dash runs in the application container. |
| Python project dependencies globally | Dependencies live in the app image and/or local venv, never system Python. |
| nginx | Omitted initially unless later approved for controlled UI exposure. |
| Kubernetes | Out of scope for Phase 1. |
| CI/CD runners | Out of scope for Phase 1. |
| Broker SDKs | Forbidden in Phase 1. |
| AI Maestro | Tabled for possible future command-center use only; not an official Phase 1 tool. |

---

## 4. Recommended version baseline

| Component | Recommended baseline | Notes |
|---|---|---|
| OS | Ubuntu 24.04 LTS | Locked project decision. |
| Python | Python 3.12.x | Locked project decision. Use `python:3.12-slim` family for the app container unless implementation chooses a more specific patch tag. |
| PostgreSQL container | `postgres:17` or later approved fixed major tag | Use a fixed major tag. Avoid `postgres:latest` for production-like runs. PostgreSQL 17 is stable and supported; PostgreSQL 18 is available but should be chosen deliberately. |
| Docker | Current Docker Engine from Docker apt repository | Install from Docker’s official apt repo, not Ubuntu’s old package if avoidable. |
| Node.js | Node.js 22 LTS recommended | One Node LTS version is enough for Claude Code, Codex CLI, and Cursor CLI. Do not install multiple Node versions unless a tool requires it later. |
| MLflow | Pin in project dependency manifest | MLflow server runs in container. Pin exact version during implementation. |
| Dash | Pin in project dependency manifest | Dash app runs in application container. |
| scikit-learn | Pin in project dependency manifest | Used by model layer. |
| pandas / numpy | Pin in project dependency manifest | Used across ingestion, features, targets, backtests, and reporting. |

**Node answer:** No separate Node versions are needed now. Install one active LTS Node version. Node 22 LTS is a conservative baseline because Claude Code requires Node 18 or later and Codex installs through npm. If a later official tool requires Node 24+, update this runbook and the environment deliberately.

---

## 5. Official download / documentation links

Use official sources first.

### Core VPS / platform

- Ubuntu Server docs: https://ubuntu.com/server/docs/
- Ubuntu 24.04 LTS release notes: https://documentation.ubuntu.com/release-notes/24.04/
- Docker Engine on Ubuntu: https://docs.docker.com/engine/install/ubuntu/
- Docker Compose docs: https://docs.docker.com/compose/
- PostgreSQL official site: https://www.postgresql.org/
- PostgreSQL Docker official image: https://hub.docker.com/_/postgres
- Git: https://git-scm.com/download/linux
- GitHub CLI: https://cli.github.com/

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
- EODHD Python library: https://github.com/EodHistoricalData/EODHD-APIs-Python-Financial-Library

---

## 6. Procedure overview

Perform setup in this order:

1. Create / verify the VPS.
2. Harden SSH and firewall.
3. Install base system packages.
4. Install Git and GitHub CLI.
5. Install Docker Engine and Docker Compose plugin.
6. Install Python 3.12 host tooling.
7. Install Node.js LTS and npm.
8. Install Claude Code, Codex CLI, and optional Cursor CLI.
9. Create the project directory layout on the VPS.
10. Clone the repo.
11. Create host `.env` from `.env.example`.
12. Build and start the Docker stack.
13. Verify Postgres, MLflow, and app container health.
14. Set up SSH tunnels for Dash and MLflow.
15. Set up backup directories and backup smoke checks.
16. Document what was installed.

---

## 7. VPS operating system setup

### 7.1 Confirm OS version

```bash
lsb_release -a
uname -a
```

Expected: Ubuntu 24.04 LTS.

### 7.2 Update the system

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### 7.3 Install basic utilities

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

### 7.4 Enable automatic security updates

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Verify:

```bash
systemctl status unattended-upgrades --no-pager
```

---

## 8. Basic VPS security

### 8.1 Create a non-root deploy user if needed

If the VPS only gives you root, create a normal user:

```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
```

Add your SSH public key:

```bash
sudo mkdir -p /home/deploy/.ssh
sudo nano /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

Then log in as `deploy` before continuing.

### 8.2 Configure UFW firewall

Allow SSH first:

```bash
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status verbose
```

For Phase 1, do **not** open Dash, MLflow, or Postgres ports to the public internet. Use SSH tunnels instead.

Do not run these unless later approved:

```bash
# Do not run by default:
# sudo ufw allow 8050/tcp
# sudo ufw allow 5000/tcp
# sudo ufw allow 5432/tcp
```

### 8.3 Install Fail2ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status
```

Optional SSH jail override:

```bash
sudo nano /etc/fail2ban/jail.d/sshd.local
```

Suggested starter content:

```ini
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 1h
findtime = 10m
```

Restart:

```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
```

---

## 9. Git and GitHub CLI setup

### 9.1 Install Git

```bash
sudo apt install -y git
```

Configure identity:

```bash
git config --global user.name "Jeremy Dempsey"
git config --global user.email "YOUR_GITHUB_EMAIL_HERE"
git config --global init.defaultBranch main
```

### 9.2 Install GitHub CLI

Use the official GitHub CLI installation instructions for Ubuntu if they change. Current pattern:

```bash
(type -p wget >/dev/null || sudo apt install wget -y) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y
```

Authenticate:

```bash
gh auth login
gh auth status
```

---

## 10. Docker Engine and Docker Compose setup

### 10.1 Remove conflicting packages if present

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt remove -y "$pkg" || true
done
```

### 10.2 Install Docker from Docker’s official apt repository

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

### 10.3 Allow non-root Docker usage

```bash
sudo usermod -aG docker "$USER"
```

Log out and back in, then verify:

```bash
docker --version
docker compose version
docker run hello-world
```

### 10.4 Docker daemon log rotation

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

---

## 11. Python 3.12 host tooling

The application runtime belongs in Docker. The host Python install is for lightweight checks only.

### 11.1 Install Python 3.12 support packages

Ubuntu 24.04 includes Python 3.12 by default. Install venv/pip support:

```bash
sudo apt install -y python3 python3.12-venv python3-pip
python3 --version
```

Expected major/minor: `Python 3.12.x`.

### 11.2 Optional host virtual environment

Use this only for local helper tools, not as the production runtime:

```bash
mkdir -p ~/venvs
python3 -m venv ~/venvs/quant-tools
source ~/venvs/quant-tools/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Optional host-only tools:

```bash
python -m pip install pytest ruff
```

Do not install the full project globally with `sudo pip`.

---

## 12. Node.js and npm setup

Node is required for the AI CLI tools. The application itself is Python/Dash and does not require Node at runtime.

### 12.1 Recommended install: Node.js 22 LTS via NodeSource

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

### 12.2 npm global package directory without sudo

Avoid global npm installs that require `sudo`.

```bash
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

## 13. Claude Code setup

Claude Code is the primary Builder tool for coding tasks in this project workflow.

### 13.1 Install

```bash
npm install -g @anthropic-ai/claude-code
```

Verify:

```bash
claude --version
```

### 13.2 Authenticate

Run:

```bash
claude
```

Follow the browser or terminal authentication flow provided by Claude Code.

For headless/API-key usage, follow Anthropic’s official docs. Do **not** paste API keys into chat, docs, code, or shell history. Use environment variables only if needed.

### 13.3 Project usage rule

Run Claude Code only from a clean Git working tree or a dedicated feature branch:

```bash
cd ~/quant/quant-research-platform
git status
git checkout -b feature/<short-task-name>
claude
```

Claude Code should not work directly on `main`.

---

## 14. OpenAI Codex CLI setup

Codex is the independent QA/reviewer tool in the project workflow. It can also be used for small implementation tasks when explicitly assigned, but it should not self-certify its own work.

### 14.1 Install

```bash
npm install -g @openai/codex
```

Verify:

```bash
codex --version
```

### 14.2 Authenticate

```bash
codex
```

Follow the sign-in flow. Use ChatGPT account authentication unless you deliberately choose API-key usage.

### 14.3 Project usage rule

Use Codex on the artifact, diff, test output, and controlling docs. Do not ask Codex to approve changes it authored unless a separate QA pass is performed by another reviewer.

---

## 15. Cursor setup

Cursor should play a smaller-scale builder/editor role, not replace the project’s Builder → QA → Approver flow.

### 15.1 Recommended use

Best default:

1. Install Cursor Desktop on your local computer.
2. Use it for small edits, file navigation, and targeted implementation tasks.
3. Push changes through the same Git branch / PR / QA process.
4. Use SSH into the VPS for terminal-based Claude Code and Codex when needed.

### 15.2 Optional Cursor CLI on VPS

Install Cursor CLI only if you want terminal agent support on the VPS:

```bash
curl https://cursor.com/install -fsS | bash
```

Then restart the shell and verify based on Cursor’s current CLI docs.

Cursor tooling should not run inside the application container and should not be given production secrets beyond what the normal user shell already has access to.

---

## 16. Project directory layout on VPS

Suggested user-level layout:

```bash
mkdir -p ~/quant
cd ~/quant
```

Clone repo:

```bash
git clone https://github.com/prodempsey/quant-research-platform.git
cd quant-research-platform
```

Confirm:

```bash
git remote -v
git status
```

Optional `/srv` layout for later production hardening:

```bash
sudo mkdir -p /srv/quant
sudo chown -R "$USER":"$USER" /srv/quant
```

Use only one canonical working copy per environment to avoid confusion.

---

## 17. Host `.env` setup

### 17.1 Create `.env`

From the repo root:

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

### 17.2 Required variables from the data-layer spec

At minimum, the file should eventually include:

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

Verify:

```bash
git status --ignored --short | grep .env || true
```

Expected: `.env` should be ignored or absent from regular `git status` output.

### 17.3 Credential handling rules

- Do not paste real credentials into prompts.
- Do not save real credentials in markdown files.
- Do not put credentials in `config/*.yaml`.
- Do not bake credentials into Docker images.
- Rotate credentials by editing host `.env` and restarting affected containers.

---

## 18. PostgreSQL setup

### 18.1 Host package

Install the client only:

```bash
sudo apt install -y postgresql-client
psql --version
```

Do not install or enable a host PostgreSQL server for Phase 1.

### 18.2 Container role

Postgres runs as a Docker Compose service using the official `postgres` image.

Expected project behavior:

- one Postgres container;
- one named volume: `pgdata`;
- two logical databases:
  - application database;
  - MLflow metadata database;
- bootstrap SQL under `scripts/postgres-init/` mounted to `/docker-entrypoint-initdb.d/`;
- application migrations under `migrations/` applied separately from database/role bootstrap.

### 18.3 Verify after Compose is available

```bash
docker compose ps
docker compose exec postgres pg_isready -U "$APP_DB_USER" -d "$APP_DB_NAME"
```

If environment variables are not available in your shell, read service names and usernames from `.env` without printing passwords.

---

## 19. MLflow setup

### 19.1 Intended Phase 1 architecture

MLflow runs as a dedicated container, not as a host service.

Expected behavior:

- MLflow metadata database is in the same Postgres container but isolated from the app database.
- MLflow artifacts are stored in the `mlflow-artifacts` Docker named volume.
- Application container writes MLflow run metadata through `MLFLOW_TRACKING_URI`.
- MLflow web UI is internal-only and reached by SSH tunnel.

### 19.2 Typical MLflow server command inside the MLflow container

The implementation may vary, but the expected shape is:

```bash
mlflow server \
  --backend-store-uri postgresql+psycopg://$MLFLOW_DB_USER:$MLFLOW_DB_PASSWORD@postgres:5432/$MLFLOW_DB_NAME \
  --default-artifact-root /mlflow/artifacts \
  --host 0.0.0.0 \
  --port 5000
```

The exact command belongs in `docker-compose.yml` or the MLflow service image definition, not as a manually run host command.

### 19.3 Verify MLflow after Compose is available

```bash
docker compose ps mlflow
docker compose logs --tail=100 mlflow
```

From the app container:

```bash
docker compose exec app python - <<'PY'
import os
print(os.environ.get("MLFLOW_TRACKING_URI"))
PY
```

Do not expose MLflow publicly.

---

## 20. Application container setup

### 20.1 Expected container responsibilities

The application container is the only container that imports project Python code. It should eventually:

- serve the Dash UI;
- run cron-in-container;
- invoke thin CLI entry points for ingestion, features, targets, model runs, backtests, portfolio decisions, and reporting;
- read YAML config from `/app/config` read-only;
- read credentials from environment variables;
- write application state to Postgres;
- write model run tracking to MLflow.

### 20.2 Python dependencies belong in project manifests

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

## 21. Python library inventory

This is the recommended Phase 1 dependency inventory. Exact pins should be chosen during implementation and committed through `pyproject.toml` and `requirements.txt`.

### 21.1 Runtime libraries likely needed

| Package | Purpose |
|---|---|
| `pandas` | Dataframes, ETL, feature/target/backtest calculations |
| `numpy` | Numeric operations |
| `scipy` | Scientific/statistical support used by ML stack |
| `scikit-learn` | Baseline regression/classification models and calibration |
| `mlflow` | Experiment tracking and model registry integration |
| `SQLAlchemy` | Database access layer |
| `psycopg[binary]` or `psycopg` | PostgreSQL driver |
| `pydantic` v2 | Provider DTOs and config/data validation |
| `PyYAML` or `ruamel.yaml` | YAML config parsing |
| `requests` or `httpx` | EODHD API calls inside provider adapter |
| `tenacity` | Retry/backoff for provider rate limits and transient failures |
| `python-dateutil` | Date handling support |
| `pandas-market-calendars` or `exchange-calendars` | U.S. trading calendar support; choose deliberately during implementation |
| `plotly` | Dash charting |
| `dash` | Operator UI |
| `dash-bootstrap-components` | Dash UI layout/styling convenience |
| `gunicorn` | Production-ish WSGI serving if selected for Dash |
| `click` or `typer` | Thin command-line entry points |
| `structlog` or standard `logging` only | Structured logging if selected; standard logging is enough initially |
| `python-dotenv` | Local development only; not a deployed runtime dependency |

### 21.2 Dev/test libraries likely needed

| Package | Purpose |
|---|---|
| `pytest` | Test runner |
| `pytest-cov` | Coverage reporting |
| `ruff` | Linting and formatting |
| `mypy` | Optional static typing check; add only if wanted |
| `types-PyYAML` / other stubs | Optional type stubs if mypy is used |
| `responses` or `respx` | Mock external HTTP calls depending on `requests` vs `httpx` |
| `freezegun` | Optional date/time tests |

### 21.3 Provider-specific library decision

EODHD has an official Python library, but the project’s provider abstraction means the platform should not become coupled to that package outside `providers/eodhd/`.

Recommended implementation stance:

- prefer simple HTTP calls with `requests` or `httpx` inside `providers/eodhd/` first;
- use the official EODHD Python package only if it materially reduces risk or maintenance;
- never let `features/`, `targets/`, `models/`, `backtest/`, `portfolio/`, `paper/`, `order_intent/`, or `ui/` import EODHD-specific packages.

---

## 22. Docker Compose startup procedure

After the repo contains the approved `Dockerfile`, `docker-compose.yml`, `.env.example`, and required bootstrap files:

```bash
cd ~/quant/quant-research-platform
cp .env.example .env
chmod 600 .env
nano .env
```

Build:

```bash
docker compose build --no-cache
```

Start:

```bash
docker compose up -d
```

Check services:

```bash
docker compose ps
docker compose logs --tail=100 postgres
docker compose logs --tail=100 mlflow
docker compose logs --tail=100 app
```

Run tests inside the app container when code exists:

```bash
docker compose exec app pytest
```

Run lint/format checks when code exists:

```bash
docker compose exec app ruff check .
docker compose exec app ruff format --check .
```

---

## 23. SSH tunnels for Dash and MLflow

Do not expose Dash or MLflow publicly in Phase 1.

From your local machine:

```bash
ssh -L 8050:localhost:8050 -L 5000:localhost:5000 deploy@YOUR_VPS_IP
```

Then browse locally:

- Dash: http://localhost:8050
- MLflow: http://localhost:5000

If the containers bind only inside Docker, the tunnel target may need to point to the host-mapped localhost ports defined in `docker-compose.yml`. Keep those ports bound to `127.0.0.1`, not `0.0.0.0`, unless public exposure is later approved.

---

## 24. Backup setup

### 24.1 Host directories

```bash
mkdir -p ~/quant/backups/postgres
mkdir -p ~/quant/backups/mlflow-artifacts
chmod 700 ~/quant/backups
```

### 24.2 Expected scripts

The repo should eventually contain:

- `scripts/backup.sh` — host-side backup wrapper that runs `pg_dump` against the Postgres container and rotates old dumps.
- `scripts/restore.sh` — controlled restore procedure.

### 24.3 Manual backup smoke pattern

Example shape only; final script should own exact names:

```bash
docker compose exec -T postgres pg_dump -U "$APP_DB_USER" "$APP_DB_NAME" > ~/quant/backups/postgres/app_$(date +%Y%m%d_%H%M%S).sql
```

For MLflow artifacts, archive the Docker named volume or mount path according to the final `docker-compose.yml`.

---

## 25. Health-check procedure

### 25.1 Host health

```bash
df -h
free -h
uptime
sudo systemctl status docker --no-pager
```

### 25.2 Container health

```bash
docker compose ps
docker stats --no-stream
```

### 25.3 App health

```bash
docker compose logs --tail=100 app
```

Expected:

- Dash process is running;
- cron process is running;
- scheduled-job failures are visible;
- app health check does not pass if cron is dead.

### 25.4 Database health

```bash
docker compose exec postgres pg_isready
```

### 25.5 MLflow health

```bash
docker compose logs --tail=100 mlflow
```

If MLflow is reachable by tunnel:

```bash
curl -I http://localhost:5000
```

---

## 26. AI agent operating guardrails on the VPS

### 26.1 Branch discipline

Before using Claude Code, Codex, or Cursor:

```bash
git status
git checkout main
git pull
git checkout -b feature/<task-name>
```

After work:

```bash
git status
git diff
git diff --stat
```

### 26.2 Agent responsibility split

| Tool | Role |
|---|---|
| Claude Code | Primary Builder for implementation tasks |
| Codex | Independent QA/reviewer; may do small tasks only when assigned |
| ChatGPT | Architecture/spec/QA guidance and final review support |
| Cursor | Smaller-scale builder/editor, useful for targeted changes and local review |
| Jeremy | Approver; final merge and strategy authority |

### 26.3 Never give agents unrestricted production authority

Agents must not:

- edit `.env` with real credentials unless you explicitly direct and inspect the result;
- commit secrets;
- modify main directly;
- expose Dash, MLflow, or Postgres publicly;
- add broker SDKs;
- create live trading code paths;
- change strategy-affecting YAML without approval;
- self-certify their own work.

---

## 27. Things not needed right now

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
- production secrets in agent tooling.

---

## 28. Final VPS readiness checklist

The VPS is ready for implementation work when all are true:

- [ ] Ubuntu 24.04 LTS confirmed.
- [ ] Non-root sudo user configured.
- [ ] SSH key login works.
- [ ] UFW enabled with SSH only.
- [ ] Fail2ban enabled.
- [ ] System packages updated.
- [ ] Git installed and configured.
- [ ] GitHub CLI installed and authenticated.
- [ ] Docker Engine installed from official Docker apt repository.
- [ ] Docker Compose plugin installed.
- [ ] Current user can run Docker without sudo.
- [ ] Docker log rotation configured.
- [ ] Python 3.12 host tooling available.
- [ ] Node.js LTS and npm installed.
- [ ] npm global prefix configured without sudo.
- [ ] Claude Code installed and authenticated.
- [ ] Codex CLI installed and authenticated.
- [ ] Cursor local desktop or optional CLI plan decided.
- [ ] Repository cloned.
- [ ] `.env` created from `.env.example` and chmod `600`.
- [ ] `.env` is ignored by Git.
- [ ] Docker stack builds.
- [ ] Docker stack starts.
- [ ] Postgres container healthy.
- [ ] MLflow container healthy.
- [ ] App container healthy.
- [ ] Dash reachable by SSH tunnel only.
- [ ] MLflow reachable by SSH tunnel only.
- [ ] Backup directory created.
- [ ] Backup/restore scripts reviewed before production-like use.
- [ ] No public database/UI/MLflow ports exposed.
- [ ] No broker SDKs installed.
- [ ] No AI Maestro installed.

---

## 29. Appendix A — quick command sequence for a fresh VPS

This section is a compact checklist version. Read the full procedure before running commands.

```bash
# Base system
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
sudo apt install -y ca-certificates curl gnupg lsb-release software-properties-common apt-transport-https unzip zip tar jq htop tree nano vim tmux build-essential pkg-config git python3 python3.12-venv python3-pip postgresql-client fail2ban unattended-upgrades

# Firewall
sudo ufw allow OpenSSH
sudo ufw enable
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Docker official repo
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"

# Node.js 22 LTS
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# AI CLIs
npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex

# Repo
mkdir -p ~/quant
cd ~/quant
git clone https://github.com/prodempsey/quant-research-platform.git
cd quant-research-platform
cp .env.example .env
chmod 600 .env
```

Log out and back in after adding your user to the Docker group, then verify:

```bash
docker run hello-world
docker compose version
node --version
npm --version
python3 --version
claude --version
codex --version
gh auth status
```

---

## 30. Appendix B — first troubleshooting checks

### Docker permission denied

Log out and back in after:

```bash
sudo usermod -aG docker "$USER"
```

Verify:

```bash
groups
```

### Docker Compose cannot read `.env`

Check:

```bash
ls -la .env
chmod 600 .env
```

Make sure `.env` is in the repo root next to `docker-compose.yml`.

### Port already in use

Check:

```bash
sudo ss -tulpn | grep -E ':8050|:5000|:5432'
```

Dash, MLflow, and Postgres should not be publicly exposed. Host-mapped ports, if used, should bind to localhost.

### MLflow cannot connect to Postgres

Check:

```bash
docker compose logs --tail=100 mlflow
docker compose logs --tail=100 postgres
docker compose exec postgres psql -U postgres -c '\l'
```

Most likely causes:

- MLflow database was not created during first-init bootstrap;
- `.env` has mismatched database credentials;
- Postgres named volume already existed before bootstrap files were added;
- MLflow backend URI uses the wrong service name.

### App cannot load config

Check that config is mounted and read-only:

```bash
docker compose exec app ls -la /app/config
```

### EODHD authentication fails

Check only that the variable exists; do not print the key:

```bash
docker compose exec app python - <<'PY'
import os
print("EODHD_API_KEY present:", bool(os.environ.get("EODHD_API_KEY")))
PY
```

---

## 31. Appendix C — source references

Project source references:

- `docs/engineering_workflow.md`
- `docs/strategy_decision_record.md`
- `docs/engineering_spec/01_architecture_overview.md`
- `docs/engineering_spec/02_data_layer.md`
- `docs/engineering_spec/03a_feature_engineering.md`
- `docs/engineering_spec/03b_target_generation.md`
- `docs/engineering_spec/03c_model_layer_mlflow.md`
- `docs/engineering_spec/04_backtest_attribution_validation.md`
- `docs/engineering_spec/05_portfolio_paper_order_intent.md`
- `docs/engineering_spec/06_operator_ui.md`
- `docs/traceability_matrix.md`

External official references are listed in Section 5.
