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
##Begin Data Analysis

data1 = pickle.load(open("exp1.p"))
clean = dict((k,v) for k,v in data1.items() if v < 7.0)
(m, b) = pylab.polyfit(clean.keys(), clean.values(), 1)
fit = dict((k,k*m+b) for k,v in clean.items())
pylab.plot(clean.keys(), clean.values(), 'k.', label='experimental data')
pylab.plot(fit.keys(), fit.values(), 'r', label='fit line, slope of %.3f V/I($\Omega$)' % m)
pylab.legend(loc = 'upper left')
pylab.xlabel('current (amps)')
pylab.ylabel('voltage (volts)')
pylab.title("Experiment 1 - V-I curve for a 10k Resistor")


data2 = pickle.load(open("exp2.p"))                                                                                                                                                
clean = dict((k,v) for k,v in data2.items() if .4<v/k<.6)
(m, b) = pylab.polyfit(clean.keys(), clean.values(), 1)
fit = dict((k,k*m+b) for k,v in clean.items())
pylab.plot(clean.keys(), clean.values(), 'k.', label='experimental data')
pylab.plot(fit.keys(), fit.values(), 'r', label='fit line, slope of %.3f' % m)
pylab.legend(loc = 'upper left')
pylab.xlabel('$V_{out}$ (volts)')
pylab.ylabel('$V_{in}$ (volts)')
pylab.title("Experiment 2 - V-V curve for a Voltage Divider")


data3 = pickle.load(open("exp3.p"))
clean = dict((k,abs(v)) for k,v in data3.items() if 0.00035<k<0.0009)
(m, b) = pylab.polyfit(clean.keys(), clean.values(), 1)
fit = dict((k,k*m+b) for k,v in clean.items())
pylab.plot(clean.keys(), clean.values(), 'k.', label='experimental data')
pylab.plot(fit.keys(), fit.values(), 'r', label='fit line, slope of %.3f' % m)
pylab.legend(loc = 'upper left')
pylab.xlabel('$I_{out}$ (amps)')
pylab.ylabel('$I_{in}$ (amps)')
pylab.title("Experiment 3 I-I curve for a Current Divider")


n1 = pickle.load(open("exp4.1.p"))
n2 = pickle.load(open("exp4.2.p"))
n3 = pickle.load(open("exp4.3.p"))
n4 = pickle.load(open("exp4.4.p"))

for num in n1.keys():
	v = 'v%s' % num
	vars()[v] = [n1[num], n2[num], n3[num], n4[num]]
	pylab.semilogy(vars()[v], 'o', label="%s volts" % num)

pylab.legend(loc = 'center right')
pylab.xlabel('"2R" Number')
pylab.ylabel('Current Measured (amps)')
pylab.title("Experiment 4 : Current through R-2R Ladder Branches")
pylab.xticks([-1, 0, 1, 2, 3, 4, 5])
pylab.yticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2])
