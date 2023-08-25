import opt4048
import time

address = 0x44

opt = opt4048.OPT4048(address) 

# Configure to run in Continuous conversions mode
#opt.write_config_reg(opt3001.I2C_LS_CONFIG_CONT_FULL_800MS)

print("Device ID - " + hex(opt.read_device_id())) #Should read 0x821 as per datasheet

print("Default Result 0 - " + hex(opt.read_register_16bit(0x00))) #Let's make sure we read a zero here

print("Initializing Device - ")

opt.write_config_reg0()
opt.write_config_reg1()

time.sleep(1) #Give it time to settle

while True:

    #print("Init Result 0 - " + hex(opt.read_register_16bit(0x00))) #Now it should read non-zero
    #print("Init Counter 0 - " + hex(opt.read_register_16bit(0x01))) #Now it should read non-zero
    #time.sleep(1)

    #EXPONENT[4] RESULT_MSB[12] RESULT_LSB [8]  COUNTER [4] CRC [4]

    print("Red - ", hex(opt.get_ADC_codes(0x00)), " - Green -", hex(opt.get_ADC_codes(0x02)), " - Blue -", hex(opt.get_ADC_codes(0x04)) )

    