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
Standings Hybrid Widget - Advanced Standings with Dynamic Hybrid Detection
Displays: Position | Logo | Class | Pilot | Best Lap | Gap | Energy%
"""

from .. import calculation as calc
from ..api_control import api
from ..const_common import TEXT_NOLAPTIME, TEXT_PLACEHOLDER
from ..formatter import random_color_class, shorten_driver_name
from ..module_info import minfo
from ..userfile.brand_logo import load_brand_logo_file
from ..userfile.heatmap import select_compound_symbol
from ..template.setting_classes import CLASSES_DEFAULT
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ._base import Overlay
from ._common import ExFrame
import os
import re


class Realtime(Overlay):
    """Draw widget - Advanced Standings with Hybrid Detection"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)

        # Fix path if needed
        if not os.path.exists(self.cfg.path.brand_logo):
            alt_path = os.path.join(os.getcwd(), "images", "logo marca")
            if os.path.exists(alt_path):
                self.cfg.path.brand_logo = alt_path + os.sep

        layout = self.set_grid_layout(gap_vert=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        self.drv_width = max(int(self.wcfg["driver_name_width"]), 1)
        self.brd_width = max(int(self.wcfg["brand_logo_width"]), 1)
        self.brd_height = max(self.wcfg["font_size"], 1)
        self.cls_width = max(int(self.wcfg["class_width"]), 0)
        self.gap_width = max(int(self.wcfg["time_gap_width"]), 1)
        self.gap_decimals = max(int(self.wcfg["time_gap_decimal_places"]), 0)
        self.tyre_width = max(int(self.wcfg.get("tyre_width", 6)), 1)
        self.energy_width = max(int(self.wcfg["energy_width"]), 3)
        self.num_width = max(int(self.wcfg.get("car_number_width", 3)), 2)
        self.dmg_width = max(int(self.wcfg.get("damage_width", 4)), 2)
        
        # Header configuration
        self.show_header = self.wcfg.get("show_header", True)
        self.show_session_info = self.wcfg.get("show_session_info", True)

        # Base style
        self.set_base_style(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Max display vehicles
        self.veh_range = min(max(int(self.wcfg["max_vehicles"]), 5), 126)
        self.pixmap_brandlogo = {}
        
        # Load checkered flag for finished vehicles
        self.pixmap_checkered_flag = None
        flag_path = os.path.join(os.getcwd(), "images", "bandeira", "bandeira-quadriculada.png")
        if os.path.exists(flag_path):
            self.pixmap_checkered_flag = QPixmap(flag_path)
            # Scale to fit gap column
            flag_height = self.wcfg["font_size"] + 4
            flag_width = int(flag_height * 1.5)  # Aspect ratio
            self.pixmap_checkered_flag = self.pixmap_checkered_flag.scaled(
                flag_width, flag_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        
        # Scan available logos
        self.available_logos = {}  # name_lower -> (real_name, extension)
        
        # Try multiple paths for logos
        possible_paths = [
            self.cfg.path.brand_logo,
            os.path.join(os.getcwd(), "images", "logo marca"),
            "images/logo marca/"
        ]
        
        self.logo_search_path = self.cfg.path.brand_logo
        
        for path in possible_paths:
            if os.path.isdir(path):
                # Check if this directory actually has images
                has_images = False
                temp_logos = {}
                
                for entry in os.scandir(path):
                    if entry.is_file():
                        name, ext = os.path.splitext(entry.name)
                        if ext.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                            temp_logos[name.lower()] = (name, ext)
                            has_images = True
                
                if has_images:
                    self.logo_search_path = path
                    if not self.logo_search_path.endswith(os.sep):
                        self.logo_search_path += os.sep
                    self.available_logos = temp_logos
                    break # Stop after finding valid path with images

        self.row_visible = [False] * self.veh_range
        
        # Track hybrid system detection per vehicle
        self.has_hybrid_system = [False] * self.veh_range
        
        # Track invalid lap times and their timestamps
        self.invalid_lap_time = {}  # {veh_idx: (laptime, timestamp)}
        self.invalid_lap_display_duration = 10.0  # seconds

        # Position column
        self.bar_style_pos = (
            self.set_qss(
                fg_color=self.wcfg["font_color_position"],
                bg_color=self.wcfg["bkg_color_position"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_player_position"],
                bg_color=self.wcfg["bkg_color_player_position"])
        )
        self.bars_pos = self.set_qlabel(
            style=self.bar_style_pos[0],
            width=2 * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_pos,
            column_index=0,
            hide_start=1,
        )

        # Brand logo column
        self.bar_style_brd = (
            self.set_qss(
                bg_color=self.wcfg["bkg_color_brand_logo"]),
            self.set_qss(
                bg_color=self.wcfg["bkg_color_player_brand_logo"])
        )
        self.bars_brd = self.set_qlabel(
            style=self.bar_style_brd[0],
            fixed_width=self.brd_width,  # Force fixed width
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_brd,
            column_index=1,
            hide_start=1,
        )

        # Car number column
        self.bar_style_num = (
            self.set_qss(
                fg_color=self.wcfg.get("font_color_car_number", "#FFFFFF"),
                bg_color=self.wcfg.get("bkg_color_car_number", "#333333")),
            self.set_qss(
                fg_color=self.wcfg.get("font_color_player_car_number", "#000000"),
                bg_color=self.wcfg.get("bkg_color_player_car_number", "#FFCC00"))
        )
        self.bars_num = self.set_qlabel(
            style=self.bar_style_num[0],
            width=self.num_width * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_num,
            column_index=2,
            hide_start=1,
        )

        # Position change column (gain/loss)
        if self.wcfg.get("show_position_change", False):
            self.bar_style_pgl = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_position_same"],
                    bg_color=self.wcfg["bkg_color_position_same"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_position_gain"],
                    bg_color=self.wcfg["bkg_color_position_gain"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_position_loss"],
                    bg_color=self.wcfg["bkg_color_position_loss"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_player_position_change"],
                    bg_color=self.wcfg["bkg_color_player_position_change"])
            )
            self.bars_pgl = self.set_qlabel(
                style=self.bar_style_pgl[0],
                width=3 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_pgl,
                column_index=3,
                hide_start=1,
            )

        # Class column
        bar_style_cls = self.set_qss(
            fg_color=self.wcfg["font_color_class"],
            bg_color=self.wcfg["bkg_color_class"]
        )
        self.bars_cls = self.set_qlabel(
            style=bar_style_cls,
            width=self.cls_width * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_cls,
            column_index=4,
            hide_start=1,
        )

        # Driver name column
        self.bar_style_drv = (
            self.set_qss(
                fg_color=self.wcfg["font_color_driver_name"],
                bg_color=self.wcfg["bkg_color_driver_name"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_player_driver_name"],
                bg_color=self.wcfg["bkg_color_player_driver_name"])
        )
        self.bars_drv = self.set_qlabel(
            style=self.bar_style_drv[0],
            width=self.drv_width * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_drv,
            column_index=5,
            hide_start=1,
        )

        # Best laptime column
        self.bar_style_blp = (
            self.set_qss(
                fg_color=self.wcfg["font_color_best_laptime"],
                bg_color=self.wcfg["bkg_color_best_laptime"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_player_best_laptime"],
                bg_color=self.wcfg["bkg_color_player_best_laptime"])
        )
        self.bars_blp = self.set_qlabel(
            style=self.bar_style_blp[0],
            width=9 * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_blp,
            column_index=6,
            hide_start=1,
        )

        # Last laptime column
        self.bar_style_llp = (
            self.set_qss(
                fg_color=self.wcfg.get("font_color_last_laptime", self.wcfg["font_color_best_laptime"]),
                bg_color=self.wcfg.get("bkg_color_last_laptime", self.wcfg["bkg_color_best_laptime"])),
            self.set_qss(
                fg_color=self.wcfg.get("font_color_player_last_laptime", self.wcfg["font_color_player_best_laptime"]),
                bg_color=self.wcfg.get("bkg_color_player_last_laptime", self.wcfg["bkg_color_player_best_laptime"]))
        )
        self.bars_llp = self.set_qlabel(
            style=self.bar_style_llp[0],
            width=9 * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_llp,
            column_index=7,
            hide_start=1,
        )

        # Time gap column
        self.bar_style_gap = (
            self.set_qss(
                fg_color=self.wcfg["font_color_time_gap"],
                bg_color=self.wcfg["bkg_color_time_gap"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_player_time_gap"],
                bg_color=self.wcfg["bkg_color_player_time_gap"])
        )
        self.bars_gap = self.set_qlabel(
            style=self.bar_style_gap[0],
            width=self.gap_width * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_gap,
            column_index=8,
            hide_start=1,
        )

        # Tyre column
        self.bar_style_tyre = (
            self.set_qss(
                fg_color=self.wcfg.get("font_color_tyre", "#FFFFFF"),
                bg_color=self.wcfg.get("bkg_color_tyre", "#222222")),
            self.set_qss(
                fg_color=self.wcfg.get("font_color_player_tyre", "#000000"),
                bg_color=self.wcfg.get("bkg_color_player_tyre", "#FFCC00"))
        )
        self.bars_tyre = self.set_qlabel(
            style=self.bar_style_tyre[0],
            width=self.tyre_width * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_tyre,
            column_index=9,
            hide_start=1,
        )

        # Energy column (with dynamic hybrid detection and dynamic backgrounds)
        self.bars_energy = self.set_qlabel(
            style="",  # Will be set dynamically
            width=self.energy_width * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_energy,
            column_index=10,
            hide_start=1,
        )

        # Vehicle damage column
        self.bar_style_dmg = (
            self.set_qss(
                fg_color=self.wcfg.get("font_color_damage", "#AAAAAA"),
                bg_color=self.wcfg.get("bkg_color_damage", "#2A2A2A")),
            self.set_qss(
                fg_color=self.wcfg.get("font_color_player_damage", "#000000"),
                bg_color=self.wcfg.get("bkg_color_player_damage", "#BBBBBB"))
        )
        self.bars_dmg = self.set_qlabel(
            style=self.bar_style_dmg[0],
            width=self.dmg_width * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_dmg,
            column_index=11,
            hide_start=1,
        )

        # Penalty column (dynamic - only shows when penalties exist)
        self.bar_style_penalty = (
            self.set_qss(
                fg_color=self.wcfg.get("font_color_penalty", "#FFFFFF"),
                bg_color=self.wcfg.get("bkg_color_penalty", "#FF0000")),
            self.set_qss(
                fg_color=self.wcfg.get("font_color_player_penalty", "#000000"),
                bg_color=self.wcfg.get("bkg_color_player_penalty", "#FF6600"))
        )
        self.bars_penalty = self.set_qlabel(
            style=self.bar_style_penalty[0],
            width=4 * font_m.width + bar_padx,
            count=self.veh_range,
        )
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_penalty,
            column_index=12,
            hide_start=1,
        )

        # Last data
        self.checked = False
        self.last_veh_data_version = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        try:
            if api.read is None:
                return
                
            if self.last_veh_data_version != minfo.vehicles.dataSetVersion:
                self.last_veh_data_version = minfo.vehicles.dataSetVersion

                if minfo.vehicles.totalVehicles < 1:
                    return

            # Get filtered list of vehicles/headers to display
            display_items = self.get_filtered_order()
            
            # Add race time at the very top (only once)
            if display_items and self.show_header:
                display_items.insert(0, self.create_race_time_header())
            
            # Update rows
            for row_idx, item in enumerate(display_items):
                if row_idx >= self.veh_range:
                    break
                
                if isinstance(item, dict):
                    if item.get("type") == "race_time":
                        self.update_race_time_row(row_idx, item)
                    elif item.get("type") == "legend":
                        self.update_legend_row(row_idx)
                    elif item.get("type") == "header":
                        self.update_header_row(row_idx, item)
                    elif "veh_idx" in item:
                        # Vehicle with class position
                        veh_idx = item["veh_idx"]
                        class_pos = item["class_pos"]
                        self.update_row(row_idx, veh_idx, minfo.vehicles.dataSet[veh_idx], class_pos)
                else:
                    # Legacy format (should not happen)
                    self.update_row(row_idx, item, minfo.vehicles.dataSet[item], 0)

            # Hide unused rows
            for row_idx in range(len(display_items), self.veh_range):
                if self.row_visible[row_idx]:
                    self.row_visible[row_idx] = False
                    self.bars_pos[row_idx].hide()
                    self.bars_brd[row_idx].hide()
                    self.bars_num[row_idx].hide()
                    if self.wcfg.get("show_position_change", False):
                        self.bars_pgl[row_idx].hide()
                    self.bars_cls[row_idx].hide()
                    self.bars_drv[row_idx].hide()
                    self.bars_blp[row_idx].hide()
                    self.bars_llp[row_idx].hide()
                    self.bars_gap[row_idx].hide()
                    self.bars_tyre[row_idx].hide()
                    self.bars_energy[row_idx].hide()
                    self.bars_dmg[row_idx].hide()
                    self.bars_penalty[row_idx].hide()
        except Exception:
            # Silently ignore errors to prevent crashes
            pass

    def get_filtered_order(self):
        """Get list of vehicle indices and class headers to display
        Regras:
        - 1 categoria: 10 carros (3 primeiros + 6 ao redor do player)
        - 2 categorias: 3 da outra + 8 da categoria do player
        - 3+ categorias: 3 de cada não-player + 8 da categoria do player
        """
        veh_total = minfo.vehicles.totalVehicles
        if veh_total < 1:
            return []

        # Group vehicles by class
        classes = {}  # name -> list of (place, veh_idx, is_player)
        player_class = None
        player_idx = -1
        
        for i in range(veh_total):
            cls = api.read.vehicle.class_name(i)
            place = api.read.vehicle.place(i)
            is_player = api.read.vehicle.is_player(i)
            
            if cls not in classes:
                classes[cls] = []
            classes[cls].append((place, i, is_player))
            
            if is_player:
                player_class = cls
                player_idx = i

        # Sort classes by leader position (overall place)
        sorted_classes = sorted(classes.items(), key=lambda x: min(v[0] for v in x[1]))
        
        # Reorder: Move player class to the BOTTOM (End of list)
        if player_class:
            p_cls_tuple = next((item for item in sorted_classes if item[0] == player_class), None)
            if p_cls_tuple:
                sorted_classes.remove(p_cls_tuple)
                sorted_classes.append(p_cls_tuple)

        # Determine limits based on class count
        num_classes = len(sorted_classes)
        
        if num_classes == 1:
            # 1 categoria: 10 carros (3 primeiros + 6 ao redor do player)
            limit_player = 10
            limit_top = 3
            limit_around = 6
            limit_others = 0
        elif num_classes == 2:
            # 2 categorias: 3 da outra + 8 da categoria do player
            limit_player = 8
            limit_top = 3
            limit_around = 5  # 8 - 3 primeiros = 5 ao redor
            limit_others = 3
        else:
            # 3+ categorias: 3 de cada não-player + 8 da categoria do player
            limit_player = 8
            limit_top = 3
            limit_around = 5
            limit_others = 3

        display_items = []
        legend_added = False  # Controle para adicionar legenda apenas uma vez
        
        for cls_name, vehicles in sorted_classes:
            # Sort vehicles in class by place
            vehicles.sort(key=lambda x: x[0])
            
            # Add Class Header with session info
            if self.show_header:
                header_info = self.create_header_info(cls_name, vehicles, cls_name == player_class)
                display_items.append(header_info)
            
            # Add legend only after the FIRST category header
            if self.show_header and not legend_added:
                display_items.append(self.create_legend_header())
                legend_added = True
            
            if cls_name == player_class:
                # Player class: Mostrar P1 (líder) + carros ao redor do player
                if num_classes == 1:
                    # 1 categoria: até 10 carros
                    indices = set()  # Usar set para evitar duplicatas
                    
                    # Encontrar player primeiro
                    p_idx = -1
                    for idx, v in enumerate(vehicles):
                        if v[2]:  # is_player
                            p_idx = idx
                            break
                    
                    # SEMPRE adicionar player primeiro
                    if p_idx != -1:
                        indices.add(p_idx)
                    
                    # Adicionar 3 primeiros
                    for i in range(min(3, len(vehicles))):
                        indices.add(i)
                    
                    # Se player não está nos 3 primeiros, adicionar ao redor dele
                    if p_idx != -1 and p_idx >= 3:
                        # Adicionar até 6 carros ao redor (3 antes, 3 depois)
                        for offset in range(-3, 4):
                            idx = p_idx + offset
                            if 0 <= idx < len(vehicles):
                                indices.add(idx)
                                if len(indices) >= limit_player:
                                    break
                    
                    # Se ainda tem espaço, preencher com próximos
                    if len(indices) < limit_player:
                        for i in range(len(vehicles)):
                            if i not in indices:
                                indices.add(i)
                                if len(indices) >= limit_player:
                                    break
                    
                    # Adicionar veículos com posição na classe
                    for i in sorted(indices):
                        display_items.append({"veh_idx": vehicles[i][1], "class_pos": i + 1})
                else:
                    # Multi-categoria: P1 (líder) + carros ao redor do player
                    indices = set()  # Usar set para evitar duplicatas
                    
                    # Encontrar player primeiro
                    p_idx = -1
                    for idx, v in enumerate(vehicles):
                        if v[2]:  # is_player
                            p_idx = idx
                            break
                    
                    # SEMPRE adicionar o P1 (líder da classe)
                    if len(vehicles) > 0:
                        indices.add(0)  # P1 sempre incluído
                    
                    # SEMPRE adicionar player
                    if p_idx != -1:
                        indices.add(p_idx)
                    
                    # Se player não é o líder, adicionar carros ao redor do player
                    if p_idx != -1 and p_idx > 0:
                        # Calcular quantos slots restam (descontando P1 e player)
                        slots_remaining = limit_player - 2  # -1 para P1, -1 para player
                        
                        # Distribuir slots: metade antes, metade depois do player
                        slots_before = slots_remaining // 2
                        slots_after = slots_remaining - slots_before
                        
                        # Adicionar carros ANTES do player (mais próximos primeiro)
                        for offset in range(1, slots_before + 2):
                            idx = p_idx - offset
                            if idx > 0:  # idx 0 já é o P1
                                indices.add(idx)
                        
                        # Adicionar carros DEPOIS do player
                        for offset in range(1, slots_after + 2):
                            idx = p_idx + offset
                            if idx < len(vehicles):
                                indices.add(idx)
                    
                    # Se ainda tem espaço, preencher com próximos após o líder
                    if len(indices) < limit_player:
                        for i in range(1, len(vehicles)):  # Começar do 2º
                            if i not in indices:
                                indices.add(i)
                                if len(indices) >= limit_player:
                                    break
                    
                    # Adicionar veículos com posição na classe (em ordem)
                    for i in sorted(indices):
                        display_items.append({"veh_idx": vehicles[i][1], "class_pos": i + 1})
            else:
                # Other class: Top 3 (ou 4 para 2 categorias)
                for idx, v in enumerate(vehicles[:limit_others]):
                    # (veh_idx, position_in_class)
                    display_items.append({"veh_idx": v[1], "class_pos": idx + 1})
        
        return display_items

    def create_race_time_header(self):
        """Create race time header to show at the very top (only once)"""
        # Session type
        session_index = api.read.session.session_type()
        if session_index == 4:  # Race
            session_type = "CORRIDA"
        elif session_index == 2:  # Qualify
            session_type = "QUALIFICAÇÃO"
        elif session_index == 3:  # Warmup
            session_type = "WARMUP"
        else:  # Practice, Testday, or other
            session_type = "PRÁTICA"
        
        # Time remaining
        try:
            time_remaining = api.read.session.remaining()
            if time_remaining > 0:
                hours = int(time_remaining // 3600)
                mins = int((time_remaining % 3600) // 60)
                secs = int(time_remaining % 60)
                if hours > 0:
                    time_str = f"{hours}h{mins:02d}:{secs:02d}"
                else:
                    time_str = f"{mins}:{secs:02d}"
            else:
                time_str = "--:--"
        except:
            time_str = "--:--"
        
        # Track time (horário da pista - clock da sessão)
        try:
            # mStartET = seconds since midnight of the event start
            start_et = api.read.session.start()
            # mCurrentET = current session time elapsed
            current_et = api.read.session.elapsed()
            
            # Calculate current track time = start time + elapsed time
            track_clock_seconds = start_et + current_et
            
            if track_clock_seconds > 0:
                # Convert to hours:minutes (24h format)
                hours = int(track_clock_seconds // 3600) % 24
                mins = int((track_clock_seconds % 3600) // 60)
                track_time_str = f"{hours:02d}:{mins:02d}"
            else:
                track_time_str = "--:--"
        except:
            track_time_str = "--:--"
        
        # System time (horário da máquina)
        try:
            from datetime import datetime
            now = datetime.now()
            system_time_str = now.strftime("%H:%M")
        except:
            system_time_str = "--:--"
        
        return {
            "type": "race_time",
            "session_type": session_type,
            "time_remaining": time_str,
            "track_time": track_time_str,
            "system_time": system_time_str
        }

    def create_legend_header(self):
        """Create legend row explaining column meanings"""
        return {
            "type": "legend"
        }

    def create_header_info(self, class_name, vehicles, is_player_class):
        """Create header dictionary with session information"""
        total_cars = len(vehicles)
        cars_started = sum(1 for v in vehicles if api.read.vehicle.place(v[1]) > 0)
        
        # Session type (not used in category header anymore)
        session_index = api.read.session.session_type()
        if session_index == 4:  # Race
            session_type = "CORRIDA"
        elif session_index == 2:  # Qualify
            session_type = "QUALIFICAÇÃO"
        elif session_index == 3:  # Warmup
            session_type = "WARMUP"
        else:  # Practice, Testday, or other
            session_type = "PRÁTICA"
        
        # Time remaining
        try:
            time_remaining = api.read.session.remaining()
            if time_remaining > 0:
                mins = int(time_remaining // 60)
                secs = int(time_remaining % 60)
                time_str = f"{mins}:{secs:02d}"
            else:
                time_str = "--:--"
        except:
            time_str = "--:--"
        
        # Laps info - baseado no líder em corrida, ou no player em quali/prática
        laps_info = "Volta: --"
        try:
            if vehicles:
                if api.read.session.in_race():
                    # Em corrida: usar líder da categoria
                    leader_idx = vehicles[0][1]  # vehicles = [(place, veh_idx, is_player), ...]
                    completed = api.read.lap.completed_laps(leader_idx)
                    total_laps = api.read.session.lap_total()
                    
                    if total_laps > 0:
                        # Corrida com número de voltas definido
                        laps_info = f"Volta: {completed}/{total_laps}"
                    else:
                        # Corrida por tempo - calcular voltas previstas
                        try:
                            time_remaining = api.read.session.remaining()
                            if time_remaining > 0 and completed > 0:
                                # Pegar tempo médio de volta do líder
                                best_lap = api.read.timing.best_laptime(leader_idx)
                                if best_lap > 0:
                                    predicted_laps = completed + (time_remaining / best_lap)
                                    laps_info = f"Volta: {completed}/{predicted_laps:.1f}"
                                else:
                                    laps_info = f"Volta: {completed}"
                            else:
                                laps_info = f"Volta: {completed}"
                        except:
                            laps_info = f"Volta: {completed}"
                else:
                    # Quali/Prática: usar voltas do player se for a categoria do player
                    if is_player_class:
                        # Encontrar o player na lista de veículos
                        player_idx = None
                        for place, veh_idx, is_player in vehicles:
                            if is_player:
                                player_idx = veh_idx
                                break
                        
                        if player_idx is not None:
                            completed = api.read.lap.completed_laps(player_idx)
                            laps_info = f"Volta: {completed}"
                        else:
                            # Fallback para líder se player não encontrado
                            leader_idx = vehicles[0][1]
                            completed = api.read.lap.completed_laps(leader_idx)
                            laps_info = f"Volta: {completed}"
                    else:
                        # Outras categorias: usar líder
                        leader_idx = vehicles[0][1]
                        completed = api.read.lap.completed_laps(leader_idx)
                        laps_info = f"Volta: {completed}"
        except:
            pass
        
        return {
            "type": "header",
            "class_name": class_name,
            "total_cars": total_cars,
            "cars_started": cars_started,
            "session_type": session_type,
            "time_remaining": time_str,
            "laps_info": laps_info
        }

    def update_race_time_row(self, row_idx, race_time_info):
        """Display race time at the very top - spans all columns"""
        if not self.row_visible[row_idx]:
            self.row_visible[row_idx] = True
        
        # Criar texto completo da sessão com horários
        session_text = (
            f"  {race_time_info['session_type']}  |  "
            f"TEMPO: {race_time_info['time_remaining']}  |  "
            f"SESSÃO: {race_time_info['track_time']}  |  "
            f"LOCAL: {race_time_info['system_time']}  "
        )
        
        # Pegar o layout grid
        layout = self.layout()
        
        # Show session info in first column, spanning all columns
        self.bars_pos[row_idx].show()
        self.bars_pos[row_idx].setText(session_text)
        self.bars_pos[row_idx].setWordWrap(False)
        self.bars_pos[row_idx].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # Fundo cinza - herda font_size global
        padding = max(2, int(self.wcfg["font_size"] * 0.25))
        self.bars_pos[row_idx].setStyleSheet(
            f"color: #FFFFFF; background-color: #555555; font-weight: bold; "
            f"border: 1px solid #666666; padding: {padding}px {padding * 3}px;"
        )
        
        # Fazer o widget ocupar todas as 13 colunas (índices 0 a 12)
        layout.addWidget(self.bars_pos[row_idx], row_idx, 0, 1, 13)
        
        # Hide all other columns for this row
        self.bars_brd[row_idx].hide()
        self.bars_num[row_idx].hide()
        
        if self.wcfg.get("show_position_change", False):
            self.bars_pgl[row_idx].hide()
        
        self.bars_cls[row_idx].hide()
        self.bars_drv[row_idx].hide()
        self.bars_blp[row_idx].hide()
        self.bars_llp[row_idx].hide()
        self.bars_gap[row_idx].hide()
        self.bars_tyre[row_idx].hide()
        self.bars_energy[row_idx].hide()
        self.bars_dmg[row_idx].hide()
        self.bars_penalty[row_idx].hide()

    def update_legend_row(self, row_idx):
        """Display legend explaining columns"""
        if not self.row_visible[row_idx]:
            self.row_visible[row_idx] = True
        
        legend_color = "#222222"
        text_color = "#AAAAAA"
        
        # P = Posição
        self.bars_pos[row_idx].show()
        self.bars_pos[row_idx].setText("P")
        self.bars_pos[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Logo = Marca
        self.bars_brd[row_idx].show()
        self.bars_brd[row_idx].setText("Mar")
        self.bars_brd[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # # = Número
        self.bars_num[row_idx].show()
        self.bars_num[row_idx].setText("#")
        self.bars_num[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # +/- = Ganho/Perda
        if self.wcfg.get("show_position_change", False):
            self.bars_pgl[row_idx].show()
            self.bars_pgl[row_idx].setText("+/-")
            self.bars_pgl[row_idx].setStyleSheet(
                f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
            )
        
        # Cls = Classe
        self.bars_cls[row_idx].show()
        self.bars_cls[row_idx].setText("Cls")
        self.bars_cls[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Driver = Piloto
        self.bars_drv[row_idx].show()
        self.bars_drv[row_idx].setText("Piloto")
        self.bars_drv[row_idx].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.bars_drv[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Best = Melhor volta
        self.bars_blp[row_idx].show()
        self.bars_blp[row_idx].setText("Best")
        self.bars_blp[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Last = Última volta
        self.bars_llp[row_idx].show()
        self.bars_llp[row_idx].setText("Last")
        self.bars_llp[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Gap = Diferença
        self.bars_gap[row_idx].show()
        self.bars_gap[row_idx].setText("Gap")
        self.bars_gap[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Tyre = Pneu
        self.bars_tyre[row_idx].show()
        self.bars_tyre[row_idx].setText("Tyr")
        self.bars_tyre[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Energy = Energia
        self.bars_energy[row_idx].show()
        self.bars_energy[row_idx].setText("Bat")
        self.bars_energy[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Dmg = Dano
        self.bars_dmg[row_idx].show()
        self.bars_dmg[row_idx].setText("Dmg")
        self.bars_dmg[row_idx].setStyleSheet(
            f"color: {text_color}; background-color: {legend_color}; font-style: italic; border: 1px solid #444444;"
        )
        
        # Esconde coluna de penalização (não usada mais)
        self.bars_penalty[row_idx].hide()

    def update_header_row(self, row_idx, header_info):
        """Display a header row for the class - spans all columns"""
        if not self.row_visible[row_idx]:
            self.row_visible[row_idx] = True
        
        class_name = header_info["class_name"]
        
        # Get class color
        cls_color = "#444444"  # Default
        for key, data in CLASSES_DEFAULT.items():
            if key.lower() in class_name.lower() or data.get("alias", "").lower() == class_name.lower():
                cls_color = data.get("color", "#444444")
                break

        # Criar texto completo do cabeçalho da categoria com contagem de voltas
        header_text = f"  {class_name.upper()}  |  Carros: {header_info['cars_started']}/{header_info['total_cars']}  |  {header_info['laps_info']}  "
        
        # Pegar o layout grid
        layout = self.layout()
        
        # Show category header spanning all columns
        self.bars_pos[row_idx].show()
        self.bars_pos[row_idx].setText(header_text)
        self.bars_pos[row_idx].setWordWrap(False)
        self.bars_pos[row_idx].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # Herda font_size global
        padding = max(2, int(self.wcfg["font_size"] * 0.2))
        self.bars_pos[row_idx].setStyleSheet(
            f"color: #FFFFFF; background-color: {cls_color}; font-weight: bold; "
            f"border: 1px solid {cls_color}; padding: {padding}px {padding * 4}px;"
        )
        
        # Fazer o widget ocupar todas as 13 colunas
        layout.addWidget(self.bars_pos[row_idx], row_idx, 0, 1, 13)
        
        # Hide all other columns for this row
        self.bars_brd[row_idx].hide()
        self.bars_num[row_idx].hide()
        
        if self.wcfg.get("show_position_change", False):
            self.bars_pgl[row_idx].hide()
        
        self.bars_cls[row_idx].hide()
        self.bars_drv[row_idx].hide()
        self.bars_blp[row_idx].hide()
        self.bars_llp[row_idx].hide()
        self.bars_gap[row_idx].hide()
        self.bars_tyre[row_idx].hide()
        self.bars_energy[row_idx].hide()
        self.bars_dmg[row_idx].hide()
        self.bars_penalty[row_idx].hide()

    def update_row(self, row_idx, veh_idx, data, class_pos=0):
        """Update row with vehicle data
        Args:
            row_idx: Row index in the display
            veh_idx: Vehicle index in the data
            data: Vehicle data object
            class_pos: Position within the class (1-based, 0 means use overall position)
        """
        # Safety check - widget might be closing
        if self.wcfg is None or api.read is None:
            return
            
        # Position
        if not self.row_visible[row_idx]:
            self.row_visible[row_idx] = True
        
        # Ensure all columns are visible (might have been hidden by header)
        self.bars_pos[row_idx].show()
        self.bars_brd[row_idx].show()
        self.bars_num[row_idx].show()
        if self.wcfg.get("show_position_change", False):
            self.bars_pgl[row_idx].show()
        self.bars_cls[row_idx].show()
        self.bars_drv[row_idx].show()
        self.bars_blp[row_idx].show()
        self.bars_llp[row_idx].show()
        self.bars_gap[row_idx].show()
        self.bars_tyre[row_idx].show()
        self.bars_energy[row_idx].show()
        self.bars_dmg[row_idx].show()
        # Penalty column is conditional, will be hidden by default and shown only if needed

        # Reset alignment for driver name
        self.bars_drv[row_idx].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Get actual place for gap calculation
        place = api.read.vehicle.place(veh_idx)

        # Update position - usar posição na classe se disponível
        if class_pos > 0:
            self.bars_pos[row_idx].setText(f"{class_pos:02d}")
        else:
            self.bars_pos[row_idx].setText(f"{place:02d}")
        self.bars_pos[row_idx].setStyleSheet(self.bar_style_pos[data.isPlayer])

        # Update brand logo
        veh_name = api.read.vehicle.vehicle_name(veh_idx)
        veh_class = api.read.vehicle.class_name(veh_idx)
        team_name = api.read.vehicle.team_name(veh_idx)
        self.update_brand_logo(self.bars_brd[row_idx], veh_name, veh_class, team_name, data.isPlayer)

        # Update car number - extrai do nome do veículo
        car_number = None
        
        # Primeira tentativa: extrair do nome do veículo (contém o número real)
        try:
            veh_name = api.read.vehicle.vehicle_name(veh_idx)
            # Procura por padrão #número no nome do veículo
            match = re.search(r'#(\d+)', veh_name)
            if match:
                car_number = int(match.group(1))
        except:
            pass
        
        # Se não achou no nome do veículo, tenta do nome do piloto
        if car_number is None or car_number == 0:
            try:
                driver_name = api.read.vehicle.driver_name(veh_idx)
                # Procura por padrão #número no nome do piloto
                match = re.search(r'#(\d+)', driver_name)
                if match:
                    car_number = int(match.group(1))
            except:
                pass
        
        # Se ainda não achou, usa slot_id como fallback
        if car_number is None or car_number == 0:
            try:
                slot_num = api.read.vehicle.slot_id(veh_idx)
                if slot_num > 0 and slot_num <= 999:
                    car_number = slot_num
            except:
                pass
        
        # Formata o número
        if car_number is not None and car_number > 0:
            if car_number > 99:
                self.bars_num[row_idx].setText(f"#{car_number:03d}")
            else:
                self.bars_num[row_idx].setText(f"#{car_number}")
        else:
            # Fallback: usa posição + 1
            self.bars_num[row_idx].setText(f"#{veh_idx + 1}")
        
        self.bars_num[row_idx].setStyleSheet(self.bar_style_num[data.isPlayer])

        # Update position change (gain/loss)
        if self.wcfg.get("show_position_change", False):
            if self.wcfg.get("show_position_change_in_class", True):
                pos_diff = data.qualifyInClass - data.positionInClass
            else:
                pos_diff = data.qualifyOverall - data.positionOverall
            
            if pos_diff > 0:
                text = f"▲{pos_diff: >2}"
                color_index = 1  # gain
            elif pos_diff < 0:
                text = f"▼{-pos_diff: >2}"
                color_index = 2  # loss
            else:
                text = "- 0"
                color_index = 0  # same
            
            if data.isPlayer:
                color_index = 3  # player color
            
            self.bars_pgl[row_idx].setText(text)
            self.bars_pgl[row_idx].setStyleSheet(self.bar_style_pgl[color_index])
            self.bars_pgl[row_idx].show()

        # Update class
        # Clean class name: remove special chars, keep only letters/numbers
        clean_class = re.sub(r'[^a-zA-Z0-9]', '', veh_class)
        # Abbreviate to max 5 chars
        display_class = clean_class[:5].upper() if len(clean_class) > 5 else clean_class.upper()
        self.bars_cls[row_idx].setText(
            display_class if self.cls_width else ""
        )
        
        # Get class color for class label
        cls_color = "#444444"
        for key, cdata in CLASSES_DEFAULT.items():
            if key.lower() in veh_class.lower() or cdata.get("alias", "").lower() == veh_class.lower():
                cls_color = cdata.get("color", "#444444")
                break
        
        # Apply class color to class column
        self.bars_cls[row_idx].setStyleSheet(
            f"color: #FFFFFF; background-color: {cls_color}; padding-left: 2px;"
        )

        # Update driver name with penalty indication
        drv_name = api.read.vehicle.driver_name(veh_idx)
        driver_text = shorten_driver_name(drv_name)
        
        # Check for penalties
        penalty_text = ""
        has_penalty = False
        try:
            finish_status = api.read.vehicle.finish_state(veh_idx)
            num_penalties = api.read.vehicle.number_penalties(veh_idx)
            
            # Check for DNF/DQ first
            if finish_status == 2:
                penalty_text = "DNF"
                has_penalty = True
            elif finish_status == 3:
                penalty_text = "DQ"
                has_penalty = True
            elif num_penalties > 0:
                # For player: try to get Stop & Go state
                if data.isPlayer:
                    try:
                        pit_estimate = api.read.vehicle.pit_estimate(veh_idx)
                        state_stopgo = pit_estimate[4]
                        if state_stopgo == 1:
                            penalty_text = f"S&G×{num_penalties}" if num_penalties > 1 else "S&G"
                        elif state_stopgo == 2:
                            penalty_text = f"S&G+×{num_penalties}" if num_penalties > 1 else "S&G+"
                        else:
                            penalty_text = f"P×{num_penalties}" if num_penalties > 1 else "P"
                    except:
                        penalty_text = f"P×{num_penalties}" if num_penalties > 1 else "P"
                else:
                    penalty_text = f"P×{num_penalties}" if num_penalties > 1 else "P"
                has_penalty = True
        except:
            pass
        
        # Set driver name - se tem punição, adiciona espaços para empurrar a punição para a direita
        if has_penalty:
            # Calcula espaços necessários para alinhar punição à direita
            available_width = self.drv_width - len(penalty_text)
            driver_padded = driver_text[:available_width].ljust(available_width)
            self.bars_drv[row_idx].setText(driver_padded + penalty_text)
        else:
            self.bars_drv[row_idx].setText(driver_text)
        
        # Check pit status for driver name color
        in_pits = api.read.vehicle.in_pits(veh_idx)
        
        # Set style based on penalty or pit status
        if has_penalty:
            # Red background with white text for penalties
            self.bars_drv[row_idx].setStyleSheet(
                "color: #FFFFFF; background-color: #FF0000; padding-left: 5px; font-weight: bold;"
            )
        elif in_pits:
            # Yellow text for pit status
            self.bars_drv[row_idx].setStyleSheet(
                f"color: #FFFF00; background-color: {self.wcfg['bkg_color_driver_name']}; padding-left: 5px;"
            )
        else:
            # Normal style with padding
            style = self.bar_style_drv[data.isPlayer]
            if "padding-left" not in style:
                style += "padding-left: 5px;"
            self.bars_drv[row_idx].setStyleSheet(style)

        # Update tyre compound
        if self.tyre_width:
            f_compound = api.read.vehicle.front_tire_compound_name(veh_idx)
            r_compound = api.read.vehicle.rear_tire_compound_name(veh_idx)
            
            f_sym = select_compound_symbol(f_compound)
            r_sym = select_compound_symbol(r_compound)
            
            # Determine display text
            if f_sym == r_sym:
                compound_str = f_sym
            else:
                # Mixed compounds: Show both (e.g. "S M")
                compound_str = f"{f_sym} {r_sym}"
            
            self.bars_tyre[row_idx].setText(compound_str)
            
            # Determine background color based on compound and class (LMU/WEC Rules)
            def get_tyre_rank_color(sym, v_class):
                # Returns (Rank, HexColor, TextColor)
                # Rank: Lower is "Softer/Faster" for display priority
                sym = sym.upper()
                v_class = v_class.lower()
                
                is_hyper = any(x in v_class for x in ["hyper", "lmh", "lmdh"])
                is_goodyear_class = any(x in v_class for x in ["gt3", "lmp2", "lmp3", "gte"])

                if is_hyper:
                    # Hypercar (Michelin) Rules
                    if "S" in sym: return (1, "#FFFFFF", "#000000") # Soft -> White (Black Text)
                    if "M" in sym: return (2, "#FFFF00", "#000000") # Medium -> Yellow (Black Text)
                    if "H" in sym: return (3, "#FF0000", "#FFFFFF") # Hard -> Red (White Text)
                    if "I" in sym: return (4, "#000000", "#FFFFFF") # Inter -> Black (White Text)
                    if "W" in sym: return (5, "#0000FF", "#FFFFFF") # Wet -> Blue (White Text)
                
                elif is_goodyear_class:
                    # Goodyear Rules (GT3, LMP2, LMP3)
                    # Yellow = Slick (Dry), White = Wet
                    if any(x in sym for x in ["S", "M", "H"]): return (1, "#FFFF00", "#000000") # Any Slick -> Yellow
                    if "W" in sym or "I" in sym: return (2, "#FFFFFF", "#000000") # Wet/Inter -> White
                
                # Fallback / Generic (Standard Sim Racing Colors)
                if "S" in sym: return (1, "#FF0000", "#FFFFFF") # Soft -> Red
                if "M" in sym: return (2, "#FFFF00", "#000000") # Medium -> Yellow
                if "H" in sym: return (3, "#FFFFFF", "#000000") # Hard -> White
                if "I" in sym: return (4, "#00FF00", "#000000") # Inter -> Green
                if "W" in sym: return (5, "#0000FF", "#FFFFFF") # Wet -> Blue
                
                return (99, "#888888", "#FFFFFF") # Unknown/Grey

            f_rank, f_color, f_text = get_tyre_rank_color(f_sym, veh_class)
            r_rank, r_color, r_text = get_tyre_rank_color(r_sym, veh_class)
            
            # Logic: "vcor fica no qul é maiore, se fica 2 de cada sempre colocar o caor do mais marcil"
            # Since we check Front vs Rear (2 vs 2), we pick the "Softer" (Lower Rank)
            
            final_color = f_color if f_rank <= r_rank else r_color
            final_text_color = f_text if f_rank <= r_rank else r_text
            
            self.bars_tyre[row_idx].setStyleSheet(
                f"background-color: {final_color}; color: {final_text_color}; font-weight: bold;"
            )

        # Update best laptime
        # Verifica se o veículo terminou a sessão (corrida ou classificação)
        try:
            finish_state = api.read.vehicle.finish_state(veh_idx)
            if finish_state == 1:  # Finished!
                # Mostra bandeira quadriculada no lugar do best lap
                if self.pixmap_checkered_flag and not self.pixmap_checkered_flag.isNull():
                    self.bars_blp[row_idx].setPixmap(self.pixmap_checkered_flag)
                    self.bars_blp[row_idx].setText("")
                else:
                    self.bars_blp[row_idx].setText("FIN")
                self.bars_blp[row_idx].setStyleSheet(self.bar_style_blp[data.isPlayer])
            else:
                # Mostra best lap normalmente
                self.bars_blp[row_idx].setPixmap(QPixmap())  # Limpa bandeira anterior
                best_time = api.read.timing.best_laptime(veh_idx)
                if best_time > 0:
                    self.bars_blp[row_idx].setText(calc.sec2laptime(best_time))
                else:
                    self.bars_blp[row_idx].setText(TEXT_NOLAPTIME)
                self.bars_blp[row_idx].setStyleSheet(self.bar_style_blp[data.isPlayer])
        except:
            # Fallback: mostra best lap normalmente
            self.bars_blp[row_idx].setPixmap(QPixmap())
            best_time = api.read.timing.best_laptime(veh_idx)
            if best_time > 0:
                self.bars_blp[row_idx].setText(calc.sec2laptime(best_time))
            else:
                self.bars_blp[row_idx].setText(TEXT_NOLAPTIME)
            self.bars_blp[row_idx].setStyleSheet(self.bar_style_blp[data.isPlayer])

        # Update last laptime - mostra a ÚLTIMA VOLTA COMPLETADA (sempre, mesmo se inválida)
        last_time = api.read.timing.last_laptime(veh_idx)
        current_time = api.read.timing.elapsed()
        
        # Sempre mostra a última volta, mesmo que seja 0 ou negativa
        if last_time != 0:
            # Se for negativa, converte para positiva para mostrar o tempo
            display_time = abs(last_time)
            laptime_text = calc.sec2laptime(display_time)
            
            # Verifica se a volta foi válida
            try:
                count_lap_flag = api.read.vehicle.count_lap_flag(veh_idx)
                is_invalid = (last_time < 0) or (count_lap_flag == 0) or (count_lap_flag == 1)
                
                if is_invalid:
                    # Volta inválida - armazena o tempo e timestamp
                    if veh_idx not in self.invalid_lap_time or self.invalid_lap_time[veh_idx][0] != display_time:
                        self.invalid_lap_time[veh_idx] = (display_time, current_time)
                    
                    # Verifica se já passou 10 segundos
                    time_elapsed = current_time - self.invalid_lap_time[veh_idx][1]
                    
                    if time_elapsed < self.invalid_lap_display_duration:
                        # Mostra tempo inválido em vermelho por 10 segundos
                        self.bars_llp[row_idx].setText(laptime_text)
                        if data.isPlayer:
                            style = f"color: #FF0000; background-color: {self.wcfg.get('bkg_color_player_last_laptime', self.wcfg['bkg_color_player_best_laptime'])};"
                        else:
                            style = f"color: #FF0000; background-color: {self.wcfg.get('bkg_color_last_laptime', self.wcfg['bkg_color_best_laptime'])};"
                        self.bars_llp[row_idx].setStyleSheet(style)
                    else:
                        # Após 10 segundos, mostra "-:--.---"
                        self.bars_llp[row_idx].setText(TEXT_NOLAPTIME)
                        self.bars_llp[row_idx].setStyleSheet(self.bar_style_llp[data.isPlayer])
                else:
                    # Volta válida - remove do registro de inválidas se existir
                    if veh_idx in self.invalid_lap_time:
                        del self.invalid_lap_time[veh_idx]
                    
                    self.bars_llp[row_idx].setText(laptime_text)
                    self.bars_llp[row_idx].setStyleSheet(self.bar_style_llp[data.isPlayer])
            except:
                # Se falhar ao obter flag, verifica apenas pelo sinal do tempo
                if last_time < 0:
                    # Texto vermelho para tempo negativo
                    if veh_idx not in self.invalid_lap_time or self.invalid_lap_time[veh_idx][0] != display_time:
                        self.invalid_lap_time[veh_idx] = (display_time, current_time)
                    
                    time_elapsed = current_time - self.invalid_lap_time[veh_idx][1]
                    
                    if time_elapsed < self.invalid_lap_display_duration:
                        self.bars_llp[row_idx].setText(laptime_text)
                        if data.isPlayer:
                            style = f"color: #FF0000; background-color: {self.wcfg.get('bkg_color_player_last_laptime', self.wcfg['bkg_color_player_best_laptime'])};"
                        else:
                            style = f"color: #FF0000; background-color: {self.wcfg.get('bkg_color_last_laptime', self.wcfg['bkg_color_best_laptime'])};"
                        self.bars_llp[row_idx].setStyleSheet(style)
                    else:
                        self.bars_llp[row_idx].setText(TEXT_NOLAPTIME)
                        self.bars_llp[row_idx].setStyleSheet(self.bar_style_llp[data.isPlayer])
                else:
                    if veh_idx in self.invalid_lap_time:
                        del self.invalid_lap_time[veh_idx]
                    self.bars_llp[row_idx].setText(laptime_text)
                    self.bars_llp[row_idx].setStyleSheet(self.bar_style_llp[data.isPlayer])
        else:
            # Nenhuma volta completada ainda - mostra apenas "--"
            self.bars_llp[row_idx].setText("--")
            self.bars_llp[row_idx].setStyleSheet(self.bar_style_llp[data.isPlayer])

        # Update time gap (relative distance in race)
        self.update_gap(row_idx, veh_idx, place, veh_class, data.isPlayer)

        # Update energy with dynamic hybrid detection and dynamic backgrounds
        self.update_energy_dynamic(row_idx, veh_idx, data.isPlayer)

        # Update vehicle damage
        self.update_damage(row_idx, veh_idx, data.isPlayer)

    def update_gap(self, row_idx, veh_idx, place, veh_class, is_player):
        """Update gap - relative distance in race, lap times in quali/prac
        
        Durante CORRIDA:
        - MESMA CATEGORIA do player: Gap relativo ao PLAYER
        - OUTRA CATEGORIA: Gap relativo ao LÍDER (P1) da categoria do veículo
        """
        
        # Get player index and class
        player_idx = api.read.vehicle.player_index()
        player_class = api.read.vehicle.class_name(player_idx)
        
        # In RACE mode
        if api.read.session.in_race():
            # If this IS the player
            if is_player:
                self.bars_gap[row_idx].setText("PLAYER")
                self.bars_gap[row_idx].setStyleSheet(self.bar_style_gap[is_player])
                return
            
            try:
                # Determinar referência: mesma categoria = player, outra categoria = líder da categoria
                if veh_class == player_class:
                    # Mesma categoria do player - gap relativo ao PLAYER
                    reference_idx = player_idx
                else:
                    # Outra categoria - gap relativo ao LÍDER (P1) da categoria do veículo
                    reference_idx = self.find_class_leader_index(veh_class)
                    
                    # Se não encontrar líder, usa placeholder
                    if reference_idx == -1:
                        self.bars_gap[row_idx].setText(TEXT_PLACEHOLDER)
                        self.bars_gap[row_idx].setStyleSheet(self.bar_style_gap[is_player])
                        return
                    
                    # Se o veículo É o líder da categoria dele
                    if veh_idx == reference_idx:
                        self.bars_gap[row_idx].setText("P1")
                        self.bars_gap[row_idx].setStyleSheet(self.bar_style_gap[is_player])
                        return
                
                # Calcular gap usando distância na pista (mais estável que laps)
                gap_time = self.calculate_time_gap_by_distance(veh_idx, reference_idx)
                
                if gap_time is not None:
                    # Verificar se diferença de voltas é >= 1
                    ref_laps = api.read.lap.completed_laps(reference_idx)
                    ref_progress = api.read.lap.progress(reference_idx)
                    ref_total = ref_laps + ref_progress
                    
                    veh_laps = api.read.lap.completed_laps(veh_idx)
                    veh_progress = api.read.lap.progress(veh_idx)
                    veh_total = veh_laps + veh_progress
                    
                    lap_diff = veh_total - ref_total
                    
                    # Se diferença de volta >= 1, mostra voltas
                    if abs(lap_diff) >= 1.0:
                        if lap_diff > 0:
                            self.bars_gap[row_idx].setText(f"+{int(lap_diff)}L")
                        else:
                            self.bars_gap[row_idx].setText(f"{int(lap_diff)}L")
                    else:
                        # Mostra gap em segundos
                        if gap_time > 0:
                            gap_text = f"+{gap_time:.{self.gap_decimals}f}s"
                        else:
                            gap_text = f"{gap_time:.{self.gap_decimals}f}s"
                        self.bars_gap[row_idx].setText(gap_text)
                else:
                    self.bars_gap[row_idx].setText(TEXT_PLACEHOLDER)
                    
            except (AttributeError, TypeError, ValueError):
                self.bars_gap[row_idx].setText(TEXT_PLACEHOLDER)
        else:
            # QUALI/PRACTICE: Show gap to class leader's best lap
            class_leader_idx = self.find_class_leader_index(veh_class)
            
            if class_leader_idx == -1:
                self.bars_gap[row_idx].setText(TEXT_PLACEHOLDER)
            elif veh_idx == class_leader_idx:
                self.bars_gap[row_idx].setText("--")
            else:
                t_leader = api.read.timing.best_laptime(class_leader_idx)
                t_veh = api.read.timing.best_laptime(veh_idx)
                
                if t_leader > 0 and t_veh > 0:
                    diff = t_veh - t_leader
                    self.bars_gap[row_idx].setText(f"+{diff:.3f}")
                else:
                    self.bars_gap[row_idx].setText(TEXT_PLACEHOLDER)
        
        self.bars_gap[row_idx].setStyleSheet(self.bar_style_gap[is_player])

    def update_energy_dynamic(self, row_idx, veh_idx, is_player):
        """
        Update energy with DYNAMIC HYBRID DETECTION
        - Automatically detects if vehicle has hybrid system OR Virtual Energy (GT3)
        - Shows percentage if hybrid system detected
        - Shows '--' for non-hybrid vehicles
        """
        try:
            # Check electric boost motor state: 0=unavailable
            boost_state = api.read.vehicle.electric_boost_motor_state(veh_idx)
            
            # Get battery charge fraction [0.0-1.0]
            charge_fraction = api.read.vehicle.battery_charge_fraction(veh_idx)
            
            # Get Virtual Energy
            virtual_energy = api.read.vehicle.virtual_energy(veh_idx)
            max_virtual_energy = api.read.vehicle.max_virtual_energy(veh_idx)
            
            # Check class for energy eligibility (to avoid false positives on LMP2 etc)
            veh_class_str = api.read.vehicle.class_name(veh_idx).lower()
            
            # Split keywords to distinguish between Real Hybrids and Virtual Energy classes
            hybrid_keywords = ['hyper', 'lmh', 'lmdh', 'lmp1']
            virtual_energy_keywords = ['gt3', 'gte', 'gtd', 'gtlm']
            
            is_hybrid_class = any(k in veh_class_str for k in hybrid_keywords)
            is_virtual_class = any(k in veh_class_str for k in virtual_energy_keywords)
            
            energy_percent = 0.0
            show_energy = False
            
            # 1. Check if in PIT first
            if api.read.vehicle.in_pits(veh_idx):
                self.bars_energy[row_idx].setText("PIT")
                # Yellow background for PIT
                self.bars_energy[row_idx].setStyleSheet("color: black; background: #FFC107; border: none;")
                return

            # 2. Virtual Energy REST API (HIGHEST PRIORITY - Most reliable for ALL categories)
            # This is the official game data, most accurate and safe
            # Works for GT3/GTE/GTD/GTLM and also Hyper/LMH if they have Virtual Energy
            # Only available for player, but is the best source when available
            if not show_energy and max_virtual_energy > 0:
                # Ensure we don't show > 100% or < 0%
                raw_percent = (virtual_energy / max_virtual_energy) * 100.0
                energy_percent = max(0.0, min(100.0, raw_percent))
                show_energy = True

            # 3. LMU Strategy Data with real-time interpolation (PRIORITY for Virtual Energy classes)
            # This correctly calculates Virtual Energy for GT3/GTE/GTD/GTLM opponents
            # Works for Le Mans Ultimate opponents AFTER they have lap history
            # This works for Le Mans Ultimate opponents AFTER they have lap history
            if not show_energy:
                try:
                    # Get base energy data from strategy
                    ve_remaining, ve_used, total_laps_done, _, _ = api.read.vehicle.stint_usage(api.read.vehicle.driver_name(veh_idx))
                    
                    # Calculate real-time interpolated energy
                    if ve_remaining > -0.9 and ve_remaining <= 1.0:
                        # Get current lap progress for real-time interpolation
                        current_lap_progress = api.read.lap.completed_laps(veh_idx) + api.read.lap.progress(veh_idx)
                        
                        # If we have usage data, apply real-time interpolation
                        if ve_used > 0 and current_lap_progress > total_laps_done:
                            # Interpolate: subtract energy used since last lap completion
                            lmu_energy = ve_remaining - ve_used * 0.95 * (current_lap_progress - total_laps_done)
                        else:
                            # No usage data yet, use base value
                            lmu_energy = ve_remaining
                        
                        # Ensure valid range
                        if lmu_energy >= 0 and lmu_energy <= 1.0:
                            energy_percent = lmu_energy * 100.0
                            show_energy = True
                except:
                    pass

            # 4. Battery Telemetry (Priority for HYBRID classes only - Real-time 10ms)
            # For LMH/Hyper/LMP1 with real hybrid battery systems
            # Only use for hybrid classes to avoid showing battery data for Virtual Energy cars
            if not show_energy and is_hybrid_class and charge_fraction is not None:
                try:
                    val = float(charge_fraction)
                    # Only accept valid charge values
                    if str(val).lower() not in ('nan', 'inf', '-inf'):
                        energy_percent = val * 100.0
                        show_energy = True
                except:
                    pass

            # 5. Battery Telemetry Fallback (for any car with charge data)
            # Universal fallback when other methods unavailable
            if not show_energy and charge_fraction is not None:
                try:
                    val = float(charge_fraction)
                    # Only accept valid charge values
                    if str(val).lower() not in ('nan', 'inf', '-inf'):
                        # Show if boost motor active OR battery has any charge
                        if boost_state > 0 or val > 0:
                            energy_percent = val * 100.0
                            show_energy = True
                except:
                    pass

            # 6. Fuel Proxy for GT3/GTE (Last resort)
            # Use fuel % as proxy for "Energy" if no other energy data available
            # We ONLY do this for Virtual Energy classes (GT3/GTE) to avoid showing fuel for LMP2
            if not show_energy and is_virtual_class:
                try:
                    fuel = api.read.vehicle.fuel(veh_idx)
                    capacity = api.read.vehicle.tank_capacity(veh_idx)
                    if capacity > 0:
                        energy_percent = (fuel / capacity) * 100.0
                        show_energy = True
                except:
                    pass

            if not show_energy:
                # No hybrid/virtual energy detected
                self.has_hybrid_system[row_idx] = False
                self.bars_energy[row_idx].setText("--")
                self.bars_energy[row_idx].setStyleSheet("color: #888888; background: transparent; border: none;")
                return
            
            # Hybrid/Virtual system detected! Update tracking
            self.has_hybrid_system[row_idx] = True
            
            # Clamp to valid range
            energy_percent = max(0.0, min(100.0, energy_percent))
            
            # Format display with 1 decimal place for smoother visual updates
            energy_text = f"{energy_percent:.1f}%"
            
            # Always update text (don't check if same) to ensure real-time display
            self.bars_energy[row_idx].setText(energy_text)
            
            # DYNAMIC BACKGROUNDS based on energy percentage
            # 100-50%: Green background
            # 49-15%: Orange background  
            # <15%: Red background
            # Text always white
            
            if energy_percent >= 50.0:
                bg_color = "#00AA00"  # Green
            elif energy_percent >= 15.0:
                bg_color = "#FFA500"  # Orange
            else:
                bg_color = "#FF0000"  # Red
            
            text_color = "#FFFFFF"  # Always white
            
            style = (
                f"color: {text_color}; "
                f"background: {bg_color}; "
                f"border: none;"
            )
            
            self.bars_energy[row_idx].setStyleSheet(style)
            
        except (AttributeError, TypeError, ZeroDivisionError, ValueError):
            # Error handling - show '--' if anything goes wrong
            self.has_hybrid_system[row_idx] = False
            self.bars_energy[row_idx].setText("--")
            self.bars_energy[row_idx].setStyleSheet("color: #888888; background: transparent; border: none;")

    def update_damage(self, row_idx, veh_idx, is_player):
        """Update vehicle damage percentage"""
        try:
            # Get vehicle integrity (0.0 = destroyed, 1.0 = perfect)
            integrity = api.read.vehicle.integrity(veh_idx)
            
            if integrity is not None and 0.0 <= integrity <= 1.0:
                # Convert to damage percentage (100% = destroyed, 0% = perfect)
                damage_percent = (1.0 - integrity) * 100.0
                
                # SEMPRE mostra o dano, mesmo se 0%
                self.bars_dmg[row_idx].setText(f"{damage_percent:.0f}%")
                
                # Color based on damage severity
                if damage_percent < 0.5:
                    # No damage - Normal style
                    style = self.bar_style_dmg[is_player]
                elif damage_percent < 25:
                    # Low damage - Yellow
                    style = self.bar_style_dmg[is_player]
                elif damage_percent < 60:
                    # Medium damage - Orange
                    style = f"color: #FFFFFF; background-color: #FF8800;"
                else:
                    # High damage - Red
                    style = f"color: #FFFFFF; background-color: #FF0000;"
                
                self.bars_dmg[row_idx].setStyleSheet(style)
                self.bars_dmg[row_idx].show()
            else:
                self.bars_dmg[row_idx].setText("0%")
                self.bars_dmg[row_idx].setStyleSheet(self.bar_style_dmg[is_player])
                self.bars_dmg[row_idx].show()
        except (AttributeError, TypeError, ValueError):
            self.bars_dmg[row_idx].setText("0%")
            self.bars_dmg[row_idx].setStyleSheet(self.bar_style_dmg[is_player])
            self.bars_dmg[row_idx].show()

    def update_penalty(self, row_idx, veh_idx, is_player):
        """
        Update penalty column - shows active penalties, DNF, DQ
        Shows: S&G (Stop & Go), PENA (generic penalty), DNF, DQ
        Note: Stop & Go detection only available for player via REST API
        """
        try:
            # Get finish status
            # 0 = running, 1 = finished, 2 = DNF, 3 = DQ
            finish_status = api.read.vehicle.finish_state(veh_idx)
            
            # Get number of active penalties
            num_penalties = api.read.vehicle.number_penalties(veh_idx)
            
            penalty_text = ""
            has_penalty = False
            
            # Check for DNF/DQ first (highest priority)
            if finish_status == 2:
                penalty_text = "DNF"
                has_penalty = True
            elif finish_status == 3:
                penalty_text = "DQ"
                has_penalty = True
            # Check for active penalties
            elif num_penalties > 0:
                # For player: try to get Stop & Go state from pit estimate
                if is_player:
                    try:
                        pit_estimate = api.read.vehicle.pit_estimate(veh_idx)
                        state_stopgo = pit_estimate[4]  # Index 4 = state_stopgo
                        
                        if state_stopgo == 1:
                            # Stop & Go only
                            penalty_text = f"S&G×{num_penalties}" if num_penalties > 1 else "S&G"
                        elif state_stopgo == 2:
                            # Service + Stop & Go
                            penalty_text = f"S&G+×{num_penalties}" if num_penalties > 1 else "S&G+"
                        else:
                            # Generic penalty (could be DT or other)
                            penalty_text = f"PENA×{num_penalties}" if num_penalties > 1 else "PENA"
                    except:
                        # Fallback to generic penalty
                        penalty_text = f"PENA×{num_penalties}" if num_penalties > 1 else "PENA"
                else:
                    # For AI/other players: can't determine specific type
                    penalty_text = f"PENA×{num_penalties}" if num_penalties > 1 else "PENA"
                
                has_penalty = True
            
            if has_penalty:
                self.bars_penalty[row_idx].setText(penalty_text)
                # Red background for penalties
                self.bars_penalty[row_idx].setStyleSheet(
                    "color: #FFFFFF; background: #FF0000; border: none;"
                )
                self.bars_penalty[row_idx].show()
            else:
                # Hide penalty column if no penalty
                self.bars_penalty[row_idx].hide()
                
        except (AttributeError, TypeError, ValueError):
            # On error, hide the penalty column
            self.bars_penalty[row_idx].hide()

    def calculate_time_gap(self, idx, leader_idx):
        """Calculate time gap from leader"""
        try:
            # Get lap progress for both vehicles
            veh_progress = api.read.lap.completed_laps(idx) + api.read.lap.progress(idx)
            leader_progress = api.read.lap.completed_laps(leader_idx) + api.read.lap.progress(leader_idx)
            
            # If behind by full lap(s), show lap difference
            lap_diff = leader_progress - veh_progress
            if lap_diff >= 1.0:
                return None  # Could show "+1 LAP" etc
            
            # Calculate time gap based on best laptime
            leader_best = api.read.timing.best_laptime(leader_idx)
            if leader_best > 0:
                time_gap = (leader_progress - veh_progress) * leader_best
                return max(0.0, time_gap)
            
            return None
        except (AttributeError, TypeError, ValueError):
            return None

    def calculate_time_gap_relative(self, idx_from, idx_to):
        """Calculate relative time gap between two vehicles (can be + or -)"""
        try:
            # Get lap progress for both vehicles
            from_laps = api.read.lap.completed_laps(idx_from)
            from_progress = api.read.lap.progress(idx_from)
            from_total = from_laps + from_progress
            
            to_laps = api.read.lap.completed_laps(idx_to)
            to_progress = api.read.lap.progress(idx_to)
            to_total = to_laps + to_progress
            
            # Calculate progress difference (positive = idx_from is ahead)
            progress_diff = from_total - to_total
            
            # Get lap time to convert progress to time (try multiple sources)
            # 1. Try best lap of reference vehicle (idx_to)
            lap_time = api.read.timing.best_laptime(idx_to)
            
            # 2. If no best lap, try last lap of reference vehicle
            if lap_time <= 0:
                lap_time = api.read.timing.last_laptime(idx_to)
            
            # 3. If still no lap, try best lap of other vehicle
            if lap_time <= 0:
                lap_time = api.read.timing.best_laptime(idx_from)
            
            # 4. If still no lap, try last lap of other vehicle
            if lap_time <= 0:
                lap_time = api.read.timing.last_laptime(idx_from)
            
            # 5. Try estimated lap time
            if lap_time <= 0:
                try:
                    lap_time = api.read.timing.estimated_laptime(idx_to)
                    if lap_time <= 0:
                        lap_time = api.read.timing.estimated_laptime(idx_from)
                except:
                    pass
            
            # 6. FALLBACK: Use distance-based estimation when no lap time available
            # This allows gap to show from grid/formation lap before completing first lap
            if lap_time <= 0:
                # Get track length
                track_length = api.read.lap.track_length()
                if track_length > 0:
                    # Get lap distance (position on track)
                    from_dist = api.read.lap.distance(idx_from)
                    to_dist = api.read.lap.distance(idx_to)
                    
                    # Calculate distance difference
                    dist_diff = from_dist - to_dist
                    
                    # Convert to fraction of lap
                    lap_fraction = dist_diff / track_length
                    
                    # Estimate using typical lap time (120 seconds as fallback)
                    # This is just for initial display, will be replaced by real time after first lap
                    estimated_time = 120.0  # 2 minutes typical
                    time_gap = lap_fraction * estimated_time
                    return time_gap
            else:
                # Use actual lap time
                time_gap = progress_diff * lap_time
                return time_gap  # Can be positive or negative
            
            return None
        except (AttributeError, TypeError, ValueError):
            return None

    def find_leader_index(self):
        """Find the leader's index"""
        for idx in range(minfo.vehicles.totalVehicles):
            if api.read.vehicle.place(idx) == 1:
                return idx
        return -1

    def find_position_index(self, target_place):
        """Find index of vehicle in specific place"""
        for idx in range(minfo.vehicles.totalVehicles):
            if api.read.vehicle.place(idx) == target_place:
                return idx
        return -1

    def find_class_leader_index(self, target_class):
        """Find the leader (P1) of a specific class"""
        min_place = 9999
        leader_idx = -1
        for idx in range(minfo.vehicles.totalVehicles):
            if api.read.vehicle.class_name(idx) == target_class:
                place = api.read.vehicle.place(idx)
                if place < min_place:
                    min_place = place
                    leader_idx = idx
        return leader_idx

    def calculate_time_gap_by_distance(self, idx_from, idx_to):
        """Calculate time gap using track distance - works immediately without needing lap completion
        
        Este método usa a distância percorrida na pista ao invés de voltas completadas,
        permitindo que o gap seja calculado desde a largada, sem precisar passar pela
        linha de chegada primeiro.
        """
        try:
            # Obter comprimento da pista
            track_length = api.read.lap.track_length()
            if track_length <= 0:
                return None
            
            # Obter voltas completadas e distância atual para ambos
            from_laps = api.read.lap.completed_laps(idx_from)
            from_distance = api.read.lap.distance(idx_from)
            from_total_distance = (from_laps * track_length) + from_distance
            
            to_laps = api.read.lap.completed_laps(idx_to)
            to_distance = api.read.lap.distance(idx_to)
            to_total_distance = (to_laps * track_length) + to_distance
            
            # Diferença de distância total
            distance_diff = from_total_distance - to_total_distance
            
            # Converter para fração de volta
            lap_fraction_diff = distance_diff / track_length
            
            # Obter tempo de volta para conversão em segundos
            # Tentar várias fontes de tempo de volta
            lap_time = api.read.timing.best_laptime(idx_to)
            if lap_time <= 0:
                lap_time = api.read.timing.last_laptime(idx_to)
            if lap_time <= 0:
                lap_time = api.read.timing.best_laptime(idx_from)
            if lap_time <= 0:
                lap_time = api.read.timing.last_laptime(idx_from)
            
            # Tentar estimated laptime
            if lap_time <= 0:
                try:
                    lap_time = api.read.timing.estimated_laptime(idx_to)
                    if lap_time <= 0:
                        lap_time = api.read.timing.estimated_laptime(idx_from)
                except:
                    pass
            
            # Se ainda não tiver tempo de volta, usar estimativa baseada em velocidade
            if lap_time <= 0:
                # Tentar calcular usando velocidade média
                try:
                    speed_from = api.read.vehicle.speed(idx_from)
                    speed_to = api.read.vehicle.speed(idx_to)
                    avg_speed = max(speed_from, speed_to, 50)  # mínimo 50 m/s para evitar divisão pequena
                    
                    # Gap em segundos = distância / velocidade
                    time_gap = distance_diff / avg_speed
                    return time_gap
                except:
                    # Último fallback: estimativa de 2 minutos por volta
                    estimated_lap_time = 120.0
                    time_gap = lap_fraction_diff * estimated_lap_time
                    return time_gap
            
            # Converter fração de volta em tempo
            time_gap = lap_fraction_diff * lap_time
            return time_gap
            
        except (AttributeError, TypeError, ValueError, ZeroDivisionError):
            return None

    def update_brand_logo(self, target, veh_name, veh_class, team_name, is_player):
        """Update brand logo with smart mapping for LMU/rF2"""
        
        # Smart Mapping Logic
        mapped_brand = None
        v_name_lower = veh_name.lower()
        v_class_lower = veh_class.lower()
        t_name_lower = team_name.lower() if team_name else ""
        
        # Combine name and team for searching to catch cases where info is in team name
        search_text = f"{v_name_lower} {t_name_lower}"

        # 1. LMP2 Mappings
        if "lmp2" in v_class_lower:
            # Check for Oreca 07 model
            if any(x in search_text for x in ["oreca", "07"]):
                mapped_brand = "Oreca"
            else:
                mapped_brand = "Oreca"  # Default for LMP2

        # 1.1 LMP3 Mappings
        elif "lmp3" in v_class_lower or "p3" in v_class_lower:
            # Check Ginetta models
            if any(x in search_text for x in ["ginetta", "g61", "lt-p325", "evo"]):
                mapped_brand = "Ginetta"
            # Check Ligier models
            elif any(x in search_text for x in ["ligier", "js p320", "js p3"]):
                mapped_brand = "Ligier"
            
            # Fallback if name doesn't contain manufacturer
            if not mapped_brand:
                if "js p3" in search_text or "p320" in search_text:
                    mapped_brand = "Ligier"
                elif "g61" in search_text:
                    mapped_brand = "Ginetta"
        
        # 2. GT3 / LMGT3 Mappings
        elif "gt3" in v_class_lower or "lmgt3" in v_class_lower:
            # Check explicit manufacturer names first (ORDEM IMPORTANTE - Ford antes de Porsche)
            if "ford" in search_text or "mustang" in search_text: mapped_brand = "Ford"
            elif "ferrari" in search_text: mapped_brand = "Ferrari"
            elif "porsche" in search_text: mapped_brand = "Porsche"
            elif "lamborghini" in search_text: mapped_brand = "Lamborghini"
            elif "bmw" in search_text: mapped_brand = "BMW"
            elif "aston" in search_text or "aston martin" in search_text: mapped_brand = "Aston Martin"
            elif "corvette" in search_text: mapped_brand = "Corvette"
            elif "lexus" in search_text: mapped_brand = "Lexus"
            elif "mclaren" in search_text: mapped_brand = "mclaren"
            elif "mercedes" in search_text or "amg" in search_text: mapped_brand = "mercedes"
            elif "audi" in search_text: mapped_brand = "Audi"
            elif "honda" in search_text or "nsx" in search_text: mapped_brand = "Honda"
            elif "acura" in search_text: mapped_brand = "Acura"
            elif "nissan" in search_text: mapped_brand = "Nissan"
            elif "bentley" in search_text: mapped_brand = "Bentley"
            
            # Check Model Names - LMGT3 Specific Models
            if not mapped_brand:
                # Ford models - CHECK FIRST
                if "mustang" in search_text: 
                    mapped_brand = "Ford"
                # Ferrari models
                elif "296" in search_text or "488" in search_text: 
                    mapped_brand = "Ferrari"
                # Porsche models
                elif "911" in search_text or "gt3 r" in search_text or "992" in search_text: 
                    mapped_brand = "Porsche"
                # Lamborghini models
                elif "huracan" in search_text or "huracán" in search_text or "evo 2" in search_text: 
                    mapped_brand = "Lamborghini"
                # BMW models
                elif "m4" in search_text or "m6" in search_text: 
                    mapped_brand = "BMW"
                # Aston Martin models
                elif "vantage" in search_text or "amr" in search_text: 
                    mapped_brand = "Aston Martin"
                # Corvette models
                elif "z06" in search_text or "c8" in search_text or "c7" in search_text: 
                    mapped_brand = "Corvette"
                # Lexus models
                elif "rc f" in search_text or "rcf" in search_text: 
                    mapped_brand = "Lexus"
                # McLaren models
                elif "720s" in search_text or "650s" in search_text or "artura" in search_text: 
                    mapped_brand = "mclaren"
                # Mercedes models
                elif "gt3" in search_text and ("amg" in search_text or "mercedes" in search_text):
                    mapped_brand = "mercedes"
                # Audi models
                elif "r8" in search_text: 
                    mapped_brand = "Audi"
                # Nissan models
                elif "gtr" in search_text or "gt-r" in search_text: 
                    mapped_brand = "Nissan"
            
            # Team Name Mappings (if manufacturer not found)
            if not mapped_brand:
                # Specific Year/Team Logic
                if "iron lynx" in search_text:
                    if "2025" in search_text or "mercedes" in search_text or "amg" in search_text:
                        mapped_brand = "mercedes"
                    else:
                        mapped_brand = "Lamborghini"
                elif "iron dames" in search_text:
                    if "2025" in search_text or "porsche" in search_text:
                        mapped_brand = "Porsche"
                    else:
                        mapped_brand = "Lamborghini"
                elif "proton" in search_text:
                    # Proton Competition no LMGT3 usa Ford Mustang!
                    # Na classe GT3/LMGT3, Proton = Ford
                    mapped_brand = "Ford"
                elif "gr racing" in search_text:
                    if "2025" in search_text or "ferrari" in search_text or "296" in search_text:
                        mapped_brand = "Ferrari"
                    elif "2024" in search_text: # User listed GR Racing 2024 under Ferrari too
                        mapped_brand = "Ferrari"
                    else:
                        mapped_brand = "Porsche" # Old GTE default
                
                # General Team Mappings - Ford teams first
                elif any(x in search_text for x in ["multimatic", "proton ford", "proton mustang"]):
                    mapped_brand = "Ford"
                elif any(x in search_text for x in ["vista", "af corse", "spirit of race", "kessel", "jmw", "richard mille", "ziggo"]):
                    mapped_brand = "Ferrari"
                elif any(x in search_text for x in ["wrt", "the bend", "walkenhorst", "rowe"]):
                    mapped_brand = "BMW"
                elif any(x in search_text for x in ["tf sport", "awa"]):
                    mapped_brand = "Corvette"
                elif any(x in search_text for x in ["heart of racing", "d'station", "racing spirit", "beechdean"]):
                    mapped_brand = "Aston Martin"
                elif any(x in search_text for x in ["united autosports", "inception", "optimum"]):
                    mapped_brand = "mclaren"
                elif any(x in search_text for x in ["grt", "fff"]):
                    mapped_brand = "Lamborghini"
                elif any(x in search_text for x in ["manthey", "pure rxcing", "pfaff", "dinamic", "1st phorm"]):
                    mapped_brand = "Porsche"
                elif any(x in search_text for x in ["akkodis", "asp", "vasser sullivan"]):
                    mapped_brand = "Lexus"
                elif any(x in search_text for x in ["winward", "gruppe m", "craft-bamboo"]):
                    mapped_brand = "mercedes"

        # 3. GTE (2023 Season)
        elif "gte" in v_class_lower:
            if "ferrari" in search_text: 
                mapped_brand = "Ferrari"
            elif "porsche" in search_text: 
                mapped_brand = "Porsche"
            elif "aston" in search_text: 
                mapped_brand = "Aston Martin"
            elif "corvette" in search_text: 
                mapped_brand = "Corvette"
            
            # Model checks
            if not mapped_brand:
                if "488" in search_text: 
                    mapped_brand = "Ferrari"
                elif "rsr" in search_text: 
                    mapped_brand = "Porsche"
                elif "vantage" in search_text: 
                    mapped_brand = "Aston Martin"
                elif "c8.r" in search_text or "c7.r" in search_text: 
                    mapped_brand = "Corvette"
            
            if not mapped_brand:
                if any(x in search_text for x in ["af corse", "kessel", "richard mille", "iron lynx"]):
                    mapped_brand = "Ferrari"
                elif any(x in search_text for x in ["proton", "project 1", "iron dames", "gr racing", "gulf"]):
                    mapped_brand = "Porsche"
                elif any(x in search_text for x in ["ort by tf", "d'station", "northwest"]):
                    mapped_brand = "Aston Martin"

        # 4. Hypercar Mappings (LMH/LMDh)
        elif any(x in v_class_lower for x in ["hyper", "lmh", "lmdh"]):
            # Check manufacturer names
            if "alpine" in search_text: 
                mapped_brand = "Alpine"
            elif "isotta" in search_text: 
                mapped_brand = "Isotta"
            elif "aston martin" in search_text or "valkyrie" in search_text: 
                mapped_brand = "Aston Martin"
            elif "bmw" in search_text: 
                mapped_brand = "BMW"
            elif "lamborghini" in search_text: 
                mapped_brand = "Lamborghini"
            elif "vanwall" in search_text or "vandervell" in search_text: 
                mapped_brand = "Vanwall"
            elif "glickenhaus" in search_text or "scg" in search_text: 
                mapped_brand = "Glickenhaus"
            elif "peugeot" in search_text: 
                mapped_brand = "Peugeot"
            elif "cadillac" in search_text: 
                mapped_brand = "Cadillac"
            elif "toyota" in search_text: 
                mapped_brand = "toyota"
            elif "ferrari" in search_text: 
                mapped_brand = "Ferrari"
            elif "porsche" in search_text: 
                mapped_brand = "Porsche"
            
            # Check specific model names
            if not mapped_brand:
                # Alpine A424
                if "a424" in search_text:
                    mapped_brand = "Alpine"
                # Aston Martin Valkyrie AMR-LMH
                elif "valkyrie" in search_text or "amr-lmh" in search_text:
                    mapped_brand = "Aston Martin"
                # BMW M Hybrid V8
                elif "m hybrid" in search_text or "m hybrid v8" in search_text:
                    mapped_brand = "BMW"
                # Cadillac V-Series.R
                elif "v-series" in search_text or "v series" in search_text:
                    mapped_brand = "Cadillac"
                # Ferrari 499P
                elif "499p" in search_text or "499" in search_text:
                    mapped_brand = "Ferrari"
                # Glickenhaus SCG 007 LMH
                elif "007" in search_text or "scg 007" in search_text:
                    mapped_brand = "Glickenhaus"
                # Isotta Tipo 6-C
                elif "tipo" in search_text or "6-c" in search_text or "6c" in search_text:
                    mapped_brand = "Isotta"
                # Lamborghini SC63
                elif "sc63" in search_text or "sc 63" in search_text:
                    mapped_brand = "Lamborghini"
                # Peugeot 9X8
                elif "9x8" in search_text:
                    mapped_brand = "Peugeot"
                # Porsche 963
                elif "963" in search_text:
                    mapped_brand = "Porsche"
                # Toyota GR010 Hybrid
                elif "gr010" in search_text or "gr 010" in search_text:
                    mapped_brand = "toyota"
                # Vanwall Vandervell 680
                elif "680" in search_text or "vandervell 680" in search_text:
                    mapped_brand = "Vanwall"
            
            # Team mappings as fallback (Hypercar)
            if not mapped_brand:
                if any(x in search_text for x in ["jota", "penske"]):
                    mapped_brand = "Porsche"
                elif any(x in search_text for x in ["af corse"]):
                    mapped_brand = "Ferrari"
                elif any(x in search_text for x in ["wrt"]):
                    mapped_brand = "BMW"
                elif any(x in search_text for x in ["action express", "whelen"]):
                    mapped_brand = "Cadillac"
                # Proton no Hypercar ainda usa Porsche 963
                elif "proton" in search_text:
                    mapped_brand = "Porsche"

        # Search for logo
        logo_name = None
        logo_ext = ".png"
        
        # Clean vehicle name: keep only letters, numbers and spaces for better matching
        # This helps when names have special chars like #, -, _, etc.
        v_name_clean = re.sub(r'[^a-zA-Z0-9\s]', '', veh_name).strip()
        v_name_clean_lower = v_name_clean.lower()

        # Try to find the mapped brand first
        if mapped_brand:
            # Check exact match
            if mapped_brand.lower() in self.available_logos:
                logo_name, logo_ext = self.available_logos[mapped_brand.lower()]
            else:
                # Check substring match for mapped brand
                for key in sorted(self.available_logos.keys(), key=len, reverse=True):
                    if key in mapped_brand.lower():
                        logo_name, logo_ext = self.available_logos[key]
                        break
        
        # If no mapping or mapping failed to find file, try original vehicle name
        if not logo_name:
            # Try exact match with original name
            if veh_name.lower() in self.available_logos:
                logo_name, logo_ext = self.available_logos[veh_name.lower()]
            # Try exact match with clean name
            elif v_name_clean_lower in self.available_logos:
                logo_name, logo_ext = self.available_logos[v_name_clean_lower]
            else:
                # Substring matching
                for key in sorted(self.available_logos.keys(), key=len, reverse=True):
                    # Check against original name
                    if key in veh_name.lower():
                        logo_name, logo_ext = self.available_logos[key]
                        break
                    # Check against clean name
                    if key in v_name_clean_lower:
                        logo_name, logo_ext = self.available_logos[key]
                        break
            
        if logo_name:
            # Check cache first
            cache_key = f"{logo_name}{logo_ext}"
            if cache_key in self.pixmap_brandlogo:
                 brand_logo = self.pixmap_brandlogo[cache_key]
            else:
                brand_logo = load_brand_logo_file(
                    self.logo_search_path, 
                    logo_name, 
                    self.brd_width, 
                    self.brd_height,
                    extension=logo_ext
                )
                self.pixmap_brandlogo[cache_key] = brand_logo
            
            if not brand_logo.isNull():
                target.setPixmap(brand_logo)
                target.setText("")
            else:
                target.setPixmap(QPixmap())
                target.setText("?")
        else:
            target.setPixmap(QPixmap())
            target.setText("?")
                
        target.setStyleSheet(self.bar_style_brd[is_player])
