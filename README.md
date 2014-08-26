git-ciscrea-regulation
======================

This is the python code to control a bare CISCREA underwater vehicle. Inside /src/rov I built the robust and PID heading controller.


To excute this code with all hardware connected:

1. Navigate to /src/rov
2. Run python rov.py /dev/ttyUSB0 ../base/rov.calib 

Note: Sometime the window do not stop. Run following code.
1. Run: jobs
2. Run: kill -9 %[jobs number]


Manual for the joystick.

Buttons:

Axis:
