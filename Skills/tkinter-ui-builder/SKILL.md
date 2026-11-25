---
name: tkinter-ui-builder
description: >-
  Use this skill when implementing, modifying, or reviewing the tkinter user
  interface and Canvas widgets of the Timer-Desligamento app in Code/. Ensures
  visual fidelity to the dark-mode specs, portable vector icons on Canvas,
  drift-free time.monotonic() timing, and safe after() lifecycle cleanup.
---

# Tkinter UI Builder (`tkinter-ui-builder`)

Esta skill orienta a implementação dos módulos de interface em `Code/timer_app/ui/` seguindo fielmente [Project/CASOS_DE_USO.md](../../Project/CASOS_DE_USO.md) e [Project/ESPECIFICACAO_TECNICA.md](../../Project/ESPECIFICACAO_TECNICA.md).

## Pré-requisitos Antes de Codificar

1. Leia as seções de paleta de cores, dimensões e assinatura de widgets em [Project/ESPECIFICACAO_TECNICA.md](../../Project/ESPECIFICACAO_TECNICA.md).
2. Confirme que não há dependências externas (`pip`) introduzidas; utilize exclusivamente `tkinter` da biblioteca padrão.

## Regras Obrigatórias de Implementação

1. **Ícones Vetoriais no `Canvas` (Zero Dependência de Emoji/Fonte):**
   - Desenhe os ícones `⌫` (backspace), `⏸` (pause), `▶` (play) e `✕` (fechar/cancelar) usando primitivas (`create_line`, `create_polygon`, `create_rectangle`) no `Canvas`.
   - Não dependa de caracteres Unicode como `⌫` ou `⏸`, pois falham ou mudam de alinhamento entre Windows e Linux.
2. **Pílulas e Barra Segmentada Suaves:**
   - Utilize `draw_rounded_rect` com polígono suavizado (`smooth=True`) para `PillButton` e `SegmentedSelector`.
   - Mantenha a barra segmentada (`Desligar | Reiniciar | Logoff`) posicionada imediatamente acima do botão `Iniciar`, com padrão inicial `PowerAction.DESLIGAR`.
3. **Temporização Sem Drift (`time.monotonic()`):**
   - Ao iniciar ou retomar, calcule `end_monotonic = time.monotonic() + remaining_seconds`.
   - Agende ticks de `50 ms` via `root.after(50, self._tick)` e guarde sempre o identificador em `self._after_id`.
   - Use `math.ceil(remaining)` para formatar `MM:SS` (`< 3600s`) ou `HH:MM:SS` (`>= 3600s`) sem pular segundos visuais.
   - Para o anel no `Canvas`, desenhe a trilha com `extent=359.9` (`RING_TRACK`) e o arco ativo (`ACCENT_BLUE`) iniciando em `start=90` reduzindo até `0.0`.
4. **Preservação de Estado e Encerramento Seguro:**
   - Ao cancelar pelo botão `X` da Tela 2 (`on_cancel_clicked`), cancele `self._after_id` antes de alternar para a Tela 1 e **preserve** o último tempo (`self.digits`) e a ação (`self.selected_action`).
   - Vincule `WM_DELETE_WINDOW` a `on_window_close()`, cancelando qualquer `after()` pendente antes de chamar `root.destroy()`.
   - Mapeie o teclado físico conforme a tela ativa: na `AppScreen.SETUP`, aceite `0`–`9`, `BackSpace`, `Escape` (limpar para `000000`) e `Return`/`KP_Enter`; na `AppScreen.COUNTDOWN`, aceite `space` (Play/Pause) e `Escape` (cancelar e voltar à Tela 1).
   - Mantenha a janela com comportamento minimalista padrão do SO (sem `topmost` forçado e sem efeitos sonoros).

## Verificação Pós-Implementação

1. Execute a suíte de fluxo de UI/estado (`python -m unittest Code/tests/test_app_flow.py -v`).
2. Execute o app em modo seguro (`python Code/main.py --dry-run --verbose`) e valide visualmente:
   - Alternância de cor do visor (`#6E7175` zerado -> `#FFFFFF` ativo).
   - Presets (`1min`, `5min`, `10min`, `15min`) preenchendo o visor sem iniciar sozinhos.
   - Seleção na barra segmentada, início, pausa/retomada e cancelamento no `X` preservando o estado.
