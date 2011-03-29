#Code by Ian Daniher - 2011-03-26

#Use this code at your own risk!

#This is a proof of concept implementation of the standard LiPo CC/CV charging algorithm.

#Tested to work with a 1000maAh / 3.7v cellphone battery. YMMV!

import modconsmu
import time
import threading

if raw_input("do you absolve the author of this code of all responsibility related to its use? (yes/no)") != "yes":
	quit()

dataStream = 1

if dataStream:
	import socket
	host = "localhost"
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, 8098))

smu = modconsmu.smu()

chargeData = []
tick = 1

def log():
	#time, (voltage, current)
	data = ( time.time(), smu.update() )
	chargeData.append(data)
	if dataStream:
		upData = "%.4f %.4f %.4f" % (data[0], data[1][0], abs(data[1][1]))
		sock.send(upData)

def CCCVProfile(constantCurrent = .2, constantVoltage = 4.2):
	#log initial open-cell voltage
	log()
	#constant current mode starts
	smu.set(amps = constantCurrent)
	#check cell voltage ever tick until it reaches 4.2v or higher
	while smu.update()[0] < constantVoltage:
		log()
		time.sleep(tick)
	#constant voltage mode starts
	smu.set(volts = constantVoltage)
	#check charge current every tick until its 50ma or less
	while abs(smu.update()[1]) > .05:
		log()
		time.sleep(tick)
	#disable charging
	smu.set(amps = 0)
	#make sure that a battery was attached
	if ( chargeData[-1][0] - chargeData[0][0] ) > 10:
		log()
		print("charging done!")
	else:
		log()
		print("no battery attached?")
		print(chargeData)

def charge(constantCurrent = .2, constantVoltage = 4.2):
	#use threading to allow for non-blocking while-loop checks
	chargeThread = threading.Thread(target=CCCVProfile, args = (constantCurrent, constantVoltage))
	chargeThread.daemon = True
	chargeThread.start()

