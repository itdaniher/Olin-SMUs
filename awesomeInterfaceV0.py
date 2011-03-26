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
		timeNow = time.time() 
		output.append(smu.update())
		i.plot(timeNow, output[-1][1], 'k.')
		v.plot(timeNow, output[-1][0], 'k.')
		i.axis([timeNow-10,timeNow+1,-.2,.2])
		v.axis([timeNow-10,timeNow+1,-10,10])
		pylab.draw()
		time.sleep(tick)

showThread = threading.Thread(target=showData)
showThread.daemon = True
showThread.start()

