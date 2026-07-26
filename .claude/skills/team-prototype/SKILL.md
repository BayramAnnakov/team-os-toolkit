---
name: team-prototype
description: "The prototyping layer of a Team OS. Turns a feature description into a working, publishable prototype, then autonomously improves it across independent Generator-Evaluator rounds — grading it against YOUR team's own glossary, personas and decision principles, not generic taste. Use when someone wants to prototype a feature, turn a spec into a clickable thing, get a live URL for a stakeholder, or test whether their team brain is good enough to build from."
effort: high
---

# Team Prototype — the prototyping layer

Build a working interactive prototype from a description, improve it through independent
evaluation rounds, and publish it to a URL someone else can open.

The difference from a generic prototype builder: **this one reads your team's brain.** The
vocabulary comes from your glossary, the users come from your personas, the sample data obeys
your object model, and the evaluation criteria are derived from the decisions your team already
made — cited by ID. An evaluator that says *"this contradicts D-01, ratified 2026-05-28"* is
doing something no generic critic can do.

You are the **Orchestrator**. You never build and you never evaluate — you manage the pipeline
and spawn independent sub-agents for both.

```
  YOU (Orchestrator)
    ├── reads → the Team OS brain (glossary · personas · object model · decisions)
    ├── spawns → Generator sub-agent  (builds; never sees the criteria)
    ├── spawns → Evaluator sub-agent  (critiques; never sees the Generator's reasoning)
    └── manages the loop — feedback flows through files only
```

## Interaction policy — read this before you ask the user anything

This skill is usually dispatched and left running. **Default to proceeding.** Do not block on
confirmations.

- If the user supplied criteria, a spec, or said anything like *"don't ask me"* / *"just run it"* /
  *"3 rounds"* — **ask nothing at all** until the loop is done.
- Otherwise you may ask **at most one** consolidated question, once, at the end of Phase 1 — and
  only if the brain gave you nothing to work from.
- If a choice is needed mid-run, make the most reasonable one, write it into
  `prototype-spec.md` under **Assumptions**, and keep going. Never idle waiting for a human.

## Phase 0 · DISCOVER THE TEAM OS

Before anything else, find out what context exists. Look in the working directory, then in any
path the user named, then one level up.

Search for these **by role, not by exact filename** — real brains vary:

| Role | Common locations |
|---|---|
| Router / entrypoint | `CLAUDE.md`, `AGENTS.md` (root) |
| What we're building | `product/00-overview.md`, `course/overview.md`, `README.md` |
| Who it's for | `product/01-personas-icp.md`, `cohort/`, `*/personas*`, `*/roster*` |
| The exact words | `product/02-glossary.md`, `course/glossary.md`, `*/glossary*` |
| Entities & states | `product/03-object-model.md`, `*/object-model*`, `*/data-model*` |
| What already exists | `product/05-features.md`, `*/features*` |
| **How we decide** | `decisions.md`, `course/decisions.md`, `*/decisions.md` |
| How we work | `principles.md`, `course/principles.md` |
| Current focus | `now.md` |
| Encoded judgment | `.claude/skills/decide-like-*/` |

Report the inventory in **one line**, then move on:

> `Team OS found: glossary (31 terms) · 8 personas · object model (4 entities) · 12 principles (5 ratified) · now.md 3 days old. Building from these.`

**No brain found?** Say so plainly in one line — *"No Team OS found; building from your
description alone. Criteria will be generic."* — and continue. The skill works without one; it
just has a lower ceiling. Never stop to ask for a brain that doesn't exist.

**Stale check.** If `now.md` or a `last_reviewed` is more than a month old, note it once and treat
specifics as possibly stale. Don't refuse to build.

## Phase 1 · CRITERIA — derive them from the brain

Evaluation criteria decide what "better" means, so they are the highest-leverage thing in the
loop. Build the set in this order.

**1. Three universal criteria (always):**
1. **Clarity** — is it understandable within 5 seconds?
2. **Visual Identity** — distinct and intentional, not a generic template?
3. **Interaction Completeness** — does every interactive element actually work?

**2. Up to three criteria mined from the brain.** Read `decisions.md` and `principles.md` and pull
out every rule that **constrains a user-facing artifact.** Convert each into something an
independent evaluator can check, and **keep the source ID**.

**Plenty of teams fold both into one file.** If there is no separate `principles.md`, that is normal
and not a problem — mine `decisions.md` and move on. Do not go hunting, do not stop to ask, and do
not tell the user their brain is incomplete because of it.

The mining test: *would a person who has never read this file be able to violate it while building
a screen?* If yes, it's a criterion.

| The team's rule | Becomes the criterion |
|---|---|
| "Refunds default to account credit except our billing error" (D-01, ratified) | **Policy fidelity (D-01)** — the flow never offers cash where credit is the default |
| "The $200 threshold is unconfirmed" (D-02, proposed) | **No unconfirmed number stated as fact (D-02)** — approval limits appear as "needs sign-off", never "$200" |
| "Cite your source; never invent" (principles) | **Provenance** — every number or claim on screen names where it came from |
| "Never promise a date we don't control" (voice) | **Honest dates** — ranges and owners, not fake precision |
| Glossary exists | **Vocabulary fidelity** — uses the team's exact terms, invents none |

**Be honest about what you couldn't use.** Many principles are about how a team works, not about
what a screen may say — those make bad criteria. Say so in one line:

> `Mined 2 criteria from decisions.md (D-01, D-02). Skipped 4 — they constrain process, not artifacts. Added 1 type-based criterion to fill the set.`

**3. Fill any remaining slots from the prototype type:**

| Type | Criteria |
|---|---|
| Landing / marketing | Competitive Differentiation · Persona Fit · CTA Effectiveness |
| Dashboard / analytics | Data Hierarchy · Scannability · Actionable Insight |
| Onboarding / wizard | Step Clarity · Progress Feedback · Error Recovery |
| Internal tool / admin | Efficiency (tasks per click) · Information Density · Navigation |
| Status / tracking | State Legibility · Expectation Setting · Dead-end Avoidance |
| Mobile layout | Touch Targets · Thumb Zone · Content Priority |
| Data visualisation | Readability · Representational Accuracy · Annotation |
| Form-heavy | Validation Feedback · Field Grouping · Completion Motivation |

**Vocabulary fidelity is mandatory whenever a glossary exists** — it is the cheapest, most
checkable brain-derived criterion there is, and the one teams most often discover they needed.

Cap the set at **6**, or **7** when a glossary forced the extra slot. More criteria means a mushier
signal, and the same failure mode the judgment layer warns about: too many principles means you
have none. Brain-derived criteria always outrank type-based ones — drop a type-based criterion
before you drop one of the team's own rules.

Write `prototyping-criteria.md` — each criterion with its source (`D-01` / `glossary` /
`type-based`) — and **proceed without waiting for confirmation** (see Interaction policy).

## Phase 2 · SPEC

Write a **one-page** `prototype-spec.md`:
- What this is (type, scope) and the **question it answers** — if you can't state what it tests or
  demonstrates, it's decoration, not discovery
- Who sees it — **named from the brain's personas** where they exist, with their actual goal
- Core screens (2-3 max) and key interactions (5 max)
- **Vocabulary** — the exact glossary terms this must use, quoted from the brain
- **Constraints from the brain** — the decision principles that bind this artifact, by ID
- **Assumptions** — every choice you made instead of asking

## Phase 3 · BUILD (Generator sub-agent)

Spawn a Generator with: `prototype-spec.md`, the relevant brain excerpts (glossary, personas,
object model, voice), and — from round 2 on — only the **latest** evaluation feedback.

```
You are a PROTOTYPE GENERATOR. Build a working interactive prototype from the spec.

Read: prototype-spec.md and the context files provided — and NOTHING ELSE.
Do NOT open any file whose name suggests criteria, evaluation, rubric, scoring or
review, even though you will see one sitting in this directory. Building to the rubric
is the one thing that invalidates this run. If you notice such a file, say so and
leave it closed.
[Round 2+] Read the evaluation feedback and implement its top 2 fixes.
[Round 2+] Also make ONE creative enhancement the evaluator did not ask for.

If the frontend-design skill is available, use it — it avoids the default template look
that kills Visual Identity scores.

Build as a multi-file project in prototypes/<name>/:
  index.html · styles.css · app.js
Use NO external fonts, stylesheets or CDN scripts — everything local. The prototype gets
published to a host that blocks external requests, and a CDN webfont silently degrades it.

SIZE: build the smallest thing that answers the spec's question — 1-2 screens. An
unrequested third screen is a defect, not generosity: every extra screen is another
screen the evaluator must verify, and scope creep costs a full round of wall clock.

Requirements:
- Every interactive element must actually work — no dead buttons, no href="#" placeholders.
- Use the team's exact vocabulary from the glossary. Invent no terms.
- Sample data must obey the object model: real-looking entities in valid states.
- Respect the voice notes. Do not write cheerful copy about someone's money.
- Responsive: usable at 375px wide.

[Round 2+] Write iteration-N-changelog.md: what changed and why.
```

**The Generator never receives:** the evaluation criteria, the Evaluator's reasoning or scoring
method, other iterations' code, or your orchestration notes.

> Withholding the criteria is deliberate. A generator that is handed the rubric writes to the
> rubric, and round 1 stops being an honest measurement of what your brain alone produces.

> ⚠️ **"Never receives" describes what you PASS it — not what it can REACH.** The Generator runs
> with file tools in the same working directory as `prototyping-criteria.md`. Nothing stops it
> opening that file except the instruction above, which is why that instruction is inside the
> prompt block rather than in this commentary. If your harness offers a sub-agent type with no
> filesystem access, or you can run the Generator in a directory that does not contain the
> criteria, prefer that — **structural isolation beats a polite request.** This was found by
> running the skill, not by reading it: a Generator noticed the criteria file sitting next to it
> mid-build and only left it closed because it had been told to.

## Phase 4 · EVALUATE (Evaluator sub-agent)

Spawn a **fresh, independent** Evaluator — separate context, no access to the Generator's
reasoning, **and no previous evaluation scores.**

```
You are a PROTOTYPE EVALUATOR. You are independent and critical. You did NOT build this
and you have never seen it before.

RULES:
- Score honestly across the full range. A 3/10 is valid. A 2/10 is valid.
- Quote specific text or code as evidence for every score.
- Every criticism names WHAT to fix and WHERE.
- Do not praise effort. Judge only the output.
- When a criterion carries a principle ID, CITE THE ID in your finding — e.g.
  "violates D-01 (ratified): the refund flow offers cash as the default option."

Read: prototyping-criteria.md, the team brain files provided, prototypes/<name>/

PROCESS:
1. VISUAL REVIEW — open it in a browser, screenshot the initial state, one-sentence
   first impression.
2. FUNCTIONAL VERIFICATION (browser automation preferred) — click every button, link
   and control; verify what actually happens; screenshot broken states; resize to 375px;
   check for overlapping text, dead controls, console errors.
   Fallback without browser automation: read the HTML/CSS/JS and verify every handler
   has a function and every link a target — and say that you did it this way.
3. SCORING — for each criterion: score 1-10, quoted evidence, and the one fix worth
   2+ points.
4. SYNTHESIS → evaluation-round-N.md: the scores table, browser results, the top 2
   highest-impact fixes, a verdict (PASS = average ≥7 and nothing below 5), and
   ONE thing the Generator will not want to hear.
```

**Why no previous evaluations:** passing prior scores creates anchoring — the Evaluator adjusts
around its own last number instead of judging fresh. Comparing across rounds is the Orchestrator's
job, not the Evaluator's.

**Why the separation matters at all:** asked to evaluate their own work, agents confidently praise
it, even when it is obviously mediocre. Independence isn't politeness — it's the only thing that
makes the score mean anything.

## Phase 5 · THE LOOP

```
Round N:
  1. You read evaluation-round-(N-1).md
  2. Spawn Generator: spec + brain context + latest feedback only
  3. Generator → updated prototype + changelog
  4. Spawn Evaluator: prototype + criteria + brain ONLY (no prior evaluations)
  5. Evaluator → evaluation-round-N.md
  6. You compare scores across rounds; note improved / regressed / stalled
  7. PASS → Phase 6.  FAIL → round N+1.
```

- Minimum **3** rounds — the round-3 creative enhancement often produces the biggest leap
- Maximum **5** — quality plateaus; stop when scores stop moving
- Any criterion below 4 after round 2 → a focused round on that criterion alone
- **Communication is via files only.** No context leaks between Generator and Evaluator.

## Phase 6 · PUBLISH

A prototype nobody can open is not a prototype. Produce **a URL someone else can open**, and
verify it. Try these in order and stop at the first that works.

**A · Claude artifact** — fastest, works from Claude Code and from Desktop/web.

⚠️ **Inline first.** Phase 3 builds `index.html` + `styles.css` + `app.js`; an artifact is a
**single self-contained page** behind a strict policy that blocks external hosts. Publishing
`index.html` on its own yields an unstyled, scriptless document at a perfectly working URL — it
looks like a success and is not. Before publishing: fold the CSS and JS inline, and strip any
webfont or CDN link.

⚠️ **Keep `<meta charset="utf-8">` when you inline.** Collapsing the `<head>` is the easy way to
lose it, and the page then renders as mojibake wherever the host doesn't declare an encoding —
`—` becomes `â€"`, and **any non-Latin text is destroyed**. This is invisible to you if your
prototype is in English and catastrophic if it isn't. Verify the inlined file in a browser before
publishing: check a dash, a quote, and any non-ASCII word.

⚠️ **Artifacts are private by default.** Tell the user explicitly, in these words, that the link is
not yet open:

> Open the URL → **Share** (top right) → **General access** → change *"Only people with access"*
> to **"Anyone with the link"** → **Copy link**.

Skipping that step produces a link that silently 404s for everyone else — the single most common
way this phase fails.

**B · GitHub Pages** — `gh repo create <name> --public --source=. --push`, then enable Pages
(Settings → Pages → deploy from `main`). Slower, needs git, and the URL outlives the session.

**C · Static drop host** — drag `prototypes/<name>/` onto a drag-and-drop host such as
`netlify.com/drop`. No account needed; some corporate networks block it.

**Verify before you report.** Fetch the URL and confirm it returns the prototype — do not hand
over a link you have not checked. If every path fails, say so plainly and give the local file
path plus the one-line reason each failed.

## Phase 7 · FINALIZE — and feed the brain back

1. **`improvement-log.md`** — the round-by-round table:

   | Criterion | Source | R1 | R2 | R3 | Δ |
   |---|---|---|---|---|---|

   Plus what changed each round, which creative enhancements landed, and where it plateaued.

2. **`product-passport.md`** — stakeholder-ready: what it is and who it's for · the question it
   answers · **3 things that need real validation** (things no evaluator can judge — willingness to
   pay, whether they return, what an angry user does) · the live URL · the recommended next step.

3. **Propose the brain update — never write it silently.** The run produced things the brain
   should know: a feature that now exists, terms the prototype needed that the glossary lacked, and
   any place the artifact collided with a principle. Offer them as a **diff or a pull request** for
   a human to ratify. Nothing self-ratifies; the brain is guarded deliberately, or it becomes a
   dump nobody trusts.

## Output summary

Report:
- **R1 → final score** (e.g. `4.1 → 7.6`), and which criteria moved
- What the brain contributed — and, honestly, what it was missing
- Any principle the Evaluator caught being violated, with its ID
- The most surprising creative enhancement
- The top remaining weakness
- **The live URL**, and whether you verified it opens
- Every file path produced

## Design principles

1. **Three-agent separation is non-negotiable.** Orchestrator manages, Generator builds,
   Evaluator critiques. No agent plays two roles.
2. **The brain sets the bar.** Generic criteria produce generic prototypes. A team's own decisions
   are the only rubric that makes an evaluation specific to *them*.
3. **File-based communication.** No context leaks.
4. **Browser verification beats code reading.** A prototype that looks right in source and breaks
   on screen teaches nothing.
5. **Creative enhancements are mandatory** — one per Generator round, unrequested. This is where
   the leaps come from.
6. **Publish or it didn't happen.**
7. **The loop has a ceiling.** It converges on the criteria you gave it. It cannot tell you whether
   anyone wants this — that still takes a person.
8. **Every prototype answers a question.** If you can't say what it tests, it's decoration.
