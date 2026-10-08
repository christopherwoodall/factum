# Factum

**Schema-driven evidence storage for research agents.**

Factum preserves what agents find, connects it through an evidence graph,
and makes it searchable through a local SQLite index. Portable JSONL
records synchronize through Git.

**Collect elsewhere. Store exactly. Search locally. Share through Git.**

## What Factum provides

- **Agent Skills** for onboarding and everyday use.
- **Strict JSON Schemas** for observations, observables, claims, and relationships.
- **Exact evidence preservation** without changing case, whitespace, or file bytes.
- **Provenance** connecting observations, artifacts, sightings, and interpretations.
- **Flexible work lanes** with editable READMEs and research writeups.
- **Local matching** using exact values, derived comparison keys, and optional fuzzy search.
- **Portable records** that can rebuild a local SQLite index.
- **Scripts runnable through uv** so agents do not need to write SQL or construct ledger files.

Factum is not a crawler, scraper, agent runtime, or hosted backend service.
Agents handle collection, external research, review, and normal Git operations.

## Install

Start with **[INSTALL.md](INSTALL.md)**, then use the
**[factum-onboarding skill](skills/factum-onboarding/SKILL.md)**.

Requirements:

- Python 3.11 or newer.
- uv.
- Git.

No database server is required.

Install both complete skill directories using your agent platform's skill
installation mechanism:

```text
skills/factum/
skills/factum-onboarding/
```

The toolkit and corpus can live in the same repository or in separate
repositories.

## Quick start

The examples below assume commands run from the Factum toolkit checkout.
Replace `<corpus-repository>` with the repository where your evidence belongs.

### Initialize a corpus

For authorized initialization:

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  init --site worker-a
```

For an existing corpus, this prepares missing local state without replacing
its shared identity or pinned schemas.

### Store an already-collected file

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  capture \
  --url 'https://Example.org/Page' \
  --file ./captures/page.html \
  --storage local \
  --tags '{"purpose":"infrastructure follow-up"}'
```

**This command does not download the URL.** It records the supplied source
information and copies the supplied file unchanged.

Use `--storage git` when you intend to include those bytes in Git.

### Record an external dataset reference

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  reference \
  --uri 'https://huggingface.co/datasets/example/dataset' \
  --revision '<pinned-revision>'
```

A reference records where material can be found. It does not claim that
remote bytes were preserved.

### Search the local corpus

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  match --url 'https://Example.org/Page'
```

For an observable:

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  match --value 'Example.COM' --type domain --mode exact
```

Successful searches return `not_found` or a list of matches. Errors and
incomplete searches are reported separately.

**`not_found` means no match in the searched Factum dataset—not global
novelty or originality.**

## How it works

```text
Agent collects and reviews data
              │
              ▼
       Factum scripts
              │
       Validate shapes
       Preserve exact values
       Store supplied bytes
              │
              ▼
     Durable pending records
              │
              ├──────────► SQLite index
              │
            export
              │
              ▼
       Portable JSONL batches
              │
       Agent commits and pushes
              │
              ▼
       Other sites pull and rebuild
```

### Storage authority

| Layer | Purpose |
|---|---|
| Portable records | Shared evidence and assertion records |
| Pending records | Durable, locally accepted work not yet exported |
| SQLite | Rebuildable local search and relationship index |
| Artifact files | Exact captured bytes, retained locally or in Git |
| Lane documents | Editable research context and writeups |

Export makes pending records portable in the working tree. It does not
commit or push them.

## Evidence model

Factum separates what was found from what an agent thinks it means.

| Shape | Meaning |
|---|---|
| `source` | Website, dataset, document, or external-system origin |
| `artifact` | Captured bytes or an explicit external reference |
| `observation` | What was encountered or submitted, when, and how |
| `observable` | An exact typed value, such as a URL, domain, hash, or term |
| `sighting` | Where an observable appeared in an observation |
| `event` | A proposed event anchor supported by citations |
| `claim` | An assertion about a subject |
| `edge` | A registered relationship between nodes |
| `assessment` | A scoped interpretation or matching assessment |
| `run` | Method and execution context |
| `annotation` | Metadata attached to an existing identity |
| `retraction` | An explicit withdrawal that preserves history |
| `lane` | An editable work context with documents and metadata |

Claims are graded:

- **OBSERVED** — grounded in what was directly recorded.
- **UPSTREAM** — an assertion made by a source.
- **INFERENCE** — an analyst or agent interpretation.

These grades describe the assertion's basis. They do not automatically
establish truth.

### Exact values and derived search keys

An observable such as `Example.COM` remains `Example.COM`.

Factum may derive `example.com` for comparison, but the derived value never
replaces the evidence.

Malformed URLs and other imperfect source values can still be stored.
Parsing problems belong in derived indexing warnings.

### Tags

Every record has a `tags` object for miscellaneous JSON metadata:

```json
{
  "tags": {
    "purpose": "follow-up",
    "review": {
      "state": "unreviewed"
    }
  }
}
```

Tags do not define graph references or change evidence identity.

Shared deterministic identities use empty tags in their identity records.
Submitted metadata becomes a separate annotation, preventing two agents
tagging the same value differently from creating false merge conflicts.

## Structured submissions

Use a bundle when submitting related observations, sightings, claims, or
relationships.

Get an example:

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  template
```

Submit a completed bundle:

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  add --input ./bundle.json
```

Bundles use short local refs for new items. Scripts assign record IDs,
hash supplied files, resolve declared reference fields, and validate the
result.

Strings inside raw values, quotes, claim values, and tags are not rewritten
during reference resolution.

See **[submission shapes](skills/factum/references/shapes.md)**.

## Work lanes

A lane can represent an investigation, a follow-up, a scan, or any other
period or thread of work.

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  lane new 'Infrastructure follow-up' \
  --date 2026-10-08 \
  --kind investigation
```

Link existing evidence:

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  lane link <lane-id> <record-id>
```

Lane membership is stored through relationships. Evidence can belong to
multiple lanes.

READMEs, findings, and methodology documents remain ordinary editable
Markdown files.

## Git workflow

### Before synchronization

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> export

uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> verify
```

Then:

1. Review the intended changes.
2. Commit according to your repository's policy.
3. Push only when authorized.

Export creates new sealed batches rather than rewriting a shared JSONL file.

### After pull, merge, or checkout

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> rebuild
```

Normal rebuilds include pending records. They must not silently discard
unexported work.

Use separate worktrees or checkouts for concurrent agents.

### Historical rebuild

```bash
uv run skills/factum/scripts/factum.py \
  --repo <corpus-repository> \
  rebuild --at HEAD~1
```

This reads the selected Git tree without changing the checkout and writes a
separate historical database. It does not replace the active writable index.

## Artifact retention

| Mode | What travels through Git |
|---|---|
| `git` | Captured bytes and portable metadata |
| `local` | Portable metadata; bytes remain on the collecting site |
| Reference | External URI and optional revision; no captured bytes implied |

The default is local storage.

Raw Git-retained files use binary Git attributes to prevent line-ending
conversion.

**Local-only evidence does not appear in another clone.** Keep its local
storage or arrange a separate backup when those bytes matter.

## Repository layout

```text
.
├── INSTALL.md
├── AGENTS.md
├── pyproject.toml
├── skills/
│   ├── factum/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── assets/
│   │   └── references/
│   └── factum-onboarding/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
├── tools/
│   └── register_schema.py
└── tests/
```

Onboarding creates this layout in the selected corpus:

```text
data/
├── corpus.json
├── schema-lock.json
├── capture-policy.json
├── schemas/
├── registry.json
├── extensions/
├── records/
├── lanes/
├── blobs/
└── .local/           # Ignored by Git
    ├── factum.db
    ├── site.json
    ├── pending/
    ├── blobs/
    └── snapshots/
```

Corpus schemas are pinned independently of the installed skill.
Updating the toolkit must not silently change how existing records validate.

## Agent commands

The factum skill can interpret requests such as:

```text
/factum status
/factum match <URL or value>
/factum capture <URL> <file>
/factum add <bundle>
/factum lane new <title>
/factum query <question>
/factum export
/factum rebuild
```

Native slash-command registration depends on the agent platform. It is not
installed automatically by the Agent Skills specification.

See **[command reference](skills/factum/references/commands.md)**.

<details>
<summary><strong>Schema extensions</strong></summary>

Use `tags` for exploratory metadata.

Use a registered type or extension schema for reusable structured data.
Operator-approved additions are handled by `tools/register_schema.py`.

Core identity, envelope, time, or reference changes require an explicit
versioned migration design. The toolkit does not silently rewrite old
evidence.

See **[schema extension guidance](skills/factum/references/schema-extension.md)**.

</details>

<details>
<summary><strong>Development</strong></summary>

Read **[AGENTS.md](AGENTS.md)** before contributing.

For local development:

```bash
uv sync --extra dev
uv run pytest
```

Public scripts use inline dependency metadata and remain runnable through
`uv run`.

Tests should cover exact evidence preservation, idempotency, pending
recovery, export/rebuild round trips, schema integrity, graph references,
and multi-site synchronization.

Only report tests as passing when they were actually run successfully.

</details>

<details>
<summary><strong>Current boundaries</strong></summary>

The initial toolkit intentionally excludes:

- External fetching and novelty searches.
- Automatic Git commits, pushes, or hooks.
- Hosted APIs and MCP servers.
- Embedding services and vector databases.
- Core schema migrations.
- Git history compaction.
- Globally coordinated offline idempotency.

Extraction operates on stored UTF-8 artifacts using registered regexes.
It does not perform OCR, unpack archives, or interpret browser captures.

Fuzzy search uses a bounded candidate set. Exhausted coverage must not
produce an authoritative `not_found`.

The initial implementation rebuilds SQLite during ingestion. Incremental
indexing is a future performance improvement if corpus size requires it.

</details>

## Core principle

> Preserve the evidence. Keep interpretation separate. Make the record
> portable and the index rebuildable.