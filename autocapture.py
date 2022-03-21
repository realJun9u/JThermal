# -*- coding: utf-8 -*-

from uvctypes import *
from labquest_ocr import onMouse, initcapture, imgtonum
import cv2
import datetime
import pandas as pd
import numpy as np
import os
import sys
import pytesseract
import re
from glob import glob

try:
  from queue import Queue
except ImportError:
  from Queue import Queue

BUF_SIZE = 2
q = Queue(BUF_SIZE)

def py_frame_callback(frame, userptr):

  array_pointer = cast(frame.contents.data, POINTER(c_uint16 * (frame.contents.width * frame.contents.height)))
  data = np.frombuffer(
    array_pointer.contents, dtype=np.dtype(np.uint16)
  ).reshape(
    frame.contents.height, frame.contents.width
  )
  if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
    return

  if not q.full():
    q.put(data)

PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)

def ktoc(val):
  return (val - 27315) / 100.0

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def main():
  if len(sys.argv) < 2 or len(sys.argv) > 4:
    print("Usage : lepton (experiment number) [,(try number),(distance)]")
    exit(1)
  dirname = "/home/pi/JThermal/images/" + sys.argv[1]
  
  if sys.argv[1] == '3' or sys.argv[1] == '4':
    if len(sys.argv) < 4:
      print("Expirement 3,4 must need try number and distance")
      exit(1)
    dirname += "/" + sys.argv[2]
    if os.path.isdir(dirname) == False:
      os.mkdir(dirname)
    else:
      print(f"{dirname} is exist.")
    dirname += "/" + sys.argv[3]
    if os.path.isdir(dirname) == False:
      os.mkdir(dirname)
    else:
      print(f"{dirname} is exist.")
    
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
      print("Camera not found!")
      exit(1)
  else:
    cap = None
    ret = False
  
  ctx = POINTER(uvc_context)()
  dev = POINTER(uvc_device)()
  devh = POINTER(uvc_device_handle)()
  ctrl = uvc_stream_ctrl()

  res = libuvc.uvc_init(byref(ctx), 0)
  if res < 0:
    print("uvc_init error")
    exit(1)

  try:
    res = libuvc.uvc_find_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0)
    if res < 0:
      print("uvc_find_device error")
      exit(1)

    try:
      res = libuvc.uvc_open(dev, byref(devh))
      if res < 0:
        print("uvc_open error")
        exit(1)
      print("device opened!")

      print_device_info(devh)
      print_device_formats(devh)

      frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
      if len(frame_formats) == 0:
        print("device does not support Y16")
        exit(1)

      libuvc.uvc_get_stream_ctrl_format_size(devh, byref(ctrl), UVC_FRAME_FORMAT_Y16,
        frame_formats[0].wWidth, frame_formats[0].wHeight, int(1e7 / frame_formats[0].dwDefaultFrameInterval)
      )

      res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
      if res < 0:
        print("uvc_start_streaming failed: {0}".format(res))
        exit(1)
      
      if cap is not None:
        cv2.namedWindow("Temperature",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Temperature", width=480, height=360)
        _,img_labquest = cap.read()
        _, coordinates = initcapture(img_labquest,2)
        ondo_pre = [0,0]
      try:
        while True:
          # Lepton read
          data = q.get(True, 500)
          if data is None:
            break
          # Labquest read
          if cap is not None:
            ret,img_labquest = cap.read()
            ondo = []
            for i in range(len(coordinates)):
              y1,y2,x1,x2 = coordinates[i]
              img_roi = img_labquest[y1:y2,x1:x2]
              try:
                ondo.append(imgtonum(img_roi))
              except:
                pass

          data_temp = data.copy()
          img = raw_to_8bit(data)
          img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)
          img = cv2.flip(img,-1)

          cv2.imshow("Lepton Radiometry", img)
          if ret:
            cv2.imshow("Temperature", img_labquest)
          k = cv2.waitKey(1000) # 1fps
          if k == 27 or np.mean(ondo) < 30: # ESC - terminate
            print("Terminate")
            break
          if not any(np.equal(ondo_pre,ondo)) and ondo: # Save
            ondo_pre = ondo
            now = datetime.datetime.now()
            fname = dirname + now.strftime("/%m%d_%H%M%S")
            cv2.imwrite(f"{fname}.jpg",img)
            print(f"File {fname}.jpg is Saved")
            print("Ondo :",ondo)
            data_temp = ktoc(data_temp)
            df = pd.DataFrame(data_temp)
            df = df.loc[::-1].loc[:,::-1]
            df.to_csv(f"{fname}.csv",index=False, header=None)
            if ret:
              cv2.imwrite(f"{fname}_.jpg",img_labquest)
        cv2.destroyAllWindows()
      finally:
        libuvc.uvc_stop_streaming(devh)
      print("done")
    finally:
      libuvc.uvc_unref_device(dev)
  finally:
    libuvc.uvc_exit(ctx)

if __name__ == '__main__':
  main()
