import numpy as np
import cv2
import os

cap = cv2.VideoCapture(0)
frame = None

B = 0
G = 1
R = 2

upper_left = None
bottom_right = None
stats = None

def select_marker(event, x, y, flags, param):
    global upper_left, bottom_right, stats

    if event == cv2.EVENT_LBUTTONDOWN:
        upper_left = (y, x)
        print "upper left: ", upper_left
    if event == cv2.EVENT_LBUTTONUP:
        bottom_right = (y, x)
        print "bottom_right: ", bottom_right
        marked_area = frame[upper_left[0]:bottom_right[0], upper_left[1]:bottom_right[1]]
        stats = {
            'red': {
                'mean': marked_area[:,:, R].mean(),
                'stddev': marked_area[:,:, R].std()
            },
            'green': {
                'mean': marked_area[:,:, G].mean(),
                'stddev': marked_area[:,:, G].std()
            },
            'blue': {
                'mean': marked_area[:,:, B].mean(),
                'stddev': marked_area[:,:, B].std()
            },
        }
        print stats


# Load all the images in the 'img/' directory and crop to 640x480
bg_images = []
for bg_image_fname in os.listdir('img'):
    bg_image = cv2.imread(os.path.join('img', bg_image_fname))
    d = bg_image.shape[0]
    m = d/2
    h = 480
    w = 640
    bg_image = bg_image[m-(h/2):m+(h/2), m-(w/2):m+(w/2)]
    bg_images.append(bg_image)

image_index = 0
step = +1
def get_current_image():
    global image_index, step
    if image_index == 0:
        step = +1
    elif image_index == len(bg_images)-1:
        step = -1
    current_image = bg_images[image_index]
    image_index += step
    print image_index
    return current_image



cv2.namedWindow('image')
cv2.setMouseCallback('image', select_marker)
cv2.namedWindow('mask')
cv2.namedWindow('transformed')

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    cv2.imshow('res',res)

    # Display the resulting frame
    if stats:
        b, g, r = cv2.split(frame)
        _, red_mask = cv2.threshold(
                r,
                stats['red']['mean']+stats['red']['stddev'],
                255,
                cv2.THRESH_BINARY)
        _, green_mask = cv2.threshold(
                r,
                stats['green']['mean']+stats['green']['stddev'],
                255,
                cv2.THRESH_BINARY)
        _, blue_mask = cv2.threshold(
                r,
                stats['blue']['mean']+stats['blue']['stddev'],
                255,
                cv2.THRESH_BINARY)
        mask = cv2.bitwise_and(red_mask, green_mask)
        mask = cv2.bitwise_and(mask, blue_mask)
        cv2.imshow('mask', mask)

        inv_mask = cv2.bitwise_not(mask)
        masked_r = cv2.bitwise_and(r, mask)
        masked_g = cv2.bitwise_and(g, mask)
        masked_b = cv2.bitwise_and(b, mask)
        masked_frame = cv2.merge((masked_b, masked_g, masked_r))

        # Apply the mask to the bg image
        bg_image = get_current_image()
        b, g, r = cv2.split(bg_image)
        masked_r = cv2.bitwise_and(r, inv_mask)
        masked_g = cv2.bitwise_and(g, inv_mask)
        masked_b = cv2.bitwise_and(b, inv_mask)
        masked_bg = cv2.merge((masked_b, masked_g, masked_r))

        result = cv2.add(masked_frame, masked_bg)
        cv2.imshow('transformed', result)
        out.write(result)

    cv2.imshow('image', frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()
