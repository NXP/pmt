# Copyright 2020-2022 NXP
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the NXP Semiconductors nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import signal
import os
import time
import copy
import csv
import pickle

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import numpy as np

import drv_ftdi

PROGRAM_VERSION = "PMT v2.5.3"
COPYRIGHT_INFO = "Copyright 2020-2023 NXP"

COLORS = [
    "#8B7825",
    "#842D2C",
    "#5E3450",
    "#00253D",
    "#205632",
    "#4E2B1B",
    "#6C561A",
    "#8A2533",
    "#5A2C5D",
    "#005474",
    "#4C762A",
    "#463626",
    "#6E4A1C",
    "#802247",
    "#2E1B45",
    "#00454E",
    "#554E24",
    "#2D2926",
    "#BE4C00",
    "#691F42",
    "#543074",
    "#244A57",
    "#817800",
    "#99AA00",
    "#73371B",
    "#572831",
    "#0A282E",
    "#004C40",
    "#B39900",
    "#83322E",
    "#632D4F",
    "#1A4086",
    "#005544",
    "#E31010",
    "#F9C21F",
    "#96F800",
    "#02FFCD",
    "#17BEF8",
    "#9F0BF7",
    "#F70BD2",
]

GROUPS_COLORS = ["#4FA383", "#007A4D", "#95A7C8", "#385C9B"]

TEMP_COLORS = ["#4CE514"]

FLAGS = {"display_all": False, "voltage_displayed_count": 0}

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class SplashScreen:
    def __init__(self):
        super().__init__()
        app = QtGui.QApplication([])
        self.windows = QtGui.QDialog()
        self.windows.setWindowFlags(
            self.windows.windowFlags() | QtCore.Qt.CustomizeWindowHint
        )
        self.windows.setWindowFlags(
            self.windows.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint
        )
        self.windows.setFixedSize(600, 380)
        self.windows.setStyleSheet("background-color: white;")
        # self.title = "Loading"
        self.text = QtGui.QLabel("Power Measurement Tool (PMT)")
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.text.setStyleSheet(
            "background-color: grey;" "color: black;" "font: bold 32px;"
        )
        self.text1 = QtGui.QLabel(PROGRAM_VERSION + " - " + COPYRIGHT_INFO)
        self.text1.setAlignment(QtCore.Qt.AlignCenter)
        self.text1.setStyleSheet("color: black;" "font: bold 24px;")
        self.pic = QtGui.QLabel(self.windows)
        self.pic.setAlignment(QtCore.Qt.AlignCenter)
        self.pic.setPixmap(QtGui.QPixmap("docs/images/nxp.png"))
        self.timer = pg.QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.layout = QtGui.QVBoxLayout()
        self.windows.setLayout(self.layout)
        # self.windows.setWindowTitle(self.title)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.pic)
        self.layout.addWidget(self.text1)
        self.windows.show()
        self.timer.singleShot(2500, app.quit)
        app.exec_()


class ProcessData(QtCore.QThread):
    sig_update_gui = QtCore.pyqtSignal()
    sig_update_instant_temp = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.parent = parent

    def run(self):
        remote_buf = []
        drv_ftdi.DATA_LOCK.acquire()
        for remote_rail in self.parent.b.data_buf:
            remote_buf.append(copy.deepcopy(remote_rail))
            remote_rail["current"] = [[0, 0]]
            remote_rail["voltage"] = [[0, 0]]
        drv_ftdi.DATA_LOCK.release()
        for rail in remote_buf:
            local_rail = next(
                (
                    item
                    for item in self.parent.rail_buf
                    if item["railnumber"] == rail["railnumber"]
                ),
                None,
            )
            if len(rail["voltage"]) > 1:
                rail["voltage"].pop(0)
                rail["current"].pop(0)
            local_rail["voltage"] = np.append(
                local_rail["voltage"],
                np.array(rail["voltage"], dtype=np.float16),
                axis=0,
            )
            local_rail["current"] = np.append(
                local_rail["current"],
                np.array(rail["current"], dtype=np.float16),
                axis=0,
            )

        self.parent.groups_buf = []
        for i, group in enumerate(self.parent.b.power_groups):
            self.parent.groups_buf.append(
                {
                    "group_name": group["name"],
                    "power": np.array([[0, 0]], dtype=np.float16),
                }
            )
            power_group = np.array([[0, 0]], dtype=np.float16)
            for rail_group in group["rails"]:
                rail = next(
                    (
                        item
                        for item in self.parent.rail_buf
                        if item["railnumber"] == rail_group
                    ),
                    None,
                )
                if rail is None:
                    return
                power_rail = np.empty_like(rail["voltage"][1:])
                power_rail[:, 0] = rail["voltage"][1:, 0]
                power_rail[:, 1] = rail["voltage"][1:, 1] * rail["current"][1:, 1]
                if power_group.shape[0] > power_rail.shape[0]:
                    power_group.resize(power_rail.shape)
                elif power_rail.shape[0] - power_group.shape[0] <= 2:
                    power_rail.resize(power_group.shape)
                power_group = power_group + power_rail
            power_group[:, 0] = power_rail[:, 0]
            self.parent.groups_buf[i]["power"] = power_group

        if self.parent.b.temperature_sensor:
            drv_ftdi.TEMP_DATA_LOCK.acquire()
            self.parent.temperature_buf = copy.deepcopy(self.parent.b.temp_buf)
            drv_ftdi.TEMP_DATA_LOCK.release()
            self.sig_update_instant_temp.emit()

        self.sig_update_gui.emit()


class Worker(QtCore.QObject):
    """creates worker class for thread"""

    def __init__(self, board, type):
        QtCore.QObject.__init__(self)
        self.board = board
        self.type = type

    def do_work(self):
        """runs function for collecting power data or temperature data"""
        if self.type == "power":
            self.board.get_data()
        else:
            time.sleep(0.5)
            self.board.process_temperature()

    def pause_thread(self):
        drv_ftdi.FLAG_PAUSE_CAPTURE = True

    def resume_thread(self):
        drv_ftdi.FLAG_PAUSE_CAPTURE = False


class ZoomDataWin(QtGui.QDialog):
    """extern window displaying data in zoom region"""

    def __init__(self, parent=None):
        super(ZoomDataWin, self).__init__(parent)
        self.parent = parent
        self.header_title = [
            "Rail",
            "P_avg",
            "P_min",
            "P_max",
            "V_avg",
            "V_min",
            "V_max",
            "I_avg",
            "I_min",
            "I_max",
        ]
        self.data_table = QtGui.QTableWidget(0, len(self.header_title))
        self.data_table.setHorizontalHeaderLabels(self.header_title)
        for rail in self.parent.b.rails_to_display:
            rowposition = self.data_table.rowCount()
            self.data_table.insertRow(rowposition)
            self.data_table.setItem(
                rowposition, 0, QtGui.QTableWidgetItem(rail["name"])
            )

        for group in self.parent.b.power_groups:
            rowposition = self.data_table.rowCount()
            self.data_table.insertRow(rowposition)
            self.data_table.setItem(
                rowposition, 0, QtGui.QTableWidgetItem(group["name"])
            )
            self.data_table.item(rowposition, 0).setBackground(
                QtGui.QColor(169, 169, 0, 169)
            )

        self.w_data_lay = QtGui.QVBoxLayout()
        self.rail_control = QtGui.QLabel("Time :")
        self.w_data_lay.addWidget(self.rail_control)
        self.w_data_lay.addWidget(self.data_table)
        self.setLayout(self.w_data_lay)

    def update_data(self, minx, maxx):
        """updates data window"""
        if self.isVisible():
            self.rail_control.setText("Time : " + str(maxx - minx) + " sec")
            i = 0
            for d_rail in self.parent.b.rails_to_display:
                rail = next(
                    (
                        item
                        for item in self.parent.rail_buf
                        if item["railnumber"] == d_rail["name"]
                    ),
                    None,
                )
                voltage = rail["voltage"][1:]
                current = rail["current"][1:]
                power = np.empty_like(voltage)
                power[:, 0] = voltage[:, 0]
                power[:, 1] = voltage[:, 1] * current[:, 1]

                min_t_p = power[:, 0].searchsorted(minx)
                max_t_p = power[:, 0].searchsorted(maxx)
                if min_t_p and min_t_p != max_t_p:
                    p_avg = power[min_t_p:max_t_p, 1].mean()
                    p_min = power[min_t_p:max_t_p, 1].min()
                    p_max = power[min_t_p:max_t_p, 1].max()
                    self.data_table.setItem(i, 1, QtGui.QTableWidgetItem(str(p_avg)))
                    self.data_table.setItem(i, 2, QtGui.QTableWidgetItem(str(p_min)))
                    self.data_table.setItem(i, 3, QtGui.QTableWidgetItem(str(p_max)))

                min_t_v = voltage[:, 0].searchsorted(minx)
                max_t_v = voltage[:, 0].searchsorted(maxx)
                if min_t_v and min_t_v != max_t_v:
                    v_avg = voltage[min_t_v:max_t_v, 1].mean()
                    v_min = voltage[min_t_v:max_t_v, 1].min()
                    v_max = voltage[min_t_v:max_t_v, 1].max()
                    self.data_table.setItem(i, 4, QtGui.QTableWidgetItem(str(v_avg)))
                    self.data_table.setItem(i, 5, QtGui.QTableWidgetItem(str(v_min)))
                    self.data_table.setItem(i, 6, QtGui.QTableWidgetItem(str(v_max)))

                min_t_c = current[:, 0].searchsorted(minx)
                max_t_c = current[:, 0].searchsorted(maxx)
                if min_t_c and min_t_c != max_t_c:
                    c_avg = current[min_t_c:max_t_c, 1].mean()
                    c_min = current[min_t_c:max_t_c, 1].min()
                    c_max = current[min_t_c:max_t_c, 1].max()
                    self.data_table.setItem(i, 7, QtGui.QTableWidgetItem(str(c_avg)))
                    self.data_table.setItem(i, 8, QtGui.QTableWidgetItem(str(c_min)))
                    self.data_table.setItem(i, 9, QtGui.QTableWidgetItem(str(c_max)))
                i += 1

            for j, group in enumerate(self.parent.groups_buf):
                time_group = group["power"][:, 0]
                power = group["power"][:, 1]
                min_t_gp = time_group.searchsorted(minx)
                max_t_gp = time_group.searchsorted(maxx)
                if min_t_gp and min_t_gp != max_t_gp:
                    gp_avg = power[min_t_gp:max_t_gp].mean()
                    gp_min = power[min_t_gp:max_t_gp].min()
                    gp_max = power[min_t_gp:max_t_gp].max()
                    self.data_table.setItem(
                        i + j, 1, QtGui.QTableWidgetItem(str(gp_avg))
                    )
                    self.data_table.setItem(
                        i + j, 2, QtGui.QTableWidgetItem(str(gp_min))
                    )
                    self.data_table.setItem(
                        i + j, 3, QtGui.QTableWidgetItem(str(gp_max))
                    )


class MPDataWin(QtGui.QDialog):
    """extern window displaying data pointed by mouse pointer"""

    def __init__(self, parent=None):
        super(MPDataWin, self).__init__(parent)
        self.parent = parent
        self.header_title = ["Rail", "Power (mW)", "Voltage (V)", "Current (mA)"]
        self.data_table = QtGui.QTableWidget(0, len(self.header_title))
        self.data_table.setHorizontalHeaderLabels(self.header_title)
        for rail in self.parent.b.rails_to_display:
            rowposition = self.data_table.rowCount()
            self.data_table.insertRow(rowposition)
            self.data_table.setItem(
                rowposition, 0, QtGui.QTableWidgetItem(rail["name"])
            )

        for group in self.parent.b.power_groups:
            rowposition = self.data_table.rowCount()
            self.data_table.insertRow(rowposition)
            self.data_table.setItem(
                rowposition, 0, QtGui.QTableWidgetItem(group["name"])
            )
            self.data_table.item(rowposition, 0).setBackground(
                QtGui.QColor(169, 169, 0, 169)
            )

        self.w_data_lay = QtGui.QVBoxLayout()
        self.rail_control = QtGui.QLabel("Time :")
        self.w_data_lay.addWidget(self.rail_control)
        self.w_data_lay.addWidget(self.data_table)
        self.setLayout(self.w_data_lay)

    def update_data(self, time_coord):
        """updates data window"""
        if self.isVisible():
            self.rail_control.setText("Time : " + str(time_coord) + " sec")
            i = 0
            for d_rail in self.parent.b.rails_to_display:
                rail = next(
                    (
                        item
                        for item in self.parent.rail_buf
                        if item["railnumber"] == d_rail["name"]
                    ),
                    None,
                )
                voltage = rail["voltage"][1:]
                current = rail["current"][1:]
                power = np.empty_like(voltage)
                power[:, 0] = voltage[:, 0]
                power[:, 1] = voltage[:, 1] * current[:, 1]
                x_coord_p = power[:, 0].searchsorted(time_coord)
                x_coord_v = voltage[:, 0].searchsorted(time_coord)
                x_coord_c = current[:, 0].searchsorted(time_coord)
                if x_coord_p:
                    mp_power = power[x_coord_p - 1, 1]
                    self.data_table.setItem(i, 1, QtGui.QTableWidgetItem(str(mp_power)))
                if x_coord_v:
                    mp_voltage = voltage[x_coord_v - 1, 1]
                    self.data_table.setItem(
                        i, 2, QtGui.QTableWidgetItem(str(mp_voltage))
                    )
                if x_coord_c:
                    mp_current = current[x_coord_c - 1, 1]
                    self.data_table.setItem(
                        i, 3, QtGui.QTableWidgetItem(str(mp_current))
                    )
                i += 1

            for j, group in enumerate(self.parent.groups_buf):
                time_group = group["power"][1:, 0]
                power = group["power"][1:, 1]
                x_coord_gp = time_group.searchsorted(time_coord)
                if x_coord_gp:
                    mp_gpower = power[x_coord_p - 1]
                    self.data_table.setItem(
                        i + j + 1, 1, QtGui.QTableWidgetItem(str(mp_gpower))
                    )

    def closeEvent(self, event):
        """function called when window is quit by clicking the red cross"""
        self.parent.proxy1.disconnect()
        self.parent.proxy2.disconnect()


class GlobalDataWin(QtGui.QDialog):
    """extern window displaying data collected since app starts"""

    def __init__(self, parent=None):
        super(GlobalDataWin, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle("Global Data Window")
        self.header_title = [
            "Rail",
            "P_avg",
            "P_min",
            "P_max",
            "V_avg",
            "V_min",
            "V_max",
            "I_avg",
            "I_min",
            "I_max",
        ]
        self.data_table = QtGui.QTableWidget(0, len(self.header_title))
        self.data_table.setHorizontalHeaderLabels(self.header_title)
        for rail in self.parent.b.rails_to_display:
            rowposition = self.data_table.rowCount()
            self.data_table.insertRow(rowposition)
            self.data_table.setItem(
                rowposition, 0, QtGui.QTableWidgetItem(rail["name"])
            )

        for group in self.parent.b.power_groups:
            rowposition = self.data_table.rowCount()
            self.data_table.insertRow(rowposition)
            self.data_table.setItem(
                rowposition, 0, QtGui.QTableWidgetItem(group["name"])
            )
            self.data_table.item(rowposition, 0).setBackground(
                QtGui.QColor(169, 169, 0, 169)
            )

        self.w_data_lay = QtGui.QVBoxLayout()
        self.w_data_lay.addWidget(self.data_table)
        self.setLayout(self.w_data_lay)

    def update_data(self):
        """updates data window"""
        if self.isVisible():
            i = 0
            for d_rail in self.parent.b.rails_to_display:
                rail = next(
                    (
                        item
                        for item in self.parent.rail_buf
                        if item["railnumber"] == d_rail["name"]
                    ),
                    None,
                )
                voltage = rail["voltage"][1:, 1]
                current = rail["current"][1:, 1]
                power = voltage * current
                p_avg = power.mean()
                p_min = power.min()
                p_max = power.max()
                v_avg = voltage.mean()
                v_min = voltage.min()
                v_max = voltage.max()
                c_avg = current.mean()
                c_min = current.min()
                c_max = current.max()
                self.data_table.setItem(i, 1, QtGui.QTableWidgetItem(str(p_avg)))
                self.data_table.setItem(i, 2, QtGui.QTableWidgetItem(str(p_min)))
                self.data_table.setItem(i, 3, QtGui.QTableWidgetItem(str(p_max)))
                self.data_table.setItem(i, 4, QtGui.QTableWidgetItem(str(v_avg)))
                self.data_table.setItem(i, 5, QtGui.QTableWidgetItem(str(v_min)))
                self.data_table.setItem(i, 6, QtGui.QTableWidgetItem(str(v_max)))
                self.data_table.setItem(i, 7, QtGui.QTableWidgetItem(str(c_avg)))
                self.data_table.setItem(i, 8, QtGui.QTableWidgetItem(str(c_min)))
                self.data_table.setItem(i, 9, QtGui.QTableWidgetItem(str(c_max)))
                i += 1

            for j, group in enumerate(self.parent.groups_buf):
                power = group["power"][:, 1]
                gp_avg = power.mean()
                gp_min = power.min()
                gp_max = power.max()
                self.data_table.setItem(i + j, 1, QtGui.QTableWidgetItem(str(gp_avg)))
                self.data_table.setItem(i + j, 2, QtGui.QTableWidgetItem(str(gp_min)))
                self.data_table.setItem(i + j, 3, QtGui.QTableWidgetItem(str(gp_max)))


class GUI(QtWidgets.QMainWindow):
    def __init__(self, board, args, parent=None):
        super(GUI, self).__init__(parent)
        self.b = board
        self.args = args
        self.rail_buf = []
        self.groups_buf = []
        self.temperature_buf = []
        self.list_power_plot_main = []
        self.list_power_plot_zoom = []
        self.list_current_plot_main = []
        self.list_current_plot_zoom = []
        self.list_voltage_plot_main = []
        self.list_voltage_plot_zoom = []
        self.list_group_plot_main = []
        self.list_group_plot_zoom = []
        self.list_rails_p = []
        self.list_groups_p = []
        self.list_rails_v = []
        self.list_rails_c = []
        self.list_groups_t = []
        self.list_rails_label = []
        self.list_groups_label = []
        self.list_temperature_label = []
        self.list_switch_res = []
        self.list_color_rails = []
        self.list_color_groups = []
        self.list_color_temperature = []
        self.list_right_lay_n = []
        self.list_right_lay_group_n = []
        self.list_right_lay_p = []
        self.list_right_lay_group_p = []
        self.list_right_lay_v = []
        self.list_right_lay_c = []
        self.state = "start"
        self.central_widget = QtGui.QWidget()
        self.timer = pg.QtCore.QTimer()
        self.menu_bar = self.menuBar()
        self.winmenu = QtGui.QMenu()
        self.status_bar = self.statusBar()
        self.spacer = QtGui.QWidget()
        self.spacer1 = QtGui.QWidget()
        self.wid_rail_scrollbar = QtGui.QWidget()
        self.rail_scrollbar = QtWidgets.QScrollArea()
        self.global_lay = QtGui.QHBoxLayout()
        self.button_lay = QtGui.QGridLayout()
        self.group_lay = QtGui.QGridLayout()
        self.temperature_lay = QtGui.QGridLayout()
        self.left_lay = QtGui.QVBoxLayout()
        self.plot_lay = QtGui.QGridLayout()
        self.right_lay = QtGui.QVBoxLayout()
        self.right_lay_group = QtGui.QGridLayout()
        self.right_lay_rail = QtGui.QGridLayout()
        self.global_graph = pg.PlotWidget(title="Main Window")
        self.global_graph_vb = pg.ViewBox()
        self.global_graph_pi = self.global_graph.plotItem
        self.zoom_graph = pg.PlotWidget(title="Zoom Area")
        self.zoom_graph_vb = pg.ViewBox()
        self.zoom_graph_pi = self.zoom_graph.plotItem
        self.zoom_region = pg.LinearRegionItem()
        self.stop_region = []
        self.stop = 0
        self.resume = 0
        self.thread_data = QtCore.QThread(parent=self)
        self.worker = Worker(self.b, "power")
        self.thread_temperature = QtCore.QThread(parent=self)
        self.worker_temperature = Worker(self.b, "temperature")
        self.thread_process_data = ProcessData(self)
        signal.signal(signal.SIGINT, self.sigint_handler)
        self.start_setup()

    def sigint_handler(self, *args):
        """displays a message box if the GUI is exit with CTRL+C command"""
        if (
            QtGui.QMessageBox.question(
                None,
                "",
                "Are you sure you want to quit?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No,
            )
            == QtGui.QMessageBox.Yes
        ):
            self.worker.resume_thread()
            drv_ftdi.FLAG_UI_STOP = True
            self.thread_data.quit()
            self.thread_data.wait()
            self.thread_temperature.quit()
            self.thread_temperature.wait()
            QtGui.QApplication.quit()

    def closeEvent(self, event):
        """function called when app is quit by clicking the red cross"""
        self.worker.resume_thread()
        drv_ftdi.FLAG_UI_STOP = True
        self.thread_data.quit()
        self.thread_data.wait()
        self.thread_temperature.quit()
        self.thread_temperature.wait()
        QtGui.QApplication.quit()

    def mousemoved_zoom_graph(self, evt):
        """gets mouse pointer values in zoom graph and updates window values"""
        pos = evt[0]
        mousepoint = self.zoom_graph.getPlotItem().getViewBox().mapSceneToView(pos)
        time_coor = mousepoint.x()
        self.mouse_pointer_window.update_data(time_coor)

    def mousemove_global_graph(self, evt):
        """gets mouse pointer values in global graph and updates window values"""
        pos = evt[0]
        mousepoint = self.global_graph.getPlotItem().getViewBox().mapSceneToView(pos)
        time_coor = mousepoint.x()
        self.mouse_pointer_window.update_data(time_coor)

    def update_instant_temp(self):
        try:
            self.temp_label.setText(
                " Current board temperature: "
                + str(self.temperature_buf[-1][1])
                + "°C "
            )
        except IndexError:
            pass

    def single_trace_update(self, index, type, trace_main, trace_zoom):
        if type == "temp":
            trace_main.setData(
                np.array(self.temperature_buf)[:, 0],
                np.array(self.temperature_buf)[:, 1],
            )
            trace_zoom.setData(
                np.array(self.temperature_buf)[:, 0],
                np.array(self.temperature_buf)[:, 1],
            )
        if type == "group":
            trace_main.setData(
                self.groups_buf[index]["power"][:, 0],
                self.groups_buf[index]["power"][:, 1],
            )
            trace_zoom.setData(
                self.groups_buf[index]["power"][:, 0],
                self.groups_buf[index]["power"][:, 1],
            )
        if type == "power":
            rail = next(
                (
                    item
                    for item in self.rail_buf
                    if item["railnumber"] == self.b.rails_to_display[index]["name"]
                ),
                None,
            )
            voltage = rail["voltage"][1:]
            current = rail["current"][1:]
            power = np.empty_like(voltage)
            power[:, 0] = voltage[:, 0]
            power[:, 1] = voltage[:, 1] * current[:, 1]
            trace_main.setData(power[:, 0], power[:, 1])
            trace_zoom.setData(power[:, 0], power[:, 1])
        if type == "voltage":
            rail = next(
                (
                    item
                    for item in self.rail_buf
                    if item["railnumber"] == self.b.rails_to_display[index]["name"]
                ),
                None,
            )
            voltage = rail["voltage"][1:]
            trace_main.setData(voltage[:, 0], voltage[:, 1])
            trace_zoom.setData(voltage[:, 0], voltage[:, 1])
        if type == "current":
            rail = next(
                (
                    item
                    for item in self.rail_buf
                    if item["railnumber"] == self.b.rails_to_display[index]["name"]
                ),
                None,
            )
            current = rail["current"][1:]
            trace_main.setData(current[:, 0], current[:, 1])
            trace_zoom.setData(current[:, 0], current[:, 1])

    def traces_update(self):
        """updates global / zoom plot and updates values"""
        if not self.args.load:
            self.global_graph.disableAutoRange()
            self.zoom_graph.disableAutoRange()

        self.zoom_graph.blockSignals(True)
        self.zoom_region.blockSignals(True)
        self.global_graph.blockSignals(True)

        maxx = None
        for i, d_rail in enumerate(self.b.rails_to_display):
            rail = next(
                (
                    item
                    for item in self.rail_buf
                    if item["railnumber"] == d_rail["name"]
                ),
                None,
            )
            maxx = rail["voltage"][-1][0]
            if rail is None or len(rail["voltage"]) <= 1:
                return
            voltage = rail["voltage"][1:]
            current = rail["current"][1:]
            power = np.empty_like(voltage)
            power[:, 0] = voltage[:, 0]
            power[:, 1] = voltage[:, 1] * current[:, 1]
            if self.list_rails_p[i].isChecked():
                self.list_power_plot_main[i].setData(power[:, 0], power[:, 1])
                self.list_power_plot_zoom[i].setData(power[:, 0], power[:, 1])

            if self.list_rails_c[i].isChecked():
                self.list_current_plot_main[i].setData(current[:, 0], current[:, 1])
                self.list_current_plot_zoom[i].setData(current[:, 0], current[:, 1])

            if self.list_rails_v[i].isChecked():
                self.list_voltage_plot_main[i].setData(voltage[:, 0], voltage[:, 1])
                self.list_voltage_plot_zoom[i].setData(voltage[:, 0], voltage[:, 1])

        for j, group in enumerate(self.groups_buf):
            maxx = group["power"][-1][0] if maxx is None else maxx
            if self.list_groups_p[j].isChecked():
                self.list_group_plot_main[j].setData(
                    group["power"][:, 0], group["power"][:, 1]
                )
                self.list_group_plot_zoom[j].setData(
                    group["power"][:, 0], group["power"][:, 1]
                )

        if self.b.temperature_sensor and self.list_groups_t[0].isChecked():
            if len(self.temperature_buf) > 1:
                self.list_temp_plot_main.setData(
                    np.array(self.temperature_buf)[:, 0],
                    np.array(self.temperature_buf)[:, 1],
                )
                self.list_temp_plot_zoom.setData(
                    np.array(self.temperature_buf)[:, 0],
                    np.array(self.temperature_buf)[:, 1],
                )

        if self.timer.isActive() or self.args.load:
            self.global_graph.autoRange(padding=0)
            self.global_graph.setXRange(0, maxx, padding=0)
            minx = maxx - 2 if maxx >= 2 else 0
            self.zoom_region.setRegion((minx, maxx))
            self.zoom_graph.enableAutoRange("y")
            self.zoom_graph.setXRange(minx, maxx, padding=0)

        for reg in self.stop_region:
            if reg not in self.global_graph_pi.vb.allChildren():
                self.global_graph_pi.addItem(reg, ignoreBounds=True)

        self.zoom_graph.blockSignals(False)
        self.zoom_region.blockSignals(False)
        self.global_graph.blockSignals(False)

        self.global_data_window.update_data()
        self.update_zoom_data()
        self.update_right_lay_data()

    def update_right_lay_data(self):
        """updates average values of plotted rails and groups"""
        for j, group in enumerate(self.groups_buf):
            p_avg = group["power"][:, 1].mean()
            self.list_right_lay_group_p[j].setText(str("%.2f" % p_avg))

        for i, d_rail in enumerate(self.b.rails_to_display):
            if (
                self.list_rails_p[i].isChecked()
                or self.list_rails_v[i].isChecked()
                or self.list_rails_c[i].isChecked()
            ):
                rail = next(
                    (
                        item
                        for item in self.rail_buf
                        if item["railnumber"] == d_rail["name"]
                    ),
                    None,
                )
                voltage = rail["voltage"][1:, 1]
                current = rail["current"][1:, 1]
                power = voltage * current
                p_avg = power.mean()
                v_avg = voltage.mean()
                c_avg = current.mean()
                self.list_right_lay_p[i].setText(str("%.2f" % p_avg))
                self.list_right_lay_v[i].setText(str("%.2f" % v_avg))
                self.list_right_lay_c[i].setText(str("%.2f" % c_avg))
                self.list_right_lay_n[i].setStyleSheet("color: black")
                self.list_right_lay_p[i].setStyleSheet("color: black")
                self.list_right_lay_v[i].setStyleSheet("color: black")
                self.list_right_lay_c[i].setStyleSheet("color: black")
            else:
                self.list_right_lay_n[i].setStyleSheet("color: grey")
                self.list_right_lay_p[i].setStyleSheet("color: grey")
                self.list_right_lay_v[i].setStyleSheet("color: grey")
                self.list_right_lay_c[i].setStyleSheet("color: grey")

    def update_zoom_view(self):
        """updates zoom view"""
        self.zoom_graph_vb.setGeometry(self.zoom_graph_pi.vb.sceneBoundingRect())
        self.zoom_graph_vb.linkedViewChanged(
            self.zoom_graph_pi.vb, self.zoom_graph_vb.XAxis
        )

    def update_global_view(self):
        """updates global view"""
        self.global_graph_vb.setGeometry(self.global_graph_pi.vb.sceneBoundingRect())
        self.global_graph_vb.linkedViewChanged(
            self.global_graph_pi.vb, self.global_graph_vb.XAxis
        )

    def update_zoom_region(self, window, viewrange):
        """updates zoom region if user moove zoom graph"""
        self.zoom_region.blockSignals(True)
        rgn = viewrange[0]
        self.zoom_region.setRegion(rgn)
        self.update_zoom_data()
        self.zoom_region.blockSignals(False)

    def update_zoom_graph(self):
        """updates zoom graph if user moove zoom region"""
        self.zoom_graph.blockSignals(True)
        self.zoom_region.blockSignals(True)

        self.zoom_region.setZValue(10)
        minx, maxx = self.zoom_region.getRegion()
        self.zoom_graph.setXRange(minx, maxx, padding=0)
        self.update_zoom_data()

        self.zoom_region.blockSignals(False)
        self.zoom_graph.blockSignals(False)

    def update_zoom_data(self):
        """updates values in zoom data windows"""
        minx, maxx = self.zoom_region.getRegion()
        self.zoom_data_window.update_data(minx, maxx)

    def temperature_changed(self):
        """signal called when temperature checkbox state changed"""
        current_state = self.list_groups_t[0].isChecked()
        if current_state:
            self.global_graph_vb.addItem(self.list_temp_plot_main)
            self.zoom_graph_vb.addItem(self.list_temp_plot_zoom)

            self.single_trace_update(
                0, "temp", self.list_temp_plot_main, self.list_temp_plot_zoom
            )

            self.global_graph.setLabels(right="Temperature (°C)")
            self.zoom_graph.setLabels(right="Temperature (°C)")
        else:
            self.global_graph_vb.removeItem(self.list_temp_plot_main)
            self.zoom_graph_vb.removeItem(self.list_temp_plot_zoom)

        self.label_v.setEnabled(not current_state)
        for but in self.list_rails_v:
            but.setEnabled(not current_state)

    def g_power_changed(self, index):
        """signal called when power checkbox state changed"""
        if self.list_groups_p[index].isChecked():
            self.global_graph.addItem(self.list_group_plot_main[index])
            self.zoom_graph.addItem(self.list_group_plot_zoom[index])

            self.single_trace_update(
                index,
                "group",
                self.list_group_plot_main[index],
                self.list_group_plot_zoom[index],
            )
        else:
            self.global_graph.removeItem(self.list_group_plot_main[index])
            self.zoom_graph.removeItem(self.list_group_plot_zoom[index])

    def power_changed(self, index):
        """signal called when power checkbox state changed"""
        if self.list_rails_p[index].isChecked():
            self.global_graph.addItem(self.list_power_plot_main[index])
            self.zoom_graph.addItem(self.list_power_plot_zoom[index])

            self.single_trace_update(
                index,
                "power",
                self.list_power_plot_main[index],
                self.list_power_plot_zoom[index],
            )
        else:
            self.global_graph.removeItem(self.list_power_plot_main[index])
            self.zoom_graph.removeItem(self.list_power_plot_zoom[index])

    def voltage_changed(self, index):
        """signal called when voltage checkbox state changed"""
        if self.list_rails_v[index].isChecked():
            FLAGS["voltage_displayed_count"] += 1
            self.global_graph_vb.addItem(self.list_voltage_plot_main[index])
            self.zoom_graph_vb.addItem(self.list_voltage_plot_zoom[index])
            self.single_trace_update(
                index,
                "voltage",
                self.list_voltage_plot_main[index],
                self.list_voltage_plot_zoom[index],
            )
        else:
            FLAGS["voltage_displayed_count"] -= 1
            self.global_graph_vb.removeItem(self.list_voltage_plot_main[index])
            self.zoom_graph_vb.removeItem(self.list_voltage_plot_zoom[index])

        if self.b.temperature_sensor:
            self.global_graph.setLabels(right="Voltage (V)")
            self.zoom_graph.setLabels(right="Voltage (V)")
            self.list_groups_t[0].setEnabled(False)
            if FLAGS["voltage_displayed_count"] == 0:
                self.list_groups_t[0].setEnabled(True)

    def current_changed(self, index):
        """signal called when current checkbox state changed"""
        if self.list_rails_c[index].isChecked():
            self.global_graph.addItem(self.list_current_plot_main[index])
            self.zoom_graph.addItem(self.list_current_plot_zoom[index])

            self.single_trace_update(
                index,
                "current",
                self.list_current_plot_main[index],
                self.list_current_plot_zoom[index],
            )
        else:
            self.global_graph.removeItem(self.list_current_plot_main[index])
            self.zoom_graph.removeItem(self.list_current_plot_zoom[index])

    def switch_res_changed(self, index):
        """switches the resistance and update the corresponding box if it has been correctly done"""
        rail = next(
            (
                item
                for item in self.rail_buf
                if item["railnumber"] == self.b.rails_to_display[index]["name"]
            ),
            None,
        )
        done, authorized = self.b.switch_res(rail, index)
        if authorized:
            if done:
                curr_state = self.list_switch_res[index].text()
                if curr_state == "L":
                    new_state = "H"
                else:
                    new_state = "L"
                self.list_switch_res[index].setText(new_state)

    def hide_all_power(self):
        """hides / shows all power rails depending of the checkbox's state"""
        current_state = self.label_p.isChecked()
        for but in self.list_rails_p:
            but.setChecked(current_state)

    def hide_all_voltage(self):
        """hides / shows all voltage rails depending of the checkbox's state"""
        current_state = self.label_v.isChecked()
        for but in self.list_rails_v:
            but.setChecked(current_state)
        FLAGS["voltage_displayed_count"] = (
            len(self.list_rails_v) if current_state else 0
        )
        if self.b.temperature_sensor:
            self.list_groups_t[0].setEnabled(not current_state)
            self.global_graph.setLabels(right="Voltage (V)")
            self.zoom_graph.setLabels(right="Voltage (V)")

    def hide_all_current(self):
        """hides / shows all current rails depending of the checkbox's state"""
        current_state = self.label_c.isChecked()
        for but in self.list_rails_c:
            but.setChecked(current_state)

    def hide_all_single_plot(self, index):
        self.list_rails_p[index].setChecked(False)
        self.list_rails_v[index].setChecked(False)
        self.list_rails_c[index].setChecked(False)

    def change_color(self, index):
        """updates the color of the selected rail"""
        COLORS[index] = self.list_color_rails[index].color().name()
        self.list_power_plot_main[index].setPen(COLORS[index])
        self.list_power_plot_zoom[index].setPen(COLORS[index])
        self.list_current_plot_main[index].setPen(
            pg.mkPen(COLORS[index], style=QtCore.Qt.DotLine)
        )
        self.list_current_plot_zoom[index].setPen(
            pg.mkPen(COLORS[index], style=QtCore.Qt.DotLine)
        )
        self.list_voltage_plot_main[index].setPen(
            pg.mkPen(COLORS[index], width=2, style=QtCore.Qt.DashDotDotLine)
        )
        self.list_voltage_plot_zoom[index].setPen(
            pg.mkPen(COLORS[index], width=2, style=QtCore.Qt.DashDotDotLine)
        )

    def change_color_g(self, index):
        """updates the color of the selected group"""
        GROUPS_COLORS[index] = self.list_color_groups[index].color().name()
        self.list_group_plot_main[index].setPen(pg.mkPen(GROUPS_COLORS[index], width=3))
        self.list_group_plot_zoom[index].setPen(pg.mkPen(GROUPS_COLORS[index], width=3))

    def change_color_t(self):
        """updates the color of the temperature"""
        TEMP_COLORS[0] = self.list_color_temperature[0].color().name()
        self.list_temp_plot_main.setPen(
            pg.mkPen(TEMP_COLORS[0], width=2, style=QtCore.Qt.DashDotDotLine)
        )
        self.list_temp_plot_zoom.setPen(
            pg.mkPen(TEMP_COLORS[0], width=2, style=QtCore.Qt.DashDotDotLine)
        )

    def save_pmt(self):
        """saves the capture as binary file with specified name"""
        name = QtGui.QFileDialog.getSaveFileName(
            caption="Save captured data as binary file",
            filter="PMT captures .pmt (*.pmt)",
        )
        if name[0]:
            filename = os.path.splitext(name[0])[0]
            filename += ".pmt"
            file_out = open(filename, "wb")
            print("Saving to binary file " + str(filename))
            pickle.dump(self.rail_buf, file_out, -1)
            pickle.dump(self.groups_buf, file_out, -1)
            if self.b.temperature_sensor:
                pickle.dump(self.temperature_buf, file_out, -1)
            file_out.close()
            print("Done.")

    def save_csv(self):
        """saves the capture as csv file with specified name"""
        headers = []
        data = []
        name = QtGui.QFileDialog.getSaveFileName(
            caption="Save captured data as csv file", filter="csv"
        )
        if name[0]:
            filename = os.path.splitext(name[0])
            if filename:
                type_data = ["voltage", "current", "power"]
                type_data_unit = [" (V)", " (mA)", " (mW)"]
                array_size = self.rail_buf[-1]["voltage"].shape[0]
                data.append(self.rail_buf[0]["voltage"][1:array_size, 0])
                headers.append("Time (ms)")
                for d_rail in self.b.rails_to_display:
                    rail = next(
                        (
                            item
                            for item in self.rail_buf
                            if item["railnumber"] == d_rail["name"]
                        ),
                        None,
                    )
                    for j in range(3):
                        headers.append(
                            str(d_rail["name"] + " " + type_data[j] + type_data_unit[j])
                        )
                        if j != 2:
                            data.append(rail[type_data[j]][1:array_size, 1])
                        else:
                            data.append(
                                rail["current"][1:array_size, 1]
                                * rail["voltage"][1:array_size, 1]
                            )
                if self.b.power_groups:
                    for group in self.b.power_groups:
                        power_group = np.array([[0, 0]], dtype=np.float16)
                        headers.append(group["name"] + " power (mW)")
                        for rail_group in group["rails"]:
                            rail = next(
                                (
                                    item
                                    for item in self.rail_buf
                                    if item["railnumber"] == rail_group
                                ),
                                None,
                            )
                            power_rail = np.empty_like(rail["voltage"][1:array_size])
                            power_rail[:, 0] = rail["voltage"][1:array_size, 0]
                            power_rail[:, 1] = (
                                rail["voltage"][1:array_size, 1]
                                * rail["current"][1:array_size, 1]
                            )
                            if power_group.shape[0] > power_rail.shape[0]:
                                power_group.resize(power_rail.shape, refcheck=False)
                            elif power_rail.shape[0] - power_group.shape[0] <= 2:
                                power_rail.resize(power_group.shape)
                            power_group = power_group + power_rail
                        data.append(power_group[:, 1])
                if self.b.temperature_sensor:
                    csv_temperature_buf = self.process_temperature_csv_export()
                    headers.append("Temperature (°C)")
                    data.append(np.array(csv_temperature_buf)[:, 1])
                np.savetxt(
                    filename[0] + ".csv",
                    np.column_stack(data),
                    delimiter=",",
                    header=",".join(headers),
                    fmt="%1.4f",
                    comments="",
                )
                print("Saved data in file " + filename[0] + ".csv")

    def process_temperature_csv_export(self):
        processed_temperature_buf = []
        ind = 0
        len_power_buf = len(self.rail_buf[-1]["voltage"])
        len_temp_buf = len(self.temperature_buf)
        for i in range(1, len_power_buf):
            processed_temperature_buf.append(self.temperature_buf[ind])
            if i == int((len_power_buf / len_temp_buf) * (ind + 1)):
                ind += 1
        return processed_temperature_buf

    def save_png(self):
        """saves the capture as png picture with specified name"""
        name = QtGui.QFileDialog.getSaveFileName(
            caption="Capture plot picture to (.png) file", filter="png"
        )
        if name[0]:
            filename = os.path.splitext(name[0])[0]
            filename += ".png"
            time.sleep(1)
            screen = QtGui.QApplication.primaryScreen()
            screenshot = screen.grabWindow(self.winId())
            screenshot.save(filename, "png")
            print("Saved image to: ", filename)

    def display_about(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("About")
        msg.setText(
            "Power Measurement Tool "
            + PROGRAM_VERSION
            + "\n"
            + COPYRIGHT_INFO
            + "\nLicense: BSD-3-Clause\nContact info: Create issue in PMT Github"
        )
        msg.exec()

    def start_record(self):
        """starts the timer if the user clicks on start button"""
        if self.state != "pause":
            if self.state == "reinit":
                self.stop_region.clear()
                drv_ftdi.T_START = time.time()
                drv_ftdi.DATA_LOCK.acquire()
                for rail in self.b.data_buf:
                    rail["current"] = [[0, 0]]
                    rail["voltage"] = [[0, 0]]
                drv_ftdi.DATA_LOCK.release()

                self.worker.resume_thread()
                self.timer.start(1000)

                if self.b.temperature_sensor:
                    drv_ftdi.TEMP_DATA_LOCK.acquire()
                    self.b.temp_buf = []
                    drv_ftdi.TEMP_DATA_LOCK.release()
                    if self.list_groups_t[0].isChecked():
                        self.global_graph_vb.addItem(self.list_temp_plot_main)
                        self.zoom_graph_vb.addItem(self.list_temp_plot_zoom)
                for i in range(len(self.list_group_plot_main)):
                    if self.list_groups_p[i].isChecked():
                        self.global_graph.addItem(self.list_group_plot_main[i])
                        self.zoom_graph.addItem(self.list_group_plot_zoom[i])
                for j in range(len(self.list_power_plot_main)):
                    if self.list_rails_p[j].isChecked():
                        self.global_graph.addItem(self.list_power_plot_main[j])
                        self.zoom_graph.addItem(self.list_power_plot_zoom[j])
                    if self.list_rails_c[j].isChecked():
                        self.global_graph.addItem(self.list_current_plot_main[j])
                        self.zoom_graph.addItem(self.list_current_plot_zoom[j])
                    if self.list_rails_v[j].isChecked():
                        self.global_graph_vb.addItem(self.list_voltage_plot_main[j])
                        self.zoom_graph_vb.addItem(self.list_voltage_plot_zoom[j])
                self.global_graph.addItem(self.zoom_region, ignoreBounds=True)
                self.traces_update()
                self.zoom_region.setRegion((0, 1))
                self.global_graph.setXRange(0, 1, padding=0)

            self.status_bar.showMessage("Recording")
            self.pause_but.setChecked(False)
            self.stop_but.setChecked(False)
            self.redo_but.setChecked(False)
            if self.state == "stop":
                self.worker.resume_thread()
                self.timer.start(1000)
                self.resume = time.time() - drv_ftdi.T_START
                region = pg.LinearRegionItem(
                    brush=QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)), movable=False
                )
                self.zoom_region.setZValue(10)
                region.setRegion((self.stop, self.resume))
                self.stop_region.append(region)
            self.state = "start"
        else:
            self.start_but.setChecked(True)

    def stop_record(self):
        """stops the capture and data collection (low-level) if the user clicks on stop button"""
        if self.state != "stop":
            self.status_bar.showMessage("Stop Recording")
            self.worker.pause_thread()
            self.pause_but.setChecked(False)
            self.start_but.setChecked(False)
            self.redo_but.setChecked(False)
            self.timer.stop()
            self.state = "stop"
            self.stop = time.time() - drv_ftdi.T_START
        else:
            self.stop_but.setChecked(True)

    def pause_record(self):
        """stops the capture refresh if the user clicks on pause button"""
        if self.state != "stop":
            if self.state != "pause":
                self.status_bar.showMessage("Pause Recording")
                self.start_but.setChecked(True)
                self.stop_but.setChecked(False)
                self.redo_but.setChecked(False)
                self.timer.stop()
                self.state = "pause"
            else:
                self.status_bar.showMessage("Recording")
                self.timer.start(1000)
                self.state = "start"

    def redo_record(self):
        """re initialization of the shared variable containing measured values"""
        self.stop_record()
        for rail in self.rail_buf:
            rail["current"] = np.zeros((2, 2), dtype=np.float16)
            rail["voltage"] = np.zeros((2, 2), dtype=np.float16)
        if self.b.temperature_sensor:
            self.temperature_buf = np.zeros((2, 2), dtype=np.float16)
        for group in self.groups_buf:
            group = []
        self.zoom_graph.clear()
        self.zoom_graph_vb.clear()
        self.global_graph.clear()
        self.global_graph_vb.clear()
        self.state = "reinit"

    def sh_global_data_window(self):
        """shows / hides global data window if user clicks in Windows menu bar item"""
        current_state = self.global_data_window.isVisible()
        self.global_data_window.setVisible(not current_state)
        if self.global_data_window.isVisible():
            self.global_data_window.update_data()

    def sh_zoom_data_window(self):
        """shows / hides zoom data window if user clicks in Windows menu bar item"""
        current_state = self.zoom_data_window.isVisible()
        self.zoom_data_window.setVisible(not current_state)
        if self.zoom_data_window.isVisible():
            self.update_zoom_data()

    def sh_mouse_pointer_data_window(self):
        """shows / hides mouse pointer data window if user clicks in Windows menu bar item"""
        current_state = self.mouse_pointer_window.isVisible()
        self.mouse_pointer_window.setVisible(not current_state)
        if self.mouse_pointer_window.isVisible():
            self.proxy1 = pg.SignalProxy(
                self.zoom_graph.scene().sigMouseMoved,
                rateLimit=20,
                slot=self.mousemoved_zoom_graph,
            )
            self.proxy2 = pg.SignalProxy(
                self.global_graph.scene().sigMouseMoved,
                rateLimit=20,
                slot=self.mousemove_global_graph,
            )
        else:
            self.proxy1.disconnect()
            self.proxy2.disconnect()

    def board_reset(self):
        """calls low level function for resetting board"""
        print("Not implemented yet")

    def board_onoff(self):
        """calls low level function for suspend / resume board"""
        print("Not implemented yet")

    def hardware_filter(self):
        self.b.pac_hw_filter()

    def pac_bipolar(self):
        self.b.pac_set_bipolar()

    def start_setup(self):
        """setup of the application"""
        self.setCentralWidget(self.central_widget)
        self.centralWidget().setLayout(self.global_lay)

        if self.args.load:
            self.setWindowTitle("Power Measurement Tool Offline")
            print("Reading %s file..." % self.args.load)
            if self.args.load.split(".")[-1] == "csv":
                with open(self.args.load, mode="r") as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=",")
                    self.b.rails_to_display = []
                    self.b.power_groups = []
                    first_run = True
                    for row in csv_reader:
                        if first_run:
                            last_el = ""
                            for r in row[1:]:
                                if r.split(" ")[0] == last_el:
                                    pass
                                elif not (
                                    "GROUP" in r.split(" ")[0]
                                    or "Temperature" in r.split(" ")[0]
                                ):
                                    self.b.rails_to_display.append(
                                        {"name": r.split(" ")[0]}
                                    )
                                    self.rail_buf.append(
                                        {
                                            "railnumber": r.split(" ")[0],
                                            "current": np.array(
                                                [[0, 0]], dtype=np.float16
                                            ),
                                            "voltage": np.array(
                                                [[0, 0]], dtype=np.float16
                                            ),
                                        }
                                    )
                                    last_el = r.split(" ")[0]
                                elif "GROUP" in r.split(" ")[0]:
                                    self.b.power_groups.append(
                                        {"name": r.split(" ")[0]}
                                    )
                                    self.groups_buf.append(
                                        {
                                            "group_name": r.split(" ")[0],
                                            "power": np.array(
                                                [[0, 0]], dtype=np.float16
                                            ),
                                        }
                                    )
                                    last_el = r.split(" ")[0]
                                elif "Temperature" in r.split(" ")[0]:
                                    self.b.temperature_sensor = True
                            first_run = False
                        else:
                            ind = 0
                            for i in range(1, len(self.rail_buf) * 3, 3):
                                self.rail_buf[ind]["current"] = np.append(
                                    self.rail_buf[ind]["current"],
                                    np.array(
                                        [[float(row[0]), float(row[i + 1])]],
                                        dtype=np.float16,
                                    ),
                                    axis=0,
                                )
                                self.rail_buf[ind]["voltage"] = np.append(
                                    self.rail_buf[ind]["voltage"],
                                    np.array(
                                        [[float(row[0]), float(row[i])]],
                                        dtype=np.float16,
                                    ),
                                    axis=0,
                                )
                                ind += 1

                            ind_g = 0
                            for i in range(1, len(self.groups_buf) + 1):
                                self.groups_buf[ind_g]["power"] = np.append(
                                    self.groups_buf[ind_g]["power"],
                                    np.array(
                                        [[row[0], row[(ind * 3) + i]]], dtype=np.float16
                                    ),
                                    axis=0,
                                )
                                ind_g += 1

                            if self.b.temperature_sensor:
                                self.temperature_buf.append(
                                    [int(float(row[0])), int(float(row[-1]))]
                                )

            elif self.args.load.split(".")[-1] == "pmt":
                with open(self.args.load, mode="rb") as pkl_file:
                    self.rail_buf = pickle.load(pkl_file)
                    self.b.rails_to_display = []
                    for rail in self.rail_buf:
                        self.b.rails_to_display.append({"name": rail["railnumber"]})
                    try:
                        self.groups_buf = pickle.load(pkl_file)
                        self.b.power_groups = []
                        for group in self.groups_buf:
                            self.b.power_groups.append({"name": group["group_name"]})
                    except EOFError:
                        self.b.power_groups = []
                    try:
                        self.temperature_buf = pickle.load(pkl_file)
                        self.b.temperature_sensor = True
                    except EOFError:
                        self.temperature_buf = []
            else:
                print("Please enter valid file to load")

        if not self.args.load:
            for i, rail in enumerate(self.b.board_mapping_power):
                self.rail_buf.append(
                    {
                        "railnumber": rail["name"],
                        "current": [[0, 0]],
                        "voltage": [[0, 0]],
                    }
                )
            self.setWindowTitle("Power Measurement Tool Live Capture")
            self.menu_bar.setNativeMenuBar(False)
            self.filemenu = self.menu_bar.addMenu("File")
            self.save_pmt = self.filemenu.addAction(
                "Save capture as .pmt", self.save_pmt
            )
            self.save_csv = self.filemenu.addAction(
                "Save capture as .csv", self.save_csv
            )
            self.save_png = self.filemenu.addAction(
                "Save capture as .png", self.save_png
            )
            self.exit = self.filemenu.addAction("Exit")
            self.exit.triggered.connect(self.closeEvent)
            self.settingmenu = self.menu_bar.addMenu("Settings")
            self.settingmenu.setToolTipsVisible(True)
            self.en_hw_filter = QtWidgets.QAction(
                "Enable PAC hardware filter", self.settingmenu, checkable=True
            )
            self.en_hw_filter.setToolTip(
                "Use the PAC's rolling average of eight most recent measurements"
            )
            self.en_bipolar = QtWidgets.QAction(
                "Enable PAC bipolar values", self.settingmenu, checkable=True
            )
            self.en_bipolar.setToolTip(
                "Switch from 0mV -- +100mV range to -100mV -- +100mV"
            )
            self.en_hw_filter.setChecked(False)
            self.en_bipolar.setChecked(True)
            self.en_hw_filter.triggered.connect(self.hardware_filter)
            self.en_bipolar.triggered.connect(self.pac_bipolar)
            self.settingmenu.addAction(self.en_hw_filter)
            self.settingmenu.addAction(self.en_bipolar)

        self.winmenu = self.menu_bar.addMenu("Windows")
        self.winmenu.addAction(
            "Show / hide Global data window", self.sh_global_data_window
        )
        self.winmenu.addAction("Show / hide Zoom data window", self.sh_zoom_data_window)
        self.winmenu.addAction(
            "Show / hide Mouse Pointer data window", self.sh_mouse_pointer_data_window
        )

        self.helpmenu = self.menu_bar.addMenu("Help")
        self.about = self.helpmenu.addAction("About PMT", self.display_about)

        if not self.args.load:
            self.status_bar.showMessage("Recording")
            # self.board_controlmenu = self.menu_bar.addMenu('Board Control')
            # self.board_controlmenu.addAction("Reset board", self.board_reset)
            # self.board_controlmenu.addAction("On / Off board", self.board_onoff)

            self.tool_bar = self.addToolBar("tt")
            self.start_but = QtWidgets.QPushButton("")
            self.start_but.setIcon(QtGui.QIcon("docs/images/record.png"))
            self.start_but.setToolTip("Start capture")
            self.stop_but = QtWidgets.QPushButton("")
            self.stop_but.setIcon(QtGui.QIcon("docs/images/stop.png"))
            self.stop_but.setToolTip("Stop capturing data")
            self.pause_but = QtWidgets.QPushButton("")
            self.pause_but.setIcon(QtGui.QIcon("docs/images/pause.png"))
            self.pause_but.setToolTip("Stop monitor refresh")
            self.redo_but = QtWidgets.QPushButton("")
            self.redo_but.setIcon(QtGui.QIcon("docs/images/trash.png"))
            self.redo_but.setToolTip("Re-init capture")

            if self.b.temperature_sensor:
                self.temp_label = QtGui.QPushButton(" Current board temp: 0.0°C ")

            self.start_but.setCheckable(True)
            self.pause_but.setCheckable(True)
            self.stop_but.setCheckable(True)

            if self.b.temperature_sensor:
                self.spacer1.setSizePolicy(
                    QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
                )
                self.tool_bar.addWidget(self.spacer1)
                self.tool_bar.addWidget(self.temp_label)

            self.spacer.setSizePolicy(
                QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
            )
            self.tool_bar.addWidget(self.spacer)
            self.tool_bar.addWidget(self.start_but)
            self.tool_bar.addWidget(self.stop_but)
            self.tool_bar.addWidget(self.pause_but)
            self.tool_bar.addWidget(self.redo_but)

            self.start_but.clicked.connect(self.start_record)
            self.stop_but.clicked.connect(self.stop_record)
            self.pause_but.clicked.connect(self.pause_record)
            self.redo_but.clicked.connect(self.redo_record)

        self.rail_control = QtGui.QLabel("Rails")
        self.rail_control.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Black))

        self.button_lay.setAlignment(QtCore.Qt.AlignTop)
        self.label_loc = QtGui.QLabel("Rail name")
        self.label_p = QtGui.QCheckBox("P")
        self.label_v = QtGui.QCheckBox("V")
        self.label_c = QtGui.QCheckBox("I")
        self.label_res = QtGui.QLabel("Res")
        self.label_p.setChecked(True)

        if self.b.temperature_sensor:
            self.label_v.setEnabled(False)

        self.label_p.stateChanged.connect(self.hide_all_power)
        self.label_v.stateChanged.connect(self.hide_all_voltage)
        self.label_c.stateChanged.connect(self.hide_all_current)

        self.button_lay.addWidget(self.label_loc, 0, 0)
        self.button_lay.addWidget(self.label_p, 0, 2)
        self.button_lay.addWidget(self.label_v, 0, 3)
        self.button_lay.addWidget(self.label_c, 0, 4)
        self.button_lay.addWidget(self.label_res, 0, 5)

        for i, rail in enumerate(self.b.rails_to_display):

            self.list_power_plot_main.append(
                pg.PlotCurveItem(
                    [],
                    pen=COLORS[i],
                    skipFiniteCheck=True,
                    dynamicRangeLimit=None,
                    clipToView=True,
                )
            )
            self.list_power_plot_zoom.append(
                pg.PlotCurveItem(
                    [],
                    pen=COLORS[i],
                    skipFiniteCheck=True,
                    dynamicRangeLimit=None,
                    clipToView=True,
                )
            )

            self.list_current_plot_main.append(
                pg.PlotCurveItem(
                    [],
                    pen=pg.mkPen(COLORS[i], style=QtCore.Qt.DotLine),
                    skipFiniteCheck=True,
                    dynamicRangeLimit=None,
                    clipToView=True,
                )
            )
            self.list_current_plot_zoom.append(
                pg.PlotCurveItem(
                    [],
                    pen=pg.mkPen(COLORS[i], style=QtCore.Qt.DotLine),
                    skipFiniteCheck=True,
                    dynamicRangeLimit=None,
                    clipToView=True,
                )
            )

            self.list_voltage_plot_main.append(
                pg.PlotCurveItem(
                    [],
                    pen=pg.mkPen(COLORS[i], width=2, style=QtCore.Qt.DashDotDotLine),
                    skipFiniteCheck=True,
                    dynamicRangeLimit=None,
                )
            )
            self.list_voltage_plot_zoom.append(
                pg.PlotCurveItem(
                    [],
                    pen=pg.mkPen(COLORS[i], width=2, style=QtCore.Qt.DashDotDotLine),
                    skipFiniteCheck=True,
                    dynamicRangeLimit=None,
                )
            )

            self.global_graph.addItem(self.list_power_plot_main[i])
            self.zoom_graph.addItem(self.list_power_plot_zoom[i])

            but_name = QtGui.QPushButton(rail["name"])
            menu = QtGui.QMenu()
            hide_action = menu.addAction("Hide all plots")
            hide_action.triggered.connect(
                lambda init, i=i: self.hide_all_single_plot(i)
            )
            but_name.setMenu(menu)
            self.list_rails_label.append(but_name)

            if not self.args.load:
                if rail["rsense"][0] == rail["rsense"][1]:
                    res_but = QtGui.QPushButton("X")
                    res_but.setEnabled(False)
                    self.list_switch_res.append(res_but)
                else:
                    res_but = QtGui.QPushButton("H")
                    self.list_switch_res.append(res_but)
                    res_but.clicked.connect(
                        lambda init, i=i: self.switch_res_changed(i)
                    )
                self.button_lay.addWidget(self.list_switch_res[i], i + 1, 5)

            self.list_color_rails.append(pg.ColorButton(color=COLORS[i]))
            self.list_color_rails[i].setMinimumHeight(30)
            self.list_color_rails[i].setMinimumWidth(30)
            self.list_rails_p.append(QtGui.QCheckBox())
            self.list_rails_p[i].setChecked(True)
            self.list_rails_v.append(QtGui.QCheckBox())
            if self.b.temperature_sensor:
                self.list_rails_v[i].setEnabled(False)
            self.list_rails_c.append(QtGui.QCheckBox())
            self.button_lay.addWidget(self.list_rails_label[i], i + 1, 0)
            self.button_lay.addWidget(self.list_color_rails[i], i + 1, 1)
            self.button_lay.addWidget(self.list_rails_p[i], i + 1, 2)
            self.button_lay.addWidget(self.list_rails_v[i], i + 1, 3)
            self.button_lay.addWidget(self.list_rails_c[i], i + 1, 4)
            self.list_color_rails[i].sigColorChanged.connect(
                lambda init, i=i: self.change_color(i)
            )
            self.list_rails_p[i].stateChanged.connect(
                lambda init, i=i: self.power_changed(i)
            )
            self.list_rails_v[i].stateChanged.connect(
                lambda init, i=i: self.voltage_changed(i)
            )
            self.list_rails_c[i].stateChanged.connect(
                lambda init, i=i: self.current_changed(i)
            )

            self.list_right_lay_n.append(QtGui.QLabel(rail["name"]))
            self.list_right_lay_p.append(QtGui.QLabel(""))
            self.list_right_lay_v.append(QtGui.QLabel(""))
            self.list_right_lay_c.append(QtGui.QLabel(""))
            self.right_lay_rail.addWidget(self.list_right_lay_n[i], i + 1, 0)
            self.right_lay_rail.addWidget(self.list_right_lay_p[i], i + 1, 1)
            self.right_lay_rail.addWidget(self.list_right_lay_v[i], i + 1, 2)
            self.right_lay_rail.addWidget(self.list_right_lay_c[i], i + 1, 3)

        self.wid_rail_scrollbar.setLayout(self.button_lay)
        self.rail_scrollbar.setWidget(self.wid_rail_scrollbar)
        self.left_lay.addWidget(self.rail_control)
        self.left_lay.addWidget(self.rail_scrollbar)

        if self.b.power_groups:
            self.group_control = QtGui.QLabel("Groups")
            self.group_control.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Black))
            self.left_lay.addWidget(self.group_control)

            for i, group in enumerate(self.b.power_groups):

                self.list_group_plot_main.append(
                    pg.PlotCurveItem(
                        [],
                        pen=pg.mkPen(GROUPS_COLORS[i], width=3),
                        skipFiniteCheck=True,
                        dynamicRangeLimit=None,
                        clipToView=True,
                    )
                )
                self.list_group_plot_zoom.append(
                    pg.PlotCurveItem(
                        [],
                        pen=pg.mkPen(GROUPS_COLORS[i], width=3),
                        skipFiniteCheck=True,
                        dynamicRangeLimit=None,
                        clipToView=True,
                    )
                )

                self.list_groups_label.append(QtGui.QPushButton(group["name"]))
                self.list_color_groups.append(pg.ColorButton(color=GROUPS_COLORS[i]))
                self.list_color_groups[i].setMinimumHeight(30)
                self.list_color_groups[i].setMinimumWidth(30)
                self.list_groups_p.append(QtGui.QCheckBox())
                self.list_groups_p[i].setChecked(False)
                self.list_groups_p[i].stateChanged.connect(
                    lambda init, i=i: self.g_power_changed(i)
                )
                self.group_lay.addWidget(self.list_groups_label[i], i + 1, 0)
                self.group_lay.addWidget(self.list_color_groups[i], i + 1, 1)
                self.group_lay.addWidget(self.list_groups_p[i], i + 1, 2)
                self.list_color_groups[i].sigColorChanged.connect(
                    lambda init, i=i: self.change_color_g(i)
                )
                self.list_right_lay_group_n.append(QtGui.QLabel(group["name"]))
                self.list_right_lay_group_p.append(QtGui.QLabel(""))
                self.right_lay_group.addWidget(self.list_right_lay_group_n[i], i + 1, 0)
                self.right_lay_group.addWidget(self.list_right_lay_group_p[i], i + 1, 1)

                self.group_lay.setAlignment(QtCore.Qt.AlignTop)
            self.left_lay.addLayout(self.group_lay)

        if self.b.temperature_sensor:
            self.global_graph_vb.addItem(
                pg.PlotCurveItem(
                    [],
                    pen=pg.mkPen(
                        TEMP_COLORS[0], width=2, style=QtCore.Qt.DashDotDotLine
                    ),
                    skipFiniteCheck=True,
                    dynamicRangeLimit=None,
                )
            )
            self.zoom_graph_vb.addItem(
                pg.PlotCurveItem(
                    [],
                    pen=pg.mkPen(
                        TEMP_COLORS[0], width=2, style=QtCore.Qt.DashDotDotLine
                    ),
                    skipFiniteCheck=True,
                    dynamicRangeLimit=None,
                )
            )

            self.list_temp_plot_main = self.global_graph_vb.addedItems[-1]
            self.list_temp_plot_zoom = self.zoom_graph_vb.addedItems[-1]

            self.temperature_control = QtGui.QLabel("Board Temperature Sensor")
            self.temperature_control.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Black))
            self.left_lay.addWidget(self.temperature_control)

            self.list_temperature_label.append(QtGui.QPushButton("TEMPERATURE"))
            self.list_color_temperature.append(pg.ColorButton(color=TEMP_COLORS[0]))
            self.list_color_temperature[0].setMinimumHeight(30)
            self.list_color_temperature[0].setMinimumWidth(30)
            self.list_groups_t.append(QtGui.QCheckBox())
            self.list_groups_t[0].setChecked(True)
            self.list_groups_t[0].stateChanged.connect(self.temperature_changed)
            self.temperature_lay.addWidget(self.list_temperature_label[0], 1, 0)
            self.temperature_lay.addWidget(self.list_color_temperature[0], 1, 1)
            self.temperature_lay.addWidget(self.list_groups_t[0], 1, 2)
            self.list_color_temperature[0].sigColorChanged.connect(self.change_color_t)
            self.temperature_lay.setAlignment(QtCore.Qt.AlignTop)
            self.left_lay.addLayout(self.temperature_lay)

        self.global_lay.addLayout(self.left_lay)
        self.global_graph.disableAutoRange()
        # self.global_graph.setDownsampling(ds=True, auto=True, mode='peak')
        self.global_graph.setMouseEnabled(x=True, y=False)
        self.global_graph_pi.showAxis("right")
        self.global_graph_pi.scene().addItem(self.global_graph_vb)
        self.global_graph_pi.getAxis("right").linkToView(self.global_graph_vb)
        self.global_graph_vb.setXLink(self.global_graph_pi)
        if self.b.temperature_sensor:
            self.global_graph.setLabels(
                left="Power (mW) / Current (mA) ",
                bottom="Time (sec)",
                right="Temperature (°C)",
            )
        else:
            self.global_graph.setLabels(
                left="Power (mW) / Current (mA) ",
                bottom="Time (sec)",
                right="Voltage (V)",
            )
        self.global_graph.addLine(y=0)
        self.global_graph.showGrid(x=True, y=True, alpha=0.30)
        self.plot_lay.addWidget(self.global_graph, 0, 0)
        self.global_graph.addItem(self.zoom_region, ignoreBounds=True)

        self.zoom_graph.setClipToView(False)
        self.zoom_graph.setMouseEnabled(x=True, y=False)
        self.zoom_graph_pi.showAxis("right")
        self.zoom_graph_pi.scene().addItem(self.zoom_graph_vb)
        self.zoom_graph_pi.getAxis("right").linkToView(self.zoom_graph_vb)
        self.zoom_graph_vb.setXLink(self.zoom_graph_pi)
        if self.b.temperature_sensor:
            self.zoom_graph.setLabels(
                left="Power (mW) / Current (mA)",
                bottom="Time (sec)",
                right="Temperature (°C)",
            )
        else:
            self.zoom_graph.setLabels(
                left="Power (mW) / Current (mA)",
                bottom="Time (sec)",
                right="Voltage (V)",
            )
        self.zoom_graph.enableAutoRange("y")
        self.zoom_graph.setAutoVisible(y=True)
        self.zoom_graph.addLine(y=0)
        self.zoom_graph.showGrid(x=True, y=True, alpha=0.30)
        self.plot_lay.addWidget(self.zoom_graph, 1, 0)

        if self.args.load:
            self.zoom_graph.enableAutoRange("y")
            self.global_graph.enableAutoRange("y")

        self.zoom_region.setZValue(10)
        self.global_lay.addLayout(self.plot_lay, 2)

        self.zoom_graph.sigRangeChanged.connect(self.update_zoom_region)
        self.zoom_region.sigRegionChanged.connect(self.update_zoom_graph)
        self.zoom_graph_pi.vb.sigResized.connect(self.update_zoom_view)
        self.global_graph_pi.vb.sigResized.connect(self.update_global_view)

        if self.b.power_groups:
            self.right_group = QtGui.QLabel("GROUPS")
            self.right_group.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Black))
            self.right_lay_group.addWidget(QtGui.QLabel("Name"), 0, 0)
            self.right_lay_group.addWidget(QtGui.QLabel("P_avg"), 0, 1)
            self.right_lay.addWidget(self.right_group)
            self.right_lay.addLayout(self.right_lay_group)

        self.right_rail = QtGui.QLabel("RAILS")
        self.right_rail.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Black))
        self.right_lay_rail.addWidget(QtGui.QLabel("Name"), 0, 0)
        self.right_lay_rail.addWidget(QtGui.QLabel("P_avg"), 0, 1)
        self.right_lay_rail.addWidget(QtGui.QLabel("V_avg"), 0, 2)
        self.right_lay_rail.addWidget(QtGui.QLabel("I_avg"), 0, 3)
        self.right_lay.addWidget(self.right_rail)
        self.right_lay.addLayout(self.right_lay_rail)
        self.right_lay.addStretch(1)

        self.global_lay.addLayout(self.right_lay)

        self.global_data_window = GlobalDataWin(self)
        self.zoom_data_window = ZoomDataWin(self)
        self.mouse_pointer_window = MPDataWin(self)
        self.zoom_data_window.setWindowTitle("Zoom Data Window")
        self.mouse_pointer_window.setWindowTitle("Mouse Pointer Data Window")

        self.setFixedSize(self.global_lay.sizeHint())

        if not self.args.load:
            self.worker.moveToThread(self.thread_data)
            self.thread_data.started.connect(self.worker.do_work)
            self.thread_data.finished.connect(self.thread_data.deleteLater)
            self.thread_data.start()
            if self.b.temperature_sensor:
                self.worker_temperature.moveToThread(self.thread_temperature)
                self.thread_temperature.started.connect(self.worker_temperature.do_work)
                self.thread_temperature.finished.connect(
                    self.thread_temperature.deleteLater
                )
                self.thread_temperature.start()

            self.thread_process_data.sig_update_gui.connect(self.traces_update)
            self.thread_process_data.sig_update_instant_temp.connect(
                self.update_instant_temp
            )
            self.thread_process_data.finished.connect(self.thread_process_data.quit)
            self.timer.timeout.connect(self.thread_process_data.start)
            self.timer.start(1000)
            self.start_but.setChecked(True)
        else:
            self.traces_update()


def run_ui(board, args):
    """starts the GUI application"""
    app = QtGui.QApplication([])
    display = GUI(board, args)
    display.show()
    QtGui.QApplication.instance().exec_()
