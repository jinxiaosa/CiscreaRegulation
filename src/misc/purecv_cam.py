import cv2
import numpy as np
c = cv2.VideoCapture(0)

while(1):
    _,f = c.read()
    cv2.imshow('e2',f)
    if cv2.waitKey(5)==27:
        break
cv2.destroyAllWindows()