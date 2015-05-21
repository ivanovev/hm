
from collections import OrderedDict as OD
from tkinter import Tk, Toplevel, BOTH, N, E, W
from tkinter.ttk import Frame, Button
from util.monitor import Monitor
from util.columns import *
from util.callbacks import alarm_trace_cb
from util import Data, process_cb, control_cb

class MoveAntenna(Monitor):
    def __init__(self, dev):
        data = get_mntr(dev)
        data.add('step', wdgt='spin', value=Data.spn(1,100), msg='Step')
        Monitor.__init__(self, data=data, dev=dev)

    def init_layout(self):
        self.root.title('Move antenna')
        f1 = Frame(self.root, width=400, height=300, padding=(3,3,3,3))
        f1.pack(fill=BOTH)
        btn = Button(f1, text='+Elevation', command=lambda:self.move_antenna(False, True))
        btn.grid(column=1, row=0, padx=5, sticky=(N, E, W))
        btn = Button(f1, text='-Azimuth', command=lambda:self.move_antenna(True, False))
        btn.grid(column=0, row=1, padx=5, sticky=(N, E, W))
        btn = Button(f1, text='+Azimuth', command=lambda:self.move_antenna(True, True))
        btn.grid(column=2, row=1, padx=5, sticky=(N, E, W))
        btn = Button(f1, text='-Elevation', command=lambda:self.move_antenna(False, False))
        btn.grid(column=1, row=2, padx=5, sticky=(N, E, W))

        cmds = self.data[0]
        l,w = self.make_cmdw(f1, 'step', cmds)
        w.configure(width=5)
        w.grid(column=1, row=1)

        def wdgts(key, column, row):
            l, w = self.mntr_cmdw(f1, key, cmds)
            if l:
                l.grid(column=column-1, row=row)
            w.grid(column=column, row=row, padx=5)
            return l,w
        wdgts('az', 4, 0)
        wdgts('az-', 5, 0)
        wdgts('az+', 6, 0)
        #wdgts('limaz-', 7, 0)
        #wdgts('limaz+', 8, 0)
        wdgts('el', 4, 1)
        wdgts('el-', 5, 1)
        wdgts('el+', 6, 1)
        #wdgts('limel-', 7, 1)
        #wdgts('limel+', 8, 1)

        btn = Button(f1, text='Stop', command=lambda: stop_cb(self))
        btn.grid(column=3, row=2, padx=5, sticky=(N, E, W))

        btn = Button(f1, text='Close', command=self.root.destroy)
        btn.grid(column=4, row=2, padx=5, sticky=(N, E, W))

    def move_antenna(self, az, sgn):
        c = self.data.get_value('az' if az else 'el')
        if not c:
            self.root.after_idle(self.io.start)
            return
        step = self.data.get_value('step')
        if sgn:
            c = int(c) + int(step)
        else:
            c = int(c) - int(step)
        if az:
            self.qo.put('az POLUS.az %s %d' % (self.data.dev[c_serial], c))
        else:
            self.qo.put('el POLUS.el %s %d' % (self.data.dev[c_serial], c))
        self.mntr_io_start(lambda: self.io.start(do_cb1=False))

    def stop_antenna(self):
        stop_cb(self)

def alarm_fmt_cb(val, read, bit):
    if read:
        v = int(val, 16)
        return '%d' % ((v >> bit) & 1)

def get_mntr(self):
    data = Data(name='Monitor')
    data.add('az', label='Azimuth', wdgt='entry', state='readonly', send=True, cmd_cb=polus_cmd_cb)
    data.add('el', label='Elevation', wdgt='entry', state='readonly', send=True, cmd_cb=polus_cmd_cb)
    def add_alarm(k, bit, msg, cmd_cb=None):
        data.add(k, wdgt='alarm', send=True if cmd_cb else False, cmd_cb=cmd_cb, fmt_cb=lambda val, read: alarm_fmt_cb(val, read, bit), msg=msg, trace_cb=alarm_trace_cb)
    add_alarm('az+', 0, 'az+', cmd_cb=lambda *args: 'POLUS.status')
    add_alarm('az-', 1, 'az-')
    #add_alarm('limaz+', 4, 'limaz+')
    #add_alarm('limaz-', 5, 'limaz-')
    add_alarm('el+', 2, 'el+')
    add_alarm('el-', 3, 'el-')
    #add_alarm('limel+', 6, 'limel+')
    #add_alarm('limel-', 7, 'limel-')
    return data

def columns():
    return get_columns([c_serial])

def startup_cb(apps, mode, dev):
    if mode == 'moveantenna':
        return MoveAntenna(dev=dev)

def polus_cmd_cb(dev, cmd, val=None):
    cmd = 'POLUS.' + cmd + ' ' + dev[c_serial]
    if val:
        cmd = cmd + ' ' + val
    return cmd

def ae0_fmt_cb(val, read, e=0):
    if read:
        vv = val.split()
        return vv[e % 2]
    else:
        if e % 2:
            setattr(ae0_fmt_cb, 'e%d' % e, val)
            ae0_fmt_cb.el = val
        else:
            return '%s %s' % (val, getattr(ae0_fmt_cb, 'e%d' % (e+1)))

def read_cb(ctrl):
    ctrl.read_cb()

def write_cb(ctrl):
    ctrl.write_cb()

def stop_cb(ctrl):
    ctrl.cmdio('POLUS.stop %s' % ctrl.data.dev[c_serial])

def get_ctrl(dev):
    ctrl_buttons = OD([('Read', read_cb), ('Write', write_cb), ('Stop', stop_cb)])
    ctrl = Data(name='Setup', buttons=ctrl_buttons)
    ctrl.add('limaz', label='Azimuth max.', wdgt='spin', value=Data.spn(0, 16383), send=True, fmt_cb=lambda val, read: ae0_fmt_cb(val, read, e=0), cmd_cb=polus_cmd_cb)
    ctrl.add('limaz2', label='Azimuth min.', wdgt='spin', value=Data.spn(0, 16383), fmt_cb=lambda val, read: ae0_fmt_cb(val, read, e=1))
    ctrl.add('limel', label='Elevation max.', wdgt='spin', value=Data.spn(0, 16383), send=True, fmt_cb=lambda val, read: ae0_fmt_cb(val, read, e=2), cmd_cb=polus_cmd_cb)
    ctrl.add('limel2', label='Elevation min.', wdgt='spin', value=Data.spn(0, 16383), fmt_cb=lambda val, read: ae0_fmt_cb(val, read, e=3))
    ctrl.add('ae0', label='New azimuth', wdgt='spin', value=Data.spn(0, 16383), send=True, fmt_cb=lambda val, read: ae0_fmt_cb(val, read, e=4), cmd_cb=polus_cmd_cb)
    ctrl.add('ae02', label='New elevation', wdgt='spin', value=Data.spn(0, 16383), fmt_cb=lambda val, read: ae0_fmt_cb(val, read, e=5))
    ctrl.add_page('Move')
    ctrl.add('az', label='Azimuth', wdgt='spin', value=Data.spn(0, 16383), send=True, cmd_cb=polus_cmd_cb)
    ctrl.add('el', label='Elevation', wdgt='spin', value=Data.spn(0, 16383), send=True, cmd_cb=polus_cmd_cb)
    return ctrl

def get_menu(dev, cc=None):
    menu = OD()
    menu['Move antenna'] = lambda dev: process_cb('moveantenna', dev)
    menu['Control'] = control_cb
    return menu

