# Chore

Docs, config, copy, dependency bumps, build or CI fixes, and test-only changes.

1. Find what consumes the change: the build, the docs renderer, the app that loads the config, the test runner, or the code that calls the dependency. For a dependency bump, read the changelog between the two versions and list each breaking change that touches this project, or write that there are none. Check the Gate. A bump with breaking changes that touch this project is a Feature, or too big.
2. Pin it. Run the consumer and keep its output.
3. Make the change. Keep it the smallest change that does the job, in the file's existing style.
4. Verify. Run the consumer again. Docs render, config loads and takes effect, the build or CI step passes, and the bumped dependency's call sites still behave. For prose, run each command and open each path it names.
5. Run Review, then Ship.

**Reply:** what changed, the consumer check before and after, and each breaking change you checked.
