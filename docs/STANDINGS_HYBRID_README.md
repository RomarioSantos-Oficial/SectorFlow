# 🏁 Standings Hybrid Widget - Documentação

## 📋 Visão Geral

O **Standings Hybrid Widget** é um overlay avançado para o SectorFlow que exibe a classificação da corrida com **detecção dinâmica automática de sistemas híbridos**. Ele funciona perfeitamente em grids mistos (por exemplo, Hypercars + GT3s) e exibe informações diferentes dependendo se cada veículo possui sistema híbrido ou não.

## ✨ Recursos Principais

### 🔍 Detecção Dinâmica de Sistemas Híbridos

O widget implementa detecção **inteligente e automática** de sistemas híbridos:

- ✅ **Verifica automaticamente** se cada veículo tem capacidade de energia virtual (`mVirtualEnergyMax`)
- ✅ **Funciona em grids mistos** - cada linha é tratada independentemente
- ✅ **Mostra `--`** para veículos sem sistema híbrido (GT3, GTE, etc.)
- ✅ **Mostra porcentagem** para veículos com sistema híbrido (LMDh, LMH, F1, etc.)
- ✅ **Tratamento robusto de erros** - valores NaN, None ou inválidos são exibidos como `--`

### 📊 Colunas Exibidas

| Coluna | Descrição |
|--------|-----------|
| **Pos** | Posição na corrida (01, 02, 03...) |
| **Logo** | Logo da marca do veículo |
| **CL** | Classe do veículo (HY, GT3, LMP2, etc.) |
| **Piloto** | Nome do piloto (encurtado conforme configuração) |
| **Best Lap** | Melhor tempo de volta |
| **Gap** | Diferença de tempo para o líder |
| **Ener.** | **Energia híbrida (% ou --)** |

### 🎯 Detecção Automática - Como Funciona

```python
# Para cada veículo no grid:
max_energy = api.read.vehicle.max_virtual_energy(index)

if max_energy > 0:
    # ✅ Sistema híbrido detectado!
    # Calcular e exibir porcentagem
    current_energy = api.read.vehicle.virtual_energy(index)
    energy_percent = (current_energy / max_energy) * 100
    display = f"{int(energy_percent)}%"
else:
    # ❌ Sem sistema híbrido
    display = "--"
```

## 🎨 Cores e Estilos

### Estados de Energia

- **🟢 Verde** (`#00FF00`) - Energia normal (> 25%)
- **🟠 Laranja** (`#FFAA00`) - Energia baixa (10-25%)
- **🔴 Vermelho** (`#FF0000`) - Energia crítica (< 10%)
- **⚪ Branco** (`--`) - Sem sistema híbrido

### Destaque do Jogador

- Todas as colunas do jogador são destacadas com fundo **amarelo** (`#FFCC00`)
- Texto em **preto** para máximo contraste

## ⚙️ Configuração

### Arquivo: `setting_widget.py`

```python
"standings_hybrid": {
    "enable": False,  # Ative para usar
    "update_interval": 100,
    "position_x": 100,
    "position_y": 100,
    "opacity": 0.9,
    "font_name": "Consolas",
    "font_size": 15,
    "max_vehicles": 20,  # Máximo de veículos exibidos
    "driver_name_width": 12,  # Largura do nome do piloto
    "brand_logo_width": 30,  # Largura do logo
    "class_width": 4,  # Largura da classe
    "time_gap_width": 7,  # Largura do gap
    "energy_width": 4,  # Largura da coluna de energia
    "energy_low_threshold": 25,  # Limite para "baixo" (%)
    "energy_critical_threshold": 10,  # Limite para "crítico" (%)
    # ... cores personalizáveis ...
}
```

## 🚀 Como Usar

### 1. Ativar o Widget

1. Abra o SectorFlow
2. Vá para a aba **"Widget"**
3. Encontre **"standings_hybrid"** na lista
4. Marque a caixa **"Enable"**
5. Clique em **"Apply"** ou **"Save"**

### 2. Personalizar Posição

- Arraste o overlay para a posição desejada
- Use **Grid Move** para ajuste fino
- **Lock** para travar a posição

### 3. Ajustar Configurações

Na aba de configuração do widget, você pode ajustar:
- Número de veículos exibidos
- Largura das colunas
- Cores personalizadas
- Limites de energia (baixo/crítico)
- Transparência

## 🔧 Casos de Uso

### Corrida Multiclasse (LMH + LMDh + LMP2 + GT3)

```
Pos | Logo      | CL  | Piloto      | Best Lap  | Gap    | Ener.
----|-----------|-----|-------------|-----------|--------|-------
01  | [Toyota]  | HY  | L. Da Costa | 1:24.432  | LEADER | 88%
02  | [Ferrari] | HY  | S. Buemi    | 1:24.810  | +2.1s  | 82%
03  | [Porsche] | HY  | B. Hartley  | 1:24.992  | +1.5s  | 79%
04  | [BMW]     | GT3 | V. Rossi    | 1:32.112  | --     | --
05  | [Aston]   | GT3 | P. Lamy     | 1:32.450  | -2.1s  | --
```

✅ **LMH/LMDh** mostram energia em %  
✅ **GT3** mostram `--` (sem sistema híbrido)

### Fórmula E / F1 Hybrid

Todos os carros têm sistema híbrido - todos mostram porcentagem.

### GT3 / GTE Puro

Nenhum carro tem sistema híbrido - todos mostram `--`.

## 🛡️ Tratamento de Erros

O widget é robusto e trata todos os casos de erro:

```python
try:
    max_energy = api.read.vehicle.max_virtual_energy(idx)
    
    # Detecção de sistema híbrido
    if max_energy is None or max_energy <= 0:
        display = "--"
        return
    
    current_energy = api.read.vehicle.virtual_energy(idx)
    
    # Tratamento de valores inválidos
    if current_energy is None or str(current_energy) in ('nan', 'inf'):
        display = "--"
        return
    
    # Cálculo seguro
    energy_percent = (current_energy / max_energy) * 100.0
    energy_percent = max(0.0, min(100.0, energy_percent))  # Clamp 0-100
    
    display = f"{int(energy_percent)}%"
    
except Exception:
    # Fallback seguro
    display = "--"
```

## 📝 Diferenças do Widget Original

| Feature | `standings` (original) | `standings_hybrid` (novo) |
|---------|----------------------|--------------------------|
| Colunas | 15+ configuráveis | 7 fixas otimizadas |
| Detecção Híbrido | ❌ Não | ✅ Automática |
| Grids Mistos | ⚠️ Problema | ✅ Totalmente suportado |
| Energia | Coluna opcional | Coluna inteligente |
| Performance | Boa | Otimizada |
| Complexidade Config | Alta (100+ opções) | Média (50 opções) |

## 🎯 Casos de Uso Ideais

✅ **Perfeito para:**
- Corridas multiclasse (IMSA, WEC)
- Ligas com regulamentos mistos
- Transmissões ao vivo
- Análise de estratégia de energia
- Coaching em tempo real

❌ **Use o widget original para:**
- Configurações muito personalizadas
- Mais de 7 colunas necessárias
- Sem necessidade de informação de energia

## 🐛 Solução de Problemas

### Energia mostra sempre `--`

**Causa:** API REST não está fornecendo dados de energia  
**Solução:** Verifique se o REST API está habilitado no rF2/LMU

### Widget não aparece

**Causa:** Widget não está habilitado  
**Solução:** Marque "Enable" na aba Widget

### Posições erradas

**Causa:** Dados de telemetria atrasados  
**Solução:** Reduza `update_interval` para 50ms

### Logos não aparecem

**Causa:** Arquivos de logo não encontrados  
**Solução:** Coloque logos PNG em `brand_logo/` com nome do veículo

## 📚 Arquivos Relacionados

- **Widget:** `validadorers/widget/standings_hybrid.py`
- **Config:** `validadorers/template/setting_widget.py`
- **API Data:** `validadorers/adapter/rf2_data.py`
- **Registro:** `validadorers/widget/__init__.py`

## 🤝 Contribuições

Sugestões de melhorias:
- [ ] Adicionar coluna de pit stops
- [ ] Mostrar delta para o carro à frente
- [ ] Animação de ultrapassagens
- [ ] Som de alerta quando energia crítica
- [ ] Export de dados para CSV

## 📄 Licença

GPL v3.0 - Same as SectorFlow

---

**Desenvolvido com ❤️ para a comunidade SectorFlow**  
*Detecção Dinâmica de Híbridos - Sem filtros manuais, sem problemas!*
