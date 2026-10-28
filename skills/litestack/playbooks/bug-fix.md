# Bug fix

**Every shipped line traces to runtime evidence.** A change that "might help" is a hypothesis, not a fix, and it does not ship.

1. **Read the failing path**, its callers, and its tests. Check the Gate.
2. **Reproduce it** yourself on the surface where it shows, through the verification skill when there is one. Ask the user only when that surface is out of reach, with the specific reason, after you drive it as far as it goes. If it will not fire, tighten the conditions, synthesize the input, or add logging until it does. Keep the failing output.
3. **Find the mechanism.** List the candidate causes. Run the check that rules out the most of them, eliminate, and repeat. Read program state with logs, a debugger, or a probe script instead of guessing. When it may be a regression, read `git log -L` or `git blame` on the broken lines. If you cannot name the mechanism after about three passes, Stop. Remove the instrumentation once you have it.
4. **Pin it.** Turn the repro into a failing test on the same path when that is cheap, and commit it as an expected failure per `playbooks/ship.md`. Otherwise the output you kept in Reproduce it is the pin.
5. **Fix the root cause** (Fix root causes). Change the first place the system goes wrong. Ship the smallest change the evidence supports, and revert anything a refuted hypothesis motivated. If the fix fails and the next idea rests on the same assumption, test that assumption first (Attack the premise).
6. **Verify on the same surface.** The original repro now passes. The type check, lint, and the touched area's tests pass. Check the other callers of anything you changed. Unit tests show a branch works, not that the bug is gone.
7. **Review, then ship**, per Review in `SKILL.md` and `playbooks/ship.md`.

**Reply:** what was broken, the root cause, the fix, and how you verified it. Paste the failing and then the passing output.
