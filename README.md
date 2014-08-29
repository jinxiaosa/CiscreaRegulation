ciscrea-regulation
======================

This is the python code to control a bare CISCREA underwater vehicle (MacOS). Inside /src/rov I built the robust and PID heading controller.
-----------------------------------------------------------

To excute this code with all hardware connected:

1. Navigate to /src/rov
2. Run python rov.py /dev/tty.usbserial-FTV7LGVK ../base/rov.calib 

Note: Here the RS485 change from /dev/ttyUSB0 (ubuntu) to tty.usbserial-FTV7LGVK now. （or cu.usbserial-FTTJHSHE for the new ciscrea）


-----------------------------------------------------------
Supports(linux user):

You need to install following package on your computer

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
Supports(MAC user):

You need to install following package on your computer

python 2.7 
python-numpy 
python-scipy 
python-pygame 
python-pymodbus
python-dev

1. (I suggest) Install python 2.7 from Macports.

2. Install MacPorts.

3. Install pygame:

$ sudo port install py-game

or 

(Suggest *.dmg) install pygame from official package

Note: If you encounter a 32 and 64 bit problem. Check you Mac OS version and download correct Pygame package.

Before reinstall pygame, remove old one by:

sudo rm -Rf /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pygame

For example, I have a macbook pro retina 2012 on mavericks 10.9, I remove wrong pygame and install "Lion apple supplied python: pygame-1.9.2pre-py2.7-macosx10.7.mpkg.zip" 

4. Install scipy and numpy

$sudo port install py27-numpy py27-scipy

$sudo easy_install numpy (You only need this line if you encounter a import failure after above commands.check: http://stackoverflow.com/questions/19605911/installing-python-packages-modules-on-mac)

5. Install pymodbus

$svn checkout http://pymodbus.googlecode.com/svn/trunk/ pymodbus-read-only

$cd pymodbus-read-only

$python setup.py install

-----------------------------------------------------------

Note: Sometime the video window do not stop. Run following code.

$jobs

$ kill -9 %[jobs number]

-----------------------------------------------------------

Manual for the joystick.

Buttons:

Btn1:

Btn2:

Btn3: Turn on Joystick controlled Yaw following program (Hinf only)

Btn4:

Btn5:

Btn6:

Btn7: Start and Stop record underwater camera

Btn8:

Btn9: Change Yaw Controller Target (114 and 275 degree)

Btn10:

Btn11: Turn on/off yaw controller

Btn12: Switch Yaw Controller between PID and Hinf Robust controller

Axis:

x aix: Horizontal Motors -127~127(Surge)

y aix: Horizontal Motors -127~127(Sway)

z aix: Vertical Motors -127~127(Depth,Heave)

hat swith up & down: Underwater Camera tilt up & down

-----------------------------------------------------------

To install a very old wireless driver for D830 

http://www.bigfatostrich.com/2011/10/solved-ubuntu-11-10-wireless-issues/comment-page-1/

This code base on the work of Irvin Probst and Rui YANG.
