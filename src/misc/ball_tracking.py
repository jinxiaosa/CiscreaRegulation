import pygame.camera
import cv2
import numpy as np
import sys

from multiprocessing import Process, Queue
from Queue import Full, Empty

pygame.camera.init()

cam_dev=pygame.camera.list_cameras()[0]
cam=pygame.camera.Camera(cam_dev, (640,480))
cam.start()
import time

pygame.init()
screen = pygame.display.set_mode((640,480))

kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4,4), (2,2))
hsv_min = np.array((10, 150, 150), np.uint8)
hsv_max = np.array((20, 255, 255), np.uint8)
red = np.array((0, 0, 255), np.uint8)

def findball(in_queue, out_queue):
    #block wainting for an image to be ready
    in_img=in_queue.get()
    while in_img is not None:
        img=cv2.resize(in_img, (240,320))
        #img=in_img
        #img=cv2.GaussianBlur(img, (9,9), 9)
        hsv_img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        tresh=cv2.inRange(hsv_img, hsv_min, hsv_max)
        tresh=cv2.dilate(tresh, kernel)
        tresh=cv2.erode(tresh, kernel)
        smooth=cv2.GaussianBlur(tresh, (9,9), 9)

#        pts=np.where(smooth<127)
#        smooth[pts]=0
        contours, hierarchy=cv2.findContours(smooth, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rect=None
        if hierarchy is not None:
            rect=[]
            for elements in zip(contours, hierarchy[0]):
                currentContour = elements[0]
                currentHierarchy = elements[1]
                if currentHierarchy[3] < 0: #keep only the outermost contours in hierarchy
                    x,y,w,h=2*np.array(cv2.boundingRect(currentContour))
                    rect.append((w*h,y,x,w,h))
                
        
        
        out_queue.put(rect)
        
#        #out.put(circles)
#        try:
#            cov=np.cov(pts)
#            eig, vec=np.linalg.eig(cov)
#            eig=np.abs(eig)
#            out_queue.put((np.mean(pts, axis=1), 3.055*np.sqrt(eig[0])))
#        except Exception, e:
#            print e
#            out_queue.put(None)
#            pass
#        ##out_queue.put(np.where(smooth>127))
        in_img=in_queue.get()
        
in_queue=Queue(1)
out_queue=Queue(1)

xy=None
old_xy=None
detect_proc=Process(target=findball, args=(in_queue, out_queue,))
detect_proc.start()
time.sleep(1)

done=False
fdrop=0
new_img_out=False
new_img_in=False
max_drop=0
while not done:
    if cam.query_image():
        pyg_img=cam.get_image()
        img = np.ndarray \
                    (shape=(640,480, 3),
                    dtype=np.uint8, buffer=pyg_img.get_buffer (),
                    offset=0, strides=(3, 1920, 1)).copy()
        #flag to ensure each frame is put once and only once into the queue
        new_img_in=True

    try:
        if new_img_in==True:
            in_queue.put_nowait(img)
            fdrop=0
            new_img_in=False
    except Full:
        fdrop+=1
#        max_drop=max(max_drop,fdrop)
#        if max_drop==fdrop:
#            print "Maximum lag by %d loops"%(fdrop)
        pass

    try:
        rects=out_queue.get_nowait()
        new_img_out=True
    except Empty:
        new_img_out=False
#
    if new_img_out and rects is not None:
        #sort by area, biggest first
        rects=sorted(rects, key=lambda rect_entry: -rect_entry[0]) 
        for rect in rects[:min(2,len(rects))]:
            pygame.draw.rect(pyg_img, (255,0,0), rect[1:], 2)
#        try:
#            cx=int(xy[0][0]*2)
#            cy=int(xy[0][1]*2)
#            r=int(xy[1]*2)
#            pygame.draw.circle(pyg_img, (255,0,0), (cx, cy), r, min(r,2))
#        except Exception, e:            
#            print e
#            pass

    if new_img_out:
        screen.blit(pyg_img, (0,0))
        pygame.display.flip()
        new_img_out=False

    event=pygame.event.poll()
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            done=True

in_queue.put(None)                    
