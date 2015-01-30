
from collections import OrderedDict as OD
from copy import deepcopy
from util import Data, alarm_trace_cb
from util.mainwnd import control_cb, monitor_cb
from util.columns import *
from util.cache import CachedDict

def cmd_io_cb(dev, cmd):
    cc = cmd.split()
    cc.insert(0, 'AMT30.cmd')
    cc.insert(1, dev[c_serial])
    cc.insert(2, dev[c_addr])
    return ' '.join(cc)

def fmt_cb_fault(val, read=True, fltn=0):
    if not hasattr(fmt_cb_fault, 'cache'):
        fmt_cb_fault.cache = None
    flts = ['DMD', 'MOD', 'TX', 'IRX', 'CEQ']
    if read and fltn == 0:
        ret = []
        for i in flts:
            ret.append('1' if val.find(i + '_FLT') != -1 else '0')
        fmt_cb_fault.cache = ret
    elif fltn:
        ret = fmt_cb_mfs.cache
    return ret[fltn]
fmt_cb_fault.msgs = ["Temp FLT", "Synthesiser FLT", "Power Detector FLT", "+12 VDC Supply FLT"]

def data_fmt_cb(val, read=True, coef=1000):
    if read:
        bps = val.split()[0]
        kbps = float(bps)/coef
        return '%g' % kbps
    else:
        kbps = float(val)*coef
        return '%d' % int(kbps)

def desmode_fmt_cb(val, read=True, coef=1000):
    if read:
        return val.split('-')[0]
    else:
        return val

def get_ctrl(dev):
    if 'devdata' not in dev:
        return
    if dev['devdata'].find('mod') == 0:
        ctrl_mod = Data(io_cb=cmd_io_cb, send=True)
        ctrl_mod.add_page('Modulator')
        if dev['devdata'][-1] == 't':
            ctrl_mod.add('CODE',label='FEC codec',wdgt='radio',value=['Turbo','Viterbi'])
        ctrl_mod.add('MOD',label='TX output',wdgt='radio',value=['Enable','Disable'])
        ctrl_mod.add('MT',label='Modulation',wdgt='radio',value=['BPSK','QPSK','8PSK','16QAM'])
        ctrl_mod.add('RATE',label='Encoder',wdgt='radio',value=['1/2','3/4','C3/4','7/8','19/20'])
        ctrl_mod.add('DATA',label='Data rate,kbps',wdgt='spin',value=Data.spn(9.6,10000,.1),fmt_cb=data_fmt_cb)
        ctrl_mod.add('CARRIER',label='Modulator Frequency,MHz',wdgt='spin',value=Data.spn(52,176,.001),fmt_cb=lambda val,read=True: data_fmt_cb(val,read,coef=1000000))
        ctrl_mod.add('SCRAM',label='Scrabler',wdgt='radio',value=['Enable','Disable'])
        return ctrl_mod
    if dev['devdata'].find('demod') == 0:
        ctrl_demod = Data(io_cb=cmd_io_cb, send=True)
        ctrl_demod.add_page('Demodulator')
        if dev['devdata'][-1] == 't':
            ctrl_demod.add('CODE',label='FEC codec',wdgt='radio',value=['Turbo','Viterbi'])
        ctrl_demod.add('ACQ',label='Acquisition',wdgt='radio',value=['FFT','SWEEP','FFT-SWEEP'])
        ctrl_demod.add('MT',label='Demodulation',wdgt='radio',value=['BPSK','QPSK','8PSK','16QAM'])
        ctrl_demod.add('RATE',label='Encoder',wdgt='radio',value=['1/2','3/4','C3/4','7/8','19/20'])
        ctrl_demod.add('DATA',label='Data rate,kbps',wdgt='spin',value=Data.spn(9.6,10000,.1),fmt_cb=data_fmt_cb)
        ctrl_demod.add('CARRIER',label='Modulator Frequency,MHz',wdgt='spin',value=Data.spn(52,176,.001),fmt_cb=lambda val,read=True: data_fmt_cb(val,read,coef=1000000))
        ctrl_demod.add('SWEEP',label='Sweep width,khz',wdgt='spin',value=Data.spn(1,512,.001),fmt_cb=data_fmt_cb)
        ctrl_demod.add('DESC',label='Descrabler',wdgt='radio',value=['Enable','Disable'])
        ctrl_demod.add('DIFF',label='Differential decoder',wdgt='radio',value=['Enable','Disable'])
        ctrl_demod.add('DESMODE',label='Descrambler mode',wdgt='radio',value=['IESS','CCITT'],fmt_cb=desmode_fmt_cb)
        return ctrl_demod

def get_devinfo(dev):
    devinfo = ''
    port = dev[c_serial] if c_serial in dev else ''
    addr = dev[c_addr] if c_addr in dev else ''
    devinfo = proxy.call(dev, 'AMT30.devinfo', port, addr)
    if not devinfo:
        return
    dd = devinfo.split()
    return dd

cache = CachedDict()

def get_menu(dev):
    dd = cache.get(lambda: get_devinfo(dev), dev[c_name], dev[c_type], dev[c_serial], dev[c_addr] if c_addr in dev else '')
    if not dd:
        return
    devices = []
    for d in dd:
        dev1 = deepcopy(dev)
        if d[0] == 'T':
            dev1[c_name] = '%s.%s' % (dev[c_name], 'Modulator')
            dev1[c_addr] = '%s/0' % (dev[c_addr] if c_addr in dev else '')
            dev1['devdata'] = 'mod'
        elif d[0] == 'R':
            dev1[c_name] = '%s.%s%s' % (dev[c_name], 'Demodulator', d[1])
            dev1[c_addr] = '%s/%s' % (dev[c_addr] if c_addr in dev else '', d[1])
            dev1['devdata'] = 'demod'
        else:
            continue
        if d[-1] == 't':
            dev1['devdata'] += '_t'
        devices.append(dev1)
    cbs = OD([('Control',control_cb), ('Monitor',monitor_cb)])
    menus = OD()
    for k,v in cbs.items():
        menus[k] = OD()
        for dev1 in devices:
            menus[k][dev1['name']] = lambda dev, v1=v, dev1=dev1: v1(dev1)
    return menus

def cd_fmt_cb(val, read=True):
    return '0' if val == 'Yes' else '1'

def dec_fmt_cb(val, read=True):
    return '0' if val == 'Lock' else '1'

def agc_roffset_fmt_cb(val, read=True):
    return val.split()[0]

def ebno_ber_fmt_cb(val, read=True):
    return '9999' if val == 'Decoder not locked' else val

def get_mntr(dev):
    if 'devdata' not in dev:
        return
    if dev['devdata'].find('mod') == 0:
        mntr_mod = Data(io_cb=cmd_io_cb, send=True)
        mntr_mod.add_page('Modulator')
        '''
        mod_mntr_pages = []
        mod_mntr = OD()
        #create_alarms('FAULT', mod_mntr, fmt_cb_fault)
        mod_mntr_pages.append(dict([('cmds',mod_mntr), ('update', True)]))
        '''
        return mntr_mod
    elif dev['devdata'].find('demod') == 0:
        mntr_demod = Data(io_cb=cmd_io_cb, send=True)
        mntr_demod.add_page('demod0')
        mntr_demod.add('CD', wdgt='alarm', msg='Carrier detect', fmt_cb=cd_fmt_cb, trace_cb=alarm_trace_cb)
        mntr_demod.add('DEC', wdgt='alarm', msg='Decoder lock', fmt_cb=dec_fmt_cb, trace_cb=alarm_trace_cb)
        mntr_demod.add_page('demod1')
        mntr_demod.add('AGC', label='RX Level, dBm', wdgt='entry', state='readonly', fmt_cb=agc_roffset_fmt_cb)
        mntr_demod.add('EBNO', label='Eb/NO', wdgt='entry', state='readonly', fmt_cb=ebno_ber_fmt_cb)
        mntr_demod.add('ROFFSET', label='Freq. offset, Hz', wdgt='entry', state='readonly', fmt_cb=agc_roffset_fmt_cb)
        mntr_demod.add('BER', label='Bit error rate', wdgt='entry', state='readonly', fmt_cb=ebno_ber_fmt_cb)
        return mntr_demod

def tooltips(*args):
    return {c_addr:'leave blank in case of RS232'}

