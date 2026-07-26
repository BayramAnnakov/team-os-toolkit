---
name: synthetic-interviews
description: "Run a synthetic user panel against a prototype, a flow, or a concept — personas built from YOUR team's brain, each walked step by step until they give up, with every finding split into what a real session would also have found versus what the model is guessing. Use when someone wants synthetic user interviews, to test a prototype before showing it to real users, to pressure-test a concept, or asks 'what would our users think of this?'. Deliberately does NOT do quantitative survey research — see the handoff at the end."
effort: high
---

# Synthetic Interviews — a panel that tells you what it's guessing

Walk a prototype (or a concept) as several distinct users, find where each one stops, and — the part
that makes this usable — **separate what a real session would also have produced from what the model
is pattern-matching out of training data.**

A synthetic panel that returns a clean, confident report is worthless, because a clean report reads
exactly the same whether the product is good or the panel is blind. The entire value of this skill
is in the second list.

## The one rule that makes this work

**The panel must not share context with whatever built the artifact.** A model that just wrote the
prototype — or read its spec, or heard the reasoning — will walk it sympathetically, because it
already knows where everything is and why. That isn't a user; that's the author with a different hat.

So: **spawn each persona as its own sub-agent, and give it only the artifact and its own persona
card.** No spec. No changelog. No design rationale. No previous persona's findings.

**"Give it only X" is not enough on its own** — that describes what you *paste*, not what the
sub-agent can *reach*. An agent with file tools can go read the spec, the brain, `decisions.md`, or
the previous persona's output, and a polite instruction won't stop it. A contaminated report looks
exactly like a clean one, so you will never find out.

**Use a sub-agent type with no filesystem access.** This toolkit ships one for exactly this purpose —
**`no-tools-reviewer`**, defined in `.claude/agents/no-tools-reviewer.md` right next to this skill, with
`Read`, `Bash`, `Grep`, `Glob`, `Write`, `Edit` and `WebFetch` all explicitly disallowed. Use it, or any
equivalent with tools stripped. Make the isolation *structural*, not promised.

**Verify it actually applied — don't assume.** After the run, check that each persona made **zero tool
calls**. A persona that "didn't need to look anything up" and a persona that *couldn't* are
indistinguishable in the output, and only one of them is evidence. If the agent type turned out to be
unavailable and the personas ran in your own context, **say so in the report and label the whole run as
weaker evidence** — a contaminated report looks exactly like a clean one, so nobody will catch this for
you. Never run all the personas in one shared context and call it a panel.

## Phase 0 · Find the team's brain

Same discovery as the rest of the toolkit — look in the working directory, then any path the user
names, then one level up:

| Role | Common locations |
|---|---|
| Who it's for | `product/01-personas-icp.md`, `*/personas*`, `cohort/`, `*/roster*` |
| The exact words | `product/02-glossary.md`, `course/glossary.md`, `*/glossary*` |
| Real states | `product/03-object-model.md`, `*/object-model*` |
| What exists | `product/05-features.md`, `*/features*` |
| How we decide | `decisions.md`, `course/decisions.md` |
| Current focus | `now.md` |

Report the inventory in one line, then move.

### Before anything else: is the packet the whole artifact?

**The most expensive failure in this skill is not a wrong finding — it is a confident finding about
something that simply wasn't in front of you.** A panel handed 4 of 9 screens will report, in good
faith, that a feature is missing. It reasoned correctly; you gave it a hole.

So, before the personas run, establish the boundary and **write it down**:

- What screens/states *should* exist — from the spec, the route list, the Figma page, the story list?
  **If there is no spec, no route list and no passport at all — that is the gate failing, not the gate
  being inapplicable.** Write "a scope document was expected here and none exists," and treat every
  "X is missing" finding as doubly unresolved. The tempting move is to skip this section because
  there is nothing to compare against; that is exactly when a panel invents boundaries and reports
  them as observations.
- Which of those are actually in the packet you're about to pass?
- Anything absent: name it explicitly as **out of scope for this run**, and treat any finding that
  amounts to "X is missing" as unresolved until you've checked X wasn't simply withheld.

Then say it in the report, up front:

> `Packet covers 4 of 9 known states (missing: Replied, Invite scheduled, Message scheduled).
>  "Missing feature" findings below are bounded by this and may be packet artefacts.`

This is stricter than the "say what nobody reached" rule later on, and it comes first: that rule
assumes you know where the edges are. Here the edge itself is invisible — which is exactly why it
has to be established before the run, by you, not discovered afterwards by an annoyed reviewer.

**No brain?** Say so plainly — *"No personas found; I'm inventing three from the artifact itself,
which makes every finding below weaker."* — and continue. Never stall.

## Phase 1 · Build the personas

**Three, by default.** More than four produces mush; fewer misses the spread.

Each persona gets a card, and the card is the ONLY context that sub-agent receives besides the
artifact:

```
NAME / ROLE:      <from the brain's personas where they exist>
GOAL RIGHT NOW:   <one sentence — what they came to do, not who they are>
CONTEXT LEVEL:    <what they already know: everything / the basics / nothing>
STATE OF MIND:    <calm · in a hurry · already annoyed>
WHAT THEY'D DO INSTEAD: <the manual workaround they'd fall back to>
```

**One of the three must be hostile or in a hurry.** Panels default to agreeable users and agreeable
users find nothing. If the brain's personas are all happy, say that out loud — it is itself a finding
about the brain.

**Vary the goal, not the costume.** Two personas with different names, ages and job titles who both
want the same thing are one persona in two outfits, and they will produce one set of findings twice.
Split on *what they came to do* — and if two real users in your brain have been merged into a single
persona because they look alike, splitting them is itself a fix to the brain. (That has happened: a
panel run surfaced two distinct users collapsed into one card in the team's own personas doc.)

**And one must be on a *successful* path**, not a broken one. Coverage is a function of persona
*goals*, not persona count: three people all chasing a stuck payment will all ignore the completed
one, and whatever is broken about the happy path goes unseen by the entire panel. Give someone a goal
that ends in "and it worked."

**Derive from the brain, don't invent.** If a persona detail isn't in the brain, either leave it out
or mark it invented — field by field, naming the source. A panel built on invented users produces
invented findings, and you want to know which ones those are.

**Never put the answers in the persona card.** The card carries who they are, what they came to do,
and how they feel — **never the content of a policy, a rule, or a known defect.** If you tell a
persona *"the approval threshold is unconfirmed"* and it then objects to seeing a hard number on the
page, that is **your** finding wearing a persona's voice, not a discovery. The panel's job is to hit
those things cold, the way a real user would. A card that contains the answer key produces a report
that confirms whatever you already believed — which is the exact failure this skill exists to avoid.

## Phase 2 · Walk it, one persona at a time

**First decide what the persona actually receives — this determines whether the run is worth
anything.** A tool-less sub-agent cannot open a browser, so you have two modes:

- **Rendered (strong) — *if* your sub-agent dispatch tool accepts image attachments. Check that
  before you rely on it; in many harnesses it does not.** *You* open the artifact, screenshot the
  relevant states, and pass the persona **the images plus the visible text**. This is what a user
  sees, so findings are directly comparable to a real session.
- **Rendered-text (the realistic middle, and usually what you actually get).** If you cannot attach
  images, open the artifact in a real browser, drive it, and extract the **rendered visible text** —
  a page-text tool, *not* the raw HTML — then pass that. This is meaningfully stronger than
  source-only: no sample-data array, no CSS, no unclicked FAQ answers leak in. But **no persona can
  then see colour, layout, what is above the fold, or anything on a phone** — so any defect that
  lives in the pixels is invisible to the entire panel, and you must **say that in the report**
  rather than quietly downgrading. Found the hard way: a run in this mode missed a completed item
  rendered in the palette's *in-progress* colour — plainly visible on screen, unreachable from text.
- **Source-only (weak, and you must say so).** You paste the HTML. The persona now **sees what no
  user sees** — the sample-data array, every FAQ answer without clicking, the CSS, the exact JS
  behind a bug — and **cannot see what every user sees**: layout, colour, what's above the fold,
  what it's like on a phone.

> ⚠️ **In source-only mode, any finding that could only have been made by reading code or unrendered
> data goes to List B, no exceptions.** A real user does not read your `filter()` call. Findings that
> arrive with a mechanism attached are the tell. Skipping this quietly inflates List A with things no
> session would ever produce — which corrupts the single thing this skill exists to protect.

Give each persona sub-agent this instruction:

```
THE ARTIFACT:
<screenshots + visible text — or, in source-only mode, the raw HTML and a note saying
 you are reading source, not a rendered page>

You are <persona card>. You have never seen this before and you know nothing about how
it was built.

Walk through the artifact step by step, trying to accomplish YOUR goal. At every step say:
  - what you expected before you looked
  - what you actually see
  - whether you continue, or stop

STOP at the first point you would genuinely give up, close the tab, or message someone
instead. Do NOT push through politely. Do NOT explore helpfully once you're stuck. Real
people leave, and where they leave is the finding.

For every problem you hit, quote the exact text or element that caused it. A finding that
cannot point at something on the screen is not a finding.

If you get all the way through, say so plainly — a clean run is a real result, not a
failure to be helpful.
```

**Interviewing a concept instead of a prototype?** Same structure, but the artifact is a description,
and you must be much more sceptical of the output: reactions to a *described* idea are the weakest
thing a synthetic panel produces, because there is nothing concrete to fail against. Say that in the
report rather than burying it.

## Phase 3 · The split — this is the deliverable

Collect the personas' findings and sort every one into exactly one of two lists.

**List A — a real session would also have produced this.**
Grounded in something observable: a missing control, an unlabelled state, a dead end, a term that
contradicts the glossary, a number the team's decisions forbid. Each carries its evidence quote.

**List B — I am guessing.**
Anything resting on how a person *feels*, what they'd *pay*, whether they'd *come back*, whether
they'd *trust* it, or how they'd *compare* it to a competitor. Also anything you produced from
generic UX priors rather than from this artifact.

Be ruthless about B. **A short, honest A-list beats a long confident one.** If you find yourself
arguing that something belongs in A, it belongs in B.

**Deduplicate, and count instead.** When two or three personas hit the same wall, that is **one
finding with a strength of 3**, not three findings. Listing it once per persona inflates the A-list
and makes a narrow panel look thorough. The count is the useful part — something all three hit
independently is the strongest signal the instrument produces.

**Say what nobody reached.** Every persona stops where they give up, which is honest and also means
whole regions of the artifact were never touched. Name them: *"no persona got as far as the export
flow, so this panel says nothing about it."* An unexplored area silently reads as a clean one.

**Keep the finding and the fix in separate columns.** Reviewers will ask "so what should I do?" —
and they should get an answer — but a direction is *your* judgment, while the finding is the
panel's evidence. Blend them and a reviewer arguing with your suggested fix will throw out the
observation underneath it. So:

| Finding (what a persona hit, with its quote) | Direction (a suggestion, not evidence) |
|---|---|

**Group by screen, and put the callout on the pixel.** A list sorted by severity makes whoever has
to fix it reassemble the map themselves. Annotate the screenshots directly, so the person looking at
the design sees the finding on the thing it points at.

Then, explicitly:

> **What I fundamentally cannot evaluate here:** <one or two things, named>

## Phase 4 · Make it checkable later

Write `synthetic-panel-<date>.md` containing the personas, both lists, and this header:

```
PREDICTIONS — to be scored against a real session later
| # | Finding (list A only) | Confirmed by a real user? |
|---|---|---|
```

This is what turns the panel from an opinion into an instrument. The next time a real person touches
this artifact, score the rows. A panel whose A-list keeps getting confirmed has earned more trust;
one that doesn't, hasn't — and now you know, instead of guessing.

## What this skill will not do

**Quantitative research** — purchase intent, price sensitivity, concept scoring across a sample,
anything with an N and a percentage. This skill produces three walkthroughs, not a survey, and
reporting "67% of users would buy" off three synthetic personas is fabrication with a decimal point.

For that job the validated approach is **Semantic Similarity Rating** (PyMC Labs; ~90% correlation
with human responses across 57 surveys) — see the `synthetic-market-research` skill if it's
available, or the published method. Different instrument, different question.

**The honest boundary, worth stating in the report:** synthetic panels are strong on **coverage** —
they walk every path, never get bored, never get embarrassed, and cost nothing at 3am. They are weak
on **surprise** — they produce the misunderstandings that are common in the training data, not the
one your actual customer has because of how your actual product taught them to think.

Use a panel so you never waste a real person's thirty minutes on a broken button. Not so you never
talk to one.
