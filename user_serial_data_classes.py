import struct
import numpy as np
from math import sin, cos, acos, sqrt
from collections import deque
import pyqtgraph as pg
from pyqtgraph.opengl import GLLinePlotItem, GLAxisItem


class QuaternionSerialData:
    def __init__(self, name, display, dtype_format_specifier='f', dsize=4):
        self.name = name
        self.display = display
        self.dtype_format_specifier = dtype_format_specifier
        self.dsize = dsize

        self.center = np.array([0,0,0])
        self.vector = np.array([0,0,1])

    def add_plot_handler(self, plot_figure):
        self.plothanlder = GLLinePlotItem(pos=[[0,0,0],[1,0,0]], width=2, antialias=False)
        plot_figure.addItem(self.plothanlder)
        plot_figure.addItem(GLAxisItem())
        plot_figure.setCameraParams(azimuth=22.5,distance=3)

    def get_data(self, serial_connection):
        quat_data = []
        for _ in range(4):
            data, = struct.unpack(self.dtype_format_specifier, serial_connection.read(size=self.dsize))
            quat_data.append(data)
        return quat_data 
    
    def update_plot(self, quaternion_vector):
        new_vector = Quaternion.from_value(quaternion_vector) * self.vector
        self.plothanlder.setData(pos=[self.center,new_vector])

class QuaternionShapeSerialData:
    def __init__(self, name, display, dtype_format_specifier='f', dsize=4):
        self.name = name
        self.display = display
        self.dtype_format_specifier = dtype_format_specifier
        self.dsize = dsize

        #define rectangular prism with point at top
        self.vectors = [
            [np.array([0,0,-1]),np.array([0.05,0.05,-1])],
            [np.array([0,0,-1]),np.array([-0.05,0.05,-1])],
            [np.array([0,0,-1]),np.array([-0.05,-0.05,-1])],
            [np.array([0,0,-1]),np.array([0.05,-0.05,-1])],
            [np.array([0.05,0.05,-1]),np.array([0.05,0.05,1.0])],
            [np.array([-0.05,0.05,-1]),np.array([-0.05,0.05,1.0])],
            [np.array([-0.05,-0.05,-1]),np.array([-0.05,-0.05,1.0])],
            [np.array([0.05,-0.05,-1]),np.array([0.05,-0.05,1.0])],
            [np.array([0.05,0.05,1.0]),np.array([0,0,1.25])],
            [np.array([-0.05,0.05,1.0]),np.array([0,0,1.25])],
            [np.array([-0.05,-0.05,1.0]),np.array([0,0,1.25])],
            [np.array([0.05,-0.05,1.0]),np.array([0,0,1.25])]
        ]

    def add_plot_handler(self, plot_figure):
        self.line_handlers = []
        for vector_set in self.vectors:
            self.line_handlers.append(GLLinePlotItem(pos=[vector_set[0],vector_set[1]], width=2, antialias=False))
            plot_figure.addItem(self.line_handlers[-1])
        plot_figure.addItem(GLAxisItem())
        plot_figure.setCameraParams(azimuth=22.5,distance=3)

    def get_data(self, serial_connection):
        quat_data = []
        for _ in range(4):
            data, = struct.unpack(self.dtype_format_specifier, serial_connection.read(size=self.dsize))
            quat_data.append(data)
        return quat_data 
    
    def update_plot(self, quaternion_vector):
        #new_vector = Quaternion.from_value(quaternion_vector) * self.vector
        quaternion = Quaternion.from_value(quaternion_vector)
        for i, vector_set in enumerate(self.vectors):
            vec_1_transform = quaternion * vector_set[0]
            vec_2_transform = quaternion * vector_set[1]
            self.line_handlers[i].setData(pos=[vec_1_transform,vec_2_transform])
        #self.plothanlder.setData(pos=[self.center,new_vector])

class GenericSerialData:
    def __init__(self, name, display, dtype_format_specifier='f', dsize=4):
        self.name = name
        self.display = display
        self.dtype_format_specifier = dtype_format_specifier
        self.dsize = dsize

        self.x_data_array = list(range(1000))
        self.y_data_array = deque([0]*1000)

    def add_plot_handler(self, current_plot):
        current_plot.setYRange(-10,20, padding=0.05)
        self.plot_handler = current_plot.plot(self.x_data_array, self.y_data_array, pen = pg.mkPen(color=(255, 0, 0)))

    def get_data(self, serial_connection):
        data, = struct.unpack(self.dtype_format_specifier, serial_connection.read(size=self.dsize))
        return data

    def update_plot(self, data):
            self.y_data_array.append(data) #this will update data in order.. need to define this more explicitly
            self.y_data_array.popleft()
            self.plot_handler.setData(self.x_data_array,self.y_data_array)

class EulerSerialData:
    def __init__(self, name, display, dtype_format_specifier='f', dsize=4):
        self.name = name
        self.display = display
        self.dtype_format_specifier = dtype_format_specifier
        self.dsize = dsize

        self.center = np.array([0,0,0])
        self.vector = np.array([0,0,1])

    def get_data(self, serial_connection):
        euler_data = []
        for _ in range(3):
            data, = struct.unpack(self.dtype_format_specifier, serial_connection.read(size=self.dsize))
            euler_data.append(data)
        return euler_data
    
    def update_plot(self, euler_angles):
        new_vector = np.array([0,0,1]) #TODO replace with code to calucate new vector based on euler angles
        self.plothanlder.setData(pos=[self.center,new_vector])
    
    def add_plot_handler(self, plot_figure):
        self.plothanlder = GLLinePlotItem(pos=[[0,0,0],[1,0,0]], width=2, antialias=False)
        plot_figure.addItem(self.plothanlder)
        plot_figure.addItem(GLAxisItem())
        plot_figure.setCameraParams(azimuth=22.5,distance=3)


#functions for quaternion plotting
def normalize(v, tolerance=0.00001):
    mag2 = sum(n * n for n in v)
    if abs(mag2 - 1.0) > tolerance:
        mag = sqrt(mag2)
        v = tuple(n / mag for n in v)
    return np.array(v)

class Quaternion:

    def from_axisangle(theta, v):
        theta = theta
        v = normalize(v)

        new_quaternion = Quaternion()
        new_quaternion._axisangle_to_q(theta, v)
        return new_quaternion

    def from_value(value):
        new_quaternion = Quaternion()
        new_quaternion._val = value
        return new_quaternion

    def _axisangle_to_q(self, theta, v):
        x = v[0]
        y = v[1]
        z = v[2]

        w = cos(theta/2.)
        x = x * sin(theta/2.)
        y = y * sin(theta/2.)
        z = z * sin(theta/2.)

        self._val = np.array([w, x, y, z])

    def __mul__(self, b):

        if isinstance(b, Quaternion):
            return self._multiply_with_quaternion(b)
        elif isinstance(b, (list, tuple, np.ndarray)):
            if len(b) != 3:
                raise Exception(f"Input vector has invalid length {len(b)}")
            return self._multiply_with_vector(b)
        else:
            raise Exception(f"Multiplication with unknown type {type(b)}")

    def _multiply_with_quaternion(self, q2):
        w1, x1, y1, z1 = self._val
        w2, x2, y2, z2 = q2._val
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
        z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2

        result = Quaternion.from_value(np.array((w, x, y, z)))
        return result

    def _multiply_with_vector(self, v):
        q2 = Quaternion.from_value(np.append((0.0), v))
        return (self * q2 * self.get_conjugate())._val[1:]

    def get_conjugate(self):
        w, x, y, z = self._val
        result = Quaternion.from_value(np.array((w, -x, -y, -z)))
        return result

    def __repr__(self):
        theta, v = self.get_axisangle()
        return f"((%.6f; %.6f, %.6f, %.6f))"%(theta, v[0], v[1], v[2])

    def get_axisangle(self):
        w, v = self._val[0], self._val[1:]
        theta = acos(w) * 2.0

        return theta, normalize(v)

    def tolist(self):
        return self._val.tolist()

    def vector_norm(self):
        w, v = self.get_axisangle()
        return np.linalg.norm(v)