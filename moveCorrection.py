#!/usr/bin/python

from __future__ import division
from Adafruit_PWM_Servo_Driver import PWM
import time
import RPi.GPIO as GPIO

pwm = PWM(0x40)

# GPIO Pins

GPIO_LEFT_US  = 12
GPIO_MIDDLE_US = 16
GPIO_RIGHT_US   = 22

GPIO_ENABLE = 10

# PWM Settings

servoZero     = 400
rightservoSpd = 380
leftservoSpd  = 419

PWMFreq = 80

# Centered Distances

# TODO Set values
rightIdeal  = 6.5
middleIdeal = 4.9 # 5.1
leftIdeal   = 6.7

def init ():

	# Initialize PWM and GPIO --------------------------------------------------

	pwm.setPWMFreq (PWMFreq)

	GPIO.setmode(GPIO.BOARD)

	GPIO.setup (GPIO_ENABLE, GPIO.IN)

	GPIO.setup (GPIO_LEFT_US,   GPIO.OUT)
	GPIO.setup (GPIO_RIGHT_US,  GPIO.OUT)
	GPIO.setup (GPIO_MIDDLE_US, GPIO.OUT)

	#cleanup output
	GPIO.output (GPIO_LEFT_US, 0)
	GPIO.output (GPIO_RIGHT_US, 0)
	GPIO.output (GPIO_MIDDLE_US, 0)

def measure (pin):

	pulseWidth = 0.000005

	# Set as output
	GPIO.setup (pin, GPIO.OUT)

	# Pulse
	GPIO.output (pin, 1)
	time.sleep  (pulseWidth)
	GPIO.output (pin, 0)

	# Set as input
	GPIO.setup (pin, GPIO.IN)

	# Measure Response
	while GPIO.input (pin) == 0:
			startTime = time.time()

	while GPIO.input (pin) == 1:
			endTime = time.time()

	duration = endTime - startTime
	distance = duration*34000/2

	return distance

def measureAll ():

	sleepTime = 0.002

	left   = measure (GPIO_LEFT_US)
        time.sleep (sleepTime)
	middle = measure (GPIO_MIDDLE_US)
	time.sleep (2*sleepTime)
	right  = measure (GPIO_RIGHT_US)

	return (left, middle, right)

def move (dist):

	try:	

		if dist < 0:
			print "Error: currently do not support backward movement"
			return

		measureFreq = 1
		count = 0
		mult = 8  # 11.46
		pulses = int(round(dist * mult))
		shortCount = 0		

		delta = 6

#		for i in range(0, pulses):
		while (True):

				if count % measureFreq == 0:
					measure = measureAll()
					offset = 0
					offsetR = 0
					offsetL = 0
					rHit = 0
					lHit = 0

					if measure[1] < middleIdeal:
						stop()
						return
						print "Warning: pre-mature stop"

					if measure[2] < 1.5 * rightIdeal:
						offsetR = measure[2] - rightIdeal
						rHit = 1

				#	if measure[0] < 1.5 * leftIdeal:
				#		offsetL =  measure[0] - leftIdeal
				#		lHit = 1
								
				#	if (rHit == 0 or lHit == 0) and shortCount == 0:
				#		shortCount = count
				#		print "Setting shortCount " + str(shortCount)
				#	elif (rHit == 0 or lHit == 0) and count - shortCount > 15:

					if rHit == 1:
						offset = offsetR
					else:
						offset = 0 # (offsetL + offsetR) /2

					iOffset = int(round(offset * delta))

					print "L: " + str(measure[0] - leftIdeal) + "\tM: " + str(measure[1]) + "\tR: " + str(measure[2] - rightIdeal) + "\tLS: " + str(iOffset) + "  RS: -" + str( iOffset)
#					print "L: " + str(measure[0] - leftIdeal) + "\tM: " + str(measure[1] - middleIdeal) + "\tR: " + str(measure[2]) + "\tLS: " + str(leftservoSpd - iOffset) + "\tRS: " + str(rightservoSpd + iOffset)

				a = 7
				b = 1
				bTime = 0.005

				for j in range (0,a):
						pwm.setPWM(0,0, rightservoSpd - 1 + iOffset)
						pwm.setPWM(1,0, leftservoSpd + iOffset)
						time.sleep (bTime/(a + b))

				for j in range (0,b):
						pwm.setPWM(0,0, rightservoSpd + iOffset)
						pwm.setPWM(1,0, leftservoSpd +  iOffset)
						time.sleep (bTime/(a + b))
			
				count += 1
		stop()

	except Exception,e: print str(e)

def rotate (angle):

	if angle == 90:
		turnRight()
	elif angle == 180:
		turnRight()
		turnRight()
	elif angle == 270:
		turnLeft()
	elif angle == -90:
		turnLeft()
	elif angle == -180:
		turnLeft()
		turnLeft()
	elif angle == -270:
		turnRight()
	else:
		print "Error: angle " + str(angle) + " unsupported"

def turnRight ():

		for i in range (0, 145):

				pwm.setPWM (0, 0, leftservoSpd)
				pwm.setPWM (1, 0, leftservoSpd)
				time.sleep (0.005)

		stop()

def turnLeft ():

		for i in range (0, 175):

				pwm.setPWM (0, 0, rightservoSpd)
				pwm.setPWM (1, 0, rightservoSpd)
				time.sleep (0.005)

		stop()

def stop ():

	pwm.setPWM (0, 0, 0)
	pwm.setPWM (1, 0, 0)

init()

start = time.time()

time.sleep (8)

while (True):
	move (0)
	time.sleep (0.005)
	left =  measure (GPIO_LEFT_US)
	
	if (left > 1.5*leftIdeal):
		turnLeft()
	else:
		turnLeft()
		turnLeft()

end = time.time()
print "Time elapsed " + str (end - start)
