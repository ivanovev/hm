
from util.serial import query_serial
import pdb

registers_intf = {
    'STRVER'    :   '\x00',
    'STATUS'    :   '\x01',
    'BA_INTF'   :   '\x02',
    'BA_DEMOD'  :   '\x03',
    'BA_MOD'    :   '\x04',
    'BA_BUC'    :   '\x05',
    'BA_REF'    :   '\x06',
    'SPARE1'    :   '\x07',
    'SPARE2'    :   '\x08',
    'SPARE3'    :   '\x09',
    'SECONDS'   :   '\x0A',
    'MINUTES'   :   '\x0B',
    'HOURS'     :   '\x0C',
    'DATE1'     :   '\x0D',
    'DATE2'     :   '\x0E',
    'SPARE4'    :   '\x0F',
    'DEVCNT'    :   '\x10',
    'DEV0_DESC' :   '\x11',
    'DEV0_TYPE' :   '\x12',
    'DEV0_ADDR' :   '\x13',
    'DEV0_EXT'  :   '\x14',
    'DEV1_DESC' :   '\x15',
    'DEV1_TYPE' :   '\x16',
    'DEV1_ADDR' :   '\x17',
    'DEV1_EXT'  :   '\x18',
    'DEV2_DESC' :   '\x19',
    'DEV2_TYPE' :   '\x1A',
    'DEV2_ADDR' :   '\x1B',
    'DEV2_EXT'  :   '\x1C',
    'DEV3_DESC' :   '\x1D',
    'DEV3_TYPE' :   '\x1E',
    'DEV3_ADDR' :   '\x1F',
    'DEV3_EXT'  :   '\x20',
    'DEV4_DESC' :   '\x21',
    'DEV4_TYPE' :   '\x22',
    'DEV4_ADDR' :   '\x23',
    'DEV4_EXT'  :   '\x24',
    'DEV5_DESC' :   '\x25',
    'DEV5_TYPE' :   '\x26',
    'DEV5_ADDR' :   '\x27',
    'DEV5_EXT'  :   '\x28',
    'DEV6_DESC' :   '\x29',
    'DEV6_TYPE' :   '\x2A',
    'DEV6_ADDR' :   '\x2B',
    'DEV6_EXT'  :   '\x2C',
    'DEV7_DESC' :   '\x2D',
    'DEV7_TYPE' :   '\x2E',
    'DEV7_ADDR' :   '\x2F',
    'DEV7_EXT'  :   '\x30',
    'SWVER'     :   '\x31',
    'SWDATE1'   :   '\x32',
    'SWDATE2'   :   '\x33',
    'SPARE5'    :   '\x34',
    'SPARE6'    :   '\x35',
    'RST'       :   '\x36',
    'SETUP'     :   '\x37',
    'BUCV1'     :   '\x38',
    'BUCV2'     :   '\x39',
    'BUCI1'     :   '\x3A',
    'BUCI2'     :   '\x3B',
    'SPARE7'    :   '\x3C',
    'SPARE8'    :   '\x3D',
    'SPARE9'    :   '\x3E',
    'SPARE10'   :   '\x3F',
    'EVLOG1'    :   '\x40',
    'EVLOG2'    :   '\x41',
    'EVLOG3'    :   '\x42',
    'EVLOG4'    :   '\x43',
    'EVTRAP1'   :   '\x44',
    'EVTRAP1'   :   '\x45',
    'EVTRAP1'   :   '\x46',
    'EVTRAP1'   :   '\x47',
    'NAME'      :   '\x48\x4F',
    'DEVMASK'   :   '\x50',
    'RDSETUP'   :   '\x51',
    'RDFORCE'   :   '\x52',
    'RDSTATUS'  :   '\x53',
    'ALARMS1'   :   '\x54',
    'ALARMS2'   :   '\x55',
    'ALMSK1'    :   '\x56',
    'ALMSK2'    :   '\x57',
    'SUMALM'    :   '\x58',
    'BUSUMALM'  :   '\x59',
    'SERIAL'    :   '\x5A\x63',
    'PN'        :   '\x64\x73'
}

registers_demod = {
    'STRVER'    :   '\x00',
    'HWCFG1'    :   '\x01',
    'HWCFG2'    :   '\x02',
    'SETUP1'    :   '\x03',
    'SETUP2'    :   '\x04',
    'REG1'      :   '\x05',
    'RST'       :   '\x06',
    'COMP1'     :   '\x07',
    'COMP2'     :   '\x08',
    'DCGAIN'    :   '\x09',
    'REG2'      :   '\x0A',
    'CENTER1'   :   '\x0B',
    'CENTER2'   :   '\x0C',
    'CENTER3'   :   '\x0D',
    'CENTER4'   :   '\x0E',
    'FPGA_VER'  :   '\x0F',
    'CPLD_VER'  :   '\x10',
    'SWDATE1'   :   '\x11',
    'SWDATE2'   :   '\x12',
    'DSP_VER'   :   '\x13\x1C',
    'SERIAL'    :   '\x1D\x26',
    'PN'        :   '\x27\x36'
}

registers_chan = {
    'STATUS'	:   '\x00',
    'AGC1'	:   '\x01',
    'AGC2'	:   '\x02',
    'EBNO1'	:   '\x03',
    'EBNO2'	:   '\x04',
    'ROFFSET1'	:   '\x05',
    'ROFFSET2'	:   '\x06',
    'ROFFSET3'	:   '\x07',
    'ROFFSET4'	:   '\x08',
    'BER1'	:   '\x09',
    'BER2'	:   '\x0A',
    'BER3'	:   '\x0B',
    'BER4'	:   '\x0C',
    'EMPTY'	:   '\x0D',
    'EMPTY'	:   '\x0E',
    'EMPTY'	:   '\x0F',
    'SETUP1'	:   '\x10',
    'SETUP2'	:   '\x11',
    'SETUP3'	:   '\x12',
    'RSREG'	:   '\x13',
    'EMPTY'	:   '\x14',
    'EMPTY'	:   '\x15',
    'BDEPTH1'	:   '\x16',
    'BDEPTH2'	:   '\x17',
    'OFFSET1'	:   '\x18',
    'OFFSET2'	:   '\x19',
    'CARRIER1'	:   '\x1A',
    'CARRIER2'	:   '\x1B',
    'CARRIER3'	:   '\x1C',
    'CARRIER4'	:   '\x1D',
    'SWEEP1'	:   '\x1E',
    'SWEEP2'	:   '\x1F',
    'SWEEP3'	:   '\x20',
    'SWEEP4'	:   '\x21',
    'DATA1'	:   '\x22',
    'DATA2'	:   '\x23',
    'DATA3'	:   '\x24',
    'DATA4'	:   '\x25',
    'EBNOCR1'	:   '\x26',
    'EBNOCR2'	:   '\x27',
    'EBNOMJ1'	:   '\x28',
    'EBNOMJ2'	:   '\x29',
    'EBNOMN1'	:   '\x2A',
    'EBNOMN2'	:   '\x2B',
    'AGCCR1'	:   '\x2C',
    'AGCCR2'	:   '\x2D',
    'AGCMJ3'	:   '\x2E',
    'AGCMJ4'	:   '\x2F',
    'AGCMN1'	:   '\x30',
    'AGCMN2'	:   '\x31'
}

registers_mod = {
    'STRVER'    :   '\x00',
    'STATUS'    :   '\x01',
    'FAULT'     :   '\x02',
    'FIVE1'     :   '\x03',
    'FIVE2'     :   '\x04',
    'TWELVE1'   :   '\x05',
    'TWELVE2'   :   '\x06',
    'WARM'      :   '\x07',
    'RST'       :   '\x08',
    'SETUP1'    :   '\x09',
    'SETUP2'    :   '\x0A',
    'SETUP3'    :   '\x0B',
    'SETUP4'    :   '\x0C',
    'LEVEL1'    :   '\x0D',
    'LEVEL2'    :   '\x0E',
    'CALIB1'    :   '\x0F',
    'CALIB2'    :   '\x10',
    'CARRIER1'  :   '\x11',
    'CARRIER2'  :   '\x12',
    'CARRIER3'  :   '\x13',
    'CARRIER4'  :   '\x14',
    'DATA1'     :   '\x15',
    'DATA2'     :   '\x16',
    'DATA3'     :   '\x17',
    'DATA4'     :   '\x18',
    'TEST'      :   '\x19',
    'RSREG'     :   '\x1A',
    'HWCFG'     :   '\x1B',
    'EEPROM'    :   '\x1C\x25',
    'VERSION'   :   '\x26\x2F',
    'SERIAL'    :   '\x30\x39',
    'PN'        :   '\x3A\x49'
}

def get_register_addr(num, param):
    if num == 'i' or num == '' and registers_intf.has_key(param):
        return registers_intf[param]
    elif num == 'm' and registers_mod.has_key(param):
        return registers_mod[param]
    elif num == 'd' and registers_demod.has_key(param):
        return registers_demod[param]
    elif num[0] == 'd' and registers_chan.has_key(param):
        return registers_chan[param]
    else:
        return None

def get_register_addr1(num, param):
    if param[0:2] == '0x':
        return chr(int(param, 16))
    a = get_register_addr(num, param)
    if a != None: return a[0]

def get_byte_count(num, param, val):
    if val == None:
        if param[0:2] == '0x': return chr(1)
        a = get_register_addr(num, param)
        if len(a) == 2:
            return chr(ord(a[1]) - ord(a[0]) + 1)
        return chr(0x01)
    else:
        return chr(len(val.split()))

def get_data_bytes(val):
    if val == None:
        return ''
    res = ''
    for i in val.split():
        res += chr(int(i, 16))
    return res

def get_checksum(q):
    n = 0
    for i in range(1, len(q)):
        n += ord(q[i])
    return chr(256 - (n % 256))

def AMT30_RS485(port, addr, param, val=''):
    """
    Функция для доступа к параметрам модема AMT30 через порт RS485
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param addr - X/Y, где X,Y = 0, 1, 2... если RS485
    @param param - FAULT, EBNO1, EBNO2... см. мануал
    @param val - новое значение при записи, пустая строка при чтении
    @return - текущее значение
    """
    n = addr.find('/')
    if n == None: return
    num = addr[n+1:]
    addr = addr[:n]
    # opening flag
    q = '\x7E'
    # destination address
    q += chr(int(addr, 16))
    # protocol id
    q += chr(0x00)
    # command type
    if val == None: q += chr(0x01)
    else: q += chr(0x00)
    # register address 1
    if num == '': q += chr(0x00)
    else:
        if num[0].isalpha():
            q += chr(int('0' + num[1:], 16))
        else:
            q += chr(int(num, 16))
    # register address 2
    a = get_register_addr1(num, param)
    if a == None: return
    q += a
    # number of bytes
    q += get_byte_count(num, param, val)
    # error code
    q += chr(0x00)
    # data field
    q += get_data_bytes(val)
    # checksum
    q += get_checksum(q)
    # closing flag
    q += '\x7E'
    out = query_serial(port, 9600, 8, 'N', 1, q, '\x7E')
    if out == None: return
    out = out.replace(q, '')
    if len(out) < 11: return
    out1 = ''
    for i in range(8, len(out) - 2):
        out1 += '0x%.2X' % ord(out[i]) + ' '
    return out1.rstrip()

def AMT30_RS232(port, addr, param, val=''):
    """
    Функция для доступа к параметрам модема AMT30 через порт RS232
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param addr - номер устройства
    @n '' (пустая строка) - команда интерфейса
    @n 0 - команда модулятора
    @n 1, 2... команда демодулятора
    @param param - FAULT, EBNO1, EBNO2... см. мануал
    @param val - новое значение при записи, пустая строка при чтении
    @return - текущее значение
    """
    q = param
    addr = addr.split('/')[-1]
    if addr:
        addr = int(addr)
        if addr == 0:
            'Modulator RS232'
            q = 'T ' + q
        elif addr > 0:
            'Demodulator RS232'
            q = 'R%d %s' % (addr, q)
    if val:	q += ' ' + val
    q += '\r'
    read = not val or True
    out = query_serial(port, 9600, 8, 'N', 1, q, '> ', read=read);
    if not read:
        return val
    if not out: return
    if out.count('=') == 1:
        x = out.find('=')
        r = out.find('\r', x, len(out))
        out = out[x+1:r]
    out = out.strip('> \n\r')
    if not out:
        return val
    return out


def AMT30_cmd(port, addr, param, val=''):
    """
    Функция для доступа к параметрам модема AMT30
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param addr - адрес устройства
    @n для RS232 - номер устройства внутри блока AMT30:
    @n '' (пустая строка) - команда интерфейса
    @n 0 - команда модулятора
    @n 1, 2... команда демодулятора
    @n для RS485:
    @n строка вида X/Y
    @n X - адрес устройства на шине RS485
    @n Y - номер устройства (см. RS232)
    @param param - FAULT, EBNO1, EBNO2... см. мануал
    @param val - новое значение при записи, пустая строка при чтении
    @return - текущее значение
    """
    aa = addr.split('/')
    if len(aa) == 1 or not aa[0]:
        return AMT30_RS232(port, addr, param, val)
    elif len(aa) == 2:
        return AMT30_RS485(port, addr, param, val)

def AMT30_devinfo(port, addr=''):
    """
    Получить информацию об устройстве AMT3X
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param addr - адрес устройства (см. описание AMT30.cmd)
    @return - внутренняя структура устройств AMT3X в виде строки, например:
    @n T0 R1 R2
    """
    aa = addr.split('/')
    if len(aa) == 1 or not aa[0]:
        di = AMT30_RS232(port, addr, 'devinfo')
        di = di.replace('\r', '\n')
        di = di.replace('\n\n', '\n')
        dd = di.split('\n')
        ret = []
        for d in dd:
            d1 = d.split()
            alias = d1[-1]
            if 'Modulator' in d1:
                ret.append(alias)
            if 'Demodulator' in d1:
                if alias == 'R':
                    alias = 'R1'
                ret.append(alias)
        return ' '.join(ret)

