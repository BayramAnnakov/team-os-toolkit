# Exercise 1 (HERO) — From a rule you wrote to a rule that stops you

> ~40 min. You leave with **one hook that blocks**, enforcing a decision your team actually
> ratified — plus the screenshot that proves it fires on the wrong thing and stays quiet on the
> right thing.
>
> ✅ **You "pass" on ANY tier below when you have BOTH halves:**
> **(1) a screenshot of your guard FIRING** on a prompt that should be caught, and
> **(2) a screenshot of it STAYING SILENT** on a prompt that should not.
>
> One without the other isn't a check — it's either theatre or a nuisance. The second screenshot
> is the one people skip, and it's the one that decides whether your team keeps the hook or rips
> it out by Thursday.
>
> **No `decisions.md` from W2?** Fine. Tier 1 below hands you a rule to enforce.

---

## Why this, today

In W2 you wrote down what your team decides. In W3 an independent critic read those decisions
and graded work against them — and it *told* you when you'd violated one. Advice.

Today the same rule stops the work.

That is the entire distance between session 2 and session 4: **advisory → enforced**. Nothing
about the rule changes. What changes is whether ignoring it is possible.

---

## Setup (2 min)

```bash
cd team-os-toolkit          # cloned in W1; if not: git clone https://github.com/BayramAnnakov/team-os-toolkit && cd team-os-toolkit
git pull
claude                      # ← START IT AFTER THE PULL
```

> 🔴 **If Claude Code is already open, quit it and start it again after the pull.** Hooks are read
> from `settings.json` when the session starts. Same trap as W3: pull into a running session and
> your hook is on disk and invisible.

You need a repo with a `.claude/` directory. Your Team OS repo is ideal. Any git repo works.

---

## Step 1 · Pick ONE rule (3 min)

Not a good rule. A rule you have **already re-explained to someone twice**.

Best source: an entry in your `decisions.md`. Second best: a finding the W3 evaluator gave you
that you agreed with. Third: the table below.

| Your recurring question | The rule worth enforcing | What the guard catches |
|---|---|---|
| *"Do we have a component for X already?"* | Don't add a component without checking the design system first | A prompt asking to build UI with no evidence the inventory was searched |
| *"What does this number mean?"* | Every metric ships with its definition, source and owner | A dashboard/metric change that names no provenance |
| *"Which insight do I escalate?"* | Insights reach a client deck only through the triage rule | Content headed for a client artifact with no triage step |
| *"Where do we focus this week?"* | Nothing gets added to the week without naming what it displaces | "let's also do X" with no trade named |
| Internal agent / knowledge base | **No principle is promoted to the knowledge base without a human ratifying it** | An auto-promotion of a "decision" nobody ruled on |
| Nothing comes to mind | **Take D-03** (below). It's ratified, it's ours, and it has a live bug attached. |

> **The last row is not a consolation prize.** Our own `decisions.md` says **D-03 — *if the vendor
> documents a way, use the documented way*.** We then improvised a symlink instead of reading the
> docs. That symlink currently arrives on Windows as **a 9-byte text file**, making the whole brain
> invisible to anyone who checks out without symlink support. It is an open item in the repo right
> now. **A hook enforcing D-03 would have caught it at the prompt that proposed it.**

Write your rule as one sentence before you touch a keyboard. If you can't, that's the finding —
it isn't a rule yet, it's a preference.

---

## Step 2 · Generate the guard — ADVISORY (8 min)

Paste this into Claude Code, replacing only the two bracketed lines:

```
Build me a UserPromptSubmit hook for this repo that enforces one decision.

THE RULE: [one sentence — the rule you picked in Step 1]
IT SHOULD CATCH: [what a prompt looks like when someone is about to break it]

Requirements:
- Write .claude/hooks/decision-guard.sh plus the .claude/settings.json snippet to wire it.
- Read the hook payload from stdin. **Do not guess the field name — dump a real payload first**
  and read the key off it. Getting it wrong makes the hook silently never fire, which looks
  identical to a hook that works. (We got this wrong ourselves: the published docs named a field
  that isn't the one Claude Code actually sends. See the box below.)
- Two modes via an env var: advise (print the nudge to stdout, exit 0 — the prompt still runs)
  and enforce (print to stderr, exit 2 — the prompt is blocked).
- Default to advise.
- Bilingual: match Russian and English phrasing of the same intent.
- An EXEMPT pattern: if the prompt already shows the person did the thing the rule asks for,
  stay silent. Say out loud what your exempt pattern is.
- Header comment carrying owner / tier / last_reviewed.

Then give me FOUR test payloads I can pipe in by hand: one that must fire, one ordinary prompt
that must stay silent, one that trips the trigger but satisfies the exemption and must stay
silent, and one in Russian that must fire.
```

A worked, tested example sits next to this sheet at **`exercises/w4/decision-guard.sh`** — copy it and swap the
`TRIGGER` / `EXEMPT` patterns if you'd rather start from something that already runs.

> 🔴 **Verify the field name against a real payload.** It is the most common way a hook fails
> silently. The fastest route is to ask Claude to do it:
>
> ```
> Dump one real UserPromptSubmit payload for me: write a hook that saves stdin to payload.json,
> wire it in .claude/settings.json, tell me to restart you, and then show me the JSON.
> ```
>
> Or do it by hand — both files, nothing to fill in:
>
> ```bash
> mkdir -p .claude/hooks
> printf '#!/usr/bin/env bash\ncat > "$CLAUDE_PROJECT_DIR/payload.json"\nexit 0\n' \
>   > .claude/hooks/dump.sh && chmod +x .claude/hooks/dump.sh
>
> cat > .claude/settings.json <<'JSON'
> { "hooks": { "UserPromptSubmit": [ { "matcher": "*", "hooks": [
>   { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/dump.sh" } ] } ] } }
> JSON
> # now restart Claude Code, send any prompt, then:
> cat payload.json
> ```
>
> **We did exactly this on 2026-08-08 and the answer was `prompt`** — while the published docs said
> `user_input`. The docs were wrong. Yours may differ again by the time you read this, which is
> precisely the point: **a guard built on a field name nobody verified is a guard that exits 0
> forever and looks like it's working.**

---

## Step 3 · Watch it fire (5 min) — this is the exercise

A hook you have not seen fire is a hook you do not have. Test it **by hand**, before trusting the
harness:

**These run as-is against the shipped D-03 guard.** If you wrote your own rule, swap the quoted
text — everything else stays.

```bash
chmod +x .claude/hooks/decision-guard.sh

# 1. MUST FIRE
printf '{"prompt":"Lets just symlink AGENTS.md so both tools see it"}' \
  | DECISION_GUARD_MODE=advise .claude/hooks/decision-guard.sh; echo "exit=$?"

# 2. MUST STAY SILENT — an ordinary request
printf '{"prompt":"add a column to the roster table"}' \
  | DECISION_GUARD_MODE=advise .claude/hooks/decision-guard.sh; echo "exit=$?"

# 3. MUST STAY SILENT — trips the trigger, but the rule was already satisfied
printf '{"prompt":"the vendor docs document an @AGENTS.md import - use that instead of a symlink"}' \
  | DECISION_GUARD_MODE=advise .claude/hooks/decision-guard.sh; echo "exit=$?"
```

Expected: **#1 prints, #2 and #3 print nothing, all exit 0.**

*(Verified on macOS + Linux, bash and zsh, with and without `jq` installed — the script falls back
to `python3` when `jq` is missing. Quotes inside the prompt text are fine.)*

Now the real thing — restart Claude Code and type the offending prompt. The nudge appears above
your prompt and the prompt still runs. **Screenshot that.**

> **If it doesn't fire:** check the field name against a real dumped payload, check `chmod +x`,
> check that you restarted Claude Code after editing `settings.json`. In that order — the field
> name is the usual culprit, by a wide margin.

---

## Step 4 · Flip to enforced (5 min)

Only now. Set the mode to `enforce` in your `settings.json` snippet and try the offending prompt
again. This time the prompt does not run at all — the guard's message comes back as an error and
your text is gone.

```bash
printf '{"prompt":"Lets just symlink AGENTS.md so both tools see it"}' \
  | DECISION_GUARD_MODE=enforce .claude/hooks/decision-guard.sh; echo "exit=$?"
# expect: the message, then exit=2
```

> **`exit=2` is the success condition here, not an error.** Exit 2 is how a hook says *block* —
> Claude Code takes the stderr text and feeds it back as the reason. If you're running this inside
> a script with `set -e`, the script will stop on that 2; that's your shell being helpful, not the
> guard failing.

**Screenshot the block.** That's your artifact.

**This is exactly what success looks like in a real session** (captured 2026-08-08 — the offending
prompt, then an innocent one, same guard, `enforce` mode):

```
$ claude -p "lets just symlink AGENTS.md to CLAUDE.md"
UserPromptSubmit operation blocked by hook:
[...decision-guard.sh]: ⚖️  D-03 — If the vendor documents a way, use the documented way.
   You're proposing a mechanism of our own. Before we build it:
   check whether the vendor already documents one, and say what you found.

Original prompt: lets just symlink AGENTS.md to CLAUDE.md

$ claude -p "reply with the single word OK"
OK
```

**Both halves, in the real harness.** The offending prompt never reached Claude; the innocent one
was untouched. That pair — not the block on its own — is the thing to screenshot.

> ⚠️ **Do not skip Step 3 to get here faster.** Constraint progression — advisory first, enforced
> after — is not politeness, it's how you find your false-positive rate before it costs somebody
> their afternoon. Ship enforced on day one and your team learns to resent the guard, then
> disables it, and you are back to a rule nobody follows with extra steps.

---

## ✅ Checkpoint — post in the Zoom chat

```
[your name] — guard on: [rule in 5 words] · fires ✅ / silent ✅ / mode: advise|enforce
```

Post the two screenshots if you can. **Both halves, or it doesn't count.**

---

## ⏱ Time warning

**At the 25-minute mark**, whatever state you're in: stop generating and run the three hand tests
on what you already have. A crude guard you have *seen fire* beats an elegant one you haven't.

---

## Fallback ladder — pick your tier

- **Tier 0 — your own repo + your own `decisions.md`.** The main path above.
- **Tier 1 — no decisions of your own yet.** Use **D-03**, and **`exercises/w4/decision-guard.sh`**
  in this repo, which already enforces it. Copy it into your own repo and run Step 3. You still
  leave with a working guard; it just enforces our rule instead of yours.
  - ⚠️ If you got this file as a chat attachment rather than via `git pull`, it is **not
    executable**. Either `chmod +x decision-guard.sh`, or call it as `bash decision-guard.sh` —
    the second needs nothing.
- **Tier 2 — no Claude Code, but you do have a terminal.** A hook is *just a shell script that
  reads JSON on stdin*, so the harness is optional. Write the script in any editor and test it with
  the three `printf | script` commands above — **you see the exit code with your own eyes, which is
  the whole lesson.** Wire it into `settings.json` later.
  - **On Windows:** use **Git Bash** (ships with Git for Windows). PowerShell will not run these.
  - You can't dump a live payload here, so take ours: **the field is `prompt`, verified
    2026-08-08** — and re-verify it the day you do get the harness, because that is exactly the
    step the published docs got wrong.
- **Tier 3 — no terminal at all, or no time.** On paper, and **this still passes**: write the rule
  in one sentence, then the two prompts — the one it must catch, and the one it must let through.
  **Bring that pair to the checkpoint and we run it against the shared guard on screen**, so you
  see your own rule fire and stay silent without installing anything. That pair *is* the design
  work; the script is the easy half.

**The bar on every tier is the same: it fires on the wrong thing, and stays silent on the right
thing, and you have seen both happen.**

---

## Fast finisher? Pick one

1. **Move up the lifecycle.** `UserPromptSubmit` catches intent. Try `PreToolUse` — it catches the
   *action*, which is where irreversibility lives. What does your rule look like as a gate on
   `Bash` or `Write` rather than on a prompt?
2. **Swap the handler type.** Your guard is a regex, so it is brittle by construction. Claude Code
   also supports a `prompt` handler — a fast model judging the same question semantically, no
   regex. Convert it and compare false positives on the same test payloads.
3. **Make the exemption teach.** Right now the guard says "no". Make it say "no, and here's the
   documented way" by having it read `decisions.md` and quote the rule it's enforcing, by ID.
4. **Run it against last week.** Take ten real prompts from your history and score the guard:
   how many true fires, how many false? That number is your golden set, and it's W4's other half.

---

## Reference — where a rule can be enforced

The course page promised you six control points. There are, as of today, **31 hook events** in
Claude Code — the surface grew faster than the slide. These are the six that carry a workflow, and
every one of them can block:

| Event | Fires | The question it answers |
|---|---|---|
| `UserPromptSubmit` | before the work starts | *Did you run the loop before deciding?* |
| `PreToolUse` | before an action executes | *Is this irreversible, and is it allowed?* |
| `PostToolUse` | after an action succeeds | *Did the result drift from our standard?* |
| `PostToolUseFailure` | after an action fails | *Are we about to claim success anyway?* |
| `SubagentStop` | when a delegated worker finishes | *Did the critic actually approve this?* |
| `Stop` | when the turn ends | *Is it finished, or does it just look finished?* |

`SubagentStop` is W3 made mandatory: the independent critic you had to remember to run, turned
into a gate the work cannot get past.

**Payload field for `UserPromptSubmit` is `prompt`** — verified on 2026-08-08 by dumping a real
payload, *not* by reading the docs, which said something else. Blocking is **exit code 2** (stderr
goes back to Claude) or `{"decision":"block","reason":"…"}` on exit 0. **Re-verify before you
trust this sheet in three months.**
