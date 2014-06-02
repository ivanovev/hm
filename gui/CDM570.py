
from collections import OrderedDict as OD
from util.mainwnd import control_cb, monitor_cb
from util.data import Data, find_key
from util.callbacks import alarm_trace_cb
from util.columns import *

def cmd_io_cb(dev, cmd, val=None):
    return 'CDM570.cmd %s %s %s' % (dev[c_serial], dev[c_addr], cmd)

def turbo_trace_cb(k, data, t='T'):
    turbo = data.get_value(k)
    ft = data.find_v(t + 'FT')
    if turbo == 'YES':
        data.update_combo(ft, [], False)
    else:
        data.update_combo(ft, ['Turbo'], False)

def turbo_cmd_cb(dev, cmd, val=None):
    if val == None:
        return cmd

def turbo_fmt_cb(val, read=True):
    if read:
        return 'YES' if val[0] == '1' else 'NO'

def ft_trace_cb(k, data, t='T'):
    ft = data.find_v(k)
    val = find_key(ft.value, data.get_value(k))
    md = data.find_v(t + 'MD')
    if val == 'Turbo':
        data.update_combo(md, [], False)
    else:
        data.update_combo(md, ['16QAM'], False)

def md_trace_cb(k, data, t='T'):
    md = data.find_v(k)
    val = find_key(md.value, data.get_value(k))
    turbo = data.get_value('EID') == 'YES'
    cr = data.find_v(t+'CR')
    if val == 'BPSK':
        if not turbo:
            data.update_combo(cr, ['1/2'], True)
        else:
            data.update_combo(cr, ['5/16', '21/44'], True)
    if val == 'QPSK':
        if not turbo:
            data.update_combo(cr, ['1/2', '3/4', '7/8'], True)
        else:
            data.update_combo(cr, ['1/2', '5/16'], False)
    if val == '16QAM':
        data.update_combo(cr, ['3/4', '7/8'], True)

def dr_fmt_cb(val, read=True):
    if read:
        f = float(val)
        return '%g' % f
    else:
        f = float(val)
        return "%08.3f" % f

def fq_fmt_cb(val, read=True):
    if read:
        f = float(val)
        return '%g' % f
    else:
        f = float(val)
        return "%09.4f" % f

def tpl_fmt_cb(val, read=True):
    if read:
        f = float(val)
        f = -abs(f)
        return '%g' % f
    else:
        f = float(val)
        f = abs(f)
        return "%04.1f" % f

def rx_trace_cb(cmd, cmds):
    trace_cb(cmd, cmds, t='R')

def rsw_fmt_cb(val, read=True):
    if read:
        i = int(val)
        return '%g' % i
    else: 
        i = int(val)
        return '%03d' % i

def flt_fmt_cb(val, read=True, fltn=0):
    if read and fltn == 0:
        ret = []
        for i in range(0, 3):
            ret.append('1' if int(val[i]) else '0')
        flt_fmt_cb.cache = ret
    elif fltn:
        ret = flt_fmt_cb.cache
    return ret[fltn]

def rsl_fmt_cb(val, read=True):
    if read:
        i = val[-2:]
        return '-%s' % i

def rfo_ebn_fmt_cb(val, read=True):
    if read:
        f = float(val)
        return '%g' % f

def get_menu(dev):
    return OD([('Control', control_cb), ('Monitor', monitor_cb)])

def get_ctrl(dev):
    ctrl = Data(send=True, io_cb=cmd_io_cb)
    ctrl.add_page('Modulator')
    ctrl.add('EID', label='Turbo', wdgt='entry', state='readonly', text='???', cmd_cb=turbo_cmd_cb, fmt_cb=turbo_fmt_cb, trace_cb=turbo_trace_cb)
    ctrl.add('TFT', label='Tx FEC Type', wdgt='radio', value=OD([('Viterbi','1'),('Turbo','6')]), trace_cb=ft_trace_cb)
    ctrl.add('TMD', label='Tx Modulation Type', wdgt='radio', value=OD([('BPSK',0),('QPSK',1),('16QAM',4)]), trace_cb=md_trace_cb)
    ctrl.add('TCR', label='Tx FEC Code Rate', wdgt='radio', value=OD([('1/2',2),('3/4',4),('7/8',5),('19/20',6),('21/44',1),('5/16',0)]))
    ctrl.add('TXO', label='Tx Carrier State', wdgt='radio', value=OD([('ON',1),('OFF',0)]))
    ctrl.add('TDR', label='Tx Data Rate, kbps', wdgt='spin', value=Data.spn(2.4, 9980, .001), fmt_cb=dr_fmt_cb)
    ctrl.add('TFQ', label='Tx Frequency, MHz', wdgt='spin', value=Data.spn(50, 90, .001), fmt_cb=fq_fmt_cb)
    ctrl.add('TPL', label='Tx Power Level', wdgt='spin', value=Data.spn(-40, 0, .1), fmt_cb=tpl_fmt_cb)
    ctrl.add('TSC', label='Tx Scrambler', wdgt='radio', value=OD([('ON',1),('OFF','0')]))
    ctrl.add_page('Demodulator')
    ctrl.add('EID', label='Turbo', wdgt='entry', state='readonly', text='???', cmd_cb=turbo_cmd_cb, fmt_cb=turbo_fmt_cb, trace_cb=lambda k,d: turbo_trace_cb(k,d,'R'))
    ctrl.add('RFT', label='Rx FEC Type', wdgt='radio', value=OD([('Viterbi',1),('Turbo',6)]), trace_cb=lambda k,d: ft_trace_cb(k,d,'R'))
    ctrl.add('RMD', label='Rx Demod type', wdgt='radio', value=OD([('BPSK',0),('QPSK',1),('16QAM',4)]), trace_cb=lambda k,d: md_trace_cb(k,d,'R'))
    ctrl.add('RCR', label='Rx FEC Code Rate', wdgt='radio', value=OD([('1/2',2),('3/4',4),('7/8',5),('19/20',6),('21/44',1),('5/16',0)]))
    ctrl.add('RDR', label='Rx Data Rate, kbps', wdgt='spin', value=Data.spn(2.4, 9980, .01), fmt_cb=dr_fmt_cb)
    ctrl.add('RFQ', label='Rx Frequency, MHz', wdgt='spin', value=Data.spn(50, 90, .001), fmt_cb=fq_fmt_cb)
    ctrl.add('RSW', label='Rx Sweep Width, kHz', wdgt='spin', value=Data.spn(1, 32), fmt_cb=rsw_fmt_cb)
    ctrl.add('RDS', label='Rx Scrambler', wdgt='radio', value=OD([('ON',1),('OFF',0)]))
    return ctrl

def get_mntr(dev):
    mntr = Data(io_cb=cmd_io_cb, send=True)
    mntr.add_page('mntr0')
    aa = lambda k, send, msg, fltn: mntr.add(k, wdgt='alarm', send=send, msg=msg, cmd='FLT', fmt_cb=lambda val, read=True, fltn=fltn: flt_fmt_cb(val, read, fltn), trace_cb=alarm_trace_cb)
    aa('FLT0', True, 'Unit fault', 0)
    aa('FLT1', False, 'TX fault', 1)
    aa('FLT2', False, 'RX fault', 2)
    mntr.add('RSL', wdgt='entry', state='readonly', pack_forget=True, fmt_cb=rsl_fmt_cb, msg='RX Level, dBm')
    mntr.add('EBN', wdgt='entry', state='readonly', pack_forget=True, fmt_cb=rfo_ebn_fmt_cb, msg='RX Eb/No, dB')
    mntr.add_page('mntr1')
    mntr.add('RSL', wdgt='entry', state='readonly', label='RX Level, dBm', fmt_cb=rsl_fmt_cb)
    mntr.add('EBN', wdgt='entry', state='readonly', label='RX Eb/No, dB', fmt_cb=rfo_ebn_fmt_cb)
    mntr.add('BFS', wdgt='entry', state='readonly', label='Buffer Fill, %')
    mntr.add('RFO', wdgt='entry', state='readonly', label='Freq Offset, kHz', fmt_cb=rfo_ebn_fmt_cb)
    mntr.add('BER', wdgt='entry', state='readonly', label='RX BER')
    mntr.add('TMP', wdgt='entry', state='readonly', label='Temperature')
    mntr.columns=2
    return mntr

