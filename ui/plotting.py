# ui/plotting.py

# -*- coding: utf-8 -*-
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class EnhancedPlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(11, 8), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig.tight_layout(pad=3.0)

    def plot_from_result(self, params, result, plot_options: dict, theme: str = 'light'):
        """
        Vẽ biểu đồ lực căng tương tác với các thành phần lực.
        plot_options: dict chứa trạng thái của các checkbox.
        theme: 'light' hoặc 'dark' để điều chỉnh màu sắc.
        """
        # --- NÂNG CẤP: Chọn màu sắc dựa trên theme ---
        if theme == 'dark':
            bg_color = '#1e293b'
            text_color = '#e2e8f0'
            grid_color = '#475569'
            line_color = '#5eead4' # Teal
        else: # light theme
            bg_color = '#ffffff'
            text_color = '#1e293b'
            grid_color = '#d1d5db'
            line_color = '#2563eb' # Blue

        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        
        self.ax.clear()
        
        if not result or not result.distances_m or not params:
            self.ax.set_title("Chưa có dữ liệu để vẽ biểu đồ", color=text_color)
            # Cấu hình màu cho biểu đồ trống
            self.ax.spines['bottom'].set_color(text_color)
            self.ax.spines['top'].set_color(text_color) 
            self.ax.spines['right'].set_color(text_color)
            self.ax.spines['left'].set_color(text_color)
            self.ax.tick_params(axis='x', colors=text_color)
            self.ax.tick_params(axis='y', colors=text_color)
            self.draw()
            return

        x = result.distances_m
        y_base = np.zeros(len(x))
        
        colors = {
            't2': '#a3e635',       # Lime
            'friction': '#fde047', # Yellow
            'lift': '#fb923c'      # Orange
        }
        labels = {
            't2': 'Lực căng T2 (căng ban đầu)',
            'friction': 'Lực do ma sát',
            'lift': 'Lực do nâng vật liệu'
        }

        if plot_options.get('show_t2', False) and result.t2_profile:
            y_new = y_base + np.array(result.t2_profile)
            self.ax.fill_between(x, y_base, y_new, color=colors['t2'], label=labels['t2'], alpha=0.7)
            y_base = y_new

        if plot_options.get('show_friction', False) and result.friction_force_profile:
            y_new = y_base + np.array(result.friction_force_profile)
            self.ax.fill_between(x, y_base, y_new, color=colors['friction'], label=labels['friction'], alpha=0.7)
            y_base = y_new
            
        if plot_options.get('show_lift', False) and result.lift_force_profile:
            y_new = y_base + np.array(result.lift_force_profile)
            self.ax.fill_between(x, y_base, y_new, color=colors['lift'], label=labels['lift'], alpha=0.7)
            y_base = y_new

        self.ax.plot(x, result.tension_profile, linewidth=2.5, color=line_color, label=f'Lực căng tổng (T1 = {result.T1:,.0f} N)')
        
        # --- NÂNG CẤP: Cấu hình màu sắc cho biểu đồ ---
        self.ax.set_title("Phân bố Lực căng và các Thành phần dọc Băng tải", fontsize=14, weight='bold', color=text_color)
        self.ax.set_xlabel("Khoảng cách (m)", fontsize=12, color=text_color)
        self.ax.set_ylabel("Lực căng (N)", fontsize=12, color=text_color)
        self.ax.grid(True, linestyle='--', alpha=0.6, color=grid_color)
        
        legend = self.ax.legend(loc='upper left')
        legend.get_frame().set_facecolor(bg_color)
        for text in legend.get_texts():
            text.set_color(text_color)

        self.ax.tick_params(axis='both', which='major', labelsize=10, colors=text_color)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(text_color)
        
        self.fig.tight_layout(pad=3.0)
        self.draw()
