import audioio
import audiomp3
import board
import digitalio

from .wheel import BLANK, ZERO

WARNING = 240
CRITICAL = 60
FAILURE = 10

class Counter:

  def __init__(self, timer, config, critical=CRITICAL, failure=FAILURE, warning=WARNING):
    self.config = config
    self.timer = timer
    self.critical = critical
    self.failure = failure
    self.warning = warning

    self.enableAudio = config.get("sound", False)
    self.enableOutput = config.get("timerOutput", False)

    self.audioLibrary = {
      "alarm": open("audio/swan-alarm.mp3", "rb"),
      "alarm-double": open("audio/swan-alarm-double.mp3", "rb"),
      "beep": open("audio/swan-beep.mp3", "rb"),
      "lockdown": open("audio/swan-lockdown.mp3", "rb"),
      "failure": open("audio/swan-system-failure.mp3", "rb")
    }

    self.mp3Decoder = audiomp3.MP3Decoder(self.audioLibrary["beep"])

    self.audio = digitalio.DigitalInOut(board.D10)
    self.audio.direction = digitalio.Direction.OUTPUT
    self.audio.value = True

  def iterate(self, func):
    if self.enableOutput: print("TIMER: %s" % (self.timer))
    self.evaluate_status(func)

# At the 4 minute mark, a steady alarm beep signal/ed and continued for the next 3 minutes.
# At the 1-minute mark, an intense alarm signalled and continued for the next 50 seconds.
# At the 10-second mark, for 20 seconds, the same alarm signalled at a much faster rate.
# During the last 10 seconds, Egyptian hieroglyphs flipped in position of the timer numbers.
# At the end of the 10 seconds, the alarm stopped and all the hieroglyphs were locked in.
# The alarm signal was immediately replaced by a recorded voice repeating: "System Failure".
# The sound of a power build-up was immediately heard, which led to the rest of the system failure effects.

  def evaluate_status(self):
    if self.timer <= 0:
      self.playSound("failure")
      for _ in range(20): print("SYSTEM FAILURE ", end="")
      return False

    if self.timer <= self.failure:
      self.playSound("alarm-double")
      print("SYSTEM CRITICAL")

    elif self.timer <= self.critical:
      if (self.timer % 2): self.playSound("alarm")
      print("SYSTEM WARNING")

    elif self.timer <= self.warning:
      if (self.timer % 4): self.playSound("beep")

    return True

  def playSound(self, filename, func=lambda: {}):
    if (self.enableAudio):
      file = self.audioLibrary[filename]
      with audioio.AudioOut(board.A0) as audio:
        self.mp3Decoder.file = file
        audio.play(self.mp3Decoder)

        while audio.playing:
          func
          pass

  def decrement(self):
    self.timer -= 1

  def getSeconds(self):
    return self.timer

  def getDigits(self):
    minutes, seconds = divmod(self.timer, 60)

    digitsMinutes = list(str(minutes))
    digitsSeconds = list(str(seconds))

    # pad the display with zero values when it makes sense
    if (len(digitsMinutes) == 1):
      digitsMinutes = [ZERO, ZERO, digitsMinutes.pop()]

    if (len(digitsMinutes) == 2):
      digitsMinutes = [ZERO, digitsMinutes.pop(), digitsMinutes.pop()]

    if (len(digitsSeconds) == 1):
      digitsSeconds = [ZERO, digitsSeconds.pop()]

    return digitsMinutes, digitsSeconds