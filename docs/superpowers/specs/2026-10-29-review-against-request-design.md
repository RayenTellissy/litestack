# Review against the request

## Why

Litestack is the light tier next to pstack. Its value is a "done" a teammate can trust without redoing the checks.

The baseline eval shows where that breaks. Two of three `feature-search` runs shipped a guess. The request did not say which stream `No matching tasks.` goes to. The runs picked stderr, wrote tests that expect stderr, and passed them. The request said "in the same format as `list`", and `list` prints its empty message to stdout. The reviewer re-ran the author's tests, so it inherited the guess. In one run it flagged the mismatch, and the author dismissed it as a product call.

pstack's Shipping playbook names the cause. An author checks what it meant to build. Only a check by an agent that did not write the code, run the way a user would, counts.

## Goals

- The reviewer judges the change against the user's request as written. It tries each thing the request asks for on the real surface, instead of re-running most of the author's checks.
- The reviewer returns a verdict, as pstack's verifier does. PASS, PASS+NOTES, or FAIL.
- The author cannot dismiss a finding that the change departs from the request. It fixes it, or lists it under "Needs your call" in the PR.
- When the request says to match something ("same format as `list`"), every detail it leaves open follows that thing.
- Runs leave no stray files. Proof scripts and kept output live under the git directory, and the reviewer's scratch lives in a temp folder it removes.

## Non-goals

- No second agent. The one reviewer changes its job.
- No change to the Gate, the pin rules, the design step, or the playbooks' build steps.
- Litestack still never waits on a person. A guess ships, labeled.

## Anti-goals

- Median wall time or tokens on the feature eval cases rise above the baseline.
- The reviewer writes to the repository, or rebuilds the author's test suite.

## Approaches

1. **Change the existing reviewer.** Picked. Same single agent, same model and effort. It drives the request itself and drops most re-runs of the author's checks, so the work swaps instead of growing.
2. **Add a separate checker next to the reviewer,** like pstack's Shipping. The cleanest split, but a second agent on every run adds time and cost.
3. **Only pass the request word for word.** The cheapest. The reviewer still spends its time on the author's tests, so it is less likely to try the request itself.

## Decided

- **Review brief** (`SKILL.md`, Review). Intent becomes Request, the user's words verbatim, plus the repro for a bug. Checks shrinks to the pin, the touched test command, and the evidence paths. The brief also leaves out the calls the author made where the request was silent, so the reviewer finds them on its own.
- **Reviewer** (`agents/litestack-reviewer.md`). It lists each thing the request asks for that a user can observe. It tries each one at the branch tip, from a `mktemp -d` folder so the run writes nothing in the repo, and removes the folder before it returns. It notes each observable detail the request leaves open, such as an output stream, an exit code, an empty state, or error text, and checks it against anything the request says to match. It re-runs the pin and the touched tests once, under the existing tree fingerprint. It no longer re-runs lint or the type check, because the author's verify step pasted those. Its output gains a `## Verdict` line and a `## Request check` table.
- **Verdict meaning.** PASS means every request item behaves as asked, with no critical or warning findings. PASS+NOTES means it works, but the change settled details the request left open. Each one is a note. FAIL means a request item does not behave as asked, or a critical finding.
- **Triage** (`SKILL.md`, Review). A departure from the request, or from what the request says to match, is never Dismissed. A FAIL never ships.
- **Rules** (`SKILL.md`). The match-what-the-request-names rule joins the "which approach" rule, ahead of "closest to existing behavior". Proof scripts and kept output go under `$(git rev-parse --git-dir)/litestack/`.
- **PR** (`playbooks/ship.md`). A `## Needs your call` section comes first, dropped when empty. `## Verification` carries the verdict.
- **Reply** (`SKILL.md`). The review part gives the verdict and the Needs your call list.
- **README** describes the reviewer's new job and the verdict.

My calls, for you to check:

- Needs your call goes first in the PR, so a reader sees it before anything else.
- The reviewer drops lint and type-check re-runs to pay for driving the request.
- Proof goes under the git directory, not a gitignored folder, because that needs no `.gitignore` change in the user's project.

## Proof it works

Rerun `feature-search` and `feature-due-date`, 3 runs each, in helper-agent mode on this account. Compare against `subagent-baseline-3ce1296`. `feature-search` should pass more often. Median wall time and tokens should not rise. `feature-due-date` gets its first numbers. The baseline predates the design-step change in `df4e5c1`, so the comparison covers both changes together. That is the version that ships.

## Left to the builder

- The exact wording in each file, in the repo's writing style.
- The `## Request check` table's columns.
- Whether `scripts/check-principles.py` needs any change. It should not, since no principle is added.
