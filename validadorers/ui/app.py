

import logging
import os
import sys
import time

# Configurar PySide6 para reduzir warnings
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import loader, overlay_signal
from ..api_control import api
from ..const_app import APP_NAME, VERSION
from ..const_file import ConfigType
from ..i18n import i18n, _
from ..module_control import mctrl, wctrl
from ..regex_pattern import API_NAME_ALIAS
from ..setting import cfg
from . import set_style_palette, set_style_window
from ._common import UIScaler
from .menu import ConfigMenu, HelpMenu, OverlayMenu, ToolsMenu, WindowMenu
from .module_view import ModuleList
from .notification import NotifyBar
from .pace_notes_view import PaceNotesControl
from .preset_view import PresetList
from .spectate_view import SpectateList

logger = logging.getLogger(__name__)


class TabView(QWidget):
    """Tab view"""

    def __init__(self, parent):
        super().__init__(parent)
        # Notify bar
        notify_bar = NotifyBar(self)

        # Tabs
        widget_tab = ModuleList(self, wctrl)
        module_tab = ModuleList(self, mctrl)
        preset_tab = PresetList(
            self, parent.reload_preset, notify_bar.presetlocked.setVisible
        )
        spectate_tab = SpectateList(
            self, notify_bar.spectate.setVisible
        )
        pacenotes_tab = PaceNotesControl(self, notify_bar.pacenotes.setVisible)

        self._tabs = QTabWidget(self)
        self._tabs.addTab(widget_tab, _("tab_widget"))  # 0
        self._tabs.addTab(module_tab, _("tab_module"))  # 1
        self._tabs.addTab(preset_tab, _("tab_preset"))  # 2
        self._tabs.addTab(spectate_tab, _("tab_spectate"))  # 3
        self._tabs.addTab(pacenotes_tab, _("tab_pace_notes"))  # 4

        # Main view
        layout_main = QVBoxLayout()
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.setSpacing(0)
        layout_main.addWidget(self._tabs)
        layout_main.addWidget(notify_bar)
        self.setLayout(layout_main)

    def refresh_tab(self, index: int = -1):
        """Refresh tab

        Args:
            index: -1 All tabs, 0 Widget, 1 Module, 2 Preset,
                   3 Spectate, 4 Pace Notes
        """
        if index < 0:
            for tab_index in range(self._tabs.count()):
                self._tabs.widget(tab_index).refresh()
        else:
            self._tabs.widget(index).refresh()

    def select_tab(self, index: int):
        """Select tab"""
        self._tabs.setCurrentIndex(index)


class StatusButtonBar(QStatusBar):
    """Status button bar"""

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent

        self.button_api = QPushButton("")
        self.button_api.clicked.connect(self.refresh)
        self.button_api.setToolTip(_("tooltip_config_api"))

        self.button_style = QPushButton(_("ui_light"))
        self.button_style.clicked.connect(self.toggle_color_theme)
        self.button_style.setToolTip(_("tooltip_toggle_theme"))

        self.button_dpiscale = QPushButton(f"{_('scale')}: {_('auto')}")
        self.button_dpiscale.clicked.connect(self.toggle_dpi_scaling)
        self.button_dpiscale.setToolTip(_("tooltip_toggle_dpi"))
        self._last_dpi_scaling = cfg.application["enable_high_dpi_scaling"]

        self.addPermanentWidget(self.button_api)
        self.addWidget(self.button_style)
        self.addWidget(self.button_dpiscale)
        self.refresh()

    def refresh(self):
        """Refresh status bar"""
        if cfg.telemetry_api["enable_active_state_override"]:
            text_api_status = _("status_api_override")
        else:
            text_api_status = api.read.state.version()
        api_text = f"API: {API_NAME_ALIAS[api.name]} ({text_api_status})"
        self.button_api.setText(api_text)

        ui_theme = cfg.application['window_color_theme']
        self.button_style.setText(f"{_('ui_theme')}: {ui_theme}")

        if cfg.application["enable_high_dpi_scaling"]:
            text_dpi = _("auto")
        else:
            text_dpi = _("off")
        dpi_scaling_enabled = cfg.application["enable_high_dpi_scaling"]
        if self._last_dpi_scaling != dpi_scaling_enabled:
            text_need_restart = "*"
        else:
            text_need_restart = ""
        self.button_dpiscale.setText(
            f"{_('scale')}: {text_dpi}{text_need_restart}"
        )

    def toggle_dpi_scaling(self):
        """Toggle DPI scaling"""
        if cfg.application["enable_high_dpi_scaling"]:
            msg_text = _("msg_disable_dpi")
        else:
            msg_text = _("msg_enable_dpi")
        
        restart_msg = QMessageBox.question(
            self, _("msg_restart_required"), msg_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if restart_msg != QMessageBox.Yes:
            return

        current_dpi = cfg.application["enable_high_dpi_scaling"]
        cfg.application["enable_high_dpi_scaling"] = not current_dpi
        cfg.save(0, cfg_type=ConfigType.CONFIG)
        # Wait saving finish
        while cfg.is_saving:
            time.sleep(0.01)
        loader.restart()

    def toggle_color_theme(self):
        """Toggle color theme"""
        if cfg.application["window_color_theme"] == "Dark":
            cfg.application["window_color_theme"] = "Light"
        else:
            cfg.application["window_color_theme"] = "Dark"
        cfg.save(cfg_type=ConfigType.CONFIG)
        self._parent.load_window_style()


class AppWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        
        # Carregar ícone da aplicação
        self._load_app_icon()

        # Status bar
        self.setStatusBar(StatusButtonBar(self))

        # Menu bar
        self.set_menu_bar()

        # Tab view
        self.tab_view = TabView(self)
        self.setCentralWidget(self.tab_view)

        # Tray icon
        self.set_tray_icon()

        # Apply color style
        self.last_style = None
        self.load_window_style()

        # Window state
        self.set_window_state()
        self.__connect_signal()

    def set_menu_bar(self):
        """Set menu bar"""
        logger.info("GUI: loading window menu")
        menu = self.menuBar()
        # Overlay menu
        menu_overlay = OverlayMenu("Overlay", self)
        menu.addMenu(menu_overlay)
        # Config menu
        menu_config = ConfigMenu("Config", self)
        menu.addMenu(menu_config)
        status_bar = self.statusBar()
        status_bar.button_api.clicked.connect(menu_config.open_config_api)
        # Tools menu
        menu_tools = ToolsMenu("Tools", self)
        menu.addMenu(menu_tools)
        # Window menu
        menu_window = WindowMenu("Window", self)
        menu.addMenu(menu_window)
        # Help menu
        menu_help = HelpMenu("Help", self)
        menu.addMenu(menu_help)
    def _load_app_icon(self):
        """Load application icon"""
        try:
            # Caminho mais robusto para encontrar os recursos
            if getattr(sys, 'frozen', False):
                # Estamos rodando no executável (congelado pelo PyInstaller)
                base_path = sys._MEIPASS
            else:
                # Estamos rodando em modo de desenvolvimento
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            icon_path = os.path.join(base_path, "images", "icon", "Logo.png")
            
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                logger.info(f"✅ Application icon loaded: {icon_path}")
            else:
                logger.warning(f"⚠️ Logo.png not found at: {icon_path}")
                # Tenta carregar o ícone .ico como fallback
                ico_path = os.path.join(os.path.dirname(base_path), "brandlogo", "Logo.ico")
                if os.path.exists(ico_path):
                    self.setWindowIcon(QIcon(ico_path))
                    logger.info(f"✅ Fallback .ico icon loaded: {ico_path}")
                else:
                    logger.warning(f"⚠️ Fallback Logo.ico not found at: {ico_path}")

        except Exception as e:
            logger.error(f"❌ Error loading application icon: {e}")
    
    def set_tray_icon(self):
        """Set tray icon"""
        logger.info("GUI: loading tray icon")
        # Salvar como atributo da classe para evitar que seja removido da memória
        self.tray_icon = QSystemTrayIcon(self)
        
        # Garantir que há um ícone antes de mostrar
        icon = self.windowIcon()
        
        # Se não houver ícone da janela, criar um padrão
        if icon.isNull():
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.blue)
            icon = QIcon(pixmap)
            logger.warning("⚠️ Using default blue icon because no valid icon was loaded.")
        
        # Config tray icon
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(self.windowTitle())
        self.tray_icon.activated.connect(self.tray_doubleclick)
        
        # Add tray menu - também salvar como atributo
        self.tray_menu = OverlayMenu("Overlay", self, True)
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Só mostrar se tiver ícone válido
        if not self.tray_icon.icon().isNull():
            self.tray_icon.show()
            logger.info("Tray icon displayed successfully")
        else:
            logger.error("Failed to set tray icon - icon is null")

    def tray_doubleclick(
        self, active_reason: QSystemTrayIcon.ActivationReason
    ):
        """Tray doubleclick"""
        if active_reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_app()

    def set_window_state(self):
        """Set initial window state"""
        self.setMinimumSize(UIScaler.size(22), UIScaler.size(36))
        # Disable maximize button
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        if cfg.application["remember_size"]:
            self.resize(
                cfg.application["window_width"],
                cfg.application["window_height"],
            )

        if cfg.application["remember_position"]:
            self.load_window_position()

        if cfg.compatibility["enable_window_position_correction"]:
            self.verify_window_position()

        if cfg.application["show_at_startup"]:
            self.showNormal()
        elif not cfg.application["minimize_to_tray"]:
            self.showMinimized()

    def load_window_position(self):
        """Load window position"""
        logger.info("GUI: loading window setting")
        app_pos_x = cfg.application["position_x"]
        app_pos_y = cfg.application["position_y"]
        # Save new x,y position if preset value at 0,0
        if 0 == app_pos_x == app_pos_y:
            self.save_window_state()
        else:
            self.move(app_pos_x, app_pos_y)

    def verify_window_position(self):
        """Verify window position"""
        # Get screen size from the screen where app window located
        screen_geo = self.screen().geometry()
        # Limiting position value if out of screen range
        app_pos_x = min(
            max(self.x(), screen_geo.left()),
            screen_geo.right() - self.minimumWidth(),
        )
        app_pos_y = min(
            max(self.y(), screen_geo.top()),
            screen_geo.bottom() - self.minimumHeight(),
        )
        # Re-adjust position only if mismatched
        if self.x() != app_pos_x or self.y() != app_pos_y:
            self.move(app_pos_x, app_pos_y)
            logger.info("GUI: window position corrected")

    def save_window_state(self):
        """Save window state"""
        save_changes = False

        if cfg.application["remember_position"]:
            last_pos = (
                cfg.application["position_x"],
                cfg.application["position_y"]
            )
            new_pos = self.x(), self.y()
            if last_pos != new_pos:
                cfg.application["position_x"] = new_pos[0]
                cfg.application["position_y"] = new_pos[1]
                save_changes = True

        if cfg.application["remember_size"]:
            last_size = (
                cfg.application["window_width"],
                cfg.application["window_height"]
            )
            new_size = self.width(), self.height()
            if last_size != new_size:
                cfg.application["window_width"] = new_size[0]
                cfg.application["window_height"] = new_size[1]
                save_changes = True

        if save_changes:
            cfg.save(0, cfg_type=ConfigType.CONFIG)

    def load_window_style(self):
        """Load window style"""
        style = cfg.application["window_color_theme"]
        logger.info("GUI: loading window color theme: %s", style)
        if self.last_style != style:
            self.last_style = style
            set_style_palette(self.last_style)
            font_size = QApplication.font().pointSize()
            self.setStyleSheet(set_style_window(font_size))
        self.statusBar().refresh()

    def show_app(self):
        """Show app window"""
        self.showNormal()
        self.activateWindow()

    def quit_app(self):
        """Quit manager"""
        logger.info("GUI: quit_app called - closing application...")
        try:
            loader.close()  # must close this first
            logger.info("GUI: loader closed")
        except Exception as e:
            logger.error(f"GUI: Error closing loader: {e}")
        
        try:
            self.save_window_state()
            logger.info("GUI: window state saved")
        except Exception as e:
            logger.error(f"GUI: Error saving window state: {e}")
        
        try:
            self.__break_signal()
            logger.info("GUI: signals disconnected")
        except Exception as e:
            logger.error(f"GUI: Error breaking signals: {e}")
        
        try:
            # Workaround: tray icon not removed after exited
            self.tray_icon.hide()
            logger.info("GUI: tray icon hidden")
        except Exception as e:
            logger.error(f"GUI: Error hiding tray icon: {e}")
        
        logger.info("GUI: calling QApplication.quit()")
        QApplication.quit()

    def closeEvent(self, event):
        """Minimize to tray"""
        if cfg.application["minimize_to_tray"]:
            event.ignore()
            self.hide()
        else:
            self.quit_app()

    def restart_api(self):
        """Restart telemetry API"""
        api.restart()
        self.statusBar().refresh()
        self.tab_view.refresh_tab(3)

    @Slot(bool)  # type: ignore[operator]
    def reload_preset(self):
        """Reload current preset"""
        loader.reload(reload_preset=True)
        self.load_window_style()
        self.refresh_states()

    def reload_only(self):
        """Reload only api, module, widget"""
        loader.reload(reload_preset=False)
        self.refresh_states()

    def refresh_states(self):
        """Refresh state"""
        self.statusBar().refresh()
        self.tab_view.refresh_tab()

    def __connect_signal(self):
        """Connect signal"""
        overlay_signal.reload.connect(self.reload_preset)
        logger.info("GUI: connect signals")

    def __break_signal(self):
        """Disconnect signal"""
        overlay_signal.reload.disconnect(self.reload_preset)
        logger.info("GUI: disconnect signals")


def main():
    """Main application entry point"""
    import sys
    import traceback
    import signal
    from PySide6.QtNetwork import QLocalServer, QLocalSocket

    # Allow Ctrl+C to kill the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # ===== VERIFICAR INSTÂNCIA ÚNICA =====
    # Tentar conectar a uma instância existente
    socket = QLocalSocket()
    socket.connectToServer("SectorFlowInstance")
    if socket.waitForConnected(500):
        # Já existe uma instância rodando
        logger.warning("SectorFlow já está em execução!")
        socket.close()
        sys.exit(0)
    socket.close()
    
    # Criar servidor para esta instância
    server = QLocalServer()
    # Remover servidor antigo caso tenha crashado
    QLocalServer.removeServer("SectorFlowInstance")
    server.listen("SectorFlowInstance")
    # =====================================
    
    # Load global configuration first
    logger.info("LOADING: configuration")
    try:
        logger.info("Loading global config...")
        cfg.load_global()
        logger.info("Global config loaded")
    except Exception as e:
        logger.error(f"Failed to load global configuration: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    # Enable High DPI
    try:
        if cfg.application and cfg.application.get("enable_high_dpi_scaling", False):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except:
        pass
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    
    # Initialize UI Scaler after QApplication is created
    from ._common import UIScaler
    UIScaler.init_font_size()
    
    # Set application style
    set_style_window(UIScaler.FONT_BASE_POINT)
    
    # Start the application using loader
    from ..loader import start
    start()
    
    # Create a timer to let the Python interpreter run occasionally to catch Ctrl+C
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    # Start application event loop
    exit_code = app.exec()
    
    # Limpar servidor ao sair
    server.close()
    sys.exit(exit_code)
