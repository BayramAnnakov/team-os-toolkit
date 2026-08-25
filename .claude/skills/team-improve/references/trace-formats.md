# Trace formats

`extract_candidates.py` reads two shapes. Everything else needs an adapter you write once.

## 1. Claude Code / Codex session JSONL (auto-detected)

Found under `~/.claude/projects/<slug>/<session-uuid>.jsonl`. One JSON object per line.

The fields the filter uses:

| Field | Why it matters |
|---|---|
| `type` | `"user"` or `"assistant"` |
| `message.content` | string, or a list of blocks (`text`, `tool_result`, `tool_use`) |
| `promptSource` | **the load-bearing one.** `typed` / `queued` / `suggestion_accepted` = a person. `sdk` = a scheduled run. `system` = a platform event |
| `isMeta`, `isCompactSummary` | machine-authored; dropped |
| `timestamp`, `cwd`, `sessionId` | provenance |

**Older logs have no `promptSource`.** They fall back to a prefix check only, so they are
kept more permissively — recall over precision, because the semantic pass filters anyway.

## 2. Generic JSONL (any other agent)

One object per line. Minimum:

```json
{"role": "assistant", "text": "Total billed in May: 1,284,500", "ts": "2026-06-02T09:06:00Z"}
{"role": "user",      "text": "check the units on that table",  "ts": "2026-06-02T09:09:00Z"}
```

`role` must be `user` or `assistant`. `text` may also be supplied as `content`. `ts` is
optional but you want it — clusters are dated.

### Exporting from a deployed agent

Whatever your agent stores, you need three things per turn: **who spoke, what they said,
when.** A rough SQL shape:

```sql
SELECT CASE WHEN from_type = 'agent' THEN 'assistant' ELSE 'user' END AS role,
       body AS text,
       created_at AS ts
FROM interactions
WHERE created_at >= '2026-06-01'
ORDER BY conversation_id, created_at;
```

Emit as JSONL, one row per line.

## Known limits — read before trusting a run

- **A wrong answer nobody challenged.** The evidence base is *corrections people typed*. The
  filter keeps a human turn only when it follows an agent reply, and Phase 2 judges that pair —
  so an answer that was wrong and got accepted produces no pair to judge, and therefore no
  candidate and no cluster. (Phase 4 can still reach one: a human may add a case the mining could
  not have produced. That is the only route in.) **A clean report means "few typed corrections",
  never "few errors."** Note this is a different blindness from the team's: they *saw* the answer
  and accepted it — one production agent ran an entire investigation against the wrong git
  branch, and it surfaced days later, from another route. They eventually found out; the miner
  never would have. A better miner does not fix this, because there is nothing in the trace to
  find. What helps is making a wrong answer cheaper to falsify at read time — stating the source,
  branch, commit or query the answer rests on. That does not manufacture a correction (people
  ignore cited sources too); it lowers the cost of noticing, and noticing is what this loop eats.
- **How the answer was reached.** Phase 1 drops tool results and token events by design, and
  Phase 2 reads only the pair `agent reply → human reply`. Duplicate tool calls, searching the
  wrong source and redoing the work, an unchanged strategy after an error, context growth and
  effort tier are outside this instrument. Whether that waste is larger or smaller than the
  semantic defects is not something a run of this skill can tell you — it is a different
  measurement, against a number rather than a human's criterion. `execution-waste.md` is how to
  run it separately. Note the partial exception: the last 1,200 characters of the agent's reply
  *are* kept, and agents often narrate the path they took, so some of this is visible in text
  even though the tool records are gone.
- **The scoring runtime is not the production runtime.** Mining reads multi-turn sessions with
  tools. `run_cases.py` scores a **single-shot question and a string answer** (`claude -p {q}` by
  default). It does not replay tool use, context growth, a wrong-branch checkout, sub-agents or
  model tier. Two consequences: a case often cannot reproduce the session defect its candidate
  came from, and a frozen set cannot detect a change that made the agent *verify less* unless the
  verification is observable in the answer text. Write criteria that make it observable — *names
  the branch it read*, *cites the row count it saw* — or accept that the suite is scoring
  something narrower than the incident.
- **Discarded prompt scaffolding.** Phase 1 drops skill preambles and, for Codex, the assembled
  user turn that includes injected `AGENTS.md`. So the miner cannot see that the agent was
  *obeying written instructions* when it did the thing someone corrected. You will stage
  "stop doing X" while X sits in a file you discarded. Before promoting any candidate, grep the
  active instruction set for the behaviour you are about to prohibit.
- **Sessions in one file.** The generic reader treats a file as one conversation. If your
  export concatenates conversations, split it per conversation or you will pair a human turn
  with the wrong agent reply.
- **Context windows.** Only the **last 1,200 characters** of the agent's reply are carried
  (`--context-chars`), and the first 2,000 of the human turn. Long replies whose defect sits
  in the middle will look unjudgeable. Raise it when replies are long.
- **Non-typed human channels.** Reactions, thumbs-down, an edited prompt, a regenerate, a
  correction made in Slack instead of to the agent — none of these appear as a typed turn.
  **This filter cannot see them.** They are real corrections and you will need another
  source for them.
- **Cross-session corrections.** A person who gives up and re-asks two days later, reworded,
  produces no correction turn at all. Only a human reading the quiet sessions finds those.
- **Sub-agent traffic.** `isSidechain` turns are not special-cased yet.
- **PII.** `candidates.jsonl` contains verbatim text from your logs. It is working material.
  Do not commit it to a shared repo without redacting it first.

## 3. Codex rollout logs (auto-detected)

`~/.codex/sessions/**/rollout-*.jsonl`. Codex writes each turn **twice**:

| Line | What it is | Used? |
|---|---|---|
| `event_msg` / `user_message` | what the person actually typed | ✅ **this one** |
| `response_item` / `message` role=user | the assembled API turn — **includes injected AGENTS.md** | ❌ dropped |
| `event_msg` / `agent_message` | what the agent replied | ✅ |
| `reasoning`, `token_count`, `function_call*`, `turn_context` | machinery | ❌ |

`event_msg` is Codex's equivalent of Claude Code's `promptSource: typed`.

**Measured on 200 real sessions:** 584 human-typed turns, of which **395 were orchestration
wrappers** — `<realtime_delegation>`, `<codex_delegation>`, and a supervisor loop beginning
*"The following is the Codex agent history…"*. Only 31 survived as correction-eligible.
If you drive Codex from scripts, expect most of your log to be your own automation.

⚠️ `~/.codex/history.jsonl` is **human prompts only** — no agent turns, so nothing can be
paired. Point the extractor at `sessions/`, not at `history.jsonl`.

**Two more Codex UI wrappers** are dropped: `# Files mentioned by the user:` and
`# Selected text:` — the editor prepends these when you attach a file or a selection.

**Expect low precision on an interview-heavy history.** Measured on one real Codex account:
31 surviving candidates, of which **16 came from a single `/init-*` session** where the agent
was asking the questions. Those are elicitation answers, not corrections — see SKILL.md
Phase 2. The yield was **two genuine, transferable rules from ~200 sessions.** That is a
realistic return, and both were things the person had forgotten they ever said.
