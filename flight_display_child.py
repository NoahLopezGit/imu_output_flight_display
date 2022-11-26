from flight_display_parent import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import csv
from user_serial_data_classes import GenericSerialData, QuaternionShapeSerialData, EulerSerialData
from serial_reading_handler import SerialRead
import multiprocessing as mp
import threading
import time
from statistics import mean
import math
from collections import deque

class FlightDisplay(Ui_MainWindow):
    #UI_MainWindow has its own __init__ method or something so no init is necessary
    def user_setup(self, data_streams, running_queue, data_queue):
        #pack all graphics widgets (2d/3d plots for now) into a display map for plot updater to find
        self.data_streams = data_streams

        #setup process logistics
        self.running = False #controls data logging/plotting, setting false stops logging
        self.running_queue = running_queue #pass to serial reader/main. main tells reader to stop on exit.
        self.data_queue = data_queue

        #construct dictionary of plot handling objects. they are identified by 'plotobj'; this must be set in the object creation
        self.plotobj_dict = {key:value for (key, value) in self.__dict__.items() if 'plotobj' in key}
        for data_stream in data_streams:
            if data_stream.display is not None:
                data_stream.add_plot_handler(self.plotobj_dict[data_stream.display])
        #connect pushButton to stop_collection function
        self.pushButton.clicked.connect(self.stop_collection)

        #setup background data handler thread
        data_handler = threading.Thread(target=self.data_handler)
        data_handler.start()

        #data for framerate tracking
        self.update_time = time.time()
        self.framerates = deque([0]*5)

        #display update event timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(math.ceil((1/60)*10**3))
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()      

    def data_handler(self):
        openfile = open('data_out.csv','w',newline='')
        csvwriter = csv.writer(openfile)
        #empty the queue
        while not self.data_queue.empty(): 
            self.data_queue.get()
        #wait for start of data flow and start program
        self.data_buff = self.data_queue.get()
        self.running = True #turn sync on when data queue starts filling
        while self.running:
            if not self.data_queue.empty(): #does this continuouslty checking if the queue is empty present a performance issue?
                self.data_buff = self.data_queue.get() 
                csvwriter.writerow(self.data_buff)
        print('data handler stopped')  

    def update_plot_data(self):
        '''
        TODO this is actually pretty slow with all graphs... need to find a faster way to update
        Doesn't seem to be affected by decreasing amount of points to plot (don't think its performance bottleneck around plotting)
        this does not refresh screen each time a setData is called. Only after update function exits does it refresh screen
        it takes the program about 0.004 seconds (4 milliseconds, 250 Hz) to get through the update function. This means the refresh is limited on the GUI app side

        I have figured out the 3d plotting is severely limiting the framerate. Taking out the 3d plotting gives 60 Hz+ rates with all the 2d plots running (before it was 10 Hz)
        '''
        for i, data_stream in enumerate(self.data_streams):
            if not self.running:
                break
            if data_stream.display is not None:
                data_stream.update_plot(self.data_buff[i])
        #display framerate
        self.label_9.setText(str(self.get_framerate()))

    def get_framerate(self):
        tmp_time = time.time()
        self.framerates.append(1/(tmp_time-self.update_time))
        self.framerates.popleft() 
        self.update_time = tmp_time
        return round(mean(self.framerates), 2)
        
    def stop_collection(self): #PyQt app recognizes this and executes on closing window
        self.running = False
        self.running_queue.put(False)


if __name__=='__main__':
    #user setup
    #this must be in order of which data is transmitted
    data_queue = mp.SimpleQueue()
    running_queue = mp.SimpleQueue()
    data_streams = [
        GenericSerialData('Duration', None, dtype_format_specifier='L'), #struct unpack unsigned long format is 'L'
        GenericSerialData('Time Period', None, dtype_format_specifier='L'),
        # GenericSerialData('Accel X', None),
        # GenericSerialData('Accel Y', None),
        # GenericSerialData('Accel Z', None),
        # GenericSerialData('Gyro X', None),
        # GenericSerialData('Gyro Y', None),
        # GenericSerialData('Gyro Z', None),
        EulerSerialData('Euler Data',None),
        QuaternionShapeSerialData('Quat Data',None),
        GenericSerialData('Accel X', 'plotobj_strip_chart_1'),
        GenericSerialData('Accel Y', 'plotobj_strip_chart_2'),
        GenericSerialData('Accel Z', 'plotobj_strip_chart_3'),
        GenericSerialData('Gyro X', 'plotobj_strip_chart_4'),
        GenericSerialData('Gyro Y', 'plotobj_strip_chart_5'),
        GenericSerialData('Gyro Z', 'plotobj_strip_chart_6')
        # EulerSerialData('Euler Data','plotobj_Euler_Plot'),
        # QuaternionShapeSerialData('Quat Data','plotobj_Quat_Plot')
    ]

    #start serial reading process
    port = 'COM3'
    baudrate = 115200
    timeout = 5
    SerialRead(port, baudrate, timeout, data_streams, data_queue, running_queue)

    #run core app
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = FlightDisplay()
    ui.setupUi(MainWindow)
    ui.user_setup(data_streams, running_queue, data_queue)
    MainWindow.show()
    sys.exit(app.exec_())
