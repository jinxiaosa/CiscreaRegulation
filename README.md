ciscrea-regulation
======================

This is the python code to control a bare CISCREA underwater vehicle (xubuntu). Inside /src/rov I built the robust and PID heading controller.
-----------------------------------------------------------

To excute this code with all hardware connected:

1. Navigate to /src/rov
2. Run python rov.py /dev/ttyUSB0 ../base/rov.calib 
-----------------------------------------------------------
Supports:

You need to intall following package on your computer

python 2.7
python-numpy
python-scipy
python-pygame
python-pymodbus
python-dev
$: sudo apt-get install [packages]

or run:
$ sudo apt-get install python2.7 python-numpy python-scipy python-pygame python-pymodbus python-dev

To avoid "import cv2" problem,Install open-cv.
Install tutorial:
http://docs.opencv.org/doc/tutorials/introduction/linux_install/linux_install.html#linux-installation

Test with:
$Python
$> import cv2

if no error you are OK

-----------------------------------------------------------

Note: Sometime the window do not stop. Run following code.
1. Run: jobs
2. Run: kill -9 %[jobs number]

-----------------------------------------------------------

Manual for the joystick.

Buttons:

Axis:

-----------------------------------------------------------

To install a very old wireless driver for D830 
http://www.bigfatostrich.com/2011/10/solved-ubuntu-11-10-wireless-issues/comment-page-1/
