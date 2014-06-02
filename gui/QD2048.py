
from collections import OrderedDict as OD
from copy import deepcopy
from util.data import Data
from util.mainwnd import monitor_cb

def flt_fmt_cb(val, read=True, fltn=0):
    return '1'
flt_fmt_cb.msgs = ["CD", "DEC", "RSYNTH"]

def get_menu(dev):
    addr = int(dev['addr'])
    menu = OD()
    menu['Monitor'] = OD()
    for i in range(0, 4):
        d1 = deepcopy(dev)
        d1['name'] = '%s.%s' % (dev['name'], '%d' % (i + 1))
        d1['addr'] = '%d' % (addr + i)
        menu['Monitor'][d1['name']] = lambda dev, d1=d1: monitor_cb(d1)
    return menu

def get_mntr(dev, cc=None):
    mntr = Data(io_cb=lambda d,c,v=None: 'QD2048.cmd %s %s %s' % (d['serial'], d['addr'], c))
    mntr.add_page('mntr0')
    aa = lambda k, send, msg: mntr.add(k, wdgt='alarm', send=send, msg=msg, cmd='FLT', fmt_cb=flt_fmt_cb)
    aa('CD', True, 'CD')
    aa('DEC', True, 'DEC')
    aa('RSYNTH', True, 'RSYNTH')
    mntr.add('EBNO', wdgt='entry', state='readonly', pack_forget=True, msg='Eb/No')
    mntr.add('BER', wdgt='entry', state='readonly', pack_forget=True, msg='BER')
    mntr.add_page('mntr1')
    mntr.add('EBNO', wdgt='entry', state='readonly', label='Eb/No')
    mntr.add('BER', wdgt='entry', state='readonly', label='BER')
    mntr.add('AGC', wdgt='entry', state='readonly', label='AGC')
    mntr.add('ROFFSET', wdgt='entry', state='readonly', label='ROFFSET')
    mntr.cmds.columns=2
    return mntr

