import cv2
import sys
import numpy as np
import pandas as pd

if len(sys.argv) != 2:
    print("Insufficient Argument")
    exit(1)

imgname = './images/' + sys.argv[1] + '.jpg'
csvname = './images/' + sys.argv[1] + '.csv'

img = cv2.imread(imgname)
drag = False
ix,iy=-1,-1
tx,ty=0,0
w,h=0,0
yellow = (0,255,255)

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
            if w > 0 and h > 0:
                tx += ix
                ty += iy
                img=img[iy:iy+h+1,ix:ix+w+1]
                cv2.imshow('Img',img)

cv2.namedWindow('Img',cv2.WINDOW_NORMAL)
cv2.resizeWindow('Img',(640,480))
cv2.imshow('Img',img)
cv2.setMouseCallback('Img',onMouse,param=img)
cv2.waitKey(0)
cv2.destroyAllWindows()

df = pd.read_csv(csvname,header=None)
roi = df.loc[ty:ty+h,tx:tx+w]
print(np.array(roi))
print("mean :",roi.mean().mean())
print("max :",roi.max().max())


