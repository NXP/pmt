# Copyright 2025 NXP
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

mapping_power = [
        {
            "name": "VDD_ARM",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [1, 0x11, 1],
            "rsense": [5,5],
        },
        {
            "name": "VDD_SOC",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [2, 0x11, 1],
            "rsense": [5,5],
        },
        {
            "name": "LPD5_VDDQ",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [3, 0x11, 1],
            "rsense": [10,10],
        },
        {
            "name": "LPD5_VDD2",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [4, 0x11, 1],
            "rsense": [10,10],
        },
        {
            "name": "LPD5_VDD1",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [1, 0x12, 2],
            "rsense": [400,400],
        },
        {
            "name": "VDD_DDR",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [2, 0x12, 2],
            "rsense": [10,10],
        },
        {
            "name": "VDDQ_DDR",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [3, 0x12, 2],
            "rsense": [10,10],
        },
        {
            "name": "VDD2_DDR",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [4, 0x12, 2],
            "rsense": [250,250],
        },
        {
            "name": "NVCC_SDIO2",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [1, 0x13, 3],
            "rsense": [100,100],
        },
        {
            "name": "NVCC_3V3",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [2, 0x13, 3],
            "rsense": [100,100],
        },
        {
            "name": "VDD_USB_3V3",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [3, 0x13, 3],
            "rsense": [400,400],
        },
        {
            "name": "VDD_ANA_0V8",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [4, 0x13, 3],
            "rsense": [10,10],
        },
        {
            "name": "VDD_ANA_1V8",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [1, 0x14, 4],
            "rsense": [50,50],
        },
        {
            "name": "NVCC_ENET_CCM",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [2, 0x14, 4],
            "rsense": [100,100],
        },
        {
            "name": "NVCC_WAKEUP",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [3, 0x14, 4],
            "rsense": [100,100],
        },
        {
            "name": "NVCC_BBSM_1V8",
            "ftdi": [1, 0xF0, 0xF0],
            "pac": [4, 0x14, 4],
            "rsense": [10000,10000],
        },
]

power_groups= [
        {
                "name": "GROUP_SOC",
                "rails": [
                        "vdd_arm,vdd_soc,nvcc_bbsm_1v8,vdd_ana_1v8,vdd_ana_0v8,vdd_usb_3v3,vdd_ddr,vddq_ddr,vdd2_ddr"
                        ],
                },
                {
                "name": "GROUP_SOC_FULL",
                "rails": [
                        "vdd_arm,vdd_soc,nvcc_bbsm_1v8,vdd_ana_1v8,vdd_ana_0v8,vdd_usb_3v3,vdd_ddr,vddq_ddr,vdd2_ddr,nvcc_sdio2,nvcc_3v3,nvcc_wakeup,nvcc_enet_ccm"
                        ],
                },
                {
                "name": "GROUP_DRAM",
                "rails": [
                        "lpd4x_vdd1,lpd4x_vddq,lpd4x_vdd2"
                        ],
                },
        ]

mapping_gpio_i2c = [
        {
                "name": "BOOT_MODE",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,0,0x0F],
                "default":0x80,
        },
        {
                "name": "FT_POR_B",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,1,0x01],
                "default":0x00,
        },
        {
                "name": "RESET",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,1,0x02],
                "default":0x70,
        },
        {
                "name": "ONOFF",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,1,0x04],
                "default":0x60,
        },
        {
                "name": "REMOTE_EN",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,1,0x08],
                "default":0x51,
        },
        {
                "name": "MODE_DIR",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,1,0x10],
                "default":0x41,
        },
        {
                "name": "FT_SD_PWREN",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,1,0x20],
                "default":0x41,
        },
        {
                "name": "FT_SD_CD",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,1,0x40],
                "default":0x11,
        },
        {
                "name": "FT_FTA_SEL",
                "ftdi": [1, 0xF0, 0xF0],
                "pca6416": [0x22,1,0x80],
                "default":0x31,
        },
]

mapping_gpio = [
        {"name": "FT_IO_NRST1", "ftdi": [1, 0x08], "default": 0x00},
           {"name": "FT_IO_NINT1", "ftdi": [1, 0x10], "default": 0x00},
            {"name": "FT_IO_NINT", "ftdi": [1, 0x20], "default": 0x00},
            {"name": "FT_IO_NRST", "ftdi": [1, 0x40], "default": 0x00},
]

boot_modes = {
        "a_usb": 0x01,
        "a_emmc": 0x02,
        "a_sd": 0x03,
        "a_nor": 0x04,
        "a_nand_2k": 0x05,
        "a_nand_4k": 0x06,
        "usb": 0x09,
        "emmc": 0x0a,
        "sd": 0x0b,
        "nor": 0x0c,
        "nand_2k": 0x0d,
        "nand_4k": 0x0e,
}

temperature_sensor = {"ftdi": [1, 0xF0, 0x00], "sensor": [0x48]}
