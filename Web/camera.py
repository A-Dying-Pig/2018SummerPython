import cv2 as cv
from PIL import Image
import sys

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

    def __init__(self):
        self.camera = self.init_camera()
        self.height = 600
        self.width = 1067
        self.size = (self.width,self.height)
        #q1 for Process1
        self.q1 = Queue()
        #q2_send,q2_receive for Process2
        self.q2_send = Queue()
        self.q2_receive = Queue()

        pro1 = Process(target=ImageProcessProgress,args=(self.q1,))
        pro1.start()

        pro2 = Process(target=TrackMovingObjectProgress,args=(self.q2_send,self.q2_receive))
        pro2.start()

    def init_camera(self):
        #RTSP
        #cap = cv.VideoCapture("rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov")
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
        #process2
        if self.q2_send.empty():
            self.q2_send.put(frame_resize)
        ret, jpeg = cv.imencode('.jpg', frame_resize)
        return jpeg.tobytes()


    def get_tracking_frame(self):
        if self.q2_receive.empty():
            return None
        else:
            return self.q2_receive.get()


def ImageProcessProgress(q):
    ip = ImageProcess()
    while(1):
        print("-----------IMAGE PROCESS-----------")
        if not q.empty():
            img = q.get()
            ip.process(img)


def TrackMovingObjectProgress(q_send,q_receive):
    track = tmo.TrackMovingObject()
    while(1):
        print("-----------TRACK MOVING OBJECT-----------")
        if not q_send.empty():
            img = q_send.get()
            img = track.process_frame(img)
            q_receive.put(img)



class ImageProcess():
    def __init__(self):
        self.object_detection = od.Object_Detection()

    def save(self,img):
        print('saving frame')
        image = Image.fromarray(img.astype('uint8')).convert('RGB')
        filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(time.time())) + ".jpg"
        image.save('output/' + filename)

    def process(self,img):
        print("in process")
        #object detection
        img = self.object_detection.detect(img)

        #save
        self.save(img)