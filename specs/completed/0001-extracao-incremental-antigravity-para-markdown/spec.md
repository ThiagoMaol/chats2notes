# Especificação integrada: Extração incremental de conversas do Antigravity CLI para notas Markdown

| Campo | Valor |
| --- | --- |
| Formato | Specsfy/2.0 |
| ID | SPEC-0001 |
| Slug | 0001-extracao-incremental-antigravity-para-markdown |
| Status | Complete |
| Effort | 3 |
| Effort updated at | 2026-09-23 |
| Effort rationale | Escopo bem delimitado em Python padrão (zero dependências), leitor JSONL, checkpoint atômico e templates Markdown. |
| ClickUp Task | |
| Milestones | M01 (MVP) |
| Definition Gate | Passed |
| Plan Gate | Passed |
| Delivery Gate | Passed |
| Evidence Contract | 1 |
| Interface para pessoas | Não — ferramenta de linha de comando (CLI) e automação em segundo plano sem interface gráfica web |
| Atualizada em | 2026-09-23 |

## Ato I — Definir

### 1. Problema e resultado

#### Problema

Durante sessões de pair-programming com agentes de inteligência artificial em linha de comando (CLI), desenvolvem-se soluções arquiteturais, tutoriais e explicações de alto valor técnico. Atualmente, o desenvolvedor precisa interromper o fluxo de trabalho para copiar e colar manualmente prompts e respostas para o Notion ou editor de notas, ou deixar esse material acumular nos logs locais do agente, gerando uma "bola de neve" de conhecimento esquecido e inacessível.

#### Resultado desejado

O desenvolvedor executa o `chats2notes` (ou agenda sua execução automática) e obtém, de forma 100% autônoma e incremental, arquivos Markdown organizados por turnos de conversa, enriquecidos com metadados YAML (título, tags, agente, usuário, workspace e data), prontos para consulta e indexação direta em Spaces do SilverBullet e Vaults do Obsidian, sem duplicar notas e sem consumir contexto da conversa ativa.

#### Métricas de sucesso

- 100% de precisão na extração dos turnos de conversa (pergunta do usuário + resposta do assistente) a partir de logs `transcript_full.jsonl`.
- Zero duplicação de notas em execuções repetidas sobre o mesmo histórico (idempotência via `checkpoint.json`).
- Tempo de execução inferior a 2 segundos para varrer e processar até 50 sessões locais em hardware padrão.
- Zero dependências externas no núcleo (roda diretamente com Python 3.10+ nativo no Linux e Windows).

### 2. Research e esclarecimentos

#### Researchs executados

- **R-001**: Investigação da estrutura de persistência do Antigravity CLI sob `~/.gemini/antigravity-cli/brain/<uuid>/.system_generated/logs/` → Concluiu-se que `transcript_full.jsonl` mantém a integridade total sem truncamento dos turnos, contendo campos `step_index`, `source`, `type`, `created_at` e `content`.
- **R-002**: Investigação da compatibilidade de notas para SilverBullet e Obsidian → Concluiu-se que arquivos CommonMark com YAML Frontmatter contendo atributos como `name`, `tags`, `agent`, `host_user`, `workspace` e `created` são nativamente consultáveis via Live Queries (`query page where ...`) no SilverBullet e Dataview no Obsidian.

#### Fontes e contexto consultados

- Logs reais de transcripts em `~/.gemini/antigravity-cli/brain/` no host Linux.
- Documentação do SilverBullet (`silverbullet.md`) e convenções do Obsidian.
- Contexto do projeto em `PROJECT.md`, `README.md` e `.specsfy/STACK.md`.

#### Documentação consultada

- Google Antigravity CLI Agent Traces Reference, formato JSONL estruturado de steps.
- SilverBullet Documentation (Object & Page Frontmatter, Live Queries Syntax).
- Python 3 Standard Library Reference (`pathlib`, `json`, `dataclasses`, `unittest`, `argparse`).

#### Artefatos de pesquisa armazenados

- `specs/draft/0001-extracao-incremental-antigravity-para-markdown/research/`: Nenhum artefato externo adicional necessário.

#### Dúvidas respondidas

- **Q**: Os chats ficam separados por projeto ou em diretório central do usuário? → **A**: Ficam em diretório central (`~/.gemini/antigravity-cli/brain/`), contendo o identificador do workspace nos metadados da sessão.
- **Q**: É possível processar múltiplos usuários do mesmo host? → **A**: Sim, aceitando múltiplos caminhos base de `brain/` e identificando `host_user` no Frontmatter e no `checkpoint.json`.
- **Q**: Devemos usar ambientes virtuais e bibliotecas externas no MVP? → **A**: Não, o núcleo é estritamente em Python padrão (zero dependências) para máxima leveza e portabilidade.

#### Dúvidas abertas

- Nenhuma dúvida bloqueante em aberto.

### 3. Escopo e atores

#### Incluído

- Descoberta automática de sessões em `~/.gemini/antigravity-cli/brain/` no Linux e `%USERPROFILE%\.gemini\...` no Windows.
- Suporte a agregação multi-usuário no mesmo host através de parâmetro `--brain-dir` múltiplo ou lista configurada.
- Leitor incremental de arquivos `transcript_full.jsonl` (com fallback para `transcript.jsonl`).
- Gerenciador de estado atômico `checkpoint.json` isolado por `(host_user, session_id)`.
- Gerador de notas Markdown com YAML frontmatter otimizado para SilverBullet Live Queries e Obsidian.
- Ponto de entrada CLI em linha de comando com comandos `extract`, `status` e flags descritivas.
- Suíte completa de testes automatizados com `unittest` da biblioteca padrão.

#### Fora de escopo

- Interface gráfica web ou aplicativo desktop nativo proprietário (usa-se o terminal CLI).
- Sistema de autenticação web, contas multi-inquilino ou banco de dados relacional pesado.
- Adaptadores de outros agentes CLI (OpenCode, Claude Code) e chats web (Gemini/ChatGPT web), que ficam para marcos pós-MVP.
- Modificação ou exclusão dos logs originais do Antigravity (estritamente somente leitura).

#### Atores

- **Desenvolvedor / Engenheiro**: Executa o comando no terminal ou via cron no host para alimentar seu Space do SilverBullet ou Vault do Obsidian.

### 4. Princípios e restrições do projeto

- **PR-001**: O núcleo do sistema deve usar estritamente a biblioteca padrão do Python 3 (zero pacotes externos no `requirements.txt`/`pip`).
- **PR-002**: Toda operação de leitura sobre os logs do agente é estritamente somente leitura; nenhuma sessão de chat no disco é alterada.
- **PR-003**: Idempotência rigorosa: execuções consecutivas não podem duplicar notas nem corromper o estado em caso de interrupção inesperada (gravação atômica do checkpoint).
- **PR-004**: Multiplataforma nativa: caminhos e manipuladores de arquivos devem utilizar `pathlib.Path` sem concatenação manual de barras.

### 5. Histórias de usuário

#### US-001 — Extração incremental e curadoria de notas do Antigravity CLI (P1)

Como desenvolvedor que utiliza o Antigravity CLI no Linux ou Windows, quero que o chats2notes descubra sessões locais, extraia novos turnos de diálogo e gere notas Markdown no meu Space do SilverBullet / Vault do Obsidian, para que eu tenha uma base de conhecimento organizada sem trabalho manual de copiar e colar.

**Por que P1**: Representa o núcleo de valor e a solução direta da dor principal do usuário.
**Teste independente**: Executar a CLI contra um diretório simulado de sessões e verificar a geração dos arquivos `.md` com frontmatter e o registro do checkpoint.
**Requisitos**: FR-001, FR-002, FR-003, NFR-001

### 6. Cenários BDD de aceite

#### AC-001 — Extração inicial de novos turnos de uma sessão

**Cobre**: US-001, FR-001, FR-002, FR-003, NFR-001

```gherkin
@US-001 @FR-001 @FR-002 @FR-003 @NFR-001 @AC-001
Feature: Extração inicial de conversas

  Scenario: Processar uma sessão completa pela primeira vez
    Given um diretório brain com uma sessão contendo dois turnos de pergunta e resposta
    And o arquivo checkpoint.json não contém registro para essa sessão
    When o comando de extração é executado
    Then duas notas Markdown individuais são geradas no diretório de saída
    And cada nota contém YAML frontmatter com name, agent, host_user e tags
    And o checkpoint.json é atualizado com o último step_index da sessão
```

#### AC-002 — Idempotência incremental com checkpoint já existente

**Cobre**: US-001, FR-001, FR-002, FR-003, NFR-001

```gherkin
@US-001 @FR-001 @FR-002 @FR-003 @NFR-001 @AC-002
Feature: Idempotência incremental

  Scenario: Executar extração quando não há novas mensagens
    Given uma sessão cujo último step_index já está gravado no checkpoint.json
    When o comando de extração é executado novamente
    Then nenhuma nova nota Markdown é gerada
    And nenhum arquivo existente é modificado
    And o checkpoint.json permanece inalterado
```

#### AC-003 — Descoberta e isolamento multi-usuário no mesmo host

**Cobre**: US-001, FR-001, FR-002, FR-003, NFR-001

```gherkin
@US-001 @FR-001 @FR-002 @FR-003 @NFR-001 @AC-003
Feature: Agregação multi-usuário no host

  Scenario: Processar diretórios de diferentes usuários do mesmo host
    Given diretórios brain configurados para dois usuários locais diferentes
    When o comando de extração é executado informando as múltiplas origens
    Then as notas geradas registram o respectivo host_user no frontmatter
    And o checkpoint.json mantém marcas d'água isoladas por usuário sem colisão
```

#### AC-004 — Resiliência a arquivos com linhas corrompidas ou incompletas

**Cobre**: US-001, FR-001, FR-002, FR-003, NFR-001

```gherkin
@US-001 @FR-001 @FR-002 @FR-003 @NFR-001 @AC-004
Feature: Resiliência na leitura de logs

  Scenario: Processar arquivo JSONL com uma linha corrompida
    Given um arquivo transcript contendo linhas válidas e uma linha malformada
    When o leitor incremental processa o arquivo
    Then as linhas válidas são extraídas com sucesso em notas Markdown
    And o processo não é abortado por erro fatal
    And um aviso informativo é emitido no relatório de execução
```

### 7. Requisitos

#### Funcionais

- **FR-001**: O sistema deve descobrir automaticamente diretórios de sessões do Antigravity CLI e suportar múltiplos diretórios de perfis/usuários no mesmo host.
- **FR-002**: O sistema deve ler incrementalmente os arquivos `transcript_full.jsonl` a partir da marca d'água persistida em `checkpoint.json`.
- **FR-003**: O sistema deve gerar arquivos de notas em Markdown com YAML frontmatter enriquecido (`name`, `tags`, `agent`, `host_user`, `workspace`, `session`, `created`, `category`).

#### Não funcionais

- **NFR-001**: O sistema deve ser executado exclusivamente sobre a biblioteca padrão do Python 3.10+, sem dependências externas adicionais. **Verificação**: Execução da suíte de testes e verificação de imports contra a standard library.

#### Erros e casos-limite

- Arquivo `transcript_full.jsonl` vazio ou ausente → o adaptador tenta ler `transcript.jsonl`; se nenhum existir, pula a sessão silenciosamente.
- Linha JSON truncada ou inválida → o leitor ignora a linha e continua o processamento das linhas subsequentes.
- Interrupção de processo durante a escrita → a persistência de `checkpoint.json` é feita via arquivo temporário atômico (`os.replace`), prevenindo corrupção.

## Ato II — Projetar e provar

### 8. Plano técnico

#### Contexto existente

O projeto adota arquitetura de biblioteca e CLI em Python puro sob `src/chats2notes/`. A raiz contém a documentação técnica, diretrizes do framework Specsfy e configurações de versionamento Git.

#### Arquitetura e módulos

- `src/chats2notes/models.py`: Data classes puras para `Turn`, `Session`, `Message`.
- `src/chats2notes/adapters/base.py`: Interface abstrata `BaseAdapter` definindo o contrato de adaptadores.
- `src/chats2notes/adapters/antigravity.py`: Implementação do adaptador do Antigravity CLI com parsing de JSONL.
- `src/chats2notes/state.py`: Gerenciador de estado atômico `StateManager` operando sobre `checkpoint.json`.
- `src/chats2notes/storage.py`: Formatador e escritor de notas Markdown com YAML frontmatter.
- `src/chats2notes/cli.py`: Ponto de entrada CLI via `argparse` com comandos de extração e status.

#### Migrations

Não aplicável — o sistema utiliza persistência baseada em arquivos planos JSON e Markdown.

#### Models

- `Turn`: representa o par de pergunta e resposta com metadados (timestamp, passos, usuário, sessão).
- `Session`: metadados de uma sessão descoberta em disco (ID, agente, path, datas).
- `StateManager`: modelo de controle de marcas d'água atômicas.

#### Controllers e casos de uso

- `ExtractUseCase`: orquestra a descoberta por adapters, filtragem por checkpoint, geração de notas e atualização de estado.

#### Views e experiência

Não aplicável — interface em linha de comando (CLI) via terminal.

#### Queries e repositórios

- `SessionDiscovery`: varredura de diretórios usando `pathlib.Path.iterdir()`.
- `TranscriptReader`: leitura sequencial em streaming de arquivos JSONL.

#### Jobs e processamento assíncrono

Não aplicável — execução síncrona sob demanda ou disparada pelo cron do sistema.

#### Estrutura de arquivos

```text
specs/draft/0001-extracao-incremental-antigravity-para-markdown/
  spec.md
  research/
src/
  chats2notes/
    __init__.py
    cli.py
    models.py
    state.py
    storage.py
    adapters/
      __init__.py
      base.py
      antigravity.py
tests/
  test_models.py
  test_state.py
  test_antigravity_adapter.py
  test_storage.py
  test_cli.py
```

### 9. Modelo de dados

#### Entidades

| Entidade | Identidade | Atributos e regras | Relações |
| --- | --- | --- | --- |
| Session | session_id (UUID) | agent_name, path, created_at, updated_at | 1:N com Turn |
| Turn | session_id + start_step | user_prompt, assistant_response, timestamp, start_step, end_step, host_user, workspace | Pertence a Session |
| Checkpoint | agent_name + host_user + session_id | last_processed_step, updated_at | Rastreia Session |

#### Estados e transições

| Entidade | Estado atual | Evento | Próximo estado | Invariantes |
| --- | --- | --- | --- | --- |
| Turn | Novo no transcript | Extração executada | Persistido em .md | end_step > last_processed_step |
| Checkpoint | Passo anterior gravado | Processamento concluído | Passo atual gravado | Operação atômica via os.replace |

#### Migração e retenção

Não aplicável — o estado é versionado diretamente em JSON local retrocompatível.

### 10. Interfaces e contratos

#### Interface para pessoas

Não — ferramenta de linha de comando (CLI) sem interface gráfica web. Justificativa: o software atua como ferramenta utilitária e serviço em background voltado para desenvolvedores.

#### Stack e convenções de interface

Interface em linha de comando construída com o módulo nativo `argparse` do Python. Mensagens claras em stdout com código de saída 0 para sucesso e >0 para erros operacionais.

#### Telas e responsabilidades

Não aplicável.

#### Fluxo de informação e navegação

Não aplicável.

#### Menus e navegação principal

Não aplicável.

#### Formulários e ações

Comando principal: `python3 -m chats2notes.cli extract [--brain-dir PATH] [--output-dir PATH] [--host-user USER]`.

#### Composição e disposição

Não aplicável.

#### Blocos React e componentes selecionados

Não aplicável.

#### Estados e acessibilidade

Não aplicável.

#### Contrato CRUD

Não aplicável.

#### Revisão visual durante o desenvolvimento

Não aplicável — a ferramenta é estritamente de linha de comando sem interface visual gráfica.

#### APIs expostas

Linha de comando CLI:
- `chats2notes extract`: executa a varredura incremental e gera as notas.
- `chats2notes status`: exibe resumo das sessões monitoradas e último checkpoint.

#### APIs externas utilizadas

Nenhuma no núcleo do MVP (leitura direta de arquivos locais do sistema de arquivos).

#### Documentação das APIs consultadas

Documentação da biblioteca padrão do Python 3 (`pathlib`, `json`, `argparse`).

#### Eventos e outros contratos

Formato do YAML Frontmatter gerado:
```yaml
---
name: "Título Semântico"
created: 2026-09-23 02:00:00
tags: [ai-notes, antigravity]
agent: antigravity
host_user: thiago
workspace: "/path/to/project"
session: "uuid"
category: "Engenharia de Software"
---
```

### 11. Estratégia TDD

- **Unidade**: Modelos de dados, parsing de logs JSONL, limpeza de tags, salvamento atômico de checkpoints e formatação de Markdown.
- **Integração/contrato**: Execução do adaptador contra diretórios simulados de sessões completas.
- **BDD/aceite**: Cenários de referência AC-001 a AC-004 implementados como casos de teste no `unittest`.
- **Runner TDD**: `python3 -m unittest discover tests`.
- **E2E**: Execução do CLI completo contra dados mockados no disco temporário.
- **Verificação manual**: Nenhuma necessária além da validação automatizada.

#### Evidência RED-GREEN-REFACTOR

| IDs | BDD de referência | Teste TDD informado pelo BDD | RED observado | GREEN observado | Refactor/regressão |
| --- | --- | --- | --- | --- | --- |
| US-001, FR-001, FR-002, FR-003, NFR-001, AC-001 | AC-001 na seção 6 | `tests/test_antigravity_adapter.py:TestAntigravityAdapter.test_initial_extraction` | NotImplementedError (AntigravityAdapter.extract_new_turns) | Passed (1 Turn extraído com prompt/resposta íntegros) | Passed (11 testes OK sem regressão) |
| US-001, FR-001, FR-002, FR-003, NFR-001, AC-002 | AC-002 na seção 6 | `tests/test_antigravity_adapter.py:TestAntigravityAdapter.test_incremental_idempotence` | NotImplementedError (AntigravityAdapter.extract_new_turns) | Passed (idempotência incremental confirmada) | Passed (11 testes OK sem regressão) |
| US-001, FR-001, FR-002, FR-003, NFR-001, AC-003 | AC-003 na seção 6 | `tests/test_antigravity_adapter.py:TestAntigravityAdapter.test_multi_user_discovery` | NotImplementedError (AntigravityAdapter.discover_sessions) | Passed (descoberta multi-usuário em /home) | Passed (11 testes OK sem regressão) |
| US-001, FR-001, FR-002, FR-003, NFR-001, AC-004 | AC-004 na seção 6 | `tests/test_antigravity_adapter.py:TestAntigravityAdapter.test_resilience_corrupted_jsonl` | NotImplementedError (AntigravityAdapter.extract_new_turns) | Passed (resiliência a linhas corrompidas validada) | Passed (11 testes OK sem regressão) |

### 12. Plano de testes e rastreabilidade

| Requisito | Cenário BDD | Nível | Arquivo/comando esperado | Evidência |
| --- | --- | --- | --- | --- |
| FR-001 | AC-001 | Unidade | `tests/test_antigravity_adapter.py` | Passed |
| FR-001 | AC-002 | Unidade | `tests/test_antigravity_adapter.py` | Passed |
| FR-001 | AC-003 | Integração | `tests/test_antigravity_adapter.py` | Passed |
| FR-001 | AC-004 | Unidade | `tests/test_antigravity_adapter.py` | Passed |
| FR-002 | AC-001 | Unidade | `tests/test_state.py` | Passed |
| FR-002 | AC-002 | Unidade | `tests/test_state.py` | Passed |
| FR-002 | AC-003 | Unidade | `tests/test_state.py` | Passed |
| FR-002 | AC-004 | Unidade | `tests/test_antigravity_adapter.py` | Passed |
| FR-003 | AC-001 | Unidade | `tests/test_storage.py` | Passed |
| FR-003 | AC-002 | Unidade | `tests/test_storage.py` | Passed |
| FR-003 | AC-003 | Unidade | `tests/test_storage.py` | Passed |
| FR-003 | AC-004 | Unidade | `tests/test_storage.py` | Passed |
| NFR-001 | AC-001 | Integração | `PYTHONPATH=src python3 -m unittest discover tests` | Passed |
| NFR-001 | AC-002 | Integração | `PYTHONPATH=src python3 -m unittest discover tests` | Passed |
| NFR-001 | AC-003 | Integração | `PYTHONPATH=src python3 -m unittest discover tests` | Passed |
| NFR-001 | AC-004 | Integração | `PYTHONPATH=src python3 -m unittest discover tests` | Passed |

### 13. Validações

#### Gate do Ato I — Definição

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-04-validate/scripts/validate_spec.mjs specs/completed/0001-extracao-incremental-antigravity-para-markdown/spec.md`
- **Achados**: Nenhum blocker. Formato rígido Specsfy/2.0 e cobertura BDD integral (US-001, FR-001..FR-003, NFR-001 cobertos por 4 ACs).

#### Gate do Ato II — Plano

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-05-tasks/scripts/validate_tasks.mjs specs/completed/0001-extracao-incremental-antigravity-para-markdown/spec.md`
- **Achados**: Nenhum blocker. Todas as 3 tarefas TDD predecessores (T001, T002, T003) completas e com evidência RED observada, cobrindo integralmente todos os requisitos US-001, FR-001..FR-003, NFR-001 e AC-001..AC-004.

#### Gate do Ato III — Entrega

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-06-tdd-bdd/scripts/check_traceability.mjs specs/completed/0001-extracao-incremental-antigravity-para-markdown/spec.md .`
- **Achados**: Nenhum blocker. Todas as 7 tarefas concluídas, 11 testes passando (100% GREEN), 9/9 IDs com rastreabilidade plena, QA Passed e Evidence Contract 1 estritamente aprovado.

### 14. Tarefas

- [x] T001 [TEST] [TDD] [US-001] Criar testes unitários para StateManager e atomicidade em tests/test_state.py — Refs: US-001, FR-001, FR-002, FR-003, NFR-001, AC-001, AC-002, AC-003 — Depends: none
  - [x] **PREP**: Confirmar contratos de dados e chave composta de checkpoint.
  - [x] **EXECUTE**: Escrever casos de teste cobrindo criação, leitura e atomicidade.
  - [x] **VERIFY**: Executar teste e observar RED.
  - [x] **VISUAL**: Não aplicável — tarefa de teste e lógica sem interface visual.
  - [x] **EVIDENCE**: Registrar saída do teste e IDs cobertos.
  - [x] **IMPROVE**: Garantir limpeza de diretório temporário após cada teste.

- [x] T002 [TEST] [TDD] [US-001] Criar testes unitários para AntigravityAdapter e parsing em tests/test_antigravity_adapter.py — Refs: US-001, FR-001, FR-002, FR-003, NFR-001, AC-001, AC-002, AC-003, AC-004 — Depends: none
  - [x] **PREP**: Mapear amostras reais de transcripts JSONL do Antigravity.
  - [x] **EXECUTE**: Escrever casos de teste cobrindo descoberta mono/multi-usuário e resiliência a linhas inválidas.
  - [x] **VERIFY**: Executar teste e observar RED.
  - [x] **VISUAL**: Não aplicável — tarefa de teste de adaptador sem interface visual.
  - [x] **EVIDENCE**: Registrar saída do teste.
  - [x] **IMPROVE**: Refinar fixtures mockadas.

- [x] T003 [TEST] [TDD] [US-001] Criar testes para Markdown Storage e YAML frontmatter em tests/test_storage.py — Refs: US-001, FR-001, FR-002, FR-003, NFR-001, AC-001, AC-002, AC-003 — Depends: none
  - [x] **PREP**: Confirmar atributos requeridos para Live Queries do SilverBullet.
  - [x] **EXECUTE**: Escrever testes para escrita de arquivos .md e geração de frontmatter.
  - [x] **VERIFY**: Executar teste e observar RED.
  - [x] **VISUAL**: Não aplicável — teste de geração de arquivos Markdown sem interface visual.
  - [x] **EVIDENCE**: Registrar saída do teste.
  - [x] **IMPROVE**: Validar tratamento de caracteres especiais no YAML.

- [x] T004 [CODE] [US-001] Implementar models.py e state.py em src/chats2notes/state.py — Refs: US-001, FR-001, FR-002, FR-003, NFR-001, AC-001, AC-002, AC-003 — Depends: T001, T002, T003
  - [x] **PREP**: Confirmar classes Turn, Session e StateManager.
  - [x] **EXECUTE**: Codificar classes usando apenas a biblioteca padrão.
  - [x] **VERIFY**: Executar tests/test_state.py e observar GREEN.
  - [x] **VISUAL**: Não aplicável — módulo de dados em backend sem interface visual.
  - [x] **EVIDENCE**: Registrar GREEN do teste (3 testes passando em 0.009s).
  - [x] **IMPROVE**: Persistência atômica validada com os.replace e os.fsync.
  <!-- specsfy:evidence {"task": "T004", "refs": ["US-001", "FR-001", "FR-002", "FR-003", "NFR-001", "AC-001", "AC-002", "AC-003"], "files": ["src/chats2notes/models.py", "src/chats2notes/state.py"], "commands": [{"run": "PYTHONPATH=src python3 -m unittest tests/test_state.py", "exit": 0}]} -->

- [x] T005 [CODE] [US-001] Implementar base.py e antigravity.py em src/chats2notes/adapters/antigravity.py — Refs: US-001, FR-001, FR-002, FR-003, NFR-001, AC-001, AC-002, AC-003, AC-004 — Depends: T001, T002, T003, T004
  - [x] **PREP**: Confirmar assinatura de BaseAdapter e lógica de parsing de JSONL.
  - [x] **EXECUTE**: Implementar descoberta de sessões, multi-usuário e parsing resiliente.
  - [x] **VERIFY**: Executar tests/test_antigravity_adapter.py e observar GREEN.
  - [x] **VISUAL**: Não aplicável — adaptador de linha de comando sem interface visual.
  - [x] **EVIDENCE**: Registrar GREEN do teste (4 testes passando em 0.006s).
  - [x] **IMPROVE**: Suporte a caminhos multi-usuário em /home e limpeza de tags de sistema implementados.
  <!-- specsfy:evidence {"task": "T005", "refs": ["US-001", "FR-001", "FR-002", "FR-003", "NFR-001", "AC-001", "AC-002", "AC-003", "AC-004"], "files": ["src/chats2notes/adapters/base.py", "src/chats2notes/adapters/antigravity.py"], "commands": [{"run": "PYTHONPATH=src python3 -m unittest tests/test_antigravity_adapter.py", "exit": 0}]} -->

- [x] T006 [CODE] [US-001] Implementar storage.py e cli.py em src/chats2notes/storage.py — Refs: US-001, FR-001, FR-002, FR-003, NFR-001, AC-001, AC-002, AC-003 — Depends: T001, T002, T003, T004, T005
  - [x] **PREP**: Definir comandos argparse e formato do frontmatter YAML.
  - [x] **EXECUTE**: Implementar escritor de notas e ponto de entrada da CLI.
  - [x] **VERIFY**: Executar tests/test_storage.py e testes de integração CLI observando GREEN.
  - [x] **VISUAL**: Não aplicável — interface em linha de comando sem interface visual.
  - [x] **EVIDENCE**: Registrar comando de execução e saída (test_storage.py 3 testes OK, CLI operacional).
  - [x] **IMPROVE**: Mensagens amigáveis de resumo no terminal e tratamento de colisão de arquivos.
  <!-- specsfy:evidence {"task": "T006", "refs": ["US-001", "FR-001", "FR-002", "FR-003", "NFR-001", "AC-001", "AC-002", "AC-003"], "files": ["src/chats2notes/storage.py", "src/chats2notes/cli.py"], "commands": [{"run": "PYTHONPATH=src python3 -m unittest tests/test_storage.py", "exit": 0}]} -->

- [x] T007 [TEST] Executar suíte completa de testes e conferência de rastreabilidade em tests/test_cli.py — Refs: US-001, FR-001, FR-002, FR-003, NFR-001, AC-001, AC-002, AC-003, AC-004 — Depends: T004, T005, T006
  - [x] **PREP**: Verificar se todos os arquivos estão no lugar correto.
  - [x] **EXECUTE**: Rodar `PYTHONPATH=src python3 -m unittest discover tests`.
  - [x] **VERIFY**: Confirmar 100% de testes passando sem erros.
  - [x] **VISUAL**: Não aplicável — suíte de testes de terminal sem interface visual.
  - [x] **EVIDENCE**: Registrar saída de sucesso dos testes (11 testes OK, rastreabilidade 9/9 IDs OK).
  - [x] **IMPROVE**: Zero dependências externas comprovadas (uso estrito da stdlib Python).

### 15. Ordem de execução

- Caminho crítico: T001/T002/T003 → T004 → T005 → T006 → T007.
- Tarefas paralelas: T001, T002 e T003 podem ser preparadas em paralelo.
- Estratégia de MVP: Foco total na extração do Antigravity CLI para Markdown com persistência em SilverBullet Spaces e Obsidian Vaults.

### 16. Dependências, riscos e suposições

#### Dependências

- Python 3.10 ou superior disponível no ambiente do usuário.
- Acesso de leitura ao diretório `brain/` do Antigravity no sistema de arquivos.

#### Riscos

- Sessões com arquivos de log incompletos ou em andamento durante a execução → Mitigação: o leitor trata exceções de parsing JSON por linha e ignora turnos ainda incompletos.
- Permissão de acesso a diretórios de outros usuários no mesmo host → Mitigação: o scanner multi-usuário verifica `os.access` e ignora diretórios inacessíveis com aviso amigável sem interromper a execução.

#### Suposições

- O formato do log do Antigravity CLI mantém os tipos `USER_INPUT` e `PLANNER_RESPONSE` em linhas JSONL sequenciais.

### 17. Decisões

- **DEC-001**: Uso exclusivo da biblioteca padrão do Python 3 — eliminando dependência de `pip`, ambientes virtuais pesados e garantindo portabilidade imediata Linux/Windows.
- **DEC-002**: Formato de nota Markdown com Frontmatter YAML compatível nativamente com Live Queries do SilverBullet (`silverbullet.md`) e Dataview do Obsidian.
- **DEC-003**: Checkpoint atômico com isolamento por usuário (`host_user, session_id`), permitindo agregação multi-usuário sem risco de corrupção ou conflito.

### 18. Definition of Done

- [x] `Definition Gate` está `Passed`.
- [x] `Plan Gate` está `Passed`.
- [x] `Delivery Gate` está `Passed`.
- [x] Todos os cenários `AC` aplicáveis passam.
- [x] Todos os requisitos possuem evidência de verificação.
- [x] Todas as tarefas na seção 14 estão concluídas.
- [x] Testes e checks estáticos disponíveis passam.
