# Code taken from https://github.com/PeiSeng/named-pipe-communication

# TODO: Security Attributes of Pipe

import win32pipe
import win32file
import pywintypes
import multiprocessing
import time

def client(num_tries: int, wait: int = 1):
    print("[CLIENT] Client")
    
    for _try in range(num_tries):

        print("[CLIENT] Service {} is started.".format(_try + 1))

        while True:
            try:
                handle = win32file.CreateFile(r'\\.\pipe\UserInput', win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, None)

                error = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)

                print("[CLIENT] SetNamedPipeHandleStatus Return Code: {}".format(error))
                
                while True:
                    data_pointer = win32file.ReadFile(handle, 65536)
                    
                    print(f"[CLIENT] Data Received: {data_pointer}")

                    if data_pointer != b'0' or data_pointer != b'':
                        return data_pointer
            
            except pywintypes.error as e:
                if e.args[0] == 2:
                    print("[CLIENT] ERROR_FILE_NOT_FOUND")
                elif e.args[0] == 109:
                    print("[CLIENT] ERROR_BROKEN_PIPE")
                
                break
        
        print("[CLIENT] Service {} ended.".format(_try + 1))

        time.sleep(wait)

def server(num_clients: int, data: int):
    print("[SERVER] Server")
    
    for _client in range(num_clients):
        print("[SERVER] Service {} is started.".format(_client + 1))
        
        pipe = win32pipe.CreateNamedPipe(r'\\.\pipe\UserInput', win32pipe.PIPE_ACCESS_DUPLEX, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT, 1, 65536, 65536, 0, None)

        print("[SERVER] Named Pipe is created. Waiting for Client to connect.")

        win32pipe.ConnectNamedPipe(pipe, None)

        print("[SERVER] Client is connected.")

        data = str.encode(str(data), encoding='ascii')

        error, num_bytes = win32file.WriteFile(pipe, data)

        print("[SERVER] Data: {}, Error: {}, Bytes Written: {}".format(data, error, num_bytes))
        
        win32file.FlushFileBuffers(pipe)

        win32pipe.DisconnectNamedPipe(pipe)

        win32file.CloseHandle(pipe)
        
        print("[SERVER] Service {} ended.".format(_client + 1))


if __name__ == '__main__':
    p1 = multiprocessing.Process(target=server, args=(1, 100))
    p2 = multiprocessing.Process(target=client, args=(3,))

    p2.start()
    p1.start()

    p2.join()
    p1.join()



