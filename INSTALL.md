# Install and update Factum

This document is for agents or operators setting up Factum in a host repository.

It covers:

1. Installing the skill.
2. Initializing or checking a corpus.
3. Updating installed skill code.
4. Installing additive schema packs.
5. Safely handling schema changes.

For everyday evidence work, read [SKILL.md](SKILL.md).

For pack design and tests, read [ARCHITECTURE.md](ARCHITECTURE.md).

## Scope and authorization

Factum stores data. It does not acquire sources or perform Git operations.

Do not interpret installation as permission to:

- start crawling;
- submit findings externally;
- publish evidence;
- change repository branch policy;
- migrate an existing corpus;
- replace installed schemas;
- delete pending work.

Follow the user's authorization and host-repository rules.

## Requirements

- Git
- uv
- Python 3.11 or later
- Python's SQLite build with FTS5 and its trigram tokenizer
- A host Git repository

The public script declares its Python dependencies through inline uv metadata.
A manually managed virtual environment is not required.

uv may need network access to obtain Python or dependencies, depending on the
local environment. Use the environment's approved installation procedure.

## 1. Choose the host repository

The host repository is where evidence belongs.

```text
host-repository/
├── .agents/skills/factum/
└── data/
```

The installed Factum clone is not the corpus.

The examples below use `.agents/skills/factum/`. Use the skills directory
recognized by the agent platform if it differs.

## 2. Install the skill

### Option A: local nested clone

From the host repository root:

```bash
git clone https://github.com/christopherwoodall/factum.git \
  .agents/skills/factum
```

Keep this nested clone out of accidental host commits.

For a local-only installation, add this line to the host repository's local
Git exclude file:

```text
/.agents/skills/factum/
```

Locate that file from the host repository:

```bash
git rev-parse --git-path info/exclude
```

Append the line without overwriting existing contents. Adjust the path if the
skill was installed elsewhere.

### Option B: shared, pinned submodule

Use this instead of the plain-clone command:

```bash
git submodule add https://github.com/christopherwoodall/factum.git \
  .agents/skills/factum
```

This lets the host repository track an approved Factum revision.

Choose one method. Do not create a nested clone and then accidentally stage
it as an unmanaged embedded repository.

## 3. Check whether a corpus already exists

From the host repository root:

```bash
uv run .agents/skills/factum/scripts/factum.py status
```

For explicit path resolution:

```bash
uv run /path/to/factum/scripts/factum.py \
  --repo /path/to/host-repository \
  status
```

`FACTUM_REPO` can also identify the host repository.

Place global options such as `--repo` and `--at` before the command.

## 4. Initialize or rebuild

### New corpus

When authorized:

```bash
uv run .agents/skills/factum/scripts/factum.py init
```

Initialization:

- creates the corpus identity;
- copies seed packs into the host repository;
- writes the schema lock;
- creates local site metadata;
- adds scoped ignore and artifact-preservation attributes;
- builds SQLite;
- leaves unrelated files and legacy directories alone.

It does not commit, push, fetch, install hooks, or import old datasets.

### Existing compatible corpus

Do not replace its packs with the latest seed files.

Check and rebuild:

```bash
uv run .agents/skills/factum/scripts/factum.py verify
uv run .agents/skills/factum/scripts/factum.py rebuild
uv run .agents/skills/factum/scripts/factum.py doctor
```

### Existing incompatible corpus

The current implementation uses portable format `2`.

Format `1` is not automatically migrated. Stop and report the incompatibility.
Do not edit `corpus.json` merely to change its version number.

A reviewed migration is separate development work.

## 5. Review initial setup

Normally, initial host changes include:

```text
.gitignore
.gitattributes
data/corpus.json
data/schema-lock.json
data/schema-packs/
```

Do not commit `data/.local/`.

Inspect `doctor` output:

- repository path;
- format and toolkit versions;
- record and lane counts;
- pending count;
- index staleness;
- database location.

SQLite capability is exercised during rebuild. If FTS5 or trigram support is
missing, use a compatible Python/SQLite distribution.

## 6. Onboard the working agent

Read [SKILL.md](SKILL.md).

The agent should then:

1. Run `status`.
2. Rebuild if stale.
3. Select or create a lane.
4. Inspect the applicable schema assignment.
5. Collect evidence using its own tools.
6. Submit files or bundles.
7. Search the actual Factum corpus before making novelty claims.
8. Keep interpretations separate from observations.
9. Export and verify before Git synchronization.

Raw files do not need to be opened simply because Factum has been installed.

## Updating the skill code

Skill code and corpus schemas have separate lifecycles.

### Before updating

- Identify the installed revision.
- Check for local modifications to the installed skill.
- Check corpus status.
- Export pending records when practical.
- Preserve pending work and local-only evidence.
- Review release notes or the proposed code diff.

Do not overwrite a modified skill checkout.

### Apply the approved code update

For a plain clone, update the installed Factum Git repository using the
approved revision and normal Git workflow.

For a submodule, update its pinned revision through the host repository's
approved workflow.

There is no `factum update` command.

### After updating

```bash
uv run .agents/skills/factum/scripts/factum.py verify
uv run .agents/skills/factum/scripts/factum.py rebuild
uv run .agents/skills/factum/scripts/factum.py doctor
```

A toolkit update must not silently replace:

```text
data/schema-packs/
data/schema-lock.json
```

Stop on incompatibility instead of copying new assets over old schemas.

## Installing a new schema pack

### What an agent may extend

Schema packs may add:

- observable types;
- observation payload schemas;
- event payload schemas;
- predicates.

They cannot add arbitrary Python execution, storage providers, or new core
record kinds.

Use `tags` for one-off metadata. Do not create a schema pack for every
temporary annotation.

### Step 1: inspect existing assignments

```bash
uv run .agents/skills/factum/scripts/factum.py schema list
```

For a specific type:

```bash
uv run .agents/skills/factum/scripts/factum.py \
  schema assigned observation web.capture
```

Inspect the returned schema ID:

```bash
uv run .agents/skills/factum/scripts/factum.py \
  schema describe urn:factum:web:web-capture:1
```

Prefer an existing suitable type over a duplicate.

### Step 2: obtain or author a candidate pack

Develop the candidate outside installed pack directories:

```text
schema-proposals/
└── research-webhooks/
    └── 1.0.0/
        ├── pack.json
        ├── definitions.json
        └── schemas/
            └── webhook-capture.schema.json
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the manifest and definition contracts.

The agent handles obtaining the pack. Factum does not download packs.

Review unfamiliar packs before activation. Data-only packs still influence
validation, matching, and reference interpretation.

### Step 3: preview installation

```bash
uv run .agents/skills/factum/scripts/factum.py \
  schema install ./schema-proposals/research-webhooks/1.0.0
```

Without `--approve`, the command validates the proposed combined catalog but
does not activate it.

It checks:

- pack structure and file inventory;
- exact dependency versions;
- JSON Schema validity;
- local reference resolution;
- duplicate schema IDs;
- duplicate type assignments;
- supported Factum reference annotations.

This is not a substitute for testing real example bundles.

### Step 4: test in a disposable repository

Before installing a nontrivial pack into an important corpus:

1. Initialize a disposable host repository.
2. Install required dependency packs.
3. Install the candidate.
4. Submit positive example bundles.
5. Confirm malformed bundles fail.
6. Export, verify, and rebuild.
7. Retrieve records and check their schema assignments.

Never use the production corpus as the only pack test environment.

### Step 5: activate when authorized

```bash
uv run .agents/skills/factum/scripts/factum.py \
  schema install ./schema-proposals/research-webhooks/1.0.0 --approve
```

Activation copies the pack, updates the lock, and rebuilds the index.

### Step 6: verify and review

```bash
uv run .agents/skills/factum/scripts/factum.py verify

uv run .agents/skills/factum/scripts/factum.py \
  schema assigned observation research.webhook_capture
```

Review and commit together:

```text
data/schema-packs/<pack-name>/<version>/
data/schema-lock.json
```

Commit dependent records with their required packs. Other sites need both.

## Updating schemas and packs

### Uninstalled draft

Edit freely while it remains a proposal. Revalidate and retest.

### Installed pack version

Do not edit it in place.

The lock pins its file contents. Modification produces schema drift.

### Additive extension

Create a pack containing only new schema IDs and new type names.

The current installer does not replace installed packs. Multiple versions
can remain installed, but duplicate definitions are rejected even when
their contents are identical.

Therefore, copying an entire installed pack, changing its version, and
reinstalling it usually fails because it repeats existing schema IDs and
type names.

A simple supported pattern is a new extension pack:

```text
research-webhooks-extra/1.0.0/
```

It can depend on:

```json
{
  "research-webhooks": "1.0.0"
}
```

It must declare only its additions.

### Breaking change to a type

Use a new schema ID and logical type name, for example:

```text
Schema ID: urn:research:webhooks:capture:2
Type name: research.webhook_capture.v2
```

New records use the new type. Old records retain their original assignment.

There is no in-place type reassignment command.

### Core schema or record migration

Stop and request explicit development authorization.

Do not:

- edit locked core schemas;
- rewrite old records to make them validate;
- recompute hashes to conceal a changed history;
- remove old packs still needed by records.

## Recovery

### `INDEX_STALE` or `INDEX_MISSING`

Run `rebuild`.

### Schema drift

Restore the intended pack bytes and corresponding lock from an approved Git
state. Do not regenerate hashes just to accept an unexplained change.

### Interrupted pack installation

The lock is the activation point.

A copied but unlocked pack directory is inactive. Retry installation from the
same unchanged candidate.

If the directory differs, stop and inspect it.

### Pack activated but rebuild failed

Inspect the error and retry `rebuild` after correcting the underlying problem.

Do not assume that an error means the pack was not activated.

### Missing artifact bytes

A metadata-only clone may not contain another site's local-only bytes.

Report the limitation. Do not silently fetch a live replacement and present
it as the original capture.

### Removing or reinstalling the skill

Preserve the host `data/` directory.

In particular, preserve pending submissions and local-only bytes. They may
not exist in Git.


---

## Register Factum in the host repository's agent instructions

After successful setup, make Factum discoverable to future agents by adding
a short integration block to the host repository's root `AGENTS.md`.

This is an agent-managed documentation step. The current `init` command does
not modify `AGENTS.md`.

### Scope

Update the host repository's instructions, not the development `AGENTS.md`
inside the installed Factum clone.

Use the instruction filename recognized by the host platform. Prefer
`AGENTS.md` when that is the repository convention.

If the repository uses `AGENT.md` instead, confirm that the platform reads it.
Do not create competing instruction files without a reason.

### Procedure

1. Read the existing host instructions.
2. Check for an existing `FACTUM INTEGRATION` marker block.
3. Add the block once, or update that existing block.
4. Substitute the actual repository-relative skill path.
5. Preserve all unrelated instructions.
6. Identify conflicting storage instructions.
7. Update those conflicts when authorized, or report them before using Factum
   as the required storage path.
8. Review the diff. Do not commit or push automatically.

A bottom-of-file block does not safely resolve contradictory earlier
instructions.

For example, if an earlier section directs agents to hand-write every new
observation into legacy `events.jsonl`, clarify that:

- historical files retain their existing schemas;
- new structured records go through Factum;
- compatibility exports require an explicit adapter;
- agents must not manually maintain two authoritative copies.

Preserve existing acquisition, publication, retention, and branch policies.

### Suggested integration block

Adjust `.agents/skills/factum/` if the skill is installed elsewhere.

```markdown
<!-- BEGIN FACTUM INTEGRATION -->
## Factum evidence storage

Use Factum for new structured evidence, provenance, claims, and relationships.

- Read `.agents/skills/factum/SKILL.md` before evidence-storage work.
- Follow `.agents/skills/factum/INSTALL.md` for setup and schema-pack changes.
- The host repository owns the corpus under `data/`.
- Run:
  `uv run .agents/skills/factum/scripts/factum.py --repo <host-repository> <command>`

Start with `status`. Use Factum scripts rather than editing managed JSONL,
manifests, SQLite, or installed schema packs directly.

Preserve exact evidence. Use `tags` for miscellaneous metadata. Install new
schema packs only through the documented, authorized workflow.

Export and verify before Git synchronization. Verify and rebuild after corpus
changes from Git. Never discard pending submissions.

Existing evidence and reports remain in place. Factum does not automatically
import or search legacy files. A Factum no-match result is not global novelty.

Repository rules for acquisition, review, retention, publication, and Git
operations remain authoritative.
<!-- END FACTUM INTEGRATION -->
```

### Existing or nested instructions

Check whether more-specific agent instructions apply in the directories where
the agent will work.

Do not silently overwrite those files. Report or reconcile conflicting
storage guidance when authorized.

### Completion report

Report:

- which host instruction file was updated;
- the installed skill path;
- whether an existing block was updated or a new one was added;
- any conflicting instructions that remain;
- whether legacy material is still outside Factum's indexed scope.