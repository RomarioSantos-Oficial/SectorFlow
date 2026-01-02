"""
Internacionalization (i18n) module for SectorFlow
Provides multi-language support for Portuguese (Brazil) and English
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class Language:
    """Language configuration"""
    PT_BR = "pt_BR"
    EN_US = "en_US"


class I18n:
    """Internationalization handler"""
    
    def __init__(self):
        self._current_language = Language.PT_BR
        self._translations: Dict[str, Dict[str, str]] = {
            # Application
            "app_name": {
                Language.PT_BR: "SectorFlow",
                Language.EN_US: "SectorFlow"
            },
            "app_description": {
                Language.PT_BR: (
                    "Aplicação de telemetria overlay gratuita e "
                    "de código aberto para simulação de corrida."
                ),
                Language.EN_US: (
                    "Free and Open Source telemetry overlay application "
                    "for racing simulation."
                )
            },
            
            # Menu items
            "menu_overlay": {
                Language.PT_BR: "Overlay",
                Language.EN_US: "Overlay"
            },
            "menu_config": {
                Language.PT_BR: "Configuração",
                Language.EN_US: "Config"
            },
            "menu_tools": {
                Language.PT_BR: "Ferramentas",
                Language.EN_US: "Tools"
            },
            "menu_window": {
                Language.PT_BR: "Janela",
                Language.EN_US: "Window"
            },
            "menu_help": {
                Language.PT_BR: "Ajuda",
                Language.EN_US: "Help"
            },
            
            # UI Elements
            "ui_theme": {
                Language.PT_BR: "Tema",
                Language.EN_US: "Theme"
            },
            "ui_light": {
                Language.PT_BR: "Claro",
                Language.EN_US: "Light"
            },
            "ui_dark": {
                Language.PT_BR: "Escuro",
                Language.EN_US: "Dark"
            },
            "scale": {
                Language.PT_BR: "Escala",
                Language.EN_US: "Scale"
            },
            "auto": {
                Language.PT_BR: "Auto",
                Language.EN_US: "Auto"
            },
            "off": {
                Language.PT_BR: "Desligado",
                Language.EN_US: "Off"
            },
            
            # Tabs
            "tab_widget": {
                Language.PT_BR: "Widget",
                Language.EN_US: "Widget"
            },
            "tab_module": {
                Language.PT_BR: "Módulo",
                Language.EN_US: "Module"
            },
            "tab_preset": {
                Language.PT_BR: "Predefinição",
                Language.EN_US: "Preset"
            },
            "tab_spectate": {
                Language.PT_BR: "Espectador",
                Language.EN_US: "Spectate"
            },
            "tab_pace_notes": {
                Language.PT_BR: "Notas de Ritmo",
                Language.EN_US: "Pace Notes"
            },
            
            # Messages
            "msg_restart_required": {
                Language.PT_BR: "Reinicialização necessária",
                Language.EN_US: "Restart required"
            },
            "msg_enable_dpi": {
                Language.PT_BR: (
                    "Ativar <b>Escala de DPI Alto</b> e reiniciar "
                    "<b>SectorFlow</b>?<br><br>"
                    "O tamanho e a posição da <b>Janela</b> e do "
                    "<b>Overlay</b> serão ajustados automaticamente de "
                    "acordo com a configuração de escala DPI do sistema."
                ),
                Language.EN_US: (
                    "Enable <b>High DPI Scaling</b> and restart "
                    "<b>SectorFlow</b>?<br><br>"
                    "<b>Window</b> and <b>Overlay</b> size and position "
                    "will be auto-scaled according to system DPI scaling setting."
                )
            },
            "msg_disable_dpi": {
                Language.PT_BR: (
                    "Desativar <b>Escala de DPI Alto</b> e reiniciar "
                    "<b>SectorFlow</b>?<br><br>"
                    "O tamanho e a posição da <b>Janela</b> e do "
                    "<b>Overlay</b> não serão ajustados em resoluções "
                    "de tela de alto DPI."
                ),
                Language.EN_US: (
                    "Disable <b>High DPI Scaling</b> and restart "
                    "<b>SectorFlow</b>?<br><br>"
                    "<b>Window</b> and <b>Overlay</b> size and position "
                    "will not be scaled under high DPI screen resolution."
                )
            },
            
            # Tooltips
            "tooltip_config_api": {
                Language.PT_BR: "Configurar API de Telemetria",
                Language.EN_US: "Config Telemetry API"
            },
            "tooltip_toggle_theme": {
                Language.PT_BR: "Alternar Tema de Cor da Janela",
                Language.EN_US: "Toggle Window Color Theme"
            },
            "tooltip_toggle_dpi": {
                Language.PT_BR: "Alternar Escala de DPI Alto",
                Language.EN_US: "Toggle High DPI Scaling"
            },
            
            # Status messages
            "status_connecting": {
                Language.PT_BR: "Conectando",
                Language.EN_US: "Connecting"
            },
            "status_connected": {
                Language.PT_BR: "Conectado",
                Language.EN_US: "Connected"
            },
            "status_disconnecting": {
                Language.PT_BR: "Desconectando",
                Language.EN_US: "Disconnecting"
            },
            "status_disconnected": {
                Language.PT_BR: "Desconectado",
                Language.EN_US: "Disconnected"
            },
            "status_api_override": {
                Language.PT_BR: "sobrescrevendo",
                Language.EN_US: "overriding"
            },
            
            # Overlay Menu
            "lock_overlay": {
                Language.PT_BR: "Travar Overlay",
                Language.EN_US: "Lock Overlay"
            },
            "auto_hide": {
                Language.PT_BR: "Ocultar Automaticamente",
                Language.EN_US: "Auto Hide"
            },
            "grid_move": {
                Language.PT_BR: "Movimento em Grade",
                Language.EN_US: "Grid Move"
            },
            "vr_compatibility": {
                Language.PT_BR: "Compatibilidade VR",
                Language.EN_US: "VR Compatibility"
            },
            "reload": {
                Language.PT_BR: "Recarregar",
                Language.EN_US: "Reload"
            },
            "restart_api": {
                Language.PT_BR: "Reiniciar API",
                Language.EN_US: "Restart API"
            },
            "reset_data": {
                Language.PT_BR: "Resetar Dados",
                Language.EN_US: "Reset Data"
            },
            "config": {
                Language.PT_BR: "Configuração",
                Language.EN_US: "Config"
            },
            "quit": {
                Language.PT_BR: "Sair",
                Language.EN_US: "Quit"
            },
            
            # Reset Data Submenu
            "delta_best": {
                Language.PT_BR: "Delta Melhor",
                Language.EN_US: "Delta Best"
            },
            "energy_delta": {
                Language.PT_BR: "Delta de Energia",
                Language.EN_US: "Energy Delta"
            },
            "fuel_delta": {
                Language.PT_BR: "Delta de Combustível",
                Language.EN_US: "Fuel Delta"
            },
            "consumption_history": {
                Language.PT_BR: "Histórico de Consumo",
                Language.EN_US: "Consumption History"
            },
            "sector_best": {
                Language.PT_BR: "Melhor Setor",
                Language.EN_US: "Sector Best"
            },
            "track_map": {
                Language.PT_BR: "Mapa da Pista",
                Language.EN_US: "Track Map"
            },
            "track_notes": {
                Language.PT_BR: "Notas da Pista",
                Language.EN_US: "Track Notes"
            },
            "qualify_rank": {
                Language.PT_BR: "Ranking de Qualificação",
                Language.EN_US: "Qualify Rank"
            },
            "session_best": {
                Language.PT_BR: "Melhor da Sessão",
                Language.EN_US: "Session Best"
            },
            
            # Tools Menu
            "fuel_calculator": {
                Language.PT_BR: "Calculadora de Combustível",
                Language.EN_US: "Fuel Calculator"
            },
            "track_notes_editor": {
                Language.PT_BR: "Editor de Notas da Pista",
                Language.EN_US: "Track Notes Editor"
            },
            "track_map_viewer": {
                Language.PT_BR: "Visualizador de Mapa da Pista",
                Language.EN_US: "Track Map Viewer"
            },
            "driver_stats_viewer": {
                Language.PT_BR: "Estatísticas de Pilotos",
                Language.EN_US: "Driver Stats Viewer"
            },
            "vehicle_brand_editor": {
                Language.PT_BR: "Editor de Marcas de Veículos",
                Language.EN_US: "Vehicle Brand Editor"
            },
            "vehicle_class_editor": {
                Language.PT_BR: "Editor de Classes de Veículos",
                Language.EN_US: "Vehicle Class Editor"
            },
            "track_info_editor": {
                Language.PT_BR: "Editor de Informações da Pista",
                Language.EN_US: "Track Info Editor"
            },
            "tyre_compound_editor": {
                Language.PT_BR: "Editor de Compostos de Pneus",
                Language.EN_US: "Tyre Compound Editor"
            },
            "brake_editor": {
                Language.PT_BR: "Editor de Freios",
                Language.EN_US: "Brake Editor"
            },
            "heatmap_editor": {
                Language.PT_BR: "Editor de Mapa de Calor",
                Language.EN_US: "Heatmap Editor"
            },
            "log_info": {
                Language.PT_BR: "Informações de Log",
                Language.EN_US: "Log Info"
            },
            
            # Config Menu
            "user_config": {
                Language.PT_BR: "Configuração de Usuário",
                Language.EN_US: "User Config"
            },
            "font_config": {
                Language.PT_BR: "Configuração de Fonte",
                Language.EN_US: "Font Config"
            },
            
            # Help Menu
            "check_updates": {
                Language.PT_BR: "Verificar Atualizações",
                Language.EN_US: "Check Updates"
            },
            "user_guide": {
                Language.PT_BR: "Guia do Usuário",
                Language.EN_US: "User Guide"
            },
            "about": {
                Language.PT_BR: "Sobre",
                Language.EN_US: "About"
            },
        }
    
    def set_language(self, language: str):
        """Set current language
        
        Args:
            language: Language code (pt_BR or en_US)
        """
        if language in (Language.PT_BR, Language.EN_US):
            self._current_language = language
            logger.info("Language set to: %s", language)
        else:
            logger.warning("Invalid language: %s", language)
    
    def get_language(self) -> str:
        """Get current language
        
        Returns:
            Current language code
        """
        return self._current_language
    
    def translate(self, key: str, default: str = "") -> str:
        """Translate a key to current language
        
        Args:
            key: Translation key
            default: Default value if key not found
            
        Returns:
            Translated string or default
        """
        if key in self._translations:
            return self._translations[key].get(
                self._current_language,
                self._translations[key].get(Language.EN_US, default)
            )
        return default or key
    
    def __call__(self, key: str, default: str = "") -> str:
        """Shorthand for translate()
        
        Args:
            key: Translation key
            default: Default value if key not found
            
        Returns:
            Translated string
        """
        return self.translate(key, default)


# Global i18n instance
i18n = I18n()

# Shorthand function for translations
def _(key: str, default: str = "") -> str:
    """Translate key to current language
    
    Args:
        key: Translation key
        default: Default value if key not found
        
    Returns:
        Translated string
    """
    return i18n.translate(key, default)
