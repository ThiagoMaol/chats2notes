# Backlog: Extração incremental de conversas do Antigravity CLI para notas Markdown

| Metainformação | Valor |
| --- | --- |
| ID | BACKLOG-0001 |
| Status | Ready |
| Produto | chats2notes |
| Épico | Extração Incremental de Conhecimento |
| Funcionalidade | Ingestão de logs do Antigravity CLI e geração de notas Markdown |
| Tipo | Funcionalidade |
| Prioridade | Alta |
| Milestones | M01 (MVP) |
| Criado em | 2026-09-23 |
| Spec promovida | Nenhuma |

## Ideia original

Ferramenta CLI e skill que lê logs estruturados (transcript_full.jsonl) do Antigravity CLI e outros agentes, extrai turnos úteis de forma incremental com controle de checkpoint e gera notas Markdown formatadas para SilverBullet e Obsidian.

## Problema percebido

Acúmulo de históricos valiosos de pair-programming sem tempo para processar manualmente, gerando perda de conhecimento técnico e quebra de fluxo ao copiar e colar.

## Pessoa afetada ou beneficiada

Desenvolvedores e engenheiros de software que usam agentes CLI de IA e mantêm sistemas de notas local-first em SilverBullet ou Obsidian.

## Resultado ou valor esperado

Notas organizadas em Markdown com frontmatter YAML salvas automaticamente no Space do SilverBullet ou Vault do Obsidian sem duplicar registros e sem poluir o contexto da conversa ativa.

## Contexto

Ambiente local-first no Linux e Windows, utilizando biblioteca padrão do Python (zero dependências) para leitura de transcripts e controle atômico de checkpoint.json.

## Referências relacionadas

- Captura original: `specs/inbox/2026-09-23-015500-extracao-incremental-de-conversas-de-agentes-cli-para-notas-markdown.md`
- Visão e Arquitetura: `README.md`
- Contexto do Sistema: `PROJECT.md`
- Stack confirmada: `.specsfy/STACK.md`

## Comportamento esperado

1. Localizar sessões ativas do Antigravity CLI sob o diretório padrão do usuário (`~/.gemini/antigravity-cli/brain/<uuid>/`) ou através de múltiplos diretórios de perfis/usuários configurados no mesmo host.
2. Identificar a autoria do chat (`host_user`) e o diretório de projeto/contexto (`workspace`) a partir dos dados da sessão.
3. Consultar `checkpoint.json` com chave isolada por `(host_user, session_id)` para obter o último `step_index` processado.
4. Ler `transcript_full.jsonl` e extrair turnos de interação (`USER_INPUT` + `PLANNER_RESPONSE`) ocorridos após o checkpoint.
5. Gerar arquivos Markdown estruturados no diretório de destino com metadados YAML enriquecidos (`name`, `tags`, `agent`, `host_user`, `workspace`, `session`, `created`, `category`).
6. Gravar a nova marca d'água em `checkpoint.json` de forma atômica e isolada por usuário.

## Regras de negócio

- A leitura dos logs originais é estritamente somente leitura; nenhum arquivo sob `brain/` deve ser alterado ou removido.
- Se uma sessão não tiver novos passos desde o último checkpoint, ela deve ser ignorada sem gerar notas vazias.
- O formato do frontmatter gerado deve respeitar o schema compatível com Live Queries do SilverBullet (`name`, `tags`, `agent`, `host_user`, `workspace`, `session`, `created`, `category`).
- Checkpoints de diferentes usuários do mesmo host não devem colidir nem sobrescrever o progresso um do outro.

## Critérios de aceitação

- Extração completa de múltiplos turnos em sessões novas.
- Execução incremental idempotente: rodar duas vezes seguidas não duplica notas nem altera arquivos já gerados.
- Suporte a escanear sessões de múltiplos usuários do mesmo host (`--brain-dir` múltiplo ou lista configurada) preservando `host_user` em cada nota.
- Tratamento resiliente para transcripts parciais ou em andamento.
- Validação por testes automatizados em `unittest` sem necessidade de instalar pacotes externos.

## Qualidades e operação

- Segurança: Operação local-first com as permissões do usuário do sistema operacional; nenhum dado é enviado externamente sem consentimento.
- Privacidade: Preservação local dos históricos sem telemetria embutida.
- Desempenho e volume: Leitura linear de arquivos JSONL com baixa pegada de memória.
- Auditoria e observabilidade: Mensagens claras no terminal reportando quantidade de sessões descobertas, turnos extraídos e notas salvas.

## Dependências

- Python 3.10+ com biblioteca padrão instalada no sistema.
- Antigravity CLI com diretório(s) `brain/` acessíveis para leitura no sistema de arquivos.

## Situações de erro

- Arquivo `transcript_full.jsonl` corrompido ou linha JSON inválida: o leitor ignora a linha corrompida e continua os demais passos sem abortar o processo.
- Diretório de saída inexistente: criado recursivamente na primeira gravação.

## Escopo

- Dentro: Descoberta de sessões (mono e multi-usuário no mesmo host), adaptador do Antigravity CLI, identificação de `host_user` e `workspace`, controle incremental via checkpoint composto, escrita de Markdown com YAML frontmatter e suíte de testes unitários.
- Fora: Outros adaptadores de agentes (OpenCode, Claude Code, chats web) — estes permanecem no roadmap pós-MVP.

## Dúvidas, decisões e riscos

- Decisão: Núcleo 100% Python padrão (zero dependências externas).
- Decisão: Formato de notas otimizado nativamente para Spaces do SilverBullet e Vaults do Obsidian.
- Decisão: Suporte nativo a agregar chats de múltiplos usuários no mesmo servidor Linux/Windows.

## Pronto para desenvolvimento

- [x] O problema e a pessoa beneficiada estão claros.
- [x] O evento inicial e o resultado esperado estão claros.
- [x] Permissões, regras e exceções relevantes estão claras.
- [x] O resultado pode ser verificado objetivamente.
- [x] Segurança, privacidade e desempenho foram avaliados conforme o risco.
- [x] Fora de escopo, dependências e decisões pendentes estão registrados.

## Próximo passo

Promover para especificação formal via `$specsfy-03-specify`.
