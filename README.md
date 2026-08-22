# Team OS Toolkit

Build a team knowledge repo that answers questions instead of you — then give it a voice.

From the AI Natives build sessions (June 2026). Reference implementation running in production at Onsa.ai.

## Quickstart

Open Claude Code (or any agent that supports the skills standard) **in this folder** — the skills load
automatically. Then, in order:

> ⚠️ **Already cloned this before? `git pull` is not enough — quit Claude Code and start it again.**
> Skills and agent types are read **once, when a session starts**, and are never re-scanned. Pull into a
> running session and the new files sit on disk invisible to it: new skills won't be offered, and
> `/synthetic-interviews` will fail with `Agent type 'no-tools-reviewer' not found`.

| Step | Skill / Spec | What you get |
|---|---|---|
| 1 | `/init-team-os` | Your team knowledge repo, built from evidence your machine already has (Claude Code history, MCP config, existing docs). You answer at most 5 questions. Ends with a real answer to your team's #1 recurring question + the message to post in your team chat. |
| 2 | `/init-team-brain` | The product-knowledge layer on top: glossary and object model mined from your code, rot-rate tiers, and a drift checker that FAILS commits when docs disagree with code. You watch it fail before you trust it. |
| 3 | `/init-team-decisions` | The judgment layer: a `decisions.md` of dated, sourced decision principles mined from your meetings and chats, plus a generated `decide-like-<your-team>` apprentice skill — recommendation first, gap analysis on reasoning, episode log, calibration, graduation. Proven by refusal: you watch it decline to answer until a recommendation is committed. |
| 4 | `/team-prototype` | The prototyping layer: a feature description becomes a working prototype at a URL someone else can open, autonomously improved across independent Generator-Evaluator rounds. What makes it *yours*: vocabulary from your glossary, users from your personas, sample data obeying your object model — and **evaluation criteria mined from your `decisions.md`, cited by ID.** A critic that says *"this contradicts D-01, ratified 2026-05-28"* is doing something no generic prototype tool can. It's also the cheapest audit of steps 1–3 you'll get: the spec's `Assumptions` section is everything the agent had to invent because your brain didn't say. |
| 4b | `/synthetic-interviews` | The companion to step 4: a synthetic user panel that walks what you just built as three personas built from *your* brain — each as an independent agent that never saw the spec — and splits every finding into **"a real session would also have found this"** vs **"I'm guessing."** The second list is the product. Deliberately not a survey tool: it hands off to Semantic Similarity Rating for anything with an N and a percentage. |
| 5 | `/team-workflow` | The execution layer: a job you repeat — ticket → PR, meeting → notes → tickets, call → CRM update — becomes a workflow an agent runs end to end, **with a human gate at the one step that can't be taken back.** It decides first whether the job deserves a harness at all (many don't — say so and build a slash command), then which of three tiers it belongs at, and derives the gate from your `decisions.md` so it names the principle by ID when it stops. The bar it holds you to: nothing is proven until you have watched it correctly produce **nothing** on an input that deserved nothing. |
| 6 | `/team-improve` | The improvement layer: your agent's own session traces become **staged improvement candidates and a frozen test set** — and then a scored run. It mines the places a person corrected the agent (mechanically first: on real logs ~92% of `user` lines are tool results, and a keyword pass is ~80% false positives), clusters by root cause, **cuts what will not transfer**, and derives cases. The rule it will not bend: **the agent brings the case, the human writes the pass criteria.** A case with empty `expected_signals` is reported UNGRADED, never passed, and the grader must be a **different vendor** from the agent under test — judges measurably prefer their own family's output. Ships with `examples/sample-traces/` for anyone who cannot open their own logs. |
| 7 | [ROBIN-SPEC.md](ROBIN-SPEC.md) + `/robin-init` | An always-on **AI chief of staff** that lives in your chat with the repo as its brain — its duties (digest, briefs, meeting prep, whatever YOUR processes need) are declared in your repo, not hardcoded. The spec is the product — tell your coding agent to implement it on YOUR stack ([openai/symphony](https://github.com/openai/symphony) model). `/robin-init` drafts your soul.md + duty roster and writes the kickoff prompt. |

## The rule behind the packaging

**Files → skill. Running process → spec.** Skills are performed by your agent in one sitting (steps 1–5 produce files). Robin must keep running after the session ends, on your stack, operated by you — so it ships as a spec your own coding agent implements, not as a template you can't debug. Step 5 sits on the same line: it produces a workflow and its gate, and hands a hosted deployment off as a kickoff rather than deploying anything itself.

## The order matters

A Robin without a knowledge repo is just a chatbot. Build the repo first (step 1), prove the value to one teammate (post the answer where they'll see it), and only then add enforcement (step 2), judgment (step 3), building (step 4), execution (step 5), and the agent (step 6). Adoption follows demonstrated value, not announcement.

Step 5 is the on-ramp to step 6, and doing it first is the point: **Robin is many always-on workflows, so build one you can watch before you deploy a fleet you can't.** The gate you place by hand in step 5 is the thing you will most wish you understood when an agent is running while you sleep.

Step 4 is also the honest test of steps 1–3. If the loop had to invent your vocabulary and guess your rules, the brain isn't load-bearing yet — and you would much rather learn that from a spec's `Assumptions` list than from an agent quietly guessing in front of a customer.

## A target structure to grow into

Want to see a finished one? [`examples/northwind/`](examples/northwind/) holds a fictional team's raw evidence (chat export, weeklies, task tracker) **and** [`examples/northwind/team-os/`](examples/northwind/team-os/) — the brain those skills produce from it: glossary, personas, object model, and a `decisions.md` with dated, sourced principles. Run any skill against it end-to-end when you don't have your own material handy.

`/init-team-os` builds the *minimal* seed — folders after the answer, never empty scaffolds. [`template/`](template/) is the **map** of where that seed grows: the lean, proven shape generalized from the `onsa-brain` reference (`now.md`, a numbered `product/`, `decisions.md`, `skills/`, the frontmatter + folder-index conventions). It's a reference to grow *into*, not a scaffold to create up front — copy a file from it when real content demands it.

## Exercises

Workshop sheets live in [`exercises/`](exercises/) — start with
[`w4/exercise-1-hooks.md`](exercises/w4/exercise-1-hooks.md), which turns a ratified decision into a
hook that blocks, and ships a working guard next to it.

## Feedback

Every question a skill asks that it could have mined, every ambiguity your coding agent hits in ROBIN-SPEC — those are bugs. Report them to @BayramAnnakov.

## Provenance

- Reference implementation in production at Onsa.ai: 276+ logged agent interactions, 4 teammates, ~$30–40/month.
- Skills 1–2 and /robin-init clean-room tested (fixture machines, scripted users, blind judges) before release; ROBIN-SPEC's v0.3 core was validated by a stranger coding agent building a working Robin from the document alone — M0 passed on the first run, at $0.039. Later additions (v0.4+) are field-patched from real implementer questions and not yet re-validated clean-room.
- `/init-team-decisions` (added Jun 12) generalizes the reference's decision system, which carries its own blind-judged eval (40/40 with the skill vs 9/40 without); the generalization itself is v0.1, not yet clean-room tested — field reports especially welcome there.
- `/team-prototype` (added Jul 26) is **v0.1**. Field-tested end-to-end against `examples/northwind/team-os/`: it mined 3 evaluation criteria from that brain's `decisions.md`, cited them by ID, and reported honestly which principles it could *not* use and why. A blind critic then scored the build **3/10** on the team's own "never state an unconfirmed number as fact" rule — it had printed the very threshold the brain flags as unsettled — and **8/10** one round later. Not clean-room tested with a stranger agent; the criteria-mining step in particular is young and gets better the more real brains it sees. Field reports very welcome.
- `/team-workflow` (added Aug 9) is **v0.1 and the youngest thing here.** Cold-run three times from a fresh clone — against the Northwind fixture, and as a no-credentials/no-brain user — where it correctly refused to invent principle IDs, declined to write a hook for a call that could never occur, and built de-duplication unprompted after finding the same task in three consecutive weeklies. Two independent reviewers (a second Anthropic model and OpenAI's codex) then returned **14 findings on the first draft, including a real one: the gate as originally specified used exit code 2, which *blocks* rather than *asks* — a control no human could approve.** That is fixed and the three hook decisions are now verified by running them. Not clean-room tested with a stranger agent, and Tier 2 has never been deployed end-to-end by anyone but its author. Field reports very welcome.
- Every patch in the spec changelog traces to a real implementer question. That flywheel is the maintenance model: your questions are the next version.

## The guided path

The toolkit is the DIY route and always will be free. If you want to build this with your team — with feedback, a cohort, and a 90-day rollout plan — that's the [AI-Native Product Team course](https://empatika.com/courses/ai-native-product-team).

## License

MIT — see [LICENSE](LICENSE).
