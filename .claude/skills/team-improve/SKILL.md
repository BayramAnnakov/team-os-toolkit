---
name: team-improve
description: Build the self-improvement loop for an agent your team already runs. Mines its session traces for the places a person corrected it, clusters them into staged improvement candidates, and derives a frozen test set from those episodes — where the agent proposes the case and the human writes the pass criteria. Use when the user says "team improve", "mine my agent's logs", "what should my agent learn", "build evals for my agent", "why does my agent keep making the same mistake", or wants a self-improvement loop that does not let the agent grade itself.
---

# /team-improve — the loop, with the evidence the agent does not control

Your team has written down what it knows: a brain, `decisions.md`, a critic, a hook. All of
that teaches the agent what you **already** know. This skill builds the part that learns
what you **don't** — from the agent's own operation — and it deliberately withholds one
thing from the agent: the criteria it will be judged by.

**The rule this whole skill exists to enforce:** *the agent brings the case; the human
writes the criterion.* An agent that proposes a change, selects the evidence, and grades
the result is the defendant, the witness and the judge.

## Preconditions

1. **Traces.** A directory of session logs. Any of:
   - `~/.claude/projects/` — Claude Code sessions. Present by default, but logging can be
     disabled, redirected or cleaned; check before promising a participant they have them.
   - an export from a deployed agent (see `references/trace-formats.md` for the generic shape)
   - `examples/sample-traces/` in this toolkit — for anyone with neither
2. **A Team OS repo** to write into. If none, say so and offer `/init-team-os` first —
   candidates and cases must live somewhere versioned, or this is a one-off report.
3. `decisions.md` is **optional but load-bearing when present**: an improvement candidate
   that contradicts a ratified principle must be flagged, never silently staged.

## Phase 1 — Extract, mechanically

Run `scripts/extract_candidates.py` against the traces directory. Do **not** read raw logs
into context: a normal machine holds ~190,000 lines per 800 sessions, of which ~1% can
possibly be a correction.

The script keeps only human-typed turns that directly follow an agent reply, and drops tool
results, scheduled prompts, skill preambles, compact summaries and inter-agent messages.
Report its counts to the user before going on — the funnel is itself the first lesson.

**Say what the funnel costs, at the moment you report it.** Two separate filters are doing the
narrowing, and they blind the method in different ways: dropping tool results removes what the
answer *cost* to produce, and keeping only human turns that follow an agent reply removes every
wrong answer nobody replied to. **A clean extract means few typed corrections, not few errors.**
`references/trace-formats.md` → *Known limits* is the full list — read it rather than these two.

## Phase 2 — Judge, semantically

Read each candidate as a pair: what the agent said, then what the person said back. Decide
whether the person was **correcting the agent's output**, and if so, which kind.

**Do not look for negation words.** Measured on real logs: a keyword pass is ~80% false
positives, and real corrections from senior people are polite and indirect. The highest-value
correction in one production store was *«А почему trace id не прикрепил?))»* — a question,
with a smiley, containing no negation at all. If your method would score that zero, your
method is wrong.

Classify each true correction:

| Class | Looks like | Rule-shaped? |
|---|---|---|
| Factual challenge | *"could you double-check that?"* | sometimes |
| Misread intent | *"I meant …"* | rarely |
| Overstatement | *"that overstates it"* | sometimes |
| Judgment disagreement | *"I don't think that's a big point"* | rarely |
| **Prohibition / instruction** | *"never do X"*, *"remember that prices are in cents"* | **usually** |
| Scope removal | *"drop that section"* | rarely |

### The four shapes that are NOT corrections

Most surviving candidates are one of these. Say so rather than stretching them into findings.

| Not a correction | Looks like |
|---|---|
| **A new instruction** | *"now draft the outreach note"* — the previous answer was fine |
| **An approval** | *"great, ship it"*, *"perfect, that's what I needed"* |
| **A decision to do nothing** | *"let's leave it, infra rebuilds that box tomorrow"* |
| **⚠️ An elicitation answer** | **the agent asked a question and the person answered it** |

**The last one is the trap, and it is invisible unless you read the preceding turn.** Any skill
that interviews the user — onboarding, `/init-*`, a requirements dialogue — produces dozens of
short human replies that are structurally identical to a correction.

Measured on one real Codex history: of 31 surviving candidates, **16 came from a single
interview session**, where the agent asked *"прямой peer, жёсткий sparring partner, терпеливый
coach?"* and the person replied *"терпеливый coach"*. Two words, directly after an agent turn,
and not a correction at all.

**The test:** did the agent's previous turn *ask* for this, or *assert* something the person is
now pushing back on? Only the second is a correction.

Report precision honestly: how many candidates you read, how many were corrections.

## Phase 3 — Cluster and stage

Group corrections by **root cause**, not by wording. Two differently-worded complaints about
the same defect are one cluster.

For each cluster write one file to `improve/candidates/YYYY-MM-DD-<slug>.md`:

- what the agent did, what the person said (quote them, dated)
- the proposed change, in one or two sentences
- **when to apply it** — the part that makes it transfer beyond its own episode
- how many independent episodes support it

Then **cut**. A skill that stages everything is a junk drawer; one that knows what *not* to
record is the product. Reject anything overfit to a single incident, anything that merely
re-describes what happened, and anything that restates a rule the team already has. Show the
rejected list with reasons — the cut is as instructive as the keep.

**Never change active behaviour.** No edits to `CLAUDE.md`, `decisions.md`, skills, hooks or
prompts. Staging only. Promotion is a human action, and it is a separate one.

## Phase 4 — Derive the test set (the point of the skill)

For each surviving cluster, propose a **case** — the input that would reproduce the failure.
Write to `improve/cases/NN_<slug>.md`, mirroring the frozen-suite shape:

```markdown
---
id: 03_trace_id_copyable
description: Asked for trace ids; the raw id must be copyable, not hidden behind a link label
expected_signals:      # ← THE HUMAN WRITES THESE
  - <written by the human>
is_ephemeral: true     # true when the correct answer changes over time
notes: <why, if ephemeral>
---

<the question, as a person would really ask it>
```

**Two hard rules.**

1. **The human writes `expected_signals`.** Leave the list empty and ask. You may transcribe
   a signal only when you can **quote a person in the trace saying it** — and then show the
   quote next to it. If you cannot point at a human utterance, do not propose the signal.
2. **Assert signals, never answers.** *"Returns a number, filters internal accounts, cites
   the source"* survives next week. *"Returns 751"* does not. Set `is_ephemeral: true` and
   say why in `notes`.

Then require two cases the mining could not have produced:

- **One negative case.** Something the agent must *decline* — say "not in the repo", ask for
  clarification, refuse to invent. A suite of only positive cases cannot tell a helpful agent
  from a confabulating one. This is the "it fires AND it stays silent" bar, applied to evals.
- **One case you did not propose.** The person adds it from their own recurring questions.
  You selected which failures they saw; that selection carries your blind spot, and this is
  the only step that can catch it.

## Phase 5 — Score it, or nothing was learned

**Staging is not learning.** A candidate that never gets measured is exactly how a real
production loop sat inert for 53 days while the same defect recurred. Run the cases:

```bash
# from the team-os-toolkit root
python3 .claude/skills/team-improve/scripts/run_cases.py improve/cases \
  --agent  '<the agent under test>' \
  --grader '<a DIFFERENT vendor>'
```

If `improve/cases` lives elsewhere, pass its real path — the script takes it as an argument.

Three rules the runner enforces, and you must not work around:

1. **A case with empty `expected_signals` is UNGRADED, not passed.** The human writes the
   criteria. A run that grades against nothing is worse than no run.
2. **The grader must not be the party that proposed the change.** Evaluators measurably
   prefer their own generations, so a same-model grade is not independent evidence.
   **A different vendor satisfies this. So does a person** — see below.
3. **A tool failure is not a score of zero.** An agent that could not be reached and an
   agent that answered wrongly are different events. Never let one be reported as the other.

### Run it before the change, not after

One score tells you where you are. It cannot tell you what the change cost, and that is the
question that actually decides a promotion: **a correct one-line change can break a line a
hundred lines above it, added by someone else, at another time.** So the run that matters is the
one standing between "I looked at it" and "I approved it".

```bash
# 1. before you change anything — this is the baseline
python3 .claude/skills/team-improve/scripts/run_cases.py improve/cases \
  --agent '<agent>' --grader '<a DIFFERENT vendor>'

# 2. make the change, then re-run against that baseline
python3 .claude/skills/team-improve/scripts/run_cases.py improve/cases \
  --agent '<agent>' --grader '<a DIFFERENT vendor>' \
  --baseline improve/results/latest.json
```

It compares **criterion by criterion, never totals** — a moved total is the least informative
number here. A run without `--baseline` writes `results/latest.json` and rolls the one before it
to `previous.json`. A run *with* `--baseline` writes `results/candidate.json` and **leaves
`latest.json` untouched**, so that re-running the same gate command does not quietly replace the
baseline with the candidate and then compare the candidate against itself.

The exit code is the verdict, and there are **three**:

| | |
|---|---|
| `0` | compared, nothing regressed |
| `1` | compared, something that used to pass now fails |
| `2` | **no verdict** — not comparable, or nothing was compared at all |

**Treat `2` the way you treat `1`.** It is the one that matters: a gate exiting 0 because every
case was excluded looks identical to a gate exiting 0 because the change was safe.

It returns `2` rather than a score in three situations, and the third is the one that catches
real mistakes:

- the **grader or agent command changed** — two graders disagree on the same answer often enough
  that a cross-grader "regression" is mostly variance. It still prints the differences, labelled
  as information, and refuses to call them a verdict.
- **nothing comparable survived** at all.
- **something the baseline measured was not measured this time.** A case that used to pass and
  has now vanished, crashed, had its criteria edited, or lost its grader verdict is reported as
  **LOST**, and lost measurements block certification. This is not pedantry: deleting the failing
  case, or an agent that crashes on it, are the two cheapest ways to make a gate go green, and
  both used to exit `0`.

A criterion neither run has a verdict for is recorded as `null` and scored neither way.

### Where independence is required — and where it is not

**Only here, and only for the grader.** Phases 1–4 run on whatever single agent the person
already has, and that is fine: Phase 2 classifies *past* turns rather than grading its own
current work, and the independence in Phase 4 is the **human** writing `expected_signals`, not
a second model.

So a person with one CLI and no second vendor is **not blocked from any part of this skill.**

| They have | `--agent` | `--grader` | Independent? |
|---|---|---|---|
| A second vendor | their agent | the other vendor | ✅ |
| **Only one CLI** | their agent | **`none`** — a person grades | ✅ **strongest** |
| Only one CLI, someone nearby | their agent | `none`, and a **colleague** scores | ✅ strongest |
| Only one vendor, two models | `claude -p` | `claude -p --model sonnet` | ⚠️ weak — the script warns |

**`--agent none --grader none`** — a person pastes the answer and a person grades it, criterion
by criterion. Nothing leaves the machine. That is a *better* run than a same-model one, not a
worse one.

The requirement was never "two vendors". It is: **the party that proposed the change must not
be the party that scores it.**

## Phase 6 — Report and hand over

Write `improve/REPORT.md`: the funnel counts, precision, clusters kept and cut with reasons,
cases written, **the scored result**, and — explicitly — **what this pass could not see**
(see `references/trace-formats.md` → *Known limits*).

Write that section against the **whole** of *Known limits*, not a favourite pair — and not as a
link. Name the ones that actually bit this corpus, and say what each means for the list you just
produced. A short candidate list reads as good news unless you say why it might not be.

**If this pass was requested because someone asked about cost, latency or wasted work, say
plainly that `/team-improve` did not measure that.** Then either attach a separate pass with a
denominator and real numbers (`references/execution-waste.md`), or state that this run cannot
answer the question. A pointer to a procedure nobody ran is not an answer.

Close with the three conditions a change must meet before it becomes permanent behaviour:
**a named human · a versioned diff · a number on a frozen set the proposing agent did not
score.** Name which of the three the team does not yet have.

Report findings, not just the score. **Read the findings before the total.** A criterion that
fails twice for the same reason is a result; a total that moved by one point is within grader
variance. Neither is automatic — a finding can fail to replicate too, and a score *is*
reproducible if you hold the model, the prompt and the case set fixed. Say which you did.

## Rules

- Question budget: at most 5, and the `expected_signals` conversation does not count — that
  is the deliverable, not overhead.
- Never promote. Never edit active behaviour. Staging and cases only.
- Show every file's substance before writing it.
- **Verify every write by reading it back**, and say so. Silent write failures are the
  documented way this class of loop dies: a store reports success, the file never exists,
  and the correction is lost for months while everyone believes it was saved.
- Quote people verbatim and date every episode. No episode → no candidate.
- If a candidate contradicts a ratified principle in `decisions.md`, flag it and stop. That
  is an escalation for a human, not a staging decision.
- Report precision as a fraction, never as an adjective.
