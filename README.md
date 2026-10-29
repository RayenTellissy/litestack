# litestack

A fast, verified workflow for small features, bug fixes, refactors, and chores. Each task runs through a playbook and a fixed set of engineering principles in one session. There are no code-writing delegates, swarms, second models, or review panels. What stays is the part that catches mistakes. Every change gets a pin before the first edit, verification on the real surface, and one independent review before it ships.

## Install

As a plugin, from inside a session:

```
/plugin install litestack --marketplace RayenTellissy/litestack
```

`/plugin` updates it from then on. A plugin's skill is named after the plugin, so the command is `/litestack:litestack`.

Or with the script, from a clone:

```bash
./install.sh
```

From GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/RayenTellissy/litestack/main/install.sh | sh
```

That installs `main`. To install a branch, tag, or commit instead, set `LITESTACK_REF`. To install from a fork, set `LITESTACK_REPO` to its `owner/name`.

```bash
curl -fsSL https://raw.githubusercontent.com/RayenTellissy/litestack/main/install.sh | LITESTACK_REF=<ref> sh
```

The script copies the `litestack` skill into `skills/` and the `litestack-designer` and `litestack-reviewer` agents into `agents/`, under `$CLAUDE_CONFIG_DIR` or `~/.claude` when that is unset. Run it again to update. Start a new session after you install so the agents load.

Use one method. With both, each agent and the skill load twice.

## Use

```
/litestack <task>
```

Litestack reads its principles, matches the task to a playbook, and copies the playbook's step labels into a task list.

| Playbook | For | The pin |
|----------|-----|---------|
| Feature | A new option, field, command, endpoint, screen element, or validation rule | An acceptance check that fails today, covering every entry point |
| Bug fix | A defect to reproduce and root-cause | The repro, failing, on the surface where the bug shows |
| Refactor | A rename, extract, inline, dedupe, or move | Tests or recorded outputs that capture today's behavior |
| Chore | Docs, config, copy, dependency bumps, build fixes, tests | The build, render, or load that consumes the change |

A mixed task splits into parts, each with its own playbook and commit.

Feature and Refactor design before they write logic when the change adds a shape the code does not have yet, such as a new type or stored field, a new module, a new signature another module calls, or state with a new owner. Otherwise a Feature builds to match the closest existing code that does the same kind of thing, a Refactor builds to the target shape it named, and a build that turns out to need a new shape stops to run the design step. A read-only `litestack-designer` in a fresh subagent, on the session's model at `xhigh` effort, sketches the types and signatures with stub bodies. It revises the sketch until it is free of red flags such as shallow modules, leaked decisions, pass-through layers, and split ownership. While it works, the session writes the acceptance check. The session then builds against the sketch, treats any surprise the sketch did not plan for as a sign the sketch may be wrong, and scraps the sketch if the build keeps fighting it.

Every playbook ends the same way.

1. **Verify.** Rerun the pin, the type check, lint, and the touched tests. UI and CLI changes are driven on the real surface, through the project's `verify-*` skill when it has one. Output is pasted verbatim.
2. **Review.** One read-only `litestack-reviewer` in a fresh subagent, on the session's model at `xhigh` effort. It sees only the code, the user's request word for word, and a short brief, never the session's reasoning or the calls it made where the request was silent. It tries each thing the request asks for the way a user would, compares each detail the request leaves open against anything the request names to match, reruns the pin, opens the evidence, and reviews the diff against the principles and the usual small-change traps. It returns PASS, PASS+NOTES, or FAIL. The session triages each finding, fixes what is real, and verifies again. A FAIL never ships. A departure from the request is never dismissed. The session fixes it on the path it built, or lists it under Needs your call when the fix would widen the change.
3. **Ship.** Small ordered commits in Conventional Commits form, and a ready PR with Needs your call, Why, What changed, Scope, Risk, and Verification sections. Needs your call comes first and lists every detail the request left open that the change decided, so a teammate knows what to check and can trust the rest.
4. **Reply.** What changed for the user, the pasted proof, the reviewer's verdict, the principles that shaped decisions, and the PR link.

## Speed

Litestack is fast because it never waits and never does work twice. It does not skip proof. It batches independent reads and commands into one message, starts dev servers and long suites in the background, and runs only the pin and the touched test file while editing. The full checks wait for verify. Repeated edits become one script. The review runs while the session drafts the commit, the PR, and the reply. Reversible calls get made, not asked about, and nothing waits on CI after the PR opens.

Two settings help on your side.

- Turn on fast mode (`/fast`) for the session.
- Allow your project's test, lint, and type-check commands in your permission settings, so prompts do not stall a run.

## Gate

Litestack takes a change in one feature area, at most about 6 non-test files and 300 changed non-test lines. Public API, schema, and format changes must be additive and backward compatible. It refuses concurrency, auth, permissions, security, payments, and data deletion. A bug qualifies when its mechanism turns up within about three passes. A design qualifies when one shape is clearly right from reading the code.

When the task fails the gate or outgrows it midway, litestack stops and reports instead of pushing on. The report names the reason and hands over the pin and what it learned.

## Files

- `skills/litestack/SKILL.md` holds the router, gate, rules, review, and writing standards.
- `skills/litestack/principles.md` holds the principles that the session, the designer, and the reviewer all apply.
- `skills/litestack/design.md` holds the design step and the red flags that the designer and the reviewer both screen for.
- `skills/litestack/playbooks/` holds the Feature, Bug fix, Refactor, Chore, and Ship playbooks.
- `agents/litestack-designer.md` is the read-only designer.
- `agents/litestack-reviewer.md` is the read-only reviewer.
- `.claude-plugin/` holds the plugin and marketplace manifests.
- `install.sh` installs the skill and both agents without the plugin system.
- `evals/` holds the eval suite that measures a prompt change. See `evals/README.md`.
- `scripts/check-principles.py` fails when a skill or agent file cites a principle that `principles.md` does not define. Cite one by its name in parentheses, as in "(Reader load)". CI runs it on every push and PR.

## License

[MIT](LICENSE)
