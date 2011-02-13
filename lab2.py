import smu, pylab

smu = smu.smu()

current = pylab.logspace(-9, -2, 60)

data = {}

for amp in pylab.logspace(-9, -2, 60):
    smu.set_current(1, amp)
    data[amp] = smu.get_voltage(1)

pickle.dump( data, open( "exp1.1.p", "wb" ) )

pylab.semilogy(data.values(), data.keys(), 'k.')

for volt in pylab.arange(.2, .7, .05):
	smu.set_voltage(1, volt)
	data[volt] = smu.get_current(1)

pickle.dump( data, open( "exp1.2.p", "wb" ) )

pylab.semilogx(data.keys(), data.values(), 'k.')

clean = dict((k,v/k) for k,v in data.items())

pylab.loglog(clean.keys(), clean.values(), 'k.')


