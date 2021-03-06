#warning. there is a bug somewhere in this code. I do not know where it is.
import usb
import atexit

buffer = []

class smu():
	def __init__(self):
		"""pass smu class instantiation the number of the SMU you want to hook to - multiSMU support hack."""

		# experimental SMU-zeroing-on-close hook
		atexit.register(self.zero)

		# find SMU
		self.dev = usb.core.find(idVendor=0x6666, idProduct=0xABCD)   

		# magic numbers
		self.SET_FN = 0
		self.GET_FN = 1
		self.SET_AUTORANGE = 2
		self.GET_AUTORANGE = 3
		self.SET_IRANGE = 4
		self.GET_IRANGE = 5
		self.SET_VRANGE = 6
		self.GET_VRANGE = 7
		self.SET_DAC = 8
		self.GET_DAC = 9
		self.SET_SRC = 10
		self.GET_SRC = 11
		self.SET_REF = 12
		self.GET_REF = 13
		self.GET_ADC = 14
		self.GET_MEAS = 15
		self.SAVE_REF = 16
		self.LOAD_REF = 17
		self.GET_ADC_KILL60HZ = 18
		self.GET_MEAS_KILL60HZ = 19

		self.OFF = 0
		self.ON = 1

		self.SRCV_MEASI = 0
		self.SRCI_MEASV = 1

		self.OVER_RANGE = 6

		self._20MA = 0
		self._2MA = 1
		self._200UA = 2
		self._20UA = 3
		self._2UA = 4
		self._200NA = 5

		self._10V = 0
		self._4V = 1
		self._2V = 2

		self.set_src_imult = ( 2e5, 2e6, 2e7, 2e8, 2e9, 2e10 )
		self.set_src_vmult = ( 0.4e3, 1e3, 2e3 )
		self.get_src_imult = ( 0.5e-5, 0.5e-6, 0.5e-7, 0.5e-8, 0.5e-9, 0.5e-10 )
		self.get_src_vmult = ( 2.5e-3, 1e-3, 0.5e-3 )
		self.get_meas_imult = ( 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10 )
		self.get_meas_vmult = ( 5e-3, 2e-3, 1e-3 )
		self.get_disp_imult = ( 1e3, 1e3, 1e6, 1e6, 1e6, 1e9 )

	def autorange(self, ch):
		"""
		AUTORANGE Select the best range for measurment on a chanel.
		   AUTORANGE(CH) automatically selects the best measurement range on
		   channel CH, where CH can be either 1 or 2, under software control.
		   Firmware autoranging is disabled upon calling this function.
		"""
		if (ch==1) or (ch==2):
			self.set_autorange(ch, self.OFF)
			done = 0
			while not done:
				buffer = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.GET_MEAS_KILL60HZ, wValue = 0, wIndex = ch, data_or_wLength = 6) 
				#ret = usb.control_transfer(self.dev, 0xC0, self.GET_MEAS_KILL60HZ, 0, ch, 6, buffer)
				res = abs(((buffer[1]<<8)|buffer[0])-((buffer[3]<<8)|buffer[2]))
				range = buffer[4]
				fn = buffer[5]
				if fn==self.SRCV_MEASI:
					if (res>2000) and (range!=self._20MA):
						range = range-1
					elif (res<100) and (range!=self._200NA):
						range = range+1
					else:
						done = 1
					self.set_irange(ch, range)
				else:
					if (res>2000) and (range!=self._10V):
						range = range-1
					elif (res<640) and (range==self._10V):
						range = range+1
					elif (res<800) and (range==self._4V):
						range = range+1
					else:
						done = 1
					self.set_vrange(ch, range)
		else:
			print "Illegal channel specified.\n"

	def close(self):
		"""
		CLOSE Close the SMU.
		   CLOSE closes the SMU.
		"""
		usb.close_device(self.dev)

	def get_autorange(self, ch):
		"""
		GET_AUTORANGE Get the state of firmware autoranging for a chanel.
		   GET_AUTORANGE(CH) returns 1 if firmware autoranging is ON for 
		   chanel CH otherwise it returns 0.  Here CH can be 1 or 2.
		"""
		if (ch==1) or (ch==2):
			buffer = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.GET_AUTORANGE, wValue = 0, wIndex = ch, data_or_wLength = 1) 
			return buffer[0]
		else:
			print "Illegal channel number specified.\n"

	def get_current(self, ch):
		"""
		GET_CURRENT Get the current value for a chanel.
		   GET_CURRENT(CH) returns the current value for chanel CH, where CH
		   can be 1 or 2.  If chanel CH is in SV/MI mode, the value returned is
		   the measured current.  If chanel CH is in SI/MV mode, the value
		   returned is the sourced current.  In either case, the units of the
		   returned value are Amperes.
		"""
		if (ch==1) or (ch==2):
			self.autorange(ch)
			if self.get_function(ch)==self.SRCI_MEASV:
				ret = self.get_source(ch)
				return ret[0]
			else:
				ret = self.get_meas(ch)
				return ret[0]
		else:
			print "Illegal channel number specified.\n"

	def get_function(self, ch):
		"""
		GET_FUNCTION Get the functional mode of a chanel.
		   GET_FUNCTION(CH) returns 1 if chanel CH is in SI/MV mode and it  
		   returns 0 if chanel CH is in SV/MI mode.  Here CH can be 1 or 2.
		"""
		if (ch==1) or (ch==2):
			buffer = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.GET_FN, wValue = 0, wIndex = ch, data_or_wLength = 1) 
			return buffer[0]
		else:
			print "Illegal channel number specified.\n"

	def get_irange(self, ch):
		"""
		GET_IRANGE Get the current range setting of a chanel.
		   GET_IRANGE(CH) returns the current range setting of chanel CH,
		   where CH can be 1 or 2.  The possible return values are as follows:

			  Range	Full-Scale	Minimum Source	Minimum Meas.
			  Number	  Value		Resolution	   Resolution
				0		  20 mA		   5 uA			10 uA
				1		   2 mA		 500 nA			 1 uA
				2		 200 uA		  50 nA		   100 nA
				3		  20 uA		   5 nA			10 nA
				4		   2 uA		 500 pA			 1 nA
				5		 200 nA		  50 pA		   100 pA
		"""
		if (ch==1) or (ch==2):
			buffer = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.GET_IRANGE, wValue = 0, wIndex = ch, data_or_wLength = 1) 
			return buffer[0]
		else:
			print "Illegal channel number specified.\n"

	def get_meas(self, ch):
		"""
		GET_MEAS Get the measurement value for a given chanel.
		   GET_MEAS(CH) returns the measurement value for chanel CH, where CH
		   can be 1 or 2.

		   [VALUE, UNITS]=GET_MEAS(CH) returns the measurement value of 
		   chanel CH in VALUE and the units of the measurement value in UNITS.
		   If UNITS is 0, the measurement units are Amperes (i.e., chanel CH is 
		   in SV/MI mode).  If UNITS is 1, the measurement units are Volts (i.e.,
		   chanel CH is in SI/MV mode).
		"""
		if (ch==1) or (ch==2):
			self.autorange(ch)
			buffer = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.GET_MEAS_KILL60HZ, wValue = 0, wIndex = ch, data_or_wLength = 6) 
			ret = []
			value = ((buffer[1]<<8)|buffer[0])-((buffer[3]<<8)|buffer[2])
			if buffer[5]==self.SRCV_MEASI:
				value = value*self.get_meas_imult[buffer[4]]
				units = 1
			else:
				value = value*self.get_meas_vmult[buffer[4]]
				units = 0
			ret.append(value)
			ret.append(units)
			return ret
		else:
			print "Illegal channel number specified.\n"

	def get_source(self, ch):
		"""
		GET_SOURCE Get the source value for a given chanel.
		   GET_SOURCE(CH) returns the source value for chanel CH, where CH
		   can be 1 or 2.

		   [VALUE, UNITS]=GET_SOURCE(CH) returns the source value of chanel
		   CH in VALUE and the units of the source value in UNITS.  If UNITS is 
		   0, the source units are Volts (i.e., chanel CH is in SV/MI mode).
		   If UNITS is 1, the source units are Amperes (i.e., chanel CH is in 
		   SI/MV mode).
		"""
		if (ch==1) or (ch==2):
			buffer = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.GET_SRC, wValue = 0, wIndex = ch, data_or_wLength = 6) 
			ret = []
			value = ((buffer[1]<<8)|buffer[0])-((buffer[3]<<8)|buffer[2])
			if buffer[5]==self.SRCV_MEASI:
				value = value*self.get_src_vmult[buffer[4]]
			else:
				value = value*self.get_src_imult[buffer[4]]
			ret.append(value)
			ret.append(buffer[5])
			return ret
		else:
			print "Illegal channel number specified.\n"
		
	def get_voltage(self, ch):
		"""
		GET_VOLTAGE Get the voltage value for a chanel.
		   GET_VOLTAGE(CH) returns the voltage value for chanel CH, where CH
		   can be 1 or 2.  If chanel CH is in SV/MI mode, the value returned is
		   the sourced voltage.  If chanel CH is in SI/MV mode, the value
		   returned is the measured voltage.  In either case, the units of the
		   returned value are Volts.
		"""
		if (ch==1) or (ch==2):
			self.autorange(ch)
			if self.get_function(ch)==self.SRCV_MEASI:
				ret = self.get_source(ch)
				return ret[0]
			else:
				ret = self.get_meas(ch)
				return ret[0]
		else:
			print "Illegal channel number specified.\n"

	def get_vrange(self, ch):
		"""
		GET_VRANGE Get the voltage range setting of a chanel.
		   GET_VRANGE(CH) returns the voltage range setting of chanel CH,
		   where CH can be 1 or 2.  The possible return values are as follows:

			  Range	Full-Scale	Minimum Source	Minimum Meas.
			  Number	  Value		Resolution	   Resolution
				0		 10 V		   2.5 mV			5 mV
				1		  4 V			 1 mV			2 mV
				2		  2 V		   500 uV			1 mV
		"""
		if (ch==1) or (ch==2):
			buffer = self.dev.ctrl_transfer(bmRequestType = 0xC0, bRequest = self.GET_VRANGE, wValue = 0, wIndex = ch, data_or_wLength = 1) 
			return buffer[0]
		else:
			print "Illegal channel number specified.\n"

	def set_autorange(self, ch, arange):
		"""
		SET_AUTORANGE Set the state of firmware autoranging for a chanel.
		   SET_AUTORANGE(CH, ARANGE) sets the state of firmware autoranging 
		   for chanel CH to ARANGE.  If ARANGE is 1, firmware autoranging is 
		   turned ON for chanel CH.  If ARANGE is 0, firmware autoranging is 
		   turned OFF for chanel CH.  Here CH can be 1 or 2.
		"""
		if (ch==1) or (ch==2):
			if (arange<0) or (arange>1):
				print "Illegal autorange setting specified.\n"
			else:
				self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = self.SET_AUTORANGE, wValue = arange, wIndex = ch)#, data_or_wLength = 0) 
		else:
			print "Illegal channel number specified.\n"

	def set_current(self, ch, value):
		"""
		SET_CURRENT Set the source value for a chanel to a given current.
		   SET_CURRENT(CH, VALUE) sets chanel CH to SI/MV mode and sets the 
		   sourced current to VALUE Amperes.  Here CH can be 1 or 2.
		"""
		self.set_source(ch, value, self.SRCI_MEASV)

	def set_function(self, ch, fn):
		"""
		SET_FUNCTION Set the functional mode of a chanel.
		   SET_FUNCTION(CH, FN) sets the functional mode of chanel CH to 
		   SV/MI if FN is 0 or to SI/MV if FN is 1.  Here CH can be 1 or 2.
		"""
		if (ch==1) or (ch==2):
			if (fn<0) or (fn>1):
				print "Illegal function specified.\n"
			else:
				self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = self.SET_FN, wValue = fn, wIndex = ch, data_or_wLength = 0) 
		else:
			print "Illegal channel number specified.\n"

	def set_irange(self, ch, irange):
		"""
		SET_IRANGE Set the current range of a chanel.
		   SET_IRANGE(CH, IRANGE) sets the current range of chanel CH to 
		   IRANGE.  Here CH can be 1 or 2.  The possible values of IRANGE are 
		   as follows:

			  Range	Full-Scale	Minimum Source	Minimum Meas.
			  Number	  Value		Resolution	   Resolution
				0		  20 mA		   5 uA			10 uA
				1		   2 mA		 500 nA			 1 uA
				2		 200 uA		  50 nA		   100 nA
				3		  20 uA		   5 nA			10 nA
				4		   2 uA		 500 pA			 1 nA
				5		 200 nA		  50 pA		   100 pA
		"""
		if (ch==1) or (ch==2):
			if (irange<0) or (irange>6):
				print "Illegal current range setting specified.\n"
			else:
				self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = self.SET_IRANGE, wValue = irange, wIndex = ch)
		else:
			print "Illegal channel number specified.\n"

	def set_source(self, ch, value, units):
		"""
		SET_SOURCE Set the source value for a given chanel.
		   SET_SOURCE(CH, VALUE, UNITS) sets the source value of chanel CH 
		   to VALUE Volts if UNITS is 0 (i.e., SV/MI mode) or to VALUE Amperes 
		   if UNITS is 1 (i.e., SI/MV mode).  Here CH can be 1 or 2.
		"""
		if (ch==1) or (ch==2):
			if (units<0) or (units>1):
				print "Illegal units specified.\n"
			else:
				if units==self.SRCV_MEASI:
					if abs(value)>10.0:
						print "Specified source voltage value is out of range.\n"
						range = self.OVER_RANGE
					elif abs(value)>4.0:
						range = self._10V
					elif abs(value)>2.0:
						range = self._4V
					else:
						range = self._2V
				else:
					if abs(value)>20e-3:
						print "Specified source current value is out of range.\n"
						range = self.OVER_RANGE
					elif abs(value)>2e-3:
						range = self._20MA
					elif abs(value)>200e-6:
						range = self._2MA
					elif abs(value)>20e-6:
						range = self._200UA
					elif abs(value)>2e-6:
						range = self._20UA
					elif abs(value)>200e-9:
						range = self._2UA
					else:
						range = self._200NA
				if range!=self.OVER_RANGE:
					if units==self.SRCV_MEASI:
						value = int(round(value*self.set_src_vmult[range]))
					else:
						value = int(round(value*self.set_src_imult[range]))
					if value>0:
						temp = (value<<3)|range
					else:
						temp = 0x8000|((-value)<<3)|range
					self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = self.SET_SRC, wValue = temp, wIndex = (units<<8)|ch)
		else:
			print "Illegal channel number specified.\n"


	def set_voltage(self, ch, value):
		"""
		SET_VOLTAGE Set the source value for a chanel to a given voltage.
		   SET_VOLTAGE(CH, VALUE) sets chanel CH to SV/MI mode and sets the 
		   sourced voltage to VALUE Volts.  Here CH can be 1 or 2.
		"""
		self.set_source(ch, value, self.SRCV_MEASI)

	def set_vrange(self, ch, vrange):
		"""
		SET_VRANGE Set the voltage range of a chanel.
		   SET_VRANGE(CH, VRANGE) sets the voltage range of chanel CH to 
		   VRANGE.  Here CH can be 1 or 2.  The possible values of VRANGE are 
		   as follows:

			  Range	Full-Scale	Minimum Source	Minimum Meas.
			  Number	  Value		Resolution	   Resolution
				0		 10 V		   2.5 mV			5 mV
				1		  4 V			 1 mV			2 mV
				2		  2 V		   500 uV			1 mV
		"""
		if (ch==1) or (ch==2):
			if (vrange<0) or (vrange>3):
				print "Illegal voltage range setting specified.\n"
			else:
				self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = self.SET_VRANGE, wValue = vrange, wIndex = ch)
		else:
			print "Illegal channel number specified.\n"

	def zero(self):
		self.set_current(1, 0)
		self.set_current(2, 0)

if __name__ == "__main__":
	smu = smu()
