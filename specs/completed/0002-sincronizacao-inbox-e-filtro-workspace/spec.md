# Especificação integrada: Sincronização de logs para vault raw e filtro de workspace

| Campo | Valor |
| --- | --- |
| Formato | Specsfy/2.0 |
| ID | SPEC-0002 |
| Slug | 0002-sincronizacao-inbox-e-filtro-workspace |
| Status | Complete |
| Effort | 2 |
| Effort updated at | 2026-09-23 |
| Effort rationale | Sincronização de arquivos raw para raw local e filtragem de workspace via stdlib Python. |
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

Na arquitetura inicial, a extração gerava diretamente arquivos `.md` processados com notas pré-formatadas, sem manter os históricos brutos originais (`transcript_full.jsonl`) em uma pasta de entrada local (`vault/raw/`) como fonte da verdade controlada. Além disso, sem filtros de exclusão por projeto, conversas de curadoria, administração ou desenvolvimento do próprio `chats2notes` poderiam ser capturadas, gerando duplicação recursiva e poluição na base de conhecimento.

#### Resultado desejado

Estabelecer a primeira etapa da arquitetura em fases:
1. **Sincronização Raw**: O comando `chats2notes sync` copia com fidelidade integral e incremental os arquivos `transcript_full.jsonl` de cada sessão do `brain/` para `vault/raw/<user>/<session_id>/transcript_full.jsonl`, servindo como fonte da verdade local e marca de referência. O diretório `vault/raw` é estritamente imutável para processamento interno, mas sincronizado dinamicamente com as fontes externas caso chats continuem ativos no brain.
2. **Filtro de Exclusão de Workspace**: Permite ignorar automaticamente sessões cujo workspace coincida com o próprio repositório `chats2notes` ou com diretórios informados via `--ignore-workspace`.
3. **Preservação de Ideias**: Registro das ideias de Blacklist de sessões e Deduplicação por Hash em documentação para marcos futuros.

#### Métricas de sucesso

- 100% dos transcripts de sessões elegíveis sincronizados em formato íntegro para `vault/raw/`.
- 100% de exclusão de sessões cujo workspace corresponda aos caminhos ignorados.
- Zero dependências externas adicionadas (100% Python Standard Library).
- Idempotência absoluta: reexecuções consecutivas copiam apenas novos bytes ou sessões novas.

### 2. Research e esclarecimentos

#### Researchs executados

- **R-001**: O formato `transcript_full.jsonl` do Antigravity CLI é appended continuamente a cada interação. Conclusão: a sincronização incremental para o raw pode comparar tamanho de arquivo (`file_size`) e data de modificação (`mtime`), copiando somente quando há novos registros.

#### Fontes e contexto consultados

- Código fonte do `chats2notes` em `src/chats2notes/`.
- Estrutura de logs reais em `~/.gemini/antigravity-cli/brain/`.

#### Documentação consultada

- Biblioteca padrão do Python 3 (`shutil`, `pathlib`, `os`, `json`, `argparse`).

#### Artefatos de pesquisa armazenados

- Nenhum artefato externo além do código e logs locais do host.

#### Dúvidas respondidas

- **Q**: Os arquivos em vault/raw devem ser modificados ou pré-processados? → **A**: Não. Devem ser cópias exatas dos arquivos brutos para manter a fonte da verdade intacta para segmentação e curadorias posteriores. Internamente são imutáveis; externamente são sincronizados dinamicamente se o log crescer na fonte.
- **Q**: O diretório `vault/` deve ser versionado no Git? → **A**: Não, deve ser explicitamente ignorado no `.gitignore` para proteger a privacidade das conversas do usuário.
- **Q**: Como tratar as ideias de Blacklist de sessões e Deduplicação por Hash? → **A**: Devem ser registradas na documentação do projeto e backlog para avaliação em marcos futuros.

### 3. Escopo e atores

#### Incluído

- Módulo de sincronização incremental raw `RawSynchronizer` (com alias `InboxSynchronizer`) copiando `transcript_full.jsonl` de `brain/` para `vault/raw/`.
- Módulo de filtragem `WorkspaceFilter` que avalia se a sessão pertence a um workspace proibido (ex: `chats2notes` ou informado por CLI).
- Novo comando CLI `chats2notes sync` com opções `--brain-dir`, `--raw-dir` (alias `--inbox-dir`), `--ignore-workspace` e `--all-users`.
- Inclusão do diretório `/vault/` no `.gitignore`.
- Registro formal das ideias futuras (Blacklist e Deduplicação Hash) na documentação.

#### Fora de escopo

- Segmentação de pares e processamento por IA das notas (reservados para as fases seguintes).
- Blacklist por ID de sessão ou deduplicação por hash de conteúdo (documentados para marcos futuros).

#### Atores

- **Desenvolvedor / Usuário**: Executa o comando `sync` manual ou agendado para atualizar a fonte da verdade local no seu vault.

### 4. Princípios e restrições do projeto

- **PR-001**: Biblioteca padrão exclusiva do Python 3 (zero dependências externas).
- **PR-002**: Operações sobre `brain/` são estritamente somente leitura.
- **PR-003**: Cópia atômica e segura no raw (usando arquivos temporários ou write com flush antes de substituir).
- **PR-004**: Idempotência de sincronização (não recopia arquivos idênticos).

### 5. Histórias de usuário

#### US-001 — Extração incremental e curadoria de notas do Antigravity CLI (Baseline)

Como desenvolvedor que utiliza o Antigravity CLI, quero extrair turnos de conversas de IA para notas Markdown estruturadas no SilverBullet e Obsidian.

**Por que P1**: Representa a funcionalidade base de geração de notas.
**Teste independente**: Executar a CLI contra diretório de sessões e verificar a geração de arquivos .md.
**Requisitos**: FR-001, FR-002, FR-003, NFR-001

#### US-002 — Sincronização incremental para raw e filtro de workspace (P1)

Como desenvolvedor que utiliza o chats2notes, quero sincronizar os arquivos de log brutos do Antigravity para uma pasta local vault/raw/ e ignorar conversas do workspace do chats2notes, para manter uma cópia íntegra local e evitar loops de auto-ingestão de chats administrativos.

**Por que P1**: Estabelece a fonte da verdade local indispensável para as fases seguintes de segmentação e curadoria, prevenindo duplicação recursiva.
**Teste independente**: Executar `chats2notes sync` contra diretório com sessões variadas (incluindo workspace ignorado) e verificar que apenas as sessões elegíveis foram copiadas para `vault/raw/`.
**Requisitos**: FR-004, FR-005, FR-006, NFR-002

### 6. Cenários BDD de aceite

#### AC-001 — Extração inicial de novos turnos de uma sessão (Baseline)

**Cobre**: US-001, FR-001, FR-002, FR-003, NFR-001

```gherkin
@US-001 @FR-001 @FR-002 @FR-003 @NFR-001 @AC-001
Feature: Extração inicial de conversas
  Scenario: Processar uma sessão completa pela primeira vez
    Given um diretório brain com uma sessão
    When o comando de extração é executado
    Then notas Markdown são geradas
```

#### AC-002 — Idempotência incremental com checkpoint já existente (Baseline)

**Cobre**: US-001, FR-001, FR-002, FR-003, NFR-001

```gherkin
@US-001 @FR-001 @FR-002 @FR-003 @NFR-001 @AC-002
Feature: Idempotência incremental
  Scenario: Executar extração quando não há novas mensagens
    Given uma sessão já extraída
    When o comando de extração é executado novamente
    Then nenhuma nova nota é gerada
```

#### AC-003 — Descoberta e isolamento multi-usuário no mesmo host (Baseline)

**Cobre**: US-001, FR-001, FR-002, FR-003, NFR-001

```gherkin
@US-001 @FR-001 @FR-002 @FR-003 @NFR-001 @AC-003
Feature: Agregação multi-usuário
  Scenario: Processar múltiplos usuários
    Given múltiplos usuários configurados
    When a extração é executada
    Then os respectivos host_users são registrados
```

#### AC-004 — Resiliência a arquivos com linhas corrompidas (Baseline)

**Cobre**: US-001, FR-001, FR-002, FR-003, NFR-001

```gherkin
@US-001 @FR-001 @FR-002 @FR-003 @NFR-001 @AC-004
Feature: Resiliência de logs
  Scenario: Linha JSON corrompida
    Given um transcript com linha corrompida
    When o leitor processa o log
    Then as linhas válidas são extraídas
```

#### AC-005 — Sincronização inicial de transcript bruto para vault/raw

**Cobre**: US-002, FR-004, FR-005, FR-006, NFR-002

```gherkin
@US-002 @FR-004 @FR-005 @FR-006 @NFR-002 @AC-005
Feature: Sincronização inicial de logs brutos

  Scenario: Sincronizar sessão elegível para o raw
    Given que existe uma sessão válida no diretório brain do Antigravity
    And o workspace da sessão não está na lista de workspaces ignorados
    When o comando de sincronização para raw for executado
    Then uma cópia exata de transcript_full.jsonl deve existir em vault/raw/<user>/<session_id>/
    And o conteúdo deve ser idêntico ao original
```

#### AC-006 — Idempotência de sincronização sem novos dados

**Cobre**: US-002, FR-004, FR-005, FR-006, NFR-002

```gherkin
@US-002 @FR-004 @FR-005 @FR-006 @NFR-002 @AC-006
Feature: Idempotência de sincronização

  Scenario: Executar sincronização quando o log não mudou
    Given que uma sessão já foi sincronizada anteriormente para vault/raw
    And o arquivo transcript_full.jsonl original não sofreu alterações
    When o comando de sincronização for executado novamente
    Then nenhum arquivo deve ser recopiado desnecessariamente
    And a sincronização deve relatar zero arquivos atualizados
```

#### AC-007 — Exclusão de sessão com workspace ignorado

**Cobre**: US-002, FR-004, FR-005, FR-006, NFR-002

```gherkin
@US-002 @FR-004 @FR-005 @FR-006 @NFR-002 @AC-007
Feature: Filtro de exclusão de workspace

  Scenario: Ignorar sessão pertencente ao workspace do chats2notes
    Given que existe uma sessão cujo workspace é a pasta do chats2notes
    When o comando de sincronização for executado com o filtro de workspace ativo
    Then a sessão ignorada não deve ser sincronizada para vault/raw
    And nenhuma pasta para essa sessão deve ser criada no destino
```

#### AC-008 — Atualização incremental de sessão com novas mensagens

**Cobre**: US-002, FR-004, FR-005, FR-006, NFR-002

```gherkin
@US-002 @FR-004 @FR-005 @FR-006 @NFR-002 @AC-008
Feature: Atualização incremental

  Scenario: Sincronizar acréscimo de novas mensagens
    Given que uma sessão já foi sincronizada anteriormente
    And novas mensagens foram adicionadas ao final de transcript_full.jsonl no brain
    When o comando de sincronização for executado novamente
    Then o arquivo em vault/raw deve ser atualizado com as novas mensagens
    And a sincronização deve relatar 1 sessão atualizada
```

### 7. Requisitos

#### Funcionais

- **FR-001**: O sistema deve descobrir automaticamente diretórios de sessões do Antigravity CLI e suportar múltiplos diretórios de perfis/usuários no mesmo host.
- **FR-002**: O sistema deve ler incrementalmente os arquivos `transcript_full.jsonl` a partir da marca d'água persistida em `checkpoint.json`.
- **FR-003**: O sistema deve gerar arquivos de notas em Markdown com YAML frontmatter enriquecido (`name`, `tags`, `agent`, `host_user`, `workspace`, `session`, `created`, `category`).
- **FR-004**: O sistema deve sincronizar incrementalmente arquivos `transcript_full.jsonl` para o diretório de destino raw preservando o identificador da sessão e do usuário host.
- **FR-005**: O sistema deve filtrar e descartar sessões cujo workspace corresponda a um workspace ignorado configurado (como `chats2notes` ou caminhos passados em `--ignore-workspace`).
- **FR-006**: O sistema deve fornecer comando CLI `sync` dedicado (ou opção integrada) para executar a sincronização bruta para o raw e exibir sumário operacional.

#### Não funcionais

- **NFR-001**: O sistema deve ser executado exclusivamente sobre a biblioteca padrão do Python 3.10+, sem dependências externas adicionais.
- **NFR-002**: A sincronização deve ser atômica e não bloquear nem corromper os logs ativos do agente, utilizando exclusivamente a biblioteca padrão do Python 3 (sem bibliotecas externas). **Verificação**: Execução da suíte de testes com imports estritamente da stdlib.

#### Erros e casos-limite

- Permissão de leitura negada em uma pasta de sessão → Registrar aviso no console e prosseguir com as demais sessões sem interromper o processo.
- Diretório de raw inexistente → Criar automaticamente os diretórios pais necessários.
- Arquivo de origem bloqueado temporariamente por escrita do agente → Tratar exceções de IO e manter a versão anterior íntegra.

## Ato II — Projetar e provar

### 8. Plano técnico

#### Contexto existente

A base atual em `src/chats2notes/` possui o leitor de sessões `AntigravityAdapter` e o ponto de entrada `cli.py`. Vamos introduzir a capacidade de sincronização de arquivos brutos para o raw antes de qualquer processamento e o filtro de workspace.

#### Arquitetura e módulos

- `src/chats2notes/filter.py`: Classe `WorkspaceFilter` para correspondência de caminhos de workspace a ignorar.
- `src/chats2notes/sync.py`: Classe `RawSynchronizer` (com alias `InboxSynchronizer`) que coordena a cópia incremental segura de `transcript_full.jsonl` para `vault/raw/<user>/<session_id>/`.
- `src/chats2notes/cli.py`: Adição do comando `sync` com opções `--brain-dir`, `--raw-dir` (alias `--inbox-dir`), `--ignore-workspace`, `--all-users`.

#### Migrations

Não aplicável — persistência baseada em arquivos planos locais.

#### Models

- `SyncResult`: data class para contabilizar sessões examinadas, sincronizadas, ignoradas e erros.

#### Controllers e casos de uso

- `SyncUseCase`: orquestra a descoberta, filtragem por workspace e sincronização para o raw local.

#### Views e experiência

Não aplicável — interface em linha de comando (CLI) via terminal.

#### Queries e repositórios

- Leitura de diretórios via `pathlib.Path` e cópia segura de arquivos com `shutil.copy2` / streams de bytes.

#### Jobs e processamento assíncrono

Não aplicável — comandos síncronos da CLI.

#### Estrutura de arquivos

```text
src/
  chats2notes/
    filter.py
    sync.py
    cli.py
tests/
  test_filter.py
  test_sync.py
  test_sync_cli.py
```

### 9. Modelo de dados

Estrutura de diretórios no Raw:
```text
vault/raw/
  └── <host_user>/
      └── <session_id>/
          ├── session_info.json (metadados: workspace, host_user, updated_at)
          └── transcript_full.jsonl (cópia exata íntegra)
```

### 10. Interfaces e contratos

Comando CLI adicionado:
```bash
chats2notes sync [--brain-dir PATH] [--raw-dir PATH] [--ignore-workspace PATH] [--all-users]
```

### 11. Estratégia TDD

- **Runner**: `python3 -m unittest discover tests`.
- Testes cobrindo sincronização raw, idempotência, filtro de workspace e ponto de entrada da CLI.

#### Evidência RED-GREEN-REFACTOR

| IDs | BDD de referência | Teste TDD informado pelo BDD | RED observado | GREEN observado | Refactor/regressão |
| --- | --- | --- | --- | --- | --- |
| US-002, FR-004, FR-005, FR-006, NFR-002, AC-005 | AC-005 na seção 6 | `tests/test_sync.py:TestSync.test_initial_sync` | NotImplementedError: InboxSynchronizer.sync_session not implemented yet | Ran 3 tests in 0.009s OK | PYTHONPATH=src python3 -m unittest discover tests (20 tests OK) |
| US-002, FR-004, FR-005, FR-006, NFR-002, AC-006 | AC-006 na seção 6 | `tests/test_sync.py:TestSync.test_idempotent_sync` | NotImplementedError: InboxSynchronizer.sync_session not implemented yet | Ran 3 tests in 0.009s OK | PYTHONPATH=src python3 -m unittest discover tests (20 tests OK) |
| US-002, FR-004, FR-005, FR-006, NFR-002, AC-007 | AC-007 na seção 6 | `tests/test_filter.py:TestFilter.test_ignore_workspace` | NotImplementedError: WorkspaceFilter.should_ignore not implemented yet | Ran 3 tests in 0.001s OK | PYTHONPATH=src python3 -m unittest discover tests (20 tests OK) |
| US-002, FR-004, FR-005, FR-006, NFR-002, AC-008 | AC-008 na seção 6 | `tests/test_sync.py:TestSync.test_incremental_append_sync` | NotImplementedError: InboxSynchronizer.sync_session not implemented yet | Ran 3 tests in 0.009s OK | PYTHONPATH=src python3 -m unittest discover tests (20 tests OK) |

### 12. Plano de testes e rastreabilidade

| Requisito | Cenário BDD | Nível | Arquivo/comando esperado | Evidência |
| --- | --- | --- | --- | --- |
| FR-001 | AC-001 | Unidade | `tests/test_adapter.py` | Passed |
| FR-002 | AC-002 | Unidade | `tests/test_state.py` | Passed |
| FR-001 | AC-003 | Unidade | `tests/test_adapter.py` | Passed |
| FR-002 | AC-004 | Unidade | `tests/test_adapter.py` | Passed |
| FR-004 | AC-005 | Unidade | `tests/test_sync.py` | Passed |
| FR-004 | AC-006 | Unidade | `tests/test_sync.py` | Passed |
| FR-004 | AC-008 | Unidade | `tests/test_sync.py` | Passed |
| FR-005 | AC-005 | Unidade | `tests/test_filter.py` | Passed |
| FR-005 | AC-007 | Unidade | `tests/test_filter.py` | Passed |
| FR-005 | AC-008 | Unidade | `tests/test_filter.py` | Passed |
| FR-006 | AC-005 | Integração | `tests/test_sync_cli.py` | Passed |
| FR-006 | AC-006 | Integração | `tests/test_sync_cli.py` | Passed |
| FR-006 | AC-007 | Integração | `tests/test_sync_cli.py` | Passed |
| NFR-002 | AC-005 | Unidade | `PYTHONPATH=src python3 -m unittest discover tests` | Passed |
| NFR-002 | AC-006 | Unidade | `PYTHONPATH=src python3 -m unittest discover tests` | Passed |
| NFR-002 | AC-007 | Unidade | `PYTHONPATH=src python3 -m unittest discover tests` | Passed |

### 13. Validações

#### Gate do Ato I — Definição

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-04-validate/scripts/validate_spec.mjs specs/defined/0002-sincronizacao-inbox-e-filtro-workspace/spec.md`
- **Achados**: Nenhum blocker. Formato rígido Specsfy/2.0 e cobertura BDD integral (US-002, FR-004..FR-006, NFR-002 cobertos por 4 ACs).

#### Gate do Ato II — Plano

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-05-tasks/scripts/validate_tasks.mjs specs/completed/0002-sincronizacao-inbox-e-filtro-workspace/spec.md`
- **Achados**: 7 tarefas com decomposição canônica, 3 predecessores TDD concluídos com RED observado e rastreabilidade estrita.

#### Gate do Ato III — Entrega

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-06-tdd-bdd/scripts/check_traceability.mjs specs/completed/0002-sincronizacao-inbox-e-filtro-workspace/spec.md .`
- **Achados**: 100% dos testes passando (20/20), 18/18 IDs cobertos, evidências estritas aprovadas sem blockers.

### 14. Tarefas

- [x] T008 [TEST] [TDD] [US-002] Criar testes de sincronização bruta e idempotência em tests/test_sync.py — Refs: US-001, US-002, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-008 — Depends: none
  - [x] **PREP**: Mapear comportamento de cópia exata de arquivos e preservação de metadados.
  - [x] **EXECUTE**: Escrever testes para cópia inicial, idempotência e atualização incremental.
  - [x] **VERIFY**: Executar teste e observar falha esperada (RED).
  - [x] **VISUAL**: Não aplicável — teste de sincronização de arquivos em backend sem interface gráfica.
  - [x] **EVIDENCE**: Registrar saída do teste.
  - [x] **IMPROVE**: Garantir limpeza dos diretórios temporários.

- [x] T009 [TEST] [TDD] [US-002] Criar testes para filtro de exclusão por workspace em tests/test_filter.py — Refs: US-001, US-002, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, AC-001, AC-002, AC-003, AC-004, AC-005, AC-007, AC-008 — Depends: none
  - [x] **PREP**: Definir regras de matching de caminhos de workspace exatos e parciais.
  - [x] **EXECUTE**: Escrever testes cobrindo exclusão de chats2notes e workspaces customizados.
  - [x] **VERIFY**: Executar teste e observar falha esperada (RED).
  - [x] **VISUAL**: Não aplicável — teste de lógica de filtragem sem interface visual.
  - [x] **EVIDENCE**: Registrar saída do teste.
  - [x] **IMPROVE**: Testar caminhos relativos e absolutos com resolução canônica.

- [x] T010 [TEST] [TDD] [US-002] Criar testes de integração para comando sync na CLI em tests/test_sync_cli.py — Refs: US-001, US-002, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007 — Depends: none
  - [x] **PREP**: Definir argumentos de linha de comando para o comando sync.
  - [x] **EXECUTE**: Escrever testes de ponta a ponta chamando CLI sync e checando vault/inbox.
  - [x] **VERIFY**: Executar teste e observar falha esperada (RED).
  - [x] **VISUAL**: Não aplicável — teste de comando de terminal sem interface visual.
  - [x] **EVIDENCE**: Registrar saída do teste.
  - [x] **IMPROVE**: Validar mensagens informativas emitidas pela CLI.

<!-- specsfy:evidence {"task": "T011", "refs": ["US-001", "US-002", "FR-001", "FR-002", "FR-003", "FR-004", "FR-005", "FR-006", "NFR-001", "NFR-002", "AC-001", "AC-002", "AC-003", "AC-004", "AC-005", "AC-006", "AC-008"], "files": ["src/chats2notes/sync.py"], "commands": [{"run": "PYTHONPATH=src python3 -m unittest tests/test_sync.py", "exit": 0}]} -->
- [x] T011 [CODE] [US-002] Implementar InboxSynchronizer em src/chats2notes/sync.py — Refs: US-001, US-002, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-008 — Depends: T008, T009, T010
  - [x] **PREP**: Confirmar classes e métodos de cópia incremental.
  - [x] **EXECUTE**: Codificar InboxSynchronizer usando shutil e pathlib.
  - [x] **VERIFY**: Executar tests/test_sync.py e observar GREEN.
  - [x] **VISUAL**: Não aplicável — módulo de backend sem interface visual.
  - [x] **EVIDENCE**: Registrar GREEN do teste.
  - [x] **IMPROVE**: Implementar cópia atômica com arquivo temporário e os.replace.

<!-- specsfy:evidence {"task": "T012", "refs": ["US-001", "US-002", "FR-001", "FR-002", "FR-003", "FR-004", "FR-005", "FR-006", "NFR-001", "NFR-002", "AC-001", "AC-002", "AC-003", "AC-004", "AC-005", "AC-007", "AC-008"], "files": ["src/chats2notes/filter.py"], "commands": [{"run": "PYTHONPATH=src python3 -m unittest tests/test_filter.py", "exit": 0}]} -->
- [x] T012 [CODE] [US-002] Implementar WorkspaceFilter em src/chats2notes/filter.py — Refs: US-001, US-002, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, AC-001, AC-002, AC-003, AC-004, AC-005, AC-007, AC-008 — Depends: T008, T009, T010, T011
  - [x] **PREP**: Definir lista padrão de exclusão incluindo chats2notes.
  - [x] **EXECUTE**: Codificar WorkspaceFilter e integrar na descoberta de sessões.
  - [x] **VERIFY**: Executar tests/test_filter.py e observar GREEN.
  - [x] **VISUAL**: Não aplicável — módulo de filtragem sem interface visual.
  - [x] **EVIDENCE**: Registrar GREEN do teste.
  - [x] **IMPROVE**: Normalização de caminhos com resolve() e case sensitivity no Linux.

<!-- specsfy:evidence {"task": "T013", "refs": ["US-001", "US-002", "FR-001", "FR-002", "FR-003", "FR-004", "FR-005", "FR-006", "NFR-001", "NFR-002", "AC-001", "AC-002", "AC-003", "AC-004", "AC-005", "AC-006", "AC-007"], "files": ["src/chats2notes/cli.py"], "commands": [{"run": "PYTHONPATH=src python3 -m unittest tests/test_sync_cli.py", "exit": 0}]} -->
- [x] T013 [CODE] [US-002] Integrar comando sync na CLI em src/chats2notes/cli.py — Refs: US-001, US-002, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007 — Depends: T008, T009, T010, T011, T012
  - [x] **PREP**: Adicionar subparser sync com argumentos --inbox-dir e --ignore-workspace.
  - [x] **EXECUTE**: Conectar comando sync a WorkspaceFilter e InboxSynchronizer.
  - [x] **VERIFY**: Executar tests/test_sync_cli.py e observar GREEN.
  - [x] **VISUAL**: Não aplicável — interface em linha de comando sem interface visual.
  - [x] **EVIDENCE**: Registrar comando e saída.
  - [x] **IMPROVE**: Exibir resumo elegante com sessões sincronizadas e ignoradas.

- [x] T014 [TEST] Executar suíte completa de regressão e conferência de rastreabilidade em tests/test_sync_cli.py — Refs: US-001, US-002, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008 — Depends: T011, T012, T013
  - [x] **PREP**: Verificar se todos os arquivos estão no lugar correto.
  - [x] **EXECUTE**: Rodar `PYTHONPATH=src python3 -m unittest discover tests`.
  - [x] **VERIFY**: Confirmar 100% de testes passando sem erros e zero dependências.
  - [x] **VISUAL**: Não aplicável — suíte de testes de terminal sem interface visual.
  - [x] **EVIDENCE**: Registrar saída de sucesso dos testes.
  - [x] **IMPROVE**: Conferir integridade de rastreabilidade no check_traceability.mjs.

### 15. Ordem de execução

- Caminho crítico: T008/T009/T010 → T011 → T012 → T013 → T014.
- Setup: T008, T009 e T010 criam os testes TDD para a nova capacidade.

### 16. Dependências, riscos e suposições

#### Dependências

- Python 3.10+ stdlib.
- Permissão de leitura nos diretórios `brain/` e de escrita em `vault/raw/`.

#### Riscos

- Logs em gravação ativa pelo agente → Mitigação: leitura segura e tratamento de erros parciais.

#### Suposições

- O diretório `vault/` está no `.gitignore`.

### 17. Decisões

- **DEC-004**: Adoção de arquitetura com repositório de entrada raw em `vault/raw/`, servindo como fonte da verdade íntegra e sincronizada dinamicamente com brains externos, para posterior segmentação em pares e curadoria em `vault/notas/`.
- **DEC-005**: Exclusão ativa de sessões do workspace `chats2notes` e diretórios ignorados para impedir auto-ingestão e recursão.
- **DEC-006**: Preservação das ideias de Blacklist de sessões e Deduplicação por Hash em backlog/documentação para marcos posteriores.

### 18. Definition of Done

- [x] `Definition Gate` está `Passed`.
- [x] `Plan Gate` está `Passed`.
- [x] `Delivery Gate` está `Passed`.
- [x] Todos os cenários `AC` aplicáveis passam.
- [x] Todos os requisitos possuem evidência de verificação.
- [x] Todas as tarefas na seção 14 estão concluídas.
- [x] Testes e checks estáticos disponíveis passam.
