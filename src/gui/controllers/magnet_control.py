"""
================
Title: Magnet Control GUI
Author: Siyuan Qiu
Create Date: 2024/12/23
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

class MagnetControl(QFrame):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 500, 800, 600)
        self.initUI()
        self.show()

    def initUI(self):
        # create resource manager to connect to the instrument and store resources in a list
        rm = visa.ResourceManager()
        resources = rm.list_resources()

        # create main grid to organize layout
        main_grid = QVBoxLayout()
        main_grid.setSpacing(10)
        self.setLayout(main_grid)
        self.setWindowTitle("Magnet Control")

        connect_hb = QHBoxLayout()

        connect_vb = QVBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_ind = QLedIndicator("orange")
        connect_vb.addWidget(self.connect_btn)
        connect_vb.addWidget(self.connect_ind)
        connect_hb.addLayout(connect_vb)

        visa_vb = QVBoxLayout()
        visa_lb = QLabel("VISA")
        self.visa_cb = QComboBox()
        self.visa_cb.addItems(resources)
        visa_vb.addWidget(visa_lb)
        visa_vb.addWidget(self.visa_cb)
        connect_hb.addLayout(visa_vb)

        model_vb = QVBoxLayout()
        model_lb = QLabel("Model")
        self.model_cb = QComboBox()
        self.model_cb.addItems(["Cryo. Mag. CS-4", "Cryo. Mag. 4G"])
        model_vb.addWidget(model_lb)
        model_vb.addWidget(self.model_cb)
        connect_hb.addLayout(model_vb)

        interval_vb = QVBoxLayout()
        interval_lb = QLabel("Update Interval (s)")
        self.interval_sb = QSpinBox()
        self.interval_sb.setMaximum(1000)
        self.interval_sb.setValue(500)
        interval_vb.addWidget(interval_lb)
        interval_vb.addWidget(self.interval_sb)
        connect_hb.addLayout(interval_vb)
        main_grid.addLayout(connect_hb)

        main_display_grid = QGridLayout()

        status_vb = QVBoxLayout()
        status_lb = QLabel("Sweep Status")
        self.status_display_lb = QLabel("sweep paused")
        self.status_display_lb.setStyleSheet("border: 1px solid black;")
        self.status_display_lb.setFixedWidth(200)
        status_vb.addWidget(status_lb)
        status_vb.addWidget(self.status_display_lb)
        main_display_grid.addLayout(status_vb, 0, 0, 1, 1, Qt.AlignCenter)

        heater_vb = QVBoxLayout()
        heater_lb = QLabel("P.S. Heater")
        self.heater_display_lb = QLabel("OFF")
        self.heater_display_lb.setStyleSheet("border: 1px solid black;")
        self.heater_display_lb.setFixedWidth(200)
        heater_vb.addWidget(heater_lb)
        heater_vb.addWidget(self.heater_display_lb)
        main_display_grid.addLayout(heater_vb, 0, 1, 1, 1, Qt.AlignCenter)

        upper_limit_vb = QVBoxLayout()
        upper_limit_lb = QLabel("Upper Sweep Limit")
        self.upper_limit_display_lb = QLabel()
        self.upper_limit_display_lb.setStyleSheet("border: 1px solid black;")
        self.upper_limit_display_lb.setFixedWidth(200)
        upper_limit_vb.addWidget(upper_limit_lb)
        upper_limit_vb.addWidget(self.upper_limit_display_lb)
        main_display_grid.addLayout(upper_limit_vb, 0, 2, 1, 1, Qt.AlignCenter)

        upper_limit_vb = QVBoxLayout()
        upper_limit_lb = QLabel("Upper Sweep Limit")
        self.upper_limit_display_lb = QLabel()
        self.upper_limit_display_lb.setStyleSheet("border: 1px solid black;")
        self.upper_limit_display_lb.setFixedWidth(200)
        upper_limit_vb.addWidget(upper_limit_lb)
        upper_limit_vb.addWidget(self.upper_limit_display_lb)
        main_display_grid.addLayout(upper_limit_vb, 0, 2, 1, 1, Qt.AlignCenter)

        output_current_vb = QVBoxLayout()
        output_current_lb = QLabel("Output Current (A)")
        self.output_current_display_lb = QLabel()
        self.output_current_display_lb.setStyleSheet("border: 1px solid black;")
        self.output_current_display_lb.setFixedWidth(200)
        output_current_vb.addWidget(output_current_lb)
        output_current_vb.addWidget(self.output_current_display_lb)
        main_display_grid.addLayout(output_current_vb, 1, 0, 1, 1, Qt.AlignCenter)

        output_voltage_vb = QVBoxLayout()
        output_voltage_lb = QLabel("Output Voltage (V)")
        self.output_voltage_display_lb = QLabel()
        self.output_voltage_display_lb.setStyleSheet("border: 1px solid black;")
        self.output_voltage_display_lb.setFixedWidth(200)
        output_voltage_vb.addWidget(output_voltage_lb)
        output_voltage_vb.addWidget(self.output_voltage_display_lb)
        main_display_grid.addLayout(output_voltage_vb, 1, 1, 1, 1, Qt.AlignCenter)

        lower_limit_vb = QVBoxLayout()
        lower_limit_lb = QLabel("Lower Sweep Limit")
        self.lower_limit_display_lb = QLabel()
        self.lower_limit_display_lb.setStyleSheet("border: 1px solid black;")
        self.lower_limit_display_lb.setFixedWidth(200)
        lower_limit_vb.addWidget(lower_limit_lb)
        lower_limit_vb.addWidget(self.lower_limit_display_lb)
        main_display_grid.addLayout(lower_limit_vb, 1, 2, 1, 1, Qt.AlignCenter)

        magnet_current_vb = QVBoxLayout()
        magnet_current_lb = QLabel("Magnet Current (A)")
        self.magnet_current_display_lb = QLabel()
        self.magnet_current_display_lb.setStyleSheet("border: 1px solid black;")
        self.magnet_current_display_lb.setFixedWidth(200)
        magnet_current_vb.addWidget(magnet_current_lb)
        magnet_current_vb.addWidget(self.magnet_current_display_lb)
        main_display_grid.addLayout(magnet_current_vb, 2, 0, 1, 1, Qt.AlignCenter)

        magnet_voltage_vb = QVBoxLayout()
        magnet_voltage_lb = QLabel("Magnet Voltage (V)")
        self.magnet_voltage_display_lb = QLabel()
        self.magnet_voltage_display_lb.setStyleSheet("border: 1px solid black;")
        self.magnet_voltage_display_lb.setFixedWidth(200)
        magnet_voltage_vb.addWidget(magnet_voltage_lb)
        magnet_voltage_vb.addWidget(self.magnet_voltage_display_lb)
        main_display_grid.addLayout(magnet_voltage_vb, 2, 1, 1, 1, Qt.AlignCenter)

        voltage_limit_vb = QVBoxLayout()
        voltage_limit_lb = QLabel("Voltage Limit")
        self.voltage_limit_display_lb = QLabel()
        self.voltage_limit_display_lb.setStyleSheet("border: 1px solid black;")
        self.voltage_limit_display_lb.setFixedWidth(200)
        voltage_limit_vb.addWidget(voltage_limit_lb)
        voltage_limit_vb.addWidget(self.voltage_limit_display_lb)
        main_display_grid.addLayout(voltage_limit_vb, 2, 2, 1, 1, Qt.AlignCenter)
        main_grid.addLayout(main_display_grid)

        control_hb = QHBoxLayout()

        control_vb = QVBoxLayout()
        self.control_btn = QPushButton("Control On")
        self.control_ind = QLedIndicator("orange")
        control_vb.addWidget(self.control_btn)
        control_vb.addWidget(self.control_ind)
        control_hb.addLayout(control_vb)

        self.mode_cb = QComboBox()
        self.mode_cb.addItems(["Persistent", "Driving"])
        control_hb.addWidget(self.mode_cb)

        self.PSHtr_cb = QComboBox()
        self.PSHtr_cb.addItems(["PSHt", "OFF"])
        control_hb.addWidget(self.PSHtr_cb)

        self.PSHtr_off_cb = QCheckBox("Turn off PSHtr after zeroing")
        control_hb.addWidget(self.PSHtr_off_cb)
        main_grid.addLayout(connect_hb)

        control_ramp_hb = QHBoxLayout()

        automatic_grid = QGridLayout()
        automatic_lb = QLabel("Automatic")
        automatic_grid.addWidget(automatic_lb, 0, 0, 1, 2, Qt.AlignCenter)
        self.setpoint_sb = QSpinBox()
        automatic_grid.addWidget(self.setpoint_sb, 1, 0, 1, 1, Qt.AlignCenter)
        self.auto_ramp_btn = QPushButton("Ramp")
        automatic_grid.addWidget(self.auto_ramp_btn, 1, 1, 1, 1, Qt.AlignCenter)
        self.auto_zero_btn = QPushButton("Zero")
        automatic_grid.addWidget(self.auto_zero_btn, 2, 0, 1, 1, Qt.AlignCenter)
        self.auto_abort_btn = QPushButton("Abort")
        automatic_grid.addWidget(self.auto_abort_btn, 2, 1, 1, 1, Qt.AlignCenter)
        control_ramp_hb.addLayout(automatic_grid)

        Separador1 = QFrame()
        Separador1.setFrameShape(QFrame.VLine)
        Separador1.setLineWidth(1)
        control_ramp_hb.addWidget(Separador1)

        manual_grid = QGridLayout()
        manual_lb = QLabel("Manual")
        manual_grid.addWidget(manual_lb, 0, 0, 1, 3, Qt.AlignCenter)
        self.manual_up_btn = QPushButton()
        manual_grid.addWidget(self.manual_up_btn, 1, 0, 1, 1, Qt.AlignCenter)
        self.manual_zero_btn = QPushButton()
        manual_grid.addWidget(self.manual_zero_btn, 1, 1, 1, 1, Qt.AlignCenter)
        self.manual_limits_btn = QPushButton()
        manual_grid.addWidget(self.manual_limits_btn, 1, 2, 1, 1, Qt.AlignCenter)
        self.manual_down_btn = QPushButton()
        manual_grid.addWidget(self.manual_down_btn, 2, 0, 1, 1, Qt.AlignCenter)
        self.manual_pause_btn = QPushButton()
        manual_grid.addWidget(self.manual_pause_btn, 2, 1, 1, 1, Qt.AlignCenter)
        self.fast_sweep_cb = QCheckBox("Fast Sweep")
        manual_grid.addWidget(self.fast_sweep_cb, 2, 2, 1, 1, Qt.AlignCenter)
        control_ramp_hb.addLayout(manual_grid)
        main_grid.addLayout(control_hb)

        progress_hb = QHBoxLayout()

        self.status_cb = QComboBox()
        self.status_cb.addItems(["Not Connected", "Idle", "Sweeping", "Persistent", "Driving", "Wait"])
        progress_hb.addWidget(self.status_cb)

        progress_lb = QLabel("Progress")
        progress_hb.addWidget(progress_lb)

        self.progress_pbar = QProgressBar()
        progress_hb.addWidget(self.progress_pbar)
        main_grid.addLayout(progress_hb)

        field_hb = QHBoxLayout()

        current_vb = QVBoxLayout()
        current_lb = QLabel("Current")
        self.current_sb = QDoubleSpinBox()
        self.current_sb.valueChanged.connect(self.multiplication)
        current_vb.addWidget(current_lb)
        current_vb.addWidget(self.current_sb)
        field_hb.addLayout(current_vb)

        multiply_lb = QLabel("X")
        multiply_lb.setFixedWidth(30)
        multiply_lb.setAlignment(Qt.AlignCenter)
        field_hb.addWidget(multiply_lb)

        ratio_vb = QVBoxLayout()
        ratio_lb = QLabel("Ratio")
        self.ratio_sb = QDoubleSpinBox()
        self.ratio_sb.setDecimals(5)
        self.ratio_sb.setValue(0.11971)
        self.ratio_sb.valueChanged.connect(self.multiplication)
        ratio_vb.addWidget(ratio_lb)
        ratio_vb.addWidget(self.ratio_sb)
        field_hb.addLayout(ratio_vb)

        equal_lb = QLabel("=")
        equal_lb.setFixedWidth(30)
        equal_lb.setAlignment(Qt.AlignCenter)
        field_hb.addWidget(equal_lb)

        field_vb = QVBoxLayout()
        field_lb = QLabel("Field")
        self.field_sb = QDoubleSpinBox()
        self.field_sb.setEnabled(False)
        field_vb.addWidget(field_lb)
        field_vb.addWidget(self.field_sb)
        field_hb.addLayout(field_vb)

        buffer_vb = QVBoxLayout()
        buffer_lb = QLabel("Stable Buffer Size")
        self.buffer_sb = QSpinBox()
        self.buffer_sb.setValue(10)
        buffer_vb.addWidget(buffer_lb)
        buffer_vb.addWidget(self.buffer_sb)
        field_hb.addLayout(buffer_vb)
        main_grid.addLayout(field_hb)

    def multiplication(self):
        self.field_sb.setValue(self.current_sb.value() * self.ratio_sb.value())


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
    window = MagnetControl()
    sys.exit(app.exec_())