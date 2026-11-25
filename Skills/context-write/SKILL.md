---
name: context-write
description: >-
  Use this skill ("context write") whenever the user asks to update or save
  the project context, or after significant decisions, requirement clarifications,
  architectural changes, milestones, or before ending a work session on the
  Timer-Desligamento project. It keeps Project/CONTEXTO.md accurate and
  self-contained so any model can resume work seamlessly.
---

# Context Write (`context-write`)

Esta skill define o procedimento padrão para manter o documento de contexto contínuo do projeto (`Project/CONTEXTO.md`) sempre atualizado, completo e autocontido, permitindo que qualquer modelo ou sessão futura retome o projeto do ponto exato em que parou.

## Quando Executar

Acione esta skill:
1. Sempre que o usuário solicitar explicitamente ("context write", "atualize o contexto", "registre o progresso", etc.).
2. Ao final de discussões em que requisitos, decisões visuais ou arquiteturais forem definidos ou alterados.
3. Após concluir uma etapa de implementação, correção de bug relevante ou criação de novos arquivos em `Code/` ou `Project/`.

## Procedimento

1. **Ler o estado atual do contexto:**
   - Leia [Project/CONTEXTO.md](../../Project/CONTEXTO.md) na íntegra para preservar o histórico anterior e evitar perda ou duplicação de informações.
2. **Coletar as novidades da sessão atual:**
   - Identifique todas as novas decisões tomadas pelo usuário (respostas a perguntas, mudanças de escopo, ajustes visuais ou de comportamento).
   - Liste arquivos criados, modificados ou removidos (especialmente em `Code/`, `Project/` e `Skills/`).
   - Registre resultados de testes/execuções realizadas (comandos executados e status observado).
   - Atualize a lista de pendências / decisões em aberto (removendo itens já resolvidos e movendo-os para decisões consolidadas).
3. **Atualizar `Project/CONTEXTO.md`:**
   - Mantenha a estrutura padronizada do arquivo:
     - **Visão Geral e Stack** (atualizar somente se houver mudança).
     - **Estrutura de Diretórios** (refletir novos arquivos relevantes).
     - **Requisitos e Decisões Consolidadas** (adicionar novas definições com clareza e sem ambiguidades).
     - **Decisões em Aberto** (manter apenas o que ainda precisa de resposta).
     - **Histórico de Sessões / Conversas** (adicionar nova entrada datada em ordem cronológica ou atualizar a sessão atual com resumo objetivo, artefatos afetados e **Próximo passo** acionável).
   - **Regra de fidelidade:** Nunca invente testes aprovados, arquivos inexistentes ou comportamentos não verificados. Registre apenas fatos diretamente observados ou explicitamente decididos pelo usuário.
4. **Sincronizar com `Project/CASOS_DE_USO.md` (se aplicável):**
   - Se a atualização envolver alteração de requisitos funcionais, fluxos ou visual, verifique se `Project/CASOS_DE_USO.md` também precisa ser atualizado ou sinalize isso nos próximos passos.
5. **Validar o resultado:**
   - Releia a seção modificada de `Project/CONTEXTO.md` para confirmar que:
     - Um modelo sem acesso ao histórico anterior consegue entender o objetivo, o estado atual do código, as decisões fechadas e exatamente o que fazer a seguir.
     - Todos os caminhos de arquivos citados existem no repositório.
