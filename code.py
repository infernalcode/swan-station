from adafruit_motorkit import MotorKit
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server

from lib.swan_counter.wheel import Wheel
from lib.swan_counter.countdown import Countdown
from lib.swan_counter.server import WebConsole, Server

from config import config
from secrets import secrets

from analogio import AnalogIn
import board
import busio
import math
import neopixel
import time

# hardware init
motor1 = MotorKit(i2c=board.I2C(), address=0x60)
motor2 = MotorKit(i2c=board.I2C(), address=0x61)
motor3 = MotorKit(i2c=board.I2C(), address=0x62)

# read settings
wheelSettings = config.get("wheels")
initializeNetwork = config.get("network")

# initialize wheels
wheels = [
  Wheel("A", motor1.stepper1, board.A1, wheelSettings.get("a"), mod=1),
  Wheel("B", motor1.stepper2, board.A2, wheelSettings.get("b"), mod=10),
  Wheel("C", motor2.stepper1, board.A3, wheelSettings.get("c"), mod=60),
  Wheel("D", motor2.stepper2, board.A4, wheelSettings.get("d"), mod=600),
  Wheel("E", motor3.stepper1, board.A5, wheelSettings.get("e"), mod=3600)
]

# initialize LED
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

## START MAIN
countdown = Countdown(wheels, config)

# initialize network
wsgiServer = None

if initializeNetwork:
  network = Server(secrets)
  network.ifconfig()

  # initialize web console
  webConsole = WebConsole(countdown)
  server.set_interface(network.esp)

  #webConsole.on("GET", "/calibrate", calibrate)
  webConsole.on("POST", "/command", webConsole.command)

  wsgiServer = server.WSGIServer(80, application=webConsole)
  wsgiServer.start()

# disable light for countdown
status_light.fill((0, 0, 0))

countdown.execute(wsgiServer)

## MAIN LOOP
while True:
  if initializeNetwork:
    wsgiServer.update_poll()

  countdown.iterate()

  time.sleep(1)
