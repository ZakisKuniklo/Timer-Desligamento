# Contexto do Projeto — Timer de Desligamento

> **Objetivo deste documento:** Registrar todo o histórico, decisões arquiteturais, especificações visuais, estado atual e próximos passos do projeto para que qualquer modelo de IA ou desenvolvedor possa ler este arquivo e retomar o trabalho exatamente de onde paramos.

---

## 1. Visão Geral do Projeto

- **Nome:** Timer-Desligamento
- **Descrição:** Aplicativo desktop em Python com interface gráfica em `tkinter` que permite ao usuário definir um temporizador (contagem regressiva) e escolher uma ação de energia para o computador (**Desligamento**, **Reinício** ou **Logoff**). Ao término do tempo, o aplicativo identifica automaticamente o sistema operacional (**Windows** ou **Linux**) e executa o script correspondente (`.bat` no Windows ou `.sh` no Linux).
- **Idioma da Interface:** Português (PT-BR), conforme referências visuais enviadas pelo usuário.
- **Stack Tecnológica Definida:**
  - Linguagem: Python 3 (exclusivamente biblioteca padrão, sem dependências externas via `pip`)
  - Interface Gráfica: `tkinter` (`Canvas` customizado para pílulas arredondadas, barra segmentada, teclado flat, anel de progresso circular e ícones vetoriais portáteis)
  - Execução de Sistema: Detecção de SO (`platform.system()`) + `subprocess.run()` para scripts `.bat` (Windows, com `CREATE_NO_WINDOW`) e `.sh` (Linux, via `bash`), além de suporte a modo CLI `--dry-run` para testes seguros.
  - Arquitetura modular em `Code/`: `main.py`, `app.pyw` (launcher sem janela de console no Windows), `timer_app/` (`config.py`, `models.py`, `time_utils.py`, `os_executor.py`, `ui/`), `scripts/` (`win/`, `linux/`) e `tests/` (`unittest`).

---

## 2. Estrutura de Diretórios do Workspace

```text
Timer-Desligamento/
├── .agents/
│   └── skills.json              # Registro local para descoberta automática da pasta Skills/
├── .gitattributes               # Regras de quebra de linha (CRLF para .bat, LF para .sh/.py)
├── .gitignore                   # Exclusões Git para Python, ambientes virtuais, IDEs e SO
├── README.md                    # Documentação completa de uso, atalhos, scripts e testes
├── Code/                        # Código-fonte do aplicativo Python, scripts e testes (v1.0)
│   ├── main.py                  # Ponto de entrada CLI (--dry-run, --verbose)
│   ├── app.pyw                  # Launcher gráfico sem console no Windows
│   ├── timer_app/
│   │   ├── __init__.py
│   │   ├── config.py            # Paleta hex, dimensões, fontes, presets e rótulos
│   │   ├── models.py            # Enums e dataclass ExecutionResult
│   │   ├── time_utils.py        # Funções puras HHMMSS, normalização e ângulos
│   │   ├── os_executor.py       # Detecção de SO, validação e execução segura
│   │   └── ui/
│   │       ├── __init__.py
│   │       ├── widgets.py       # Componentes Canvas (pílulas, barra, teclado, anel, ícones)
│   │       ├── setup_view.py    # Tela 1 (Configuração)
│   │       ├── countdown_view.py# Tela 2 (Contagem Regressiva Ativa)
│   │       └── app_window.py    # Controlador principal TimerShutdownApp
│   ├── scripts/
│   │   ├── win/                 # desligar.bat, reiniciar.bat, logoff.bat (CRLF)
│   │   └── linux/               # desligar.sh, reiniciar.sh, logoff.sh (LF)
│   └── tests/                   # Suíte unittest (test_time_utils, test_os_executor, test_app_flow)
├── Project/                     # Documentação do projeto
│   ├── CONTEXTO.md              # Este arquivo: contexto contínuo de conversas e decisões
│   ├── PRD.md                   # Product Requirements Document (escopo, RFs, RNFs e critérios de aceite v1.0)
│   ├── CASOS_DE_USO.md          # Casos de uso, especificações visuais e fluxos de execução
│   └── ESPECIFICACAO_TECNICA.md # Especificação técnica detalhada (módulos, funções e fluxos)
└── Skills/                      # Habilidades personalizadas do agente
    ├── context-write/
    │   └── SKILL.md             # Habilidade "context write" para manter este documento atualizado
    ├── power-scripts-validator/
    │   └── SKILL.md             # Habilidade para criar/validar scripts .bat/.sh e testes --dry-run
    └── tkinter-ui-builder/
        └── SKILL.md             # Habilidade para construir UI Canvas e loop monotonic sem drift
```

---

## 3. Referências Visuais Fornecidas pelo Usuário

O usuário enviou 2 imagens de referência inspiradas em um aplicativo de timer moderno em tema escuro (estilo Google Relógio):

1. **Tela de Configuração do Timer** (`.user_uploaded/media_1795627484477_de85310e.jpg`):
   - Fundo escuro/preto (`#000000` / `#121212`).
   - Visor superior com 3 pares de dígitos grandes: `00` `00` `00` com rótulos `Horas`, `Minutos`, `Segundos`.
   - Fileira de botões rápidos em formato pílula: `1min`, `5min`, `10min`, `15min`.
   - Botão principal largo em formato pílula: `Iniciar`.
   - Teclado numérico 3x4 abaixo (`1`–`9`, `00`, `0`, e ícone de backspace `⌫`).
   - *Adaptação necessária:* Incluir seletor da ação de energia (**Desligar**, **Reiniciar**, **Logoff**) sem poluir a estética minimalista da referência.

2. **Tela de Contagem Regressiva Ativa** (`.user_uploaded/media_1795627484477_c9f8a185.jpg`):
   - Fundo cinza-azulado escuro (`#1F242D`).
   - Cabeçalho superior: título à esquerda (ex.: `Timer de 5min` — adaptável para indicar também a ação selecionada) e ícone `X` (fechar/cancelar) à direita.
   - Centro: Anel circular azul vibrante (`#1A73E8` / `#2575FC`) representando o progresso restante da contagem.
   - Interior do anel: Tempo restante centralizado em fonte branca fina (`05:00` ou `HH:MM:SS`) e ícone branco de Play/Pause logo abaixo dos dígitos.

---

## 4. Requisitos Funcionais e Decisões Consolidadas

1. **Escolha do comando:** O usuário escolhe entre **Desligar**, **Reiniciar** ou **Logoff** através de uma **barra segmentada** posicionada **acima do botão `Iniciar`** na tela de configuração (ação padrão inicial: **Desligar**).
2. **Definição de tempo, Presets e Atalhos de Teclado:**
   - Teclado numérico virtual `3x4` (com entrada da direita para a esquerda em `HH MM SS`, além de suporte a teclado físico: `0`–`9`, `BackSpace`, `Enter` para iniciar e `Esc` para zerar o visor na Tela 1) e 4 botões rápidos mantendo exatamente `1min`, `5min`, `10min` e `15min`.
   - Clicar em um preset apenas **preenche o visor** (`00 05 00`, etc.) e aguarda o usuário clicar em **`Iniciar`**.
3. **Tela de Contagem Regressiva Ativa:**
   - Janela 100% minimalista (comportamento padrão do SO, sem `always-on-top` e sem sons), anel circular azul de progresso, contador central e controle Play/Pause vetorial (`⏸` / `▶`, acionável também via tecla `Espaço`).
   - Clicar no botão **`X`** no canto superior direito (ou pressionar `Esc`) **cancela a contagem** (sem executar nenhuma ação) e **retorna para a tela de configuração preservando o último valor digitado e a ação selecionada**.
4. **Tecnologia, Arquitetura e Lançamento:** Desenvolvido em **Python 3** usando exclusivamente a biblioteca padrão (**`tkinter`**, `Canvas`, `time.monotonic`, `subprocess`, `unittest`) em arquitetura modular (`Code/main.py`, `Code/app.pyw` para abrir sem console no Windows, `timer_app/ui/`, `timer_app/`, `scripts/`, `tests/`), conforme detalhado em [Project/PRD.md](./PRD.md) e [Project/ESPECIFICACAO_TECNICA.md](./ESPECIFICACAO_TECNICA.md).
5. **Detecção de SO e Scripts:**
   - O programa identifica automaticamente **Windows** ou **Linux**.
   - **Organização dos scripts:** Arquivos separados por ação e SO (`scripts/win/{desligar,reiniciar,logoff}.bat` e `scripts/linux/{desligar,reiniciar,logoff}.sh`).
   - **Flags Windows (`.bat`):** `desligar.bat` usa `shutdown /s /f /t 0`; `reiniciar.bat` usa `shutdown /r /f /t 0`; `logoff.bat` usa `shutdown /l`.
   - **Disparo final, falhas e pós-execução:** Execução **imediata** do script correspondente ao zerar o timer; em caso de sucesso na execução real, o app fecha a janela (`root.destroy()`). Em falha de permissão no Linux, exibe alerta (`messagebox.showerror`) e retorna à Tela 1 sem usar `sudo` interativo nem `pkexec`.
6. **Modo de Teste Seguro (`--dry-run`):** O ponto de entrada `Code/main.py` aceita `--dry-run` e `--verbose` para validar toda a UI, detecção de SO e resolução de scripts; ao zerar em `--dry-run`, exibe o script simulado via diálogo e retorna à Tela 1.
7. **Estado atual (v1.0 implementada):** O aplicativo completo foi implementado em `Code/`, validado com 26 testes automatizados (`unittest`), verificação sintática dos scripts `.sh` (`bash -n`), validação de fim de linha CRLF/LF e teste funcional em modo `--dry-run`, além da preparação do repositório para GitHub (`README.md`, `.gitignore`, `.gitattributes`).

---

## 5. Decisões em Aberto

- Definir se o repositório terá arquivo `LICENSE` (ex.: MIT) antes do push para o GitHub.
- Definir se o repositório Git local (`git init` + commit inicial) deve ser inicializado nesta pasta ou se será configurado manualmente pelo usuário.
- *(Opcional futuro)* Empacotamento em executável standalone (ex.: PyInstaller) ou permissões `polkit`/sem senha em distribuições Linux específicas, caso necessário após a v1.0.

---

## 6. Histórico de Sessões / Conversas

### Sessão 1 — 2026-11-25 (Inicialização, Documentação e Alinhamento de Requisitos)
- **Resumo:** O usuário apresentou o escopo inicial do projeto *Timer-Desligamento*, enviou duas capturas de tela de referência visual e solicitou:
  1. Criação do documento de contexto contínuo na pasta `Project/`.
  2. Criação da skill `"context write"` para atualizar esse documento de contexto.
  3. Criação de um documento completo de casos de uso, especificações visuais e fluxos de execução na pasta `Project/`.
  4. Levantamento de perguntas de esclarecimento antes de iniciar qualquer código.
- **Decisões respondidas pelo usuário nesta sessão:**
  - Seletor de comando: barra segmentada (`Desligar | Reiniciar | Logoff`) acima do botão `Iniciar`.
  - Presets (`1min`, `5min`, `10min`, `15min`): mantidos exatamente como na print; ao clicar, preenchem o visor e aguardam o clique em `Iniciar`.
  - Botão `X` na tela do timer ativo: cancela a contagem e retorna para a tela de configuração.
  - Scripts `.bat` / `.sh`: arquivos separados por ação e SO (`desligar`, `reiniciar`, `logoff`), com execução imediata ao zerar o timer.
- **Artefatos criados/atualizados nesta sessão:**
  - [Project/CONTEXTO.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/CONTEXTO.md)
  - [Project/CASOS_DE_USO.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/CASOS_DE_USO.md)
  - [Skills/context-write/SKILL.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Skills/context-write/SKILL.md)
  - [.agents/skills.json](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/.agents/skills.json)
- **Próximo passo:** Criar especificação técnica detalhada e resolver decisões pendentes antes da codificação.

### Sessão 2 — 2026-11-25 (Especificação Técnica Detalhada e Skills de Construção)
- **Resumo:** Com base no contexto e nos casos de uso, foram esclarecidos os detalhes técnicos pendentes com o usuário, criada a especificação técnica detalhada por módulo e por caso de uso (`UC01`–`UC11`), criadas duas skills especializadas em `Skills/` para apoiar a construção segura do código, e sincronizados os documentos do projeto.
- **Decisões respondidas pelo usuário nesta sessão:**
  - Stack e organização: apenas biblioteca padrão (`tkinter` + `Canvas`), sem dependências externas, organizada em módulos separados (`ui/`, `core`/lógica, `scripts/`, `tests/`).
  - Scripts Windows (`.bat`): usar flag `/f` em desligamento e reinício (`shutdown /s /f /t 0` e `shutdown /r /f /t 0`).
  - Pós-disparo e botão `X`: fechar o app após disparar o script real com sucesso; ao clicar em `X` na Tela 2, voltar à Tela 1 preservando o último tempo e a ação selecionados.
  - Modo de simulação: incluir suporte a `--dry-run` via CLI para testar todo o fluxo sem desligar o computador.
- **Artefatos criados/atualizados nesta sessão:**
  - [Project/ESPECIFICACAO_TECNICA.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/ESPECIFICACAO_TECNICA.md)
  - [Project/CASOS_DE_USO.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/CASOS_DE_USO.md)
  - [Project/CONTEXTO.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/CONTEXTO.md)
  - [Skills/tkinter-ui-builder/SKILL.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Skills/tkinter-ui-builder/SKILL.md)
  - [Skills/power-scripts-validator/SKILL.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Skills/power-scripts-validator/SKILL.md)
- **Próximo passo:** Iniciar a implementação na pasta `Code/` seguindo [Project/ESPECIFICACAO_TECNICA.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/ESPECIFICACAO_TECNICA.md) e utilizando as skills `tkinter-ui-builder` e `power-scripts-validator`, validando ao final com `unittest` e `--dry-run`.

### Sessão 3 — 2026-11-25 (Validação Final de Pontas Soltas e Criação do PRD)
- **Resumo:** Foram validadas com o usuário todas as pontas soltas finais (atalhos de teclado, launcher sem terminal no Windows, minimalismo da janela, comportamento do `--dry-run` e tratamento de erro no Linux), criado o **PRD (Product Requirements Document)** da v1.0 e sincronizados todos os documentos de especificação e skills.
- **Decisões respondidas pelo usuário nesta sessão:**
  - Atalhos físicos e retorno no `X`: suportar `Esc` (limpa visor na Tela 1 / cancela contagem na Tela 2) e `Espaço` (Play/Pause na Tela 2); no `X`, retornar mantendo o último valor digitado e a ação selecionada.
  - Lançamento diário na v1.0: via `python Code/main.py` e launcher `Code/app.pyw` (sem janela de console no Windows).
  - Minimalismo da Tela 2: janela padrão do SO, sem `always-on-top` e sem efeitos sonoros.
  - Finalização `--dry-run` e erro Linux: em `--dry-run`, exibe diálogo com o script simulado e retorna à Tela 1; em erro de permissão no Linux, exibe alerta e retorna à Tela 1 sem usar `sudo` interativo ou `pkexec`.
- **Artefatos criados/atualizados nesta sessão:**
  - [Project/PRD.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/PRD.md)
  - [Project/ESPECIFICACAO_TECNICA.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/ESPECIFICACAO_TECNICA.md)
  - [Project/CASOS_DE_USO.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/CASOS_DE_USO.md)
  - [Project/CONTEXTO.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/CONTEXTO.md)
  - [Skills/tkinter-ui-builder/SKILL.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Skills/tkinter-ui-builder/SKILL.md)
- **Próximo passo:** Implementar a versão 1.0 na pasta `Code/` seguindo [Project/PRD.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/PRD.md) e [Project/ESPECIFICACAO_TECNICA.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/ESPECIFICACAO_TECNICA.md), utilizando as skills `tkinter-ui-builder` e `power-scripts-validator`, e validar com `python -m unittest discover -s Code/tests -v` e `python Code/main.py --dry-run --verbose`.

### Sessão 4 — 2026-11-25 (Implementação da v1.0 em `Code/`, Testes e Preparação para GitHub)
- **Resumo:** Construída integralmente a versão 1.0 do aplicativo *Timer-Desligamento* na pasta `Code/` seguindo as especificações e skills do projeto, além da criação da documentação e arquivos de configuração para publicação no GitHub.
- **Implementação e ajustes realizados:**
  - Núcleo de domínio (`models.py`, `config.py`, `time_utils.py`, `os_executor.py`), pontos de entrada (`main.py` e `app.pyw`) e camada visual em `tkinter.Canvas` (`widgets.py`, `setup_view.py`, `countdown_view.py`, `app_window.py`) sem dependências externas.
  - Scripts nativos criados e validados: `Code/scripts/win/{desligar,reiniciar,logoff}.bat` (CRLF sem BOM) e `Code/scripts/linux/{desligar,reiniciar,logoff}.sh` (LF sem BOM).
  - Corrigida colisão de atributo `self._options` em `SegmentedSelector` (`tk.Misc._options`) renomeando para `self._segments`.
  - Preparação para GitHub com `README.md`, `.gitignore` e `.gitattributes`.
- **Validações executadas:**
  - `python -m unittest discover -s Code/tests -v`: **26 testes executados, 26 aprovados (`OK`)** cobrindo `test_time_utils.py`, `test_os_executor.py` e `test_app_flow.py`.
  - `bash -n Code/scripts/linux/*.sh`: código de saída `0` (sintaxe válida).
  - Teste smoke da GUI em `--dry-run` (abertura, preset, seleção de ação, início, pausa, cancelamento preservando estado e fechamento seguro): concluído com sucesso (`SMOKE_OK`).
- **Artefatos criados/atualizados nesta sessão:**
  - [README.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/README.md)
  - [.gitignore](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/.gitignore)
  - [.gitattributes](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/.gitattributes)
  - [Code/main.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/main.py)
  - [Code/app.pyw](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/app.pyw)
  - [Code/timer_app/models.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/timer_app/models.py)
  - [Code/timer_app/config.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/timer_app/config.py)
  - [Code/timer_app/time_utils.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/timer_app/time_utils.py)
  - [Code/timer_app/os_executor.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/timer_app/os_executor.py)
  - [Code/timer_app/ui/widgets.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/timer_app/ui/widgets.py)
  - [Code/timer_app/ui/setup_view.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/timer_app/ui/setup_view.py)
  - [Code/timer_app/ui/countdown_view.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/timer_app/ui/countdown_view.py)
  - [Code/timer_app/ui/app_window.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/timer_app/ui/app_window.py)
  - [Code/scripts/win/desligar.bat](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/scripts/win/desligar.bat), [reiniciar.bat](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/scripts/win/reiniciar.bat), [logoff.bat](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/scripts/win/logoff.bat)
  - [Code/scripts/linux/desligar.sh](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/scripts/linux/desligar.sh), [reiniciar.sh](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/scripts/linux/reiniciar.sh), [logoff.sh](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/scripts/linux/logoff.sh)
  - [Code/tests/test_time_utils.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/tests/test_time_utils.py), [test_os_executor.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/tests/test_os_executor.py), [test_app_flow.py](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Code/tests/test_app_flow.py)
  - [Project/CONTEXTO.md](file:///c:/Users/sousaj/Documents/Projetos/Timer-Desligamento/Project/CONTEXTO.md)
- **Próximo passo:** Realizar inspeção visual interativa via `python Code/main.py --dry-run --verbose`, decidir sobre adição de arquivo `LICENSE` (ex.: MIT) e inicializar/enviar o repositório para o GitHub (`git init`, commit inicial e `git push`).
