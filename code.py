from lib.adafruit_motor.stepper import BACKWARD, INTERLEAVE
import time
from adafruit_motor.stepper import DOUBLE, FORWARD
import board
from analogio import AnalogIn
import neopixel
import math
from glyphs import Glyphs

from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())
kit.stepper1.release()

a = AnalogIn(board.A0)
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

stepAngle = 1.8                    # per NEMA 17 datasheet
stepsPerRotation = 360 / stepAngle # per NEMA 17 datasheet, 200 steps per rotation

glyphs = Glyphs.GetGlyphs()

print("Total Glyphs: %s" % len(glyphs))

totalSec = len(glyphs)
stepsPerArc = stepsPerRotation / totalSec   # How many steps to move to the next flap
timerLength = 6480 # 108 minutes x 60 seconds = 6480
currentTimerCount = timerLength

def status(pin, arc, counter):
  if at_index(pin):
    pixels.fill((255, 255, 255))
    arc = 1
    counter = Glyphs.ResetTo()
  else:
    pixels.fill((0, 255, 0))
    arc += 1
    counter -= 1

  return arc, counter

def get_voltage(pin):
  return (pin.value * 3.3) / 65536

def at_index(pin):
    voltage = get_voltage(pin)
    return math.floor(voltage) >= 3

def reset(pin):
  while True:
    if at_index(pin): return
    kit.stepper1.onestep()
    time.sleep(0.005)

def step(motor, times, direction=FORWARD):
  for _ in range(times):
    motor.onestep(direction=direction)
    time.sleep(0.1)

if not at_index(a): reset(a)
arc = 1
counter = Glyphs.ResetTo()

while True:
  # check arc
  arc, counter = status(a, arc, counter)

  # reset or advance
  if (counter == Glyphs.ResetAt()):
    reset(a)
  else:
    step(kit.stepper1, stepsPerArc)

  # show debug
  voltage = get_voltage(a)
  print("Glpyh: %s, Arc: %s, Voltage: %s (atIndex: %s)" % (glyphs[counter], arc, math.floor(voltage), at_index(a)))

  time.sleep(1)


