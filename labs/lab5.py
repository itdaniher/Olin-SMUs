import smu
smu = smu.smu()
from pylab import *
import pickle

V_dd = 5

def FETSweep(V_i, V_o, V_step, fileName):
    I_d = []
    V_d = []
    V_g = arange(V_i, V_o, V_step)
    for volt in V_g:
        smu.set_voltage(1, volt)
		V_d.append(V_dd)
		smu.set_voltage(2, V_dd)
		I_d.append(smu.get_current(2))
    pickle.dump( (I_d, V_d, V_g) , open( fileName, "wb" ) )
	return (I_d, V_d, V_g)

def FETSweep(V_i, V_o, V_step, fileName):
    I_s = []
    V_s = arange(V_i, V_o, V_step)
    for volt in V_s:
        smu.set_voltage(1, volt)
        I_s.append(smu.get_current(1))
    pickle.dump( (I_s, V_s) , open( fileName, "wb" ) )
    return (I_s, V_s)

V_thresh = .7

smu.set_voltage(1, V_thresh-.1)

I_d = []
V_d = []

for volt in arange(0, 5, .005):
	smu.set_voltage(2, volt)
	I_d.append(smu.get_current(2))
	V_d.append(volt)

pickle.dump( (I_d, V_d) , open( 'exp3.subThresh.6vnfet.p', "wb" ) )

smu.set_voltage(1, V_thresh)

I_d = []
V_d = []

for volt in arange(0, 5, .005):
    smu.set_voltage(2, volt)
    I_d.append(smu.get_current(2))
    V_d.append(volt)

pickle.dump( (I_d, V_d) , open( 'exp3.Thresh.7vnfet.p', "wb" ) )

