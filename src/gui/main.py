"""
================
Title: MIM HyperControl GUI
Author: Philip David Suh and Siyuan Qiu 
Create Date: 2025/07/23
Institution: Stanford University, Department of Physics
=================
"""

# Import pylablib for attocube connection
try:
    from pylablib.devices import Attocube
    print("✅ Pylablib Attocube imported successfully")
except (ImportError, AttributeError) as e:
    print(f"❌ Pylablib import failed: {e}")
    print("💡 Please install pylablib: pip install pylablib")
    Attocube = None

from .controllers.mim_control import MIMControl
from .controllers.helium_monitor import HeliumMonitor
from .controllers.temperature_control import TemperatureControl
from .controllers.magnet_control import MagnetControl
from .controllers.experiment_control import CreateExperiment
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import sip
import pyqtgraph as pg
import sys
import matplotlib
matplotlib.use("Qt5Agg")
matplotlib.rcParams['savefig.dpi'] = 600
import pyvisa as visa
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import time



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # set the size and title of the window
        self.setGeometry(100, 50, 1550, 1100)
        self.setWindowTitle('MIM Main Control')

        self.init_UI()

        self._createActions()
        self._createMenuBar()

    def init_UI(self):
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)




        global main_widget
        global MIM_widget
        global helium_widget
        global temperature_widget
        global magnet_widget
        global experiment_widget

        MIM_widget = MIMControl()
        MIM_widget.hide()

        temperature_widget = TemperatureControl()
        temperature_widget.hide()

        helium_widget = HeliumMonitor()
        helium_widget.hide()

        # Remove the signal connection since HeliumMonitor doesn't emit signals anymore
        # helium_widget.helium_level_changed.connect(self.on_helium_level_changed)

        magnet_widget = MagnetControl()
        magnet_widget.hide()

        experiment_widget = CreateExperiment()
        experiment_widget.hide()

        main_widget = MainControl()

        splitter.addWidget(main_widget)

        """
        self.show()

        # bring window to top and act like a "normal" window!
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # set always on top flag, makes window disappear
        self.show() # makes window reappear, but it's ALWAYS on top
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint) # clear always on top flag, makes window disappear
        self.show() # makes window reappear, acts like normal window now (on top now but can be underneath if you raise another window)
        """

        self.show()

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a title
        windowMenu = menuBar.addMenu("&Window")
        windowMenu.addSeparator()
        windowMenu.addAction(self.initializeAction)
        windowMenu.addAction(self.exitAction)
        controlMenu = menuBar.addMenu("&Control")
        controlMenu.addAction(self.initializeMIM)
        controlMenu.addAction(self.initializeTransport)
        controlMenu.addAction(self.initializeLockin)
        experimentMenu = menuBar.addMenu("&Experiment")
        experimentMenu.addAction(self.createExperiment)
        experimentMenu.addAction(self.initializeExperimentControl)

    def _createActions(self):
        # Creating actions using the second constructor
        self.initializeAction = QAction("&Reinitialize...", self)
        self.initializeAction.triggered.connect(self.reinitialize)
        self.exitAction = QAction("&Exit...", self)
        self.exitAction.triggered.connect(self.exit)
        self.initializeMIM = QAction("&MIM", self)
        self.initializeMIM.triggered.connect(MIM_widget.show)
        self.initializeTransport = QAction("&Transport", self)
        self.initializeLockin = QAction("&Lockin", self)
        self.createExperiment = QAction("&Create Experiment", self)
        self.createExperiment.triggered.connect(experiment_widget.show)
        self.initializeExperimentControl = QAction("&Experiment Control", self)
        self.initializeExperimentControl.triggered.connect(self.update_experiment_widget)

    def update_experiment_widget(self):
        experiment_widget.experimentControl.show()

    def reinitialize(self):
        buttonReply = QMessageBox.question(self, 'Reintialize', "Are you sure to reinitialize everything?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.init_UI()
        else:
            return

    def show_mainControl(self):
        self.show()

    def exit(self):
        app.quit()

    def closeEvent(self, event):
        app.quit()

class MainControl(QFrame):
    def __init__(self):
        super().__init__()

        # 222
        self.nanonis = None
        self.attocube = None
        self.connect_to_nanonis()  # Auto-connect to nanonis on initialization

        # 222

        self.initUI()

        # Add timer to update helium level display
        self.helium_update_timer = QTimer(self)
        self.helium_update_timer.timeout.connect(self.update_helium_display)
        self.helium_update_timer.start(1000)  # Update every second

        # Add timer to update position labels since Nanonis is auto-connected
        self.position_update_timer = QTimer(self)
        self.position_update_timer.timeout.connect(self.update_position_labels)
        self.position_update_timer.start(100)  # Update every 100ms

        # Track current encoder axis to avoid unnecessary digital line updates
        self.current_encoder_axis = "X"  # Default to X axis

        self.show()

        # Populate nanonis channels if connected
        if hasattr(self, 'populate_nanonis_channel_cbs') and self.nanonis:
            self.populate_nanonis_channel_cbs()

        # Set initial encoder axis digital lines (default to X axis)
        if self.nanonis:
            self.set_encoder_axis_digital_lines("X")

    def initUI(self):

        # create main grid to organize layout
        main_grid = QVBoxLayout()
        main_grid.setSpacing(10)
        self.setLayout(main_grid)
        self.setWindowTitle("MIM Main Control")

        # top display row
        top_display_hb = QHBoxLayout()
        scanner_display_grid = QGridLayout()
        TControl_display_grid = QGridLayout()
        Magnet_display_grid = QGridLayout()

        scanner_lb = QLabel("Scanner")
        scanner_display_grid.addWidget(scanner_lb, 0, 0, 1, 1, Qt.AlignCenter)
        scanner_control_hb = QHBoxLayout()
        self.scanner_connection_btn = QPushButton("On")
        self.scanner_ind = QLedIndicator('orange')
        scanner_control_hb.addWidget(self.scanner_connection_btn)
        scanner_control_hb.addWidget(self.scanner_ind)

        # 222
        self.scanner_connection_btn.clicked.connect(self.toggle_attocube_connection)
        # 222

        scanner_display_grid.addLayout(scanner_control_hb, 1, 0, 1, 1, Qt.AlignCenter)

        X1_lb = QLabel("X")
        self.X1_num_lb = QLabel()
        self.X1_num_lb.setStyleSheet("border: 1px solid black;")
        self.X1_num_lb.setFixedWidth(100)
        X1_hb = QHBoxLayout()
        X1_hb.addWidget(X1_lb)
        X1_hb.addWidget(self.X1_num_lb)
        scanner_display_grid.addLayout(X1_hb, 0, 1, 1, 1, Qt.AlignCenter)

        Y1_lb = QLabel("Y")
        self.Y1_num_lb = QLabel()
        self.Y1_num_lb.setStyleSheet("border: 1px solid black;")
        self.Y1_num_lb.setFixedWidth(100)
        Y1_hb = QHBoxLayout()
        Y1_hb.addWidget(Y1_lb)
        Y1_hb.addWidget(self.Y1_num_lb)
        scanner_display_grid.addLayout(Y1_hb, 0, 2, 1, 1, Qt.AlignCenter)

        Z1_lb = QLabel("Z")
        self.Z1_num_lb = QLabel()
        self.Z1_num_lb.setStyleSheet("border: 1px solid black;")
        self.Z1_num_lb.setFixedWidth(100)
        Z1_hb = QHBoxLayout()
        Z1_hb.addWidget(Z1_lb)
        Z1_hb.addWidget(self.Z1_num_lb)
        scanner_display_grid.addLayout(Z1_hb, 0, 3, 1, 1, Qt.AlignCenter)

        X2_lb = QLabel("X")
        self.X2_num_lb = QLabel()
        self.X2_num_lb.setStyleSheet("border: 1px solid black;")
        self.X2_num_lb.setFixedWidth(100)
        X2_hb = QHBoxLayout()
        X2_hb.addWidget(X2_lb)
        X2_hb.addWidget(self.X2_num_lb)
        scanner_display_grid.addLayout(X2_hb, 1, 1, 1, 1, Qt.AlignCenter)

        Y2_lb = QLabel("Y")
        self.Y2_num_lb = QLabel()
        self.Y2_num_lb.setStyleSheet("border: 1px solid black;")
        self.Y2_num_lb.setFixedWidth(100)
        Y2_hb = QHBoxLayout()
        Y2_hb.addWidget(Y2_lb)
        Y2_hb.addWidget(self.Y2_num_lb)
        scanner_display_grid.addLayout(Y2_hb, 1, 2, 1, 1, Qt.AlignCenter)

        Z2_lb = QLabel("Z")
        self.Z2_num_lb = QLabel()
        self.Z2_num_lb.setStyleSheet("border: 1px solid black;")
        self.Z2_num_lb.setFixedWidth(100)
        Z2_hb = QHBoxLayout()
        Z2_hb.addWidget(Z2_lb)
        Z2_hb.addWidget(self.Z2_num_lb)
        scanner_display_grid.addLayout(Z2_hb, 1, 3, 1, 1, Qt.AlignCenter)

        TControl_hb = QHBoxLayout()
        self.TControl_btn = QPushButton("T Ctrl")
        self.TControl_btn.clicked.connect(temperature_widget.show)
        self.TControl_ind = QLedIndicator('orange')
        TControl_hb.addWidget(self.TControl_btn)
        TControl_hb.addWidget(self.TControl_ind)
        TControl_display_grid.addLayout(TControl_hb, 0, 0, 1, 1, Qt.AlignCenter)

        T_Sample_lb = QLabel("Sample")
        self.T_Sample_num_lb = QLabel("0 K")
        self.T_Sample_num_lb.setStyleSheet("border: 1px solid black;")
        self.T_Sample_num_lb.setFixedWidth(100)
        T_Sample_hb = QHBoxLayout()
        T_Sample_hb.addWidget(T_Sample_lb)
        T_Sample_hb.addWidget(self.T_Sample_num_lb)
        TControl_display_grid.addLayout(T_Sample_hb, 0, 1, 1, 1, Qt.AlignCenter)

        Helium_hb = QHBoxLayout()
        self.Helium_btn = QPushButton("Helium")
        self.Helium_btn.clicked.connect(self.show_helium_monitor)
        self.Helium_ind = QLedIndicator('orange')
        Helium_hb.addWidget(self.Helium_btn)
        Helium_hb.addWidget(self.Helium_ind)
        TControl_display_grid.addLayout(Helium_hb, 0, 2, 1, 1, Qt.AlignCenter)

        A_lb = QLabel("A")
        self.A_num_lb = QLabel("0 K")
        self.A_num_lb.setStyleSheet("border: 1px solid black;")
        self.A_num_lb.setFixedWidth(100)
        A_hb = QHBoxLayout()
        A_hb.addWidget(A_lb)
        A_hb.addWidget(self.A_num_lb)
        TControl_display_grid.addLayout(A_hb, 1, 0, 1, 1, Qt.AlignCenter)

        B_lb = QLabel("B")
        self.B_num_lb = QLabel("0 K")
        self.B_num_lb.setStyleSheet("border: 1px solid black;")
        self.B_num_lb.setFixedWidth(100)
        B_hb = QHBoxLayout()
        B_hb.addWidget(B_lb)
        B_hb.addWidget(self.B_num_lb)
        TControl_display_grid.addLayout(B_hb, 1, 1, 1, 1, Qt.AlignCenter)

        He_lb = QLabel("He")
        self.He_num_lb = QLabel("0 in")
        self.He_num_lb.setStyleSheet("border: 1px solid black;")
        self.He_num_lb.setFixedWidth(100)
        He_hb = QHBoxLayout()
        He_hb.addWidget(He_lb)
        He_hb.addWidget(self.He_num_lb)
        TControl_display_grid.addLayout(He_hb, 1, 2, 1, 1, Qt.AlignCenter)

        Magnet_hb = QHBoxLayout()
        self.Magnet_btn = QPushButton("Magnet")
        self.Magnet_btn.clicked.connect(magnet_widget.show)
        self.Magnet_ind = QLedIndicator('orange')
        Magnet_hb.addWidget(self.Magnet_btn)
        Magnet_hb.addWidget(self.Magnet_ind)
        Magnet_display_grid.addLayout(Magnet_hb, 0, 0, 1, 1, Qt.AlignCenter)

        Magnet_I_lb = QLabel("I")
        self.Magnet_I_num_lb = QLabel("0 A")
        self.Magnet_I_num_lb.setStyleSheet("border: 1px solid black;")
        self.Magnet_I_num_lb.setFixedWidth(100)
        Magnet_I_hb = QHBoxLayout()
        Magnet_I_hb.addWidget(Magnet_I_lb)
        Magnet_I_hb.addWidget(self.Magnet_I_num_lb)
        Magnet_display_grid.addLayout(Magnet_I_hb, 1, 0, 1, 1, Qt.AlignCenter)

        Magnet_B_lb = QLabel("B")
        self.Magnet_B_num_lb = QLabel("0 T")
        self.Magnet_B_num_lb.setStyleSheet("border: 1px solid black;")
        self.Magnet_B_num_lb.setFixedWidth(100)
        Magnet_B_hb = QHBoxLayout()
        Magnet_B_hb.addWidget(Magnet_B_lb)
        Magnet_B_hb.addWidget(self.Magnet_B_num_lb)
        Magnet_display_grid.addLayout(Magnet_B_hb, 1, 2, 1, 1, Qt.AlignCenter)

        # Add a dashed line separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)  # Horizontal line
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("border: 3px dashed gray;")

        # Add a dashed line separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.VLine)  # Horizontal line
        line2.setFrameShadow(QFrame.Plain)
        line2.setStyleSheet("border: 3px dashed gray;")

        top_display_hb.addLayout(scanner_display_grid)
        top_display_hb.addWidget(line)
        top_display_hb.addLayout(TControl_display_grid)
        top_display_hb.addWidget(line2)
        top_display_hb.addLayout(Magnet_display_grid)

        # Data saving directory
        data_directory_hb = QHBoxLayout()
        self.select_folder_btn = QPushButton("Select directory")
        self.select_folder_btn.clicked.connect(self.select_directory)
        self.data_directory_lb = QLabel()
        self.data_directory_lb.setStyleSheet("border: 1px solid black;")
        self.data_directory_lb.setFixedWidth(1000)
        update_interval_vb = QVBoxLayout()
        update_interval_lb = QLabel("Update interval (ms)")
        update_interval_sb = QSpinBox()
        update_interval_sb.setValue(50)
        update_interval_vb.addWidget(update_interval_lb)
        update_interval_vb.addWidget(update_interval_sb)
        data_directory_hb.addWidget(self.select_folder_btn)
        data_directory_hb.addWidget(self.data_directory_lb)
        data_directory_hb.addLayout(update_interval_vb)

        # Z controller
        Z_controller_vb = QVBoxLayout()

        Z_controller_hb = QHBoxLayout()
        Z_controller_name_lb = QLabel("Z Controller")
        Z_controller_name_lb.setStyleSheet("font-weight: bold;")
        self.Z_controller_position_lb = QLabel("0.0 nm")
        self.Z_controller_position_lb.setStyleSheet("border: 1px solid black;")
        self.Z_controller_position_lb.setFixedWidth(100)
        Z_controller_hb.addWidget(Z_controller_name_lb)
        Z_controller_hb.addWidget(self.Z_controller_position_lb)
        Z_controller_vb.addLayout(Z_controller_hb)

        Z_controller_btn_hb = QHBoxLayout()
        self.Z_controller_btn = QPushButton("On")
        self.z_controller_active = False  # Track Z controller state

        # 222
        self.Z_controller_btn.clicked.connect(self.toggle_z_controller)
        # 222
        self.Z_controller_ind = QLedIndicator('orange')
        Z_controller_btn_hb.addWidget(self.Z_controller_btn)
        Z_controller_btn_hb.addWidget(self.Z_controller_ind)
        Z_controller_vb.addLayout(Z_controller_btn_hb)

        Z_controller_withdraw_hb = QHBoxLayout()
        self.withdraw_btn = QPushButton("Withdraw")
        self.withdraw_btn.setIcon(QIcon("UpArrow.jpg"))
        self.withdraw_btn.setIconSize(self.withdraw_btn.sizeHint())
        self.withdraw_btn.setStyleSheet("text-align: center;")

        # 222
        self.withdraw_btn.clicked.connect(self.withdraw_tip)
        # 222

        self.app_withdraw_btn = QPushButton("App & Withdraw")

        # 222
        self.app_withdraw_btn.clicked.connect(self.approach_withdraw)
        # 222

        Z_controller_withdraw_hb.addWidget(self.withdraw_btn)
        Z_controller_withdraw_hb.addWidget(self.app_withdraw_btn)
        Z_controller_vb.addLayout(Z_controller_withdraw_hb)

        Z_controller_lift_hb = QHBoxLayout()
        tipLift_vb = QVBoxLayout()

        self.lift_btn = QPushButton("App & Lift")

        # 222
        self.lift_btn.clicked.connect(self.approach_lift)
        # 222

        self.lift_btn.setIcon(QIcon("DownArrow.jpg"))
        self.lift_btn.setIconSize(self.lift_btn.sizeHint())
        self.lift_btn.setStyleSheet("text-align: center;")
        tipLift_lb = QLabel("Tip Lift (μm)")
        self.tipLift_sb = QDoubleSpinBox()
        self.tipLift_sb.setDecimals(3)  # 3 decimal places
        self.tipLift_sb.editingFinished.connect(self.update_tip_lift_to_nanonis)
        tipLift_vb.addWidget(tipLift_lb)
        tipLift_vb.addWidget(self.tipLift_sb)
        delay_vb = QVBoxLayout()
        delay_lb = QLabel("Delay (ms)")
        self.delay_sb = QDoubleSpinBox()
        self.delay_sb.setDecimals(3)  # 3 decimal places
        self.delay_sb.editingFinished.connect(self.update_delay_to_nanonis)
        delay_vb.addWidget(delay_lb)
        delay_vb.addWidget(self.delay_sb)
        Z_controller_lift_hb.addWidget(self.lift_btn)
        Z_controller_lift_hb.addLayout(tipLift_vb)
        Z_controller_lift_hb.addLayout(delay_vb)
        Z_controller_vb.addLayout(Z_controller_lift_hb)

        self.lowLimit_btn = QPushButton("Set current Z as low limit")

        # 222
        self.lowLimit_btn.clicked.connect(self.set_current_z_as_low_limit)
        # 222

        Z_controller_vb.addWidget(self.lowLimit_btn)

        Z_controller_lowLimit_hb = QHBoxLayout()
        Z_lowLimit_lb = QLabel("Z low limit (μm)")
        self.Z_lowLimit_sb = QDoubleSpinBox()
        self.Z_lowLimit_sb.setRange(-12.0, 12.0)  # Allow range from -12 to +12 micrometers
        self.Z_lowLimit_sb.setDecimals(3)  # Allow precision to 0.001 μm = 1 nm
        self.Z_lowLimit_sb.editingFinished.connect(self.update_z_low_limit_to_nanonis)
        self.fullRange_btn = QPushButton("Full range")

        # 222
        self.fullRange_btn.clicked.connect(self.set_full_range)
        # 222

        Z_controller_lowLimit_hb.addWidget(Z_lowLimit_lb)
        Z_controller_lowLimit_hb.addWidget(self.Z_lowLimit_sb)
        Z_controller_lowLimit_hb.addWidget(self.fullRange_btn)
        Z_controller_vb.addLayout(Z_controller_lowLimit_hb)

        Z_controller_voltageLimit_hb = QHBoxLayout()
        Z_voltageLimit_lb = QLabel("Z voltage limit (V)")
        self.Z_voltageLimit_sb = QDoubleSpinBox()

        # 222
        self.Z_voltageLimit_sb.setRange(0.0, 80.0)         # Enforce allowable range
        self.Z_voltageLimit_sb.setSingleStep(0.1)
        self.Z_voltageLimit_sb.setDecimals(1)              # 1 decimal place
        self.Z_voltageLimit_sb.setValue(30.0)              # Default value is 30.0 V
        # 222

        self.setAttocubeOffset_btn = QPushButton("Set attocube offset")

        # 222
        self.setAttocubeOffset_btn.clicked.connect(self.set_attocube_offset)
        # 222

        Z_controller_voltageLimit_hb.addWidget(Z_voltageLimit_lb)
        Z_controller_voltageLimit_hb.addWidget(self.Z_voltageLimit_sb)
        Z_controller_voltageLimit_hb.addWidget(self.setAttocubeOffset_btn)
        Z_controller_vb.addLayout(Z_controller_voltageLimit_hb)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)  # Set to horizontal line
        line.setFrameShadow(QFrame.Sunken)  # Optional: give a shadow effect
        Z_controller_vb.addWidget(line)

        # XYZ positioner
        XYZ_positioner_vb = QVBoxLayout()

        XYZ_positioner_lb = QLabel("XYZ Positioner")
        XYZ_positioner_lb.setStyleSheet("font-weight: bold;")
        XYZ_positioner_vb.addWidget(XYZ_positioner_lb)

        axis_hb = QHBoxLayout()
        axis_vb = QVBoxLayout()
        axis_lb = QLabel("Axis")
        self.axis_cb = QComboBox()
        self.axis_cb.addItems(["X", "Y", "Z"])      # This is for XYZ stage movement
        self.axis_cb.currentIndexChanged.connect(self.on_axis_changed)  # Connect to update function
        axis_vb.addWidget(axis_lb)
        axis_vb.addWidget(self.axis_cb)
        self.gnd_lb = QLabel("GND")
        self.gnd_lb.setStyleSheet("border: 1px solid black;")
        self.gnd_btn = QPushButton("GND all")
        self.gnd_btn.clicked.connect(self.gnd_all_axes)

        axis_hb.addLayout(axis_vb)
        axis_hb.addWidget(self.gnd_lb)
        axis_hb.addWidget(self.gnd_btn)
        XYZ_positioner_vb.addLayout(axis_hb)

        positioner_setting1_hb = QHBoxLayout()
        frequency_vb = QVBoxLayout()
        frequency_lb = QLabel("Frequency (Hz)")
        self.frequency_sb = QDoubleSpinBox()

        # 222
        self.frequency_sb.setRange(1.0, 10000.0)  # TO BE CHANGED
        self.frequency_sb.setSingleStep(10.0)
        self.frequency_sb.setDecimals(1)
        self.frequency_sb.setValue(1000.0)  # Default
        self.frequency_sb.editingFinished.connect(self.update_frequency_to_attocube)
        # 222

        frequency_vb.addWidget(frequency_lb)
        frequency_vb.addWidget(self.frequency_sb)
        steps_vb = QVBoxLayout()
        steps_lb = QLabel("Number steps")
        self.steps_sb = QSpinBox()
        steps_vb.addWidget(steps_lb)
        steps_vb.addWidget(self.steps_sb)
        positioner_setting1_hb.addLayout(frequency_vb)
        positioner_setting1_hb.addLayout(steps_vb)
        XYZ_positioner_vb.addLayout(positioner_setting1_hb)

        positioner_setting2_hb = QHBoxLayout()
        voltage_vb = QVBoxLayout()
        voltage_lb = QLabel("Voltage")
        self.voltage_sb = QDoubleSpinBox()

        # 222
        self.voltage_sb.setRange(0.0, 80.0)  # Volts
        self.voltage_sb.setSingleStep(0.1)
        self.voltage_sb.setDecimals(1)
        self.voltage_sb.setValue(50.0)  # Default
        self.voltage_sb.editingFinished.connect(self.update_voltage_to_attocube)
        # 222

        voltage_vb.addWidget(voltage_lb)
        voltage_vb.addWidget(self.voltage_sb)
        self.direction_btn = QPushButton("Up")
        self.direction_btn.setIcon(QIcon("UpArrow.jpg"))
        self.direction_btn.setIconSize(self.direction_btn.sizeHint())
        self.direction_btn.setStyleSheet("text-align: center;")
        self.direction_btn.clicked.connect(self.toggle_upDown)
        positioner_setting2_hb.addLayout(voltage_vb)
        positioner_setting2_hb.addWidget(self.direction_btn)
        XYZ_positioner_vb.addLayout(positioner_setting2_hb)

        move_hb = QHBoxLayout()
        self.move_btn = QPushButton("Move")

        # 222
        self.move_btn.clicked.connect(self.move_positioner)
        # 222

        self.stop_btn = QPushButton("Stop")

        # 222
        self.stop_btn.clicked.connect(self.stop_positioner)
        # 222

        move_hb.addWidget(self.move_btn)
        move_hb.addWidget(self.stop_btn)
        XYZ_positioner_vb.addLayout(move_hb)

        self.autoApproach_cb = QCheckBox("Auto approach background loop")
        XYZ_positioner_vb.addWidget(self.autoApproach_cb)

        # 222
        self.autoApproach_cb.stateChanged.connect(self.handle_auto_approach_checkbox)
        # 222

        delay_hb = QHBoxLayout()
        self.resetFreq_cb = QCheckBox("Reset Freq")
        delay_lb = QLabel("Delay (ms)")
        self.XYZ_delay_sb = QDoubleSpinBox()
        delay_hb.addWidget(self.resetFreq_cb)
        delay_hb.addWidget(delay_lb)
        delay_hb.addWidget(self.XYZ_delay_sb)
        XYZ_positioner_vb.addLayout(delay_hb)

        self.safeTip_cb = QCheckBox("Safe tip")

        # 222
        self.safeTip_cb.stateChanged.connect(self.safe_tip_changed)
        # 222

        XYZ_positioner_vb.addWidget(self.safeTip_cb)

        left_main_grid = QVBoxLayout()
        left_main_grid.addLayout(Z_controller_vb)
        left_main_grid.addLayout(XYZ_positioner_vb)

        # Center graphs
        """
        center_main_grid = QVBoxLayout()
        self.MIM_plot = pg.PlotWidget()
        self.MIM_plot.setBackground('w')  # White background
        self.encoder_plot = pg.PlotWidget()
        self.encoder_plot.setBackground('w')  # White background
        center_main_grid.addWidget(self.MIM_plot)
        center_main_grid.addWidget(self.encoder_plot)
        """
        # 222
        # Center graphs (Z vs. MIM and X/Y vs. MIM)
        center_main_grid = QVBoxLayout()

        # === MIM_plot controls ===
        mim_plot_controls_hb = QHBoxLayout()
        self.mim_plot_interval_sb = QSpinBox()
        self.mim_plot_interval_sb.setRange(100, 10000)
        self.mim_plot_interval_sb.setValue(1000)
        mim_plot_interval_label = QLabel("Update interval (ms):")
        self.mim_plot_value_label = QLabel("Current Value: --")
        self.mim_plot_clear_btn = QPushButton("Clear")
        self.mim_plot_clear_btn.clicked.connect(lambda: self.clear_plot(self.MIM_plot, 'mim_plot_buffer'))
        mim_plot_controls_hb.addWidget(mim_plot_interval_label)
        mim_plot_controls_hb.addWidget(self.mim_plot_interval_sb)
        mim_plot_controls_hb.addWidget(self.mim_plot_value_label)
        mim_plot_controls_hb.addWidget(self.mim_plot_clear_btn)
        center_main_grid.addLayout(mim_plot_controls_hb)

        # === Dropdown to select real/imaginary channel ===
        # === Dropdowns for Real/Imag channel (Z and XY plots independently) ===
        axis_selector_hb = QHBoxLayout()

        # Axis selector for main plot
        axis_label = QLabel("Axis:")
        self.plot_axis_cb = QComboBox()
        self.plot_axis_cb.addItems(["X", "Y", "Z"])
        self.plot_axis_cb.setCurrentText("Z")  # Default to Z axis
        axis_selector_hb.addWidget(axis_label)
        axis_selector_hb.addWidget(self.plot_axis_cb)

        # Real/Imag selector for main plot
        mim_channel_label = QLabel("MIM Channel:")
        self.mim_channel_cb = QComboBox()
        self.mim_channel_cb.addItems(["MIM-Im", "MIM-Re", "MIM-Re_AC-X", "MIM-Im_AC-X"])
        axis_selector_hb.addWidget(mim_channel_label)
        axis_selector_hb.addWidget(self.mim_channel_cb)

        self.plot_axis_cb.currentIndexChanged.connect(self.update_mim_plot)
        self.mim_channel_cb.currentIndexChanged.connect(self.update_mim_plot)

        # Create the top plot widget before adding to layout
        self.MIM_plot = pg.PlotWidget()
        self.MIM_plot.setBackground('w')
        center_main_grid.addLayout(axis_selector_hb)
        center_main_grid.addLayout(mim_plot_controls_hb)
        center_main_grid.addWidget(self.MIM_plot)

        # MIM plot data buffer and timer for time-based updates
        self.mim_plot_buffer = []  # list of (t, pos, mim_val)
        self.mim_plot_start_time = time.time()
        self.mim_plot_timer = QTimer(self)
        self.mim_plot_timer.timeout.connect(self.update_mim_plot_timed)
        self.mim_plot_timer.start(self.mim_plot_interval_sb.value())
        self.mim_plot_interval_sb.valueChanged.connect(lambda val: self.mim_plot_timer.setInterval(val))
        self.plot_axis_cb.currentIndexChanged.connect(self.reset_mim_plot_buffer)
        self.mim_channel_cb.currentIndexChanged.connect(self.reset_mim_plot_buffer)



        # Encoder plot controls (bottom middle plot)
        encoder_controls_hb = QHBoxLayout()
        self.encoder_axis_cb = QComboBox()
        self.encoder_axis_cb.addItems(["X", "Y", "Z"])
        encoder_axis_label = QLabel("Encoder Axis:")
        self.encoder_interval_sb = QSpinBox()
        self.encoder_interval_sb.setRange(100, 10000)
        self.encoder_interval_sb.setValue(1000)
        encoder_interval_label = QLabel("Update interval (ms):")
        self.encoder_value_label = QLabel("Current Value: --")
        self.encoder_clear_btn = QPushButton("Clear")
        self.encoder_clear_btn.clicked.connect(lambda: self.clear_plot(self.encoder_plot, 'encoder_buffer'))
        encoder_controls_hb.addWidget(encoder_axis_label)
        encoder_controls_hb.addWidget(self.encoder_axis_cb)
        encoder_controls_hb.addWidget(encoder_interval_label)
        encoder_controls_hb.addWidget(self.encoder_interval_sb)
        encoder_controls_hb.addWidget(self.encoder_value_label)
        encoder_controls_hb.addWidget(self.encoder_clear_btn)
        center_main_grid.addLayout(encoder_controls_hb)

        self.encoder_plot = pg.PlotWidget()
        self.encoder_plot.setBackground('w')
        center_main_grid.addWidget(self.encoder_plot)

        # Encoder plot data buffer and timer
        self.encoder_buffer = []  # list of (t, value)
        self.encoder_start_time = time.time()
        self.encoder_timer = QTimer(self)
        self.encoder_timer.timeout.connect(self.update_encoder_plot)
        self.encoder_timer.start(self.encoder_interval_sb.value())
        self.encoder_interval_sb.valueChanged.connect(lambda val: self.encoder_timer.setInterval(val))
        self.encoder_axis_cb.currentIndexChanged.connect(self.reset_encoder_buffer)



        # Right graphs
        right_main_grid = QVBoxLayout()
        self.nanonis_plot_channel_cbs = []
        self.nanonis_plot_buffers = []
        self.nanonis_plot_start_times = []
        self.nanonis_plot_value_labels = []
        self.nanonis_plot_widgets = []
        self.nanonis_plot_interval_sbs = []
        self.nanonis_plot_timers = []
        for i in range(4):
            controls_hb = QHBoxLayout()
            channel_cb = QComboBox()
            channel_cb.setMinimumWidth(200)
            channel_cb.addItem("(loading...)")  # Will populate after nanonis is connected
            interval_sb = QSpinBox()
            interval_sb.setRange(100, 10000)
            interval_sb.setValue(1000)
            interval_label = QLabel("Update interval (ms):")
            value_label = QLabel("Current Value: --")
            clear_btn = QPushButton("Clear")
            clear_btn.clicked.connect(lambda checked, idx=i: self.clear_nanonis_plot(idx))
            controls_hb.addWidget(QLabel(f"Channel {i+1}:") )
            controls_hb.addWidget(channel_cb)
            controls_hb.addWidget(interval_label)
            controls_hb.addWidget(interval_sb)
            controls_hb.addWidget(value_label)
            controls_hb.addWidget(clear_btn)
            right_main_grid.addLayout(controls_hb)
            plot_widget = pg.PlotWidget()
            plot_widget.setBackground('w')
            right_main_grid.addWidget(plot_widget)
            self.nanonis_plot_channel_cbs.append(channel_cb)
            self.nanonis_plot_buffers.append([])  # Each buffer is a list of (t, value)
            self.nanonis_plot_start_times.append(time.time())
            self.nanonis_plot_value_labels.append(value_label)
            self.nanonis_plot_widgets.append(plot_widget)
            self.nanonis_plot_interval_sbs.append(interval_sb)
            # Timer will be created after nanonis is connected
            self.nanonis_plot_timers.append(None)

        # After connecting to nanonis, populate channel combo boxes
        def populate_nanonis_channel_cbs():
            if self.nanonis and hasattr(self.nanonis, 'signals'):
                # Default channels for the four right plots
                default_channels = [
                    "MIM-Re (V)",
                    "MIM-Im (V)",
                    "MIM-Re_AC-X (V)",
                    "MIM-Im_AC-X (V)"
                ]

                for i, cb in enumerate(self.nanonis_plot_channel_cbs):
                    cb.clear()
                    cb.addItems(self.nanonis.signals)

                    # Set default channel if available
                    if i < len(default_channels):
                        default_channel = default_channels[i]
                        if default_channel in self.nanonis.signals:
                            cb.setCurrentText(default_channel)
                        else:
                            # Fallback to first available channel if default not found
                            if len(self.nanonis.signals) > 0:
                                cb.setCurrentIndex(0)
        self.populate_nanonis_channel_cbs = populate_nanonis_channel_cbs

        # Call this after nanonis connection
        # self.populate_nanonis_channel_cbs()

        # Timer update functions for each right plot
        def make_update_fn(idx):
            def update():
                if not self.nanonis or not hasattr(self.nanonis, 'signals'):
                    return
                channel_cb = self.nanonis_plot_channel_cbs[idx]
                value_label = self.nanonis_plot_value_labels[idx]
                plot_widget = self.nanonis_plot_widgets[idx]
                buffer = self.nanonis_plot_buffers[idx]
                start_time = self.nanonis_plot_start_times[idx]
                channel_name = channel_cb.currentText()
                if channel_name not in self.nanonis.signals:
                    value_label.setText("Current Value: --")
                    return
                try:
                    index = self.nanonis.signals.index(channel_name)
                    value = self.nanonis.sig_val_get_by_index(index)
                except Exception as e:
                    value_label.setText("Current Value: --")
                    return
                t = time.time() - self.nanonis_plot_start_times[idx]
                buffer.append((t, value))
                if len(buffer) > 1000:
                    del buffer[0:len(buffer)-1000]
                xs, ys = zip(*buffer) if buffer else ([],[])
                plot_widget.clear()
                plot_widget.plot(xs, ys, pen='b')
                plot_widget.setLabel("bottom", "Time", units="s")
                plot_widget.setLabel("left", channel_name, units=self.get_axis_units(channel_name))
                self.configure_plot_appearance(plot_widget, channel_name)
                value_label.setText(self.format_value_with_units(value, channel_name))
            return update

        # Set up timers and channel change logic
        for i in range(4):
            update_fn = make_update_fn(i)
            timer = QTimer(self)
            timer.timeout.connect(update_fn)
            timer.start(self.nanonis_plot_interval_sbs[i].value())
            self.nanonis_plot_interval_sbs[i].valueChanged.connect(lambda val, idx=i: self.nanonis_plot_timers[idx].setInterval(val))
            self.nanonis_plot_channel_cbs[i].currentIndexChanged.connect(lambda _, idx=i: self.reset_nanonis_plot_buffer(idx))
            self.nanonis_plot_timers[i] = timer

        def reset_nanonis_plot_buffer(idx):
            self.nanonis_plot_buffers[idx].clear()
            self.nanonis_plot_start_times[idx] = time.time()
        self.reset_nanonis_plot_buffer = reset_nanonis_plot_buffer

        main_grid.addLayout(top_display_hb)
        main_grid.addLayout(data_directory_hb)
        # After defining left_main_grid, center_main_grid, right_main_grid
        bottom_main_grid = QHBoxLayout()
        bottom_main_grid.addLayout(left_main_grid)
        bottom_main_grid.addLayout(center_main_grid)
        bottom_main_grid.addLayout(right_main_grid)

        main_grid.addLayout(bottom_main_grid)

    def select_directory(self):
        # Open a dialog to select a directory
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")

        # Update the label to show the selected directory
        if directory:
            self.data_directory_lb.setText(f"{directory}")

    def toggle_upDown(self):
        if self.direction_btn.text() == "Up":
            self.direction_btn.setText("Down")
            self.direction_btn.setIcon(QIcon("DownArrow.jpg"))
            self.direction_btn.setStyleSheet("text-align: center;")
        else:
            self.direction_btn.setText("Up")
            self.direction_btn.setIcon(QIcon("UpArrow.jpg"))
            self.direction_btn.setStyleSheet("text-align: center;")

    # 222 Z CONTROLLER FUNCTIONS START
    def connect_to_nanonis(self):
        """Auto-connect to Nanonis on initialization"""
        if self.nanonis is not None:
            print("✅ Already connected to Nanonis.")
            return

        try:
            import pyvisa
            from Nanonis import Nanonis

            rm = pyvisa.ResourceManager()

            # Try to open and immediately close a test connection to avoid crashing Nanonis
            try:
                test_instr = rm.open_resource('TCPIP0::localhost::6501::SOCKET')
                test_instr.close()
            except Exception as conn_error:
                raise RuntimeError("Device not reachable") from conn_error

            # If that works, we safely create the full Nanonis object
            self.nanonis = Nanonis(rm, 'TCPIP0::localhost::6501::SOCKET')

            print("✅ Auto-connected to Nanonis.")

            # Note: Channel combo boxes will be populated after initUI is called

        except Exception as e:
            print("❌ Failed to auto-connect to Nanonis:", e)
            self.nanonis = None

    def connect_to_scanner(self):
        """Connect to Attocube when scanner button is pressed"""
        if self.attocube is not None:
            print("✅ Already connected to Attocube.")
            return

        try:
            self.connect_to_attocube()

            if self.attocube is not None:
                self.scanner_connection_btn.setText("Connected")
                self.scanner_ind.setChecked(True)
                self.scanner_ind.changeColor("green")
                print("✅ Connected to Attocube.")
            else:
                self.scanner_connection_btn.setText("Failed")
                self.scanner_ind.setChecked(True)
                self.scanner_ind.changeColor("red")
                print("❌ Failed to connect to Attocube.")

        except Exception as e:
            print("❌ Failed to connect to Attocube:", e)
            self.attocube = None
            self.scanner_connection_btn.setText("Failed")
            self.scanner_ind.setChecked(True)
            self.scanner_ind.changeColor("red")

    def update_position_labels(self):
        if not self.nanonis:
            # Show "Not Connected" when Nanonis is not available
            self.X1_num_lb.setText("Not Connected")
            self.Y1_num_lb.setText("Not Connected")
            self.Z1_num_lb.setText("Not Connected")
            self.Z_controller_position_lb.setText("Not Connected")
            return

        try:
            # Get the currently selected encoder axis
            encoder_axis = self.encoder_axis_cb.currentText() if hasattr(self, 'encoder_axis_cb') else "Z"

            # Get current Z, X, Y positions in meters from Nanonis
            z_pos = self.nanonis.z_pos_get()
            x_pos, y_pos = self.nanonis.XY_pos_get()

            # Get scanner voltage signals (in V, convert to mV for display)
            try:
                # Try to get scanner X, Y, Z voltage signals from Nanonis
                if hasattr(self.nanonis, 'signals'):
                    # Look for scanner voltage signals
                    x_voltage = 0.0  # Default value
                    y_voltage = 0.0
                    z_voltage = 0.0

                    # Debug: Print available signals (first time only)
                    if not hasattr(self, '_printed_signals'):
                        print("🔍 Available Nanonis signals:")
                        for i, signal_name in enumerate(self.nanonis.signals):
                            print(f"  [{i}] {signal_name}")
                        self._printed_signals = True

                    # Get encoder value from "LI Demod 1 R (V)" channel
                    encoder_value = 0.0
                    if "LI Demod 1 R (V)" in self.nanonis.signals:
                        index = self.nanonis.signals.index("LI Demod 1 R (V)")
                        encoder_value = self.nanonis.sig_val_get_by_index(index)

                    # Only update the box corresponding to the selected encoder axis
                    # Other boxes keep their last displayed values (don't overwrite them)
                    if encoder_axis == "X":
                        self.X1_num_lb.setText(f"{encoder_value * 1000:.3f} mV")
                        # Y1 and Z1 keep their previous values - don't update
                    elif encoder_axis == "Y":
                        self.Y1_num_lb.setText(f"{encoder_value * 1000:.3f} mV")
                        # X1 and Z1 keep their previous values - don't update
                    elif encoder_axis == "Z":
                        self.Z1_num_lb.setText(f"{encoder_value * 1000:.3f} mV")
                        # X1 and Y1 keep their previous values - don't update

                else:
                    # Fallback if signals not available
                    self.X1_num_lb.setText("-- mV")
                    self.Y1_num_lb.setText("-- mV")
                    self.Z1_num_lb.setText("-- mV")

            except Exception as voltage_error:
                print(f"❌ Failed to get scanner voltages: {voltage_error}")
                self.X1_num_lb.setText("-- mV")
                self.Y1_num_lb.setText("-- mV")
                self.Z1_num_lb.setText("-- mV")

            # Update positioner position displays (bottom row - X2, Y2, Z2)
            # These should show current positioner positions, not encoder-axis dependent
            try:
                # Get positioner positions from attocube if available
                if hasattr(self, 'attocube') and self.attocube is not None:
                    # Try to get actual positioner positions
                    try:
                        # These might be different method names - adjust as needed
                        if hasattr(self.attocube, 'get_position'):
                            x_pos_um = self.attocube.get_position(4) * 1e6  # Axis 4 = X, convert to μm
                            y_pos_um = self.attocube.get_position(5) * 1e6  # Axis 5 = Y, convert to μm
                            z_pos_um = self.attocube.get_position(6) * 1e6  # Axis 6 = Z, convert to μm
                        elif hasattr(self.attocube, 'PosGet'):
                            positions = self.attocube.PosGet()  # Might return [x, y, z]
                            if len(positions) >= 3:
                                x_pos_um = positions[0] * 1e6
                                y_pos_um = positions[1] * 1e6
                                z_pos_um = positions[2] * 1e6
                            else:
                                raise Exception("PosGet returned insufficient data")
                        else:
                            # Fallback - use scanner positions as approximation
                            x_pos_um = x_pos * 1e6
                            y_pos_um = y_pos * 1e6
                            z_pos_um = z_pos * 1e6

                        # Display positioner positions (bottom row)
                        self.X2_num_lb.setText(f"{x_pos_um:.3f} μm")
                        self.Y2_num_lb.setText(f"{y_pos_um:.3f} μm")
                        self.Z2_num_lb.setText(f"{z_pos_um:.3f} μm")

                    except Exception as pos_error:
                        print(f"❌ Failed to get positioner positions: {pos_error}")
                        # Fallback to scanner positions
                        self.X2_num_lb.setText(f"{x_pos * 1e6:.3f} μm")
                        self.Y2_num_lb.setText(f"{y_pos * 1e6:.3f} μm")
                        self.Z2_num_lb.setText(f"{z_pos * 1e6:.3f} μm")
                else:
                    # No attocube connection - use scanner positions
                    self.X2_num_lb.setText(f"{x_pos * 1e6:.3f} μm")
                    self.Y2_num_lb.setText(f"{y_pos * 1e6:.3f} μm")
                    self.Z2_num_lb.setText(f"{z_pos * 1e6:.3f} μm")

            except Exception as positioner_error:
                print(f"❌ Failed to update positioner displays: {positioner_error}")
                self.X2_num_lb.setText("Error")
                self.Y2_num_lb.setText("Error")
                self.Z2_num_lb.setText("Error")

            # Always update Z controller position display in nanometers
            self.Z_controller_position_lb.setText(f"{z_pos * 1e9:.1f} nm")

        except Exception as e:
            print("❌ Failed to update positions:", e)
            # Show error status
            self.X1_num_lb.setText("Error")
            self.Y1_num_lb.setText("Error")
            self.Z1_num_lb.setText("Error")
            self.Z_controller_position_lb.setText("Error")

    def withdraw_tip(self):
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        try:
            # Call z_withdraw function from Nanonis
            self.nanonis.z_withdraw()
            print("✅ Tip withdrawn using z_withdraw function")
        except Exception as e:
            print("❌ Failed to withdraw tip:", e)

    # def approach_lift(self):
    #     if not self.nanonis:
    #         print("❌ Not connected to Nanonis.")
    #         return
    #
    #     try:
    #         # --- Step 1: Turn on Z controller (tip will start moving toward Z low limit) ---
    #         print("🔽 Starting approach: Turning on Z controller")
    #         self.nanonis.z_controller_OnOffSet(1)  # 1 = on
    #
    #         # Update the tip lift and delay settings to nanonis
    #         tip_lift_um = self.tipLift_sb.value()
    #         delay_ms = self.delay_sb.value()
    #
    #         # Set tip lift in nanonis (convert μm to m)
    #         self.nanonis.z_controller_TipLiftSet(tip_lift_um * 1e-6)
    #         print(f"✅ Set tip lift to {tip_lift_um:.2f} μm")
    #
    #         # Set switch off delay in nanonis (convert ms to s)
    #         self.nanonis.z_controller_SwitchOffDelaySet(delay_ms / 1000)
    #         print(f"✅ Set switch off delay to {delay_ms:.0f} ms")
    #
    #         z_low_limit_um = self.Z_lowLimit_sb.value()
    #         print(f"⏱ Z controller active - tip approaching Z low limit {z_low_limit_um:.2f} μm...")
    #         print("⏱ Waiting for tip to reach low limit...")
    #
    #         # Wait for approach to complete by monitoring Z position vs Z low limit
    #         z_low_limit_m = z_low_limit_um * 1e-6  # Convert μm to m for comparison
    #         approach_timeout = 30.0  # Maximum wait time in seconds
    #         start_time = time.time()
    #
    #         while True:
    #             try:
    #                 current_z_pos = self.nanonis.z_pos_get()  # Get current Z position in meters
    #
    #                 # Check if we've reached the low limit (within small tolerance)
    #                 tolerance = 0.1e-9  # 0.1 nm tolerance
    #                 if abs(current_z_pos - z_low_limit_m) <= tolerance:
    #                     print(f"✅ Tip reached Z low limit: {current_z_pos*1e6:.3f} μm (target: {z_low_limit_um:.3f} μm)")
    #                     break
    #
    #                 # Check for timeout
    #                 if time.time() - start_time > approach_timeout:
    #                     print(f"⚠️ Approach timeout after {approach_timeout}s - current Z: {current_z_pos*1e6:.3f} μm, target: {z_low_limit_um:.3f} μm")
    #                     break
    #
    #                 # Small delay between checks
    #                 time.sleep(0.1)  # Check every 100ms
    #
    #             except Exception as pos_error:
    #                 print(f"❌ Error reading Z position during approach: {pos_error}")
    #                 time.sleep(0.5)  # Wait longer on error
    #                 continue
    #
    #         # --- Step 2: Turn off Z controller (nanonis will automatically apply tip lift and delay) ---
    #         print("⬆️ Approach complete: Turning off Z controller")
    #         print("✅ Nanonis will automatically apply tip lift and delay")
    #         self.nanonis.z_controller_OnOffSet(0)  # 0 = off
    #
    #         print("✅ Approach & Lift completed with automatic tip lift and delay.")
    #
    #     except Exception as e:
    #         print("❌ Failed during App & Lift:", e)
    def approach_lift(self):
        self.nanonis.autoApproach_OnOffSet(True)
        time.sleep(1)
        self.nanonis.autoApproach_OnOffSet(False)

    def update_tip_lift_to_nanonis(self):
        """Update tip lift value to nanonis immediately when value changes"""
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        try:
            tip_lift_um = self.tipLift_sb.value()
            # Convert μm to m for nanonis
            self.nanonis.z_controller_TipLiftSet(tip_lift_um * 1e-6)
            print(f"✅ Updated tip lift to {tip_lift_um:.2f} μm")
        except Exception as e:
            print(f"❌ Failed to update tip lift: {e}")

    def update_delay_to_nanonis(self):
        """Update delay value to nanonis immediately when value changes"""
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        try:
            delay_ms = self.delay_sb.value()
            # Convert ms to s for nanonis
            self.nanonis.z_controller_SwitchOffDelaySet(delay_ms / 1000)
            print(f"✅ Updated delay to {delay_ms:.0f} ms")
        except Exception as e:
            print(f"❌ Failed to update delay: {e}")

    def set_current_z_as_low_limit(self):
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        try:
            current_z = self.nanonis.z_pos_get()  # in meters
            self.Z_lowLimit_sb.setValue(current_z * 1e6)  # convert to μm
            print(f"✅ Set Z low limit to {current_z * 1e6:.2f} μm")
        except Exception as e:
            print("❌ Failed to set Z low limit:", e)

    def toggle_z_controller(self):
        """Toggle Z controller on/off"""
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        try:
            if not self.z_controller_active:
                # Activate Z controller
                self.nanonis.z_controller_OnOffSet(1)  # 1 = on
                print("✅ Z Controller activated.")
                self.Z_controller_btn.setText("Off")
                self.Z_controller_ind.setChecked(True)
                self.Z_controller_ind.changeColor("green")
                self.z_controller_active = True
            else:
                # Deactivate Z controller
                self.nanonis.z_controller_OnOffSet(0)  # 0 = off
                print("✅ Z Controller deactivated.")
                self.Z_controller_btn.setText("On")
                self.Z_controller_ind.setChecked(False)
                self.Z_controller_ind.changeColor("orange")
                self.z_controller_active = False

        except Exception as e:
            print("❌ Failed to toggle Z Controller:", e)
            self.Z_controller_btn.setText("Failed")
            self.Z_controller_ind.setChecked(True)
            self.Z_controller_ind.changeColor("red")

    def approach_withdraw(self):
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        try:
            # --- Step 1: Turn on Z controller to approach ---
            print("🔽 Starting approach: Turning on Z controller")
            self.nanonis.z_controller_OnOffSet(1)  # 1 = on

            # Wait for tip to reach Z low limit
            z_low_limit_um = self.Z_lowLimit_sb.value()        # [um]
            print(f"⏱ Waiting for tip to reach Z low limit {z_low_limit_um:.2f} μm...")

            # Wait for approach to complete by monitoring Z position vs Z low limit
            z_low_limit_m = z_low_limit_um * 1e-6  # Convert μm to m for comparison
            approach_timeout = 30.0  # Maximum wait time in seconds
            start_time = time.time()

            while True:
                try:
                    current_z_pos = self.nanonis.z_pos_get()  # Get current Z position in meters

                    # Check if we've reached the low limit (within small tolerance)
                    tolerance = 0.1e-9  # 0.1 nm tolerance
                    if abs(current_z_pos - z_low_limit_m) <= tolerance:
                        print(f"✅ Tip reached Z low limit: {current_z_pos*1e6:.3f} μm (target: {z_low_limit_um:.3f} μm)")
                        break

                    # Check for timeout
                    if time.time() - start_time > approach_timeout:
                        print(f"⚠️ Approach timeout after {approach_timeout}s - current Z: {current_z_pos*1e6:.3f} μm, target: {z_low_limit_um:.3f} μm")
                        break

                    # Small delay between checks
                    time.sleep(0.1)  # Check every 100ms

                except Exception as pos_error:
                    print(f"❌ Error reading Z position during approach: {pos_error}")
                    time.sleep(0.5)  # Wait longer on error
                    continue

            # --- Step 2: Turn off Z controller and withdraw ---
            print("⬆️ Approach complete: Turning off Z controller and withdrawing")
            self.nanonis.z_controller_OnOffSet(0)  # 0 = off

            # Withdraw tip using z_withdraw function
            self.nanonis.z_withdraw()

            print("✅ App & Withdraw completed.")

        except Exception as e:
            print("❌ Failed during App & Withdraw:", e)

    def set_full_range(self):
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        try:
            # Disable limits to use default full range
            self.nanonis.z_controller_LimitsEnabledSet(1)  # 0 = disabled
            print(self.z_controller_LimitsEnabledGet())
            print("✅ Z controller limits disabled - using full range")

            # Set the standard full range: -3 to +3 μm
            # Always use the standard range regardless of what Nanonis returns
            self.Z_lowLimit_sb.setValue(-3.0)  # Low limit: -3.0 μm
            print("✅ Full Range set: -3.0 μm to +3.0 μm")

            # Optional: Try to get the actual limits for debugging
            try:
                limits = self.nanonis.z_controller_LimitsGet()  # Returns [high_limit, low_limit]
                if isinstance(limits, list) and len(limits) >= 2:
                    z_high_limit = limits[0]  # in meters
                    z_low_limit = limits[1]   # in meters
                    print(f"🔍 Nanonis reported limits: Low = {z_low_limit * 1e6:.2f} μm, High = {z_high_limit * 1e6:.2f} μm")
            except Exception as limit_error:
                print(f"⚠️ Could not read Nanonis limits: {limit_error}")

        except Exception as e:
            print(f"❌ Failed to set full range: {e}")

    def update_z_low_limit_to_nanonis(self):
        """Update Z low limit to nanonis when manually entered"""
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        try:
            z_low_limit_um = self.Z_lowLimit_sb.value()  # [μm]
            z_low_limit_m = z_low_limit_um * 1e-6  # Convert to meters

            # Enable limits first
            self.nanonis.z_controller_LimitsEnabledSet(1)  # 1 = enabled
            print("✅ Z controller limits enabled")

            # Get current limits to preserve high limit
            try:
                limits = self.nanonis.z_controller_LimitsGet()  # Returns [high_limit, low_limit]
                if isinstance(limits, list) and len(limits) >= 2:
                    z_high_limit_m = limits[0]  # Keep current high limit
                else:
                    z_high_limit_m = 3.0e-6  # Default high limit if can't read
            except Exception as get_error:
                print(f"⚠️ Failed to get current limits: {get_error}")
                z_high_limit_m = 3.0e-6  # Default high limit

            # Set both limits (high limit stays the same, low limit updated)
            self.nanonis.z_controller_LimitsSet(z_high_limit_m, z_low_limit_m)
            print(f"✅ Set Z low limit to {z_low_limit_um:.2f} μm (high limit: {z_high_limit_m * 1e6:.2f} μm)")

        except Exception as e:
            print(f"❌ Failed to update Z low limit: {e}")

    def set_attocube_offset(self):
        if not hasattr(self, 'attocube') or self.attocube is None:
            print("❌ Not connected to Attocube.")
            print("💡 You can still use other features without Attocube connection.")
            return

        try:
            voltage = self.Z_voltageLimit_sb.value()  # Get voltage from input box
            axis_number = 3  # Z scanner is axis 3

            # Set the mode correctly for offset operation
            try:
                # First set the mode to "off" (offset mode) using the correct string value
                if hasattr(self.attocube, 'set_mode'):
                    self.attocube.set_mode(axis_number, "off")  # "off" = offset mode
                    print(f"✅ Set axis {axis_number} to offset mode using set_mode")
                elif hasattr(self.attocube, 'set_offset_mode'):
                    self.attocube.set_offset_mode(axis_number, True)  # Enable offset mode
                    print(f"✅ Set axis {axis_number} to offset mode using set_offset_mode")
                elif hasattr(self.attocube, 'enable_offset'):
                    self.attocube.enable_offset(axis_number)
                    print(f"✅ Enabled offset for axis {axis_number} using enable_offset")
                else:
                    print(f"⚠️ Offset mode method not found, proceeding with voltage set")
            except Exception as offset_error:
                print(f"⚠️ Failed to set offset mode: {offset_error}")

            # Set the offset voltage with improved error handling
            success = self.set_z_voltage_with_limit(axis_number, voltage)
            if success:
                print(f"✅ Z scanner offset voltage set to {voltage:.2f} V")
            else:
                print(f"❌ Failed to set Z scanner offset voltage to {voltage:.2f} V")

        except Exception as e:
            print("❌ Failed to set Attocube offset:", e)


    def set_z_voltage_with_limit(self, axis_number: int, voltage: float):
        limit = self.Z_voltageLimit_sb.value()  # Get limit from input box

        if voltage < 0 or voltage > limit:
            print(f"❌ Voltage {voltage:.2f} V exceeds Z limit ({limit:.2f} V)")
            return False

        try:
            # Use pylablib method - according to docs, it's set_offset()
            self.attocube.set_offset(axis_number, voltage)
            print(f"✅ Set Attocube offset voltage to {voltage:.2f} V")
            return True
        except AttributeError:
            # If set_offset doesn't exist, try alternative method names
            try:
                self.attocube.set_offset_voltage(axis_number, voltage)
                print(f"✅ Set Attocube offset voltage to {voltage:.2f} V")
                return True
            except AttributeError:
                print(f"❌ Could not find offset voltage setting method")
                return False
        except Exception as e:
            print(f"❌ Failed to set Attocube offset voltage:", e)
            return False

    def toggle_attocube_connection(self):
        """Toggle Attocube connection on/off"""
        if self.attocube is None:
            # Connect to Attocube
            self.connect_to_attocube()
            if self.attocube is not None:
                self.scanner_connection_btn.setText("Off")
                self.scanner_ind.setChecked(True)
                self.scanner_ind.changeColor("green")
        else:
            # Disconnect from Attocube
            self.disconnect_attocube()

    def disconnect_attocube(self):
        """Disconnect from Attocube"""
        try:
            if self.attocube is not None:
                self.attocube.close()
                self.attocube = None
                self.scanner_connection_btn.setText("On")
                self.scanner_ind.setChecked(False)
                self.scanner_ind.changeColor("orange")
                print("✅ Disconnected from Attocube")
        except Exception as e:
            print(f"❌ Failed to disconnect from Attocube: {e}")

    def connect_to_attocube(self):
        """Connect to Attocube using pylablib"""
        if Attocube is None:
            print("❌ Pylablib not available for Attocube connection")
            self.attocube = None
            return
        self._connect_to_attocube_pylablib()

    def _connect_to_attocube_pylablib(self):
        """Connect to Attocube using pylablib"""
        try:
            import pyvisa

            # Connect directly to COM6 since we know that's where the attocube is
            port = "COM6"

            try:
                print(f"Attempting pylablib connection to: {port}")

                # Use pylablib's ANC300 class as per documentation
                # Add timeout parameter to handle slow connections
                self.attocube = Attocube.ANC300(port)

                # Test the connection - according to pylablib docs, update_available_axes() is called automatically
                print(f"✅ Connected to Attocube via {port}")

                # According to pylablib documentation, we can check available axes
                # The method might be different in this version
                try:
                    # Try the documented method first
                    available_axes = self.attocube.update_available_axes()
                    print(f"Available axes: {available_axes}")
                except AttributeError:
                    # If that fails, try to get axis information differently
                    try:
                        # Check if we can get axis info by trying to access axis 1
                        axis_info = self.attocube.get_axis_serial(1)
                        print(f"Axis 1 info: {axis_info}")
                        available_axes = [1]  # Assume axis 1 is available
                    except:
                        print("⚠️ Could not determine available axes, but connection successful")
                        available_axes = "Unknown"

                return

            except Exception as e:
                error_msg = str(e)
                if "PermissionError" in error_msg or "Access is denied" in error_msg:
                    print(f"⚠️ {port} is in use by another application")
                elif "timeout" in error_msg.lower():
                    print(f"⚠️ {port} timeout - device may not be responding")
                else:
                    print(f"❌ Failed to connect to {port}: {e}")

                print("❌ Failed to connect to Attocube on COM6")
                self.attocube = None

        except Exception as e:
            print(f"❌ Pylablib attocube connection failed: {e}")
            self.attocube = None




    # 222 Z CONTROLLER FUNCTIONS END

    # 222 XYZ POSITIONER FUNCTIONS START

    def move_positioner(self):
        if not hasattr(self, 'attocube') or self.attocube is None:
            print("❌ Not connected to Attocube.")
            return

        try:
            # === 1. Get axis information ===
            axis_map = {"X": 4, "Y": 5, "Z": 6}
            axis = self.axis_cb.currentText()
            axis_number = axis_map.get(axis, 4)

            # === 2. Set mode to STP (step mode) for movement ===
            print(f"🔧 Attempting to set axis {axis_number} to STP mode...")
            mode_set_success = False

            # Try different method names with "stp" mode value
            try:
                if hasattr(self.attocube, 'set_mode'):
                    self.attocube.set_mode(axis_number, "stp")
                    print(f"✅ Set axis {axis_number} to STP mode using set_mode")
                    mode_set_success = True
                elif hasattr(self.attocube, 'set_axis_mode'):
                    self.attocube.set_axis_mode(axis_number, "stp")
                    print(f"✅ Set axis {axis_number} to STP mode using set_axis_mode")
                    mode_set_success = True
                elif hasattr(self.attocube, 'enable_axis'):
                    # Try enabling the axis first
                    self.attocube.enable_axis(axis_number)
                    print(f"✅ Enabled axis {axis_number} using enable_axis")
                    mode_set_success = True
                else:
                    print(f"⚠️ No suitable mode setting method found")
                    available_methods = [m for m in dir(self.attocube) if 'mode' in m.lower() or 'enable' in m.lower()]
                    print(f"💡 Available mode/enable methods: {available_methods}")

            except Exception as mode_error:
                print(f"❌ Failed to set STP mode: {mode_error}")
                available_methods = [m for m in dir(self.attocube) if 'mode' in m.lower() or 'enable' in m.lower()]
                print(f"💡 Available mode/enable methods: {available_methods}")

            if not mode_set_success:
                print(f"⚠️ Could not set STP mode - attempting movement anyway")
                print(f"🔍 Current axis methods: {[m for m in dir(self.attocube) if 'axis' in m.lower()]}")

            # === 3. Set Frequency and Voltage ===
            freq = self.frequency_sb.value()
            volt = self.voltage_sb.value()

            # Set frequency and voltage for the selected axis with better error handling
            try:
                self.attocube.set_frequency(axis_number, freq)
                print(f"✅ Set frequency to {freq:.1f} Hz for axis {axis_number}")
            except Exception as freq_error:
                print(f"❌ Failed to set frequency: {freq_error}")
                print(f"💡 Available methods: {[m for m in dir(self.attocube) if 'freq' in m.lower()]}")

            try:
                self.attocube.set_voltage(axis_number, volt)
                print(f"✅ Set voltage to {volt:.2f} V for axis {axis_number}")
            except Exception as volt_error:
                print(f"❌ Failed to set voltage: {volt_error}")
                print(f"💡 Available methods: {[m for m in dir(self.attocube) if 'volt' in m.lower()]}")

            print(f"⚙️ Frequency: {freq:.1f} Hz, Voltage: {volt:.2f} V for axis {axis_number}")

            # === 4. Determine direction and steps ===
            direction = self.direction_btn.text()
            steps = self.steps_sb.value()

            # Convert direction to positive/negative steps
            if direction == "Down":
                steps = -steps  # Negative steps for downward movement

            # === 5. Move using attocube move_by function ===
            try:
                self.attocube.move_by(axis_number, steps)
                print(f"✅ Moving {axis} by {steps} steps")

                # === 6. Wait for movement to complete (optional) ===
                # You might want to add a small delay or check for completion
                self.attocube.wait_move(axis_number)
                time.sleep(0.1)  # Brief pause to ensure movement starts

            except Exception as move_error:
                print(f"❌ Failed to move: {move_error}")
                print(f"💡 Available methods: {[m for m in dir(self.attocube) if 'move' in m.lower()]}")

            # === 7. Set mode back to GND (ground) after movement ===
            print(f"🔧 Setting axis {axis_number} back to GND mode...")
            try:
                if hasattr(self.attocube, 'set_mode'):
                    self.attocube.set_mode(axis_number, "gnd")
                    print(f"✅ Set axis {axis_number} back to GND mode")
                elif hasattr(self.attocube, 'set_axis_mode'):
                    self.attocube.set_axis_mode(axis_number, "gnd")
                    print(f"✅ Set axis {axis_number} back to GND mode using set_axis_mode")
                elif hasattr(self.attocube, 'disable_axis'):
                    # Alternative: disable the axis
                    self.attocube.disable_axis(axis_number)
                    print(f"✅ Disabled axis {axis_number} using disable_axis")
                else:
                    print(f"⚠️ No suitable mode setting method available for grounding")

                # Update the GND label to reflect the new state
                self.update_gnd_label(axis_number)

            except Exception as gnd_error:
                print(f"❌ Failed to set GND mode: {gnd_error}")
                print(f"💡 Available methods: {[m for m in dir(self.attocube) if 'mode' in m.lower() or 'disable' in m.lower()]}")

        except Exception as e:
            print("❌ Failed to move positioner:", e)
            # Try to set back to GND mode even if movement failed
            try:
                axis_map = {"X": 4, "Y": 5, "Z": 6}
                axis = self.axis_cb.currentText()
                axis_number = axis_map.get(axis, 4)
                if hasattr(self.attocube, 'set_mode'):
                    self.attocube.set_mode(axis_number, "gnd")  # "gnd" = GND mode
                    print(f"✅ Set axis {axis_number} back to GND mode after error")
                    self.update_gnd_label(axis_number)
            except Exception as cleanup_error:
                print(f"❌ Failed to cleanup mode after error: {cleanup_error}")

    def stop_positioner(self):
        if not hasattr(self, 'attocube') or self.attocube is None:
            print("❌ Not connected to Attocube.")
            return

        try:
            # Stop all positioner axes (4, 5, 6)
            for axis in [4, 5, 6]:
                self.attocube.stop(axis)
            print("⛔ Movement stopped.")
        except Exception as e:
            print("❌ Failed to stop movement:", e)

    def on_axis_changed(self):
        """Handle axis selection change - update frequency/voltage and GND status"""
        if not hasattr(self, 'attocube') or self.attocube is None:
            print("❌ Not connected to Attocube")
            return

        try:
            # Get current axis
            axis_map = {"X": 4, "Y": 5, "Z": 6}
            axis = self.axis_cb.currentText()
            axis_number = axis_map.get(axis, 4)

            # Read initial frequency and voltage from attocube with better error handling
            # Set axis-specific default values
            axis_defaults = {
                "X": {"freq": 1000.0, "volt": 50.0},
                "Y": {"freq": 1000.0, "volt": 50.0},
                "Z": {"freq": 50.0, "volt": 50.0}   # Z axis should be 50Hz
            }

            try:
                freq = self.attocube.get_frequency(axis_number)
                print(f"✅ Read frequency: {freq:.1f} Hz for axis {axis_number}")
            except Exception as freq_error:
                print(f"❌ Failed to read frequency: {freq_error}")
                print(f"💡 Available methods: {[m for m in dir(self.attocube) if 'freq' in m.lower()]}")
                freq = axis_defaults[axis]["freq"]  # Use axis-specific default

            try:
                volt = self.attocube.get_voltage(axis_number)
                print(f"✅ Read voltage: {volt:.2f} V for axis {axis_number}")
            except Exception as volt_error:
                print(f"❌ Failed to read voltage: {volt_error}")
                print(f"💡 Available methods: {[m for m in dir(self.attocube) if 'volt' in m.lower()]}")
                volt = axis_defaults[axis]["volt"]  # Use axis-specific default

            # Update the spinboxes
            self.frequency_sb.setValue(freq)
            self.voltage_sb.setValue(volt)

            # Update GND label based on axis status
            self.update_gnd_label(axis_number)

            print(f"✅ Updated to {axis} axis - Freq: {freq:.1f} Hz, Volt: {volt:.2f} V")

        except Exception as e:
            print(f"❌ Failed to update axis settings: {e}")

    def update_gnd_label(self, axis_number):
        """Update GND label to show grounding status or mode of selected axis"""
        try:
            # Step 1: Check if axis is enabled (not grounded) using is_enabled
            if hasattr(self.attocube, 'is_enabled'):
                is_enabled = self.attocube.is_enabled(axis_number)
                print(f"✅ Used is_enabled: {is_enabled} for axis {axis_number}")

                if not is_enabled:
                    # Axis is grounded/disabled
                    self.gnd_lb.setText("GND")
                    print(f"🔌 Axis {axis_number} is grounded")
                else:
                    # Axis is enabled - get the mode and display it
                    if hasattr(self.attocube, 'get_mode'):
                        try:
                            mode = self.attocube.get_mode(axis_number)
                            print(f"✅ Used get_mode: {mode} for axis {axis_number}")

                            # Display the mode (could be string or number)
                            if isinstance(mode, str):
                                self.gnd_lb.setText(mode.upper())
                            else:
                                # If mode is a number, convert to meaningful text
                                mode_map = {0: "GND", 1: "STP", 2: "ROT", 3: "CNT"}
                                mode_text = mode_map.get(mode, f"MODE{mode}")
                                self.gnd_lb.setText(mode_text)
                            print(f"🎛️ Axis {axis_number} mode: {mode}")
                        except Exception as mode_error:
                            print(f"❌ Failed to get mode: {mode_error}")
                            self.gnd_lb.setText("ENABLED")
                    else:
                        print(f"⚠️ get_mode method not available")
                        self.gnd_lb.setText("ENABLED")
            else:
                print(f"⚠️ is_enabled method not found")
                # Fallback to old logic if is_enabled is not available
                available_methods = [m for m in dir(self.attocube) if ('enable' in m.lower() or 'mode' in m.lower())]
                print(f"💡 Available enable/mode methods: {available_methods}")
                self.gnd_lb.setText("Unknown")

        except Exception as e:
            print(f"❌ Failed to update GND label: {e}")
            print(f"💡 Available methods: {[m for m in dir(self.attocube) if ('enable' in m.lower() or 'mode' in m.lower())]}")
            self.gnd_lb.setText("Error")

    def gnd_all_axes(self):
        if not hasattr(self, 'attocube') or self.attocube is None:
            print("❌ Not connected to Attocube.")
            return

        try:
            # Ground axes 4, 5, 6 (XYZ positioner axes)
            for axis in [4, 5, 6]:
                self.attocube.disable_axis(axis)
            self.gnd_lb.setText("GND")
            print("✅ All XYZ positioner axes grounded.")
        except Exception as e:
            print("❌ Failed to ground all axes:", e)

    def safe_tip_changed(self, state):
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return

        # State: 0=unchecked, 2=checked
        if state == Qt.Checked:
            try:
                self.nanonis.safeTip_OnOffSet(1)  # 1 = on
                print("✅ Safe Tip enabled.")
            except Exception as e:
                print("❌ Failed to enable Safe Tip:", e)
        else:
            try:
                self.nanonis.safeTip_OnOffSet(2)  # 2 = off
                print("✅ Safe Tip disabled.")
            except Exception as e:
                print("❌ Failed to disable Safe Tip:", e)



    def handle_auto_approach_checkbox(self, state):
        if state == Qt.Checked:
            print("🔄 Auto Approach enabled")
            self.start_auto_approach_loop()
        else:
            print("⏹️ Auto Approach disabled")
            self.stop_auto_approach_loop()

    def start_auto_approach_loop(self):
        if hasattr(self, 'auto_approach_timer') and self.auto_approach_timer.isActive():
            return  # Already running
        self.auto_approach_timer = QTimer(self)
        self.auto_approach_timer.timeout.connect(self.auto_approach_check_and_move)
        self.auto_approach_timer.start(100)  # 100 ms

    def stop_auto_approach_loop(self):
        if hasattr(self, 'auto_approach_timer'):
            self.auto_approach_timer.stop()

    def auto_approach_check_and_move(self):
        if not self.nanonis:
            print("❌ Not connected to Nanonis.")
            return
        try:
            _, line_val = self.nanonis.TTLValGet(0, 3)  # Port A=0, Line 3
            print(f"TTL line 3 value: {line_val}")
            if line_val == 1:
                # Move positioner 1 step down in Z
                print("🔽 TTL high: moving Z positioner")
                axis = "Z"
                self.axis_cb.setCurrentText(axis)
                self.direction_btn.setText("Down")
                self.steps_sb.setValue(1)
                self.move_positioner()
            else:
                print("TTL line low: not moving")
        except Exception as e:
            print(f"❌ Auto approach check failed: {e}")

    def update_frequency_to_attocube(self):
        """Update frequency to attocube immediately when value changes"""
        if not hasattr(self, 'attocube') or self.attocube is None:
            print("❌ Not connected to Attocube.")
            return

        try:
            freq = self.frequency_sb.value()
            axis_map = {"X": 4, "Y": 5, "Z": 6}
            axis = self.axis_cb.currentText()
            axis_number = axis_map.get(axis, 4)

            self.attocube.set_frequency(axis_number, freq)
            print(f"✅ Updated frequency to {freq:.1f} Hz for axis {axis}")
        except Exception as e:
            print(f"❌ Failed to update frequency: {e}")

    def update_voltage_to_attocube(self):
        """Update voltage to attocube immediately when value changes"""
        if not hasattr(self, 'attocube') or self.attocube is None:
            print("❌ Not connected to Attocube.")
            return

        try:
            volt = self.voltage_sb.value()
            axis_map = {"X": 4, "Y": 5, "Z": 6}
            axis = self.axis_cb.currentText()
            axis_number = axis_map.get(axis, 4)

            self.attocube.set_voltage(axis_number, volt)
            print(f"✅ Updated voltage to {volt:.2f} V for axis {axis}")
        except Exception as e:
            print(f"❌ Failed to update voltage: {e}")

    # 222 XYZ POSITIONER FUNCTIONS END

    # 222 CENTER PLOT FUNCTIONS START
    def update_center_plots(self):
        # This function is now deprecated in favor of per-plot update functions
        pass

    def format_value_with_units(self, value, channel_name):
        """Format value with appropriate units and significant figures based on channel type"""
        if value is None:
            return "Current Value: --"

        # Determine units and precision based on channel name
        if "MIM" in channel_name:
            if abs(value) >= 1e-3:
                return f"Current Value: {value:.6f} V"
            elif abs(value) >= 1e-6:
                return f"Current Value: {value*1e6:.3f} μV"
            else:
                return f"Current Value: {value*1e9:.3f} nV"
        elif "Position" in channel_name or "X" in channel_name or "Y" in channel_name or "Z" in channel_name:
            if abs(value) >= 1e-3:
                return f"Current Value: {value*1e6:.3f} μm"
            else:
                return f"Current Value: {value*1e9:.3f} nm"
        elif "Current" in channel_name or ("I" in channel_name and "LI" not in channel_name):
            if abs(value) >= 1e-6:
                return f"Current Value: {value*1e6:.3f} μA"
            else:
                return f"Current Value: {value*1e9:.3f} nA"
        elif "Voltage" in channel_name or "V" in channel_name:
            if abs(value) >= 1e-3:
                return f"Current Value: {value:.6f} V"
            elif abs(value) >= 1e-6:
                return f"Current Value: {value*1e6:.3f} μV"
            else:
                return f"Current Value: {value*1e9:.3f} nV"
        elif "Temperature" in channel_name or "T" in channel_name:
            return f"Current Value: {value:.3f} K"
        elif "Frequency" in channel_name or "Freq" in channel_name:
            if abs(value) >= 1e6:
                return f"Current Value: {value/1e6:.3f} MHz"
            elif abs(value) >= 1e3:
                return f"Current Value: {value/1e3:.3f} kHz"
            else:
                return f"Current Value: {value:.3f} Hz"
        else:
            # Default formatting for unknown channels
            if abs(value) >= 1e-3:
                return f"Current Value: {value:.6f}"
            elif abs(value) >= 1e-6:
                return f"Current Value: {value*1e6:.3f} μ"
            else:
                return f"Current Value: {value*1e9:.3f} n"

    def get_axis_units(self, channel_name):
        """Get appropriate axis units based on channel name"""
        # If channel name already contains units in parentheses, don't add more units
        if "(" in channel_name and ")" in channel_name:
            return ""  # PyQtGraph will use the existing units in the channel name

        # Otherwise, determine units based on channel type
        if "MIM" in channel_name:
            return "V"
        elif "Position" in channel_name or "X" in channel_name or "Y" in channel_name or "Z" in channel_name:
            return "μm"
        elif "Current" in channel_name or "I" in channel_name:
            return "μA"
        elif "Voltage" in channel_name or "V" in channel_name:
            return "V"
        elif "Temperature" in channel_name or "T" in channel_name:
            return "K"
        elif "Frequency" in channel_name or "Freq" in channel_name:
            return "Hz"
        else:
            return ""

    def configure_plot_appearance(self, plot_widget, channel_name):
        """Configure plot appearance with appropriate tick formatting and grid"""
        # Set grid
        plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Configure axis appearance
        plot_widget.getAxis('left').setTextPen('k')
        plot_widget.getAxis('bottom').setTextPen('k')

        # Set appropriate tick formatting based on channel type
        if "MIM" in channel_name or "Voltage" in channel_name or "V" in channel_name:
            # For voltage channels, use scientific notation for small values
            plot_widget.getAxis('left').setStyle(showValues=True)
        elif "Position" in channel_name or "X" in channel_name or "Y" in channel_name or "Z" in channel_name:
            # For position channels, use μm units
            plot_widget.getAxis('left').setStyle(showValues=True)
        elif "Current" in channel_name or "I" in channel_name:
            # For current channels, use μA units
            plot_widget.getAxis('left').setStyle(showValues=True)
        elif "Temperature" in channel_name or "T" in channel_name:
            # For temperature channels, use K units
            plot_widget.getAxis('left').setStyle(showValues=True)
        elif "Frequency" in channel_name or "Freq" in channel_name:
            # For frequency channels, use Hz units
            plot_widget.getAxis('left').setStyle(showValues=True)
        else:
            # Default formatting
            plot_widget.getAxis('left').setStyle(showValues=True)

    def update_mim_plot(self):
        if not self.nanonis:
            return
        try:
            axis = self.plot_axis_cb.currentText()
            channel = self.mim_channel_cb.currentText()
            z = self.nanonis.z_pos_get() * 1e6
            x, y = self.nanonis.XY_pos_get()
            x *= 1e6
            y *= 1e6

            # Get the selected MIM channel value
            if channel in self.nanonis.signals:
                index = self.nanonis.signals.index(channel)
                mim_val = self.nanonis.sig_val_get_by_index(index)
            else:
                # Fallback to old method if channel not found
                mim_imag, mim_real = self.nanonis.sig_vals_get("MIM-Im (V)", "MIM-Re (V)")
                if "Im" in channel:
                    mim_val = mim_imag
                else:
                    mim_val = mim_real

            pos = {"X": x, "Y": y, "Z": z}[axis]
            if not hasattr(self, 'mainplot_data_x'):
                self.mainplot_data_x = []
                self.mainplot_data_y = []
            self.mainplot_data_x.append(pos)
            self.mainplot_data_y.append(mim_val)
            self.MIM_plot.clear()
            self.MIM_plot.plot(self.mainplot_data_x, self.mainplot_data_y, pen='b')
            self.MIM_plot.setTitle(f"{axis} vs. {channel}")
            self.MIM_plot.setLabel("bottom", f"{axis} Position", units="μm")
            self.MIM_plot.setLabel("left", channel, units="V")
            self.configure_plot_appearance(self.MIM_plot, channel)
            self.mim_plot_value_label.setText(self.format_value_with_units(mim_val, channel))
        except Exception as e:
            print("❌ Failed to update main plot:", e)

    def update_mim_plot_timed(self):
        """Time-based update for MIM plot - plots position vs MIM signal with time-based updates"""
        if not self.nanonis:
            return
        try:
            axis = self.plot_axis_cb.currentText()
            channel = self.mim_channel_cb.currentText()

            # Get position data
            z = self.nanonis.z_pos_get() * 1e6
            x, y = self.nanonis.XY_pos_get()
            x *= 1e6
            y *= 1e6

            # Get the selected MIM channel value
            if channel in self.nanonis.signals:
                index = self.nanonis.signals.index(channel)
                mim_val = self.nanonis.sig_val_get_by_index(index)
            else:
                # Fallback to old method if channel not found
                mim_imag, mim_real = self.nanonis.sig_vals_get("MIM-Im (V)", "MIM-Re (V)")
                if "Im" in channel:
                    mim_val = mim_imag
                else:
                    mim_val = mim_real

            # Get position value for the selected axis
            pos = {"X": x, "Y": y, "Z": z}[axis]

            # Calculate time since start (for buffer management, not plotting)
            t = time.time() - self.mim_plot_start_time

            # Add data to buffer
            self.mim_plot_buffer.append((t, pos, mim_val))

            # Limit buffer size
            if len(self.mim_plot_buffer) > 1000:
                del self.mim_plot_buffer[0:len(self.mim_plot_buffer)-1000]

            # Plot position vs MIM signal (X-axis = position, Y-axis = MIM signal)
            if self.mim_plot_buffer:
                times, positions, mim_values = zip(*self.mim_plot_buffer)
                self.MIM_plot.clear()
                self.MIM_plot.plot(positions, mim_values, pen='b')  # X=positions, Y=mim_values
                self.MIM_plot.setTitle(f"{axis} Position vs {channel}")
                self.MIM_plot.setLabel("bottom", f"{axis} Position", units="μm")
                self.MIM_plot.setLabel("left", channel, units=self.get_axis_units(channel))
                self.configure_plot_appearance(self.MIM_plot, channel)
                self.mim_plot_value_label.setText(self.format_value_with_units(mim_val, channel))

        except Exception as e:
            print("❌ Failed to update position-based MIM plot:", e)

    def reset_mim_plot_buffer(self):
        """Reset MIM plot buffer when axis or channel changes"""
        self.mim_plot_buffer.clear()
        self.mim_plot_start_time = time.time()
        # Clear the plot
        if hasattr(self, 'MIM_plot'):
            self.MIM_plot.clear()

    def update_mim_plot2(self):
        # Update self.mim_plot2_value_label with the current value
        self.mim_plot2_value_label.setText("Current Value: --")

    def set_encoder_axis_digital_lines(self, axis):
        """Set digital lines to control which axis is read by the encoder
        Port B, bits 0-1: 00=X, 01=Z, 10=Y
        """
        if not hasattr(self, 'nanonis') or self.nanonis is None:
            return False

        try:
            # Digital lines mapping: 00=X, 10=Z, 01=Y (flipped from original)
            axis_bits = {
                "X": 0,  # 00
                "Z": 2,  # 10 (was 01, now 10)
                "Y": 1   # 01 (was 10, now 01)
            }

            if axis not in axis_bits:
                print(f"❌ Invalid axis: {axis}")
                return False

            # Set digital lines on Port B, bits 0-1
            # Assuming the nanonis object has a method to set digital output status
            # This would need to be implemented in the nanonis.py file
            bit_value = axis_bits[axis]

            # Set bit 0 (least significant bit)
            bit0_value = bit_value & 1  # Get bit 0
            # Set bit 1 (second least significant bit)
            bit1_value = (bit_value >> 1) & 1  # Get bit 1

            # Call nanonis digital lines functions
            self.nanonis.OutStatusSet(1, 1, bit0_value)  # Port B, bit 0
            self.nanonis.OutStatusSet(1, 2, bit1_value)  # Port B, bit 1

            print(f"✅ Set encoder axis to {axis} (bits: {bit1_value}{bit0_value})")
            return True

        except Exception as e:
            print(f"❌ Failed to set encoder axis digital lines: {e}")
            return False

    def update_encoder_plot(self):
        if not hasattr(self, 'nanonis') or self.nanonis is None:
            return
        try:
            # Get the selected axis
            axis = self.encoder_axis_cb.currentText()

            # Only set digital lines if axis has changed
            if axis != self.current_encoder_axis:
                if not self.set_encoder_axis_digital_lines(axis):
                    self.encoder_value_label.setText("Current Value: --")
                    return
                self.current_encoder_axis = axis

            # Read from "LI Demod 1 R (V)" channel instead of position
            try:
                # Get the index of "LI Demod 1 R (V)" in the signals list
                if hasattr(self.nanonis, 'signals') and "LI Demod 1 R (V)" in self.nanonis.signals:
                    index = self.nanonis.signals.index("LI Demod 1 R (V)")
                    value = self.nanonis.sig_val_get_by_index(index)
                else:
                    # Fallback to position if LI Demod channel not available
                    pos = self.nanonis.PosGet()  # [x_pos, y_pos, z_pos]
                    axis_idx = self.encoder_axis_cb.currentIndex()  # 0=X, 1=Y, 2=Z
                    value = pos[axis_idx]
            except Exception as e:
                print(f"❌ Failed to read encoder value: {e}")
                self.encoder_value_label.setText("Current Value: --")
                return

        except Exception as e:
            self.encoder_value_label.setText("Current Value: --")
            return

        t = time.time() - self.encoder_start_time
        self.encoder_buffer.append((t, value))
        if len(self.encoder_buffer) > 1000:
            del self.encoder_buffer[0:len(self.encoder_buffer)-1000]
        xs, ys = zip(*self.encoder_buffer) if self.encoder_buffer else ([],[])
        self.encoder_plot.clear()
        self.encoder_plot.plot(xs, ys, pen='g')
        self.encoder_plot.setLabel("bottom", "Time", units="s")
        self.encoder_plot.setLabel("left", f"{axis} Encoder", units="V")
        self.configure_plot_appearance(self.encoder_plot, f"{axis} Encoder")
        self.encoder_value_label.setText(self.format_value_with_units(value, "LI Demod 1 R (V)"))

    def reset_encoder_buffer(self):
        self.encoder_buffer.clear()
        self.encoder_start_time = time.time()
        # Clear the plot when buffer is reset
        if hasattr(self, 'encoder_plot'):
            self.encoder_plot.clear()

    def update_nanonis_plot1(self):
        self.nanonis_plot1_value_label.setText("Current Value: --")

    def update_nanonis_plot2(self):
        self.nanonis_plot2_value_label.setText("Current Value: --")

    def update_nanonis_plot3(self):
        self.nanonis_plot3_value_label.setText("Current Value: --")

    def update_nanonis_plot4(self):
        self.nanonis_plot4_value_label.setText("Current Value: --")

    # 222 CENTER PLOT FUNCTIONS END

    def clear_plot(self, plot_widget, buffer_name):
        """Clear a plot and its associated data buffer"""
        try:
            # Clear the plot widget
            plot_widget.clear()

            # Clear the associated buffer if it exists
            if hasattr(self, buffer_name + '_x') and hasattr(self, buffer_name + '_y'):
                # For mainplot_data (has _x and _y)
                getattr(self, buffer_name + '_x').clear()
                getattr(self, buffer_name + '_y').clear()
            elif hasattr(self, buffer_name):
                # For encoder_buffer and mim_plot_buffer (single buffer)
                getattr(self, buffer_name).clear()
                # Reset start time for time-based plots
                if buffer_name == 'encoder_buffer':
                    self.encoder_start_time = time.time()
                elif buffer_name == 'mim_plot_buffer':
                    self.mim_plot_start_time = time.time()
            print(f"✅ Cleared {buffer_name} plot")
        except Exception as e:
            print(f"❌ Failed to clear plot: {e}")

    def clear_nanonis_plot(self, plot_index):
        """Clear a specific nanonis plot and its buffer"""
        try:
            if 0 <= plot_index < len(self.nanonis_plot_widgets):
                # Clear the plot widget
                self.nanonis_plot_widgets[plot_index].clear()
                # Clear the buffer
                self.nanonis_plot_buffers[plot_index].clear()
                # Reset start time
                self.nanonis_plot_start_times[plot_index] = time.time()
                print(f"✅ Cleared nanonis plot {plot_index + 1}")
        except Exception as e:
            print(f"❌ Failed to clear nanonis plot {plot_index + 1}: {e}")

    def update_helium_display(self):
        """Update the helium level display in the main control"""
        try:
            # Check if helium monitor is connected and active
            if hasattr(helium_widget, 'is_connected') and helium_widget.is_connected():
                helium_level = helium_widget.get_current_helium_level()
                if helium_level is not None:
                    self.He_num_lb.setText(f"{helium_level:.2f} in")
                    self.Helium_ind.setChecked(True)
                    self.Helium_ind.changeColor("green")
                else:
                    self.He_num_lb.setText("--")
                    self.Helium_ind.setChecked(True)
                    self.Helium_ind.changeColor("orange")
            else:
                self.He_num_lb.setText("--")
                self.Helium_ind.setChecked(False)
                self.Helium_ind.changeColor("orange")
        except Exception as e:
            print("❌ Failed to update helium display:", e)
            self.He_num_lb.setText("--")
            self.Helium_ind.setChecked(True)
            self.Helium_ind.changeColor("red")

    def show_helium_monitor(self):
        """Show the HeliumMonitor widget."""
        helium_widget.show()

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
    window = MainWindow()
    sys.exit(app.exec_())