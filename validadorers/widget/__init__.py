#  SectorFlow is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 SectorFlow developers
#  Based on TinyPedal - Copyright (C) 2022-2025 TinyPedal developers
#
#  This file is part of SectorFlow.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Widget modules

Add new widget to import list below in ascending order,
file name must match corresponding key name
in template/setting_widget.py dictionary.
"""

__all__ = [
    "battery",
    "brake_bias",
    "brake_performance",
    "brake_pressure",
    "brake_temperature",
    "brake_wear",
    "cruise",
    "damage",
    "deltabest",
    "deltabest_extended",
    "differential",
    "drs",
    "electric_motor",
    "elevation",
    "engine",
    "flag",
    "force",
    "friction_circle",
    "fuel",
    "fuel_energy_saver",
    "gear",
    "heading",
    "instrument",
    "lap_time_history",
    "laps_and_position",
    "navigation",
    "p2p",
    "pace_notes",
    "pedal",
    "pit_stop_estimate",
    "radar",
    "rake_angle",
    "relative",
    "relative_finish_order",
    "ride_height",
    "rivals",
    "roll_angle",
    "sectors",
    "session",
    "slip_ratio",
    "speedometer",
    "standings",
    "standings_hybrid",  # Corrigido: garantir que o widget híbrido seja carregado
    "steering",
    "steering_wheel",
    "stint_history",
    "suspension_force",
    "suspension_position",
    "system_performance",
    "tempo_completo",
    "timing",
    "track_map",
    "track_notes",
    "trailing",
    "tyre_carcass",
    "tyre_inner_layer",
    "tyre_load",
    "tyre_pressure",
    "tyre_temperature",
    "tyre_visual",
    "tyre_wear",
    "virtual_energy",
    "weather",
    "weather_forecast",
    "weight_distribution",
    "wheel_alignment",
]

from . import battery
from . import brake_bias
from . import brake_performance
from . import brake_pressure
from . import brake_temperature
from . import brake_wear
from . import cruise
from . import damage
from . import deltabest
from . import deltabest_extended
from . import differential
from . import drs
from . import electric_motor
from . import elevation
from . import engine
from . import flag
from . import force
from . import friction_circle
from . import fuel
from . import fuel_energy_saver
from . import gear
from . import heading
from . import instrument
from . import lap_time_history
from . import laps_and_position
from . import navigation
from . import p2p
from . import pace_notes
from . import pedal
from . import pit_stop_estimate
from . import radar
from . import rake_angle
from . import relative
from . import relative_finish_order
from . import ride_height
from . import rivals
from . import roll_angle
from . import sectors
from . import session
from . import slip_ratio
from . import speedometer
from . import standings
from . import standings_hybrid  # Corrigido: garantir que o widget híbrido seja carregado
from . import steering
from . import steering_wheel
from . import stint_history
from . import suspension_force
from . import suspension_position
from . import system_performance
from . import tempo_completo
from . import timing
from . import track_map
from . import track_notes
from . import trailing
from . import tyre_carcass
from . import tyre_inner_layer
from . import tyre_load
from . import tyre_pressure
from . import tyre_temperature
from . import tyre_visual
from . import tyre_wear
from . import virtual_energy
from . import weather
from . import weather_forecast
from . import weight_distribution
from . import wheel_alignment
