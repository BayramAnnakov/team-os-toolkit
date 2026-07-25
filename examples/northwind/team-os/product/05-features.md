---
owner: irina
stability: evolving
last_reviewed: 2026-07-24
sources: [../../weekly-2026-07-06.md, ../../weekly-meeting-notes.md, ../../team-chat-export.md, ../../task-tracker-export.md]
---
# Features

Status as of the **2026-07-06** weekly — the newest evidence behind this repo. The task tracker owns live status; this is a dated snapshot.

## Catalog

| Feature | Status | Notes | Source |
|---|---|---|---|
| Per-seat monthly billing | live | The billing unit. Only "Growth" is an attested plan name | 2026-06-13; 2026-05-12 |
| Invoicing agencies (and their end-clients) | live | The product | `../../README.md` |
| Account credit on the next invoice | live | The default outcome of a refund request (D-01) | 2026-05-28; 2026-06-13 |
| Cash refunds | live, **manual** | Approval is a Slack ping to Pavel. Deliberately **no UI** | 2026-07-06, item 1 |
| Stripe disputes | live, **manual** | Marcus gathers evidence; >$500 → Pavel; 7-day clock | 2026-05-19; 2026-06-13 |
| **Self-serve refund-status page** | **shipping now** | The independent win — kills "where's my refund?" tickets (D-03) | 2026-07-06, item 2 |
| Automated refund flow | **held** | Depends on the Stripe migration; revisit when it lands (D-03) | 2026-07-06, item 2 |
| Stripe migration | in flight | The critical path everything refund-automation waits on | 2026-07-06, item 2 |
| Cash-refund approval UI | **not building** | *"No bad refund has ever slipped through"*; ~a week we don't have. Revisit if refund volume doubles (D-03) | 2026-07-06, item 1 |
| Dispute evidence template | open (#151) | For >$500 escalations | task tracker |
| Localized invoices (German) | deprioritized | No reasoning recorded — status only, not a principle | 2026-07-06, item 5 |
| E-sign integration | contract signed, pilot pending | Stated as ~3 weeks out on 2026-07-06 | 2026-07-06, item 5 |

## Known gaps — where the real work is

- **No canonical refund/dispute policy.** #142 (Irina) has been open since 2026-05-23, *"keeps slipping; high pain."* Sofia found **two contradictory Notion pages** in week 1 (2026-06-03). This repo is the attempt to close it — and it isn't canonical until the team says so (`../now.md`).
- **The cash-approval threshold is unconfirmed** — $200 or $500, #149, ~4 weeks unresolved. The support flow runs on a number nobody can cite (`../decisions.md` D-02).
- **Seat-billing FAQ missing** (#155, tied to #142): proration vs credit is answered by precedent, not by a document.
- **We can't count the thing we want to fix.** Sofia's refund-question volume isn't tracked, so "the repo cut support load" is unprovable (Dana, 2026-07-06, item 4; D-04). The *cost* side **is** measured: ~20 min per question, 4+ a month (#160).
- **Refund approval has no audit trail** beyond Slack. That's an accepted trade, not an oversight — but it's the thing that breaks first if volume doubles (2026-07-06, item 1).
- **The settlement window is not ours.** Even with the status page shipped, customers wait on the card networks (`03-object-model.md`). The page reduces the tickets; it can't reduce the wait.
- **Onboarding depends on all of the above.** #138 (Sofia's onboarding pack, Dana) needs the refund + billing FAQ that doesn't exist yet.

<!-- not in evidence: anything about the product's UI, API, integrations beyond e-sign and Stripe, mobile, or reporting. The evidence is a support channel, three weeklies and a task tracker — it is rich on money-going-backwards and silent on the rest of the surface. Don't fill the gaps in. -->
