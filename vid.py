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
    'frame_width': 1600,
    'frame_height': 900,
    'show_image': False,
    'show_mask': False,
    'show_result': True,
    'show_controls': True,
    'save_image': False,
    'save_result': False,
    'morph_transform_mask': (cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)),
}

cap = cv2.VideoCapture(config['camera_id'])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['frame_height'])
cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['frame_width'])
FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
FRAME_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print(FRAME_HEIGHT, FRAME_WIDTH)

# Global variable that will accum with each video frame.
TIME = 0

# Open the background video (if given)
background_video = None
background_n_frames = None
if len(sys.argv) > 1:
    background_video = cv2.VideoCapture(sys.argv[1])
    print("Backgorund video: " + sys.argv[1])
    if not background_video.isOpened():
        background_video = None
        print("Unavailable backgorund video")
    else:
        background_n_frames = background_video.get(cv2.CAP_PROP_FRAME_COUNT)

# If no background_video given, then load images
bg_images = []
if background_video is None:
    for bg_image_fname in os.listdir('img'):
        bg_image = cv2.imread(os.path.join('img', bg_image_fname))
        bg_images.append(cv2.resize(bg_image, (FRAME_WIDTH, FRAME_HEIGHT)))


# Either with a background video or a list of images, choose the next one.
image_index = 0
step = +1
step_delay = 0
delay_factor = 1
frame_counter = 0
def get_current_image():
    global image_index, step, step_delay, frame_counter

    if background_video is not None:
        flag, f = background_video.read()
        if flag:
            current_image = f.astype(np.uint8)
            current_image = cv2.resize(current_image, (FRAME_WIDTH, FRAME_HEIGHT))
            frame_counter += 1
            if frame_counter == background_n_frames:
                frame_counter = 0 #Or whatever as long as it is the same as next line
                background_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
        if image_index == 0:
            step = +1
        elif image_index == len(bg_images)-1:
            step = -1
        current_image = bg_images[image_index]
        step_delay = (step_delay + 1) % delay_factor
        if step_delay == 0:
            image_index += step
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
invert_mode = False

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
        global invert_mode
        if x == 0:
            invert_mode = False
        else:
            invert_mode = True
        print(x, invert_mode)

    # create switch for ON/OFF functionality
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch, 'controls',  0, 1, switch_toggle)


# Del frame transformado, creo una máscara:
#  - Tiene 255 en los píxeles que están dentro del rango actual. 0 en los que no.
#    El rango actual es el valor que haya en color_low, color_high
#    Ese rango actual va cambiando de acuerdo a los controles.
#    Se puede cambiar el rango con otra cosa (arduino, etc)
def create_masks(source_frame, color_mode):
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
    if invert_mode:
        aux = mask
        mask = inv_mask
        inv_mask = aux

    return Masks(mask, inv_mask)

# Loop principal. Funciona hasta que se aprieta 'q'
# Se ejecuta todo para cada frame de video.
while True:
    # Acá capturo un frame de video.
    frame_loaded, frame = cap.read()
    if frame_loaded:
        TIME += 1
        if TIME % 50 == 0: invert_mode = not invert_mode
        masks = create_masks(frame, color_mode)
        if config['show_mask']: cv2.imshow('mask', masks.normal)

        masked_frame = cv2.bitwise_and(frame, frame, mask=masks.inverted)

        # Obtengo la imagen fractalica actual y aplico la máscara
        # (o sea, dejo solo lo que queda dentro)
        bg_image = get_current_image()
        masked_bg = cv2.bitwise_and(bg_image, bg_image, mask=masks.normal)

        # Finalmente, sumo las dos imágenes (frame de video + fractalica)
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
if background_video is not None: background_video.release()
if config['save_image']: original_out.release()
if config['save_result']: transformed_out.release()

cv2.destroyAllWindows()
