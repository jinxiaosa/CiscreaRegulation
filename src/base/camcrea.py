import pygame.camera
import pygame
import cv2
import uuid #generate unique filenames
import numpy as np
import sys
import time
from multiprocessing import Process, Queue
from Queue import Full
import os
import signal

#initialize camera

class CamCrea():
    """Implemets a simple movie recorder + get_image from pygame.camera.
    Unfortunately the init() stuff from pygame.camera makes it impractical
    to inherit from pygame.camera.Camera unless rewritting the OS checks
    in camera.py
    """
    def __init__(self):
        """Optionnal Ciscrea instance (sync or async) in order to
        control the camera tilt"""
        
        pygame.camera.init()
        self.__connected=False
        try:
            if os.name=="posix":
                cam_dev=pygame.camera.list_cameras()[0]
                self.cam=pygame.camera.Camera(cam_dev, (640,480))
                self.cam.start()
                self.__pygame_cam=True
            else:
                self.cam = cv2.VideoCapture(0)
                self.__pygame_cam=False
                self.__last_query=time.time()
            self.__connected=True
        except Exception,e:
            print e
            pass
        
        #flag for recording state
        self.__recording=False
    
    def is_connected(self):
        return self.__connected
        
    def start_movie(self):
        """
        1/ Creates a new OpenCV VideoWriter process is none exists,
        store the movie in the videos/ subdirectory with a random name.
        2/ toggle the recording flag to true so that any call to query_image 
        will automatically append the picture to the movie
        """
        if not hasattr(self, "encoder_proc"): 
            self.__recording=True
            self.img_queue = Queue(5)
            #start a new separate python interpreter and not a thread
            #we git rid of the GIL this way and use the 2nd CPU core
            self.encoder_proc = Process(target=self.add_frame,
                                    args=(self.img_queue,))
            self.encoder_proc.start()
            
        
    def add_frame(self, img_queue):
            #get video encoder from openCV
            cv_codec=cv2.cv.CV_FOURCC('X','V','I','D')
            video_writer=cv2.VideoWriter("videos/"+str(uuid.uuid4())+".avi", cv_codec, 30, (640,480), True)
            img=img_queue.get()
            while img is not None:
                img=np.transpose(img, (1,0,2))
                video_writer.write(img)
                img=img_queue.get()
                
    def stop_movie(self):
        if not hasattr(self, "encoder_proc"): 
            print "No movie to stop"
            return None
        
        self.__recording=False
        self.img_queue.put(None)
        self.encoder_proc.join()
        del self.encoder_proc
        
    def is_recording(self):
        return self.__recording
    
    #having no inheritance s*cks here
    def query_image(self):
        if self.__pygame_cam:
            return self.cam.query_image()
        else:
            #quick and dirty fix for openCV cameras
            #wontfix further, do not use with windows
            t=time.time()
            if t-self.__last_query>0.04:
                self.__last_query=t
                return True
            else:
                return False
    
    def get_image(self):
        if self.__pygame_cam:
            img=self.cam.get_image()
            if self.__recording:
                try:
                    #img_array=pygame.surfarray.pixels3d(pyg_img).copy()
                    
                    #custom function to avoid some calls, see surfarray.pixels3d code
                    #use copy() to unlock the pyg_img surface
                    #keep RGB here as video writer expects this, otherwise
                    #BGR is offset=2, strides=(3, 1920, -1)
                    img_array = np.ndarray(
                        shape=(640, 480, 3),
                        dtype=np.uint8,
                        buffer=img.get_buffer (),
                        offset=0, strides=(3, 1920, 1)
                        )
    
                    self.img_queue.put(img_array.copy())
                except Full:
                    print "skipping frame"
            return img
        else:
            _,img=self.cam.read()
            img=np.ndarray(
                        shape=(640, 480, 3),
                        dtype=np.uint8,
                        buffer=img,
                        offset=2, strides=(3, 1920, -1)
                        )
            return pygame.surfarray.make_surface(img)
        
