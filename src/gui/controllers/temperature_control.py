"""
================
Title: Temperature Control GUI
Author: Siyuan Qiu
Create Date: 2024/12/19
Institution: Stanford University, Department of Physics
=================
"""
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import sys
import matplotlib
matplotlib.use("Qt5Agg")
matplotlib.rcParams['savefig.dpi'] = 600
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pyvisa as visa

class TemperatureControl(QFrame):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 500, 1600, 800)
        self.initUI()
        self.show()

    def initUI(self):
        # create resource manager to connect to the instrument and store resources in a list
        rm = visa.ResourceManager()
        resources = rm.list_resources()

        # create main grid to organize layout
        main_grid = QHBoxLayout()
        main_grid.setSpacing(10)
        self.setLayout(main_grid)
        self.setWindowTitle("Temperature Control")

        left_vb = QVBoxLayout()
        top_hb = QHBoxLayout()

        instr_vb = QVBoxLayout()

        connect_hb = QHBoxLayout()
        connect_vb = QVBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_ind = QLedIndicator("orange")
        connect_vb.addWidget(self.connect_btn)
        connect_vb.addWidget(self.connect_ind)
        connect_hb.addLayout(connect_vb)

        model_vb = QVBoxLayout()
        model_lb = QLabel("Model")
        self.model_cb = QComboBox()
        self.model_cb.addItems(["LS 332", "LS 340"])
        model_vb.addWidget(model_lb)
        model_vb.addWidget(self.model_cb)
        connect_hb.addLayout(model_vb)
        instr_vb.addLayout(connect_hb)

        visa_vb = QVBoxLayout()
        visa_lb = QLabel("VISA resource name")
        self.visa_cb = QComboBox()
        self.visa_cb.addItems(resources)
        visa_vb.addWidget(visa_lb)
        visa_vb.addWidget(self.visa_cb)
        instr_vb.addLayout(visa_vb)

        interval_hb = QHBoxLayout()
        interval_vb = QVBoxLayout()
        interval_lb = QLabel("Interval (ms)")
        self.interval_sb = QSpinBox()
        self.interval_sb.setMaximum(1000)
        self.interval_sb.setValue(500)
        interval_vb.addWidget(interval_lb)
        interval_vb.addWidget(self.interval_sb)
        interval_hb.addLayout(interval_vb)

        sample_temp_vb = QVBoxLayout()
        sample_temp_lb = QLabel("Sample Temp")
        self.sample_temp_cb = QComboBox()
        self.sample_temp_cb.addItems(["A", "B", "C", "D"])
        sample_temp_vb.addWidget(sample_temp_lb)
        sample_temp_vb.addWidget(self.sample_temp_cb)
        interval_hb.addLayout(sample_temp_vb)
        instr_vb.addLayout(interval_hb)
        top_hb.addLayout(instr_vb)

        right_grid = QGridLayout()
        right_grid_widget = QWidget()
        right_grid_widget.setLayout(right_grid)
        right_grid_widget.setStyleSheet("""
            QWidget#RightGridWidget {
                border: 1px solid rgb(255, 0, 0);
            }
        """)
        right_grid_widget.setObjectName("RightGridWidget")

        A_lb = QLabel("A")
        self.A_num_lb = QLabel("0 K")
        self.A_num_lb.setStyleSheet("border: 1px solid black;")
        self.A_num_lb.setFixedWidth(100)
        A_hb = QHBoxLayout()
        A_hb.addWidget(A_lb)
        A_hb.addWidget(self.A_num_lb)
        right_grid.addLayout(A_hb, 0, 0, 1, 1, Qt.AlignCenter)

        B_lb = QLabel("B")
        self.B_num_lb = QLabel("0 K")
        self.B_num_lb.setStyleSheet("border: 1px solid black;")
        self.B_num_lb.setFixedWidth(100)
        B_hb = QHBoxLayout()
        B_hb.addWidget(B_lb)
        B_hb.addWidget(self.B_num_lb)
        right_grid.addLayout(B_hb, 0, 1, 1, 1, Qt.AlignCenter)

        C_lb = QLabel("C")
        self.C_num_lb = QLabel("0 K")
        self.C_num_lb.setStyleSheet("border: 1px solid black;")
        self.C_num_lb.setFixedWidth(100)
        C_hb = QHBoxLayout()
        C_hb.addWidget(C_lb)
        C_hb.addWidget(self.C_num_lb)
        right_grid.addLayout(C_hb, 1, 0, 1, 1, Qt.AlignCenter)

        D_lb = QLabel("D")
        self.D_num_lb = QLabel("0 K")
        self.D_num_lb.setStyleSheet("border: 1px solid black;")
        self.D_num_lb.setFixedWidth(100)
        D_hb = QHBoxLayout()
        D_hb.addWidget(D_lb)
        D_hb.addWidget(self.D_num_lb)
        right_grid.addLayout(D_hb, 1, 1, 1, 1, Qt.AlignCenter)

        S_lb = QLabel("S")
        self.S_num_lb = QLabel("0 K")
        self.S_num_lb.setStyleSheet("border: 1px solid black;")
        self.S_num_lb.setFixedWidth(100)
        S_hb = QHBoxLayout()
        S_hb.addWidget(S_lb)
        S_hb.addWidget(self.S_num_lb)
        right_grid.addLayout(S_hb, 2, 0, 1, 1, Qt.AlignCenter)

        heater_lb = QLabel("Heater")
        self.heater_mode_lb = QLabel("High")
        self.heater_mode_lb.setStyleSheet("border: 1px solid black;")
        self.heater_mode_lb.setFixedWidth(100)
        heater_mode_hb = QHBoxLayout()
        heater_mode_hb.addWidget(heater_lb)
        heater_mode_hb.addWidget(self.heater_mode_lb)
        right_grid.addLayout(heater_mode_hb, 2, 1, 1, 1, Qt.AlignCenter)

        self.heater_level_pbar = QProgressBar()
        self.heater_level_pbar.setStyleSheet("QProgressBar::chunk "
                          "{"
                          "background-color: red;"
                          "}")
        self.heater_level_pbar.setOrientation(Qt.Vertical)
        self.heater_level_pbar.setValue(0)
        self.heater_level_pbar.setMinimumWidth(60)
        self.heater_level_pbar.setMinimumHeight(250)
        right_grid.addWidget(self.heater_level_pbar, 1, 2, 1, 3, Qt.AlignCenter)
        top_hb.addWidget(right_grid_widget)
        left_vb.addLayout(top_hb)

        ramp_hb = QHBoxLayout()

        loop_vb = QVBoxLayout()
        loop_lb = QLabel("Loop")
        self.loop_sb = QSpinBox()
        self.loop_sb.setValue(1)
        loop_vb.addWidget(loop_lb)
        loop_vb.addWidget(self.loop_sb)
        ramp_hb.addLayout(loop_vb)

        setpoint_vb = QVBoxLayout()
        setpoint_lb = QLabel("Setpoint (K)")
        self.setpoint_sb = QDoubleSpinBox()
        self.setpoint_sb.setValue(4)
        setpoint_vb.addWidget(setpoint_lb)
        setpoint_vb.addWidget(self.setpoint_sb)
        ramp_hb.addLayout(setpoint_vb)

        self.ramp_cb = QCheckBox("Ramp")
        ramp_hb.addWidget(self.ramp_cb)

        ramp_rate_vb = QVBoxLayout()
        ramp_rate_lb = QLabel("Ramp Rate (K/min)")
        self.ramp_rate_sb = QSpinBox()
        self.ramp_rate_sb.setValue(10)
        ramp_rate_vb.addWidget(ramp_rate_lb)
        ramp_rate_vb.addWidget(self.ramp_rate_sb)
        ramp_hb.addLayout(ramp_rate_vb)

        self.set_ramp_btn = QPushButton("Set")
        ramp_hb.addWidget(self.set_ramp_btn)
        left_vb.addLayout(ramp_hb)

        ramp_setting_grid = QGridLayout()
        ramp_setting_grid_widget = QWidget()
        ramp_setting_grid_widget.setLayout(ramp_setting_grid)
        ramp_setting_grid_widget.setStyleSheet("""
                    QWidget#RampSettingWidget {
                        border: 1px solid black;
                    }
                """)
        ramp_setting_grid_widget.setObjectName("RampSettingWidget")

        heater_range_vb = QVBoxLayout()
        heater_range_lb = QLabel("Loop 1 Heater Range")
        self.heater_range_cb = QComboBox()
        self.heater_range_cb.addItems(["Off", "Low (0.5W)", "Med (5W)", "High (50W)"])
        heater_range_vb.addWidget(heater_range_lb)
        heater_range_vb.addWidget(self.heater_range_cb)
        ramp_setting_grid.addLayout(heater_range_vb, 0, 0, 1, 1, Qt.AlignCenter)

        manual_output_vb = QVBoxLayout()
        manual_output_lb = QLabel("Manual Output (%)")
        self.manual_output_sb = QSpinBox()
        self.manual_output_sb.setValue(0)
        manual_output_vb.addWidget(manual_output_lb)
        manual_output_vb.addWidget(self.manual_output_sb)
        ramp_setting_grid.addLayout(manual_output_vb, 0, 1, 1, 1, Qt.AlignCenter)

        self.set_PID_btn = QPushButton("Set PID")
        ramp_setting_grid.addWidget(self.set_PID_btn, 0, 2, 1, 1, Qt.AlignCenter)

        gain_vb = QVBoxLayout()
        gain_lb = QLabel("Gain (P)")
        self.gain_sb = QSpinBox()
        self.gain_sb.setValue(10)
        gain_vb.addWidget(gain_lb)
        gain_vb.addWidget(self.gain_sb)
        ramp_setting_grid.addLayout(gain_vb, 1, 0, 1, 1, Qt.AlignCenter)

        reset_vb = QVBoxLayout()
        reset_lb = QLabel("Reset (I)")
        self.reset_sb = QSpinBox()
        self.reset_sb.setValue(10)
        reset_vb.addWidget(reset_lb)
        reset_vb.addWidget(self.reset_sb)
        ramp_setting_grid.addLayout(reset_vb, 1, 1, 1, 1, Qt.AlignCenter)

        rate_vb = QVBoxLayout()
        rate_lb = QLabel("Rate (D)")
        self.rate_sb = QSpinBox()
        self.rate_sb.setValue(20)
        rate_vb.addWidget(rate_lb)
        rate_vb.addWidget(self.rate_sb)
        ramp_setting_grid.addLayout(rate_vb, 1, 2, 1, 1, Qt.AlignCenter)
        left_vb.addWidget(ramp_setting_grid_widget)

        temperature_log_hb = QHBoxLayout()
        self.temperature_log_cb = QCheckBox("Temperature Log to file")
        self.temperature_log_cb.setChecked(False)
        temperature_log_period_lb = QLabel("Every (s)")
        self.temperature_log_period_sb = QSpinBox()
        self.temperature_log_period_sb.setValue(5)
        temperature_log_hb.addWidget(self.temperature_log_cb)
        temperature_log_hb.addWidget(temperature_log_period_lb)
        temperature_log_hb.addWidget(self.temperature_log_period_sb)
        left_vb.addLayout(temperature_log_hb)

        data_directory_hb = QHBoxLayout()
        self.select_folder_btn = QPushButton("Select directory")
        self.select_folder_btn.clicked.connect(self.select_directory)
        self.data_directory_lb = QLabel()
        self.data_directory_lb.setStyleSheet("border: 1px solid black;")
        self.data_directory_lb.setMinimumWidth(800)
        data_directory_hb.addWidget(self.select_folder_btn)
        data_directory_hb.addWidget(self.data_directory_lb)
        left_vb.addLayout(data_directory_hb)

        right_vb = QVBoxLayout()
        self.temperature_plot1 = pg.PlotWidget()
        self.temperature_plot1.setBackground('w')  # White background
        self.temperature_plot2 = pg.PlotWidget()
        self.temperature_plot2.setBackground('w')  # White background
        self.temperature_plot3 = pg.PlotWidget()
        self.temperature_plot3.setBackground('w')  # White background
        self.temperature_plot4 = pg.PlotWidget()
        self.temperature_plot4.setBackground('w')  # White background
        right_vb.addWidget(self.temperature_plot1)
        right_vb.addWidget(self.temperature_plot2)
        right_vb.addWidget(self.temperature_plot3)
        right_vb.addWidget(self.temperature_plot4)

        main_grid.addLayout(left_vb)
        main_grid.addLayout(right_vb)

    def select_directory(self):
        # Open a dialog to select a directory
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")

        # Update the label to show the selected directory
        if directory:
            self.data_directory_lb.setText(f"{directory}")

    # from https://github.com/nlamprian/pyqt5-led-indicator-widget/blob/master/LedIndicatorWidget.py
class QLedIndicator(QAbstractButton):
    scaledSize = 1000.0

    def __init__(self, color='green', parent=None):  # added a color option to use red or orange
        QAbstractButton.__init__(self, parent)

        self.setMinimumSize(24, 24)
        self.setCheckable(True)

        # prevent user from changing indicator color by clicking
        self.setEnabled(False)

        if color.lower() == 'red':
            self.on_color_1 = QColor(255, 0, 0)
            self.on_color_2 = QColor(192, 0, 0)
            self.off_color_1 = QColor(28, 0, 0)
            self.off_color_2 = QColor(128, 0, 0)
        elif color.lower() == 'orange':
            self.on_color_1 = QColor(255, 175, 0)
            self.on_color_2 = QColor(170, 115, 0)
            self.off_color_1 = QColor(90, 60, 0)
            self.off_color_2 = QColor(150, 100, 0)
        else:  # default to green if user does not give valid option
            self.on_color_1 = QColor(0, 255, 0)
            self.on_color_2 = QColor(0, 192, 0)
            self.off_color_1 = QColor(0, 28, 0)
            self.off_color_2 = QColor(0, 128, 0)

    def changeColor(self, color):
        '''change color by inputting a string only for red, orange, and green'''
        if color.lower() == 'red':
            self.on_color_1 = QColor(255, 0, 0)
            self.on_color_2 = QColor(192, 0, 0)
            self.off_color_1 = QColor(28, 0, 0)
            self.off_color_2 = QColor(128, 0, 0)
        elif color.lower() == 'orange':
            self.on_color_1 = QColor(255, 175, 0)
            self.on_color_2 = QColor(170, 115, 0)
            self.off_color_1 = QColor(90, 60, 0)
            self.off_color_2 = QColor(150, 100, 0)
        elif color.lower() == 'green':
            self.on_color_1 = QColor(0, 255, 0)
            self.on_color_2 = QColor(0, 192, 0)
            self.off_color_1 = QColor(0, 28, 0)
            self.off_color_2 = QColor(0, 128, 0)

        self.update()

    def resizeEvent(self, QResizeEvent):
        self.update()

    def paintEvent(self, QPaintEvent):
        realSize = min(self.width(), self.height())

        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(realSize / self.scaledSize, realSize / self.scaledSize)

        gradient = QRadialGradient(QPointF(-500, -500), 1500, QPointF(-500, -500))
        gradient.setColorAt(0, QColor(224, 224, 224))
        gradient.setColorAt(1, QColor(28, 28, 28))
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(0, 0), 500, 500)

        gradient = QRadialGradient(QPointF(500, 500), 1500, QPointF(500, 500))
        gradient.setColorAt(0, QColor(224, 224, 224))
        gradient.setColorAt(1, QColor(28, 28, 28))
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(0, 0), 450, 450)

        painter.setPen(pen)
        if self.isChecked():
            gradient = QRadialGradient(QPointF(-500, -500), 1500, QPointF(-500, -500))
            gradient.setColorAt(0, self.on_color_1)
            gradient.setColorAt(1, self.on_color_2)
        else:
            gradient = QRadialGradient(QPointF(500, 500), 1500, QPointF(500, 500))
            gradient.setColorAt(0, self.off_color_1)
            gradient.setColorAt(1, self.off_color_2)

        painter.setBrush(gradient)
        painter.drawEllipse(QPointF(0, 0), 400, 400)

    @pyqtProperty(QColor)
    def onColor1(self):
        return self.on_color_1

    @onColor1.setter
    def onColor1(self, color):
        self.on_color_1 = color

    @pyqtProperty(QColor)
    def onColor2(self):
        return self.on_color_2

    @onColor2.setter
    def onColor2(self, color):
        self.on_color_2 = color

    @pyqtProperty(QColor)
    def offColor1(self):
        return self.off_color_1

    @offColor1.setter
    def offColor1(self, color):
        self.off_color_1 = color

    @pyqtProperty(QColor)
    def offColor2(self):
        return self.off_color_2

    @offColor2.setter
    def offColor2(self, color):
        self.off_color_2 = color


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Calibri")
    font.setPointSize(14)
    app.setFont(font)
    window = TemperatureControl()
    sys.exit(app.exec_())