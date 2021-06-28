import math

from adafruit_itertools import cycle
from micropython import const

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

RESET_AT = ZERO
RESET_TO = NINE

glyphMap = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, BLANK, CLOTH, SPIRAL, FEATHER, BIRD, STICK, STAPLE, MAN, BREAD, HAND]

class Wheel:
  # motor details
  stepAngle = 1.8                    # per NEMA 17 datasheet
  stepsPerRotation = 360 / stepAngle # per NEMA 17 datasheet, 200 steps per rotation

  totalArc = len(glyphMap)
  stepsPerArc = stepsPerRotation / totalArc   # How many steps to move to the next flap
  stepsPerArc = 20

  def __init__(self, name, stepper, pin, offset):
    self.name = name
    self.stepper = stepper
    self.pin = pin
    self.offset = offset

    self.counter = RESET_TO
    self.glyph = glyphMap[self.counter]
    self.reset_at = RESET_AT
    self.stepper.release()

  def _get_voltage(self):
    return (self.pin.value * 3.3) / 65536

  def at_index(self):
    return self._get_voltage() > 3.0

  def calibrate(self):
    if not self.at_index(): self.reset()

  def reset(self):
    while True:
      if self.at_index():
        self.step(self.offset)
        return
      self.step(4)

  def flip(self):
    steps = Wheel.stepsPerArc * (len(glyphMap)/2)
    self.step(steps)

  def step(self, times=stepsPerArc):
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
    print("Wheel %s: Timer: %s, Glpyh: %s, Counter: %s, Voltage: %s (atIndex: %s, +offset: %s)" % (self.name, timer, self.glyph, self.counter, self._get_voltage(), self.at_index(), self.offset))

  def get_glyphs(self):
    return cycle(self.map)
