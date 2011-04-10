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

#Vb = 4.30

def getData(fileName, dataName):
	smu1.set_voltage(1, 0)
	smu1.set_current(2, 0)
	dataSet = [[], [], []]
	numV2s = 3
	numV1s = 50
	V2s = linspace(1, 4, 5).tolist()
	for V2 in V2s:
		smu0.set_voltage(1, V2)
		for V1 in linspace(V2-.5, V2+.5, numV1s):
			smu0.set_voltage(2, V1)
			dataSet[V2s.index(V2)].append(getState())
	sio.savemat(fileName, mdict={dataName: dataSet})
	return dataSet

plot([ a[0]-a[2] for a in dataSet[1] ], [ a[5] for a in dataSet[1] ] )

fileName = "pFET-VbBelowThresh-Vout1.mat"
dataName = "VbBelowThresh"
getData(fileName, dataName)
#s11 - Vout2

fileName = "pFET-VbBelowThresh-Vout2.mat"
dataName = "VbBelowThresh"
getData(fileName, dataName)
#s11 - Vout1
