# Feature

**You own the design and the proof.** Small features only, in one feature area, where one shape is clearly right.

1. **Read the subsystem.** Trace the closest existing feature end to end: its entry point, its data shape, where it is stored or rendered, and its tests. Note the conventions you will follow. Check the Gate.
2. **Name the data shape** and its structure (Model the domain). Write down the type or shape the feature adds or changes, where it lives, and each entry point the feature will have. Pick the structure before you write logic.
3. **Design it** per `design.md`. The designer subagent sketches the shape and screens it against the red flags, and you write the step 4 acceptance check while it works. Carry the sketch's open decisions into the reply. If the designer returns Stop, Stop.
4. **Write the acceptance check.** A test or an exact surface observation that fails today and passes once the feature works, written from the user's side (Test behavior). Cover the happy path, the main error or empty state, and every entry point the feature has, using the verification skill's feature file when there is one. Run it and keep the failing output. Once the sketch returns, align the check with its signatures.
5. **Build against the sketch** in verifiable units (`design.md` steps 3 and 4). Subtract first if dead weight is in the way. Add the shape, then the logic, then the surface, and check each before the next. Put the new behavior where it belongs, not as a special case in a shared path (Design it as if it was always there). Validate external input at the boundary (Boundaries). Defaults, errors, and empty states get the same care as the happy path (Experience first).
6. **Verify.** The acceptance check passes. The type check, lint, and the touched area's tests pass. For a UI, CLI, or TUI change, drive the real surface and capture the evidence (output, screenshot, or the file written).
7. **Review, then ship**, per Review in `SKILL.md` and `playbooks/ship.md`.

**Reply:** what the user can now do, the shape you chose and why, the acceptance check failing and then passing, and open decisions.
