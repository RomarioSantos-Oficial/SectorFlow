# Contribuindo para o SectorFlow

Obrigado por considerar contribuir para o SectorFlow! 🎉

## Como Contribuir

### Reportando Bugs

1. Verifique se o bug já foi reportado nas [Issues](../../issues)
2. Se não, crie uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Screenshots (se aplicável)
   - Versão do Python e do sistema operacional
   - Logs relevantes

### Sugerindo Melhorias

1. Verifique se a sugestão já existe nas issues
2. Crie uma issue descrevendo:
   - O que você gostaria de adicionar/mudar
   - Por que isso seria útil
   - Como poderia funcionar

### Pull Requests

1. **Fork** o repositório
2. **Clone** seu fork
3. Crie uma **branch** para sua feature:
   ```bash
   git checkout -b feature/minha-feature
   ```
4. Faça suas alterações seguindo as diretrizes de código
5. **Teste** suas mudanças
6. **Commit** com mensagens descritivas:
   ```bash
   git commit -m "feat: adiciona widget de temperatura do motor"
   ```
7. **Push** para seu fork:
   ```bash
   git push origin feature/minha-feature
   ```
8. Abra um **Pull Request**

## Diretrizes de Código

### Estilo Python

- Siga **PEP 8**
- Máximo de **88 caracteres por linha** (compatível com Black)
- Use **type hints** onde possível
- Documente funções e classes com **docstrings**

Exemplo:
```python
def calcular_delta(tempo_atual: float, tempo_melhor: float) -> float:
    """Calcula o delta entre tempos.
    
    Args:
        tempo_atual: Tempo da volta atual em segundos.
        tempo_melhor: Melhor tempo em segundos.
        
    Returns:
        Diferença de tempo em segundos.
    """
    return tempo_atual - tempo_melhor
```

### Formatação Automática

Use as ferramentas de formatação:

```bash
# Black (formatação)
black validadorers/

# Flake8 (linting)
flake8 validadorers/

# isort (importações)
isort validadorers/
```

### Commits

Use mensagens de commit semânticas:

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` mudanças na documentação
- `style:` formatação, espaços, etc.
- `refactor:` refatoração de código
- `test:` adiciona ou modifica testes
- `chore:` tarefas de manutenção

Exemplo: `feat: adiciona suporte para ACC telemetry API`

### Testes

- Teste suas mudanças antes de submeter
- Adicione testes para novas funcionalidades
- Verifique que todos os testes existentes passam

### Documentação

- Atualize o README.md se necessário
- Documente novas features no wiki
- Comente código complexo
- Mantenha docstrings atualizadas

## Estrutura do Projeto

```
validadorers/
├── adapter/        # Conectores de API
├── module/         # Módulos de processamento
├── process/        # Processos de cálculo
├── template/       # Templates de configuração
├── ui/             # Interface gráfica
├── userfile/       # Arquivos de usuário
└── widget/         # Widgets de overlay
```

### Adicionando um Novo Widget

1. Crie arquivo em `validadorers/widget/seu_widget.py`
2. Herde de `_base.py`
3. Implemente métodos necessários
4. Adicione ao `__init__.py`
5. Crie template de configuração em `template/`
6. Documente no README

## Internacionalização (i18n)

### Adicionando Novas Traduções

O SectorFlow suporta múltiplos idiomas. Para adicionar novas traduções:

1. Abra `validadorers/i18n.py`
2. Adicione as traduções no dicionário `_translations`:

```python
"nova_chave": {
    Language.PT_BR: "Texto em Português",
    Language.EN_US: "Text in English"
}
```

3. Use a função `_()` no código:

```python
from ..i18n import _

text = _("nova_chave")
```

### Idiomas Suportados

- 🇧🇷 Português (Brasil) - `pt_BR` (padrão)
- 🇺🇸 English (US) - `en_US`

### Alterando o Idioma

Edite `language_config.json` ou use a interface da aplicação para mudar o idioma.

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite feedback construtivo
- Foque no que é melhor para a comunidade
- Demonstre empatia com outros membros

## Dúvidas?

- Abra uma [issue de discussão](../../issues)
- Entre em contato com os mantenedores

---

**Obrigado por contribuir! 🚀**
