#!/usr/bin/env python3
"""Score a frozen case set — the leg the loop is missing without it.

Staging a candidate is not learning. A change to permanent behaviour lands only
when three things hold: a named human, a versioned diff, and **a number on a
frozen set the proposing agent did not score**. This script produces the number.

    python3 run_cases.py improve/cases \\
        --agent 'claude -p {q}' \\
        --grader 'codex exec -s read-only --skip-git-repo-check {q}'

Two rules it enforces, and will not be talked out of:

1. **A case with no `expected_signals` is not scored.** It is reported as
   UNGRADED. The human writes the criteria; that is the whole point, and a run
   that quietly grades against nothing is worse than no run.
2. **The grader should not be the same model as the agent under test.** Evaluators
   measurably prefer *their own generations* (Panickssery, Bowman & Feng, 2024 —
   arXiv:2404.13076); related work reports the effect leaking across models of the
   same family. Either way, a same-model grade is not independent evidence. The
   script warns when they match. `--grader none` hands grading to a person, which
   is the most independent option available.

Offline: `--agent none` prompts you to paste the answer. Works with no API at all.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


def parse_case(path: str) -> dict | None:
    """Minimal YAML-subset parse: scalars and `- ` lists. No dependency."""
    raw = open(path, encoding="utf-8").read()
    m = FM.match(raw)
    if not m:
        print(f"  !! {os.path.basename(path)}: no --- frontmatter, skipped")
        return None
    head, body = m.group(1), m.group(2).strip()
    case: dict = {"path": path, "question": body, "expected_signals": []}
    key = None
    for line in head.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and key:
            case.setdefault(key, [])
            if isinstance(case[key], list):
                case[key].append(line.lstrip()[2:].strip().strip("\"'"))
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            key = k.strip()
            v = v.strip()
            case[key] = [] if v == "" else v.strip("\"'")
    case["id"] = case.get("id") or os.path.splitext(os.path.basename(path))[0]
    if not isinstance(case.get("expected_signals"), list):
        case["expected_signals"] = []
    return case


def run_cmd(template: str, question: str, timeout: int) -> tuple[bool, str]:
    """Run a user-supplied command template with the question substituted.

    The template is intentionally shell-interpreted — it is typed by the operator
    and carries pipes/flags. The QUESTION is not: it comes from a case file that
    may be shared between teams, so it is shell-quoted before substitution.
    `shlex.quote` is POSIX; `list2cmdline` is Windows-only quoting and would let
    `; rm -rf ~ ;` in a case body execute.
    """
    if "{q}" not in template:
        template += " {q}"
    quote = shlex.quote if os.name != "nt" else subprocess.list2cmdline
    safe = quote(question) if os.name != "nt" else quote([question])
    cmd = template.replace("{q}", safe)
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s"
    out = (p.stdout or "").strip() or (p.stderr or "").strip()
    return p.returncode == 0 and bool(out), out


GRADE_PROMPT = """You are grading one answer against criteria a human wrote. \
Do not judge style, length or tone. Judge only whether each criterion is met.

QUESTION:
{q}

ANSWER UNDER TEST:
{a}

CRITERIA (written by a human — treat as authoritative, do not reinterpret):
{s}

Reply with ONLY a JSON object, no prose, no code fence:
{{"signals": [{{"signal": "<verbatim criterion>", "met": true|false, \
"why": "<max 15 words>"}}], "notes": "<max 25 words, or empty>"}}"""


def grade_by_human(case: dict, answer: str) -> dict:
    """A person grades, one criterion at a time. This is not a degraded mode.

    A human grader is more independent than any model, and it is the only path
    that works with no second vendor, on a locked laptop, or when the answer
    must not leave the room.
    """
    print("\n   ── HUMAN GRADING ──")
    print(f"   Q: {case['question'][:300]}")
    print(f"\n   ANSWER:\n   {answer[:1200]}")
    sigs = []
    for s in case["expected_signals"]:
        while True:
            print(f"\n   Criterion: {s}")
            v = input("   met? [y/n] ").strip().lower()
            if v in ("y", "yes", "n", "no"):
                break
        why = ""
        if v.startswith("n"):
            why = input("   why not (few words): ").strip()
        sigs.append({"signal": s, "met": v.startswith("y"), "why": why})
    return {"signals": sigs, "notes": "graded by a human"}


def grade(case: dict, answer: str, grader: str, timeout: int) -> dict:
    sig = "\n".join(f"- {s}" for s in case["expected_signals"])
    prompt = GRADE_PROMPT.format(q=case["question"], a=answer[:6000], s=sig)
    ok, out = run_cmd(grader, prompt, timeout)
    if not ok:
        return {"error": out[:300]}
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        return {"error": "grader returned no JSON: " + out[:200]}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"error": f"unparseable grader JSON: {e}"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cases_dir")
    ap.add_argument("--agent", default="claude -p {q}",
                    help="command under test; 'none' to paste answers by hand")
    ap.add_argument("--grader", default="codex exec -s read-only --skip-git-repo-check {q}",
                    help="grader command — use a DIFFERENT vendor than --agent; "
                         "'none' means a PERSON grades, which is the most independent option")
    ap.add_argument("--out", default=None, help="results markdown (default: <cases_dir>/../results/)")
    ap.add_argument("--timeout", type=int, default=180)
    a = ap.parse_args()

    if os.path.isfile(a.cases_dir):
        paths = [a.cases_dir]          # a single case file is a legitimate run
    else:
        paths = sorted(glob.glob(os.path.join(a.cases_dir, "*.md")))
    if not paths:
        print(f"No cases in {a.cases_dir}. Write some first (/team-improve Phase 4).")
        return 2

    def vendor(c: str) -> str:
        c = c.lower()
        for v in ("claude", "codex", "cursor-agent", "agy", "gemini"):
            if v in c:
                return v
        return "unknown"

    if (a.agent != "none" and a.grader != "none"
            and vendor(a.agent) == vendor(a.grader) != "unknown"):
        print(f"\n  ⚠  agent and grader are both '{vendor(a.agent)}'. A judge prefers its own")
        print("     family's output — this grade is not independent. Continuing anyway.\n")

    cases = [c for c in (parse_case(p) for p in paths) if c]
    graded, ungraded, rows, errors = [], [], [], []

    for c in cases:
        print(f"\n── {c['id']}")
        if not c["expected_signals"]:
            print("   UNGRADED — expected_signals is empty. A human must write them.")
            ungraded.append(c)
            continue
        if a.agent == "none":
            print(f"   Q: {c['question'][:160]}")
            print("   Paste the answer, then a line containing only END:")
            buf = []
            for line in sys.stdin:
                if line.strip() == "END":
                    break
                buf.append(line)
            answer = "".join(buf).strip()
            if not answer:
                # Empty paste (stray Ctrl-D, piped input). Grading "" would produce a
                # confident-looking zero for a case nobody actually ran.
                print("   NOT RUN — no answer was pasted.")
                errors.append((c["id"], "agent", "empty answer pasted"))
                continue
        else:
            ok, answer = run_cmd(a.agent, c["question"], a.timeout)
            if not ok:
                # An infrastructure failure is NOT a score of zero. Recording it as
                # 0/N invents a false low number — the exact failure mode this whole
                # skill exists to prevent. Excluded from the denominator instead.
                print(f"   AGENT FAILED: {answer[:160]}")
                errors.append((c["id"], "agent", answer[:200]))
                continue
        res = (grade_by_human(c, answer) if a.grader == "none"
               else grade(c, answer, a.grader, a.timeout))
        if "error" in res:
            print(f"   GRADER FAILED: {res['error'][:160]}")
            errors.append((c["id"], "grader", res["error"][:200]))
            continue
        sigs = res.get("signals", [])
        met = sum(1 for s in sigs if s.get("met"))
        for s in sigs:
            print(f"   [{'PASS' if s.get('met') else 'FAIL'}] {s.get('signal','')[:70]}"
                  f"{'' if s.get('met') else '  — ' + str(s.get('why',''))[:50]}")
        rows.append((c["id"], met, len(c["expected_signals"]), res.get("notes", "")))
        graded.append((c, answer, res))

    total_met = sum(r[1] for r in rows)
    total_sig = sum(r[2] for r in rows)
    print("\n" + "=" * 58)
    print(f"  {len(rows)} case(s) scored · {total_met}/{total_sig} criteria met")
    if ungraded:
        print(f"  {len(ungraded)} UNGRADED (no human criteria): "
              + ", ".join(c["id"] for c in ungraded))
    if errors:
        print(f"  {len(errors)} NOT RUN (infrastructure, NOT a zero): "
              + ", ".join(f"{cid}[{kind}]" for cid, kind, _ in errors))
        print("     A tool that failed is not an agent that was wrong. Fix and re-run")
        print("     before quoting any number from this session.")
    print(f"  agent  : {a.agent}")
    print(f"  grader : {a.grader}")
    print("=" * 58)
    print("  Read the FINDINGS before the score. A single total moves with grader")
    print("  variance; a criterion that fails twice for the same reason is a result.")

    outdir = a.out or os.path.join(os.path.dirname(os.path.abspath(a.cases_dir)), "results")
    os.makedirs(outdir, exist_ok=True)
    dest = os.path.join(outdir, "latest.md")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("# Case run\n\n")
        f.write(f"- agent: `{a.agent}`\n- grader: `{a.grader}`\n")
        f.write(f"- scored: {len(rows)} · criteria met: {total_met}/{total_sig}\n")
        if ungraded:
            f.write(f"- **UNGRADED (no human criteria):** {', '.join(c['id'] for c in ungraded)}\n")
        if errors:
            f.write("- **NOT RUN — infrastructure failure, excluded from the denominator:**\n")
            for cid, kind, msg in errors:
                f.write(f"  - `{cid}` ({kind}): {msg}\n")
        f.write("\n| case | met | of | notes |\n|---|---:|---:|---|\n")
        for cid, met, tot, note in rows:
            f.write(f"| {cid} | {met} | {tot} | {str(note)[:80]} |\n")
        f.write("\n## Per-case detail\n")
        for c, answer, res in graded:
            f.write(f"\n### {c['id']}\n\n**Q:** {c['question'][:400]}\n\n")
            for s in res.get("signals", []):
                f.write(f"- [{'x' if s.get('met') else ' '}] {s.get('signal','')} "
                        f"— {s.get('why','')}\n")
            f.write(f"\n<details><summary>answer</summary>\n\n```\n{answer[:2500]}\n```\n</details>\n")
    print(f"  written: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
