# Validadorers package initialization

import logging
from io import StringIO
from PySide6.QtCore import QObject, Signal

class RealtimeState:
    """Global realtime state"""
    def __init__(self):
        self.active = False
        self.paused = False

# Create global instance
realtime_state = RealtimeState()

# Signal system using Qt
class OverlaySignal(QObject):
    """Overlay signal handler using Qt signals"""
    iconify = Signal(bool)
    locked = Signal(bool)
    hidden = Signal(bool)
    paused = Signal(bool)
    reload = Signal()
    updates = Signal(bool)  # Changed from str to bool to match emit(True/False)
    
    def __init__(self):
        super().__init__()

# Create global signal instance
overlay_signal = OverlaySignal()

# Loader flag with restart method reference
class Loader:
    """Loader state and control"""
    is_loading = False
    restart = None  # Will be set by loader module

loader = Loader()

# Log stream for capturing logs
log_stream = StringIO()

__all__ = ['realtime_state', 'overlay_signal', 'loader', 'log_stream']
