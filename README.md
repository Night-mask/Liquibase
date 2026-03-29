# SQL → Liquibase Changelog Automation

Two chained GitHub Actions workflows that automatically convert SQL files into Liquibase XML changelogs and apply them to a database — with zero manual steps.

## Pipeline Overview

```
push / pull_request / workflow_dispatch
            │
            ▼
┌────────────────────────────┐
│   automation.yml           │
│   SQL to changelog         │
│   CONVERTER via python     │
│                            │
│  1. Detect changed .sql    │
│  2. Run SCRIPT.py per file │
│  3. Commit & push XMLs     │
└────────────┬───────────────┘
             │  on: workflow_run (completed + success)
             ▼
┌────────────────────────────┐
│   Liquibase.yml            │
│   Liquibase updation       │
│   on master xml            │
│                            │
│  1. Setup Java 17          │
│  2. Install Liquibase 5.0  │
│  3. liquibase update       │
└────────────────────────────┘
```

---

## Workflow 1 — `automation.yml`: SQL to Changelog Converter

### Triggers
- Push to `main`
- Pull request targeting `main`
- Manual trigger via `workflow_dispatch`

### What It Does

| Step | Description |
|---|---|
| Checkout | Full history checkout (`fetch-depth: 0`) required for `git diff` |
| Detect SQL files | Diffs `before..after` SHA to find changed `.sql` files; on first push, lists all `.sql` files |
| Generate changelogs | Runs `python3 SCRIPT.py <file.sql>` for each changed SQL file |
| Commit & push | Stages `changelog/child/*.xml` and auto-commits; skips if last commit was already by `github-actions` to prevent infinite loops |

### Loop-prevention
If the last git commit author is `github-actions`, the commit step exits early — preventing the auto-commit from re-triggering the workflow indefinitely.

---

## Workflow 2 — `Liquibase.yml`: Database Update

### Trigger
Runs automatically after `automation.yml` completes **successfully** (`workflow_run` event).

### What It Does

| Step | Description |
|---|---|
| Checkout | Checks out the exact commit that triggered the upstream workflow |
| Setup Java 17 | Uses Temurin distribution |
| Install Liquibase | Installs Liquibase OSS `v5.0.0` via `liquibase/setup-liquibase@v2` |
| Run update | Executes `liquibase update` against `changelog/master.xml` |

---

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       ├── automation.yml
│       └── Liquibase.yml
├── changelog/
│   ├── master.xml          ← root changelog (referenced by Liquibase)
│   └── child/
│       └── *.xml           ← auto-generated per SQL file
├── SCRIPT.py               ← converts a .sql file → Liquibase XML changeset
└── *.sql                   ← your SQL migration files
```

---

## Setup

### 1. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|---|---|
| `DB_URL` | JDBC connection URL for your database (e.g. `jdbc:postgresql://host:5432/db`) |
| `DB_USERNAME` | Database username |
| `DB_PASSWORD` | Database password |

> `GITHUB_TOKEN` is provided automatically by GitHub — no manual secret needed for the git push in `automation.yml`.

### 2. Ensure `SCRIPT.py` exists at the repo root

`SCRIPT.py` must accept a `.sql` filepath as its first argument and produce a corresponding XML changeset file under `changelog/child/`.

Example signature:
```python
# SCRIPT.py
import sys

sql_file = sys.argv[1]
# ... parse SQL and write changelog/child/<name>.xml
```

### 3. Ensure `changelog/master.xml` includes child changelogs

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                   http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.0.xsd">

    <includeAll path="child/" relativeToChangelogFile="true"/>

</databaseChangeLog>
```

---

## Permissions

| Workflow | Permission | Reason |
|---|---|---|
| `automation.yml` | `contents: write` | Required to push auto-generated changelog XML files |
| `Liquibase.yml` | `contents: read`, `id-token: write` | Read repo; `id-token` reserved for OIDC if cloud auth is added |

---

## Notes

- Only `.sql` files changed in the push are processed — unchanged files are skipped.
- The Liquibase job is **skipped** if `automation.yml` fails or is cancelled.
- Liquibase OSS `v5.0.0` is used; update the version in `Liquibase.yml` to upgrade.
- `SCRIPT.py` is the only component not provided by this repository — it must be authored to match your SQL conventions and changelog format.
