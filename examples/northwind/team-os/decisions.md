---
owner: pavel
stability: evolving
last_reviewed: 2026-07-24
sources: [../team-chat-export.md, ../weekly-meeting-notes.md, ../weekly-2026-07-06.md, ../task-tracker-export.md]
---
# Decisions & principles
How Northwind decides. Every principle carries the dated episode it was mined from — **no episode, no principle**. A pattern walked at least **twice** is stronger than one walked once, and says so.

**Status lifecycle:** `proposed → ratified → retired`. Everything starts `proposed`. Only **Pavel** (Founder/CEO, the calibration authority) ratifies. Entries marked `ratified` below are ones Pavel decided **on the record in a weekly** — nothing here was ratified by decree in a doc review. `proposed` entries are mined and advisory; cite them as "mined, not yet ratified."

**Aging:** every principle has a scope. When the scope changes (team size, refund volume, the Stripe migration landing), revisit — don't let May's judgment decide September's questions.

**Review cadence:** the existing weekly (`../weekly-meeting-notes.md` shows Jun 6 / 13 / 20, `../weekly-2026-07-06.md` shows Jul 6). New episodes and status changes ride that meeting — no new meeting.

**File rule:** no customer PII and no account state in here. This file records team judgment only. Where an episode involves a named account, the account is described, not named.

---

## Principles

### D-01 — Refunds default to account credit; cash only when the charge was our error
**Rule.** Give account credit by default. Give cash only when we caused the charge — and then give it immediately, without an approval conversation.
**Episode.** 2026-05-28 (`../team-chat-export.md`) — Marcus asked whether to prorate a partial refund for unused seats mid-cycle. Pavel: *"default to **account credit**, not cash, unless it's our billing error. Credit keeps them with us."*
**Also walked.** 2026-05-12 (same file) — Pavel: *"If it's our billing bug, refund immediately, no approval needed. If it's 'changed my mind,' it's case-by-case — ping me."* · 2026-06-13 weekly — *"mid-cycle seat removal → credit on next invoice, not prorated cash."* Three walks.
**Reasoning.** Credit keeps the money inside the relationship instead of ending it. And when the charge was our mistake, the customer shouldn't have to negotiate to get their own money back — friction there is a second injury.
**Scope.** Refund requests from agencies, any plan. Does **not** cover Stripe disputes (→ D-07): once it's a dispute, the customer has already left our process.
**Status.** `ratified` — Pavel, 2026-06-06 weekly (`../weekly-meeting-notes.md`).

### D-02 — An unconfirmed threshold gets flagged as unconfirmed, not guessed
**Rule.** When the number everyone is arguing about was never written down, record it as unconfirmed and route the call to the authority. Do not end the argument by picking a value.
**Episode.** 2026-05-19 (`../team-chat-export.md`) — Marcus asked the process for a $480 Stripe dispute. Dana: *"I think Pavel approves anything over $200? Or was it $500? Let me check… we don't really have it written down."*
**Also walked.** 2026-06-06 weekly recorded it and still couldn't close it: *"Anything cash over ~$200 needs Pavel's sign-off. (To be confirmed — nobody's sure if it's $200 or $500.)"* Task **#149** (Pavel, open, *"source of repeated confusion"*) was still open at the 2026-06-20 weekly — **~4 weeks unresolved**. The deferral itself is the evidence.
**Reasoning.** The confusion is cheap; a wrong number quoted confidently is not. Sofia asked for the policy in week 1 (2026-06-03) — a guessed threshold gets applied on day 1 as if it were policy, and then it's precedent.
**Scope.** Cash-refund approval only. ⚠️ The **dispute** escalation threshold (>$500 → Pavel) **is** confirmed — see D-07. Two different numbers; do not borrow one for the other.
**Status.** `proposed` — and the threshold itself stays **UNCONFIRMED**. No file in this repo, no answer built on this repo, and no agent reading it may state $200 or $500 as fact. The correct answer is: *"unconfirmed — ask Pavel (task #149)."*

### D-03 — Ship the independent win now; hold dependent work behind the critical path; every deferral names its revisit trigger
**Rule.** If a piece of work doesn't depend on the thing in flight, ship it now. If it does, hold it — and name the event that brings it back.
**Episode.** 2026-07-06 weekly, item 2 (`../weekly-2026-07-06.md`) — Pavel: ship the self-serve refund-status page **now**, because it's independent of the billing rebuild and it kills the "where's my refund?" tickets; **hold** the automated-refund flow until the Stripe migration lands (it depends on it), revisit right after the migration.
**Also walked.** Same weekly, item 1 — don't build the cash-refund approval UI: *"no bad refund has ever slipped through,"* and the UI is ~a week we don't have. Revisit trigger: **refund volume doubles**. Same shape — a deferral that names what brings it back.
**Reasoning.** Dependent work started early is inventory, not progress: it will be reworked when the dependency lands. And a deferral without a trigger isn't a decision, it's forgetting — the trigger is what makes "not now" reviewable instead of permanent.
**Scope.** Sequencing work already chosen for a cycle. Not a rule about *what* to build.
**Status.** `ratified` — Pavel, 2026-07-06 weekly.

### D-04 — Don't claim a win we can't count
**Rule.** If the instrument for a claimed improvement doesn't exist, the claim is blocked. Build the count first, then claim.
**Episode.** 2026-07-06 weekly, item 4 (`../weekly-2026-07-06.md`) — Dana: *"we keep saying 'the knowledge repo will cut Sofia's refund questions,' but we don't actually track how many she gets — that number is a guess. Don't claim the win until we count it."*
**Contrast (same team, measured properly).** Time lost to "where's the policy?" **was** counted: ~20 min per question, 4+ in a month — assigned to Dana at the 2026-06-06 weekly, reported 2026-06-09 in chat, tracked as **#160**. That number may be cited. Sofia's question volume may not.
**Reasoning.** An uncounted win is indistinguishable from a story we like. Worse, it retires the pressure to fix the actual problem — once "the repo fixed it" is believed, nobody counts.
**Scope.** Claims about internal process improvement. (Also the reason `now.md` keeps this as an open question rather than a result.)
**Status.** `proposed` — Dana raised it and the room didn't object, but the 2026-07-06 notes record no decision line from Pavel on item 4 (items 1 and 2 carry an explicit *"Decision (Pavel)"*; item 4 does not). Mined, not yet ratified.

### D-05 — A pricing commitment to a customer is a one-way door: it escalates to Pavel and never becomes a rule
**Rule.** Discounts, plan changes, and any price promised to a customer route to Pavel as a brief. No one else calls it, and no past call becomes a policy.
**Episode.** 2026-07-06 weekly, item 3 (`../weekly-2026-07-06.md`) — a renewing account asked for a **20% annual discount**. Decision: *"Pavel owns this, not Dana — it's a pricing commitment to a customer."* Pavel's lean, on the record: *"a renewal is worth more than the discount, but I make this call."* (Account deliberately not named here — see the file rule above.)
**Reasoning.** A discount isn't one concession; it re-sets that account's price and sets the anchor for the next negotiation and for anyone who hears about it. Reversing it costs the relationship, which is exactly what makes it one-way.
**Scope.** Any pricing, plan, or discount commitment to a customer. See **One-way doors** below.
**Status.** `ratified` as a **routing** rule — Pavel stated the ownership on the record, 2026-07-06. ⚠️ The *content* of his lean is **not** a principle and must not be mined into one: "a renewal is worth more than the discount" was a lean on one deal, explicitly reserved to himself. Anyone converting it into "we approve 20%" has manufactured a policy the team never made.

### D-06 — A question that has already cost the team time twice gets a written canonical answer, not a third verbal one
**Rule.** Second time a question costs real time, stop answering it and write it down once, where everyone (and every agent) reads the same words.
**Episode.** 2026-05-23 (`../team-chat-export.md`) — Irina: a new hire asked *"what's our refund policy"* and *"I realized I'd answer it differently than Dana would."*
**Also walked.** 2026-06-03 — Sofia, week 1: searched Notion, *"found two different pages"* · 2026-06-09 — Dana: ~20 min per refund question, four already that month · 2026-06-20 weekly — new hires keep asking the same 5–6 questions, *"the answers aren't consistent,"* idea floated for one team knowledge repo any of us or our AI tools can read. Four walks.
**Reasoning.** The cost isn't the answer, it's the re-derivation plus the drift: two people answering the same question differently is a policy fork nobody voted for.
⚠️ **Honest caveat.** This is stated far more often than it is executed. Pavel's reply on 2026-05-23 was *"👍 someday"*; **#142** sat open 4 weeks (*"keeps slipping; high pain"*) and the 2026-06-13 weekly logged it *"STILL open."* The recurrence is evidence of the **pain**, not evidence of the **habit** — treat this as the team's stated intent, not its track record.
**Scope.** Internal knowledge. Not customer-facing documentation.
**Status.** `proposed`.

### D-07 — Disputes go to Marcus first, above $500 to Pavel — and the Stripe clock outranks our process
**Rule.** Marcus gathers evidence on every dispute; only disputes over $500 escalate to Pavel. The 7-day response window sets urgency; the amount only sets who signs.
**Episode.** 2026-06-13 weekly (`../weekly-meeting-notes.md`) — *"Stripe disputes are handled by Marcus first (gather evidence), escalate to Pavel only if > $500."*
**Also walked.** 2026-05-19 (`../team-chat-export.md`) — Marcus put the hard constraint on record: *"Stripe gives us only **7 calendar days** to respond to a dispute before it auto-finalizes against us. Miss that window and we lose it automatically — this has to be in the policy."* Task **#151** (dispute evidence template) exists *"for >$500 escalations."*
**Reasoning.** The window is external and unforgiving: an unanswered dispute is a loss by default, so waiting for a sign-off can cost more than the sign-off protects. Routing by amount is safe *only* because the clock is handled first.
**Scope.** Stripe disputes. Refunds we initiate are D-01.
**Status.** `ratified` — 2026-06-13 weekly. ⚠️ The **>$500** figure here **is** confirmed; the cash-refund threshold in D-02 is **not**. Do not merge them.

---

## Not mined (and why)
Recording what was deliberately *not* promoted is part of the file. A decisions.md that mines everything is a junk drawer.

| Line | Source | Why not a principle |
|---|---|---|
| "Localized invoices (German) deprioritized for now." | 2026-07-06, item 5 | A decision with no visible reasoning. A rule mined from it would only re-describe its own incident. Recorded as **status** in `product/05-features.md`. |
| "E-sign integration reached contract; first pilot ~3 weeks out." | 2026-07-06, item 5 | A status update, not a decision. Lives in `now.md` with its date. |
| "A renewal is worth more than the discount." | 2026-07-06, item 3 | Pavel's lean on one deal, explicitly reserved to himself. Escalation input, never a rule → D-05. |
| "The knowledge repo will cut Sofia's refund questions." | 2026-07-06, item 4 | Blocked by an instrument gap — we don't count them → D-04. |
| Roster and role lines | `../task-tracker-export.md` | Org facts, not episodes: no date, no visible reasoning on a specific call. They belong in `CLAUDE.md`. |

---

## One-way doors
Expensive or impossible to reverse. These produce an **escalation brief** for Pavel — recommendation + reasoning + precedents attached — never a decision made by a teammate or an agent. The test is reversibility-for-us, not the topic.

1. **Pricing, plan, and discount commitments to a customer** — D-05, episode 2026-07-06. Reversing a price costs the relationship.
2. **Letting the Stripe 7-day dispute window expire** — nobody *decides* this, which is exactly why it's listed: after day 7 it *"auto-finalizes against us"* and *"we lose it automatically"* (2026-05-19). On a dispute, "we'll get to it" is a one-way door.
3. **Cash out the door** — a cash refund cannot be recalled; an account credit can be adjusted. This asymmetry is *why* D-01's default exists and why cash needs Pavel's sign-off. (Threshold unconfirmed — D-02.)

**Not yet walked:** hiring/firing, legal and contracts, public statements, spend beyond agreed budgets. These are on the standard starter list, but this evidence contains **no episode** for any of them — nothing here is calibrated for them. Route them to Pavel and log the episode, so the next one has a precedent.

---

## Decision log
No silent episodes: every decision run through the loop gets an entry, so calibration is possible later. Pavel marks the verdicts at the weekly.

**Entry format**

```
### <yyyy-mm-dd> — <the question>
- **Recommendation + reasoning (teammate):** <their call, their criteria, what would change their mind>
- **Team's lean:** <principles cited by ID, e.g. D-01, D-03> · confidence: <low|med|high — grounded in how many independent precedents support it>
- **Divergence:** <match on both / same conclusion different reasoning / different conclusion — and what evidence would settle it>
- **What was done:** <the action actually taken>
- **Authority verdict (Pavel):** pending | agree | disagree — <reasoning>
```

*No episodes logged yet.* The first real decision this week goes here — including one where the lean and the teammate disagreed, since a well-reasoned disagreement that fixes or retires a principle is the most valuable entry in this log.
