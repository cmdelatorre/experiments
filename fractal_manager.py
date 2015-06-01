import cv2
import os
import serial

from image_processing import mask_by_pixel_value, dark_mask, masked_merge


class BlendModes:
    MASK, OVERLAY = range(2)


class FractalsDirectory(object):
    """
    Keep a sequence of images and provide a method to merge the current image
    into another one.

    """
    def __init__(self, data_src=None, mode='mask', filter_conf=None,
                 color_low=None, color_high=None):
        super(FractalsDirectory, self).__init__()
        self.data_src = data_src
        self.mode = mode
        self.images = []
        self.height = None
        self.width = None
        self.current_index = 0
        self.current_image = None
        # Merge's specific parameters
        if mode == BlendModes.MASK and (
                filter_conf is None or color_low is None or color_high is None):
            raise Exception("If fractal mode is MASK, then filter_conf, "
                            "color_low and color_high arguments must be given")
        self.filter_conf = filter_conf
        self.color_low = color_low
        self.color_high = color_high

    def set_dimensions(self, height, width):
        self.height = height
        self.width = width

    def load(self):
        """
        Load all the jpg or png images in the source directory.

        If necessary, resize to the fractal's height and width.

        """
        for image_fname in os.listdir(self.data_src):
            fname = os.path.join(self.data_src, image_fname)
            _, file_extension = os.path.splitext(fname)
            if file_extension.lower() in ['.jpg', '.png']:
                image = cv2.imread(fname)
                height, width, _ = image.shape
                if self.height is not None and height != self.height:
                    height = self.height
                if self.width is not None and width != self.width:
                    width = self.width
                self.images.append(cv2.resize(image, (width, height)))
        self.current_image = self.images[0]
        return self

    def next_image(self):
        self.current_image = self.images[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.images)
        return self.current_image

    def merge(self, image):
        fractal = self.next_image()

        if self.mode == BlendModes.MASK:
            # Transform the BGR image to the HSV color space.
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            # Create a Mask by subseting the HSV values of the image.
            mask = mask_by_pixel_value(
                hsv_image, self.color_low, self.color_high,
                filter_conf=self.filter_conf)
            invert_mask = False
        else:  # BlendModes.OVERLAY
            # Create a mask with the dark pixels of the fractal
            mask = dark_mask(fractal)
            invert_mask = True
        return masked_merge(image, fractal, mask, invert_mask=invert_mask)


def sorted_index(arr, item, delta=0):
    """
    Return the position that the item should occupy to keep the list sorted.

    Assumes that arr is a sorted list.

    """
    if len(arr) == 0:
        pos = 0
    elif len(arr) == 1:
        if item <= arr[0]:
            pos = 0
        else:
            pos = 1
    elif len(arr) == 2:
        if item <= arr[0]:
            pos = 0
        elif item <= arr[1]:
            pos = 1
        else:
            pos = 2
    else:
        ini = 0
        end = len(arr)
        mid = int((end + ini) / 2)
        if item == arr[mid]:
            pos = mid
        elif item < arr[mid]:
            pos = sorted_index(arr[ini: mid], item, delta=ini)
        else:
            pos = sorted_index(arr[mid+1: end], item, delta=mid+1)
    return pos + delta


# A FractalManager registers FractalGallery instances and implements a policy to
# decide which Fractal to return when get_current() is called.
# By sub-classing the FractalManager class, different fractal-selection
# policies can be implemented, using different inputs (sensors).
# The current implementation of the FractalManager defines a validity range
# for each registered Fractal. It uses a DistanceSensor instance to get a
# distance value and select a Fractal based on it.
class FractalManager(object):
    def __init__(self, sensor):
        super(FractalManager, self).__init__()
        # fractals and distances are two lists matched by index:
        # the i-th distance in the list corresponds to the i-th fractal
        self.fractals = []
        self.distances = []
        self.sensor = sensor
        self.current_fractal = None

    def register(self, fractal, distance, height=480, width=640):
        fractal.set_dimensions(height=height, width=width)
        fractal.load()
        pos = sorted_index(self.distances, distance)
        if pos < len(self.distances) and self.distances[pos] == distance:
            raise Exception("There's another fractal at distance %d" % distance)
        self.fractals.insert(pos, fractal)
        self.distances.insert(pos, distance)
        if self.current_fractal is None:
            self.current_fractal = fractal

    def get_current(self):
        """Return the fractal corresponding to the sensed distance."""
        distance = self.sensor.get_data()
        if distance:
            target = sorted_index(self.distances, distance)
            if target < len(self.fractals):
                self.current_fractal = self.fractals[target]
            else:  # the distance is higher than the upper limit
                self.current_fractal = self.fractals[-1]
        return self.current_fractal
