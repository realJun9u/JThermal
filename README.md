## Debug
### radiometry.py
python radiometry.py
1. uvc_open_error
```bash
sudo python radiometry.py
```
2. X Error: BadAccess (attempt to access private resource denied) 10
```bash
sudo QT_X11_NO_MITSHM=1 python radiometry.py 
```
### Failed to open /dev/video0: Permission denied
웹캠 사용 시 발생할 수 있는 에러. 유저를 video 그룹에 추가하고 재부팅한다.
```bash
sudo usermod -a -G username video
sudo reboot -h now
```
