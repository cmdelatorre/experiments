import cv2
import numpy as np

img1 = cv2.imread("img/im-julia.png")
print "img/im-julia.png", img1.shape
d1 = img1.shape[0]
m1 = d1/2
a = img1[m1-10:m1+10, m1-10:m1+10]
mean_red = a[:,:,2].mean()
cv2.imshow('a', img1)


b, g, red_layer = cv2.split(img1)
_, mask_over = cv2.threshold(red_layer, mean_red+1, 255, cv2.THRESH_BINARY)
#_, mask_below = cv2.threshold(red_layer, mean_red-1, 255, cv2.THRESH_BINARY_INV)

cv2.imshow('mo', mask_over)
#cv2.imshow('mb', mask_below)


inv_mask = cv2.bitwise_not(mask_over)

masked_r = cv2.bitwise_and(red_layer, inv_mask)
masked_g = cv2.bitwise_and(g, inv_mask)
masked_b = cv2.bitwise_and(b, inv_mask)
masked_img = cv2.merge((masked_b, masked_g, masked_r))
cv2.imshow('masked_img', masked_img)

img2 = cv2.imread("img/0.20.6im-julia9.png")
print "img/0.20.6im-julia9.png", img2.shape
d2 = img2.shape[0]
m2 = d2/2
img2 = img2[m2-(d1/2):m2+(d1/2), m2-(d1/2):m2+(d1/2)]
cv2.imshow('b', img2)

b2, g2, r2 = cv2.split(img2)
masked_r = cv2.bitwise_and(r2, mask_over)
masked_g = cv2.bitwise_and(g2, mask_over)
masked_b = cv2.bitwise_and(b2, mask_over)
masked_2 = cv2.merge((masked_b, masked_g, masked_r))
cv2.imshow('masked_2', masked_2)

cv2.imshow('res', cv2.add(masked_img, masked_2))


cv2.waitKey(0)
cv2.destroyAllWindows()
