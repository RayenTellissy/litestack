# Design

Feature runs this before it writes logic. Refactor runs it when the target shape spans more than one function. Skip it when the change stays inside one function body, and say so. A sketch is the interface and a few lines of pseudocode, so keep each one short.

## Steps

1. Sketch first. In a scratch file outside the repository, write the types, signatures, and module layout the change needs. Give every body a stub that fails when called, such as `throw new Error("not implemented")`, with pseudocode for the logic. Write no real logic yet.
2. Design it twice. Sketch a second shape that differs in structure, not detail. It might give the state a different owner, draw a different module boundary, use a table instead of branches, or expose a different interface. A point fix inside the first shape does not count.
3. Screen both against the Red flags below. A shape with a red flag gets revised or dropped. When the two shapes differ in behavior you can observe, write a probe: the smallest runnable scratch program that exercises only that behavior in each shape. Let its output pick.
4. Pick one. Prefer the shape that hides the most behind the smallest interface, that keeps reader load lowest, and where a change that looks right from one file is right for the whole repository. Note the shape you rejected and why, for the reply.
5. Build against the sketch. For a Feature, bring the chosen sketch into the repository and replace each stub with code. For a Refactor, the sketch is the target. Move the existing code toward it in pin-green steps, and never replace a live body with a stub. The sketch is the contract. When the code needs something the sketch did not plan, such as a new parameter, a second writer of some state, or a special case, stop. Decide whether the sketch was wrong, a requirement was missed, or the code is overreaching, and fix that one.
6. Scrap it when it is wrong. If the build keeps fighting the sketch, discard the sketch and drop the code and commits built on it, keeping the pin and the acceptance check. Return to step 1 with what you learned. Never bolt fixes onto a wrong shape. If the second round fails too, Stop, because the design is not small.

## Red flags

- **Shallow module.** A large interface that hides little. Callers must call several functions in order to do one thing, or its options expose internal steps.
- **Leaked decision.** One internal detail, such as a storage format, a policy, or a wire type, shows up in more than one module, so changing it means coordinated edits. Parse outside data into domain types behind one boundary.
- **Split by time, not knowledge.** Modules cut into load, validate, transform, and save stages that each relearn the same representation and its rules. Group code by what it knows and owns.
- **Pass-through layer.** A function that forwards its arguments to another of the same shape and adds no policy or adaptation.
- **Split ownership.** Two modules write the same state, or each keeps its own copy. Give each piece of state one owner that the others ask.
- **Two ways to do one task.** Whichever way a reader finds first gains the next caller. Fix an internal one per Migrate, then delete. A public one stays, per the Gate, and goes in the reply as an open item.
- **Reachable internals.** Outside code can import a module's internals, so they turn into its interface. Make them unreachable from outside.
- **Hand-synced lists.** Adding an item means editing several lists. Derive them from one list, or make the build fail when they disagree.
