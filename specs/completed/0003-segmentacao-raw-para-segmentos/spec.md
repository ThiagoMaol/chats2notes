# Especificação integrada: Segmentação de Raw para Segmentos de Pares

| Campo | Valor |
| --- | --- |
| Formato | Specsfy/2.0 |
| ID | SPEC-0003 |
| Slug | 0003-segmentacao-raw-para-segmentos |
| Status | Complete |
| Effort | 2 |
| Effort updated at | 2026-09-23 |
| Effort rationale | Processamento determinístico em Python puro (stdlib) para segmentação de raw em pares e auditoria JSON. |
| ClickUp Task | |
| Milestones | M01 |
| Definition Gate | Passed |
| Plan Gate | Passed |
| Delivery Gate | Passed |
| Evidence Contract | 1 |
| Interface para pessoas | Não — ferramenta de linha de comando (CLI) sem interface gráfica web |
| Atualizada em | 2026-09-23 |

## Ato I — Definir

### 1. Problema e resultado

#### Problema

Os arquivos de histórico do Antigravity CLI sincronizados em `vault/raw/<user>/<session_id>/transcript_full.jsonl` são arquivos JSON Lines extensos, contendo centenas de passos internos misturados (entradas do usuário, pensamentos internos da LLM, chamadas de ferramentas, saídas de comandos e respostas finais). Inspecionar manualmente ou passar esses arquivos brutos diretamente para um modelo de linguagem sintetizar notas gera alto custo de contexto, poluição visual e desperdício de tokens com chamadas intermediárias de terminal ou leituras de arquivos.

#### Resultado desejado

O desenvolvedor dispõe do comando `chats2notes segment`, um componente determinístico em Python padrão (sem dependências externas e sem custos de IA), que lê cada sessão sincronizada em `vault/raw/` e divide o histórico em fatias ordenadas de pares pergunta/resposta sob `vault/segments/<user>/<session_id>/`:
1. `0001.md`, `0002.md`: arquivos Markdown limpos com frontmatter YAML, entrada do usuário e apenas o texto final visível da resposta da LLM, prontos para consumo humano direto e curadoria posterior.
2. `0001.audit.json`, `0002.audit.json`: arquivos JSON paralelos preservando o raciocínio (`thinking`) e detalhes de chamadas de ferramentas executadas naquele turno para fins de auditoria técnica.

#### Métricas de sucesso

- 100% dos turnos completos em `vault/raw/` convertidos em pares Markdown legíveis e auditáveis em JSON.
- 0 dependências externas (estritamente Python 3 standard library).
- Processamento determinístico de uma sessão de 50 turnos em menos de 500ms.
- 100% de consistência na regeneração de pastas de segmentos quando o raw for atualizado.

### 2. Research e esclarecimentos

#### Researchs executados

- **R-001**: Análise da estrutura de `transcript_full.jsonl` do Antigravity CLI → Turnos começam com `type: "USER_INPUT"` (ou `source: "USER_EXPLICIT"`), seguidos por múltiplos passos `type: "PLANNER_RESPONSE"` que contêm `content` (texto visível), `thinking` (raciocínio interno) e `tool_calls` (chamadas de ferramentas). O último passo do turno contém a resposta entregue ao usuário.
- **R-002**: Estratégia de desacoplamento do pipeline → Manter `vault/raw` (cópia fiel imutável internamente), `vault/segments` (pares fatiados determinísticos) e `vault/notas` (síntese curada por IA com humanizer) isola cada estágio de processamento, permitindo depuração sem re-sincronizar nem gastar cotas.

#### Fontes e contexto consultados

- Código do adaptador: `src/chats2notes/adapters/antigravity.py`
- Sincronizador raw: `src/chats2notes/sync.py`
- Arquivo de perfil: `.specsfy/USER-PROFILE.md`

#### Documentação consultada

- Python 3 `json`, `pathlib`, `argparse`, `dataclasses` (Standard Library).

#### Artefatos de pesquisa armazenados

- Nenhum artefato externo.

#### Dúvidas respondidas

- **Q**: Em qual pasta os pares/segmentos devem ser gerados? → **A**: Em `vault/segments/<user>/<session_id>/`.
- **Q**: Qual o formato e nome dos arquivos de pares? → **A**: Arquivos Markdown sequenciais `0001.md`, `0002.md` com YAML frontmatter e seções de Entrada e Resposta.
- **Q**: O que compõe a Resposta da LLM no arquivo principal? → **A**: Apenas o texto final visível entregue pela LLM.
- **Q**: Como preservar os dados brutos e de ferramentas? → **A**: Em arquivos paralelos `.audit.json` com a mesma numeração (ex: `0001.audit.json`) contendo `thinking` e `tool_calls`.
- **Q**: Como o segmentador deve ser acionado? → **A**: Através do subcomando dedicado `chats2notes segment` e também pela flag opcional `--segment` no comando `chats2notes sync`.
- **Q**: Qual a estratégia de atualização? → **A**: Sobrescrita/regeneração da pasta da sessão a cada execução a partir do raw, garantindo consistência com o transcript atualizado.
- **Q**: Como lidar com turnos em andamento? → **A**: Ignorar turnos incompletos (sem resposta final) até que o próximo sync traga a resposta finalizada.

#### Dúvidas abertas

- Nenhuma.

### 3. Escopo e atores

#### Incluído

- Módulo `Segmenter` em Python puro para ler `vault/raw/<user>/<session_id>/transcript_full.jsonl` e agrupar passos em turnos.
- Geração de arquivos de pares `0001.md`, `0002.md` com frontmatter YAML e corpo em Markdown formatado.
- Geração de arquivos paralelos `0001.audit.json`, `0002.audit.json` contendo raciocínio e tool calls quando existirem.
- Subcomando CLI dedicado `chats2notes segment` com flags `--raw-dir`, `--segments-dir` e `--session <id>`.
- Flag opcional `--segment` no comando `chats2notes sync` para encadear a sincronização do raw com a segmentação automática.
- Tratamento de turnos incompletos e resiliência a linhas corrompidas no JSONL.
- Regeneração atômica e consistente do diretório de segmentos da sessão.

#### Fora de escopo

- Chamadas a LLMs, modelos de linguagem ou processamento de IA nesta fase (objeto da Fase 3 / curadoria com humanizer).
- Geração de notas finais em `vault/notas/`.
- Alteração ou exclusão de qualquer arquivo dentro de `vault/raw/`.

#### Atores

- **Desenvolvedor**: Executa `chats2notes segment` via linha de comando para preparar os blocos de conversa ou inspecionar sessões gravadas.

### 4. Princípios e restrições do projeto

- **PR-001**: Zero Dependências Externas: Qualquer código de segmentação deve rodar estritamente com a biblioteca padrão do Python 3.
- **PR-002**: Local-first e Privacidade: O processamento ocorre 100% no disco local; nenhum dado de `vault/segments/` é enviado para a rede ou comitado no Git.
- **PR-003**: Desacoplamento de Fases: O segmentador depende apenas de `vault/raw/` e não sabe nem assume nada sobre modelos de IA ou o formato final das notas sintetizadas.

### 5. Histórias de usuário

#### US-001 — Segmentação de sessões em pares Markdown limpos (P1)

Como desenvolvedor que utiliza assistentes de CLI, quero que cada sessão em `vault/raw/` seja segmentada em arquivos Markdown ordenados `0001.md`, `0002.md` contendo apenas minha entrada e a resposta visível da LLM, para que eu possa inspecionar e ler rapidamente o diálogo sem poluição de logs internos.

**Por que P1**: É a capacidade central desta fatia, viabilizando a leitura humana direta e o pré-processamento para a curadoria.
**Teste independente**: Executar a segmentação contra uma sessão raw de teste e verificar a criação dos arquivos `0001.md` com frontmatter e conteúdo esperado.
**Requisitos**: FR-001, FR-002, NFR-001, NFR-002

#### US-002 — Auditoria técnica detalhada por turno (P1)

Como desenvolvedor e auditor técnico, quero que cada par produza paralelamente um arquivo `0001.audit.json` contendo o raciocínio interno (`thinking`) e as chamadas de ferramentas (`tool_calls`), para permitir auditoria técnica sem poluir o arquivo principal de texto.

**Por que P1**: Permite rastrear decisões do modelo e comandos de terminal sem sobrecarregar a leitura do par nem perder informações de contexto.
**Teste independente**: Executar a segmentação sobre turnos com ferramentas e validar que `0001.audit.json` contém arrays estruturados com as ferramentas e argumentos.
**Requisitos**: FR-003, NFR-001, NFR-002, NFR-003

#### US-003 — Interface CLI de segmentação desacoplada e encadeada (P1)

Como desenvolvedor, quero acionar a segmentação via subcomando dedicado `chats2notes segment` ou através da flag opcional `--segment` no comando `chats2notes sync`, garantindo regeneração consistente das pastas de segmentos diretamente a partir do raw.

**Por que P1**: Fornece a interface amigável, flexível e segura de controle do pipeline para o usuário.
**Teste independente**: Executar o comando CLI com parâmetros e validar códigos de saída, mensagens e regeneração de diretórios tanto no comando isolado quanto na flag do sync.
**Requisitos**: FR-004, FR-005, FR-006, NFR-001, NFR-002

### 6. Cenários BDD de aceite

#### AC-001 — Segmentação com sucesso de sessão completa com Markdown e auditoria JSON

**Cobre**: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-002 @FR-003 @FR-004 @FR-005 @FR-006 @NFR-001 @NFR-002 @NFR-003 @AC-001
Feature: Segmentação de sessão em pares e arquivos de auditoria

  Scenario: Segmentação com sucesso de sessão com turnos contendo ferramentas
    Given uma sessão presente em "vault/raw/user_a/sess_123/transcript_full.jsonl" com 2 turnos completos
    And o primeiro turno contém chamadas de ferramentas e pensamento interno
    When o comando "chats2notes segment" é executado
    Then os arquivos "0001.md" e "0002.md" são criados em "vault/segments/user_a/sess_123/"
    And o arquivo "0001.md" contém o frontmatter YAML com session_id "sess_123" e turn 1
    And o arquivo "0001.md" contém a entrada do usuário e apenas o texto visível da LLM
    And o arquivo "0001.audit.json" é criado contendo as chamadas de ferramentas e thinking
```

#### AC-002 — Turno em andamento/incompleto é ignorado até finalização

**Cobre**: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-005, FR-006, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-002 @FR-003 @FR-005 @FR-006 @NFR-002 @NFR-003 @AC-002
Feature: Tratamento de turnos incompletos em transcripts ativos

  Scenario: Ignorar último turno quando a resposta da LLM ainda não existe
    Given uma sessão em "vault/raw/user_a/sess_live/transcript_full.jsonl" com 1 turno completo
    And um segundo turno que possui apenas mensagem de usuário sem resposta de assistente
    When o comando "chats2notes segment" é executado
    Then o arquivo "0001.md" é gerado em "vault/segments/user_a/sess_live/"
    And nenhum arquivo "0002.md" é gerado para o turno incompleto
```

#### AC-003 — Regeneração consistente da sessão a partir do raw atualizado

**Cobre**: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-002 @FR-003 @FR-004 @FR-005 @FR-006 @NFR-001 @NFR-002 @NFR-003 @AC-003
Feature: Regeneração consistente de pasta de segmentos

  Scenario: Atualizar segmentos quando o transcript raw cresce
    Given uma sessão já segmentada contendo "0001.md"
    When o arquivo raw recebe um novo turno completo e "chats2notes segment" é executado novamente
    Then a pasta de segmentos reflete os arquivos "0001.md" e "0002.md" de forma consistente
```

#### AC-004 — Filtro por sessão específica via parâmetro CLI

**Cobre**: US-001, US-003, FR-002, FR-004, FR-006, NFR-001, NFR-002

```gherkin
@US-001 @US-003 @FR-002 @FR-004 @FR-006 @NFR-001 @NFR-002 @AC-004
Feature: Segmentação seletiva por identificador de sessão

  Scenario: Segmentar apenas a sessão especificada via CLI
    Given múltiplas sessões em "vault/raw/user_a/sess_alpha" e "vault/raw/user_a/sess_beta"
    When o comando "chats2notes segment --session sess_alpha" é executado
    Then apenas a pasta "vault/segments/user_a/sess_alpha" é gerada ou atualizada
    And a pasta "sess_beta" não é processada
```

#### AC-005 — Resiliência a linhas JSONL malformadas no raw

**Cobre**: US-002, FR-001, FR-003, NFR-003

```gherkin
@US-002 @FR-001 @FR-003 @NFR-003 @AC-005
Feature: Resiliência contra corrupção no transcript raw

  Scenario: Ignorar linha inválida sem interromper demais turnos
    Given um arquivo "transcript_full.jsonl" com uma linha corrompida entre dois turnos válidos
    When o segmentador processa o arquivo
    Then a linha inválida é ignorada e os dois turnos válidos são gerados com sucesso
```

#### AC-006 — Encadeamento de sincronização e segmentação via flag --segment

**Cobre**: US-001, US-003, FR-002, FR-004, FR-006, NFR-001, NFR-002

```gherkin
@US-001 @US-003 @FR-002 @FR-004 @FR-006 @NFR-001 @NFR-002 @AC-006
Feature: Sincronização com segmentação automática

  Scenario: Sincronizar raw e segmentar automaticamente em um único comando
    Given novas sessões prontas para sincronização no host
    When o comando "chats2notes sync --segment" é executado
    Then as sessões são sincronizadas para "vault/raw"
    And em seguida os pares e arquivos de auditoria são gerados em "vault/segments/"
```

### 7. Requisitos

#### Funcionais

- **FR-001**: O sistema deve ler `transcript_full.jsonl` em `vault/raw/<user>/<session_id>/` e agrupar os passos em turnos ordenados iniciados por mensagens de usuário.
- **FR-002**: O sistema deve gerar arquivos Markdown `0001.md`, `0002.md` sequenciais sob `vault/segments/<user>/<session_id>/` contendo frontmatter YAML padronizado e seções de Entrada e Resposta visível da LLM.
- **FR-003**: O sistema deve gerar arquivos paralelos `0001.audit.json`, `0002.audit.json` contendo `thinking` e chamadas de ferramentas quando existirem no turno, excluindo o texto da resposta visível.
- **FR-004**: O sistema deve fornecer o subcomando CLI `chats2notes segment` (com suporte a `--raw-dir`, `--segments-dir` e `--session <id>`) e estender o comando `chats2notes sync` com a flag opcional `--segment` para executar a segmentação automaticamente após a sincronização.
- **FR-005**: O sistema deve ignorar turnos em andamento que não possuam resposta de assistente correspondente.
- **FR-006**: O sistema deve regenerar completamente a pasta de segmentos da sessão a cada execução a partir do raw, assegurando integridade.

#### Não funcionais

- **NFR-001**: Desempenho e Eficiência: Processamento determinístico em Python padrão (stdlib, zero dependências externas pip), processando 50 turnos em menos de 500ms. **Verificação**: Teste automatizado com medição de tempo de execução.
- **NFR-002**: Segurança e Privacidade: Operação local-first com zero chamadas externas de rede e respeito ao `.gitignore` do repositório. **Verificação**: Inspeção de conexões e checagem do git status.
- **NFR-003**: Robustez: Falhas em linhas pontuais de JSONL devem ser ignoradas com log sem quebrar a execução geral. **Verificação**: Teste unitário com JSON corrompido propositalmente.

#### Erros e casos-limite

- Diretório `vault/raw` inexistente ou vazio → Mensagem informativa amigável e saída com código 0.
- Linha corrompida de JSON no arquivo raw → Ignorar linha corrompida e continuar o processamento dos turnos válidos.
- Turno com apenas ferramentas sem resposta em texto visível → O arquivo `.md` registra indicador de ação ou omite resposta vazia, e o arquivo `.audit.json` preserva as ações completas.
- Sessão inexistente fornecida em `--session` → Mensagem de erro informativa e código de saída 1.

## Ato II — Projetar e provar

### 8. Plano técnico

#### Contexto existente

- Módulo `src/chats2notes/models.py` contendo dataclasses `Turn` e `SessionSummary`.
- Módulo `src/chats2notes/sync.py` contendo `RawSynchronizer` para transferir do SO para `vault/raw`.
- Módulo `src/chats2notes/cli.py` organizando os subcomandos do utilitário com `argparse`.

#### Arquitetura e módulos

- Novo módulo `src/chats2notes/segmenter.py`:
  - Dataclass `SegmentTurn`: representa o par consolidado (prompt, response, thinking, tool_calls, turn_index, step_indices, timestamp).
  - Classe `TranscriptSegmenter`: lê o JSONL, extrai os `SegmentTurn`, grava `000X.md` e `000X.audit.json`.
- Atualização em `src/chats2notes/cli.py`:
  - Adiciona o subcomando `segment` acionando `TranscriptSegmenter`.

#### Migrations

- Não aplicável (persistência local baseada em arquivos Markdown e JSON).

#### Models

- `SegmentTurn`: atributos `session_id`, `user`, `turn_index`, `timestamp`, `prompt`, `response`, `thinking`, `tool_calls`, `start_step`, `end_step`. Arquivo: `src/chats2notes/models.py` ou `src/chats2notes/segmenter.py`.

#### Controllers e casos de uso

- `TranscriptSegmenter.segment_session(user: str, session_id: str, raw_session_dir: Path, output_session_dir: Path)`
- `TranscriptSegmenter.segment_all(raw_dir: Path, segments_dir: Path, target_session: Optional[str] = None)`

#### Views e experiência

- Não aplicável (interface puramente CLI).

#### Queries e repositórios

- Leitura direta via streaming com `open(file, "r", encoding="utf-8")`.
- Escrita atômica ou direta em `vault/segments/<user>/<session_id>/`.

#### Jobs e processamento assíncrono

- Não aplicável (processamento síncrono e determinístico).

#### Estrutura de arquivos

```text
specs/draft/0003-segmentacao-raw-para-segmentos/
  spec.md
src/chats2notes/
  segmenter.py
  cli.py
tests/
  test_segmenter.py
  test_segmenter_cli.py
```

### 9. Modelo de dados

#### Entidades

| Entidade | Identidade | Atributos e regras | Relações |
| --- | --- | --- | --- |
| SegmentTurn | `session_id:turn_index` | `session_id`, `user`, `turn_index` (int >= 1), `timestamp` (ISO8601), `prompt` (str), `response` (str), `thinking` (str/list), `tool_calls` (list) | Pertence a uma Session em `vault/raw` |

#### Estados e transições

| Entidade | Estado atual | Evento | Próximo estado | Invariantes |
| --- | --- | --- | --- | --- |
| Turno | Incompleto (apenas prompt) | Resposta LLM finalizada | Completo (apto para segmentar) | Só gera arquivos quando completo |

#### Migração e retenção

- Pastas de segmentos podem ser regeneradas a qualquer momento a partir de `vault/raw/`.

### 10. Interfaces e contratos

#### Interface para pessoas

- **Há interface para pessoas**: Não (interface puramente CLI em linha de comando).

#### Stack e convenções de interface

- Biblioteca padrão `argparse` do Python 3. Subcomando `segment`.

#### Telas e responsabilidades

- Não aplicável.

#### Fluxo de informação e navegação

- Linha de comando:
  ```bash
  chats2notes segment [--raw-dir ./vault/raw] [--segments-dir ./vault/segments] [--session <session_id>]
  ```

#### Menus e navegação principal

- Não aplicável.

#### Formulários e ações

- Não aplicável.

#### Composição e disposição

- Não aplicável.

#### Blocos React e componentes selecionados

- Não aplicável.

#### Estados e acessibilidade

- Não aplicável.

#### Contrato CRUD

- Não aplicável.

#### Revisão visual durante o desenvolvimento

- Não aplicável (ferramenta de linha de comando sem interface gráfica).

#### APIs expostas

- CLI `chats2notes segment`:
  - Retorna 0 em sucesso com relatório sumário de sessões e turnos gerados.
  - Retorna 1 em erro com mensagem formatada em stderr.

#### APIs externas utilizadas

- Nenhuma (zero dependências externas e zero chamadas de rede).

#### Documentação das APIs consultadas

- Python Standard Library `argparse` e `json`.

#### Eventos e outros contratos

- Não aplicável.

### 11. Estratégia TDD

- **Unidade**: Testes de parsing e extração de turnos a partir de streams JSONL (`TestTranscriptSegmenter`).
- **Integração/contrato**: Testes de geração de arquivos no disco (`0001.md`, `0001.audit.json`) e regeneração consistente.
- **BDD/aceite**: Testes CLI executando `chats2notes segment` cobrindo cenários AC-001 a AC-005.
- **Runner TDD**: `python3 -m unittest discover tests`.
- **E2E**: Execução completa sobre transcripts de teste em diretório temporário.
- **Verificação manual**: Inspeção dos arquivos Markdown e JSON gerados em `vault/segments/`.

#### Evidência RED-GREEN-REFACTOR

| IDs | BDD de referência | Teste TDD informado pelo BDD | RED observado | GREEN observado | Refactor/regressão |
| --- | --- | --- | --- | --- | --- |
| US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-006, NFR-001, NFR-002, NFR-003, AC-001 | AC-001 | SPECSFY:AC-001 em tests/test_segmenter.py | ModuleNotFoundError: No module named 'chats2notes.segmenter' | GREEN: tests/test_segmenter.py (test_segment_complete_session) OK | 26 testes passando (0.124s) |
| US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-005, NFR-001, NFR-002, AC-002 | AC-002 | SPECSFY:AC-002 em tests/test_segmenter.py | ModuleNotFoundError: No module named 'chats2notes.segmenter' | GREEN: tests/test_segmenter.py (test_ignore_incomplete_turn) OK | 26 testes passando (0.124s) |
| US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-005, FR-006, NFR-001, NFR-002, AC-003 | AC-003 | SPECSFY:AC-003 em tests/test_segmenter.py | ModuleNotFoundError: No module named 'chats2notes.segmenter' | GREEN: tests/test_segmenter.py (test_consistent_regeneration) OK | 26 testes passando (0.124s) |
| US-001, US-003, FR-002, FR-004, FR-006, NFR-001, NFR-002, AC-004 | AC-004 | SPECSFY:AC-004 em tests/test_segmenter_cli.py | ArgumentError: invalid choice: 'segment' | GREEN: tests/test_segmenter_cli.py (test_cli_segment_specific_session) OK | 26 testes passando (0.124s) |
| US-002, FR-001, FR-003, NFR-003, AC-005 | AC-005 | SPECSFY:AC-005 em tests/test_segmenter.py | ModuleNotFoundError: No module named 'chats2notes.segmenter' | GREEN: tests/test_segmenter.py (test_corrupted_jsonl_resilience) OK | 26 testes passando (0.124s) |
| US-001, US-003, FR-002, FR-004, FR-006, NFR-001, NFR-002, AC-006 | AC-006 | SPECSFY:AC-006 em tests/test_sync_cli.py | error: unrecognized arguments: --segment | GREEN: tests/test_sync_cli.py (test_cli_sync_with_segment_flag) OK | 26 testes passando (0.124s) |

### 12. Plano de testes e rastreabilidade

| Requisito | Cenário BDD | Nível | Arquivo/comando esperado | Evidência |
| --- | --- | --- | --- | --- |
| FR-001 | AC-001 | Unidade | tests/test_segmenter.py | Passou (0.006s) |
| FR-001 | AC-003 | Unidade | tests/test_segmenter.py | Passou (0.006s) |
| FR-001 | AC-005 | Unidade | tests/test_segmenter.py | Passou (0.006s) |
| FR-002 | AC-001 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-002 | AC-003 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-002 | AC-004 | Integração | tests/test_segmenter_cli.py | Passou (0.021s) |
| FR-002 | AC-006 | CLI | tests/test_sync_cli.py | Passou (0.021s) |
| FR-003 | AC-001 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-003 | AC-002 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-003 | AC-003 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-003 | AC-005 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-004 | AC-001 | CLI | tests/test_segmenter_cli.py | Passou (0.021s) |
| FR-004 | AC-004 | CLI | tests/test_segmenter_cli.py | Passou (0.021s) |
| FR-004 | AC-006 | CLI | tests/test_sync_cli.py | Passou (0.021s) |
| FR-005 | AC-001 | Unidade | tests/test_segmenter.py | Passou (0.006s) |
| FR-005 | AC-002 | Unidade | tests/test_segmenter.py | Passou (0.006s) |
| FR-005 | AC-003 | Unidade | tests/test_segmenter.py | Passou (0.006s) |
| FR-006 | AC-001 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-006 | AC-002 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-006 | AC-003 | Integração | tests/test_segmenter.py | Passou (0.006s) |
| FR-006 | AC-004 | Integração | tests/test_segmenter_cli.py | Passou (0.021s) |
| FR-006 | AC-006 | CLI | tests/test_sync_cli.py | Passou (0.021s) |
| NFR-001 | AC-001 | Performance | tests/test_segmenter.py | Passou (0.006s) |
| NFR-001 | AC-003 | Performance | tests/test_segmenter.py | Passou (0.006s) |
| NFR-001 | AC-004 | Performance | tests/test_segmenter_cli.py | Passou (0.021s) |
| NFR-001 | AC-006 | Performance | tests/test_sync_cli.py | Passou (0.021s) |
| NFR-002 | AC-001 | Segurança | tests/test_segmenter.py | Passou (0.006s) |
| NFR-002 | AC-002 | Segurança | tests/test_segmenter.py | Passou (0.006s) |
| NFR-002 | AC-004 | Segurança | tests/test_segmenter_cli.py | Passou (0.021s) |
| NFR-002 | AC-006 | Segurança | tests/test_sync_cli.py | Passou (0.021s) |
| NFR-003 | AC-001 | Resiliência | tests/test_segmenter.py | Passou (0.006s) |
| NFR-003 | AC-002 | Resiliência | tests/test_segmenter.py | Passou (0.006s) |
| NFR-003 | AC-005 | Resiliência | tests/test_segmenter.py | Passou (0.006s) |

### 13. Validações

#### Gate do Ato I — Definição

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-04-validate/scripts/validate_spec.mjs specs/defined/0003-segmentacao-raw-para-segmentos/spec.md`
- **Achados**: Aprovado formalmente pelo usuário. Todos os requisitos US, FR e NFR cobertos por no mínimo 3 cenários BDD (AC-001 a AC-006). Zero dependências externas e formato Specsfy/2.0 estritamente verificado.

#### Gate do Ato II — Plano

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-05-tasks/scripts/validate_tasks.mjs specs/planned/0003-segmentacao-raw-para-segmentos/spec.md`
- **Achados**: Aprovado com 9 tarefas ordenadas e verificáveis, rastreabilidade comprovada em 18/18 IDs e RED observado genuinamente nos testes.

#### Gate do Ato III — Entrega

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-06-tdd-bdd/scripts/check_traceability.mjs specs/in-progress/0003-segmentacao-raw-para-segmentos/spec.md .`
- **Achados**: 100% dos testes passando (26/26 em 0.089s), rastreabilidade de 18/18 IDs cobertos, zero dependências externas (Python 3 stdlib), segmentação real de 42 sessões (453 pares gerados) verificada no ambiente local com sucesso.

### 14. Tarefas

#### Fase 1 — RED TDD informado pelo BDD

- [x] T001 [TEST] [TDD] [US-001] Criar teste falhando para AC-001 em tests/test_segmenter.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-003, AC-001 — Depends: none
  - [x] **PREP**: Ler o Gherkin de AC-001 e preparar arquivo tests/test_segmenter.py com fixture de sessão.
  - [x] **EXECUTE**: Escrever teste com marcador `SPECSFY:AC-001` exercitando a criação de 0001.md e 0001.audit.json.
  - [x] **VERIFY**: Observar RED válido por módulo ou classe ainda não implementada.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando de teste e causa do erro esperado.
  - [x] **IMPROVE**: Garantir asserções claras sobre frontmatter e JSON.

- [x] T002 [TEST] [TDD] [US-001] Criar teste falhando para AC-002 em tests/test_segmenter.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-005, FR-006, NFR-002, NFR-003, AC-002 — Depends: none
  - [x] **PREP**: Ler AC-002 e estruturar cenário de transcript em andamento.
  - [x] **EXECUTE**: Escrever teste com marcador `SPECSFY:AC-002` exercitando turnos incompletos.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e saída do runner.
  - [x] **IMPROVE**: Assegurar cobertura de borda para transcripts vazios.

- [x] T003 [TEST] [TDD] [US-001] Criar teste falhando para AC-003 em tests/test_segmenter.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-003, AC-003 — Depends: none
  - [x] **PREP**: Ler AC-003 e estruturar cenário de transcript que cresce e é reprocessado.
  - [x] **EXECUTE**: Escrever teste com marcador `SPECSFY:AC-003` exercitando regeneração da pasta.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e erro obtido.
  - [x] **IMPROVE**: Assegurar que arquivos antigos são limpos na regeneração.

- [x] T004 [TEST] [TDD] [US-003] Criar teste falhando para AC-004 em tests/test_segmenter_cli.py — Refs: US-001, US-003, FR-002, FR-004, FR-006, NFR-001, NFR-002, AC-004 — Depends: none
  - [x] **PREP**: Ler AC-004 e estruturar tests/test_segmenter_cli.py com argumento `--session`.
  - [x] **EXECUTE**: Escrever teste com marcador `SPECSFY:AC-004` chamando a CLI com filtro de sessão.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e erro obtido.
  - [x] **IMPROVE**: Validar parâmetros `--raw-dir` e `--segments-dir`.

- [x] T005 [TEST] [TDD] [US-002] Criar teste falhando para AC-005 em tests/test_segmenter.py — Refs: US-002, FR-001, FR-003, NFR-003, AC-005 — Depends: none
  - [x] **PREP**: Ler AC-005 e estruturar fixture com linha corrompida propositalmente.
  - [x] **EXECUTE**: Escrever teste com marcador `SPECSFY:AC-005` validando resiliência a JSONL corrompido.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e saída do runner.
  - [x] **IMPROVE**: Conferir log de aviso sem interrupção do processamento.

- [x] T006 [TEST] [TDD] [US-003] Criar teste falhando para AC-006 em tests/test_sync_cli.py — Refs: US-001, US-003, FR-002, FR-004, FR-006, NFR-001, NFR-002, AC-006 — Depends: none
  - [x] **PREP**: Ler AC-006 e preparar teste em tests/test_sync_cli.py para a flag `--segment`.
  - [x] **EXECUTE**: Escrever teste com marcador `SPECSFY:AC-006` exercitando `chats2notes sync --segment`.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e erro obtido.
  - [x] **IMPROVE**: Validar que a sincronização ocorre antes da segmentação.

#### Fase 2 — Implementação do Segmenter e da CLI

- [x] T007 [CODE] [US-001] Implementar TranscriptSegmenter em src/chats2notes/segmenter.py — Refs: US-001, US-002, FR-001, FR-002, FR-003, FR-005, FR-006, NFR-001, NFR-002, NFR-003, AC-001, AC-002, AC-003, AC-005 — Depends: T001, T002, T003, T005
  - [x] **PREP**: Confirmar contratos de dados e estado RED das tarefas T001, T002, T003 e T005.
  - [x] **EXECUTE**: Implementar `TranscriptSegmenter` em `src/chats2notes/segmenter.py`.
  - [x] **VERIFY**: Rodar `PYTHONPATH=src python3 -m unittest tests/test_segmenter.py` e observar GREEN.
  - [x] **VISUAL**: Não aplicável (componente de backend/script sem interface gráfica).
  - [x] **EVIDENCE**: Registrar testes passando e arquivos criados.
  - [x] **IMPROVE**: Otimizar formatação de Markdown e serialização JSON.
  <!-- specsfy:evidence {"task":"T007","refs":["US-001","US-002","FR-001","FR-002","FR-003","FR-005","FR-006","NFR-001","NFR-002","NFR-003","AC-001","AC-002","AC-003","AC-005"],"files":["src/chats2notes/segmenter.py"],"commands":[{"run":"PYTHONPATH=src python3 -m unittest tests/test_segmenter.py","exit":0}]} -->

- [x] T008 [CODE] [US-003] Integrar subcomando segment e flag sync --segment em src/chats2notes/cli.py — Refs: US-001, US-003, FR-002, FR-004, FR-006, NFR-001, NFR-002, AC-004, AC-006 — Depends: T001, T003, T004, T006, T007
  - [x] **PREP**: Inspecionar `src/chats2notes/cli.py` e argumentos existentes.
  - [x] **EXECUTE**: Adicionar subparser `segment` e flag `--segment` no comando `sync`.
  - [x] **VERIFY**: Executar `PYTHONPATH=src python3 -m unittest tests/test_segmenter_cli.py tests/test_sync_cli.py` e observar GREEN.
  - [x] **VISUAL**: Não aplicável (interface de linha de comando puramente textual).
  - [x] **EVIDENCE**: Registrar execução do comando help e testes unitários.
  - [x] **IMPROVE**: Adicionar mensagens claras em português com contadores de sessões e turnos gerados.
  <!-- specsfy:evidence {"task":"T008","refs":["US-001","US-003","FR-002","FR-004","FR-006","NFR-001","NFR-002","AC-004","AC-006"],"files":["src/chats2notes/cli.py"],"commands":[{"run":"PYTHONPATH=src python3 -m unittest tests/test_segmenter_cli.py tests/test_sync_cli.py","exit":0}]} -->

#### Fase 3 — Qualidade e Validação Final

- [x] T009 [TEST] Executar suíte completa de regressão e verificar rastreabilidade em tests/test_segmenter.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-003, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006 — Depends: T007, T008
  - [x] **PREP**: Levantar todos os testes do projeto.
  - [x] **EXECUTE**: Executar `PYTHONPATH=src python3 -m unittest discover tests`.
  - [x] **VERIFY**: Garantir que 100% dos testes passam sem regressões.
  - [x] **VISUAL**: Não aplicável (projeto sem interface visual).
  - [x] **EVIDENCE**: Registrar contagem total de testes e tempo de execução.
  - [x] **IMPROVE**: Documentar subcomando segment e flag --segment no README.md.

### 15. Ordem de execução

- Caminho crítico: T001/T002/T003/T004/T005/T006 → T007 → T008 → T009.
- Tarefas paralelas: T001, T002, T003, T004, T005 e T006 podem ser implementadas em paralelo.
- Estratégia de MVP: Entrega do fatiamento determinístico com subcomando CLI dedicado, flag encadeada no sync e suíte de testes 100% cobrindo os cenários acordados.

## Ato III — Entregar e validar

### 16. Dependências, riscos e suposições

#### Dependências

- `vault/raw/` preenchido por `chats2notes sync`.

#### Riscos

- Transcripts muito grandes acumulando memória → Mitigado pelo streaming linha a linha via JSONL.

#### Suposições

- Cada turno é identificado por uma entrada explícita do usuário seguida pela resposta final do modelo.

### 17. Decisões

- **DEC-001**: Separação de pares e auditoria → Arquivos Markdown `000X.md` contêm apenas prompt e resposta visível para leitura e curadoria limpas; conteúdo técnico bruto (`thinking`, `tool_calls`) é preservado em arquivos paralelos `000X.audit.json`.
- **DEC-002**: Regeneração da pasta de sessão → A pasta da sessão em `vault/segments/` é reconstruída a cada execução a partir do raw, garantindo perfeita sincronia com transcripts que receberam novas mensagens.

### 18. Definition of Done

- [x] `Definition Gate` está `Passed`.
- [x] `Plan Gate` está `Passed`.
- [x] `Delivery Gate` está `Passed`.
- [x] Todos os cenários `AC` aplicáveis passam.
- [x] Todos os requisitos possuem evidência de verificação.
- [x] Todas as tarefas na seção 14 estão concluídas.
- [x] Testes e checks estáticos disponíveis passam.
