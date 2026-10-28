# shop

The message layer of a small web shop. Every user-facing string lives in one
module per area under `shop/`. `python3 -m shop <area> <message> [args...]`
prints one message, for example `python3 -m shop cart add mug 2`.

Run the tests with `python3 -m unittest discover -s tests`.
