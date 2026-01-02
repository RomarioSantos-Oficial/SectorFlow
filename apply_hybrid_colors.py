#!/usr/bin/env python3
"""
Script para aplicar as cores do standings_hybrid em todos os widgets
"""

import json
import re

# Padrão de cores do standings_hybrid
HYBRID_COLORS = {
    # Cores normais (não-player)
    "normal": {
        "text": "#FFFFFF",
        "background": "#222222"
    },
    # Cores do player
    "player": {
        "text": "#000000",
        "background": "#FFFFFF"
    },
    # Cores especiais (cinza mais claro)
    "special": {
        "text": "#CCCCCC",
        "background": "#222222"
    }
}

# Mapeamento de cores antigas para novas
COLOR_MAPPING = {
    # Fundos antigos → novo fundo escuro
    "#333333": "#222222",
    "#444444": "#222222",
    
    # Textos antigos → novo texto branco
    "#DDDDDD": "#FFFFFF",
    "#CCCCCC": "#FFFFFF",
    "#AAAAAA": "#FFFFFF",
    
    # Player backgrounds antigos → novo player background
    "#DDDDDD": "#FFFFFF",  # já player background
    "#CCCCCC": "#FFFFFF",  # já player background
}

def update_widget_colors(widget_config):
    """Atualiza as cores de um widget"""
    changes = 0
    
    for key, value in widget_config.items():
        if not isinstance(value, str):
            continue
            
        # Detectar tipo de campo pela chave
        is_player_field = "player" in key.lower()
        is_background = "bkg" in key or "background" in key
        is_font = "font_color" in key or "color" in key and not is_background
        
        # Atualizar cores baseado no contexto
        if is_font:
            if is_player_field:
                # Texto do player → preto
                if value.startswith("#") and value != "#000000":
                    widget_config[key] = "#000000"
                    changes += 1
            else:
                # Texto normal → branco
                if value in ["#DDDDDD", "#CCCCCC", "#AAAAAA", "#888888", "#999999"]:
                    widget_config[key] = "#FFFFFF"
                    changes += 1
        
        elif is_background:
            if is_player_field:
                # Fundo do player → branco
                if value in ["#DDDDDD", "#CCCCCC", "#AAAAAA"]:
                    widget_config[key] = "#FFFFFF"
                    changes += 1
            else:
                # Fundo normal → cinza escuro
                if value in ["#333333", "#444444", "#555555"]:
                    widget_config[key] = "#222222"
                    changes += 1
    
    return changes

def process_config_file(filepath):
    """Processa um arquivo JSON de configuração"""
    print(f"\n📄 Processando: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        total_changes = 0
        
        # Processar cada widget no arquivo
        for widget_name, widget_config in config.items():
            if isinstance(widget_config, dict):
                changes = update_widget_colors(widget_config)
                if changes > 0:
                    total_changes += changes
                    print(f"  ✓ {widget_name}: {changes} cores alteradas")
        
        if total_changes > 0:
            # Salvar arquivo modificado
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"\n✅ Total: {total_changes} cores alteradas e salvas!")
        else:
            print(f"\n⚠️  Nenhuma alteração necessária")
        
        return total_changes
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 0

if __name__ == "__main__":
    import os
    
    print("="*60)
    print("🎨 APLICANDO CORES DO STANDINGS_HYBRID EM TODOS OS WIDGETS")
    print("="*60)
    
    # Arquivos a processar
    files = [
        "settings/default.json",
        "settings/Joana.json",
    ]
    
    total = 0
    for filepath in files:
        if os.path.exists(filepath):
            total += process_config_file(filepath)
    
    print("\n" + "="*60)
    print(f"🎉 CONCLUÍDO! {total} cores alteradas no total")
    print("="*60)
    print("\n💡 Reinicie o programa para ver as mudanças!")
