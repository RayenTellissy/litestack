# litestack evals

This suite measures whether a change to litestack's prompts makes it better or worse. It runs `/litestack` headless on five tiny fixture repos, grades the end state with hidden tests and git history, and writes a summary you can compare against another run.

## Cases

| Case | Kind | Expect | A run passes when |
|---|---|---|---|
| `bug-split-remainder` | Bug fix | Ship | Hidden tests pass, including ones that call the root-cause function `allocate` directly. The run's own tests fail against the original code. |
| `feature-search` | Feature | Ship | The hidden acceptance test for `tasks search` passes. The run's own tests fail against the original code. |
| `refactor-report-dedupe` | Refactor | Ship | Existing tests and 24 hidden golden outputs still pass. The duplicated grouping and formatting appear once, and the change deletes more source lines than it adds. |
| `stop-oversized-i18n` | Size gate | Stop | Litestack stops with no source edits. The task touches 10 modules and needs 300 translations. |
| `stop-gate-auth` | Gate | Stop | Litestack stops with no source edits. The task is two small edits, both on the login and session path. |

Every Ship case also needs at least one commit, the visible tests green, and no Stop. The fixtures are Python with only the standard library, so they need nothing installed.

## Run it

You need `claude` logged in, `python3` 3.9 or later, and `git`.

Runs use the account the terminal `claude` is logged into, which can differ from the desktop app's. `claude auth status` shows it. To use another account for the eval only, run `claude setup-token` and pass the token as `CLAUDE_CODE_OAUTH_TOKEN`.

Check the graders first. This makes no model calls and takes a few seconds.

```bash
python3 evals/run.py selftest
```

Record a run of the skill as it is in the working tree. The default is 3 runs per case and 2 at once.

```bash
python3 evals/run.py run --label baseline-$(git rev-parse --short HEAD)
```

Change the prompts, run again under a new label, and compare.

```bash
python3 evals/run.py compare baseline-eafa70d my-change
```

Useful `run` options are `--case 'stop-*'` to run a subset, `--runs 5` for more samples, `--jobs 3` for more parallel runs, `--model`, `--effort`, `--timeout-min` (default 45), and `--max-budget-usd` as a per-run cap.

Launch it from a plain terminal. Each run uses `--dangerously-skip-permissions` inside its throwaway copy, and Claude Code's auto mode refuses to start such a child from inside a session.

`python3 evals/run.py grade <label>` regrades a finished run from its kept workdirs after a grader change, with no model calls.

## Run it from a Claude Code session instead

When the terminal `claude` cannot run, a Claude Code session can drive the same cases with helper agents, on the session's own account. Helper agents can start their own helpers, so the designer and reviewer still run.

1. Set up the workdirs. Each printed run folder gets a `brief.md`.

   ```bash
   python3 evals/run.py prepare --label subagent-baseline-$(git rev-parse --short HEAD) --workdir <folder the session can write>
   ```

2. Ask the session to start one `general-purpose` agent per run folder, with that folder's `brief.md` as the prompt and no model override. When an agent finishes, the session saves its final message as `reply.txt`, its usage numbers as `usage.json` (`{"subagent_tokens": …, "tool_uses": …, "duration_ms": …}`), and its transcript as `transcript.jsonl`, all in that run folder.
3. Grade it.

   ```bash
   python3 evals/run.py grade subagent-baseline-<commit>
   ```

This mode is close to real use but not identical. The skill is read from a brief instead of typed as `/litestack`, and the run inherits the driving session's settings. Cost is not reported, and tokens are one total. Compare a helper-agent run only with another helper-agent run. `compare` warns when the modes differ.

## What one run does

1. Copies the case's `repo/` to a temp dir, runs `git init`, and commits it as the base. The repo has no remote, so litestack stops at the commit and opens no PR.
2. Installs `skills/litestack/` and `agents/litestack-*.md` from the working tree into the copy's `.claude/`, which `.git/info/exclude` hides from git. The prompts name `~/.claude/` paths, so the installed copy points those at itself. `--setting-sources project,local` hides your global litestack install, your user settings, and your plugins.
3. Runs `claude -p "/litestack <task>"` with `--output-format stream-json`, `--no-session-persistence`, and an environment stripped to PATH, HOME, locale, and auth variables. The transcript is saved next to the result.
4. Grades the worktree that is furthest ahead of the base, so a run that branches or adds a worktree is still found.

## Results

Each run writes `evals/results/<label>/runs/<case>/<n>/result.json` and `diff.patch`. Transcripts and stderr sit beside them and are gitignored. `summary.json` and `summary.md` hold one row per case.

| Field | Meaning |
|---|---|
| `pass` | Runs that met the case's pass rule above. |
| `stop_correct` | Runs that stopped when they should and shipped when they should. A run counts as stopped when its reply says stop and it left no source edits. |
| `hidden_pass` | Ship runs whose hidden tests passed. |
| `pin_fails_on_base` | Bug and feature runs whose final test files fail against the original code, so the pin really catches the problem. |
| `commits_median` | Commits on top of the base. |
| `wall_median_s`, `cost_mean_usd` | Wall time from the runner, and cost from the CLI's final result event, subagents included. |
| `designer_spawns_mean`, `reviewer_spawns_mean` | How often the run spawned each litestack subagent. |
| `total_tokens_median` | All tokens, subagents included. |
| `errors` | Runs lost to auth, usage limits, a crash, or a helper-agent run with no saved reply. They are left out of every rate. A usage-limit or auth error stops the remaining runs. |

Each `result.json` also keeps the final reply, the commit titles, `test_commit_before_fix`, `skill_invoked`, `permission_denials`, and the tails of the test output. A timeout or a max-turns ending counts as a failed run, not an error.

Three runs per case is the floor. A one-run swing on one case is noise. Trust a change when it moves several cases the same way, or rerun the moved cases with `--runs 5`.

## Baseline

Not recorded yet. The CLI login on this machine hit its weekly usage limit on 2026-10-28, and the eval could not be launched from inside a Claude Code session. Record it with the `run` command above, labelled `baseline-<commit>`, and commit `evals/results/<label>/`.

## Why not `claude plugin eval`

The installed CLI has it, and it does not fit litestack.

- Its graders run no code, so they cannot run hidden tests or read git history.
- Each run gets a temp HOME and an empty workspace. Litestack's prompts read `~/.claude/skills/litestack/`, which would be empty there.
- It loads the repo as a plugin, which renames the agent types litestack spawns.
- Its JSON has no per-run wall time or tokens.

## Adding a case

Make `cases/<name>/` with these parts.

- `repo/` is the fixture. Give it a README that says how to run its tests, and a `.gitignore`.
- `case.json` holds `task` (the text after `/litestack`), `kind` (`bug`, `feature`, `refactor`, or a label for a stop case), `expect` (`ship` or `stop`), and `test_cmd`. A refactor adds `duplicate`, a list of `{file, pattern, max}` checks.
- `hidden/` holds unittest files that run from the repo root and stay out of the agent's view.
- `reference/` holds a known-good solution that overlays `repo/`, so `selftest` can prove the graders pass it.

Then run `python3 evals/run.py selftest --case <name>`.
