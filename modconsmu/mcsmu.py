#Ian Daniher - Mar11 2011

import sys
import usb.core
import array
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

	def __init__(self):
		"""Find a USB device with the VID and PID of the ModCon SMU."""
		self.dev = usb.core.find(idVendor=0x6666, idProduct=0x0005)
		if self.dev is None:
			sys.exit("Can't find ModCon SMU")
		self.set(self.zero)

	def set(self, value = zero, type = 'i'):
		if type == 'v':
			direction = 0
			value = int(self.zero + value/self.scaleFactorV) 
		elif type == 'i':
			direction = 1
			value = int(self.zero + value * 10000)
		else:
			print("bad type")
		buffer = array.array('b', [0, 0, 0, 0])
		self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = self.vReqs['SET_DIGOUT'], wValue = direction, wIndex = 0, data_or_wLength = buffer)
		return self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['UPDATE'], wValue = value, wIndex = 0, data_or_wLength = 12)

	def get(self):
		VADC_VALS = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['GET_VADC_VALS'], wValue = 0, wIndex = 0, data_or_wLength = 8, timeout = None)
		IADC_VALS = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['GET_IADC_VALS'], wValue = 0, wIndex = 0, data_or_wLength = 8, timeout = None) 
		RES_VAL = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.vReqs['GET_RES_VAL'], wValue = 0, wIndex = 0, data_or_wLength = 8, timeout = None) 
		return (IADC_VALS, VADC_VALS, RES_VAL)
