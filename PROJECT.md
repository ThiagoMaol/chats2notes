# Projeto

## História e motivação

O chats2notes nasceu para solucionar o gargalo de copiar e colar manualmente prompts e respostas de alto valor técnico gerados durante sessões de pair-programming com agentes de linha de comando (CLI). O acúmulo de sessões não processadas gera uma "bola de neve" de conhecimento esquecido no disco. O projeto transforma esses históricos em uma base organizada de notas em Markdown sem interromper o fluxo de trabalho.

## Finalidade

Extrair de forma incremental e automatizada os turnos de diálogo de agentes de CLI (com foco inicial no Antigravity CLI e AGY IDE), filtrar ruídos operacionais e sintetizar notas técnicas estruturadas em Markdown com YAML frontmatter, integradas diretamente a Spaces do SilverBullet e Vaults do Obsidian.

## Pessoas e contexto de uso

Desenvolvedores e engenheiros de software que utilizam agentes de CLI em servidores Linux ou ambientes desktop Windows e mantêm sistemas de anotações e gestão de conhecimento pessoal (PKM) com ferramentas local-first (SilverBullet e Obsidian).

## Capacidades principais

1. **Arquitetura em Duas Etapas**:
   - **Etapa 1 (Sincronização Raw Inbox)**: O comando `chats2notes sync` copia com fidelidade integral e incremental os arquivos `transcript_full.jsonl` de cada sessão do `brain/` para `vault/inbox/<user>/<session_id>/`, servindo como fonte da verdade local e marca de referência.
   - **Etapa 2 (Curadoria e Geração de Notas)**: Processamento posterior dos arquivos brutos do inbox para síntese de notas curadas em Markdown em `vault/notas/`.
2. **Filtro de Exclusão de Workspace**: Descarta automaticamente sessões cujo workspace coincida com o próprio repositório `chats2notes` ou com diretórios configurados em `--ignore-workspace`, prevenindo auto-ingestão e loops recursivos.
3. **Leitura Incremental de Transcripts**: Monitora e extrai turnos completos de diálogo a partir de logs estruturados locais (`transcript_full.jsonl`).
4. **Gerenciamento de Checkpoint**: Rastreia a marca d'água de leitura por sessão e agente em `state.json`, garantindo zero reprocessamento ou duplicação.
5. **Formatação Otimizada para SilverBullet e Obsidian**: Gera notas com YAML frontmatter compatível com Live Queries do SilverBullet e Dataview do Obsidian.
6. **Arquitetura Pluggable via Adapters**: Suporta Antigravity CLI (ativo/MVP), AGY IDE, OpenCode, Claude Code e futuros chats web.

## Limites

1. Não é um serviço SaaS multi-inquilino nem requer autenticação web na versão 1.0 (é uma ferramenta local-first / CLI).
2. Não altera nem remove os logs originais dos agentes de CLI (operação estritamente somente leitura nas fontes).
3. Não controla a execução dos agentes externos, operando apenas sobre a persistência de suas trajetórias.
4. O diretório `vault/` e seus subdiretórios (`inbox/`, `notas/`) são privados do usuário e estritamente ignorados no versionamento Git.

## Backlog de ideias futuras

1. **Filtro por Blacklist de Sessões**: Capacidade de registrar IDs de sessões descartáveis ou confidenciais em lista de bloqueio para serem ignoradas na sincronização e extração.
2. **Deduplicação por Hash de Conteúdo**: Identificação de turnos repetidos ou comandos redundantes através de cálculo de hash criptográfico (ex: SHA-256) do conteúdo das mensagens.

## Contexto técnico

Aplicação CLI em Python puro (priorizando biblioteca padrão para máxima leveza e portabilidade multiplataforma Linux/Windows), com armazenamento de notas no sistema de arquivos local. Detalhes em `.specsfy/STACK.md`.
