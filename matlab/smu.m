
classdef smu < handle
    properties
        buffer
        dev
    end
    properties (Constant)
        SET_FN = 0
        GET_FN = 1
        SET_AUTORANGE = 2
        GET_AUTORANGE = 3
        SET_IRANGE = 4
        GET_IRANGE = 5
        SET_VRANGE = 6
        GET_VRANGE = 7
        SET_DAC = 8
        GET_DAC = 9
        SET_SRC = 10
        GET_SRC = 11
        SET_REF = 12
        GET_REF = 13
        GET_ADC = 14
        GET_MEAS = 15
        SAVE_REF = 16
        LOAD_REF = 17
        GET_ADC_KILL60HZ = 18
        GET_MEAS_KILL60HZ = 19
        GET_DISPLAY = 20
        OFF = 0
        ON = 1
        SRCV_MEASI = 0
        SRCI_MEASV = 1
        OVER_RANGE = 6
        I20MA = 0
        I2MA = 1
        I200UA = 2
        I20UA = 3
        I2UA = 4
        I200NA = 5
        V10V = 0
        V4V = 1
        V2V = 2
        set_src_imult = [ 2e5, 2e6, 2e7, 2e8, 2e9, 2e10 ];
        set_src_vmult = [ 0.4e3, 1e3, 2e3 ];
        get_src_imult = [ 0.5e-5, 0.5e-6, 0.5e-7, 0.5e-8, 0.5e-9, 0.5e-10 ];
        get_src_vmult = [ 2.5e-3, 1e-3, 0.5e-3 ];
        get_meas_imult = [ 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10 ];
        get_meas_vmult = [ 5e-3, 2e-3, 1e-3 ];
        get_disp_imult = [ 1e3, 1e3, 1e6, 1e6, 1e6, 1e9 ];
        get_disp_srci_fmt = char('Isrc=%+07.3fmA', 'Isrc=%+07.4fmA', ['Isrc=%+07.2f', char(181), 'A'], ['Isrc=%+07.3f', char(181), 'A'], ['Isrc=%+07.4f', char(181), 'A'], 'Isrc=%+07.2fnA');
        get_disp_srcv_fmt = char('Vsrc=%+08.4fV', 'Vsrc=%+07.4fV ', 'Vsrc=%+07.4fV ');
        get_disp_measi_fmt = char('%+06.2fmA', '%+06.3fmA', ['%+06.1f', char(181), 'A'], ['%+06.2f', char(181), 'A'], ['%+06.3f', char(181), 'A'], '%+06.1fnA');
        get_disp_measv_fmt = char('%+07.3fV', '%+06.3fV ', '%+06.3fV ');
    end
    methods
        function obj = smu(varargin)
            if nargin==0
                num = 0;
            else
                num = varargin(1);
                num = num{1};
            end
            if not(libisloaded('usb'))
                loadlibrary('libusb.so.1.0.1', 'usb.h');
                calllib('usb', 'initialize');
            end
            obj.buffer = libpointer('uint8Ptr', int8(zeros(1, 64)));
            obj.dev = calllib('usb', 'open_device', 26214, 43981, num);
            if obj.dev==-1
                fprintf('Found device with vendor ID = 0x6666 and product ID = 0xABCD, but could not open it.\n');
            elseif obj.dev==-2
                fprintf('Found device with vendor ID = 0x6666 and product ID = 0xABCD, but too many devices already open.\n');
            elseif obj.dev==-3
                fprintf('No device found with vendor ID = 0x6666 and product ID = 0xABCD.\n');
            end
            ret = calllib('usb', 'control_transfer', obj.dev, 0, 9, 1, 0, 0, obj.buffer);
            if ret<0
                fprintf('Could not issue SET_CONFIGURATION(1) standard request.\n');
            end
        end

%%
%%      AUTORANGE Select the best range for measurment on a chanel.
%%         AUTORANGE(CH) automatically selects the best measurement range on
%%         channel CH, where CH can be either 1 or 2, under software control.
%%         Firmware autoranging is disabled upon calling this function.
%%
        function autorange(obj, ch)
           if obj.dev>=0
                if (ch==1) || (ch==2)
                    obj.set_autorange(ch, obj.OFF);
                    done = 0;
                    while done==0
                        ret = calllib('usb', 'control_transfer', obj.dev, 192, obj.GET_MEAS_KILL60HZ, 0, uint16(ch), 6, obj.buffer);
                        if ret<0
                            fprintf('Unable to send GET_MEAS_KILL60HZ vendor request.\n');
                            done = 1;
                        else
                            val = 256*uint16(obj.buffer.value(2))+uint16(obj.buffer.value(1));
                            ref = 256*uint16(obj.buffer.value(4))+uint16(obj.buffer.value(3));
                            if (val>=ref)
                                res = val-ref;
                            else
                                res = ref-val;
                            end
                            range = uint8(obj.buffer.value(5));
                            fn = uint8(obj.buffer.value(6));
                            if fn==obj.SRCV_MEASI
                                if (res>2000) && (range~=obj.I20MA)
                                    range = range-1;
                                elseif (res<100) && (range~=obj.I200NA)
                                    range = range+1;
                                else
                                    done = 1;
                                end
                                obj.set_irange(ch, range);
                            else
                                if (res>2000) && (range~=obj.V10V)
                                    range = range-1;
                                elseif (res<640) && (range==obj.V10V)
                                    range = range+1;
                                elseif (res<800) && (range==obj.V4V)
                                    range = range+1;
                                else
                                    done = 1;
                                end
                                obj.set_vrange(ch, range);
                            end
                        end
                    end
                else
                    fprintf('Illegal channel specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      CLOSE Close the SMU.
%%         CLOSE closes the SMU.
%%
        function close(obj)
            if obj.dev>=0
                calllib('usb', 'close_device', obj.dev);
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_AUTORANGE Get the state of firmware autoranging for a chanel.
%%         GET_AUTORANGE(CH) returns 1 if firmware autoranging is ON for 
%%         chanel CH otherwise it returns 0.  Here CH can be 1 or 2.
%%
        function autorange = get_autorange(obj, ch)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    ret = calllib('usb', 'control_transfer', obj.dev, 192, obj.GET_AUTORANGE, 0, uint16(ch), 1, obj.buffer);
                    if ret<0
                        fprintf('Unable to send GET_AUTORANGE vendor request.\n');
                    else
                        autorange = uint8(obj.buffer.value(1));
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_CURRENT Get the current value for a chanel.
%%         GET_CURRENT(CH) returns the current value for chanel CH, where CH
%%         can be 1 or 2.  If chanel CH is in SV/MI mode, the value returned is
%%         the measured current.  If chanel CH is in SI/MV mode, the value
%%         returned is the sourced current.  In either case, the units of the
%%         returned value are Amperes.
%%
        function current = get_current(obj, ch)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    if obj.get_function(ch)==obj.SRCI_MEASV
                        [current, units] = obj.get_source(ch);
                    else
                        [current, units] = obj.get_meas(ch);
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_DISPLAY Support function for UPDATE_DISPLAY.
%%         GET_DISPLAY is support function for UPDATE_DISPLAY.  You will 
%%         probably not want to call it directly in your own scripts.
%%
        function [src1str, meas1str, auto1str, src2str, meas2str, auto2str] = get_display(obj)
            if obj.dev>=0
                ret = calllib('usb', 'control_transfer', obj.dev, 192, obj.GET_DISPLAY, 0, 1, 24, obj.buffer);
                if ret<0
                    fprintf('Unable to send GET_DISPLAY vendor request.\n');
                else
                    if uint8(obj.buffer.value(6))==obj.SRCV_MEASI
                        value = double(256*uint16(obj.buffer.value(2))+uint16(obj.buffer.value(1)))-double(256*uint16(obj.buffer.value(4))+uint16(obj.buffer.value(3)));
                        value = obj.get_src_vmult(uint8(obj.buffer.value(5))+1)*value;
                        src1str = sprintf(deblank(obj.get_disp_srcv_fmt(uint8(obj.buffer.value(5))+1, :)), value);
                        value = double(256*uint16(obj.buffer.value(8))+uint16(obj.buffer.value(7)))-double(256*uint16(obj.buffer.value(10))+uint16(obj.buffer.value(9)));
                        value = obj.get_meas_imult(uint8(obj.buffer.value(11))+1)*value;
                        meas1str = sprintf(deblank(obj.get_disp_measi_fmt(uint8(obj.buffer.value(11))+1, :)), obj.get_disp_imult(uint8(obj.buffer.value(11))+1)*value);
                    else
                        value = double(256*uint16(obj.buffer.value(2))+uint16(obj.buffer.value(1)))-double(256*uint16(obj.buffer.value(4))+uint16(obj.buffer.value(3)));
                        value = obj.get_src_imult(uint8(obj.buffer.value(5))+1)*value;
                        src1str = sprintf(deblank(obj.get_disp_srci_fmt(uint8(obj.buffer.value(5))+1, :)), obj.get_disp_imult(uint8(obj.buffer.value(5))+1)*value);
                        value = double(256*uint16(obj.buffer.value(8))+uint16(obj.buffer.value(7)))-double(256*uint16(obj.buffer.value(10))+uint16(obj.buffer.value(9)));
                        value = obj.get_meas_vmult(uint8(obj.buffer.value(11))+1)*value;
                        meas1str = sprintf(deblank(obj.get_disp_measv_fmt(uint8(obj.buffer.value(11))+1, :)), value);
                    end
                    if uint8(obj.buffer.value(12))==obj.ON
                        auto1str = 'AUTO';
                    else
                        auto1str = '    ';
                    end
                    if uint8(obj.buffer.value(18))==obj.SRCV_MEASI
                        value = double(256*uint16(obj.buffer.value(14))+uint16(obj.buffer.value(13)))-double(256*uint16(obj.buffer.value(16))+uint16(obj.buffer.value(15)));
                        value = obj.get_src_vmult(uint8(obj.buffer.value(17))+1)*value;
                        src2str = sprintf(deblank(obj.get_disp_srcv_fmt(uint8(obj.buffer.value(17))+1, :)), value);
                        value = double(256*uint16(obj.buffer.value(20))+uint16(obj.buffer.value(19)))-double(256*uint16(obj.buffer.value(22))+uint16(obj.buffer.value(21)));
                        value = obj.get_meas_imult(uint8(obj.buffer.value(23))+1)*value;
                        meas2str = sprintf(deblank(obj.get_disp_measi_fmt(uint8(obj.buffer.value(23))+1, :)), obj.get_disp_imult(uint8(obj.buffer.value(23))+1)*value);
                    else
                        value = double(256*uint16(obj.buffer.value(14))+uint16(obj.buffer.value(13)))-double(256*uint16(obj.buffer.value(16))+uint16(obj.buffer.value(15)));
                        value = obj.get_src_imult(uint8(obj.buffer.value(17))+1)*value;
                        src2str = sprintf(deblank(obj.get_disp_srci_fmt(uint8(obj.buffer.value(17))+1, :)), obj.get_disp_imult(uint8(obj.buffer.value(17))+1)*value);
                        value = double(256*uint16(obj.buffer.value(20))+uint16(obj.buffer.value(19)))-double(256*uint16(obj.buffer.value(22))+uint16(obj.buffer.value(21)));
                        value = obj.get_meas_vmult(uint8(obj.buffer.value(23))+1)*value;
                        meas2str = sprintf(deblank(obj.get_disp_measv_fmt(uint8(obj.buffer.value(23))+1, :)), value);
                    end
                    if uint8(obj.buffer.value(24))==obj.ON
                        auto2str = 'AUTO';
                    else
                        auto2str = '    ';
                    end
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_FUNCTION Get the functional mode of a chanel.
%%         GET_FUNCTION(CH) returns 1 if chanel CH is in SI/MV mode and it  
%%         returns 0 if chanel CH is in SV/MI mode.  Here CH can be 1 or 2.
%%
        function fn = get_function(obj, ch)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    ret = calllib('usb', 'control_transfer', obj.dev, 192, obj.GET_FN, 0, uint16(ch), 1, obj.buffer);
                    if ret<0
                        fprintf('Unable to send GET_FN vendor request.\n');
                    else
                        fn = uint8(obj.buffer.value(1));
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_IRANGE Get the current range setting of a chanel.
%%         GET_IRANGE(CH) returns the current range setting of chanel CH,
%%         where CH can be 1 or 2.  The possible return values are as follows:
%%
%%            Range    Full-Scale    Minimum Source    Minimum Meas.
%%            Number      Value        Resolution       Resolution
%%              0          20 mA           5 uA            10 uA
%%              1           2 mA         500 nA             1 uA
%%              2         200 uA          50 nA           100 nA
%%              3          20 uA           5 nA            10 nA
%%              4           2 uA         500 pA             1 nA
%%              5         200 nA          50 pA           100 pA
%%
        function range = get_irange(obj, ch)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    ret = calllib('usb', 'control_transfer', obj.dev, 192, obj.GET_IRANGE, 0, uint16(ch), 1, obj.buffer);
                    if ret<0
                        fprintf('Unable to send GET_IRANGE vendor request.\n');
                    else
                        range = uint8(obj.buffer.value(1));
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_MEAS Get the measurement value for a given chanel.
%%         GET_MEAS(CH) returns the measurement value for chanel CH, where CH
%%         can be 1 or 2.
%%
%%         [VALUE, UNITS]=GET_MEAS(CH) returns the measurement value of 
%%         chanel CH in VALUE and the units of the measurement value in UNITS.
%%         If UNITS is 0, the measurement units are Amperes (i.e., chanel CH is 
%%         in SV/MI mode).  If UNITS is 1, the measurement units are Volts (i.e.,
%%         chanel CH is in SI/MV mode).
%%
        function [value, units] = get_meas(obj, ch)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    ret = calllib('usb', 'control_transfer', obj.dev, 192, obj.GET_MEAS_KILL60HZ, 0, uint16(ch), 6, obj.buffer);
                    if ret<0
                        fprintf('Unable to send GET_MEAS_KILL60HZ vendor request.\n');
                    else
                        value = double(256*uint16(obj.buffer.value(2))+uint16(obj.buffer.value(1)))-double(256*uint16(obj.buffer.value(4))+uint16(obj.buffer.value(3)));
                        if uint8(obj.buffer.value(6))==obj.SRCV_MEASI
                            value = value*obj.get_meas_imult(uint8(obj.buffer.value(5))+1);
                            units = 1;
                        else
                            value = value*obj.get_meas_vmult(uint8(obj.buffer.value(5))+1);
                            units = 0;
                        end
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_SOURCE Get the source value for a given chanel.
%%         GET_SOURCE(CH) returns the source value for chanel CH, where CH
%%         can be 1 or 2.
%%
%%         [VALUE, UNITS]=GET_SOURCE(CH) returns the source value of chanel
%%         CH in VALUE and the units of the source value in UNITS.  If UNITS is 
%%         0, the source units are Volts (i.e., chanel CH is in SV/MI mode).
%%         If UNITS is 1, the source units are Amperes (i.e., chanel CH is in 
%%         SI/MV mode).
%%
        function [value, units] = get_source(obj, ch)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    ret = calllib('usb', 'control_transfer', obj.dev, 192, obj.GET_SRC, 0, uint16(ch), 6, obj.buffer);
                    if ret<0
                        fprintf('Unable to send GET_SRC vendor request.\n');
                    else
                        value = double(256*uint16(obj.buffer.value(2))+uint16(obj.buffer.value(1)))-double(256*uint16(obj.buffer.value(4))+uint16(obj.buffer.value(3)));
                        if uint8(obj.buffer.value(6))==obj.SRCV_MEASI
                            value = value*obj.get_src_vmult(uint8(obj.buffer.value(5))+1);
                        else
                            value = value*obj.get_src_imult(uint8(obj.buffer.value(5))+1);
                        end
                        units = uint8(obj.buffer.value(6));
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_VOLTAGE Get the voltage value for a chanel.
%%         GET_VOLTAGE(CH) returns the voltage value for chanel CH, where CH
%%         can be 1 or 2.  If chanel CH is in SV/MI mode, the value returned is
%%         the sourced voltage.  If chanel CH is in SI/MV mode, the value
%%         returned is the measured voltage.  In either case, the units of the
%%         returned value are Volts.
%%
        function voltage = get_voltage(obj, ch)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    if obj.get_function(ch)==obj.SRCV_MEASI
                        [voltage, units] = obj.get_source(ch);
                    else
                        [voltage, units] = obj.get_meas(ch);
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      GET_VRANGE Get the voltage range setting of a chanel.
%%         GET_VRANGE(CH) returns the voltage range setting of chanel CH,
%%         where CH can be 1 or 2.  The possible return values are as follows:
%%
%%            Range    Full-Scale    Minimum Source    Minimum Meas.
%%            Number      Value        Resolution       Resolution
%%              0         10 V           2.5 mV            5 mV
%%              1          4 V             1 mV            2 mV
%%              2          2 V           500 uV            1 mV
%%
        function range = get_vrange(obj, ch)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    ret = calllib('usb', 'control_transfer', obj.dev, 192, obj.GET_VRANGE, 0, uint16(ch), 1, obj.buffer);
                    if ret<0
                        fprintf('Unable to send GET_VRANGE vendor request.\n');
                    else
                        range = uint8(obj.buffer.value(1));
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      SET_AUTORANGE Set the state of firmware autoranging for a chanel.
%%         SET_AUTORANGE(CH, ARANGE) sets the state of firmware autoranging 
%%         for chanel CH to ARANGE.  If ARANGE is 1, firmware autoranging is 
%%         turned ON for chanel CH.  If ARANGE is 0, firmware autoranging is 
%%         turned OFF for chanel CH.  Here CH can be 1 or 2.
%%
        function set_autorange(obj, ch, arange)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    if (arange<0) || (arange>1)
                        fprintf('Illegal autorange setting specified.\n');
                    else
                        ret = calllib('usb', 'control_transfer', obj.dev, 64, obj.SET_AUTORANGE, uint16(arange), uint16(ch), 0, obj.buffer);
                        if ret<0
                            fprintf('Unable to send SET_AUTORANGE vendor request.\n');
                        end
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      SET_CURRENT Set the source value for a chanel to a given current.
%%         SET_CURRENT(CH, VALUE) sets chanel CH to SI/MV mode and sets the 
%%         sourced current to VALUE Amperes.  Here CH can be 1 or 2.
%%
        function set_current(obj, ch, value)
            if obj.dev>=0
                obj.set_source(ch, value, obj.SRCI_MEASV);
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      SET_FUNCTION Set the functional mode of a chanel.
%%         SET_FUNCTION(CH, FN) sets the functional mode of chanel CH to 
%%         SV/MI if FN is 0 or to SI/MV if FN is 1.  Here CH can be 1 or 2.
%%
        function set_function(obj, ch, fn)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    if (fn<0) || (fn>1)
                        fprintf('Illegal function specified.\n');
                    else
                        ret = calllib('usb', 'control_transfer', obj.dev, 64, obj.SET_FN, uint16(fn), uint16(ch), 0, obj.buffer);
                        if ret<0
                            fprintf('Unable to send SET_FN vendor request.\n');
                        end
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      SET_IRANGE Set the current range of a chanel.
%%         SET_IRANGE(CH, IRANGE) sets the current range of chanel CH to 
%%         IRANGE.  Here CH can be 1 or 2.  The possible values of IRANGE are 
%%         as follows:
%%
%%            Range    Full-Scale    Minimum Source    Minimum Meas.
%%            Number      Value        Resolution       Resolution
%%              0          20 mA           5 uA            10 uA
%%              1           2 mA         500 nA             1 uA
%%              2         200 uA          50 nA           100 nA
%%              3          20 uA           5 nA            10 nA
%%              4           2 uA         500 pA             1 nA
%%              5         200 nA          50 pA           100 pA
%%
        function set_irange(obj, ch, irange)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    if (irange<0) || (irange>6)
                        fprintf('Illegal current range setting specified.\n');
                    else
                        ret = calllib('usb', 'control_transfer', obj.dev, 64, obj.SET_IRANGE, uint16(irange), uint16(ch), 0, obj.buffer);
                        if ret<0
                            fprintf('Unable to send SET_IRANGE vendor request.\n');
                        end
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      SET_SOURCE Set the source value for a given chanel.
%%         SET_SOURCE(CH, VALUE, UNITS) sets the source value of chanel CH 
%%         to VALUE Volts if UNITS is 0 (i.e., SV/MI mode) or to VALUE Amperes 
%%         if UNITS is 1 (i.e., SI/MV mode).  Here CH can be 1 or 2.
%%
        function set_source(obj, ch, value, units)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    if (units<0) || (units>1)
                        fprintf('Illegal units specified.\n');
                    else
                        if units==obj.SRCV_MEASI
                            if abs(value)>10.0
                                fprintf('Specified source voltage value is out of range.\n');
                                range = obj.OVER_RANGE;
                            elseif abs(value)>4.0
                                range = obj.V10V;
                            elseif abs(value)>2.0
                                range = obj.V4V;
                            else
                                range = obj.V2V;
                            end
                        else
                            if abs(value)>20e-3
                                fprintf('Specified source current value is out of range.\n');
                                range = obj.OVER_RANGE;
                            elseif abs(value)>2e-3
                                range = obj.I20MA;
                            elseif abs(value)>200e-6
                                range = obj.I2MA;
                            elseif abs(value)>20e-6
                                range = obj.I200UA;
                            elseif abs(value)>2e-6
                                range = obj.I20UA;
                            elseif abs(value)>200e-9
                                range = obj.I2UA;
                            else
                                range = obj.I200NA;
                            end
                        end
                        if range~=obj.OVER_RANGE
                            if units==obj.SRCV_MEASI
                                value = int16(round(value*obj.set_src_vmult(range+1)));
                            else
                                value = int16(round(value*obj.set_src_imult(range+1)));
                            end
                            if value>0
                                temp = 8*uint16(value)+range;
                            else
                                temp = 32768+8*uint16(-value)+range;
                            end
                            ret = calllib('usb', 'control_transfer', obj.dev, 64, obj.SET_SRC, temp, uint16(256*units+ch), 0, obj.buffer);
                            if ret<0
                                fprintf('Unable to send SET_SRC vendor request.\n');
                            end
                        end
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      SET_SRC_STR Set the source value of a given chanel from a string.
%%         SET_SRC_STR(CH, STR) sets the source value of chanel CH 
%%         to the value specified in the string STR.  Here CH can be 1 or 2.
%%         If STR contains units, the mode of chanel CH will change if 
%%         necessary.  The units can also include one of the following prefixes: 
%%         'm' for milli, 'u' for micro, 'n' for nano, and 'p' for pico.
%%
        function set_src_str(obj, ch, str)
            if obj.dev>=0
                if length(str)~=0
                    if (ch==1) || (ch==2)
                        fn = obj.get_function(ch);
                        if str(length(str))=='A' || str(length(str))=='a'
                            fn = 1;
                            str = str(1:length(str)-1);
                        elseif str(length(str))=='V' || str(length(str))=='v'
                            fn = 0;
                            str = str(1:length(str)-1);
                        end
                        mult = 1;
                        if str(length(str))=='P' || str(length(str))=='p'
                            mult = 1e-12;
                            str = str(1:length(str)-1);
                        elseif str(length(str))=='N' || str(length(str))=='n'
                            mult = 1e-9;
                            str = str(1:length(str)-1);
                        elseif str(length(str))=='U' || str(length(str))=='u'
                            mult = 1e-6;
                            str = str(1:length(str)-1);
                        elseif str(length(str))=='M' || str(length(str))=='m'
                            mult = 1e-3;
                            str = str(1:length(str)-1);
                        end
                        value = str2num(str)*mult;
                        obj.set_source(ch, value, fn)
                    else
                        fprintf('Illegal channel number specified.\n');
                    end
                end
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      SET_VOLTAGE Set the source value for a chanel to a given voltage.
%%         SET_VOLTAGE(CH, VALUE) sets chanel CH to SV/MI mode and sets the 
%%         sourced voltage to VALUE Volts.  Here CH can be 1 or 2.
%%
        function set_voltage(obj, ch, value)
            if obj.dev>=0
                obj.set_source(ch, value, obj.SRCV_MEASI);
            else
                fprintf('No smu device open.\n');
            end
        end

%%
%%      SET_VRANGE Set the voltage range of a chanel.
%%         SET_VRANGE(CH, VRANGE) sets the voltage range of chanel CH to 
%%         VRANGE.  Here CH can be 1 or 2.  The possible values of VRANGE are 
%%         as follows:
%%
%%            Range    Full-Scale    Minimum Source    Minimum Meas.
%%            Number      Value        Resolution       Resolution
%%              0         10 V           2.5 mV            5 mV
%%              1          4 V             1 mV            2 mV
%%              2          2 V           500 uV            1 mV
%%
        function set_vrange(obj, ch, vrange)
            if obj.dev>=0
                if (ch==1) || (ch==2)
                    if (vrange<0) || (vrange>3)
                        fprintf('Illegal voltage range setting specified.\n');
                    else
                        ret = calllib('usb', 'control_transfer', obj.dev, 64, obj.SET_VRANGE, uint16(vrange), uint16(ch), 0, obj.buffer);
                        if ret<0
                            fprintf('Unable to send SET_VRANGE vendor request.\n');
                        end
                    end
                else
                    fprintf('Illegal channel number specified.\n');
                end
            else
                fprintf('No smu device open.\n');
            end
        end
    end
end
