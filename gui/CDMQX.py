
from collections import OrderedDict as OD
from copy import deepcopy
from . import CDM570
from util.columns import *
from util import Data, CachedDict, proxy, control_cb, monitor_cb, dev_io_cb, alarm_trace_cb

cache = CachedDict()

def dr_fmt_cb(val, read=True):
    if read:
        f = float(val)
        return '%g' % f
    else:
        f = float(val)
        return '%09.3f' % f

def flt_fmt_cb(val, read=True, fltn=0):
    if not hasattr(flt_fmt_cb, 'cache'):
        flt_fmt_cb.cache = None
    if read and fltn == 0:
        ret = []
        ret.append(val[0])
        for i in range(1, 8, 2):
            flt = val[i:i+2]
            ret.append(flt)
        flt_fmt_cb.cache = ret
    elif fltn:
        ret = flt_fmt_cb.cache
    return ret[fltn]
flt_fmt_cb.msgs = ['Unit fault', 'Slot1', 'Slot2', 'Slot3', 'Slot4']

def dev_cmd(dev, cmd):
    if c_serial in dev and c_addr in dev:
        return proxy.call(dev, 'CDM570.cmd', dev[c_serial], dev[c_addr], cmd)

def get_ctrl(dev, cd=None):
    if dev['devdata'] == 'mod':
        data = CDM570.get_ctrl(dev)
        data.pop(1)
        data.select(0)
        data.cmds['TCR'].value = OD([('1/2',2),('3/4',4),('7/8',5),('17/18',6),('21/44',1),('5/16',0)])
        data.cmds['TDR'].fmt_cb = dr_fmt_cb
        return data
    elif dev['devdata'] == 'demod':
        data = CDM570.get_ctrl(dev)
        data.pop(0)
        data.select(0)
        data.cmds['RCR'].value = OD([('1/2',2),('3/4',4),('7/8',5),('17/18',6),('21/44',1),('5/16',0)])
        data.cmds['RDR'].fmt_cb = dr_fmt_cb
        return data

def get_subdevices(dev):
    who = dev_cmd(dev, 'WHO')
    grp = dev_cmd(dev, 'GRP')
    if not who or not grp:
        return
    ret = []
    addr = int(dev['addr'])
    who = who.split(',')
    ctrl = CDM570.get_ctrl(dev)
    for i in range(0, len(who)):
        d1 = deepcopy(dev)
        if who[i][0] == '1':
            d1['name'] = '.'.join([dev['name'], ctrl[0].name, '%d' % (i + 1)])
            d1['devdata'] = 'mod'
            ret.append(d1)
        elif who[i][0] == '2':
            d1['name'] = '.'.join([dev['name'], ctrl[1].name, '%d' % (i + 1)])
            d1['devdata'] = 'demod'
            ret.append(d1)
    grp = int(grp)
    if grp & 1:
        for i in (0,1):
            ret[i]['addr'] = '%d' % addr
    if grp & 2:
        for i in (2,3):
            ret[i]['addr'] = '%d' % (addr + 2)
    return ret

def get_menu(dev):
    subd = cache.get(lambda: get_subdevices(dev), dev['name'], dev['server'], dev['addr'])
    menu = OD()
    menu['Control'] = OD()
    menu['Monitor'] = OD()
    for i in subd:
        menu['Control'][i['name']] = lambda dev, d=i: control_cb(d)
        menu['Monitor'][i['name']] = lambda dev, d=i: monitor_cb(d)
    return menu

def flt_fmt_cb(val, read=True, fltn=0):
    if read and fltn == 0:
        ret = int(val[0], 16)
        val = val[1:]
        cc = []
        for i in range(0, 4):
            v1 = val[2*i:2*i+1]
            cc.append(int(v1, 16))
        flt_fmt_cb.cache = cc
    elif fltn and hasattr(flt_fmt_cb, 'cache'):
        cc = flt_fmt_cb.cache
        ret = cc[fltn-1]
    return '1' if ret else '0'

def get_mntr(dev):
    mntr = Data(io_cb=CDM570.cmd_io_cb, send=True)
    mntr.add_page('mntr0')
    aa = lambda k, send, msg, fltn: mntr.add(k, wdgt='alarm', send=send, msg=msg, cmd='FLT', fmt_cb=lambda val,read=True: flt_fmt_cb(val, read, fltn=fltn), trace_cb=alarm_trace_cb)
    aa('FLT0', True, 'Unit fault', 0)
    aa('FLT1', False, 'Slot 1', 1)
    aa('FLT2', False, 'Slot 2', 2)
    aa('FLT3', False, 'Slot 3', 3)
    aa('FLT4', False, 'Slot 4', 4)
    mntr.add('TMP', wdgt='entry', msg='Temperature')
    if dev['devdata'] == 'mod':
        return mntr
    if dev['devdata'] == 'demod':
        mntr1 = CDM570.get_mntr(dev)
        mntr.add_page(name=mntr1[1].name, cmds=mntr1[1])
        return mntr

