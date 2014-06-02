
from collections import OrderedDict as OD
from util.mainwnd import control_cb, monitor_cb
from util.data import Data
from util.columns import *
from util.callbacks import dev_serial_io_cb, cmd_serial_io_cb, alarm_trace_cb

def columns():
    return get_columns([c_serial])

def chan_trace_cb(k, data, t='T', offset=5904):
    ch = data.get_value(k)
    try:
        freq = int(ch) + offset
        data.set_value(t + 'XFREQ', '%d' % freq)
    except:
        pass

def adc_cmd_cb(dev, cmd, val=None):
    return 'ADC %s' % cmd

def alarm_fmt_cb(val, read=True, almn='ALARM0'):
    alarms = OD([
        ('General', ['FANERR', 'PROMERR', 'WARMING', 'UCMUTE']), \
        ('TEMP', ['PATEMP']), \
        ('PLL', ['OSLOCK', 'TXLOCK', 'RXLOCK', 'OSPLL', 'TXPLL', 'RXPLL']), \
        ('TX/RX', ['RXOUT', 'TXIN', 'TXOUT']), \
        ('PWR', ['P12V', 'P5V', 'PA', 'N5V', 'LBNV']) \
        ])
    n = int(almn.replace('ALARM', ''))
    kk = list(alarms.keys())
    vv = val.split()
    aa = alarms[kk[n]]
    for a in vv:
        if a in aa:
            return '1'
    return '0'

def freq_gain_fmt_cb(val, read=True):
    if read:
        return '%g' % float(val)
    else:
        return val

def get_ctrl(dev):
    ctrl = Data(io_cb=cmd_serial_io_cb, send=True, name='ctrl')
    ctrl.add('TX', label='TX', wdgt='radio', value=['ON', 'OFF'])
    #ctrl.add('TXCHAN', label='TX chan', wdgt='spin', value=Data.spn(1, 501), trace_cb=chan_trace_cb)
    ctrl.add('TXFREQ', label='TX freq [MHz]', wdgt='spin', value=Data.spn(5925, 6475), fmt_cb=freq_gain_fmt_cb)
    ctrl.add('TXGAIN', label='TX gain [dB]', wdgt='spin', value=Data.spn(38, 74), fmt_cb=freq_gain_fmt_cb)
    #ctrl.add('RXCHAN', label='RX chan', wdgt='spin', value=Data.spn(1, 501), trace_cb=lambda k,d: chan_trace_cb(k,d,'R',3579))
    ctrl.add('RXFREQ', label='RX freq [MHz]', wdgt='spin', value=Data.spn(3650, 4200), fmt_cb=freq_gain_fmt_cb)
    ctrl.add('RXGAIN', label='RX gain [dB]', wdgt='spin', value=Data.spn(80, 105), fmt_cb=freq_gain_fmt_cb)
    return ctrl

def get_mntr(dev):
    mntr=Data(io_cb=dev_serial_io_cb, send=True)
    mntr.add_page('mntr0')
    aa = lambda k, send, msg: mntr.add(k, wdgt='alarm', send=send, msg=msg, cmd='ALARM', fmt_cb=lambda val,read=True,almn=k: alarm_fmt_cb(val,read,almn), trace_cb=alarm_trace_cb)
    aa('ALARM0', True, 'General')
    aa('ALARM1', False, 'TEMP')
    aa('ALARM2', False, 'PLL')
    aa('ALARM3', False, 'TX/RX')
    aa('ALARM4', False, 'PWR')
    mntr.add('TEMP', wdgt='entry', state='readonly', msg='Temperature', cmd_cb=adc_cmd_cb)
    mntr.add('TXIN', wdgt='entry', state='readonly', pack_forget=True, msg='TX In', cmd_cb=adc_cmd_cb)
    mntr.add_page('mntr1')
    ae = lambda cmd, label: mntr.add(cmd, wdgt='entry', state='readonly', label=label, cmd_cb=adc_cmd_cb, send=True)
    ae('TXIN', 'TX In')
    ae('TXOUT', 'TX Out')
    ae('RXOUT', 'RX Out')
    ae('OSLPLL', 'OSLPLL')
    ae('TXPLL', 'TXPLL')
    ae('RXPLL', 'RXPLL')
    for i in range(1, 7):
        ae('PA%d' % i, 'PA%d, V' % i)
    ae('P12V', '+12V')
    ae('P5V', '+5V')
    ae('LNBV', 'LNBV')
    ae('N5V', '-5V')
    mntr.cmds.columns=4
    return mntr

def get_menu(dev):
    return OD([('Control', control_cb), ('Monitor', monitor_cb)])

