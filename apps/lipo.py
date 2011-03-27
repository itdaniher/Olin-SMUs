import modconsmu
import time
import threading
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("km-dockstar", 8098))

smu = modconsmu.smu()

chargeData = []
tick = 1

if raw_input("do you absolve the author of this code of all responsibility related to its use? (yes/no)") != "yes":
	quit()

def log():
	#time, (voltage, current)
	data = ( time.time(), smu.update() )
	upData = "%f %f %f" % (data[0], data[1][0], abs(data[1][1]))
	sock.send(upData)
	chargeData.append(data)

def chargeProfile():
	log()
	smu.set(amps = .2)
	while smu.update()[0] < 4.2:
		log()
		time.sleep(tick)
	smu.set(volts = 4.2)
	while abs(smu.update()[1]) > .05:
		log()
		time.sleep(tick)
	smu.set(amps = 0)
	if ( chargeData[-1][0] - chargeData[0][0] ) > 10:
		log()
		print("charging done!")
	else:
		print("no battery attached?")

def charge():
	chargeThread = threading.Thread(target=chargeProfile)
	chargeThread.daemon = True
	chargeThread.start()

