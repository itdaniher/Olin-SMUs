import ctypes

usb = ctypes.cdll.LoadLibrary("./smu/_smu.so")
usb.initialize()

buffer = ctypes.c_buffer(64)

class smu():
	def __init__(self):
		self.init()
	
	def init(self, num = 0):
		"""Now need to manually call smu.init(), allowing for use of multiple SMUs on one system."""
		self.dev = usb.open_device(0x6666, 0xABCD, num)
		usb.control_transfer(self.dev, 0x00, 0x09, 1, 0, 0, buffer)
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
		self.GET_DISPLAY = 20

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
		self.get_disp_srci_fmt = ( u'Isrc=%+07.3fmA', u'Isrc=%+07.4fmA', u'Isrc=%+07.2f\u00B5A', u'Isrc=%+07.3f\u00B5A', u'Isrc=%+07.4f\u00B5A', u'Isrc=%+07.2fnA', u'Isrc=%+07.3fnA' )
		self.get_disp_srcv_fmt = ( u'Vsrc=%+08.4fV', u'Vsrc=%+07.4fV ', u'Vsrc=%+07.4fV ' )
		self.get_disp_measi_fmt = ( u'%+06.2fmA', u'%+06.3fmA', u'%+06.1f\u00B5A', u'%+06.2f\u00B5A', u'%+06.3f\u00B5A', u'%+06.1fnA', u'%+06.2fnA' )
		self.get_disp_measv_fmt = ( u'%+07.3fV', u'%+06.3fV ', u'%+06.3fV ' )

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
				ret = usb.control_transfer(self.dev, 0xC0, self.GET_MEAS_KILL60HZ, 0, ch, 6, buffer)
				if ret<0:
					print "Unable to send GET_MEAS_KILL60HZ vendor request.\n"
					done = 1
				else:
					res = abs(((ord(buffer.raw[1])<<8)|ord(buffer.raw[0]))-((ord(buffer.raw[3])<<8)|ord(buffer.raw[2])))
					range = ord(buffer.raw[4])
					fn = ord(buffer.raw[5])
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
			ret = usb.control_transfer(self.dev, 0xC0, self.GET_AUTORANGE, 0, ch, 1, buffer)
			if ret<0:
				print "Unable to send GET_AUTORANGE vendor request.\n"
			else:
				return ord(buffer.raw[0])
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

	def get_display(self):
		"""
		GET_DISPLAY Support function for UPDATE_DISPLAY.
		   GET_DISPLAY is support function for UPDATE_DISPLAY.  You will 
		   probably not want to call it directly in your own scripts.
		"""
		ret = usb.control_transfer(self.dev, 0xC0, self.GET_DISPLAY, 0, 1, 24, buffer)
		if ret<0:
			print "Unable to send GET_DISPLAY vendor request.\n"
		else:
			ret = []
			if ord(buffer.raw[5])==self.SRCV_MEASI:
				value = ((ord(buffer.raw[1])<<8)|ord(buffer.raw[0]))-((ord(buffer.raw[3])<<8)|ord(buffer.raw[2]))
				value = self.get_src_vmult[ord(buffer.raw[4])]*value
				ret.append(self.get_disp_srcv_fmt[ord(buffer.raw[4])] % value)
				value = ((ord(buffer.raw[7])<<8)|ord(buffer.raw[6]))-((ord(buffer.raw[9])<<8)|ord(buffer.raw[8]))
				value = self.get_meas_imult[ord(buffer.raw[10])]*value
				ret.append(self.get_disp_measi_fmt[ord(buffer.raw[10])] % (self.get_disp_imult[ord(buffer.raw[10])]*value))
			else:
				value = ((ord(buffer.raw[1])<<8)|ord(buffer.raw[0]))-((ord(buffer.raw[3])<<8)|ord(buffer.raw[2]))
				value = self.get_src_imult[ord(buffer.raw[4])]*value
				ret.append(self.get_disp_srci_fmt[ord(buffer.raw[4])] % (self.get_disp_imult[ord(buffer.raw[4])]*value))
				value = ((ord(buffer.raw[7])<<8)|ord(buffer.raw[6]))-((ord(buffer.raw[9])<<8)|ord(buffer.raw[8]))
				value = self.get_meas_vmult[ord(buffer.raw[10])]*value
				ret.append(self.get_disp_measv_fmt[ord(buffer.raw[10])] % value)
			if ord(buffer.raw[11])==self.ON:
				ret.append(u'AUTO')
			else:
				ret.append(u'	')
			if ord(buffer.raw[17])==self.SRCV_MEASI:
				value = ((ord(buffer.raw[13])<<8)|ord(buffer.raw[12]))-((ord(buffer.raw[15])<<8)|ord(buffer.raw[14]))
				value = self.get_src_vmult[ord(buffer.raw[16])]*value
				ret.append(self.get_disp_srcv_fmt[ord(buffer.raw[16])] % value)
				value = ((ord(buffer.raw[19])<<8)|ord(buffer.raw[18]))-((ord(buffer.raw[21])<<8)|ord(buffer.raw[20]))
				value = self.get_meas_imult[ord(buffer.raw[22])]*value
				ret.append(self.get_disp_measi_fmt[ord(buffer.raw[22])] % (self.get_disp_imult[ord(buffer.raw[22])]*value))
			else:
				value = ((ord(buffer.raw[13])<<8)|ord(buffer.raw[12]))-((ord(buffer.raw[15])<<8)|ord(buffer.raw[14]))
				value = self.get_src_imult[ord(buffer.raw[16])]*value
				ret.append(self.get_disp_srci_fmt[ord(buffer.raw[16])] % (self.get_disp_imult[ord(buffer.raw[16])]*value))
				value = ((ord(buffer.raw[19])<<8)|ord(buffer.raw[18]))-((ord(buffer.raw[21])<<8)|ord(buffer.raw[20]))
				value = self.get_meas_vmult[ord(buffer.raw[22])]*value
				ret.append(self.get_disp_measv_fmt[ord(buffer.raw[22])] % value)
			if ord(buffer.raw[23])==self.ON:
				ret.append(u'AUTO')
			else:
				ret.append(u'	')
			return ret

	def get_function(self, ch):
		"""
		GET_FUNCTION Get the functional mode of a chanel.
		   GET_FUNCTION(CH) returns 1 if chanel CH is in SI/MV mode and it  
		   returns 0 if chanel CH is in SV/MI mode.  Here CH can be 1 or 2.
		"""
		if (ch==1) or (ch==2):
			ret = usb.control_transfer(self.dev, 0xC0, self.GET_FN, 0, ch, 1, buffer)
			if ret<0:
				print "Unable to send GET_FN vendor request.\n"
			else:
				return ord(buffer.raw[0])
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
			ret = usb.control_transfer(self.dev, 0xC0, self.GET_IRANGE, 0, ch, 1, buffer)
			if ret<0:
				print "Unable to send GET_IRANGE vendor request.\n"
			else:
				return ord(buffer.raw[0])
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
			ret = usb.control_transfer(self.dev, 0xC0, self.GET_MEAS_KILL60HZ, 0, ch, 6, buffer)
			if ret<0:
				print "Unable to send GET_MEAS_KILL60HZ vendor request.\n"
			else:
				ret = []
				value = ((ord(buffer.raw[1])<<8)|ord(buffer.raw[0]))-((ord(buffer.raw[3])<<8)|ord(buffer.raw[2]))
				if ord(buffer.raw[5])==self.SRCV_MEASI:
					value = value*self.get_meas_imult[ord(buffer.raw[4])]
					units = 1
				else:
					value = value*self.get_meas_vmult[ord(buffer.raw[4])]
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
			ret = usb.control_transfer(self.dev, 0xC0, self.GET_SRC, 0, ch, 6, buffer)
			if ret<0:
				print "Unable to send GET_SRC vendor request.\n"
			else:
				ret = []
				value = ((ord(buffer.raw[1])<<8)|ord(buffer.raw[0]))-((ord(buffer.raw[3])<<8)|ord(buffer.raw[2]))
				if ord(buffer.raw[5])==self.SRCV_MEASI:
					value = value*self.get_src_vmult[ord(buffer.raw[4])]
				else:
					value = value*self.get_src_imult[ord(buffer.raw[4])]
				ret.append(value)
				ret.append(ord(buffer.raw[5]))
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
			ret = usb.control_transfer(self.dev, 0xC0, self.GET_VRANGE, 0, ch, 1, buffer)
			if ret<0:
				print "Unable to send GET_VRANGE vendor request.\n"
			else:
				return ord(buffer.raw[0])
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
				ret = usb.control_transfer(self.dev, 0x40, self.SET_AUTORANGE, arange, ch, 0, buffer)
				if ret<0:
					print "Unable to send SET_AUTORANGE vendor request.\n"
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
				ret = usb.control_transfer(self.dev, 0x40, self.SET_FN, fn, ch, 0, buffer)
				if ret<0:
					print "Unable to send SET_FN vendor request.\n"
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
				ret = usb.control_transfer(self.dev, 0x40, self.SET_IRANGE, irange, ch, 0, buffer)
				if ret<0:
					print "Unable to send SET_IRANGE vendor request.\n"
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
					ret = usb.control_transfer(self.dev, 0x40, self.SET_SRC, temp, (units<<8)|ch, 0, buffer)
					if ret<0:
						print "Unable to send SET_SRC vendor request.\n"
		else:
			print "Illegal channel number specified.\n"

	def set_src_str(self, ch, str):
		"""
		SET_SRC_STR Set the source value of a given chanel from a string.
		   SET_SRC_STR(CH, STR) sets the source value of chanel CH 
		   to the value specified in the string STR.  Here CH can be 1 or 2.
		   If STR contains units, the mode of chanel CH will change if 
		   necessary.  The units can also include one of the following prefixes: 
		   'm' for milli, 'u' for micro, 'n' for nano, and 'p' for pico.
		"""
		if len(str)!=0:
			if (ch==1) or (ch==2):
				fn = self.get_function(ch)
				if (str[len(str)-1]=='A') or (str[len(str)-1]=='a'):
					fn = 1
					str = str[0:len(str)-1]
				elif (str[len(str)-1]=='V') or (str[len(str)-1]=='v'):
					fn = 0
					str = str[0:len(str)-1]
				mult = 1
				if (str[len(str)-1]=='P') or (str[len(str)-1]=='p'):
					mult = 1e-12
					str = str[0:len(str)-1]
				elif (str[len(str)-1]=='N') or (str[len(str)-1]=='n'):
					mult = 1e-9
					str = str[0:len(str)-1]
				elif (str[len(str)-1]=='U') or (str[len(str)-1]=='u'):
					mult = 1e-6
					str = str[0:len(str)-1]
				elif (str[len(str)-1]=='M') or (str[len(str)-1]=='m'):
					mult = 1e-3
					str = str[0:len(str)-1]
				value = float(str)*mult
				self.set_source(ch, value, fn)
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
				ret = usb.control_transfer(self.dev, 0x40, self.SET_VRANGE, vrange, ch, 0, buffer)
				if ret<0:
					print "Unable to send SET_VRANGE vendor request.\n"
		else:
			print "Illegal channel number specified.\n"
