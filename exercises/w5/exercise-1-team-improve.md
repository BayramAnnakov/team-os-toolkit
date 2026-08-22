# Exercise 1 — Build the loop that improves your agent

**Time:** 50 minutes · **Dispatch by minute 55, hard.**

## You pass when you have

**A scored run.** Three cases, criteria **you** wrote, run against your agent, graded by a
**different** model than the one that proposed them — and a results file with a number in it.

Staged notes are not learning. A number nobody else produced is the deliverable.

---

## Pick your tier now, in 30 seconds

| Tier | You have | Do this |
|---|---|---|
| **0** | Claude Code or Codex on this machine | Your own logs |
| **1** | A deployed agent (Robin, a bot, a tracker agent) | Its export — see *Other agents* |
| **2** | A locked laptop, or logs you must not open | **The sample set.** Same exercise |
| **3** | No terminal | Paper. Jump to *Tier 3* |

**Bank, fintech, regulated → Tier 2.** You lose nothing that is graded.

> **Be precise about what leaves the machine.** Steps 1–2 are fully local: the extractor and
> your candidate file never leave your disk. **Step 3 is not local** — scoring sends the
> *question* and the *agent's answer* to two model vendors. It does not send your logs. If even
> that is not allowed, use `--agent none` and have a **person** grade it. That is a legitimate
> run, and on some teams it is the better one.

---

## Setup (2 min)

Already have the toolkit:

```bash
cd ~/GH/team-os-toolkit && git pull
```

Don't have it, or can't find it:

```bash
git clone https://github.com/BayramAnnakov/team-os-toolkit.git
cd team-os-toolkit
```

> ⚠️ **`git pull` is not enough — quit Claude Code and start it again.** Skills are read once,
> when a session starts. Pull into a running session and `/team-improve` sits on disk invisible
> to it. This costs ten minutes if you skip it.

Everything below runs **from inside `team-os-toolkit`**. The sample traces are committed — you
do not need to build them.

---

## Step 1 — Extract (3 min)

**Tier 2 (sample):**

```bash
python3 .claude/skills/team-improve/scripts/extract_candidates.py \
  examples/sample-traces/traces -o candidates.jsonl
```

**Tier 0 (your logs):**

```bash
python3 .claude/skills/team-improve/scripts/extract_candidates.py \
  ~/.claude/projects --since 2026-06-01 --max-files 300 -o candidates.jsonl
```

> `--max-files` matters. Files are read newest-first, so a big cap can still cut the calendar
> spread you need — a pattern that repeats monthly is only visible across months. If you get
> fewer than ~15 candidates, raise it.

Read the funnel it prints. **Post the "eligible" number in chat.** Checkpoint 1.

---

## Step 2 — Judge and cluster (20 min)

Paste this. Change only the path.

```
/team-improve

Traces: candidates.jsonl (already extracted).
My Team OS repo: <path, or "none — write locally">.

Judge each candidate against what the agent said immediately before it.
Do NOT search for negation words. Real corrections are polite — if your method
scores "could you double-check that?" as zero, your method is wrong.

Cluster by root cause, not by wording. Stage candidates. Cut the ones that will
not transfer, and show me what you cut and why.

Then propose cases and STOP. I write expected_signals, not you. You may suggest
one only if you can quote a person in the trace saying it — show the quote.

Report precision as a fraction.
```

**No `/team-improve`?** The skill lives in the repo you just pulled. If your setup does not
load it, open `.claude/skills/team-improve/SKILL.md` and paste Phases 2–4 as your prompt.
Nothing is lost.

### Two things the mining will get wrong. Expect both.

**It will hand you something that looks like a rule and is not.** An explicit "never do X"
with a reason attached is often tied to one destination, one audience, one day. Ask: *would
this still be right for a different reader next month?* If not, cut it — and say so out loud.

**A human correction can itself be wrong.** You will see one at the start of today's session:
the amendment that caused a 53-day defect was written by a person, deliberately, for a good
reason. Frequency is not correctness, and the loudest correction is not the truest.

---

## Step 3 — Write the criteria and SCORE (20 min) ← the deliverable

When the agent asks for `expected_signals`, **that is the exercise.**

Assert behaviour, never values:

- ✅ *"Returns a number, excludes internal accounts, names the source table"*
- ❌ *"Returns 361"* — true this week, false next week. Mark those `is_ephemeral: true`.

Add **two cases the mining cannot give you**:

- **One negative case** — something your agent must **refuse**: say "not in the repo", ask
  for clarification, decline to guess. Only positive cases cannot tell a helpful agent from
  one that confabulates. *It fires AND it stays silent*, applied to evals.
- **One case your agent did not propose.** It chose which failures you saw; that choice
  carries its blind spot.

> **Where to find one:** look at the sessions the miner returned **nothing** from. Someone
> asked, the agent answered, and the person never replied. That is either a perfect answer or
> a person who gave up — **and the log cannot tell you which.** The miner's silence is
> evidence too.

Then run them:

```bash
python3 .claude/skills/team-improve/scripts/run_cases.py improve/cases \
  --agent 'claude -p {q}' \
  --grader 'cursor-agent -p --mode ask --trust --model cursor-grok-4.6-high --output-format text {q}'
```

`--agent` is **whatever you want to test.** `claude -p` tests your coding agent. To test your
*team's* agent instead, put its command there — or use `--agent none` and paste its answer from
Telegram/Slack by hand. **That is the path if your agent is not a CLI**, and it is the one most
of you should take.

**Agent and grader must be different vendors.** A judge measurably prefers its own family's
output, so a same-model grade is not independent. The script warns you if they match.

No second vendor? Use `--agent none` and paste the answer by hand — you still get a graded
result. A case with empty `expected_signals` is reported **UNGRADED**, not passed.

---

## Checkpoint — post in chat

Counts and shapes only. **No content from your logs.**

```
eligible: N   ·   real corrections: M/N
staged: X   ·   cut: Y  (one word why)
scored: 3 cases, C/S criteria met   ·   grader: <vendor>
```

---

## Time warning

**Minute 35: stop mining.** Whatever you have is enough. Everything after that is criteria
and the run. A perfect cluster list with nothing scored is the failure this session is about.

---

## Persona notes

- **Regulated / enterprise:** Tier 2 for the mining, **your real agent for the scoring**.
  Then take one question home: *who in my org is allowed to promote a change to an agent's
  permanent behaviour?* If the answer is "nobody decided", that is your finding.
- **Speed / scale:** add the counter you will actually watch — **human override rate per
  duty, per week**. Not a score. A count of times a person had to step in.
- **Founder / builder:** point it at your product's agent, not your dev sessions. Customer
  corrections are the same data with better stakes.

---

## Fast finishers

1. **Run the same cases twice.** Different results? Then one run was never evidence. Use
   `pass^k`, not `pass@k`, for anything that must work every time.
2. **Grade once more with a third vendor.** Where graders disagree is where your criteria
   are vague — not where the models are.
3. **Retire something.** Find one rule in `decisions.md` or `CLAUDE.md` that has gone stale.
   Deleting a wrong rule beats adding a right one.

---

## Other agents (Tier 1)

Export history to JSONL, one object per line:

```json
{"role": "assistant", "text": "...", "ts": "2026-08-01T10:00:00Z"}
{"role": "user", "text": "could you double-check that?", "ts": "2026-08-01T10:01:00Z"}
```

Point the extractor at that file. Full notes: `.claude/skills/team-improve/references/trace-formats.md`.

---

## Tier 3 — paper, 15 minutes, still passes

1. Write down **three times this month you told your agent the same thing twice.**
2. For each: the question that reproduces it, and **two things a correct answer must
   contain.** Those are your criteria.
3. Add one thing it must **refuse**.
4. Ask the person next to you to be the grader. Read them your criteria, read them the
   agent's last answer, let *them* score it. That is the whole point, done with a human.
5. Post the counts in chat.
