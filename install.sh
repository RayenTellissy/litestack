#!/bin/sh
# Installs litestack into $CLAUDE_CONFIG_DIR, default ~/.claude, or updates it.
# From a clone: ./install.sh
# From GitHub: curl -fsSL https://raw.githubusercontent.com/RayenTellissy/litestack/main/install.sh | sh
set -eu

dest="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

# Piped into sh, $0 is the shell's name, and its dirname would be the working directory.
case $0 in
  install.sh | */install.sh) src=$(cd "$(dirname "$0")" && pwd) ;;
  *) src= ;;
esac

if [ -z "$src" ] || [ ! -f "$src/skills/litestack/SKILL.md" ]; then
  ref="${LITESTACK_REF:-main}"
  repo="${LITESTACK_REPO:-RayenTellissy/litestack}"
  src=$(mktemp -d)
  trap 'rm -rf "$src"' EXIT
  curl -fsSL "https://github.com/$repo/archive/$ref.tar.gz" | tar -xz -C "$src" --strip-components=1
fi

# Check the download before the old install is removed.
if [ ! -f "$src/skills/litestack/SKILL.md" ]; then
  echo "No litestack skill in ${repo:-$src} at ${ref:-this clone}. Nothing was changed." >&2
  exit 1
fi

if grep -q '"litestack@' "$dest/plugins/installed_plugins.json" 2>/dev/null; then
  echo "Warning: the litestack plugin is also installed, so the skill and agents will load twice. Keep one." >&2
fi

mkdir -p "$dest/skills" "$dest/agents"
rm -rf "$dest/skills/litestack" "$dest"/agents/litestack-*.md
cp -R "$src/skills/litestack" "$dest/skills/"
cp "$src"/agents/litestack-*.md "$dest/agents/"

echo "litestack is installed in $dest. Start a new session to load it."
