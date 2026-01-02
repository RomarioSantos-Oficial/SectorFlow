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
Tempo Completo Widget - Visual Weather Display with Icons
Shows: Temperature, Track Temp, Day/Night, Rain/Cloudy Status
Uses icons from images/tempo directory
"""

from ..api_control import api
from ..units import set_symbol_temperature, set_unit_temperature
from ._base import Overlay
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
import os


class Realtime(Overlay):
    """Draw widget - Tempo Completo with Weather Icons"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        
        # Main layout - horizontal
        layout = self.set_grid_layout(gap=self.wcfg.get("bar_gap", 3))
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        self.icon_size = max(int(self.wcfg.get("icon_size", 32)), 16)
        
        # Config units
        self.unit_temp = set_unit_temperature(self.cfg.units["temperature_unit"])
        self.symbol_temp = set_symbol_temperature(self.cfg.units["temperature_unit"])

        # Base style
        self.set_base_style(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Load weather icons
        self.icons = self._load_icons()
        
        # ===== Column 0: Thermometer + Air Temperature =====
        bar_style_temp = self.set_qss(
            fg_color=self.wcfg.get("font_color_temperature", "#FFFFFF"),
            bg_color=self.wcfg.get("bkg_color_temperature", "#333333")
        )
        
        # Thermometer icon
        self.icon_thermo = QLabel()
        self.icon_thermo.setAlignment(Qt.AlignCenter)
        self.icon_thermo.setFixedSize(self.icon_size, self.icon_size)
        if "termômetro" in self.icons:
            self.icon_thermo.setPixmap(self.icons["termômetro"])
        layout.addWidget(self.icon_thermo, 0, 0)
        
        # Air temperature label
        self.bar_air_temp = self.set_qlabel(
            text="--°C",
            style=bar_style_temp,
            width=font_m.width * 6 + bar_padx,
        )
        self.bar_air_temp.last = None
        layout.addWidget(self.bar_air_temp, 1, 0)
        
        # ===== Column 1: Track Icon + Track Temperature =====
        bar_style_track = self.set_qss(
            fg_color=self.wcfg.get("font_color_track_temp", "#FFAA00"),
            bg_color=self.wcfg.get("bkg_color_track_temp", "#333333")
        )
        
        # Track icon
        self.icon_track = QLabel()
        self.icon_track.setAlignment(Qt.AlignCenter)
        self.icon_track.setFixedSize(self.icon_size, self.icon_size)
        if "Pista" in self.icons:
            self.icon_track.setPixmap(self.icons["Pista"])
        layout.addWidget(self.icon_track, 0, 1)
        
        # Track temperature label
        self.bar_track_temp = self.set_qlabel(
            text="--°C",
            style=bar_style_track,
            width=font_m.width * 6 + bar_padx,
        )
        self.bar_track_temp.last = None
        layout.addWidget(self.bar_track_temp, 1, 1)
        
        # ===== Column 2: Day/Night Icon =====
        self.icon_daynight = QLabel()
        self.icon_daynight.setAlignment(Qt.AlignCenter)
        self.icon_daynight.setFixedSize(self.icon_size, self.icon_size)
        self.icon_daynight.last = None
        layout.addWidget(self.icon_daynight, 0, 2, 2, 1)  # Span 2 rows
        
        # ===== Column 3: Weather Condition Icon (Rain/Cloudy) - Only shown when active =====
        self.icon_weather = QLabel()
        self.icon_weather.setAlignment(Qt.AlignCenter)
        self.icon_weather.setFixedSize(self.icon_size, self.icon_size)
        self.icon_weather.last = None
        self.icon_weather.hide()  # Hidden by default
        layout.addWidget(self.icon_weather, 0, 3, 2, 1)  # Span 2 rows
        
        # ===== Column 4: Rain percentage (optional) =====
        bar_style_rain = self.set_qss(
            fg_color=self.wcfg.get("font_color_rain", "#00AAFF"),
            bg_color=self.wcfg.get("bkg_color_rain", "#333333")
        )
        
        self.bar_rain_pct = self.set_qlabel(
            text="",
            style=bar_style_rain,
            width=font_m.width * 4 + bar_padx,
        )
        self.bar_rain_pct.last = None
        self.bar_rain_pct.hide()  # Hidden by default
        layout.addWidget(self.bar_rain_pct, 0, 4, 2, 1)  # Span 2 rows

    def _load_icons(self):
        """Load weather icons from images/tempo directory"""
        icons = {}
        tempo_path = os.path.join(os.getcwd(), "images", "tempo")
        
        icon_files = {
            "termômetro": "termômetro.png",
            "Pista": "Pista.png",
            "Sol": "Sol.png",
            "noite": "noite.png",
            "nublado": "nublado.png",
            "Chuva": "Chuva.png",
        }
        
        for name, filename in icon_files.items():
            path = os.path.join(tempo_path, filename)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # Scale to icon size
                    icons[name] = pixmap.scaled(
                        self.icon_size, self.icon_size,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
        
        return icons

    def timerEvent(self, event):
        """Update weather data"""
        
        # === Air Temperature ===
        try:
            air_temp = api.read.session.ambient_temperature()
            if self.bar_air_temp.last != air_temp:
                self.bar_air_temp.last = air_temp
                temp_value = self.unit_temp(air_temp)
                self.bar_air_temp.setText(f"{temp_value:.1f}{self.symbol_temp}")
        except:
            pass
        
        # === Track Temperature ===
        try:
            track_temp = api.read.session.track_temperature()
            if self.bar_track_temp.last != track_temp:
                self.bar_track_temp.last = track_temp
                temp_value = self.unit_temp(track_temp)
                self.bar_track_temp.setText(f"{temp_value:.1f}{self.symbol_temp}")
        except:
            pass
        
        # === Day/Night Detection ===
        try:
            # Get track clock time (seconds since midnight)
            track_time = api.read.session.track_clock_time()
            
            if track_time < 0:
                # Fallback: use elapsed time + start time
                start_et = api.read.session.start()
                current_et = api.read.session.elapsed()
                track_time = start_et + current_et
            
            # Convert to hours
            hours = (track_time / 3600) % 24
            
            # Determine day or night (6:00-18:00 = day)
            is_day = 6 <= hours < 18
            
            if self.icon_daynight.last != is_day:
                self.icon_daynight.last = is_day
                if is_day:
                    if "Sol" in self.icons:
                        self.icon_daynight.setPixmap(self.icons["Sol"])
                else:
                    if "noite" in self.icons:
                        self.icon_daynight.setPixmap(self.icons["noite"])
        except:
            pass
        
        # === Rain/Cloudy Detection ===
        try:
            raininess = api.read.session.raininess()
            wet_min, wet_max, wet_avg = api.read.session.wetness()
            
            # Determine weather condition
            # raininess: 0 = no rain chance, 1 = 100% rain
            # wetness: 0 = dry, 1 = fully wet
            
            weather_state = "clear"  # default: clear sky
            
            if raininess >= 0.5 or wet_avg >= 0.3:
                weather_state = "rain"
            elif raininess >= 0.1:
                weather_state = "cloudy"
            
            if self.icon_weather.last != weather_state:
                self.icon_weather.last = weather_state
                
                if weather_state == "rain":
                    if "Chuva" in self.icons:
                        self.icon_weather.setPixmap(self.icons["Chuva"])
                    self.icon_weather.show()
                elif weather_state == "cloudy":
                    if "nublado" in self.icons:
                        self.icon_weather.setPixmap(self.icons["nublado"])
                    self.icon_weather.show()
                else:
                    self.icon_weather.hide()
            
            # Update rain percentage if raining
            rain_pct = int(raininess * 100)
            if self.bar_rain_pct.last != rain_pct:
                self.bar_rain_pct.last = rain_pct
                if rain_pct > 0:
                    self.bar_rain_pct.setText(f"{rain_pct}%")
                    self.bar_rain_pct.show()
                else:
                    self.bar_rain_pct.hide()
                    
        except:
            pass
