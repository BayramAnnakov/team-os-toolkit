# Team OS Toolkit

Build a team knowledge repo that answers questions instead of you — then give it a voice.

From the AI Natives build sessions (June 2026). Reference implementation running in production at Onsa.ai.

## Quickstart

Open Claude Code (or any agent that supports the skills standard) **in this folder** — the skills load automatically. Then, in order:

| Step | Skill / Spec | What you get |
|---|---|---|
| 1 | `/init-team-os` | Your team knowledge repo, built from evidence your machine already has (Claude Code history, MCP config, existing docs). You answer at most 5 questions. Ends with a real answer to your team's #1 recurring question + the message to post in your team chat. |
| 2 | `/init-team-brain` | The product-knowledge layer on top: glossary and object model mined from your code, rot-rate tiers, and a drift checker that FAILS commits when docs disagree with code. You watch it fail before you trust it. |
| 3 | `/init-team-decisions` | The judgment layer: a `decisions.md` of dated, sourced decision principles mined from your meetings and chats, plus a generated `decide-like-<your-team>` apprentice skill — recommendation first, gap analysis on reasoning, episode log, calibration, graduation. Proven by refusal: you watch it decline to answer until a recommendation is committed. |
| 4 | [ROBIN-SPEC.md](ROBIN-SPEC.md) + `/robin-init` | An always-on **AI chief of staff** that lives in your chat with the repo as its brain — its duties (digest, briefs, meeting prep, whatever YOUR processes need) are declared in your repo, not hardcoded. The spec is the product — tell your coding agent to implement it on YOUR stack ([openai/symphony](https://github.com/openai/symphony) model). `/robin-init` drafts your soul.md + duty roster and writes the kickoff prompt. |

## The rule behind the packaging

**Files → skill. Running process → spec.** Skills are performed by your agent in one sitting (steps 1–3 produce files). Robin must keep running after the session ends, on your stack, operated by you — so it ships as a spec your own coding agent implements, not as a template you can't debug.

## The order matters

A Robin without a knowledge repo is just a chatbot. Build the repo first (step 1), prove the value to one teammate (post the answer where they'll see it), and only then add enforcement (step 2), judgment (step 3), and the agent (step 4). Adoption follows demonstrated value, not announcement.

## A target structure to grow into

`/init-team-os` builds the *minimal* seed — folders after the answer, never empty scaffolds. [`template/`](template/) is the **map** of where that seed grows: the lean, proven shape generalized from the `onsa-brain` reference (`now.md`, a numbered `product/`, `decisions.md`, `skills/`, the frontmatter + folder-index conventions). It's a reference to grow *into*, not a scaffold to create up front — copy a file from it when real content demands it.

## Feedback

Every question a skill asks that it could have mined, every ambiguity your coding agent hits in ROBIN-SPEC — those are bugs. Report them to @BayramAnnakov.

## Provenance

- Reference implementation in production at Onsa.ai: 276+ logged agent interactions, 4 teammates, ~$30–40/month.
- Skills 1–2 and /robin-init clean-room tested (fixture machines, scripted users, blind judges) before release; ROBIN-SPEC's v0.3 core was validated by a stranger coding agent building a working Robin from the document alone — M0 passed on the first run, at $0.039. Later additions (v0.4+) are field-patched from real implementer questions and not yet re-validated clean-room.
- `/init-team-decisions` (added Jun 12) generalizes the reference's decision system, which carries its own blind-judged eval (40/40 with the skill vs 9/40 without); the generalization itself is v0.1, not yet clean-room tested — field reports especially welcome there.
- Every patch in the spec changelog traces to a real implementer question. That flywheel is the maintenance model: your questions are the next version.

## The guided path

The toolkit is the DIY route and always will be free. If you want to build this with your team — with feedback, a cohort, and a 90-day rollout plan — that's the [AI-Native Product Team course](https://empatika.com/courses/ai-native-product-team).

## License

MIT — see [LICENSE](LICENSE).
