from operator import xor
import os
import time
import smbus

# Constants

I2C_LS_REG_EXPONENT0 = 0x00
I2C_LS_REG_RESULT0 = 0x01
I2C_LS_REG_EXPONENT1 = 0x02
I2C_LS_REG_RESULT1 = 0x03
I2C_LS_REG_EXPONENT2 = 0x04
I2C_LS_REG_RESULT2 = 0x05
I2C_LS_REG_EXPONENT3 = 0x06
I2C_LS_REG_RESULT3 = 0x07
I2C_LS_REG_TL = 0x19
I2C_LS_REG_TH = 0x09

I2C_LS_REG_CONFIG0 = 0x0A
I2C_LS_REG_CONFIG1 = 0x0B

I2C_LS_REG_DEVICEID = 0x11

#Configdata for Register "Configuration0"
I2C_LS_REG_CONFIG0_DEFAULT = 0xc838
#Bit 15 0 - QWAKE not applicable outside OneShot Mode
#Bit 14 0 - Musts read or write 0
#Bit 13..10 - 12 AutoRange
#Bit 9..6 - 8 100ms Conversion Time
#Bit 5..4 - 3 Continuous
#Bit 3 Latch 1 - INT Config - leave at reset
#Bit 2 INT_POL - 0 Active Low
#BITS 1..0 - FAULT COUNT - 0h default


#  0   | 0  |  12    |   8  |  3   | 1  | 0 | 0  | Decimal Value
#  0   | 0  | 1100   | 1000 | 0011 | 1  | 0 | 00 | Binary
#  0x0 |0x0 |  0xC   |  0x8 | 0x3  |0x1 |0x0|0x0 | Hex
#  15  | 14 | 13..10 | 9..6 | 5..4 | 3  | 2 |1..0| Bit # in Decimal


#001100100000111000b  to Hex = 0xc838

# Configdata for Register "Configuration1"
I2C_LS_REG_CONFIG1_DEFAULT = 0x4011
# Bit 15..7 - 128 Must Read of Write 128
# Bit 6..5 - 0 - Channel Select for Threshold Logic
# Bit 4 - INT_DIR - 1 OUTPUT
# Bit 3..2 - INT_CFG - 0 - Smbus alert
# Bit 1 - 0 - Must read or write 0
# Bit 0 - 1 - I2C_BURST Enabled

#    128    | 0    | 1 | 0    | 0 | 1 | Decimal Value
# 010000000 | 00   | 1 | 00   | 0 | 1 | Binary
#   0x80    | 0x0  |0x1| 0x0  |0x0|0x1| Hex
#   15..7   | 6..5 | 4 | 3..2 | 1 | 0 | Bit # in Decimal

#0100000000010001b to Hex = 0x4011

i2c_ch = 0  # /dev/i2c-0 is where M0 is
#i2c_address = 0x48  # This is default but can be changed
#bus = smbus.SMBus(i2c_ch)  # Initialize i2c Bus

print("\nOPT4048 Demo Driver")

class OPT4048:
    def __init__(self, address=0x44, bus=3): #bus=1 is just default
        """ -----------------------------------------------
        Name: init

        Description:  initialize the opt4048

        Input:  address - i2c address of the opt4048
        bus - default 1
        """

        self.bus = smbus.SMBus(bus)
        self.address = address

    def read_register_16bit(self, adr):
        """ -----------------------------------------------
        Name: read_register_16bit

        Description: reads a register of the opt4048

        Input:  adr - registeradress to read from

        Return: data
        """
        values = self.bus.read_i2c_block_data(self.address, adr, 2)
        data = (values[0] << 8) | values[1]
        return data

    def write_register_16bit(self, adr, data):
        """ -----------------------------------------------
        Name: write_register_16bit

        Description:  write to a register of the opt4048

        Input:  adr - registeradress to write to
                data - data to write to register

        Return: void
        """
        d1 = (data >> 8)
        d0 = data & 0xFF
        return self.bus.write_i2c_block_data(self.address, adr, [d1, d0])
    
    def write_config_reg0(self):
        """ -----------------------------------------------
        Name: write_config_req

        Description:  write to config register

        Input:  data - data to write to register

        Ausgang: void
        """
        return self.write_register_16bit(I2C_LS_REG_CONFIG0, I2C_LS_REG_CONFIG0_DEFAULT)
    
    def write_config_reg1(self):
        """ -----------------------------------------------
        Name: write_config_req

        Description:  write to config register

        Input:  data - data to write to register

        Ausgang: void
        """
        return self.write_register_16bit(I2C_LS_REG_CONFIG1, I2C_LS_REG_CONFIG1_DEFAULT)
    
    
    def read_device_id(self):
        """ -----------------------------------------------
        Name: read_device_id

        Description:  read device id of the opt3001

        Input: void

        Ausgang: manufacture id
        """
        return self.read_register_16bit(I2C_LS_REG_DEVICEID)
    
    def get_ADC_codes(self, I2C_LS_REG_EXPONENT0):
        data = self.read_register_16bit(I2C_LS_REG_EXPONENT0)
        exponent = (data >> 12) #Shift bits 12 to the right to get EXPONENT[4]
        result_msb = data & 0xFFF #Get RESULT_MSB [12] by &ing with FFF

        data = self.read_register_16bit(I2C_LS_REG_EXPONENT0 + 1)
        result_lsb = (data >> 8) #RESULT_LSB
        counter = (data & 0xFF) >> 4
        crc = data & 0xFFF

        mantissa = (result_msb<<8) + result_lsb
        adc_codes = mantissa << exponent 
        return adc_codes

    def read_lux_fixpoint(self):
        """ -----------------------------------------------
        Name: read_lux_fixpoint

        Description:  read the brightness of the opt3001 with two fixed decimal places

        Input:  void

        Ausgang: manufacture id
        """
        # Register Value
        req_value = self.read_register_16bit(I2C_LS_REG_RESULT)

        # Convert to LUX
        mantisse = req_value & 0x0fff
        exponent = (req_value & 0xf000) >> 12

        return 2**exponent * mantisse  # mantisse << exponent;

    def read_lux_float(self):
        """ -----------------------------------------------
        Name: read_lux_float

        Description:  read the brightness of the opt3001 as float

        Input:  void

        Ausgang: manufacture id
        """
        # Register Value
        req_value = self.read_register_16bit(I2C_LS_REG_RESULT)

        # Convert to LUX
        mantisse = req_value & 0x0fff
        exponent = (req_value & 0xf000) >> 12

        return 2**exponent * mantisse * 0.01  # mantisse << exponent * 0.01;
    
    #def calcCRC(result_msb, result_lsb, exponent, crc):
    #    r = (result_msb << 8) + result_lsb
    #    x0 = xor()
    #    x1 = 
    #    x2 = 