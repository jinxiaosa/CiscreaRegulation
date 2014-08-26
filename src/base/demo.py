from ciscrea import Ciscrea
from console import Console
from plugins import add_module
import sys

if len(sys.argv)>2:
    jack=Ciscrea(sys.argv[1])
else:
    sys.exit(1)
    
print jack
jack.load_calibration(sys.argv[2]+".calib")

#add_module(jack, "pwm")

if not jack.calib:
    print "Run calibcrea.py first !"
    sys.exit(1)
Console(jack)