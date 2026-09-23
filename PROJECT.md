# Projeto

## História e motivação

O chats2notes nasceu para solucionar o gargalo de copiar e colar manualmente prompts e respostas de alto valor técnico gerados durante sessões de pair-programming com agentes de linha de comando (CLI). O acúmulo de sessões não processadas gera uma "bola de neve" de conhecimento esquecido no disco. O projeto transforma esses históricos em uma base organizada de notas em Markdown sem interromper o fluxo de trabalho.

## Finalidade

Extrair de forma incremental e automatizada os turnos de diálogo de agentes de CLI (com foco inicial no Antigravity CLI e AGY IDE), filtrar ruídos operacionais e sintetizar notas técnicas estruturadas em Markdown com YAML frontmatter, integradas diretamente a Spaces do SilverBullet e Vaults do Obsidian.

## Pessoas e contexto de uso

Desenvolvedores e engenheiros de software que utilizam agentes de CLI em servidores Linux ou ambientes desktop Windows e mantêm sistemas de anotações e gestão de conhecimento pessoal (PKM) com ferramentas local-first (SilverBullet e Obsidian).

## Capacidades principais

1. **Leitura Incremental de Transcripts**: Monitora e extrai turnos completos de diálogo a partir de logs estruturados locais (`transcript_full.jsonl`).
2. **Gerenciamento de Checkpoint**: Rastreia a marca d'água de leitura por sessão e agente em `checkpoint.json`, garantindo zero reprocessamento ou duplicação.
3. **Curadoria Inteligente**: Descarta ruídos triviais de terminal e sintetiza notas com título semântico, resumo, conceitos e código.
4. **Formatação Otimizada para SilverBullet e Obsidian**: Gera notas com YAML frontmatter compatível com Live Queries do SilverBullet e Dataview do Obsidian.
5. **Arquitetura Pluggable via Adapters**: Suporta Antigravity CLI (ativo/MVP), AGY IDE, OpenCode, Claude Code e futuros chats web.

## Limites

1. Não é um serviço SaaS multi-inquilino nem requer autenticação web na versão 1.0 (é uma ferramenta local-first / CLI).
2. Não altera nem remove os logs originais dos agentes de CLI (operação estritamente somente leitura nas fontes).
3. Não controla a execução dos agentes externos, operando apenas sobre a persistência de suas trajetórias.

## Contexto técnico

Aplicação CLI em Python puro (priorizando biblioteca padrão para máxima leveza e portabilidade multiplataforma Linux/Windows), com armazenamento de notas no sistema de arquivos local. Detalhes em `.specsfy/STACK.md`.
