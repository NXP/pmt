# Copyright 2022 NXP
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

"""describes the configuration of the board iMX93 EVK"""
mapping_power = [
    {
        "name": "VDD_1V8",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [1, 0x11, 1],
        "rsense": [20, 20],
    },
    {
        "name": "VDD_3V3",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [3, 0x11, 1],
        "rsense": [20, 20],
    },
    {
        "name": "NVCC_BBSM_1P8",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [4, 0x11, 1],
        "rsense": [10000, 10000],
    },
    {
        "name": "LPD4X_VDDQ",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [1, 0x12, 2],
        "rsense": [250, 250],
    },
    {
        "name": "VDD_SOC",  # Low/High shunts are not in the same PAC
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [2, 0x12, 2, 2, 0x11, 1],
        "rsense": [20, 1020, 1],
        "rsense_ctl": "FSC_CTRL_3",
    },
    {
        "name": "NVCC_SD2",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [3, 0x12, 2],
        "rsense": [1000, 1000],
    },
    {
        "name": "VDD2_DDR",  # Low/High shunts are not in the same PAC
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [4, 0x12, 2, 3, 0x13, 3],
        "rsense": [50, 2050, 1],
        "rsense_ctl": "FSC_CTRL_4",
    },
    {
        "name": "VDDQ_DDR",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [2, 0x13, 3, 1],
        "rsense": [50, 2050, 1],
        "rsense_ctl": "FSC_CTRL_5",
    },
    {
        "name": "LPD4X_VDD2",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [4, 0x13, 3],
        "rsense": [100, 100],
    },
    {
        "name": "VSYS_5V",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [1, 0x14, 4],
        "rsense": [20, 20],
    },
    {
        "name": "NVCC_3P3",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [2, 0x14, 4],
        "rsense": [100, 100],
    },
    {
        "name": "VDD_USB_3P3",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [3, 0x14, 4],
        "rsense": [4990, 4990],
    },
    {
        "name": "VDD_ANA_0P8",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [4, 0x14, 4],
        "rsense": [400, 400],
    },
    {
        "name": "LPD4X_VDD1",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [1, 0x15, 5],
        "rsense": [250, 250],
    },
    {
        "name": "VDD_ANA_1P8",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [2, 0x15, 5],
        "rsense": [250, 250],
    },
    {
        "name": "VSD2_3V3",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [3, 0x15, 5],
        "rsense": [100, 100],
    },
    {
        "name": "NVCC_1P8",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [4, 0x15, 5],
        "rsense": [100, 100],
    },
    {
        "name": "VPCIE_3V3",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [1, 0x16, 6],
        "rsense": [10, 10],
    },
    {
        "name": "DCDC_5V",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [2, 0x16, 6],
        "rsense": [10, 10],
    },
    {
        "name": "VSYS_IN",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [3, 0x16, 6],
        "rsense": [10, 10],
    },
    {
        "name": "VDD_5V_IN",
        "ftdi": [1, 0xF0, 0xF0],
        "pac": [4, 0x16, 6],
        "rsense": [10, 10],
    },
]

power_groups = [
    {
        "name": "GROUP_SOC",
        "rails": [
            "NVCC_BBSM_1P8",
            "VDD_SOC",
            "VDD2_DDR",
            "VDDQ_DDR",
            "VDD_ANA_0P8",
            "VDD_ANA_1P8",
            "VDD_USB_3P3",
        ],
    },
    {
        "name": "GROUP_SOC_FULL",
        "rails": [
            "NVCC_BBSM_1P8",
            "VDD_SOC",
            "VDD2_DDR",
            "VDDQ_DDR",
            "VDD_ANA_0P8",
            "VDD_ANA_1P8",
            "VDD_USB_3P3",
            "NVCC_SD2",
            "NVCC_3P3",
            "NVCC_1P8",
        ],
    },
    {
        "name": "GROUP_DRAM",
        "rails": [
            "LPD4X_VDD1",
            "LPD4X_VDDQ",
            "LPD4X_VDD2",
        ],
    },
    {"name": "GROUP_PLATFORM", "rails": ["VSYS_IN"]},
]

mapping_gpio_i2c = [
    {
        "name": "BOOT_MODE",
        "ftdi": [1, 0xF0, 0xF0],
        "pca6416": [0x21, 0, 0x0F],
        "default": 0x80,
    },
    {
        "name": "FT_POR_B",
        "ftdi": [1, 0xF0, 0xF0],
        "pca6416": [0x21, 1, 0x01],
        "default": 0x70,
    },
    {
        "name": "RESET",
        "ftdi": [1, 0xF0, 0xF0],
        "pca6416": [0x21, 1, 0x02],
        "default": 0x60,
    },
    {
        "name": "FT_ONOFF",
        "ftdi": [1, 0xF0, 0xF0],
        "pca6416": [0x21, 1, 0x04],
        "default": 0x50,
    },
    {
        "name": "REMOTE_EN",
        "ftdi": [1, 0xF0, 0xF0],
        "pca6416": [0x21, 1, 0x08],
        "default": 0x41,
    },
    {
        "name": "MODE_DIR",
        "ftdi": [1, 0xF0, 0xF0],
        "pca6416": [0x21, 1, 0x10],
        "default": 0x31,
    },
    {
        "name": "FT_SD_PWREN",
        "ftdi": [1, 0xF0, 0xF0],
        "pca6416": [0x21, 1, 0x20],
        "default": 0x11,
    },
    {
        "name": "FT_SD_CD",
        "ftdi": [1, 0xF0, 0xF0],
        "pca6416": [0x21, 1, 0x40],
        "default": 0x21,
    },
    {
        "name": "FSC_CTRL_1",
        "ftdi": [1, 0xF0, 0xF0],
        "adp5585": [0x34, 0, 0x01],
        "default": 0,
    },
    {
        "name": "FSC_CTRL_2",
        "ftdi": [1, 0xF0, 0xF0],
        "adp5585": [0x34, 0, 0x02],
        "default": 0,
    },
    {
        "name": "FSC_CTRL_3",
        "ftdi": [1, 0xF0, 0xF0],
        "adp5585": [0x34, 0, 0x04],
        "default": 0,
    },
    {
        "name": "FSC_CTRL_4",
        "ftdi": [1, 0xF0, 0xF0],
        "adp5585": [0x34, 0, 0x08],
        "default": 0,
    },
    {
        "name": "FSC_CTRL_5",
        "ftdi": [1, 0xF0, 0xF0],
        "adp5585": [0x34, 0, 0x10],
        "default": 0,
    },
]

mapping_gpio = [
    {"name": "FT_IO_NRST1", "ftdi": [1, 0x08], "default": 0x00},
    {"name": "FT_IO_NINT1", "ftdi": [1, 0x10], "default": 0x00},
    {"name": "FT_IO_NINT", "ftdi": [1, 0x20], "default": 0x00},
    {"name": "FT_IO_NRST", "ftdi": [1, 0x40], "default": 0x00},
]

boot_modes = {
    "fuse": 0x00,
    "usb": 0x01,
    "emmc": 0x02,
    "sd": 0x03,
    "nor": 0x04,
    "nand_2k": 0x05,
    "infinite_loop": 0x06,
    "test_mode": 0x07,
    "m_fuse": 0x08,
    "m_usb": 0x09,
    "m_emmc": 0x0A,
    "m_sd": 0x0B,
    "m_nor": 0x0C,
    "m_nand_2k": 0x0D,
    "m_infinite_loop": 0x0E,
    "m_test_mode": 0x0F,
}

temperature_sensor = {"ftdi": [1, 0xF0, 0x00], "sensor": [0x48]}
