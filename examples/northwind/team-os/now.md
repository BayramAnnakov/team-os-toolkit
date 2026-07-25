---
owner: irina
stability: volatile
last_reviewed: 2026-07-24
sources: [../weekly-2026-07-06.md, ../task-tracker-export.md, ../weekly-meeting-notes.md]
---
# Now
The team's current focus + open questions — the first thing an agent reads. Updated after the weekly.

> **Staleness warning.** The newest evidence behind this repo is the **2026-07-06** weekly. Anything decided after that date is not in here. For live values: the task tracker owns `#` items, Stripe owns refund and dispute status.

## Current focus
- **Ship the self-serve refund-status page.** The independent win — it doesn't wait on the billing rebuild and it kills the "where's my refund?" tickets (2026-07-06, item 2; D-03).
- **Automated-refund flow: held.** It depends on the Stripe migration. Revisit trigger: the migration lands (2026-07-06, item 2; D-03).
- **Cash-refund approval stays manual** — Pavel by Slack ping, no approval UI. Revisit trigger: refund volume doubles (2026-07-06, item 1; D-03).
- **Canonical refund/dispute policy** (#142, Irina, open since 2026-05-23, "keeps slipping; high pain"). This repo is that attempt. It has not been declared canonical yet — see the open question below.
- **Sofia's onboarding pack** (#138, Dana, in progress) needs the refund + billing FAQ. Day-1 read is `product/02-glossary.md` then `product/05-features.md`.
- **Deprioritized:** localized invoices (German), 2026-07-06 item 5.
- **Elsewhere, not ours to sequence:** e-sign integration reached contract; first pilot stated as ~3 weeks out on 2026-07-06 (so roughly end of July — the tracker, not this file, is the system of record).

## Open questions
- **$200 or $500?** The cash-refund approval threshold (#149, Pavel) has been unconfirmed since 2026-05-19 — still open at the 2026-06-20 weekly, ~4 weeks. Until Pavel confirms it, no file here and no agent reading this may state a number (D-02).
- **Do we count Sofia's refund questions?** We don't track them today. Until we do, "the knowledge repo cut support load" is a blocked claim (Dana, 2026-07-06 item 4; D-04). The *other* number — ~20 min × 4+/month — is measured and may be used (#160).
- **Is this repo the single source of truth?** If yes, #142 closes. If not, we've added a third page to the two contradictory ones Sofia already found in Notion (2026-06-03) — which is worse than none.
- **The 20% annual discount** for the renewing account is with Pavel as of 2026-07-06; no outcome recorded. One-way door — nobody else calls it (D-05).
- **Is proration ever right?** #155 (seat-billing FAQ) is still open. Every episode in evidence resolves to credit-on-next-invoice, never prorated cash (2026-06-13) — but "never" is our reading of three episodes, not a stated rule.
