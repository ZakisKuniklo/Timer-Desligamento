# Timer de Desligamento

Aplicativo desktop minimalista em **Python 3 + Tkinter** (sem dependências externas) para agendar o **desligamento**, **reinício** ou **logoff** do computador por meio de uma contagem regressiva visual em tema escuro.

Ao término da contagem regressiva, o aplicativo identifica automaticamente o sistema operacional (**Windows** ou **Linux**) e dispara o script nativo correspondente (`.bat` no Windows ou `.sh` no Linux).

---

## Principais Recursos

- **Zero dependências externas:** Construído exclusivamente com a biblioteca padrão do Python 3 (`tkinter`, `time.monotonic`, `subprocess`, `pathlib`, `argparse`, `unittest`).
- **Interface minimalista em tema escuro:** Janela fixa (`390 × 650 px`), centralizada e com componentes desenhados em `tkinter.Canvas` (pílulas arredondadas, barra segmentada, teclado numérico flat, anel circular de progresso e ícones vetoriais portáteis).
- **Entrada numérica intuitiva (`HH MM SS`):** Teclado virtual `3x4` e suporte completo ao teclado físico com preenchimento da direita para a esquerda e normalização automática de tempo (ex.: `00 00 90` equivale a `01:30`).
- **Atalhos rápidos (Presets):** Botões `1min`, `5min`, `10min` e `15min` preenchem o visor para revisão antes de iniciar.
- **Três ações de energia:** Seletor em barra segmentada (`Desligar | Reiniciar | Logoff`), com **Desligar** selecionado por padrão.
- **Precisão temporal sem drift:** Cálculo baseado em `time.monotonic()`, mantendo o tempo restante fiel mesmo sob atrasos de interface ou suspensão breve do sistema.
- **Modo seguro `--dry-run`:** Permite testar toda a interface, validação de scripts e disparo final simulado sem desligar o computador.
- **Execução discreta no Windows:** Inclui launcher `Code/app.pyw` (sem janela de console) e executa scripts `.bat` com `CREATE_NO_WINDOW`.

---

## Como Funciona

O aplicativo opera em duas telas conectadas a uma máquina de estados simples (`IDLE` → `RUNNING` / `PAUSED` → `FINISHED`):

### 1. Tela de Configuração (`SETUP`)
- **Visor `HH MM SS`:** Exibe `00 00 00` em cinza (`#6E7175`) quando zerado e passa a branco (`#FFFFFF`) assim que um tempo é definido. Caso tente iniciar com tempo zero, o visor pisca brevemente em vermelho (`#E53935`).
- **Presets (`1min`, `5min`, `10min`, `15min`):** Preenchem o visor instantaneamente e aguardam o clique em **Iniciar** (não disparam sozinhos).
- **Barra segmentada (`Desligar | Reiniciar | Logoff`):** Define qual comando será executado ao término da contagem.
- **Teclado `3x4` (`1`–`9`, `00`, `0`, `⌫`):** Insere dígitos da direita para a esquerda em até 6 posições (`HHMMSS`).

### 2. Tela de Contagem Regressiva Ativa (`COUNTDOWN`)
- **Cabeçalho:** Mostra a ação e a duração configurada (ex.: `Desligar • 05:00`) e um botão vetorial **`X`** no canto superior direito para cancelar imediatamente a contagem e retornar à Tela 1 **preservando o último tempo e a ação selecionados**.
- **Anel Circular de Progresso:** Arco azul (`#1A73E8`) que reduz suavemente conforme o tempo restante, exibindo `MM:SS` (abaixo de 1 hora) ou `HH:MM:SS` (1 hora ou mais).
- **Play / Pause (`⏸` / `▶`):** Congela e retoma o tempo restante exato a qualquer momento antes do término.
- **Disparo imediato ao zerar:** Ao atingir `00:00`, o aplicativo executa imediatamente o script do sistema operacional correspondente:
  - Em caso de **sucesso real**, o aplicativo fecha a janela automaticamente após entregar o comando ao SO.
  - Em caso de **erro** (ex.: falta de permissão no Linux), exibe uma caixa de diálogo detalhando o erro e retorna à Tela 1.
  - Em **`--dry-run`**, exibe uma janela informativa com o comando que seria executado e retorna à Tela 1.

---

## Atalhos de Teclado

| Tela | Tecla | Ação |
| :--- | :--- | :--- |
| **Configuração** | `0` – `9` | Insere o dígito da direita para a esquerda |
| **Configuração** | `BackSpace` | Apaga o último dígito inserido |
| **Configuração** | `Esc` | Zera o visor para `00 00 00` |
| **Configuração** | `Enter` | Inicia a contagem regressiva (se tempo > 0) |
| **Contagem Ativa** | `Espaço` | Pausa ou retoma a contagem |
| **Contagem Ativa** | `Esc` | Cancela o timer e retorna à Tela 1 preservando tempo e ação |

---

## Pré-requisitos

- **Python 3.8 ou superior** (recomendado Python 3.10+)
- **Tkinter** (incluído por padrão no instalador oficial do Python para Windows)
- **Sistema Operacional suportado:** Windows ou Linux

> **Nota para usuários Linux (Debian/Ubuntu/Mint):** algumas distribuições não incluem o Tkinter no pacote básico do Python. Se necessário, instale com:
> ```bash
> sudo apt update && sudo apt install -y python3-tk
> ```

---

## Como Executar

Clone o repositório e acesse a pasta do projeto:

```bash
git clone <URL_DO_REPOSITORIO>
cd Timer-Desligamento
```

### Windows

- **Uso diário sem janela de console (recomendado):** dê um duplo clique em `Code/app.pyw` ou execute:
  ```powershell
  pythonw Code/app.pyw
  ```
- **Via terminal:**
  ```powershell
  python Code/main.py
  ```

### Linux

```bash
python3 Code/main.py
```

### Modo de Simulação Segura (`--dry-run`)

Para testar toda a interface, contagem, pausa, cancelamento e resolução do script **sem desligar o computador**:

```bash
python Code/main.py --dry-run --verbose
```

Flags disponíveis em `Code/main.py`:
- `--dry-run`: simula o disparo final ao zerar o timer e exibe um diálogo com o comando/script que seria chamado.
- `--verbose`: ativa logs detalhados (`DEBUG`) no terminal.

---

## Scripts de Energia por Sistema Operacional

Cada ação possui um arquivo dedicado por sistema operacional em `Code/scripts/`:

| Ação | Windows (`Code/scripts/win/`, CRLF) | Linux (`Code/scripts/linux/`, LF) |
| :--- | :--- | :--- |
| **Desligar** | `desligar.bat` (`shutdown /s /f /t 0`) | `desligar.sh` (`systemctl poweroff` / `shutdown -h now` / `poweroff`) |
| **Reiniciar** | `reiniciar.bat` (`shutdown /r /f /t 0`) | `reiniciar.sh` (`systemctl reboot` / `shutdown -r now` / `reboot`) |
| **Logoff** | `logoff.bat` (`shutdown /l`) | `logoff.sh` (`loginctl terminate-session "$XDG_SESSION_ID"` / `terminate-user`) |

- No **Windows**, os arquivos `.bat` são executados com `CREATE_NO_WINDOW` para não exibir janela de prompt.
- No **Linux**, os arquivos `.sh` são invocados via `bash <caminho_do_script>`, não dependendo da permissão `+x` no sistema de arquivos. Caso o ambiente exija privilégios elevados (ex.: ambiente sem `systemd`/`polkit` configurado para usuário comum), o aplicativo captura a falha e exibe o erro retornado sem travar.

---

## Estrutura do Projeto

```text
Timer-Desligamento/
├── .gitignore                   # Arquivos ignorados no versionamento Git
├── .gitattributes               # Garante CRLF para .bat e LF para .sh/.py
├── README.md                    # Documentação principal do repositório
├── Code/                        # Código-fonte, scripts de SO e testes
│   ├── main.py                  # Ponto de entrada CLI (--dry-run, --verbose)
│   ├── app.pyw                  # Launcher gráfico sem console no Windows
│   ├── timer_app/
│   │   ├── __init__.py
│   │   ├── config.py            # Paleta de cores, dimensões, fontes e presets
│   │   ├── models.py            # Enums e dataclass ExecutionResult
│   │   ├── time_utils.py        # Lógica pura HHMMSS, normalização e ângulos
│   │   ├── os_executor.py       # Detecção de SO, validação e execução segura
│   │   └── ui/
│   │       ├── __init__.py
│   │       ├── widgets.py       # Componentes Canvas (pílulas, anel, ícones vetoriais)
│   │       ├── setup_view.py    # Tela 1: configuração e teclado numérico
│   │       ├── countdown_view.py# Tela 2: contagem regressiva e Play/Pause
│   │       └── app_window.py    # Controlador principal e loop time.monotonic()
│   ├── scripts/
│   │   ├── win/                 # desligar.bat, reiniciar.bat, logoff.bat
│   │   └── linux/               # desligar.sh, reiniciar.sh, logoff.sh
│   └── tests/                   # Suíte de testes automatizados (unittest)
│       ├── test_time_utils.py
│       ├── test_os_executor.py
│       └── test_app_flow.py
├── Project/                     # Documentação de produto e arquitetura
│   ├── PRD.md
│   ├── CASOS_DE_USO.md
│   ├── ESPECIFICACAO_TECNICA.md
│   └── CONTEXTO.md
└── Skills/                      # Skills de apoio ao fluxo de desenvolvimento
```

---

## Testes Automatizados

Os testes utilizam `unittest` e `unittest.mock` para validar toda a lógica temporal, integridade de scripts (incluindo quebras de linha CRLF/LF) e fluxo da interface **sem executar comandos reais de desligamento**:

```bash
python -m unittest discover -s Code/tests -v
```

> **Regra de segurança:** nunca execute os scripts em `Code/scripts/` diretamente durante testes; utilize sempre `unittest` ou `python Code/main.py --dry-run`.

---

## Documentação Adicional

- [Product Requirements Document (PRD)](./Project/PRD.md)
- [Casos de Uso e Especificações Visuais](./Project/CASOS_DE_USO.md)
- [Especificação Técnica Detalhada](./Project/ESPECIFICACAO_TECNICA.md)
- [Contexto Contínuo do Projeto](./Project/CONTEXTO.md)

---

## Desenvolvimento

Este projeto foi desenvolvido com o auxílio do **Google Antigravity** e do modelo **Gemini 4 Hydrogen**, seguindo práticas de arquitetura modular, documentação técnica estruturada e validação por testes automatizados.
