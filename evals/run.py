#!/usr/bin/env python3
"""Run the litestack eval cases headless, grade them, and compare runs. See evals/README.md."""

import argparse
import datetime
import fnmatch
import hashlib
import io
import json
import os
import re
import shutil
import signal
import statistics
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EVALS = Path(__file__).resolve().parent
ROOT = EVALS.parent
CASES = EVALS / "cases"
RESULTS = EVALS / "results"

# The child gets only these from the caller's environment, so a run launched from inside
# another Claude Code session behaves like one launched from a plain terminal.
ENV_KEEP = {"PATH", "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "LANG", "TERM",
            "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN"}
STOP_WORD = re.compile(r"\bstop(?:ped|ping|s)?\b", re.I)
FATAL = ("usage_limit_reached", "Not logged in", "authentication_failed", "Invalid API key")


def child_env(**extra):
    env = {k: v for k, v in os.environ.items() if k in ENV_KEEP or k.startswith("LC_")}
    return {**env, **extra}


def git(cwd, *args):
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(f"git {' '.join(args)} in {cwd}: {out.stderr.strip()}")
    return out.stdout


def shell(cmd, cwd):
    env = child_env(PYTHONDONTWRITEBYTECODE="1")
    try:
        out = subprocess.run(cmd, cwd=cwd, env=env, shell=True, capture_output=True, text=True, timeout=300)
        return out.returncode, (out.stdout + out.stderr)[-2000:]
    except subprocess.TimeoutExpired:
        return 124, "timed out after 300s"


def load_cases(pattern="*"):
    cases = []
    for d in sorted(CASES.iterdir()):
        if d.is_dir() and fnmatch.fnmatch(d.name, pattern):
            cases.append({"name": d.name, "dir": d, **json.loads((d / "case.json").read_text())})
    if not cases:
        sys.exit(f"no case matches {pattern!r}")
    return cases


def skill_files():
    return sorted((ROOT / "skills" / "litestack").rglob("*.md")) + sorted((ROOT / "agents").glob("litestack-*.md"))


def skill_version():
    digest = hashlib.sha256()
    for f in skill_files():
        digest.update(str(f.relative_to(ROOT)).encode() + b"\0" + f.read_bytes())
    dirty = git(ROOT, "status", "--porcelain", "--", "skills", "agents").strip()
    return {"skill_sha256": digest.hexdigest()[:16], "commit": git(ROOT, "rev-parse", "--short", "HEAD").strip(),
            "skill_dirty": bool(dirty)}


def setup(case, repo):
    shutil.copytree(case["dir"] / "repo", repo, ignore=shutil.ignore_patterns("__pycache__"))
    git(repo, "init", "-q", "-b", "main")
    for key, value in [("user.name", "Eval Fixture"), ("user.email", "fixture@example.com"),
                       ("commit.gpgsign", "false"), ("core.hooksPath", "/dev/null")]:
        git(repo, "config", key, value)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: initial import")
    install(repo)
    return git(repo, "rev-parse", "HEAD").strip()


def install(repo):
    # A project-level copy plus --setting-sources project,local hides any global install.
    # The prompts find their files through ${CLAUDE_SKILL_DIR}, and older ones through ~/.claude/.
    # A helper agent reads SKILL.md raw with nothing substituted, so the copy names its own folder.
    dot = repo / ".claude"
    shutil.copytree(ROOT / "skills" / "litestack", dot / "skills" / "litestack")
    (dot / "agents").mkdir()
    for f in (ROOT / "agents").glob("litestack-*.md"):
        shutil.copy(f, dot / "agents" / f.name)
    for f in dot.rglob("*.md"):
        text = f.read_text().replace("${CLAUDE_SKILL_DIR}", str(dot / "skills" / "litestack"))
        f.write_text(text.replace("~/.claude/", f"{dot}/"))
    with open(repo / ".git" / "info" / "exclude", "a") as fh:
        fh.write(".claude/\n")


def run_claude(case, repo, out, opts):
    cmd = ["claude", "-p", f"/litestack {case['task']}", "--output-format", "stream-json", "--verbose",
           "--dangerously-skip-permissions", "--setting-sources", "project,local", "--no-session-persistence"]
    if opts.model:
        cmd += ["--model", opts.model]
    if opts.effort:
        cmd += ["--effort", opts.effort]
    if opts.max_budget_usd:
        cmd += ["--max-budget-usd", str(opts.max_budget_usd)]
    start = time.monotonic()
    timed_out = False
    with open(out / "transcript.jsonl", "w") as stdout, open(out / "stderr.log", "w") as stderr:
        proc = subprocess.Popen(cmd, cwd=repo, env=child_env(), stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            proc.wait(timeout=opts.timeout_min * 60)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
    return {"wall_seconds": round(time.monotonic() - start, 1), "timed_out": timed_out, "exit_code": proc.returncode}


def agent_name(call):
    """The skill's fallback spawns general-purpose with a brief that names the agent file."""
    name = call.get("subagent_type") or "general-purpose"
    for kind in ("litestack-designer", "litestack-reviewer"):
        if name == "general-purpose" and f"agents/{kind}.md" in str(call.get("prompt", "")):
            return kind
    return name


def parse_transcript(path, skill_marker):
    init, result, agents = {}, {}, []
    raw = path.read_text() if path.exists() else ""
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            init = event
        elif event.get("type") == "result":
            result = event
        elif event.get("type") == "assistant":
            for block in event.get("message", {}).get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") in ("Agent", "Task"):
                    agents.append(agent_name(block.get("input") or {}))
    tokens = {}
    for usage in (result.get("modelUsage") or {}).values():
        for key, value in usage.items():
            if isinstance(value, (int, float)) and key != "contextWindow":
                tokens[key] = round(tokens.get(key, 0) + value, 6)
    error = run_error = None
    if not result:
        error = "no result event"
    elif result.get("api_error") or any(f in str(result.get("result")) for f in FATAL):
        error = result.get("api_error") or result.get("result")
    elif result.get("is_error") or result.get("subtype") != "success":
        run_error = result.get("subtype") or result.get("result")
    return {
        "model": init.get("model"),
        "claude_version": init.get("claude_code_version"),
        "skill_invoked": skill_marker in raw or "/.claude/skills/litestack/" in raw,
        "reply": result.get("result") or "",
        "error": error,
        "run_error": run_error,
        "cost_usd": result.get("total_cost_usd"),
        "num_turns": result.get("num_turns"),
        "permission_denials": len(result.get("permission_denials") or []),
        "tokens": tokens,
        "models": sorted((result.get("modelUsage") or {}).keys()),
        "subagents": {name: agents.count(name) for name in sorted(set(agents))},
    }


def transcript_tokens(paths):
    """Token usage summed over every API call in agent transcripts, counting each message once."""
    calls = {}
    for path in paths:
        for line in path.read_text(errors="replace").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            message = event.get("message") or {}
            if event.get("type") == "assistant" and message.get("usage"):
                calls[(path.name, message.get("id"))] = message["usage"]
    keys = {"inputTokens": "input_tokens", "cacheCreationInputTokens": "cache_creation_input_tokens",
            "cacheReadInputTokens": "cache_read_input_tokens", "outputTokens": "output_tokens"}
    return {mine: sum(u.get(theirs) or 0 for u in calls.values()) for mine, theirs in keys.items()}


def is_test(path):
    name = os.path.basename(path)
    return path.startswith("tests/") or "/tests/" in path or name.startswith("test_") or name.endswith("_test.py")


def pick_tree(repo, base):
    """The worktree holding the change: the one furthest ahead of base, else the run's own checkout."""
    best, best_key = repo, (-1, False)
    for line in git(repo, "worktree", "list", "--porcelain").splitlines():
        if not line.startswith("worktree "):
            continue
        tree = Path(line.split(" ", 1)[1])
        try:
            ahead = int(git(tree, "rev-list", "--count", f"{base}..HEAD"))
        except RuntimeError:
            continue
        key = (ahead, bool(git(tree, "status", "--porcelain").strip()))
        if key > best_key:
            best, best_key = tree, key
    return best


def changed_lines(tree, base):
    changed = {}
    for line in git(tree, "diff", "--numstat", "--no-renames", base).splitlines():
        added, deleted, path = line.split("\t", 2)
        changed[path] = (int(added) if added != "-" else 0, int(deleted) if deleted != "-" else 0)
    for path in git(tree, "ls-files", "--others", "--exclude-standard").splitlines():
        try:
            changed[path] = (len((tree / path).read_text().splitlines()), 0)
        except (UnicodeDecodeError, IsADirectoryError):
            changed[path] = (0, 0)
    return changed


def test_commit_before_fix(tree, base):
    for sha in git(tree, "rev-list", "--reverse", f"{base}..HEAD").split():
        files = git(tree, "diff-tree", "--no-commit-id", "--name-only", "-r", sha).split()
        if any(not is_test(f) for f in files):
            return False
        if files:
            return True
    return False


def tests_on_base(case, tree, base, test_paths):
    """Run the final test files against the untouched base code."""
    archive = subprocess.run(["git", "archive", base], cwd=tree, capture_output=True, check=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        tarfile.open(fileobj=io.BytesIO(archive)).extractall(tmp)
        for path in test_paths:
            src, dst = tree / path, Path(tmp) / path
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dst)
            elif dst.exists():
                dst.unlink()
        return shell(case["test_cmd"], tmp)[0]


def grade(case, repo, base, reply):
    tree = pick_tree(repo, base)
    changed = changed_lines(tree, base)
    source = {p: v for p, v in changed.items() if not is_test(p)}
    # Line counts judge what shipped. Scratch files left in the tree still count against a Stop.
    committed_all = {}
    for line in git(tree, "diff", "--numstat", "--no-renames", base, "HEAD").splitlines():
        added, deleted, path = line.split("\t", 2)
        committed_all[path] = (int(added) if added != "-" else 0, int(deleted) if deleted != "-" else 0)
    committed = {p: v for p, v in committed_all.items() if not is_test(p)}
    tests = sorted(p for p in changed if is_test(p))
    commits = git(tree, "log", "--reverse", "--format=%s", f"{base}..HEAD").splitlines()
    g = {
        "tree": str(tree),
        "commits": len(commits),
        "commit_titles": commits,
        "source_files_changed": sorted(source),
        "source_lines_added": sum(a for a, _ in committed.values()),
        "source_lines_deleted": sum(d for _, d in committed.values()),
        "left_uncommitted": sorted(set(changed) - set(committed_all)),
        "test_files_changed": tests,
        "said_stop": bool(STOP_WORD.search(reply)),
    }
    g["stopped"] = g["said_stop"] and not source
    g["stop_correct"] = g["stopped"] == (case["expect"] == "stop")
    g["visible_exit"], g["visible_tail"] = shell(case["test_cmd"], tree)
    hidden = case["dir"] / "hidden"
    if hidden.is_dir():
        g["hidden_exit"], g["hidden_tail"] = shell(f"python3 -m unittest discover -s '{hidden}'", tree)
    if tests:
        code = tests_on_base(case, tree, base, tests)
        g["pin_fails_on_base"] = code != 0
    else:
        g["pin_fails_on_base"] = None
    g["test_commit_before_fix"] = test_commit_before_fix(tree, base)
    g["duplicate_counts"] = [len(re.findall(d["pattern"], (tree / d["file"]).read_text()))
                             if (tree / d["file"]).exists() else 0 for d in case.get("duplicate", [])]

    shipped_ok = not g["stopped"] and g["commits"] > 0 and g["visible_exit"] == 0 and g.get("hidden_exit", 0) == 0
    if case["expect"] == "stop":
        g["pass"] = g["stopped"]
    elif case["kind"] in ("bug", "feature"):
        g["pass"] = shipped_ok and g["pin_fails_on_base"] is True
    elif case["kind"] == "refactor":
        g["pass"] = (shipped_ok and g["source_lines_added"] < g["source_lines_deleted"]
                     and all(n <= d["max"] for n, d in zip(g["duplicate_counts"], case["duplicate"])))
    else:
        g["pass"] = shipped_ok
    (Path(repo).parent / "diff.patch").write_text(git(tree, "diff", base))
    return g


def skill_marker():
    body = (ROOT / "skills" / "litestack" / "SKILL.md").read_text().split("---", 2)[-1]
    return next(line for line in body.splitlines() if line.strip() and not line.startswith("#"))[:60]


def one_run(case, index, out_root, work_root, opts, abort):
    out = out_root / "runs" / case["name"] / str(index)
    out.mkdir(parents=True, exist_ok=True)
    record = {"case": case["name"], "run": index, "kind": case["kind"], "expect": case["expect"]}
    if abort.is_set():
        record["error"] = "skipped after a fatal error in an earlier run"
        (out / "result.json").write_text(json.dumps(record, indent=2))
        return record
    repo = work_root / f"{case['name']}-{index}" / "repo"
    base = setup(case, repo)
    print(f"start {case['name']}#{index} in {repo}", flush=True)
    record.update(run_claude(case, repo, out, opts))
    record.update(parse_transcript(out / "transcript.jsonl", skill_marker()))
    if record["timed_out"]:
        record["error"], record["run_error"] = None, "timeout"
    if record["error"] and any(f in str(record["error"]) for f in FATAL):
        abort.set()
    record["grade"] = grade(case, repo, base, record["reply"])
    if record["run_error"]:
        record["grade"]["pass"] = False
    shutil.copy(repo.parent / "diff.patch", out / "diff.patch")
    record["workdir"] = str(repo)
    (out / "result.json").write_text(json.dumps(record, indent=2))
    g = record["grade"]
    print(f"done  {case['name']}#{index} pass={g['pass']} stopped={g['stopped']} commits={g['commits']} "
          f"wall={record['wall_seconds']}s cost={record['cost_usd']} error={record['error'] or record['run_error']}", flush=True)
    return record


def safe_run(case, index, out_root, work_root, opts, abort):
    try:
        return one_run(case, index, out_root, work_root, opts, abort)
    except Exception as exc:
        print(f"error {case['name']}#{index}: {exc!r}", flush=True)
        return {"case": case["name"], "run": index, "kind": case["kind"], "expect": case["expect"],
                "error": f"runner: {exc!r}"}


def start_results(opts, mode):
    label = opts.label or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_root = RESULTS / label
    if out_root.exists():
        sys.exit(f"{out_root} exists; pick another --label")
    parent = Path(opts.workdir) if getattr(opts, "workdir", None) else None
    if parent:
        parent.mkdir(parents=True, exist_ok=True)
    work_root = Path(tempfile.mkdtemp(prefix=f"litestack-eval-{label}-", dir=parent))
    meta = {"label": label, "mode": mode, "started": datetime.datetime.now().isoformat(timespec="seconds"),
            "runs_per_case": opts.runs, "model": opts.model, "effort": getattr(opts, "effort", None),
            "claude_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
            **skill_version()}
    out_root.mkdir(parents=True)
    (out_root / "meta.json").write_text(json.dumps(meta, indent=2))
    return out_root, work_root, meta


BRIEF = """You are a fresh Claude Code session. The user typed this command in the repository at {repo}:

/litestack {task}

Run it. Read `{repo}/.claude/skills/litestack/SKILL.md` in full and follow it exactly, as if the user had invoked the skill. Its other files are next to it in `{repo}/.claude/skills/litestack/`.

Rules for this environment:
- Work only inside {repo}. Run every command from there. Never read or search outside it.
- The litestack-designer and litestack-reviewer agent types in this session may be an older install. For each, use `subagent_type: "general-purpose"` and open its brief with "Read `{repo}/.claude/agents/<type>.md` in full and follow it. Edit nothing." Keep the skill's other subagent rules.
- Nobody will answer questions. Decide as the skill says, and Stop where it says to Stop.
- Your final message is the skill's reply to the user.
"""


def cmd_prepare(opts):
    """Set up workdirs for runs that a Claude Code session drives with helper agents."""
    cases = load_cases(opts.case)
    out_root, work_root, _ = start_results(opts, "subagent")
    for i in range(1, opts.runs + 1):
        for case in cases:
            out = out_root / "runs" / case["name"] / str(i)
            out.mkdir(parents=True)
            repo = work_root / f"{case['name']}-{i}" / "repo"
            base = setup(case, repo)
            record = {"case": case["name"], "run": i, "kind": case["kind"], "expect": case["expect"],
                      "mode": "subagent", "workdir": str(repo), "base": base, "error": None, "run_error": None}
            (out / "result.json").write_text(json.dumps(record, indent=2))
            (out / "brief.md").write_text(BRIEF.format(repo=repo, task=case["task"]))
            print(out)


def cmd_run(opts):
    cases = load_cases(opts.case)
    out_root, work_root, meta = start_results(opts, "cli")
    label = meta["label"]
    abort = threading.Event()
    jobs = [(case, i) for i in range(1, opts.runs + 1) for case in cases]
    with ThreadPoolExecutor(max_workers=opts.jobs) as pool:
        records = list(pool.map(lambda job: safe_run(*job, out_root, work_root, opts, abort), jobs))
    if abort.is_set() and not any("grade" in r and not r.get("error") for r in records):
        blocked = next(r for r in records if r.get("error") and not r["error"].startswith("skipped"))
        shutil.rmtree(out_root)
        shutil.rmtree(work_root, ignore_errors=True)
        sys.exit(f"Nothing was graded. Claude refused every run: {blocked.get('reply') or blocked['error']}\n"
                 f"Removed {out_root}. Rerun the same command once that is fixed.")
    meta["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    (out_root / "meta.json").write_text(json.dumps(meta, indent=2))
    write_summary(out_root, records)
    print(f"\nworkdirs kept in {work_root}")


def median(values):
    values = [v for v in values if v is not None]
    return round(statistics.median(values), 1) if values else None


def mean(values):
    values = [v for v in values if v is not None]
    return round(statistics.mean(values), 3) if values else None


def rate(records, test):
    hits = [test(r) for r in records]
    hits = [h for h in hits if h is not None]
    return f"{sum(hits)}/{len(hits)}" if hits else "-"


def summarize_case(name, records):
    graded = [r for r in records if "grade" in r and not r.get("error")]
    ship = graded and graded[0]["expect"] == "ship"
    designer = [r.get("subagents", {}).get("litestack-designer", 0) for r in graded]
    reviewer = [r.get("subagents", {}).get("litestack-reviewer", 0) for r in graded]
    return {
        "case": name,
        "runs": len(graded),
        "errors": len(records) - len(graded),
        "pass": rate(graded, lambda r: r["grade"]["pass"]),
        "stop_correct": rate(graded, lambda r: r["grade"]["stop_correct"]),
        "hidden_pass": rate(graded, lambda r: r["grade"]["hidden_exit"] == 0 if ship and "hidden_exit" in r["grade"] else None),
        "pin_fails_on_base": rate(graded, lambda r: bool(r["grade"]["pin_fails_on_base"]) if ship and r["kind"] in ("bug", "feature") else None),
        "skill_invoked": rate(graded, lambda r: r["skill_invoked"]),
        "commits_median": median([r["grade"]["commits"] for r in graded]),
        "wall_median_s": median([r["wall_seconds"] for r in graded]),
        "cost_mean_usd": mean([r.get("cost_usd") for r in graded]),
        "output_tokens_median": median([r["tokens"].get("outputTokens") for r in graded]),
        "total_tokens_median": median([sum(r["tokens"].get(k, 0) for k in (
            "inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens")) or None for r in graded]),
        "designer_spawns_mean": mean(designer),
        "reviewer_spawns_mean": mean(reviewer),
    }


def write_summary(out_root, records=None):
    if records is None:
        records = [json.loads(p.read_text()) for p in sorted((out_root / "runs").glob("*/*/result.json"))]
    by_case = {}
    for r in records:
        by_case.setdefault(r["case"], []).append(r)
    rows = [summarize_case(name, rs) for name, rs in sorted(by_case.items())]
    graded = [r for r in records if "grade" in r and not r.get("error")]
    total = {
        "pass": rate(graded, lambda r: r["grade"]["pass"]),
        "errors": len(records) - len(graded),
        "cost_total_usd": round(sum(r.get("cost_usd") or 0 for r in records), 2),
        "wall_median_s": median([r["wall_seconds"] for r in graded]),
    }
    meta = json.loads((out_root / "meta.json").read_text())
    summary = {"meta": meta, "total": total, "cases": rows}
    (out_root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    cols = ["case", "pass", "stop_correct", "hidden_pass", "pin_fails_on_base", "commits_median",
            "wall_median_s", "cost_mean_usd", "output_tokens_median", "total_tokens_median", "designer_spawns_mean", "reviewer_spawns_mean", "errors"]
    lines = [f"# {meta['label']}", "",
             f"Mode {meta.get('mode', 'cli')}. Skill {meta['skill_sha256']} at {meta['commit']}{' (dirty)' if meta['skill_dirty'] else ''}, "
             f"{meta['claude_version']}, model {meta.get('model') or 'default'}, {meta['runs_per_case']} runs per case.", "",
             f"Total pass {total['pass']}, errors {total['errors']}, cost ${total['cost_total_usd']}, "
             f"median wall {total['wall_median_s'] if total['wall_median_s'] is not None else '-'}s.", "",
             "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(row[c]) if row[c] is not None else "-" for c in cols) + " |" for row in rows]
    (out_root / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def cmd_grade(opts):
    out_root = RESULTS / opts.label
    cases = {c["name"]: c for c in load_cases()}
    records = []
    for path in sorted((out_root / "runs").glob("*/*/result.json")):
        record = json.loads(path.read_text())
        reply, usage = path.parent / "reply.txt", path.parent / "usage.json"
        if reply.exists():
            record["reply"] = reply.read_text()
            record["skill_invoked"] = True
        if usage.exists():
            u = json.loads(usage.read_text())
            record["wall_seconds"] = round(u["duration_ms"] / 1000, 1)
            record["final_context_tokens"] = u["subagent_tokens"]
            record["tool_uses"] = u.get("tool_uses")
        if (path.parent / "transcript.jsonl").exists() and record.get("mode") == "subagent":
            record["subagents"] = parse_transcript(path.parent / "transcript.jsonl", "")["subagents"]
            record["tokens"] = transcript_tokens([path.parent / "transcript.jsonl", *sorted(path.parent.glob("nested-*.jsonl"))])
        if record.get("mode") == "subagent" and not reply.exists():
            record["error"] = "no reply recorded"
        if record.get("workdir") and Path(record["workdir"]).exists():
            repo = Path(record["workdir"])
            base = record.get("base") or git(repo, "rev-list", "--max-parents=0", "HEAD").split()[0]
            record["grade"] = grade(cases[record["case"]], repo, base, record.get("reply", ""))
            shutil.copy(repo.parent / "diff.patch", path.parent / "diff.patch")
            path.write_text(json.dumps(record, indent=2))
        records.append(record)
    write_summary(out_root, records)


def cmd_compare(opts):
    a, b = (json.loads((RESULTS / label / "summary.json").read_text()) for label in (opts.a, opts.b))
    print(f"A = {opts.a} (skill {a['meta']['skill_sha256']}), B = {opts.b} (skill {b['meta']['skill_sha256']})\n")
    if a["meta"].get("mode", "cli") != b["meta"].get("mode", "cli"):
        print("Warning: A and B ran in different modes, so their numbers are not comparable.\n")
    cols = ["pass", "stop_correct", "hidden_pass", "pin_fails_on_base", "wall_median_s", "cost_mean_usd",
            "output_tokens_median", "total_tokens_median"]
    print("| case | " + " | ".join(f"{c} A → B" for c in cols) + " |")
    print("|---|" + "---|" * len(cols))
    rows_b = {row["case"]: row for row in b["cases"]}
    for row in a["cases"]:
        other = rows_b.get(row["case"], {})
        print(f"| {row['case']} | " + " | ".join(f"{row.get(c)} → {other.get(c)}" for c in cols) + " |")
    print(f"\nTotal pass {a['total']['pass']} → {b['total']['pass']}. Median wall {a['total']['wall_median_s']}s → "
          f"{b['total']['wall_median_s']}s. Total cost ${a['total']['cost_total_usd']} → ${b['total']['cost_total_usd']}.")


def cmd_selftest(opts):
    """Check the graders offline: untouched fixtures, reference solutions, and stop replies."""
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for case in load_cases(opts.case):
            scenarios = [("untouched, says done", None, "Done.", False),
                         ("untouched, says stop", None, "Stop. The Gate failed.", case["expect"] == "stop")]
            if (case["dir"] / "reference").is_dir():
                scenarios.append(("reference solution", "reference", "Shipped.", True))
            else:
                scenarios.append(("edits source, says stop", "touch", "Stop. The Gate failed.", False))
            for i, (label, change, reply, expected) in enumerate(scenarios):
                repo = Path(tmp) / f"{case['name']}-{i}" / "repo"
                base = setup(case, repo)
                installed = (repo / ".claude" / "skills" / "litestack" / "SKILL.md").read_text()
                assert ("~/.claude/" not in installed and "${CLAUDE_SKILL_DIR}" not in installed
                        and str(repo / ".claude" / "skills" / "litestack") in installed), "install rewrite failed"
                if change == "reference":
                    ref = case["dir"] / "reference"
                    for wanted in (True, False):
                        for f in ref.rglob("*"):
                            rel = f.relative_to(ref).as_posix()
                            if f.is_file() and is_test(rel) == wanted:
                                (repo / rel).parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy(f, repo / rel)
                        git(repo, "add", "-A")
                        if git(repo, "status", "--porcelain").strip():
                            git(repo, "commit", "-q", "-m", "test: pin" if wanted else "fix: change")
                elif change == "touch":
                    target = next(p for p in sorted(repo.rglob("*.py")) if ".claude" not in p.parts and not is_test(p.relative_to(repo).as_posix()))
                    target.write_text(target.read_text() + "\n# edited\n")
                g = grade(case, repo, base, reply)
                ok = g["pass"] == expected
                if case.get("kind") in ("bug", "feature") and change == "reference":
                    ok = ok and g["pin_fails_on_base"] is True and g["test_commit_before_fix"]
                failures += not ok
                print(f"{'ok  ' if ok else 'FAIL'} {case['name']}: {label} -> pass={g['pass']} (want {expected})"
                      + ("" if ok else f" {json.dumps({k: g[k] for k in g if k not in ('visible_tail', 'hidden_tail')})}"))
    sys.exit(1 if failures else 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run every case headless and grade it")
    run.add_argument("--runs", type=int, default=3, help="runs per case (default 3)")
    run.add_argument("--jobs", type=int, default=2, help="runs at once (default 2)")
    run.add_argument("--case", default="*", help="case name glob")
    run.add_argument("--label", help="results folder name (default: timestamp)")
    run.add_argument("--model", help="model for the session (default: the CLI default)")
    run.add_argument("--effort", help="effort for the session (default: the CLI default)")
    run.add_argument("--timeout-min", type=float, default=45, help="per-run timeout in minutes (default 45)")
    run.add_argument("--max-budget-usd", type=float, help="per-run spend cap passed to claude")
    run.set_defaults(func=cmd_run)
    prepare = sub.add_parser("prepare", help="set up workdirs and briefs for helper-agent runs")
    prepare.add_argument("--runs", type=int, default=3)
    prepare.add_argument("--case", default="*")
    prepare.add_argument("--label")
    prepare.add_argument("--model", help="model the driving session uses, recorded only")
    prepare.add_argument("--workdir", help="parent folder for the workdirs (default: system temp)")
    prepare.set_defaults(func=cmd_prepare)
    grade_cmd = sub.add_parser("grade", help="grade or regrade a run from its kept workdirs")
    grade_cmd.add_argument("label")
    grade_cmd.set_defaults(func=cmd_grade)
    compare = sub.add_parser("compare", help="compare two results folders")
    compare.add_argument("a")
    compare.add_argument("b")
    compare.set_defaults(func=cmd_compare)
    selftest = sub.add_parser("selftest", help="check the graders offline, with no model calls")
    selftest.add_argument("--case", default="*")
    selftest.set_defaults(func=cmd_selftest)
    opts = parser.parse_args()
    opts.func(opts)


if __name__ == "__main__":
    main()
