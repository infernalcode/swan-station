from adafruit_motorkit import MotorKit

from analogio import AnalogIn
from swan_counter.wheel import Wheel
from swan_counter.counter import Counter

from settings import settings

import board
import math
import neopixel
import supervisor
import time

# hardware init
motor1 = MotorKit(i2c=board.I2C(), address=0x60)
motor2 = MotorKit(i2c=board.I2C(), address=0x61)
motor3 = MotorKit(i2c=board.I2C(), address=0x62)

# read settings
offsetA = settings.get("offsetA", 0)
offsetB = settings.get("offsetB", 0)
offsetC = settings.get("offsetC", 0)
offsetD = settings.get("offsetD", 0)
offsetE = settings.get("offsetE", 0)

# initialize wheels
WheelA = Wheel("A", motor1.stepper1, AnalogIn(board.A1), offsetA)
WheelB = Wheel("B", motor1.stepper2, AnalogIn(board.A2), offsetB)
WheelC = Wheel("C", motor2.stepper1, AnalogIn(board.A3), offsetC)
WheelD = Wheel("D", motor2.stepper2, AnalogIn(board.A4), offsetD)
WheelE = Wheel("E", motor3.stepper1, AnalogIn(board.A5), offsetE)

# turn of LED
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0)
pixels.fill((0, 0, 0))

## START MAIN
counter = Counter(6480) # 108 minutes x 60 seconds = 6480
systemCritical = False

calibration = bool(settings.get("calibrateOnBoot", "false"))

if calibration:
  print(">: BRUN CALIBRATE.BIN")
  print(">: ", end="")

while calibration:
  if supervisor.runtime.serial_bytes_available:
    value = input().strip()

    if value == "":
        continue
    elif value == "RA":
      WheelA.reset()
    elif value == "FA":
      WheelA.flip()
    elif value == "a":
      WheelA.step(1)
    elif value == "A":
      WheelA.step(5)

    elif value == "RB":
      WheelB.reset()
    elif value == "FB":
      WheelB.flip()
    elif value == "b":
      WheelB.step(1)
    elif value == "B":
      WheelB.step(5)

    elif value == "continue":
      calibration = False
    else:
      print("Command not found: {}".format(value))

    print(">: ", end="")


print(">: BRUN RADZINSKY.BIN")
print(">: ", end="")
while True:
  WheelA.stepOrAdvance(counter.timer, mod=1)
  WheelB.stepOrAdvance(counter.timer, mod=10)

  #WheelC.stepOrAdvance(counter.timer, mod=60)
  #WheelD.stepOrAdvance(counter.timer, mod=600)
  #WheelE.stepOrAdvance()

  counter.iterate()

  time.sleep(1)
