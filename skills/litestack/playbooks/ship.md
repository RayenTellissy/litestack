# Ship

**Commits.** Commit each verified unit as you go, so the history tells the story in order: the subtraction, then the reshape, then the behavior, or the failing test, then the fix. Commit a failing test marked as an expected failure, such as `test.fails` in Vitest, `test.failing` in Jest, or `pytest.mark.xfail(strict=True)`, and remove the mark in the fix commit. Keep its failing output from a run without the mark. When the runner has no such mark, commit the test with the fix. Every commit passes the pin, the touched test file, and the type check, so `git bisect` and per-commit CI stay usable. Fold a review fix into the commit it belongs to. Amend when that is the last commit. Otherwise run `git commit --fixup <sha>`, then `git rebase --autosquash <base>`. Git before 2.44 applies `--autosquash` only with `-i`, so there run `GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>`. A commit body says why, never what the diff already shows. Skip the body when the title says it all.

**Titles.** Use Conventional Commits, `type(scope): subject`. The type is `feat`, `fix`, `refactor`, `test`, `docs`, `perf`, or `chore`. The scope is the area. The subject is short and imperative, has no trailing period, and names the real symbol when one carries the change, as in `fix(slug): collapse separator runs in slugify`.

**PR.** Open one when the repository has a remote and the user did not ask to keep the work local. Otherwise stop at the commit and say so. Use the session's built-in PR tool when it has one, else `gh pr create`. Open it ready, never as a draft. Reuse the commit title for a one-commit PR. Run `gh pr view` before you report its state.

**Description.** Write a one-minute briefing for a reviewer who has the diff, in short sentences with few identifiers. Use these `##` headings in this order, and drop any with nothing to say.

- `## Needs your call`. Each open decision from the reply and each note from the reviewer's verdict, one line each, with what the change does now. A request item that still fails goes first, with its input and what it prints. List one only when the change could reasonably have gone another way and a user would notice. Leave out what the request, or what it names to match, already settles. A departure from the request you kept goes here too, with its reason.
- `## Why`. The problem and the approach, in one to three sentences.
- `## What changed`. One to three bullets. Name both sides of a rename.
- `## Scope`. What it covers and what it leaves out on purpose.
- `## Risk`. Who or what it touches, and why that is safe.
- `## Verification`. The reviewer's verdict and the commit it reviewed, with any commits made after it. Then each check you ran and its result. Attach a screenshot or recording when it proves a UI claim.

Keep the body under about 30 lines.

**After.** Post the PR URL and stop. Do not wait on CI or review bots unless the user asks.
