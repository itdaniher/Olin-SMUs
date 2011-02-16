import smu, pickle
from pylab import *

smu = smu.smu()

#5v → collector
#ch1 → base
#ch2 → emitter to ground

I_b = []
I_e = []
I_c = []
V_b = arange(0, 1, .001)

for volt in V_b:
	smu.set_voltage(1, volt)
	I_b.append(smu.get_current(1))
	I_e.append(smu.get_current(2))
	#KCL Muthafucka, KCL Goddamn! -cdt
	I_c.append(I_e[-1]-I_b[-1])



