---
owner: irina
stability: stable
last_reviewed: 2026-07-24
sources: [../../README.md, ../../team-chat-export.md, ../../weekly-meeting-notes.md, ../../weekly-2026-07-06.md]
---
# Personas / ICP

## Who we sell to
**Small agencies** (`../../README.md`). In our vocabulary, "agency" always means **our paying customer** — never the agency's own client (`02-glossary.md`). They buy **seats** (one per user) and are billed **per seat, per month** (2026-06-13 weekly).

Only one plan name appears anywhere in the evidence: **Growth** (2026-05-12 chat). <!-- not in evidence: the full plan lineup, price points, seat minimums, and whether annual billing is a plan or a term. An annual renewal is referenced on 2026-07-06, so annual terms exist — but nothing more is attested. -->

## Who inside the agency touches us

| Who | What they do with us | Attested by |
|---|---|---|
| **Agency admin / owner** | Buys and removes seats, sees invoices, asks for refunds, negotiates renewals | 2026-05-12, 2026-05-28, 2026-06-13, 2026-07-06 |
| **Agency staff (a seat)** | A user licence — the unit we bill | 2026-06-13; chat vocabulary line |
| **End-client** | The agency's own customer, who receives an invoice from us on the agency's behalf | `../../README.md` ("invoicing / payments for small agencies") |

> **End-clients never log in.** They only ever receive invoice links by email — they have no account, no seat, and no way to see refund status.
> <!-- not in evidence: this is the intended model and the reason the self-serve refund-status page is scoped to agencies, but no evidence line states it. Confirm against the billing code or with Irina (#155) before telling a customer. -->

## Use-case archetypes (each one is a real episode, not a hypothetical)

1. **"We removed a seat mid-cycle — refund the rest?"** → account credit on the next invoice, not prorated cash. (2026-05-28 chat; 2026-06-13 weekly; D-01)
2. **"You charged us twice."** → our billing error → full cash refund, immediately, no approval conversation. (2026-05-12 chat; D-01)
3. **"Changed our mind."** → case-by-case, and it goes to Pavel. Not a self-serve path. (2026-05-12 chat; D-01)
4. **The customer disputes the charge with their card instead of asking us** → a Stripe dispute, a different flow with a 7-calendar-day clock, owned by Marcus and escalated above $500. (2026-05-19 chat; 2026-06-13 weekly; D-07)
5. **"Discount our annual renewal."** → a pricing commitment. Pavel calls it; nobody else, and no precedent applies. (2026-07-06; D-05)
6. **"Where's my refund?"** → the ticket class the self-serve refund-status page exists to kill. (2026-07-06, item 2)

## The internal reader (this repo's other audience)
The repo was built because the *team* couldn't answer these consistently, so it has a second ICP:

- **Sofia (CS, week 1 as of 2026-06-03)** — the calibration reader. She searched Notion for the refund policy and found two contradictory pages. If a doc here doesn't answer her without a Slack ping, the doc has failed.
- **Dana (Support Lead)** — triages refund questions; measured the cost (~20 min each, 4+/month, #160).
- **Marcus (CS)** — owns disputes and the 7-day clock.
- **Irina (PM)** — owns this knowledge (#142, #155).
- **Pavel (CEO)** — the approver and the calibration authority for `../decisions.md`.
