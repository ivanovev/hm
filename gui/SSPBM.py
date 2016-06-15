
from collections import OrderedDict as OD
from util import Data, control_cb, monitor_cb, dev_serial_io_cb, alarm_trace_cb
from util.columns import *

def get_mntr(dev):
    mntr=Data(io_cb=dev_serial_io_cb)
    mntr.add_page('mntr0', send=True)
    mntr.add('alarm', wdgt='alarm', msg='Sum Alarm', trace_cb=alarm_trace_cb)
    mntr.add('temp', wdgt='entry', state='readonly', msg='Temperature')
    mntr.add('pwr', wdgt='entry', state='readonly', msg='Power level')
    return mntr

def get_ctrl(dev):
    ctrl = Data(io_cb=dev_serial_io_cb, send=True, name='ctrl')
    ctrl.add('tx', label='Mute/unmute tx', wdgt='combo', state='readonly', value=OD([('ON','1'), ('OFF','0')]))
    ctrl.add('gain', label='Gain', wdgt='entry')
    ctrl.add('atten', label='Attenuation', wdgt='entry')
    return ctrl

def get_menu(dev):
    return OD([('Control', control_cb), ('Monitor', monitor_cb)])

def columns():
    return get_columns([c_serial])

