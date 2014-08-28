ciscrea-regulation
======================

This is the python code to control a bare CISCREA underwater vehicle (xubuntu). Inside /src/rov I built the robust and PID heading controller.
-----------------------------------------------------------

To excute this code with all hardware connected:

1. Navigate to /src/rov
2. Run python rov.py /dev/ttyUSB0 ../base/rov.calib 


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

6. Install Opencv

Install Opencv using official documents (linux manual works).

Note that on Mac you need to point opencv to the correct python when you run CMAKE (There might be Apple Python, Macports Python, Brew python simultaneously) 

For me I choose Macport Python, and I remove the three PATH export commands inside ".profile".

After opencv installation.

$python
>>import cv2

No error appear.

---------------------------
Fail process( Do not read)

Fail 1:

I tried  the tutorial :http://docs.opencv.org/doc/tutorials/introduction/linux_install/linux_install.html#linux-installation (I prefer its github way).

Then I face the problem that cv.so is missing. 

I follow the solution in http://www.daveperrett.com/articles/2010/12/14/face-detection-with-osx-and-python/.

Just add export PYTHONPATH=/usr/local/lib/python2.7/site-packages/:$PYTHONPATH to .profile

or

 another way : http://yiliangzhou.com/blog/?p=11.
 
Both methods crash my python when I "import  cv2"  inside Python terminal!!! 

(Online Answer: The problem is that you have 2 different Python versions, probably incompatible ones, installed on your machine - analysis of CMakeCache.txt proves that. Remove the one installed in "/opt" and everything should go well. On my OSX Lion machine cv2 works great.)


Fail 3:

Changing Python from default to macports version and install opencv by macport (Python27, Suggest) : 

http://stackoverflow.com/questions/5846745/opencv-python-osx, https://www.youtube.com/watch?v=1_0p9nA3yxM

$sudo port install python27
$sudo port select --set python python27
$sudo port install opencv +python27

Write export PYTHONPATH=/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages:$PYTHONPATH into .profile

It crash again, with the same segmentation 11 problem.

TOO MANY PYTHON PROBLEM(http://stackoverflow.com/questions/14117945/too-many-different-python-versions-on-my-system-and-causing-problems)

Not try:

I did not test the brew solution(Maybe you can try)

http://www.daveperrett.com/articles/2010/12/14/face-detection-with-osx-and-python/
-----------------------------------------------------------

Note: Sometime the video window do not stop. Run following code.

$jobs

$ kill -9 %[jobs number]

-----------------------------------------------------------

Manual for the joystick.

Buttons:
Btn1:
Btn1:
Btn1:
Btn1:

Axis:

-----------------------------------------------------------

To install a very old wireless driver for D830 

http://www.bigfatostrich.com/2011/10/solved-ubuntu-11-10-wireless-issues/comment-page-1/

This code base on the work of Irvin Probst and Rui YANG.
