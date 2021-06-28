class Settings:

  defaultOffset = 8
  defaultVoltageThreshold = 3.0

  def __init__(self, offset, voltageThreshold):
    self.__offset = offset
    self.__voltageThreshold = voltageThreshold

  @property
  def offset(self):
    return self.__offset

  @property
  def voltageThreshold(self):
    return self.__voltageThreshold

  @staticmethod
  def parse(settingsDict):
    offset = settingsDict.get("offset", Settings.defaultOffset)
    threshold = settingsDict.get("voltageThreshold", Settings.defaultVoltageThreshold)
    return Settings(offset=offset, voltageThreshold=threshold)