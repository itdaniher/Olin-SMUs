import smu, pylab

smu = smu.smu()

data = {}

for amp in pylab.logspace(-9, -2, 60):
    smu.set_current(1, amp)
    data[amp] = smu.get_voltage(1)

pickle.dump( data, open( "exp1.1.p", "wb" ) )

pylab.semilogy(data.values(), data.keys(), 'k.')

for volt in pylab.arange(.2, .7, .005):
	smu.set_voltage(1, volt)
	data[volt] = smu.get_current(1)

pickle.dump( data, open( "exp1.2.p", "wb" ) )

pylab.semilogx(data.keys(), data.values(), 'k.')

clean = dict((k,v/k) for k,v in data.items())

pylab.loglog(clean.keys(), clean.values(), 'k.')

#begin data analysis / plotting

exp1data1 = pickle.load(open("exp1.1.p"))
pylab.semilogx(exp1data1.keys(), exp1data1.values(), 'k.')
pylab.title('current-source V-I characterization of a pseudodiode')
pylab.ylabel('Voltage(V)')
pylab.xlabel('Log of Current(I)')

exp1data1_cleanlog = dict((pylab.log(k),v) for k,v in exp1data1.items() if v > 0.1)  



exp1data2 = pickle.load(open("exp1.2.p"))
pylab.semilogy(exp1data2.keys(), exp1data2.values(), 'k.')
pylab.title('voltage-source V-I characterization of a pseudodiode')
pylab.ylabel('Log of Current (I)')
pylab.xlabel('Voltage(V)')

#pylab.log on current, polyfit to get U_T and I_s
#pylab.diff(V)/pylab.diff(I)

hund = pickle.load(open("exp2.1.p"))
#hund
onek = pickle.load(open("exp2.2.p")) 
#onek
tenk = pickle.load(open("exp2.3.p")) 
#tenk
hunk = pickle.load(open("exp2.4.p")) 
#hunk

pylab.plot(hund[0].keys(), hund[0].values(), 'ro', label='100 $\Omega$')
pylab.plot(onek[0].keys(), onek[0].values(), 'b^', label='1k $\Omega$')
pylab.plot(tenk[0].keys(), tenk[0].values(), 'gs', label='10k $\Omega$')
