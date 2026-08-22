# Exercise 2 — Give the loop a body (`/robin-init`)

**Time:** 15 minutes if it survives · **Sacrificial. If Exercise 1 runs long, this becomes
homework and nothing is lost** — the skill is shipped, tested, and works unattended.

> **Facilitator: do not dispatch this before minute 100.** Exercise 1's scoring step is the
> deliverable. This one has a working home in `homework.md` and a skill that does not need a
> classroom.

---

## Why this exists, in one sentence

Exercise 1 built a loop. A loop needs something to improve.

Most of you pointed it at your coding sessions today, because that is the evidence everybody
has. That works, and it is not where the value is. The value is an agent that runs for your
**team** — one that answers the same questions you keep answering, on a schedule, from the
repo you have been building since Session 1.

The `robin/` folder in the cohort brain repo has been empty since June, with a note saying
*"we build Robin in the session that teaches it."* This is that session.

---

## Run it

```bash
cd ~/GH/team-os-toolkit && git pull
```

Then, from **your own Team OS repo**:

```
/robin-init
```

It asks at most five questions. Most of what it needs it mines: your chat platform from your
MCP config, your runtime from what is installed, your data sources from the pointers already
in your repo.

**It does not write agent code.** It writes four things into your repo:

| File | What it is |
|---|---|
| `soul.md` | who your agent is for this team, and its response conventions |
| `robin/duties.md` | the roster — trigger, inputs, output, destination, owner |
| `ROBIN-SPEC.local.md` | the spec with every open slot resolved or explicitly deferred |
| `KICKOFF.md` | the prompt you paste into a coding agent to build it |

Duties live in your repo, not in config. Changing one is a pull request, like any other team
knowledge. That is the point.

---

## The one thing to carry over from Exercise 1

When it asks for your team's recurring question — the M0 acceptance test — **do not invent
one.** Use a case you wrote an hour ago, with the criteria you wrote yourself.

You wrote those before this agent existed. That is the only moment they could have been
honest, and it is the closest thing to a held-out set you will ever get for free.

---

## Checkpoint — post in chat

```
slots resolved: N   ·   questions asked: M
duties declared: X   ·   M0 test: <your recurring question, one line>
```

---

## No Team OS repo?

The skill offers the on-ramp itself — `/init-team-os`, five questions, a few minutes — and
then continues. There is deliberately no skip path. **An agent without a knowledge repo is
just a chatbot**, and you would be building the thing this course spent four sessions
arguing against.

---

## Fast finishers — build M0 now

One question. One answer. From your repo. With the source file cited.

```
Implement M0 from ./ROBIN-SPEC.local.md on <your stack>.
Acceptance test: answer "<your recurring question>" from <your repo path>,
citing the source file. Nothing else. Log every clarifying question you have
to ask into ./QUESTIONS.md instead of guessing.
```

That last instruction matters more than it looks. **Every question your coding agent has to
ask is a defect in the spec**, and the spec improves by collecting them rather than by
someone imagining what was unclear.

---

## What NOT to do today

**Do not deploy it into a live team channel from this call.** An agent that answers your
team's questions wrongly, in public, on day one, costs more trust than it saves time.

M0 is local and private. M1 — a teammate asking in the real chat and getting a repo-grounded
answer with a citation — is the moment it starts existing for your team, and it deserves a
day when you are watching.
