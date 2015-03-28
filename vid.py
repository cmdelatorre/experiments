import numpy as np
import cv2
import os

cap = cv2.VideoCapture(0)
FRAME_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
FRAME_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

# Load all the images in the 'img/' directory and crop to 640x480
bg_images = []
for bg_image_fname in os.listdir('img'):
    bg_image = cv2.imread(os.path.join('img', bg_image_fname))
    # d = bg_image.shape[0]
    # m = d/2
    # h = FRAME_HEIGHT
    # w = FRAME_WIDTH
    # bg_image = bg_image[m-(h/2):m+(h/2), m-(w/2):m+(w/2)]
    bg_images.append(bg_image)

image_index = 0
step = +1
step_delay = 0
delay_factor = 5
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


out = None
# Define the codec and create VideoWriter object
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi', fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))


# define range of blue color in HSV
color_low = np.array([160, 80, 80])
color_high = np.array([180, 255, 255])
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


#red_l2 = np.array([0, 100, 150])
#red_u2 = np.array([20, 255, 255])

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Convert BGR to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv_frame, color_low, color_high)
    #m2 = cv2.inRange(hsv_frame, red_l2, red_u2)
    #mask = cv2.bitwise_or(mask, m2)
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


    inv_mask = cv2.bitwise_not(mask)
    #cv2.imshow('mask', inv_mask)
    # Bitwise-AND mask and original image
    masked_frame = cv2.bitwise_and(frame, frame, mask=inv_mask)
    #cv2.imshow('masked_frame', masked_frame)

    # Apply the inverted mask to the bg image
    bg_image = get_current_image()
    masked_bg = cv2.bitwise_and(bg_image, bg_image, mask=mask)

    result = cv2.add(masked_frame, masked_bg)
    cv2.imshow('transformed', result)
    if out: out.write(result)

    cv2.imshow('image', frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
if out: out.release()
cv2.destroyAllWindows()
