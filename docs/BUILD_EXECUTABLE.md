# 🚀 Como Criar o Executável do SectorFlow

## Pré-requisitos

1. **Python 3.10+** instalado
2. **PyInstaller** instalado:
   ```bash
   pip install pyinstaller
   ```

## 🔨 Criar Executável

### Método 1: Script Automático (Recomendado)

```bash
python scripts\build_exe.py
```

Este script irá:
- ✅ Limpar builds anteriores
- ✅ Criar executável único (onefile)
- ✅ Incluir todos os recursos necessários (imagens, settings, etc.)
- ✅ Configurar ícone da aplicação
- ✅ Otimizar tamanho removendo módulos desnecessários

### Método 2: PyInstaller Manual

```bash
pyinstaller --name SectorFlow ^
            --onefile ^
            --windowed ^
            --icon images\icon\Logo.png ^
            --add-data "images;images" ^
            --add-data "settings;settings" ^
            --add-data "brandlogo;brandlogo" ^
            --hidden-import pyRfactor2SharedMemory ^
            --hidden-import PySide6.QtCore ^
            --hidden-import PySide6.QtGui ^
            --hidden-import PySide6.QtWidgets ^
            run.py
```

## 📦 Resultado

Após a compilação, o executável estará em:

```
dist/
└── SectorFlow.exe    (executável único)
```

## ▶️ Executar

```bash
cd dist
.\SectorFlow.exe
```

## 🗂️ Arquivos Necessários para Distribuição

O executável precisa estar na mesma estrutura de diretórios:

```
SectorFlow/
├── SectorFlow.exe       ← Executável
├── settings/            ← Configurações JSON
├── brandlogo/           ← Logos de marcas (opcional)
├── images/              ← Ícones e imagens
└── logs/                ← Logs (criado automaticamente)
```

## 🔧 Solução de Problemas

### Erro: "Cannot find Logo.png"
- Certifique-se que o arquivo `images/icon/Logo.png` existe
- Ou remova a opção `--icon` do comando

### Erro: "Module not found"
- Adicione o módulo com `--hidden-import nome_modulo`

### Executável muito grande
- Use `--onefile` para criar um único arquivo
- Remova módulos desnecessários com `--exclude-module`

### Antivírus bloqueia o executável
- Crie exceção no antivírus para a pasta `dist/`
- Use certificado digital para assinar o executável (produção)

## 📝 Notas

- **Primeira execução**: Pode demorar alguns segundos para extrair arquivos
- **Logs**: Salvos em `logs/sectorflow.log`
- **Configurações**: Salvas em `settings/`
- **Idioma**: Português BR por padrão

## 🌐 Tradução de Menus

Os menus já estão traduzidos para Português Brasileiro:

- ✅ Travar Overlay
- ✅ Ocultar Automaticamente  
- ✅ Movimento em Grade
- ✅ Compatibilidade VR
- ✅ Recarregar
- ✅ Reiniciar API
- ✅ Resetar Dados
- ✅ Configuração
- ✅ Ferramentas
- ✅ Ajuda

## 🎯 Próximos Passos

1. Teste o executável em máquina limpa (sem Python instalado)
2. Crie instalador com NSIS ou Inno Setup (opcional)
3. Distribua o executável com README e LICENSE
