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

import threading
import copy
import time
import curses
import sys

import numpy as np

import drv_ftdi


MAIN_INFOS = [" Voltage (V) ", " Current (mA) ", " Power (mW) "]
MAIN_INFOS_PLACE = [1, 41, 81]
SUB_INFOS = ["now ", "avg ", "min ", "max "]
SUB_INFOS_PLACE = [1, 11, 21, 31]


def run_ui(board, args):
    """runs TUI and collects data in a thread"""
    rail_data = []
    rail_buf = []
    temp_data = []
    v_now, c_now, p_now = (0 for i in range(3))
    v_min = []
    c_min = []
    p_min = []
    v_max = []
    c_max = []
    p_max = []

    stdscr = curses.initscr()
    num_rows, num_cols = stdscr.getmaxyx()
    if num_rows < 38 or num_cols < 160:
        curses.endwin()
        print("ERROR : Terminal size is too small for TUI!")
        sys.exit()
    thread_process = threading.Thread(target=board.get_data)
    thread_process.start()
    time.sleep(1)
    time_start = time.time()
    if board.temperature_sensor:
        time.sleep(0.2)
        thread_temperature = threading.Thread(target=board.process_temperature)
        thread_temperature.start()
    curr_time = 0
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    curses.start_color()
    stdscr.nodelay(1)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    for i, rail in enumerate(board.board_mapping_power):
        rail_buf.append(
            {
                "railnumber": rail["name"],
                "current": np.array([[0, 0]], dtype=np.float16),
                "voltage": np.array([[0, 0]], dtype=np.float16),
            }
        )
    # set static informations
    stdscr.border(0)
    stdscr.addstr(0, int(num_cols / 2), "Power Measurements Tool", curses.A_BOLD)

    # get the longest power probe name for correctly display it and init values
    longest_probe_name = 0
    for power_probes in board.rails_to_display:
        v_min.append(9999)
        c_min.append(9999)
        p_min.append(9999)
        v_max.append(0)
        c_max.append(0)
        p_max.append(0)
        longest_probe_name = (
            len(power_probes["name"])
            if len(power_probes["name"]) > longest_probe_name
            else longest_probe_name
        )
    longest_probe_name += 5

    # display main and sub-infos
    num_info = 0
    for i in MAIN_INFOS:
        k = 0
        stdscr.addstr(
            2,
            longest_probe_name + MAIN_INFOS_PLACE[num_info],
            i,
            curses.color_pair(num_info),
        )
        for sub in SUB_INFOS:
            stdscr.addstr(
                3,
                longest_probe_name + MAIN_INFOS_PLACE[num_info] + SUB_INFOS_PLACE[k],
                sub,
                curses.color_pair(num_info),
            )
            k += 1
        num_info += 1

    stdscr.addstr(
        2,
        longest_probe_name + MAIN_INFOS_PLACE[2] + 45,
        " Resistance Lvl",
        curses.color_pair(4),
    )

    stdscr.addstr(3, 1, "Location")
    stdscr.hline(4, 1, "-", 160)
    # end of static informations init

    # parse power_board of entered board and display it
    probe_number = 0
    while probe_number < len(board.rails_to_display):
        maj_min = 65 if probe_number < 26 else 71
        stdscr.addstr(
            5 + probe_number,
            1,
            chr(maj_min + probe_number)
            + ". "
            + board.rails_to_display[probe_number]["name"],
        )
        stdscr.addstr(5 + probe_number, longest_probe_name, "|", curses.color_pair(5))
        probe_number += 1

    if board.power_groups:
        group_ind = probe_number
        for ind, group in enumerate(board.power_groups):
            stdscr.addstr(6 + probe_number, 1, group["name"])
            probe_number += 1

    stdscr.addstr(10 + probe_number, 1, "Hot-key command:")
    stdscr.addstr(
        11 + probe_number,
        1,
        "1 : reset Avg and Max/Min ;  2 : Use PAC avg values ; 3 : Use PAC bipolar values ; Rail_letter : "
        "Switch res rail ; 0 : quit ",
    )
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(12 + probe_number, 1, "Bold values are in mV and uA / uW ")
    stdscr.attroff(curses.A_BOLD)
    # Update collected datas and updated view while q is not pressed
    while True:
        try:
            remote_buf = []
            drv_ftdi.DATA_LOCK.acquire()
            for remote_rail in board.data_buf:
                remote_buf.append(copy.deepcopy(remote_rail))
                remote_rail["current"] = [[0, 0]]
                remote_rail["voltage"] = [[0, 0]]
            drv_ftdi.DATA_LOCK.release()

            for rail in remote_buf:
                local_rail = next(
                    (
                        item
                        for item in rail_buf
                        if item["railnumber"] == rail["railnumber"]
                    ),
                    None,
                )
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
            if board.temperature_sensor:
                drv_ftdi.TEMP_DATA_LOCK.acquire()
                temp_data = (
                    copy.deepcopy(board.temp_buf[-1][1])
                    if len(board.temp_buf) != 0
                    else 0
                )
                drv_ftdi.TEMP_DATA_LOCK.release()
            char = stdscr.getch()
            if char == ord("0"):
                drv_ftdi.FLAG_UI_STOP = True
                break
            if char == ord("1"):
                for index, rail in enumerate(board.rails_to_display):
                    v_min[index] = 9999
                    c_min[index] = 9999
                    p_min[index] = 9999
                    v_max[index] = 0
                    c_max[index] = 0
                    p_max[index] = 0
                drv_ftdi.DATA_LOCK.acquire()
                for rail in board.data_buf:
                    rail["current"] = [[0, 0]]
                    rail["voltage"] = [[0, 0]]
                drv_ftdi.DATA_LOCK.release()
                for rail in rail_buf:
                    rail["current"] = [[0, 0]]
                    rail["voltage"] = [[0, 0]]
                v_avg = 0
                c_avg = 0
                p_avg = 0
                drv_ftdi.T_START = time.time()
                time_start = time.time()
            if char == ord("2"):
                board.pac_hw_filter()
            if char == ord("3"):
                board.pac_set_bipolar()
            if chr(char + 1).isalpha():
                railnumber = char - 65 if char <= 90 else char - 71
                if railnumber < probe_number:
                    if (
                        board.rails_to_display[railnumber]["rsense"][0]
                        != board.rails_to_display[railnumber]["rsense"][1]
                    ):
                        rail = next(
                            (
                                item
                                for item in rail_buf
                                if item["railnumber"]
                                == board.rails_to_display[railnumber]["name"]
                            ),
                            None,
                        )
                        board.switch_res(rail, railnumber)
            for index, d_rail in enumerate(board.rails_to_display):
                rail = next(
                    (item for item in rail_buf if item["railnumber"] == d_rail["name"]),
                    None,
                )
                rail2 = next(
                    (
                        item
                        for item in board.board_mapping_power
                        if item["name"] == d_rail["name"]
                    ),
                    None,
                )
                if rail and len(rail["voltage"]) > 2:
                    v_now = rail["voltage"][-1, 1]
                    rail_data.append(v_now)
                    v_avg = rail["voltage"][1:, 1].mean(0)
                    rail_data.append(v_avg)
                    v_min[index] = v_now if v_now < v_min[index] else v_min[index]
                    rail_data.append(v_min[index])
                    v_max[index] = v_now if v_now > v_max[index] else v_max[index]
                    rail_data.append(v_max[index])

                    c_now = rail["current"][-1, 1]
                    rail_data.append(c_now)
                    c_avg = rail["current"][1:, 1].mean(0)
                    rail_data.append(c_avg)
                    c_min[index] = c_now if c_now < c_min[index] else c_min[index]
                    rail_data.append(c_min[index])
                    c_max[index] = c_now if c_now > c_max[index] else c_max[index]
                    rail_data.append(c_max[index])

                    p_now = v_now * c_now
                    rail_data.append(p_now)
                    p_avg = v_avg * c_avg
                    rail_data.append(p_avg)
                    p_min[index] = p_now if p_now < p_min[index] else p_min[index]
                    rail_data.append(p_min[index])
                    p_max[index] = p_now if p_now > p_max[index] else p_max[index]
                    rail_data.append(p_max[index])

                    for ind, group in enumerate(board.power_groups):
                        power_group = np.zeros([1, 2], dtype=np.float16)
                        for rail_group in group["rails"]:
                            rail = next(
                                (
                                    item
                                    for item in rail_buf
                                    if item["railnumber"] == rail_group
                                ),
                                None,
                            )
                            power_rail = np.empty_like(rail["voltage"][1:])
                            power_rail[:, 0] = rail["voltage"][1:, 0]
                            power_rail[:, 1] = (
                                rail["voltage"][1:, 1] * rail["current"][1:, 1]
                            )
                            if power_group.shape[0] > power_rail.shape[0]:
                                power_group.resize(power_rail.shape)
                            elif power_rail.shape[0] - power_group.shape[0] <= 2:
                                power_rail.resize(power_group.shape)
                            power_group = power_group + power_rail
                        power_group[:, 0] = power_rail[:, 0]
                        avg_power_group = power_group[:, 1].mean()
                        min_power_group = power_group[:, 1].min()
                        max_power_group = power_group[:, 1].max()
                        stdscr.addstr(
                            6 + group_ind + ind,
                            20,
                            "avg power: " + str("%.2f" % avg_power_group),
                        )
                        stdscr.addstr(
                            6 + group_ind + ind,
                            40,
                            "min power: " + str("%.2f" % min_power_group),
                        )
                        stdscr.addstr(
                            6 + group_ind + ind,
                            60,
                            "max power: " + str("%.2f" % max_power_group),
                        )

                    ind_s = 0
                    for ind_m in range(len(MAIN_INFOS)):
                        for i in range(len(SUB_INFOS)):
                            stdscr.attron(curses.color_pair(ind_m))
                            if rail_data[ind_m + ind_s] < 1.0:
                                stdscr.attron(curses.A_BOLD)
                                stdscr.addstr(
                                    5 + index,
                                    longest_probe_name
                                    + MAIN_INFOS_PLACE[ind_m]
                                    + SUB_INFOS_PLACE[i],
                                    str("%.2f" % (rail_data[ind_m + ind_s] * 1000)),
                                )
                                stdscr.attroff(curses.A_BOLD)
                            else:
                                stdscr.addstr(
                                    5 + index,
                                    longest_probe_name
                                    + MAIN_INFOS_PLACE[ind_m]
                                    + SUB_INFOS_PLACE[i],
                                    str("%.2f" % rail_data[ind_m + ind_s]),
                                )
                            stdscr.attroff(curses.color_pair(ind_m))
                            stdscr.clrtoeol()
                            ind_s += 1
                        ind_s -= 1
                    col = 3 if rail2["rsense"][0] != rail2["rsense"][1] else 4
                    stdscr.addstr(
                        5 + index,
                        longest_probe_name + MAIN_INFOS_PLACE[2] + 45,
                        str(drv_ftdi.CURR_RSENSE.get(rail2["name"])),
                        curses.color_pair(col),
                    )
                    stdscr.clrtoeol()
                    curr_time = time.time() - time_start
                    stdscr.addstr(
                        7 + probe_number,
                        1,
                        "Duration : "
                        + str("%.2f" % curr_time)
                        + " sec"
                        + " ; Frequency : "
                        + str(
                            "%.1f" % (rail["voltage"].shape[0] / rail["voltage"][-1, 0])
                        )
                        + "Hz",
                    )
                    if board.temperature_sensor:
                        stdscr.addstr(
                            7 + probe_number,
                            41,
                            " ; Board Temperature: " + str("%.2f" % temp_data) + " C",
                        )
                    stdscr.clrtoeol()
                    stdscr.addstr(
                        8 + probe_number,
                        1,
                        "avg_values: "
                        + str(board.params["hw_filter"])
                        + " ; bipolar mode: "
                        + str(board.params["bipolar"]),
                    )
                    stdscr.clrtoeol()
                    rail_data.clear()
                    stdscr.refresh()
            if args.time:
                if curr_time >= int(args.time):
                    drv_ftdi.FLAG_UI_STOP = True
                    break
            time.sleep(0.1)
        except KeyboardInterrupt:
            drv_ftdi.FLAG_UI_STOP = True
            break
    curses.nocbreak()
    curses.curs_set(1)
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    if args.dump:
        file, _, ext = args.dump.partition(".")
        if ext:
            name = file + "." + ext
        else:
            name = file + ".csv"
        headers = []
        data = []
        type_data = ["voltage", "current", "power"]
        type_data_unit = [" (V)", " (mA)", " (mW)"]
        array_size = rail_buf[-1]["voltage"].shape[0]
        data.append(rail_buf[0]["voltage"][1:array_size, 0])
        headers.append("Time (ms)")
        for d_rail in board.rails_to_display:
            rail = next(
                (item for item in rail_buf if item["railnumber"] == d_rail["name"]),
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
        if board.power_groups:
            power_group = np.zeros([1, 2], dtype=np.float16)
            for group in board.power_groups:
                headers.append(group["name"] + " power (mW)")
                for rail_group in group["rails"]:
                    rail = next(
                        (item for item in rail_buf if item["railnumber"] == rail_group),
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
        np.savetxt(
            name,
            np.column_stack(data),
            delimiter=",",
            header=",".join(headers),
            fmt="%1.4f",
            comments="",
        )
        print("Saved data in file " + name)
