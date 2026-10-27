---
name: litestack
description: A fast, verified workflow for small features, bug fixes, refactors, and chores. Routes the task to a playbook, applies a fixed set of engineering principles, pins behavior before any edit, makes the change in the main session, verifies on the real surface, gets one independent review, and ships a clean commit and PR. Stops and reports when the task is too big for it. Use for /litestack.
disable-model-invocation: true
---

# Litestack

Small changes, full rigor. You run the whole task in this session, with no code-writing delegates, swarms, or review panels. The only helpers are one read-only reviewer and, when search stalls, one read-only search. A playbook gives the task its steps. The principles shape every decision. One fresh reviewer checks the result. Nothing ships without a pin that held and pasted output that shows it.

The files named here live next to this one, in `~/.claude/skills/litestack/`. Read them by path.

## Start

1. In one batch of parallel tool calls, read `principles.md`, the playbook that matches the task, and `playbooks/ship.md` in full, plus `design.md` for Feature or Refactor, and run `git status` and the first searches for the code the task touches. Commits happen as you go, so Ship is needed from the start.
2. If the code shows the task belongs to another playbook, read that one and switch.
3. Open a task list whose first items are that playbook's steps, copied verbatim. A step you skip stays in the list with `skip: <reason>`.
4. Before the first edit, start a fresh branch off the base branch, named `<type>/<short-topic>`. If the tree has unrelated changes, use a new worktree.

## Playbooks

- **Feature** (`playbooks/feature.md`). New or changed behavior a user can see, such as a new option, field, command, endpoint, screen element, or validation rule.
- **Bug fix** (`playbooks/bug-fix.md`). A defect to reproduce, root-cause, and fix.
- **Refactor** (`playbooks/refactor.md`). A behavior-preserving change of structure, such as a rename, extract, inline, dedupe, or move.
- **Chore** (`playbooks/chore.md`). Docs, config, copy, dependency bumps, build or CI fixes, and test-only changes.

Split a mixed task into parts, each with its own playbook and commit. A refactor that reveals a bug ships the refactor first, then the fix. A feature that needs a reshape first runs Refactor for the reshape, then Feature.

Every playbook ends with **Review** below, then Ship (`playbooks/ship.md`).

## Gate

Litestack fits only when every line holds. Judge it against the code you read in the playbook's first step, not the wording of the request.

- The change stays in one feature area, at most about 6 non-test files and 300 changed non-test lines. A vertical slice through one area's layers, such as its UI, handler, and store, counts as one area.
- A change to a public API, schema, persisted format, or wire protocol is additive and backward compatible. Nothing needs a data migration or a version bump, or changes what existing callers get.
- No concurrency, auth, permissions, security, payments, or data deletion on the changed path.
- For a bug, the code and the repro point at a mechanism you can confirm. The hunt gets about three passes, then you Stop.
- For a change that needs the design step, one shape already looks clearly better from reading the code, or a quick probe can settle the fork.

## Rules

- Any code. Name the data shape first, and pick its structure per Model the domain.
- A "which approach" question. If running something can answer it (behavior, output, layout, timing), write a quick probe and let the result decide. For a product or preference call, take the option closest to existing behavior, act on it, and report it as an open decision. Ask first only when nothing existing suggests a default and a wrong guess would be costly to undo.
- A UI, CLI, or TUI change. Drive the real surface. If the project has a verification skill at `.claude/skills/verify-*/SKILL.md`, read it and the file in its `features/` folder for the touched feature. Follow its launch, drive, evidence, and cleanup steps, and cover every entry point the feature file lists. If one of its steps breaks for a reason unrelated to the change, drive the surface directly and report the broken step. Without one, use a browser tool for web and Electron, Bash for a CLI, and `expect` or `script` for a TUI.
- Every check. Keep its output verbatim. An inconclusive or wrong-surface result is a fail. Fix it or Stop.
- A tool or skill that breaks mid-task. Say so. Never work around it silently.
- Reversible work proceeds without asking. Always pause before an irreversible action: a force-push to a shared branch, a deploy, data deletion, or a message to another person.
- No is an acceptable answer. When the user proposes an approach or scope, give your real judgment, and push back when it does not earn its place.

## Speed

Speed comes from never waiting and never doing work twice, not from skipping proof.

- Batch. Send independent tool calls in one message. That covers the Start reads, every file a step needs, and the verify step's type check, lint, and tests. Never run one at a time what could run together.
- Locate, then read. Find code with Grep and Glob before you open files. Read the matching ranges of a long file, not all of it. If two rounds of search have not found the code, spawn one `Explore` subagent with the question.
- Start slow things early. Launch a dev server, a build, or a long test suite in the background as soon as you know you need it, and keep working. You are notified when a build or test run ends, so never sleep to wait for one. A server never ends. Wait for it through the verification skill's launch step, or with one readiness check that has a timeout, such as a `curl` retry loop.
- Keep the inner loop tight. While you edit, run only the pin and the touched test file, using the runner's file or name filter. Save the area's full tests and lint for verify.
- Build the lever. A repeated edit is one scripted pass, per the principle of that name, not a run of hand edits.
- No double work. Do not re-read a file you just edited. Do not rerun a check whose inputs have not changed. Trim long output with `tail`, `head`, or `grep`.
- Overlap the review. Start the reviewer the moment verify passes. While it runs, draft the commit message, the PR body, and the reply.
- Do not wait on people or bots. Decide reversible calls and report them. After the PR opens, post the URL and stop.

## Stop

Stop when the Gate fails, or when one of these fires.

- The diff outgrows the Gate's size.
- A fix attempt fails, and the next one would rest on the same premise.
- A design fork that neither the red-flag screen nor a probe settles.
- The build fights the sketch for a second round.
- The review raises a design-level finding.
- Verification cannot reach the real surface.

To stop, name the Gate line or tripwire that fired, and what the task needs that litestack does not do, such as a longer root-cause hunt, a design tradeoff no probe settles, or a migration plan. Hand over the pin, the repro output, and what you learned. Leave the branch as it is, and list its commits and any uncommitted edits.

## Review

Make one Agent call with `subagent_type: "litestack-reviewer"`, `effort: "xhigh"`, and `run_in_background: true`. Overlap it per Speed.

Use a different model from this session's, so the review is a second voice. Pass `model: "opus"` when this session runs on Fable, and `model: "fable"` otherwise. If that model is unavailable or rate limited, retry once on the other one and say so in the reply.

If the `litestack-reviewer` agent type does not exist, the session started before the install. Use `subagent_type: "general-purpose"`, and open the brief with "Read `~/.claude/agents/litestack-reviewer.md` in full and follow it. Edit nothing."

The brief holds four parts. Give pointers, not conclusions.

- Kind. The playbook you ran.
- Intent. One paragraph on what the change must do and what it must leave unchanged, from the user's request. For a bug, the symptom and the repro.
- Base. The base ref to diff against, and the untracked files that belong to the change.
- Checks. The exact pin and verify commands, with roughly how long each took, the path of each piece of evidence the verification skill saved, each comparison script and the path of its kept output, and any script that made a repeated edit.

Leave out your diagnosis, your design rationale, and what you already checked. They anchor the reviewer.

Triage each finding as Act on or Dismissed, with a one-line reason. Judge it against the code, not the reviewer's word.

- A hypothetical bug is real only when a caller can reach it. Trace the call path before you decide.
- "I would do it differently" without a concrete defect is Dismissed.
- A new abstraction for one call site is Dismissed.
- A finding about code the change did not touch is Dismissed, unless the change makes it worse.
- Dismiss a correctness or security finding only with the code path that refutes it.
- A review of only nits means the change is sound. Fix the cheap ones and dismiss the rest.

Fix every Act on, then rerun the playbook's verify step. If the fixes changed logic beyond the lines the findings named, run one more review with a new reviewer. Stop on any design-level finding, or on an Act on that survives the second round.

## Writing

This covers the reply, code comments, commit messages, and the PR. Write it clean as you draft. A cleanup pass afterward does not fix these.

- Short declarative sentences, one thought each.
- No long-dash character. No colon as a mid-sentence connector, though a colon before a list is fine.
- No filler, hedging, or praise.
- Terse never drops content. Every part the playbook's reply names stays.
- Lead with impact. Say who notices the change and what changes for them before any implementation detail. Then say what the next maintainer inherits.
- Every claim carries its evidence or its label (measured, inferred, or guess) in the same sentence. Never hand the user a check you could run.
- Never fabricate a link, citation, or output. Link only what you produced or read this session.
- A comment states a non-obvious why that the code cannot show, and nothing else. No narration, no commented-out code, and no step comments in tests or scripts, where the assertion message documents the step.

## Reply

Give the playbook's reply parts in order, written per Writing. Then the review, with the reviewer's model, the findings you fixed, and each dismissed finding with its reason. Then name each principle that changed a decision and the choice it changed. Name anything you could not verify, and why. End with the PR link, or the branch and commit when there is no PR, and any stop or open item.
