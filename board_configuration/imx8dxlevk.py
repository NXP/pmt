# Copyright 2020-2021 NXP
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

"""describes the configuration of the board iMX8DXL EVK"""
mapping_power = [
    {'name': '5V0', 'ftdi': [1, 0x60, 0x40], 'pca9548': [1, 0x70], 'pac': [1, 0x10, 1], 'rsense': [10, 10]},
    {'name': '3V3_USB', 'ftdi': [1, 0x60, 0x40], 'pca9548': [1, 0x70], 'pac': [2, 0x10, 1],
     'rsense': [1650, 1650]},
    {'name': '3V3_IO', 'ftdi': [1, 0x60, 0x40], 'pca9548': [1, 0x70], 'pac': [3, 0x10, 1],
     'rsense': [1650, 1650]},
    {'name': 'VDD_ENET0_SEL', 'ftdi': [1, 0x60, 0x40], 'pca9548': [1, 0x70], 'pac': [4, 0x10, 1],
     'rsense': [3300, 3300]},
    {'name': '3V3_PMIC', 'ftdi': [1, 0x60, 0x40], 'pca9548': [2, 0x70], 'pac': [1, 0x10, 2], 'rsense': [10, 10]},
    {'name': '3V3', 'ftdi': [1, 0x60, 0x40], 'pca9548': [2, 0x70], 'pac': [2, 0x10, 2], 'rsense': [10, 10]},
    {'name': 'VDD_SNVS1', 'ftdi': [1, 0x60, 0x40], 'pca9548': [2, 0x70], 'pac': [3, 0x10, 2],
     'rsense': [2000, 2000]},
    {'name': 'VDD_MAIN', 'ftdi': [1, 0x60, 0x40], 'pca9548': [2, 0x70], 'pac': [4, 0x10, 2],
     'rsense': [64, 10000, 1], 'rsense_ctl': 'VDD_MAIN_I_SW'},
    {'name': 'VDD_MEMC', 'ftdi': [1, 0x60, 0x40], 'pca9548': [3, 0x70], 'pac': [1, 0x10, 3],
     'rsense': [54, 10000, 1], 'rsense_ctl': 'VDD_MEMC_I_SW'},
    {'name': 'VDD_DDR_VDDQ', 'ftdi': [1, 0x60, 0x40], 'pca9548': [3, 0x70], 'pac': [2, 0x10, 3],
     'rsense': [124, 10000, 1], 'rsense_ctl': 'VDD_DDRIO_I_SW'},
    {'name': 'DDR_VDD2', 'ftdi': [1, 0x60, 0x40], 'pca9548': [3, 0x70], 'pac': [3, 0x10, 3], 'rsense': [10, 10]},
    {'name': 'VDD_ENET_IO', 'ftdi': [0, 0x60, 0x40], 'pca9548': [3, 0x70], 'pac': [4, 0x10, 3],
     'rsense': [3320, 3320]},
    {'name': 'VDD_ANA', 'ftdi': [1, 0x60, 0x40], 'pca9548': [4, 0x70], 'pac': [1, 0x10, 4],
     'rsense': [4, 10000, 1], 'rsense_ctl': 'VDD_ANA_I_SW'},
    {'name': 'DDR_VDD1', 'ftdi': [1, 0x60, 0x40], 'pca9548': [4, 0x70], 'pac': [2, 0x10, 4], 'rsense': [10, 10]},
    {'name': '1V8_1', 'ftdi': [1, 0x60, 0x40], 'pca9548': [4, 0x70], 'pac': [3, 0x10, 4], 'rsense': [600, 600]},
    {'name': '1V8_2', 'ftdi': [1, 0x60, 0x40], 'pca9548': [4, 0x70], 'pac': [4, 0x10, 4],
     'rsense': [1000, 1000]},
    {'name': '1V8_3', 'ftdi': [1, 0x60, 0x40], 'pca9548': [5, 0x70], 'pac': [1, 0x10, 5],
     'rsense': [1000, 1000]},
    {'name': '1V8_4', 'ftdi': [1, 0x60, 0x40], 'pca9548': [5, 0x70], 'pac': [2, 0x10, 5], 'rsense': [680, 680]},
    {'name': '1V8_5', 'ftdi': [1, 0x60, 0x40], 'pca9548': [5, 0x70], 'pac': [3, 0x10, 5], 'rsense': [440, 440]},
    {'name': '1V8', 'ftdi': [1, 0x60, 0x40], 'pca9548': [5, 0x70], 'pac': [4, 0x10, 5], 'rsense': [10, 10]},
    {'name': '1V8_6', 'ftdi': [1, 0x60, 0x40], 'pca9548': [6, 0x70], 'pac': [1, 0x10, 6], 'rsense': [10, 10]},
    {'name': 'ANA1', 'ftdi': [1, 0x60, 0x40], 'pca9548': [6, 0x70], 'pac': [2, 0x10, 6], 'rsense': [500, 500]},
    {'name': 'EMMC0', 'ftdi': [1, 0x60, 0x40], 'pca9548': [6, 0x70], 'pac': [3, 0x10, 6],
     'rsense': [3000, 3000]},
    {'name': 'FLT_12V0', 'ftdi': [1, 0x60, 0x40], 'pca9548': [6, 0x70], 'pac': [4, 0x10, 6], 'rsense': [10, 10]}
]

power_groups = [
    {'name': 'GROUP_SOC', 'rails': ['VDD_MAIN', '3V3_USB', 'VDD_ENET0_SEL', 'VDD_SNVS1', 'VDD_MEMC', 'VDD_DDR_VDDQ',
                                    'VDD_ANA', '1V8_1', '1V8_4', '1V8_5']},
    {'name': 'GROUP_SOC_FULL', 'rails': ['VDD_MAIN', '3V3_USB', 'VDD_ENET0_SEL', 'VDD_SNVS1', 'VDD_MEMC',
                                         'VDD_DDR_VDDQ', 'VDD_ANA', '1V8_1', '1V8_4', '1V8_5', '3V3_IO',
                                         'VDD_ENET_IO', '1V8_2', '1V8_3']},
    {'name': 'GROUP_DRAM', 'rails': ['DDR_VDD1', 'DDR_VDD2']},
    {'name': 'GROUP_PLATFORM', 'rails': ['FLT_12V0']}
]

mapping_gpio_i2c = [
    {'name': 'HOST_BOOT_MODE', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 0, 0x07],
     'default': 0x80},
    {'name': 'HOST_SD_PWR', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 0, 0x08],
     'default': 0x51},
    {'name': 'HOST_SD_WP', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 0, 0x10],
     'default': 0x61},
    {'name': 'HOST_SD_CD', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 0, 0x20],
     'default': 0x71},
    {'name': 'EXP5_P0_6', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 0, 0x40], 'default': 0},
    {'name': 'EXP5_P0_7', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 0, 0x80], 'default': 0},
    {'name': 'VDD_MAIN_I_SW', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 1, 0x01],
     'default': 0},
    {'name': 'VDD_MEMC_I_SW', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 1, 0x02],
     'default': 0},
    {'name': 'VDD_DDRIO_I_SW', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 1, 0x04],
     'default': 0},
    {'name': 'VDD_ANA_I_SW', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 1, 0x08],
     'default': 0},
    {'name': 'EXP5_P1_4', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 1, 0x10], 'default': 0},
    {'name': 'EXP5_P1_5', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 1, 0x20], 'default': 0},
    {'name': 'TEST_MODE_SELECT', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 1, 0x40],
     'default': 0},
    {'name': 'BOOT_SRC_SEL', 'ftdi': [1, 0x60, 0x40], 'pca9548': [0, 0x70], 'pca6416': [0x20, 1, 0x80],
     'default': 0x90}
]

mapping_gpio = [{'name': 'FTA_RESET', 'ftdi': [0, 0x20], 'default': 0x11},
                {'name': 'JTAG_SEL', 'ftdi': [0, 0x40], 'default': 0x01},
                {'name': 'FTA_PWR_ON_OFF', 'ftdi': [0, 0x80], 'default': 0x21},
                {'name': 'FTB_SELECT', 'ftdi': [1, 0x20], 'default': 0x40},
                {'name': 'FTB_RESET', 'ftdi': [1, 0x40], 'default': 0x31}
                ]

boot_modes = {
    'efuse': 0x00,
    'usb': 0x01,
    'emmc': 0x02,
    'sd': 0x03,
    'nand': 0x04,
    'm4_infinite_loop': 0x05,
    'spi': 0x06,
    'dft_burnin_mode': 0x07
}
