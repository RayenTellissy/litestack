# Feature

**You own the design and the proof.** Small features only, in one feature area, where designing it twice gives a clear winner.

1. Read the subsystem. Trace the closest existing feature end to end: its entry point, its data shape, where it is stored or rendered, and its tests. Note the conventions you will follow. Check the Gate.
2. Name the data shape and its structure (Model the domain). Write down the type or shape the feature adds or changes, and where it lives. Pick the structure before you write logic.
3. Design it per `design.md`. Sketch first, design it twice, screen both shapes against the red flags, and pick one. If the two shapes differ in behavior you can observe, let a probe pick. A product call follows the Rules. If the pick is a real design tradeoff that neither the screen nor a probe settles, Stop.
4. Write the acceptance check. A test or an exact surface observation that fails today and passes once the feature works, written from the user's side (Test behavior). Cover the happy path, the main error or empty state, and every entry point the feature has, using the verification skill's feature file when there is one. Run it and keep the failing output.
5. Build against the sketch in verifiable units (`design.md` steps 5 and 6). Subtract first if dead weight is in the way. Add the shape, then the logic, then the surface, and check each before the next. Put the new behavior where it belongs, not as a special case in a shared path (Design it as if it was always there). Validate external input at the boundary (Boundaries). Defaults, errors, and empty states get the same care as the happy path (Experience first).
6. Verify. The acceptance check passes. The type check, lint, and the touched area's tests pass. For a UI, CLI, or TUI change, drive the real surface and capture the evidence (output, screenshot, or the file written).
7. Run Review, then Ship.

**Reply:** what the user can now do, the shape you chose and the one you rejected, with why, the forks you settled and how, the acceptance check failing and then passing, and open decisions.
