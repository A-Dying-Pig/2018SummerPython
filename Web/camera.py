import cv2 as cv


class MyCamera():

    def __init__(self):
        self.camera = self.init_camera()


    def init_camera(self):
        #RTSP
        cap = cv.VideoCapture("rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov")
        #System Camera
        #cap = cv.VideoCapture(0)
        return cap


    def get_frame(self):
        ret, frame = self.camera.read()
        ret, jpeg = cv.imencode('.jpg', frame)
        return jpeg.tobytes()