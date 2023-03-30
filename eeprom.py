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

import oyaml as yaml
import sys
import time
from collections import OrderedDict
import eeprom_mapping_table
import common_function as common_func
from board_configuration import common


if common_func.OS == "Linux":
    from pyftdi import ftdi
elif common_func.OS == "Windows":
    import ftd2xx as ftdi


class FTDIEeprom:
    def __init__(self, args):
        self.args = args
        self.eeprom_info = OrderedDict(
            [
                ("CONFIG_FLAG", None),
                ("BOARD_ID", None),
                ("BOARD_REV", None),
                ("SOC_ID", None),
                ("SOC_REV", None),
                ("PMIC_ID", None),
                ("PMIC_REV", None),
                ("NBR_PWR_RAILS", None),
                ("BOARD_SN", None),
            ]
        )
        self.file_info = []
        self.device = None
        self.type = None  # 0 for serial and 1 for I2C

    def deinit(self):
        self.device.close()

    def detect_type(self, id, dev):
        if common_func.OS == "Linux":
            serial_number = dev[0][4]
            self.type = 1 if serial_number is None else 0
            return self.type, dev[0]
        elif common_func.OS == "Windows":
            device = ftdi.openEx(dev['location'], ftdi.defines.OPEN_BY_LOCATION)
            try:
                device.eeRead()
            except:
                self.type = 1
            else:
                self.type = 0
            device.close()
            return self.type, dev

    def init_system(self, desc, ind):
        if self.type == 1:  # i2c mode
            self.device = common_func.ftdi_open(ind, 1, desc)
            common_func.ftdic_setbitmode(self.device, 0x0, 0x00)
            common_func.ftdic_setbitmode(self.device, 0x0, 0x02)
        else:  # serial mode
            if common_func.OS == "Windows":
                self.device = common_func.ftdi_open(ind, 0, desc)
            elif common_func.OS == "Linux":
                self.device = ftdi.Ftdi()
                self.device.open(vendor=desc[0], product=desc[1], address=desc[3])

    def show_devices(self):
        dev_ = self.list_eeprom_devices()
        for ind, dev in enumerate(dev_):
            print("ID: " + str(ind) + " --> " + str(dev))

    def list_eeprom_devices(self):
        dev = []
        if common_func.OS == "Linux":
            self.device = ftdi.Ftdi()
            tmp = self.device.list_devices()
            dev = sorted(tmp, key=lambda tup: tup[0][3], reverse=True)
            return dev
        elif common_func.OS == "Windows":
            n = ftdi.listDevices()
            if n is not None:
                for i, d in enumerate(n):
                    if d != b"":
                        if chr(d[-1]) == "A":
                            dev.append(ftdi.getDeviceInfoDetail(i))
                else:
                    pass
            return dev

    def collect_eeprom_info(self):
        with open(self.args.file, "r") as file:
            datas = yaml.safe_load(file)
            for item, value in datas.items():
                if any(i in item for i in ["BOARD_ID", "SOC_ID", "PMIC_ID"]):
                    for cpt in eeprom_mapping_table.INFOS:
                        if cpt["name"] == item:

                            code = next(
                                (
                                    key
                                    for key, val in cpt["datas"].items()
                                    if val == str(value)
                                ),
                                "0x7f",
                            )
                            self.file_info.append([item, code])
                            break
                else:
                    if value == "NOT FOUND":
                        self.file_info.append([item, "0x7f"])
                        continue
                    if "BOARD_SN" in item or "NBR_PWR_RAILS" in item:
                        self.file_info.append([item, hex(value + 1)])
                    else:
                        rev_l = ord(value[0]) - ord("A") + 1
                        rev_n = int(value[1]) + 1
                        rev = hex((rev_l << 4) + rev_n)
                        self.file_info.append([item, rev])

    def read_eeprom_board_id_rev(self, pins=None):
        board_id_index = 1
        if self.type == 0:
            if common_func.OS == "Linux":
                out = self.device.read_eeprom(addr=0x1A, length=3)
                soc = hex(((out[0] & 0xFC) >> 2) | ((out[1] - 1) << 6))
                rev = (
                    chr((out[2] >> 4) + ord("A") - 1) + str((out[2] & 0xF) - 1)
                    if (out[2] != 0x7F and out[2] != 0xFF)
                    else "Unknown"
                )
                return (
                    eeprom_mapping_table.INFOS[board_id_index]["datas"].get(
                        soc, "Unknown"
                    ),
                    rev,
                )
            elif common_func.OS == "Windows":
                out = self.device.eeUARead(3)
                if len(out) == 0:
                    print(
                        "\n!! EEPROM content is empty, please flash it with EEPROM Programmer Tool !!\n"
                    )
                    return "Unknown", "Unknown"
                soc = hex(((out[0] & 0xFC) >> 2) | ((out[1] - 1) << 6))
                rev = (
                    chr((out[2] >> 4) + ord("A") - 1) + str((out[2] & 0xF) - 1)
                    if (out[2] != 0x7F and out[2] != 0xFF)
                    else "Unknown"
                )
                return (
                    eeprom_mapping_table.INFOS[board_id_index]["datas"].get(
                        soc, "Unknown"
                    ),
                    rev,
                )
        else:
            out = self.read_eeprom_i2c(pins)
            soc = hex(((out[0][0] & 0xFC) >> 2) | ((out[1][0] - 1) << 6))
            rev = (
                chr((out[2][0] >> 4) + ord("A") - 1) + str((out[2][0] & 0xF) - 1)
                if (out[2] != 0x7F and out[2] != 0xFF)
                else "Unknown"
            )
            return (
                eeprom_mapping_table.INFOS[board_id_index]["datas"].get(soc, "Unknown"),
                rev,
            )

    def display_eeprom_info(self):
        i = 0
        for info, data in self.eeprom_info.items():
            if any(i in info for i in ["BOARD_ID", "SOC_ID", "PMIC_ID", "CONFIG_FLAG"]):
                print(
                    info
                    + ": "
                    + eeprom_mapping_table.INFOS[i]["datas"].get(data, "Unknown")
                )
                i += 1
            else:
                print(f"{info}: {data}")

    def read(self, id):
        dev_list = self.list_eeprom_devices()
        if not dev_list:
            print("ERROR: Board not detected or connected... Leaving.")
            return
        if id >= len(dev_list):  # board Id specified is higher than boards connected
            print("ERROR: Board ID passed in command line doesn't exist... Leaving.")
            return
        if (
            id == -1 and len(dev_list) > 1
        ):  # no board id specified but different boards connected
            print(
                "ERROR: Different boards are connected, please specify board ID... Leaving."
            )
            return
        if (
            id == -1 and len(dev_list) == 1
        ):  # one board connected and no board id specified
            id = 0
        __, desc = self.detect_type(id, dev_list[id])
        self.init_system(desc, id)
        if self.type == 0:
            print("** Reading serial EEPROM ...\n")
            self.read_eeprom_serial()
            self.deinit()
            print("\n** Done.")
        else:
            print(
                "I2C EEPROM - Which board are you using ? ( (1) imx8dxlevk / (2) imx8mpevkpwr(a0 / a1) )"
            )
            char = sys.stdin.read(1)
            if char == "1" or char == "2":
                print("** Reading I2C EEPROM ...\n")
                self.read_eeprom_seq(int(char) - 1)
                self.deinit()
                print("\n** Done.")
            else:
                print("ABORTED.")

    def read_eeprom_serial(self):
        if common_func.OS == "Linux":
            ret_data = self.device.read_eeprom(addr=0x1A, length=10)
        elif common_func.OS == "Windows":
            ret_data = self.device.eeUARead(10)
        if len(ret_data) == 0:
            print(
                "\n!! EEPROM content is empty, please flash it with EEPROM Programmer Tool !!\n"
            )
            return
        self.eeprom_info["CONFIG_FLAG"] = hex(ret_data[0] & 0x01)
        self.eeprom_info["BOARD_ID"] = hex(
            ((ret_data[0] & 0xFC) >> 2) | ((ret_data[1] - 1) << 6)
        )
        self.eeprom_info["BOARD_REV"] = (
            chr((ret_data[2] >> 4) + ord("A") - 1) + str((ret_data[2] & 0xF) - 1)
            if (ret_data[2] != 0x7F and ret_data[2] != 0xFF)
            else "Unknown"
        )
        self.eeprom_info["SOC_ID"] = hex(ret_data[3])
        self.eeprom_info["SOC_REV"] = (
            chr((ret_data[4] >> 4) + ord("A") - 1) + str((ret_data[4] & 0xF) - 1)
            if (ret_data[4] != 0x7F and ret_data[4] != 0xFF)
            else "Unknown"
        )
        self.eeprom_info["PMIC_ID"] = hex(ret_data[5])
        self.eeprom_info["PMIC_REV"] = (
            chr((ret_data[6] >> 4) + ord("A") - 1) + str((ret_data[6] & 0xF) - 1)
            if (ret_data[6] != 0x7F and ret_data[6] != 0xFF)
            else "Unknown"
        )
        self.eeprom_info["NBR_PWR_RAILS"] = (
            int(ret_data[7] - 1) if (ret_data[7] <= 254) else "Unknown"
        )
        self.eeprom_info["BOARD_SN"] = (
            int(((ret_data[9] - 1) << 8) + ((ret_data[8] - 1)))
            if ((((ret_data[9] - 1) << 8) + ((ret_data[8] - 1))) >= 1)
            else "Unknown"
        )
        self.display_eeprom_info()

    def write(self, id):
        id = 0 if id == -1 else id
        dev_list = self.list_eeprom_devices()
        if not dev_list:
            print("ERROR: Board not detected or connected... Leaving.")
            return
        __, desc = self.detect_type(id, dev_list[id])
        self.init_system(desc, id)
        self.collect_eeprom_info()
        print("** Info collected.\n")
        print(
            "/!\ You are going to overwrite EEPROM content, want to continue? Y/y/N/n"
        )
        char = sys.stdin.read(1)
        if char == "Y" or char == "y":
            if self.type == 0:
                print("** Writing to serial EEPROM ...")
                self.write_eeprom_serial()
                self.deinit()
                print("** Done.")
            else:
                print(
                    "I2C EEPROM - Which board are you using ? ( (1) imx8dxlevk / (2) imx8mpevkpwr(a0 / a1) )"
                )
                char = sys.stdin.read(2)
                if char[1] == "1" or char[1] == "2":
                    print("** Writing to I2C EEPROM ...")
                    self.write_eeprom_page_i2c(int(char) - 1)
                    self.deinit()
                    print("** Done.")
                else:
                    print("ABORTED.")
        else:
            print("ABORTED.")

    def write_eeprom_serial(self):
        infos = []
        for info in self.file_info:
            info[1] = int(info[1], 16)
            if info[0] == "BOARD_ID":
                data1 = info[1] << 2 if info[1] <= 40 else (info[1] << 2) & 0xFF
                data1 |= 0x01
                data2 = 1 if info[1] <= 40 else (((info[1] << 2) & 0xFF00) >> 8) + 1
                infos.append(data1)
                infos.append(data2)
            elif info[0] == "BOARD_SN":
                data1 = info[1] & 0xFF
                data2 = (info[1] >> 8) + 1
                infos.append(data1)
                infos.append(data2)
            else:
                infos.append(info[1])
        if common_func.OS == "Linux":
            self.device.write_eeprom(int("0x1a", 16), infos, dry_run=False)
        elif common_func.OS == "Windows":
            self.device.eeUAWrite(bytes(infos))

    def write_eeprom_page_i2c(self, ep_num):
        infos = []
        address = 0
        for info in self.file_info:
            info[1] = int(info[1], 16)
            if info[0] == "BOARD_ID":
                data1 = info[1] << 2 if info[1] <= 40 else (info[1] << 2) & 0xFF
                data1 |= 0x01
                data2 = 1 if info[1] <= 40 else (((info[1] << 2) & 0xFF00) >> 8) + 1
                infos.append(data1)
                infos.append(data2)
            elif info[0] == "BOARD_SN":
                data1 = info[1] & 0xFF
                data2 = (info[1] >> 8) + 1
                infos.append(data1)
                infos.append(data2)
            else:
                infos.append(info[1])
        add_write = (common.board_eeprom_i2c[ep_num]["at24cxx"]["addr"] << 1) + 0
        pins = common.board_eeprom_i2c[ep_num]
        common_func.ftdi_i2c_init(self.device, pins)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_write)
        if common.board_eeprom_i2c[ep_num]["at24cxx"]["type"]:
            common_func.ftdi_i2c_write(self.device, pins, 0)
        common_func.ftdi_i2c_write(self.device, pins, 0x1A)
        for ind in range(0, len(infos)):
            if ind != 0 and ((0x1A + ind) % 8 == 0):
                common_func.ftdi_i2c_stop(self.device, pins)
                time.sleep(0.01)
                common_func.ftdi_i2c_start(self.device, pins)
                common_func.ftdi_i2c_write(self.device, pins, add_write)
                if common.board_eeprom_i2c[ep_num]["at24cxx"]["type"]:
                    common_func.ftdi_i2c_write(self.device, pins, 0)
                common_func.ftdi_i2c_write(self.device, pins, 0x1A + ind)
            common_func.ftdi_i2c_write(self.device, pins, infos[ind])
        common_func.ftdi_i2c_stop(self.device, pins)

    def read_eeprom_i2c(self, pins):
        out = []
        add_write = (pins["at24cxx"]["addr"] << 1) + 0
        add_read = (pins["at24cxx"]["addr"] << 1) + 1
        common_func.ftdi_i2c_init(self.device, pins)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_write)
        if pins["at24cxx"]["type"]:
            common_func.ftdi_i2c_write(self.device, pins, 0)
        common_func.ftdi_i2c_write(self.device, pins, 0x1A)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_read)
        for i in range(2):
            out.append(common_func.ftdi_i2c_read(self.device, pins, 0))
        out.append(common_func.ftdi_i2c_read(self.device, pins, 1))
        common_func.ftdi_i2c_stop(self.device, pins)
        return out

    def read_eeprom_seq(self, ep_num):
        ret_data = []
        i = 0
        address = 0
        add_write = (common.board_eeprom_i2c[ep_num]["at24cxx"]["addr"] << 1) + 0
        add_read = (common.board_eeprom_i2c[ep_num]["at24cxx"]["addr"] << 1) + 1
        pins = common.board_eeprom_i2c[ep_num]
        common_func.ftdi_i2c_init(self.device, pins)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_write)
        if common.board_eeprom_i2c[ep_num]["at24cxx"]["type"]:
            common_func.ftdi_i2c_write(self.device, pins, 0)
        common_func.ftdi_i2c_write(self.device, pins, 0x1A)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_read)
        while i < 9:
            ret_data.append(common_func.ftdi_i2c_read(self.device, pins, 0))
            i += 1
        ret_data.append(common_func.ftdi_i2c_read(self.device, pins, 1))
        common_func.ftdi_i2c_stop(self.device, pins)
        if ret_data[0][0] == 0:
            ret_data.pop(0)
        self.eeprom_info["CONFIG_FLAG"] = (
            hex(0x01) if hex(ret_data[0][0] & 0x0F) != hex(0xF) else hex(0x0)
        )
        self.eeprom_info["BOARD_ID"] = hex(
            ((ret_data[0][0] & 0xFC) >> 2) | ((ret_data[1][0] - 1) << 6)
        )
        self.eeprom_info["BOARD_REV"] = (
            chr((ret_data[2][0] >> 4) + ord("A") - 1) + str((ret_data[2][0] & 0xF) - 1)
            if (ret_data[2][0] != 0x7F and ret_data[2][0] != 0xFF)
            else "Unknown"
        )
        self.eeprom_info["SOC_ID"] = hex(ret_data[3][0])
        self.eeprom_info["SOC_REV"] = (
            chr((ret_data[4][0] >> 4) + ord("A") - 1) + str((ret_data[4][0] & 0xF) - 1)
            if (ret_data[4][0] != 0x7F and ret_data[4][0] != 0xFF)
            else "Unknown"
        )
        self.eeprom_info["PMIC_ID"] = hex(ret_data[5][0])
        self.eeprom_info["PMIC_REV"] = (
            chr((ret_data[6][0] >> 4) + ord("A") - 1) + str((ret_data[6][0] & 0xF) - 1)
            if (ret_data[6][0] != 0x7F and ret_data[6][0] != 0xFF)
            else "Unknown"
        )
        self.eeprom_info["NBR_PWR_RAILS"] = (
            int(ret_data[7][0] - 1) if (ret_data[7][0] <= 254) else "Unknown"
        )
        self.eeprom_info["BOARD_SN"] = (
            int(((ret_data[9][0] - 1) << 8) + ((ret_data[8][0] - 1)))
            if ((((ret_data[9][0] - 1) << 8) + ((ret_data[8][0] - 1))) >= 1)
            else "Unknown"
        )
        self.display_eeprom_info()
