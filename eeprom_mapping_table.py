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

INFOS = [
    {
        "name": "CONFIG_FLAG",
        "datas": {
            "0x0": "Empty EEPROM",
            "0x1": "Programmed EEPROM",
            "0x2": "Programmed EEPROM",
            "0x3": "Empty EEPROM",
        },
    },
    {
        "name": "BOARD_ID",
        "datas": {
            "0x1": "NXP i.MX8DXL EVK Board",
            "0x2": "NXP i.MX8DXL EVK DDR3 Board",
            "0x3": "NXP i.MX8MP EVK Board",
            "0x4": "NXP i.MX8MP EVK PWR Board",
            "0x5": "NXP i.MX8MP DDR3L Board",
            "0x6": "NXP i.MX8MP DDR4 Board",
            "0x7": "NXP i.MX8ULP EVK Board",
            "0x8": "NXP VAL_BOARD_1 Board",
            "0x9": "NXP VAL_BOARD_2 Board",
            "0xa": "NXP i.MX8ULP EVK9 Board",
        },
    },
    {
        "name": "SOC_ID",
        "datas": {
            "0x1": "i.MX8DXL",
            "0x2": "i.MX8MP",
            "0x3": "i.MX8ULP",
            "0x4": "VAL_BOARD_1",
            "0x5": "VAL_BOARD_2",
        },
    },
    {
        "name": "PMIC_ID",
        "datas": {
            "0x1": "PP7100BVM1ES",
            "0x2": "PCA9450CHN",
            "0x3": "PPF7100BMMA2ES",
            "0x4": "PCA9460AUK",
            "0x5": "PCA9450AAHN",
            "0x6": "PCA9450BHN",
        },
    },
]
