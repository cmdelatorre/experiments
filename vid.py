# coding: utf-8
import numpy as np
import cv2
import os

cap = cv2.VideoCapture(0)
FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#FRAME_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
FRAME_WIDTH = 600  # Tamano de las imgs de hoy

# Load all the images in the 'img/' directory and crop to 640x480
# Acá estoy cargando todas las imágenes del directorio img en una lista.
# - Se pueden tener varios fractales (listas de imágenes)
bg_images = []
for bg_image_fname in os.listdir('img'):
    bg_image = cv2.imread(os.path.join('img', bg_image_fname))
    d = bg_image.shape[0]
    m = d/2
    h = FRAME_HEIGHT
    w = FRAME_WIDTH
    bg_image = bg_image[m-(h/2):m+(h/2), m-(w/2):m+(w/2)]
    bg_images.append(bg_image)


# Esto es para hacer que el fractal avanze y retroceda.
# Es la función que va a devolver una imagen para mezclar con cada frame.
# - Se puede hacer que el sentido dependa de alguna variable,
#   se puede meter aleatoriedad, se puede hacer que cambie el
#   fractal que se está mostrando, se pueden usar imágenes más grandes
#   que la ventana de video y mover la ventana sobre las imágenes (paneo o zoom)
image_index = 0
step = +1
step_delay = 0
delay_factor = 1
def get_current_image():
    global image_index, step, step_delay
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
out = None
# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
original_out = cv2.VideoWriter('original.avi', fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
transformed_out = cv2.VideoWriter('fractalized.avi', fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))
out = True



# Acá defino dos rangos (low,high), A y B.
# Con el boton de switch activo uno o el otro seteo.
A_low = np.array([0, 0, 56])
A_high = np.array([24, 161, 255])

B_low = np.array([62, 84, 36])
B_high = np.array([179, 255, 255])

# Estas variables de acá definen el rango actual en cada momento.
color_low = A_low.copy()
color_high = A_high.copy()


# Acá dibujo los controles en una ventanita.
cv2.namedWindow('controls')
# create trackbars for color change
def set_val_factory(arr, i):
    def set_val(x):
        arr[i] = x
    return set_val

cv2.createTrackbar('Lower H', 'controls', color_low[0], 179, set_val_factory(color_low, 0))
cv2.createTrackbar('Lower S', 'controls', color_low[1], 255, set_val_factory(color_low, 1))
cv2.createTrackbar('Lower V', 'controls', color_low[2], 255, set_val_factory(color_low, 2))

cv2.createTrackbar('Upper H', 'controls', color_high[0], 179, set_val_factory(color_high, 0))
cv2.createTrackbar('Upper S', 'controls', color_high[1], 255, set_val_factory(color_high, 1))
cv2.createTrackbar('Upper V', 'controls', color_high[2], 255, set_val_factory(color_high, 2))

def switch_toggle(x):
    print x
    if x == 0:
        color_low = A_low.copy()
        color_high = A_high.copy()
        print color_high
    else:
        color_low = B_low.copy()
        color_high = B_high.copy()
        print color_high
    cv2.setTrackbarPos('Lower H', 'controls', color_low[0])
    cv2.setTrackbarPos('Lower S', 'controls', color_low[1])
    cv2.setTrackbarPos('Lower V', 'controls', color_low[2])

    cv2.setTrackbarPos('Upper H', 'controls', color_high[0])
    cv2.setTrackbarPos('Upper S', 'controls', color_high[1])
    cv2.setTrackbarPos('Upper V', 'controls', color_high[2])

# create switch for ON/OFF functionality
switch = '0 : OFF \n1 : ON'
cv2.createTrackbar(switch, 'controls',  0, 1, switch_toggle)


# Loop principal. Funciona hasta que se aprieta 'q'
# Se ejecuta todo para cada frame de video.
while(True):
    # Acá capturo un frame de video.
    ret, frame = cap.read()
    # Acá estoy modificando el ancho porque las imgs que tengo son de 600x600 y la camara 640x480.
    frame = frame[:, : FRAME_WIDTH, :]

    # Creación de la máscara:
    # Primero transformo los valores de cada píxel, cambiando de (Blue, Green, Red) a HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Del frame transformado, creo una máscara:
    #  - Tiene 255 en los píxeles que están dentro del rango actual. 0 en los que no.
    #    El rango actual es el valor que haya en color_low, color_high
    #    Ese rango actual va cambiando de acuerdo a los controles.
    #    Se puede cambiar el rango con otra cosa (arduino, etc)
    mask = cv2.inRange(hsv_frame, color_low, color_high)
    # Luego, aplico un filtro morfolóligo para suavizar la máscara
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Acá creo una copia invertida de la máscara.
    inv_mask = cv2.bitwise_not(mask)
    cv2.imshow('mask', inv_mask)  # Esto es para ver la másccara
    # Aplico la máscara invertida en el frame original (o sea, borro lo que queda dentro)
    masked_frame = cv2.bitwise_and(frame, frame, mask=inv_mask)
    #cv2.imshow('masked_frame', masked_frame)

    # Obtengo la imagen fractalica actual y aplico la máscara
    # (o sea, dejo solo lo que queda dentro)
    bg_image = get_current_image()
    masked_bg = cv2.bitwise_and(bg_image, bg_image, mask=mask)

    # Finalmente, sumo las dos imágenes (frame de video + fractalica)
    result = cv2.add(masked_frame, masked_bg)

    # Muestro los frames de video en sus ventanitas y grabo esos frames en archivos separados.
    cv2.imshow('transformed', result)
    cv2.imshow('image', frame)
    if out:
        original_out.write(frame)
        transformed_out.write(result)

    # Si se aprieta 'q' sale del loop
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
if out:
    original_out.release()
    transformed_out.release()

cv2.destroyAllWindows()
