# Especificação Técnica e Fluxo de Código — Timer-Desligamento

> **Versão:** 1.1 (Sincronizada com [PRD.md](./PRD.md))  
> **Documentos Relacionados:** [PRD.md](./PRD.md) | [CONTEXTO.md](./CONTEXTO.md) | [CASOS_DE_USO.md](./CASOS_DE_USO.md)  
> **Status:** Especificação fechada e pronta para implementação em `Code/`.

---

## 1. Tecnologias e Dependências

O projeto utiliza **exclusivamente a biblioteca padrão do Python 3** (recomendado Python **3.10+**, mantendo compatibilidade com **3.8+** via `from __future__ import annotations`), sem dependências externas (`pip` não é necessário).

### 1.1 Módulos e Recursos Utilizados

| Camada | Tecnologia / Módulo | Finalidade no Projeto |
| :--- | :--- | :--- |
| Interface Gráfica | `tkinter`, `tkinter.font`, `tkinter.messagebox` | Janela desktop fixa, telas de configuração e contagem regressiva, alertas de erro/simulação. |
| Componentes Visuais | `tkinter.Canvas` | Botões em pílula (`PillButton`), barra segmentada (`SegmentedSelector`), teclado flat (`KeypadButton`), anel circular de progresso (`CircularProgressRing`) e ícones vetoriais (`⌫`, `⏸`, `▶`, `✕`). |
| Temporização | `time.monotonic()`, `math.ceil()`, `tk.Tk.after()` | Contagem regressiva resistente a *drift* ou suspensão do SO, com loop assíncrono não bloqueante a cada `50 ms`. |
| Detecção de SO e Caminhos | `platform.system()`, `pathlib.Path`, `sys` | Identificação automática entre `"Windows"` e `"Linux"` e resolução segura do diretório `scripts/` relativa ao código-fonte. |
| Execução de Scripts | `subprocess.run()`, `subprocess.CREATE_NO_WINDOW` (Windows) | Execução imediata de `.bat` (sem janela de console) ou `bash <script.sh>` no Linux, capturando `returncode`, `stdout` e `stderr`. |
| CLI e Diagnóstico | `argparse`, `logging` | Suporte à flag `--dry-run` e `--verbose` para validação segura sem desligar a máquina. |
| Tipagem e Modelos | `dataclasses`, `enum`, `typing` | Contratos explícitos para ações de energia, estados do timer, sistemas operacionais e resultados de execução. |
| Scripts de Sistema | Windows Batch (`.bat`) / Bash (`.sh`) | Comandos nativos `shutdown` (Windows) e `systemctl` / `loginctl` (Linux) isolados por ação e SO. |
| Testes Automatizados | `unittest`, `unittest.mock` | Cobertura unitária da lógica de tempo, resolução/execução com *mocks* e máquina de estados sem risco de desligamento real. |

### 1.2 Decisões Técnicas de Portabilidade (Windows e Linux)

1. **Ícones vetoriais no `Canvas`:** Em vez de depender de caracteres Unicode (`⌫`, `⏸`, `▶`, `✕`) que variam ou falham em fontes Linux/Windows, os ícones do botão backspace, play/pause e fechar (`X`) serão desenhados diretamente com primitivas vetoriais (`create_line`, `create_polygon`, `create_rectangle`) no `Canvas`.
2. **Suavidade do anel circular:** O `Canvas` do `tkinter` usa `create_arc(..., style=tk.ARC, start=90, extent=...)` para a trilha de fundo (`359.9°` para círculo fechado) e para o arco azul de progresso (`extent` negativo para reduzir no sentido horário a partir do topo, ou positivo conforme referência — padrão: iniciar em `359.9°` e reduzir suavemente até `0.0°`).
3. **Resolução de fontes:** O utilitário `get_font_family()` seleciona `"Segoe UI"` no Windows e `"DejaVu Sans"` (com fallback `"TkDefaultFont"`) no Linux.
4. **Encoding e fim de linha dos scripts:**
   - Arquivos `scripts/win/*.bat`: fim de linha **CRLF** (`\r\n`) e encoding ASCII/UTF-8 sem BOM.
   - Arquivos `scripts/linux/*.sh`: fim de linha **LF** (`\n`) e encoding UTF-8 sem BOM, invocados via `bash <caminho>` (não depende do bit `+x`).

---

## 2. Arquitetura de Diretórios e Módulos (`Code/`)

```text
Code/
├── main.py                      # CLI (--dry-run, --verbose), inicialização e ponto de entrada
├── app.pyw                      # Launcher gráfico sem janela de console no Windows (delega para main.main)
├── timer_app/
│   ├── __init__.py
│   ├── config.py                # Paleta hex, dimensões, fontes, presets e rótulos PT-BR
│   ├── models.py                # Enums e dataclasses de domínio e resultado
│   ├── time_utils.py            # Funções puras de entrada HHMMSS, normalização, formatação e ângulo
│   ├── os_executor.py           # Detecção de SO, validação de scripts e execução (real ou --dry-run)
│   └── ui/
│       ├── __init__.py
│       ├── widgets.py           # Componentes customizados em Canvas e helpers de desenho
│       ├── setup_view.py        # Tela 1: Visor, presets, barra segmentada, botão Iniciar e teclado 3x4
│       ├── countdown_view.py    # Tela 2: Cabeçalho com X, anel circular, contador e Play/Pause
│       └── app_window.py        # Classe principal TimerShutdownApp (orquestrador + loop after)
├── scripts/
│   ├── win/
│   │   ├── desligar.bat
│   │   ├── reiniciar.bat
│   │   └── logoff.bat
│   └── linux/
│       ├── desligar.sh
│       ├── reiniciar.sh
│       └── logoff.sh
└── tests/
    ├── __init__.py
    ├── test_time_utils.py
    ├── test_os_executor.py
    └── test_app_flow.py
```

---

## 3. Especificação de Modelos, Constantes e Funções por Módulo

### 3.1 `Code/timer_app/models.py`

Define os tipos centrais compartilhados entre UI, lógica de tempo e executor de SO:

```python
class PowerAction(str, Enum):
    DESLIGAR = "desligar"
    REINICIAR = "reiniciar"
    LOGOFF = "logoff"

class OperatingSystem(str, Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    UNSUPPORTED = "Unsupported"

class AppScreen(str, Enum):
    SETUP = "setup"
    COUNTDOWN = "countdown"

class TimerState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"

@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    os_type: OperatingSystem
    action: PowerAction
    script_path: Path | None
    command: list[str]
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    dry_run: bool = False
    error_message: str = ""
```

### 3.2 `Code/timer_app/config.py`

Centraliza constantes visuais e configurações derivadas de `CASOS_DE_USO.md`:

- **Classe `Colors`:**
  - `BG_SETUP = "#000000"`
  - `BG_COUNTDOWN = "#1F242D"`
  - `SURFACE = "#24262B"`
  - `SURFACE_HOVER = "#33363D"`
  - `SURFACE_DISABLED = "#1A1C20"`
  - `DIGITS_INACTIVE = "#6E7175"`
  - `TEXT_PRIMARY = "#FFFFFF"`
  - `TEXT_SECONDARY = "#D0D3D8"`
  - `TEXT_MUTED = "#8A8E96"`
  - `ACCENT_BLUE = "#1A73E8"`
  - `ACCENT_BLUE_HOVER = "#2575FC"`
  - `RING_TRACK = "#2C323E"`
  - `ALERT_RED = "#E53935"`
- **Classe `Dimensions`:**
  - `WINDOW_WIDTH = 390`
  - `WINDOW_HEIGHT = 650`
  - `TICK_INTERVAL_MS = 50`
  - `RING_SIZE = 270`
  - `RING_STROKE = 11`
- **Constantes de domínio:**
  - `PRESETS_MINUTES: tuple[int, ...] = (1, 5, 10, 15)`
  - `ACTION_LABELS: dict[PowerAction, str] = {DESLIGAR: "Desligar", REINICIAR: "Reiniciar", LOGOFF: "Logoff"}`
  - `SCRIPT_FILENAMES: dict[OperatingSystem, dict[PowerAction, str]]`
- **Função `get_font_family(os_type: OperatingSystem) -> str`:**
  - Retorna `"Segoe UI"` se `os_type == OperatingSystem.WINDOWS`, `"DejaVu Sans"` se `os_type == OperatingSystem.LINUX`, ou `"TkDefaultFont"` caso contrário.

### 3.3 `Code/timer_app/time_utils.py`

Módulo 100% puro (sem dependência de `tkinter` ou SO):

| Função | Assinatura | Responsabilidade |
| :--- | :--- | :--- |
| `push_digit` | `(digits: str, token: str) -> str` | Recebe string de 6 dígitos (ex.: `"000000"`) e token (`"0"`–`"9"` ou `"00"`). Desloca para a esquerda mantendo até 6 dígitos. Ignora se o buffer não tiver espaço suficiente para o token (`digits[0] != "0"` para 1 dígito; `digits[:2] != "00"` para `"00"`). |
| `pop_digit` | `(digits: str) -> str` | Remove o dígito mais à direita e preenche `"0"` à esquerda (`"0" + digits[:-1]`). |
| `preset_to_digits` | `(minutes: int) -> str` | Converte um preset em minutos (ex.: `5`) para string de 6 dígitos `HHMMSS` (ex.: `"000500"`). |
| `digits_to_hms` | `(digits: str) -> tuple[int, int, int]` | Fatia os 6 dígitos em `(horas, minutos, segundos)` sem alterar o visor durante a digitação. |
| `digits_to_total_seconds` | `(digits: str) -> int` | Calcula `horas * 3600 + minutos * 60 + segundos` (normalizando automaticamente casos como `00 00 90` -> `90` segundos). |
| `seconds_to_digits` | `(total_seconds: int) -> str` | Converte segundos totais normalizados em `HHMMSS` (limitado a `99:59:59` se necessário). |
| `format_countdown` | `(remaining_seconds: float) -> str` | Converte `ceil_sec = max(0, math.ceil(remaining_seconds))`. Se `< 3600`, retorna `"MM:SS"`; se `>= 3600`, retorna `"HH:MM:SS"`. |
| `format_header_title` | `(action: PowerAction, total_seconds: int) -> str` | Formata o cabeçalho da Tela 2, ex.: `"Desligar • 05:00"` ou `"Reiniciar • 01:30:00"`. |
| `calculate_progress_extent` | `(remaining_seconds: float, total_seconds: int) -> float` | Retorna ângulo proporcional entre `0.0` e `359.9`: se `total_seconds <= 0` ou `remaining <= 0`, retorna `0.0`; senão `min(359.9, 359.9 * (remaining_seconds / total_seconds))`. |

### 3.4 `Code/timer_app/os_executor.py`

Responsável por detectar o SO, validar e invocar os scripts `.bat` e `.sh`:

| Função | Assinatura | Responsabilidade |
| :--- | :--- | :--- |
| `detect_os` | `() -> OperatingSystem` | Chama `platform.system()`. `"Windows"` -> `OperatingSystem.WINDOWS`; `"Linux"` -> `OperatingSystem.LINUX`; qualquer outro -> `OperatingSystem.UNSUPPORTED`. |
| `get_scripts_base_dir` | `() -> Path` | Resolve `Path(__file__).resolve().parent.parent.parent / "scripts"` (compatível com execução a partir de qualquer CWD e testável via injeção de `base_dir`). |
| `resolve_script_path` | `(action: PowerAction, os_type: OperatingSystem, base_dir: Path \| None = None) -> Path` | Mapeia `(os_type, action)` para `win/{desligar,reiniciar,logoff}.bat` ou `linux/{desligar,reiniciar,logoff}.sh`. Levanta `ValueError` se `os_type == UNSUPPORTED`. |
| `validate_scripts` | `(os_type: OperatingSystem, base_dir: Path \| None = None) -> list[Path]` | Verifica a existência (`is_file()`) dos 3 scripts do SO atual na inicialização e retorna lista com os caminhos ausentes (lista vazia = tudo OK). |
| `build_command` | `(script_path: Path, os_type: OperatingSystem) -> list[str]` | Windows: `[str(script_path)]`; Linux: `["bash", str(script_path)]`. |
| `execute_power_action` | `(action: PowerAction, os_type: OperatingSystem \| None = None, dry_run: bool = False, base_dir: Path \| None = None) -> ExecutionResult` | Valida SO e arquivo. Se `dry_run=True`, **não executa** `subprocess.run()`, registra log e retorna `ExecutionResult(success=True, dry_run=True, ...)`. Em execução real, chama `subprocess.run(cmd, capture_output=True, text=True, check=False, creationflags=...)` (usando `getattr(subprocess, "CREATE_NO_WINDOW", 0)` no Windows) e encapsula exceções (`FileNotFoundError`, `PermissionError`, `OSError`, `subprocess.SubprocessError`). |

### 3.5 `Code/timer_app/ui/widgets.py`

Componentes visuais desenhados em `tkinter.Canvas` para atingir fidelidade total ao tema escuro:

- **`draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs) -> int`**: Desenha retângulo com cantos arredondados suaves (`smooth=True` via polígono). Usado para pílulas (`radius = height // 2`) e barra segmentada.
- **`PillButton(tk.Canvas)`**:
  - Métodos: `__init__(parent, text, command, width, height, bg_color, hover_color, text_color, disabled_bg, disabled_fg, font)`, `set_enabled(enabled: bool)`, `set_colors(bg, hover, fg)`, `_on_enter`, `_on_leave`, `_on_click`, `_redraw()`.
- **`SegmentedSelector(tk.Canvas)`**:
  - Renderiza os 3 segmentos contíguos (`Desligar | Reiniciar | Logoff`) dentro de um container pílula `#24262B`, destacando a opção selecionada em `#1A73E8`.
  - Métodos: `__init__(parent, options: list[tuple[PowerAction, str]], initial: PowerAction, on_change: Callable[[PowerAction], None], width, height, font)`, `set_selected(action: PowerAction)`, `get_selected() -> PowerAction`, `_on_click(event)`, `_on_motion(event)`, `_redraw()`.
- **`KeypadButton(tk.Canvas)`**:
  - Botão circular/flat para dígitos (`0`–`9`, `00`) e ícone vetorial `backspace` (`icon_type="backspace"`).
  - Ao passar o mouse ou clicar, exibe círculo sutil (`#24262B` / `#33363D`) sobre o fundo `#000000`.
- **`CircularProgressRing(tk.Canvas)`**:
  - Desenha o anel de fundo (`RING_TRACK`), o arco de progresso (`ACCENT_BLUE`), o contador central (`MM:SS` ou `HH:MM:SS`) e o botão interno clicável de Play/Pause vetorial (`⏸` / `▶`).
  - Métodos: `__init__(parent, size, stroke_width, font_time, on_toggle_pause)`, `set_state(time_text: str, extent: float, is_paused: bool)`, `_draw_toggle_icon(is_paused: bool)`, `_on_canvas_click(event)`.

### 3.6 `Code/timer_app/ui/setup_view.py`

Implementa a **Tela 1 (Configuração)** herdando de `tk.Frame(bg=Colors.BG_SETUP)`:

- **Atributos visuais:** Labels de pares de dígitos (`lbl_hours`, `lbl_minutes`, `lbl_seconds`) + rótulos (`Horas`, `Minutos`, `Segundos`), fileira de 4 `PillButton` (`1min`, `5min`, `10min`, `15min`), `SegmentedSelector`, `PillButton` principal `Iniciar`, grade `3x4` de `KeypadButton`.
- **Métodos principais:**
  - `update_digits(digits: str) -> None`: Atualiza os três blocos (`HH`, `MM`, `SS`) e alterna a cor entre `DIGITS_INACTIVE` (`"000000"`) e `TEXT_PRIMARY` (`!= "000000"`).
  - `set_selected_action(action: PowerAction) -> None`: Sincroniza a barra segmentada.
  - `set_start_enabled(enabled: bool) -> None`: Atualiza o visual do botão `Iniciar`.
  - `flash_zero_warning() -> None`: Pisca brevemente os dígitos do visor em `ALERT_RED` por `300 ms` caso o usuário clique em `Iniciar` com `00 00 00`.

### 3.7 `Code/timer_app/ui/countdown_view.py`

Implementa a **Tela 2 (Contagem Regressiva Ativa)** herdando de `tk.Frame(bg=Colors.BG_COUNTDOWN)`:

- **Cabeçalho:** Frame superior com `lbl_title` à esquerda (`"Desligar • 05:00"`) e `Canvas` de ícone vetorial `X` (`btn_cancel`) à direita (`36 x 36 px`) com hover circular.
- **Centro:** Instância de `CircularProgressRing`.
- **Métodos principais:**
  - `configure_timer(title: str, initial_time_text: str) -> None`: Define título, arco inicial em `359.9°`, estado `is_paused=False` (`⏸`).
  - `update_progress(time_text: str, extent: float, is_paused: bool) -> None`: Atualiza arco, texto central e ícone interno.

### 3.8 `Code/timer_app/ui/app_window.py`

Orquestrador principal `TimerShutdownApp`:

- **Estado interno:**
  - `self.os_type: OperatingSystem`
  - `self.dry_run: bool`
  - `self.digits: str = "000000"`
  - `self.selected_action: PowerAction = PowerAction.DESLIGAR`
  - `self.timer_state: TimerState = TimerState.IDLE`
  - `self.total_seconds: int = 0`
  - `self.remaining_seconds: float = 0.0`
  - `self.end_monotonic: float | None = None`
  - `self._after_id: str | None = None`
- **Métodos principais:**
  - `__init__(self, root: tk.Tk, os_type: OperatingSystem, dry_run: bool = False)`
  - `run() -> None`
  - `on_digit_input(token: str) -> None`
  - `on_backspace() -> None`
  - `on_preset_selected(minutes: int) -> None`
  - `on_action_selected(action: PowerAction) -> None`
  - `on_start_clicked() -> None`
  - `on_toggle_pause() -> None`
  - `on_cancel_clicked() -> None`
  - `on_clear_digits() -> None`
  - `on_key_press(event: tk.Event) -> None`
  - `_show_screen(screen: AppScreen) -> None`
  - `_schedule_tick() -> None`
  - `_cancel_after_loop() -> None`
  - `_tick() -> None`
  - `_handle_timer_finished() -> None`
  - `on_window_close() -> None`

### 3.9 `Code/main.py`

- `parse_args(argv: list[str] | None = None) -> argparse.Namespace`: Suporta `--dry-run` (`action="store_true"`) e `--verbose` (`action="store_true"`).
- `configure_logging(verbose: bool) -> None`: Configura `logging.basicConfig(...)`.
- `main(argv: list[str] | None = None) -> int`:
  1. Faz `parse_args(argv)` e `configure_logging(args.verbose)`.
  2. Cria `root = tk.Tk()`, detecta `os_type = detect_os()`.
  3. Instancia `app = TimerShutdownApp(root, os_type=os_type, dry_run=args.dry_run)`.
  4. Inicia `app.run()` (`root.mainloop()`).

---

## 4. Fluxo de Código Detalhado por Caso de Uso

### UC01 — Inicialização e Detecção do Sistema Operacional

1. Usuário executa `python Code/main.py` (ou `python Code/main.py --dry-run`).
2. `main()` chama `detect_os()` -> `platform.system()` retorna `"Windows"` ou `"Linux"` (ou outro -> `OperatingSystem.UNSUPPORTED`).
3. `TimerShutdownApp.__init__()` configura a janela (`390x650`, `resizable(False, False)`, centralizada via `update_idletasks()` + `geometry()`, comportamento padrão do SO sem `always-on-top` e sem sons, protocolo `WM_DELETE_WINDOW -> on_window_close`).
   - *Launcher Windows:* `Code/app.pyw` importa `main` de `main.py` e executa `raise SystemExit(main())` para abrir via `pythonw` sem janela de console.
4. Instancia `SetupView` e `CountdownView`, exibe `AppScreen.SETUP` com `digits="000000"`, `selected_action=PowerAction.DESLIGAR` e botão `Iniciar` visualmente atenuado (`set_start_enabled(False)`).
5. `root.after(0, self._check_environment_on_startup)` executa após abrir a janela:
   - **Se `os_type == UNSUPPORTED`:** Exibe `messagebox.showwarning` informando que apenas Windows e Linux são suportados (a menos que `dry_run=True`, onde permite testar a UI com aviso).
   - **Se `validate_scripts(os_type)` retornar caminhos ausentes:** Exibe `messagebox.showwarning` listando os scripts `.bat`/`.sh` não encontrados antes mesmo do usuário iniciar o timer.

---

### UC02 — Definir Tempo via Teclado Numérico (Virtual e Físico)

1. **Entrada por clique (virtual):** `KeypadButton` invoca `app.on_digit_input(token)` (`"0"`–`"9"` ou `"00"`) ou `app.on_backspace()`.
2. **Entrada por teclado físico:** `root.bind("<Key>", app.on_key_press)` mapeia por tela ativa:
   - Na **Tela 1 (`AppScreen.SETUP`):**
     - `event.char in "0123456789"` -> `on_digit_input(event.char)`
     - `event.keysym == "BackSpace"` -> `on_backspace()`
     - `event.keysym == "Escape"` -> `on_clear_digits()` (zera para `"000000"` e desabilita `Iniciar`)
     - `event.keysym in ("Return", "KP_Enter")` -> `on_start_clicked()`
   - Na **Tela 2 (`AppScreen.COUNTDOWN`):**
     - `event.keysym == "space"` -> `on_toggle_pause()`
     - `event.keysym == "Escape"` -> `on_cancel_clicked()`
3. **Atualização de estado:**
   - `self.digits = push_digit(self.digits, token)` (ou `pop_digit(self.digits)` no backspace).
   - `total = digits_to_total_seconds(self.digits)`
   - `setup_view.update_digits(self.digits)`
   - `setup_view.set_start_enabled(total > 0)`
4. **Regra de limite e normalização:**
   - Se todos os 6 dígitos estiverem ocupados (`digits[0] != "0"`), `push_digit()` devolve `digits` inalterado.
   - Se o usuário digitar `"000090"` (`90` segundos), o visor preserva `00 00 90` durante a digitação e `digits_to_total_seconds()` calcula `90` segundos ao iniciar.

---

### UC03 — Definir Tempo via Botões Rápidos (Presets)

1. Usuário clica em `1min`, `5min`, `10min` ou `15min` (`PillButton`).
2. Callback chama `app.on_preset_selected(minutes)`.
3. `self.digits = preset_to_digits(minutes)` (ex.: `5 -> "000500"`).
4. `setup_view.update_digits(self.digits)` atualiza o visor para `00 05 00` em branco (`#FFFFFF`).
5. `setup_view.set_start_enabled(True)` habilita o botão `Iniciar`.
6. **Importante:** O timer **não** inicia automaticamente; aguarda o clique em `Iniciar`.

---

### UC04 — Selecionar Comando de Energia

1. Usuário clica em `Desligar`, `Reiniciar` ou `Logoff` dentro de `SegmentedSelector`.
2. `SegmentedSelector._on_click()` identifica o terço clicado, atualiza destaque azul `#1A73E8` e chama `app.on_action_selected(action)`.
3. `app.on_action_selected()` atualiza `self.selected_action = action`.
4. Se o usuário não alterar a seleção, permanece o padrão `PowerAction.DESLIGAR`.

---

### UC05 — Iniciar Contagem Regressiva

1. Usuário clica em `Iniciar` (ou pressiona `Enter`).
2. `on_start_clicked()` calcula `total = digits_to_total_seconds(self.digits)`.
3. **Se `total <= 0`:** Chama `setup_view.flash_zero_warning()` e retorna sem trocar de tela.
4. **Se `total > 0`:**
   - `self.total_seconds = total`
   - `self.remaining_seconds = float(total)`
   - `self.end_monotonic = time.monotonic() + self.remaining_seconds`
   - `self.timer_state = TimerState.RUNNING`
   - Normaliza exibição opcional ou preserva `self.digits` para retorno no `X` (decisão do usuário: preservar último tempo e ação ao cancelar).
   - Chama `countdown_view.configure_timer(format_header_title(self.selected_action, total), format_countdown(total))`.
   - Alterna tela via `_show_screen(AppScreen.COUNTDOWN)`.
   - Inicia loop com `_schedule_tick()` (`self._after_id = self.root.after(Dimensions.TICK_INTERVAL_MS, self._tick)`).

---

### UC06 — Pausar e Retomar Contagem Regressiva

1. Usuário clica no botão vetorial `⏸` / `▶` dentro de `CircularProgressRing`.
2. `CircularProgressRing._on_canvas_click()` invoca `app.on_toggle_pause()`.
3. **Se `self.timer_state == TimerState.RUNNING` (Pausar):**
   - `_cancel_after_loop()` cancela `self._after_id`.
   - Recalcula exato: `self.remaining_seconds = max(0.0, self.end_monotonic - time.monotonic())`.
   - `self.end_monotonic = None`
   - `self.timer_state = TimerState.PAUSED`
   - Atualiza `countdown_view.update_progress(format_countdown(self.remaining_seconds), calculate_progress_extent(self.remaining_seconds, self.total_seconds), is_paused=True)` -> ícone vira `▶`.
4. **Se `self.timer_state == TimerState.PAUSED` (Retomar):**
   - `self.end_monotonic = time.monotonic() + self.remaining_seconds`
   - `self.timer_state = TimerState.RUNNING`
   - Atualiza ícone para `⏸` (`is_paused=False`) e chama `_schedule_tick()`.

---

### UC07 — Cancelar Timer em Andamento (`X`)

1. Usuário clica no botão `X` no canto superior direito da `CountdownView`.
2. Callback invoca `app.on_cancel_clicked()`.
3. `on_cancel_clicked()` chama `_cancel_after_loop()`.
4. Redefine `self.timer_state = TimerState.IDLE`, `self.end_monotonic = None`, `self.remaining_seconds = 0.0`.
5. **Preservação de estado (decisão consolidada):** Não zera `self.digits` nem `self.selected_action`; apenas chama `_show_screen(AppScreen.SETUP)` para retornar à Tela 1 com o último tempo e ação selecionados prontos para editar ou reiniciar.

---

### UC08 — Execução da Ação ao Zerar o Timer (Windows — `.bat`)

1. No método `_tick()`:
   - `remaining = max(0.0, self.end_monotonic - time.monotonic())`
   - `self.remaining_seconds = remaining`
   - Atualiza `countdown_view.update_progress(format_countdown(remaining), calculate_progress_extent(remaining, self.total_seconds), is_paused=False)`.
   - Se `remaining > 0.0`: agenda próximo `_tick()` com `_schedule_tick()` e retorna.
2. Quando `remaining <= 0.0`:
   - `_cancel_after_loop()`, `self.timer_state = TimerState.FINISHED`, garante `extent=0.0` e texto `"00:00"`.
   - Chama `_handle_timer_finished()`.
3. `_handle_timer_finished()` chama `result = execute_power_action(self.selected_action, os_type=self.os_type, dry_run=self.dry_run)`:
   - No Windows, `resolve_script_path()` aponta para `Code/scripts/win/{desligar,reiniciar,logoff}.bat`.
   - **Se `dry_run=True`:** Loga comando `[str(script_path)]`, exibe `messagebox.showinfo("Modo Simulação (--dry-run)", ...)` indicando qual script `.bat` seria executado e retorna à Tela 1 (ou encerra com segurança conforme fluxo de teste — padrão: retorna à Tela 1 para permitir novos testes na mesma sessão).
   - **Se `dry_run=False` e `result.success=True`:** Fecha o aplicativo imediatamente com `self.root.destroy()`.
   - **Se `result.success=False`:** Exibe `messagebox.showerror("Erro ao executar ação", result.error_message)` e retorna para a Tela 1 sem encerrar abruptamente.

---

### UC09 — Execução da Ação ao Zerar o Timer (Linux — `.sh`)

1. Segue o mesmo loop `_tick()` -> `_handle_timer_finished()` -> `execute_power_action()`.
2. No Linux, `resolve_script_path()` aponta para `Code/scripts/linux/{desligar,reiniciar,logoff}.sh`.
3. `build_command()` constrói `["bash", str(script_path)]`.
4. `subprocess.run(["bash", str(script_path)], capture_output=True, text=True, check=False)` executa o script.
5. **Tratamento de resultado:**
   - `returncode == 0`: fecha a janela (`self.root.destroy()`).
   - `returncode != 0` (ex.: erro de permissão polkit/root ou comando ausente): retorna `ExecutionResult(success=False, error_message=...)` com `returncode` e `stderr`, exibindo `messagebox.showerror(...)` e voltando à Tela 1.

---

### UC10 — Tratamento de Erros, Fechamento pelo SO e `--dry-run`

1. **`WM_DELETE_WINDOW`:** `self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)`:
   - Chama `_cancel_after_loop()` antes de `self.root.destroy()`, garantindo que nenhum `_tick()` pendente dispare após fechar a janela.
2. **Exceções de I/O e `subprocess`:**
   - `execute_power_action()` captura `ValueError` (SO não suportado), `FileNotFoundError` (script ausente), `PermissionError`, `subprocess.SubprocessError` e `OSError`, nunca deixando exceção não tratada derrubar a thread da UI.
3. **Modo `--dry-run`:**
   - Permite validar todo o ciclo (seleção de ação, contagem, troca de tela, resolução exata do caminho do `.bat`/`.sh`, validação de existência do arquivo) sem executar o comando de desligamento real no sistema operacional.

---

### UC11 — Execução Imediata ao Zerar

1. Não existe modal de confirmação ou contagem extra após `remaining <= 0.0`.
2. A proteção contra disparo acidental é feita exclusivamente antes do término via botão `X` (`UC07`), botão Pause (`UC06`) ou fechamento da janela (`UC10`).

---

## 5. Especificação Exata dos Scripts de Sistema

### 5.1 Windows (`Code/scripts/win/*.bat`, CRLF)

- **`desligar.bat`:**
  ```bat
  @echo off
  shutdown /s /f /t 0
  ```
- **`reiniciar.bat`:**
  ```bat
  @echo off
  shutdown /r /f /t 0
  ```
- **`logoff.bat`:**
  ```bat
  @echo off
  shutdown /l
  ```
  > *Nota técnica:* No Windows, o comando `shutdown /l` não aceita `/t` nem `/f` (o uso combinado retorna erro de sintaxe no `shutdown.exe`); por isso `logoff.bat` usa exclusivamente `shutdown /l`, enquanto `desligar.bat` e `reiniciar.bat` usam `/f /t 0` conforme definido pelo usuário.

### 5.2 Linux (`Code/scripts/linux/*.sh`, LF `\n`)

- **`desligar.sh`:**
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail

  if command -v systemctl >/dev/null 2>&1; then
      systemctl poweroff
  elif command -v shutdown >/dev/null 2>&1; then
      shutdown -h now
  else
      poweroff
  fi
  ```
- **`reiniciar.sh`:**
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail

  if command -v systemctl >/dev/null 2>&1; then
      systemctl reboot
  elif command -v shutdown >/dev/null 2>&1; then
      shutdown -r now
  else
      reboot
  fi
  ```
- **`logoff.sh`:**
  ```bash
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
  ```

---

## 6. Estratégia de Testes e Validação Segura

1. **Testes Unitários (`Code/tests/test_time_utils.py`):**
   - Entrada deslizante (`push_digit` com `"1"`, `"00"`, limite de 6 dígitos, `pop_digit`).
   - Presets (`preset_to_digits(5) == "000500"`).
   - Normalização (`digits_to_total_seconds("000090") == 90`).
   - Formatação (`format_countdown(59.1) == "01:00"`, `format_countdown(3600) == "01:00:00"`).
   - Ângulos (`calculate_progress_extent`).
2. **Testes do Executor (`Code/tests/test_os_executor.py`):**
   - `mock.patch("platform.system")` para `"Windows"`, `"Linux"` e `"Darwin"`.
   - Verificação de existência e conteúdo dos 6 scripts em `Code/scripts/`.
   - `execute_power_action(..., dry_run=True)` garante que `subprocess.run` **não** é chamado.
   - `mock.patch("subprocess.run")` valida exatamente os argumentos (`CREATE_NO_WINDOW` no Windows; `["bash", ...]` no Linux), sucesso (`returncode=0`) e falha (`returncode=1`, `FileNotFoundError`).
3. **Testes de Fluxo UI/Controlador (`Code/tests/test_app_flow.py`):**
   - Simulação de UC02–UC07 (iniciar, pausar, retomar, cancelar `X` preservando último tempo/ação, fechamento seguro `on_window_close`).
4. **Execução Manual Segura:**
   - `python -m unittest discover -s Code/tests -v`
   - `python Code/main.py --dry-run --verbose` (testar cliques, presets, teclado físico, pausa/retomada e término do timer sem desligar o PC).
