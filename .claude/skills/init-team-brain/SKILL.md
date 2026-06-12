---
name: init-team-brain
description: Generate a product-knowledge layer (a "brain") for a team's codebase - glossary and object model mined from real code, rot-rate tiers, a claims-manifest drift checker that fails commits when docs disagree with code, an eval harness, and a weekly sync skill. Use when the user says "init team brain", "create a product brain", "set up drift-checked product docs", or wants onsa-brain-style product knowledge for their repos.
---

# /init-team-brain — Product Knowledge Layer Generator

Generate the product-knowledge layer on top of a team's code: the exact vocabulary, object model, and current state that agents must not invent — plus the machinery that keeps it from rotting.

The brain is also the **context layer for synthesis tasks**: point any meeting- or customer-interview summarizer at it. A summarizer that doesn't know your product, personas, and terminology produces inadequate summaries even from a perfect transcript — ground it in the glossary and overview first.

## Principles

1. **Only document what code can verify or humans have judged.** Generate the derivable layer (enums, components, vocabulary) from code; scaffold the judgment layer (pivots, gotchas, strategy) as explicit `TODO(owner)` markers. Never fabricate judgment.
2. **Enforcement must be seen failing before it is trusted.** The setup is not done until the user has watched the drift checker reject a synthetic drift in red.
3. **Tiers by rot-rate.** Every doc carries `tier: stable|evolving|volatile` and `last_reviewed`. Volatile docs older than 14 days must be discounted by agents reading them — write that rule into the entry file.
4. The brain stores permanent context, never active state: how to navigate to systems of record, not the values inside them. **The one declared exception is `now.md`** — a date-stamped volatile snapshot of current focus, refreshed weekly and staleness-discounted; it is a dated snapshot with a refresh contract, not live state.
5. **Descriptive one-liners are judgment too.** "OrderTable — component rendering orders" inferred from a name is fabrication unless the code or README says so. If a description isn't verifiable from source, write the verifiable part and mark the rest `TODO(owner)`.

## State Management

Create the brain repo directory first, then write progress to `.brain-setup/state.md` at its root after every phase (commit it with the repo — it documents provenance). On restart, resume from it.

## Phase 1 — Discover

- Locate the team's code repos (ask for paths or discover from the workspace; confirm the list).
- Inspect languages and conventions: enum-like constructs (TS `enum`, Python `Enum`, Go `const` blocks, string unions), exported component names, status/state fields.
- Mine vocabulary: recurring domain terms from code identifiers, README, and any provided evidence (chat exports, meeting notes).

## Phase 2 — Propose the Claim Set

Present candidate claims with provenance. Scale to the codebase: on small repos, propose every verifiable claim; on large ones, cap proposals around 20 — high-value claims beat noisy ones, and the user prunes. Claim types and their checker semantics:
- `enum-values` — the doc section documenting that symbol (not the whole doc) must contain every value the code defines
- `pointer-only` — the doc must reference the symbol AND its file path, and the symbol must still exist in source; member lists are deliberately not transcribed
- `symbol-exists` — the named component/file still exists in the codebase

```yaml
# claims.yaml — every entry is a promise the docs make about the code
- id: task-status-values
  doc: product/object-model.md
  type: enum-values        # doc must contain every value the code defines
  source: { repo: ../server, path: src/tasks/types.ts, symbol: TaskStatus }
- id: outreach-stage-pointer
  doc: product/object-model.md
  type: pointer-only       # doc references symbol+file, never transcribes members (use for high-churn enums)
  source: { repo: ../app, path: src/helpers/resolveProgress.ts, symbol: OutreachStage }
- id: lead-table-component
  doc: product/object-model.md
  type: symbol-exists      # named component/file still exists in the codebase
  source: { repo: ../app, symbol: LeadTableWidget }
```

## Phase 3 — Generate

Into a `*-brain` repo or `brain/` subtree. Every **markdown** file carries owner/tier/last_reviewed frontmatter; non-markdown artifacts (yaml, scripts, hooks, workflows) carry the same fields as a comment header instead:

- `AGENTS.md` — entry point: reading order, the staleness-discount rule, what this brain is and is not.
- `now.md` — "the one thing" + current focus (volatile; seeded from evidence, marked for weekly refresh).
- `product/glossary.md` — exact vocabulary; agents may not invent terms.
- `product/object-model.md` — entities and real enum states extracted from code.
- `claims.yaml` — the confirmed claim set.
- `scripts/check_drift.py` — the generated checker (always Python with stdlib only; a team wanting another language regenerates from the claims.yaml contract). Requirements:
  - exit 1 on any failed claim with a side-by-side "code says / doc says" listing
  - skip-with-notice (never fail) when a source repo isn't checked out, naming what it could not verify — and the summary line must say "skipped", never "verified", for skipped claims
  - catch code→doc additions (the silent-rot case); stale extras in docs are weekly-sweep territory, not failures
  - accept a `--source-root <dir>` override (or `DRIFT_SOURCE_ROOT` env var) remapping the claims' relative repo paths — this is what makes the red demo runnable against a scratch copy
- `.githooks/pre-commit` running the checker + a CI workflow for PR time. `git init` the brain repo (set user identity if unset), `chmod +x` the hook and checker, then wire with `git config core.hooksPath .githooks`.
- **Checker contract note** — one paragraph stating that `claims.yaml` is the contract and any agent may re-implement the checker in another language (claims schema + exit/skip semantics above are the whole spec). Lives in the `claims.yaml` comment header, referenced from `AGENTS.md`.
- `evals/knowledge-impact.md` — with/without harness: same task ± brain, n≥5, blind-ish judging. "If the brain stops winning the eval, the docs have rotted."
- `MAINTENANCE.md` — who reviews what, on what cadence; volatile docs refresh from the team's weekly meeting.
- `skills/update-knowledge/SKILL.md` — the weekly sync skill: read the week's reality (meeting notes, git history, team chat), update volatile docs, bump `last_reviewed`, open a PR for human review. Never push directly. If a `decisions.md` exists (see `/init-team-decisions`), the sync also runs a **decision-mining pass** (new episodes → `proposed` entries, same PR) and a **principles revisit** (propose retire/amend for principles the week contradicted; note confirmations — recurrence strengthens the lean; principles age in public, not silently).
- `skills/README.md` — the skill registry: one table (skill · for whom · what it does), install instructions (symlink so updates propagate), and — if a team agent consumes these skills — the **pointer-skill contract**: the agent's own skill registry holds thin pointers (trigger frontmatter + "read the canonical SKILL.md under the synced mount"), never copies; edits propagate on sync; the only manual step is updating a pointer's trigger metadata when a skill's scope changes.

Show the user each file's substance before writing.

## Phase 4 — Prove It

1. Run the checker: green on the real codebase.
2. **The red demo (checker)**: copy one source repo to a scratch directory, add a fake enum value there, run the checker with `--source-root` pointing at the scratch copy — show the user the red failure naming the exact claim. Delete the scratch copy.
3. **The red demo (hook)**: temporarily add the fake value to the REAL source repo (verify `git status` is clean for that file first), attempt `git commit --allow-empty -m drift-demo` in the brain repo — watch the hook block it — then restore the source file (`git checkout -- <file>`) and show a clean commit passing.
4. Only after both red demos: declare enforcement live.

## Phase 5 — Hand Off

Report: claims active, files generated, judgment TODOs awaiting owners, the weekly cadence, and the eval as the standing health check. Point to `/init-team-decisions` when "how do we decide X" questions recur, and to `/robin-init` when the team wants the brain to answer questions in chat.
