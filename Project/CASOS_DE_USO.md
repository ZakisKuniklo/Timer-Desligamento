# Documento de Casos de Uso, Especificações Visuais e Fluxos de Execução — Timer-Desligamento

> **Versão:** 1.3 (Sincronizada com [PRD.md](./PRD.md) e [ESPECIFICACAO_TECNICA.md](./ESPECIFICACAO_TECNICA.md))  
> **Status:** Pronto para implementação na pasta `Code/`.

---

## 1. Visão Geral e Escopo

O **Timer-Desligamento** é um aplicativo desktop desenvolvido em **Python + Tkinter** cujo objetivo é agendar, por meio de uma contagem regressiva visual minimalista, a execução automática de uma ação de energia no computador (**Desligamento**, **Reinício** ou **Logoff**).  

Ao final da contagem regressiva, o aplicativo identifica automaticamente o sistema operacional em execução (**Windows** ou **Linux**) e dispara o script correspondente (**`.bat`** para Windows ou **`.sh`** para Linux).

### 1.1 Atores
- **Usuário Final:** Pessoa que interage com a interface gráfica para escolher a ação desejada, definir o tempo e controlar o temporizador (iniciar, pausar, retomar, cancelar).
- **Sistema Operacional (Windows / Linux):** Ambiente hospedeiro detectado pela aplicação e responsável por executar o script `.bat` ou `.sh` correspondente.

---

## 2. Especificações Visuais (Design System & Telas)

O design segue fielmente o estilo visual das duas imagens de referência fornecidas pelo usuário (tema escuro moderno inspirado no aplicativo de timer do Android/Google Relógio), adaptado para uma janela desktop fixa em `tkinter`.

### 2.1 Especificações Gerais da Janela
- **Proporção sugerida (Desktop):** Formato vertical compacto estilo cartão/widget (ex.: `380 x 640 px` ou `400 x 660 px`), centralizada na tela ao abrir.
- **Redimensionamento:** Janela não redimensionável (`resizable(False, False)`) para preservar as proporções do anel circular no `Canvas` e do teclado numérico. *(Alternativa: responsiva com escala proporcional, caso desejado).*
- **Título da janela (barra do SO):** `Timer de Desligamento`.
- **Fonte:** Família sans-serif limpa e moderna disponível em Windows e Linux (ex.: `"Segoe UI"` no Windows, `"DejaVu Sans"` / `"Ubuntu"` / `"Noto Sans"` no Linux, ou fallback automático do Tkinter).

### 2.2 Paleta de Cores

| Elemento | Cor (Hex) | Aplicação |
| :--- | :--- | :--- |
| Fundo — Tela de Configuração | `#000000` | Fundo principal da tela inicial (conforme Print 2) |
| Fundo — Tela de Contagem Ativa | `#1F242D` | Fundo principal da tela do timer rodando (conforme Print 1) |
| Superfície de Botões / Pills | `#24262B` | Botões rápidos (`1min`, `5min`, `10min`, `15min`), botão `Iniciar` e seletor de ação |
| Superfície Hover / Pressionado | `#33363D` | Feedback visual ao passar o mouse ou clicar |
| Dígitos Inativos (`00 00 00`) | `#6E7175` | Cor dos zeros iniciais antes da digitação (Print 2) |
| Texto Principal / Dígitos Ativos | `#FFFFFF` | Dígitos preenchidos, teclado numérico, rótulos e título |
| Texto Secundário / Rótulos | `#D0D3D8` | Rótulos `Horas`, `Minutos`, `Segundos` |
| Destaque / Anel de Progresso | `#1A73E8` | Anel circular azul da contagem regressiva (Print 1) |
| Trilha do Anel (Fundo do Círculo) | `#2C323E` | Fundo sutil atrás do arco azul à medida que o progresso diminui |
| Cor de Alerta / Ação Crítica | `#E53935` | Feedback de erro ou destaque opcional para ação de Desligamento |

---

### 2.3 Tela 1 — Configuração do Timer (Baseada na Print 2)

Disposição vertical de cima para baixo:

1. **Visor de Tempo (`HH MM SS`)**
   - Três blocos numéricos de 2 dígitos lado a lado em fonte grande (aprox. `44–52 pt`):
     - `00` — rótulo inferior: `Horas`
     - `00` — rótulo inferior: `Minutos`
     - `00` — rótulo inferior: `Segundos`
   - **Cor dinâmica:** Quando todo o valor for `00 00 00`, os dígitos ficam em cinza (`#6E7175`). Assim que o usuário insere valores, os dígitos preenchidos (ou todo o visor ativo) ficam em branco (`#FFFFFF`).
2. **Botões de Atalho Rápido (Presets)**
   - Quatro botões em formato pílula arredondada lado a lado:
     - `1min` | `5min` | `10min` | `15min`
   - Fundo `#24262B`, texto branco, bordas totalmente arredondadas (desenhados via `Canvas` ou `Frame` estilizado).
3. **Seletor de Comando / Ação de Energia (Barra Segmentada)**
   - Posicionado logo **acima do botão `Iniciar`**.
   - Três segmentos em formato pílula contígua: **Desligar** | **Reiniciar** | **Logoff**.
   - Fundo base `#24262B`, segmento ativo destacado em `#1A73E8` com texto branco (`#FFFFFF`) e opção padrão inicial **Desligar**.
4. **Botão Principal (`Iniciar`)**
   - Botão largo em formato pílula ocupando a largura útil da tela, com o texto centralizado `Iniciar`.
   - **Estado desabilitado (tempo = 0):** Fundo `#24262B`, texto atenuado (clique não inicia contagem e exibe feedback discreto).
   - **Estado habilitado (tempo > 0):** Fundo `#24262B` com realce ao hover (ou destaque azul `#1A73E8`), texto branco nítido.
5. **Teclado Numérico Virtual (Grade 3x4)**
   - Botões limpos sem borda visível (estilo flat sobre fundo `#000000`, com leve realce circular no hover/clique):
     ```text
     1     2     3
     4     5     6
     7     8     9
     00    0     ⌫
     ```
   - O ícone `⌫` segue o desenho de seta para a esquerda com `x` interno, conforme a Print 2.

---

### 2.4 Tela 2 — Contagem Regressiva Ativa (Baseada na Print 1)

Exibida imediatamente após clicar em `Iniciar`:

1. **Cabeçalho Superior**
   - **Esquerda:** Título descritivo em branco (ex.: `Timer de 5min • Desligar` ou `Desligar em 5min`).
   - **Direita:** Ícone `X` branco clicável para cancelar o timer e retornar à Tela 1.
2. **Anel Circular de Progresso (Centro)**
   - Desenhado com `tkinter.Canvas` com suavização visual.
   - Traço espesso (`width` ~ `10–12 px`) em azul vibrante (`#1A73E8`) sobre uma trilha discreta (`#2C323E`).
   - O arco inicia em 360° (círculo completo) e reduz suavemente no sentido anti-horário/horário conforme o tempo restante (`proporcao = restante / total`).
3. **Contador Numérico Interno**
   - Centralizado dentro do círculo, em fonte branca leve/fina (`38–46 pt`).
   - **Formato:**
     - Se tempo restante `< 1 hora`: `MM:SS` (ex.: `05:00`, conforme Print 1).
     - Se tempo restante `>= 1 hora`: `HH:MM:SS` (ex.: `01:30:00`).
4. **Botão Play / Pause Interno**
   - Posicionado centralmente logo abaixo dos dígitos, dentro do anel circular.
   - **Timer em execução:** Exibe ícone branco de **Pause** (`⏸`).
   - **Timer pausado:** Exibe ícone branco de **Play** (`▶`), exatamente como ilustrado na Print 1.

---

## 3. Catálogo Completo de Casos de Uso

### UC01 — Inicialização e Detecção do Sistema Operacional
- **Ator:** Usuário / Sistema.
- **Pré-condição:** Python 3 com `tkinter` instalado e diretório de scripts acessível.
- **Fluxo Principal:**
  1. O usuário executa o aplicativo Python.
  2. O sistema identifica o SO atual (`platform.system()` -> `"Windows"` ou `"Linux"`).
  3. O sistema verifica a disponibilidade dos scripts necessários (`.bat` no Windows, `.sh` no Linux).
  4. A janela abre exibindo a **Tela 1 (Configuração)** com o visor zerado (`00 00 00`) e a ação padrão pré-selecionada (**Desligar**).
- **Fluxo de Exceção:**
  - **E1 (SO não suportado):** Se não for Windows nem Linux (ex.: macOS/Darwin), o aplicativo exibe um alerta claro informando que apenas Windows e Linux são suportados, desabilitando o disparo de execução.
  - **E2 (Scripts ausentes):** Se a pasta/arquivos `.bat` ou `.sh` esperados não forem encontrados, exibe aviso na interface antes mesmo de iniciar o timer.

---

### UC02 — Definir Tempo via Teclado Numérico (Virtual e Físico)
- **Ator:** Usuário.
- **Pré-condição:** Aplicativo na Tela 1 (Configuração).
- **Fluxo Principal (Entrada Deslizante da Direita para a Esquerda):**
  1. O usuário clica nos botões `0`–`9` ou `00` do teclado virtual (ou digita números no teclado físico).
  2. Os dígitos entram pela extremidade direita (`Segundos`) e empurram os dígitos anteriores para a esquerda (`Segundos` -> `Minutos` -> `Horas`), mantendo no máximo 6 dígitos (`HHMMSS`).
     - *Exemplo:* Digitar `5`, `0`, `0` resulta em `00` `05` `00` (5 minutos).
     - *Exemplo:* Digitar `1`, `3`, `0`, `0`, `0` resulta em `01` `30` `00` (1 hora e 30 minutos).
  3. O usuário clica em `⌫` (ou tecla `Backspace` no teclado físico) para apagar o último dígito inserido, deslocando os demais para a direita e preenchendo a esquerda com `0`.
  4. Quando o valor total em segundos é maior que `0`, o botão `Iniciar` passa ao estado ativo.
- **Fluxos Alternativos:**
  - **A1 (Limite de dígitos):** Se os 6 dígitos já estiverem ocupados (ex.: primeiro dígito > 0), novos dígitos são ignorados até o usuário apagar com `⌫`.
  - **A2 (Normalização de minutos/segundos >= 60):** Caso o usuário digite `90` em segundos (ex.: `00 00 90`), o aplicativo pode converter para `00 01 30` ao clicar em `Iniciar` (calculando `total_segundos = H*3600 + M*60 + S`) — garantindo que qualquer combinação numérica digitada funcione sem travar a digitação.
  - **A3 (Atalho `Enter` e `Esc`):** Pressionar `Enter` no teclado físico com tempo > 0 aciona `Iniciar`; pressionar `Esc` na Tela 1 limpa o visor para `00 00 00`.

---

### UC03 — Definir Tempo via Botões Rápidos (Presets)
- **Ator:** Usuário.
- **Pré-condição:** Aplicativo na Tela 1 (Configuração).
- **Fluxo Principal:**
  1. O usuário clica em um dos botões rápidos: `1min`, `5min`, `10min` ou `15min`.
  2. O sistema preenche o visor com o tempo correspondente (ex.: `5min` -> `00 05 00`) sem iniciar o timer automaticamente.
  3. O botão `Iniciar` fica habilitado para o usuário confirmar e iniciar a contagem.

---

### UC04 — Selecionar Comando de Energia
- **Ator:** Usuário.
- **Pré-condição:** Aplicativo na Tela 1 (Configuração).
- **Fluxo Principal:**
  1. O usuário visualiza a barra segmentada acima do botão `Iniciar` com as três opções: **Desligar**, **Reiniciar** e **Logoff**.
  2. O usuário clica na opção desejada.
  3. A interface destaca visualmente o segmento selecionado em azul (`#1A73E8`) e armazena a escolha no estado da aplicação para ser usada ao término do timer.
- **Fluxo Alternativo:**
  - Caso o usuário não clique em nenhuma opção, permanece selecionada a opção padrão inicial (**Desligar**).

---

### UC05 — Iniciar Contagem Regressiva
- **Ator:** Usuário.
- **Pré-condição:** Ação selecionada e tempo definido maior que `00:00:00`.
- **Fluxo Principal:**
  1. O usuário clica no botão `Iniciar`.
  2. O sistema valida se o tempo total em segundos é `> 0`.
  3. O sistema converte o tempo para total de segundos (normalizando valores como `90s` para `01:30`).
  4. A janela alterna da **Tela 1** para a **Tela 2 (Contagem Regressiva Ativa)**.
  5. O título superior exibe a referência do timer/ação (ex.: `Timer de 5min` ou `Desligar • 05:00`), o anel azul aparece completo (360°) e a contagem regressiva inicia imediatamente (ícone interno `⏸`).
- **Fluxo de Exceção:**
  - **E1 (Tempo zero):** Se o usuário tentar iniciar com `00 00 00`, a contagem não inicia; exibe um feedback visual discreto (ex.: tremor/destaque no visor ou mensagem informando para definir um tempo maior que zero).

---

### UC06 — Pausar e Retomar Contagem Regressiva
- **Ator:** Usuário.
- **Pré-condição:** Aplicativo na Tela 2 (Contagem Regressiva Ativa).
- **Fluxo Principal (Pausar):**
  1. Durante a execução, o usuário clica no botão `⏸` dentro do anel circular (ou pressiona `Espaço` no teclado físico).
  2. O timer congela o tempo restante exato e o arco azul permanece parado na posição atual.
  3. O ícone interno alterna para `▶` (conforme Print 1).
- **Fluxo Principal (Retomar):**
  1. Com o timer pausado, o usuário clica no botão `▶` (ou pressiona `Espaço` no teclado físico).
  2. A contagem regressiva retoma a partir do tempo restante salvo, recalculando o timestamp de término para manter precisão.
  3. O ícone interno retorna para `⏸`.

---

### UC07 — Cancelar Timer em Andamento (`X`)
- **Ator:** Usuário.
- **Pré-condição:** Aplicativo na Tela 2 (Contagem Regressiva Ativa).
- **Fluxo Principal:**
  1. O usuário clica no botão `X` no canto superior direito da Tela 2 (ou pressiona `Esc` no teclado físico).
  2. O loop da contagem regressiva (`after`) é imediatamente cancelado, garantindo que nenhum comando de desligamento/reinício/logoff seja disparado.
  3. O aplicativo retorna para a **Tela 1 (Configuração)** preservando o último tempo e a ação selecionados para permitir ajuste ou reinício imediato.

---

### UC08 — Execução da Ação ao Zerar o Timer (Windows — `.bat`)
- **Ator:** Sistema.
- **Pré-condição:** SO detectado como `Windows`, contagem regressiva chega a `00:00`.
- **Fluxo Principal:**
  1. O tempo restante atinge `0` e o anel de progresso chega a 0%.
  2. O aplicativo resolve o caminho do script `.bat` separado correspondente à ação selecionada:
     - **Desligar (`desligar.bat`):** executa `shutdown /s /f /t 0`.
     - **Reiniciar (`reiniciar.bat`):** executa `shutdown /r /f /t 0`.
     - **Logoff (`logoff.bat`):** executa `shutdown /l`.
  3. O aplicativo invoca o script `.bat` imediatamente via `subprocess` (utilizando `CREATE_NO_WINDOW` para não abrir janela preta de console).
  4. O comando é entregue ao Windows e o aplicativo encerra após o disparo bem-sucedido.
- **Fluxo de Exceção:**
  - **E1 (Arquivo `.bat` não encontrado):** Exibe caixa de diálogo de erro detalhando o caminho esperado e retorna ao estado seguro sem fechar abruptamente.
  - **E2 (Código de retorno != 0):** Exibe mensagem com o código de erro e `stderr` retornado pelo script.

---

### UC09 — Execução da Ação ao Zerar o Timer (Linux — `.sh`)
- **Ator:** Sistema.
- **Pré-condição:** SO detectado como `Linux`, contagem regressiva chega a `00:00`.
- **Fluxo Principal:**
  1. O tempo restante atinge `0` e o anel de progresso chega a 0%.
  2. O aplicativo resolve o caminho do script `.sh` separado correspondente à ação selecionada:
     - **Desligar (`desligar.sh`):** `systemctl poweroff` (com fallback para `shutdown -h now` / `poweroff`).
     - **Reiniciar (`reiniciar.sh`):** `systemctl reboot` (com fallback para `shutdown -r now` / `reboot`).
     - **Logoff (`logoff.sh`):** Encerramento da sessão do usuário atual (`loginctl terminate-session "$XDG_SESSION_ID"` ou `loginctl terminate-user "$USER"`).
  3. O aplicativo invoca o `.sh` imediatamente via `subprocess` (`bash <caminho_do_script>`), garantindo funcionamento mesmo se o bit `+x` não tiver sido preservado no filesystem.
  4. O comando é entregue ao Linux e o aplicativo encerra após o disparo bem-sucedido.
- **Fluxo de Exceção:**
  - **E1 (Permissão negada / necessita privilégios root):** Se o sistema exigir `sudo`/polkit e falhar sem terminal interativo, exibe mensagem clara ao usuário explicando o erro retornado.
  - **E2 (Arquivo `.sh` não encontrado ou sem permissão):** Exibe diálogo de erro detalhado e interrompe o disparo com segurança.

---

### UC10 — Tratamento de Erros e Exceções Gerais
- **Ator:** Sistema / Usuário.
- **Cenários cobertos:**
  1. **Fechamento da janela pelo `X` do sistema operacional:** Cancela qualquer callback `after` agendado antes de destruir a janela (`WM_DELETE_WINDOW`), evitando erros de callback órfão e garantindo que nenhum script seja executado após fechar o app.
  2. **Arquivo `.bat`/`.sh` corrompido ou falha de permissão:** Captura exceções (`FileNotFoundError`, `PermissionError`, `subprocess.SubprocessError`, `OSError`) e apresenta mensagem amigável via `tkinter.messagebox.showerror`.
  3. **Drift de tempo no loop Tkinter:** Caso o sistema operacional hiberne ou o Tkinter atrase um frame, o cálculo baseado em `time.monotonic()` garante que o tempo real decorrido seja respeitado.
  4. **Modo de simulação segura (`--dry-run`):** Quando iniciado com `--dry-run`, o aplicativo executa todo o fluxo visual e a validação dos caminhos de script, exibindo aviso informativo com o comando que seria executado sem disparar a ação real de energia no SO.

---

### UC11 — Execução Imediata ao Zerar (Sem Janela de Carência Extra)
- **Ator:** Usuário / Sistema.
- **Descrição:** Conforme alinhado com o usuário, ao atingir `00:00` não haverá janela adicional de carência/confirmação; o cancelamento pode ser feito a qualquer momento antes do término clicando no botão `X` da Tela 2 (UC07).

---

## 4. Fluxos de Execução e Arquitetura Lógica

### 4.1 Máquina de Estados da Aplicação

```text
[INÍCIO]
   │
   ▼
┌─────────────────────┐
│   CONFIGURACAO      │◄───────────────────────────┐
│  - Define tempo     │                            │
│  - Escolhe ação     │                            │
└─────────┬───────────┘                            │
          │ Clicar "Iniciar" (tempo > 0)           │ Clicar "X" (cancelar)
          ▼                                        │ (se configurado para voltar)
┌─────────────────────┐      Clicar "⏸"      ┌─────┴───────────────┐
│     EXECUTANDO      │─────────────────────►│       PAUSADO       │
│  - Anel diminui     │◄─────────────────────│  - Anel congelado   │
│  - Decrementa tempo │      Clicar "▶"      │  - Exibe ícone ▶    │
└─────────┬───────────┘                      └─────────────────────┘
          │ Tempo restante == 0
          ▼
┌─────────────────────┐
│  DETECTAR SO &      │
│  EXECUTAR SCRIPT    │
│  - Win  -> .bat     │
│  - Linux -> .sh     │
└─────────┬───────────┘
          │
     ┌────┴────┐
     ▼         ▼
 [SUCESSO]  [ERRO]
  Executa   Exibe alerta
  ação SO   na interface
```

### 4.2 Fluxo de Temporização (Sem Travar a Interface Tkinter)
Para manter a interface responsiva e o anel de progresso fluido (ex.: atualização a cada `50ms` ou `100ms` para o arco e atualização exata a cada segundo no texto):
1. Ao iniciar (ou retomar), calcula-se `end_time = time.monotonic() + remaining_seconds`.
2. Um método `_tick()` agenda-se via `root.after(50, self._tick)`.
3. A cada tick:
   - `remaining = max(0.0, end_time - time.monotonic())`
   - Atualiza o ângulo do arco no `Canvas`: `extent = 360.0 * (remaining / total_seconds)`
   - Atualiza o texto do contador (`math.ceil(remaining)` formatado em `MM:SS` ou `HH:MM:SS`) para evitar pular segundos.
   - Quando `remaining <= 0.0`: para o loop, garante arco em `0`, texto em `00:00` e aciona o executor de SO.

### 4.3 Fluxo de Detecção de SO e Disparo de Script

```text
detect_os()
  ├── platform.system() == "Windows"
  │     ├── Ação "desligar"  -> scripts/win/desligar.bat
  │     ├── Ação "reiniciar" -> scripts/win/reiniciar.bat
  │     └── Ação "logoff"    -> scripts/win/logoff.bat
  │
  ├── platform.system() == "Linux"
  │     ├── Ação "desligar"  -> scripts/linux/desligar.sh
  │     ├── Ação "reiniciar" -> scripts/linux/reiniciar.sh
  │     └── Ação "logoff"    -> scripts/linux/logoff.sh
  │
  └── Outro SO
        └── Levanta erro / exibe mensagem de SO não suportado
```

> **Nota sobre scripts `.bat` e `.sh`:** Cada ação possui seu próprio arquivo dedicado por sistema operacional (`scripts/win/{desligar,reiniciar,logoff}.bat` e `scripts/linux/{desligar,reiniciar,logoff}.sh`), com disparo imediato ao término da contagem regressiva.
