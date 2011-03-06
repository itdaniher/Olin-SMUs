import smu, pickle
from pylab import *

smu = smu.smu()

#5v → collector
#ch1 → base
#ch2 → emitter to ground

def tranSweep(V_i, V_o, V_step, fileName):
	I_b = []
	I_e = []
	I_c = []
	V_b = arange(V_i, V_o, V_step)
	for volt in V_b:
		smu.set_voltage(1, volt)
		I_b.append(smu.get_current(1))
		I_e.append(smu.get_current(2))
		#KCL Muthafucka, KCL Goddamn! -cdt
		I_c.append(I_e[-1]-I_b[-1])
	pickle.dump( (I_e, I_b, I_c, V_b) , open( fileName, "wb" ) )
	return (I_e, I_b, I_c, V_b)

tranSweep(0, 1, .001, "exp1.p")

def tranSweep(V_i, V_o, V_step, fileName):
    V_b = arange(V_i, V_o, V_step)
	V_o = []
	for volt in V_b:
		smu.set_voltage(1, volt)
		V_o.append(smu.get_voltage(2))
	pickle.dump( (V_b, V_o) , open( fileName, "wb" ) )

tranSweep(0, 5, .001, 'exp3.1000.p')
tranSweep(0, 5, .001, 'exp4.2000.p')
tranSweep(0, 5, .001, 'exp4.3900.p')
tranSweep(0, 5, .001, 'exp4.5100.p')
  
