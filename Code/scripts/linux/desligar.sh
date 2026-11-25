#!/usr/bin/env bash
set -euo pipefail

if command -v systemctl >/dev/null 2>&1; then
    systemctl poweroff
elif command -v shutdown >/dev/null 2>&1; then
    shutdown -h now
else
    poweroff
fi
