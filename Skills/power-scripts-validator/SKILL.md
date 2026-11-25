---
name: power-scripts-validator
description: >-
  Use this skill when creating, editing, or testing OS power scripts (.bat and
  .sh) and os_executor.py in Timer-Desligamento. Enforces safe dry-run and
  mocked testing so power commands never execute accidentally on the dev machine.
---

# Power Scripts Validator (`power-scripts-validator`)

Esta skill define o procedimento seguro para construir e validar `Code/timer_app/os_executor.py`, os scripts `Code/scripts/win/*.bat` e `Code/scripts/linux/*.sh`, e os testes automatizados correspondentes.

## Regra Crítica de Segurança

- **NUNCA** execute `desligar.bat`, `reiniciar.bat`, `logoff.bat`, `desligar.sh`, `reiniciar.sh` ou `logoff.sh` diretamente no terminal durante desenvolvimento ou testes.
- Toda validação funcional de disparo deve usar `unittest.mock` ou a flag `--dry-run` da aplicação.

## Procedimento para Scripts e Executor

1. **Scripts Windows (`Code/scripts/win/`):**
   - Salve com fim de linha **CRLF** (`\r\n`) e sem BOM UTF-8.
   - `desligar.bat`: `@echo off` + `shutdown /s /f /t 0`
   - `reiniciar.bat`: `@echo off` + `shutdown /r /f /t 0`
   - `logoff.bat`: `@echo off` + `shutdown /l` (não incluir `/t` nem `/f`, pois `shutdown /l` não aceita esses parâmetros no Windows).
   - No `os_executor.py`, invoque com `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` para ocultar janela de console.
2. **Scripts Linux (`Code/scripts/linux/`):**
   - Salve com fim de linha **LF** (`\n`) e permissão padrão legível (`#!/usr/bin/env bash` + `set -euo pipefail`).
   - `desligar.sh` / `reiniciar.sh`: priorize `systemctl poweroff` / `systemctl reboot`, com fallback para `shutdown -h now` / `shutdown -r now` e `poweroff` / `reboot`.
   - `logoff.sh`: priorize `loginctl terminate-session "$XDG_SESSION_ID"` com fallback para `loginctl terminate-user "$USER"`.
   - No `os_executor.py`, invoque sempre via `["bash", str(script_path)]` para não depender do bit `+x` em sistemas de arquivos diversos.
3. **Implementação de `--dry-run` em `execute_power_action()`:**
   - Valide SO (`detect_os()`) e existência do arquivo (`resolve_script_path(...).is_file()`) mesmo em `--dry-run`.
   - Quando `dry_run=True`, registre o comando montado via `logging` e retorne `ExecutionResult(success=True, dry_run=True, ...)` **antes** de chamar `subprocess.run()`.

## Checklist de Validação

1. Verifique via Python se todos os `.bat` terminam linhas com `\r\n` e se todos os `.sh` não contêm `\r` (apenas `\n`).
2. Se `bash` estiver disponível no ambiente, execute verificação de sintaxe estática (`bash -n Code/scripts/linux/*.sh`) — apenas análise sintática, nunca execução.
3. Execute a suíte automatizada completa:
   ```powershell
   python -m unittest discover -s Code/tests -v
   ```
4. Execute o fluxo ponta a ponta em modo seguro:
   ```powershell
   python Code/main.py --dry-run --verbose
   ```
   Confirme que o diálogo de simulação exibe o caminho exato do script esperado para o SO atual e que nenhum processo real de desligamento foi disparado.
