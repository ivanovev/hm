
from collections import OrderedDict as OD
from copy import deepcopy
from util import Data, monitor_cb

hm_SL2048_io_cb = lambda d,c: 'SL2048.cmd %s %s %s' % (d['serial'], d['addr'], c)

def get_menu(dev):
    menu = OD()
    devices = ['Modulator', 'Demodulator']
    devdata = ['mod', 'demod']
    cbs = OD([('Monitor', monitor_cb)])
    names = []
    for i in range(0, len(devices)):
        names.append('.'.join([dev['name'], devices[i]]))
    for k,v in cbs.items():
        menu[k] = OD()
        for i in range(0, len(devices)):
            d1 = deepcopy(dev)
            d1['name'] = names[i]
            d1['devdata'] = devdata[i]
            menu[k][devices[i]] = lambda dev, d1=d1: v(d1)
    return menu

def get_mntr(dev):
    if dev['devdata'] == 'mod':
        mntr_mod = Data(io_cb=hm_SL2048_io_cb)
        mntr_mod.add_page('mod')
        mntr_mod.add('TFAULT', wdgt='alarm', msg='TFAULT')
        return mntr_mod
    if dev['devdata'] == 'demod':
        mntr_demod = Data(io_cb=hm_SL2048_io_cb)
        mntr_demod.add_page('demod')
        mntr_demod.add('RCD', wdgt='alarm', msg='RCD')
        mntr_demod.add('RDEC', wdgt='alarm', msg='RDEC')
        mntr_demod.add('RSYNTH', wdgt='alarm', msg='RSYNTH')
        mntr_demod.add('REBNO', wdgt='entry', state='readonly', pack_forget=True, msg='Eb/No')
        mntr_demod.add('RBER', wdgt='entry', state='readonly', pack_forget=True, msg='BER')
        mntr_demod.add_page('demod1')
        mntr_demod.add('REBNO', wdgt='entry', state='readonly', label='Eb/No')
        mntr_demod.add('RBER', wdgt='entry', state='readonly', label='BER')
        mntr_demod.add('RAGC', wdgt='entry', state='readonly', label='AGC')
        mntr_demod.add('RROFFSET', wdgt='entry', state='readonly', label='ROFFSET')
        return mntr_demod

