import audiocore
import audioio
import board
import digitalio

WARNING = 300
CRITICAL = 180
FAILURE = 60

class Counter:

  def __init__(self, timer, config, critical=CRITICAL, failure=FAILURE, warning=WARNING):
    self.config = config
    self.timer = timer
    self.critical = critical
    self.failure = failure
    self.warning = warning

    self.enableAudio = config.get("sound", False)
    self.enableOutput = config.get("timerOutput", False)
    self.warning_filename =  "swan-beep.wav"
    self.alert_filename = "swan-alarm.wav"
    self.destruction_filename = "swan-destruction.wav"
    self.audio = digitalio.DigitalInOut(board.D10)
    self.audio.direction = digitalio.Direction.OUTPUT
    self.audio.value = True

  def iterate(self):
    if self.enableOutput: print("TIMER: %s" % (self.timer))

    self.evaluate_status()
    self.timer -= 1

  def evaluate_status(self):
    if self.timer <= 0:
      self.play_sound(self.destruction_filename)
      print("UNDERWORLD")

      return False
    if self.timer <= self.failure:
      self.play_sound(self.alert_filename)
      for _ in range(20): print("SYSTEM FAILURE ", end="")

    elif self.timer <= self.critical:
      self.play_sound(self.warning_filename)
      print("SYSTEM CRITICAL")

    elif self.timer <= self.warning:
      if (self.timer % 2): self.play_sound(self.warning_filename)
      print("SYSTEM WARNING")

    return True

  def play_sound(self, filename):
    print("playing %s" % (filename))

    if (self.enableAudio):
      with audioio.AudioOut(board.A0) as audio:
        sfx_file = open(filename, "rb")
        wave = audiocore.WaveFile(sfx_file)

        audio.play(wave)
        while audio.playing:
            pass