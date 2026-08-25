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

Every run also writes `latest.json` next to the markdown, and rolls the run before
it to `previous.json` so nothing is destroyed. That exists so a later run can be
compared against it — the baseline is read before anything is overwritten, so the
file you want is almost always `latest.json`:

    python3 run_cases.py improve/cases --baseline improve/results/latest.json

`--baseline` answers the only question a single score cannot: **did fixing this
break something that already worked?** A correct one-line change can break a line
a hundred lines above it, added by someone else, at another time — so the run
that matters is the one *before* you make a change permanent, not after.

It compares criterion by criterion, never totals, and it refuses to turn three
things into a score:

- **A different grader or a different agent.** Two graders disagree on the same
  answer often enough that a "regression" across them is usually just variance.
  Comparing those is manufacturing evidence, so the script says so, loudly.
- **Criteria that changed between runs.** Then the set was not frozen and the
  cases are not the same cases. Reported as NOT COMPARABLE, not as movement.
- **A case that changed status class** (graded / ungraded / not-run). An agent
  that could not be reached is not an agent that got it wrong.

With `--baseline` the exit code is the verdict, and there are three of them:

    0  compared, nothing regressed
    1  compared, something that used to pass now fails
    2  NO VERDICT — the runs were not comparable, or nothing was compared at all

Wire it in front of a merge and treat 2 the way you treat 1. A gate that exits 0
because every case was excluded looks exactly like a gate that exits 0 because
the change was safe, which is the failure this script exists to prevent.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import re
import shlex
import subprocess
import sys

FM = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$", re.S)

# ` # trailing comment`, but not a `#` inside a quoted value.
_COMMENT = re.compile(r"\s+#.*$")


def _scalar(v: str) -> str:
    """Strip a trailing YAML comment, then quotes.

    This exists because the case template in SKILL.md writes
    `expected_signals:      # <- THE HUMAN WRITES THESE`. Without this, the value
    parsed as the comment string, the `- ` items below it were never appended,
    and every case written from the documented template scored as UNGRADED —
    silently, and with no error anywhere. Verified against the real template.
    """
    v = v.strip()
    if v[:1] not in ("'", '"'):
        v = _COMMENT.sub("", v).strip()
    return v.strip("\"'")


def parse_case(path: str) -> dict | None:
    """Minimal YAML-subset parse: scalars and `- ` lists. No dependency."""
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"  !! {os.path.basename(path)}: unreadable ({e}), skipped")
        return None
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
            if not isinstance(case.get(key), list):
                # The key line carried a comment or stray text; the list under it
                # is what was meant. Do not let that silently discard the items.
                case[key] = []
            case[key].append(_scalar(line.lstrip()[2:]))
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            key = k.strip()
            v = _scalar(v)
            case[key] = [] if v == "" else v
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


def align_signals(case: dict, res: dict) -> list[dict]:
    """Key the stored verdicts on the CASE's criteria, not the grader's echo.

    The frozen thing is the case file. Graders paraphrase; if the record kept the
    grader's wording, the next comparison would see the criteria change and call
    every case NOT COMPARABLE, which is a silent way to never detect a regression.
    A criterion the grader returned no verdict for is stored as `met: null` — an
    absent verdict is not a failure.
    """
    want = case["expected_signals"]
    got = [s for s in (res.get("signals") or []) if isinstance(s, dict)]
    by_text: dict[str, dict] = {}
    for s in got:
        by_text.setdefault(str(s.get("signal", "")), s)
    exact = [by_text.get(sig) for sig in want]

    # Positional fallback is only safe when the grader paraphrased EVERY criterion
    # and returned exactly as many verdicts as we asked for. If some matched by
    # text and some did not, order cannot be trusted: a grader that reorders while
    # paraphrasing part of the list would assign a verdict to the wrong criterion,
    # which can both hide a regression and invent one.
    use_positional = want and not any(exact) and len(got) == len(want)

    out = []
    for i, sig in enumerate(want):
        s = exact[i] or (got[i] if use_positional else None)
        out.append({
            "signal": sig,
            "met": bool(s.get("met")) if s is not None else None,
            "why": (str(s.get("why", ""))[:160] if s is not None
                    else "grader returned no verdict for this criterion"),
        })
    return out


def load_baseline(path: str) -> dict | None:
    """Read a prior run's JSON. Any failure is loud and returns None — a baseline
    that silently did not load would report every case as NEW and zero regressions,
    which looks exactly like a clean run."""
    try:
        with open(path, encoding="utf-8") as f:
            b = json.load(f)
    except FileNotFoundError:
        print(f"\n  !! baseline not found: {path}")
        print("     Run once without --baseline first — it writes results/latest.json,")
        print("     and rolls the run before it to results/previous.json.")
        return None
    except (json.JSONDecodeError, OSError) as e:
        print(f"\n  !! baseline unreadable ({e}): {path}")
        return None
    if not isinstance(b, dict) or not isinstance(b.get("cases"), dict):
        print(f"\n  !! not a run_cases result (no 'cases' object): {path}")
        return None
    return b


def compare(base: dict, now: dict, base_path: str) -> int:
    """Criterion-by-criterion diff against a prior run. Returns an EXIT CODE.

        0 — compared, nothing regressed
        1 — compared, at least one criterion that used to pass now fails
        2 — **no verdict**: the two runs are not comparable, or nothing was
            actually compared. Treat this as "not verified", never as a pass.

    Deliberately never subtracts one total from another. A moved total is the
    least informative thing here and the easiest to over-read; a named criterion
    that flipped from met to unmet is the finding.

    The 2 matters more than it looks. A gate that returns 0 because every case
    was excluded is indistinguishable from a gate that returned 0 because the
    change was safe, and that is the failure this whole script exists to avoid.
    """
    print("\n" + "=" * 58)
    print("  BASELINE COMPARISON")
    print(f"  base: {base_path}"
          + (f"  ({base['written']})" if base.get("written") else ""))

    # The guard that matters most. Graders disagree with each other on the same
    # answer often enough that a cross-grader "regression" is usually variance.
    # Normalise first: `claude -p` and `claude -p {q}` are the same command, since
    # run_cmd appends the placeholder when it is missing. Flagging that as drift
    # would refuse a verdict on two identical runs.
    def norm(c: str) -> str:
        c = (c or "").strip()
        return c if "{q}" in c else (c + " {q}").strip()

    drift = [(k, base.get(k), now.get(k)) for k in ("agent", "grader")
             if norm(base.get(k, "")) != norm(now.get(k, ""))]
    if drift:
        print("\n  ⚠  THIS COMPARISON IS NOT SOUND — the setup changed between runs:")
        for k, was, isnow in drift:
            print(f"       {k}: {was!r}  →  {isnow!r}")
        print("     A score only replicates if the model, the prompt and the case set are")
        print("     held fixed. Differences below are at least partly that change, and")
        print("     there is no way to tell how much. Re-run the baseline setup instead.")

    b_cases, n_cases = base["cases"], now["cases"]
    regressed, improved, incomparable, blocked = [], [], [], []
    unchanged = no_verdict = 0

    # A case that WAS scored in the baseline and cannot be scored-and-compared now
    # is a lost measurement, not a pass. Certifying a change while a
    # previously-passing case silently dropped out is the whole failure mode this
    # gate exists to prevent — and it is easy to cause by accident (the agent
    # crashed on that case) or on purpose (delete the case, edit its criteria).
    def drop(cid: str, why: str, was_graded: bool) -> None:
        (blocked if was_graded else incomparable).append((cid, why))

    for cid in sorted(set(b_cases) | set(n_cases)):
        b, n = b_cases.get(cid), n_cases.get(cid)
        if b is None:
            incomparable.append((cid, "new case — no baseline to compare against"))
            continue
        was_graded = b.get("status") == "graded"
        if n is None:
            drop(cid, "was in the baseline, absent from this run", was_graded)
            continue
        if b.get("status") != n.get("status"):
            drop(cid, f"status {b.get('status')} → {n.get('status')}"
                      " — not a score change, but also not a result", was_graded)
            continue
        if n.get("status") != "graded":
            incomparable.append((cid, f"{n.get('status')} in both runs — nothing scored"))
            continue
        b_sig = [s.get("signal", "") for s in b.get("signals", [])]
        n_sig = [s.get("signal", "") for s in n.get("signals", [])]
        if sorted(b_sig) != sorted(n_sig):     # order is not part of the identity
            drop(cid, "criteria changed between runs — the set was not frozen, so"
                      " these are not the same case", was_graded)
            continue
        b_met = {s.get("signal", ""): s.get("met") for s in b.get("signals", [])}
        for s in n.get("signals", []):
            sig, met = s.get("signal", ""), s.get("met")
            was = b_met.get(sig)
            if met is None:
                # No verdict now. If the baseline HAD one, a measurement was lost
                # and this run cannot certify the case.
                if was is None:
                    no_verdict += 1
                else:
                    blocked.append((cid, f"no verdict for “{sig[:48]}” this run,"
                                         " but the baseline had one"))
                continue
            if was is None:
                no_verdict += 1
                continue
            if was and not met:
                regressed.append((cid, sig, s.get("why", "")))
            elif met and not was:
                improved.append((cid, sig))
            else:
                unchanged += 1

    if regressed:
        print(f"\n  ✗ REGRESSED — {len(regressed)} criterion(s) that used to pass:")
        for cid, sig, why in regressed:
            print(f"      {cid} · {sig[:66]}")
            if why:
                print(f"        — {str(why)[:70]}")
    if improved:
        print(f"\n  ✓ IMPROVED — {len(improved)}:")
        for cid, sig in improved:
            print(f"      {cid} · {sig[:66]}")
    print(f"\n  = unchanged: {unchanged} criterion(s)")
    if no_verdict:
        print(f"  ? no verdict on either side: {no_verdict} criterion(s) — never scored")
    if blocked:
        print(f"\n  ⛔ LOST — {len(blocked)}: scored in the baseline, not scored now:")
        for cid, why in blocked:
            print(f"      {cid} — {why}")
    if incomparable:
        print(f"\n  ~ NOT COMPARABLE — {len(incomparable)} case(s), excluded from both counts:")
        for cid, why in incomparable:
            print(f"      {cid} — {why}")
    print("=" * 58)

    # Three ways there is no verdict. All must be louder than a pass, because all
    # of them LOOK like a pass to anything that reads an exit code.
    if drift:
        print("  NO VERDICT (exit 2). The differences above are informational only —")
        print("  the setup changed, so they cannot be attributed to your change. Re-run")
        print("  the baseline's agent and grader if you need this to gate anything.")
        return 2
    if blocked:
        print("  NO VERDICT (exit 2). Something the baseline measured was not measured")
        print("  this time. A case that used to pass and then vanished, crashed, lost")
        print("  its criteria or lost its verdict is not evidence that a change is safe.")
        print("  Fix those cases and re-run before treating this as a gate.")
        return 2
    if (len(regressed) + len(improved) + unchanged) == 0:
        print("  NO VERDICT (exit 2). Nothing was actually compared — every case was")
        print("  excluded above. This is not a clean run; check the baseline is the run")
        print("  you meant, and that the cases still parse.")
        return 2

    if regressed:
        print("  A criterion that used to pass and now fails is the finding. Read it")
        print("  before you read anything else, and do not promote over it.")
        return 1
    return 0


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
    ap.add_argument("--baseline", default=None,
                    help="a prior run's results JSON (usually <results>/latest.json, which "
                         "is read before it is overwritten). Compares criterion by criterion "
                         "and exits 1 on any regression")
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

    baseline = load_baseline(a.baseline) if a.baseline else None
    if a.baseline and baseline is None:
        # Fail before spending a run. A baseline that did not load would report
        # every case as new, zero regressions, and read as a clean gate.
        return 2

    cases = [c for c in (parse_case(p) for p in paths) if c]

    # Results are keyed by case id. Two cases sharing an id means one silently
    # overwrites the other in the record — and if the overwritten one was the
    # regression, it disappears from the comparison entirely.
    seen: dict[str, str] = {}
    for c in cases:
        if c["id"] in seen:
            print(f"\n  !! duplicate case id {c['id']!r}:")
            print(f"       {seen[c['id']]}\n       {c['path']}")
            print("     One would overwrite the other and a regression could vanish.")
            print("     Give them distinct ids and re-run.")
            return 2
        seen[c["id"]] = c["path"]

    graded, ungraded, rows, errors = [], [], [], []
    record: dict[str, dict] = {}

    for c in cases:
        print(f"\n── {c['id']}")
        if not c["expected_signals"]:
            print("   UNGRADED — expected_signals is empty. A human must write them.")
            ungraded.append(c)
            record[c["id"]] = {"status": "ungraded"}
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
                record[c["id"]] = {"status": "not_run", "error": "empty answer pasted"}
                continue
        else:
            ok, answer = run_cmd(a.agent, c["question"], a.timeout)
            if not ok:
                # An infrastructure failure is NOT a score of zero. Recording it as
                # 0/N invents a false low number — the exact failure mode this whole
                # skill exists to prevent. Excluded from the denominator instead.
                print(f"   AGENT FAILED: {answer[:160]}")
                errors.append((c["id"], "agent", answer[:200]))
                record[c["id"]] = {"status": "not_run", "error": answer[:200]}
                continue
        res = (grade_by_human(c, answer) if a.grader == "none"
               else grade(c, answer, a.grader, a.timeout))
        if "error" in res:
            print(f"   GRADER FAILED: {res['error'][:160]}")
            errors.append((c["id"], "grader", res["error"][:200]))
            record[c["id"]] = {"status": "not_run", "error": res["error"][:200]}
            continue
        sigs = res.get("signals", [])
        met = sum(1 for s in sigs if s.get("met"))
        for s in sigs:
            print(f"   [{'PASS' if s.get('met') else 'FAIL'}] {s.get('signal','')[:70]}"
                  f"{'' if s.get('met') else '  — ' + str(s.get('why',''))[:50]}")
        rows.append((c["id"], met, len(c["expected_signals"]), res.get("notes", "")))
        graded.append((c, answer, res))
        record[c["id"]] = {"status": "graded", "met": met,
                           "of": len(c["expected_signals"]),
                           "signals": align_signals(c, res)}

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

    # Anchor on the cases DIRECTORY even when a single case file was passed, or
    # the results land in `cases/results/` instead of the documented `../results/`.
    anchor = os.path.abspath(a.cases_dir)
    if os.path.isfile(a.cases_dir):
        anchor = os.path.dirname(anchor)
    outdir = a.out or os.path.join(os.path.dirname(anchor), "results")
    os.makedirs(outdir, exist_ok=True)
    gating = baseline is not None
    dest = os.path.join(outdir, "candidate.md" if gating else "latest.md")
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

    # Machine-readable twin, so a later run can be compared against this one.
    #
    # When gating (--baseline), write to candidate.json and leave latest.json
    # ALONE. Overwriting the baseline with the candidate's own result means that
    # simply re-running the identical command compares the candidate against
    # itself and exits 0 — a CI retry, or an impatient second run, silently
    # defeats the gate. Only a baseline run may move latest.json.
    jdest = os.path.join(outdir, "candidate.json" if gating else "latest.json")
    if not gating and os.path.exists(jdest):
        try:
            os.replace(jdest, os.path.join(outdir, "previous.json"))
        except OSError as e:
            print(f"  !! could not roll latest.json → previous.json ({e})")
    payload = {
        "schema": 1,
        "written": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "agent": a.agent,
        "grader": a.grader,
        "cases_dir": os.path.abspath(a.cases_dir),
        "cases": record,
    }
    # Write-then-rename. A SIGINT or a full disk midway through a direct write
    # would leave a truncated latest.json that still parses as "a baseline".
    tmp = jdest + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, jdest)
    # Verify the write by reading it back. A store that reports success and leaves
    # no file is the documented way this class of loop dies quietly.
    try:
        with open(jdest, encoding="utf-8") as f:
            n_back = len(json.load(f).get("cases", {}))
        print(f"  written: {jdest}  ({n_back} case(s), read back OK)")
    except (OSError, json.JSONDecodeError) as e:
        print(f"  !! {jdest} did NOT read back ({e}) — do not treat this run as recorded")
        return 2

    if baseline is not None:
        return compare(baseline, payload, a.baseline)
    else:
        print(f"\n  Next time, compare against this run with"
              f"\n       --baseline {jdest}"
              f"\n  (it is read before anything is overwritten; `previous.json` is one older)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
