from analogio import AnalogIn
from random import randrange

# import atexit
import board
import re
import supervisor
import time

from .wheel import BLANK, CLOTH, SPIRAL, FEATHER, BIRD, STICK, HAND

VALENZETTI_EQUATION = "4 8 15 16 23 42"

class Countdown:

  def __init__(self, wheels, counter, config):
    print(">: INITIALIZING SWAN STATION COUNTDOWN SYSTEM")

    self.__wheels = wheels
    self.__config = config
    self.__counter = counter
    self.__calibrationMode = self.__config.get("calibrateOnBoot", False)
    self.__enableNetwork = self.__config.get("network", False)

    #atexit.register(self.shutdown)
    supervisor.disable_autoreload()

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
        try:
          webConsole.update_poll()
        except:
          print("WSGI server update failed")

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
          self.setWheels(result.group(5), result.group(4), result.group(3), result.group(2), result.group(1))

        elif re.match(r"^CAL (\d+):(\d+):(\d+):(\d+):(\d+)", command):
          cmd = re.compile(r"^CAL (\d+):(\d+):(\d+):(\d+):(\d+)")
          result = cmd.search(command)
          self.__wheels[0].parseCommand("CALIBRATE A %s" % result.group(5))
          self.__wheels[1].parseCommand("CALIBRATE B %s" % result.group(4))
          self.__wheels[2].parseCommand("CALIBRATE C %s" % result.group(3))
          self.__wheels[3].parseCommand("CALIBRATE D %s" % result.group(2))
          self.__wheels[4].parseCommand("CALIBRATE E %s" % result.group(1))
          self.reset()
          self.prompt()

        else:
          result = self.parseCommand(value)
          self.prompt()

  def calibrateBlank(self):
    for wheel in self.__wheels:
        r, o = wheel.parseCommand("CALIBRATE %s 10" % wheel.getName())

  def parseCommand(self, command):
    if command == VALENZETTI_EQUATION:
      self.__counter.reset()
      self.setTimer()
      return "CLEAR"

    elif command == "STATUS":
      return self.status()

    elif command == "CALIBRATE":
      return self.calibrateBlank()

    elif command == "UNDERWORLD":
      return self.__counter.resetTimer(-10)

    elif command == "TIMER":
      return self.__counter.getTimerValue()

    elif command == "PAUSE":
      self.__counter.halt()
      return "TIMER PAUSED"

    elif command == "RESUME":
      self.__counter.resume()
      return "TIMER RESUMED"

    elif command == "LOCKDOWN":
      self.__counter.playSound("lockdown")
      self.prompt()

    elif re.match(r"^SET (\d+)", command):
      cmd = re.compile(r"^SET (\d+)")
      result = cmd.search(command)
      self.__counter.resetTimer(result.group(1))

    elif re.match(r"^CAL (\d+):(\d+):(\d+):(\d+):(\d+)", command):
      cmd = re.compile(r"^CAL (\d+):(\d+):(\d+):(\d+):(\d+)")
      result = cmd.search(command)
      self.__wheels[0].parseCommand("CALIBRATE A %s" % result.group(5))
      self.__wheels[1].parseCommand("CALIBRATE B %s" % result.group(4))
      self.__wheels[2].parseCommand("CALIBRATE C %s" % result.group(3))
      self.__wheels[3].parseCommand("CALIBRATE D %s" % result.group(2))
      self.__wheels[4].parseCommand("CALIBRATE E %s" % result.group(1))
      self.reset()
      self.prompt()

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

  def setWheels(self, secondDigit, tenSecondDigit, minuteDigit, tenMinuteDigit, hundredMinuteDigit):
    self.__wheels[0].stepTo(int(secondDigit))
    self.__wheels[1].stepTo(int(tenSecondDigit))
    self.__wheels[2].stepTo(int(minuteDigit))
    self.__wheels[3].stepTo(int(tenMinuteDigit))
    self.__wheels[4].stepTo(int(hundredMinuteDigit))

  def underworld(self):
    self.setWheels(STICK, BIRD, FEATHER, SPIRAL, CLOTH)

  def reset(self):
    self.setWheels(BLANK, BLANK, BLANK, BLANK, BLANK)

  def setTimer(self):
    if (self.__counter.getSeconds() > 0):
      digitsMinutes, digitsSeconds = self.__counter.getDigits()
      self.setWheels(digitsSeconds[1], digitsSeconds[0], digitsMinutes[2], digitsMinutes[1], digitsMinutes[0])
    else:
      if (self.__counter.getSeconds() > -10):
        self.setWheels(randrange(CLOTH, HAND), randrange(CLOTH, HAND), randrange(CLOTH, HAND), randrange(CLOTH, HAND), randrange(CLOTH, HAND))
      else:
        self.underworld()

  def iterate(self):
    self.__counter.iterate(callback=self.setTimer)

  def shutdown(self):
    for wheel in self.__wheels:
      wheel.release()