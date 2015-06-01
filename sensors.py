import serial


class Sensor(object):
    """Base class to represent the Sensor interface."""

    def get_data(self):
        raise NotImplementedError()


# The Sensor class abstracts a data-input mechanism. Currently, the
# DistanceSensor reads data from the Serial port where an Arduino board sends
# distance data.
class DistanceSensor(Sensor):
    def __init__(self, device, baud):
        self.arduino = serial.Serial(device, baud)

    def get_data(self):
        data = None
        try:
            # TODO: Improve this: read the last measure sent.
            data = int(self.arduino.readline())
        except:
            pass
        return data


class TestSensor(Sensor):
    """
    Returns the sequence of values from min to max, until max is reached. Then
    the inverse sequence is returned. Finally, it starts again.

    """
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val
        self.current = min_val
        self.step = 1

    def get_data(self):
        if self.current == self.min_val:
            self.step = 1
        elif self.current == self.max_val:
            self.step = -1

        self.current += self.step

        return self.current
