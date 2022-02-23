#!/home/pi/JThermal/.env/bin/python
try:
    import cv2
except ImportError:
    print("ERROR python-opencv must be installed")
    exit(1)
try:
    from aht10 import measure
except ImportError:
    print("aht10 import error")
    exit(1)

class OpenCvCapture(object):

    def __init__(self):
        cv2_tcap = cv2.VideoCapture(0)
        cv2_cap = cv2.VideoCapture(2)

        if not cv2_cap.isOpened() or not cv2_tcap.isOpened():
            print("Camera not found!")
            exit(1)
        
        cv2_cap.set(3,640)
        cv2_cap.set(4,480)

        self.cv2_cap = cv2_cap
        self.cv2_tcap = cv2_tcap

    def show_video(self):
        cv2.namedWindow("lepton", cv2.WINDOW_NORMAL)
        cv2.namedWindow("camera", cv2.WINDOW_NORMAL)
        print("Running, ESC or Ctrl-c to exit...")
        cnt = 0
        while True:
            ret, img = self.cv2_cap.read()
            tret, timg = self.cv2_tcap.read()

            if ret == False and tret == False:
                print("Error reading image")
                break
            #timg = cv2.flip(cv2.resize(timg, (640, 480)),1)
            #img = cv2.flip(cv2.resize(img, (640, 480)),1)
            #img = cv2.flip(img,1)
            cv2.imshow("lepton", timg)
            cv2.imshow("camera", img)
            if cnt == 8:
                measure()
                cnt = 0
            cnt += 1
            if cv2.waitKey(125) == 27: # 8fps
                break

        cv2.destroyAllWindows()

if __name__ == '__main__':
    OpenCvCapture().show_video()
