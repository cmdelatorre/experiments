# The Gallery class abstracts an iterator over images. It provides a method to
# mix/merge/blend the current image into another given image.
# The Gallery class can be subclassed to provide images from a directory, from a
# video file, they can be automatically generated, etc.
#
# A GalleriesManager registers Gallery instances and implements a policy to
# decide which Gallery to return when get_gallery() is called. Such policy is
# implemented by using Sensors data.
# By sub-classing the GalleriesManager class, different gallery-selection
# policies can be implemented and different sensors can be used.
# The current implementation of the GalleriesManager defines a validity range
# for each registered Gallery. It uses a DistanceSensor instance to get a
# distance value and select a Gallery based on it.
#
# The Sensor class abstracts a data-input mechanism. Currently, the
# DistanceSensor reads data from the Serial port where an Arduino board sends
# distance data.


class Gallery(object):
    def __init__(self, *args, **kwargs):
        pass

    def merge(self, image):
        pass


class Sensor(object):
    pass

    def get_data(self):
        pass


class GalleriesManager(object):
    def __init__(self):
        pass

    def register(self, gallery, *args, **kwargs):
        pass

    def get_gallery(self):
        pass
