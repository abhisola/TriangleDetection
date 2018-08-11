import cv2
import sys
import numpy as np

srcImgfile = sys.argv[1]
dstImgfile = sys.argv[2]

#print(srcImgfile)
#print(dstImgfile)

img = cv2.imread(srcImgfile)
kernel = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
img = cv2.filter2D(img, -1, kernel)
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 19, 15)
cv2.imwrite(dstImgfile, img)

