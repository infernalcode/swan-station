from adafruit_motorkit import MotorKit

from analogio import AnalogIn
from swan_counter.wheel import Wheel
from swan_counter.counter import Counter

import board
import math
import neopixel
import time

# hardware init
motor1 = MotorKit(i2c=board.I2C(), address=0x60)
motor2 = MotorKit(i2c=board.I2C(), address=0x61)
motor3 = MotorKit(i2c=board.I2C(), address=0x62)

WheelA = Wheel("A", motor1.stepper1, AnalogIn(board.A1))
WheelB = Wheel("B", motor1.stepper2, AnalogIn(board.A2))
WheelC = Wheel("C", motor2.stepper1, AnalogIn(board.A3))
WheelD = Wheel("D", motor2.stepper2, AnalogIn(board.A4))
WheelE = Wheel("E", motor3.stepper1, AnalogIn(board.A5))

# turn of LED
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0)
pixels.fill((0, 0, 0))

## START MAIN
counter = Counter(6480) # 108 minutes x 60 seconds = 6480
systemCritical = False

#WheelA.reset()
#WheelB.reset()
#WheelC.reset()
#WheelD.reset()
#WheelE.reset()

while True:

  #WheelA.stepOrAdvance()
  #WheelB.stepOrAdvance()
  #WheelC.stepOrAdvance()
  #WheelD.stepOrAdvance()
  #WheelE.stepOrAdvance()

  counter.iterate()

  time.sleep(1)
