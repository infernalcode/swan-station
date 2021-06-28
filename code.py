from _pixelbuf import wheel
from adafruit_motorkit import MotorKit

from analogio import AnalogIn
from swan_counter.wheel import Wheel
from swan_counter.countdown import Countdown

from config import config

import board
import math
import neopixel
import time

# hardware init
motor1 = MotorKit(i2c=board.I2C(), address=0x60)
motor2 = MotorKit(i2c=board.I2C(), address=0x61)
motor3 = MotorKit(i2c=board.I2C(), address=0x62)

# read settings
wheelSettings = config.get("wheels")

# initialize wheels
WheelA = Wheel("A", motor1.stepper1, AnalogIn(board.A1), wheelSettings.get("a"))
WheelB = Wheel("B", motor1.stepper2, AnalogIn(board.A2), wheelSettings.get("b"))
WheelC = Wheel("C", motor2.stepper1, AnalogIn(board.A3), wheelSettings.get("c"))
WheelD = Wheel("D", motor2.stepper2, AnalogIn(board.A4), wheelSettings.get("d"))
WheelE = Wheel("E", motor3.stepper1, AnalogIn(board.A5), wheelSettings.get("e"))

# turn of LED
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0)
pixels.fill((0, 0, 0))

## START MAIN
countdown = Countdown(WheelA, WheelB, WheelC, WheelD, WheelE, config)

while True:
  countdown.iterate()

  time.sleep(1)
