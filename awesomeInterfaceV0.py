import modconsmu
import pylab
import time
import threading

smu = modconsmu.smu()

pylab.ion()

output = []

tick = .01

def showData():
	i = pylab.subplot(1, 2, 1)
	i.hold(True)
	pylab.ylabel('current')
	v = pylab.subplot(1, 2, 2)
	v.hold(True)
	pylab.ylabel('voltage')
	pylab.draw()
	while True:
		output.append(smu.update())
		i.plot(time.time(), output[-1][1], 'k.')
		v.plot(time.time(), output[-1][0], 'k.')
		i.axis([time.time()-10,time.time()+10,-.2,.2])
		v.axis([time.time()-10,time.time()+10,-10,10])
		pylab.draw()
		time.sleep(tick)

showThread = threading.Thread(target=showData)
showThread.daemon = True
showThread.start()

