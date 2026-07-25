---
owner: irina
stability: stable
last_reviewed: 2026-07-24
sources: [../../README.md, ../../weekly-meeting-notes.md, ../../weekly-2026-07-06.md, ../../team-chat-export.md]
---
# Overview

Northwind is a 9-person B2B SaaS selling **invoicing and payments to small agencies** (`../../README.md`). Agencies pay us **per seat, per month** (2026-06-13 weekly) and use us to bill their own end-clients. Five of the nine are named in our evidence: Pavel (CEO), Dana (Support Lead), Marcus (CS/disputes), Irina (PM/docs), Sofia (CS, new) — see the roster in `../CLAUDE.md`.

Almost everything expensive about the product right now sits at the same place: **money going backwards**. Refunds, credits, and Stripe disputes are where the rules are ambiguous, where support time disappears (~20 min per question, 4+ a month — task #160), and where the newest teammate got stuck in week 1 (2026-06-03).

## Strategy spine

- **Keep the customer, not the cash.** The default on a refund is account credit, not a cash payout — *"credit keeps them with us"* (Pavel, 2026-05-28). Cash is reserved for charges we caused. See `../decisions.md` D-01.
- **Remove the waiting, keep the human.** The current bet is to take the *status* question off support (self-serve refund-status page, shipping now) while deliberately **keeping** the manual approval on cash refunds — *"no bad refund has ever slipped through"* and an approval UI is ~a week the team doesn't have (2026-07-06, items 1–2). Automation follows the Stripe migration, not the other way round.
- **The clock beats the process.** A Stripe dispute auto-finalizes against us after 7 calendar days (2026-05-19). Anything we build or decide around disputes is subordinate to that window.
- **One answer, in one place.** The repeated cost isn't answering the question, it's answering it *differently* (Irina, 2026-05-23; Sofia found two contradictory Notion pages, 2026-06-03). This repo is the response to that — see `../decisions.md` D-06, and its honest caveat that the team has stated this intent more often than it has executed it.

<!-- not in evidence: Northwind's market position, competitors, pricing tiers beyond the "Growth plan" named on 2026-05-12, and revenue. The evidence is a support channel, three weeklies, and a task tracker — it says a lot about how the team decides and nothing about the market. Do not fill this in from imagination. -->

## Voice — how we write about money

Plain, calm, specific about money and dates.

- **Say the amount, the date, and who decides.** Vagueness about money reads as evasion.
- **Never be cheerful about a refund.** A refund means something went wrong for the person reading. No exclamation marks, no "Happy to help!" — just what happened, what we did, and what's next.
- **Never promise a date we don't control.** Once a refund is sent, settlement is the card networks' window, not ours (`03-object-model.md`). Say what we have done and where they can see it — never when the money will land.
- **When a rule is unconfirmed, say so and name who can confirm it.** "Unconfirmed — Pavel decides" is a better answer than a confident number (`../decisions.md` D-02).
- **Don't claim an improvement we haven't measured** — internally or to a customer (D-04).

<!-- Voice is authored, not mined: the evidence contains no style guide. It is derived from constraints that ARE in evidence — the settlement window we don't control, the unconfirmed threshold, and Dana's "don't claim the win until we count it" (2026-07-06). Treat it as a proposal to ratify, not as a recorded team decision. -->
