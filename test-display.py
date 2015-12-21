#!/usr/bin/env python2.7  
# HDMIPi_toggle.py by Alex Eames http://raspi.tv/?p=7540 
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN)
 
# If 25 is set as an input, the hardware pullup on the HDMIPi board 
# keeps value at HIGH. We only change the port to an output when we 
# want to toggle the button. 
# This is because, when set as an output, the HDMIPi buttons are disabled.
# So each time we toggle the HDMIPi on or off, we set port back to input
 
def toggle():
    GPIO.setup(16, GPIO.OUT, initial=1)
    GPIO.output(16, 0)         # this is our simulated button press
    sleep(0.2)                 # hold button for 0.2 seconds
    GPIO.output(16, 1)         # release button
    GPIO.setup(16, GPIO.IN)    # set port back to input (re-enables buttons)
 
for x in range(3):             # on for 10s, off for 5s iterate 3 times 
    print "HDMIPi will stay on for 10 seconds"
    sleep(9)
    print "HDMIPi is switching off for 5 seconds"
    sleep(1)
    toggle() #off
    sleep(5)
    toggle() #on
 
print "finished, cleaning up"
GPIO.cleanup()
