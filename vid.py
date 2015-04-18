# coding: utf-8
import numpy as np
import cv2
import os
import sys
import math

from collections import namedtuple

MaskMode = namedtuple('MaskMode', ('low', 'high'))
Masks = namedtuple('Masks', ('normal', 'inverted'))

config = {
    'camera_id': 1,
    'frame_width': 1920,
    'frame_height': 1080,
    'show_image': False,
    'show_mask': False,
    'show_result': True,
    'show_controls': True,
    'save_image': False,
    'save_result': False,
    'morph_transform_mask': (cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)),
}

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

fungi_images = []
for image_fname in os.listdir('fungi'):
    bg_image = cv2.imread(os.path.join('fungi', image_fname))
    fungi_images.append(cv2.resize(bg_image, (FRAME_WIDTH, FRAME_HEIGHT)))

quarf_images = []
for image_fname in os.listdir('quarf'):
    bg_image = cv2.imread(os.path.join('quarf', image_fname))
    quarf_images.append(cv2.resize(bg_image, (FRAME_WIDTH, FRAME_HEIGHT)))



step = +1
step_delay = 0
delay_factor = 1

fungi_index = 0
def get_current_fungi():
    global fungi_index, step, step_delay
    current_image = fungi_images[fungi_index]
    step_delay = (step_delay + 1) % delay_factor
    if step_delay == 0:
        fungi_index = (fungi_index + step) % len(fungi_images)
    return current_image

quarf_index = 0
def get_current_quarf():
    global quarf_index, step, step_delay
    current_image = quarf_images[quarf_index]
    step_delay = (step_delay + 1) % delay_factor
    if step_delay == 0:
        quarf_index = (quarf_index + step) % len(quarf_images)
    return current_image

# Esto es para grabar los dos videos (original y tocado)
if config['save_image']:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    original_out = cv2.VideoWriter('original.avi', fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))
if config['save_result']:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    transformed_out = cv2.VideoWriter('fractalized.avi', fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))


# Estas variables de acá definen el rango actual en cada momento.
color_mode = MaskMode(low=np.array([38, 0, 0]), high=np.array([82, 255, 255]))
fractal_mode = 'fungi'  # Otra opción es quarf

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


    def switch_toggle(x):
        global fractal_mode
        if x == 0:
            fractal_mode = 'fungi'
        else:
            fractal_mode = 'quarf'
        print(x, fractal_mode)

    # create switch for ON/OFF functionality
    switch = '0 : Fungi \n1 : Quarf'
    cv2.createTrackbar(switch, 'controls',  0, 1, switch_toggle)


def find_quarf(source_frame, color_mode):
    # Primero transformo los valores de cada píxel,
    # cambiando de (Blue, Green, Red) a HSV
    hsv_frame = cv2.cvtColor(source_frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, color_mode.low, color_mode.high)
    morph = config['morph_transform_mask']
    if morph:
        mask = cv2.morphologyEx(mask, *morph)

    x = int(200 + TIME*10) % 1500
    y = 400 + int(400*math.sin(TIME/100.0))
    center = (x, y)
    radius = int(math.fabs(250*math.sin(TIME/100.0)))+1
    cv2.circle(mask, center, radius, np.ones(3)*255, -1)
    # Acá creo una copia invertida de la máscara.
    inv_mask = cv2.bitwise_not(mask)
    if fractal_mode:
        aux = mask
        mask = inv_mask
        inv_mask = aux

    return Masks(mask, inv_mask)


def find_fungi(current_image):
    color_range = MaskMode(low=np.array([0, 0, 0]), high=np.array([5, 5, 5]))
    mask = cv2.inRange(current_image, color_range.low, color_range.high)
    if config['morph_transform_mask']:
        mask = cv2.morphologyEx(mask, *config['morph_transform_mask'])
    return Masks(mask, cv2.bitwise_not(mask))


# Loop principal. Funciona hasta que se aprieta 'q'
# Se ejecuta todo para cada frame de video.
while True:
    # Acá capturo un frame de video.
    frame_loaded, frame = cap.read()
    if frame_loaded:
        TIME += 1
        if fractal_mode == 'fungi':
            bg_image = get_current_fungi()
            r = 300
            n = 100
            x, y = (math.cos(2*math.pi/n * TIME)*r, math.sin(2*math.pi/n*TIME)*r)

            translation = np.float32([[1, 0, x], [0, 1, y]])
            bg_image = cv2.warpAffine(bg_image, translation, (FRAME_WIDTH, FRAME_HEIGHT))
            masks = find_fungi(bg_image)
            if config['show_mask']: cv2.imshow('mask', masks.normal)
            masked_bg = cv2.bitwise_and(bg_image, bg_image, mask=masks.inverted)
            masked_frame = cv2.bitwise_and(frame, frame, mask=masks.normal)
        else:  # quarf
            masks = find_quarf(frame, color_mode)
            if config['show_mask']: cv2.imshow('mask', masks.normal)
            masked_frame = cv2.bitwise_and(frame, frame, mask=masks.inverted)
            bg_image = get_current_quarf()
            masked_bg = cv2.bitwise_and(bg_image, bg_image, mask=masks.normal)

        result = masked_frame + masked_bg

        # Muestro los frames de video en sus ventanitas y grabo esos frames en archivos separados.
        if config['show_image']: cv2.imshow('image', frame)
        if config['show_result']: cv2.imshow('transformed', result)
        if config['save_image']: original_out.write(frame)
        if config['save_result']: transformed_out.write(result)

        # Si se aprieta 'q' sale del loop
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break


# When everything done, release the capture
cap.release()

if config['save_image']: original_out.release()
if config['save_result']: transformed_out.release()

cv2.destroyAllWindows()
