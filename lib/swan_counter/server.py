from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

import board
import busio
from digitalio import DigitalInOut
import json as json_module
import os

class Server:
  def __init__(self, secrets):
    print(">: INITIALIZING NETWORK")
    esp32_cs = DigitalInOut(board.D13)
    esp32_ready = DigitalInOut(board.D11)
    esp32_reset = DigitalInOut(board.D12)

    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    self.__esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    requests.set_socket(socket, self.__esp)

    while not self.__esp.is_connected:
      try:
        self.__esp.connect_AP(secrets["ssid"], secrets["password"])
      except RuntimeError as e:
        print("  NETWORK UNABLE TO INITIALIZE, RETRYING:", str(e).upper())
        continue

  @property
  def esp(self):
    return self.__esp

  def ifconfig(self):
    print("  NETWORK CONNECTED: %s, RSSI: %s" % (str(self.__esp.ssid, "utf-8"), self.__esp.rssi))
    print("  IPV4: %s" % (self.__esp.pretty_ip(self.__esp.ip_address)))

class WebConsole:

  INDEX = "/index.html"
  CHUNK_SIZE = 8912  # max number of bytes to read at once when reading files

  def __init__(self, countdown, static_dir="/static", debug=False):
    self.countdown = countdown
    self._debug = debug
    self._listeners = {}
    self._start_response = None
    self._static = static_dir
    if self._static:
      self._static_files = ["/" + file for file in os.listdir(self._static)]

  def __call__(self, environ, start_response):
    """
    Called whenever the server gets a request.
    The environ dict has details about the request per wsgi specification.
    Call start_response with the response status string and headers as a list of tuples.
    Return a single item list with the item being your response data string.
    """
    if self._debug:
      self._log_environ(environ)

    self._start_response = start_response
    status = ""
    headers = []
    resp_data = []

    key = self._get_listener_key(
      environ["REQUEST_METHOD"].lower(), environ["PATH_INFO"]
    )
    if key in self._listeners:
      status, headers, resp_data = self._listeners[key](environ)
    if environ["REQUEST_METHOD"].lower() == "get" and self._static:
      path = environ["PATH_INFO"]
      if path in self._static_files:
        status, headers, resp_data = self.serve_file(
          path, directory=self._static
        )
      elif path == "/" and self.INDEX in self._static_files:
        status, headers, resp_data = self.serve_file(
          self.INDEX, directory=self._static
        )

    self._start_response(status, headers)
    return resp_data

  def on(self, method, path, request_handler):
    """
    Register a Request Handler for a particular HTTP method and path.
    request_handler will be called whenever a matching HTTP request is received.

    request_handler should accept the following args:
      (Dict environ)
    request_handler should return a tuple in the shape of:
      (status, header_list, data_iterable)

    :param str method: the method of the HTTP request
    :param str path: the path of the HTTP request
    :param func request_handler: the function to call
    """
    self._listeners[self._get_listener_key(method, path)] = request_handler

  def serve_file(self, file_path, directory=None):
    status = "200 OK"
    headers = [("Content-Type", self._get_content_type(file_path))]

    full_path = file_path if not directory else directory + file_path

    def resp_iter():
      with open(full_path, "rb") as file:
        while True:
          chunk = file.read(self.CHUNK_SIZE)
          if chunk:
            yield chunk
          else:
            break

    return (status, headers, resp_iter())

  def _log_environ(self, environ):
    print("environ map:")
    for name, value in environ.items():
      print(name, value)

  def _get_listener_key(self, method, path):
    return "{0}|{1}".format(method.lower(), path)

  def _get_content_type(self, file):
    ext = file.split(".")[-1]
    if ext in ("html", "htm"):
      return "text/html"
    if ext == "js":
      return "application/javascript"
    if ext == "css":
      return "text/css"
    if ext in ("jpg", "jpeg"):
      return "image/jpeg"
    if ext == "png":
      return "image/png"
    return "text/plain"

  def command(environ):
      json = json_module.loads(environ["wsgi.input"].getvalue())
      #result = self.countdown.parseCommand(json)
      result = "doing something"
      return ("200 OK", [], result)