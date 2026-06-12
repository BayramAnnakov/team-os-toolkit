---
name: robin-init
description: Configure a personalized Robin (AI chief of staff) spec for any team. Reads the user's TeamOS knowledge repo, mines MCP config and installed runtimes to resolve ROBIN-SPEC's implementation-defined slots, drafts the team's soul.md and duty roster into their repo, and emits ROBIN-SPEC.local.md plus a KICKOFF.md prompt for any coding agent to implement Robin on the user's stack. Use when the user says "robin init", "configure my robin spec", "set up a team agent spec", "set up a chief of staff agent", or wants to start implementing a Robin-style team agent.
---

# /robin-init — Robin Spec Configurator

Configure, don't implement. This skill resolves ROBIN-SPEC's implementation-defined slots for one team and hands their coding agent a ready-to-run kickoff. It never writes Robin code — the spec governs the running process; this skill only produces files.

## Preconditions

1. Locate the upstream spec: `ROBIN-SPEC.md` in the current directory or a user-supplied path; if neither exists, ask for it (one question, doesn't count against the budget) — do not proceed without a spec. Record its version: git commit if the spec lives in a git repo, otherwise its `Status:` line + sha256 of the file. Either way the local copy must be diffable against future spec patches.
2. Locate the team's knowledge repo (TeamOS): the current working directory or its immediate parent — do not search the whole disk. **If none found, stop politely:** "Robin without a knowledge repo is just a bot — run /init-team-os first." This ordering is the product working as designed, not a limitation.

## Phase 1 — Mine Before Asking

Never ask what you can mine; detect presence only — never read secret values.

- **Chat platform**: MCP config and installed bots (telegram MCP → Telegram; Slack MCP → Slack; Discord tooling → Discord).
- **Agent runtime**: installed CLIs and SDKs (`claude` CLI, Agent SDK dependencies, other coding-agent CLIs).
- **Read-only data sources**: MCP servers + pointers inside the TeamOS repo (DB references, analytics, trackers).
- **Meeting layer (optional slots)**: calendar tools, meeting-recorder/notetaker MCPs, or transcript stores → evidence for the spec's optional meeting-presence slots. Absent any such evidence, mark those slots "deferred — no meeting capture detected" rather than asking about them.
- **Team context**: repo entry file, identity/soul material, glossary, the team's recurring question (from the repo or `.team-os-setup/state.md` if present).
- **Tunables**: take the spec's stated defaults where they exist (staleness budget 14d, DM idle 60min); where the spec gives only a reference value or no value (ambient N, digest cadence + destination), PROPOSE one and mark it as the configurator's proposal, not a spec default. The override moment is the Phase 2 slot-table confirmation — say so when presenting it.
- **Slot set**: resolve against the spec's "Implementation-Defined Slot Registry" appendix — that list IS the completeness criterion. "Resolved" includes "explicitly deferred to the implementing agent with a documented default." Every registry entry must appear in the local spec one way or the other.

## Phase 2 — Resolve Slots

Present the slot table with provenance per row ("Telegram — from your MCP config"). The user confirms or overrides.

Ask only what mining cannot answer:
1. **Hosting** — the one guaranteed question: local cron / VPS / Fly.io / other.
2. Chat platform — only if ambiguous or absent.
3. Runtime — only if multiple equally plausible options found.

## Phase 3 — Define Identity and Duties (files into the TeamOS repo)

Robin is a chief of staff, and a chief of staff's job differs by team — so identity and duties are THEIR files, drafted here and versioned in THEIR repo, changed by PR rather than by reconfiguring Robin.

1. **Draft `soul.md`** — mine the TeamOS repo first (roster, product description, the language the team writes in, tone of existing docs). Propose a complete draft: who Robin is for this team, voice (default: direct, concise, no hedging — overridable in review), the two universal conventions (cite your source; answer in the asker's language), plus team-specific conventions if evidence suggests any. Show it, revise on feedback, write it to the **TeamOS repo root as `soul.md`** (matching spec §4).
2. **Propose a duty roster** — seeded from repo evidence: a meetings folder suggests meeting prep; metrics/data pointers suggest a morning brief; the digest is on by default (the spec's minimum roster). Present as a table — duty, trigger, inputs, output, destination, owner — and let the user prune/adjust in ONE confirmation. Write the declaration into the TeamOS repo (e.g., `robin/duties.md`).

## Phase 4 — Emit Two Files (both to the TeamOS repo root)

**`ROBIN-SPEC.local.md`**
- A copy of the upstream spec with every registry slot resolved or deferred, visibly marked: `> Resolved: Telegram (from your MCP config)`.
- Normative content (MUST/SHOULD/MAY text) untouched — byte-identical outside the marked additions. A configurator that edits MUSTs corrupts the contract.
- **The marking convention (all additions, no exceptions):** lines beginning `> Resolved:` (the version/hash/date header is itself written as `> Resolved:` lines at the top), plus ONE appendix delimited by the exact heading `## Appendix (local, added by /robin-init) — Conformance Checklist`. Stripping those reconstructs the upstream file byte-for-byte — verify by hash before finishing.
- The conformance checklist: the spec's M0–M5 acceptance tests with the team's REAL recurring question substituted as the M0/M1 test case, and the declared duties as the M2 cases.

**`KICKOFF.md`** — the prompt to paste into their coding agent:
- "Implement Robin according to ./ROBIN-SPEC.local.md on <resolved stack>. Robin's identity is ./soul.md and its duty roster ./robin/duties.md — versioned team files; they change by PR, never by config."
- "Choose and document where the implementation code lives (the knowledge repo stays read-only at Robin's runtime — a sibling directory is the usual answer)."
- "Build M0 first. Its acceptance test: <their real team question> answered from <their repo path>, source file cited."
- "Log every clarifying question you have to ask in ./QUESTIONS.md — each one is a spec bug for upstreaming. Do not patch the local spec to answer them yourself."
- The stack sentence names platforms and service bindings (chat platform, runtime, MCP servers, databases) — never libraries or packages; those belong to the implementing agent.
- The configurator's OWN findings (defaults the spec lacked, ambiguities hit during configuration) go into the same `QUESTIONS.md`, created now — the implementer appends to it.

## Phase 5 — Point at the Finish Line

Tell the user: M1's acceptance test IS the demonstration event — a teammate asking in the team chat and getting a repo-grounded answer. That moment, not the deployment, is when Robin starts existing for the team.

## Rules

- Show every file's substance before writing (soul.md, duties, and both emitted files).
- Total question budget: at most 5 — hosting (Phase 2) and the duty-roster confirmation (Phase 3) are the only guaranteed ones; everything else is mined and confirmed.
- Question-log findings flow upstream to the spec maintainer, never patched silently into local copies.
- Finish by reporting: slots resolved (with provenance), questions asked (count), files written (soul.md + duties in their repo; local spec + kickoff), and the single next action (paste KICKOFF.md into a coding agent).
