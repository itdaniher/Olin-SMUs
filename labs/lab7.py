from numpy import linspace
import circuitsmu
from scipy import io as sio


#s01 - V1
#s02 - V2
#s11 - Vout1
#s12 - V

smu0 = circuitsmu.smu(0)
smu1 = circuitsmu.smu(1)

def getState():
	return (smu0.get_voltage(1), smu0.get_current(1), smu0.get_voltage(2), smu0.get_current(2), smu1.get_voltage(1), smu1.get_current(1), smu1.get_voltage(2), smu1.get_current(2))

smu1.set_voltage(1, 5)
smu1.set_current(2, 0)
#Vb = 0.673

VbBelowThresh = [[], [], []]

numV2s = 3
numV1s = 300

V2s = linspace(2.5, 3.5, numV2s).tolist()
V1s = linspace(2.0, 4, numV1s).tolist()

for V2 in V2s:
	smu0.set_voltage(1, V2)
	for V1 in V1s:
		smu0.set_voltage(2, V1)
		VbBelowThresh[V2s.index(V2)].append(getState())

sio.savemat("nFET-VbBelowThresh-Vout1.mat", mdict={'VbBelowThresh': VbBelowThresh})

#s11 - Vout2

VbBelowThresh = [[], [], []]

for V2 in V2s:
	smu0.set_voltage(1, V2)
	for V1 in V1s:
		smu0.set_voltage(2, V1)
		VbBelowThresh[V2s.index(V2)].append(getState())

sio.savemat("nFET-VbBelowThresh-Vout2.mat", mdict={'VbBelowThresh': VbBelowThresh})

#Vb = 0.803
#s11 - Vout1
VbAboveThresh = [[], [], []]

for V2 in V2s:
    smu0.set_voltage(1, V2)
    for V1 in V1s:
        smu0.set_voltage(2, V1)
        VbAboveThresh[V2s.index(V2)].append(getState())

sio.savemat("nFET-VbAboveThresh-Vout1.mat", mdict={'VbAboveThresh': VbAboveThresh})


