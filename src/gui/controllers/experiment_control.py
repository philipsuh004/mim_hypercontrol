"""
================
Title: Measurement Control GUI
Author: Siyuan Qiu
Create Date: 2024/12/26
Institution: Stanford University, Department of Physics
Adapted from https://pymeasure.readthedocs.io/en/stable/tutorial/graphical.html
=================
"""

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import tempfile
import random
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow, ManagedWindowBase
from pymeasure.display.widgets import TableWidget, LogWidget, PlotWidget, ImageWidget
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime, timedelta
import numpy as np

class CreateExperiment(QFrame):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 500, 500, 200)
        self.experimentControl = ExperimentControl(MIMProcedure, False, ['1st Param Range', '1st Param Delay Time', '1st Param'])
        self.initUI()
        # self.show()

    def initUI(self):
        # create main grid to organize layout
        main_grid = QGridLayout()
        main_grid.setSpacing(10)
        self.setLayout(main_grid)
        self.setWindowTitle("Create Experiment")

        scan_lb = QLabel("Scan Geometry")
        main_grid.addWidget(scan_lb, 0, 0, 1, 1, Qt.AlignCenter)
        self.scan_geo_cb = QComboBox()
        self.scan_geo_cb.addItems(["Point", "Multiple Points", "Line", "Plane"])
        main_grid.addWidget(self.scan_geo_cb, 1, 0, 1, 1, Qt.AlignCenter)

        first_param_lb = QLabel("1st Param")
        main_grid.addWidget(first_param_lb, 0, 1, 1, 1, Qt.AlignCenter)
        self.first_param_cb = QComboBox()
        self.first_param_cb.addItems(["Bottom Gate", "Top Gate", "DS Voltage", "Magnetic Field", "Temperature"])
        main_grid.addWidget(self.first_param_cb, 1, 1, 1, 1, Qt.AlignCenter)

        self.second_param_cb = QComboBox()
        self.second_param_cb.setEnabled(False)
        self.second_param_cb.addItems(["Bottom Gate", "Top Gate", "DS Voltage", "Magnetic Field", "Temperature"])
        main_grid.addWidget(self.second_param_cb, 1, 2, 1, 1, Qt.AlignCenter)
        self.second_param_chb = QCheckBox("2nd Param")
        self.second_param_chb.stateChanged.connect(self.toggle2ndParam)
        main_grid.addWidget(self.second_param_chb, 0, 2, 1, 1, Qt.AlignCenter)

        self.create_btn = QPushButton("Create")
        self.create_btn.clicked.connect(self.create_experiment)
        main_grid.addWidget(self.create_btn, 2, 2, 1, 1, Qt.AlignCenter)

    def toggle2ndParam(self):
        if self.second_param_chb.isChecked():
            self.second_param_cb.setEnabled(True)
        else:
            self.second_param_cb.setEnabled(False)

    def create_experiment(self):
        if self.second_param_chb.isChecked() and (self.first_param_cb.currentText() == self.second_param_cb.currentText()):
            QMessageBox.warning(self, "Fail to create", "Cannot use the same parameter!")
            return
        buttonReply = QMessageBox.question(self, 'Create experiment', "Are you sure to create a new experiment?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.No:
            return

        if self.scan_geo_cb.currentText() == "Point":
            MIMProcedure.position = Parameter('Position', default='[0,0]')
        # Need to implement similar argument for other geometries

        MIMProcedure.first_param_range = Parameter('{} Range'.format(self.first_param_cb.currentText()), default='range(0, 101, 1)')
        MIMProcedure.first_param_delay = FloatParameter('{} Delay Time'.format(self.first_param_cb.currentText()), units='s', default=0.2)
        if MIMProcedure.first_param_range.value.startswith("range(") and MIMProcedure.first_param_range.value.endswith(")"):
            # Remove 'range(' and ')'
            params = MIMProcedure.first_param_range.value[6:-1]
            # Split the parameters by commas and convert them to integers
            start, stop, step = map(float, params.split(","))
            setattr(MIMProcedure, '{}_start'.format(self.first_param_cb.currentText()), start)
            setattr(MIMProcedure, '{}_end'.format(self.first_param_cb.currentText()), stop)
            setattr(MIMProcedure, '{}_step'.format(self.first_param_cb.currentText()), step)
            # Generate the range
            MIMProcedure.first_param_range_np = np.arange(start, stop, step)
        MIMProcedure.use_second_param = self.second_param_chb.isChecked()
        if self.second_param_chb.isChecked():
            MIMProcedure.second_param_range = Parameter('{} Range'.format(self.second_param_cb.currentText()),
                                                        default='range(0, 101, 1)')
            MIMProcedure.second_param_delay = FloatParameter('{} Delay Time'.format(self.second_param_cb.currentText()),
                                                             units='s', default=0.2)
            if MIMProcedure.second_param_range.value.startswith("range(") and MIMProcedure.second_param_range.value.endswith(")"):
                # Remove 'range(' and ')'
                params = MIMProcedure.second_param_range.value[6:-1]
                # Split the parameters by commas and convert them to integers
                start, stop, step = map(float, params.split(","))
                setattr(MIMProcedure, '{}_start'.format(self.second_param_cb.currentText()), start)
                setattr(MIMProcedure, '{}_end'.format(self.second_param_cb.currentText()), stop)
                setattr(MIMProcedure, '{}_step'.format(self.second_param_cb.currentText()), step)
                # Generate the range
                MIMProcedure.second_param_range_np = np.arange(start, stop, step)
            MIMProcedure.DATA_COLUMNS = [self.first_param_cb.currentText(),
                                         self.second_param_cb.currentText(),
                                         "Result"]

            self.experimentControl = ExperimentControl(MIMProcedure, self.second_param_chb.isChecked(), [self.first_param_cb.currentText(),
                                                        self.second_param_cb.currentText(), 'Result'])
        else:
            MIMProcedure.DATA_COLUMNS = [self.first_param_cb.currentText(), "Result"]
            self.experimentControl = ExperimentControl(MIMProcedure, self.second_param_chb.isChecked(), [self.first_param_cb.currentText(),
                                                        'Result'])
        self.experimentControl.show()

class MIMProcedure(Procedure):

    position = Parameter('Position', default='[0,0]')
    first_param_range = Parameter('1st Param Range', default='range(0, 101, 1)')
    first_param_delay = FloatParameter('1st Param Delay Time', units='s', default=0.2)
    first_param_range_np = np.arange(0, 101, 1)
    use_second_param = False
    second_param_range = Parameter('2nd Param Range', default='range(0, 101, 1)')
    second_param_delay = FloatParameter('2nd Param Delay Time', units='s', default=0.2)
    second_param_range_np = np.arange(0, 101, 1)

    DATA_COLUMNS = ['1st Param', 'Result']

    def startup(self):
        log.info("Setting up the parameters")
        if self.first_param_range.startswith("range(") and self.first_param_range.endswith(")"):
            # Remove 'range(' and ')'
            params = self.first_param_range[6:-1]
            # Split the parameters by commas and convert them to integers
            start, stop, step = map(float, params.split(","))
            setattr(self, '{}_start'.format(self.DATA_COLUMNS[0]), start)
            setattr(self, '{}_end'.format(self.DATA_COLUMNS[0]), stop)
            setattr(self, '{}_step'.format(self.DATA_COLUMNS[0]), step)
            # Generate the range
            self.first_param_range_np = np.arange(start, stop, step)
        if self.use_second_param and self.second_param_range.startswith(
                "range(") and self.second_param_range.endswith(")"):
            # Remove 'range(' and ')'
            params = self.second_param_range[6:-1]
            # Split the parameters by commas and convert them to integers
            start, stop, step = map(float, params.split(","))
            setattr(self, '{}_start'.format(self.DATA_COLUMNS[1]), start)
            setattr(self, '{}_end'.format(self.DATA_COLUMNS[1]), stop)
            setattr(self, '{}_step'.format(self.DATA_COLUMNS[1]), step)
            # Generate the range
            self.second_param_range_np = np.arange(start, stop, step)

    def execute(self):
        log.info("Starting the loop")
        # Add commands to move the tip, or config scanning mode
        for i in range(len(self.first_param_range_np)):
            log.debug('{}: %g'.format(self.DATA_COLUMNS[0]) % self.first_param_range_np[i])
            if self.use_second_param:
                for j in range(len(self.second_param_range_np)):
                    log.debug('{}: %g'.format(self.DATA_COLUMNS[1]) % self.second_param_range_np[j])
                    data = {
                        self.DATA_COLUMNS[0]: self.first_param_range_np[i],
                        self.DATA_COLUMNS[1]: self.second_param_range_np[j],  # Measurement result
                        self.DATA_COLUMNS[2]: 100 * (len(self.second_param_range_np)*i+j) / len(self.first_param_range_np) / len(self.second_param_range_np)
                    }
                    self.emit('results', data)
                    log.debug("Emitting results: %s" % data)
                    self.emit('progress', 100 * (len(self.second_param_range_np)*i+j) / len(self.first_param_range_np) / len(self.second_param_range_np) )
                    sleep(self.second_param_delay)
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break
                sleep(self.first_param_delay)
                if self.should_stop():
                    # log.warning("Caught the stop flag in the procedure")
                    break
            else:
                data = {
                    self.DATA_COLUMNS[0]: self.first_param_range_np[i],
                    self.DATA_COLUMNS[1]: i # Measurement result
                }
                self.emit('results', data)
                log.debug("Emitting results: %s" % data)
                self.emit('progress', 100 * i / len(self.first_param_range_np))
                sleep(self.first_param_delay)
                if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break

    # def get_estimates(self, sequence_length=None, sequence=None):
    #
    #     if self.use_second_param:
    #         duration = len(self.first_param_range_np) * (len(self.second_param_range_np) * self.second_param_delay + self.first_param_delay)
    #         estimates = [
    #             ("Duration", "%d s" % int(duration)),
    #             ("Number of 1st param", "%d" % int(len(self.first_param_range_np))),
    #             ("Number of 2nd param", "%d" % int(len(self.second_param_range_np))),
    #             ("Sequence length", str(sequence_length)),
    #             ('Measurement finished at', str(datetime.now() + timedelta(seconds=duration))),
    #         ]
    #     else:
    #         duration = len(self.first_param_range_np) * self.first_param_delay
    #         estimates = [
    #             ("Duration", "%d s" % int(duration)),
    #             ("Number of 1st param", "%d" % int(len(self.first_param_range_np))),
    #             ("Sequence length", str(sequence_length)),
    #             ('Measurement finished at', str(datetime.now() + timedelta(seconds=duration))),
    #         ]
    #
    #     return estimates

class ExperimentControl(ManagedWindowBase):

    def __init__(self, procedure_class, use_second_param, inputs):
        if use_second_param:
            widget_list = (ImageWidget("Experiment Image",
                                       MIMProcedure.DATA_COLUMNS,
                                       x_axis=inputs[0],
                                       y_axis=inputs[1],
                                       z_axis=inputs[2]
                                       ),
                           PlotWidget("Experiment Plot",
                                       MIMProcedure.DATA_COLUMNS,
                                      x_axis=inputs[0],
                                      y_axis=inputs[2]
                                       ),
                           LogWidget("Experiment Log"),
                           )
            super().__init__(
                procedure_class=procedure_class,
                inputs=['first_param_range', 'first_param_delay', 'second_param_range', 'second_param_delay'],
                displays=['first_param_range', 'first_param_delay', 'second_param_range', 'second_param_delay'],
                sequencer = True,  # Added line
                sequencer_inputs = ['first_param_range', 'first_param_delay', 'second_param_range', 'second_param_delay'],  # Added line
                widget_list=widget_list
                # sequence_file = "gui_sequencer_example_sequence.txt",  # Added line, optional
            )
            logging.getLogger().addHandler(widget_list[2].handler)
            log.setLevel(self.log_level)
            log.info("ManagedWindow connected to logging")
        else:
            widget_list = (PlotWidget("Experiment Plot",
                                      MIMProcedure.DATA_COLUMNS,
                                      x_axis=inputs[0],
                                      y_axis=inputs[1]
                                      ),
                           LogWidget("Experiment Log"),
                           )
            super().__init__(
                procedure_class=MIMProcedure,
                inputs=['first_param_range', 'first_param_delay'],
                displays=['first_param_range', 'first_param_delay'],
                sequencer=True,  # Added line
                sequencer_inputs=['first_param_range', 'first_param_delay'],  # Added line
                widget_list = widget_list
            # sequence_file = "gui_sequencer_example_sequence.txt",  # Added line, optional
            )
            logging.getLogger().addHandler(widget_list[1].handler)
            log.setLevel(self.log_level)
            log.info("ManagedWindow connected to logging")
        self.setWindowTitle('MIM Experiment GUI')
        self.setGeometry(100, 100, 2000, 1400)
        # super().plot_widget.columns_x_label.setMinimumWidth(100)
        # super().plot_widget.columns_y_label.setMinimumWidth(100)

        self.filename = r'default_filename_delay{Delay Time:4f}s'  # Sets default filename
        self.directory = r'C:/Path/to/default/directory'  # Sets default directory
        self.store_measurement = False  # Controls the 'Save data' toggle
        self.file_input.extensions = ["csv", "txt",
                                      "data"]  # Sets recognized extensions, first entry is the default extension
        self.file_input.filename_fixed = False  # Controls whether the filename-field is frozen (but still displayed)

# class ExperimentControl(ManagedWindow):
#
#     def __init__(self, procedure_class, use_second_param, inputs):
#         # Check how procedure class is called by ManagedWindow
#         if use_second_param:
#             super().__init__(
#                 procedure_class=procedure_class,
#                 inputs=['first_param_range', 'first_param_delay', 'second_param_range', 'second_param_delay'],
#                 displays=['first_param_range', 'first_param_delay', 'second_param_range', 'second_param_delay'],
#                 x_axis=inputs[0],
#                 y_axis=inputs[2],
#                 sequencer = True,  # Added line
#                 sequencer_inputs = ['first_param_range', 'first_param_delay', 'second_param_range', 'second_param_delay']  # Added line
#                 # sequence_file = "gui_sequencer_example_sequence.txt",  # Added line, optional
#             )
#         else:
#             super().__init__(
#                 procedure_class=MIMProcedure,
#                 inputs=['first_param_range', 'first_param_delay'],
#                 displays=['first_param_range', 'first_param_delay'],
#                 x_axis=inputs[0],
#                 y_axis=inputs[2],
#                 sequencer=True,  # Added line
#                 sequencer_inputs=['first_param_range', 'first_param_delay']  # Added line
#             # sequence_file = "gui_sequencer_example_sequence.txt",  # Added line, optional
#             )
#         self.setWindowTitle('GUI Example')
#         self.setGeometry(100, 100, 2000, 1400)
#         # super().plot_widget.columns_x_label.setMinimumWidth(100)
#         # super().plot_widget.columns_y_label.setMinimumWidth(100)
#
#         self.filename = r'default_filename_delay{Delay Time:4f}s'  # Sets default filename
#         self.directory = r'C:/Path/to/default/directory'  # Sets default directory
#         self.store_measurement = False  # Controls the 'Save data' toggle
#         self.file_input.extensions = ["csv", "txt",
#                                       "data"]  # Sets recognized extensions, first entry is the default extension
#         self.file_input.filename_fixed = False  # Controls whether the filename-field is frozen (but still displayed)