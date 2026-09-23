# Pesquisa: Convenções de Frontmatter e Live Queries do SilverBullet

## 1. Contexto e Referência

O **SilverBullet** é um ambiente de anotações e gestão de conhecimento pessoal (PKM) extensível e baseado em arquivos Markdown abertos. O SilverBullet trata cada página Markdown como uma entidade consultável através de seu mecanismo nativo de **Live Queries**.

## 2. Padrões de Frontmatter YAML

No SilverBullet, os atributos declarados no frontmatter YAML do topo da página tornam-se propriedades diretamente acessíveis na linguagem de consulta de páginas:

```yaml
---
name: "Como configurar SSH no Debian"
tags:
  - faq
  - linux
  - debian
  - ssh
project: null
created: "2026-09-23 15:40:00"
chat_date: "2026-09-23 13:10:00"
segment_ref: "vault/segments/thiago/sess_1/0001.md"
related_notes: []
source: "antigravity"
---
```

## 3. Consultas Dinâmicas (Live Queries)

Exemplos de Live Queries utilizadas pelos usuários no SilverBullet:

```markdown
<!-- Listar todas as notas de FAQ -->
```query
page where contains(tags, "faq") order by created desc render [[Library/Core/Query/Table]]
```

<!-- Listar notas associadas a um projeto específico -->
```query
page where project = "chats2notes" render [[Library/Core/Query/Table]]
```
```

## 4. Convenção de Nomes e Estrutura Plana

- **Nome da Página = Nome do Arquivo**: O SilverBullet nomeia a página a partir do nome do arquivo no disco (ex: `Como configurar SSH no Debian.md` vira `[[Como configurar SSH no Debian]]`). Nomes com espaços e em Title Case são o formato nativo recomendado.
- **Estrutura Plana**: Uma pasta plana como `vault/notas/` evita caminhos complexos nos links e delega a organização para os atributos do YAML (`tags`, `project`), permitindo consultas transversais limpas.
