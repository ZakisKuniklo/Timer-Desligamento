#!/usr/bin/env bash
set -euo pipefail

if command -v systemctl >/dev/null 2>&1; then
    systemctl reboot
elif command -v shutdown >/dev/null 2>&1; then
    shutdown -r now
else
    reboot
fi
