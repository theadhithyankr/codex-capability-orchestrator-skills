#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SKILL_NAME="capability-orchestrator"
SOURCE_DIR="$ROOT_DIR/$SKILL_NAME"
SCOPE="${1:-}"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "error: $SKILL_NAME directory was not found next to install.sh" >&2
  exit 1
fi

case "$SCOPE" in
  --global|global)
    choice=1
    ;;
  --local|local)
    choice=2
    ;;
  "")
    echo "Install Codex Capability Orchestrator Skills"
    echo
    echo "Choose install location:"
    echo "  1) Global Codex skills (~/.codex/skills)"
    echo "  2) Local project skills (./.codex/skills)"
    echo
    printf "Enter 1 or 2 [1]: "
    read -r choice
    choice=${choice:-1}
    ;;
  *)
    echo "error: usage: ./install.sh [--global|--local]" >&2
    exit 1
    ;;
esac

case "$choice" in
  1)
    TARGET_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
    ;;
  2)
    TARGET_ROOT="$PWD/.codex/skills"
    ;;
  *)
    echo "error: expected 1 or 2" >&2
    exit 1
    ;;
esac

TARGET_DIR="$TARGET_ROOT/$SKILL_NAME"

mkdir -p "$TARGET_ROOT"
rm -rf "$TARGET_DIR"
cp -R "$SOURCE_DIR" "$TARGET_DIR"

echo
echo "Installed $SKILL_NAME to:"
echo "  $TARGET_DIR"
