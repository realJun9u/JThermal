#!/home/pi/.env/bin/python
# -*- coding: utf-8 -*-

from uvctypes import *
import time
import cv2
import numpy as np
import datetime
import pandas as pd
import sys
import os
try:
  from queue import Queue
except ImportError:
  from Queue import Queue
import platform

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

def ktof(val):
  return (1.8 * ktoc(val) + 32.0)

def ktoc(val):
  return (val - 27315) / 100.0

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def display_temperature(img, val_k, loc, color):
  # Kelvin to Celsius
  val = ktoc(val_k)
  # cv2.putText(img,"{0:.1f} degC".format(val), loc, cv2.FONT_HERSHEY_SIMPLEX, 0.25, color, 2)
  x, y = loc
  # draw crossline
  cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
  cv2.line(img, (x, y - 2), (x, y + 2), color, 1)

def main():
  if len(sys.argv) < 2 and len(sys.argv) > 3:
    print("Usage : lepton (experement number) [,(try number)]")
    exit(1)
  dirname = "/home/pi/test/JThermal/images/" + sys.argv[1]
  
  if sys.argv[1] == '3' or sys.argv[1] == '4':
    if len(sys.argv) != 3:
      print("Expirement 3,4 must need try number")
      exit(1)
    dirname += "/" + sys.argv[2]
  
  if sys.argv[1] == '3' or sys.argv[1] == '4':
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
      print("Camera not found!")
      exit(1)
    # cap.set(3,cap.get(3)/2)
    # cap.set(4,cap.get(4)/2)
  else:
    cap = None
    ret = False
  
  if os.path.isdir(dirname) == False:
    os.mkdir(dirname)
  else:
    print(dirname,"is exist!")
    exit(1)
  
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
      
      # cv2.namedWindow("Lepton Radiometry",cv2.WINDOW_NORMAL)
      # cv2.resizeWindow("Lepton Radiometry", width=240, height=180)
      if cap is not None:
        cv2.namedWindow("Temperature",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Temperature", width=480, height=360)
      try:
        while True:
          data = q.get(True, 500)
          if cap is not None:
            ret,img2 = cap.read()
          if data is None:
            break
          minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(data)
          data_temp = data.copy()
          img = raw_to_8bit(data)
          img = cv2.applyColorMap(img, cv2.COLORMAP_INFERNO)
          # display_temperature(img, minVal, minLoc, (255, 0, 0))
          # display_temperature(img, maxVal, maxLoc, (0, 0, 255))
          img = cv2.flip(img,-1)
          cv2.imshow("Lepton Radiometry", img)
          if ret:
            cv2.imshow("Temperature", img2)
          k = cv2.waitKey(50) # 10fps
          if k == 27:
            break
          elif k == ord('t'):
            print("Max Temperature :",ktoc(maxVal))
          elif k == 13:
            now = datetime.datetime.now()
            fname = dirname + now.strftime("/%m%d_%H%M%S")
            cv2.imwrite(f"{fname}.jpg",img)
            print(f"File {fname}.jpg is Saved")
            data_temp = ktoc(data_temp)
            df = pd.DataFrame(data_temp)
            df = df.loc[::-1].loc[:,::-1]
            df.to_csv(f"{fname}.csv",index=False, header=None)
            if ret:
              cv2.imwrite(f"{fname}_.jpg",img2)
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
