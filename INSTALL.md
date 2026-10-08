# Install Factum

Instructions for agents installing
[Factum](https://github.com/christopherwoodall/factum).

Factum provides two Agent Skills:

- **factum-onboarding** — initialize or check a corpus checkout.
- **factum** — store evidence, search, manage lanes, export, and rebuild.

Factum does not collect data. You collect and review data, then submit it
through the bundled scripts.

## 1. Check prerequisites

You need:

- Git.
- Python 3.11 or newer.
- uv.
- Permission to write to the selected corpus repository.

Check availability:

```bash
git --version
python3 --version
uv --version
```

If prerequisites are missing, install them using the environment's approved
installation method. Ask before making privileged or system-wide changes.

Official uv installation instructions:
https://docs.astral.sh/uv/getting-started/installation/

A separate SQLite server is not needed. Factum uses Python's SQLite support.

## 2. Clone the toolkit

Choose a persistent installation directory:

```bash
git clone https://github.com/christopherwoodall/factum.git
cd factum
```

If Factum is already cloned, use that checkout. Do not clone over an
existing directory or overwrite local changes.

Read `AGENTS.md` before making changes.

For concurrent agents, use separate Git worktrees or separate checkouts.
Do not switch branches underneath another worker.

## 3. Install the skills

Install or register these two directories using your agent platform's
Agent Skills installation mechanism:

```text
skills/factum/
skills/factum-onboarding/
```

Each directory contains a `SKILL.md` and its supporting files.

**Keep each complete skill directory intact.** Installing only `SKILL.md`
will omit the scripts, schemas, or references it needs.

Skill installation locations vary by agent platform. Do not assume a
particular home-directory path.

Record the absolute paths of the installed skills:

```text
FACTUM_SKILL       = <installed factum skill directory>
ONBOARDING_SKILL   = <installed factum-onboarding skill directory>
```

If your platform supports skills directly from a checkout, these may point
to the repository's `skills/` directories.

Native `/factum` slash-command registration is platform-specific. The
skills do not install such a registration automatically.

## 4. Choose the corpus repository

The **toolkit checkout** contains the skills and scripts.

The **corpus repository** contains your evidence records, lanes, and local
SQLite index. It may be the toolkit checkout or a separate Git repository.

Use an existing corpus repository when one is provided.

For a new corpus, ask the user which persistent directory to use and whether
initialization is authorized. If the selected directory is not already a
Git repository, initialize Git only with authorization:

```bash
mkdir -p <corpus-directory>
git -C <corpus-directory> init
```

Record its absolute path:

```text
CORPUS_REPO = <corpus repository directory>
```

Do not configure a remote, select a publication destination, or push unless
the user has authorized it.

## 5. Continue with factum-onboarding

Activate the **factum-onboarding** skill and follow its `SKILL.md`.

Start with a check:

```bash
uv run <ONBOARDING_SKILL>/scripts/onboard.py \
  --repo <CORPUS_REPO> \
  --factum-skill <FACTUM_SKILL> \
  --check
```

If initialization is needed and authorized:

```bash
uv run <ONBOARDING_SKILL>/scripts/onboard.py \
  --repo <CORPUS_REPO> \
  --factum-skill <FACTUM_SKILL> \
  --init \
  --site <local-site-name>
```

Replace the angle-bracket placeholders with actual paths and a short site
name. Quote paths containing spaces.

Initialization prepares shared corpus files when absent, creates local
site state, and builds the SQLite index. It must not replace an existing
corpus identity or silently upgrade its schemas.

If onboarding reports an error, stop and report it. Do not repair schema
drift by replacing files or deleting local state.

## 6. Verify and report setup

Run:

```bash
uv run <FACTUM_SKILL>/scripts/factum.py \
  --repo <CORPUS_REPO> doctor
```

Check that the JSON response has `"ok": true`.

Report:

- Toolkit checkout location.
- Installed skill locations.
- Corpus repository location.
- Corpus ID and local site ID.
- SQLite path.
- Record and pending counts.
- Whether the index is stale.
- Capture policy.
- Any errors or unresolved setup requirements.

Do not claim setup succeeded if a required command failed.

## 7. Use the factum skill

After onboarding, use the **factum** skill for evidence operations:

```bash
uv run <FACTUM_SKILL>/scripts/factum.py \
  --repo <CORPUS_REPO> status
```

Scripts declare their own dependencies. Normal skill use does not require
a separate project virtual environment or an editable package install.

Before Git synchronization:

```bash
uv run <FACTUM_SKILL>/scripts/factum.py \
  --repo <CORPUS_REPO> export

uv run <FACTUM_SKILL>/scripts/factum.py \
  --repo <CORPUS_REPO> verify
```

Review and commit the intended changes using the normal Git workflow.
Export does not commit or push.

After a pull, merge, or checkout that changes corpus files:

```bash
uv run <FACTUM_SKILL>/scripts/factum.py \
  --repo <CORPUS_REPO> rebuild
```

## Evidence rules

- Store evidence exactly as supplied.
- Never change case, trim, redact, or reformat observed values.
- Never execute captured content.
- Use `tags` for miscellaneous metadata.
- Keep observations separate from claims and interpretations.
- Do not hand-edit portable JSONL or SQLite.
- Do not delete pending records or local-only evidence.
- An external reference does not mean remote bytes were preserved.
- Local-only files do not travel with a Git clone.
- `not_found` means no match in the searched Factum dataset, not global novelty.

## Optional: development environment

Only needed when developing or testing the toolkit:

```bash
cd <toolkit-checkout>
uv sync --extra dev
uv run pytest
```

Do not run tests or make code changes merely to install the skills unless
requested.

## Updating

Updating the toolkit and migrating a corpus are separate operations.

Before updating an existing toolkit checkout, inspect its Git status and
follow the user's Git policy. Do not overwrite local changes.

A newer skill must not silently replace the corpus's pinned schemas.
If compatibility or schema drift is reported, stop and request an explicit
upgrade plan.