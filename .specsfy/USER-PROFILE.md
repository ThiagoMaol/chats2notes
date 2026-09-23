# Perfil de interação do Specsfy

Este arquivo guarda somente o nível de conhecimento e as respostas confirmadas
durante o setup. Ele orienta a forma da conversa e não substitui `PROJECT.md`,
`STACK.md`, `RULES.md`, `DATABASE.md`, `INTERFACE.md`, `DESIGNSYSTEM.MD` ou uma
spec.

## Nível de conhecimento

| Campo | Valor |
| --- | --- |
| Nível atual | iniciante |
| Fonte da confirmação | Resposta à Pergunta 1 do setup na conversa |
| Última confirmação | 2026-09-23 |

Valores permitidos: `iniciante`, `intermediário` e `experiente`.

## Respostas confirmadas

Registre somente respostas dadas pela pessoa ou declarações inequívocas já
presentes nas fontes lidas. Não registre segredos, tokens, senhas ou dados de
produção.

| Área | Pergunta ou assunto | Resposta normalizada | Fonte | Confirmado em |
| --- | --- | --- | --- | --- |
| Geral | Nível de orientação | iniciante | Pergunta 1 do setup | 2026-09-23 |
| Geral | Diretório do projeto | /mnt/dados/home/thiago/PROJETOS/ghub_thiago/chats2notes | Confirmação inicial do setup | 2026-09-23 |
| Produto | Objetivo e resultado principal | Extrair conversas de CLI e gerar notas Markdown para SilverBullet e Obsidian | README.md / PROJECT.md | 2026-09-23 |
| Produto | Pessoas usuárias e papéis | Desenvolvedor individual em Linux/Windows (sem multitenancy) | README.md / PROJECT.md | 2026-09-23 |
| Segurança | Acesso, autenticação e permissões | Local-first, leitura de logs do usuário no SO, sem login | README.md / PROJECT.md | 2026-09-23 |
| Dados | Dados principais e retenção | JSONL de entrada, checkpoint.json de estado e Markdown de saída | README.md / PROJECT.md | 2026-09-23 |
| Interface | Telas e navegação | Interface CLI (linha de comando) e automação em segundo plano | README.md / PROJECT.md | 2026-09-23 |
| Tecnologia | Stack de execução e testes | Python 3 standard library (zero dependências) e unittest | Pergunta 2 do setup | 2026-09-23 |
| IA e Integrações | Modelo de curadoria e cota | Híbrido: cota nativa do Antigravity CLI no chat + chave opcional para cron | Pergunta 3 do setup | 2026-09-23 |
| Dados | Destino dos segmentos de pares | `vault/segments/<user>/<session_id>/` | Pergunta 1 de descoberta SPEC-0003 | 2026-09-23 |
| Dados | Formato dos segmentos de pares | Markdown sequencial `0001.md` com frontmatter YAML e seções de Entrada e Resposta | Pergunta 2 de descoberta SPEC-0003 | 2026-09-23 |
| Dados | Composição da resposta e auditoria | Resposta da LLM contém apenas texto visível final; conteúdo bruto (thinking + tool_calls) é salvo em arquivo paralelo de auditoria | Pergunta 3 de descoberta SPEC-0003 | 2026-09-23 |
| Dados | Formato do arquivo de auditoria | JSON estruturado com sufixo `.audit.json` (ex: `0001.audit.json`) | Pergunta 4 de descoberta SPEC-0003 | 2026-09-23 |
| Interface | Comando CLI de segmentação | Ambos: subcomando dedicado `chats2notes segment` e flag opcional `--segment` em `chats2notes sync` | Pergunta 5 de descoberta SPEC-0003 (atualizado) | 2026-09-23 |
| Dados | Estratégia de regeneração dos segmentos | Sobrescrever/regenerar toda a pasta de segmentos da sessão a cada execução a partir do `vault/raw`, garantindo consistência com o transcript atualizado | Pergunta 6 de descoberta SPEC-0003 | 2026-09-23 |
| Dados | Turnos em andamento/incompletos | Ignorar turnos incompletos sem resposta final e só gerar quando a resposta estiver concluída | Pergunta 7 de descoberta SPEC-0003 | 2026-09-23 |
| Roadmap | Ingestão NotebookLM | Suportar chats do NotebookLM via extração de terceiros ou export manual (copia + cola) | Alinhamento de perspectivas pós SPEC-0003 | 2026-09-23 |
| Roadmap | Reorganização SilverBullet/Obsidian | Reorganizar notas preexistentes de SilverBullet e Obsidian na nova estrutura do projeto | Alinhamento de perspectivas pós SPEC-0003 | 2026-09-23 |
| Roadmap | Migração Notion/Evernote | Suportar migração e tratamento de notas de Notion e Evernote para o ambiente SilverBullet | Alinhamento de perspectivas pós SPEC-0003 | 2026-09-23 |
| Curadoria | Granularidade das notas | Notas atômicas autossuficientes (segundo cérebro / enciclopédia pessoal): par Q&A, registro de entrega/conclusão ou input longo do usuário | Definição de preferências da Fase 3 | 2026-09-23 |
| Curadoria | Filtragem de ruído | Descartar mensagens triviais/operacionais ("sim", "1", "prossiga"); incluir comandos reexecutáveis/consultáveis | Definição de preferências da Fase 3 | 2026-09-23 |
| Curadoria | Categorização de diálogos | FAQs para Q&A geral; "Pair-Programming" / "pAIr-Programming" para interações de etapas de frameworks (Specsfy, MVPfy, etc.) | Definição de preferências da Fase 3 | 2026-09-23 |
| Curadoria | Divisão de perguntas múltiplas | Separar em notas distintas quando não comprometer a compreensão; manter juntas se a separação prejudicar o contexto | Definição de preferências da Fase 3 | 2026-09-23 |
| Curadoria | Estrutura de pastas | Estrutura totalmente plana na raiz de `vault/notas/` sem subpastas, aproveitando Live Queries e atributos do frontmatter no SilverBullet | Pergunta 2 de descoberta SPEC-0004 | 2026-09-23 |
| Curadoria | Frontmatter YAML | tags, project (se aplicável), datas (criação e mensagem original), link para segmento original (`vault/segments/...`), link para notas complementares, source | Definição de preferências da Fase 3 | 2026-09-23 |
| Curadoria | Diagramação de FAQ | Título curto; Pergunta resumida destacada; Resposta enxuta nível Jr em tópicos (sem prolixidade); divisor `---`; Pergunta completa; Resposta completa | Definição de preferências da Fase 3 | 2026-09-23 |
| Curadoria | Diagramação de Pair-Programming | Título `<projeto> - <framework> - Pergunta <N>`; Pergunta resumida sem alternativas; Resposta escolhida + complemento humano; divisor `---`; Pergunta completa com alternativas | Definição de preferências da Fase 3 | 2026-09-23 |
| Interface | Mecanismo de execução da curadoria | Abordagem híbrida: subcomando CLI `chats2notes curate` (em lote/cron com API key opcional) e rotina assistida no chat pelo agente de pair-programming | Pergunta 1 de descoberta SPEC-0004 | 2026-09-23 |
| Curadoria | Nomenclatura de arquivos e colisão | Nomes em Title Case com espaços refletindo o título da nota; sufixo numérico de desambiguação `(2)` se houver colisão de títulos idênticos | Pergunta 3 de descoberta SPEC-0004 | 2026-09-23 |
| Curadoria | Rastreamento e memória de descarte | Manifesto dedicado `vault/.curated.json` isolado de raw/sync, registrando segmentos avaliados, notas geradas e ruídos descartados com flag `--force` | Pergunta 4 de descoberta SPEC-0004 | 2026-09-23 |
| IA e Integrações | Provedores de IA na CLI de curadoria | Suporte nativo via stdlib a Google Gemini API (`GEMINI_API_KEY`) e endpoints compatíveis com OpenAI/Ollama (`OPENAI_API_KEY`, `OPENAI_BASE_URL`) | Pergunta 5 de descoberta SPEC-0004 | 2026-09-23 |
| Curadoria | Taxonomia e geração de tags | Vocabulário controlado a partir de lista base extensível de termos técnicos do projeto, unificando sinônimos e cunhando tags novas apenas para assuntos inéditos | Pergunta 6 de descoberta SPEC-0004 | 2026-09-23 |
| Escopo | Estratégia de fatiamento da SPEC-0004 | Foco inicial no motor de curadoria, regras, prompts, diagramações (FAQ e Pair-Programming) e manifesto, deixando adaptadores de rede de provedores para refinamento posterior | Pergunta 7 de descoberta SPEC-0004 | 2026-09-23 |

## Uso pelo setup

- Antes de perguntar, leia este arquivo, a conversa atual e os contextos do
  projeto disponíveis.
- Uma resposta já registrada ou explicitamente declarada em outra fonte não
  volta a ser perguntada.
- Se fontes divergirem, pergunte apenas para resolver a divergência e registre
  a nova fonte e o alcance da resposta.
