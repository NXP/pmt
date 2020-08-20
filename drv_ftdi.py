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

import sys
import time
import logging
import platform
import threading
import os
import importlib.util

import numpy as np

import ftdi_def as ft_def
import program_config
from main import LOG_LEVEL
from board_configuration import common


if platform.system() == 'Linux':
    import pylibftdi as ftdi

    OS = 'Linux'
elif platform.system() == 'Windows':
    import ftd2xx as ftdi

    OS = 'Windows'

logging.basicConfig(level=LOG_LEVEL)
DATA_LOCK = threading.Lock()
FTDI_LOCK = threading.Lock()
CURR_RSENSE = {}
FLAG_UI_READY = False
FLAG_UI_STOP = False
T_START = 0

PAC1934_ADDR_REG_VBUS = 0x07
PAC1934_ADDR_REG_VBUS_AVG = 0x0F


def load_library(board_name):
    """load the correct board configuration file depending of the board name"""
    cur_dir = os.getcwd()
    board_config_dir = cur_dir + '/board_configuration'
    (_, _, filenames) = next(os.walk(board_config_dir))
    for file in filenames:
        module_name = file.split('.')[0]
        if module_name == board_name:
            spec = importlib.util.spec_from_file_location(module_name, board_config_dir + '/' + board_name + '.py')
            board_c = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = board_c
            spec.loader.exec_module(board_c)
            return board_c


def list_connected_devices():
    """lists devices connected to the PC host"""
    if OS == 'Linux':
        dev_list = ftdi.Driver().list_devices()
        location = len(dev_list)
        for i, device in enumerate(dev_list):
            location -= 1
            print('board[', i, '] - location:', location, '-->', (device))
    elif OS == 'Windows':
        num_of_dev = int(ftdi.createDeviceInfoList() / 4)
        for i in range(num_of_dev):
            dev_list = ftdi.getDeviceInfoDetail(i)
            print('board[', i, '] - location:', dev_list['index'], '-->', dev_list['description'])


class Board:
    def __init__(self, args):
        self.board_mapping_power = []
        self.rails_to_display = []
        self.power_groups = []
        self.board_mapping_gpio_i2c = None
        self.board_mapping_gpio = None
        self.boot_modes = None
        self.ftdic = None
        self.name = None
        self.id = None
        self.data_buf = []
        self.dev_list_num_i2c = None
        self.dev_list_num_gpio = None
        self.params = {'hw_filter': False, 'bipolar': False}
        print("Starting board(s) detection...")
        boards_infos = self.get_all_board()
        print('Number of board(s) detected: ' + str(len(boards_infos)))
        if len(boards_infos) > 1:
            if (args.board and args.id == -1) or (args.id != -1 and not args.board):
                board_found = next(
                    (item for item in boards_infos if item['name'] == args.board or item['loc_id'] == args.id),
                    None)
                if board_found:
                    self.name = board_found['name']
                    self.id = board_found['loc_id']
                else:
                    logging.error("Board name or id entered doesn't match with detected ones... Leaving")
                    sys.exit()
            elif args.board and args.id != -1:
                board_found = next(
                    (item for item in boards_infos if item['name'] == args.board and item['loc_id'] == args.id),
                    None)
                if board_found:
                    self.name = board_found['name']
                    self.id = board_found['loc_id']
                else:
                    logging.error("Board name entered doesn't match with entered id... Leaving")
                    sys.exit()
            else:
                logging.error(
                    "2 or more boards are detected, please specify at least board name or id (lsftdi command)... Leaving")
                sys.exit()
        elif len(boards_infos) == 1:
            if args.board:
                if boards_infos[0]['name'] == args.board:
                    self.name = boards_infos[0]['name']
                    self.id = 0
                else:
                    logging.error('Board connected is not the one passed in command line... Leaving')
                    sys.exit()
            elif args.id != -1:
                if args.id == 0:
                    self.name = boards_infos[0]['name']
                    self.id = 0
                else:
                    logging.error('Board connected is not the one passed in command line (id error)... Leaving')
                    sys.exit()
            else:
                self.name = boards_infos[0]['name']
                self.id = 0
        else:
            logging.error("Board not recognized or doesn't match with command line... Leaving")
            sys.exit()
        print("Done.")
        print("Starting measurements procedure with board " + str(self.name))
        print('Board Initialization...')
        self.board_c = load_library(self.name)
        if next((item for item in program_config.RAILS_TO_PROBE if item == 'all'), None):
            self.board_mapping_power = self.board_c.mapping_power
            self.rails_to_display = self.board_mapping_power
        else:
            for name in program_config.RAILS_TO_PROBE:
                for rail in self.board_c.mapping_power:
                    if name == rail['name']:
                        self.board_mapping_power.append(rail)
                        self.rails_to_display.append(rail)
        for name in program_config.RAILS_TO_PROBE:
            for group in self.board_c.power_groups:
                if name == group['name']:
                    self.power_groups.append(group)
                    for group_rail in group['rails']:
                        add_rail = next((item for item in self.board_c.mapping_power if item['name'] == group_rail), None)
                        if add_rail in self.board_mapping_power:
                            pass
                        else:
                            self.board_mapping_power.append(add_rail)
        self.board_mapping_gpio_i2c = self.board_c.mapping_gpio_i2c
        self.board_mapping_gpio = self.board_c.mapping_gpio
        self.boot_modes = self.board_c.boot_modes
        self.board_mapping_power = sorted(self.board_mapping_power,
                                          key=lambda i: (i['pac'][2], i['pac'][0]))
        print('Done.')

    def lsbootmode(self):
        """prints supported boot mode for the corresponding board"""
        print('Available Boot modes for board : ' + self.name)
        for bootm in self.boot_modes:
            print('- ' + bootm)

    def lsgpio(self):
        """prints available gpio for the corresponding board"""
        print('Available board ' + self.name + ' control GPIO:')
        for gpio_name in self.board_mapping_gpio_i2c:
            print('- ' + gpio_name['name'])
        for gpio_name in self.board_mapping_gpio:
            print('- ' + gpio_name['name'])

    def get_all_board(self):
        """checks if connected boards to PC host are supported by the program and return a list"""
        boards_infos = []
        dev_list = []
        if OS == 'Linux':
            dev_list = ftdi.Driver().list_devices()
            for num in range(len(dev_list)):
                for gpio in common.board_eeprom:
                    ret = self.get_eeprom_board(gpio, num)
                    if not ret:
                        boards_infos.append({'name': gpio['board_name'], 'loc_id': num, 'board_num': num})
            return boards_infos
        elif OS == 'Windows':
            dev_list = ftdi.listDevices()
            if dev_list:
                self.dev_list_num_i2c = [i for i, x in enumerate(dev_list) if x == b'B']
                self.dev_list_num_gpio = [i for i, x in enumerate(dev_list) if x == b'A']
                for num in range(len(self.dev_list_num_i2c)):
                    for gpio in common.board_eeprom:
                        ret = self.get_eeprom_board(gpio, num)
                        if not ret:
                            boards_infos.append({'name': gpio['board_name'], 'loc_id': num, 'board_num': num})
            return boards_infos

    def get_eeprom_board(self, pins, board_id):
        """checks if the eeprom is present on the current board"""
        self.ftdic = self.ftdi_open(board_id, 1)
        self.ftdic_setbitmode(0x0, 0x00)
        self.ftdic_setbitmode(0x0, 0x02)
        self.ftdi_i2c_init(pins)
        add_write = (pins['at24cxx'][0] << 1) + 0
        self.ftdi_i2c_start(pins)
        if self.ftdi_i2c_write(pins, add_write):
            self.ftdi_i2c_stop(pins)
            self.ftdic.close()
            return 1
        else:
            self.ftdi_i2c_stop(pins)
            self.ftdic.close()
            return 0

    def ftdic_write(self, buf):
        """FTDI write function depending of the current OS"""
        if OS == 'Linux':
            self.ftdic.write(bytes(buf))
        elif OS == 'Windows':
            self.ftdic.write(buf)

    def ftdic_write_gpio(self, buf):
        """FTDI write gpio function depending of the current OS"""
        if OS == 'Linux':
            self.ftdic.write(bytes([buf]))
        elif OS == 'Windows':
            self.ftdic.write(bytes([buf]))

    def ftdic_read_gpio(self):
        """FTDI read depending function of the current OS"""
        if OS == 'Linux':
            return self.ftdic.read(1)[0]
        elif OS == 'Windows':
            return self.ftdic.getBitMode()

    def ftdi_open(self, board_id, channel):
        """opens FTDI device function depending of the current OS"""
        if OS == 'Linux':
            return ftdi.Device(device_index=board_id, interface_select=channel + 1)
        elif OS == 'Windows':
            if channel:
                return ftdi.open(self.dev_list_num_i2c[board_id])
            else:
                return ftdi.open(self.dev_list_num_gpio[board_id])

    def ftdic_setbitmode(self, out_pins, value):
        """"FTDI set bitmode function depending of the current OS"""
        if OS == 'Linux':
            self.ftdic.ftdi_fn.ftdi_set_bitmode(out_pins, value)
        elif OS == 'Windows':
            self.ftdic.setBitMode(out_pins, value)

    def pca9548_set_channel(self, pins):
        """I2C communication for setting the channel of the PCA"""
        logging.debug('pca9548_set_channel')
        add_write = (pins['pca9548'][1]) << 1
        change_channel_cmd = 1 << pins['pca9548'][0]
        self.ftdi_i2c_start(pins)
        self.ftdi_i2c_write(pins, add_write)
        self.ftdi_i2c_write(pins, change_channel_cmd)
        self.ftdi_i2c_stop(pins)

    def pca_write(self, pins, gpio_value):
        """I2C communication for writing new value to the PCA"""
        output_data = []
        logging.debug('pca_write')
        add_write = (pins['pca6416'][0] << 1) + 0
        add_read = (pins['pca6416'][0] << 1) + 1
        conf_cmd = (pins['pca6416'][1]) + 0x02
        self.ftdi_i2c_start(pins)
        status = self.ftdi_i2c_write(pins, add_write)
        if status != 0: return status
        status = self.ftdi_i2c_write(pins, conf_cmd)
        if status != 0: return status
        self.ftdi_i2c_start(pins)
        status = self.ftdi_i2c_write(pins, add_read)
        if status != 0: return status
        current_config = self.ftdi_i2c_read(pins, 1)
        logging.debug('Current PCA GPIO configuration: ' + hex(current_config[0]))
        self.ftdi_i2c_stop(pins)
        output_data = (current_config[0] & ~pins['pca6416'][2]) | (gpio_value & pins['pca6416'][2])
        logging.debug('Modified PCA GPIO configuration: ' + hex(output_data))
        self.ftdi_i2c_start(pins)
        status = self.ftdi_i2c_write(pins, add_write)
        if status != 0: return status
        status = self.ftdi_i2c_write(pins, conf_cmd)
        if status != 0: return status
        status = self.ftdi_i2c_write(pins, output_data)
        if status != 0: return status
        self.ftdi_i2c_stop(pins)

    def pca6416_set_direction(self, pins):
        """I2C communication for defining PCA pins as I/O"""
        logging.debug('pca6416_set_direction')
        add_write = (pins['pca6416'][0] << 1) + 0
        add_read = (pins['pca6416'][0] << 1) + 1
        conf_cmd = (pins['pca6416'][1]) + 0x06
        self.ftdi_i2c_start(pins)
        status = self.ftdi_i2c_write(pins, add_write)
        if status != 0: return status
        status = self.ftdi_i2c_write(pins, conf_cmd)
        if status != 0: return status
        self.ftdi_i2c_start(pins)
        status = self.ftdi_i2c_write(pins, add_read)
        if status != 0: return status
        current_confg = self.ftdi_i2c_read(pins, 1)
        logging.debug('Current PCA pins direction: ' + hex(current_confg[0]))
        self.ftdi_i2c_stop(pins)
        intput_bitmask = (~(pins['pca6416'][2])) & current_confg[0]
        logging.debug('Input PCA  bitmask pins direction: ' + hex(intput_bitmask))
        self.ftdi_i2c_start(pins)
        status = self.ftdi_i2c_write(pins, add_write)
        if status != 0: return status
        status = self.ftdi_i2c_write(pins, conf_cmd)
        if status != 0: return status
        status = self.ftdi_i2c_write(pins, intput_bitmask)
        if status != 0: return status
        self.ftdi_i2c_stop(pins)

    def pca6416_get_output(self, pins):
        """returns the current pins configuration of the PCA"""
        logging.debug('pca_get_output')
        add_write = (pins['pca6416'][0] << 1) + 0
        add_read = (pins['pca6416'][0] << 1) + 1
        conf_cmd = (pins['pca6416'][1]) + 0x02
        self.ftdi_i2c_start(pins)
        status = self.ftdi_i2c_write(pins, add_write)
        if status != 0: return status
        status = self.ftdi_i2c_write(pins, conf_cmd)
        if status != 0: return status
        self.ftdi_i2c_start(pins)
        status = self.ftdi_i2c_write(pins, add_read)
        if status != 0: return status
        current_out = self.ftdi_i2c_read(pins, 1)
        self.ftdi_i2c_stop(pins)
        return current_out[0] & pins['pca6416'][2]

    def ftdi_i2c_read(self, pins, is_nack):
        """low-level I2C read"""
        logging.debug('ftdi_i2c_read')
        val_bitmask = pins['ftdi'][2]
        dir_bitmask = pins['ftdi'][1]
        buf = []
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
        buf.append(ft_def.DIRECTION_SCLOUT_SDAIN | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_DATA_IN_BITS_POS_EDGE)
        buf.append(ft_def.DATA_SIZE_8BITS)
        buf.append(ft_def.MPSSE_CMD_SEND_IMMEDIATE)
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE)
        buf.append(0x00)
        if is_nack:
            buf.append(0x80)
        else:
            buf.append(0x00)
        buf_to_send = bytes(buf)
        self.ftdic_write(buf_to_send)
        time.sleep(0.0001)
        receive = self.ftdic.read(1)
        return receive

    def ftdi_i2c_write(self, pins, data):
        """low-level I2C write"""
        logging.debug('ftdi_i2c_write')
        val_bitmask = pins['ftdi'][2]
        dir_bitmask = pins['ftdi'][1]
        buf = []
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE)
        buf.append(ft_def.DATA_SIZE_8BITS)
        buf.append(data)
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
        buf.append(ft_def.DIRECTION_SCLOUT_SDAIN | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_DATA_IN_BITS_POS_EDGE)
        buf.append(ft_def.DATA_SIZE_1BIT)
        buf.append(ft_def.MPSSE_CMD_SEND_IMMEDIATE)
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf_to_send = bytes(buf)
        self.ftdic_write(buf_to_send)
        time.sleep(0.0005)
        in_buff = self.ftdic.read(1)
        if (in_buff[0] & 0x01) != 0:
            logging.warning("Can't get ack after write!")
            return -1
        return 0

    def ftdi_i2c_stop(self, pins):
        """low-level I2C stop"""
        logging.debug('ftdi_i2c_stop')
        val_bitmask = pins['ftdi'][2]
        dir_bitmask = pins['ftdi'][1]
        buf = []
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)  # SCL low, SDA low
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLHIGH_SDALOW | val_bitmask)  # SCL high, SDA low
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLHIGH_SDAHIGH | val_bitmask)  # SCL high, SDA high
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf_to_send = bytes(buf)
        self.ftdic_write(buf_to_send)

    def ftdi_i2c_start(self, pins):
        """low-level I2C start"""
        logging.debug('ftdi_i2c_start')
        val_bitmask = pins['ftdi'][2]
        dir_bitmask = pins['ftdi'][1]
        buf = []
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLHIGH_SDAHIGH | val_bitmask)  # SCL high, SDA high
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLHIGH_SDALOW | val_bitmask)  # SCL high, SDA low
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
        buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)  # SCL low, SDA low
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf_to_send = bytes(buf)
        self.ftdic_write(buf_to_send)

    def ftdi_i2c_init(self, pins):
        """low-level I2C initialization"""
        logging.debug('ftdi_i2c_init')
        val_bitmask = pins['ftdi'][2]
        dir_bitmask = pins['ftdi'][1]
        buf = []
        buf.append(
            ft_def.MPSSE_CMD_DISABLE_CLOCK_DIVIDE_BY_5)  # Ensure disable clock divide by 5 for 60Mhz master clock
        buf.append(ft_def.MPSSE_CMD_DISABLE_ADAPTIVE_CLOCKING)  # Ensure turn off adaptive clocking
        buf.append(
            ft_def.MPSSE_CMD_ENABLE_3PHASE_CLOCKING)  # PAC 1934 need it. Enable 3 phase data clock, used by I2C to allow data on one clock edge
        buf_to_send = bytes(buf)
        self.ftdic_write(buf_to_send)
        buf.clear()
        buf.append(
            ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)  # Command to set directions of lower 8 pins and force value on bits set as output
        buf.append(ft_def.VALUE_SCLHIGH_SDAHIGH | val_bitmask)
        buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
        buf.append(ft_def.MPSSE_CMD_SET_CLOCK_DIVISOR)  # Command to set clock divisor
        buf.append(
            ft_def.CLOCK_DIVISOR_400K & 0xFF)  # problem with byte(), result M instead of 4D - Set 0xValueL of clock divisor
        buf.append((ft_def.CLOCK_DIVISOR_400K >> 8) & 0xFF)  # Set 0xValueH of clock divisor
        buf_to_send = bytes(buf)
        self.ftdic_write(buf_to_send)
        buf.clear()
        buf.append(ft_def.MPSEE_CMD_DISABLE_LOOPBACK)  # Command to turn off loop back of TDI/TDO connection
        buf_to_send = bytes(buf)
        self.ftdic_write(buf_to_send)

    def ftdi_gpio_write(self, gpio_name, gpio_value):
        """writes desired value to the gpio passed in parameter"""
        logging.debug('ftdi_gpio_write')
        gpio_add = gpio_name['ftdi'][1]
        current_output = self.ftdic_read_gpio()
        logging.debug('current GPIO configuration: ' + hex(current_output))
        if not gpio_value:
            data = current_output & ~gpio_add
            self.ftdic_write_gpio(data)
        if gpio_value == 1 or gpio_value == 0xFF:
            data = current_output | gpio_add
            self.ftdic_write_gpio(data)
        if gpio_value == 2:
            data = current_output ^ gpio_add
            self.ftdic_write_gpio(data)
            time.sleep(0.5)
            self.ftdic_write_gpio(current_output)
        # add traces as debug
        current_output = self.ftdic_read_gpio()
        logging.debug('modified GPIO configuration: ' + hex(current_output))

    def deinit_system(self):
        """closes FTDI interaction"""
        self.ftdic.close()

    def init_system(self, pins):
        """initialization of the FTDI chip"""
        mode = 1 if pins in self.board_mapping_gpio_i2c or pins in self.board_mapping_power else 0
        channel = pins['ftdi'][0]
        out_pins = 0
        logging.info('FTDI Initialization...')
        self.ftdic = self.ftdi_open(self.id, channel)
        if mode == 0:  # if GPIO mode
            for gpio in self.board_mapping_gpio:  # if channel 0, parse gpio default value of channel 0
                if gpio['ftdi'][0] == channel:
                    out_pins += gpio['ftdi'][1]
            self.ftdic_setbitmode(0xFF, 0x1)
        if mode == 1:  # if I2C mode
            self.ftdic_setbitmode(0x0, 0x00)  # reset the controller
            self.ftdic_setbitmode(0x0, 0x02)  # set as MPSSE
            self.ftdi_i2c_init(pins)  # Init FT4232H MPSSE with correct parameters
        logging.info('Done.')

    def resume(self):
        print("start resuming / suspending...")
        gpio = next((item for item in self.board_mapping_gpio if(item['name'] == 'FTA_PWR_ON_OFF' or item['name'] == 'FT_ONOFF_B')), None)
        FTDI_LOCK.acquire()
        self.set_gpio(gpio, 0xFF)
        time.sleep(0.5)
        self.set_gpio(gpio, 0x00)
        FTDI_LOCK.release()
        print("Done.")

    def reset_getgpio(self, initid):
        """returns gpio value to set"""
        for gpio in self.board_mapping_gpio:
            if gpio['default'] >> 4 == initid:
                return gpio, gpio['default'] & 0x0F
        for gpio in self.board_mapping_gpio_i2c:
            if gpio['default'] >> 4 == initid:
                return gpio, gpio['default'] & 0x0F
        return None, -1

    def init_sequence(self, mode):
        """sets correct gpio value depending of board configuration before resetting the board"""
        out = 0
        initid = 1
        while out >= 0:
            gpio, out = self.reset_getgpio(initid)
            if out < 0:
                print('Rebooting ...')
                break
            if gpio['name'].split('_')[1] == 'BOOT':
                if mode:
                    val = self.boot_modes.get(mode)
                    self.set_gpio(gpio, val)
                initid += 1
                continue
            self.set_gpio(gpio, out * 0xFF)
            initid += 1

    def reset(self, mode, delay):
        """resets the board with possible boot mode and delay"""
        self.init_sequence(mode)
        time.sleep(delay)
        for rail in self.board_c.mapping_power:
            if rail['rsense'][0] != rail['rsense'][1]:
                self.init_system(rail)
                self.init_res(rail)
                self.deinit_system()
        gpio = next((item for item in self.board_mapping_gpio if
                     (item['name'] == 'FTA_RESET' or item['name'] == 'FT_SYS_nRST')), None)
        self.set_gpio(gpio, 0x00)
        time.sleep(0.5)
        if mode:
            self.set_gpio(gpio, 0xFF)
        else:
            gpio = next((item for item in self.board_mapping_gpio_i2c if item['name'] == 'BOOT_SRC_SEL'), None)
            if gpio:
                self.set_gpio(gpio, 0xFF)
                gpio = next((item for item in self.board_mapping_gpio if item['name'] == 'FTA_RESET'), None)
                self.set_gpio(gpio, 0xFF)
            else:
                gpio = next((item for item in self.board_mapping_gpio_i2c if item['name'] == 'FT_REMOTE_SEL'), None)
                self.set_gpio(gpio, 0x00)
        print('Done.')

    def set_gpio(self, gpio_name, gpio_value):
        """sets value to gpio with init and close of the FTDI"""
        self.init_system(gpio_name)
        self.setgpio(gpio_name, gpio_value)
        self.deinit_system()

    def setgpio(self, gpio_name, gpio_value):
        """low-level set value to gpio depending of the gpio source (I2C or not)"""
        mode = 1 if gpio_name in self.board_mapping_gpio_i2c else 0  # mode 1 for I2C and mode 0 for GPIO
        if mode == 0:
            self.ftdi_gpio_write(gpio_name, gpio_value)
        if mode == 1:
            if gpio_name.get('pca9548'):
                self.pca9548_set_channel(gpio_name)
            self.pca6416_set_direction(gpio_name)
            self.pca_write(gpio_name, gpio_value)


    def switch_res(self, rail, rail_num):
        """checks if switching desired resistance is authorised and return the status"""
        switch_res_permitted = False
        gpio = next((item for item in self.board_mapping_gpio_i2c if item['name'] == rail['rsense_ctl']), None)
        if CURR_RSENSE.get(rail['name']) == rail['rsense'][1]:  # switch low_current shunt to high_current shunt
            gpio_value = rail['rsense'][2]
            next_rsense = rail['rsense'][0]
            switch_res_permitted = True
        else:
            sampling_rate = self.data_buf[rail_num]['current'].shape[0] / self.data_buf[rail_num]['current'][-1, 0]
            number_of_val = int(sampling_rate / 3)
            cur_limit = (100 / rail['rsense'][1]) * 1000
            cur_limit *= (1 - (program_config.LOW_SWITCH_RESISTANCE_OFFSET / 100))
            DATA_LOCK.acquire()
            avg_current = self.data_buf[rail_num]['current'][-number_of_val:, 1].mean(0)
            DATA_LOCK.release()
            if avg_current > cur_limit:
                return False, switch_res_permitted
            else:
                gpio_value = not rail['rsense'][2]
                switch_res_permitted = True
                next_rsense = rail['rsense'][1]
        if switch_res_permitted:
            FTDI_LOCK.acquire()
            self.setgpio(gpio, gpio_value * 0xFF)
            check_value = self.pca6416_get_output(gpio)
            FTDI_LOCK.release()
            if (check_value / gpio['pca6416'][2]) != gpio_value:
                return False, switch_res_permitted
            else:
                CURR_RSENSE[rail['name']] = next_rsense
                if len(rail['pac']) > 3:  # in case of 8MP_EVK with PM rail
                    temp = rail['pac'][0]
                    rail['pac'][0] = rail['pac'][3]
                    rail['pac'][3] = temp
                return True, switch_res_permitted

    def init_res(self, rail):
        """initialization of the current rail's resistance to high current shunt"""
        err = 0
        if rail['rsense'][0] != rail['rsense'][1]:
            gpio = next((item for item in self.board_mapping_gpio_i2c if item['name'] == rail['rsense_ctl']), None)
            init_value = rail['rsense'][2]
            self.setgpio(gpio, init_value * 0xFF)
            while (self.pca6416_get_output(gpio) / gpio['pca6416'][2]) != init_value:
                err += 1
                self.setgpio(gpio, init_value * 0xFF)
                if err == 5:
                    print('Failed to init resistance switch ' + gpio['name'] + ' to high level.')
                    break
        CURR_RSENSE[rail['name']] = rail['rsense'][0]

    def reset_pac(self, pins):
        """I2C communication for sending reset command to the current PAC"""
        add_write = (pins['pac'][1] << 1) + 0
        self.ftdi_i2c_start(pins)
        self.ftdi_i2c_write(pins, add_write)
        self.ftdi_i2c_write(pins, 0x00)
        self.ftdi_i2c_stop(pins)

    def pac_set_bipolar(self):
        self.params['bipolar'] = not self.params['bipolar']
        FTDI_LOCK.acquire()
        for index, rail in enumerate(self.board_mapping_power):
            if rail['pac'][2] != self.board_mapping_power[index - 1]['pac'][2]:
                self.pca9548_set_channel(rail)
                add_write = (rail['pac'][1] << 1)
                self.ftdi_i2c_start(rail)
                self.ftdi_i2c_write(rail, add_write)
                self.ftdi_i2c_write(rail, 0x1D)
                if self.params['bipolar']:
                    self.ftdi_i2c_write(rail, 0xF0)
                else:
                    self.ftdi_i2c_write(rail, 0x00)
                self.ftdi_i2c_stop(rail)
        FTDI_LOCK.release()

    def pac_hw_filter(self):
        self.params['hw_filter'] = not self.params['hw_filter']

    def process_current(self, current):
        if self.params['bipolar']:
            if current >= 32768:
                return (current - 65536) / 32768 * 100000
            else:
                return current / 32768 * 100000
        else:
            return current / 65535 * 100000

    def block_read(self, pins, index, rail_of_pac):
        """I2C communication for PAC block read and return list of voltage / current"""
        data = []
        voltage = []
        current = []
        if self.params['hw_filter']:
            register = PAC1934_ADDR_REG_VBUS_AVG
        else:
            register = PAC1934_ADDR_REG_VBUS
        add_write = (pins['pac'][1] << 1) + 0
        add_read = (pins['pac'][1] << 1) + 1
        self.ftdi_i2c_start(pins)
        self.ftdi_i2c_write(pins, add_write)
        self.ftdi_i2c_write(pins, register)
        self.ftdi_i2c_start(pins)
        self.ftdi_i2c_write(pins, add_read)
        for i in range(15):
            data.append(self.ftdi_i2c_read(pins, 0))
        data.append(self.ftdi_i2c_read(pins, 1))
        for i in range(rail_of_pac):
            channel = self.board_mapping_power[i + index]['pac'][0]
            volt = (((data[(2 * channel) - 2][0] << 8) + data[(2 * channel) - 1][0]) * 32) / 65535
            voltage.append(volt)
            curr = self.process_current((((data[8 + (2 * channel) - 2][0] << 8) + data[8 + (2 * channel) - 1][0]) * 1))
            current.append(curr)
        return voltage, current

    def get_data(self):
        """reads PAC while the app doesn't stop and update shared variable with power/voltage/current"""
        global FLAG_UI_READY
        global T_START
        rail_per_pac = {}
        first_probe = True
        self.init_system(self.board_mapping_power[0])
        for index, rail in enumerate(self.board_mapping_power):
            self.init_res(rail)
            self.data_buf.append({'railnumber': rail['name'], 'current': np.empty([1, 2], dtype=np.float16),
                                  'voltage': np.empty([1, 2], dtype=np.float16)})
            if len(self.board_mapping_power) == 1:
                rail_of_pac = 1
                rail_per_pac[rail['pac'][2]] = rail_of_pac
            else:
                if rail['pac'][2] != self.board_mapping_power[index - 1]['pac'][2] or first_probe:
                    first_probe = False
                    rail_of_pac = 0
                    for i in range(4):
                        if index + i < len(self.board_mapping_power):
                            if self.board_mapping_power[index + i]['pac'][2] == rail['pac'][2]:
                                rail_of_pac += 1
                            else:
                                break
                        else:
                            break
                    rail_per_pac[rail['pac'][2]] = rail_of_pac
        FLAG_UI_READY = True
        self.pac_set_bipolar()
        T_START = time.time()
        while not FLAG_UI_STOP:
            for index, rail in enumerate(self.board_mapping_power):
                if len(self.board_mapping_power) == 1:
                    FTDI_LOCK.acquire()
                    self.pca9548_set_channel(rail)
                    self.reset_pac(rail)
                    voltage, current = self.block_read(rail, index, rail_per_pac[rail['pac'][2]])
                    FTDI_LOCK.release()
                    t_stop = time.time()
                    DATA_LOCK.acquire()
                    for i in range(rail_per_pac[rail['pac'][2]]):
                        tmp_cur = self.data_buf[index + i]['current']
                        tmp_volt = self.data_buf[index + i]['voltage']
                        self.data_buf[index + i]['current'] = np.empty(
                            [(self.data_buf[index + i]['current'].shape[0] + 1), 2],
                            dtype=np.float16)
                        self.data_buf[index + i]['voltage'] = np.empty(
                            [(self.data_buf[index + i]['voltage'].shape[0] + 1), 2],
                            dtype=np.float16)
                        self.data_buf[index + i]['current'][:tmp_cur.shape[0]] = tmp_cur
                        self.data_buf[index + i]['voltage'][:tmp_volt.shape[0]] = tmp_volt
                        self.data_buf[index + i]['current'][tmp_cur.shape[0]:, 0] = t_stop - T_START
                        self.data_buf[index + i]['voltage'][tmp_volt.shape[0]:, 0] = t_stop - T_START
                        self.data_buf[index + i]['voltage'][tmp_volt.shape[0]:, 1] = voltage[i]
                        self.data_buf[index + i]['current'][tmp_volt.shape[0]:, 1] = current[i] / CURR_RSENSE[
                            self.data_buf[index + i]['railnumber']]
                    DATA_LOCK.release()
                else:
                    # We check if the PAC of the current rail is different to the precedent rail, if yes then we can continue
                    # the procedure for block read else continue to next rail.
                    # Another case is if we have only different rails of the same PAC. In this case we continue the
                    # procedure only if it is the first rail of the PAC.
                    if rail['pac'][2] != self.board_mapping_power[index - 1]['pac'][2] or (
                            len(rail_per_pac) == 1 and index < 1):
                        FTDI_LOCK.acquire()
                        # We have to change the channel of the PCA if the current one is different to previous rail.
                        # In all case we then proceed to reset the PAC with REFRESH command and do block read.
                        if rail['pca9548'][0] != self.board_mapping_power[index - 1]['pca9548'][0] or (
                                len(rail_per_pac) == 1 and index < 1):
                            self.pca9548_set_channel(rail)
                        self.reset_pac(rail)
                        voltage, current = self.block_read(rail, index, rail_per_pac[rail['pac'][2]])
                        FTDI_LOCK.release()
                        t_stop = time.time()
                        DATA_LOCK.acquire()
                        for i in range(rail_per_pac[rail['pac'][2]]):
                            tmp_cur = self.data_buf[index + i]['current']
                            tmp_volt = self.data_buf[index + i]['voltage']
                            self.data_buf[index + i]['current'] = np.empty(
                                [(self.data_buf[index + i]['current'].shape[0] + 1), 2],
                                dtype=np.float16)
                            self.data_buf[index + i]['voltage'] = np.empty(
                                [(self.data_buf[index + i]['voltage'].shape[0] + 1), 2],
                                dtype=np.float16)
                            self.data_buf[index + i]['current'][:tmp_cur.shape[0]] = tmp_cur
                            self.data_buf[index + i]['voltage'][:tmp_volt.shape[0]] = tmp_volt
                            self.data_buf[index + i]['current'][tmp_cur.shape[0]:, 0] = t_stop - T_START
                            self.data_buf[index + i]['voltage'][tmp_volt.shape[0]:, 0] = t_stop - T_START
                            self.data_buf[index + i]['voltage'][tmp_volt.shape[0]:, 1] = voltage[i]
                            self.data_buf[index + i]['current'][tmp_volt.shape[0]:, 1] = current[i] / CURR_RSENSE[
                                self.data_buf[index + i]['railnumber']]
                        DATA_LOCK.release()
