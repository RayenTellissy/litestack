---
name: litestack
description: A fast, verified workflow for small bug fixes, refactors, and tweaks. Sizes the task, pins behavior before any edit, makes the change in the main session, verifies on the real artifact, gets one independent review, and ships a clean commit and PR. Stops and reports when the task is too big for it. Use for /litestack.
disable-model-invocation: true
---

# Litestack

Small changes, full proof. You make the change in this session. One fresh reviewer checks it. Nothing ships without a pin that held and pasted output that shows it.

## Gate

Litestack fits only when every line holds. Judge it against the code you read in step 1, not the wording of the request.

- The change stays inside one module or feature area, at most about 5 non-test files and 200 changed non-test lines.
- No new or changed public API, schema, data model, persisted format, or wire protocol. Renaming an internal symbol is fine.
- No concurrency, auth, security, payments, migrations, or data deletion on the changed path.
- For a bug, you can name the mechanism after reading the code and reproducing it. A cause you must hunt for is too big.
- One shape is clearly right. Two valid designs with real tradeoffs are too big.

## Stop

Stop when the Gate fails in step 1, or when one of these fires later.

- The diff outgrows the Gate's size.
- A fix attempt fails, and the next one would rest on the same premise.
- The review raises a design-level finding.
- Verification cannot reach the real surface.

To stop, name the Gate line or tripwire that fired, and what the task needs that litestack does not do, such as a root-cause hunt, a design comparison, or a migration plan. Hand over the pin, the repro output, and what you learned. Leave any edits uncommitted on the branch and list them.

## Steps

Open a task list whose first items are these steps, copied verbatim. A step you skip stays in the list with `skip: <reason>`.

1. **Size it.** Read the code the task touches yourself. Name the files you expect to change and the data shape involved. Check the Gate. If it fails, Stop.
2. **Pin it.** Before any edit, write the check that proves the result. Run it and keep its output. If the project has a verification skill at `.claude/skills/verify-*/SKILL.md`, read it and the file in its `features/` folder that covers the touched feature. Drive every surface pin and check through it.
   - Bug fix. Reproduce on the surface where the bug shows, through the verification skill when there is one, or with a failing test that drives the same path. A test that passes before the fix does not pin the bug.
   - Refactor. Run the existing tests that cover the code you will move and confirm they pass. If none cover it, write a small characterization test first. Type check and lint are not a pin.
   - Feature or tweak. Write a test, or name the exact command or surface observation that fails now and must pass after.
   - Docs, config, or copy. The pin is the build, render, or load that consumes the file.
3. **Make the change.** Work on a fresh branch off the base branch. If the tree has unrelated changes, use a new worktree. Make the edits yourself in this session. Ship the smallest change that passes the pin, and delete before you add (dead code, one-caller wrappers, stale references). For a rename or API reshape inside the Gate, migrate every caller and delete the old name in the same change, then grep for the old name in strings, docs, and config. Add a comment only for a non-obvious why the code cannot show. Match the naming and idiom of the code around it.
4. **Verify.** Re-run the pin. A bug or feature pin now passes. A refactor pin stays green. Then run the project's type check, lint, and tests for the touched area. For a UI, CLI, or TUI change, drive the real surface. With a verification skill, follow its launch, drive, evidence, and cleanup steps, and cover every entry point its feature file lists for the changed behavior. If a step of that skill breaks for a reason unrelated to the change, drive the surface directly and report the broken step. Without one, use a browser tool for web and Electron, Bash for a CLI, and `expect` or `script` for a TUI. Keep the output verbatim. An inconclusive or wrong-surface result is a fail. Fix it or Stop.
5. **Review.** Spawn one fresh reviewer per **Review** below. Triage each finding as Act on or Dismissed, with a one-line reason. Fix every Act on, then re-run step 4. If the fixes changed logic beyond the lines the findings named, run one more review with a new reviewer. Stop on any design-level finding, or on an Act on that survives the second round.
6. **Ship.** Commit and open the PR per **Ship** below.
7. **Reply.** Per **Reply** below.

## Review

Make one Agent call with `subagent_type: "litestack-reviewer"`, `effort: "high"`, and `run_in_background: true`. Draft the commit message and PR body while it runs.

Use a different model from this session's, so the review is a second voice. Pass `model: "opus"` when this session runs on Fable, and `model: "fable"` otherwise. If that model is unavailable or rate limited, retry once on the other one and say so in the reply.

If the `litestack-reviewer` agent type does not exist, the session started before the install. Use `subagent_type: "general-purpose"`, and open the brief with "Read `~/.claude/agents/litestack-reviewer.md` in full and follow it. Edit nothing."

The brief holds three parts. Give pointers, not conclusions.

- Intent. One paragraph on what the change must do and what it must leave unchanged, from the user's request. For a bug, the symptom and the repro.
- Base. The base ref to diff against, and the untracked files that belong to the change.
- Checks. The exact pin and step 4 commands, with roughly how long each took, and the path of each piece of evidence the verification skill saved.

Leave out your diagnosis, your design rationale, and what you already checked. They anchor the reviewer.

Triage each finding against the code, not the reviewer's word.

- A hypothetical bug is real only when a caller can reach it. Trace the call path before you decide.
- "I would do it differently" without a concrete defect is Dismissed.
- A new abstraction for one call site is Dismissed.
- A finding about code the change did not touch is Dismissed, unless the change makes it worse.
- Dismiss a correctness or security finding only with the code path that refutes it.
- A review of only nits means the change is sound. Fix the cheap ones and dismiss the rest.

## Ship

- One commit is the norm. For a bug fix with a cheap test, commit the failing test first and the fix on top. For a refactor that deletes before it reshapes, commit the subtraction first.
- Title each commit `type(scope): subject` (Conventional Commits). The type is `fix`, `feat`, `refactor`, `test`, `docs`, `perf`, or `chore`. The subject is short and imperative, with no trailing period. A body says why, never what the diff already shows. Skip the body when the title says it all.
- Open the PR when the repository has a remote and the user did not ask to keep the work local. Otherwise stop at the commit and say so.
- Create the PR with the session's built-in PR tool when it has one, else `gh pr create`. Open it ready, never as a draft. Reuse the commit title. The body has `## Why` (one to three sentences), `## What changed` (one to three bullets), and `## Verification` (each check you ran and its result), in about 20 lines or fewer.
- Post the PR URL and stop. Do not wait on CI or review bots.

## Reply

Short declarative sentences. No long-dash character. Every claim carries its evidence or its label (measured, inferred, or guess). Give these parts in order, and drop a part with nothing to say.

- What changed and who notices, in one or two sentences.
- The pin and the verification, with the key output lines pasted verbatim. For a bug, the failing run and then the passing run.
- The review. The reviewer's model, the findings you fixed, and each dismissed finding with its reason.
- The PR link, or the branch and commit when there is no PR.
- Any stop or open item.
