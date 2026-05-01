# Quant Research Platform — VPS Security Baseline Procedure

**Phase 1 scope:** ETF tactical research platform  
**Document type:** Runbook / security procedure  
**Canonical suggested path:** `docs/runbooks/vps_security_baseline.md`  
**Document status:** v0.2.1 DRAFT / targeted polish pass on top of v0.2  
**Created:** 2026-04-30  
**Last updated:** 2026-05-01  
**Document status:** v1.0 LOCKED / APPROVED 
**Approved by:**Approved by Jeremy dempsey May 1 2026

---

## Changelog

### v0.2.1 DRAFT / targeted polish pass

Targeted polish pass on top of v0.2. No scope changes. Edits:

1. Replaced section-number cross-reference with a stable phrase that does not depend on numbering.
2. Added a journald-persistence fallback for the case where `/etc/systemd/journald.conf` has no `Storage=` line at all.
3. Added one sentence near the first package-install command noting that the install command may appear more than once for procedural completeness; running it once is sufficient.

### v0.2 DRAFT / targeted security QA revision

Targeted security QA revision. Major changes:

1. Added source-authority and traceability notes clarifying that this is an operational runbook, not an Engineering Specification section.
2. Added explicit Docker / UFW warning: UFW does not reliably protect Docker-published ports; Phase 1 requires loopback-only host bindings or internal Docker networking.
3. Added Docker port-binding examples and non-loopback listener verification command.
4. Clarified SSH hardening verification with `sshd -T` instead of misleading root-login tests.
5. Added `ChallengeResponseAuthentication no` alongside `KbdInteractiveAuthentication no`.
6. Added verification that `/etc/ssh/sshd_config.d/*.conf` is included before relying on SSH override files.
7. Clarified `deploy` user password purpose and SSH key ownership/permissions.
8. Added journald persistence check for Fail2ban when using `backend = systemd`.
9. Added IPv6 guidance to provider firewall section.
10. Changed backup directory default permissions to `700`.
11. Added off-host backup requirement before meaningful research data, MLflow artifacts, or secrets are stored.
12. Added weekly backup timestamp verification and periodic restore-test reminder.
13. Completed the Windows SSH note enough to avoid ambiguity.
14. Added Open Questions section.

### v0.1 DRAFT

Initial VPS security baseline procedure covering SSH hardening, UFW, Fail2ban, unattended security updates, Docker exposure discipline, secrets handling, backups, recurring checks, and incident response basics.

---

## 1. Purpose

This runbook defines the minimum VPS security baseline that should be completed before installing or running the `quant-research-platform` application stack.

This is a procedure document, not an Engineering Specification section. It does not change the approved project architecture, does not expose the Dash UI publicly, does not expose MLflow publicly, does not expose Postgres publicly, and does not introduce live trading, broker APIs, or broker credentials.

The goal is to make the first Ubuntu VPS safe enough for Phase 1 development and internal paper-portfolio operation by establishing:

1. key-based SSH access;
2. no root SSH login;
3. no password-based SSH login;
4. host firewall enabled;
5. brute-force protection enabled;
6. automatic security updates configured;
7. Docker exposure constrained;
8. secrets protected;
9. off-host backup requirement documented;
10. recurring security checks defined.

---

## 2. Source authority and status

This runbook is an operational procedure, not an Engineering Specification section.

The locked Strategy Decision Record, Engineering Workflow, and Engineering Specification remain the source of truth for architecture, service ownership, Phase 1 scope, deployment exposure, and no-live-trading boundaries.

This runbook implements the approved Phase 1 private Ubuntu VPS operating pattern using Docker Compose, Postgres, MLflow, Dash, SSH-tunneled access, and no public exposure of application services.

Operational defaults in this runbook, such as the `deploy` user, `/srv/quant` host path, SSH key naming examples, and use of `sudo docker` instead of docker group membership, are runbook-level defaults. They are subject to override by a future approved deployment specification or Approver-directed runbook amendment.

This runbook should be completed before the general VPS setup procedure continues.

---

## 3. Traceability note

This runbook does not update `docs/traceability_matrix.md` because it is not an Engineering Specification section and does not create a new implementation module, database schema, model rule, portfolio rule, or deployment exposure change.

Future changes that alter deployment exposure, service topology, Docker Compose behavior, public access, or the approved security posture must go through the normal Engineering Workflow approval path and may require a traceability update.

Examples of changes that would require additional approval discipline:

1. exposing Dash, MLflow, Postgres, or application ports publicly;
2. adding nginx, reverse proxy, public TLS, VPN, or public authentication surfaces;
3. changing the Docker Compose service topology;
4. adding new public management services;
5. adding live broker connectivity or broker credentials.

---

## 4. Security baseline summary

Complete these items before continuing with `docs/runbooks/vps_setup_procedure.md`.

| Area | Required Phase 1 baseline |
|---|---|
| Admin access | Non-root sudo user only |
| SSH authentication | SSH key-based login |
| Root SSH | Disabled |
| Password SSH | Disabled after key login is tested |
| Firewall | UFW enabled; deny incoming by default; allow SSH only by default |
| Public app exposure | None by default; no public Postgres, MLflow, Dash, or app ports |
| Docker exposure | Host-published app ports must bind to `127.0.0.1`; internal services should use Docker networking / `expose` |
| Brute-force protection | Fail2ban enabled for SSH |
| Security updates | `unattended-upgrades` enabled and verified |
| Docker access | Use `sudo docker ...` initially; do not casually add users to the `docker` group |
| Secrets | `.env` gitignored, permissioned, and backed up securely outside Git |
| Recovery | Provider console access and off-host backup requirement verified |
| Monitoring | Basic recurring checks defined |

---

## 5. Required packages

Most security tools should be installed from Ubuntu package repositories, not from random websites.

The package install command may appear more than once in this runbook for procedural completeness; running it once is sufficient.

Install these on the VPS:

```bash
sudo apt update
sudo apt install -y ufw fail2ban unattended-upgrades apt-listchanges needrestart
```

Optional later, after the baseline is stable:

```bash
sudo apt install -y auditd
```

Do not start with heavy monitoring stacks such as Wazuh, CrowdSec, SIEM tooling, Kubernetes, public TLS, a reverse proxy, Tailscale, WireGuard, or VPN requirements. Those may be useful later, but they add operational complexity before the basic hardening is in place.

---

## 6. Before starting: gather these values

Fill these in before running commands.

```text
VPS public IPv4:                  <your-vps-ipv4>
VPS public IPv6, if assigned:      <your-vps-ipv6-or-none>
Local SSH key name:               ~/.ssh/quant_vps_ed25519
Initial VPS user from provider:   root or provider-created user
New admin user to create:         deploy
Project base directory:           /srv/quant
Repository directory:             /srv/quant/dev/quant-research-platform
Provider console URL/location:    <provider-console-location>
```

If the provider gives browser-based console access, verify that you know how to open it before changing SSH settings. This is your recovery path if you lock yourself out.

---

## 7. Local machine: create an SSH key

Run this on your local computer, not on the VPS.

### 7.1 macOS / Linux / Git Bash / WSL

Create a dedicated SSH key for this VPS:

```bash
ssh-keygen -t ed25519 -C "quant-research-platform-vps" -f ~/.ssh/quant_vps_ed25519
```

Use a passphrase when prompted. Store the passphrase in your password manager.

Confirm the files exist:

```bash
ls -l ~/.ssh/quant_vps_ed25519 ~/.ssh/quant_vps_ed25519.pub
```

The `.pub` file is safe to copy to the server. The private key file without `.pub` must stay private.

### 7.2 Windows PowerShell / Windows Terminal

Windows 10/11 normally includes the OpenSSH Client. Check first:

```powershell
ssh -V
```

If `ssh` is not recognized, install or enable the Windows OpenSSH Client before continuing.

Create the key:

```powershell
ssh-keygen -t ed25519 -C "quant-research-platform-vps" -f "$env:USERPROFILE\.ssh\quant_vps_ed25519"
```

Connect with the key later using:

```powershell
ssh -i "$env:USERPROFILE\.ssh\quant_vps_ed25519" deploy@<your-vps-ip>
```

Do not turn this into a shared key. This key is for this VPS only.

---

## 8. First VPS login and system update

Log in using the initial provider credentials.

```bash
ssh root@<your-vps-ip>
```

or, if the provider created a non-root user:

```bash
ssh <provider-user>@<your-vps-ip>
```

Update the base system:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y ufw fail2ban unattended-upgrades apt-listchanges needrestart curl ca-certificates gnupg lsb-release
```

If the upgrade says a reboot is required, reboot before continuing:

```bash
sudo reboot
```

Reconnect after the reboot.

---

## 9. Create a non-root sudo user

Use a dedicated admin/deployment user such as `deploy`.

If logged in as root:

```bash
adduser deploy
usermod -aG sudo deploy
```

If logged in as a non-root provider user with sudo:

```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
```

The password created by `adduser deploy` is for sudo and provider-console recovery, not for ongoing SSH password login. SSH password login will be disabled later after key-based login is verified.

Use a strong password and store it in your password manager.

Verify the user exists:

```bash
id deploy
```

Expected result includes the `sudo` group.

---

## 10. Install the SSH public key for the new user

On the VPS:

```bash
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo nano /home/deploy/.ssh/authorized_keys
```

Paste the contents of your local public key.

On your local machine, show the public key with:

```bash
cat ~/.ssh/quant_vps_ed25519.pub
```

On Windows PowerShell:

```powershell
Get-Content "$env:USERPROFILE\.ssh\quant_vps_ed25519.pub"
```

After pasting the public key into `/home/deploy/.ssh/authorized_keys`, set ownership and permissions on the VPS:

```bash
sudo chown -R deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

Why this matters: `sshd` may reject key-based login if `.ssh` or `authorized_keys` are owned by the wrong user or are group/world writable. Do not “fix” these files back to root ownership.

---

## 11. Test key-based login before changing SSH security

Do not close the original SSH session yet.

Open a second terminal window on your local machine and test:

```bash
ssh -i ~/.ssh/quant_vps_ed25519 deploy@<your-vps-ip>
```

From Windows PowerShell:

```powershell
ssh -i "$env:USERPROFILE\.ssh\quant_vps_ed25519" deploy@<your-vps-ip>
```

Then verify sudo:

```bash
sudo whoami
```

Expected result:

```text
root
```

Only continue after the second terminal successfully logs in as `deploy` and `sudo whoami` returns `root`.

Lockout guardrail:

1. Keep the original SSH session open.
2. Open a second terminal.
3. Confirm key-based login works.
4. Confirm sudo works.
5. Only then disable root/password SSH login.

---

## 12. Harden SSH configuration

### 12.1 Back up the SSH config

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%Y%m%d_%H%M%S)
```

### 12.2 Verify SSH include-directory support

Before relying on `/etc/ssh/sshd_config.d/99-quant-security.conf`, verify that the main SSH config includes the directory:

```bash
grep -i '^Include' /etc/ssh/sshd_config
```

Expected result should include something like:

```text
Include /etc/ssh/sshd_config.d/*.conf
```

If this include line is missing, pause before continuing. Either add the include line carefully or edit the main config directly. Do not assume override files work until this is verified.

### 12.3 Create a project hardening override

Using a file under `/etc/ssh/sshd_config.d/` is cleaner than editing the main config directly when the include directive exists.

```bash
sudo nano /etc/ssh/sshd_config.d/99-quant-security.conf
```

Add:

```text
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PubkeyAuthentication yes
X11Forwarding no
AllowUsers deploy
```

Notes:

- `AllowUsers deploy` means only the `deploy` user may log in by SSH.
- If you choose a different admin username, change this line.
- Do not add `AllowUsers deploy` until the `deploy` key-based login has been tested.
- Keep provider console access available before applying this.

### 12.4 Validate SSH config syntax

```bash
sudo sshd -t
```

If there is no output, the syntax is valid.

### 12.5 Restart SSH

On Ubuntu, the service may be named `ssh`.

```bash
sudo systemctl restart ssh
sudo systemctl status ssh --no-pager
```

### 12.6 Verify effective SSH security settings

Use `sshd -T` to confirm the effective configuration instead of relying on a login failure test.

```bash
sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|kbdinteractiveauthentication|challengeresponseauthentication|pubkeyauthentication|allowusers'
```

Expected baseline:

```text
permitrootlogin no
passwordauthentication no
kbdinteractiveauthentication no
challengeresponseauthentication no
pubkeyauthentication yes
allowusers deploy
```

Some OpenSSH versions may not return `challengeresponseauthentication` as a separate line. If that occurs, confirm that the syntax check passed and that password / keyboard-interactive authentication are disabled.

### 12.7 Test a new login again

Keep your current terminal open. Open another new terminal and test:

```bash
ssh -i ~/.ssh/quant_vps_ed25519 deploy@<your-vps-ip>
```

Expected result: login succeeds as `deploy` using the SSH key.

Do not close your original session until this works.

---

## 13. Configure the host firewall with UFW

Ubuntu uses `ufw` as the default firewall configuration tool. UFW is typically disabled by default, so explicitly enable it.

Important limitation: UFW is a host firewall baseline. It does not reliably protect against incorrectly published Docker ports. Docker port publishing is handled separately in the Docker security baseline section below.

### 13.1 Allow SSH before enabling the firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw status verbose
```

If you later choose a custom SSH port, allow that port before enabling the firewall.

### 13.2 Enable UFW

```bash
sudo ufw enable
sudo ufw status verbose
```

Expected result should include:

```text
Status: active
OpenSSH ALLOW Anywhere
```

If IPv6 is enabled, UFW may also show OpenSSH rules for IPv6. That is acceptable only for SSH.

### 13.3 Confirm no application ports are intentionally allowed

For Phase 1, do not publicly allow these ports:

| Service | Typical port | Public access? |
|---|---:|---:|
| Postgres | 5432 | No |
| MLflow | 5000 | No |
| Dash app | commonly 8050 or app-defined | No |
| Internal app health endpoints | app-defined | No |

Access MLflow and Dash through SSH tunnels or other explicitly approved private access patterns only.

---

## 14. Configure Fail2ban for SSH protection

Fail2ban watches logs and bans hosts with repeated failed login attempts.

### 14.1 Enable service

```bash
sudo systemctl enable --now fail2ban
sudo systemctl status fail2ban --no-pager
```

### 14.2 Check journald persistence

This runbook uses `backend = systemd` for the SSH jail. Some VPS images keep journald logs only in memory. If journald storage is volatile, useful Fail2ban history may not persist across reboots.

Check the current setting:

```bash
grep -E '^Storage' /etc/systemd/journald.conf
```

If the command returns nothing or shows volatile storage, enable persistent journal storage:

```bash
sudo mkdir -p /var/log/journal
sudo sed -i 's/^#\?Storage=.*/Storage=persistent/' /etc/systemd/journald.conf
sudo systemctl restart systemd-journald
```

Verify:

```bash
grep -E '^Storage' /etc/systemd/journald.conf
```

Expected:

```text
Storage=persistent
```

Fallback if the verify command still returns nothing (the original config had no `Storage=` line at all):

```bash
echo 'Storage=persistent' | sudo tee -a /etc/systemd/journald.conf
sudo systemctl restart systemd-journald
grep -E '^Storage' /etc/systemd/journald.conf
```

### 14.3 Create local SSH jail

Do not edit the default jail file directly. Create a local override:

```bash
sudo nano /etc/fail2ban/jail.d/sshd.local
```

Add:

```ini
[sshd]
enabled = true
port = ssh
filter = sshd
backend = systemd
maxretry = 5
findtime = 10m
bantime = 1h
```

Restart Fail2ban:

```bash
sudo systemctl restart fail2ban
```

### 14.4 Verify Fail2ban

```bash
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

Expected result: `sshd` appears as an active jail.

Do not overcomplicate Fail2ban beyond SSH protection for Phase 1.

---

## 15. Configure automatic security updates

Ubuntu Server commonly enables security updates by default, but this project should verify and document the configuration.

### 15.1 Install packages

```bash
sudo apt install -y unattended-upgrades apt-listchanges
```

### 15.2 Enable unattended upgrades

```bash
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Choose `Yes` when prompted.

### 15.3 Verify configuration files

```bash
cat /etc/apt/apt.conf.d/20auto-upgrades
```

Expected baseline:

```text
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```

### 15.4 Verify service and logs

```bash
systemctl status unattended-upgrades --no-pager
ls -l /var/log/unattended-upgrades/
```

### 15.5 Reboot discipline

Check for required reboots:

```bash
if [ -f /var/run/reboot-required ]; then cat /var/run/reboot-required; fi
```

A simple Phase 1 policy:

1. apply security updates automatically;
2. check weekly whether a reboot is required;
3. reboot manually during a quiet window;
4. confirm containers come back up after reboot once Docker is installed.

---

## 16. Docker security baseline

Docker is required for this project, but Docker access and Docker networking must be treated carefully.

### 16.1 Do not casually add users to the `docker` group

Docker's official documentation warns that membership in the `docker` group grants root-level privileges. For the first VPS build, prefer:

```bash
sudo docker ps
sudo docker compose ps
```

Avoid this unless you explicitly accept the security tradeoff:

```bash
sudo usermod -aG docker deploy
```

Runbook default: do not add `deploy` to the `docker` group during the initial Phase 1 VPS setup.

### 16.2 Critical warning: UFW does not reliably protect Docker-published ports

Docker-published ports can bypass the effective protection you expect from UFW because Docker manages its own firewall / iptables rules.

Do not treat `ufw status` as proof that Docker-published services are private.

Phase 1 standard:

1. Any host-published service port must bind to `127.0.0.1` only.
2. Internal container-to-container traffic should use Docker internal networking or `expose`, not public `ports`.
3. Any `0.0.0.0` host binding or public IPv6 binding is a security defect unless explicitly approved as a deployment exposure change.
4. UFW is still required for baseline host firewall protection, but Docker Compose port bindings are the primary enforcement point for container service exposure.

### 16.3 Safe and unsafe Docker Compose examples

Acceptable for local SSH tunnel access only:

```yaml
ports:
  - "127.0.0.1:8050:8050"
  - "127.0.0.1:5000:5000"
```

Not acceptable for Phase 1:

```yaml
ports:
  - "8050:8050"
  - "0.0.0.0:8050:8050"
```

Also not acceptable if the host has public IPv6:

```yaml
ports:
  - "[::]:8050:8050"
```

Preferred for internal-only service access:

```yaml
# Internal-only service; no host port exposed.
# Other containers can reach it on the Docker network.
expose:
  - "5432"
```

### 16.4 SSH tunnel access pattern

If MLflow or Dash are bound to loopback on the VPS, connect from your local computer using SSH tunnels.

Example:

```bash
ssh -i ~/.ssh/quant_vps_ed25519 -L 5000:127.0.0.1:5000 -L 8050:127.0.0.1:8050 deploy@<your-vps-ip>
```

Then browse locally to:

```text
http://127.0.0.1:5000
http://127.0.0.1:8050
```

### 16.5 Verify exposed listening ports

Run:

```bash
sudo ss -tulpen | grep -v 127.0.0.1 | grep -v '\[::1\]'
```

Passing condition:

```text
Only sshd should be listening on non-loopback addresses.
Postgres, MLflow, Dash, and application service ports must not appear on 0.0.0.0 or public IPv6 addresses.
```

Acceptable non-loopback listener:

```text
sshd on port 22, or the approved SSH port if changed
```

Not acceptable:

```text
Postgres 5432 on 0.0.0.0 or public IPv6
MLflow 5000 on 0.0.0.0 or public IPv6
Dash 8050 on 0.0.0.0 or public IPv6
Any unapproved application service on 0.0.0.0 or public IPv6
```

Also review:

```bash
sudo ss -tulpen
sudo ufw status verbose
```

Remember: UFW output alone is not enough to validate Docker exposure. The listening-address check is required.

---

## 17. Project directory and file permissions

Create a controlled project area:

```bash
sudo mkdir -p /srv/quant/dev
sudo chown -R deploy:deploy /srv/quant
sudo chmod 750 /srv/quant
```

Recommended layout:

```text
/srv/quant/
  dev/
    quant-research-platform/
  backups/
  secrets/
```

Create protected directories:

```bash
mkdir -p /srv/quant/backups /srv/quant/secrets
chmod 700 /srv/quant/secrets
chmod 700 /srv/quant/backups
```

Why `700` for backups: backups may contain Postgres dumps, MLflow artifacts, or `.env` snapshots. Default to owner-only access. Relax permissions only if a specific approved backup-pull pattern requires group access.

---

## 18. Secrets and `.env` protection

### 18.1 Required rules

- Never commit `.env`.
- Never paste real secrets into LLM chats.
- Never bake secrets into Docker images.
- Never print full credentials in logs.
- Never show secrets in the Dash UI.
- Back up the `.env` file securely outside Git.
- Rotate secrets after suspected compromise.

### 18.2 File permissions

Inside the repository directory, once `.env` exists:

```bash
chmod 600 .env
ls -l .env
```

Expected permission pattern:

```text
-rw-------
```

### 18.3 Keep an example file in Git

The repository should have:

```text
.env.example
```

The example file should contain placeholder names only, never real values.

---

## 19. VPS provider firewall / security group

If the VPS provider offers an external firewall or security group, use it as a second layer.

Recommended inbound provider firewall rule:

| Protocol | Port | Source |
|---|---:|---|
| TCP | 22 | Your IP address if stable; otherwise all IPv4/IPv6 with Fail2ban active |

If the VPS has a public IPv6 address, apply equivalent rules to IPv6. Do not assume IPv4-only firewall rules protect IPv6.

Do not open Postgres, MLflow, Dash, or application ports in the provider firewall during Phase 1.

Provider firewall is a second layer, not a replacement for:

1. safe Docker bindings;
2. UFW;
3. SSH key authentication;
4. no public app service exposure.

---

## 20. Backups as a security control

Backups protect against compromise, accidental deletion, bad migrations, failed upgrades, provider issues, and user mistakes.

At minimum, back up:

1. Postgres application database;
2. MLflow metadata database;
3. MLflow artifact volume;
4. `.env` file, stored securely outside Git;
5. key YAML config files if not already recoverable from Git;
6. Docker Compose deployment files once implementation begins.

### 20.1 Off-host backup requirement

Off-host backups are required before the platform stores meaningful research data, MLflow artifacts, or secrets.

An off-host backup is a copy stored outside the VPS itself, such as:

1. local computer storage;
2. Backblaze B2;
3. Cloudflare R2;
4. AWS S3;
5. another server;
6. another approved external backup destination.

Provider snapshots are useful but are not enough by themselves because they remain tied to the same provider account, provider infrastructure, and provider control panel.

### 20.2 Minimum backup baseline before serious use

Before serious use:

1. define the off-host backup destination;
2. define retention period;
3. perform one test restore;
4. document the restore command in a later backup runbook.

Suggested future runbook:

```text
docs/runbooks/vps_backup_restore.md
```

The detailed backup/restore procedure can be deferred to that future runbook, but the requirement belongs here.

---

## 21. Basic verification checklist

Run these after completing the baseline.

### 21.1 Identity and sudo

```bash
whoami
sudo whoami
```

Expected:

```text
deploy
root
```

### 21.2 SSH status

```bash
sudo sshd -t
sudo systemctl status ssh --no-pager
sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|kbdinteractiveauthentication|challengeresponseauthentication|pubkeyauthentication|allowusers'
```

Expected baseline:

```text
permitrootlogin no
passwordauthentication no
kbdinteractiveauthentication no
pubkeyauthentication yes
allowusers deploy
```

`challengeresponseauthentication no` may also appear depending on OpenSSH version.

### 21.3 Firewall status

```bash
sudo ufw status verbose
```

Expected:

```text
Status: active
Default: deny (incoming), allow (outgoing)
OpenSSH ALLOW
```

### 21.4 Fail2ban status

```bash
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

### 21.5 Automatic updates status

```bash
systemctl status unattended-upgrades --no-pager
cat /etc/apt/apt.conf.d/20auto-upgrades
```

### 21.6 Listening ports

Filtered check:

```bash
sudo ss -tulpen | grep -v 127.0.0.1 | grep -v '\[::1\]'
```

Passing condition:

```text
Only sshd should be listening on non-loopback addresses.
```

Full check:

```bash
sudo ss -tulpen
```

Expected public listening service: SSH only, unless a future approved exposure change exists.

### 21.7 Login history

```bash
last -a | head -20
```

Review for unknown source IPs.

### 21.8 Backup requirement check

Before serious use, verify:

```text
Off-host backup destination selected: yes/no
Latest Postgres backup exists off-host: yes/no
Latest MLflow artifact backup exists off-host: yes/no
Latest .env/secrets backup exists off-host and secured: yes/no
Restore test performed: yes/no
```

---

## 22. Recurring maintenance checklist

Run weekly during active development.

```bash
sudo ufw status verbose
sudo fail2ban-client status sshd
sudo apt update
apt list --upgradable
if [ -f /var/run/reboot-required ]; then cat /var/run/reboot-required; fi
sudo ss -tulpen | grep -v 127.0.0.1 | grep -v '\[::1\]'
docker ps
```

Weekly backup checks:

1. confirm the latest off-host backup timestamp is recent;
2. confirm the latest Postgres backup exists;
3. confirm the latest MLflow artifact backup exists;
4. confirm the latest secured `.env` / secrets backup exists;
5. investigate immediately if backups are missing or stale.

Run monthly:

```bash
sudo journalctl -p warning -n 200 --no-pager
last -a | head -50
sudo find /srv/quant -name ".env" -exec ls -l {} \;
```

Monthly backup discipline:

1. confirm backup retention is not growing without control;
2. confirm at least one restore test has been performed recently;
3. document restore-test result in the backup runbook once created.

---

## 23. Incident response basics

If you suspect the VPS is compromised:

1. Do not keep experimenting on the live server.
2. Use the provider console to take a snapshot if available.
3. Disconnect public access if needed through the provider firewall.
4. Rotate API keys, GitHub tokens, EODHD token, database passwords, and SSH keys.
5. Rebuild from a clean image if compromise is likely.
6. Restore only trusted database backups and known-good Git revisions.
7. Do not reuse the same `.env` values after a suspected compromise.

For Phase 1, a clean rebuild is usually safer than trying to surgically repair a compromised VPS.

---

## 24. Open questions

These do not block the v0.2 security baseline, but they should be resolved before the platform stores meaningful research data, MLflow artifacts, or secrets.

| ID | Open question | Current disposition |
|---|---|---|
| OQ-VPS-SEC-01 | What is the final off-host backup destination? | Open; likely Backblaze B2, Cloudflare R2, AWS S3, local encrypted backup, or another approved external destination. |
| OQ-VPS-SEC-02 | Should `/srv/quant` and `deploy` later be promoted from runbook defaults into a deployment spec? | Open; currently runbook-level operational defaults. |
| OQ-VPS-SEC-03 | Should a provider-specific firewall template be created after the VPS provider is selected? | Open; recommended after Hostinger / Contabo / other provider choice is final. |
| OQ-VPS-SEC-04 | Should a dedicated backup-and-restore runbook be created before first serious data accumulation? | Yes; recommended path is `docs/runbooks/vps_backup_restore.md`. |

---

## 25. Completion criteria

This security baseline is complete when all items are true:

- [ ] `deploy` or equivalent non-root sudo user exists.
- [ ] `deploy` has a strong sudo/console password stored in a password manager.
- [ ] SSH key login works for the non-root user.
- [ ] Sudo works for the non-root user.
- [ ] `/etc/ssh/sshd_config.d/*.conf` include behavior is verified.
- [ ] Root SSH login is disabled.
- [ ] Password SSH login is disabled.
- [ ] Keyboard-interactive / challenge-response authentication is disabled where supported.
- [ ] UFW is active.
- [ ] UFW denies incoming by default.
- [ ] UFW allows SSH.
- [ ] No app/database/MLflow/Dash ports are publicly exposed.
- [ ] Docker exposure rule is understood: loopback-only host bindings or internal Docker networking.
- [ ] Non-loopback listener check shows only SSH.
- [ ] Fail2ban is active for `sshd`.
- [ ] Journald persistence is checked for Fail2ban's systemd backend.
- [ ] Automatic security updates are enabled.
- [ ] Provider console or recovery access is verified.
- [ ] Provider firewall does not expose app/database/MLflow/Dash ports over IPv4 or IPv6.
- [ ] `.env` discipline is documented before secrets are created.
- [ ] Backup directory permissions default to owner-only.
- [ ] Off-host backup destination is selected before serious use.
- [ ] Backup/restore runbook is planned before serious data accumulation.

After this checklist is complete, continue with:

```text
docs/runbooks/vps_setup_procedure.md
```

---

## 26. Official references

Use official documentation where possible:

- Ubuntu UFW firewall documentation: https://ubuntu.com/server/docs/how-to/security/firewalls/
- Ubuntu automatic updates documentation: https://ubuntu.com/server/docs/how-to/software/automatic-updates/
- Ubuntu Fail2ban community documentation: https://help.ubuntu.com/community/Fail2ban
- Docker Linux post-installation documentation: https://docs.docker.com/engine/install/linux-postinstall/
- Docker rootless mode documentation: https://docs.docker.com/engine/security/rootless/

---

End of `docs/runbooks/vps_security_baseline.md` v0.2.1 DRAFT.
