
from machine import Pin, PWM, I2C # type: ignore
from register_definitions import *
from config_file import bmi270_config_file
from time import sleep

class BMI270(None):
    def __init__(self, serial_device : I2C) -> None:

        self.serial_device : I2C = serial_device
        self.acc_range = (2 * GRAVITY)
        self.acc_odr = 100
        self.gyr_range = 1000
        self.gyr_odr = 200

        self.LoadConfiguration()
        self.SetAccelerometerRange(ACC_RANGE_2G)
        self.SetGyroscopeRange(GYR_RANGE_1000)
        self.SetAccelerometerBWP(ACC_BWP_NORMAL)
        self.SetGyroscopeBWP(GYR_BWP_NORMAL)
        self.EnableAccelerometer()
        self.EnableGyroscope()


        return None


    def LoadConfiguration(self) -> None:
        """
        This function 'loads' / 'flashes' the sensor with the configuration file if the device has not already been configured previously.
        """

        internal_status : int = self.ReadRegister(INTERNAL_STATUS)
        if(internal_status == 0x01):
            return None
        else:

            self.WriteRegister(PWR_CONF, 0x00)
            sleep(0.00045)
            self.WriteRegister(INIT_CTRL, 0x00)

            for B in range(256):
                self.WriteRegister(INIT_ADDR_0, 0x00)
                self.WriteRegister(INIT_ADDR_1, B)
                self.WriteI2CBlock(I2C_PRIM_ADDR, INIT_DATA, bmi270_config_file[(B*32):((B+1)*32)])
                sleep(0.000020)

            self.WriteRegister(INIT_CTRL, 0x01)
            sleep(0.02)


        return None


    def WriteI2CBlock(self, address : int, register : int, data : int) -> None:
        if(not isinstance(data, bytes)):
            if(not isinstance(data, list)):
                data = list(data)
            data = bytes(data)


        register_size = 8
        if(isinstance(register, list)):
            temp = 0
            register_size = 0
            for r in bytes(register):
                temp <<= 8
                temp |= r
                register_size += 8
            register = temp


        self.serial_device.writeto_mem(address, register, data, addrsize=register_size)
        return None


    def ReadRegister(self, address : int) -> int:
        """
        Reads the value from register accessed with "address" and returns the value held within said register as a little-endian integer.
        """
        return int.from_bytes(self.serial_device.readfrom_mem(I2C_PRIM_ADDR, address, 1), 'little')

    def WriteRegister(self, address : int, value : int) -> None:
        """
        Writes to register at "address" the data "value" an integer/byte value (assuming little-endian architecture).
        """
        self.serial_device.writeto_mem(I2C_PRIM_ADDR, address, bytearray(int.to_bytes(value, 1, 'little')))
        return None

    def UNSIGNED_TO_SIGNED(self, integer : int, byte_count : int) -> int:
        """
        Converts an unsigned integer of n bytes to a signed version of itself and returns the signed value
        """
        return int.from_bytes(integer.to_bytes(byte_count, 'little', signed=False), 'little', signed=True)

    def SIGNED_TO_UNSIGNED(self, integer : int, byte_count : int) -> int:
        """
        Converts a signed integer of n bytes to an unsigned version of itself and returns the signed value
        """
        return int.from_bytes(integer.to_bytes(byte_count, 'little', signed=True), 'little', signed=False)


    def SetLowPower(self) -> None:
        """
        Sets the sensor settings to consume less power than normal.
        """
        self.WriteRegister(PWR_CTRL, 0x04)
        self.WriteRegister(ACC_CONF, 0x17)
        self.WriteRegister(GYR_CONF, 0x28)
        self.WriteRegister(PWR_CONF, 0x03)
        self.acc_odr = 50
        self.gyr_odr = 100

        return None

    def SetNormalPower(self) -> None:
        """
        Sets the sensor settings to consume 'standard' amounts of power.
        """
        self.WriteRegister(PWR_CTRL, 0x0E)
        self.WriteRegister(ACC_CONF, 0xA8)
        self.WriteRegister(GYR_CONF, 0xA9)
        self.WriteRegister(PWR_CONF, 0x02)
        self.acc_odr = 100
        self.gyr_odr = 200

        return None

    def SetHighPower(self) -> None:
        """
        Sets the sensor settings to consume 'more' amounts of power.
        """
        self.WriteRegister(PWR_CTRL, 0x0E)
        self.WriteRegister(ACC_CONF, 0xA8)
        self.WriteRegister(GYR_CONF, 0xE9)
        self.WriteRegister(PWR_CONF, 0x02)
        self.acc_odr = 100
        self.gyr_odr = 200

        return None

    def SetPowerMode(self, mode : str = "performance") -> None:

        mode = mode.lower()

        if(mode == "performance"):
            self.SetHighPower()
        elif(mode == "normal"):
            self.SetNormalPower()
        elif(mode == "low_power"):
            self.SetLowPower()
        else:
            print("Invalid option!")
            return None

        return None


    def EnableAuxillary(self) -> None:
        self.WriteRegister(PWR_CTRL, (self.ReadRegister(PWR_CTRL) | BIT_0))
        return None


    def DisableAuxillary(self) -> None:
        self.WriteRegister(PWR_CTRL, (self.ReadRegister(PWR_CTRL) & ~BIT_0))
        return None


    def EnableGyroscope(self) -> None:
        self.WriteRegister(PWR_CTRL, (self.ReadRegister(PWR_CTRL) | BIT_1))
        return None


    def DisableGyroscope(self) -> None:
        self.WriteRegister(PWR_CTRL, (self.ReadRegister(PWR_CTRL) & ~BIT_1))
        return None


    def EnableAccelerometer(self) -> None:
        self.WriteRegister(PWR_CTRL, (self.ReadRegister(PWR_CTRL) | BIT_2))
        return None

    def DisableAccelerometer(self) -> None:
        self.WriteRegister(PWR_CTRL, (self.ReadRegsiter(PWR_CTRL) & ~BIT_2))
        return None

    def EnableTemperature(self) -> None:
        self.WriteRegister(PWR_CTRL, (self.ReadRegister(PWR_CTRL) | BIT_3))
        return None

    def DisableTemperature(self) -> None:
        self.WriteRegister(PWR_CTRL, (self.ReadRegister(PWR_CTRL) & ~BIT_3))
        return None

    def EnableFIFOHeader(self) -> None:
        self.WriteRegister(FIFO_CONFIG_1, (self.ReadRegister(FIFO_CONFIG_1) | BIT_4))
        return None

    def DisableFIFOHeader(self) -> None:
        self.WriteRegister(FIFO_CONFIG_1, (self.ReadRegister(FIFO_CONFIG_1) & ~BIT_4))
        return None

    def EnableDataStreaming(self) -> None:
        self.WriteRegister(FIFO_CONFIG_1, (self.ReadRegister(FIFO_CONFIG_1) | LAST_3_BITS))
        return None

    def DisableDataStreaming(self) -> None:
        self.WriteRegister(FIFO_CONFIG_1, (self.ReadRegister(FIFO_CONFIG_1) & ~LAST_3_BITS))
        return None

    def EnableAccelFilterPeformance(self) -> None:
        self.WriteRegister(ACC_CONF, (self.ReadRegister(ACC_CONF) | BIT_7))
        return None

    def DisableAccelFilterPerformance(self) -> None:
        self.WriteRegister(ACC_CONF, (self.ReadRegister(ACC_CONF) & ~BIT_7))
        return None

    def EnableGyroNoisePerformance(self) -> None:
        self.WriteRegister(GYR_CONF, (self.ReadRegister(GYR_CONF) | BIT_6))
        return None

    def DisableGyroNoisePerformance(self) -> None:
        self.WriteRegister(GYR_CONF, (self.ReadRegister(GYR_CONF) & ~BIT_6))
        return None

    def EnableGyroFilterPerformance(self) -> None:
        self.WriteRegister(GYR_CONF, (self.ReadRegister(GYR_CONF) | BIT_7))
        return None

    def DisableGyroFilterPerformance(self) -> None:
        self.WriteRegister(GYR_CONF, (self.ReadRegister(GYR_CONF) & ~BIT_7))
        return None
    
    
    def SetAccelerometerRange(self, new_range : int = ACC_RANGE_2G) -> None:
        if(new_range == ACC_RANGE_2G):
            self.WriteRegister(ACC_RANGE, ACC_RANGE_2G)
            self.acc_range = (2 * GRAVITY)
        elif(new_range == ACC_RANGE_4G):
            self.WriteRegister(ACC_RANGE, ACC_RANGE_4G)
            self.acc_range = (4 * GRAVITY)
        elif(new_range == ACC_RANGE_8G):
            self.WriteRegister(ACC_RANGE, ACC_RANGE_8G)
            self.acc_range = (8 * GRAVITY)
        elif(new_range == ACC_RANGE_16G):
            self.WriteRegister(ACC_RANGE, ACC_RANGE_16G)
            self.acc_range = (16 * GRAVITY)
        else:
            print("Invalid command / setting!")
    
        return None
    

    def SetGyroscopeRange(self, new_range : int = GYR_RANGE_2000) -> None:
        
        if(new_range == GYR_RANGE_2000):
            self.WriteRegister(GYR_RANGE, GYR_RANGE_2000)
            self.gyr_range = 2000
        elif(new_range == GYR_RANGE_1000):
            self.WriteRegister(GYR_RANGE, GYR_RANGE_1000)
            self.gyr_range = 1000
        elif(new_range == GYR_RANGE_500):
            self.WriteRegister(GYR_RANGE, GYR_RANGE_500)
            self.gyr_range = 500
        elif(new_range == GYR_RANGE_250):
            self.WriteRegister(GYR_RANGE_250)
            self.gyr_range = 250
        elif(new_range == GYR_RANGE_125):
            self.WriteRegister(GYR_RANGE_125)
            self.gyr_range = 125
        else:
            print("Invalid command / setting!")

        return None
    
    

    def SetAccelerometerODR(self, ODR_VALUE : int) -> None:
        if(ODR_VALUE == ACC_ODR_1600):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & MSB_MASK_8BIT) | ACC_ODR_1600))
            self.acc_odr = 1600
        elif(ODR_VALUE == ACC_ODR_800):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & MSB_MASK_8BIT) | ACC_ODR_800))
            self.acc_odr = 800
        elif(ODR_VALUE == ACC_ODR_400):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & MSB_MASK_8BIT) | ACC_ODR_400))
            self.acc_odr = 400
        elif(ODR_VALUE == ACC_ODR_200):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & MSB_MASK_8BIT) | ACC_ODR_200))
            self.acc_odr = 200
        elif(ODR_VALUE == ACC_ODR_100):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & MSB_MASK_8BIT) | ACC_ODR_100))
            self.acc_odr = 100
        elif(ODR_VALUE == ACC_ODR_50):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & MSB_MASK_8BIT) | ACC_ODR_50))
            self.acc_odr = 50
        elif(ODR_VALUE == ACC_ODR_25):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & MSB_MASK_8BIT) | ACC_ODR_25))
            self.acc_odr = 25
        else:
            print("Invalid command / setting!")
            
        return None

  
    def SetGyroscopeODR(self, odr : int = GYR_ODR_200) -> None:      
        if(odr == GYR_ODR_3200):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & MSB_MASK_8BIT) | GYR_ODR_3200))
            self.gyr_odr = 3200
        elif(odr == GYR_ODR_1600):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & MSB_MASK_8BIT) | GYR_ODR_1600))
            self.gyr_odr = 1600
        elif(odr == GYR_ODR_800):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & MSB_MASK_8BIT) | GYR_ODR_800))
            self.gyr_odr = 800
        elif(odr == GYR_ODR_400):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & MSB_MASK_8BIT) | GYR_ODR_400))
            self.gyr_odr = 400
        elif(odr == GYR_ODR_200):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & MSB_MASK_8BIT) | GYR_ODR_200))
            self.gyr_odr = 200
        elif(odr == GYR_ODR_100):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & MSB_MASK_8BIT) | GYR_ODR_100))
            self.gyr_odr = 100
        elif(odr == GYR_ODR_50):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & MSB_MASK_8BIT) | GYR_ODR_50))
            self.gyr_odr = 50
        elif(odr == GYR_ODR_25):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & MSB_MASK_8BIT) | GYR_ODR_25))
            self.gyr_odr = 25
        else:
            print("Invalid command / setting!")
    
        return None


    def SetAccelerometerBWP(self, bwp : int = ACC_BWP_NORMAL) -> None:
        if(bwp == ACC_BWP_OSR4):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & LSB_MASK_8BIT_8) | (ACC_BWP_OSR4 << 4)))
        elif(bwp == ACC_BWP_OSR2):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & LSB_MASK_8BIT_8) | (ACC_BWP_OSR2 << 4)))
        elif(bwp == ACC_BWP_NORMAL):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & LSB_MASK_8BIT_8) | (ACC_BWP_NORMAL << 4)))
        elif(bwp == ACC_BWP_CIC):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & LSB_MASK_8BIT_8) | (ACC_BWP_CIC << 4)))
        elif(bwp == ACC_BWP_RES16):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & LSB_MASK_8BIT_8) | (ACC_BWP_RES16 << 4)))
        elif(bwp == ACC_BWP_RES32):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & LSB_MASK_8BIT_8) | (ACC_BWP_RES32 << 4)))
        elif(bwp == ACC_BWP_RES64):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & LSB_MASK_8BIT_8) | (ACC_BWP_RES64 << 4)))
        elif(bwp == ACC_BWP_RES128):
            self.WriteRegister(ACC_CONF, ((self.ReadRegister(ACC_CONF) & LSB_MASK_8BIT_8) | (ACC_BWP_RES128 << 4)))
        else:
            print("Invalid command / setting!")

        return None


    def SetGyroscopeBWP(self, bwp : int = GYR_BWP_NORMAL) -> None:
        if(bwp == GYR_BWP_OSR4):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & LSB_MASK_8BIT_8) | (GYR_BWP_OSR4 << 4)))
        elif(bwp == GYR_BWP_OSR2):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & LSB_MASK_8BIT_8) | (GYR_BWP_OSR2 << 4)))
        elif(bwp == GYR_BWP_NORMAL):
            self.WriteRegister(GYR_CONF, ((self.ReadRegister(GYR_CONF) & LSB_MASK_8BIT_8) | (GYR_BWP_NORMAL << 4)))
        else:
            print("Invalid setting / command !")
            
        return None


    def RawAccelerometer_XData(self) -> int:
        raw_acc_x_data : int = ((self.ReadRegister(ACC_X_15_8) << 8) | self.ReadRegister(ACC_X_7_0))
        return raw_acc_x_data

    def RawAccelerometer_YData(self) -> int:
        raw_acc_y_data : int = ((self.ReadRegister(ACC_Y_15_8) << 8) | self.ReadRegister(ACC_Y_7_0))
        return raw_acc_y_data

    def RawAccelerometer_ZData(self) -> int:
        raw_acc_z_data : int = ((self.ReadRegister(ACC_Z_15_8) << 8) | self.ReadRegister(ACC_Z_7_0))
        return raw_acc_z_data

    def RawAccelerometerData(self) -> tuple:
        x_data = self.RawAccelerometer_XData()
        y_data = self.RawAccelerometer_YData()
        z_data = self.RawAccelerometer_ZData()

        full_data = (x_data, y_data, z_data)

        return full_data

    def FormatRawAccelerometer(self, value : int) -> float:
        if(value > 32767):
            new_value : float = (((value - 65536) / 32768) * self.acc_range)
        else:
            new_value : float =  ((value / 32768) * self.acc_range)

        return new_value


    def FormatAccelerometerData(self) -> tuple:
        new_x_data = self.FormatRawAccelerometer(value=self.RawAccelerometer_XData())
        new_y_data = self.FormatRawAccelerometer(value=self.RawAccelerometer_YData())
        new_z_data = self.FormatRawAccelerometer(value=self.RawAccelerometer_ZData())

        new_data_tuple : tuple = (new_x_data, new_y_data, new_z_data)

        return new_data_tuple



    def RawGyroscope_XData(self) -> int:
        raw_gyr_x_data : int = ((self.ReadRegister(GYR_X_15_8) << 8) | self.ReadRegister(GYR_Y_7_0))
        return raw_gyr_x_data

    def RawGyroscope_YData(self) -> int:
        raw_gyr_y_data : int = ((self.ReadRegister(GYR_Y_15_8) << 8) | self.ReadRegister(GYR_Y_7_0))
        return raw_gyr_y_data

    def RawGyroscope_ZData(self) -> int:
        raw_gyr_z_data : int = ((self.ReadRegister(GYR_Z_15_8) << 8) | self.ReadRegister(GYR_Z_7_0))
        return raw_gyr_z_data


    def RawGyroscopeData(self) -> tuple:
        x_data = self.RawGyroscope_XData()
        y_data = self.RawGyroscope_YData()
        z_data = self.RawGyroscope_ZData()

        full_data = (x_data, y_data, z_data)

        return full_data


    def FormatRawGyroscope(self, value : int) -> float:
        if(value > 32767):
            new_data = (1.2 * ((value - 65536) / 32768) * self.gyr_range)
        else:
            new_data = (1.2 * (value / 32768) * self.gyr_range)

        return new_data


    def FormatGyroscopeData(self) -> tuple:
        new_x_data : float = self.FormatRawGyroscope(value=self.RawGyroscope_XData())
        new_y_data : float = self.FormatRawGyroscope(value=self.RawGyroscope_YData())
        new_z_data : float = self.FormatRawGyroscope(value=self.RawGyroscope_ZData())

        format_gyro_data : tuple[float] = (new_x_data, new_y_data, new_z_data)

        return format_gyro_data


    def RawTemperatureData(self) -> int:
        temp_value_lsb : int = self.ReadRegister(TEMP_7_0)
        temp_value_msb : int = self.ReadRegister(TEMP_15_8)
        temp_value_full = ((temp_value_msb << 8) | temp_value_lsb)
        
        temp_value_full = self.UNSIGNED_TO_SIGNED(temp_value_full, 2)

        return temp_value_full


    def FormatTemperatureData(self) -> float:
        raw_temp_data = self.RawTemperatureData()
        if(raw_temp_data > 32767):
            temp_celsius = (((raw_temp_data - 65536) * 0.001952594) + 32)
        else:
            temp_celsius = ((raw_temp_data - 65536) * 0.001952594)

        return temp_celsius



    def FormatSensorTime(self) -> int:
        time_0 : int = self.ReadRegister(SENSORTIME_0)
        time_1 : int = self.ReadRegister(SENSORTIME_1)
        time_2 : int = self.ReadRegister(SENSORTIME_2)

        full_time = ((time_2 << 16) | (time_1 << 8) | time_0)

        return full_time













