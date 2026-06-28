---
owner: <your-handle>
stability: stable
last_reviewed: <yyyy-mm-dd>
purpose: Agent entry point + router for <team>'s knowledge base
---

# <team>-brain — read this first

You are an AI agent working on <product/team> for a teammate. This repo is the team's shared brain: what we're building, for whom, the vocabulary, how we decide, and what's happening right now. It answers **"<the recurring question your team asks you>"**.

## How to use this repo
1. **Read `now.md` first** — the current focus + open questions. If its `last_reviewed` is >2 weeks old, treat specifics as possibly stale.
2. **Pull only the docs you need** (index below) — you rarely need all of them.
3. **Ground every claim in a source.** When this repo conflicts with the system of record (code, CRM, tracker), the system of record wins — flag the drift.

## Doc index
| Read when you need… | File | Stability |
|---|---|---|
| What's happening **right now** + open questions | `now.md` | volatile |
| The one-paragraph + strategy | `product/00-overview.md` | stable |
| Who it's for | `product/01-personas-icp.md` | stable |
| The exact words to use | `product/02-glossary.md` | stable |
| Entities, states/enums (if software) | `product/03-object-model.md` | evolving |
| Feature catalog + status + gaps | `product/05-features.md` | evolving |
| How the team decides | `decisions.md` | evolving |
| Reusable team skills | `skills/` | evolving |

## What does NOT belong here (the trust boundary)
- Secrets / keys / employer-confidential data.
- Live state (ticket statuses, metric values) — point to the system of record instead.
- <your team's specific boundary>

## Conventions
- Every doc carries frontmatter: `owner`, `stability`, `last_reviewed`, `sources`.
- Every folder has a `CLAUDE.md` index. Filenames kebab-case. Add via PR.
