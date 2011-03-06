#include <p18f2455.h>
#include "usb_defs.h"

#pragma config PLLDIV = 1
#pragma config CPUDIV = OSC1_PLL2
#pragma config USBDIV = 2
#pragma config FOSC = XTPLL_XT
#pragma config FCMEM = OFF
#pragma config IESO = OFF
#pragma config PWRT = OFF
#pragma config BOR = ON
#pragma config BORV = 3
#pragma config VREGEN = ON
#pragma config WDT = OFF
#pragma config WDTPS = 32768
#pragma config MCLRE = ON
#pragma config LPT1OSC = OFF
#pragma config PBADEN = OFF
#pragma config CCP2MX = ON
#pragma config STVREN = ON
#pragma config LVP = OFF
//#pragma config ICPRT = OFF
#pragma config XINST = OFF
#pragma config DEBUG = OFF
#pragma config CP0 = OFF
#pragma config CP1 = OFF
#pragma config CP2 = OFF
//#pragma config CP3 = OFF
#pragma config CPB = OFF
#pragma config CPD = OFF
#pragma config WRT0 = OFF
#pragma config WRT1 = OFF
#pragma config WRT2 = OFF
//#pragma config WRT3 = OFF
#pragma config WRTB = OFF
#pragma config WRTC = OFF
#pragma config WRTD = OFF
#pragma config EBTR0 = OFF
#pragma config EBTR1 = OFF
#pragma config EBTR2 = OFF
//#pragma config EBTR3 = OFF
#pragma config EBTRB = OFF

#define SET_FN				0
#define GET_FN				1
#define SET_AUTORANGE		2
#define GET_AUTORANGE		3
#define SET_IRANGE			4
#define GET_IRANGE			5
#define SET_VRANGE			6
#define GET_VRANGE			7
#define SET_DAC				8
#define GET_DAC				9
#define SET_SRC				10
#define GET_SRC				11
#define SET_REF				12
#define GET_REF				13
#define GET_ADC				14
#define GET_MEAS			15
#define SAVE_REF			16
#define LOAD_REF			17
#define GET_ADC_KILL60HZ	18
#define GET_MEAS_KILL60HZ	19
#define GET_DISPLAY			20

#define CH1					0
#define CH2					1

#define OFF					0
#define ON					1

#define SRCV_MEASI			0
#define SRCI_MEASV			1

#define _20MA				0
#define _2MA				1
#define _200UA				2
#define _20UA				3
#define _2UA				4
#define _200NA				5
#define _20NA				6
#define _OPEN				7

#define _10V				0
#define _4V					1
#define _2V					2

void UpdateFunction1(void);
void UpdateIrange1(void);
void UpdateVrange1(void);
void UpdateFunction2(void);
void UpdateIrange2(void);
void UpdateVrange2(void);

#pragma udata
BUFDESC USB_buffer_desc;
unsigned char USB_buffer_data[8];
unsigned char USB_error_flags;
unsigned char USB_curr_config;
unsigned char USB_device_status;
unsigned char USB_dev_req;
unsigned char USB_address_pending;
unsigned char rom *USB_desc_ptr;
unsigned char USB_bytes_left;
unsigned char USB_packet_length;
unsigned char USB_USTAT;
unsigned char USB_USWSTAT;

unsigned char AUTORANGE[2];
unsigned char FUNCTION[2];
unsigned char IRANGE[2];
unsigned char VRANGE[2];
unsigned char DACAL[2];
unsigned char DACAH[2];
unsigned char DACBL[2];
unsigned char DACBH[2];
unsigned int REF[2][2][7];

#pragma romdata
rom const unsigned char Device[] = {
	0x12,	// bLength
	DEVICE,	// bDescriptorType
	0x10,	// bcdUSB (low byte)
	0x01,	// bcdUSB (high byte)
	0x00,	// bDeviceClass
	0x00,	// bDeviceSubClass
	0x00,	// bDeviceProtocol
	MAX_PACKET_SIZE,	// bMaxPacketSize
	0x66,	// idVendor (low byte)
	0x66,	// idVendor (high byte)
	0x34,	// idProduct (low byte)
	0x12,	// idProduct (high byte)
	0x00,	// bcdDevice (low byte)
	0x00,	// bcdDevice (high byte)
	0x01,	// iManufacturer
	0x02,	// iProduct
	0x00,	// iSerialNumber (none)
	NUM_CONFIGURATIONS	// bNumConfigurations
};

rom const unsigned char Configuration1[] = {
	0x09,	// bLength
	CONFIGURATION,	// bDescriptorType
	0x12,	// wTotalLength (low byte)
	0x00,	// wTotalLength (high byte)
	NUM_INTERFACES,	// bNumInterfaces
	0x01,	// bConfigurationValue
	0x00,	// iConfiguration (none)
	0xA0,	// bmAttributes
	0x32,	// bMaxPower (100 mA)
	0x09,	// bLength (Interface1 descriptor starts here)
	INTERFACE,	// bDescriptorType
	0x00,	// bInterfaceNumber
	0x00,	// bAlternateSetting
	0x00,	// bNumEndpoints (excluding EP0)
	0xFF,	// bInterfaceClass (vendor specific class code)
	0x00,	// bInterfaceSubClass
	0xFF,	// bInterfaceProtocol (vendor specific protocol used)
	0x00	// iInterface (none)
};

rom const unsigned char String0[] = {
	0x04,	// bLength
	STRING,	// bDescriptorType
	0x09,	// wLANGID[0] (low byte)
	0x04	// wLANGID[0] (high byte)
};

rom const unsigned char String1[] = {
	0x1A,	// bLength
	STRING,	// bDescriptorType
	'O', 0x00, 'l', 0x00, 'i', 0x00, 'n', 0x00, ' ', 0x00, 
	'C', 0x00, 'o', 0x00, 'l', 0x00, 'l', 0x00, 'e', 0x00, 'g', 0x00, 'e', 0x00
};

rom const unsigned char String2[] = {
	0x30,	// bLength
	STRING,	// bDescriptorType
	'U', 0x00, 'S', 0x00, 'B', 0x00, ' ', 0x00,
	'S', 0x00, 'o', 0x00, 'u', 0x00, 'r', 0x00, 'c', 0x00, 'e', 0x00, '/', 0x00,
	'M', 0x00, 'e', 0x00, 'a', 0x00, 's', 0x00, 'u', 0x00, 'r', 0x00, 'e', 0x00, ' ', 0x00,
	'U', 0x00, 'n', 0x00, 'i', 0x00, 't', 0x00
};

#pragma code
void InitUSB(void) {
	UIE = 0x00;					// mask all USB interrupts
	UIR = 0x00;					// clear all USB interrupt flags
	UCFG = 0x14;				// configure USB for full-speed transfers and to use the on-chip transciever and pull-up resistor
	UCON = 0x08;				// enable the USB module and its supporting circuitry
	USB_curr_config = 0x00;
	USB_USWSTAT = 0x00;			// default to powered state
	USB_device_status = 0x01;
	USB_dev_req = NO_REQUEST;	// No device requests in process
#ifdef SHOW_ENUM_STATUS
	TRISB = 0x00;				// set all bits of PORTB as outputs
	PORTB = 0x01;				// set bit zero to indicate Powered status
#endif
	while (UCONbits.SE0);		// wait for the first SE0 to end
}

void ServiceUSB(void) {
	BUFDESC *buf_desc_ptr;

	if (UIRbits.UERRIF) {
		UEIR = 0x00;
	} else if (UIRbits.SOFIF) {
		UIRbits.SOFIF = 0;
	} else if (UIRbits.IDLEIF) {
		UIRbits.IDLEIF = 0;
		UCONbits.SUSPND = 1;
#ifdef SHOW_ENUM_STATUS
		PORTB &= 0xE0;
		PORTBbits.RB4 = 1;
#endif
	} else if (UIRbits.ACTVIF) {
		UIRbits.ACTVIF = 0;
		UCONbits.SUSPND = 0;
#ifdef SHOW_ENUM_STATUS
		PORTB &= 0xE0;
		PORTB |= 0x01<<USB_USWSTAT;
#endif
	} else if (UIRbits.STALLIF) {
		UIRbits.STALLIF = 0;
	} else if (UIRbits.URSTIF) {
		USB_curr_config = 0x00;
		UIRbits.TRNIF = 0;		// clear TRNIF four times to clear out the USTAT FIFO
		UIRbits.TRNIF = 0;
		UIRbits.TRNIF = 0;
		UIRbits.TRNIF = 0;
		UEP0 = 0x00;				// clear all EP control registers to disable all endpoints
		UEP1 = 0x00;
		UEP2 = 0x00;
		UEP3 = 0x00;
		UEP4 = 0x00;
		UEP5 = 0x00;
		UEP6 = 0x00;
		UEP7 = 0x00;
		UEP8 = 0x00;
		UEP9 = 0x00;
		UEP10 = 0x00;
		UEP11 = 0x00;
		UEP12 = 0x00;
		UEP13 = 0x00;
		UEP14 = 0x00;
		UEP15 = 0x00;
		BD0O.bytecount = MAX_PACKET_SIZE;
		BD0O.address = EP0_OUT_buffer;	// EP0 OUT gets a buffer
		BD0O.status = 0x88;				// set UOWN bit (USB can write)
		BD0I.address = EP0_IN_buffer;	// EP0 IN gets a buffer
		BD0I.status = 0x08;				// clear UOWN bit (MCU can write)
		UADDR = 0x00;				// set USB Address to 0
		UIR = 0x00;				// clear all the USB interrupt flags
		UEP0 = ENDPT_CONTROL;	// EP0 is a control pipe and requires an ACK
		UEIE = 0xFF;			// enable all error interrupts
		USB_USWSTAT = DEFAULT_STATE;
		USB_device_status = 0x01;	// self powered, remote wakeup disabled
#ifdef SHOW_ENUM_STATUS
		PORTB &= 0xE0;
		PORTBbits.RB1 = 1;		// set bit 1 of PORTB to indicate Powered state
#endif
	} else if (UIRbits.TRNIF) {
		buf_desc_ptr = (BUFDESC *)((unsigned char *)(&BD0O)+(USTAT&0x7C));	// mask out bits 0, 1, and 7 of USTAT for offset into the buffer descriptor table
		USB_buffer_desc.status = buf_desc_ptr->status;
		USB_buffer_desc.bytecount = buf_desc_ptr->bytecount;
		USB_buffer_desc.address = buf_desc_ptr->address;
		USB_USTAT = USTAT;		// save the USB status register
		UIRbits.TRNIF = 0;		// clear TRNIF interrupt flag
#ifdef SHOW_ENUM_STATUS
		switch (USB_USTAT&0x18) {	// toggle bit 5, 6, or 7 of PORTB to reflect EP0, EP1, or EP2 activity
			case EP0:
				PORTB ^= 0x20;
				break;
			case EP1:
				PORTB ^= 0x40;
				break;
			case EP2:
				PORTB ^= 0x80;
		}
#endif
		USB_error_flags = 0x00;	// clear USB error flags
		switch (USB_buffer_desc.status&0x3C) {	// extract PID bits
			case TOKEN_SETUP:
				ProcessSetupToken();
				break;
			case TOKEN_IN:
				ProcessInToken();
				break;
			case TOKEN_OUT:
				ProcessOutToken();
		}
		if (USB_error_flags&0x01) {		// if there was a Request Error...
			BD0O.bytecount = MAX_PACKET_SIZE;	// ...get ready to receive the next Setup token...
			BD0I.status = 0x84;
			BD0O.status = 0x84;					// ...and issue a protocol stall on EP0
		}
	}
}

void ProcessSetupToken(void) {
	unsigned char n;

	for (n = 0; n<8; n++) {
		USB_buffer_data[n] = USB_buffer_desc.address[n];
	}
	BD0O.bytecount = MAX_PACKET_SIZE;	// reset the EP0 OUT byte count
	BD0I.status = 0x08;			// return the EP0 IN buffer to us (dequeue any pending requests)			
	BD0O.status = (!(USB_buffer_data[bmRequestType]&0x80) && (USB_buffer_data[wLength] || USB_buffer_data[wLengthHigh])) ? 0xC8:0x88;	// set EP0 OUT UOWN back to USB and DATA0/DATA1 packet according to the request type
	UCONbits.PKTDIS = 0;			// assuming there is nothing to dequeue, clear the packet disable bit
	USB_dev_req = NO_REQUEST;		// clear the device request in process
	switch (USB_buffer_data[bmRequestType]&0x60) {	// extract request type bits
		case STANDARD:
			StandardRequests();
			break;
		case CLASS:
			ClassRequests();
			break;
		case VENDOR:
			VendorRequests();
			break;
		default:
			USB_error_flags |= 0x01;	// set Request Error Flag
	}
}

void StandardRequests(void) {
	unsigned char *UEP;
	unsigned char n;
	BUFDESC *buf_desc_ptr;

	switch (USB_buffer_data[bRequest]) {
		case GET_STATUS:
			switch (USB_buffer_data[bmRequestType]&0x1F) {	// extract request recipient bits
				case RECIPIENT_DEVICE:
					BD0I.address[0] = USB_device_status;
					BD0I.address[1] = 0x00;
					BD0I.bytecount = 0x02;
					BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
					break;
				case RECIPIENT_INTERFACE:
					switch (USB_USWSTAT) {
						case ADDRESS_STATE:
							USB_error_flags |= 0x01;	// set Request Error Flag
							break;
						case CONFIG_STATE:
							if (USB_buffer_data[wIndex]<NUM_INTERFACES) {
								BD0I.address[0] = 0x00;
								BD0I.address[1] = 0x00;
								BD0I.bytecount = 0x02;
								BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
							} else {
								USB_error_flags |= 0x01;	// set Request Error Flag
							}
					}
					break;
				case RECIPIENT_ENDPOINT:
					switch (USB_USWSTAT) {
						case ADDRESS_STATE:
							if (!(USB_buffer_data[wIndex]&0x0F)) {	// get EP, strip off direction bit and see if it is EP0
								BD0I.address[0] = (((USB_buffer_data[wIndex]&0x80) ? BD0I.status:BD0O.status)&0x04)>>2;	// return the BSTALL bit of EP0 IN or OUT, whichever was requested
								BD0I.address[1] = 0x00;
								BD0I.bytecount = 0x02;
								BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
							} else {
								USB_error_flags |= 0x01;	// set Request Error Flag
							}
							break;
						case CONFIG_STATE:
							UEP = (unsigned char *)&UEP0;
							n = USB_buffer_data[wIndex]&0x0F;	// get EP and strip off direction bit for offset from UEP0
							buf_desc_ptr = &BD0O+((n<<1)|((USB_buffer_data[wIndex]&0x80) ? 0x01:0x00));	// compute pointer to the buffer descriptor for the specified EP
							if (UEP[n]&((USB_buffer_data[wIndex]&0x80) ? 0x02:0x04)) { // if the specified EP is enabled for transfers in the specified direction...
								BD0I.address[0] = ((buf_desc_ptr->status)&0x04)>>2;	// ...return the BSTALL bit of the specified EP
								BD0I.address[1] = 0x00;
								BD0I.bytecount = 0x02;
								BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
							} else {
								USB_error_flags |= 0x01;	// set Request Error Flag
							}
							break;
						default:
							USB_error_flags |= 0x01;	// set Request Error Flag
					}
					break;
				default:
					USB_error_flags |= 0x01;	// set Request Error Flag
			}
			break;
		case CLEAR_FEATURE:
		case SET_FEATURE:
			switch (USB_buffer_data[bmRequestType]&0x1F) {	// extract request recipient bits
				case RECIPIENT_DEVICE:
					switch (USB_buffer_data[wValue]) {
						case DEVICE_REMOTE_WAKEUP:
							if (USB_buffer_data[bRequest]==CLEAR_FEATURE)
								USB_device_status &= 0xFE;
							else
								USB_device_status |= 0x01;
							BD0I.bytecount = 0x00;		// set EP0 IN byte count to 0
							BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
							break;
						default:
							USB_error_flags |= 0x01;	// set Request Error Flag
					}
					break;
				case RECIPIENT_ENDPOINT:
					switch (USB_USWSTAT) {
						case ADDRESS_STATE:
							if (!(USB_buffer_data[wIndex]&0x0F)) {	// get EP, strip off direction bit, and see if its EP0
								BD0I.bytecount = 0x00;		// set EP0 IN byte count to 0
								BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
							} else {
								USB_error_flags |= 0x01;	// set Request Error Flag
							}
							break;
						case CONFIG_STATE:
							UEP = (unsigned char *)&UEP0;
							if (n = USB_buffer_data[wIndex]&0x0F) {	// get EP and strip off direction bit for offset from UEP0, if not EP0...
								buf_desc_ptr = &BD0O+((n<<1)|((USB_buffer_data[wIndex]&0x80) ? 0x01:0x00));	// compute pointer to the buffer descriptor for the specified EP
								if (USB_buffer_data[wIndex]&0x80) {	// if the specified EP direction is IN...
									if (UEP[n]&0x02) {	// if EPn is enabled for IN transfers...
										buf_desc_ptr->status = (USB_buffer_data[bRequest]==CLEAR_FEATURE) ? 0x00:0x84;
									} else {
										USB_error_flags |= 0x01;	// set Request Error Flag									
									}
								} else {	// ...otherwise the specified EP direction is OUT, so...
									if (UEP[n]&0x04) {	// if EPn is enabled for OUT transfers...
										buf_desc_ptr->status = (USB_buffer_data[bRequest]==CLEAR_FEATURE) ? 0x88:0x84;
									} else {
										USB_error_flags |= 0x01;	// set Request Error Flag									
									}
								}
							}
							if (!(USB_error_flags&0x01)) {	// if there was no Request Error...
								BD0I.bytecount = 0x00;
								BD0I.status = 0xC8;		// ...send packet as DATA1, set UOWN bit
							}
							break;
						default:
							USB_error_flags |= 0x01;	// set Request Error Flag
					}
					break;
				default:
					USB_error_flags |= 0x01;	// set Request Error Flag
			}
			break;
		case SET_ADDRESS:
			if (USB_buffer_data[wValue]>0x7F) {	// if new device address is illegal, send Request Error
				USB_error_flags |= 0x01;	// set Request Error Flag
			} else {
				USB_dev_req = SET_ADDRESS;	// processing a SET_ADDRESS request
				USB_address_pending = USB_buffer_data[wValue];	// save new address
				BD0I.bytecount = 0x00;		// set EP0 IN byte count to 0
				BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			}
			break;
		case GET_DESCRIPTOR:
			USB_dev_req = GET_DESCRIPTOR;	// processing a GET_DESCRIPTOR request
			switch (USB_buffer_data[wValueHigh]) {
				case DEVICE:
					USB_desc_ptr = Device;
					USB_bytes_left = USB_desc_ptr[0];
					if ((USB_buffer_data[wLengthHigh]==0x00) && (USB_buffer_data[wLength]<USB_bytes_left)) {
						USB_bytes_left = USB_buffer_data[wLength];
					}
					SendDescriptorPacket();
					break;
				case CONFIGURATION:
					switch (USB_buffer_data[wValue]) {
						case 0:
							USB_desc_ptr = Configuration1;
							break;
						default:
							USB_error_flags |= 0x01;	// set Request Error Flag
					}
					if (!(USB_error_flags&0x01)) {
						USB_bytes_left = USB_desc_ptr[2];	// wTotalLength at an offset of 2
						if ((USB_buffer_data[wLengthHigh]==0x00) && (USB_buffer_data[wLength]<USB_bytes_left)) {
							USB_bytes_left = USB_buffer_data[wLength];
						}
						SendDescriptorPacket();
					}
					break;
				case STRING:
					switch (USB_buffer_data[wValue]) {
						case 0:
							USB_desc_ptr = String0;
							break;
						case 1:
							USB_desc_ptr = String1;
							break;
						case 2:
							USB_desc_ptr = String2;
							break;
						default:
							USB_error_flags |= 0x01;	// set Request Error Flag
					}
					if (!(USB_error_flags&0x01)) {
						USB_bytes_left = USB_desc_ptr[0];
						if ((USB_buffer_data[wLengthHigh]==0x00) && (USB_buffer_data[wLength]<USB_bytes_left)) {
							USB_bytes_left = USB_buffer_data[wLength];
						}
						SendDescriptorPacket();
					}
					break;
				default:
					USB_error_flags |= 0x01;	// set Request Error Flag
			}
			break;
		case GET_CONFIGURATION:
			BD0I.address[0] = USB_curr_config;	// copy current device configuration to EP0 IN buffer
			BD0I.bytecount = 0x01;
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case SET_CONFIGURATION:
			if (USB_buffer_data[wValue]<=NUM_CONFIGURATIONS) {
				UEP1 = 0x00;	// clear all EP control registers except for EP0 to disable EP1-EP15 prior to setting configuration
				UEP2 = 0x00;
				UEP3 = 0x00;
				UEP4 = 0x00;
				UEP5 = 0x00;
				UEP6 = 0x00;
				UEP7 = 0x00;
				UEP8 = 0x00;
				UEP9 = 0x00;
				UEP10 = 0x00;
				UEP11 = 0x00;
				UEP12 = 0x00;
				UEP13 = 0x00;
				UEP14 = 0x00;
				UEP15 = 0x00;
				switch (USB_curr_config = USB_buffer_data[wValue]) {
					case 0:
						USB_USWSTAT = ADDRESS_STATE;
#ifdef SHOW_ENUM_STATUS
						PORTB &= 0xE0;
						PORTBbits.RB2 = 1;
#endif
						break;
					default:
						USB_USWSTAT = CONFIG_STATE;
#ifdef SHOW_ENUM_STATUS
						PORTB &= 0xE0;
						PORTBbits.RB3 = 1;
#endif
				}
				BD0I.bytecount = 0x00;		// set EP0 IN byte count to 0
				BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			} else {
				USB_error_flags |= 0x01;	// set Request Error Flag
			}
			break;
		case GET_INTERFACE:
			switch (USB_USWSTAT) {
				case CONFIG_STATE:
					if (USB_buffer_data[wIndex]<NUM_INTERFACES) {
						BD0I.address[0] = 0x00;	// always send back 0 for bAlternateSetting
						BD0I.bytecount = 0x01;
						BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
					} else {
						USB_error_flags |= 0x01;	// set Request Error Flag
					}
					break;
				default:
					USB_error_flags |= 0x01;	// set Request Error Flag
			}
			break;
		case SET_INTERFACE:
			switch (USB_USWSTAT) {
				case CONFIG_STATE:
					if (USB_buffer_data[wIndex]<NUM_INTERFACES) {
						switch (USB_buffer_data[wValue]) {
							case 0:		// currently support only bAlternateSetting of 0
								BD0I.bytecount = 0x00;		// set EP0 IN byte count to 0
								BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
								break;
							default:
								USB_error_flags |= 0x01;	// set Request Error Flag
						}
					} else {
						USB_error_flags |= 0x01;	// set Request Error Flag
					}
					break;
				default:
					USB_error_flags |= 0x01;	// set Request Error Flag
			}
			break;
		case SET_DESCRIPTOR:
		case SYNCH_FRAME:
		default:
			USB_error_flags |= 0x01;	// set Request Error Flag
	}
}

void ClassRequests(void) {
	switch (USB_buffer_data[bRequest]) {
		default:
			USB_error_flags |= 0x01;	// set Request Error Flag
	}
}

void VendorRequests(void) {
	unsigned char i, n, ch, resl, resh;
	unsigned int res, temp;
	unsigned short long temp1, temp2;

	if (USB_USWSTAT!=CONFIG_STATE) {
		USB_error_flags |= 0x01;
		return;
	}
	ch = USB_buffer_data[wIndex]-1;
	if ((ch!=CH1) && (ch!=CH2)) {
		USB_error_flags != 0x01;
		return;
	}
	switch (USB_buffer_data[bRequest]) {
		case SET_FN:
			FUNCTION[ch] = (USB_buffer_data[wValue]) ? SRCI_MEASV:SRCV_MEASI;
			if (ch==CH1)
				UpdateFunction1();
			else
				UpdateFunction2();
			BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_FN:
			BD0I.address[0] = FUNCTION[ch];
			BD0I.bytecount = 0x01;	// set EP0 IN byte count to 1
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case SET_AUTORANGE:
			AUTORANGE[ch] = (USB_buffer_data[wValue]) ? ON:OFF;
			BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_AUTORANGE:
			BD0I.address[0] = AUTORANGE[ch];
			BD0I.bytecount = 0x01;	// set EP0 IN byte count to 1
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case SET_IRANGE:
			if (USB_buffer_data[wValue]<7) {
				IRANGE[ch] = USB_buffer_data[wValue];
				if (ch==CH1)
					UpdateIrange1();
				else
					UpdateIrange2();
				BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
				BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			} else {
				USB_error_flags |= 0x01;
			}
			break;
		case GET_IRANGE:
			BD0I.address[0] = IRANGE[ch];
			BD0I.bytecount = 0x01;	// set EP0 IN byte count to 1
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case SET_VRANGE:
			if (USB_buffer_data[wValue]<3) {
				VRANGE[ch] = USB_buffer_data[wValue];
				if (ch==CH1)
					UpdateVrange1();
				else
					UpdateVrange2();
				BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
				BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			} else {
				USB_error_flags |= 0x01;
			}
			break;
		case GET_VRANGE:
			BD0I.address[0] = VRANGE[ch];
			BD0I.bytecount = 0x01;	// set EP0 IN byte count to 1
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case SET_DAC:
			if ((USB_buffer_data[wIndexHigh]==0x00) || (USB_buffer_data[wIndexHigh]==0x01)) {
				DACAL[ch] = USB_buffer_data[wValue];
				DACAH[ch] = USB_buffer_data[wValueHigh];
				if (ch==CH1) {
					PORTBbits.RB2 = 0;		// set CH1 DAC _CS low
				} else {
					PORTCbits.RC6 = 0;		// set CH2 DAC _CS low
				}
				SSPBUF = (DACAH[ch]&0x0F)|0x30;	// write DACAH to DACA, unbuffered Vref, output gain = 1, and enable output buffer via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				n = SSPBUF;					// read received data in SPI buffer and throw it away
				SSPBUF = DACAL[ch];			// write DACAL to DACA via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				n = SSPBUF;					// read received data in SPI buffer and throw it away
				if (ch==CH1) {
					PORTBbits.RB2 = 1;		// set CH1 DAC _CS high
				} else {
					PORTCbits.RC6 = 1;		// set CH2 DAC _CS high
				}
			} else if ((USB_buffer_data[wIndexHigh]==0x00) || (USB_buffer_data[wIndexHigh]==0x02)) {
				DACBL[ch] = USB_buffer_data[wValue];
				DACBH[ch] = USB_buffer_data[wValueHigh];
				if (ch==CH1) {
					PORTBbits.RB2 = 0;		// set CH1 DAC _CS low
				} else {
					PORTCbits.RC6 = 0;		// set CH2 DAC _CS low
				}
				SSPBUF = (DACBH[ch]&0x0F)|0xB0;	// write DACBH to DACB, unbuffered Vref, output gain = 1, and enable output buffer via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				n = SSPBUF;					// read received data in SPI buffer and throw it away
				SSPBUF = DACBL[ch];			// write DACBL to DACB via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				n = SSPBUF;					// read received data in SPI buffer and throw it away
				if (ch==CH1) {
					PORTBbits.RB2 = 1;		// set CH1 DAC _CS high
				} else {
					PORTCbits.RC6 = 1;		// set CH2 DAC _CS high
				}
			}
			PORTCbits.RC2 = 0;		// set _LDAC low
			PORTCbits.RC2 = 0;		// set _LDAC low
			PORTCbits.RC2 = 0;		// set _LDAC low
			PORTCbits.RC2 = 1;		// set _LDAC high
			BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_DAC:
			BD0I.address[0] = DACAL[ch];
			BD0I.address[1] = DACAH[ch];
			BD0I.address[2] = DACBL[ch];
			BD0I.address[3] = DACBH[ch];
			BD0I.bytecount = 0x04;	// set EP0 IN byte count to 4
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case SET_SRC:
			temp = ((unsigned int)(USB_buffer_data[wValueHigh])<<8)|(unsigned int)USB_buffer_data[wValue];
			temp = (temp>>4)&0x07FF;
			if (USB_buffer_data[wValueHigh]&0x80) {
				res = 2048-temp;
				if (USB_buffer_data[wValue]&0x08)
					res--;
				DACAL[ch] = (unsigned char)(res&0xFF);
				DACAH[ch] = (unsigned char)(res>>8);
				res = 2048+temp;
				DACBL[ch] = (unsigned char)(res&0xFF);
				DACBH[ch] = (unsigned char)(res>>8);
			} else {
				res = 2048+temp;
				if (USB_buffer_data[wValue]&0x08)
					res++;
				DACAL[ch] = (unsigned char)(res&0xFF);
				DACAH[ch] = (unsigned char)(res>>8);
				res = 2048-temp;
				DACBL[ch] = (unsigned char)(res&0xFF);
				DACBH[ch] = (unsigned char)(res>>8);
			}
			if (ch==CH1) {
				PORTBbits.RB2 = 0;		// set CH1 DAC _CS low
			} else {
				PORTCbits.RC6 = 0;		// set CH2 DAC _CS low
			}
			SSPBUF = (DACAH[ch]&0x0F)|0x30;	// write DACAH to DACA, unbuffered Vref, output gain = 1, and enable output buffer via SPI
			while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
			n = SSPBUF;					// read received data in SPI buffer and throw it away
			SSPBUF = DACAL[ch];			// write DACAL to DACA via SPI
			while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
			n = SSPBUF;					// read received data in SPI buffer and throw it away
			if (ch==CH1) {
				PORTBbits.RB2 = 1;		// set CH1 DAC _CS high
				PORTBbits.RB2 = 0;		// set CH1 DAC _CS low
			} else {
				PORTCbits.RC6 = 1;		// set CH2 DAC _CS high
				PORTCbits.RC6 = 0;		// set CH2 DAC _CS low
			}
			SSPBUF = (DACBH[ch]&0x0F)|0xB0;	// write DACBH to DACB, unbuffered Vref, output gain = 1, and enable output buffer via SPI
			while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
			n = SSPBUF;					// read received data in SPI buffer and throw it away
			SSPBUF = DACBL[ch];			// write DACBL to DACB via SPI
			while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
			n = SSPBUF;					// read received data in SPI buffer and throw it away
			if (ch==CH1) {
				PORTBbits.RB2 = 1;		// set CH1 DAC _CS high
			} else {
				PORTCbits.RC6 = 1;		// set CH2 DAC _CS high
			}
			PORTCbits.RC2 = 0;			// set _LDAC low
			PORTCbits.RC2 = 0;			// set _LDAC low
			PORTCbits.RC2 = 0;			// set _LDAC low
			PORTCbits.RC2 = 1;			// set _LDAC high
			FUNCTION[ch] = (USB_buffer_data[wIndexHigh]&0x01) ? SRCI_MEASV:SRCV_MEASI;
			if (FUNCTION[ch]==SRCV_MEASI) {
				VRANGE[ch] = (USB_buffer_data[wValue])&0x07;
			} else {
				IRANGE[ch] = (USB_buffer_data[wValue])&0x07;
			}
			if (ch==CH1) {
				UpdateFunction1();
				UpdateVrange1();
				UpdateIrange1();
			} else {
				UpdateFunction2();
				UpdateVrange2();
				UpdateIrange2();
			}
			BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_SRC:
			BD0I.address[0] = DACAL[ch];
			BD0I.address[1] = DACAH[ch];
			BD0I.address[2] = DACBL[ch];
			BD0I.address[3] = DACBH[ch];
			BD0I.address[4] = (FUNCTION[ch]==SRCV_MEASI) ? VRANGE[ch]:IRANGE[ch];
			BD0I.address[5] = FUNCTION[ch];
			BD0I.bytecount = 0x06;	// set EP0 IN byte count to 6
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case SET_REF:
			REF[ch][FUNCTION[ch]][(FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch]]= ((unsigned int)(USB_buffer_data[wValueHigh])<<8)|(unsigned int)USB_buffer_data[wValue];
			BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_REF:
			temp = REF[ch][FUNCTION[ch]][(FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch]];
			BD0I.address[0] = (unsigned char)(temp&0xFF);
			BD0I.address[1] = (unsigned char)(temp>>8);
			BD0I.bytecount = 0x02;	// set EP0 IN byte count to 2
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_ADC:
			res = 0x0000;
			for (n = 0; n<16; n++) {
				PORTCbits.RC1 = 0;			// set ADC _CS low
				SSPBUF = 0x01;				// write out the start bit via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF;				// read received data in SPI buffer and throw it away
				SSPBUF = (ch==CH1) ? 0xA0:0xE0;	// set SGL/_DIFF bit high (single ended), ODD/_SIGN bit according to ch, and MSBF bit high, via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF&0x0F;			// read received data in SPI buffer, saving the four most-significant bits of the result
				SSPBUF = 0x00;				// send out eight 0s via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resl = SSPBUF;				// read received data in SPI buffer, saving the eight least-significant bits of the result
				PORTCbits.RC1 = 1;			// set ADC _CS high
				res += ((unsigned int)resh<<8)|(unsigned int)resl;
			}
			res >>= 4;
			BD0I.address[0] = (unsigned char)(res&0xFF);
			BD0I.address[1] = (unsigned char)(res>>8);
			BD0I.bytecount = 0x02;	// set EP0 IN byte count to 2
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_MEAS:
			temp = 0x0000;
			for (i = 0; i<4; i++) {
				res = 0x0000;
				for (n = 0; n<16; n++) {
					PORTCbits.RC1 = 0;			// set ADC _CS low
					SSPBUF = 0x01;				// write out the start bit via SPI
					while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
					resh = SSPBUF;				// read received data in SPI buffer and throw it away
					SSPBUF = (ch==CH1) ? 0xA0:0xE0;	// set SGL/_DIFF bit high (single ended), ODD/_SIGN bit according to ch, and MSBF bit high, via SPI
					while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
					resh = SSPBUF&0x0F;			// read received data in SPI buffer, saving the four most-significant bits of the result
					SSPBUF = 0x00;				// send out eight 0s via SPI
					while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
					resl = SSPBUF;				// read received data in SPI buffer, saving the eight least-significant bits of the result
					PORTCbits.RC1 = 1;			// set ADC _CS high
					res += ((unsigned int)resh<<8)|(unsigned int)resl;
				}
				temp += res>>4;
			}
			res = temp>>2;
			temp = REF[ch][FUNCTION[ch]][(FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch]];
			BD0I.address[0] = (unsigned char)(res&0xFF);
			BD0I.address[1] = (unsigned char)(res>>8);
			BD0I.address[2] = (unsigned char)(temp&0xFF);
			BD0I.address[3] = (unsigned char)(temp>>8);
			BD0I.address[4] = (FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch];
			BD0I.address[5] = FUNCTION[ch];
			BD0I.bytecount = 0x06;	// set EP0 IN byte count to 6
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case SAVE_REF:
			INTCONbits.GIE = 0;
			EECON1bits.EEPGD = 0;
			EECON1bits.CFGS = 0;
			EECON1bits.WREN = 1;
			EEADR = (ch<<5)|(FUNCTION[ch]<<4)|(((FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch])<<1);
			EEDATA = (unsigned char)(REF[ch][FUNCTION[ch]][(FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch]]&0xFF);
			EECON2 = 0x55;
			EECON2 = 0xAA;
			EECON1bits.WR = 1;
			while (!PIR2bits.EEIF);
			PIR2bits.EEIF = 0;
			EEADR++;
			EEDATA = (unsigned char)(REF[ch][FUNCTION[ch]][(FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch]]>>8);
			EECON2 = 0x55;
			EECON2 = 0xAA;
			EECON1bits.WR = 1;
			while (!PIR2bits.EEIF);
			PIR2bits.EEIF = 0;
			EECON1bits.WREN = 0;
			INTCONbits.GIE = 1;
			BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case LOAD_REF:
			EECON1bits.EEPGD = 0;
			EECON1bits.CFGS = 0;
			EEADR = (ch<<5)|(FUNCTION[ch]<<4)|(((FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch])<<1);
			EECON1bits.RD = 1;
			resl = EEDATA;
			EEADR++;
			EECON1bits.RD = 1;
			resh = EEDATA;
			REF[ch][FUNCTION[ch]][(FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch]] = ((unsigned int)(resh)<<8)|(unsigned int)resl;
			BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_ADC_KILL60HZ:
			temp1 = 0x000000;
			for (i = 0; i<250; i++) {
				while (!(PIR1bits.TMR2IF));	// wait for Timer2 to go off, which happens every 66.67 us
				PIR1bits.TMR2IF = 0;		// reset Timer2 interrupt flag
				PORTCbits.RC1 = 0;			// set ADC _CS low
				SSPBUF = 0x01;				// write out the start bit via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF;				// read received data in SPI buffer and throw it away
				SSPBUF = (ch==CH1) ? 0xA0:0xE0;	// set SGL/_DIFF bit high (single ended), ODD/_SIGN bit according to ch, and MSBF bit high, via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF&0x0F;			// read received data in SPI buffer, saving the four most-significant bits of the result
				SSPBUF = 0x00;				// send out eight 0s via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resl = SSPBUF;				// read received data in SPI buffer, saving the eight least-significant bits of the result
				PORTCbits.RC1 = 1;			// set ADC _CS high
				temp1 += ((unsigned int)resh<<8)|(unsigned int)resl;
			}
			res = (unsigned int)(temp1/250);
			BD0I.address[0] = (unsigned char)(res&0xFF);
			BD0I.address[1] = (unsigned char)(res>>8);
			BD0I.bytecount = 0x02;	// set EP0 IN byte count to 2
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_MEAS_KILL60HZ:
			temp1 = 0x000000;
			for (i = 0; i<250; i++) {
				while (!(PIR1bits.TMR2IF));	// wait for Timer2 to go off, which happens every 66.67 us
				PIR1bits.TMR2IF = 0;		// reset Timer2 interrupt flag
				PORTCbits.RC1 = 0;			// set ADC _CS low
				SSPBUF = 0x01;				// write out the start bit via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF;				// read received data in SPI buffer and throw it away
				SSPBUF = (ch==CH1) ? 0xA0:0xE0;	// set SGL/_DIFF bit high (single ended), ODD/_SIGN bit according to ch, and MSBF bit high, via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF&0x0F;			// read received data in SPI buffer, saving the four most-significant bits of the result
				SSPBUF = 0x00;				// send out eight 0s via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resl = SSPBUF;				// read received data in SPI buffer, saving the eight least-significant bits of the result
				PORTCbits.RC1 = 1;			// set ADC _CS high
				temp1 += ((unsigned int)resh<<8)|(unsigned int)resl;
			}
			res = (unsigned int)(temp1/250);
			temp = REF[ch][FUNCTION[ch]][(FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch]];
			BD0I.address[0] = (unsigned char)(res&0xFF);
			BD0I.address[1] = (unsigned char)(res>>8);
			BD0I.address[2] = (unsigned char)(temp&0xFF);
			BD0I.address[3] = (unsigned char)(temp>>8);
			BD0I.address[4] = (FUNCTION[ch]==SRCV_MEASI) ? IRANGE[ch]:VRANGE[ch];
			BD0I.address[5] = FUNCTION[ch];
			BD0I.bytecount = 0x06;	// set EP0 IN byte count to 6
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case GET_DISPLAY:
			temp1 = 0x000000;
			temp2 = 0x000000;
			for (i = 0; i<250; i++) {
				while (!(PIR1bits.TMR2IF));	// wait for Timer2 to go off, which happens every 66.67 us
				PIR1bits.TMR2IF = 0;		// reset Timer2 interrupt flag
				PORTCbits.RC1 = 0;			// set ADC _CS low
				SSPBUF = 0x01;				// write out the start bit via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF;				// read received data in SPI buffer and throw it away
				SSPBUF = 0xA0;				// set SGL/_DIFF bit high (single ended), ODD/_SIGN bit to read CH1, and MSBF bit high, via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF&0x0F;			// read received data in SPI buffer, saving the four most-significant bits of the result
				SSPBUF = 0x00;				// send out eight 0s via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resl = SSPBUF;				// read received data in SPI buffer, saving the eight least-significant bits of the result
				PORTCbits.RC1 = 1;			// set ADC _CS high
				temp1 += ((unsigned int)resh<<8)|(unsigned int)resl;
				PORTCbits.RC1 = 0;			// set ADC _CS low
				SSPBUF = 0x01;				// write out the start bit via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF;				// read received data in SPI buffer and throw it away
				SSPBUF = 0xE0;				// set SGL/_DIFF bit high (single ended), ODD/_SIGN bit to read CH2, and MSBF bit high, via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF&0x0F;			// read received data in SPI buffer, saving the four most-significant bits of the result
				SSPBUF = 0x00;				// send out eight 0s via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resl = SSPBUF;				// read received data in SPI buffer, saving the eight least-significant bits of the result
				PORTCbits.RC1 = 1;			// set ADC _CS high
				temp2 += ((unsigned int)resh<<8)|(unsigned int)resl;
			}
			BD0I.address[0] = DACAL[CH1];
			BD0I.address[1] = DACAH[CH1];
			BD0I.address[2] = DACBL[CH1];
			BD0I.address[3] = DACBH[CH1];
			BD0I.address[4] = (FUNCTION[CH1]==SRCV_MEASI) ? VRANGE[CH1]:IRANGE[CH1];
			BD0I.address[5] = FUNCTION[CH1];
			res = (unsigned int)(temp1/250);
			temp = REF[CH1][FUNCTION[CH1]][(FUNCTION[CH1]==SRCV_MEASI) ? IRANGE[CH1]:VRANGE[CH1]];
			BD0I.address[6] = (unsigned char)(res&0xFF);
			BD0I.address[7] = (unsigned char)(res>>8);
			BD0I.address[8] = (unsigned char)(temp&0xFF);
			BD0I.address[9] = (unsigned char)(temp>>8);
			BD0I.address[10] = (FUNCTION[CH1]==SRCV_MEASI) ? IRANGE[CH1]:VRANGE[CH1];
			BD0I.address[11] = AUTORANGE[CH1];
			BD0I.address[12] = DACAL[CH2];
			BD0I.address[13] = DACAH[CH2];
			BD0I.address[14] = DACBL[CH2];
			BD0I.address[15] = DACBH[CH2];
			BD0I.address[16] = (FUNCTION[CH2]==SRCV_MEASI) ? VRANGE[CH2]:IRANGE[CH2];
			BD0I.address[17] = FUNCTION[CH2];
			res = (unsigned int)(temp2/250);
			temp = REF[CH2][FUNCTION[CH2]][(FUNCTION[CH2]==SRCV_MEASI) ? IRANGE[CH2]:VRANGE[CH2]];
			BD0I.address[18] = (unsigned char)(res&0xFF);
			BD0I.address[19] = (unsigned char)(res>>8);
			BD0I.address[20] = (unsigned char)(temp&0xFF);
			BD0I.address[21] = (unsigned char)(temp>>8);
			BD0I.address[22] = (FUNCTION[CH2]==SRCV_MEASI) ? IRANGE[CH2]:VRANGE[CH2];
			BD0I.address[23] = AUTORANGE[CH2];
			BD0I.bytecount = 0x18;	// set EP0 IN byte count to 24
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		default:
			USB_error_flags |= 0x01;	// set Request Error Flag
	}
}

void ProcessInToken(void) {
	switch (USB_USTAT&0x18) {	// extract the EP bits
		case EP0:
			switch (USB_dev_req) {
				case SET_ADDRESS:
					switch (UADDR = USB_address_pending) {
						case 0:
							USB_USWSTAT = DEFAULT_STATE;
#ifdef SHOW_ENUM_STATUS
							PORTB &= 0xE0;
							PORTBbits.RB1 = 1;
#endif
							break;
						default:
							USB_USWSTAT = ADDRESS_STATE;
#ifdef SHOW_ENUM_STATUS
							PORTB &= 0xE0;
							PORTBbits.RB2 = 1;
#endif
					}
					break;
				case GET_DESCRIPTOR:
					SendDescriptorPacket();
					break;
			}
			break;
		case EP1:
			break;
		case EP2:
			break;
	}
}

void ProcessOutToken(void) {
	switch (USB_USTAT&0x18) {	// extract the EP bits
		case EP0:
			BD0O.bytecount = MAX_PACKET_SIZE;
			BD0O.status = 0x88;
			BD0I.bytecount = 0x00;	// set EP0 IN byte count to 0
			BD0I.status = 0xC8;		// send packet as DATA1, set UOWN bit
			break;
		case EP1:
			break;
		case EP2:
			break;
	}
}

void SendDescriptorPacket(void) {
	unsigned char n;

	if (USB_bytes_left<MAX_PACKET_SIZE) {
		USB_dev_req = NO_REQUEST;	// sending a short packet, so clear device request
		USB_packet_length = USB_bytes_left;
		USB_bytes_left = 0x00;
	} else {
		USB_packet_length = MAX_PACKET_SIZE;
		USB_bytes_left -= MAX_PACKET_SIZE;
	}
	for (n = 0; n<USB_packet_length; n++) {
		BD0I.address[n] = *USB_desc_ptr++;
	}
	BD0I.bytecount = USB_packet_length;
	BD0I.status = ((BD0I.status^0x40)&0x40)|0x88; // toggle the DATA01 bit, clear the PIDs bits, and set the UOWN and DTS bits
}

void UpdateFunction1(void) {
	switch (FUNCTION[CH1]) {
		case SRCV_MEASI:
			PORTBbits.RB3 = 0;
			break;
		case SRCI_MEASV:
			PORTBbits.RB3 = 1;
	}
}

void UpdateIrange1(void) {
	switch (IRANGE[CH1]) {
		case _20MA:
			PORTBbits.RB6 = 0;
			PORTBbits.RB7 = 0;
			PORTAbits.RA5 = 0;
			break;
		case _2MA:
			PORTBbits.RB6 = 1;
			PORTBbits.RB7 = 0;
			PORTAbits.RA5 = 0;
			break;
		case _200UA:
			PORTBbits.RB6 = 0;
			PORTBbits.RB7 = 1;
			PORTAbits.RA5 = 0;
			break;
		case _20UA:
			PORTBbits.RB6 = 1;
			PORTBbits.RB7 = 1;
			PORTAbits.RA5 = 0;
			break;
		case _2UA:
			PORTBbits.RB6 = 0;
			PORTBbits.RB7 = 0;
			PORTAbits.RA5 = 1;
			break;
		case _200NA:
			PORTBbits.RB6 = 1;
			PORTBbits.RB7 = 0;
			PORTAbits.RA5 = 1;
			break;
		case _20NA:
			PORTBbits.RB6 = 0;
			PORTBbits.RB7 = 1;
			PORTAbits.RA5 = 1;
	}
}

void UpdateVrange1(void) {
	switch (VRANGE[CH1]) {
		case _10V:
			PORTBbits.RB5 = 0;
			PORTBbits.RB4 = 0;
			break;
		case _4V:
			PORTBbits.RB5 = 1;
			PORTBbits.RB4 = 0;
			break;
		case _2V:
			PORTBbits.RB5 = 0;
			PORTBbits.RB4 = 1;
	}
}

void UpdateFunction2(void) {
	switch (FUNCTION[CH2]) {
		case SRCV_MEASI:
			PORTAbits.RA4 = 0;
			break;
		case SRCI_MEASV:
			PORTAbits.RA4 = 1;
	}
}

void UpdateIrange2(void) {
	switch (IRANGE[CH2]) {
		case _20MA:
			PORTAbits.RA1 = 0;
			PORTAbits.RA0 = 0;
			PORTCbits.RC0 = 0;
			break;
		case _2MA:
			PORTAbits.RA1 = 1;
			PORTAbits.RA0 = 0;
			PORTCbits.RC0 = 0;
			break;
		case _200UA:
			PORTAbits.RA1 = 0;
			PORTAbits.RA0 = 1;
			PORTCbits.RC0 = 0;
			break;
		case _20UA:
			PORTAbits.RA1 = 1;
			PORTAbits.RA0 = 1;
			PORTCbits.RC0 = 0;
			break;
		case _2UA:
			PORTAbits.RA1 = 0;
			PORTAbits.RA0 = 0;
			PORTCbits.RC0 = 1;
			break;
		case _200NA:
			PORTAbits.RA1 = 1;
			PORTAbits.RA0 = 0;
			PORTCbits.RC0 = 1;
			break;
		case _20NA:
			PORTAbits.RA1 = 0;
			PORTAbits.RA0 = 1;
			PORTCbits.RC0 = 1;
	}
}

void UpdateVrange2(void) {
	switch (VRANGE[CH2]) {
		case _10V:
			PORTAbits.RA2 = 0;
			PORTAbits.RA3 = 0;
			break;
		case _4V:
			PORTAbits.RA2 = 1;
			PORTAbits.RA3 = 0;
			break;
		case _2V:
			PORTAbits.RA2 = 0;
			PORTAbits.RA3 = 1;
	}
}

void main(void) {
	unsigned char n, resl, resh, ch, fn, range;
	unsigned int ref, res;

	PORTA = 0x00;
    ADCON1 = 0x0F;      // set up PORTA to be digital I/Os
	TRISA = 0x00;		// set up PORTA pins as outputs
	PORTB = 0x04;		// initialize RB2 (CH1 DAC _CS) high
	TRISB = 0x01;		// set up RB0 (SDI) as an input and RB1...RB7 as outputs
	PORTC = 0x46;		// initialize RC1 (ADC _CS), RC2 (_LDAC), and RC6 (CH2 DAC _CS) high
	TRISC = 0x00;		// set up PORTC as outputs
	SSPSTAT = 0x40;
	SSPCON1 = 0x21;		// initialize MSSP for Mode 0,0, SPI Master Mode, clock = Fosc/16, and enable MSSP
	PR2 = 199;			// initialize Timer2...
	T2CON = 0x05;		// ...to go off every 66.67 us
	InitUSB();			// initialize the USB registers and serial interface engine
	while (USB_USWSTAT!=CONFIG_STATE) {		// while the peripheral is not configured...
		ServiceUSB();						// ...service USB requests
	}

	AUTORANGE[CH1] = OFF;
	FUNCTION[CH1] = SRCV_MEASI;
	IRANGE[CH1] = _20MA;
	UpdateIrange1();
	VRANGE[CH1] = _10V;
	UpdateVrange1();
	DACAL[CH1] = 0x00;
	DACAH[CH1] = 0x00;
	DACBL[CH1] = 0x00;
	DACBH[CH1] = 0x00;


	AUTORANGE[CH2] = OFF;
	FUNCTION[CH2] = SRCV_MEASI;
	IRANGE[CH2] = _20MA;
	UpdateIrange2();
	VRANGE[CH2] = _10V;
	UpdateVrange2();
	DACAL[CH2] = 0x00;
	DACAH[CH2] = 0x00;
	DACBL[CH2] = 0x00;
	DACBH[CH2] = 0x00;

	for (ch = 0; ch<2; ch++) {
		for (fn = 0; fn<2; fn++) {
			for (range = 0; range<7; range++) {
				EECON1bits.EEPGD = 0;
				EECON1bits.CFGS = 0;
				EEADR = (ch<<5)|(fn<<4)|(range<<1);
				EECON1bits.RD = 1;
				resl = EEDATA;
				EEADR++;
				EECON1bits.RD = 1;
				resh = EEDATA;
				REF[ch][fn][range] = ((unsigned int)(resh)<<8)|(unsigned int)resl;
			}
		}
	}

	while (1) {
		ServiceUSB();
		if (AUTORANGE[CH1]==ON) {
			ref = REF[CH1][FUNCTION[CH1]][(FUNCTION[CH1]==SRCV_MEASI) ? IRANGE[CH1]:VRANGE[CH1]];
			res = 0x0000;
			for (n = 0; n<8; n++) {
				PORTCbits.RC1 = 0;			// set ADC _CS low
				SSPBUF = 0x01;				// write out the start bit via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF;				// read received data in SPI buffer and throw it away
				SSPBUF = 0xA0;				// set SGL/_DIFF bit high (single ended), ODD/_SIGN bit low (select ch0), and MSBF bit high, via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF&0x0F;			// read received data in SPI buffer, saving the four most-significant bits of the result
				SSPBUF = 0x00;				// send out eight 0s via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resl = SSPBUF;				// read received data in SPI buffer, saving the eight least-significant bits of the result
				PORTCbits.RC1 = 1;			// set ADC _CS high
				res += ((unsigned int)resh<<8)|(unsigned int)resl;
			}
			res >>= 3;
			res = (res<ref) ? ref-res:res-ref;
			if (FUNCTION[CH1]==SRCV_MEASI) {
				if ((res>2000) && (IRANGE[CH1]!=_20MA))
					IRANGE[CH1]--;
				else if ((res<100) && (IRANGE[CH1]!=_200NA))
					IRANGE[CH1]++;
				UpdateIrange1();
			} else {
				if ((res>2000) && (VRANGE[CH1]!=_10V))
					VRANGE[CH1]--;
				else if ((res<640) && (VRANGE[CH1]==_10V))
					VRANGE[CH1]++;
				else if ((res<800) && (VRANGE[CH1]==_4V))
					VRANGE[CH1]++;
				UpdateVrange1();
			}
		}
		if (AUTORANGE[CH2]==ON) {
			ref = REF[CH2][FUNCTION[CH2]][(FUNCTION[CH2]==SRCV_MEASI) ? IRANGE[CH2]:VRANGE[CH2]];
			res = 0x0000;
			for (n = 0; n<8; n++) {
				PORTCbits.RC1 = 0;			// set ADC _CS low
				SSPBUF = 0x01;				// write out the start bit via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF;				// read received data in SPI buffer and throw it away
				SSPBUF = 0xE0;				// set SGL/_DIFF bit high (single ended), ODD/_SIGN bit high (select ch1), and MSBF bit high, via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resh = SSPBUF&0x0F;			// read received data in SPI buffer, saving the four most-significant bits of the result
				SSPBUF = 0x00;				// send out eight 0s via SPI
				while (!SSPSTATbits.BF);	// do nothing until the transmission is complete
				resl = SSPBUF;				// read received data in SPI buffer, saving the eight least-significant bits of the result
				PORTCbits.RC1 = 1;			// set ADC _CS high
				res += ((unsigned int)resh<<8)|(unsigned int)resl;
			}
			res >>= 3;
			res = (res<ref) ? ref-res:res-ref;
			if (FUNCTION[CH2]==SRCV_MEASI) {
				if ((res>2000) && (IRANGE[CH2]!=_20MA))
					IRANGE[CH2]--;
				else if ((res<100) && (IRANGE[CH2]!=_200NA))
					IRANGE[CH2]++;
				UpdateIrange2();
			} else {
				if ((res>2000) && (VRANGE[CH2]!=_10V))
					VRANGE[CH2]--;
				else if ((res<640) && (VRANGE[CH2]==_10V))
					VRANGE[CH2]++;
				else if ((res<800) && (VRANGE[CH2]==_4V))
					VRANGE[CH2]++;
				UpdateVrange2();
			}
		}
	}
}
