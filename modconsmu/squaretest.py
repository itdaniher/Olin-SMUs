import mcsmu
import numpy

smu = mcsmu.smu()

c = 10000

h = c*[5]
l = c*[0]

smu.update()

smu.master = 'v'
smu.updateNeeded = 1

for i in range(len(h)):
	smu.v = h[i]
	smu.update()
	smu.v = l[i]
	smu.update()
