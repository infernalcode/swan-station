import supervisor

from .counter import Counter

class Countdown:

  def __init__(self, wheelA, wheelB, wheelC, wheelD, wheelE, config):
    print(">: INITIALIZING SWAN STATION COUNTDOWN SYSTEM")

    self.__wheelA = wheelA
    self.__wheelB = wheelB
    self.__wheelC = wheelC
    self.__wheelD = wheelD
    self.__wheelE = wheelE

    self.__config = config
    self.__counter = Counter(self.__config.get("countdownSec", 20), config)

    if self.__config.get("calibrateOnBoot", False):
      self.calibrate()

  def calibrate(self):
    print(">: BRUN CALIBRATE.BIN")

    calibration = True
    while calibration:
      if supervisor.runtime.serial_bytes_available:
        value = input().strip()

        if value == "":
            continue
        elif value == "CONTINUE" or value == "C":
          calibration = False
        else:
          result = self.parseCommand(value)
          print(result)
          print(">: ", end="")

  def parseCommand(self, command):
    if self.__wheelA.parseCommand(command): return
    elif self.__wheelB.parseCommand(command): return
    elif self.__wheelC.parseCommand(command): return
    elif self.__wheelD.parseCommand(command): return
    elif self.__wheelE.parseCommand(command): return
    else:
      return "COMMAND NOT FOUND: %s" % (command)

  def execute(self):
    print(">: BRUN RADZINSKY.BIN")
    print(">: ", end="")

  def iterate(self):
    self.__wheelA.stepOrAdvance(self.__counter.timer, mod=1)
    self.__wheelB.stepOrAdvance(self.__counter.timer, mod=10)
    self.__wheelC.stepOrAdvance(self.__counter.timer, mod=60)
    self.__wheelD.stepOrAdvance(self.__counter.timer, mod=600)
    self.__wheelE.stepOrAdvance(self.__counter.timer, mod=3600)

    self.__counter.iterate()