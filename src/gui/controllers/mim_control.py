"""
================
Title: MIM Control GUI
Author: Siyuan Qiu
Create Date: 2024/12/17
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

class MIMControl(QFrame):
    def __init__(self):
        super().__init__()
        self.setGeometry(400, 400, 1300, 750)
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
        self.setWindowTitle("MIM Control")

        # create top hb
        main_hb = QHBoxLayout()

        lockin_vb = QVBoxLayout()
        lockin_lb = QLabel("Lockin")
        self.lockin_cb = QComboBox()
        self.lockin_cb.addItems(resources)
        lockin_vb.addWidget(lockin_lb)
        lockin_vb.addWidget(self.lockin_cb)
        main_hb.addLayout(lockin_vb)

        agilent_vb = QVBoxLayout()
        agilent_lb = QLabel("Agilent Source")
        self.agilent_cb = QComboBox()
        self.agilent_cb.addItems(resources)
        agilent_vb.addWidget(agilent_lb)
        agilent_vb.addWidget(self.agilent_cb)
        main_hb.addLayout(agilent_vb)

        Separador1 = QFrame()
        Separador1.setFrameShape(QFrame.VLine)
        Separador1.setLineWidth(1)
        main_hb.addWidget(Separador1)

        power_offset_vb = QVBoxLayout()
        power_offset_lb = QLabel("Excitation Power Offset (dBm) \nWhen Atten=0dB")
        self.power_offset_sb = QDoubleSpinBox()
        self.power_offset_sb.setMinimum(-50)
        self.power_offset_sb.setMaximum(0)
        self.power_offset_sb.setValue(-35)
        power_offset_vb.addWidget(power_offset_lb)
        power_offset_vb.addWidget(self.power_offset_sb)
        main_hb.addLayout(power_offset_vb)

        excitation_atten_vb = QVBoxLayout()
        excitation_atten_lb = QLabel("Excitation Atten")
        self.excitation_atten_sld = QDoubleSlider()
        self.excitation_atten_sld.setOrientation(Qt.Horizontal)
        self.excitation_atten_sld.setMinimum(0)
        self.excitation_atten_sld.setMaximum(31.5)
        self.excitation_atten_sld.setValue(0)
        self.excitation_atten_sld.setTickPosition(QSlider.TicksBelow)
        self.excitation_atten_sld.setTickInterval(10000)
        self.excitation_atten_sld.setSingleStep(1)
        self.excitation_atten_sb = QDoubleSpinBox()
        self.excitation_atten_sb.setMinimum(0)
        self.excitation_atten_sb.setMaximum(31.5)
        self.excitation_atten_sb.setValue(0)
        excitation_atten_hb = QHBoxLayout()
        excitation_atten_min_lb = QLabel("0")
        excitation_atten_min_lb.setAlignment(Qt.AlignLeft)
        excitation_atten_max_lb = QLabel("31.5")
        excitation_atten_max_lb.setAlignment(Qt.AlignRight)
        excitation_atten_hb.addWidget(excitation_atten_min_lb)
        excitation_atten_hb.addWidget(self.excitation_atten_sb)
        excitation_atten_hb.addWidget(excitation_atten_max_lb)
        excitation_atten_vb.addWidget(excitation_atten_lb)
        excitation_atten_vb.addWidget(self.excitation_atten_sld)
        excitation_atten_vb.addLayout(excitation_atten_hb)
        main_hb.addLayout(excitation_atten_vb)

        RF_power_vb = QVBoxLayout()
        RF_power_lb = QLabel("RF Source Power (dBm)")
        self.RF_power_sb = QDoubleSpinBox()
        self.RF_power_btn = QPushButton("Set")
        RF_power_vb.addWidget(RF_power_lb)
        RF_power_vb.addWidget(self.RF_power_sb)
        RF_power_vb.addWidget(self.RF_power_btn)
        main_hb.addLayout(RF_power_vb)

        main_grid.addLayout(main_hb)

        # create tab screen
        self.tabs = QTabWidget()
        self.tabs.setMaximumHeight(500)
        main_grid.addWidget(self.tabs)

        # initalize all tabs
        self.initControlTab()
        self.initTuningTab()

    def initControlTab(self):
        # create tab
        control_tab = QWidget()

        # create main hbox and main vbox to organize layout
        main_hbox = QHBoxLayout()
        main_hbox.setSpacing(10)
        control_tab.setLayout(main_hbox)

        main_vbox1 = QVBoxLayout()

        excitation_vbox = QVBoxLayout()

        excitation_lb = QLabel("Excitation")
        excitation_vbox.addWidget(excitation_lb)

        freq_lb = QLabel("Frequency (MHz)")
        self.freq_sb = QDoubleSpinBox()
        self.freq_sb.setMinimum(0)
        self.freq_sb.setMaximum(10000)
        self.freq_sb.setValue(1000)
        excitation_vbox.addWidget(freq_lb)
        excitation_vbox.addWidget(self.freq_sb)

        power_lb = QLabel("Power (dBm)")
        self.power_sb = QDoubleSpinBox()
        self.power_sb.setMinimum(-100)
        self.power_sb.setMaximum(0)
        self.power_sb.setValue(-40)
        self.power_set_btn = QPushButton("Set")
        excitation_vbox.addWidget(power_lb)
        excitation_vbox.addWidget(self.power_sb)
        excitation_vbox.addWidget(self.power_set_btn)

        reference_vbox = QVBoxLayout()

        reference_lb = QLabel("Reference")
        reference_vbox.addWidget(reference_lb)

        ref_phase_lb = QLabel("Ref Phase (Aux2)")
        self.ref_phase_sld = QDoubleSlider()
        self.ref_phase_sld.setOrientation(Qt.Horizontal)
        self.ref_phase_sld.setMinimum(0)
        self.ref_phase_sld.setMaximum(10)
        self.ref_phase_sld.setTickPosition(QSlider.TicksBelow)
        self.ref_phase_sld.setTickInterval(10000)
        self.ref_phase_sld.setSingleStep(1)
        ref_phase_hb = QHBoxLayout()
        self.ref_phase_sb = QDoubleSpinBox()
        self.ref_phase_sb.setMinimum(0)
        self.ref_phase_sb.setMaximum(10)
        ref_phase_min_lb = QLabel("0")
        ref_phase_min_lb.setAlignment(Qt.AlignLeft)
        ref_phase_max_lb = QLabel("10")
        ref_phase_max_lb.setAlignment(Qt.AlignRight)
        ref_phase_hb.addWidget(ref_phase_min_lb)
        ref_phase_hb.addWidget(self.ref_phase_sb)
        ref_phase_hb.addWidget(ref_phase_max_lb)
        reference_vbox.addWidget(ref_phase_lb)
        reference_vbox.addWidget(self.ref_phase_sld)
        reference_vbox.addLayout(ref_phase_hb)

        main_vbox1.addLayout(excitation_vbox)
        main_vbox1.addLayout(reference_vbox)

        main_vbox2 = QVBoxLayout()

        cancellation_vb = QVBoxLayout()

        cancellation_lb = QLabel("Cancellation")
        cancellation_vb.addWidget(cancellation_lb)

        cancel_phase_lb = QLabel("Cancel Phase (Aux1)")
        self.cancel_phase_sld = QDoubleSlider()
        self.cancel_phase_sld.setMinimum(-1)
        self.cancel_phase_sld.setMaximum(10.5)
        self.cancel_phase_sld.setValue(0)
        self.cancel_phase_sld.setOrientation(Qt.Horizontal)
        self.cancel_phase_sld.setTickPosition(QSlider.TicksBelow)
        self.cancel_phase_sld.setTickInterval(10000)
        self.cancel_phase_sld.setSingleStep(1)
        cancel_phase_hb = QHBoxLayout()
        self.cancel_phase_sb = QDoubleSpinBox()
        self.cancel_phase_sb.setMinimum(-1)
        self.cancel_phase_sb.setMaximum(10.5)
        cancel_phase_min_lb = QLabel("-1")
        cancel_phase_min_lb.setAlignment(Qt.AlignLeft)
        cancel_phase_max_lb = QLabel("10.5")
        cancel_phase_max_lb.setAlignment(Qt.AlignRight)
        cancel_phase_hb.addWidget(cancel_phase_min_lb)
        cancel_phase_hb.addWidget(self.cancel_phase_sb)
        cancel_phase_hb.addWidget(cancel_phase_max_lb)
        cancellation_vb.addWidget(cancel_phase_lb)
        cancellation_vb.addWidget(self.cancel_phase_sld)
        cancellation_vb.addLayout(cancel_phase_hb)

        cancel_atten_lb = QLabel("Cancel Atten Digital (dB)")
        self.cancel_atten_sld = QDoubleSlider()
        self.cancel_atten_sld.setOrientation(Qt.Horizontal)
        self.cancel_atten_sld.setMinimum(0)
        self.cancel_atten_sld.setMaximum(31.5)
        self.cancel_atten_sld.setValue(0)
        self.cancel_atten_sld.setTickPosition(QSlider.TicksBelow)
        self.cancel_atten_sld.setTickInterval(10000)
        self.cancel_atten_sld.setSingleStep(1)
        cancel_atten_hb = QHBoxLayout()
        self.cancel_atten_sb = QDoubleSpinBox()
        self.cancel_atten_sb.setMinimum(0)
        self.cancel_atten_sb.setMaximum(31.5)
        self.cancel_atten_sb.setValue(0)
        cancel_atten_min_lb = QLabel("0")
        cancel_atten_min_lb.setAlignment(Qt.AlignLeft)
        cancel_atten_max_lb = QLabel("31.5")
        cancel_atten_max_lb.setAlignment(Qt.AlignRight)
        cancel_atten_hb.addWidget(cancel_atten_min_lb)
        cancel_atten_hb.addWidget(self.cancel_atten_sb)
        cancel_atten_hb.addWidget(cancel_atten_max_lb)
        cancellation_vb.addWidget(cancel_atten_lb)
        cancellation_vb.addWidget(self.cancel_atten_sld)
        cancellation_vb.addLayout(cancel_atten_hb)

        cancel_atten_analog_lb = QLabel("Cancel Atten Analog (Aux3)")
        self.cancel_atten_analog_sld = QDoubleSlider()
        self.cancel_atten_analog_sld.setOrientation(Qt.Horizontal)
        self.cancel_atten_analog_sld.setMinimum(-3)
        self.cancel_atten_analog_sld.setMaximum(10)
        self.cancel_atten_analog_sld.setValue(0)
        self.cancel_atten_analog_sld.setTickPosition(QSlider.TicksBelow)
        self.cancel_atten_analog_sld.setTickInterval(10000)
        self.cancel_atten_analog_sld.setSingleStep(1)
        cancel_atten_analog_hb = QHBoxLayout()
        self.cancel_atten_analog_sb = QDoubleSpinBox()
        self.cancel_atten_analog_sb.setMinimum(-3)
        self.cancel_atten_analog_sb.setMaximum(10)
        self.cancel_atten_analog_sb.setValue(0)
        cancel_atten_analog_min_lb = QLabel("-3")
        cancel_atten_analog_min_lb.setAlignment(Qt.AlignLeft)
        cancel_atten_analog_max_lb = QLabel("10")
        cancel_atten_analog_max_lb.setAlignment(Qt.AlignRight)
        cancel_atten_analog_hb.addWidget(cancel_atten_analog_min_lb)
        cancel_atten_analog_hb.addWidget(self.cancel_atten_analog_sb)
        cancel_atten_analog_hb.addWidget(cancel_atten_analog_max_lb)
        cancellation_vb.addWidget(cancel_atten_analog_lb)
        cancellation_vb.addWidget(self.cancel_atten_analog_sld)
        cancellation_vb.addLayout(cancel_atten_analog_hb)

        main_vbox2.addLayout(cancellation_vb)

        main_vbox3 = QVBoxLayout()
        power_monitor_hb = QHBoxLayout()
        self.start_monitor_btn = QPushButton("Start monitor")
        self.monitor_ind = QLedIndicator('orange')
        self.refresh_rate = QDoubleSpinBox()
        self.refresh_rate.setValue(10.0)
        refresh_rate_unit_lb = QLabel("ms")
        power_monitor_hb.addWidget(self.start_monitor_btn)
        power_monitor_hb.addWidget(self.monitor_ind)
        power_monitor_hb.addWidget(self.refresh_rate)
        power_monitor_hb.addWidget(refresh_rate_unit_lb)
        main_vbox3.addLayout(power_monitor_hb)

        self.power_monitor_plot = pg.PlotWidget()
        self.power_monitor_plot.setBackground('w')
        main_vbox3.addWidget(self.power_monitor_plot)

        main_hbox.addStretch()

        main_hbox.addLayout(main_vbox1)
        main_hbox.addLayout(main_vbox2)
        main_hbox.addLayout(main_vbox3)

        self.tabs.addTab(control_tab, 'MIM Control')

    def initTuningTab(self):
        # create tab
        tuning_tab = QWidget()

        # create main hbox and main vbox to organize layout
        main_hbox = QHBoxLayout()
        main_hbox.setSpacing(10)
        tuning_tab.setLayout(main_hbox)

        main_vbox1 = QVBoxLayout()

        param_vb = QVBoxLayout()
        param_lb = QLabel("Sweep Param")
        self.param_cb = QComboBox()
        self.param_cb.addItems(["Frequency", "Ref Phase"])
        param_vb.addWidget(param_lb)
        param_vb.addWidget(self.param_cb)
        main_vbox1.addLayout(param_vb)

        start_hb = QHBoxLayout()
        start_vb = QVBoxLayout()
        start_lb = QLabel("Start")
        self.start_sb = QSpinBox()
        start_vb.addWidget(start_lb)
        start_vb.addWidget(self.start_sb)
        stop_vb = QVBoxLayout()
        stop_lb = QLabel("Stop")
        self.stop_sb = QSpinBox()
        stop_vb.addWidget(stop_lb)
        stop_vb.addWidget(self.stop_sb)
        start_hb.addLayout(start_vb)
        start_hb.addLayout(stop_vb)
        main_vbox1.addLayout(start_hb)

        step_hb = QHBoxLayout()
        step_vb = QVBoxLayout()
        step_lb = QLabel("Step")
        self.step_sb = QSpinBox()
        step_vb.addWidget(step_lb)
        step_vb.addWidget(self.step_sb)
        step_time_vb = QVBoxLayout()
        step_time_lb = QLabel("Step Time (ms)")
        self.step_time_sb = QSpinBox()
        step_time_vb.addWidget(step_time_lb)
        step_time_vb.addWidget(self.step_time_sb)
        step_hb.addLayout(step_vb)
        step_hb.addLayout(step_time_vb)
        main_vbox1.addLayout(step_hb)

        recording_vb = QVBoxLayout()
        recording_lb = QLabel("Recording Param")
        self.recording_cb = QComboBox()
        self.recording_cb.addItems(["Power monitor", "Main Ch1", "Main Ch2", "Main Ch3", "Main Ch4"])
        recording_vb.addWidget(recording_lb)
        recording_vb.addWidget(self.recording_cb)
        main_vbox1.addLayout(recording_vb)

        button_hb = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        button_hb.addWidget(self.start_btn)
        button_hb.addWidget(self.stop_btn)
        main_vbox1.addLayout(button_hb)

        main_vbox2 = QVBoxLayout()
        self.freq_sweep_plot = pg.PlotWidget()
        self.freq_sweep_plot.setBackground('w')
        main_vbox2.addWidget(self.freq_sweep_plot)

        main_hbox.addLayout(main_vbox1)
        main_hbox.addLayout(main_vbox2)

        self.tabs.addTab(tuning_tab, 'Tuning')


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

# from https://gist.github.com/dennis-tra/994a65d6165a328d4eabaadbaedac2cc
class QDoubleSlider(QSlider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decimals = 5
        self._max_int = 10 ** self.decimals

        super().setMinimum(0)
        super().setMaximum(self._max_int)

        self._min_value = 0.0
        self._max_value = 1.0

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def value(self):
        return float(super().value()) / self._max_int * self._value_range + self._min_value

    def setValue(self, value):
        super().setValue(int((value - self._min_value) / self._value_range * self._max_int))

    def setMinimum(self, value):
        if value > self._max_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        self._min_value = value
        self.setValue(self.value())

    def setMaximum(self, value):
        if value < self._min_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        self._max_value = value
        self.setValue(self.value())

    def minimum(self):
        return self._min_value

    def maximum(self):
        return self._max_value

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     font = QFont("Calibri")
#     font.setPointSize(14)  # Set font size (14pt in this example)
#     app.setFont(font)
#     window = MIMControl()
#     sys.exit(app.exec_())