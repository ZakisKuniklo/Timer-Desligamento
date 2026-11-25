# Product Requirements Document (PRD) — Timer-Desligamento

> **Produto:** Timer-Desligamento  
> **Versão Alvo:** 1.0  
> **Idioma da Interface:** Português (PT-BR)  
> **Status:** Validado e aprovado para implementação em `Code/`  
> **Documentos Complementares:** [CASOS_DE_USO.md](./CASOS_DE_USO.md) | [ESPECIFICACAO_TECNICA.md](./ESPECIFICACAO_TECNICA.md) | [CONTEXTO.md](./CONTEXTO.md)

---

## 1. Resumo Executivo e Problema

Usuários de desktop Windows e Linux frequentemente precisam agendar o **desligamento**, **reinício** ou **logoff** do computador após um intervalo específico (ex.: ao finalizar um download, renderização, backup ou antes de dormir), sem recorrer a comandos manuais no terminal (`shutdown /s /t ...` ou `systemctl poweroff`).

O **Timer-Desligamento** resolve essa necessidade oferecendo um aplicativo desktop leve, offline e zero-dependência em **Python 3 + Tkinter**, com estética minimalista em tema escuro inspirada no timer do Google Relógio, capaz de detectar automaticamente o sistema operacional e executar o script nativo correspondente ao término da contagem regressiva.

---

## 2. Objetivos do Produto e Critérios de Sucesso

| Objetivo | Métrica / Critério de Sucesso (v1.0) |
| :--- | :--- |
| **Simplicidade de configuração** | Usuário consegue selecionar ação e definir tempo (via preset ou teclado) em até 2–3 cliques ou diretamente pelo teclado físico. |
| **Fidelidade visual minimalista** | Interface reproduz o tema escuro das referências (`#000000` na configuração, `#1F242D` na contagem, anel circular `#1A73E8`), sem elementos supérfluos, sons ou janela fixa no topo. |
| **Confiabilidade multiplataforma** | Detecção automática entre Windows e Linux, com scripts isolados `.bat` e `.sh` e cobertura automatizada de testes unitários e de fluxo (`unittest`) com 100% de aprovação. |
| **Zero dependências externas** | Execução garantida apenas com Python 3 padrão (`tkinter` incluído), sem necessidade de `pip install` em ambiente padrão. |
| **Segurança operacional** | Cancelamento imediato pelo botão `X` ou `Esc` antes do término sem disparar comandos; modo `--dry-run` permite testar todo o fluxo sem desligar a máquina. |

---

## 3. Público-Alvo e Cenários de Uso

- **Usuário final de desktop (Windows / Linux):** Busca uma interface direta para agendar desligamento, reinício ou encerramento de sessão sem memorizar comandos de linha de comando.
- **Desenvolvedor / Power User:** Pode lançar o app sem terminal no Windows (`Code/app.pyw`) ou via CLI (`python Code/main.py`, incluindo `--dry-run --verbose` para inspeção e testes).

---

## 4. Escopo da Versão 1.0

### 4.1 Incluído no Escopo (In-Scope)
- Duas telas minimalistas em janela fixa (`390 x 650 px`, centralizada, não redimensionável):
  - **Tela 1 — Configuração:** Visor `HH MM SS` (`Horas`, `Minutos`, `Segundos`), presets rápidos (`1min`, `5min`, `10min`, `15min`), barra segmentada (`Desligar | Reiniciar | Logoff`), botão `Iniciar` e teclado numérico `3x4` (`1`–`9`, `00`, `0`, `⌫`).
  - **Tela 2 — Contagem Regressiva Ativa:** Cabeçalho com ação/tempo e botão `X`, anel circular de progresso azul, contador regressivo central (`MM:SS` ou `HH:MM:SS`) e controle Play/Pause vetorial (`⏸` / `▶`).
- Suporte completo a mouse e teclado físico (`0`–`9`, `BackSpace`, `Enter`, `Esc`, `Espaço`).
- Detecção automática de SO (`Windows` / `Linux`) e scripts separados por ação e SO (`scripts/win/*.bat` e `scripts/linux/*.sh`).
- Execução imediata do script ao atingir `00:00`, encerrando o app automaticamente em caso de disparo real bem-sucedido.
- Launcher sem janela de console no Windows (`Code/app.pyw`) e CLI com `--dry-run` e `--verbose` (`Code/main.py`).
- Suíte de testes automatizados (`Code/tests/`) com *mocks* seguros.

### 4.2 Fora do Escopo na v1.0 (Out-of-Scope / Backlog Futuro)
- Suporte a macOS (Darwin) — na v1.0 exibe aviso claro de SO não suportado.
- Empacotamento em executável standalone (ex.: `.exe` via PyInstaller ou AppImage).
- Elevação interativa de privilégios no Linux (`sudo` / `pkexec`).
- Agendamento por horário absoluto do relógio (ex.: "desligar às 23:30") — v1.0 atua exclusivamente como timer regressivo.
- Alertas sonoros, notificações do sistema ou modo *always-on-top*.
- Janela adicional de carência/confirmação ao zerar o timer.

---

## 5. Requisitos Funcionais

| ID | Requisito | Descrição e Regras de Negócio | Caso de Uso |
| :--- | :--- | :--- | :--- |
| **RF01** | Detecção de SO e validação inicial | Identificar `Windows` ou `Linux` na inicialização; alertar se o SO não for suportado ou se algum script esperado estiver ausente. | `UC01` |
| **RF02** | Entrada numérica deslizante | Teclado virtual `3x4` e teclas `0`–`9`/`BackSpace` inserem dígitos da direita para a esquerda em 6 posições (`HHMMSS`). Valores `>= 60` em `MM`/`SS` permanecem editáveis no visor e são normalizados ao iniciar. | `UC02` |
| **RF03** | Atalhos rápidos (Presets) | Botões `1min`, `5min`, `10min`, `15min` preenchem o visor (`00 01 00`, etc.) sem iniciar o timer automaticamente. | `UC03` |
| **RF04** | Seleção de ação de energia | Barra segmentada `Desligar \| Reiniciar \| Logoff` acima de `Iniciar`, iniciando com `Desligar` selecionada por padrão. | `UC04` |
| **RF05** | Início da contagem regressiva | Botão `Iniciar` (ou `Enter` na Tela 1) valida `total_segundos > 0`, alterna para Tela 2 e inicia contagem imediata. Com tempo zero, pisca feedback visual em vermelho no visor sem trocar de tela. | `UC05` |
| **RF06** | Pausar e retomar | Clique no ícone central (`⏸`/`▶`) ou tecla `Espaço` na Tela 2 congela/retoma a contagem mantendo o tempo restante exato via `time.monotonic()`. | `UC06` |
| **RF07** | Cancelamento e preservação de estado | Clique no `X` ou tecla `Esc` na Tela 2 cancela o loop `after()` sem disparar script e retorna à Tela 1 **preservando** o último tempo digitado e a ação selecionada. | `UC07` |
| **RF08** | Limpeza rápida na Tela 1 | Tecla `Esc` na Tela 1 limpa o visor de volta para `00 00 00` e desabilita `Iniciar`. | `UC02` |
| **RF09** | Execução imediata Windows (`.bat`) | Ao zerar no Windows, executa `desligar.bat` (`shutdown /s /f /t 0`), `reiniciar.bat` (`shutdown /r /f /t 0`) ou `logoff.bat` (`shutdown /l`) sem abrir janela de console (`CREATE_NO_WINDOW`) e fecha o app em caso de sucesso. | `UC08`, `UC11` |
| **RF10** | Execução imediata Linux (`.sh`) | Ao zerar no Linux, executa `bash <script>.sh` (`desligar.sh`, `reiniciar.sh`, `logoff.sh` via `systemctl`/`shutdown`/`loginctl`). Em falha de permissão ou código `!= 0`, exibe `messagebox.showerror` e retorna à Tela 1 sem usar `sudo` interativo ou `pkexec`. | `UC09`, `UC11` |
| **RF11** | Encerramento seguro e `--dry-run` | `WM_DELETE_WINDOW` cancela loops pendentes antes de destruir a janela. Com `--dry-run`, valida o script e exibe `messagebox.showinfo` com o comando simulado, retornando à Tela 1 sem desligar a máquina. | `UC10` |

---

## 6. Requisitos Não Funcionais

- **RNF01 — Zero Dependências Externas:** Todo o código de produção deve depender somente da biblioteca padrão do Python 3 (`>= 3.8`, recomendado `>= 3.10`).
- **RNF02 — Precisão Temporal:** Uso obrigatório de `time.monotonic()` para cálculo de tempo restante, evitando acúmulo de atraso (*drift*) do loop `tkinter.after(50, ...)` ou suspensão breve do sistema.
- **RNF03 — Portabilidade Visual:** Ícones (`⌫`, `⏸`, `▶`, `✕`) desenhados vetorialmente no `Canvas` para evitar inconsistência de glifos/emojis entre fontes Windows e Linux.
- **RNF04 — Discrição de Execução (Windows):** Fornecimento de `Code/app.pyw` para inicialização gráfica sem console e uso de `CREATE_NO_WINDOW` na invocação de arquivos `.bat`.
- **RNF05 — Minimalismo da Janela:** Janela com comportamento padrão do sistema operacional (sem `always-on-top` forçado e sem efeitos sonoros).
- **RNF06 — Integridade dos Scripts:** Arquivos `.bat` gravados em **CRLF** (`\r\n`) e arquivos `.sh` em **LF** (`\n`) UTF-8 sem BOM.
- **RNF07 — Segurança de Desenvolvimento e Testes:** Nenhuma rotina de teste automatizado pode invocar comandos reais de desligamento; validações reais de fluxo devem usar `unittest.mock` ou `--dry-run`.

---

## 7. Experiência do Usuário e Mapeamento de Controles

### 7.1 Mapa de Navegação e Atalhos

| Contexto | Ação do Usuário | Resultado |
| :--- | :--- | :--- |
| Tela 1 (`SETUP`) | Clique em `0`–`9`, `00` ou teclas `0`–`9` | Insere dígitos da direita para a esquerda até 6 dígitos (`HHMMSS`). |
| Tela 1 (`SETUP`) | Clique em `⌫` ou tecla `BackSpace` | Remove o dígito mais à direita e preenche `0` à esquerda. |
| Tela 1 (`SETUP`) | Tecla `Esc` | Zera o visor para `00 00 00`. |
| Tela 1 (`SETUP`) | Clique em `1min` / `5min` / `10min` / `15min` | Preenche o visor correspondente sem iniciar a contagem. |
| Tela 1 (`SETUP`) | Clique em `Desligar` / `Reiniciar` / `Logoff` | Seleciona o comando de energia (destaque azul `#1A73E8`). |
| Tela 1 (`SETUP`) | Clique em `Iniciar` ou tecla `Enter` | Se `total > 0`, abre Tela 2 e inicia contagem; se `0`, pisca alerta no visor. |
| Tela 2 (`COUNTDOWN`) | Clique em `⏸` / `▶` ou tecla `Espaço` | Pausa ou retoma a contagem regressiva. |
| Tela 2 (`COUNTDOWN`) | Clique em `X` ou tecla `Esc` | Cancela contagem sem disparar script e volta à Tela 1 preservando último tempo e ação. |
| Qualquer Tela | Fechar janela pelo botão do SO | Cancela callbacks `after()` pendentes e encerra o app com segurança. |

---

## 8. Arquitetura Técnica de Referência

A implementação em `Code/` segue exatamente a arquitetura modular especificada em [ESPECIFICACAO_TECNICA.md](./ESPECIFICACAO_TECNICA.md):

- **Entradas:** `Code/main.py` (CLI com `--dry-run` e `--verbose`) e `Code/app.pyw` (launcher sem console no Windows).
- **Núcleo de Domínio:** `timer_app/models.py`, `timer_app/config.py`, `timer_app/time_utils.py`, `timer_app/os_executor.py`.
- **Camada de UI (`tkinter.Canvas`):** `timer_app/ui/widgets.py`, `timer_app/ui/setup_view.py`, `timer_app/ui/countdown_view.py`, `timer_app/ui/app_window.py`.
- **Scripts de Energia:** `Code/scripts/win/{desligar,reiniciar,logoff}.bat` e `Code/scripts/linux/{desligar,reiniciar,logoff}.sh`.
- **Habilidades de Construção:** [tkinter-ui-builder](../Skills/tkinter-ui-builder/SKILL.md) e [power-scripts-validator](../Skills/power-scripts-validator/SKILL.md).

---

## 9. Critérios de Aceitação para Conclusão da v1.0

1. [ ] Todos os módulos previstos em `Code/` implementados sem dependências externas (`pip`).
2. [ ] `Code/app.pyw` abre a aplicação no Windows sem exibir janela de terminal ao fundo.
3. [ ] Todos os 6 scripts (`.bat` em CRLF e `.sh` em LF) presentes e validados quanto à sintaxe/conteúdo.
4. [ ] Entrada deslizante, presets, normalização (`00 00 90` -> `01:30`), atalhos (`Enter`, `Esc`, `Espaço`, `BackSpace`) e preservação de estado no `X` funcionando conforme especificado.
5. [ ] Suíte `python -m unittest discover -s Code/tests -v` passando 100% sem executar comandos reais no SO.
6. [ ] Teste manual via `python Code/main.py --dry-run --verbose` validado ponta a ponta na Tela 1 e Tela 2 (incluindo pausa, cancelamento e término simulado retornando à Tela 1).

---

## 10. Riscos e Mitigações

| Risco | Impacto | Mitigação Definida na v1.0 |
| :--- | :--- | :--- |
| Falha de permissão ao desligar/reiniciar no Linux (sem `polkit` ativo) | Alto | Scripts com fallback (`systemctl` -> `shutdown` -> `poweroff`/`reboot`), captura de `returncode`/`stderr` e feedback claro via `messagebox.showerror` retornando à Tela 1. |
| Quebra de linha incorreta em scripts (LF no `.bat` ou CRLF no `.sh`) | Médio | Validação automática nos testes unitários verificando `\r\n` para `.bat` e ausência de `\r` para `.sh`. |
| Inconsistência visual de emojis Unicode entre Windows e Linux | Médio | Desenho vetorial explícito no `Canvas` para `⌫`, `⏸`, `▶` e `✕`. |
| Janela preta de terminal aberta no Windows | Baixo | Fornecimento de `Code/app.pyw` para uso diário e `CREATE_NO_WINDOW` ao chamar `.bat`. |
| Disparo acidental de desligamento durante testes | Crítico | Modo `--dry-run` nativo, isolamento via `unittest.mock` e checklist obrigatório na skill `power-scripts-validator`. |
