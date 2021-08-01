import supervisor
import time

from analogio import AnalogIn
import board

from .counter import Counter

DEFAULT_COUNTDOWN_TIME = 6480

class Countdown:

  def __init__(self, wheels, config):
    print(">: INITIALIZING SWAN STATION COUNTDOWN SYSTEM")

    self.__wheels = wheels
    self.__config = config
    self.__counter = Counter(self.__config.get("countdownSec", DEFAULT_COUNTDOWN_TIME), config)
    self.__engageFlaps = self.__config.get("flaps", True)

    if self.__config.get("calibrateOnBoot", False):
      self.calibrate()

  def calibrate(self):
    print(">: LOAD CALIBRATE.1")
    print(">: RUN CALIBRATE.1")
    print(">: ", end="")

    calibration = True
    while calibration:
      if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        command = value.upper()

        if value == "":
            continue
        elif command == "STATUS":
          self.status()
          self.prompt()

        elif command == "WATCH":
          while True:
            self.status()
            time.sleep(1)

        elif command == "PINS":
          while True:
            self.monitorPins()
            time.sleep(1)

        elif command == "SAVE":
          calibration = False
          # save the offset to storage for future runs
        else:
          result = self.parseCommand(value)
          self.prompt()

  def parseCommand(self, command):
    for wheel in self.__wheels:
      result, output = wheel.parseCommand(command)

      if result:
        return output

    return "COMMAND NOT FOUND: %s" % (command)

  def status(self):
    for wheel in self.__wheels:
      wheel.info()
    print(" ")

  def prompt(self):
    print(">: ", end="")

  def execute(self):
    print(">: LOAD RADZINSKY.1")
    print(">: RUN RADZINSKY.1")
    print(">: ", end="")

  def monitorPins(self):
    # debug code
    pins = [board.A1, board.A2, board.A3, board.A4, board.A5]

    for pin in pins:
      p = AnalogIn(pin)
      print("%s: %f" % (pin, p.value))
      p.deinit()
    print(" ")

  def iterate(self):
    if self.__engageFlaps:
      for wheel in self.__wheels:
        wheel.stepOrAdvance(self.__counter.timer)

    self.__counter.iterate()