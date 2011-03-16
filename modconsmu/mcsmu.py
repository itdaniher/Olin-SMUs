#Ian Daniher - Mar11 2011

import sys
import usb.core

class smu:
	vReqs = {'UPDATE' : 1, 
			'SET_DIGOUT' : 2, 
			'GET_DAC_VALS' : 3,
			'SET_DAC_VALS' : 4,
			'GET_VADC_VALS' : 5,
			'SET_VADC_VALS' : 6,
			'GET_IADC_VALS' : 7,
			'SET_IADC_VALS' : 8,
			'GET_RES_VAL' : 9,
			'SET_RES_VAL' : 10,
			'GET_NAME' : 11,
			'SET_NAME' : 12}

	def __init__(self):
		"""Find a USB device with the VID and PID of the ModCon SMU."""
		self.dev = usb.core.find(idVendor=0x6666, idProduct=0x0005)
		if self.dev is None:
			sys.exit("Can't find ModCon SMU")

	def setMotors(self, valMotorA, valMotorB):
		"""Arguments should be in form of a number between 0 and 100, positive or negative. Magic numbers used for the ctrl_transfer derived from sniffing USB coms."""
		self.valMotorA = self.processMotorValues(valMotorA)
		self.valMotorB = self.processMotorValues(valMotorB)
		data = [64, self.valMotorA&0xFF, self.valMotorB&0xFF, 0x00, 0x00, 0x00, 0x00, 0x00]
		self.dev.ctrl_transfer(bmRequestType = 0x21, bRequest = 0x09, wValue = 0x0200, wIndex = 0, data_or_wLength = data)


	def getData(self):
		"""Sensor data is contained in the 2nd and 4th byte, with sensor IDs being contained in the 3rd and 5th byte respectively."""
		rawData = self.getRawData()
		sensorData = {rawData[3]: rawData[2], rawData[5]: rawData[4]}
		return sensorData