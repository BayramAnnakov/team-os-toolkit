---
name: init-team-os
description: Evidence-first Team OS setup. Mines the host agent's local transcripts (Claude Code, Codex, …), MCP config, and existing repos to pre-populate a team knowledge repo interview, asks at most 5 questions, builds the minimal repo that answers the team's top recurring question, and ends with a ready-to-post demonstration message. Use when the user says "init team os", "set up our team os from evidence", "build our team knowledge repo", or wants a TeamOS scaffolded from what their machine already knows.
---

# /init-team-os — Evidence-First Team OS Setup

Build the smallest team knowledge repo that answers the team's most expensive recurring question — populated from evidence, not from a questionnaire.

## Principles (non-negotiable)

1. **Never ASK what you can MINE.** The machine already knows the user's tools, projects, and repeated pain.
2. **Never USE what you can't SHOW.** Every mined fact is presented with provenance ("seen 5× in onsa-server sessions since May") and confirmed before use.
3. **Never WRITE what the user hasn't REVIEWED.** No file lands without the user seeing its substance first.
4. **Folders after the answer, never before.** No empty directories. Structure grows when content demands it.
5. The user answers **at most 5 questions** across the whole flow. Review confirmations (Phase 1 evidence review, Phase 3 file approval) do NOT count against this budget — only substantive questions do. If you are about to ask a sixth, you failed to mine — say so and mine harder.

## State Management

Create `.team-os-setup/state.md` **at the root of the new repo's working directory** at the start. Append findings after every phase (evidence results, confirmed facts, answered questions, files written). If the session compacts or restarts, restore from this file and never re-ask an answered question.

## Phase 0 — Evidence Sweep (silent, local; narrate progress briefly)

Mining is read-only. Local files never leave the machine; already-connected tools (MCP servers) may be QUERIED read-only, but name each one to the user before its first query. Redact anything credential-shaped (keys, tokens, passwords, connection strings) the moment it is read. **Redaction means: display only the credential TYPE and the date it was seen ("staging API key, May 28") — never more than the first 4 characters of the value, anywhere, including the state file.** A 14-character prefix is a leak, not a mask.

**Path safety:** Claude Code project slugs begin with `-` (e.g. `-Users-you-repo`). `grep`/`jq` parse such paths as flags and return empty output WITH NO ERROR — silently losing all evidence. Always invoke them with `--` before path arguments or `./`-prefixed paths.

Sources, in value order:

1. **The host agent's conversation history** — you are running INSIDE an agent; mine ITS session transcripts first (you know where you store your own). Sample the most recent 30–60 days, mtime-capped. Stream with `grep`/`jq`; never read whole files (they can be GBs). Locations by agent:
   - **Claude Code:** `~/.claude/projects/<slug>/*.jsonl` (slugs begin with `-`; see Path safety).
   - **Codex CLI:** `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` (date-partitioned JSONL; `~/.codex/session_index.jsonl` indexes them by `thread_name`, and `~/.codex/history.jsonl` is the flat input history).
   - **Cursor / other agents:** locate your own session store (Cursor keeps chats in its workspace DB). If you're an agent not listed here, you still know where your sessions live — find them before falling back to asking.
   Extract two distinct signals, whatever the file schema:
   - Questions the user asked their agent repeatedly → knowledge the user lacks.
   - Context the user RE-EXPLAINED repeatedly (people, products, acronyms, decisions) → knowledge the repo should hold so nobody explains it again. **This is the higher-value signal.**
   Also extract tool/MCP usage (Claude Code: `mcp__<server>__<tool>`; Codex: the tool-call entries in its rollout JSONL) → the team's real tool inventory.
2. **The host agent's config** — the MCP/tool config: Claude Code `~/.claude.json` + `~/.claude/settings.json` (`mcpServers`, `enabledPlugins`); Codex `~/.codex/config.toml` (`mcp_servers`). → connected tools (chat platforms, trackers, DBs, calendars). Redact credential-shaped values the moment they're read.
3. **Connected read-only sources** — task trackers, meeting recorders, and wikis the config just revealed. A backlog IS team evidence: open/closed items reveal roster, roles, active projects, and vocabulary. (Field result: a "we have no knowledge base" team's Todoist held 137 tasks that yielded the roster and structure on the first query.) Name the source before querying; reads only.
4. **Existing CLAUDE.md / AGENTS.md** across workspace repos → knowledge that already exists. Index it; never recreate it.
5. **git history** of team repos → author names/emails (roster candidates), README (product description).
6. **Calendar** (only if a calendar tool is already connected) → recurring meetings.
7. **Drop-in files** the user provides: chat exports, meeting notes, a real artifact (transcript, strategy doc).

If no transcripts exist after checking your own agent's store (a genuinely fresh machine): say so plainly, accept exported history if offered, and fall back to asking. Never fabricate evidence.

## Phase 1 — Evidence Review

Present findings grouped (recurring questions / re-explained context / tools / people / existing docs / **prior TeamOS-like artifacts, each marked live or dormant** / **redacted credentials** — type and date only), each item with provenance and count. The user confirms, corrects, or deletes. Deleted items are gone — do not resurrect them. This review replaces any later "did the evidence get anything wrong?" question — do not ask it again.

## Phase 2 — The Irreducible Questions (≤5)

1. "What question does your team ask YOU repeatedly?" — seed with the top mined candidates; the user picks or overrides. **This becomes the build target.**
2. "What must NOT go in this repo?" — the trust boundary. Record it in state AND as a short "What does NOT belong here" section in the root CLAUDE.md (collaborators must learn the boundary too, or they will violate it innocently).
3. Only if the evidence leaves the structure choice open (named customers exist but tracking preference is unknown): "track customer accounts individually, one file per account?"
4. "Who besides you will plausibly read this in the next 30 days?" — calibrates scope.
5. Reserved — use only if a genuine gap emerged that mining and review could not settle.

## Phase 3 — Minimal Build

- Root `CLAUDE.md` under 50 lines: one-paragraph identity, doc index, roster (confirmed candidates), tool pointers, and the "What does NOT belong here" boundary section.
- The 2–3 content files that answer the top confirmed questions, populated from confirmed evidence and the imported artifact.
- Every file gets frontmatter: `owner` (a lowercase handle, consistent across files), `tier: stable|evolving|volatile`, `last_reviewed: <today>`.
- **Status-type questions** ("what's the status of X?") are answered with a date-stamped snapshot file: `tier: volatile`, the facts as of `last_reviewed`, plus a "where the live status lives" pointer (system of record or owner). That is how a status question coexists with the no-active-state rule — the repo holds the dated snapshot and the pointer, never a value pretending to be current.
- Other active state (ticket statuses, metric values) does NOT go in the repo — the repo records how to navigate to systems of record.
- Show the user each file's substance before writing. Honor the trust boundary from Phase 2.

## Phase 4 — The Demonstration Event (the actual deliverable)

1. Answer question #1 FROM the repo, citing the file — in a fresh sub-session/subagent if the runtime offers one (the strong proof); otherwise via explicit re-read, saying plainly that the weaker form was used.
2. Draft the message the user posts to their team channel: the answer + one line — "this came from our new team repo: <link/path>".
3. Tell the user: adoption follows demonstrated value. Post the answer where the team will see it; wait for "how did you do that?"

## Phase 5 — Optional Hardening (each independently skippable)

- ONE enforcement hook (e.g., frontmatter check or kebab-case check) — `git init` the repo first if it isn't one, then demonstrate the hook FAILING on a bad commit before trusting it.
- `gh repo create <name> --private --source=. --push` if they want it shared now.
- Point the user to **`template/`** (in this toolkit) as the **growth map** — the lean, proven shape (generalized from the `onsa-brain` reference) their seed grows into, with the frontmatter/index conventions. It is a reference to grow *into*, not a scaffold to create now: honor Principle 4 (folders after the answer, never before). Do NOT pre-create its empty folders.
- Point to `/init-team-brain` when they're ready for the product-knowledge layer with drift detection, and to `/init-team-decisions` when the mined evidence shows recurring "what would <the lead> say?" / "should we do X or Y?" questions — that signal wants the judgment layer, not another doc.

## Rules

- Conversational questions, not forms. Number them so the user can answer in one message.
- Declarative output, grepable markdown, kebab-case filenames.
- **Prior attempts are evidence, not completion.** When the sweep finds existing TeamOS-like artifacts (old knowledge repos, wiki exports, half-built brains), classify each by liveness (recent commits/edits vs dormant) and let the user sort them in the Phase 1 review: canonical (extend it — never create a rival), raw material (mine it), or ignore. Never conclude "a TeamOS already exists" unless the user names one canonical repo. (Field failure: a machine littered with abandoned knowledge-base attempts convinced the agent the picture was complete — "I'm done" — before the interview even started.)
- Finish by reporting: questions asked (count), files written, evidence items used vs discarded, and the one next action (post the message).
