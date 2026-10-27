# Refactor

**The structure changes. The behavior does not.** If the cleanup reveals a bug or a missing feature, note it, ship the refactor first against the pin, then run that playbook.

1. Learn the contract. Read the code, its callers, and its tests. Write down what callers rely on: inputs, outputs, errors, side effects, and ordering. Check the Gate.
2. Pin the behavior. Run the tests that cover the contract. Where coverage is missing, write a characterization test, or a script that records current outputs for representative inputs. A type check and lint are not a pin.
3. Name the target shape. Describe what the code would look like if you wrote it today (Model the domain, Design it as if it was always there). The reshape must delete branches, layers, or invalid states, not add indirection. Code that is already clear stays. If the target spans more than one function, design it per `design.md`, with two candidate target shapes.
4. Subtract first. Delete dead code, one-caller wrappers, redundant checks, and orphan references (Subtract before you add). Run the pin, and commit the subtraction on its own.
5. Move in small behavior-preserving steps toward the target shape, and run the pin after each. With a sketch, build against it per `design.md` steps 5 and 6. Migrate every caller and delete the old name or API in the same change (Migrate, then delete). Grep for the old name in strings, docs, config, and tests, because renames miss those.
6. Prove nothing changed. The pin stays green. For a larger move, rerun the recorded-output script and diff the results. Drive the surface when the code backs one.
7. Confirm it earned its place (Reader load). Compare the layers, files, and branches a reader must follow, before and after. Revert the change and say so when it raises reader load without a reason, or when the user did not ask for it and it does not lower reader load.
8. Run Review, then Ship.

**Reply:** the structure that changed, the target shape you rejected when you designed it twice, the pin, the equivalence proof, the reader-load delta, and what shipped and what you reverted. No new behavior.
