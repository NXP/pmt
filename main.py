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

import argparse
import logging

import drv_ftdi
from board_configuration import common
import gui
import tui


PROGRAM_VERSION = 'PMT 1.1'

LOG_LEVEL = logging.WARNING


def list_supported_board():
    """prints supported boards"""
    print('Board(s) currently supported :')
    for board_name in common.supported_boards:
        print('- ' + board_name)


def found_bootm(bootm_name, board):
    """returns 1 if boot name exist is the boot mode structure of the board"""
    if bootm_name in board.boot_modes:
        return 1
    else:
        return 0


def found_gpio(gpio_name, board):
    """returns the gpio if the gpio name exist in the gpio structure of the board"""
    for gpio in board.board_mapping_gpio:
        if gpio_name == gpio['name']:
            return gpio
        else:
            pass
    for gpio in board.board_mapping_gpio_i2c:
        if gpio_name == gpio['name']:
            return gpio
        else:
            pass
    return 0


def found_value(gpio_value):
    """checks if the gpio value entered in command line is supported and return the corresponding value"""
    if gpio_value in common.gpio_supported_values:
        if common.gpio_supported_values[gpio_value] == 0 or common.gpio_supported_values[gpio_value] == 1:
            return common.gpio_supported_values[gpio_value] * 0xFF
        else:
            return common.gpio_supported_values[gpio_value]
    else:
        return 0


def main():
    """checks arguments passed in command line and starts the program"""
    logging.basicConfig(level=LOG_LEVEL)

    parser = argparse.ArgumentParser(description='PMT tool for power monitoring')
    subparser = parser.add_subparsers(dest='command')

    parser_lsftdi = subparser.add_parser('lsftdi', help='list available ftdi chip(s) for board location and id information')
    parser_lsboard = subparser.add_parser('lsboard', help='list supported board(s)')

    parser_lsgpio = subparser.add_parser('lsgpio', help='list gpio available for a specific board')
    parser_lsgpio.add_argument('-b', '--board', required=False, help='specify supported board name', metavar='board')
    parser_lsgpio.add_argument('-i', '--id', required=False, type=int, default=-1, help='specify id of the board', metavar='id')

    parser_lsbootmode = subparser.add_parser('lsbootmode', help='list boot modes available for a specific board')
    parser_lsbootmode.add_argument('-b', '--board', required=False, help='specify supported board name', metavar='board')
    parser_lsbootmode.add_argument('-i', '--id', required=False, type=int, default=-1, help='specify id of the board', metavar='id')

    parser_reset = subparser.add_parser('reset', help='reset the specified board')
    parser_reset.add_argument('-b', '--board', required=False, help='specify supported board name', metavar='board')
    parser_reset.add_argument('-bootm', '--boot_mode', required=False, help='specify boot mode', metavar='boot mode')
    parser_reset.add_argument('-d', '--delay', required=False, type=int, default=0, help='reset the board after a delay', metavar='delay')
    parser_reset.add_argument('-i', '--id', required=False, type=int, default=-1, help='specify id of the board', metavar='id')

    parser_setgpio = subparser.add_parser('set_gpio', help='control gpio of the specified board')
    parser_setgpio.add_argument('-b', '--board', required=False, help='specify supported board name', metavar='board')
    parser_setgpio.add_argument('-g', '--gpio_name', required=True, help='GPIO to modify', metavar='gpio')
    parser_setgpio.add_argument('-v', '--value', required=True, help='desired value for GPIO', metavar='val')
    parser_setgpio.add_argument('-i', '--id', required=False, type=int, default=-1, help='specify id of the board', metavar='id')

    parser_monitor = subparser.add_parser('monitor', help='monitoring data collected in GUI or TUI')
    parser_monitor.add_argument('-b', '--board', required=False, help='specify supported board name', metavar='board')
    parser_monitor.add_argument('-m', '--mode', required=False, help='monitoring mode, gui or tui', metavar='mode')
    parser_monitor.add_argument('-l', '--load', required=False, help='load a .csv or .pmt file in GUI', metavar='file')
    parser_monitor.add_argument('-i', '--id', required=False, type=int, default=-1, help='specify id of the board', metavar='id')
    parser_monitor.add_argument('-d', '--dump', required=False, help='dump data in TUI mode', metavar='file')
    parser_monitor.add_argument('-t', '--time', required=False, help='monitor in TUI during specified time', metavar='time')

    parser_resume = subparser.add_parser('resume', help='resume / suspend the board')
    parser_resume.add_argument('-b', '--board', required=False, help='specify supported board name', metavar='board')
    parser_resume.add_argument('-i', '--id', required=False, type=int, default=-1, help='specify id of the board',
                               metavar='id')
    parser_version = parser.add_argument('-v', '--version', action='version', version=PROGRAM_VERSION, help='print the current version of the PMT')

    args = parser.parse_args()
    logging.debug(args)

    if not args.command:
        print('*************************************************************************')
        print('Please specify arguments. You can refer to help with command main.py -h.')
        print('*************************************************************************')

    if args.command == 'lsftdi':
        drv_ftdi.list_connected_devices()

    if args.command == 'lsboard':
        list_supported_board()

    if args.command == 'lsgpio':
        board = drv_ftdi.Board(args)
        board.lsgpio()

    if args.command == 'lsbootmode':
        board = drv_ftdi.Board(args)
        board.lsbootmode()

    if args.command == 'reset':
        board = drv_ftdi.Board(args)
        if not args.boot_mode or found_bootm(args.boot_mode, board):
            board.reset(args.boot_mode, args.delay)
        else:
            logging.warning('Please enter valid boot mode')

    if args.command == 'set_gpio':
        board = drv_ftdi.Board(args)
        foundgpio = found_gpio(args.gpio_name, board)
        if foundgpio:
            foundvalue = found_value(args.value)
            if foundvalue >= 0:
                board.set_gpio(foundgpio, foundvalue)
            else:
                logging.warning('Please enter valid GPIO value')
        else:
            logging.warning('Please enter valid GPIO name')

    if args.command == 'monitor':
        board = drv_ftdi.Board(args)
        if (args.mode == 'tui') or (args.mode is None):
            tui.run_ui(board, args)
        elif args.mode == 'gui':
            gui.run_ui(board, args)
        else:
            logging.warning('Please enter valid monitor mode')

    if args.command == 'resume':
        print('Not implemented yet.')



if __name__ == '__main__':
    main()
