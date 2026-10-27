# litestack

A fast, verified workflow for small changes: bug fixes, refactors, and tweaks. It skips the design fan-outs and multi-agent panels that a large change needs, and keeps the parts that catch mistakes. Every change gets a pin before the first edit, verification on the real surface, and one independent review before it ships.

## Install

From a clone:

```bash
./install.sh
```

From GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/RayenTellissy/litestack/main/install.sh | sh
```

The script copies the `litestack` skill into `~/.claude/skills/` and the `litestack-reviewer` agent into `~/.claude/agents/`. Run it again to update. Start a new session after you install so the agent loads.

## Use

```
/litestack <task>
```

The run has seven steps.

1. **Size it.** Read the code and check the gate. Litestack takes a change inside one module, at most about 5 files and 200 lines. It refuses public API, schema, and persisted-format changes, as well as concurrency, auth, security, payments, migrations, and data deletion. A bug qualifies only when its cause is clear once you reproduce it.
2. **Pin it.** Before any edit, write the check that proves the result. That is a failing repro for a bug, a green test for a refactor, and a failing test or exact observation for a tweak.
3. **Make the change.** On a fresh branch, in the main session, with no delegates. The smallest change that passes the pin.
4. **Verify.** Re-run the pin, the type check, lint, and the touched tests. Drive the real surface for UI and CLI changes, through the project's `verify-*` skill when it has one. Paste the output.
5. **Review.** One read-only `litestack-reviewer` on a different model from the session's. It re-runs the fast checks and reviews the diff for correctness, root cause, pin quality, missed call sites, scope, simplicity, comments, and security. The session triages each finding, fixes what is real, and verifies again.
6. **Ship.** A Conventional Commits commit and a ready PR with Why, What changed, and Verification sections.
7. **Reply.** What changed, the pasted proof, the review outcome, and the PR link.

Litestack stops and reports instead of pushing on when the task is too big. That happens when the gate fails, the diff outgrows it, a fix fails on a shaky premise, the review finds a design-level problem, or the real surface is out of reach. The report names the reason and hands over the pin and what it learned.

## Files

- `skills/litestack/SKILL.md` is the workflow.
- `agents/litestack-reviewer.md` is the read-only reviewer.
- `install.sh` installs both.

## License

[MIT](LICENSE)
