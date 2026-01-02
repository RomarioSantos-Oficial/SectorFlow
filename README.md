# 🏎️ SectorFlow

**Aplicação de telemetria overlay para simulação de corrida.**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)

---

## 📖 Sobre o Projeto

**SectorFlow** é uma aplicação de telemetria overlay para simuladores de corrida, focada principalmente em **rFactor 2**. 

> 🙏 **Baseado no [TinyPedal](https://github.com/s-victor/TinyPedal)** - um projeto open source desenvolvido por TinyPedal developers. O SectorFlow foi criado a partir do código do TinyPedal e modificado para atender necessidades específicas de telemetria e visualização.

### Informações em Tempo Real:
- ⏱️ Delta times e setores
- ⛽ Gestão de combustível e energia
- 🛞 Temperatura e desgaste de pneus
- 🚦 Telemetria de freios
- 📊 Classificação com contagem de voltas por categoria
- 🗺️ Mapas de pista
- 🔋 Monitoramento de sistemas híbridos
- E muito mais...

---

## 🚀 Instalação

### Opção 1: Executável (Recomendado)

1. Baixe o arquivo `SectorFlow.exe`
2. Coloque em uma pasta de sua preferência
3. Execute o `SectorFlow.exe`
4. Inicie o rFactor 2 e aproveite!

### Opção 2: Código Fonte

**Pré-requisitos:**
- Python 3.9 ou superior
- Windows 10/11

**Passos:**

```bash
# Clone ou baixe o repositório
git clone <repository-url>
cd SectorFlow

# Crie um ambiente virtual (opcional mas recomendado)
python -m venv venv
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python run.py
```

---

## 🎮 Como Usar

### Primeira Execução

1. Execute o `SectorFlow.exe` ou `python run.py`
2. Um ícone aparecerá na bandeja do sistema (system tray)
3. Clique com botão direito no ícone para acessar o menu
4. Vá em **Configuração** para personalizar os widgets
5. Ative os widgets desejados na aba **Widget**
6. Inicie o rFactor 2 - os overlays aparecerão automaticamente

### Widgets Disponíveis

| Widget | Descrição |
|--------|-----------|
| **Standings Hybrid** | Classificação com posição, logo da marca, tempo, gap, energia e voltas por categoria |
| **Delta Best** | Comparação de tempo com sua melhor volta |
| **Fuel & Energy** | Consumo de combustível e bateria |
| **Tire Monitor** | Temperatura, pressão e desgaste dos pneus |
| **Brake System** | Temperatura e performance dos freios |
| **Track Map** | Mapa da pista com posições dos carros |
| **Laps & Position** | Volta atual e posição na corrida |
| **Weather** | Condições meteorológicas |

### Recursos do Standings Hybrid

O widget de classificação mostra:
- **Cabeçalho por categoria**: Nome da classe, quantidade de carros e **contagem de voltas**
  - Em corrida: `Volta: 5/20` (atual/total) ou `Volta: 5/12.3` (previsão em corridas por tempo)
  - Em quali/prática: `Volta: 3` (apenas volta atual)
- **Logo da marca** do carro
- **Número do carro**
- **Nome do piloto**
- **Melhor volta e última volta**
- **Gap** para o líder ou carro à frente
- **Porcentagem de bateria** (para carros híbridos)
- **Bandeira quadriculada** quando um piloto termina a corrida

### Presets

Você pode criar múltiplos presets (layouts) e alternar entre eles:
1. Configure os widgets como desejado
2. Salve o preset com um nome
3. Troque rapidamente entre presets pelo menu

---

## 🛠️ Compilando o Executável

Para criar seu próprio executável:

```bash
# Instale o PyInstaller
pip install pyinstaller

# Compile
pyinstaller --onefile --windowed --name SectorFlow --icon=brandlogo/Logo.ico run.py --add-data "images;images" --add-data "brandlogo;brandlogo" --add-data "deltabest;deltabest" --add-data "settings;settings" --noconfirm

# O executável estará em dist/SectorFlow.exe
```

---

## 🔧 Modificações e Personalização

Este projeto é **open source** e você é livre para modificá-lo!

### Você pode:
- ✅ Modificar o código para uso pessoal
- ✅ Adicionar novos widgets
- ✅ Personalizar cores e estilos
- ✅ Adaptar para outros simuladores
- ✅ Contribuir com melhorias

### Estrutura do Projeto

```
SectorFlow/
├── run.py                 # Ponto de entrada da aplicação
├── validadorers/          # Código principal
│   ├── adapter/          # Conectores de API (rF2)
│   ├── module/           # Módulos de dados
│   ├── ui/               # Interface gráfica
│   └── widget/           # Widgets de overlay
├── images/               # Imagens e ícones
├── brandlogo/            # Logos das marcas de carros
├── deltabest/            # Dados salvos de delta times
└── settings/             # Configurações
```

### Dicas para Desenvolvedores

- Os widgets ficam em `validadorers/widget/`
- A API do rFactor 2 é acessada via `api.read.*`
- Configurações são carregadas via `self.wcfg`
- Use `PySide6` para interface gráfica

---

## 📝 Licença

Este projeto é licenciado sob a **GNU General Public License v3.0**.

**Baseado no TinyPedal** - Copyright © 2022-2025 TinyPedal developers

Você pode:
- ✅ Modificar para uso pessoal
- ✅ Estudar o código
- ✅ Uso privado

**Restrições:**
- ❌ Uso comercial não autorizado
- ❌ Redistribuição sem permissão

Desde que:
- Mantenha o código fonte aberto
- Inclua a licença original
- Documente as mudanças

Veja o arquivo [LICENSE](LICENSE) para detalhes completos.

---

## 🙏 Créditos

- **[TinyPedal](https://github.com/s-victor/TinyPedal)** - Projeto original que serviu de base
- **TinyPedal developers** - Pelo excelente trabalho no código original
- **Comunidade rFactor 2** - Pelo suporte e feedback

---

## 📧 Suporte

Encontrou um bug? Tem uma sugestão? Abra uma issue no repositório!

---

**SectorFlow** - Feito com ❤️ para a comunidade de sim racing
