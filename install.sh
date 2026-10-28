#!/bin/sh
# Installs litestack into $CLAUDE_CONFIG_DIR, default ~/.claude, or updates it.
# From a clone: ./install.sh
# From GitHub: curl -fsSL https://raw.githubusercontent.com/RayenTellissy/litestack/main/install.sh | sh
set -eu

dest="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
src=$(cd "$(dirname "$0")" && pwd)

if [ ! -f "$src/skills/litestack/SKILL.md" ]; then
  ref="${LITESTACK_REF:-main}"
  repo="${LITESTACK_REPO:-RayenTellissy/litestack}"
  src=$(mktemp -d)
  trap 'rm -rf "$src"' EXIT
  curl -fsSL "https://github.com/$repo/archive/$ref.tar.gz" | tar -xz -C "$src" --strip-components=1
fi

mkdir -p "$dest/skills" "$dest/agents"
rm -rf "$dest/skills/litestack"
cp -R "$src/skills/litestack" "$dest/skills/"
cp "$src"/agents/litestack-*.md "$dest/agents/"

echo "litestack is installed in $dest. Start a new session to load it."
