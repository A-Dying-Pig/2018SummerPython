import cv2 as cv
from PIL import Image
import sys
from flask_socketio import SocketIO

#please change the path to the folder 'tensorflow'
TENSORFLOW_DIR = "/anaconda2/lib/python2.7/site-packages/tensorflow"
#---------------------------------------------
MR_DIR = TENSORFLOW_DIR + "/models/research"
OD_DIR = MR_DIR + "/object_detection"
# This is needed since the notebook is stored in the object_detection folder.
sys.path.insert(0,OD_DIR)
sys.path.insert(1,MR_DIR)

import od
import tmo
import time
from multiprocessing import Process,Lock,Queue


class MyCamera():

    def __init__(self,socketio,app):
        self.socket = socketio
        self.ap = app
        self.camera = self.init_camera()
        self.height = 600
        self.width = 1067
        self.size = (self.width,self.height)

        #q1 for Process1
        self.q1 = Queue()

        self.t_m_o = tmo.TrackMovingObject()

        pro1 = Process(target=ImageProcessProcess,args=(self.q1,self.socket,self.ap))
        pro1.start()


    def init_camera(self):
        #RTSP
        #cap = cv.VideoCapture("rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov")
        #cap = cv.VideoCapture("rtsp://admin:admin@59.66.68.38:554/cam/realmonitor?channel=1&subtype=0")
        #System Camera
        cap = cv.VideoCapture(0)
        return cap


    def get_frame(self):
        ret, frame = self.camera.read()
        frame_resize = cv.resize(frame,(self.width,self.height))
        #process1
        if self.q1.empty():
            temp = cv.cvtColor(frame_resize, cv.COLOR_BGR2RGB)
            self.q1.put(temp)
        ret, jpeg = cv.imencode('.jpg', frame_resize)
        return jpeg.tobytes()


    def get_tracking_frame(self):
        if self.t_m_o.background_ready:
            ret, frame = self.camera.read()
            frame_resize = cv.resize(frame, (self.width, self.height))
            # process1
            if self.q1.empty():
                temp = cv.cvtColor(frame_resize, cv.COLOR_BGR2RGB)
                self.q1.put(temp)
            jpeg = self.t_m_o.process_frame(frame_resize)
            return jpeg
        else:
            time.sleep(self.t_m_o.background_reset_time)
            ret, frame = self.camera.read()
            frame_resize = cv.resize(frame, (self.width, self.height))
            self.t_m_o.set_background(frame_resize)


    def track_setting(self,blur,bri):
        self.t_m_o.blur_x = blur
        self.t_m_o.blur_y = blur
        self.t_m_o.color_threshold = bri


def ImageProcessProcess(q,socketio,app):
    ip = ImageProcess(socketio,app)
    while(1):
        #print("-----------IMAGE PROCESS-----------")
        if not q.empty():
            img = q.get()
            ip.process(img)


class ImageProcess():
    def __init__(self,socketio,app):
        self.object_detection = od.Object_Detection(socketio,app)

    def save(self,img):
        print('saving frame')
        image = Image.fromarray(img.astype('uint8')).convert('RGB')
        filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(time.time())) + ".jpg"
        image.save('output/' + filename)

    def process(self,img):
        #object detection
        img = self.object_detection.detect(img)
        #save
        self.save(img)