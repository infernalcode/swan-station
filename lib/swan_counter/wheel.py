import math

from adafruit_itertools import cycle
from micropython import const

from .settings import Settings

ZERO = const(0)
ONE = const(1)
TWO = const(2)
THREE = const(3)
FOUR = const(4)
FIVE = const(5)
SIX = const(6)
SEVEN = const(7)
EIGHT = const(8)
NINE = const(9)
BLANK = const(10)
CLOTH = const(11)
SPIRAL = const(12)
FEATHER = const(13)
BIRD = const(14)
STICK = const(15)
STAPLE = const(16)
MAN = const(17)
BREAD = const(18)
HAND = const(19)

RESET_AT = ONE
RESET_TO = NINE

glyphMap = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, BLANK, CLOTH, SPIRAL, FEATHER, BIRD, STICK, STAPLE, MAN, BREAD, HAND]

class Wheel:
  # motor details
  stepAngle = 1.8                    # per NEMA 17 datasheet
  stepsPerRotation = 360 / stepAngle # per NEMA 17 datasheet, 200 steps per rotation
  rotationsPerGear = 2               # smaller gear needs 2 rotations for full rotation on large gear

  totalArc = len(glyphMap)
  stepsPerArc = stepsPerRotation / totalArc          # should be 10
  arcStepsSmallGear = stepsPerArc * rotationsPerGear # should be 20

  def __init__(self, name, stepper, pin, settings):

    self.name = name
    self.stepper = stepper
    self.pin = pin
    self.settings = Settings.parse(settings)

    self.offset = self.settings.defaultOffset
    self.arc = 0
    self.position = 0

    self.counter = BLANK
    self.glyph = glyphMap[self.counter]
    self.reset_at = RESET_AT
    self.stepper.release()

  def _get_voltage(self):
    return (self.pin.value * 3.3) / 65536

  def at_index(self):
    return self._get_voltage() > self.settings.voltageThreshold

  def calibrate(self):
    self.offset = 0
    if not self.at_index(): self.reset()
    self.saveCalibration()

  def saveCalibration(self):
    self.arc = 0
    self.position = 0
    self.info()

  def reset(self):
    while True:
      if self.at_index():
        self.step(self.offset)
        return
      self.step(1)

  def flip(self):
    steps = Wheel.arcStepsSmallGear * (Wheel.totalArc / 2)
    self.step(steps)

  def full(self):
    self.step(times=Wheel.arcStepsSmallGear * Wheel.totalArc)

  def arcStep(self):
    self.arc += 1
    for _ in range(Wheel.arcStepsSmallGear):
      self.step(1)
      self.position += 1

  def step(self, times=arcStepsSmallGear):
    for _ in range(times):
      self.stepper.onestep()

  def stepOrAdvance(self, timer, mod=1):
    if (timer % mod) > 0: return

    if (self.counter < self.reset_at):
      self.flip()
      self.counter = RESET_TO
    else:
      self.step()
      self.counter -= 1

    self.glyph = glyphMap[self.counter]
    print("Wheel %s: {Position: %s, Arc: %s, Voltage: %s (atIndex: %s)}" % (self.name, self.position, self.arc, self._get_voltage(), self.at_index()))

  def info(self):
    print("Wheel %s: {Arc: %s, ArcStep: %s, Offset: %s}" % (self.name, self.arc, self.position, self.offset))

  def get_glyphs(self):
    return cycle(self.map)

  def parseCommand(self, data):
    # control commands
    if data == "CALIBRATE %s" % (self.name.upper()):
      self.calibrate()
      return True
    elif data == "SAVE %s" % (self.name.upper()):
      self.saveCalibration()
      return True
    elif data == "R%s" % (self.name.upper()):
      self.reset()
      return True
    elif data == "FULL %s" % (self.name.upper()):
      self.full()
      return True
    elif data == "F%s" % (self.name.upper()):
      self.flip()
      return True
    elif data == "I%s" % (self.name.upper()):
      self.info()
      return True

    # step commands
    elif data == "%s" % (self.name.upper()):
      self.arcStep()
      return True
    elif data == "%s%s" % (self.name.upper(), self.name.upper()):
      self.full()
      return True
    elif data == "%s" % (self.name.lower()):
      self.step(times=1)
      return True

    return False
