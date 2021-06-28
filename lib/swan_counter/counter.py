import audiocore
import audioio
import board
import digitalio

CRITICAL = 240
FAILURE = 60

class Counter:

  def __init__(self, timer, critical=CRITICAL, failure=FAILURE):
    self.timer = timer
    self.critical = critical
    self.failure = failure
    self.isCritical = False

    self.beep_filename =  "swan-beep.wav"
    self.audio = digitalio.DigitalInOut(board.D10)
    self.audio.direction = digitalio.Direction.OUTPUT
    self.audio.value = True

  def iterate(self):
    print("Counter Timer: %s" % (self.timer))

    if (self.timer % 2):
      print("beep")
      #self.play_beep()
    elif (self.isCritical):
      print("beep")
      #self.play_beep()

    self.timer -= 1
    self.isCritical = self.check_status()

  def play_beep(self):
    with audioio.AudioOut(board.A0) as audio:
      sfx_file = open(self.beep_filename, "rb")
      wave = audiocore.WaveFile(sfx_file)

      audio.play(wave)
      while audio.playing:
          pass

  def check_status(self):
    if (self.timer <= self.failure):
      for _ in range(20):
        print("SYSTEM FAILURE ", end="")
      return True
    elif (self.timer <= self.critical):
      print("SYSTEM CRITICAL")
      return True

    return False