
from util.serial import query_serial
from util.cache import CachedDict
import pdb

cache = CachedDict()

def SSPBM_addr(port='COM3', addr=''):
    '''
    Получить или задать адрес устройства, подключенного к порту %port%
    @return addr
    '''
    if not addr:
        a = cache.find(port, 'addr')
        return a if a else '1'
    return cache.get(lambda: addr, port, 'addr', forceupd=True)

def SSPBM_cmd(port='COM3', byte2='08', byte3='AA', byte4='AA', byte5='AA', byte6='AA'):
    """
    Функция для доступа к параметрам передатчика SSPBM-KS10-DSE
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @param byte* - байты 2-6 (запрос)
    @return byte* - байты 2-6 (ответ)
    """
    q = bytes([0x55])
    q += bytes([int(SSPBM_addr(port), 16)])
    q += bytes([int(byte2, 16)])
    q += bytes([int(byte3, 16)])
    q += bytes([int(byte4, 16)])
    q += bytes([int(byte5, 16)])
    q += bytes([int(byte6, 16)])
    n = 0
    for i in range (1, len(q)):
        n = n + q[i]
    n %= 256
    q += bytes([n])
    #print('q: ', ' '.join(['%.2X' % i for i in q]))
    out = query_serial(port, 9600, 8, 'N', 1, q, read=True, readlen=8)
    if len(out) == 8:
        #print('out: ', ' '.join(['%.2X' % i for i in out]))
        return ' '.join(['%.2X' % out[i] for i in range(2, 7)])
    else:
        print(out, len(out), type(out))
    return ''

def SSPBM_sn(port='COM3'):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @return серийный номер
    """
    c8 = SSPBM_cmd(port, byte2='08')
    if len(c8):
        cc = c8.split()
        ret = ''
        for i in cc:
            ret += chr(int(i, 16))
        return ret
    return '' 

def cmd_b2_b3(port, b2, b3='AA'):
    cc = SSPBM_cmd(port, byte2=b2, byte3=b3)
    if len(cc):
        cc = cc.split()
        b2 = cc[0]
        b3 = cc[1]
        f = 256.*int(cc[0], 16) + int(cc[1], 16)
        return '%.1f' % (f/10)
    return ''

def SSPBM_temp(port='COM3'):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @return температура
    """
    return cmd_b2_b3(port, '12')

def SSPBM_pwr(port='COM3'):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @return power level
    """
    return cmd_b2_b3(port, '25')

def cmd_gain_atten(port, b3, v=''):
    if v:
        vf = float(v)*10
        b4 = '%.2X' % (vf / 256)
        b5 = '%.2X' % (vf % 256)
        SSPBM_cmd(port, byte2='05', byte3=b3, byte4=b4, byte5=b5, byte6='AA')
        return v
    else:
        return cmd_b2_b3(port, '0A', b3)

def SSPBM_gain(port='COM3', gain=''):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @param gain - SSPBM gain
    @return gain
    """
    return cmd_gain_atten(port, '5A', gain)

def cmd_gain_atten_range(port, b3):
    cc = SSPBM_cmd(port, byte2='0D', byte3=b3)
    if not cc:
        return
    cc = cc.split()
    fmin = 256.*int(cc[0], 16) + int(cc[1], 16)
    fmax = 256.*int(cc[3], 16) + int(cc[4], 16)
    return '%.1f-%.1f' % (fmin/10, fmax/10)

def SSPBM_atten_range(port='COM3'):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @return atten range
    """
    return cmd_gain_atten_range(port, '55')

def SSPBM_gain_range(port='COM3'):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @return gain range
    """
    return cmd_gain_atten_range(port, '5A')

def SSPBM_atten(port='COM3', atten=''):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @param atten - SSPBM atten
    @return atten
    """
    return cmd_gain_atten(port, '55', atten)

def SSPBM_tx(port='COM3', tx=''):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @param tx - SSPBM tx
    @return tx
    """
    if tx:
        if int(tx):
            SSPBM_cmd(port, byte2='02', byte3='A5')
        else:
            SSPBM_cmd(port, byte2='02', byte3='5A')
        return tx
    else:
        c01 = SSPBM_cmd(port, byte2='01')
        if c01:
            return '%d' % (int(c01.split()[3], 16) & 1)
    return ''

def SSPBM_alarm(port='COM3'):
    """
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @return sum alarm
    """
    c01 = SSPBM_cmd(port, byte2='01')
    if c01:
        return '1' if (int(c01.split()[3], 16) & 2) else '0'
    return ''

def SSPBM_csr5(port='COM3'):
    """
    Получить 5-й байт команды 0x05 (CONDITION STATUS RESPONSE)
    @param port - для windows: COM1, COM2..., для *nix: ttyr*...
    @return XX
    """
    csr = SSPBM_cmd(port, byte2='05')
    cc = csr.split()
    if len(cc) == 5:
        return cc[3]
    return ''

