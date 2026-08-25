# Execution waste — a separate procedure, not part of `/team-improve`

**Read this first: `/team-improve` does not do this analysis, and this file does not add it.**
The skill mines corrections people typed. It cannot see what an answer cost to produce, and
nothing here changes that. This is a note on how to run that measurement yourself, kept next to
the skill because that is where people ask for it — not because the skill performs it.

Why it is kept out rather than folded into Phases 1–3: a semantic candidate is judged against a
human's criterion, and a waste finding is judged against a number. Those are different kinds of
evidence, and the agent that spots the waste is also the one that would propose the fix — which
is the arrangement the skill exists to forbid. Keeping them apart is a design choice you may
disagree with; it is not a claim that the waste does not matter.

**One thing that is *not* out of scope:** if a person *typed* a complaint about process — *"stop
grepping the same path three times"*, *"why did you read that file again"* — that is a correction
under Phase 2's existing taxonomy and belongs in the candidate list like any other. The exclusion
here is on mining **telemetry** as candidates, never on what a human said.

## Before you start

**Redaction.** This procedure sends an agent your **full** traces with tool calls and results
intact. That is a larger and more sensitive corpus than `candidates.jsonl`, which
`trace-formats.md` already warns must be redacted before it is committed anywhere shared. Full
traces can carry credentials echoed by tools, customer records, and internal URLs. Decide where
the output may be written before you run it, and do not commit the working material.

**Check your export can answer the question.** Most of the table below needs per-turn timing,
token counts, cache figures and tool-call records. **The generic JSONL shape in
`trace-formats.md` (`role` / `text` / `ts`) carries none of that**, so this procedure is
inoperable against it — you will get confident-looking numbers with nothing underneath. Claude
Code JSONL and Codex rollout logs do carry it, under names those formats define; find the fields
before you ask for percentiles.

## What to measure

Point an agent at the raw turns with tool calls intact — not `candidates.jsonl`. State your
denominator and the window, or nothing below can be interpreted.

| | Why it matters |
|---|---|
| turns analysed, and the time window | Everything else is meaningless without it |
| duration p50 / p95 / max | The tail is what people remember |
| input tokens, split **cached vs uncached** | See the cost note below — the split is the point |
| output tokens | Usually the most expensive per token; do not omit |
| tool re-searches per turn | The agent rediscovering its own toolset |
| skill/reference read volume, as a share of all tool output | The context tax on every new MD file you write |
| effort/model tier distribution | Trivial questions running at the top tier |
| repeated identical tool calls | Sometimes free to remove, sometimes a retry — see below |

## Five shapes worth naming

1. **Unbounded context on every turn.** The whole thread, or unrelated scaffolding, prepended to
   each message.
2. **Contract re-read per use.** A skill or reference file reloaded before every action it
   governs, when loading once per turn and holding a hash would do.
3. **Wrong source first, then redo.** The agent searches the place it knows before the place that
   has the answer. It *rhymes* with answering from the wrong branch, but do not treat them as one
   thing: here the agent notices and redoes the work, and you pay in latency; there the wrong
   source reaches a person as a confident answer. Same shape, different consequence, different
   fix.
4. **Unchanged strategy after an error.** The same call, repeated, with no new approach.
5. **Effort-tier inflation.** Everything at the top tier because nothing routes.

## Sort every finding before you act on it

**One-time config defects.** A trim function that trims nothing; a hardcoded reload. Fix once and
they stay fixed. Do not put these on a recurring list — after the first pass they are noise.

**Recurring shapes.** Effort-tier inflation, context growth from new skill files, tool re-search
and cache-key breakage come back the week after somebody adds a feature. These do not need a
mining phase; they need a threshold somebody watches. Pick the number, write down what "too high"
is, and have it fail loudly rather than appear in a report nobody re-reads. A threshold that
fires is harder to ignore than a checklist you intended to re-run — not impossible to ignore, and
thresholds do get quietly raised, so put a name against it.

**Both are human actions.** `/team-improve` forbids its own agent from editing active behaviour —
skills, hooks, prompts, `CLAUDE.md`. Nothing here licenses that. The agent measures and reports;
a person changes the config and owns the threshold.

## Two traps

**Cost accounting.** A high cache-hit rate makes *gross* input tokens a bad proxy for spend, but
"uncached input" is not the whole bill either: output tokens are billed, usually at the highest
per-token rate, and cached input is billed at a **reduced** rate rather than free. Report the
three numbers separately and apply your provider's actual rates. And do not conclude the waste is
therefore fake: latency, round-trips and context pressure are real at any cache rate, and a cache
is one prefix change — a timestamp, a reordered block, a changed file hash — away from not
existing. Likewise, identical repeated calls are cheap to remove **when they are redundant**; a
retry after an error and an idempotent re-confirmation are not the same thing, and you have to
read the trace to tell which you are looking at.

**Goodhart, in its purest form.** Fewer tool calls is trivially achieved by checking less. An
agent told to reduce its own tool calls will stop verifying, and the metric will improve while
the work gets worse.

The obvious control — *"only accept an efficiency change if the frozen case set still passes"* —
is worth running and is **not sufficient**, for a reason worth being explicit about: the case
runner scores a **single-shot question and a string answer**. It does not replay a multi-turn
session, tool use, context growth or model tier. So the frozen set can catch an efficiency change
that broke a *stated* answer, and it cannot catch one that made the agent verify less on the way
there. If that is the risk you care about, you need a case that makes the verification itself
observable in the answer — *"names the branch it read"*, *"cites the row count it saw"* — or you
need to read sessions. Do not let a green case run stand for a claim it cannot support.

## The shape both halves keep converging on

Twice now, in one production agent, the two passes reached for the same idea: the efficiency pass
wanted a skill contract loaded once per turn and stored as a **receipt/hash**; the correctness
pass wanted every code answer to carry a **`repo@SHA` receipt** that a reviewer blocks approval
without.

That is n=2 in one shop rather than a law, but the primitive is worth reaching for before either
a config patch or a prompt rule: **pin the input, hash it, prove what was used.** Note the thing
it does not solve for free — what the pin *covers*. A hash over a fixed file list silently
ignores files added later; a hash over a whole directory changes every time anyone adds anything.
Decide which you meant, and write it down.
