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

import logging
import platform
import time

import ftdi_def as ft_def

if platform.system() == 'Linux':
    import pylibftdi

    OS = 'Linux'
elif platform.system() == 'Windows':
    import ftd2xx as ftdi

    OS = 'Windows'


def ftdi_i2c_init(ftdi_device, pins):
    """low-level I2C initialization"""
    logging.debug('ftdi_i2c_init')
    val_bitmask = pins['ftdi'][2]
    dir_bitmask = pins['ftdi'][1]
    buf = []
    buf.append(
        ft_def.MPSSE_CMD_DISABLE_CLOCK_DIVIDE_BY_5)  # Ensure disable clock divide by 5 for 60Mhz master clock
    buf.append(ft_def.MPSSE_CMD_DISABLE_ADAPTIVE_CLOCKING)  # Ensure turn off adaptive clocking
    buf.append(
        ft_def.MPSSE_CMD_ENABLE_3PHASE_CLOCKING)  # PAC 1934 need it. Enable 3 phase data clock, used by I2C to allow data on one clock edge
    buf_to_send = bytes(buf)
    ftdic_write(ftdi_device, buf_to_send)
    buf.clear()
    buf.append(
        ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)  # Command to set directions of lower 8 pins and force value on bits set as output
    buf.append(ft_def.VALUE_SCLHIGH_SDAHIGH | val_bitmask)
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_SET_CLOCK_DIVISOR)  # Command to set clock divisor
    buf.append(
        ft_def.CLOCK_DIVISOR_400K & 0xFF)  # problem with byte(), result M instead of 4D - Set 0xValueL of clock divisor
    buf.append((ft_def.CLOCK_DIVISOR_400K >> 8) & 0xFF)  # Set 0xValueH of clock divisor
    buf_to_send = bytes(buf)
    ftdic_write(ftdi_device, buf_to_send)
    buf.clear()
    buf.append(ft_def.MPSEE_CMD_DISABLE_LOOPBACK)  # Command to turn off loop back of TDI/TDO connection
    buf_to_send = bytes(buf)
    ftdic_write(ftdi_device, buf_to_send)


def ftdi_i2c_stop(ftdi_device, pins):
    """low-level I2C stop"""
    logging.debug('ftdi_i2c_stop')
    val_bitmask = pins['ftdi'][2]
    dir_bitmask = pins['ftdi'][1]
    buf = []
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)  # SCL low, SDA low
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLHIGH_SDALOW | val_bitmask)  # SCL high, SDA low
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLHIGH_SDAHIGH | val_bitmask)  # SCL high, SDA high
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf_to_send = bytes(buf)
    ftdic_write(ftdi_device, buf_to_send)


def ftdi_i2c_read(ftdi_device, pins, is_nack):
    """low-level I2C read"""
    logging.debug('ftdi_i2c_read')
    val_bitmask = pins['ftdi'][2]
    dir_bitmask = pins['ftdi'][1]
    buf = []
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
    buf.append(ft_def.DIRECTION_SCLOUT_SDAIN | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_DATA_IN_BITS_POS_EDGE)
    buf.append(ft_def.DATA_SIZE_8BITS)
    buf.append(ft_def.MPSSE_CMD_SEND_IMMEDIATE)
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE)
    buf.append(0x00)
    if is_nack:
        buf.append(0x80)
    else:
        buf.append(0x00)
    buf_to_send = bytes(buf)
    ftdic_write(ftdi_device, buf_to_send)
    time.sleep(0.0001)
    receive = ftdi_device.read(1)
    return receive


def ftdi_i2c_write(ftdi_device, pins, data):
    """low-level I2C write"""
    logging.debug('ftdi_i2c_write')
    val_bitmask = pins['ftdi'][2]
    dir_bitmask = pins['ftdi'][1]
    buf = []
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE)
    buf.append(ft_def.DATA_SIZE_8BITS)
    buf.append(data)
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
    buf.append(ft_def.DIRECTION_SCLOUT_SDAIN | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_DATA_IN_BITS_POS_EDGE)
    buf.append(ft_def.DATA_SIZE_1BIT)
    buf.append(ft_def.MPSSE_CMD_SEND_IMMEDIATE)
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf_to_send = bytes(buf)
    ftdic_write(ftdi_device, buf_to_send)
    time.sleep(0.0005)
    in_buff = ftdi_device.read(1)
    if (in_buff[0] & 0x01) != 0:
        logging.warning("Can't get ack after write!")
        return -1
    return 0


def ftdi_i2c_start(ftdi_device, pins):
    """low-level I2C start"""
    logging.debug('ftdi_i2c_start')
    val_bitmask = pins['ftdi'][2]
    dir_bitmask = pins['ftdi'][1]
    buf = []
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLHIGH_SDAHIGH | val_bitmask)  # SCL high, SDA high
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLHIGH_SDALOW | val_bitmask)  # SCL high, SDA low
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf.append(ft_def.MPSSE_CMD_SET_DATA_BITS_LOWBYTE)
    buf.append(ft_def.VALUE_SCLLOW_SDALOW | val_bitmask)  # SCL low, SDA low
    buf.append(ft_def.DIRECTION_SCLOUT_SDAOUT | dir_bitmask)
    buf_to_send = bytes(buf)
    ftdic_write(ftdi_device, buf_to_send)


def ftdic_write(ftdi_device, buf):
    """FTDI write function depending of the current OS"""
    if OS == 'Linux':
        ftdi_device.write(bytes(buf))
    elif OS == 'Windows':
        ftdi_device.write(buf)


def ftdic_write_gpio(ftdi_device, buf):
    """FTDI write gpio function depending of the current OS"""
    if OS == 'Linux':
        ftdi_device.write(bytes([buf]))
    elif OS == 'Windows':
        ftdi_device.write(bytes([buf]))


def ftdic_read_gpio(ftdi_device):
    """FTDI read depending function of the current OS"""
    if OS == 'Linux':
        return ftdi_device.read(1)[0]
    elif OS == 'Windows':
        return ftdi_device.getBitMode()


def ftdi_open(board_id, channel, desc=None):
    """opens FTDI device function depending of the current OS"""
    if OS == 'Linux':
        return pylibftdi.Device(device_index=board_id, interface_select=channel + 1)
    elif OS == 'Windows':
        add = desc.get('location')
        dev_list = ftdi.listDevices()
        dev_channel = None
        for i, d in enumerate(dev_list):
            if d != b'':
                if chr(d[-1]) == chr(ord('A') + channel):
                    tmp_dev = ftdi.getDeviceInfoDetail(i)
                    if tmp_dev.get('location') == add + channel:
                        dev_channel = tmp_dev.get('index')
            else:
                pass
        return ftdi.open(dev_channel)


def ftdic_setbitmode(ftdi_device, out_pins, value):
    """"FTDI set bitmode function depending of the current OS"""
    if OS == 'Linux':
        ftdi_device.ftdi_fn.ftdi_set_bitmode(out_pins, value)
    elif OS == 'Windows':
        ftdi_device.setBitMode(out_pins, value)
