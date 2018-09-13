import RPi.GPIO as GPIO ## Import GPIO library
GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(7, GPIO.OUT) ## Setup GPIO Pin 7 to OUT
GPIO.output(7,True) ## Turn on GPIO pin 7



import RPi.GPIO as GPIO ## Import GPIO library
import time ## Import 'time' library. Allows us to use 'sleep'

GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(7, GPIO.OUT) ## Setup GPIO Pin 7 to OUT

##Define a function named Blink()
def Blink(numTimes,speed):
for i in range(0,numTimes):## Run loop numTimes
print "Iteration " + str(i+1)## Print current loop
GPIO.output(7,True)## Switch on pin 7
time.sleep(speed)## Wait
GPIO.output(7,False)## Switch off pin 7
time.sleep(speed)## Wait
print "Done" ## When loop is complete, print "Done"
GPIO.cleanup()
