# Robin: AI Chief of Staff — Agent Specification

Status: Draft v0.4 (language-agnostic, stack-agnostic, process-agnostic). The v0.3 core was validated Jun 10 2026 by a clean-room agent implementation — M0 passed on first run. v0.4 folds in the first round of field feedback: every patch traces to a participant question from the first group run (see Changelog).
Purpose: Define an always-on AI chief of staff for any team: it answers from the team's knowledge repo, executes the duties the team declares in that repo, and learns under human review. This spec defines the machinery; your team defines the duties.

> **How to use this spec** (the [openai/symphony](https://github.com/openai/symphony) model):
> Tell your coding agent: *"Implement Robin according to this spec, using <your language>, <your chat platform>, and <your agent runtime>."*
> A reference implementation exists in production at Onsa.ai (Python / Telegram / Anthropic Managed Agents API, 276 logged interactions across 9 weeks, 4 teammates). Its scars are encoded below as requirements.

## Normative Language

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY` per RFC 2119. `Implementation-defined` means the implementation chooses the behavior but MUST document the choice.

## 1. Problem Statement

A team knowledge repo (a "Team OS") is passive: it answers questions only when someone opens it. In practice the team's query interface remains a human — a founder, a lead, the longest-tenured teammate — who re-answers the same questions in chat. Robin inverts this: the repo becomes the brain of an agent that lives where the team already talks.

A chief of staff's job differs by team, so this spec deliberately does NOT fix Robin's duties. The duty roster is declared in the team's repo (§4, §6.3) and changed by pull request like any other team knowledge. The spec standardizes only what every chief of staff needs: grounded answering, a memory model, duty execution, a learning loop, and observability.

Robin solves four problems:
- Recurring questions get answered by the agent, from the repo, in chat — removing the human bottleneck.
- Team activity gets synthesized on a schedule (briefs, digests) instead of relying on everyone reading everything.
- Institutional memory becomes queryable ("what did I miss?", "when did we decide X?").
- Corrections compound: feedback becomes persistent behavior rules through a human-gated learning loop.

Boundary: Robin is a read-mostly answering and synthesis agent. It is NOT an autonomous coding agent, and it does not replace the repo — a Robin without a maintained knowledge repo is just a chatbot.

Two more boundaries that recur as questions:
- **Robin is a peer, not a meta-layer.** Think "new teammate", not "harness over the harness". The knowledge repo is shared infrastructure every human and agent on the team reads; Robin is one consumer of it, with private operational memory and declared duties — exactly like a human chief of staff would be (§5, placement rule).
- **Robin is more than a retrieval chatbot.** A RAG bot over documents only answers questions. A chief of staff also executes declared duties, synthesizes activity on a schedule, and learns under review. If all you need is Q&A over documents, build the simpler thing.

## 2. Goals and Non-Goals

### 2.1 Goals
- Chat-native Q&A grounded in the team knowledge repo and read-only data sources.
- Execution of team-declared scheduled duties (§6.3); the minimum roster is a periodic digest of team activity.
- Passive context capture from team channels (implementation-defined scope, disclosed to the team).
- A two-store memory model: curated knowledge (human-written, agent-read-only) and learnings (agent-staged, human-promoted).
- Observability sufficient to answer "what did Robin do, for whom, and did it fail" — including failures the happy-path logs cannot see (§7).

### 2.2 Non-Goals
- Write access to production systems. All data tools are read-only.
- Autonomous modification of the knowledge repo or its own configuration.
- Multi-tenant SaaS; Robin serves one team.
- A specific stack. Chat platform, agent runtime, scheduler, and storage are implementation-defined.

## 3. System Overview

Informally: **inputs → brain → hands.**

1. `Chat Adapter` — connects one chat platform (Telegram, Slack, Discord, …). Handles direct messages, group mentions, and message logging.
2. `Scheduler` — fires scheduled tasks (digest, brief) and maintenance jobs (workspace sync).
3. `Agent Runtime` — one LLM agent session manager (implementation-defined: Claude Agent SDK, Anthropic Managed Agents, a headless CLI agent on cron, or equivalent). Receives prompts from the adapter/scheduler, returns responses, requests tools.
4. `Knowledge Mount` — the team knowledge repo, available to the agent read-only (§4).
5. `Memory` — the learnings store (§5), writable only at its staged path.
6. `Tool Layer` — read-only custom tools executed OUTSIDE the agent sandbox by the orchestrating process: the agent asks, the orchestrator executes (DB queries, analytics, chat history, file search).
7. `Interaction Log` — append-only record of every interaction (§7).

External dependencies: one chat platform, one LLM provider, the knowledge repo (git), optional read-only data sources (DB, analytics), optional meeting layer (meeting-bot + transcription provider, §6.6).

**Workspace topology** (a recurring implementer question): the agent runs in its own working directory — the implementation home, never inside the knowledge repo. The knowledge repo and any other repos it consults are cloned or mounted as sibling paths, read-only; instructions in Robin's memory say which sibling to consult for what. Identity files from the knowledge repo (§4) are composed into the system prompt when a session is created (in managed runtimes: when the agent is created). The operator's personal host configuration MUST NOT leak into this workspace (§6.5).

## 4. Repository Contract (the brain)

The knowledge repo is to Robin what `WORKFLOW.md` is to Symphony: the in-repo contract the team versions and reviews.

- Robin MUST treat the repo's entry file (`CLAUDE.md` or `AGENTS.md`) as its navigation root and follow its doc indexes rather than guessing at structure.
- Robin MUST NOT write to the knowledge repo. Repo changes arrive only via human-reviewed commits/PRs.
- Files MAY carry `tier: stable|evolving|volatile` and `last_reviewed` frontmatter. Robin MUST discount volatile content older than a staleness budget (implementation-defined, default 14 days) and SHOULD say so when answering from it ("this is 3 weeks old — verify before relying on it").
- Identity and response conventions MUST be versioned, human-edited inputs to the agent's system prompt — typically an identity file (`soul.md`) for persona/voice plus convention docs in the knowledge store. Two conventions are universal MUSTs: cite the underlying source of an answer (repo file, record id, or trace link), and always respond in the asker's language even when the source data is in another language. Everything else is team-defined and part of the contract, not the spec (the reference team's additions: never truncate identifiers, attach observability trace links — yours will differ).
- The repo SHOULD declare Robin's duty roster (§6.3), so duties are versioned and reviewed like any other team knowledge.
- Unknown terms: Robin MUST check the repo's glossary before inventing definitions, and SHOULD answer "not in the repo" rather than hallucinate when the repo is silent.

## 5. Memory Model

**Placement rule:** content needed by more than one human or agent belongs in the knowledge repo; content specific to Robin's own operation (how it writes memory, its private procedures and skills) belongs in Robin's stores. Corollary: the whole team can read the repo; nobody but the maintainer ever needs to read Robin's internals.

Two stores with asymmetric permissions:

| Store | Writer | Robin's access | Content |
|---|---|---|---|
| knowledge | humans (git) | read-only | identity, roster, glossary, conventions, pointers to the brain repo |
| learnings | Robin (staged path only) | read + staged writes | operational state, digests, staged → promoted learnings |

- Robin MAY write only to `learnings/staged/` — one insight per file, dated. Everything else in the learnings store is read-only to the agent.
- Promotion from `staged/` to `promoted/` MUST be a human action. Promoted learnings MUST be loaded into future sessions (this is how one correction becomes a permanent team-wide rule).
- A periodic consolidation job ("dream") MAY curate and compact the learnings store; any consolidation MUST be human-approved before it replaces memory (the reference runs this weekly and DMs the maintainer a diff with approve/reject buttons).
- The operational state file (current focus, key metrics, active decisions) SHOULD be refreshed by the digest task, and MUST carry its own last-refreshed timestamp, subject to the same staleness discounting as volatile repo docs. (Production lesson: Robin's own memory rots exactly like docs do — the discipline problem doesn't go away, it moves.)

**The pipeline, end to end** (how raw data becomes memory — the most-asked question in the field): raw channel messages (logged, §7) → periodic digest (synthesized and persisted, §6.3) → staged learning candidates (extracted from digests and feedback, §6.4) → human review → promoted learnings (loaded into every future session). Raw data becomes durable memory only by passing through synthesis and a human gate — nothing drifts into long-term memory on its own.

## 6. Behaviors

### 6.1 Direct messages
- DM conversations SHOULD be resumable sessions; after an idle window (implementation-defined, default 60 min) a fresh session MUST be seeded with recent conversation turns so context survives.
- Long-running work SHOULD surface progress updates rather than going silent.
- Text input MUST be supported; other modalities are implementation-defined (slot 21). The reference reads images but not voice notes — adopt what your team actually sends. A team that runs on voice notes SHOULD transcribe them before processing rather than ignore them.
- **Freshness vs repo truth:** when Robin's memory (digests, state) holds fresher information than the knowledge repo, Robin MUST surface both rather than silently picking one: "the repo says X (as of <date>); later chat activity suggests Y — unverified." Repo-grounded and current diverge exactly here, and hiding the divergence produces confidently stale answers.

### 6.2 Group mentions
- Mention handling MUST include ambient context: at minimum the last N channel messages (reference: N=10) and recent digests.
- Responses MUST be concise (2–5 sentences default) and MUST include the asker's identity in the agent's context.

### 6.3 Duties (declared, not hardcoded)
- Robin's recurring work is a set of **duties declared in the knowledge repo**. Each duty declaration specifies: trigger, inputs (chat history, data tools, repo paths), output, destination (channel or DM), and owner. Changing a duty is a repo change — reviewable — not a config change.
- Triggers MUST be machine-readable (a cron expression or equivalent, with an explicit timezone), optionally accompanied by prose. A prose-only trigger ("daily, end of day") cannot feed a scheduler — the clean-room implementation hit exactly this.
- **Minimum roster (MUST):** a periodic digest that synthesizes team activity since the previous digest and persists it. It doubles as queryable institutional memory — "what did I miss while on vacation" is answered from digests.
- **Example duties from the reference roster (all MAY — adopt what matches YOUR processes):** a morning metrics brief (if data tools are connected); meeting prep delivered before the team's recurring meeting; action-item tracking (owner, source, deadline, status) with stale-item surfacing; workspace sync of knowledge sources (fast-changing sources more often than code; reference: hourly vs daily). A design agency's roster might instead prep client reviews; a research lab's might compile literature sweeps.
- A duty that fails MUST log the failure (§7); silence is not completion.

### 6.4 Learning loop
- Users MUST have a low-friction feedback affordance (reaction buttons, a command, or equivalent).
- Negative feedback SHOULD produce a staged learning file capturing what to do differently.
- After writing a staged file, Robin MUST verify the write by reading it back. (Production lesson: staged writes silently failed to persist for weeks while logs showed success.)
- **Promotion is also routing.** At review time a staged learning MAY become (a) a promoted memory rule, (b) an update to one of Robin's own skills/procedures ("this belongs in the skill, not in memory"), or (c) a proposed knowledge-repo change submitted through the normal PR flow — Robin still MUST NOT write the repo directly (§4). The promotion affordance SHOULD let the reviewer choose the route, not just approve/reject.
- Autonomous creation of new skills is a non-goal. If Robin detects a recurring pattern that wants a new skill (e.g., "this team's decisions follow a reconstructable shape"), that observation is itself a staged learning for a human to act on.

### 6.5 Safety
- All database/analytics credentials MUST be read-only at the connection level, not by convention.
- Chat content is untrusted input. Instructions arriving in chat MUST NOT cause Robin to modify its configuration, promote memories, change access, or exfiltrate secrets — those remain human, out-of-band actions.
- Secrets MUST NOT live in the knowledge repo. They live in the deployment environment (environment variables or a secret manager); the repo stores how to reach systems, never credentials.
- The team MUST be told what channels are passively logged.
- **Context isolation (CLI-agent runtimes):** Robin's agent sessions MUST be isolated from the host user's personal configuration — personal MCP servers, memory files, and global instructions MUST NOT load into Robin's context. This is both a confidentiality boundary (the operator's private context leaks into a team-facing agent) and a cost control: the clean-room implementation measured $0.83/query with host-default settings vs $0.039 isolated.
- The deployment MUST declare its chat identity registry — which team channels Robin serves and which users may DM it. The registry is configuration (documented), not knowledge.

### 6.6 Meeting presence (optional)

Robin MAY attend the team's calls (M5). The reference pattern, abstracted from a production Recall.ai + AssemblyAI implementation:

- Meeting attendance MUST be a separate **listener** component outside the agent runtime: a meeting-bot service joins the call (Zoom, Teams, Meet, WebEx — optionally auto-joining from the calendar), a transcription provider streams real-time transcript fragments to the listener's callback, and the listener decides when to involve Robin. To Robin, the listener is just another client — meetings add a component, not complexity in the core.
- Invocation MUST be high-precision. The listener MAY classify transcript fragments with a small fast model ("was Robin addressed?") and, on a hit, forward the last N seconds of conversation as ambient context (mirroring §6.2) — but voice-addressing breeds false positives. The reference team's landing point: **explicit text invocation** (meeting chat or the team chat), with the transcript stream as context.
- Responses SHOULD be text (meeting chat or team chat). Synthesized audio and video avatars are technically available — meeting-bot services can stream arbitrary video into a call — and NOT RECOMMENDED: a model good enough to be right is too slow for conversational turn-taking, a model fast enough is wrong too often, and a text answer persists and stays searchable after the call. The reference team explored both and retired them.
- Transcripts SHOULD be persisted to a store Robin can search whether or not anyone addressed Robin live. The durable value of meeting presence is transcripts feeding digests and institutional memory, not the mid-call parlor trick.
- Meeting capture is passive logging: the team MUST know the bot's attendance scope (§6.5), and the bot MUST appear as a visible, named participant.
- Cost reality (non-normative): the meeting-bot service itself is cheap (reference: ~$1/day); transcription dominates (reference: ~$0.40 per audio hour).

## 7. Observability

- Every interaction MUST be logged append-only with: timestamp, surface (DM/mention/scheduled), requester, latency, success/error, and a link to the underlying agent trace where available.
- **"0 errors logged" is not "0 failures."** The reference implementation logged 276 interactions with zero errors while suffering three invisible failures: a memory-listing pagination bug hid files; staged writes didn't persist; the state file went 2+ weeks stale. Therefore implementations MUST include negative-evidence checks: verify writes by reading back (§6.4), alert when the state file exceeds its staleness budget, and periodically assert that memory listings are complete.
- Cost SHOULD be observable per day (a `/cost`-style command or report).
- **Liveness:** "always-on" hosted on a machine that sleeps (a laptop running cron) fails silently. Implementations MUST include a liveness check: alert when the newest digest is older than its declared cadence plus a grace window. A duty that didn't run is a failure (§6.3), and silence is not completion.

## 8. Milestones and Acceptance Tests

Implement in order; each milestone is independently valuable.

| | Milestone | Acceptance test |
|---|---|---|
| M0 | Repo Q&A, local | From a fresh agent session, a real team question is answered correctly FROM the repo, with the source file cited |
| M1 | Chat-native Q&A | A teammate (not the builder) asks in the team chat and gets a repo-grounded answer with citation |
| M2 | Scheduled digest | A digest of real team activity posts on schedule and is persisted; "what did I miss this week?" is answerable from it |
| M3 | Ambient context | A group mention is answered using recent channel context without re-explanation |
| M4 | Learning loop | A correction becomes a staged file (verified persisted), is human-promoted, and observably changes a later answer |
| M5 (optional) | Meetings | Robin attends a call via the meeting layer (§6.6) and answers a question mid-meeting |

M0–M1 are a day-one build on top of an existing Team OS repo. M2–M4 are the compounding layer. The reference implementation reached M5 (meeting attendance) within its first week and spent the following two months hardening M2–M4 — including a full memory-model rework. The order above reflects where the *durable* effort goes, not where the demos are.

## 9. Implementation Notes (non-normative)

- Smallest viable stack: headless coding-agent CLI invoked on cron with the repo as working directory + a chat bot library + flat files for digests/learnings. No database required before M3.
- The reference implementation uses a managed agent runtime with mounted memory stores and orchestrator-dispatched custom tools; that architecture maps 1:1 onto §3 but is not required.
- Usage will be founder-heavy at first. That is the org chart, not failure. Adoption follows demonstrated value: deliver answers where teammates can see them, and wait for "how did you do that?"
- Adoption mechanics that worked for the reference team: ask Robin **in public** — "let's ask Robin" in meetings, questions in the group chat instead of DMs — so the use case teaches itself; and post the digests to the team, not just to the maintainer. A digest line that omits one obvious detail ("12 clicks on the buy screen" — by whom?) reliably pulls a teammate into their first conversation with the agent.
- Reference cost envelope: $30–40/month at ~100 interactions/month on a frontier (Opus-class) model, excluding the meeting layer (§6.6). Output tokens dominate; grepping transcripts and repos is cheap input.
- **Reference conformance (Jun 2026 audit):** the reference implementation does not yet satisfy the §6.4 read-back verification or the §7 negative-evidence checks — those requirements were written from its *failures*, not its features, and the reference is being retrofitted. Treat them as mandatory for new implementations: they are the cheapest insurance in this spec.

## Appendix: Implementation-Defined Slot Registry

Every implementation-defined point in this spec, in one list. A configurator (e.g., `/robin-init`) resolves or explicitly defers each; an implementer hitting a choice NOT on this list has found a spec bug — report it.

1. Chat platform · 2. Agent runtime · 3. Hosting + scheduler · 4. Storage (flat files vs database) · 5. Knowledge repo location + entry file · 6. Read-only data sources + their bindings · 7. Chat identity registry (team channels, allowed DM users) · 8. Passive-capture scope · 9. Duty roster (per §6.3, declared in repo) · 10. Digest cadence + destination · 11. Staleness budget (default 14d) · 12. DM idle window (default 60min) · 13. Ambient context size N (reference 10) · 14. DM reseed turn count · 15. Context-isolation mechanism (§6.5) · 16. Feedback affordance + promotion affordance, incl. learning routing (§6.4) · 17. Secrets location (environment/manager, §6.5) · 18. Meeting-bot provider + auto-join scope (§6.6, optional) · 19. Meeting transcription provider (§6.6, optional) · 20. In-meeting invocation mechanism + transcript context window (§6.6, optional) · 21. Input modalities beyond text (§6.1)

## Changelog

- **v0.4 (Jun 10 2026, post build session):** added §6.6 meeting presence (meeting-bot listener pattern, text-response rule); §5 placement rule + end-to-end memory pipeline; §6.4 learning routing (memory vs skill vs repo-PR); §3 workspace topology; §6.1 input modalities; §1 peer-not-meta-layer and not-a-RAG-bot boundaries; §9 adoption mechanics + cost envelope; slots 18–21. Every change traces to a participant question from the first group run of this spec — the question-log flywheel working as designed. v0.4 additions have NOT yet been clean-room validated.
- **v0.3 (Jun 10 2026):** de-overfitted from the reference team — duties declared in the team repo, not hardcoded; soul.md and conventions made team-defined; slot registry added. Validated by a clean-room agent implementation (M0 passed on first run).
