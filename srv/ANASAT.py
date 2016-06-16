
from util import CachedDict
from util.serial import query_serial

cache = CachedDict()

table_act = {
    'TEMP': 0,
    'TXOUT': 1,
    'RXOUT': 1,
    'P12V': 3,
    'PA3': 4,
    'PA4': 5,
    'PA5': 6,
    'PA6': 7,
    'N5V': 8,
    'OSLPLL': 9,
    'TXPLL': 10,
    'RXPLL': 11,
    'LNBV': 12,
    'TXIN': 13,
    'TXOPLL': 17,
    'P5V': 19,
    'PA1': 20,
    'PA2': 21
}

table_offset = {
    'TXGAIN': 0,
    'RXGAIN': 1,
    'TXIN': 2,
    'RXOUT': 3,
    'TXOUT': 4
}

table_p = {
    'RXOUT': 98,
    'TXIN': 100,
    'TXOUT': 102
}

def get_baudrate_valid(baud):
    return int(baud) in [1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600]

def get_query_string(port, cmd):
    a = ANASAT_addr(port)
    param = cmd.split()[0]
    if not a or param in ['R', 'CONNECT', 'DISCONNECT']:
        a = '0000'
    q = '%s02%s%s' % ('\2', a, cmd)
    n = 0
    for i in range (1, len(q)):
        n = n + ord(q[i])
    n %= 256
    q = '%s%X%s' % (q, n, '\3')
    return q

def strip_data(out, cmd):
    if len(out) > 10:
        out = out[7:]
    if len(out) > 3:
        out = out[:len(out)-3]
    cc = cmd.split()
    for c in cc:
        if out.find(c) == 0:
            out = out[len(c)+1:]
        out = out.strip()
    ret = ''
    for i in range(0, len(out)):
        if out[i].isprintable():
            ret += out[i]
    return ret

def ANASAT_cmd(port='COM1', cmd='INFO', *args):
    """
    Функция для доступа к параметрам приёмопередатчика ANASAT
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param cmd - ALARMS, ADC TXIN, ACT P12V... см. мануал
    @return - текущее значение
    """
    cmd = ' '.join([cmd] + list(args))
    cmd = cmd.strip()
    cc = cmd.split()
    param = cc[0]
    a = ANASAT_addr(port)
    if not a and param not in ['R', 'BAUDRATE', 'CONNECT', 'DISCONNECT']:
        a = ANASAT_find(port)
        if not a:
            return ''
    bps = ANASAT_bps(port)
    read = param not in ['BAUDRATE', 'CONNECT', 'DISCONNECT']
    q = get_query_string(port, cmd)
    out = query_serial(port, bps, 8, 'N', 1, q, '\x03', True)
    #print('q:', q, 'cmd:', cmd, 'param:', param, 'bps:', bps, 'read:', read, 'len(out)', len(out), 'out:', out)
    if not out: return ''
    if param in ['TX', 'TXR', 'TXREQ', 'TXREQUEST', 'TXCHAN', 'RXCHAN', 'TXGAIN', 'RXGAIN', 'TXFREQ', 'RXFREQ'] and len(cc) > 1:
        return cc[1]
    return strip_data(out, cmd)

def ANASAT_BAUDRATE(port='COM1', bps='9600'):
    '''
    Установить скорость которая будет использоваться для работы с приёмопередатчиком
    @n команда BAUDRATE в последовательный порт ПОСЫЛАЕТСЯ
    @param bps - скорость, что-то из списка: 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600
    @n либо пустая строка для запроса текущего значения bps
    @return bps
    '''
    if not get_baudrate_valid(bps):
        return ''
    ANASAT_cmd(port, 'BAUDRATE %s' % bps)
    return ANASAT_bps(port, bps)

def ANASAT_ADC_VREF(port='COM1'):
    '''
    То же самое что и ANASAT.cmd(port, 'ADC_VREF')
    @return ADC_VREF
    '''
    return cache.get(lambda: ANASAT_cmd(port, 'ADC_VREF'), port, 'ADC_VREF')

def ANASAT_ACT(port='COM1', param='TEMP'):
    '''
    Получить offset и gain для параметра param
    @param param - monitor_point из списка:
    @n TEMP, TXOUT, RXOUT, P12V, PA3, PA4, PA5, PA6, N5V, OSLPLL, TXPLL, RXPLL, LNBV, TXIN, TXOPLL, P5V, PA1, PA2
    @return offset gain
    '''
    act = cache.get(lambda: ANASAT_cmd(port, 'ACT'), port, 'ACT')
    if not act:
        return ''
    if param not in table_act:
        return ''
    p = table_act[param]
    aa = act.split()
    if len(aa) < 2*(p+1):
        return ''
    return '%s %s' % (aa[2*p], aa[2*p+1])

def ANASAT_OFFSET_TABLE(port='COM1'):
    a = ANASAT_addr(port)
    offset_table = cache.get(lambda: ANASAT_cmd(port, 'OFFSET_TABLE'), port, 'OFFSET_TABLE')
    if not offset_table and a != '0000':
        a = ANASAT_addr(port, '0000')
        offset_table = cache.get(lambda: ANASAT_cmd(port, 'OFFSET_TABLE'), port, 'OFFSET_TABLE')
        ANASAT_addr(port, a)
    return offset_table

def ANASAT_ADC(port='COM1', param='TEMP'):
    '''
    Получить пересчитанное значение АЦП
    @ для получения непересчинанного значения можно использовать ANASAT.cmd(port, 'ADC %param%')
    @param param - monitor_point из списка:
    @n TEMP, TXOUT, RXOUT, P12V, PA3, PA4, PA5, PA6, N5V, OSLPLL, TXPLL, RXPLL, LNBV, TXIN, TXOPLL, P5V, PA1, PA2
    @return значение %param%
    '''
    adc = cache.get(lambda: ANASAT_cmd(port, 'ADC'), port, 'ADC', duration=10)
    if not adc:
        return
    p = table_act[param]
    aa = adc.split()
    if len(aa) < p + 1:
        return ''
    adc = aa[p]
    if param in ['RXOUT', 'TXIN', 'TXOUT']:
        p = cache.get(lambda: ANASAT_cmd(port, 'P'), port, 'P', duration=10)
        if not p:
            return ''
        tp = table_p[param]
        sp = p[tp:tp+2]
        ip = int(sp, 16)
        if ip >= 128: ip = ip - 256
        #offset_table = cache.get(lambda: ANASAT_cmd(port, 'OFFSET_TABLE'), port, 'OFFSET_TABLE')#, duration=10)
        offset_table = ANASAT_OFFSET_TABLE(port)
        if not offset_table:
            return ''
        ot = offset_table.split()
        tot = table_offset[param]
        fot = float(ot[tot])
        value = ip + fot
        return '%.1f' % value
    elif param in table_act:
        vref = ANASAT_ADC_VREF(port)
        if not vref:
            return ''
        act = ANASAT_ACT(port, param)
        if not act:
            return
        vref = float(vref)
        adc = int(adc, 16)
        vread = (float(adc)/255)*vref
        aa = act.split()
        offset = float(aa[0])
        gain = float(aa[1])
        value = (vread - offset)*gain
        ret = '%.2f' % value
        ret = ret.rstrip('0')
        ret = ret.rstrip('.')
        return ret

def ANASAT_ALARM(port='COM1'):
    '''
    То же самое что и ANASAT.cmd(port, 'ALARM')
    @return ALARM
    '''
    return ANASAT_cmd(port, 'ALARM')

def ANASAT_find(port='COM1'):
    """
    Получить адрес приёмопередатчика ANASAT (ODU Packet Address)
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @return - адрес (например 01FF)
    """
    print('ANASAT_find')
    ANASAT_addr(port, addr='0000')
    ANASAT_bps(port, '9600')
    r = ANASAT_cmd(port, 'DISCONNECT; R 0 1')
    if not r:
        ANASAT_bps(port, '1200')
        r = ANASAT_cmd(port, 'DISCONNECT; R 0 1')
        if not r:
            return ''
    rr = r.split()
    sn = rr[-2]
    a = rr[-1]
    #ANASAT_cmd(port, 'CONNECT %s' % sn)
    ANASAT_addr(port, a)
    if ANASAT_bps(port) != '9600':
        ANASAT_BAUDRATE(port, '9600')
    return a

def ANASAT_addr(port='COM1', addr=''):
    '''
    Получить или задать адрес устройства, подключенного к порту %port%
    @return addr
    '''
    if not addr:
        a = cache.find(port, 'addr')
        return a if a else ''
    return cache.get(lambda: addr, port, 'addr', forceupd=True)

def ANASAT_bps(port='COM1', bps=''):
    '''
    Установить скорость которая будет использоваться для работы с приёмопередатчиком
    @n команда BAUDRATE в последовательный порт НЕ ПОСЫЛАЕТСЯ
    @param bps - скорость, что-то из списка: 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600
    @n либо пустая строка для запроса текущего значения bps
    @return bps
    '''
    if not bps:
        return '%d' % cache.get(lambda: 1200, port, 'bps')
    if not get_baudrate_valid(bps):
        return ''
    cache.get(lambda: int(bps), port, 'bps', forceupd=True)
    return bps

