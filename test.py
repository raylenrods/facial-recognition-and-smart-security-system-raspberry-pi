# -*- coding: utf-8 -*-

import cv2


cam = cv2.VideoCapture(0)

img_counter=0

ret, frame = cam.read()
img_name = "alert/alert_{}.jpg".format(img_counter)
cv2.imwrite(img_name, frame)
print("{} written!".format(img_name))

cam.release()

cv2.destroyAllWindows()

