import machine
import time
import math

class MPU6050():
    rps = 100

    acc_x = 0
    acc_y = 0
    acc_z = 0

    gyro_x = 0
    gyro_y = 0
    gyro_z = 0
    
    gx = 0.0
    gy = 0.0
    gz = 0.0
    
    g_sens = 65.5
    
    gyro_x_offset = 0.0
    gyro_y_offset = 0.0
    gyro_z_offset = 0.0

    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr

        self.iic.start()
        self.iic.writeto(self.addr, bytearray([0x6B, 0]))
        self.iic.stop()
        
    def calibrate(self, cycles = 2000):
        for i in range(cycles):
            self.read()

            self.gyro_x_offset += self.gyro_x
            self.gyro_y_offset += self.gyro_y
            self.gyro_z_offset += self.gyro_z

            time.sleep_ms(1)
    
        self.gyro_x_offset /= cycles
        self.gyro_y_offset /= cycles
        self.gyro_z_offset /= cycles

    def read(self):
        self.iic.start()
        self.iic.writeto(self.addr, bytearray([0x3B]))
        self.iic.stop()
        
        self.iic.start()
        res = self.iic.readfrom(self.addr, 14)
        self.iic.stop()
        
        self.acc_x = self.bytes_toint(res[0], res[1])
        self.acc_y = self.bytes_toint(res[2], res[3])
        self.acc_z = self.bytes_toint(res[4], res[5])
        
        #temp = self.bytes_toint(res[6], res[7])
        
        self.gyro_x = self.bytes_toint(res[8], res[9]) / self.g_sens
        self.gyro_y = self.bytes_toint(res[10], res[11]) / self.g_sens
        self.gyro_z = self.bytes_toint(res[12], res[13]) / self.g_sens
    
    def read_calibrated(self):
        self.read()
        
        self.gyro_x -= self.gyro_x_offset
        self.gyro_y -= self.gyro_y_offset
        self.gyro_z -= self.gyro_z_offset
        
    def read_computed(self):
        """
        ```py
        started_at = time.ticks_ms()
        mpu.read_computed()
        # do_some_stuff
        time.sleep_ms(int((1 / mpu.rps * 1000) - (time.ticks_ms() - started_at)))
        ```
        """

        self.read_calibrated()
        
        # angles based on accelerometer
        self.ay = math.atan2(self.acc_x, math.sqrt(self.acc_y*self.acc_y + self.acc_z*self.acc_z)) * 180 / 3.1415926
        self.ax = math.atan2(self.acc_y, math.sqrt(self.acc_x*self.acc_x + self.acc_z*self.acc_z)) * 180 / 3.1415926

        # angles based on gyro (deg/s)
        self.gx += self.gyro_x / self.rps
        self.gy -= self.gyro_y / self.rps
        self.gz += self.gyro_z / self.rps

        # complementary filter
        # tau = DT*(A)/(1-A)
        # = 0.48sec
        self.gx = self.gx * 0.96 + self.ax * 0.04
        self.gy = self.gy * 0.96 + self.ay * 0.04

    def bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)




