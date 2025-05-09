

from machine import Pin, PWM, I2C  # type: ignore
from BMI270 import BMI270
from register_definitions import *
from config_file import bmi270_config_file
from math import cos, sin, tan, degrees, radians
from filter import Fusion



class IMU(None):
    def __init__(self, sclpin=1, sdapin=0, sample_rate=100) -> None:

        self.serial_device : I2C = I2C(0, scl=Pin(sclpin), sda=Pin(sdapin))
        self.BMI270 = BMI270(serial_device = self.serial_device)

        self.sample_rate = sample_rate
        self.address = I2C_PRIM_ADDR
        self.acc_data = (0, 0, 0)
        self.gyro_data = (0, 0, 0)
        self.yaw = 0
        self.angle = 0.0
        self.matrix_z = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


        self.filter = Fusion()
        
        return None


    def UpdateAccelerometer(self) -> None:
        self.acc_data = self.BMI270.FormatAccelerometerData()
        self.gyro_data = self.BMI270.FormatGyroscopeData()
        self.filter.update(self.acc_data, self.gyro_data, dt=0.01)

        return None



    def UpdatePsi(self, dt : float = 0.01) -> None:
        omega_psi : float = self.BMI270.FormatGyroscopeData()[2] * dt
        self.angle += omega_psi
        
        return None



    def UpdateMatrix(self, dt : float = 0.01) -> None:
        self.UpdatePsi(dt=dt)

        cos_psi : float = cos(radians(self.angle))
        sin_psi : float = sin(radians(self.angle))

        r_one : tuple = (cos_psi, (-1 * sin_psi), 0)
        r_two : tuple = (sin_psi, cos_psi, 0)
        r_three : tuple = (0, 0, 1)
        
        R = (r_one, r_two, r_three)
        self.matrix_z = R

        return None

    
    

