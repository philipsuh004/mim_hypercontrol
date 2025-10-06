"""
================
Title: Helium monitor GUI
Author: Philip David Suh and Siyuan Qiu
Create Date: 2025/03/24
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

class HeliumMonitor(QFrame):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 500, 800, 900)
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
        self.setWindowTitle("Helium Monitor")

        main_hb = QHBoxLayout()

        main_vb = QVBoxLayout()

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
        model_vb.addWidget(model_lb)
        model_vb.addWidget(self.model_cb)
        connect_hb.addLayout(model_vb)

        main_vb.addLayout(connect_hb)
        mode_hb = QHBoxLayout()

        mode_vb = QVBoxLayout()
        mode_lb = QLabel("Sample Mode")
        self.mode_cb = QComboBox()
        self.mode_cb.addItems(["Sample Hold", "Continuous"])
        mode_vb.addWidget(mode_lb)
        mode_vb.addWidget(self.mode_cb)
        mode_hb.addLayout(mode_vb)

        interval_vb = QVBoxLayout()
        interval_lb = QLabel("Interval (s)")
        self.interval_sb = QSpinBox()
        self.interval_sb.setMaximum(1000)
        self.interval_sb.setValue(300)
        interval_vb.addWidget(interval_lb)
        interval_vb.addWidget(self.interval_sb)
        mode_hb.addLayout(interval_vb)

        range_vb = QVBoxLayout()
        range_lb = QLabel("Display Range")
        self.range_cb = QComboBox()
        self.range_cb.addItems(["Auto", "Last 30min", "Last 24hr"])
        range_vb.addWidget(range_lb)
        range_vb.addWidget(self.range_cb)
        mode_hb.addLayout(range_vb)

        main_vb.addLayout(mode_hb)
        main_hb.addLayout(main_vb)

        he_level_vb = QVBoxLayout()
        he_level_lb = QLabel("Helium Level (in)")
        self.level_lb = QLabel()
        self.level_lb.setStyleSheet("border: 1px solid black;")
        self.level_lb.setFixedWidth(100)
        he_level_vb.addWidget(he_level_lb)
        he_level_vb.addWidget(self.level_lb)
        main_hb.addLayout(he_level_vb)

        self.helium_level_plot = pg.PlotWidget()
        self.helium_level_plot.setBackground('w')

        main_grid.addLayout(main_hb)
        main_grid.addWidget(self.helium_level_plot)


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
    window = HeliumMonitor()
    sys.exit(app.exec_())