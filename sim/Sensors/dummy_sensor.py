"""A dummy sensor for testing and creating a sensor"""

from sim.sensors.sensor import Sensor, SensorType
from sim.utils.builder import BuilderTemplate


class DummySensorBuilder(BuilderTemplate):
    """Basic builder to construct a DummySensor"""

    def __init__(self):
        self._dummy_sensor = DummySensor()
        self._id = 1
        self._name = "dummy"

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def _reset(self):
        self._dummy_sensor = DummySensor()
        self._id = 1
        self._name = "dummy"

    # TODO: Render this thing :)

    def build(self):
        product = self._dummy_sensor
        self._reset()
        return product


class DummySensor(Sensor):
    """_summary_
    A dummy sensor that contains all the things to make a sensor... but no special functions

    Args:
        Sensor (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.type = SensorType.DUMMY
        self.name = "dummy"
