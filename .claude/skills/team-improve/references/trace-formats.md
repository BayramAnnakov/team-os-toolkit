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
