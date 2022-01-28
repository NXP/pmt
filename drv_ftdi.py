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

import logging
import sys
import threading
import time
import os
import importlib.util

import numpy as np
import common_function as common_func
from board_configuration import common
import eeprom
import program_config
from main import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
DATA_LOCK = threading.Lock()
FTDI_LOCK = threading.Lock()
TEMP_DATA_LOCK = threading.Lock()
CURR_RSENSE = {}
FLAG_UI_STOP = False
FLAG_PAUSE_CAPTURE = False
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


class Board:
    def __init__(self, args):
        self.args = args
        self.board_mapping_power = []
        self.rails_to_display = []
        self.power_groups = []
        self.board_mapping_gpio_i2c = None
        self.board_mapping_gpio = None
        self.boot_modes = None
        self.ftdic = None
        self.temperature_sensor = None
        self.name = None
        self.id = None
        self.data_buf = []
        self.temp_buf = []
        self.dev_list_num_i2c = None
        self.dev_list_num_gpio = None
        self.params = {'hw_filter': False, 'bipolar': False}
        self.eeprom = eeprom.FTDIEeprom(args)
        if self.args.command == 'eeprom' or self.args.command == 'lsftdi' or (self.args.command == 'monitor' and self.args.load):
            pass
        else:
            self.init_class()

    def init_class(self):
        print("Starting board(s) detection...")
        boards_infos = self.get_all_board()
        print('Number of board(s) detected: ' + str(len(boards_infos)))
        if len(boards_infos) > 1:
            if (self.args.board and self.args.id == -1) or (self.args.id != -1 and not self.args.board):
                board_found = next(
                    (item for item in boards_infos if item['name'] == self.args.board or item['loc_id'] == self.args.id),
                    None)
                if board_found:
                    self.name = board_found['name']
                    self.id = board_found['loc_id']
                else:
                    logging.error("Board name or id entered doesn't match with detected ones... Leaving")
                    sys.exit()
            elif self.args.board and self.args.id != -1:
                board_found = next(
                    (item for item in boards_infos if item['name'] == self.args.board and item['loc_id'] == self.args.id),
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
            if self.args.board:
                self.name = self.args.board
                self.id = 0
                if not boards_infos[0]['name'] == self.args.board:
                    print('!!! WARNING: The board name passed in command line does not match with the configuration flashed in EEPROM, please double-check. !!!')
                    time.sleep(3)
            elif self.args.id != -1:
                if self.args.id == 0:
                    self.name = boards_infos[0]['name']
                    self.id = 0
                else:
                    logging.error('Board connected is not the one passed in command line (id error)... Leaving')
                    sys.exit()
            else:
                self.name = boards_infos[0]['name']
                self.id = 0
        elif len(boards_infos) == 0:
            if self.args.board:
                self.name = self.args.board
                self.id = 0
                logging.warning('The board name passed in command line does not match with the configuration flashed in EEPROM, please double-check.')
                time.sleep(3)
            else:
                logging.error("Board not recognized or doesn't match board name specified in command line... Leaving")
                sys.exit()
        else:
            logging.error("Board not recognized or doesn't match with command line... Leaving")
            sys.exit()
        print("Done.")
        self.board_c = load_library(self.name)
        if self.board_c is None:
            print("Board " + self.name + " is not supported... Leaving")
            sys.exit()
        else:
            print("Starting measurements procedure with board " + str(self.name))
            print('Board Initialization...')
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
                            add_rail = next((item for item in self.board_c.mapping_power if item['name'] == group_rail),
                                            None)
                            if add_rail in self.board_mapping_power:
                                pass
                            else:
                                self.board_mapping_power.append(add_rail)
            self.board_mapping_gpio_i2c = self.board_c.mapping_gpio_i2c
            self.board_mapping_gpio = self.board_c.mapping_gpio
            self.boot_modes = self.board_c.boot_modes
            self.temperature_sensor = self.board_c.temperature_sensor if "temperature_sensor" in dir(self.board_c) \
                else None
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
        boards_def = {'NXP i.MX8DXL EVK Board' : 'imx8dxlevk',
                      'NXP i.MX8DXL EVK DDR3 Board': 'imx8dxlevkddr3',
                      'NXP i.MX8MP EVK Board' : 'imx8mpevk',
                      'NXP i.MX8MP EVK PWR Board' : 'imx8mpevkpwr',
                      'NXP i.MX8MP DDR3L Board' : 'imx8mpddr3l',
                      'NXP i.MX8MP DDR4 Board' : 'imx8mpddr4',
                      'NXP i.MX8ULP EVK Board' : 'imx8ulpevk',
                      'NXP i.MX8ULP EVK9 Board': 'imx8ulpevk9',
                      'NXP VAL_BOARD_1 Board' : 'val_board_1',
                      'NXP VAL_BOARD_2 Board' : 'val_board_2'
                      }
        boards_infos = []
        dev_list = self.eeprom.list_eeprom_devices()
        for ind in range(len(dev_list)):
            type, desc = self.eeprom.detect_type(dev_list[ind])
            if type == 1: # i2c eeprom
                for pins in common.board_eeprom_i2c:
                    self.eeprom.init_system(desc, ind)
                    board_id, board_rev = self.eeprom.read_eeprom_board_id_rev(pins)
                    self.eeprom.deinit()
                    board_id = boards_def.get(board_id, 'Unknown')
                    if board_id != 'Unknown':
                        if board_rev != 'Unknown' and board_id not in ['imx8dxlevk', 'imx8ulpevk', 'val_board_1', 'val_board_2', 'imx8ulpevk9']:  # temporary hack to be align with bcu (don't specify board revision for these boards)
                            board_id = board_id + board_rev.lower()
                        boards_infos.append({'name': board_id, 'loc_id': ind})
                        break
            else: # serial eeprom
                self.eeprom.init_system(desc, ind)
                board_id, board_rev = self.eeprom.read_eeprom_board_id_rev()
                self.eeprom.deinit()
                board_id = boards_def.get(board_id, 'Unknown')
                if board_id != 'Unknown':
                    if board_rev != 'Unknown' and board_id not in ['imx8dxlevk', 'imx8ulpevk', 'val_board_1', 'val_board_2', 'imx8ulpevk9']:  # temporary hack to be align with bcu (don't specify board revision for these boards)
                        board_id = board_id + board_rev.lower()
                    boards_infos.append({'name': board_id, 'loc_id': ind})
            time.sleep(0.2)
        return boards_infos

    def board_eeprom_read(self):
        self.eeprom.read(self.args.id)

    def board_eeprom_write(self):
        self.eeprom.write(self.args.id)

    def get_eeprom_board(self, pins, board_id):
        """checks if the eeprom is present on the current board"""
        self.ftdic = common_func.ftdi_open(board_id, 1)
        common_func.ftdic_setbitmode(self.ftdic, 0x0, 0x00)
        common_func.ftdic_setbitmode(self.ftdic, 0x0, 0x02)
        common_func.ftdi_i2c_init(self.ftdic, pins)
        add_write = (pins['at24cxx'][0] << 1) + 0
        common_func.ftdi_i2c_start(self.ftdic, pins)
        if common_func.ftdi_i2c_write(self.ftdic, pins, add_write):
            common_func.ftdi_i2c_stop(self.ftdic, pins)
            self.ftdic.close()
            return 1
        else:
            common_func.ftdi_i2c_stop(self.ftdic, pins)
            self.ftdic.close()
            return 0

    def pca9548_set_channel(self, pins):
        """I2C communication for setting the channel of the PCA"""
        logging.debug('pca9548_set_channel')
        add_write = (pins['pca9548'][1]) << 1
        change_channel_cmd = 1 << pins['pca9548'][0]
        common_func.ftdi_i2c_start(self.ftdic, pins)
        common_func.ftdi_i2c_write(self.ftdic, pins, add_write)
        common_func.ftdi_i2c_write(self.ftdic, pins, change_channel_cmd)
        common_func.ftdi_i2c_stop(self.ftdic, pins)

    def pca_write(self, pins, gpio_value):
        """I2C communication for writing new value to the PCA"""
        output_data = []
        logging.debug('pca_write')
        add_write = (pins['pca6416'][0] << 1) + 0
        add_read = (pins['pca6416'][0] << 1) + 1
        conf_cmd = (pins['pca6416'][1])
        conf_cmd = conf_cmd + 0x02 if (self.name != 'val_board_1' and self.name != 'val_board_2') else conf_cmd + 0x04
        common_func.ftdi_i2c_start(self.ftdic, pins)
        status = common_func.ftdi_i2c_write(self.ftdic, pins, add_write)
        if status != 0: return status
        status = common_func.ftdi_i2c_write(self.ftdic, pins, conf_cmd)
        if status != 0: return status
        common_func.ftdi_i2c_start(self.ftdic, pins)
        status = common_func.ftdi_i2c_write(self.ftdic, pins, add_read)
        if status != 0: return status
        current_config = common_func.ftdi_i2c_read(self.ftdic, pins, 1)
        logging.debug('Current PCA GPIO configuration: ' + hex(current_config[0]))
        common_func.ftdi_i2c_stop(self.ftdic, pins)
        output_data = (current_config[0] & ~pins['pca6416'][2]) | (gpio_value & pins['pca6416'][2])
        logging.debug('Modified PCA GPIO configuration: ' + hex(output_data))
        common_func.ftdi_i2c_start(self.ftdic, pins)
        status = common_func.ftdi_i2c_write(self.ftdic, pins, add_write)
        if status != 0: return status
        status = common_func.ftdi_i2c_write(self.ftdic, pins, conf_cmd)
        if status != 0: return status
        status = common_func.ftdi_i2c_write(self.ftdic, pins, output_data)
        if status != 0: return status
        common_func.ftdi_i2c_stop(self.ftdic, pins)

    def pca6416_set_direction(self, pins):
        """I2C communication for defining PCA pins as I/O"""
        logging.debug('pca6416_set_direction')
        add_write = (pins['pca6416'][0] << 1) + 0
        add_read = (pins['pca6416'][0] << 1) + 1
        conf_cmd = (pins['pca6416'][1])
        conf_cmd = conf_cmd + 0x06 if (self.name != 'val_board_1' and self.name != 'val_board_2') else conf_cmd + 0x0C
        common_func.ftdi_i2c_start(self.ftdic, pins)
        status = common_func.ftdi_i2c_write(self.ftdic, pins, add_write)
        if status != 0: return status
        status = common_func.ftdi_i2c_write(self.ftdic, pins, conf_cmd)
        if status != 0: return status
        common_func.ftdi_i2c_start(self.ftdic, pins)
        status = common_func.ftdi_i2c_write(self.ftdic, pins, add_read)
        if status != 0: return status
        current_confg = common_func.ftdi_i2c_read(self.ftdic, pins, 1)
        logging.debug('Current PCA pins direction: ' + hex(current_confg[0]))
        common_func.ftdi_i2c_stop(self.ftdic, pins)
        intput_bitmask = (~(pins['pca6416'][2])) & current_confg[0]
        logging.debug('Input PCA  bitmask pins direction: ' + hex(intput_bitmask))
        common_func.ftdi_i2c_start(self.ftdic, pins)
        status = common_func.ftdi_i2c_write(self.ftdic, pins, add_write)
        if status != 0: return status
        status = common_func.ftdi_i2c_write(self.ftdic, pins, conf_cmd)
        if status != 0: return status
        status = common_func.ftdi_i2c_write(self.ftdic, pins, intput_bitmask)
        if status != 0: return status
        common_func.ftdi_i2c_stop(self.ftdic, pins)

    def pca6416_get_output(self, pins):
        """returns the current pins configuration of the PCA"""
        logging.debug('pca_get_output')
        add_write = (pins['pca6416'][0] << 1) + 0
        add_read = (pins['pca6416'][0] << 1) + 1
        conf_cmd = (pins['pca6416'][1])
        conf_cmd = conf_cmd + 0x02 if (self.name != 'val_board_1' and self.name != 'val_board_2') else conf_cmd + 0x04
        common_func.ftdi_i2c_start(self.ftdic, pins)
        status = common_func.ftdi_i2c_write(self.ftdic, pins, add_write)
        if status != 0: return status
        status = common_func.ftdi_i2c_write(self.ftdic, pins, conf_cmd)
        if status != 0: return status
        common_func.ftdi_i2c_start(self.ftdic, pins)
        status = common_func.ftdi_i2c_write(self.ftdic, pins, add_read)
        if status != 0: return status
        current_out = common_func.ftdi_i2c_read(self.ftdic, pins, 1)
        common_func.ftdi_i2c_stop(self.ftdic, pins)
        return current_out[0] & pins['pca6416'][2]

    def ftdi_gpio_write(self, gpio_name, gpio_value):
        """writes desired value to the gpio passed in parameter"""
        logging.debug('ftdi_gpio_write')
        gpio_add = gpio_name['ftdi'][1]
        current_output = common_func.ftdic_read_gpio(self.ftdic)
        logging.debug('current GPIO configuration: ' + hex(current_output))
        if not gpio_value:
            data = current_output & ~gpio_add
            common_func.ftdic_write_gpio(self.ftdic, data)
        if gpio_value == 1 or gpio_value == 0xFF:
            data = current_output | gpio_add
            common_func.ftdic_write_gpio(self.ftdic, data)
        if gpio_value == 2:
            data = current_output ^ gpio_add
            common_func.ftdic_write_gpio(self.ftdic, data)
            time.sleep(0.5)
            common_func.ftdic_write_gpio(self.ftdic, current_output)
        # add traces as debug
        current_output = common_func.ftdic_read_gpio(self.ftdic)
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
        dev_list =self.eeprom.list_eeprom_devices()
        __, desc = self.eeprom.detect_type(dev_list[self.id])
        self.ftdic = common_func.ftdi_open(self.id, channel, desc)
        if mode == 0:  # if GPIO mode
            for gpio in self.board_mapping_gpio:  # if channel 0, parse gpio default value of channel 0
                if gpio['ftdi'][0] == channel:
                    out_pins += gpio['ftdi'][1]
                    common_func.ftdic_setbitmode(self.ftdic, 0xFF, 0x1)
        if mode == 1:  # if I2C mode
            common_func.ftdic_setbitmode(self.ftdic, 0x0, 0x00)  # reset the controller
            common_func.ftdic_setbitmode(self.ftdic, 0x0, 0x02)  # set as MPSSE
            common_func.ftdi_i2c_init(self.ftdic, pins)  # Init FT4232H MPSSE with correct parameters
        logging.info('Done.')

    def resume(self):
        print("start resuming / suspending...")
        gpio = next((item for item in self.board_mapping_gpio if
                     (item['name'] == 'FTA_PWR_ON_OFF' or item['name'] == 'FT_ONOFF_B')), None)
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
            if gpio.get("BOOT_MODE"):
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
                     (item['name'] == 'RESET')), None)
        if gpio is None:
            gpio = next((item for item in self.board_mapping_gpio_i2c if
                         (item['name'] == 'RESET')), None)
        mask = gpio['default'] & 0xF
        self.set_gpio(gpio, 0x00 if mask else 0xFF)
        time.sleep(0.5)
        if mode:
            self.set_gpio(gpio, 0xFF if mask else 0x00)
        else:
            gpio = next((item for item in self.board_mapping_gpio_i2c if item['name'] == 'BOOT_SRC_SEL'), None)
            if gpio:
                self.set_gpio(gpio, 0xFF)
                gpio = next((item for item in self.board_mapping_gpio if item['name'] == 'RESET'), None)
                mask = gpio['default'] & 0xF
                self.set_gpio(gpio, 0xFF if mask else 0x00)
            else:
                gpio = next((item for item in self.board_mapping_gpio_i2c if item['name'] == 'REMOTE_EN'), None)
                if gpio is None:
                    gpio = next((item for item in self.board_mapping_gpio if item['name'] == 'REMOTE_EN'), None)
                mask = gpio['default'] & 0xF
                self.set_gpio(gpio, 0x00 if mask else 0xFF)
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
        gpio = next((item for item in self.board_mapping_gpio_i2c if item['name'] == self.rails_to_display[rail_num]['rsense_ctl']), None)
        if CURR_RSENSE.get(self.rails_to_display[rail_num]['name']) == self.rails_to_display[rail_num]['rsense'][1]:  # switch low_current shunt to high_current shunt
            gpio_value = self.rails_to_display[rail_num]['rsense'][2]
            next_rsense = self.rails_to_display[rail_num]['rsense'][0]
            switch_res_permitted = True
        else:
            sampling_rate = rail['current'].shape[0] / rail['current'][-1, 0]
            number_of_val = int(sampling_rate / 3)
            cur_limit = (100 / self.rails_to_display[rail_num]['rsense'][1]) * 1000
            cur_limit *= (1 - (program_config.LOW_SWITCH_RESISTANCE_OFFSET / 100))
            DATA_LOCK.acquire()
            avg_current = rail['current'][-number_of_val:, 1].mean(0)
            DATA_LOCK.release()
            if avg_current > cur_limit:
                return False, switch_res_permitted
            else:
                gpio_value = not self.rails_to_display[rail_num]['rsense'][2]
                switch_res_permitted = True
                next_rsense = self.rails_to_display[rail_num]['rsense'][1]
        if switch_res_permitted:
            FTDI_LOCK.acquire()
            self.setgpio(gpio, gpio_value * 0xFF)
            check_value = self.pca6416_get_output(gpio)
            FTDI_LOCK.release()
            if (check_value / gpio['pca6416'][2]) != gpio_value:
                return False, switch_res_permitted
            else:
                CURR_RSENSE[self.rails_to_display[rail_num]['name']] = next_rsense
                if len(self.rails_to_display[rail_num]['pac']) > 3:  # in case of 8MP_EVK with PM rail
                    self.rails_to_display[rail_num]['pac'][0], self.rails_to_display[rail_num]['pac'][3] = \
                        self.rails_to_display[rail_num]['pac'][3], self.rails_to_display[rail_num]['pac'][0]
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
        common_func.ftdi_i2c_start(self.ftdic, pins)
        common_func.ftdi_i2c_write(self.ftdic, pins, add_write)
        common_func.ftdi_i2c_write(self.ftdic, pins, 0x00)
        common_func.ftdi_i2c_stop(self.ftdic, pins)

    def pac_set_bipolar(self):
        self.params['bipolar'] = not self.params['bipolar']
        FTDI_LOCK.acquire()
        for index, rail in enumerate(self.board_mapping_power):
            if rail['pac'][2] != self.board_mapping_power[index - 1]['pac'][2]:
                if rail.get('pca9548'):
                    self.pca9548_set_channel(rail)
                add_write = (rail['pac'][1] << 1)
                common_func.ftdi_i2c_start(self.ftdic, rail)
                common_func.ftdi_i2c_write(self.ftdic, rail, add_write)
                common_func.ftdi_i2c_write(self.ftdic, rail, 0x1D)
                if self.params['bipolar']:
                    common_func.ftdi_i2c_write(self.ftdic, rail, 0xF0)
                else:
                    common_func.ftdi_i2c_write(self.ftdic, rail, 0x00)
                    common_func.ftdi_i2c_stop(self.ftdic, rail)
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
        common_func.ftdi_i2c_start(self.ftdic, pins)
        common_func.ftdi_i2c_write(self.ftdic, pins, add_write)
        common_func.ftdi_i2c_write(self.ftdic, pins, register)
        common_func.ftdi_i2c_start(self.ftdic, pins)
        common_func.ftdi_i2c_write(self.ftdic, pins, add_read)
        data = common_func.ftdi_i2c_read_buffer(self.ftdic, pins, 16)
        for i in range(rail_of_pac):
            channel = self.board_mapping_power[i + index]['pac'][0]
            volt = (((data[(2 * channel) - 2] << 8) + data[(2 * channel) - 1]) * 32) / 65535
            voltage.append(volt)
            curr = self.process_current((((data[8 + (2 * channel) - 2] << 8) + data[8 + (2 * channel) - 1]) * 1))
            current.append(curr)
        return voltage, current

    def get_data(self):
        """reads PAC while the app doesn't stop and update shared variable with power/voltage/current"""
        global T_START
        rail_per_pac = {}
        first_probe = True
        self.init_system(self.board_mapping_power[0])
        for index, rail in enumerate(self.board_mapping_power):
            self.init_res(rail)
            self.data_buf.append({'railnumber': rail['name'], 'current': [[0, 0]],
                                  'voltage': [[0, 0]]})
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
        self.pac_set_bipolar()
        T_START = time.time()
        while not FLAG_UI_STOP:
            while FLAG_PAUSE_CAPTURE:
                time.sleep(0.2)
            for index, rail in enumerate(self.board_mapping_power):
                if len(self.board_mapping_power) == 1:
                    FTDI_LOCK.acquire()
                    if rail.get('pca9548'):
                        self.pca9548_set_channel(rail)
                    self.reset_pac(rail)
                    voltage, current = self.block_read(rail, index, rail_per_pac[rail['pac'][2]])
                    FTDI_LOCK.release()
                    t_stop = time.time()
                    DATA_LOCK.acquire()
                    for i in range(rail_per_pac[rail['pac'][2]]):
                        self.data_buf[index + i]['current'].append(
                            [t_stop - T_START, current[i] / CURR_RSENSE[self.data_buf[index + i]['railnumber']]])
                        self.data_buf[index + i]['voltage'].append([t_stop - T_START, voltage[i]])
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
                        if rail.get('pca9548') and self.board_mapping_power[index - 1].get('pca9548'):
                            if rail['pca9548'][0] != self.board_mapping_power[index - 1]['pca9548'][0] or (
                            len(rail_per_pac) == 1 and index < 1):
                                self.pca9548_set_channel(rail)
                        self.reset_pac(rail)
                        voltage, current = self.block_read(rail, index, rail_per_pac[rail['pac'][2]])
                        FTDI_LOCK.release()
                        t_stop = time.time()
                        DATA_LOCK.acquire()
                        for i in range(rail_per_pac[rail['pac'][2]]):
                            if FLAG_PAUSE_CAPTURE:
                                break
                            self.data_buf[index + i]['current'].append(
                                [t_stop - T_START, current[i] / CURR_RSENSE[self.data_buf[index + i]['railnumber']]])
                            self.data_buf[index + i]['voltage'].append([t_stop - T_START, voltage[i]])
                        DATA_LOCK.release()

    def process_temperature(self):
        global T_START
        while not FLAG_UI_STOP:
            while FLAG_PAUSE_CAPTURE:
                time.sleep(0.2)
            FTDI_LOCK.acquire()
            out = self.get_temperature(self.temperature_sensor)
            FTDI_LOCK.release()
            TEMP_DATA_LOCK.acquire()
            out = ((out[1] >> 5) + ((out[0] & 0x01) << 3)) + ((out[0] >> 1) << 4)
            positive_temp = True if out >> 10 == 0 else False
            temp_value = out * 0.125 if positive_temp else out * -0.125
            t_stop = time.time()
            self.temp_buf.append([t_stop - T_START, temp_value])
            TEMP_DATA_LOCK.release()
            time.sleep(1)

    def get_temperature(self, pins):
        out = []
        add_read = (pins['sensor'][0] << 1) + 1
        common_func.ftdi_i2c_init(self.ftdic, pins)
        common_func.ftdi_i2c_start(self.ftdic, pins)
        common_func.ftdi_i2c_write(self.ftdic, pins, add_read)
        out = common_func.ftdi_i2c_read_buffer(self.ftdic, pins, 2)
        common_func.ftdi_i2c_stop(self.ftdic, pins)
        return out
