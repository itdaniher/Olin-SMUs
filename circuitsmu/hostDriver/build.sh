gcc -c -fPIC usb.c -o usb.o
gcc -shared -Wl,-soname,_smu.so -o _smu.so -lusb-1.0 usb.o 
mv _smu.so ../
