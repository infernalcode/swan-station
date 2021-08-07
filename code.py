from adafruit_motorkit import MotorKit
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server

from lib.swan_counter.wheel import Wheel
from lib.swan_counter.counter import Counter
from lib.swan_counter.countdown import Countdown
from lib.swan_counter.server import WebConsole, Server

from config import config
from secrets import secrets

from analogio import AnalogIn
import board
import neopixel
import time

# hardware init
motor1 = MotorKit(i2c=board.I2C(), address=0x60)
motor2 = MotorKit(i2c=board.I2C(), address=0x61)
motor3 = MotorKit(i2c=board.I2C(), address=0x62)

# read settings
wheelSettings = config.get("wheels")
initializeNetwork = config.get("network")
enableStartupSound = config.get("startupSound")

# initialize wheels
wheels = [
  Wheel("A", motor1.stepper1, board.A1, wheelSettings.get("a"), config),
  Wheel("B", motor1.stepper2, board.A2, wheelSettings.get("b"), config),
  Wheel("C", motor2.stepper1, board.A3, wheelSettings.get("c"), config),
  Wheel("D", motor2.stepper2, board.A4, wheelSettings.get("d"), config),
  Wheel("E", motor3.stepper1, board.A5, wheelSettings.get("e"), config)
]

# initialize counter
counter = Counter(config)

# initialize LED
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

## START MAIN
countdown = Countdown(wheels, counter, config)

# initialize network
wsgiServer = None

if initializeNetwork:
  network = Server(secrets)
  network.ifconfig()
  if enableStartupSound: counter.playSound("startup")

  # initialize web console
  webConsole = WebConsole(countdown)
  server.set_interface(network.esp)

  webConsole.on("POST", "/command", webConsole.command)

  wsgiServer = server.WSGIServer(80, application=webConsole)
  wsgiServer.start()

# disable light for countdown
status_light.fill((0, 0, 0))

countdown.execute(wsgiServer)

## MAIN LOOP
while True:
  if initializeNetwork:
    try:
      wsgiServer.update_poll()
    except:
      print("WSGI server update failed")

  countdown.iterate()

  time.sleep(1)
