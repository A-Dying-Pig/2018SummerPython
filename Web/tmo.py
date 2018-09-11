#--coding:utf-8--
import cv2 as cv
import numpy as np

class TrackMovingObject():
    def __init__(self):
        self.background = None
        self.WaitFrame = 100
        self.CountFrame = 0

        #值越大，可以去掉更多的细节，必须是奇数
        self.blur_x = 21
        self.blur_y = 21
        #值越小，就只能识别出和背景差异较大的物体
        self.color_threshold = 100
        #忽略过于小的物体
        self.min_area = 1500
        #矩形框的颜色[r,g,b]
        self.FRAME_RGB = [0,245,255]


    def process_frame(self,frame):
        if self.CountFrame < self.WaitFrame:
            self.CountFrame += 1
            return None
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (self.blur_x, self.blur_y), 0)
        if self.background is None:
            self.background = gray
            return None
        diff = cv.absdiff(self.background, gray)
        diff = cv.threshold(diff, self.color_threshold, 255, cv.THRESH_BINARY_INV)[1]
        diff = cv.dilate(diff, None, iterations=2)
        image, contours, hierarchy = cv.findContours(diff.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv.contourArea(c) < self.min_area:  # 对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
                continue
            (x, y, w, h) = cv.boundingRect(c)  # 该函数计算矩形的边界框
            cv.rectangle(frame, (x, y), (x + w, y + h), (self.FRAME_RGB[2],self.FRAME_RGB[1], self.FRAME_RGB[0]), 2)
        return frame

