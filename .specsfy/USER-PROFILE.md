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

## Uso pelo setup

- Antes de perguntar, leia este arquivo, a conversa atual e os contextos do
  projeto disponíveis.
- Uma resposta já registrada ou explicitamente declarada em outra fonte não
  volta a ser perguntada.
- Se fontes divergirem, pergunte apenas para resolver a divergência e registre
  a nova fonte e o alcance da resposta.
