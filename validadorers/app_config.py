

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AppConfig:
    """Application-wide configuration constants
    
    Optimized for:
        - Le Mans Ultimate (primary)
        - rFactor 2 (alternative)
        - Endurance racing telemetry
        - Multi-class racing support
    """
    
    # ========== Version Requirements ==========
    PYTHON_MIN: Tuple[int, int] = (3, 8)
    PYTHON_MAX: Tuple[int, int] = (3, 14)
    PYTHON_RECOMMENDED: Tuple[int, int] = (3, 10)
    
    # ========== Performance Settings ==========
    # Update intervals in milliseconds (optimized for endurance racing)
    MODULE_UPDATE_INTERVAL_MS: int = 16  # ~60 FPS for smooth telemetry
    WIDGET_UPDATE_INTERVAL_MS: int = 16  # Match module rate
    API_CHECK_INTERVAL_MS: int = 200  # Check game state every 0.2s
    OVERLAY_UPDATE_MS: int = 16  # Smooth overlay updates
    
    # ========== Racing Limits ==========
    # LMU supports up to 62 cars in official races
    MAX_VEHICLES: int = 128  # Safe upper limit
    MAX_HISTORY_LAPS: int = 200  # For endurance races (e.g., 24h Le Mans)
    MAX_STINT_LAPS: int = 100  # Typical stint length
    
    # ========== Data Management ==========
    MAX_LOG_SIZE_MB: int = 10  # Larger for long endurance races
    MAX_CONSUMPTION_HISTORY: int = 50  # Fuel/energy history
    MAX_SECTOR_HISTORY: int = 100  # Sector time tracking
    
    # ========== Timeouts ==========
    API_CONNECT_TIMEOUT: int = 5  # seconds
    FILE_SAVE_TIMEOUT: int = 3  # seconds
    RESTART_DELAY: float = 0.5  # seconds between restart
    
    # ========== File Paths ==========
    CONFIG_SUBDIR: str = "TinyPedal"
    LOG_FILENAME: str = "tinypedal.log"
    PID_FILENAME: str = "pid.log"
    
    # ========== LMU Specific ==========
    # Hypercar hybrid system parameters
    HYBRID_DEPLOYMENT_MAX: int = 100  # Max deployment percentage
    HYBRID_REGEN_MAX: int = 100  # Max regeneration percentage
    
    # Multi-class racing
    VEHICLE_CLASSES: Tuple[str, ...] = (
        "Hypercar",
        "LMP2", 
        "LMGTE Pro",
        "LMGTE Am",
        "LMP3",
        "GT3",
    )
    
    # Endurance race durations (in hours)
    RACE_DURATIONS: Tuple[int, ...] = (1, 2, 4, 6, 8, 12, 24)
    
    # ========== UI Settings ==========
    DEFAULT_FONT_SIZE: int = 10
    DEFAULT_BAR_HEIGHT: int = 20
    DEFAULT_BAR_GAP: int = 1
    MIN_WIDGET_WIDTH: int = 50
    MIN_WIDGET_HEIGHT: int = 20
    
    # ========== Network ==========
    # LMU Rest API default ports
    LMU_REST_API_PORT: int = 6397
    RF2_REST_API_PORT: int = 5397
    
    # ========== Debug ==========
    DEBUG_MODE: bool = False
    VERBOSE_LOGGING: bool = False


# Global configuration instance
APP_CONFIG = AppConfig()


# ========== Helper Functions ==========

def is_endurance_race(duration_hours: float) -> bool:
    """Check if race is endurance (6+ hours)"""
    return duration_hours >= 6


def is_hypercar_class(vehicle_class: str) -> bool:
    """Check if vehicle is Hypercar (hybrid system)"""
    return "hypercar" in vehicle_class.lower()


def is_lmp2_class(vehicle_class: str) -> bool:
    """Check if vehicle is LMP2"""
    return "lmp2" in vehicle_class.lower()


def supports_hybrid(vehicle_class: str) -> bool:
    """Check if vehicle class supports hybrid systems"""
    return is_hypercar_class(vehicle_class)


def get_recommended_update_interval(vehicle_class: str) -> int:
    """Get recommended update interval based on vehicle class
    
    Args:
        vehicle_class: Vehicle class name
        
    Returns:
        Update interval in milliseconds
    """
    # Hypercars need faster updates for hybrid management
    if is_hypercar_class(vehicle_class):
        return 10  # 100 FPS for hybrid system
    return APP_CONFIG.MODULE_UPDATE_INTERVAL_MS
