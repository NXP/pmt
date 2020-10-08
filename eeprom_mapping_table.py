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

INFOS = [
    {'name': 'CONFIG_FLAG', 'datas': {
        '0x0': 'Empty EEPROM',
        '0x1': 'Programmed EEPROM',
        '0x2': 'Programmed EEPROM',
        '0x3': 'Empty EEPROM'}
    },
    {'name': 'BOARD_ID', 'datas': {
        '0x1': 'NXP i.MX8DXL EVK Board',
        '0x2': 'NXP i.MX8DXL EVK DDR3 Board',
        '0x3': 'NXP i.MX8MP EVK Board',
        '0x4': 'NXP i.MX8MP EVK PWR Board',
        '0x5': 'NXP i.MX8MP DDR3L Board',
        '0x6': 'NXP i.MX8MP DDR4L Board'}
    },
    {'name': 'BOARD_REV', 'datas': {
        '0x11': 'A0',
        '0x12': 'A1',
        '0x13': 'A2',
        '0x14': 'A3',
        '0x15': 'A4',
        '0x21': 'B0',
        '0x22': 'B1',
        '0x23': 'B2',
        '0x24': 'B3',
        '0x25': 'B4',
        '0x31': 'C0',
        '0x32': 'C1',
        '0x33': 'C2',
        '0x34': 'C3',
        '0x35': 'C4'}
    },
    {'name': 'SOC_ID', 'datas': {
        '0x1': 'imx8dxlevk',
        '0x2': 'imx8mppwrevk'}
    },
    {'name': 'SOC_REV', 'datas': {
        '0x11': 'A0',
        '0x12': 'A1',
        '0x13': 'A2',
        '0x14': 'A3',
        '0x15': 'A4',
        '0x21': 'B0',
        '0x22': 'B1',
        '0x23': 'B2',
        '0x24': 'B3',
        '0x25': 'B4',
        '0x31': 'C0',
        '0x32': 'C1',
        '0x33': 'C2',
        '0x34': 'C3',
        '0x35': 'C4'}
    },
    {'name': 'PMIC_ID', 'datas': {
        '0x1': 'PP7100BVM1ES',
        '0x2': 'PCA9450CHN'}
    },
    {'name': 'PMIC_REV', 'datas': {
        '0x11': 'A0',
        '0x12': 'A1',
        '0x13': 'A2',
        '0x14': 'A3',
        '0x15': 'A4',
        '0x21': 'B0',
        '0x22': 'B1',
        '0x23': 'B2',
        '0x24': 'B3',
        '0x25': 'B4',
        '0x31': 'C0',
        '0x32': 'C1',
        '0x33': 'C2',
        '0x34': 'C3',
        '0x35': 'C4'}
    },
    {'name': 'NBR_PWR_RAILS', 'datas': {
        '0x1': '0',
        '0x2': '1',
        '0x3': '2',
        '0x4': '3',
        '0x5': '4',
        '0x6': '5',
        '0x7': '6',
        '0x8': '7',
        '0x9': '8',
        '0xa': '9',
        '0xb': '10',
        '0xc': '11',
        '0xd': '12',
        '0xe': '13',
        '0xf': '14',
        '0x10': '15',
        '0x11': '16',
        '0x12': '17',
        '0x13': '18',
        '0x14': '19',
        '0x15': '20',
        '0x16': '21',
        '0x17': '22',
        '0x18': '23',
        '0x19': '24',
        '0x1a': '25',
        '0x1b': '26',
        '0x1c': '27',
        '0x1d': '28',
        '0x1e': '29',
        '0x1f': '30'}
    },
    {'name': 'BOARD_SN', 'datas': {
        '0x1': '0',
        '0x2': '1',
        '0x3': '2',
        '0x4': '3',
        '0x5': '4',
        '0x6': '5',
        '0x7': '6',
        '0x8': '7',
        '0x9': '8',
        '0xa': '9',
        '0xb': '10',
        '0xc': '11',
        '0xd': '12',
        '0xe': '13',
        '0xf': '14',
        '0x10': '15',
        '0x11': '16',
        '0x12': '17',
        '0x13': '18',
        '0x14': '19',
        '0x15': '20',
        '0x16': '21',
        '0x17': '22',
        '0x18': '23',
        '0x19': '24',
        '0x1a': '25',
        '0x1b': '26',
        '0x1c': '27',
        '0x1d': '28',
        '0x1e': '29',
        '0x1f': '30'}
    }
]
