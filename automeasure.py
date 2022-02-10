#!/usr/bin/env python3
import signal
import sys
import RPi.GPIO as GPIO
import smbus
import csv
from Adafruit_AMG88xx import Adafruit_AMG88xx
from time import sleep

BUTTON_GPIO = 16

def signal_handler(sig, frame):
    f.close()
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):
    i2c.write_i2c_block_data(AHT10_DEV_ADDR, 0xAC, MeasureCmd)
    sleep(0.5)
    data = i2c.read_i2c_block_data(AHT10_DEV_ADDR,0x00)
    temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
    ctemp = ((temp*200) / 1048576) - 50
    ctemp = round(ctemp,3)
    tmp = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    ctmp = int(tmp * 100 / 1048576)

    luxBytes = i2c.read_i2c_block_data(BH1750_DEV_ADDR, ONETIME_H_RES_MODE, 2)
    lux = int.from_bytes(luxBytes, byteorder='big')

    pixels = sensor.readPixels()
    print(u'Temperature: {0}°C'.format(ctemp))
    print(u'Humidity: {0}%'.format(ctmp))
    print('{0} lux'.format(lux))

    print("*"*20)
    for j in range(8):
        for i in range(8):
            print(f"{pixels[8*i:8*(i+1)]:.2f}",end=" ")
        print()
    print("*"*20)

    # Write Data in Csv
    wr.writerow([ctemp,ctmp,lux])
    
if __name__ == '__main__':
    f = open("test.csv","a",newline='')
    wr = csv.writer(f)
    sensor = Adafruit_AMG88xx()

    I2C_CH=1
    i2c = smbus.SMBus(I2C_CH)

    AHT10_DEV_ADDR = 0x38
    config = [0x08, 0x00]
    MeasureCmd = [0x33, 0x00]

    BH1750_DEV_ADDR = 0x23 # BH1750 주소
    CONT_H_RES_MODE     = 0x10 #1lx 해상도, 측정 시간 : 120ms
    CONT_H_RES_MODE2    = 0x11 #0.5lx 해상도, 측정 시간 : 120ms
    CONT_L_RES_MODE     = 0x13 #4lx 해상도, 측정 시간 : 16ms
    ONETIME_H_RES_MODE  = 0x20 #1lx 해상도, 측정 시간 : 120ms, 한번 측정하고 절전모드 진입
    ONETIME_H_RES_MODE2 = 0x21 #0.5lx 해상도, 측정 시간 : 120ms, 한번 측정하고 절전모드 진입
    ONETIME_L_RES_MODE  = 0x23 #4lx 해상도, 측정 시간 : 16ms, 한번 측정하고 절전모드 진입

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, 
            callback=button_pressed_callback, bouncetime=1000)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
