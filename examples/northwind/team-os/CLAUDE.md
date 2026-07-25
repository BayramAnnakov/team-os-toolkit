---
owner: irina
stability: stable
last_reviewed: 2026-07-24
purpose: Agent entry point + router for Northwind's knowledge base
---

# northwind-brain — read this first

You are an AI agent working on Northwind (invoicing and payments for small agencies) for a teammate. This repo is the team's shared brain: what we sell, to whom, the exact vocabulary, how we decide, and what's happening right now. It answers **"What's our refund / dispute policy, and who can approve one?"** — the question that cost the team ~20 minutes each, 4+ times in a month (`../team-chat-export.md`, 2026-06-09; task #160).

The judgment version of that question — *credit or cash, when do we discount, where do we focus* — lives in `decisions.md`, not here.

## How to use this repo
1. **Read `now.md` first** — the current focus + open questions. If its `last_reviewed` is >2 weeks old, treat specifics as possibly stale.
2. **Pull only the docs you need** (index below) — you rarely need all of them.
3. **Ground every claim in a source.** When this repo conflicts with the system of record — Stripe for money movement and disputes, the task tracker for `#` items — the system of record wins; flag the drift.
4. **Never state the cash-refund approval threshold as a number.** $200 vs $500 is unconfirmed (`decisions.md` D-02). The correct answer is "unconfirmed — ask Pavel (task #149)."

## Doc index
| Read when you need… | File | Stability |
|---|---|---|
| What's happening **right now** + open questions | `now.md` | volatile |
| The one-paragraph + strategy + how we write | `product/00-overview.md` | stable |
| Who it's for (agencies, and who inside them) | `product/01-personas-icp.md` | stable |
| The exact words — refund vs credit, dispute, billing error | `product/02-glossary.md` | stable |
| Entities + the real refund/dispute states | `product/03-object-model.md` | evolving |
| Feature catalog + status + gaps | `product/05-features.md` | evolving |
| How the team decides (D-01…D-07, one-way doors) | `decisions.md` | evolving |

*(`/init-team-decisions` also generates a `decide-like-northwind` apprentice skill under `.claude/skills/`. It is not part of this snapshot — this folder is the knowledge + judgment layers only.)*

## Roster (5 named of 9; `../task-tracker-export.md`, `../weekly-meeting-notes.md` 2026-06-20)
- **Pavel** — Founder/CEO. Final approver on cash refunds and large disputes. Calibration authority for `decisions.md`.
- **Dana** — Support Lead. Owns onboarding; triages refund questions.
- **Marcus** — CS. Owns Stripe disputes.
- **Irina** — PM. Owns documentation / knowledge (tasks #142, #155).
- **Sofia** — CS, week 1 as of 2026-06-03. The newest reader: if a doc here doesn't answer her, the doc is wrong.

## What does NOT belong here (the trust boundary)
- Customer PII, card data, account balances, Stripe keys — nothing that identifies a payer.
- Live state. A refund's actual status lives in Stripe; a ticket's status lives in the task tracker. This repo holds the rule and the dated snapshot, never the current value.
- A confident answer to something the evidence left open. Flag it instead (see D-02).

## Conventions
- Every doc carries frontmatter: `owner`, `stability`, `last_reviewed`, `sources`.
- Every folder has a `CLAUDE.md` index. Filenames kebab-case. Add via PR.
- `sources:` points at the raw evidence in `../` — every fact here is meant to be checkable against a dated line.
- Anything written here that the evidence does **not** support carries an inline `<!-- not in evidence -->` note. Do not quote those lines as fact.
