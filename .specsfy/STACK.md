# Stack do sistema

Documente tecnologias estruturais e a evidência executável que confirma cada
uma. Preserve decisões humanas nas seções livres deste arquivo.

## Inventário detectado

<!-- specsfy:stack:start -->
| Camada | Tecnologia | Evidência |
| --- | --- | --- |
| Linguagem / Núcleo | Python 3 (Standard Library) | Decisão de setup / `README.md` |
| Testes | Python unittest | Decisão de setup |
| Formato de Dados | JSON / JSONL / Markdown com YAML | `README.md` |
| Gestão do Framework | Node.js / Specsfy | `package.json` |
<!-- specsfy:stack:end -->

## Decisões e observações do projeto

- **Arquitetura Zero-Dependencies**: O núcleo de extração, gerenciamento de checkpoints e geração de notas em Markdown é construído exclusivamente sobre a biblioteca padrão do Python (`pathlib`, `json`, `urllib.request`, `argparse`, `unittest`, `dataclasses`), garantindo execução imediata sem necessidade de instalação de pacotes (`pip`/`venv`) no Linux ou Windows.
- **Ecossistema Node.js**: Utilizado apenas pelas ferramentas de documentação e skills do Specsfy (`package.json`), sem acoplamento ao executável da ferramenta.
