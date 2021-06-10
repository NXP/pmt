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

import datetime
import threading
import copy
import socket
import numpy as np

import drv_ftdi

HOST = '0.0.0.0'
STOP_THREAD = False


def client_thread(board, conn, addr):
    global STOP_THREAD
    last_sec_len_buf = 0
    rail_buf = []
    for i, rail in enumerate(board.board_mapping_power):
        rail_buf.append({'railnumber': rail['name'], 'current': np.array([[0, 0]], dtype=np.float16),
                              'voltage': np.array([[0, 0]], dtype=np.float16)})
    while not STOP_THREAD:
        try:
            d = conn.recv(1024)
            if not d:
                break
        except socket.error as err:
            print("error while receiving:: " + str(err))
            break
        remote_buf = []
        drv_ftdi.DATA_LOCK.acquire()
        for remote_rail in board.data_buf:
            remote_buf.append(copy.deepcopy(remote_rail))
            remote_rail['current'] = [[0, 0]]
            remote_rail['voltage'] = [[0, 0]]
        drv_ftdi.DATA_LOCK.release()

        for rail in remote_buf:
            local_rail = next((item for item in rail_buf if item['railnumber'] == rail['railnumber']), None)
            rail['voltage'].pop(0)
            rail['current'].pop(0)
            local_rail['voltage'] = np.append(local_rail['voltage'], np.array(rail['voltage'], dtype=np.float16),
                                              axis=0)
            local_rail['current'] = np.append(local_rail['current'], np.array(rail['current'], dtype=np.float16),
                                              axis=0)
        data = datetime.datetime.now().isoformat() + ";"
        curr_len_buf = len(rail_buf[-1]['voltage'])
        rail_buf_len = curr_len_buf - last_sec_len_buf
        for d_rail in rail_buf:
            tmp_v = d_rail['voltage'][-rail_buf_len:, 1].mean()
            tmp_c = d_rail['current'][-rail_buf_len:, 1].mean()
            tmp_p = tmp_v * tmp_c
            tmp = d_rail['railnumber'] + ':' + str(tmp_p)
            data = data + tmp + ";"
        try:
            conn.sendall(bytes(data, encoding='utf8'))
            last_sec_len_buf = curr_len_buf
        except socket.error as e:
            print("error while sending:: " + str(e))
    print('Closing connection from {:s}:{:d}'.format(addr[0], addr[1]))
    conn.close()


def run_server(board, port):
    global STOP_THREAD
    thread_process = threading.Thread(target=board.get_data)
    thread_process.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen(10)
        while True:
            try:
                try:
                    conn, addr = s.accept()
                    print('Accepting connection from {:s}:{:d}'.format(addr[0], addr[1]))
                    try:
                        threading.Thread(target=client_thread, args=(board, conn, addr)).start()
                    except:
                        import traceback
                        traceback.print_exc()
                except socket.error as err:
                    print("error while accepting connections:: " + str(err))
            except KeyboardInterrupt:
                STOP_THREAD = True
                drv_ftdi.FLAG_UI_STOP = True
                s.close()
                break
