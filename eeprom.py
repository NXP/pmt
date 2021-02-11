# Copyright 2020 NXP.
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
from collections import OrderedDict
import eeprom_mapping_table
import common_function as common_func
from board_configuration import common


if common_func.OS == 'Linux':
    from pyftdi import ftdi
elif common_func.OS == 'Windows':
    import ftd2xx as ftdi


class FTDIEeprom:
    def __init__(self, args):
        self.args = args
        self.eeprom_info = OrderedDict([('CONFIG_FLAG', None), ('BOARD_ID', None), ('BOARD_REV', None), ('SOC_ID', None), ('SOC_REV', None), ('PMIC_ID', None), ('PMIC_REV', None), ('NBR_PWR_RAILS', None), ('BOARD_SN', None)])
        self.file_info = []
        self.device = None
        self.type = None  # 0 for serial and 1 for I2C

    def deinit(self):
        self.device.close()

    def detect_type(self, dev):
        if common_func.OS == 'Linux':
            serial_number = dev[0][4]
            self.type = 1 if serial_number is None else 0
            return self.type, dev[0]
        elif common_func.OS == 'Windows':
            self.type = 1 if len(dev['serial']) <= 1 else 0
            return self.type, dev

    def init_system(self, desc, ind):
        if self.type == 1:  # i2c mode
            self.device = common_func.ftdi_open(ind, 1)
            common_func.ftdic_setbitmode(self.device, 0x0, 0x00)
            common_func.ftdic_setbitmode(self.device, 0x0, 0x02)
        else:  # serial mode
            if common_func.OS == 'Windows':
                self.device = common_func.ftdi_open(ind, 0)
            elif common_func.OS == 'Linux':
                self.device = ftdi.Ftdi()
                self.device.open(vendor=desc[0], product=desc[1], address=desc[3])

    def show_devices(self):
        dev = self.list_eeprom_devices()
        ind = 0
        for dev in reversed(dev):
            print('ID: ' + str(ind) + ' --> ' + str(dev))
            ind += 1

    def list_eeprom_devices(self):
        dev = []
        if common_func.OS == 'Linux':
            self.device = ftdi.Ftdi()
            dev = self.device.list_devices()
            return dev
        elif common_func.OS == 'Windows':
            dev.append(ftdi.getDeviceInfoDetail())
            return dev

    def collect_eeprom_info(self):
        with open(self.args.file, 'r') as file:
            datas = (yaml.safe_load(file))
            for item, value in datas.items():
                for cpt in eeprom_mapping_table.INFOS:
                    if cpt['name'] == item:
                        code = next((key for key, val in cpt['datas'].items()
                                     if val == str(value)), '0x7f')
                        self.file_info.append([item, code])
                        break

    def read_eeprom_board_id_rev(self, pins=None):
        board_id_index = 1
        board_rev_index = 2
        if self.type == 0:
            if common_func.OS == 'Linux':
                out = self.device.read_eeprom(addr=0x1a, length=3)
                soc = hex(((out[0] & 0xFC) >> 2) | ((out[1] - 1) << 6))
                rev = hex(out[2])
                return eeprom_mapping_table.INFOS[board_id_index]['datas'].get(soc, 'Unknown'), \
                    eeprom_mapping_table.INFOS[board_rev_index]['datas'].get(rev, 'Unknown')
            elif common_func.OS == 'Windows':
                soc = self.device.eeUARead(board_id_index + 1)
                rev = self.device.eeUARead(board_rev_index + 1)
                return eeprom_mapping_table.INFOS[board_id_index]['datas'].get(soc, 'Unknown'), \
                    eeprom_mapping_table.INFOS[board_rev_index]['datas'].get(rev, 'Unknown')
        else:
            out = self.read_eeprom_i2c(pins)
            soc = hex(((out[0][0] & 0xFC) >> 2) | ((out[1][0] - 1) << 6))
            rev = hex(out[2][0])
            return eeprom_mapping_table.INFOS[board_id_index]['datas'].get(soc, 'Unknown'), \
                eeprom_mapping_table.INFOS[board_rev_index]['datas'].get(rev, 'Unknown')

    def display_eeprom_info(self):
        i = 0
        for info, data in self.eeprom_info.items():
            print(info + ': ' + eeprom_mapping_table.INFOS[i]['datas'].get(data, 'Unknown'))
            i += 1

    def read(self, id):
        dev_list = self.list_eeprom_devices()
        __, desc = self.detect_type(dev_list[id])
        self.init_system(desc, id)
        if self.type == 0:
            print('** Reading serial EEPROM ...\n')
            self.read_eeprom_serial()
            self.deinit()
            print('\n** Done.')
        else:
            print('I2C EEPROM - Which board are you using ? ( (1) imx8dxlevk / (2) imx8mpevkpwr(a0 / a1) )')
            char = sys.stdin.read(1)
            if char == '1' or char == '2':
                print('** Reading I2C EEPROM ...\n')
                self.read_eeprom_seq(int(char) - 1)
                self.deinit()
                print('\n** Done.')
            else:
                print('ABORTED.')

    def read_eeprom_serial(self):
        if common_func.OS == 'Linux':
            ret_data = self.device.read_eeprom(addr=0x1a, length=9)
        elif common_func.OS == 'Windows':
            ret_data = self.device.eeUARead(9)
        self.eeprom_info['CONFIG_FLAG'] = hex(ret_data[0] & 0x01)
        self.eeprom_info['BOARD_ID'] = hex(((ret_data[0] & 0xFC) >> 2) | ((ret_data[1] - 1) << 6))
        self.eeprom_info['BOARD_REV'] = hex(ret_data[2])
        self.eeprom_info['SOC_ID'] = hex(ret_data[3])
        self.eeprom_info['SOC_REV'] = hex(ret_data[4])
        self.eeprom_info['PMIC_ID'] = hex(ret_data[5])
        self.eeprom_info['PMIC_REV'] = hex(ret_data[6])
        self.eeprom_info['NBR_PWR_RAILS'] = hex(ret_data[7])
        self.eeprom_info['BOARD_SN'] = hex(ret_data[8])
        self.display_eeprom_info()

    def write(self, id):
        dev_list = self.list_eeprom_devices()
        __, desc = self.detect_type(dev_list[id])
        self.init_system(desc, id)
        self.collect_eeprom_info()
        print('** Info collected.\n')
        print('/!\ You are going to overwrite EEPROM content, want to continue? Y/y/N/n')
        char = sys.stdin.read(1)
        if char == 'Y' or char == 'y':
            if self.type == 0:
                print('** Writing to serial EEPROM ...')
                self.write_eeprom_serial()
                self.deinit()
                print('** Done.')
            else:
                print('I2C EEPROM - Which board are you using ? ((1) imx8dxlevk / (2) imx8mpevkpwr(a0 / a1) )')
                char = sys.stdin.read(2)
                if char[1] == '1' or char[1] == '2':
                    print('** Writing to I2C EEPROM ...')
                    self.write_eeprom_page_i2c(int(char) - 1)
                    self.deinit()
                    print('** Done.')
                else:
                    print('ABORTED.')
        else:
            print('ABORTED.')

    def write_eeprom_serial(self):
        infos = []
        for info in self.file_info:
            if info[0] == 'BOARD_ID':
                info[1] = int(info[1], 16)
                data1 = info[1] << 2 if info[1] <= 40 else (info[1] << 2) & 0xFF
                data1 |= 0x01
                data2 = 1 if info[1] <= 40 else (((info[1] << 2) & 0xFF00) >> 8) + 1
                infos.append(data1)
                infos.append(data2)
            else:
                data = int(info[1], 16)
                infos.append(data)
        if common_func.OS == 'Linux':
            self.device.write_eeprom(int('0x1a', 16), infos, dry_run=False)
        elif common_func.OS == 'Windows':
            self.device.eeUAWrite(bytes(infos))

    def write_eeprom_i2c(self, address, data, ep_num):
        add_write = (common.board_eeprom[ep_num]['at24cxx']['addr'] << 1) + 0
        pins = common.board_eeprom[ep_num]
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_write)
        if common.board_eeprom[ep_num]['at24cxx']['type']:
            common_func.ftdi_i2c_write(self.device, pins, address >> 8)
            common_func.ftdi_i2c_write(self.device, pins, address & 0xFF)
        else:
            common_func.ftdi_i2c_write(self.device, pins, address)
        common_func.ftdi_i2c_write(self.device, pins, data)
        common_func.ftdi_i2c_stop(self.device, pins)

    def write_eeprom_page_i2c(self, ep_num):
        infos = []
        address = 0
        for info in self.file_info:
            if info[0] == 'BOARD_ID':
                info[1] = int(info[1], 16)
                data1 = info[1] << 2 if info[1] <= 40 else (info[1] << 2) & 0xFF
                data1 |= 0x01
                data2 = 1 if info[1] <= 40 else (((info[1] << 2) & 0xFF00) >> 8) + 1
                infos.append(data1)
                infos.append(data2)
            else:
                data = int(info[1], 16)
                infos.append(data)
        add_write = (common.board_eeprom[ep_num]['at24cxx']['addr'] << 1) + 0
        pins = common.board_eeprom[ep_num]
        common_func.ftdi_i2c_init(self.device, pins)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_write)
        if common.board_eeprom[ep_num]['at24cxx']['type']:
            common_func.ftdi_i2c_write(self.device, pins, address >> 8)
            common_func.ftdi_i2c_write(self.device, pins, address & 0xFF)
        else:
            common_func.ftdi_i2c_write(self.device, pins, address)
        for ind in range(0, len(infos) - 1):
            common_func.ftdi_i2c_write(self.device, pins, infos[ind])
        common_func.ftdi_i2c_stop(self.device, pins)
        common_func.time.sleep(0.3)
        self.write_eeprom_i2c(8, infos[-1], ep_num)

    def read_eeprom_i2c(self, pins):
        out = []
        add_write = (pins['at24cxx']['addr'] << 1) + 0
        add_read = (pins['at24cxx']['addr'] << 1) + 1
        common_func.ftdi_i2c_init(self.device, pins)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_write)
        if pins['at24cxx']['type']:
            common_func.ftdi_i2c_write(self.device, pins, 0 >> 8)
            common_func.ftdi_i2c_write(self.device, pins, 0 & 0xFF)
        else:
            common_func.ftdi_i2c_write(self.device, pins, 0)
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
        add_write = (common.board_eeprom[ep_num]['at24cxx']['addr'] << 1) + 0
        add_read = (common.board_eeprom[ep_num]['at24cxx']['addr'] << 1) + 1
        pins = common.board_eeprom[ep_num]
        common_func.ftdi_i2c_init(self.device, pins)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_write)
        if common.board_eeprom[ep_num]['at24cxx']['type']:
            common_func.ftdi_i2c_write(self.device, pins, address >> 8)
            common_func.ftdi_i2c_write(self.device, pins, address & 0xFF)
        else:
            common_func.ftdi_i2c_write(self.device, pins, address)
        common_func.ftdi_i2c_start(self.device, pins)
        common_func.ftdi_i2c_write(self.device, pins, add_read)
        while i < 10:
            ret_data.append(common_func.ftdi_i2c_read(self.device, pins, 0))
            i += 1
        common_func.ftdi_i2c_stop(self.device, pins)
        if ret_data[0][0] == 0:
            ret_data.pop(0)
        self.eeprom_info['CONFIG_FLAG'] = hex(0x01) if hex(ret_data[0][0] & 0x0F) != hex(0xF) else hex(0x0)
        self.eeprom_info['BOARD_ID'] = hex(((ret_data[0][0] & 0xFC) >> 2) | ((ret_data[1][0] - 1) << 6))
        self.eeprom_info['BOARD_REV'] = hex(ret_data[2][0])
        self.eeprom_info['SOC_ID'] = hex(ret_data[3][0])
        self.eeprom_info['SOC_REV'] = hex(ret_data[4][0])
        self.eeprom_info['PMIC_ID'] = hex(ret_data[5][0])
        self.eeprom_info['PMIC_REV'] = hex(ret_data[6][0])
        self.eeprom_info['NBR_PWR_RAILS'] = hex(ret_data[7][0])
        self.eeprom_info['BOARD_SN'] = hex(ret_data[8][0])
        self.display_eeprom_info()
