
from collections import OrderedDict as OD
from util.mainwnd import control_cb, monitor_cb
from util.data import Data
from util.callbacks import cmd_serial_io_cb, alarm_trace_cb
import copy

def mf_fmt_cb(val, read=True):
    if read:
        f = float(val)
        return '%g' % f
    else:
        f = float(val)
        return "%010.6f" % f

def amrv_fmt_cb(val, read=True, vn=0):
    if read:
        vv = val.split('_')
        vn = vn % 2
        if len(vv) > vn:
            return vv[vn]
        else:
            return val
    else:
        if vn % 2:
            f = float(val)
            setattr(amrv_fmt_cb, 'rate%d' % vn, "%08.3f" % f)
        else:
            return '_'.join([val, getattr(amrv_fmt_cb, 'rate%d' % (vn+1))])

def mop_fmt_cb(val, read=True):
    if read:
        f = float(val)
        return '%g' % f
    else:
        f = float(val)
        return "%05.1f" % f

def adrv_fmt_cb(val, read=True):
    if read:
        v = val.split('_')
        adrv2_fmt_cb.rate = v[1]
        return v[0]
    else:
        v = '_'.join([val, adrv2_fmt_cb.rate])
        return v

def adrv2_fmt_cb(val, read=True):
    if read:
        return adrv2_fmt_cb.rate
    else:
        f = float(val)
        adrv2_fmt_cb.rate = "%08.3f" % f

def swr_fmt_cb(val, read=True):
    if read:
        f = float(val)
        return '%g' % f
    else:
        d = int(val)
        return "%05d" % d

def mfs_fmt_cb(val, read=True, fltn=0):
    flts = ['DMD', 'MOD', 'TX', 'IRX', 'CEQ']
    print(flts[fltn], val.find('%s_FLT' % flts[fltn]))
    return '1' if (val.find('%s_FLT' % flts[fltn]) != -1) else '0'

def rsl_fmt_cb(val, read=True):
    if read:
        val = val.strip('<dBm')
        return val

def csv_fmt_cb(val, read=True):
    if read:
        val = val.split(';')
        return val[0]

def ibfs_fmt_cb(val, read=True):
    if read:
        val = val.strip('%')
        return val

def get_menu(dev):
    return OD([('Control', control_cb), ('Monitor', monitor_cb)])

def get_ctrl(dev):
    ctrl = Data(io_cb=cmd_serial_io_cb)
    ctrl.add_page('Modulator', send=True)
    ctrl.add('RF', label='RF Output', wdgt='radio', value=['ON', 'OFF'])
    ctrl.add('MF', label='Modulator Frequency, MHz', wdgt='spin', value=Data.spn(50, 180, .001), fmt_cb=mf_fmt_cb)
    ctrl.add('AMRV', label='Modulation type', wdgt='radio', value=OD([('QPSK 1/2','1/2'),('QPSK 3/4','3/4'),('QPSK 7/8','7/8'),('BPSK 1/2','BP12')]), fmt_cb=amrv_fmt_cb)
    ctrl.add('AMRV2', label='Data rate, kbps', wdgt='spin', value=Data.spn(2.4, 5000, .1), fmt_cb=lambda val, read: amrv_fmt_cb(val, read, 1), send=False)
    ctrl.add('MOP', label='Power Level, dBm', wdgt='spin', value=Data.spn(-30, -5), fmt_cb=mop_fmt_cb)
    ctrl.add('SE', label='Scrambler Enable', wdgt='radio', value=['ON', 'OFF'])
    ctrl.add('DENC', label='Dif Decoder Enable', wdgt='radio', value=['ON', 'OFF'])
    ctrl.add_page('Demodulator', send=True)
    ctrl.add('DF', label='Demodulator Frequency', wdgt='spin', value=Data.spn(50, 180, .001), fmt_cb=mf_fmt_cb)
    ctrl.add('ADRV', label='Modulation type', wdgt='radio', value=OD([('QPSK 1/2','1/2'),('QPSK 3/4','3/4'),('QPSK 7/8','7/8'),('BPSK 1/2','BP12')]), fmt_cb=lambda val, read: amrv_fmt_cb(val, read, 2))
    ctrl.add('ADRV2', label='Data rate, kbps', wdgt='spin', value=Data.spn(2.4, 5000, .1), fmt_cb=lambda val, read: amrv_fmt_cb(val, read, 3), send=False)
    ctrl.add('SWR', label='Sweep Width, Hz', wdgt='spin', value=Data.spn(0, 70000), fmt_cb=swr_fmt_cb)
    ctrl.add('SR', label='Sweep Reacquision, s', wdgt='spin', value=Data.spn(0, 999))
    ctrl.add('DE', label='Descrambler enable', wdgt='radio', value=['ON', 'OFF'])
    ctrl.add('DDEC', label='Differential decoder', wdgt='radio', value=['ON', 'OFF'])
    return ctrl

def get_mntr(dev):
    mntr = Data(io_cb=cmd_serial_io_cb, send=True)
    mntr.add_page('mntr0')
    aa = lambda k, send, fltn, msg: mntr.add(k, wdgt='alarm', send=send, msg=msg, cmd='MFS', fmt_cb=lambda val, read, fltn=fltn: mfs_fmt_cb(val, read, fltn), trace_cb=alarm_trace_cb)
    aa('DMD', True, 0, 'Modulator')
    aa('MOD', False, 1, 'Demodulator')
    aa('TX', False, 2, 'Interface transmit side')
    aa('IRX', False, 3, 'Interface receive side')
    aa('CEQ', False, 4, 'Common equipment')
    mntr.add('EBN0', wdgt='entry', state='readonly', pack_forget=True, msg='Eb/No')
    mntr.add('CBER', wdgt='entry', state='readonly', pack_forget=True, msg='Corrected BER')
    mntr.add_page('mntr1')
    mntr.add('RSL', wdgt='entry', state='readonly', label='RX Level [dBm]', fmt_cb=rsl_fmt_cb)
    mntr.add('EBN0', wdgt='entry', state='readonly', label='Eb/No')
    mntr.add('CSV', wdgt='entry', state='readonly', label='Current sweep', fmt_cb=csv_fmt_cb)
    mntr.add('CBER', wdgt='entry', state='readonly', label='Corrected BER')
    mntr.add('IBFS', wdgt='entry', state='readonly', label='Buffer fill [%]', fmt_cb=ibfs_fmt_cb)
    mntr.add('RBER', wdgt='entry', state='readonly', label='Raw BER')
    mntr.columns = 2
    return mntr

