import supervisor

from .counter import Counter

class Countdown:

  def __init__(self, wheelA, wheelB, wheelC, wheelD, wheelE, config):
    self.__wheelA = wheelA
    self.__wheelB = wheelB
    self.__wheelC = wheelC
    self.__wheelD = wheelD
    self.__wheelE = wheelE

    self.__config = config
    self.__counter = Counter(self.__config.get("countdownSec", 20))

    if bool(self.__config.get("calibrateOnBoot", "false")):
      self.calibrate()

    print(">: BRUN RADZINSKY.BIN")
    print(">: ", end="")

  def calibrate(self):
    print(">: BRUN CALIBRATE.BIN")
    print(">: ", end="")

    calibration = True
    while calibration:
      if supervisor.runtime.serial_bytes_available:
        value = input().strip()

        if value == "":
            continue
        elif value == "continue":
          calibration = False
        else:
          if self.__wheelA.parseCommand(value): print(">: ", end="")
          elif self.__wheelB.parseCommand(value): print(">: ", end="")
          elif self.__wheelC.parseCommand(value): print(">: ", end="")
          elif self.__wheelD.parseCommand(value): print(">: ", end="")
          elif self.__wheelE.parseCommand(value): print(">: ", end="")
          else:
            print("COMMAND NOT FOUND: %s" % (value))
            print(">: ", end="")

  def iterate(self):
    self.__wheelA.stepOrAdvance(self.__counter.timer, mod=1)
    self.__wheelB.stepOrAdvance(self.__counter.timer, mod=10)
    self.__wheelC.stepOrAdvance(self.__counter.timer, mod=60)
    self.__wheelD.stepOrAdvance(self.__counter.timer, mod=600)
    self.__wheelE.stepOrAdvance(self.__counter.timer, mod=3600)

    self.__counter.iterate()