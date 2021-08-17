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

"""describes the configuration of the board iMX8MP EVK"""
mapping_power = [
    {'name': 'VDD_ARM', 'ftdi': [1, 0x60, 0x40], 'pac': [1, 0x11, 1, 2],
     'rsense': [20, 5010, 1], 'rsense_ctl': 'FT_IO_04'},
    {'name': 'NVCC_DRAM_1V1', 'ftdi': [1, 0x60, 0x40], 'pac': [3, 0x11, 1, 4],
     'rsense': [50, 2050, 1], 'rsense_ctl': 'FT_IO_06'},
    {'name': 'VSYS_5V', 'ftdi': [1, 0x60, 0x40], 'pac': [1, 0x12, 2, 2],
     'rsense': [20, 420, 1], 'rsense_ctl': 'FT_IO_01'},
    {'name': 'VDD_SOC', 'ftdi': [1, 0x60, 0x40], 'pac': [3, 0x12, 2, 4],
     'rsense': [10, 1010, 1], 'rsense_ctl': 'FT_IO_03'},
    {'name': 'LPD4_VDDQ', 'ftdi': [1, 0x60, 0x40], 'pac': [1, 0x13, 3, 2],
     'rsense': [50, 2050, 1], 'rsense_ctl': 'FT_IO_07'},
    {'name': 'LPD4_VDD2', 'ftdi': [1, 0x60, 0x40], 'pac': [3, 0x13, 3],
     'rsense': [50, 50]},
    {'name': 'NVCC_SD2', 'ftdi': [1, 0x60, 0x40], 'pac': [4, 0x13, 3],
     'rsense': [1000, 1000]},
    {'name': 'VDD_LVDS_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [1, 0x14, 4],
     'rsense': [1000, 1000]},
    {'name': 'VDD_HDMI_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [2, 0x14, 4],
     'rsense': [2000, 2000]},
    {'name': 'NVCC_SNVS_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [3, 0x14, 4],
     'rsense': [10000, 509000, 1], 'rsense_ctl': 'FT_IO_02'},
    {'name': 'VDD_EARC_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [4, 0x14, 4],
     'rsense': [2000, 2000]},
    {'name': 'VDD_USB_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [1, 0x15, 5],
     'rsense': [2000, 2000]},
    {'name': 'VDD_PCI_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [2, 0x15, 5],
     'rsense': [1000, 1000]},
    {'name': 'VDD_MIPI_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [3, 0x15, 5],
     'rsense': [2000, 2000]},
    {'name': 'VDD_PLL_ANA_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [4, 0x15, 5],
     'rsense': [1008, 11000, 1], 'rsense_ctl': 'FT_IO_05'},
    {'name': 'NVCC_SD1', 'ftdi': [1, 0x60, 0x40], 'pac': [1, 0x16, 6],
     'rsense': [100, 100]},
    {'name': 'LPD4_VDD1', 'ftdi': [1, 0x60, 0x40], 'pac': [2, 0x16, 6],
     'rsense': [4990, 4990]},
    {'name': 'CPU_VDD_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [3, 0x16, 6],
     'rsense': [100, 100]},
    {'name': 'BB_VDD_1V8', 'ftdi': [1, 0x60, 0x40], 'pac': [4, 0x16, 6],
     'rsense': [50, 50]},
    {'name': 'VDD_PLL_ANA_0V8', 'ftdi': [1, 0x60, 0x40], 'pac': [1, 0x17, 7],
     'rsense': [1000, 1000]},
    {'name': 'VDD_PCI_0V8', 'ftdi': [1, 0x60, 0x40], 'pac': [2, 0x17, 7],
     'rsense': [400, 400]},
    {'name': 'VDD_MIPI_0V8', 'ftdi': [1, 0x60, 0x40], 'pac': [3, 0x17, 7],
     'rsense': [1000, 1000]},
    {'name': 'VDD_HDMI_0V8', 'ftdi': [1, 0x60, 0x40], 'pac': [4, 0x17, 7],
     'rsense': [1000, 1000]},
    {'name': 'VDD_USB_3V3', 'ftdi': [1, 0x60, 0x40], 'pac': [1, 0x18, 8],
     'rsense': [1000, 1000]},
    {'name': 'VDD_USB_0V8', 'ftdi': [1, 0x60, 0x40], 'pac': [2, 0x18, 8],
     'rsense': [400, 400]},
    {'name': 'VDD_SD1_3V3', 'ftdi': [1, 0x60, 0x40], 'pac': [3, 0x18, 8],
     'rsense': [250, 250]},
    {'name': 'BB_VDD_3V3', 'ftdi': [1, 0x60, 0x40], 'pac': [4, 0x18, 8],
     'rsense': [50, 50]}
]

power_groups = [
    {'name': 'GROUP_SOC', 'rails': ['VDD_ARM', 'VDD_SOC', 'NVCC_SNVS_1V8', 'VDD_PLL_ANA_0V8', 'VDD_PLL_ANA_1V8',
                                    'NVCC_DRAM_1V1', 'VDD_HDMI_0V8', 'VDD_HDMI_1V8', 'VDD_MIPI_0V8', 'VDD_MIPI_1V8',
                                    'VDD_PCI_0V8', 'VDD_PCI_1V8', 'VDD_USB_0V8', 'VDD_USB_1V8', 'VDD_USB_3V3',
                                    'VDD_LVDS_1V8', 'VDD_EARC_1V8']},
    {'name': 'GROUP_SOC_FULL', 'rails': ['VDD_ARM', 'VDD_SOC', 'NVCC_SNVS_1V8', 'VDD_PLL_ANA_0V8', 'VDD_PLL_ANA_1V8',
                                         'NVCC_DRAM_1V1', 'VDD_HDMI_0V8', 'VDD_HDMI_1V8', 'VDD_MIPI_0V8',
                                         'VDD_MIPI_1V8', 'VDD_PCI_0V8', 'VDD_PCI_1V8', 'VDD_USB_0V8', 'VDD_USB_1V8',
                                         'VDD_USB_3V3', 'VDD_LVDS_1V8', 'VDD_EARC_1V8', 'CPU_VDD_1V8', 'NVCC_SD1',
                                         'NVCC_SD2']},
    {'name': 'GROUP_DRAM', 'rails': ['LPD4_VDD1', 'LPD4_VDD2', 'LPD4_VDDQ']},
    {'name': 'GROUP_PLATFORM', 'rails': ['VSYS_5V']}

]

mapping_gpio_i2c = [{'name': 'FT_BOOT_MODE', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 0, 0x0F], 'default': 0x30},
                    {'name': 'FT_IO_01', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 0, 0x10], 'default': 0},
                    {'name': 'FT_IO_02', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 0, 0x20], 'default': 0},
                    {'name': 'FT_IO_03', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 0, 0x40], 'default': 0},
                    {'name': 'FT_IO_04', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 0, 0x80], 'default': 0},
                    {'name': 'FT_REMOTE_SEL', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 1, 0x01], 'default': 0x41},
                    {'name': 'FT_IO_05', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 1, 0x02], 'default': 0},
                    {'name': 'FT_IO_06', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 1, 0x04], 'default': 0},
                    {'name': 'FT_IO_07', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 1, 0x08], 'default': 0},
                    {'name': 'FT_IO_08', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 1, 0x10], 'default': 0},
                    {'name': 'FT_IO_09', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 1, 0x20], 'default': 0},
                    {'name': 'FT_IO_010', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 1, 0x40], 'default': 0},
                    {'name': 'FT_IO_011', 'ftdi': [1, 0xF0, 0x00], 'pca6416': [0x20, 1, 0x80], 'default': 0}
                   ]

mapping_gpio = [{'name': 'FT_RESET_B', 'ftdi': [0, 0x10], 'default': 0},
                {'name': 'FT_SYS_nRST', 'ftdi': [0, 0x20], 'default': 0x21},
                {'name': 'FT_IO_nRST', 'ftdi': [0, 0x40], 'default': 0x11},
                {'name': 'FT_ONOFF_B', 'ftdi': [0, 0x80], 'default': 0},
                {'name': 'FT_IO_nINT', 'ftdi': [1, 0x08], 'default': 0},
                {'name': 'FT_GPIO1', 'ftdi': [1, 0x10], 'default': 0},
                {'name': 'FT_GPIO2', 'ftdi': [1, 0x20], 'default': 0},
                {'name': 'FT_GPIO3', 'ftdi': [1, 0x40], 'default': 0},
                {'name': 'FT_GPIO4', 'ftdi': [1, 0x80], 'default': 0}
               ]

boot_modes = {
    'fuse': 0x00,
    'usb': 0x01,
    'emmc': 0x02,
    'sd': 0x03,
    'nand_256': 0x04,
    'nand_512': 0x05,
    'qspi_3b_read': 0x06,
    'qspi_hyperflash': 0x07,
    'ecspi': 0x08,
    'infinite_loop': 0x0E
}
