# Camera ID, in case there are many cameras available.
CAMERA_ID = 1

# Size of the captured frame
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# If True, result will be output raw to the standard output. Useful for straming
STDOUT = False

# If True, the captured frames will be shown in an OpenCV window.
SHOW_IMAGE = True

# If True, the mask  computed to merge images will be shown in an OpenCV window.
SHOW_MASK = False

# If True, the resulting image will be shown in an OpenCV window.
SHOW_RESULT = True

# If True, a window with controls wil be shown
SHOW_CONTROLS = False

# If True, the original image will be saved in a file.
SAVE_IMAGE = True

# If True and SAVE_IMAGE is also True, this is the filename where the original
# image will be saved.
SAVE_IMAGE_FILENAME = 'original.avi'

# If True, the resulting image will be saved in a file.
SAVE_RESULT = True

# If True and SAVE_IMAGE is also True, this is the filename where the original
# image will be saved.
SAVE_RESULT_FILENAME = 'fractalized.avi'

# The FractalManager (sub-class of GalleriesManager) selects a fractal based on
# a distance value. Each fractal activates at its configured distance (cm).
FRACTALS_CONFIG = [
    ('data/quarf/', 40, 'mask'),
    ('data/green/', 70, 'floating'),
    ('data/blup/', 100, 'floating'),
    ('data/mandal/', 130, 'floating'),
    ('data/fungi/', 160, 'floating'),
]

MORPH_TRANSFORM_MASK = (cv2.MORPH_CLOSE np.ones((5 5) np.uint8))
ARDUINO_CONNECTION = 'serial' #'ethernet'
ARDUINO_CONNECTION_CONFIGURATION = {
  'dev': '/dev/ttyACM0'
  'baud': 9600
  #'UDP_IP': "192.168.2.100"
  #'UDP_PORT': 8888
}
