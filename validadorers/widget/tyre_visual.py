"""
Tyre Visual Widget - Display de Pneus e Freios
Layout: 8 retângulos arredondados (4 grandes pneus + 4 pequenos freios)

Linha 1 (Frente):  100%                         100%
                [PNEU FL] [Freio FL] [Freio FR] [PNEU FR]

Linha 2 (Trás):    100%                         100%
                [PNEU RL] [Freio RL] [Freio RR] [PNEU RR]

- Pneus: cor muda com temperatura (azul frio, verde bom, laranja quente)
- Acima do pneu: porcentagem de desgaste (100% = novo)
- Fundo cinza único
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget

from ..api_control import api
from ..units import set_unit_temperature, set_unit_pressure
from ..userfile.heatmap import (
    HEATMAP_DEFAULT_TYRE,
    HEATMAP_DEFAULT_BRAKE,
    load_heatmap_style,
    select_tyre_heatmap_name,
    select_brake_heatmap_name,
    set_predefined_brake_name,
)
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget - Visual de pneus e freios com 8 retângulos"""

    def __init__(self, config, widget_name):
        super().__init__(config, widget_name)
        
        # Container principal com fundo cinza
        main_frame = QFrame(self)
        main_frame.setStyleSheet(
            "background-color: rgba(32, 32, 32, 230);"
            "border-radius: 8px;"
        )
        
        # Layout principal
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(8, 6, 8, 8)
        main_layout.setSpacing(6)
        
        # Overlay layout
        overlay_layout = self.set_grid_layout(gap=0)
        overlay_layout.addWidget(main_frame, 0, 0)
        self.set_primary_layout(layout=overlay_layout)

        # Configurações de unidades
        self.unit_temp = set_unit_temperature(self.cfg.units["temperature_unit"])
        self.unit_pressure = set_unit_pressure(self.cfg.units["pressure_unit"])

        # Dicionários para componentes
        self.tyre_frames = {}
        self.tyre_temps = {}
        self.brake_frames = {}
        self.brake_temps = {}
        self.wear_labels = {}
        
        # Heatmap styles
        self.tyre_heatmap_styles = [
            load_heatmap_style(
                heatmap_name=HEATMAP_DEFAULT_TYRE,
                default_name=HEATMAP_DEFAULT_TYRE,
                swap_style=True,
                fg_color="#FFFFFF",
                bg_color="#333333",
            ) for _ in range(4)
        ]
        self.brake_heatmap_styles = [
            load_heatmap_style(
                heatmap_name=HEATMAP_DEFAULT_BRAKE,
                default_name=HEATMAP_DEFAULT_BRAKE,
                swap_style=True,
                fg_color="#FFFFFF",
                bg_color="#333333",
            ) for _ in range(4)
        ]
        
        # Cache
        self.last_tcmpd_f = ""
        self.last_tcmpd_r = ""
        self.last_in_pits = -1

        # === LINHA FRENTE (FL=0, FR=1) ===
        front_row = QWidget()
        front_layout = QHBoxLayout(front_row)
        front_layout.setContentsMargins(0, 0, 0, 0)
        front_layout.setSpacing(4)
        
        # Coluna FL (desgaste + pneu)
        fl_col = QWidget()
        fl_layout = QVBoxLayout(fl_col)
        fl_layout.setContentsMargins(0, 0, 0, 0)
        fl_layout.setSpacing(2)
        self.wear_labels[0] = self.create_wear_label()
        self.tyre_frames[0], self.tyre_temps[0] = self.create_tyre_box()
        fl_layout.addWidget(self.wear_labels[0], alignment=Qt.AlignCenter)
        fl_layout.addWidget(self.tyre_frames[0])
        front_layout.addWidget(fl_col)
        
        # Freio FL (pequeno)
        self.brake_frames[0], self.brake_temps[0] = self.create_brake_box()
        front_layout.addWidget(self.brake_frames[0], alignment=Qt.AlignBottom)
        
        # Freio FR (pequeno)
        self.brake_frames[1], self.brake_temps[1] = self.create_brake_box()
        front_layout.addWidget(self.brake_frames[1], alignment=Qt.AlignBottom)
        
        # Coluna FR (desgaste + pneu)
        fr_col = QWidget()
        fr_layout = QVBoxLayout(fr_col)
        fr_layout.setContentsMargins(0, 0, 0, 0)
        fr_layout.setSpacing(2)
        self.wear_labels[1] = self.create_wear_label()
        self.tyre_frames[1], self.tyre_temps[1] = self.create_tyre_box()
        fr_layout.addWidget(self.wear_labels[1], alignment=Qt.AlignCenter)
        fr_layout.addWidget(self.tyre_frames[1])
        front_layout.addWidget(fr_col)
        
        main_layout.addWidget(front_row)
        
        # === LINHA TRÁS (RL=2, RR=3) ===
        rear_row = QWidget()
        rear_layout = QHBoxLayout(rear_row)
        rear_layout.setContentsMargins(0, 0, 0, 0)
        rear_layout.setSpacing(4)
        
        # Coluna RL (desgaste + pneu)
        rl_col = QWidget()
        rl_layout = QVBoxLayout(rl_col)
        rl_layout.setContentsMargins(0, 0, 0, 0)
        rl_layout.setSpacing(2)
        self.wear_labels[2] = self.create_wear_label()
        self.tyre_frames[2], self.tyre_temps[2] = self.create_tyre_box()
        rl_layout.addWidget(self.wear_labels[2], alignment=Qt.AlignCenter)
        rl_layout.addWidget(self.tyre_frames[2])
        rear_layout.addWidget(rl_col)
        
        # Freio RL (pequeno)
        self.brake_frames[2], self.brake_temps[2] = self.create_brake_box()
        rear_layout.addWidget(self.brake_frames[2], alignment=Qt.AlignBottom)
        
        # Freio RR (pequeno)
        self.brake_frames[3], self.brake_temps[3] = self.create_brake_box()
        rear_layout.addWidget(self.brake_frames[3], alignment=Qt.AlignBottom)
        
        # Coluna RR (desgaste + pneu)
        rr_col = QWidget()
        rr_layout = QVBoxLayout(rr_col)
        rr_layout.setContentsMargins(0, 0, 0, 0)
        rr_layout.setSpacing(2)
        self.wear_labels[3] = self.create_wear_label()
        self.tyre_frames[3], self.tyre_temps[3] = self.create_tyre_box()
        rr_layout.addWidget(self.wear_labels[3], alignment=Qt.AlignCenter)
        rr_layout.addWidget(self.tyre_frames[3])
        rear_layout.addWidget(rr_col)
        
        main_layout.addWidget(rear_row)

    def create_wear_label(self):
        """Cria label de desgaste (100% = novo)"""
        label = self.set_qlabel(
            text="100%",
            style="color: #AAAAAA; font-size: 10px; background: transparent;"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(50)
        return label

    def create_tyre_box(self):
        """Cria retângulo grande do pneu com temperatura"""
        frame = QFrame()
        frame.setFixedSize(50, 45)
        frame.setStyleSheet(
            "background-color: #2E7D32;"
            "border-radius: 8px;"
        )
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        temp_label = self.set_qlabel(
            text="--.-°",
            style="color: #FFFFFF; font-size: 13px; font-weight: bold; background: transparent;"
        )
        temp_label.setAlignment(Qt.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(temp_label)
        layout.addStretch()
        
        return frame, temp_label

    def create_brake_box(self):
        """Cria retângulo pequeno do freio com temperatura"""
        frame = QFrame()
        frame.setFixedSize(34, 30)
        frame.setStyleSheet(
            "background-color: #455A64;"
            "border-radius: 6px;"
        )
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        
        temp_label = self.set_qlabel(
            text="---°",
            style="color: #FFFFFF; font-size: 10px; font-weight: bold; background: transparent;"
        )
        temp_label.setAlignment(Qt.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(temp_label)
        layout.addStretch()
        
        return frame, temp_label

    def get_tyre_color(self, temp_c):
        """Retorna cor do pneu baseado na temperatura
        Azul = frio (<70°C), Verde = bom (70-95°C), Laranja = quente (>95°C)
        """
        if temp_c < 60:
            return "#1565C0"  # Azul escuro - muito frio
        elif temp_c < 70:
            return "#1E88E5"  # Azul - frio
        elif temp_c < 80:
            return "#43A047"  # Verde escuro - esquentando
        elif temp_c < 95:
            return "#2E7D32"  # Verde - ideal
        elif temp_c < 105:
            return "#F57C00"  # Laranja - quente
        else:
            return "#E64A19"  # Laranja escuro - muito quente

    def get_brake_color(self, temp_c):
        """Retorna cor do freio baseado na temperatura"""
        if temp_c < 200:
            return "#455A64"  # Cinza azulado - frio
        elif temp_c < 400:
            return "#558B2F"  # Verde - bom
        elif temp_c < 600:
            return "#F9A825"  # Amarelo - quente
        else:
            return "#E64A19"  # Laranja - muito quente

    def update_tyre_heatmaps(self, tcmpd_f, tcmpd_r):
        """Atualiza os heatmaps de pneu baseado no composto"""
        heatmap_front = select_tyre_heatmap_name(tcmpd_f)
        heatmap_rear = select_tyre_heatmap_name(tcmpd_r)
        
        for i in range(2):
            self.tyre_heatmap_styles[i] = load_heatmap_style(
                heatmap_name=heatmap_front,
                default_name=HEATMAP_DEFAULT_TYRE,
                swap_style=True,
                fg_color="#FFFFFF",
                bg_color="#333333",
            )
        
        for i in range(2, 4):
            self.tyre_heatmap_styles[i] = load_heatmap_style(
                heatmap_name=heatmap_rear,
                default_name=HEATMAP_DEFAULT_TYRE,
                swap_style=True,
                fg_color="#FFFFFF",
                bg_color="#333333",
            )

    def update_brake_heatmaps(self, class_name, vehicle_name):
        """Atualiza os heatmaps de freio"""
        brake_name_front = set_predefined_brake_name(class_name, vehicle_name, True)
        brake_name_rear = set_predefined_brake_name(class_name, vehicle_name, False)
        
        heatmap_front = select_brake_heatmap_name(brake_name_front)
        heatmap_rear = select_brake_heatmap_name(brake_name_rear)
        
        for i in range(2):
            self.brake_heatmap_styles[i] = load_heatmap_style(
                heatmap_name=heatmap_front,
                default_name=HEATMAP_DEFAULT_BRAKE,
                swap_style=True,
                fg_color="#FFFFFF",
                bg_color="#333333",
            )
        
        for i in range(2, 4):
            self.brake_heatmap_styles[i] = load_heatmap_style(
                heatmap_name=heatmap_rear,
                default_name=HEATMAP_DEFAULT_BRAKE,
                swap_style=True,
                fg_color="#FFFFFF",
                bg_color="#333333",
            )

    def timerEvent(self, event):
        """Atualização em tempo real"""
        # Detectar mudança de composto
        in_pits = api.read.vehicle.in_pits()
        
        if in_pits or in_pits != self.last_in_pits:
            self.last_in_pits = in_pits
            
            class_name = api.read.vehicle.class_name()
            player_idx = api.read.vehicle.player_index()
            vehicle_name = api.read.vehicle.vehicle_name(player_idx)
            
            tcmpd_f = f"{class_name} - {api.read.tyre.compound_name_front()}"
            tcmpd_r = f"{class_name} - {api.read.tyre.compound_name_rear()}"
            
            if tcmpd_f != self.last_tcmpd_f or tcmpd_r != self.last_tcmpd_r:
                self.update_tyre_heatmaps(tcmpd_f, tcmpd_r)
                self.update_brake_heatmaps(class_name, vehicle_name)
                self.last_tcmpd_f = tcmpd_f
                self.last_tcmpd_r = tcmpd_r
        
        # Buscar dados
        all_temps = api.read.tyre.inner_temperature_avg()
        all_wears = api.read.tyre.wear()
        all_brakes = api.read.brake.temperature()
        
        for i in range(4):
            # === PNEU ===
            temp_c = all_temps[i]
            wear_pct = all_wears[i] * 100
            
            # Atualizar temperatura
            self.tyre_temps[i].setText(f"{temp_c:.1f}°")
            
            # Atualizar desgaste
            self.wear_labels[i].setText(f"{wear_pct:.0f}%")
            
            # Atualizar cor do pneu
            tyre_color = self.get_tyre_color(temp_c)
            self.tyre_frames[i].setStyleSheet(
                f"background-color: {tyre_color};"
                "border-radius: 8px;"
            )
            
            # === FREIO ===
            brake_c = all_brakes[i]
            self.brake_temps[i].setText(f"{brake_c:.0f}°")
            
            # Atualizar cor do freio
            brake_color = self.get_brake_color(brake_c)
            self.brake_frames[i].setStyleSheet(
                f"background-color: {brake_color};"
                "border-radius: 6px;"
            )