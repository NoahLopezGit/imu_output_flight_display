#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define BNO055_SAMPLERATE_DELAY_MS (10) //this defines the samplerate of the sensor
Adafruit_BNO055 myIMU = Adafruit_BNO055(); //create IMU object 

struct{
    imu::Vector<3> acceleration; //these can be indexed like [0],[1],[2]
    imu::Vector<3> angular_acceleration;
    //imu::Vector<3> magnetic_field;
    imu::Vector<3> euler_angles;
    imu::Quaternion quaternions; //looks like this is 4 vector of doubles
}my_serial_packet;

void setup() {
    Serial.begin(115200);
    myIMU.begin(); //start IMU
    delay(1000);
    int8_t temp = myIMU.getTemp(); //apparently some data depends on temp 
    myIMU.setExtCrystalUse(true); // not sure
};

void loop() {
    //tell what sensor to work with :: send vector with 3 numbers (components) acc is variable which data goes into (you don't have to declare this variable)
    // .getVector(Sensor::Type of data you want)
    my_serial_packet.acceleration = myIMU.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    my_serial_packet.angular_acceleration = myIMU.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
    //my_serial_packet.magnetic_field = myIMU.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER);
    my_serial_packet.euler_angles = myIMU.getVector(Adafruit_BNO055::VECTOR_EULER);
    my_serial_packet.quaternions = myIMU.getQuat();


    //how to access the data in the vectors (the vector is some custom object created with imu class)
    //starting pattern
    Serial.write(byte(0));
    Serial.write(byte(255));
    Serial.write(byte(0));
    Serial.write(byte(255));
    byte* b = (byte *) &my_serial_packet;
    for (int i=0;i<sizeof(my_serial_packet);i++){
        Serial.write(*(b+i));
    };
    // transmit each double
    // byte * b = (byte *) &accel_vector;
    // for (int i=0;i<sizeof(accel_vector);i++){
    //     Serial.write(*(b+j));
    // }
    
    // gyro.x()
    // gyro.y()
    // gyro.z()
    // delay(100);
};