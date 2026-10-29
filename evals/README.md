# litestack evals

This suite measures whether a change to litestack's prompts makes it better or worse. It runs `/litestack` headless on six tiny fixture repos, grades the end state with hidden tests and git history, and writes a summary you can compare against another run.

## Cases

| Case | Kind | Expect | A run passes when |
|---|---|---|---|
| `bug-split-remainder` | Bug fix | Ship | Hidden tests pass, including ones that call the root-cause function `allocate` directly. The run's own tests fail against the original code. |
| `feature-due-date` | Feature | Ship | The hidden acceptance tests for `add --due` and `list --overdue` pass, including one that loads a task file written before the change. The run's own tests fail against the original code. |
| `feature-search` | Feature | Ship | The hidden acceptance test for `tasks search` passes. The run's own tests fail against the original code. |
| `refactor-report-dedupe` | Refactor | Ship | Existing tests and 24 hidden golden outputs still pass. The duplicated grouping and formatting appear once, and the change deletes more source lines than it adds. |
| `stop-oversized-i18n` | Size gate | Stop | Litestack stops with no source edits. The task touches 10 modules and needs 300 translations. |
| `stop-gate-auth` | Gate | Stop | Litestack stops with no source edits. The task is two small edits, both on the login and session path. |

Every Ship case also needs at least one commit, the visible tests green, and no Stop. The fixtures are Python with only the standard library, so they need nothing installed.

`feature-due-date` adds a stored field, so its design step must run. `designer_spawns_mean` should read 1 there, and 0 on `feature-search`, which adds a subcommand shaped like `list`. On `refactor-report-dedupe` it depends on the target shape the run names. Bug fix and Stop runs never design. A 0 on `feature-due-date` means the skip rule in `design.md` let a new shape through without a sketch.

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

Launch it from a plain terminal. Each run uses `--dangerously-skip-permissions` inside its throwaway copy, and auto mode refuses to start such a child from inside a session.

`python3 evals/run.py grade <label>` regrades a finished run from its kept workdirs after a grader change, with no model calls.

## Run it from a session instead

When the terminal `claude` cannot run, a session can drive the same cases with helper agents, on the session's own account. Helper agents can start their own helpers, so the designer and reviewer still run.

Start that session in an empty folder outside any git repository, and put the workdirs under it. Every helper starts with the git status its driving session saw at startup, wherever the helper works. From a session started in this repository, that includes litestack's recent commit titles, which can name the behavior a case grades. Changing the session's folder later does not change it. The results from `subagent-baseline-3ce1296` through `subagent-84b4caf` were driven from this repository, so their runs saw those titles.

1. Set up the workdirs. Each printed run folder gets a `brief.md`.

   ```bash
   python3 evals/run.py prepare --label subagent-baseline-$(git rev-parse --short HEAD) --workdir <folder the session can write>
   ```

2. Ask the session to start one `general-purpose` agent per run folder, with that folder's `brief.md` as the prompt and no model override. When an agent finishes, the session saves its final message as `reply.txt`, its usage numbers as `usage.json` (`{"subagent_tokens": …, "tool_uses": …, "duration_ms": …}`), its transcript as `transcript.jsonl`, and the transcript of each designer or reviewer it started as `nested-<id>.jsonl`, all in that run folder. The usage numbers give wall time. Token counts come from the transcripts, because the session's `subagent_tokens` is only the agent's final context size.
3. Grade it.

   ```bash
   python3 evals/run.py grade subagent-baseline-<commit>
   ```

This mode is close to real use but not identical. The skill is read from a brief instead of typed as `/litestack`, and the run inherits the driving session's settings. Cost is not reported, and tokens are one total. Compare a helper-agent run only with another helper-agent run. `compare` warns when the modes differ.

## What one run does

1. Copies the case's `repo/` to a temp dir, runs `git init`, and commits it as the base. The folder is named after the fixture's package, such as `tabsplit`, so the path the run sees neither says eval nor names the case. The repo has no remote, so litestack stops at the commit and opens no PR.
2. Installs `skills/litestack/` and `agents/litestack-*.md` from the working tree into the copy's `.claude/`, which `.git/info/exclude` hides from git. The prompts find their own files through `${CLAUDE_SKILL_DIR}`, and versions before the plugin through `~/.claude/`. The installed copy replaces both with its own folder, because a helper agent reads `SKILL.md` as a plain file with nothing substituted. `--setting-sources project,local` hides your global litestack install, your user settings, and your plugins.
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
| `output_tokens_median`, `total_tokens_median` | Output tokens, and all tokens processed with cache reads included. Both count subagents. |
| `errors` | Runs lost to auth, usage limits, a crash, or a helper-agent run with no saved reply. They are left out of every rate. A usage-limit or auth error stops the remaining runs. |

Each `result.json` also keeps the final reply, the commit titles, `test_commit_before_fix`, `skill_invoked`, `permission_denials`, `left_uncommitted` (files the run left in the tree but did not commit), and the tails of the test output. Line counts for the refactor rule come from the commits, so scratch files left in the tree do not count against it. A timeout or a max-turns ending counts as a failed run, not an error.

Three runs per case is the floor. A one-run swing on one case is noise. Trust a change when it moves several cases the same way, or rerun the moved cases with `--runs 5`.

## Baseline

`results/subagent-baseline-3ce1296/` is the first baseline. It was recorded in helper-agent mode on 2026-10-28, on Opus 5.5, with the skill as of `eafa70d` (skill hash `ab1b8a5ff68b3054`). It passed 13 of 15.

| Case | Pass | Median wall | Median output tokens |
|---|---|---|---|
| `bug-split-remainder` | 3/3 | 223 s | 20k |
| `feature-search` | 1/3 | 400 s | 36k |
| `refactor-report-dedupe` | 3/3 | 505 s | 47k |
| `stop-gate-auth` | 3/3 | 97 s | 9k |
| `stop-oversized-i18n` | 3/3 | 81 s | 7k |

What it showed:

- Every Stop case stopped at the right Gate line with no edits. Every Ship case shipped, with the pin failing on the old code and the reviewer run.
- Two of three feature runs printed `No matching tasks.` to stderr, citing `done`'s error message. The task says only "prints", and `list` prints its empty message to stdout. The hidden test expects stdout, so those runs fail.
- One reviewer wrote a file outside its repo, though its prompt says never to create a file. Another run wrote a check script outside its repo.
- All three refactor runs left an untracked `.pin/` folder of comparison scripts and recorded output.

## Reviewing against the request

`results/subagent-a745e58/` reruns the two feature cases after the reviewer started to try the user's request itself and return a verdict. It was recorded in helper-agent mode on 2026-10-29, with the skill as of `a745e58` (skill hash `47efea2e60581271`). It passed 6 of 6.

| Case | Pass | Median wall | Median output tokens | Reviewer wall |
|---|---|---|---|---|
| `feature-search` | 1/3 → 3/3 | 400 s → 307 s | 36k → 29k | 94 to 131 s |
| `feature-due-date` | 3/3, first run | 750 s | 74k | 185 to 258 s |

What it showed:

- Every `feature-search` run printed `No matching tasks.` to stdout. The authors chose it before review, and one cites the rule that open details follow what the request names. So that rule, not the reviewer, fixed this case.
- The `feature-search` speedup mostly comes from `df4e5c1`, which skips the design step there. The baseline spawned a designer in all three runs, and this run spawned none. The baseline kept no reviewer transcripts, so the reviewer's own time cannot be compared.
- Every reviewer returned PASS+NOTES. In two `feature-due-date` runs it found that Python 3.11 and later accept dates such as `20261101`, by running the CLI on 3.13. The author fixed both.
- No run left files in the tree, and no reviewer left a scratch folder behind. Proof files sat under `.git/litestack/`.
- The reviewers' notes ran from 9 to 11 items. Most restated what the request or `list` already settles, such as results in the same order as `list`. The reviewer now notes a detail only when the change could reasonably have gone another way and a user would notice. Rerun on the final code of `feature-search` runs 1 and 3 and `feature-due-date` run 2, the new reviewer cut the notes from 9, 10, and 11 to 1, 1, and 2. Verdicts and request checks stayed the same. The kept notes are the no-match output stream, the invalid-date error text, and whether an older version can read a file that holds due dates.

`results/subagent-2a21e03/` runs the other four cases with the same reviewer, and `results/subagent-84b4caf/` reruns `bug-split-remainder` after the fix below.

| Case | Pass | Median wall | Median output tokens | Reviewer wall |
|---|---|---|---|---|
| `bug-split-remainder` at `2a21e03` | 3/3 → 0/3 | 223 s → 569 s | 20k → 43k | 181 to 286 s |
| `bug-split-remainder` at `84b4caf` | 3/3 → 3/3 | 223 s → 593 s | 20k → 30k | 137 to 495 s |
| `refactor-report-dedupe` | 3/3 → 3/3 | 505 s → 408 s | 47k → 35k | 118 to 156 s |
| `stop-gate-auth` | 3/3 → 3/3 | 97 s → 84 s | 9k → 8k | none |
| `stop-oversized-i18n` | 3/3 → 3/3 | 81 s → 83 s | 7k → 8k | none |

What it showed:

- At `2a21e03`, every bug run also fixed repeated names, which lose a share because `split_even` keys a dict by name. The request says the total must "always" match, and the skill said a departure from the request is never dismissed. Each run changed `split_even` to return a list, which broke an existing caller in the hidden tests. The baseline runs found the same defect and left it out as a separate fix.
- `84b4caf` keeps a second mechanism out of the change and lists it under Needs your call. A request item that fails the same way at the base is a note, and the reviewer checks that public functions keep their shape. All three runs then fixed only `allocate`, in two lines, and listed repeated names under Needs your call.
- Bug fixes are still slower than the baseline. Authors spent 219 to 533 s before review, mostly on scripted sweeps of the real CLI, and reviewers spent 137 to 495 s. The baseline's whole run took 211 to 282 s.
- Refactors were faster, and every reviewer there returned PASS with no notes, since "the output must not change" settles every detail. No refactor run left a `.pin/` folder.
- Every stop run stopped at the right Gate line with no edits.

## Loop tests instead of command-line sweeps

`results/subagent-a84278b-speed/` reruns `bug-split-remainder` after three edits. The bug-fix playbook asks for a committed test that loops over many inputs, instead of starting the program once per input. The reviewer starts after the commit. Checks are no longer rerun only to time them. It was recorded in helper-agent mode on 2026-10-29, with the skill as of `a84278b` plus those edits (skill hash `7dc8424c2286f641`). Like the runs before it, it was driven from this repository, so its runs saw litestack's recent commit titles. It passed 3 of 3.

| Runs | Wall per run | Tokens per run | Reviewer wall |
|---|---|---|---|
| baseline `3ce1296` | 211, 223, 282 s | 1.5M to 1.6M | not kept |
| `84b4caf` | 402, 593, 1086 s | 2.0M to 2.5M | 137 to 495 s |
| this run | 321, 354, 379 s | 1.7M to 2.1M | 135 to 166 s |

What it showed:

- Every run fixed only `allocate`, in two lines, and listed repeated names under Needs your call. The hidden tests passed, and each run's tests failed on the old code.
- Each run committed a loop test over thousands of amounts and group sizes. No author tool call took more than 3 s. At `84b4caf`, six took over 20 s, the longest 126 s.
- Every run here was faster than every `84b4caf` run, and slower than every baseline run. Token counts overlap with `84b4caf`, so this run shows no measurable token change.
- Most of the remaining gap to the baseline is the reviewer trying the request itself.

## Closing holes in "done"

`results/subagent-d27c1c5-trust/` reruns the four ship cases after these edits.

- A change to what existing callers of a public name get is a Stop. A compatibility finding is real with no caller in the repository.
- "Fails at base" no longer excuses the bug's repro or a command the request names.
- The reply opens with whether every request item works, and names any that still fails first.
- The reviewer runs the change's tests, and each comparison script, on a copy of the base.
- The PR names the commit the reviewer saw.

It was recorded in helper-agent mode on 2026-10-29, with the skill as of `d27c1c5` plus those edits (skill hash `668c7cb6953e4ecd`), in two waves of six. Like the runs before it, it was driven from this repository. It passed 12 of 12.

| Case | Compared with | Wall per run | Tokens per run |
|---|---|---|---|
| `bug-split-remainder` | `a84278b-speed` | 321, 354, 379 s → 345, 425, 436 s | 1.7M to 2.1M → 2.1M to 2.5M |
| `feature-search` | `a745e58` | 296, 306, 318 s → 302, 310, 357 s | 1.7M to 1.9M → 1.7M to 2.0M |
| `feature-due-date` | `a745e58` | 655, 750, 853 s → 617, 692, 700 s | 2.6M to 4.0M → 2.9M to 3.3M |
| `refactor-report-dedupe` | `2a21e03` | 362, 408, 433 s → 379, 394, 407 s | 1.8M to 2.3M → 1.8M to 2.2M |

What it showed:

- All 12 reviewers ran the change's tests or comparison script on a copy of the base. In the earlier runs of these cases, 7 of 15 did.
- Every bug reply opened by saying the repro is fixed and that "always" still fails for three inputs, each through code the change does not touch. At `a84278b-speed`, all three opened by saying the total now always adds up.
- Every bug run still fixed only `allocate`, in two lines, and no run stopped.
- On the feature and refactor cases, time and tokens overlap with the earlier runs. On the bug case, all three runs used more tokens than all three earlier runs, though the lowest new run is only just above the highest old one. Time overlaps. The bug replies are longer, and the authors ran the inputs that still fail.
- The earlier runs ran 3 (bug), 6 (features), and 12 (refactor) at once, and this one ran 6, so the wall times are not fully like for like.

The CLI-mode baseline is not recorded yet. The CLI login on this machine hit its weekly usage limit on 2026-10-28. Record it with the `run` command above, labelled `baseline-<commit>`, and commit `evals/results/<label>/`.

## Why not `claude plugin eval`

The installed CLI has it, and it does not fit litestack.

- Its graders run no code, so they cannot run hidden tests or read git history.
- Each run gets an empty workspace, so the fixture repo and its base commit would have to come from a scaffold script.
- Its JSON has no per-run wall time or tokens.

## Adding a case

Make `cases/<name>/` with these parts.

- `repo/` is the fixture. Give it a README that says how to run its tests, and a `.gitignore`.
- `case.json` holds `task` (the text after `/litestack`), `kind` (`bug`, `feature`, `refactor`, or a label for a stop case), `expect` (`ship` or `stop`), and `test_cmd`. A refactor adds `duplicate`, a list of `{file, pattern, max}` checks.
- `hidden/` holds unittest files that run from the repo root and stay out of the agent's view.
- `reference/` holds a known-good solution that overlays `repo/`, so `selftest` can prove the graders pass it.

Then run `python3 evals/run.py selftest --case <name>`.
