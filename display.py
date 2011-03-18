from Tkinter import *
import circuitsmu

def ch1_mode_callback():
    meas = smu.get_meas(1)
    smu.set_source(1, meas[0], meas[1])

def ch1_auto_callback():
    smu.set_autorange(1, 1-smu.get_autorange(1))

def ch1_range_down_callback():
    function = smu.get_function(1)
    if function==0:
        range = smu.get_irange(1)
        if range!=5:
            smu.set_irange(1, range+1)
    elif function==1:
        range = smu.get_vrange(1)
        if range!=2:
            smu.set_vrange(1, range+1)

def ch1_range_up_callback():
    function = smu.get_function(1)
    if function==0:
        range = smu.get_irange(1)
        if range!=0:
            smu.set_irange(1, range-1)
    elif function==1:
        range = smu.get_vrange(1)
        if range!=0:
            smu.set_vrange(1, range-1)

def ch1_entry_callback(event):
    str = ch1cmd.get()
    smu.set_src_str(1, str.strip())
    ch1cmd.set('')

def ch2_mode_callback():
    meas = smu.get_meas(2)
    smu.set_source(2, meas[0], meas[1])

def ch2_auto_callback():
    smu.set_autorange(2, 1-smu.get_autorange(2))

def ch2_range_down_callback():
    function = smu.get_function(2)
    if function==0:
        range = smu.get_irange(2)
        if range!=5:
            smu.set_irange(2, range+1)
    elif function==1:
        range = smu.get_vrange(2)
        if range!=2:
            smu.set_vrange(2, range+1)

def ch2_range_up_callback():
    function = smu.get_function(2)
    if function==0:
        range = smu.get_irange(2)
        if range!=0:
            smu.set_irange(2, range-1)
    elif function==1:
        range = smu.get_vrange(2)
        if range!=0:
            smu.set_vrange(2, range-1)

def ch2_entry_callback(event):
    str = ch2cmd.get()
    smu.set_src_str(2, str.strip())
    ch2cmd.set('')

root = Tk()
root.title('USB Source-Measure Unit')
root.configure(bg = '#C8C8C8')

display = Frame(root, bg = '#C8C8C8')
ch1frame = Frame(display, bg = '#C8C8C8')
ch1disp = Frame(ch1frame, bg = '#000000', relief = SUNKEN, border = 3)
ch1row1 = Frame(ch1disp, bg = '#000000')
ch1label = Label(ch1row1, text = 'CH1', font = ('Courier', 12, 'bold'), bg = '#000000', fg = '#00FFFF')
ch1label.pack(side = LEFT)
ch1auto = Label(ch1row1, text = '    ', font = ('Courier', 12, 'bold'), bg = '#000000', fg = '#00FFFF')
ch1auto.pack(side = RIGHT)
ch1row1.pack(side = TOP, fill = X)
ch1meas = Label(ch1disp, text = u'---.--\u00B5A', font = ('Courier', 36, 'bold'), bg = '#000000', fg = '#00FFFF')
ch1meas.pack(side = TOP, anchor = W)
ch1src = Label(ch1disp, text = 'Vsrc=+0.0000V ', font = ('Courier', 21, 'bold'), bg = '#000000', fg = '#00FFFF')
ch1src.pack(side = TOP, anchor = W)
ch1disp.pack(side = TOP)
ch1ctrls = Frame(ch1frame, bg = '#C8C8C8')
Button(ch1ctrls, text = 'MODE', bg = '#C8C8C8', highlightbackground = '#C8C8C8', font = ('Helvetica', 12), command = ch1_mode_callback).pack(side = LEFT)
Button(ch1ctrls, text = '>', bg = '#C8C8C8', highlightbackground = '#C8C8C8', font = ('Helvetica', 12), command = ch1_range_up_callback).pack(side = RIGHT)
Button(ch1ctrls, text = 'AUTO', bg = '#C8C8C8', highlightbackground = '#C8C8C8', font = ('Helvetica', 12), command = ch1_auto_callback).pack(side = RIGHT)
Button(ch1ctrls, text = '<', bg = '#C8C8C8', highlightbackground = '#C8C8C8', font = ('Helvetica', 12), command = ch1_range_down_callback).pack(side = RIGHT)
ch1ctrls.pack(side = TOP, fill = X, pady = 5)
ch1cmd = StringVar()
ch1entry = Entry(ch1frame, textvariable = ch1cmd, font = ('Helvetica', 12))
ch1entry.bind('<KeyPress-Return>', ch1_entry_callback)
ch1entry.pack(side = TOP, fill = X)
ch1frame.pack(side = LEFT, padx = 5, pady = 10)

ch2frame = Frame(display, bg = '#C8C8C8')
ch2disp = Frame(ch2frame, bg = '#000000', relief = SUNKEN, border = 3)
ch2row1 = Frame(ch2disp, bg = '#000000')
ch2label = Label(ch2row1, text = 'CH2', font = ('Courier', 12, 'bold'), bg = '#000000', fg = '#00FFFF')
ch2label.pack(side = LEFT)
ch2auto = Label(ch2row1, text = '    ', font = ('Courier', 12, 'bold'), bg = '#000000', fg = '#00FFFF')
ch2auto.pack(side = RIGHT)
ch2row1.pack(side = TOP, fill = X)
ch2meas = Label(ch2disp, text = u'---.--\u00B5A', font = ('Courier', 36, 'bold'), bg = '#000000', fg = '#00FFFF')
ch2meas.pack(side = TOP, anchor = W)
ch2src = Label(ch2disp, text = 'Vsrc=+0.0000V ', font = ('Courier', 21, 'bold'), bg = '#000000', fg = '#00FFFF')
ch2src.pack(side = TOP, anchor = W)
ch2disp.pack(side = TOP)
ch2ctrls = Frame(ch2frame, bg = '#C8C8C8')
Button(ch2ctrls, text = 'MODE', bg = '#C8C8C8', highlightbackground = '#C8C8C8', font = ('Helvetica', 12), command = ch2_mode_callback).pack(side = LEFT)
Button(ch2ctrls, text = '>', bg = '#C8C8C8', highlightbackground = '#C8C8C8', font = ('Helvetica', 12), command = ch2_range_up_callback).pack(side = RIGHT)
Button(ch2ctrls, text = 'AUTO', bg = '#C8C8C8', highlightbackground = '#C8C8C8', font = ('Helvetica', 12), command = ch2_auto_callback).pack(side = RIGHT)
Button(ch2ctrls, text = '<', bg = '#C8C8C8', highlightbackground = '#C8C8C8', font = ('Helvetica', 12), command = ch2_range_down_callback).pack(side = RIGHT)
ch2ctrls.pack(side = TOP, fill = X, pady = 5)
ch2cmd = StringVar()
ch2entry = Entry(ch2frame, textvariable = ch2cmd, font = ('Helvetica', 12))
ch2entry.bind('<KeyPress-Return>', ch2_entry_callback)
ch2entry.pack(side = TOP, fill = X)
ch2frame.pack(side = LEFT, padx = 5, pady = 10)

display.pack(side = LEFT, padx = 5)

def make_display_small():
    ch1label.configure(font = ('Courier', 9, 'bold'))
    ch1auto.configure(font = ('Courier', 9, 'bold'))
    ch1meas.configure(font = ('Courier', 20, 'bold'))
    ch1src.configure(font = ('Courier', 12, 'bold'))
    ch2label.configure(font = ('Courier', 9, 'bold'))
    ch2auto.configure(font = ('Courier', 9, 'bold'))
    ch2meas.configure(font = ('Courier', 20, 'bold'))
    ch2src.configure(font = ('Courier', 12, 'bold'))

def make_display_large():
    ch1label.configure(font = ('Courier', 12, 'bold'))
    ch1auto.configure(font = ('Courier', 12, 'bold'))
    ch1meas.configure(font = ('Courier', 36, 'bold'))
    ch1src.configure(font = ('Courier', 21, 'bold'))
    ch2label.configure(font = ('Courier', 12, 'bold'))
    ch2auto.configure(font = ('Courier', 12, 'bold'))
    ch2meas.configure(font = ('Courier', 36, 'bold'))
    ch2src.configure(font = ('Courier', 21, 'bold'))

def update_display():
    disp = smu.get_display()
    ch1src.configure(text = disp[0])
    ch1meas.configure(text = disp[1])
    ch1auto.configure(text = disp[2])
    ch2src.configure(text = disp[3])
    ch2meas.configure(text = disp[4])
    ch2auto.configure(text = disp[5])
    display.after(100, update_display)

smu = circuitsmu.smu()
display.after(100, update_display)
if __name__=='__main__':
    root.mainloop()
