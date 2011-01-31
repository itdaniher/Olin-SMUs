#include <libusb/libusb.h>

#define MAX_DEVICES_OPEN    10

libusb_device_handle *open_devices[MAX_DEVICES_OPEN];
int devices_open;

void initialize(void) {
    int i;
    
    libusb_init(NULL);

    devices_open = 0;
    for (i = 0; i<MAX_DEVICES_OPEN; i++)
        open_devices[i] = NULL;
}

void deinitialize(void) {
    libusb_exit(NULL);
}

void set_debug(int level) {
    libusb_set_debug(NULL, level);
}

int open_device(unsigned int vendorID, unsigned int productID, int n) {
    libusb_device **list, *dev;
    libusb_device_handle *dev_handle;
    ssize_t cnt, j;
    struct libusb_device_descriptor desc;
    int err, i;
    
    cnt = libusb_get_device_list(NULL, &list);
    if (cnt<0) {
        libusb_free_device_list(list, 1);
        return -4;  /* Indicates no USB devices found at all. */
    }

    i = 0;
    for (j = 0; j<cnt; j++) {
        dev = list[j];
        libusb_get_device_descriptor(dev, &desc);
        if ((desc.idVendor==vendorID) && (desc.idProduct==productID)) {
            if (i==n) {
                for (i = 0; i<MAX_DEVICES_OPEN; i++) {
                    if (open_devices[i]==NULL) {
                        err = libusb_open(dev, &dev_handle);
                        open_devices[i] = dev_handle;
                        libusb_free_device_list(list, 1);
                        if (err) {
                            return -1;  /* Indicates matching USB device found, but could not be opened. */
                        } else {
                            devices_open++;
                            return i;
                        }
                    }
                }
                libusb_free_device_list(list, 1);
                return -2;  /* Indicates matching USB device found, but too many devices already opened. */
            } else {
                i++;
            }
        }
    }
    libusb_free_device_list(list, 1);
    return -3;  /* Indicates no matching USB device found. */
}

int close_device(int device) {
    if ((device<0) || (device>=MAX_DEVICES_OPEN))
        return -1;
    if (open_devices[device]) {
        libusb_close(open_devices[device]);
        devices_open--;
        open_devices[device] = NULL;
        return 0;
    }
    return -2;
}

int num_devices_open(void) {
    return devices_open;
}

int control_transfer(int device, unsigned char bmRequestType, unsigned char bRequest, unsigned int wValue, unsigned int wIndex, unsigned int wLength, unsigned char *buffer) {
    if ((device<0) || (device>=MAX_DEVICES_OPEN))
        return -1;
    if (open_devices[device])
        return libusb_control_transfer(open_devices[device], (uint8_t)bmRequestType, (uint8_t)bRequest, (uint16_t)wValue, (uint16_t)wIndex, buffer, (uint16_t)wLength, 0);
    return -2;
}
