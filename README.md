# Team OS Toolkit

Build a team knowledge repo that answers questions instead of you — then give it a voice.

From the AI Natives build sessions (June 2026). Reference implementation running in production at Onsa.ai.

## Quickstart

Open Claude Code (or any agent that supports the skills standard) **in this folder** — the skills load automatically. Then, in order:

| Step | Skill / Spec | What you get |
|---|---|---|
| 1 | `/init-team-os` | Your team knowledge repo, built from evidence your machine already has (Claude Code history, MCP config, existing docs). You answer at most 5 questions. Ends with a real answer to your team's #1 recurring question + the message to post in your team chat. |
| 2 | `/init-team-brain` | The product-knowledge layer on top: glossary and object model mined from your code, rot-rate tiers, and a drift checker that FAILS commits when docs disagree with code. You watch it fail before you trust it. |
| 3 | [ROBIN-SPEC.md](ROBIN-SPEC.md) + `/robin-init` | An always-on **AI chief of staff** that lives in your chat with the repo as its brain — its duties (digest, briefs, meeting prep, whatever YOUR processes need) are declared in your repo, not hardcoded. The spec is the product — tell your coding agent to implement it on YOUR stack ([openai/symphony](https://github.com/openai/symphony) model). `/robin-init` drafts your soul.md + duty roster and writes the kickoff prompt. |

## The rule behind the packaging

**Files → skill. Running process → spec.** Skills are performed by your agent in one sitting (steps 1–2 produce files). Robin must keep running after the session ends, on your stack, operated by you — so it ships as a spec your own coding agent implements, not as a template you can't debug.

## The order matters

A Robin without a knowledge repo is just a chatbot. Build the repo first (step 1), prove the value to one teammate (post the answer where they'll see it), and only then add enforcement (step 2) and the agent (step 3). Adoption follows demonstrated value, not announcement.

## Feedback

Every question a skill asks that it could have mined, every ambiguity your coding agent hits in ROBIN-SPEC — those are bugs. Report them to @BayramAnnakov.

## Provenance

- Reference implementation in production at Onsa.ai: 276+ logged agent interactions, 4 teammates, ~$30–40/month.
- All three skills clean-room tested (fixture machines, scripted users, blind judges) before release; ROBIN-SPEC v0.4 was validated by a stranger coding agent building a working Robin from the document alone — M0 passed on the first run, at $0.039.
- Every patch in the spec changelog traces to a real implementer question. That flywheel is the maintenance model: your questions are the next version.

## The guided path

The toolkit is the DIY route and always will be free. If you want to build this with your team — with feedback, a cohort, and a 90-day rollout plan — that's the [AI-Native Product Team course](https://empatika.com/courses/ai-native-product-team).

## License

MIT — see [LICENSE](LICENSE).
