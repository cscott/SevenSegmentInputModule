# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""CircuitPython I2C Device Address Scan"""
import time
import board
import busio
import microcontroller
from digitalio import DigitalInOut

#i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# To create I2C bus on specific pins
# import busio
i2c = busio.I2C(microcontroller.pin.GPIO27, microcontroller.pin.GPIO26)

while not i2c.try_lock():
    pass

LED_ADDR = 0x34

def reg_write(reg, value):
    i2c.writeto(LED_ADDR, bytes([reg, value]))
def reg_read(reg):
    result = bytearray(1)
    i2c.writeto_then_readfrom(LED_ADDR, bytes([reg]), result)
    return result[0]

try:
    # bring out of hardware shutdown
    SDB = DigitalInOut(microcontroller.pin.GPIO29)
    SDB.switch_to_output(True)
    # reset the chip
    reg_write(0xCF, 0xAE)
    # configure the chip: 9SWx15CS, LGC=0 (?), enable short detect
    reg_write(0xA0, 0x01)
    print("Config:", hex(reg_read(0xA0)))
    # short detect
    reg_write(0xA1, 0x01)
    reg_write(0xA0, 0x03) # open detect
    for reg in range(0xB3, 0xC5):
        print("Open?", hex(reg), hex(reg_read(reg)))
    reg_write(0xA0, 0x05) # short detect
    for reg in range(0xB3, 0xC5):
        print("Short?", hex(reg), hex(reg_read(reg)))
    reg_write(0xA0, 0x01)
    # max brightness! (GCC)
    reg_write(0xA1, 0x40)
    print(hex(reg_read(0xA1)))
    for reg in range(0x90, 0xA0):
        reg_write(reg, 0xFF)
    # first segment on
    reg_write(0x01, 0xFF)
    for reg in range(0x02, 0x90):
        time.sleep(0.05)
        print(reg)
        reg_write(reg, 0xFF)
        #reg_write(reg-1, 0x00)

finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
    i2c.unlock()
