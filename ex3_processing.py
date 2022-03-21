import cv2
import os
import sys
import pytesseract
import numpy as np
from scipy.ndimage.interpolation import shift
from PIL import Image
import matplotlib.pyplot as plt
from glob import glob

def onMouse(event,x,y,flags,param):
    global drag,ix,iy,tx,ty,w,h,yellow,img
    if event == cv2.EVENT_LBUTTONDOWN:
        drag = True
        ix,iy=x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drag:
            img_draw = img.copy()
            cv2.rectangle(img_draw,(ix,iy),(x,y),yellow,1)
            cv2.imshow('Img',img_draw)
    elif event == cv2.EVENT_LBUTTONUP:
        if drag:
            drag = False
            w = x - ix
            h = y - iy
            if w >= 0 and h >= 0:
                tx += ix
                ty += iy
                img=img[iy:iy+h+1,ix:ix+w+1]
                cv2.imshow('Img',img)

def initcapture(sample_file):
    coordinates=[]
    sample_img = cv2.imread(sample_file)
    for _ in range(1):
        global drag,ix,iy,tx,ty,w,h,yellow,img
        img = sample_img.copy()
        drag = False
        ix,iy=-1,-1
        tx,ty=0,0
        w,h=0,0
        yellow = (0,255,255)
        cv2.namedWindow('Img',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Img',(640,480))
        cv2.imshow('Img',img)
        cv2.setMouseCallback('Img',onMouse)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        coordinates.append((iy,iy+h+1,ix,ix+w+1))
    # ROI 확인
    for i in range(len(coordinates)):
        y1,y2,x1,x2 = coordinates[i]
        print(y1,y2,x1,x2)
        cv2.imshow("Img",sample_img[y1:y2,x1:x2])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    valid = input("want to continue? [y/n] : ").lower()
    if valid == 'y':
        ret = True
    else:
        ret = False
    return ret, coordinates

def main():
    if len(sys.argv) == 1:
        img_list = ['sample.jpg']
    elif len(sys.argv) == 2:
        path = os.path.join(os.getcwd(),'images/3',sys.argv[1])
        os.chdir(path)
        img_list = sorted(glob('*_.jpg'))
    else:
        print("invalid arguments")
        exit(1)

    ret, coordinates = initcapture(img_list[0]) # ROI 뜯기
    if ret == False:
        exit(1)

    kernel = np.ones((5,5),np.uint8)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(12,12))
    filename = str(os.getpid()) + ".png"
    for file in img_list:
        origin_img = cv2.imread(file,cv2.IMREAD_GRAYSCALE)
        for i in range(len(coordinates)):
            y1,y2,x1,x2 = coordinates[i]
            img = origin_img[y1:y2,x1:x2]
            img = cv2.resize(img,dsize=(320,240),interpolation=cv2.INTER_CUBIC)
            img = cv2.bitwise_not(img)
            img = clahe.apply(img)
            img = cv2.threshold(img,10,250,cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            img = cv2.dilate(img,kernel,iterations=3)

            # --------Tesseract---------
            cv2.imwrite(filename, img)
            result = pytesseract.image_to_string(filename,config='digits')
            print(result)
            # try:
            #     print(float(result))
            # except:
            #     pass

            cv2.imshow("Img",img)
            cv2.waitKey(0)
    cv2.destroyAllWindows()
    os.remove(filename)

if __name__=="__main__":
    main()
