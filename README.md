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
