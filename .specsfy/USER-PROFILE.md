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

## Uso pelo setup

- Antes de perguntar, leia este arquivo, a conversa atual e os contextos do
  projeto disponíveis.
- Uma resposta já registrada ou explicitamente declarada em outra fonte não
  volta a ser perguntada.
- Se fontes divergirem, pergunte apenas para resolver a divergência e registre
  a nova fonte e o alcance da resposta.
