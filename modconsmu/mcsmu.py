#Ian Daniher - Mar11 2011

import sys
import usb.core
import numpy 
"""
if (libusb_control_transfer(udev[i], 0x00, 0x09, 1, 0, buffer, 0, 0) < 0) {
if (libusb_control_transfer(udev[i], 0x40, SET_DIGOUT, digout, 0, buffer, 0, 0) < 0) {
if (libusb_control_transfer(udev[i], 0xC0, GET_DAC_VALS, 0, 0, buffer, 4, 0) < 0) {
if (libusb_control_transfer(udev[i], 0xC0, GET_VADC_VALS, 0, 0, buffer, 4, 0) < 0) {
if (libusb_control_transfer(udev[i], 0xC0, GET_IADC_VALS, 0, 0, buffer, 4, 0) < 0) {
if (libusb_control_transfer(udev[i], 0xC0, GET_RES_VAL, 0, 0, buffer, 2, 0) < 0) {
if (libusb_control_transfer(udev[i], 0xC0, UPDATE, DACA, 0, buffer, 12, 0) < 0) {
if (libusb_control_transfer(udev[i], 0xC0, UPDATE, (uint16_t)dac0[i], 0, buffer, 12, 0) < 0) {
"""

class smu:
	vReqs = {'UPDATE' : 1, 
			'SET_DIGOUT' : 2, 
			'GET_DAC_VALS' : 3,
			'SET_DAC_VALS' : 4,
			'GET_VADC_VALS' : 5,
			'GET_IADC_VALS' : 7,
			'GET_RES_VAL' : 9,
			'GET_NAME' : 11,
			'SET_NAME' : 12}

	zero = 0x07CF
	maxV = 9.93
	minV = -10.45
	scaleFactorV = (minV-maxV)/(2**12)

	v = 0
	i = 0
	master = "i"


	def sign(self, x):
		if x > 32767:
			return 65536-x
		else:
			return x

	def __init__(self):
		"""Find a USB device with the VID and PID of the ModCon SMU."""
		self.dev = usb.core.find(idVendor=0x6666, idProduct=0x0005)
		if self.dev is None:
			sys.exit("Can't find ModCon SMU")
		VADC_VALS = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['GET_VADC_VALS'], wValue = 0, wIndex = 0, data_or_wLength = 4)
		IADC_VALS = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['GET_IADC_VALS'], wValue = 0, wIndex = 0, data_or_wLength = 4)
		RES_VAL = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['GET_RES_VAL'], wValue = 0, wIndex = 0, data_or_wLength = 2)
		DAC_VALS = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['GET_DAC_VALS'], wValue = 0, wIndex = 0, data_or_wLength = 4)
		self.DAC = ( DAC_VALS[0] | ( DAC_VALS[1] << 8 ) ) / 16.0
		VALUE = self.sign( DAC_VALS[2] | DAC_VALS[3] << 8 )
		self.DACGAIN = -200*VALUE/16384.0
		self.VADC = ( VADC_VALS[0] | ( VADC_VALS[1] << 8 ) ) / 16.0
		VALUE = self.sign( VADC_VALS[2] | ( VADC_VALS[3] << 8 ) )
		self.VADCGAIN = 50*VALUE/16384.0
		self.IADC = ( IADC_VALS[0] | ( IADC_VALS[1] << 8 ) ) / 16.0
		VALUE = self.sign( IADC_VALS[2] | ( IADC_VALS[3] << 8 ) )
		self.IADCGAIN = 50*VALUE/16384.0
		VALUE = self.sign( RES_VAL[0] | ( RES_VAL[1] << 8 ) )
		self.RES = 51*VALUE/16384.0
		

	def update(self):
		if self.master == "v":
			value = int(self.zero + self.v/self.scaleFactorV)
			direction = 0
		elif self.master == "i":
			value = int(self.zero + self.i * 10000)
			direction = 1
		else:
			print("bad type")
		data = numpy.zeros(12)
		self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = self.vReqs['SET_DIGOUT'], wValue = direction, wIndex = 0, data_or_wLength = data)
		data = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['UPDATE'], wValue = value, wIndex = 0, data_or_wLength = 12)
		retVolt = ((data[0]|data[1]<<8)-self.VADC)/self.VADCGAIN
		retAmp = ((data[4]|data[5]<<8)-self.IADC)/(self.IADCGAIN*self.RES)
		return (retVolt, retAmp)
