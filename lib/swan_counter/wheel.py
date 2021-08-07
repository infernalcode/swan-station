from lib.adafruit_motor.stepper import FORWARD, SINGLE, DOUBLE, INTERLEAVE
import math
import re

from analogio import AnalogIn

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

GLYPH_MAP = [HAND, BREAD, MAN, STAPLE, STICK, BIRD, FEATHER, SPIRAL, CLOTH, BLANK, NINE, EIGHT, SEVEN, SIX, FIVE, FOUR, THREE, TWO, ONE, ZERO]

class Wheel:
  # motor details
  stepAngle = 1.8                    # per NEMA 17 datasheet
  stepsPerRotation = 360 / stepAngle # per NEMA 17 datasheet, 200 steps per rotation
  rotationsPerGear = 2               # smaller gear needs 2 rotations for full rotation on large gear

  totalArc = len(GLYPH_MAP)
  stepsPerArc = stepsPerRotation / totalArc          # should be 10
  arcStepsSmallGear = stepsPerArc * rotationsPerGear # should be 20

  def __init__(self, name, stepper, pin, settings, config, startAt=NINE, resetAt=HAND):
    self.name = name
    self.stepper = stepper
    self.pin = pin
    self.config = config
    self.settings = Settings.parse(settings)

    self.enableDebug = self.config.get("debug", False)

    self.startAt = startAt
    self.resetAt = resetAt

    self.offset = self.settings.defaultOffset
    self.glyph = self.startAt

    self.calibrateStart = BLANK
    self.counter = self.calibrateStart

  def _get_voltage(self):
    pin = AnalogIn(self.pin)
    voltage = (pin.value * 3.3) / 65536
    pin.deinit()
    return voltage

  def getName(self):
    return self.name.upper()

  def _get_glyph(self):
    return GLYPH_MAP[self.glyph]

  def at_index(self):
    return self._get_voltage() > self.settings.voltageThreshold

  def calibrate(self, value):
    self.counter = value
    self.glyph = value
    self.saveCalibration()

  def saveCalibration(self):
    self.offset = 0
    self.info()

  def reset(self, withOffset=True):
    while True:
      if self.at_index(): return
      self.step()

  def flip(self):
    self.stepTo(self.startAt)

  def full(self):
    self.step(times=Wheel.arcStepsSmallGear * Wheel.totalArc)

  def glyphStep(self):
    self.step(times=self.arcStepsSmallGear)
    nextGlyphIndex = (self.glyph - 1) % Wheel.totalArc
    self.glyph = nextGlyphIndex
    self.counter -= 1

  def step(self, times=1, direction=FORWARD, style=SINGLE):
    for _ in range(times):self.stepper.onestep()
    if self.enableDebug: self.info()

  def info(self):
    info = "Wheel %s: {Glyph: %s, Voltage: %s, AtIndex: %s}" % (self.name, self.glyph, self._get_voltage(), self.at_index())
    print(info)

    return info

  def get_glyphs(self):
    return cycle(GLYPH_MAP)

  def distanceTo(self, glyph):
    glyphs = cycle(GLYPH_MAP)
    if self.glyph == glyph: return 0
    distance = 1
    while self.glyph != next(glyphs): continue
    while glyph != next(glyphs): distance += 1
    return distance

  def stepTo(self, glyph):
    distance = self.distanceTo(glyph)
    self.step(times=distance * Wheel.arcStepsSmallGear)
    self.glyph = glyph

  def release(self):
    self.stepper.release()

  def parseCommand(self, data):
    # control commands
    if re.match(r"^CALIBRATE %s (\d+)" % (self.getName()), data):
      cmd = re.compile(r"^CALIBRATE %s (\d+)" % (self.getName()))
      result = cmd.search(data)
      self.calibrate(value=int(result.group(1)))

      return True, "CALIBRATING %s to value %s" % (self.getName(), result.group(1))

    elif data == "SAVE %s" % (self.getName()):
      self.saveCalibration()

      return True, "CALIBRATION SAVED FOR WHEEL %s" % (self.getName())

    elif data == "RESET %s" % (self.getName()):
      self.reset()

      return True, "RESETTING %s" % (self.getName())

    elif re.match(r"^SET %s (\d+)" % (self.getName()), data):
      cmd = re.compile(r"^SET %s (\d+)" % (self.getName()))
      result = cmd.search(data)
      self.stepTo(glyph=int(result.group(1)))

      return True, "SETTING %s (CURRENT GLYPH: %s) TO GLYPH %s" % (self.getName(), self.glyph, result.group(1))

    elif re.match(r"^D%s (\d+)" % (self.getName()), data):
      cmd = re.compile(r"^D%s (\d+)" % (self.getName()))
      result = cmd.search(data)
      distance = self.distanceTo(glyph=int(result.group(1)))

      return True, "WHEEL %s: DISTANCE FROM CURRENT %s TO %s => %s" % (self.getName(), self.glyph, result.group(1), distance)

    elif data == "F%s" % (self.getName()):
      self.flip()

      return True, "FLIPPING %s" % (self.getName())

    elif data == "I%s" % (self.getName()):
      return True, self.info()

    # step commands
    elif re.match(r"^R%s (\d+)" % (self.getName()), data):
      cmd = re.compile(r"^R%s (\d+)" % (self.getName()))
      result = cmd.search(data)
      self.step(times=int(result.group(1)))

      return True, "STEPPING %s %s TIMES" % (self.getName(), result.group(1))

    elif data == "%s" % (self.getName()):
      self.glyphStep()

      return True, "GLYPH STEP FOR WHEEL %s" % (self.getName())

    elif data == "%s%s" % (self.getName(), self.getName()):
      self.full()

      return True, "ROTATING %s FULL" % (self.getName())

    elif data == "%s" % (self.name.lower()):
      self.step(times=1)

      return True, "SINGLE STEP %s" % (self.getName())

    return False, "INVALID COMMAND"