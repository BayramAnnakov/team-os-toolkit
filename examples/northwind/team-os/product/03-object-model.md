---
owner: irina
stability: evolving
last_reviewed: 2026-07-24
sources: [../../team-chat-export.md, ../../weekly-meeting-notes.md, ../../weekly-2026-07-06.md]
---
# Object model

The core entities and their **real** states. The most common agent failure is inventing a status that doesn't exist — so where a state name is confirmed by evidence it is marked ✅, and where it is our reading rather than an attested line it is marked ⚠️. **Never quote a ⚠️ state to a customer without checking the billing code or Stripe.**

## Entities and relationships

```
Agency ──1:*── Seat            (a seat = one user licence; billed monthly)
Agency ──1:*── Invoice         (monthly, per seat)
Agency ──1:*── Refund
Invoice ◄──── AccountCredit    (a credit attaches to the NEXT invoice)
Charge  ◄──── Dispute          (raised at Stripe by the cardholder, not with us)
Invoice ──sent to──► End-client (on the agency's behalf)
```

## Refund

The lifecycle:

| State | Meaning | Who moves it |
|---|---|---|
| `requested` | An agency has asked for money back — in chat, email, or a ticket | The agency (via support) |
| `approved` | Signed off. A **billing error** needs no approval conversation; other cash refunds need Pavel | Pavel, by Slack ping — there is deliberately **no approval UI** (2026-07-06, item 1) |
| `sent` | Submitted to Stripe. Our part is over | Support / Stripe |
| `settled` | The money is visible on the cardholder's statement | **The card networks. Not us.** |

> **Card settlement takes 5–10 business days, and Northwind does not control that window.** Once a refund is `sent`, we can say what we did and where to see it — we cannot promise when it lands (`00-overview.md`, Voice). This gap is why "where's my refund?" is a ticket class at all, and what the self-serve refund-status page is for (2026-07-06, item 2).

⚠️ **Provenance.** The four state *names* and the 5–10 business day settlement figure are **not attested in the evidence**. What the evidence supports is: refunds have a status worth exposing (the refund-status page), approval is a manual Slack step, and customers wait long enough to file tickets. Treat the enum as the working model to verify against the billing code — not as a quotable fact. <!-- not in evidence -->

**Not modelled:** a rejected/declined path. The evidence says "changed my mind" refunds are *"case-by-case — ping me"* (2026-05-12) but never records a refusal, so there is no attested terminal state for one. Don't invent it.

**Routing (this part is attested):**

| Transition | Who decides | Source |
|---|---|---|
| Billing error → cash refund | Nobody's approval needed — proceed | 2026-05-12 chat; 2026-06-06 weekly |
| Changed mind / unused seats → account credit | The default; support proceeds | 2026-05-28 chat; 2026-06-13 weekly |
| Any other cash refund | **Pavel**, above a threshold that is **unconfirmed** ($200 vs $500 — #149) | 2026-05-19, 2026-06-06 · `../decisions.md` D-02 |

## Dispute

A dispute is **not** a refund. It is raised by the cardholder at Stripe, and it runs on Stripe's clock.

- **Response window: 7 calendar days.** Miss it and it *"auto-finalizes against us"* — *"we lose it automatically"* (Marcus, 2026-05-19). ✅ attested, and the hardest constraint in the product.
- **Owner: Marcus** — gathers evidence first. **Escalates to Pavel only above $500** (2026-06-13 weekly). ✅ attested. A reusable evidence template is still open (#151).
- Observed amount for scale: a $480 dispute on 2026-05-19 — i.e. real disputes land just under the escalation line.

⚠️ **States.** No dispute enum appears in the evidence. The observable lifecycle is: *received from Stripe → evidence gathered → responded → resolved (won or lost)*, with a fifth outcome — *auto-finalized against us* — if day 7 passes with no response. These names are ours, not Stripe's. Read the Stripe dashboard for the real ones. <!-- not in evidence -->

## Invoice

- Issued **monthly, per seat** (2026-06-13). ✅
- An **account credit** applies to the **next** invoice — never as prorated cash back on the current one (2026-05-28, 2026-06-13). ✅
- Sent to the agency; also the artefact the agency's **end-clients** receive on their behalf (`01-personas-icp.md`).

⚠️ **Invoice states are not in the evidence.** Do not invent them (`draft`/`open`/`paid`/`void` are Stripe's words, not confirmed as ours). If you need them, read the billing code or ask Irina — the seat-billing FAQ (#155) is the open task that would settle it. <!-- not in evidence -->

## Seat

- One user licence; the unit of billing.
- **Mid-cycle removal → credit on the next invoice, not prorated cash** (2026-06-13). ✅ The single most-asked billing question after refunds.
