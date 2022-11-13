# imu_output_flight_display
This repo contains the code to display a stream of serial data (commonly sent through a COM port with an arduino) on a PyQt5 GUI as a sort of flight display. This application is meant to be a high performance display which can refresh at atleast 144 Hz. Similar display approaches use matplotlib which has limited performance (20 Hz). All streamed data is logged to a csv as well. 

This app is designed to be customizable. Different flight displays can be created in QtDesigner and connected to the pyqtgraph plot handling. 

![flight display](/pictures/20221113-Flight_Display.png?raw=true "Title")
