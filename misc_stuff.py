import smu, numpy, pickle

smu = smu.smu()

data = {}

for v in numpy.arange(1, 5, .05):
	smu.set_voltage(1, v)
	data[v]=smu.get_voltage(2)

for v in numpy.arange(1, 5, .05):
	smu.set_current(2, 0)
    smu.set_voltage(1, v)  
    data[v]=smu.get_voltage(2)

for a in numpy.arange(.0001, .01, .00005):
    smu.set_voltage(2, 0)
    smu.set_current(1, a)
    data[a]=smu.get_current(2)


pickle.dump( data, open( "exp1.p", "wb" ) )

