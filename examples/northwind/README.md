# Northwind — sample team evidence

Fictional **Northwind** team — a 9-person B2B SaaS (invoicing / payments for small
agencies). Generic on purpose, so anyone can relate. Use this folder to run the toolkit's
skills end-to-end when you don't have your own chats/meetings handy — it exercises the
**real evidence sweep**, not a paste-into-chat shortcut.

## The same evidence feeds two different skills

| Skill | Mines this evidence for… | Recurring question it answers |
|---|---|---|
| `/init-team-os` (W1) | the **facts** — glossary, roster, refund policy, single source of truth | *"What's our refund / dispute policy and who can approve one?"* |
| `/init-team-decisions` (W2) | the **judgment** — dated decision principles + one-way doors | *"Credit or cash? When do we discount? Where do we focus?"* |

That's the whole point: the repo answers the *words*; your recurring question was secretly
asking for the *judgment*. Same raw evidence, two layers.

## How to use

From a Claude Code session in this repo:

```
/init-team-decisions        # (or /init-team-os for the W1 knowledge layer)
```

…then point it at this folder: *"Mine `examples/northwind/` for decision episodes and build the judgment layer."*

## Files

- `team-chat-export.md` — the `#product-help` channel; the same few questions recur and the answers drift.
- `weekly-meeting-notes.md` — decisions + action items + vocabulary (Jun 6 / 13 / 20).
- `task-tracker-export.md` — roster, roles, open items (incl. the deferred approval-threshold task).
- `weekly-2026-07-06.md` — a later weekly where **focus + pricing** get decided. This is the one that
  shows `/init-team-decisions` doing four distinct things: mine a clean principle, **reject** an
  un-mineable line, **escalate** a one-way door (the discount), and **refuse to crown** a call the
  room never committed to.
- `team-os/` — the **built brain**: what `/init-team-os` + `/init-team-decisions` produce from the
  evidence above (`CLAUDE.md`, `now.md`, `decisions.md`, `product/`). It's the "after" to everything
  else here being the "before", and it's what the next skill in the chain reads. **If you're doing the
  mining exercise, build your own first** — reading the answer key skips the part that teaches you
  anything. Compare afterwards; disagreeing with it is a fine outcome.

## Who's who (roster)

- **Pavel** — Founder/CEO. Final approver on cash refunds + large disputes. The calibration authority.
- **Dana** — Support Lead. Owns onboarding, triages refund questions.
- **Marcus** — CS. Owns Stripe disputes.
- **Irina** — PM. Owns documentation / knowledge.
- **Sofia** — CS (new). The reason the gaps are now visible.

## Deliberate seams (so the skills have something real to do)

- The cash-refund approval threshold (**$200 vs $500**) is left **contradictory** on purpose — a good
  repo *flags it as unconfirmed* rather than silently picking one; a good decisions.md logs the
  4-week deferral (task #149) as its own candidate principle.
- The Stripe **"7 calendar days to respond to a dispute"** fact lives in **only one file**
  (`team-chat-export.md`) — delete that file and the answer visibly loses something (the W1
  "delete-a-source" degradation demo).

## Then: the refusal test (W2)

After `/init-team-decisions` writes `decisions.md` + the `decide-like-northwind` skill, ask the new
skill a real decision question **with no recommendation** (e.g. `Should we give an agency a cash
refund for unused seats mid-cycle?`). Pass = it **refuses** and asks for your call + reasoning first.
A decision skill you haven't watched refuse is not yet trustworthy.
