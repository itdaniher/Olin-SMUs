import mcsmu
import numpy

smu = mcsmu.smu()

smu.master = 'v'

for v in numpy.sin(numpy.arange(0, 1000*2*numpy.pi, .125)):
	smu.v = v
	smu.update()
