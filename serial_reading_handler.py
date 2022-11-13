import threading
import serial
import multiprocessing as mp
import time


class SerialRead:
    def __init__(self, port, baudrate, timeout, data_streams, data_queue, process_queue):
        self.running = True
        self.process_queue = process_queue

        #serial data parsing
        self.data_streams = data_streams

        #serial_reading thread
        serial_reading_process = mp.Process(target=self.serial_reading, args=(port, baudrate, timeout, data_queue))
        serial_reading_process.start()

    def serial_reading(self, port, baudrate, timeout, queue):
        #thread to check if main process has ended
        run_checker_thread = threading.Thread(target=self.run_checker, args=(self.process_queue,))
        run_checker_thread.start()

        serial_connection = serial.Serial(port=port,baudrate=baudrate, timeout=timeout)
        self.synchronize_connection(serial_connection)

        while self.running:
            if serial_connection.in_waiting:
                data_list = []
                for data_stream in self.data_streams:
                    data_list.append(data_stream.get_data(serial_connection))
                queue.put(data_list)
                if not self.synchronized(serial_connection): #check if synchronized. also clears sync bits
                    print('desync ... resynchronizing')
                    self.synchronize_connection(serial_connection)
        print('Serial reading stopped')

    def run_checker(self, process_queue):
        while True:
            if not process_queue.empty():
                self.running = process_queue.get()
                break

    def synchronize_connection(self, serial_connection):
        time.sleep(1)
        while serial_connection.in_waiting > 0:
            serial_connection.read()
        sync_false=True
        while sync_false:
            sync_byte=b'\x00'
            for i in range(4):
                if serial_connection.read() != sync_byte:
                    break
                if sync_byte == b'\x00': 
                    sync_byte=b'\xff'
                else:
                    sync_byte=b'\x00'
            if i==3:
                sync_false=False
                #print("Sync Detected")
    
    def synchronized(self, serial_connection):
        if serial_connection.read(size=4)==b'\x00\xff\x00\xff':
            return True
        else: 
            return False


if __name__=='__main__':
    # my_data_streams = [
    #     {'Name':'Stream1','Byte Length':8,'Format':'Double','Display':'main_plot_1'},
    #     {'Name':'Stream2','Byte Length':8,'Format':'Double','Display':'main_plot_2'},
    #     {'Name':'Stream3','Byte Length':8,'Format':'Double','Display':'sub_plot_1'}#,
    #     # {'Name':'Stream4','Byte Length':2,'Format':'Unsigned Short','Display':'sub_plot_2'},
    #     # {'Name':'Stream5','Byte Length':2,'Format':'Unsigned Short','Display':'sub_plot_3'}
    # ]
    # data_queue = mp.SimpleQueue()
    # running_queue = mp.SimpleQueue()
    # SerialRead('COM4',115200, 5, my_data_streams, data_queue, running_queue)
    pass
