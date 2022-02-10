# https://github.com/Thinary/AHT10/blob/master/src/Thinary_AHT10.cpp
# https://myhydropi.com/raspberry-pi-i2c-temperature-sensor
import smbus
import time
import csv
import sys

# Csv File
if len(sys.argv) != 2:
    print("Insufficient arguments")
    sys.exit()

file_path = sys.argv[1] + ".csv"
f = open(file_path,"a",newline='')
wr = csv.writer(f)
# I2C Channel
I2C_CH=1
# Get I2C bus object
i2c = smbus.SMBus(I2C_CH)
# time.sleep(1) #wait here to avoid 121 IO Error

# ----------------AHT10-------------------
AHT10_DEV_ADDR = 0x38

#i2c.write_i2c_block_data(AHT10_DEV_ADDR, 0xE1, config)
#time.sleep(0.5)
config = [0x08, 0x00]
MeasureCmd = [0x33, 0x00]
i2c.write_i2c_block_data(AHT10_DEV_ADDR, 0xAC, MeasureCmd)
time.sleep(0.5)
data = i2c.read_i2c_block_data(AHT10_DEV_ADDR,0x00)
temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
ctemp = ((temp*200) / 1048576) - 50
ctemp = round(ctemp,3)
print(u'Temperature: {0}°C'.format(ctemp))
tmp = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
#print(tmp)
ctmp = int(tmp * 100 / 1048576)
print(u'Humidity: {0}%'.format(ctmp))
# ----------------------------------------

# ----------------BH1750------------------
BH1750_DEV_ADDR = 0x23 # BH1750 주소
CONT_H_RES_MODE     = 0x10 #1lx 해상도, 측정 시간 : 120ms
CONT_H_RES_MODE2    = 0x11 #0.5lx 해상도, 측정 시간 : 120ms
CONT_L_RES_MODE     = 0x13 #4lx 해상도, 측정 시간 : 16ms
ONETIME_H_RES_MODE  = 0x20 #1lx 해상도, 측정 시간 : 120ms, 한번 측정하고 절전모드 진입
ONETIME_H_RES_MODE2 = 0x21 #0.5lx 해상도, 측정 시간 : 120ms, 한번 측정하고 절전모드 진입
ONETIME_L_RES_MODE  = 0x23 #4lx 해상도, 측정 시간 : 16ms, 한번 측정하고 절전모드 진입

luxBytes = i2c.read_i2c_block_data(BH1750_DEV_ADDR, CONT_H_RES_MODE, 2)
lux = int.from_bytes(luxBytes, byteorder='big')
print('{0} lux'.format(lux))
# ----------------------------------------
# Write Data in Csv
wr.writerow([ctemp,ctmp,lux])
f.close()
