import smu, numpy, pickle

smu = smu.smu()

for a in numpy.arange(.0001, .01, .00005):
	smu.set_current(1, a)
	data[a]=smu.get_voltage(1)


pickle.dump( data, open( "exp1.p", "wb" ) )

