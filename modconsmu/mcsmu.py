#Ian Daniher - Mar11 2011

import sys
import usb.core

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

	def __init__(self):
		"""Find a USB device with the VID and PID of the ModCon SMU."""
		self.dev = usb.core.find(idVendor=0x6666, idProduct=0x0005)
		if self.dev is None:
			sys.exit("Can't find ModCon SMU")

	def set(type = 'voltage', value):
		if type == voltage:
			direction = 1
		elif type == current:
			direction = 0
		else:
			print("bad type value")
		data = [0, 0, 0, 0, 0, 0, 0, 0]
		self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = vReqs['SET_DIGOUT'], wValue = direction, wIndex = 0, data_or_wLength = data)
		scaleValue = lambda x: int(x)
		self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = vReqs['UPDATE'], wValue = , wIndex = 0, data_or_wLength = data)
		

#	data = [64, self.valMotorA&0xFF, self.valMotorB&0xFF, 0x00, 0x00, 0x00, 0x00, 0x00]
#	self.dev.ctrl_transfer(bmRequestType = 0x21, bRequest = 0x09, wValue = 0x0200, wIndex = 0, data_or_wLength = data)
