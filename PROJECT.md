# Projeto

## História e motivação

O chats2notes nasceu para solucionar o gargalo de copiar e colar manualmente prompts e respostas de alto valor técnico gerados durante sessões de pair-programming com agentes de linha de comando (CLI). O acúmulo de sessões não processadas gera uma "bola de neve" de conhecimento esquecido no disco. O projeto transforma esses históricos em uma base organizada de notas em Markdown sem interromper o fluxo de trabalho.

## Finalidade

Extrair de forma incremental e automatizada os turnos de diálogo de agentes de CLI (com foco inicial no Antigravity CLI e AGY IDE), filtrar ruídos operacionais e sintetizar notas técnicas estruturadas em Markdown com YAML frontmatter, integradas diretamente a Spaces do SilverBullet e Vaults do Obsidian.

## Pessoas e contexto de uso

Desenvolvedores e engenheiros de software que utilizam agentes de CLI em servidores Linux ou ambientes desktop Windows e mantêm sistemas de anotações e gestão de conhecimento pessoal (PKM) com ferramentas local-first (SilverBullet e Obsidian).

## Capacidades principais

1. **Pipeline em Três Fases**:
   - **Fase 1 (Sincronização Raw)**: O comando `chats2notes sync` copia com fidelidade integral e incremental os arquivos `transcript_full.jsonl` de cada sessão do `brain/` para `vault/raw/<user>/<session_id>/`. O diretório `vault/raw` é imutável para o processamento interno da aplicação, mas dinamicamente sincronizado com os brains externos quando um chat continuar ativo e crescer na fonte.
   - **Fase 2 (Segmentação em Pares)**: Processamento determinístico via script puro (sem IA) que segmenta cada log do `vault/raw` em pares sequenciais de `[prompt do usuário] + [resposta da LLM]` com metadados e numeração ordenada (`0001.md`, `0002.md`) e arquivos técnicos paralelos de auditoria (`0001.audit.json`). Suporta subcomando dedicado `chats2notes segment` e flag encadeada `chats2notes sync --segment`.
   - **Fase 3 (Curadoria e Geração de Notas Humanizadas)**: Síntese inteligente das notas em Markdown em `vault/notas/`, orientada pela skill `humanizer` para produzir texto direto, limpo e sem clichês de IA.
2. **Filtro de Exclusão de Workspace**: Descarta automaticamente sessões cujo workspace coincida com o próprio repositório `chats2notes` ou com diretórios configurados em `--ignore-workspace`, prevenindo auto-ingestão e loops recursivos.
3. **Leitura Incremental de Transcripts**: Monitora e extrai turnos completos de diálogo a partir de logs estruturados locais (`transcript_full.jsonl`).
4. **Gerenciamento de Checkpoint**: Rastreia a marca d'água de leitura por sessão e agente em `state.json`, garantindo zero reprocessamento ou duplicação.
5. **Formatação Otimizada para SilverBullet e Obsidian**: Gera notas com YAML frontmatter compatível com Live Queries do SilverBullet e Dataview do Obsidian.
6. **Arquitetura Pluggable via Adapters**: Suporta Antigravity CLI (ativo/MVP), AGY IDE, OpenCode, Claude Code e futuros chats web.

## Limites

1. Não é um serviço SaaS multi-inquilino nem requer autenticação web na versão 1.0 (é uma ferramenta local-first / CLI).
2. Não altera nem remove os logs originais dos agentes de CLI (operação estritamente somente leitura nas fontes).
3. Não controla a execução dos agentes externos, operando apenas sobre a persistência de suas trajetórias.
4. O diretório `vault/` e seus subdiretórios (`raw/`, `notas/`, etc.) são privados do usuário e estritamente ignorados no versionamento Git.

## Backlog de ideias futuras

1. **Filtro por Blacklist de Sessões**: Capacidade de registrar IDs de sessões descartáveis ou confidenciais em lista de bloqueio para serem ignoradas na sincronização e extração.
2. **Deduplicação por Hash de Conteúdo**: Identificação de turnos repetidos ou comandos redundantes através de cálculo de hash criptográfico (ex: SHA-256) do conteúdo das mensagens.

## Contexto técnico

Aplicação CLI em Python puro (priorizando biblioteca padrão para máxima leveza e portabilidade multiplataforma Linux/Windows), com armazenamento de notas no sistema de arquivos local. Detalhes em `.specsfy/STACK.md`.
