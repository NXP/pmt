import datetime
import threading
import copy
import socket

import drv_ftdi

HOST = '0.0.0.0'
STOP_THREAD = False


def client_thread(board, conn, addr):
    global STOP_THREAD
    last_sec_len_buf = 0
    while not STOP_THREAD:
        try:
            d = conn.recv(1024)
            if not d:
                break
        except socket.error as err:
            print("error while receiving:: " + str(err))
            break
        drv_ftdi.DATA_LOCK.acquire()
        rail_buf = copy.deepcopy(board.data_buf)
        drv_ftdi.DATA_LOCK.release()
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
