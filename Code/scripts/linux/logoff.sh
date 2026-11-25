#!/usr/bin/env bash
set -euo pipefail

if command -v loginctl >/dev/null 2>&1 && [[ -n "${XDG_SESSION_ID:-}" ]]; then
    loginctl terminate-session "$XDG_SESSION_ID"
elif command -v loginctl >/dev/null 2>&1 && [[ -n "${USER:-}" ]]; then
    loginctl terminate-user "$USER"
else
    echo "Erro: nao foi possivel encerrar a sessao automaticamente (XDG_SESSION_ID/loginctl indisponivel)." >&2
    exit 1
fi
