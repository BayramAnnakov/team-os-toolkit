#!/usr/bin/env python3
"""Build the sample trace set for /team-improve.

Deterministic: re-running produces byte-identical output.

Synthetic logs of a small product team's agent, in the real Claude Code JSONL
schema, so the same extraction path serves the sample and a real machine. Shaped
from measurements of production logs: tool results dominate by volume,
machine-authored turns arrive in the user role, and human corrections are mostly
polite and indirect.

    python3 build_sample_traces.py [-o OUTDIR]

The traces are committed. You do not need to run this to do the exercise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os

PRODUCT = "Northwind"          # reuse the toolkit's existing example product
# Real logs measured ~92.6% tool_result. A transcript that reads cleanly is not a
# log, and a filter that looks unnecessary on clean data is the wrong lesson.
TOOL_MULT = 4
CWD = "/home/dev/northwind-ops"
BRANCH = "main"
VERSION = "2.1.235"

# --------------------------------------------------------------------------
# Sessions. Each turn: ("h", text) human · ("a", text) agent ·
# ("t", n) n tool results · ("m", kind) machine-authored contamination.
# --------------------------------------------------------------------------
SESSIONS: list[dict] = [
    # ---------- billing figures
    {"date": "2026-06-02", "turns": [
        ("h", "what did we bill last month?"),
        ("t", 6),
        ("a", "Total billed in May: 1,284,500. Top account: Contoso at 299,00."),
        ("h", "1.2 million? we're not there yet :) check the units on that table"),
        ("t", 4),
        ("a", "May billing: $12,845. Top account Contoso at $299."),
    ]},
    {"date": "2026-06-19", "turns": [
        ("m", "skill_preamble"),
        ("h", "pull ARR by plan tier"),
        ("t", 9),
        ("a", "Pro: 89,700/mo. Team: 149,500/mo. Enterprise: 420,000/mo."),
        ("h", "same thing as last time — those look like cents again"),
        ("t", 3),
        ("a", "Pro $897/mo. Team $1,495/mo. Enterprise $4,200/mo."),
    ]},
    {"date": "2026-07-08", "turns": [
        ("h", "revenue for the board deck please"),
        ("t", 11),
        ("a", "Q2 revenue: 3,912,000."),
        ("h", "Remember: every money column in billing_* is in cents. Divide by 100 before you show me anything."),
        ("t", 2),
        ("a", "Q2 revenue: $39,120."),
    ]},

    # ---------- user and activation metrics
    {"date": "2026-06-11", "turns": [
        ("h", "how many active users this week?"),
        ("t", 7),
        ("a", "412 active users in the last 7 days."),
        ("h", "is that including our own accounts?"),
        ("t", 5),
        ("a", "Excluding @northwind.io addresses: 361."),
    ]},
    {"date": "2026-06-24", "turns": [
        ("h", "weekly activation number"),
        ("t", 8),
        ("a", "Activation rate 34% (128 of 376)."),
        ("h", "hmm that seems high vs what the dashboard says"),
        ("t", 6),
        ("a", "Excluding internal workspaces: 29% (109 of 376)."),
    ]},
    {"date": "2026-07-14", "turns": [
        ("m", "sdk_scheduled"),
        ("t", 5),
        ("a", "Daily metrics: 44 signups, 402 WAU, 12 trials converted."),
    ]},
    {"date": "2026-07-21", "turns": [
        ("h", "who used the export feature last month?"),
        ("t", 9),
        ("a", "31 users. Top: qa-bot@northwind.io (204 exports), then 30 customers."),
        ("h", "does that have the test workspace in it?"),
        ("t", 4),
        ("a", "30 customers, excluding the test workspace."),
    ]},
    {"date": "2026-08-04", "turns": [
        ("h", "WAU trend for the last 6 weeks"),
        ("t", 12),
        ("a", "402, 398, 415, 431, 428, 440 — steady growth."),
        ("h", "can you split out staff vs customers on that"),
        ("t", 7),
        ("a", "Customers only: 351, 349, 362, 371, 369, 377. Staff accounts add ~50-60/wk."),
    ]},

    # ---------- churn review
    {"date": "2026-07-02", "turns": [
        ("h", "summarize the churn review for me"),
        ("t", 6),
        ("a", "Here's the summary, with a retention chart attached."),
        ("h", "don't include the chart — I'm pasting this into Slack and images get stripped"),
        ("t", 2),
        ("a", "Text-only summary below."),
    ]},

    # ---------- churn causes
    {"date": "2026-07-27", "turns": [
        ("h", "which customers churned last month and why?"),
        ("t", 8),
        ("a", "6 churned: Fabrikam, Tailspin, Adventure Works, Litware, Proseware, Wingtip."),
    ]},
    {"date": "2026-07-29", "turns": [
        ("h", "can you pull churn reasons out of the support tickets for last month"),
        ("t", 14),
        ("a", "From tickets: 3 cite missing SSO, 2 cite price, 1 cite an unresolved data-import bug."),
        ("h", "that's what I needed, thanks"),
    ]},

    # ---------- failed imports
    {"date": "2026-08-06", "turns": [
        ("h", "give me the 10 most recent failed imports with their job ids"),
        ("t", 10),
        ("a", "| Customer | Job | Status |\n| Contoso | job_8f2a… | failed |\n| Litware | job_31bc… | failed |"),
        ("h", "а id целиком можно?)) мне их в поиск вставлять"),
        ("t", 3),
        ("a", "job_8f2a41d7c9be4a02, job_31bc77e0a5124f8d, job_5d90ae13f7724b6c, …"),
    ]},

    # ---------- assorted sessions
    {"date": "2026-06-30", "turns": [
        ("h", "is the staging db up?"),
        ("t", 3),
        ("a", "Connection refused on staging-db:5432. It looks down."),
    ]},
    {"date": "2026-07-05", "turns": [
        ("m", "compact_summary"),
        ("h", "carry on where we left off"),
        ("t", 4),
        ("a", "Resuming the migration checklist. Steps 1-3 are done."),
    ]},
    {"date": "2026-07-11", "turns": [
        ("h", "what's the weather in Lisbon"),
        ("a", "I don't have weather access — that's outside what I'm connected to."),
    ]},
    {"date": "2026-07-16", "turns": [
        ("m", "teammate_message"),
        ("t", 6),
        ("a", "Acknowledged the hand-off; picking up the export audit."),
    ]},
    {"date": "2026-07-19", "turns": [
        ("h", "draft the release notes for 2.4"),
        ("t", 7),
        ("a", "Draft below: 4 features, 11 fixes, 2 breaking changes."),
        ("h", "great, ship it"),
    ]},
    {"date": "2026-08-11", "turns": [
        ("h", "why did the nightly job fail"),
        ("t", 9),
        ("a", "Timeout after 900s on the enrichment step. Retried twice, same result."),
        ("h", "ok I'll ask infra"),
    ]},
    {"date": "2026-08-14", "turns": [
        ("m", "sdk_scheduled"),
        ("t", 4),
        ("a", "Daily metrics: 51 signups, 440 WAU, 9 trials converted."),
    ]},

    # ---------- further sessions
    {"date": "2026-06-16", "turns": [
        ("h", "list the accounts with expiring trials"),
        ("t", 6),
        ("a", "9 trials expire in the next 7 days. Largest: Contoso (48 seats)."),
        ("h", "ok now draft an outreach note for the top three"),
        ("t", 5),
        ("a", "Three drafts below, one per account."),
    ]},
    {"date": "2026-06-27", "turns": [
        ("h", "what changed in the import pipeline this sprint?"),
        ("t", 8),
        ("a", "Four merged PRs: retry backoff, CSV delimiter sniffing, two schema migrations."),
        ("h", "and what about the export side?"),
        ("t", 7),
        ("a", "Export had one change: parallel chunking behind a flag, off by default."),
    ]},
    {"date": "2026-07-09", "turns": [
        ("h", "summarize this week's support themes"),
        ("t", 9),
        ("a", "Three themes: SSO setup friction, slow exports, unclear seat billing."),
        ("h", "can you do the same for last week so I can compare"),
        ("t", 8),
        ("a", "Last week: SSO setup, slow exports, and two reports of duplicate invoices."),
    ]},
    {"date": "2026-07-23", "turns": [
        ("h", "check whether the enrichment cache is stale"),
        ("t", 7),
        ("a", "Oldest partition is 4 days old; the job last succeeded on the 19th."),
        ("h", "right, let's leave it — infra is rebuilding that box tomorrow"),
    ]},
    {"date": "2026-07-31", "turns": [
        ("h", "how many seats does Litware have"),
        ("t", 5),
        ("a", "Litware: 120 seats, 84 active in the last 30 days."),
        ("h", "perfect, that's what I needed"),
    ]},
    {"date": "2026-08-08", "turns": [
        ("h", "write the migration runbook for 2.5"),
        ("t", 11),
        ("a", "Runbook drafted: 7 steps, 2 requiring downtime, rollback noted per step."),
        ("h", "add a section on what to do if step 4 half-applies"),
        ("t", 6),
        ("a", "Added: partial-apply detection and the reconciliation query."),
    ]},
    {"date": "2026-08-17", "turns": [
        ("h", "which imports failed more than twice this month"),
        ("t", 10),
        ("a", "Five jobs failed 3+ times, all on the same customer schema."),
        ("h", "open a ticket for that and assign it to the data team"),
        ("t", 4),
        ("a", "Ticket opened and assigned."),
    ]},
    {"date": "2026-08-19", "turns": [
        ("h", "is the 2.5 release note ready to send?"),
        ("t", 5),
        ("a", "Draft is ready. 4 features, 9 fixes, no breaking changes."),
        ("h", "send it"),
    ]},
]

MACHINE_TEXT = {
    "skill_preamble": (
        "Base directory for this skill: /home/dev/.claude/skills/reporting\n\n"
        "# Reporting CLI\n\nAlways use the `report` CLI for metric pulls. Never query the "
        "warehouse directly. Do not assume a cached extract is fresh."
    ),
    "sdk_scheduled": (
        "Post the daily metrics summary to #ops. Do not assume the cache is fresh — "
        "check the extract timestamp first. Never include internal accounts."
    ),
    "teammate_message": (
        "<teammate-message teammate_id=\"export-audit\" color=\"blue\">\n"
        "{\"type\":\"idle_notification\",\"from\":\"export-audit\"}\n</teammate-message>"
    ),
    "compact_summary": (
        "This session is being continued from a previous conversation that ran out of "
        "context. The summary below covers the earlier portion.\n\nSummary: migration "
        "checklist steps 1-3 complete; do not re-run step 2."
    ),
}

TOOL_SNIPPETS = [
    "SELECT count(*) FROM app_user WHERE last_seen > now() - interval '7 days';\n-- 412",
    "rows=18 cols=4 (truncated)",
    "$ ./report metrics --range 7d\nok (1.2s)",
    "warehouse: 3 partitions scanned, 1.4M rows",
    "ERROR: relation \"billing_invoice_v2\" does not exist\nHINT: perhaps you meant billing_invoice",
    "file: ops/queries/activation.sql (61 lines)",
    "HTTP 200 · 84ms · 12 records",
]


def _uuid(seed: str) -> str:
    h = hashlib.sha1(seed.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def build():
    lines: list[dict] = []
    # Emit in DATE order. Grouped-by-pattern output let students cluster by
    # noticing candidates were neighbours rather than by root cause.
    for si, sess in enumerate(sorted(SESSIONS, key=lambda x: x['date'])):
        sid = _uuid(f"session-{si}-{sess['date']}")
        clock = [9, 0]

        def ts() -> str:
            clock[1] += 3
            if clock[1] >= 60:
                clock[1] -= 60
                clock[0] += 1
            return f"{sess['date']}T{clock[0]:02d}:{clock[1]:02d}:00.000Z"

        base = {"isSidechain": False, "userType": "external", "entrypoint": "cli",
                "cwd": CWD, "sessionId": sid, "version": VERSION, "gitBranch": BRANCH}
        parent = None
        n = 0

        def emit(rec: dict):
            nonlocal parent, n
            uid = _uuid(f"{sid}-{n}")
            rec.update(base)
            rec["uuid"] = uid
            rec["parentUuid"] = parent
            parent = uid
            n += 1
            lines.append(rec)

        for kind, val in sess["turns"]:
            if kind == "h":
                emit({"type": "user", "timestamp": ts(), "promptSource": "typed",
                      "permissionMode": "default",
                      "message": {"role": "user", "content": val}})
            elif kind == "a":
                emit({"type": "assistant", "timestamp": ts(), "requestId": _uuid(f"r{sid}{n}"),
                      "message": {"role": "assistant",
                                  "content": [{"type": "text", "text": val}]}})
            elif kind == "t":
                for k in range(val * TOOL_MULT):
                    emit({"type": "user", "timestamp": ts(),
                          "message": {"role": "user", "content": [{
                              "type": "tool_result",
                              "tool_use_id": _uuid(f"tu{sid}{n}{k}"),
                              "content": TOOL_SNIPPETS[(n + k) % len(TOOL_SNIPPETS)]}]}})
            elif kind == "m":
                rec = {"type": "user", "timestamp": ts(),
                       "message": {"role": "user", "content": MACHINE_TEXT[val]}}
                if val == "sdk_scheduled":
                    rec["promptSource"] = "sdk"
                elif val == "compact_summary":
                    rec["isCompactSummary"] = True
                    rec["promptSource"] = "typed"
                else:
                    rec["promptSource"] = "typed"
                emit(rec)
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "traces"))
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    lines = build()
    by_session: dict[str, list[dict]] = {}
    for rec in lines:
        by_session.setdefault(rec["sessionId"], []).append(rec)

    for sid, recs in by_session.items():
        with open(os.path.join(a.outdir, f"{sid}.jsonl"), "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    tool = sum(1 for r in lines if isinstance(r["message"].get("content"), list)
               and any(b.get("type") == "tool_result" for b in r["message"]["content"]))
    print(f"sessions {len(by_session)}  lines {len(lines)}  "
          f"tool_result {tool} ({100.0*tool/len(lines):.1f}%)  -> {a.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
