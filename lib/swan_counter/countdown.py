import supervisor
from random import randrange
import re
import time

from analogio import AnalogIn
import audioio
import audiomp3
import digitalio
import audiocore

import board

from .counter import Counter
from .wheel import BLANK, CLOTH, SPIRAL, FEATHER, BIRD, STICK, HAND

DEFAULT_COUNTDOWN_TIME = 6480

class Countdown:

  def __init__(self, wheels, config):
    print(">: INITIALIZING SWAN STATION COUNTDOWN SYSTEM")

    self.__wheels = wheels
    self.__config = config
    self.__counter = Counter(self.__config.get("countdownSec", DEFAULT_COUNTDOWN_TIME), config)
    self.__calibrationMode = self.__config.get("calibrateOnBoot", False)
    self.__enableNetwork = self.__config.get("network", False)

  def prompt(self):
    print(">: ", end="")

  def execute(self, webConsole):
    if self.__calibrationMode:
      self.calibrate(webConsole)

    print(">: LOAD RADZINSKY.1")
    print(">: RUN RADZINSKY.1")
    self.prompt()

  def calibrate(self, webConsole):
    print(">: LOAD CALIBRATE.1")
    print(">: RUN CALIBRATE.1")
    print("  ADVANCE ALL SPLIT FLAP DISPLAYS TO THE BLANK TILE AND TYPE 'SAVE' TO CONTINUE")
    self.prompt()

    while self.__calibrationMode:
      if self.__enableNetwork:
        webConsole.update_poll()

      if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        command = value.upper()

        if value == "":
            continue

        elif command == "WATCH":
          while True:
            self.status()
            time.sleep(1)

        elif command == "PINS":
          while True:
            self.monitorPins()
            time.sleep(1)

        elif command == "FAILURE":
          self.__counter.playSound("failure")
          self.prompt()

        elif command == "LOCKDOWN":
          self.__counter.playSound("lockdown")
          self.prompt()

        elif command == "BEEP":
          self.__counter.playSound("beep")
          self.prompt()

        elif re.match(r"^SET (\d)(\d)(\d):(\d)(\d)", command):
          cmd = re.compile(r"^SET (\d)(\d)(\d):(\d)(\d)")
          result = cmd.search(command)
          self.setTimer(result.group(5), result.group(4), result.group(3), result.group(2), result.group(1))

        else:
          result = self.parseCommand(value)
          self.prompt()

  def calibrateBlank(self):
    for wheel in self.__wheels:
        r, o = wheel.parseCommand("CALIBRATE %s 10" % wheel.getName())

  def parseCommand(self, command):
    if command == "STATUS":
      return self.status()

    elif command == "CALIBRATE":
      return self.calibrateBlank()

    elif command == "UNDERWORLD":
      return self.underworld()

    elif command == "SAVE":
      self.__calibrationMode = False
      result, output = False, ""
      self.calibrateBlank()
      return "CALIBRATION SAVED"

    for wheel in self.__wheels:
      result, output = wheel.parseCommand(command)

      if result:
        return output

    return "COMMAND NOT FOUND: %s" % (command)

  def status(self):
    status = ""
    for wheel in self.__wheels:
      status += wheel.info() + "\n"
    print(" ")

    return status

  def monitorPins(self):
    # debug code
    pins = [board.A1, board.A2, board.A3, board.A4, board.A5]

    for pin in pins:
      p = AnalogIn(pin)
      print("%s: %f" % (pin, p.value))
      p.deinit()
    print(" ")

  def setTimer(self, secondDigit, tenSecondDigit, minuteDigit, tenMinuteDigit, hundredMinuteDigit):
    self.__wheels[0].stepTo(int(secondDigit))
    self.__wheels[1].stepTo(int(tenSecondDigit))
    self.__wheels[2].stepTo(int(minuteDigit))
    self.__wheels[3].stepTo(int(tenMinuteDigit))
    self.__wheels[4].stepTo(int(hundredMinuteDigit))

  def underworld(self):
    self.setTimer(STICK, BIRD, FEATHER, SPIRAL, CLOTH)

  def reset(self):
    self.setTimer(BLANK, BLANK, BLANK, BLANK, BLANK)

  def iterate(self):

    self.__counter.iterate()

    if (self.__counter.getSeconds() > 0):
      digitsMinutes, digitsSeconds = self.__counter.getDigits()
      self.setTimer(digitsSeconds[1], digitsSeconds[0], digitsMinutes[2], digitsMinutes[1], digitsMinutes[0])
    else:
      if (self.__counter.getSeconds() > -10):
        self.setTimer(randrange(CLOTH, HAND), randrange(CLOTH, HAND), randrange(CLOTH, HAND), randrange(CLOTH, HAND), randrange(CLOTH, HAND))
      else:
        self.underworld()

    self.__counter.decrement()