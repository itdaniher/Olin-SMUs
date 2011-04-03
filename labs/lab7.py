import circuitsmu
from pylab import *

VbBelowThresh = []
VbAboveThresh = []

smu0 = circuitsmu.smu(0)
smu1 = circuitsmu.smu(1)

def log(data):
	data.append((smu0.get_voltage(1), smu0.get_current(1), smu0.get_voltage(2), smu0.get_current(2), smu1.get_voltage(1), smu1.get_current(1), smu1.get_voltage(2), smu1.get_current(2)))

#s01 - V1
#s02 - V2
#s11 - Vout1
#s12 - V

smu1.set_voltage(1, 5)
smu1.set_current(2, 0)

for v in linspace(2.5, 3.5, 5):
	smu0.set_voltage(1, v)
	for v in linspace(2.5, 3.5, 500):
		smu0.set_voltage(2, v)
		log(VbBelowThresh)

sio.savemat("stuff.mat", mdict={'VbBelowThresh': VbBelowThresh})

for v in linspace(2.5, 3.5, 5):
	smu0.set_voltage(1, v)
	for v in linspace(2.5, 3.5, 500):
		smu0.set_voltage(2, v)
		log(VbAboveThresh)

sio.savemat("stuff1.mat", mdict={'VbAboveThresh': VbAboveThresh})


#move s11 from Vout1 to Vout2
VbBelowThresh = []
VbAboveThresh = []

for v in linspace(2.5, 3.5, 5):
    smu0.set_voltage(1, v)
    for v in linspace(2.5, 3.5, 500):
        smu0.set_voltage(2, v)
        log(VbAboveThresh)

sio.savemat("stuff2.mat", mdict={'VbAboveThresh': VbAboveThresh})

for v in linspace(2.5, 3.5, 5):
    smu0.set_voltage(1, v)
    for v in linspace(2.5, 3.5, 500):
        smu0.set_voltage(2, v)
        log(VbAboveThresh)

sio.savemat("stuff3.mat", mdict={'VbBelowThresh': VbAboveThresh})


