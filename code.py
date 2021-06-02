from adafruit_motor.stepper import DOUBLE, FORWARD
from adafruit_motorkit import MotorKit
from analogio import AnalogIn
from glyphs import Glyphs

import audiocore
import audioio
import board
import digitalio
import math
import neopixel
import time

# hardware init
kit = MotorKit(i2c=board.I2C())
kit.stepper1.release()
a = AnalogIn(board.A4)
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

# audio details
WAV_FILE_NAME = "swan-beep.wav"
enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

# split flap details
glyphs = Glyphs.GetGlyphs()

# motor details
stepAngle = 1.8                    # per NEMA 17 datasheet
stepsPerRotation = 360 / stepAngle # per NEMA 17 datasheet, 200 steps per rotation
totalSec = len(glyphs)
stepsPerArc = stepsPerRotation / totalSec   # How many steps to move to the next flap

# countdown details
timerLength = 6480 # 108 minutes x 60 seconds = 6480
currentTimerCount = timerLength
criticalThreshold = 240
failureThreshold = 60

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
    time.sleep(0.001)

def step(motor, times, direction=FORWARD):
  for _ in range(times):
    motor.onestep(direction=direction)
    time.sleep(0.05)

def play_beep():
  with audioio.AudioOut(board.A0) as audio:
    sfx_file = open(WAV_FILE_NAME, "rb")
    wave = audiocore.WaveFile(sfx_file)

    audio.play(wave)
    while audio.playing:
        pass

if not at_index(a): reset(a)
arc = 1
currentGlyph = Glyphs.ResetTo()
systemCritical = False
systemFailure = False

while True:
  # check arc
  rc, currentGlyph = status(a, arc, currentGlyph)

  # reset or advance
  if (currentGlyph == Glyphs.ResetAt()):
    reset(a)
  else:
    step(kit.stepper1, stepsPerArc)

  # show debug
  voltage = get_voltage(a)
  print("Glpyh: %s, Timer: %s, Arc: %s, Voltage: %s (atIndex: %s)" % (glyphs[currentGlyph], currentTimerCount, arc, math.floor(voltage), at_index(a)))

  currentTimerCount -= 1

  if (currentTimerCount <= criticalThreshold and not systemFailure):
    systemCritical = True
    print("SYSTEM CRITICAL")

  if (currentTimerCount <= failureThreshold):
    systemFailure = True
    for _ in range(totalSec):
      print("SYSTEM FAILURE ", end="")

  #play_beep()

  time.sleep(1)






