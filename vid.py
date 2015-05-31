# coding: utf-8
import numpy as np
import cv2
import os
import sys
import serial
import socket

from collections import namedtuple


MaskMode = namedtuple('MaskMode', ('low', 'high'))
Masks = namedtuple('Masks', ('normal', 'inverted'))

config = {
    'camera_id': 1,
    'frame_width': 1280,
    'frame_height': 720,
    'stdout': False,
    'show_image': True,
    'show_mask': False,
    'show_result': True,
    'show_controls': False,
    'save_image': True,
    'save_result': True,
    'morph_transform_mask': (cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)),
    'arduino_connection': 'serial',  #'ethernet',
    'arduino_connection_configuration': {
        'dev': '/dev/ttyACM0',
        'baud': 9600,
        #'UDP_IP': "192.168.2.100",
        #'UDP_PORT': 8888
    },
}


class Fractal(object):
    """
    mode is 'mask' when it should appear within a mask. 'floating' is when it
    should appear completely over the image.
    distance is the distance in cm where this must appear.
    data is the directory name or video file name for the fractal data.

    """
    def __init__(self, mode='mask', distance=0, data=None, height=480, width=640):
        if data is None:
            raise Exception("Data must be given: dir or video file.")
        self.mode = mode
        self.distance = distance
        self.data_src = data
        self.images = []
        self.height = height
        self.width = width
        self.current_index = 0
        self.current_image = None

    def load(self):
        #print('loading ' + self.data_src)
        for image_fname in os.listdir(self.data_src):
            fname = os.path.join(self.data_src, image_fname)
            _, file_extension = os.path.splitext(fname)
            if file_extension.lower() in ['.jpg', '.png']:
                bg_image = cv2.imread(fname)
                #print('\tloading: ' + image_fname)
                self.images.append(cv2.resize(bg_image, (self.width, self.height)))
        self.current_image = self.images[0]
        return self

    def next_image(self):
        self.current_image = self.images[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.images)
        return self.current_image

    def as_masks(self):
        """
        Return 2 masks, one with the non-black portions of the current image.
        The other one is the negation of the first.

        """
        color_range = MaskMode(low=np.array([0, 0, 0]), high=np.array([5, 5, 5]))
        mask = cv2.inRange(self.current_image, color_range.low, color_range.high)
        if config['morph_transform_mask']:
            mask = cv2.morphologyEx(mask, *config['morph_transform_mask'])
        return Masks(mask, cv2.bitwise_not(mask))


class FractalManager(object):
    def __init__(self):
        self.fractals = []
        self.index = 0

    def register(self, mode, distance, data, height=480, width=640):
        new_fractal = Fractal(mode, distance=distance, data=data, height=height, width=width).load()
        self.fractals.append(new_fractal)

    def get_current_by(self, distance):
        """
        Return the next fractal corresponding to the given distance

        """
        #print('get fractal at distance: %d' % distance)
        if distance <= 0:
            return self.fractals[0]
        i = 0
        while i < len(self.fractals) and distance > self.fractals[i].distance:
            i += 1

        if i >= len(self.fractals):
            return self.fractals[len(self.fractals)-1]
        else:
            return self.fractals[i]


source = config['camera_id']
if len(sys.argv) > 1:
    source = sys.argv[1]

cap = cv2.VideoCapture(source)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['frame_height'])
cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['frame_width'])
FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
FRAME_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

print(FRAME_HEIGHT, FRAME_WIDTH)

# Global variable that will accum with each video frame.
TIME = 0

fractals = FractalManager()
fractals.register('mask', 40, 'data/quarf/', height=FRAME_HEIGHT, width=FRAME_WIDTH)
fractals.register('floating', 70, 'data/green/', height=FRAME_HEIGHT, width=FRAME_WIDTH)
fractals.register('floating', 100, 'data/blup/', height=FRAME_HEIGHT, width=FRAME_WIDTH)
fractals.register('floating', 130, 'data/mandal/', height=FRAME_HEIGHT, width=FRAME_WIDTH)
fractals.register('floating', 160, 'data/fungi/', height=FRAME_HEIGHT, width=FRAME_WIDTH)


# Esto es para grabar los dos videos (original y tocado)
if config['save_image']:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    original_out = cv2.VideoWriter('original.avi', fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))
if config['save_result']:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    transformed_out = cv2.VideoWriter('fractalized.avi', fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))


# Estas variables de acá definen el rango actual en cada momento.
color_mode = MaskMode(low=np.array([0, 0, 69]), high=np.array([129, 118, 255]))
target_distance = 0  #Will be updated by the Arduino sensors

if config['show_controls']:
    # Acá dibujo los controles en una ventanita.
    cv2.namedWindow('controls')

    # create trackbars for color change
    def set_val_factory(arr, i):
        def set_val(x):
            arr[i] = x
        return set_val

    cv2.createTrackbar('Lower H', 'controls', color_mode.low[0], 179, set_val_factory(color_mode.low, 0))
    cv2.createTrackbar('Lower S', 'controls', color_mode.low[1], 255, set_val_factory(color_mode.low, 1))
    cv2.createTrackbar('Lower V', 'controls', color_mode.low[2], 255, set_val_factory(color_mode.low, 2))

    cv2.createTrackbar('Upper H', 'controls', color_mode.high[0], 179, set_val_factory(color_mode.high, 0))
    cv2.createTrackbar('Upper S', 'controls', color_mode.high[1], 255, set_val_factory(color_mode.high, 1))
    cv2.createTrackbar('Upper V', 'controls', color_mode.high[2], 255, set_val_factory(color_mode.high, 2))
    # #
    # def switch_toggle(x):
    #     global target_distance
    #     if x == 0:
    #         target_distance = 1
    #     elif x == 1:
    #         target_distance = 51
    #     elif x == 2:
    #         target_distance = 101
    #     elif x == 3:
    #         target_distance = 151
    #     elif x == 4:
    #         target_distance = 201
    #     elif x == 5:
    #         target_distance = 251
    #
    # # Create switch to mock distance sensor
    # switch = '0 : Quarf\n1 : Green\n2 : Blup\n3 : Mandala\n4 : Fungi'
    # cv2.createTrackbar(switch, 'controls',  0, 5, switch_toggle)


def mask_by_color(source_frame, color_mode):
    # Primero transformo los valores de cada píxel,
    # cambiando de (Blue, Green, Red) a HSV
    hsv_frame = cv2.cvtColor(source_frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, color_mode.low, color_mode.high)
    morph = config['morph_transform_mask']
    if morph:
        mask = cv2.morphologyEx(mask, *morph)

    # x = int(200 + TIME*10) % 1500
    # y = 400 + int(400*math.sin(TIME/100.0))
    # center = (x, y)
    # radius = int(math.fabs(250*math.sin(TIME/100.0)))+1
    # cv2.circle(mask, center, radius, np.ones(3)*255, -1)
    inv_mask = cv2.bitwise_not(mask)
    return Masks(mask, inv_mask)



def get_arduino_data_from_ethernet():
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    return int(data)

if config['arduino_connection'] == 'serial':
    arduino = serial.Serial(config['arduino_connection_configuration']['dev'],
                            config['arduino_connection_configuration']['baud'])
    def get_arduino_data_from_serial():
        data = 0
        try:
            data = int(arduino.readline())
        except:
            pass
        return data
    get_arduino_data = get_arduino_data_from_serial
elif config['arduino_connection'] == 'ethernet':
    UDP_IP = config['arduino_connection_configuration']['UDP_IP']
    UDP_PORT = config['arduino_connection_configuration']['UDP_PORT']
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    get_arduino_data = get_arduino_data_from_ethernet


# Loop principal. Funciona hasta que se aprieta 'q'
# Se ejecuta todo para cada frame de video.
if config['show_image']:
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)

while True:
    # Acá capturo un frame de video.
    frame_loaded, frame = cap.read()
    if frame_loaded:
        TIME += 1

        new_distance = get_arduino_data()

        if new_distance > 0:
            target_distance = new_distance
        #print(target_distance)
        fractal = fractals.get_current_by(target_distance)

        bg_image = fractal.next_image()

        if fractal.mode == 'mask':
            masks = mask_by_color(frame, color_mode)
            if config['show_mask']: cv2.imshow('mask', masks.normal)
            masked_frame = cv2.bitwise_and(frame, frame, mask=masks.inverted)
            masked_bg = cv2.bitwise_and(bg_image, bg_image, mask=masks.normal)
        else:  # quarf
            masks = fractal.as_masks()
            if config['show_mask']: cv2.imshow('mask', masks.normal)
            masked_bg = cv2.bitwise_and(bg_image, bg_image, mask=masks.inverted)
            masked_frame = cv2.bitwise_and(frame, frame, mask=masks.normal)

        result = masked_frame + masked_bg

        # Muestro los frames de video en sus ventanitas y grabo esos frames en archivos separados.
        if config['show_image']: cv2.imshow('image', frame)
        if config['show_result']: cv2.imshow('transformed', result)
        if config['save_image']: original_out.write(frame)
        if config['save_result']: transformed_out.write(result)

        if config['stdout']: sys.stdout.write(result.tostring())

        # Si se aprieta 'q' sale del loop
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break


# When everything done, release the capture
cap.release()

if config['save_image']: original_out.release()
if config['save_result']: transformed_out.release()

cv2.destroyAllWindows()
