# Design

Feature runs this before it writes logic. Refactor runs it when the target shape spans more than one function. Skip it when the change stays inside one function body, and say so. A sketch is the interface and a few lines of pseudocode, so keep it short.

## Run it

Sketch and Screen run in a `litestack-designer` subagent, spawned per the Subagents rules in `SKILL.md`. While it runs, do only work that touches no code the designer reads, such as writing the Feature acceptance check in a new test file. A Refactor waits for the sketch. The brief holds these parts.

- Kind. Feature or Refactor.
- Intent. What the change must do and what it must leave unchanged, from the user's request.
- Shape. For a Feature, the data shape from the playbook's Name the data shape step. For a Refactor, the contract from Learn the contract and the target shape from Name the target shape.
- Entry points. For a Feature, each way in that the acceptance check will drive, such as a command, a route, or a public function, so the sketch keeps them.
- Code. The files and symbols you read, and the closest existing code that does something similar.
- For a second sketch, what made the build fight the first one.

If the designer returns Stop, Stop. Otherwise its sketch is the contract for Build and Scrap, which run in this session.

## Steps

1. **Sketch.** Write the types, signatures, and module layout the change needs, as code blocks headed with the repository path each belongs in. Give every body a stub that fails when called, such as `throw new Error("not implemented")`, with pseudocode for the logic. Write no real logic yet. Aim for the smallest interface that hides the most.
2. **Screen** the sketch against the Red flags below, and revise it until none apply, except a flag whose own text says it stays. If no shape is clearly right from the code, return Stop. A flag that no revision clears means no shape is clearly right.
3. **Build** against the sketch. For a Feature, write the sketch into the repository and replace each stub with code. For a Refactor, the sketch is the target. Move the existing code toward it in pin-green steps, and never replace a live body with a stub. The sketch is the contract. When the code needs something the sketch did not plan, such as a new parameter, a second writer of some state, or a special case, stop. Decide whether the sketch was wrong, a requirement was missed, or the code is overreaching, and fix that one.
4. **Scrap** it when it is wrong. If the build keeps fighting the sketch, discard the sketch and drop the code and commits built on it, keeping the pin and the acceptance check. Spawn a new designer whose brief says what fought the first sketch. Never bolt fixes onto a wrong shape. If the build fights the second sketch too, Stop, because the design is not small.

## Red flags

- **Shallow module.** A large interface that hides little. Callers must call several functions in order to do one thing, or its options expose internal steps.
- **Leaked decision.** One internal detail, such as a storage format, a policy, or a wire type, shows up in more than one module, so changing it means coordinated edits. Parse outside data into domain types behind one boundary.
- **Split by time, not knowledge.** Modules cut into load, validate, transform, and save stages that each relearn the same representation and its rules. Group code by what it knows and owns.
- **Pass-through layer.** A function that forwards its arguments to another of the same shape and adds no policy or adaptation.
- **Split ownership.** Two modules write the same state, or each keeps its own copy. Give each piece of state one owner that the others ask.
- **Two ways to do one task.** Whichever way a reader finds first gains the next caller. Fix an internal one by moving its callers and deleting it (Migrate, then delete). A public one stays, per the Gate, and goes in the reply as an open item.
- **Reachable internals.** Outside code can import a module's internals, so they turn into its interface. Make them unreachable from outside.
- **Hand-synced lists.** Adding an item means editing several lists. Derive them from one list, or make the build fail when they disagree.
