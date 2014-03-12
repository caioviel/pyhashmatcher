'''
Created on May 11, 2012

@author: erick
'''

from cv2 import cv
#import kaept.util.cvadapter as cvadapter


medias = [19.73160947450408, 23.454414721375695, 53.35533913993746, 60.88197529732891, 22.494225127219806, 27.272708973538464, 62.42983486869562, 71.70654311372121, 22.859377269178026, 28.23588843130625, 66.03876245696352, 76.2857419426732, 23.53530013512501, 28.813563368961262, 68.11354710187311, 78.29932849053715]
errors = [28.10215413676879, 33.760780094153475, 35.455708395050976, 36.94861137616652, 31.810563673825303, 38.39366069251784, 39.85072924673173, 41.58289850575968, 32.384981230282705, 38.747774318977505, 39.78590027459013, 42.558745157394775, 33.31722076379771, 39.712054254893786, 40.19325161167611, 42.21300545927706]


import hashlib
import pickle
import time
#import shutil
import os

import logging
logging.basicConfig(level=logging.INFO)

class SampleBase(object):
    def __init__(self, directory, sample_list=None):
        self.directory = directory
        self.filename_list = sample_list
        self.samples_map = {}
        self.samples = []
        
    @property
    def size(self):            
        return len(self.samples)
        
    def load_base(self):
        if self.filename_list is None:
            self.filename_list = os.listdir(self.directory)
        
        logging.info("Loading %d samples", len(self.filename_list))
        counter = 1
        for filename in self.filename_list:
            logging.info("Sample %d of %d", counter, len(self.filename_list))
            sample = Sample(filename, self.directory)
            sample.load_sample()
            self.samples_map[filename] = sample
            self.samples.append(sample)
            counter += 1
            
class Sample(object):
    def __init__(self, name, directory):
        self.name = name
        self.directory = directory
        self.fps = None
        self.width = None
        self.height = None
        self.md5 = None
        self.number_frames = None
        self.frames = None
        
    def get_frame(self, index):
        return self.frames[index]

    def __str__( self ):
        return "(Sample: %s)" % (self.name)
    
    @property
    def size(self):            
        return len(self.frames)
    
    
    def load_sample(self):
        path = os.path.join(self.directory, self.name)
        
        capturer = cv.CaptureFromFile(path)
        self.fps = round(cv.GetCaptureProperty(capturer,cv.CV_CAP_PROP_FPS))
        self.width = round(cv.GetCaptureProperty(capturer,cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = round(cv.GetCaptureProperty(capturer,cv.CV_CAP_PROP_FRAME_HEIGHT))
        self.number_frames = cv.GetCaptureProperty(capturer , cv.CV_CAP_PROP_FRAME_COUNT)
        
        logging.info("Loading file \"%s\": %sx%s@%s", path, self.width, self.height, self.fps)
        
        self.load_frames(capturer)
        
        #self.calc_md5(path)
        
    def calc_md5(self, path):
        if self.config.md5:
            fh = open(path, 'rb')    
            md5 = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                md5.update(data)
                self.md5=md5.hexdigest()
            self.save()
            logging.info("MD5 from file: %s ", self.md5)
    
    def load_frames(self, capturer):
        begintime = time.clock()
        i=0
        self.frames = []
        while(True):
            #begin_time = time.clock()
            img = cv.QueryFrame(capturer)
            
            if (img == None):
                break;
            
            frame = Frame(pos=i,sample=self)
            frame.calc_sign_from_image(img)
            self.frames.append(frame)
            ##end_time = time.clock()
            #print end_time - begin_time
            #break
            i+=1
            
        self.number_frames = len(self.frames)
        total = time.clock() - begintime
        logging.info("The process took %s seconds for %d frames", total, len(self.frames))          
        
        # calculate hash of the file

class Frame(object):
    def __init__(self, sample, pos):
        self.sample = sample
        self.pos = pos
        self.data = None
        self.fingerprint = None
        self.signs = []
        self.pixels = None
        
    def calc_sign_from_image(self, img):
        gray = Frame.convertToGray(img)
        small = Frame.reduceFrame(gray, 2)
        width, heigh = cv.GetSize(small)
        #cv.SaveImage("/home/caioviel/Desktop/original.png", img)
        #cv.SaveImage("/home/caioviel/Desktop/gray.png", gray)
            
        deltaX, deltaY = width/4, heigh/4
        pixels = 0
        for x in xrange(4):
            for y in xrange(4):
                x0, x1 = x*deltaX, (x+1)*deltaX
                y0, y1 = y*deltaY, (y+1)*deltaY
                p, sign = self.__calc_sign(gray, x0, x1, y0, y1)
                #subimage = small[y0 : y1, x0 : x1]
                #cv.SaveImage("/home/caioviel/Desktop/image%s_%s.png" % (x, y), subimage)
                pixels += p
                self.signs.append(sign)
        
    def  __calc_sign(self, image, x0, x1, y0, y1):
        pixelsum = 0
        pixels = 0
        for x in xrange(x0, x1):
            for y in xrange(y0, y1):
                pixelsum += image[y, x]
                pixels += 1
        return pixels, pixelsum / ( (x1-x0) * (y1-y0) )
                
    def load(self, data):
        pass
        #a = pickle.loads(self.data)
        #print (data)
        #raw_input("before data")
        #self.image = data
        #self.image = cvadapter.array2cv(a)
    
    @staticmethod
    def convertToGray(img):
        frame_size = cv.GetSize(img)
        gray = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
        cv.CvtColor(img,gray,cv.CV_BGR2GRAY)
        return gray
    
    @staticmethod
    def reduceFrame(frame, num):
        src = cv.GetMat(frame)
        for _ in xrange(num):
            w, h = cv.GetSize(src)
            small = cv.CreateMat((h + 1) / 2, (w + 1) / 2, src.type)
            cv.PyrDown(src, small)
            src = cv.CreateMat((h + 1) / 2, (w + 1) / 2, src.type)        
            cv.Copy(small, src)
        return small
    

def test():
    sample = Sample("Videosactivia.avi", "/home/caioviel/minibase")
    sample.load_sample()
    
def calc_median_values(directory):
    import math
    base = SampleBase(directory)
    base.load_base()
    medias = []
    errors = []
    
    for i in xrange(16):
        total_frames = 0
        media = 0
        error = 0
        
        for sample in base.samples:
            for frame in sample.frames:
                media += frame.signs[i]
                total_frames += 1
        media = media /  total_frames
        
        for sample in base.samples:
            for frame in sample.frames:
                error += math.pow(frame.signs[i] - media, 2)
                
        error = math.sqrt(error / (total_frames-1))
        
        medias.append(media)
        errors.append(error)
        
    print medias
    print errors
    
    

if __name__ == '__main__':
    calc_median_values("/home/caioviel/Videos")
    #test()
    
    
    
