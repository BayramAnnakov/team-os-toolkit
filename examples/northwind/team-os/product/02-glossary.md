---
owner: irina
stability: stable
last_reviewed: 2026-07-24
sources: [../../team-chat-export.md, ../../weekly-meeting-notes.md, ../../weekly-2026-07-06.md]
---
# Glossary
The exact words Northwind uses. Agents and teammates must use these and never invent terms. The recurring-vocabulary line at the bottom of `../../team-chat-export.md` is the authority for the money words; the 2026-06-13 weekly is the authority for the billing words.

## Money going backwards

- **Refund** — money returned to the customer. Always qualify which kind; unqualified "refund" is the ambiguity that cost this team 20 minutes a pop.
  - **Cash refund** — money actually leaves us and returns to the card. Reserved for **billing errors**; otherwise needs Pavel's sign-off. Cannot be recalled.
  - **Account credit** (a.k.a. *credit on the next invoice*) — the default. The balance stays with us and reduces the agency's next invoice. *"Credit keeps them with us"* (Pavel, 2026-05-28). Never call this "a refund" to a customer — it isn't one.
- **Billing error** — a charge **we** caused (e.g. a double charge, 2026-05-12). Always a **full cash refund**, immediately, no approval needed. This is the only word that unlocks that path — don't stretch it to cover a customer's change of mind.
- **Changed mind / unused seats** — the customer's circumstances changed, not our system. Defaults to **account credit**; case-by-case above that (2026-05-12, 2026-05-28).
- **Proration** — charging or refunding a partial period in cash. **We don't do it for mid-cycle seat removal** — that resolves to credit on the next invoice (2026-06-13). Whether proration is ever right is still open (#155).
- **Refund status** — where a refund is in its lifecycle: `requested → approved → sent → settled` (`03-object-model.md`). The self-serve **refund-status page** (in flight, 2026-07-06) exists to answer this without a ticket.
- **Approval threshold** — the cash-refund amount above which Pavel must sign off. **UNCONFIRMED: $200 or $500** (2026-05-19, 2026-06-06, task #149). Never state a number — say "unconfirmed, ask Pavel" (`../decisions.md` D-02). Not to be confused with the **>$500 dispute escalation**, which *is* confirmed (D-07).

## Disputes

- **Dispute** — our word, and Stripe's, for a customer challenging a charge with their card issuer instead of asking us. A **separate flow** from a refund, owned by Marcus (2026-05-19, 2026-06-13).
- **Chargeback** — the card-network word for the same thing. It does **not** appear in our evidence; we standardise on **dispute**. If a customer or a bank says "chargeback," answer about the dispute.
- **Dispute response window** — **7 calendar days** (not business days) to respond before it *"auto-finalizes against us"* and *"we lose it automatically"* (Marcus, 2026-05-19). The hardest deadline in the product.
- **Dispute evidence** — what Marcus gathers to respond. A reusable template is still to be built, *"for >$500 escalations"* (#151).

## Customers and billing

- **Agency** — **our paying customer**. Always. (Chat vocabulary line, `../../team-chat-export.md`.)
- **End-client** — the agency's own customer, who receives an invoice from us on the agency's behalf. **End-clients never log in; they only get invoice links by email.** <!-- not in evidence: the "never log in / links by email" mechanism is the intended model, not an attested line. Confirm against the billing code before stating it to a customer. -->
- **Seat** — a user licence. The billing unit: we charge **per seat, per month** (2026-06-13).
- **Invoice** — the monthly per-seat bill to an agency, and the object an **account credit** attaches to (the *next* one).
- **Growth plan** — the only plan name attested anywhere in the evidence (2026-05-12). Don't invent others.

## Team words

- **Calibration authority** — Pavel. The person whose judgment `../decisions.md` encodes and the only one who moves a principle to `ratified`.
- **One-way door** — a decision that is expensive or impossible to reverse. It produces an escalation brief for Pavel, never a decision by a teammate or an agent (`../decisions.md`).
