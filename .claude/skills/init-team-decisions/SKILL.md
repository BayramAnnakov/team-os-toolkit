---
name: init-team-decisions
description: >
  Mine how YOUR team actually decides into a decisions.md — dated, sourced decision
  principles with statuses, scopes, and one-way doors — and generate a
  decide-like-<your-team> apprentice-loop skill: teammate commits to a recommendation
  first, the skill cites principles and gap-analyzes the reasoning, episodes get
  logged for calibration, and consistently-calibrated teammates graduate to owning
  whole decision classes. Use when the user says "init team decisions", "set up a
  decision system", "capture how we decide", "build a decide-like-us skill", or keeps
  getting pinged with "what would <the founder> say?".
---

# /init-team-decisions — The Judgment Layer

The glossary gives agents and teammates the team's *words*; this layer gives them the
team's *judgment*. Built from evidence: real decision episodes where the reasoning is
visible — never from decision-theory boilerplate.

## Principles (non-negotiable)

1. **Judgment is mined, not invented.** Every principle carries the dated episode it
   came from. No episode → no principle. Everything starts `proposed`; only the named
   calibration authority ratifies.
2. **Codify the loop, not the answers.** The generated skill runs an apprentice
   protocol; the principles are data it cites by ID. A skill that vends verdicts is
   the failure mode, not the product.
3. **Recommendation first — no vending.** If the asker hasn't committed to their own
   recommendation, the loop hasn't started. (Reference eval: on a question with no
   recommendation, the no-skill arm answered anyway and scored 0/10; the skill arm
   refused and asked for the recommendation — that refusal IS the design.)
4. **Principles age.** Statuses `proposed → ratified → retired`; each principle has a
   scope, and stage-specific principles get retired when the stage changes — don't
   let January's judgment decide June's questions.
5. **One-way doors always escalate.** Expensive-to-reverse decisions produce an
   escalation brief (recommendation + reasoning + precedents attached), never a
   decision. The escalation gets faster, not slower.

## State Management

Write progress to `.decisions-setup/state.md` after every phase. On restart, resume —
never re-ask an answered question.

## Phase 0 — Evidence Sweep (decision episodes, not opinions)

Mine, read-only, naming each source before first use. Look for episodes where both
the decision AND the reasoning are visible ("decided X because Y"):

1. **Meeting summaries / notes** — weekly agendas, retro notes, design-review notes.
2. **Chat exports** the user provides — decision threads, "let's just do X" moments.
3. **Agent digests** if a team agent already runs — their Decisions sections are
   pre-distilled ore (the reference's first decision skill was mined from 14 nightly
   digests).
4. **PR discussions / ADRs** for engineering teams.
5. Recurring deferral patterns are evidence too — a question "deferred" repeatedly
   with no date is a candidate principle about deferral itself.

Extract candidates: the episode (dated, sourced), the generalized principle behind it
(**encode what transfers, keep the episode as the example** — a rule that only
re-describes its own incident never fires again), and a scope.

**Zero episodes found → do NOT fabricate and do NOT stall.** Roles, org charts, and
aspirational docs are not episodes (no date, no visible reasoning on a specific call).
Say exactly what the sweep lacked, then offer **interview mode**: elicit the last ~3
real decisions one at a time (approximate date · the question · the call · the ACTUAL
reasoning · how expensive to reverse), record each as a dated episode marked
`source: recalled (unverified)`, and continue the normal flow. Recalled episodes are
honest as long as they are labeled — invite the user to verify them against real
exports later and upgrade the provenance.

## Phase 1 — Evidence Review

Present candidate principles with provenance (episode, date, source, recurrence
count — a principle walked twice is stronger than one walked once). The user
confirms, corrects, or deletes. Also surface the mined candidate for **who the
calibration authority is** (whose verdicts the log will be scored against).

## Phase 2 — The Irreducible Questions (≤3)

1. **Calibration authority** — confirm the mined candidate ("decisions seem to route
   to <X> — is <X> the judgment being encoded?").
2. **One-way doors** — seed with the universal list (pricing & plan changes ·
   hiring/firing · commitments to customers · public statements · legal/contracts ·
   spend beyond agreed budgets); the user edits. These ALWAYS escalate.
3. **Review cadence** — when does the authority review pending episodes and proposed
   principles? Default: attach to an existing weekly ritual, never a new meeting.

## Phase 3 — Generate (show substance before writing)

Into the team's knowledge repo:

- **`decisions.md`** — preamble (what this file is, status lifecycle, aging rule),
  the one-way-doors list, the confirmed principles (each: ID `D-xx`, episode,
  reasoning, scope, status `proposed`), and a **Decision log** section with the entry
  template (question · teammate recommendation + reasoning · skill lean with cited
  IDs + confidence · what was done · authority verdict: pending/agree/disagree).
- **`skills/decide-like-<team>/SKILL.md`** — the apprentice loop:
  0. *Classify*: on the one-way-doors list (or expensive to reverse, or
     precedent-setting) → output is an escalation brief; still run steps 1–2.
  1. *Force the recommendation*: (a) their call, (b) their reasoning and criteria,
     (c) what would change their mind. No recommendation → help form one; never
     skip ahead.
  2. *Surface the team's lean*: applicable principles cited by ID (`ratified`
     weighted above `proposed` — qualify proposed as "mined, not yet ratified"),
     precedents, confidence grounded in how many independent precedents support it.
     **No matching principle → say exactly that and route to the authority. A
     confident guess in their name is worse than a question.**
  3. *Gap analysis on reasoning, not just conclusion*: match on both → say so;
     same conclusion / different reasoning → flag it (right-for-the-wrong-reason
     fails silently next time); different conclusion → name the principle that
     produces the difference and what evidence would settle it. The human owns
     the call.
  4. *Log the episode* in decisions.md — no silent episodes; the log is what makes
     calibration possible.
  5. *Calibration & graduation*: at the review cadence, the authority marks
     agree/disagree (+why). Disagreements are the valuable ones — each fixes, adds,
     or retires a principle. A teammate with **5 agreed verdicts of the last 6 in a
     decision class** owns that class. (Deliberately N-of-last-M, not consecutive:
     consecutive-agreement taxes honest disagreement at exactly the moment voice
     matters most.)

## Phase 4 — Prove It (the refusal test)

Before declaring done: ask the generated skill a real decision question **without
giving a recommendation**. It must refuse to vend an answer and ask for the
recommendation first. A decision skill you haven't watched refuse is not yet
trustworthy — same doctrine as watching the drift checker fail.

## Phase 5 — Wire the Ritual

- If a weekly knowledge-sync skill exists (e.g. from `/init-team-brain`): propose
  adding a **decision-mining pass** (collect new episodes as `proposed` entries) and
  a **principles revisit** (propose retire/amend for principles the week
  contradicted; note confirmations — recurrence strengthens the lean) to it, by PR.
- If the calibration authority also mined and ratified the seed set, say so in the
  file header — self-ratified principles become the team's through the calibration
  loop, not by decree. Honesty here is what makes the log trustworthy later.

## Phase 6 — Enforce it (optional): the decision-guard hook

The decisions layer is **advisory** until something makes the loop unskippable — the same
step `/init-team-brain` takes with its drift-checker. Offer to generate a **Claude Code
hook** that catches a decision made without the recommendation-first loop. **Enforcement
must be seen firing before it is trusted** (same doctrine as watching the drift checker fail).

Generate into the repo (`.claude/hooks/decision-guard.sh` + a `.claude/settings.json` snippet),
carrying an `owner/tier/last_reviewed` comment header:

- **Advisory (default — start here).** A `UserPromptSubmit` **command hook**: on a prompt that
  asks to *make* a decision (choose/approve/commit/ship/merge/reject/prioritize · "should we" ·
  "стоит ли" · "что лучше") but states **no recommendation**, print a nudge to stdout and
  `exit 0` (the nudge is injected as context; the prompt still runs). Deterministic, offline,
  free. Bilingual keyword match.
- **Robust / enforced (the upgrade).** A `UserPromptSubmit` **prompt hook** (`type: "prompt"`,
  a fast `model`, `$ARGUMENTS` = the hook JSON) that judges the same thing semantically and
  returns `{"decision":"block","reason":"…run the loop / escalate one-way doors as a brief"}`
  — no brittle regex. `type: "agent"` can even Read `decisions.md` to confirm a one-way door
  was escalated. (Five handler types exist: command · http · mcp_tool · prompt · agent.)

**Constraint progression — do NOT start enforced.** Ship advisory, watch false-positive rate,
then upgrade to the prompt hook, then flip to `block`. Starting enforced punishes false
positives and teaches people to resent the guard.

**Watch it fire (the red demo — required before declaring it live):** submit a decision
question with no recommendation → see the guard fire; submit the same with a recommendation
committed → silence. Only then is enforcement trusted.

> This is the W2→W4 bridge: the judgment layer (advisory) + a hook that enforces it =
> constraint progression (Advisory → Enforced). Optional here; deepened when hooks are taught.

## Rules

- No customer PII or account state in decisions.md — it records team judgment only.
- Conversational questions, numbered; ≤3 substantive questions total.
- Every generated file shown before writing; the repo's normal review flow (PR)
  applies.
- Finish by reporting: principles seeded (and how many were walked ≥2 times),
  questions asked, files written, and the single next action: **run the first real
  episode through the loop this week.**

---
*Provenance: generalized Jun 12, 2026 from the reference implementation at Onsa.ai
(decisions.md D-01..D-18 + decide-like-onsa; blind-judged eval 40/40 with-skill vs
9/40 without). This generalization is v0.1 — field-tested at n=1, not yet
clean-room tested. Issues welcome.*
