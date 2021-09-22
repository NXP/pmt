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

"""defines supported gpio value, supported boards and eeprom path of the supported boards"""
gpio_supported_values = {
    '0': 0,
    'low': 0,
    '1': 1,
    'high': 1,
    'toggle': 2,
    '2': 2
}

supported_boards = ["imx8dxlevk",
                    "imx8mpevkpwra0",
                    "imx8mpevkpwra1",
                    "imx8ulpevk",
                    "imx8ulpevk9",
                    "val_board_1",
                    "val_board_2"
                    ]

"""defines i2c eeprom of the different supported boards. Don't specify serial eeprom"""
board_eeprom_i2c = [{'board_name': 'imx8dxlevk', 'ftdi': [1, 0x60, 0x40], 'at24cxx': {'addr': 0x57, 'type': 0}},
                {'board_name': 'imx8mpevkpwra0', 'ftdi': [1, 0xF0, 0x00], 'at24cxx': {'addr': 0x50, 'type': 1}},
                {'board_name': 'imx8mpevkpwra1', 'ftdi': [1, 0xF0, 0x00], 'at24cxx': {'addr': 0x50, 'type': 1}}
               ]
