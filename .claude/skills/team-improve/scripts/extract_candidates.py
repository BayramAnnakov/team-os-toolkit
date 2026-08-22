#!/usr/bin/env python3
"""Extract correction candidates from agent session logs.

Mechanical work only. This script decides what COULD be a human correcting the
agent. It never decides whether something IS one — that judgment belongs to the
model reading the output, because it provably cannot be done with keywords.

    python3 extract_candidates.py <traces_dir> [-o out.jsonl] [--since YYYY-MM-DD]
                                  [--max-files N] [--stats-only]

Input formats
-------------
1. **Claude Code / Codex JSONL** (auto-detected): one JSON object per line with
   `type`, `message`, `promptSource`, `timestamp`.
2. **Generic JSONL** fallback: one object per line with at least
   `{"role": "user"|"assistant", "text": "...", "ts": "..."}`.
   Export from any other agent into this shape and the same pipeline applies.

Why the filter looks like this (all measured, 2026-08-22, 800 real sessions):
  - 92.6% of `type:user` lines are `tool_result` — the environment answering,
    not a person.
  - A keyword pass over unfiltered turns was ~80% false positives: skill
    preambles, scheduled prompts and inter-agent messages are full of
    "don't" and "never".
  - Only a turn that FOLLOWS an assistant reply can be a correction.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HUMAN_SOURCES = {"typed", "queued", "suggestion_accepted"}

# Machine-authored text that arrives in a user-role turn. Anchored at the start.
MACHINE_PREFIX = re.compile(
    r"^\s*(?:"
    r"<teammate-message"
    r"|Another Claude session sent a message:"
    r"|<task-notification>"
    r"|<command-message>"
    r"|<command-name>"
    r"|<local-command"
    r"|<system-reminder>"
    r"|Base directory for this skill:"
    r"|Caveat:"
    r"|This session is being continued from a previous conversation"
    r")",
    re.I,
)


def _text(content) -> str | None:
    """Plain text of a message, or None if there is none.

    A message carrying a tool_result AND text is not discarded: the text is a
    person writing alongside the result, which is exactly a correction. Only a
    message that is *purely* tool results returns None.
    """
    if isinstance(content, str):
        return content or None
    if isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        joined = "\n".join(p for p in parts if p)
        if joined:
            return joined
        return None
    return None


def _is_pure_tool_result(content) -> bool:
    return (isinstance(content, list)
            and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)
            and not any(isinstance(b, dict) and b.get("type") == "text" and b.get("text") for b in content))


def classify(rec: dict) -> tuple[str, str | None]:
    """-> (role, text). role in {human, assistant, machine, skip}."""
    # --- generic fallback shape ---
    if "role" in rec and "type" not in rec:
        role = rec.get("role")
        txt = rec.get("text") or _text(rec.get("content"))
        if role == "assistant":
            return "assistant", txt
        if role == "user" and txt:
            return ("machine", txt) if MACHINE_PREFIX.match(txt) else ("human", txt)
        return "skip", None

    # --- Claude Code / Codex shape ---
    t = rec.get("type")
    if t == "assistant":
        return "assistant", _text((rec.get("message") or {}).get("content"))
    if t != "user":
        return "skip", None
    if rec.get("isMeta") or rec.get("isCompactSummary"):
        return "machine", None
    content = (rec.get("message") or {}).get("content")
    if _is_pure_tool_result(content):
        return "skip", None
    txt = _text(content)
    if not txt or not txt.strip():
        return "skip", None
    if MACHINE_PREFIX.match(txt):
        return "machine", txt
    src = rec.get("promptSource")
    if src is None:
        # Legacy logs predate the field. Prefix check above is the only guard.
        return "human", txt
    return ("human", txt) if src in HUMAN_SOURCES else ("machine", txt)


def walk(root: str, max_files: int | None):
    files = []
    if os.path.isfile(root):
        files = [root]
    else:
        for dp, _, names in os.walk(root):
            for n in names:
                if n.endswith(".jsonl"):
                    files.append(os.path.join(dp, n))
        files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[:max_files] if max_files else files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("traces_dir")
    ap.add_argument("-o", "--out", default="candidates.jsonl")
    ap.add_argument("--since", default=None, help="ISO date; keep turns at or after it")
    ap.add_argument("--max-files", type=int, default=None)
    ap.add_argument("--context-chars", type=int, default=1200,
                    help="how much of the preceding agent reply to carry (default 1200)")
    ap.add_argument("--stats-only", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(a.traces_dir):
        print(f"ERROR: no such path: {a.traces_dir}", file=sys.stderr)
        return 2

    files = walk(a.traces_dir, a.max_files)
    if not files:
        print(f"ERROR: no .jsonl files under {a.traces_dir}", file=sys.stderr)
        return 2

    stats = {"files": len(files), "lines": 0, "tool_result_or_skip": 0, "machine": 0,
             "human": 0, "human_after_reply": 0, "kept": 0}
    out: list[dict] = []
    dropped_samples: list[str] = []

    for path in files:
        prev_reply, prev_ts = None, None
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                stats["lines"] += 1
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                role, txt = classify(rec)
                if role == "human" and not txt:
                    role = "skip"  # defensive: never index a None below
                if role == "assistant":
                    # An assistant turn carrying ONLY a tool_use block has no text.
                    # It must not erase the last real reply, or every correction that
                    # follows a tool call is silently dropped.
                    if txt:
                        prev_reply = txt
                        prev_ts = rec.get("timestamp") or rec.get("ts")
                    continue
                if role == "machine":
                    stats["machine"] += 1
                    # Keep a few, to SHOW what was dropped. Otherwise the filter looks
                    # like bureaucracy: these turns state real-sounding rules and are
                    # exactly what a keyword search would surface as "corrections".
                    if txt and len(dropped_samples) < 4:
                        one = " ".join(txt.split())[:150]
                        if (one not in dropped_samples
                                and re.search(r"\b(never|don'?t|do not|always|must)\b", one, re.I)):
                            dropped_samples.append(one)
                    continue
                if role == "skip":
                    stats["tool_result_or_skip"] += 1
                    continue
                stats["human"] += 1
                if prev_reply is None:
                    continue
                stats["human_after_reply"] += 1
                ts = rec.get("timestamp") or rec.get("ts") or prev_ts or ""
                if a.since and ts and ts[:10] < a.since:
                    prev_reply = None
                    continue
                out.append({
                    "session": os.path.basename(path),
                    "cwd": rec.get("cwd"),
                    "ts": ts,
                    "agent_said": (prev_reply or "")[-a.context_chars:],
                    "human_said": (txt or "")[:2000],
                })
                stats["kept"] += 1
                prev_reply = None

    if not a.stats_only:
        with open(a.out, "w", encoding="utf-8") as f:
            for r in out:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("=" * 58)
    print("  MECHANICAL FILTER — what could be a correction")
    print("=" * 58)
    print(f"  files scanned            {stats['files']:>8,}")
    print(f"  lines read               {stats['lines']:>8,}")
    print(f"  tool results / other     {stats['tool_result_or_skip']:>8,}   dropped")
    print(f"  machine-authored turns   {stats['machine']:>8,}   dropped")
    print(f"  human-typed turns        {stats['human']:>8,}")
    print(f"  ...following a reply     {stats['human_after_reply']:>8,}   <- eligible")
    if a.stats_only:
        print(f"  eligible (NOT written)   {stats['kept']:>8,}   --stats-only")
    else:
        # Report what is actually on disk, not what we believe we wrote.
        on_disk = sum(1 for _ in open(a.out, encoding="utf-8")) if os.path.exists(a.out) else 0
        print(f"  written to {a.out:<14} {on_disk:>8,}"
              + ("" if on_disk == stats["kept"] else f"   !! expected {stats['kept']:,}"))
    print("=" * 58)
    if stats["kept"] == 0:
        print("  No candidates. Widen --since, raise --max-files, or check the path.")
    else:
        print("  NOT all of these are corrections. A model must now read each one")
        print("  against `agent_said` and judge. Keywords cannot do this — measured.")

    if dropped_samples:
        print("\n  Dropped as machine-authored — note what they say:")
        for d in dropped_samples:
            print(f"    · {d}")
        print("  These are skill preambles, scheduled prompts and inter-agent messages.")
        print("  They read like team policy and nobody typed them. A keyword search")
        print("  would have returned every one of them as a 'correction'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
