# Copyright 2021 NXP
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

"""describes the configuration of the board iMX8ULP EVK"""
mapping_power = [
    {'name': 'BUCK4_CPU_1V1', 'ftdi': [1, 0xF0, 0x10], 'pac': [1, 0x10, 1, 2], 'rsense': [400, 400, 1],
     'rsense_ctl': 'FT_IO_01'},
    {'name': 'BUCK1_CPU_1V8', 'ftdi': [1, 0xF0, 0x10], 'pac': [3, 0x10, 1, 4], 'rsense': [100, 10000, 1],
     'rsense_ctl': 'FT_IO_00'},
    {'name': 'BUCK2_CPU_1V0', 'ftdi': [1, 0xF0, 0x10], 'pac': [1, 0x11, 2, 2], 'rsense': [50, 10000, 1],
     'rsense_ctl': 'FT_IO_02'},
    {'name': 'BUCK3_CPU_1V0', 'ftdi': [1, 0xF0, 0x10], 'pac': [3, 0x11, 2, 4], 'rsense': [20, 10000, 1],
     'rsense_ctl': 'FT_IO_03'},
    {'name': 'LDO5_CPU_3V0', 'ftdi': [1, 0xF0, 0x10], 'pac': [1, 0x12, 3], 'rsense': [250000, 250000]},
    {'name': 'LDO1_CPU_1V1', 'ftdi': [1, 0xF0, 0x10], 'pac': [2, 0x12, 3], 'rsense': [100, 100]},
    {'name': 'BUCK1_LSW1_CPU_1V8', 'ftdi': [1, 0xF0, 0x10], 'pac': [3, 0x12, 3], 'rsense': [100, 100]},
    {'name': 'BUCK1_LSW4_CPU_1V8', 'ftdi': [1, 0xF0, 0x10], 'pac': [4, 0x12, 3], 'rsense': [100, 100]},
    {'name': 'BUCK1_LSW2_CPU_1V8', 'ftdi': [1, 0xF0, 0x10], 'pac': [1, 0x13, 4], 'rsense': [100, 100]},
    {'name': 'BUCK1_LSW3_CPU_1V8', 'ftdi': [1, 0xF0, 0x10], 'pac': [2, 0x13, 4], 'rsense': [100, 100]},
    {'name': 'LDO4_CPU_1V8', 'ftdi': [1, 0xF0, 0x10], 'pac': [3, 0x13, 4], 'rsense': [100, 100]},
    {'name': 'LDO2_CPU_3V3', 'ftdi': [1, 0xF0, 0x10], 'pac': [4, 0x13, 4], 'rsense': [100, 100]},
    {'name': 'VSYS_5V0_4V2', 'ftdi': [1, 0xF0, 0x10], 'pac': [1, 0x14, 5, 2], 'rsense': [20, 10000, 1],
     'rsense_ctl': 'FT_IO_04'},
    {'name': 'LDO1_CPU_1V1_0V6', 'ftdi': [1, 0xF0, 0x10], 'pac': [3, 0x14, 5], 'rsense': [50, 50]},
    {'name': 'BUCK4_DRAM_1V1', 'ftdi': [1, 0xF0, 0x10], 'pac': [4, 0x14, 5], 'rsense': [50, 50]}
]

power_groups = [
    {'name': 'GROUP_SOC_FULL',
     'rails': ['BUCK1_CPU_1V8', 'BUCK2_CPU_1V0', 'BUCK3_CPU_1V0', 'BUCK4_CPU_1V1', 'LDO1_CPU_1V1',
               'LDO1_CPU_1V1_0V6', 'BUCK1_LSW2_CPU_1V8', 'BUCK1_LSW3_CPU_1V8', 'LDO5_CPU_3V0', 'LDO2_CPU_3V3',
               'BUCK1_LSW1_CPU_1V8', 'LDO4_CPU_1V8', 'BUCK1_LSW4_CPU_1V8']},
    {'name': 'GROUP_PLATFORM', 'rails': ['VSYS_5V0_4V2']}
]

mapping_gpio_i2c = [
    {'name': 'FT_BOOT_MODE', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 0, 0xFF], 'default': 0x40},
    {'name': 'FT_REMOTE_EN', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 1, 0x01], 'default': 0x51},
    {'name': 'FT_SYS_RST', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 1, 0x02], 'default': 0x20},
    {'name': 'FT_ONOFF', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 1, 0x04], 'default': 0x30},
    {'name': 'RESET0_B_BUFFER', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 1, 0x08], 'default': 0},
    {'name': 'RESET1_B_BUFFER', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 1, 0x10], 'default': 0},
    {'name': 'CPU_POWER_MODE0', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 1, 0x20], 'default': 0},
    {'name': 'CPU_POWER_MODE1', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 1, 0x40], 'default': 0},
    {'name': 'CPU_POWER_MODE2', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x20, 1, 0x80], 'default': 0},
    {'name': 'FT_IO_00', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x21, 0, 0x01], 'default': 0},
    {'name': 'FT_IO_01', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x21, 0, 0x02], 'default': 0},
    {'name': 'FT_IO_02', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x21, 0, 0x04], 'default': 0},
    {'name': 'FT_IO_03', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x21, 0, 0x08], 'default': 0},
    {'name': 'FT_IO_04', 'ftdi': [1, 0xF0, 0x10], 'pca6416': [0x21, 0, 0x10], 'default': 0}
]

mapping_gpio = [{'name': 'FTB_INT_B', 'ftdi': [1, 0x08], 'default': 0x00},
                {'name': 'FTB_RESET_B', 'ftdi': [1, 0x10], 'default': 0x11}
                ]

boot_modes = {
    'fuse': 0x00,
    'usb': 0x40,
    'emmc_s': 0x80,
    'emmc_nor_lp': 0x81,
    'emmc_nor': 0x82,
    'nand_nor': 0x92,
    'nor_s': 0xa0,
    'nor_nor_lp': 0xa1,
    'nor_nor': 0xa2,
}
