# Quant Research Platform — VPS Backup and Restore Procedure

**Phase 1 scope:** ETF tactical research platform  
**Document type:** Runbook / backup and restore procedure  
**Canonical suggested path:** `docs/runbooks/vps_backup_restore.md`  
**Document status:** v1.0 LOCKED / APPROVED 
**Approval:** Approved by Jeremy Dempsey May 1st 2026
**Version:** 0.2  
**Created:** 2026-05-01  
**Last updated:** 2026-05-01  

---

## Changelog

### v0.2 DRAFT — QA pass

QA pass: corrected companion-document list, added secrets plaintext gap callout, added single-Postgres assumption, added shell-cleanup note, added connection-drain note, added pipefail note for future scripting, added volume-name note to restore, added four open questions.

### v0.1 DRAFT — initial backup and restore procedure

Initial documentation-only draft defining the lane-aware backup model, off-host backup requirement, manual backup command patterns, conservative restore procedure, restore-test procedure, verification checklist, retention defaults, incident recovery outline, open questions, and completion criteria.

No application code, `docker-compose.yml`, scripts, cron jobs, traceability matrix updates, Engineering Specification sections, public ports, backup tooling installs, provider selections, live trading components, broker SDKs, CI/CD runners, VPNs, nginx, Kubernetes, AI Maestro, or production deployment changes are introduced by this runbook.

---

## 1. Source authority and status

This is an operational runbook. It is not an Engineering Specification section, not an ADR, and not implementation authorization.

The following documents remain controlling:

1. Quant Research Platform — Strategy Decision Record v1.0 LOCKED / APPROVED;
2. Quant Research Platform — Engineering Workflow v1.5 LOCKED;
3. Engineering Specification sections 01–06 v1.0 LOCKED / APPROVED;
4. `docs/traceability_matrix.md`;
5. `docs/runbooks/governor_gated_github_pr_agent_loop.md` v1.0 APPROVED;
6. `docs/implementation_context_governance.md`, if present in the repository;
7. `docs/runbooks/vps_security_baseline.md`;
8. `docs/runbooks/vps_development_environment.md`;
9. `docs/runbooks/vps_setup_procedure.md`.

If this runbook conflicts with any locked source-of-truth document or approved runbook, the locked / controlling source wins.

This runbook does not update `docs/traceability_matrix.md` because it does not create a new implementation module, database schema, model rule, portfolio rule, deployment exposure change, service topology change, or approved architecture change.

---

## 2. Purpose

This runbook defines how to create, store, verify, and restore backups for the single-VPS Phase 1 deployment of the `quant-research-platform` project.

Backups protect against:

1. VPS compromise;
2. accidental deletion;
3. failed migrations;
4. bad deployments;
5. provider account or infrastructure failure;
6. operator mistakes;
7. corrupted runtime data;
8. lost secrets.

A backup does not count as trusted until a restore has been tested. A file that has never been restored is only a backup candidate.

---

## 3. What must be backed up

Backups must cover runtime state and secrets that GitHub does not protect.

| Asset | Why it matters | Backup owner / source |
|---|---|---|
| Postgres application database | System-of-record data for universe, prices, features, targets, models, backtests, attribution, portfolio, paper state, order intent, and ops metadata | Postgres container / app database |
| MLflow metadata database | Experiment and model-run tracking metadata | Postgres container / MLflow database |
| MLflow artifact volume or mount path | Fitted model artifacts, MLflow run artifacts, calibration artifacts, and related files | Docker named volume or mounted artifact path |
| Lane-specific `.env` files | Runtime credentials and service connection values | Host filesystem inside each lane working tree |
| Lane-level deployment files not recoverable from Git | Any local deployment override that is approved but not in Git | Lane working tree or approved private operator storage |
| Optional logs | Troubleshooting only; logs are not a primary backup asset | Docker logs, app logs, or approved log path |

The `.env` backup is stored locally in plaintext at `chmod 600` in this v0.1 procedure. Encryption is required before any off-host copy and is tracked as OQ-VPS-BR-02. Treat the local secrets backup as sensitive accordingly.

GitHub backs up committed source code, documentation, config templates, and approved YAML configuration. GitHub does not back up runtime databases, Docker volumes, `.env` files, provider secrets, MLflow artifacts, or uncommitted local deployment state.

---

## 4. Lane-aware backup model

The canonical local backup root is:

```text
/srv/quant/backups/<lane>/
```

Approved lane roots:

```text
/srv/quant/backups/dev/
/srv/quant/backups/stage/
/srv/quant/backups/prod/
```

Recommended subdirectories under each lane backup root:

```text
/srv/quant/backups/<lane>/
  postgres/
  mlflow-artifacts/
  secrets/
  manifests/
  restore-tests/
```

Lane backups must not be mixed:

1. Development backups go under `/srv/quant/backups/dev/`.
2. Staging backups go under `/srv/quant/backups/stage/`.
3. Production backups go under `/srv/quant/backups/prod/`.
4. Production backups are never restored into dev or stage without an explicit manual review step.
5. Dev or stage backups are never restored into production.
6. Cross-lane backup movement must confirm the source lane, target lane, data sensitivity, and reason before any restore happens.

---

## 5. Off-host backup requirement

An off-host backup is a copy stored outside the VPS itself.

Provider snapshots are useful, but they are not sufficient by themselves because they remain tied to the same VPS provider account, provider infrastructure, provider control panel, and provider failure domain.

Off-host backups are required before the platform stores meaningful research data, MLflow artifacts, or secrets.

The final off-host destination is still an open question. Possible future destinations include:

1. Backblaze B2;
2. Cloudflare R2;
3. AWS S3;
4. an encrypted local copy on Jeremy's workstation or external drive;
5. another approved external destination.

This runbook does not require `rclone`, provider-native CLI tools, cloud backup agents, or any new backup tooling yet. A future approved implementation pass may choose `rclone`, a provider-native CLI, manual encrypted download, or another approved method.

---

## 6. Proposed backup cadence

These are proposed operational defaults, not final automation rules.

| Situation | Proposed backup action |
|---|---|
| Before major migrations or deployment changes | Manual backup first |
| During active development with meaningful data | At least weekly local backup, then off-host copy |
| Production-like or production lane once serious data exists | Daily or scheduled backup, to be approved later |
| After `.env` or secrets change | Update secure off-host secrets backup |
| Before destructive restore testing | Backup the target lane first if it contains anything worth keeping |

Automation is intentionally deferred. This v0.2 runbook does not create cron jobs, scripts, timers, or scheduled backup services.

---

## 7. Manual backup procedure — illustrative command patterns

The commands in this section are command patterns only. They are not final implementation commands until `docker-compose.yml`, service names, database names, volume names, and `.env.example` are finalized.

The patterns assume:

1. the operator is in the lane repository root, such as `/srv/quant/dev/quant-research-platform/`;
2. the Compose service name for Postgres is `postgres`;
3. the Compose project name is lane-specific (`qrp_dev`, `qrp_stage`, or `qrp_prod`);
4. the lane `.env` defines database names and users;
5. Docker commands use `sudo docker compose` during initial setup unless a later approved lane-user pattern allows non-sudo Docker operation;
6. a single Postgres Compose service named `postgres` hosts both the application database and the MLflow metadata database. If the final Compose topology splits MLflow onto a separate Postgres instance, §7.5 and §9.6 must be re-targeted to that service.

### 7.1 Choose the lane and prepare variables

Example for the development lane:

```bash
cd /srv/quant/dev/quant-research-platform

LANE="dev"
COMPOSE_PROJECT_NAME="qrp_dev"
BACKUP_ROOT="/srv/quant/backups/${LANE}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_PATH="$(pwd)"
GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
```

Example lane values:

| Lane | Repository root | Compose project name | Backup root |
|---|---|---|---|
| dev | `/srv/quant/dev/quant-research-platform` | `qrp_dev` | `/srv/quant/backups/dev` |
| stage | `/srv/quant/stage/quant-research-platform` | `qrp_stage` | `/srv/quant/backups/stage` |
| prod | `/srv/quant/prod/quant-research-platform` | `qrp_prod` | `/srv/quant/backups/prod` |

### 7.2 Create backup directories

```bash
mkdir -p \
  "${BACKUP_ROOT}/postgres" \
  "${BACKUP_ROOT}/mlflow-artifacts" \
  "${BACKUP_ROOT}/secrets" \
  "${BACKUP_ROOT}/manifests" \
  "${BACKUP_ROOT}/restore-tests"

chmod 700 "${BACKUP_ROOT}" "${BACKUP_ROOT}/secrets"
```

### 7.3 Load non-secret variable names carefully

This pattern loads `.env` into the shell without printing it. Do not run `cat .env` and do not paste `.env` into an LLM chat.

```bash
set -a
. ./.env
set +a
```

If this is not acceptable for the final implementation, replace it with an approved safer method later. The key rule is that commands must not print passwords or API keys.

### 7.4 Back up the Postgres application database

Illustrative custom-format dump pattern:

```bash
sudo docker compose -p "${COMPOSE_PROJECT_NAME}" exec -T postgres \
  pg_dump \
  -U "${APP_DB_USER}" \
  -d "${APP_DB_NAME}" \
  --format=custom \
  --no-owner \
  --no-acl \
  > "${BACKUP_ROOT}/postgres/${TS}_${LANE}_app_db.dump"
```

If authentication requires a password inside the container, the final implementation must use an approved method that does not print the password. Do not paste the password into the command line.

### 7.5 Back up the MLflow metadata database

Illustrative custom-format dump pattern:

```bash
sudo docker compose -p "${COMPOSE_PROJECT_NAME}" exec -T postgres \
  pg_dump \
  -U "${MLFLOW_DB_USER}" \
  -d "${MLFLOW_DB_NAME}" \
  --format=custom \
  --no-owner \
  --no-acl \
  > "${BACKUP_ROOT}/postgres/${TS}_${LANE}_mlflow_db.dump"
```

### 7.6 Back up MLflow artifacts

The exact artifact backup command depends on whether MLflow artifacts are stored in a Docker named volume or a host bind mount.

If artifacts are in a Docker named volume, the likely volume name pattern is namespaced by Compose project. Example pattern:

```bash
sudo docker run --rm \
  -v "${COMPOSE_PROJECT_NAME}_mlflow-artifacts:/mlflow-artifacts:ro" \
  -v "${BACKUP_ROOT}/mlflow-artifacts:/backup" \
  alpine \
  tar -czf "/backup/${TS}_${LANE}_mlflow_artifacts.tar.gz" -C /mlflow-artifacts .
```

If artifacts are mounted into the MLflow container at a known path, an alternate pattern is:

```bash
sudo docker compose -p "${COMPOSE_PROJECT_NAME}" exec -T mlflow \
  tar -czf - -C /mlflow/artifacts . \
  > "${BACKUP_ROOT}/mlflow-artifacts/${TS}_${LANE}_mlflow_artifacts.tar.gz"
```

Only one of these patterns should be used after the actual artifact location is finalized.

### 7.7 Back up `.env` securely

The lane `.env` is sensitive. Back it up locally with owner-only permissions and prefer encryption before any off-host copy.

```bash
install -m 600 .env "${BACKUP_ROOT}/secrets/${TS}_${LANE}.env"
chmod 600 "${BACKUP_ROOT}/secrets/${TS}_${LANE}.env"
```

Preferred future pattern after encryption method is approved:

```bash
# Placeholder only — final encryption method is an open question.
# Encrypt "${BACKUP_ROOT}/secrets/${TS}_${LANE}.env" before copying it off-host.
```

Do not commit `.env`. Do not include real `.env` values in markdown, issues, PRs, logs, screenshots, or LLM prompts.

### 7.8 Generate checksums

```bash
cd "${BACKUP_ROOT}"

sha256sum \
  "postgres/${TS}_${LANE}_app_db.dump" \
  "postgres/${TS}_${LANE}_mlflow_db.dump" \
  "mlflow-artifacts/${TS}_${LANE}_mlflow_artifacts.tar.gz" \
  "secrets/${TS}_${LANE}.env" \
  > "manifests/${TS}_${LANE}_sha256sums.txt"

chmod 600 "manifests/${TS}_${LANE}_sha256sums.txt"
```

If `.env` is encrypted later, generate checksums for the encrypted file that is copied off-host.

### 7.9 Create a backup manifest

The manifest should describe what was created without exposing secrets.

```bash
cat > "${BACKUP_ROOT}/manifests/${TS}_${LANE}_manifest.txt" <<MANIFEST
backup_timestamp_utc=${TS}
lane=${LANE}
repo_path=${REPO_PATH}
git_commit_sha=${GIT_SHA}
compose_project=${COMPOSE_PROJECT_NAME}
app_db_dump=postgres/${TS}_${LANE}_app_db.dump
mlflow_db_dump=postgres/${TS}_${LANE}_mlflow_db.dump
mlflow_artifacts_archive=mlflow-artifacts/${TS}_${LANE}_mlflow_artifacts.tar.gz
env_backup=secrets/${TS}_${LANE}.env
checksums=manifests/${TS}_${LANE}_sha256sums.txt
notes=Manual backup command pattern; verify restore before trusting.
MANIFEST

chmod 600 "${BACKUP_ROOT}/manifests/${TS}_${LANE}_manifest.txt"
```

### 7.10 Verify local backup files

```bash
ls -lh \
  "${BACKUP_ROOT}/postgres/${TS}_${LANE}_app_db.dump" \
  "${BACKUP_ROOT}/postgres/${TS}_${LANE}_mlflow_db.dump" \
  "${BACKUP_ROOT}/mlflow-artifacts/${TS}_${LANE}_mlflow_artifacts.tar.gz" \
  "${BACKUP_ROOT}/secrets/${TS}_${LANE}.env" \
  "${BACKUP_ROOT}/manifests/${TS}_${LANE}_sha256sums.txt" \
  "${BACKUP_ROOT}/manifests/${TS}_${LANE}_manifest.txt"

cd "${BACKUP_ROOT}"
sha256sum -c "manifests/${TS}_${LANE}_sha256sums.txt"
```

A backup with missing files, zero-byte files, or failed checksums must be treated as failed.

After verifying the backup, exit the shell or unset the loaded variables. Do not leave a shell with secrets in its environment open longer than the backup window.

---

## 8. Off-host copy procedure — placeholder

Do not pick the off-host provider in this v0.2 runbook.

Required flow after the destination is approved:

1. create local backup;
2. verify local file sizes;
3. generate local checksums;
4. copy backup files to the approved off-host destination;
5. verify remote listing;
6. verify remote checksum where the destination supports it;
7. record the off-host copy location in the manifest or private operator notes.

Placeholder command shape:

```bash
# Placeholder only.
# Final command depends on the approved destination.
# Examples could later use rclone, provider-native CLI, secure copy, or manual encrypted download.
```

Do not treat the backup as complete until both the local backup and off-host copy are verified.

---

## 9. Restore procedure

Restores must be conservative. A restore can destroy or overwrite data if run against the wrong lane or database.

Restore into dev or another approved test target first whenever practical. Never restore directly into production unless Jeremy explicitly approves the restore plan.

### 9.1 Restore guardrails

Before any restore:

1. identify the source backup timestamp;
2. identify the source lane;
3. identify the target lane;
4. confirm the target lane repository path;
5. confirm the target Compose project name;
6. confirm the target database names;
7. confirm whether existing target data will be destroyed;
8. stop affected lane containers before restoring where appropriate;
9. use a new or empty restore target where practical;
10. verify checksums before restoring;
11. do not expose any public service ports for restore access.

Production-specific guardrail:

```text
Never overwrite the production lane without an approved restore plan.
```

### 9.2 Set restore variables

Illustrative pattern:

```bash
SOURCE_LANE="dev"
TARGET_LANE="dev"
TARGET_COMPOSE_PROJECT_NAME="qrp_dev"
TARGET_REPO="/srv/quant/dev/quant-research-platform"
BACKUP_TS="<backup_timestamp_utc>"
BACKUP_ROOT="/srv/quant/backups/${SOURCE_LANE}"

cd "${TARGET_REPO}"
set -a
. ./.env
set +a
```

If `SOURCE_LANE` and `TARGET_LANE` differ, do not continue until the cross-lane restore review is complete.

### 9.3 Verify checksums before restore

```bash
cd "${BACKUP_ROOT}"
sha256sum -c "manifests/${BACKUP_TS}_${SOURCE_LANE}_sha256sums.txt"
```

If checksums fail, stop. Do not restore from a backup whose integrity check failed.

### 9.4 Stop write-capable services before restore

The exact stop pattern depends on the final service design. The safest default is to stop services that may write to Postgres or MLflow artifacts while keeping the Postgres service available for `pg_restore`.

Illustrative pattern:

```bash
cd "${TARGET_REPO}"
sudo docker compose -p "${TARGET_COMPOSE_PROJECT_NAME}" stop app mlflow
sudo docker compose -p "${TARGET_COMPOSE_PROJECT_NAME}" up -d postgres
```

Do not use a full `docker compose down` immediately before `pg_restore` unless the restore plan also starts the Postgres service again before database restore commands are run.

Before running `pg_restore`, confirm no other clients hold connections to the target database. Either rely on the stopped containers being the only writers, or terminate remaining backends against the target DB before restore.

### 9.5 Restore the Postgres application database

This pattern assumes the database already exists and the restore target is approved.

```bash
cd "${TARGET_REPO}"

cat "${BACKUP_ROOT}/postgres/${BACKUP_TS}_${SOURCE_LANE}_app_db.dump" | \
  sudo docker compose -p "${TARGET_COMPOSE_PROJECT_NAME}" exec -T postgres \
  pg_restore \
  -U "${APP_DB_USER}" \
  -d "${APP_DB_NAME}" \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl
```

For production restore, this command must not be run until the restore plan is approved.

When this pattern is later wrapped in a script, the script must enable `set -o pipefail` or equivalent so that a non-zero `pg_restore` exit status is not masked by `cat`.

### 9.6 Restore the MLflow metadata database

```bash
cat "${BACKUP_ROOT}/postgres/${BACKUP_TS}_${SOURCE_LANE}_mlflow_db.dump" | \
  sudo docker compose -p "${TARGET_COMPOSE_PROJECT_NAME}" exec -T postgres \
  pg_restore \
  -U "${MLFLOW_DB_USER}" \
  -d "${MLFLOW_DB_NAME}" \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl
```

### 9.7 Restore MLflow artifacts

The volume name pattern below assumes the same Compose volume naming convention used in §7.6. Confirm against the final `docker-compose.yml` before running.

If using a Docker named volume, one possible pattern is:

```bash
sudo docker run --rm \
  -v "${TARGET_COMPOSE_PROJECT_NAME}_mlflow-artifacts:/mlflow-artifacts" \
  -v "${BACKUP_ROOT}/mlflow-artifacts:/backup:ro" \
  alpine \
  sh -c "rm -rf /mlflow-artifacts/* && tar -xzf /backup/${BACKUP_TS}_${SOURCE_LANE}_mlflow_artifacts.tar.gz -C /mlflow-artifacts"
```

If using a mounted artifact path, use the approved final path and restore method. Do not guess the production artifact path during an incident.

### 9.8 Restore `.env` only from a secure source

Do not restore `.env` from Git because real `.env` files are never committed.

```bash
install -m 600 "${BACKUP_ROOT}/secrets/${BACKUP_TS}_${SOURCE_LANE}.env" "${TARGET_REPO}/.env"
chmod 600 "${TARGET_REPO}/.env"
```

If the restore follows suspected compromise, do not reuse the old `.env` secrets. Create a fresh `.env` with rotated credentials instead.

### 9.9 Start containers and run smoke checks

```bash
cd "${TARGET_REPO}"
sudo docker compose -p "${TARGET_COMPOSE_PROJECT_NAME}" up -d
sudo docker compose -p "${TARGET_COMPOSE_PROJECT_NAME}" ps
```

Illustrative database checks:

```bash
sudo docker compose -p "${TARGET_COMPOSE_PROJECT_NAME}" exec postgres \
  pg_isready -U "${APP_DB_USER}" -d "${APP_DB_NAME}"

sudo docker compose -p "${TARGET_COMPOSE_PROJECT_NAME}" exec postgres \
  pg_isready -U "${MLFLOW_DB_USER}" -d "${MLFLOW_DB_NAME}"
```

Confirm Dash and MLflow only through SSH tunnel or localhost-only access. Do not open public ports to make restore validation easier.

### 9.10 Confirm no public ports were opened

Run the listener check after restore:

```bash
sudo ss -tulpen | grep -v 127.0.0.1 | grep -v '\[::1\]'
```

Passing condition:

```text
Only sshd should be listening on non-loopback addresses.
Postgres, MLflow, Dash, and application service ports must not appear on 0.0.0.0 or public IPv6 addresses.
```

---

## 10. Restore test procedure

At least one restore test is required before backups are trusted.

Recommended restore-test pattern:

1. use the dev lane or another approved test target;
2. create a backup from the source lane;
3. verify checksums;
4. restore the app database;
5. restore the MLflow metadata database;
6. restore MLflow artifacts;
7. restore or recreate `.env` securely;
8. start containers;
9. verify the application starts;
10. verify MLflow metadata and artifacts are readable;
11. verify Dash and MLflow are reachable only through SSH tunnel / localhost-only access;
12. verify no public ports were opened;
13. verify secrets were not committed, logged, or written into documentation.

Once serious data exists, perform restore tests monthly or at another approved periodic cadence.

Restore-test notes should be stored under:

```text
/srv/quant/backups/<lane>/restore-tests/
```

or in private operator notes if the restore test includes sensitive details.

Suggested restore-test note format:

```text
restore_test_timestamp_utc=<timestamp>
source_backup_timestamp_utc=<backup timestamp>
source_lane=<lane>
target_lane=<lane>
operator=<name>
app_db_restore=pass/fail
mlflow_db_restore=pass/fail
mlflow_artifacts_restore=pass/fail
app_start=pass/fail
dash_access_local_only=pass/fail
mlflow_access_local_only=pass/fail
non_loopback_listener_check=pass/fail
secrets_not_exposed=pass/fail
notes=<short non-secret notes>
```

---

## 11. Backup verification checklist

Use this checklist after each manual backup and after each restore test.

| Check | Pass / Fail |
|---|---|
| Correct lane selected |  |
| Local backup root exists under `/srv/quant/backups/<lane>/` |  |
| App database dump exists |  |
| MLflow metadata database dump exists |  |
| MLflow artifact archive exists |  |
| `.env` backup exists or fresh secrets are documented separately |  |
| Backup files are non-zero size |  |
| Checksums were generated |  |
| Checksum verification passed |  |
| Manifest was created |  |
| File permissions are owner-only where sensitive |  |
| Off-host copy exists |  |
| Off-host copy listing/checksum verified where supported |  |
| Latest backup timestamp is recent enough for the lane |  |
| Restore test has been performed before trusting the backup set |  |
| `.env` backup is secured and preferably encrypted before off-host copy |  |
| No secrets were committed, logged, pasted, or documented |  |
| Non-loopback listener check still passes after restore |  |

---

## 12. Proposed retention policy

These are proposed defaults pending approval.

| Lane | Proposed retention default | Rationale |
|---|---|---|
| dev | Keep the most recent 2–4 weekly backup sets | Dev data changes often and can usually be recreated |
| stage | Keep the most recent 4–8 weekly backup sets if staging is used | Stage should preserve enough history for deployment testing |
| prod | Keep at least 30 daily backups and 12 monthly backups once serious data exists | Production-like evidence and MLflow artifacts become harder to recreate |

Open items:

1. final retention periods by lane;
2. storage growth limits;
3. MLflow artifact cleanup policy;
4. whether older prod backups should be archived to cheaper storage;
5. whether retention should differ before and after serious production-like use.

Do not delete backups automatically until the retention policy is approved and restore testing is reliable.

---

## 13. What not to do

Do not:

1. store backups only on the VPS;
2. treat provider snapshots as the only backup;
3. commit `.env` or secrets;
4. paste secrets into LLM chats;
5. print passwords or API keys in logs;
6. restore a production backup into dev or stage without review;
7. restore dev or stage data into production;
8. overwrite production without an approved restore plan;
9. expose Postgres, MLflow, Dash, or application ports publicly for backup or restore;
10. weaken SSH, UFW, Docker binding, or provider firewall rules to make restore easier;
11. create backup scripts in this v0.2 runbook;
12. create cron jobs in this v0.2 runbook;
13. install backup tooling in this v0.2 runbook;
14. install or activate AI Maestro as part of backup or restore;
15. add live broker SDKs, broker credentials, or live trading behavior.

---

## 14. Incident recovery outline

If compromise is suspected:

1. preserve evidence if safe to do so;
2. take a provider snapshot only if it does not worsen the incident;
3. disconnect public access if needed;
4. rotate secrets;
5. assume the old `.env` may be compromised;
6. rebuild a clean VPS from approved docs and Git;
7. restore only from trusted backups created before the compromise;
8. do not reuse old secrets from the compromised VPS;
9. run restore smoke checks;
10. verify no public ports are exposed;
11. document the incident and recovery steps in private operator notes.

A clean rebuild is preferred over repairing a compromised VPS.

---

## 15. Open questions

| ID | Question | Current disposition |
|---|---|---|
| OQ-VPS-BR-01 | What is the final off-host backup destination? | Open |
| OQ-VPS-BR-02 | What encryption method should be used for `.env` and secrets backups? | Open |
| OQ-VPS-BR-03 | What are final retention periods by lane? | Open |
| OQ-VPS-BR-04 | Should `scripts/backup.sh` be created later? | Open; not created by this runbook |
| OQ-VPS-BR-05 | Should `scripts/restore.sh` be created later? | Open; not created by this runbook |
| OQ-VPS-BR-06 | Should scheduled backups be automated later? | Open; no cron jobs or timers created by this runbook |
| OQ-VPS-BR-07 | Should future implementation use `rclone`, provider-native CLI, secure copy, or manual encrypted download? | Open |
| OQ-VPS-BR-08 | Should restore testing use a dedicated restore lane separate from dev/stage/prod? | Open |
| OQ-VPS-BR-09 | Should production backups require separate encryption keys from dev/stage backups? | Open |
| OQ-VPS-BR-10 | What is the final MLflow artifact storage path or volume name? | Open until implementation finalizes Compose details |
| OQ-VPS-BR-11 | What is the approved authentication method for `pg_dump` / `pg_restore` invocations inside the Postgres container? | Open |
| OQ-VPS-BR-12 | Should the backup manifest capture image tags and Postgres extension list at backup time? | Open |
| OQ-VPS-BR-13 | What is the soft RPO target per lane? | Open |
| OQ-VPS-BR-14 | What is the soft RTO target per lane, particularly for prod? | Open |

---

## 16. Completion criteria

This runbook is complete for a lane when:

- [ ] backup root exists under `/srv/quant/backups/<lane>/`;
- [ ] required subdirectories exist;
- [ ] local manual backup has been created;
- [ ] app database dump exists;
- [ ] MLflow metadata database dump exists;
- [ ] MLflow artifact archive exists;
- [ ] secrets backup is handled securely;
- [ ] checksums are generated;
- [ ] checksum verification passes;
- [ ] backup manifest is generated;
- [ ] off-host copy destination is selected before serious use;
- [ ] off-host copy is completed before serious use;
- [ ] at least one restore test is performed before trusting backups;
- [ ] restore-test notes are recorded;
- [ ] no public ports are opened;
- [ ] no secrets are committed, pasted, logged, or included in markdown.

---

## 17. Official references

Use official references when finalizing commands:

- PostgreSQL backup and restore documentation: https://www.postgresql.org/docs/current/backup.html
- PostgreSQL `pg_dump` documentation: https://www.postgresql.org/docs/current/app-pgdump.html
- PostgreSQL `pg_restore` documentation: https://www.postgresql.org/docs/current/app-pgrestore.html
- Docker storage volumes documentation: https://docs.docker.com/engine/storage/volumes/
- Docker Compose documentation: https://docs.docker.com/compose/
- MLflow artifact store documentation: https://mlflow.org/docs/latest/tracking/artifacts-stores/
- Ubuntu security documentation: https://ubuntu.com/server/docs/security
- UFW documentation: https://help.ubuntu.com/community/UFW
- rclone documentation, possible future tooling only: https://rclone.org/docs/

---

## 18. Closing statement

This runbook defines backup and restore discipline for the Phase 1 VPS deployment without changing the approved architecture or starting implementation. The next step after QA is to revise this draft if needed, approve it as an operational runbook, and later fill in final command details when `docker-compose.yml`, `.env.example`, service names, database names, and MLflow artifact storage are finalized through the normal project workflow.
