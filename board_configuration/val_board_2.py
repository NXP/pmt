# Copyright 2021-2022 NXP
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

"""describes the configuration of the board val_board_2"""
mapping_power = [
    {
        "name": "VBUS_IN",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x10, 1],
        "rsense": [10, 10],
    },
    {
        "name": "DCDC_5V",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [2, 0x10, 1],
        "rsense": [10, 10],
    },
    {
        "name": "VDD_5V",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x10, 1],
        "rsense": [20, 20],
    },
    {
        "name": "VDDEXT_3V3",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [4, 0x10, 1],
        "rsense": [20, 20],
    },
    {
        "name": "VDD_ARM",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x11, 2, 2],
        "rsense": [20, 5010, 1],
        "rsense_ctl": "FT_IO_07",
    },
    {
        "name": "NVCC_DRAM_1V1",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x11, 2, 4],
        "rsense": [50, 2050, 1],
        "rsense_ctl": "FT_IO_08",
    },
    {
        "name": "VSYS_5V",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x12, 3, 2],
        "rsense": [20, 420, 1],
        "rsense_ctl": "FT_IO_01",
    },
    {
        "name": "VDD_SOC",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x12, 3, 4],
        "rsense": [20, 1020, 1],
        "rsense_ctl": "FT_IO_03",
    },
    {
        "name": "VQSPI_1V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x13, 4],
        "rsense": [1000, 1000],
    },
    {
        "name": "LPD4_VDDQ",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [2, 0x13, 4],
        "rsense": [100, 100],
    },
    {
        "name": "LPD4_VDD2",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x13, 4],
        "rsense": [50, 50],
    },
    {
        "name": "NVCC_SD2",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [4, 0x13, 4],
        "rsense": [1000, 1000],
    },
    {
        "name": "VDD_PHY_0V9",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x14, 5],
        "rsense": [1000, 1000],
    },
    {
        "name": "VDD_PHY_1V2",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [2, 0x14, 5],
        "rsense": [1000, 1000],
    },
    {
        "name": "NVCC_SNVS_1V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x14, 5, 3],
        "rsense": [10000, 509000, 1],
        "rsense_ctl": "FT_IO_02",
    },
    {
        "name": "VDD_SNVS_0V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [4, 0x14, 5, 4],
        "rsense": [10000, 509000, 1],
        "rsense_ctl": "FT_IO_04",
    },
    {
        "name": "VDD_GPU",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x15, 6, 2],
        "rsense": [50, 10050, 1],
        "rsense_ctl": "FT_IO_05",
    },
    {
        "name": "VDD_MIPI_1V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x15, 6],
        "rsense": [2000, 2000],
    },
    {
        "name": "VDD_PLL_ANA_1V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [4, 0x15, 6],
        "rsense": [200, 200],
    },
    {
        "name": "NVCC_SD1",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x16, 7],
        "rsense": [100, 100],
    },
    {
        "name": "LPD4_VDD1",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [2, 0x16, 7],
        "rsense": [4990, 4990],
    },
    {
        "name": "CPU_VDD_1V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x16, 7],
        "rsense": [100, 100],
    },
    {
        "name": "BB_VDD_1V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [4, 0x16, 7],
        "rsense": [50, 50],
    },
    {
        "name": "VDD_PLL_ANA_0V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x17, 8],
        "rsense": [1000, 1000],
    },
    {
        "name": "VDD_USB_1V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [2, 0x17, 8],
        "rsense": [2000, 2000],
    },
    {
        "name": "CPU_VDD_3V3",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x17, 8],
        "rsense": [100, 100],
    },
    {
        "name": "VCCQ_SD1",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [4, 0x17, 8],
        "rsense": [100, 100],
    },
    {
        "name": "VDD_USB_3V3",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x18, 9],
        "rsense": [1000, 1000],
    },
    {
        "name": "VDD_USB_0V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [2, 0x18, 9],
        "rsense": [400, 400],
    },
    {
        "name": "VDD_SD1_3V3",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x18, 9],
        "rsense": [250, 250],
    },
    {
        "name": "BB_VDD_3V3",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [4, 0x18, 9],
        "rsense": [50, 50],
    },
    {
        "name": "VDD_DRAM",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [1, 0x1A, 11, 2],
        "rsense": [50, 10050, 1],
        "rsense_ctl": "FT_IO_06",
    },
    {
        "name": "VDD_DRAM_PLL_0V8",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [3, 0x1A, 11],
        "rsense": [250, 250],
    },
    {
        "name": "NVCC_ENET",
        "ftdi": [1, 0xF0, 0x00],
        "pac": [4, 0x1A, 11],
        "rsense": [100, 100],
    },
]

power_groups = [
    {
        "name": "GROUP_SOC",
        "rails": [
            "NVCC_SNVS_1V8",
            "VDD_SNVS_0V8",
            "VDD_SOC",
            "VDD_PLL_ANA_0V8",
            "VDD_USB_0V8",
            "VDD_GPU",
            "VDD_DRAM",
            "VDD_DRAM_PLL_0V8",
            "VDD_PHY_0V9",
            "VDD_ARM",
            "VDD_PLL_ANA_1V8",
            "VDD_USB_1V8",
            "VDD_MIPI_1V8",
            "NVCC_DRAM_1V1",
            "VDD_USB_3V3",
            "VDD_PHY_1V2",
        ],
    },
    {
        "name": "GROUP_SOC_FULL",
        "rails": [
            "NVCC_SNVS_1V8",
            "VDD_SNVS_0V8",
            "VDD_SOC",
            "VDD_PLL_ANA_0V8",
            "VDD_USB_0V8",
            "VDD_GPU",
            "VDD_DRAM",
            "VDD_DRAM_PLL_0V8",
            "VDD_PHY_0V9",
            "VDD_ARM",
            "VDD_PLL_ANA_1V8",
            "VDD_USB_1V8",
            "VDD_MIPI_1V8",
            "NVCC_DRAM_1V1",
            "VDD_USB_3V3",
            "VDD_PHY_1V2",
            "CPU_VDD_1V8",
            "NVCC_SD1",
            "NVCC_SD2",
            "NVCC_ENET",
            "CPU_VDD_3V3",
        ],
    },
    {"name": "GROUP_DRAM", "rails": ["LPD4_VDD1", "LPD4_VDDQ", "LPD4_VDD2"]},
    {"name": "GROUP_PLATFORM", "rails": ["VBUS_IN"]},
]

mapping_gpio_i2c = [
    {
        "name": "BOOT_MODE",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 0, 0x0F],
        "default": 0x30,
    },
    {
        "name": "FT_IO_01",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 0, 0x10],
        "default": 0,
    },
    {
        "name": "FT_IO_02",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 0, 0x20],
        "default": 0,
    },
    {
        "name": "FT_IO_03",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 0, 0x40],
        "default": 0,
    },
    {
        "name": "FT_IO_04",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 0, 0x80],
        "default": 0,
    },
    {
        "name": "REMOTE_EN",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 1, 0x01],
        "default": 0x41,
    },
    {
        "name": "FT_IO_05",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 1, 0x02],
        "default": 0,
    },
    {
        "name": "FT_IO_06",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 1, 0x04],
        "default": 0,
    },
    {
        "name": "FT_IO_07",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 1, 0x08],
        "default": 0,
    },
    {
        "name": "FT_IO_08",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 1, 0x10],
        "default": 0,
    },
    {
        "name": "FT_IO_09",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 1, 0x20],
        "default": 0,
    },
    {
        "name": "FT_IO_010",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 1, 0x40],
        "default": 0,
    },
    {
        "name": "FT_IO_011",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x22, 1, 0x80],
        "default": 0,
    },
    {
        "name": "FT_BT_CFG0",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x23, 0, 0xFF],
        "default": 0,
    },
    {
        "name": "FT_BT_CFG1",
        "ftdi": [1, 0xF0, 0x00],
        "pca6416": [0x23, 1, 0xFF],
        "default": 0,
    },
]

mapping_gpio = [
    {"name": "FT_RESET_B", "ftdi": [0, 0x10], "default": 0},
    {"name": "RESET", "ftdi": [0, 0x20], "default": 0x21},
    {"name": "FT_IO_nRST", "ftdi": [0, 0x40], "default": 0x11},
    {"name": "FT_ONOFF_B", "ftdi": [0, 0x80], "default": 0},
    {"name": "FT_GPIO1", "ftdi": [1, 0x10], "default": 0},
    {"name": "FT_GPIO2", "ftdi": [1, 0x20], "default": 0},
    {"name": "FT_GPIO3", "ftdi": [1, 0x40], "default": 0},
    {"name": "FT_IO_nINT", "ftdi": [1, 0x80], "default": 0},
]

boot_modes = {"fuse": 0x00, "usb": 0x01, "internal_boot": 0x02}

temperature_sensor = {"ftdi": [1, 0xF0, 0x00], "sensor": [0x48]}
