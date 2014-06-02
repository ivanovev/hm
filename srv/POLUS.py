
from util.serial import query_serial

polus_azcmd = '1'
polus_statuscmd = '8'

def merge_bytes(msb, lsb):
    return '%d' % ((int(msb, 16) << 8) | int(lsb, 16))

def merge_words(r):
    if not r:
        return r
    rr = r.split()
    return '%s %s' % (merge_bytes(rr[1], rr[2]), merge_bytes(rr[3], rr[4]))

def POLUS_azcmd(port='ttyUSB0', azcmd=''):
    '''
    Получить/задать номер команды использующийся для перемещений антенны по азимуту
    @n в основном это должно быть '3', но иногда может быть и '1'
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param azcmd - '3' или '1', пустая строка - запрос
    @return - номер команды
    '''
    global polus_azcmd
    if azcmd in ['3', '1']:
        polus_azcmd = azcmd
        return azcmd
    else:
        return polus_azcmd

def POLUS_statuscmd(port='ttyUSB0', statuscmd=''):
    '''
    Получить/задать номер команды для получения состояния антенны
    @n в основном это должно быть '0', но иногда может быть и '8'
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @return - номер команды
    '''
    global polus_statuscmd
    if statuscmd in ['0', '8']:
        polus_statuscmd = statuscmd
        return statuscmd
    else:
        return polus_statuscmd

def POLUS_cmd(port='ttyUSB0', cmd=polus_statuscmd, param1='0', param2='0'):
    """
    Функция для работы с блоками ПОЛЮС
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param cmd - 0, 1, 2... 15 - номер команды
    @param param1 - параметр1: 0, 1, 2... 65535
    @param param2 - параметр1: 0, 1, 2... 65535
    @return - набор байт (0xAA 0xBB 0xCC 0xDD 0xEE)
    """
    cmd = int(cmd)
    param1 = int(param1)
    param2 = int(param2)
    p = bytes([cmd, int(param1/256), param1%256, int(param2/256), param2%256])
    cksum = 0
    for i in p:
        cksum += i
    cksum %= 256
    q = bytes([170]) + p + bytes([cksum]) + bytes([85])
    #for i in range(0, len(q)): print(q[i])
    r = query_serial(port, 9600, 8, 'N', 1, q, 85, dtr=True, rts=False)
    if len(r) < 8:
        return ''
    if r[0] != 170:
        return ''
    r = r[1:]
    ret = ['0x%.2X' % r[i] for i in range(0, 5)]
    return ' '.join(ret)

def POLUS_status(port='ttyUSB0'):
    '''
    Получить байт статуса
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @return - байт статуса
    '''
    r = POLUS_cmd(port, cmd='8')
    if not r:
        return r
    return r.split()[0]

def POLUS_ae(port='ttyUSB0', ae='', e='1'):
    '''
    Получить направление/переместить антенну по азимуту или углу места
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param ae - 0, 1, 2... 65536
    @param e - '0' - азимут, '1' - угол места
    @return - координата по азимуту или углу места
    '''
    if ae:
        if e == '0':
            global polus_azcmd
            POLUS_cmd(port, cmd=polus_azcmd, param1=ae)
        else:
            POLUS_cmd(port, cmd='4', param2=ae)
        return ae
    else:
        global polus_statuscmd
        r = POLUS_cmd(port, cmd=polus_statuscmd)
        if not r:
            return r
        rr = r.split()
        if e == '0':
            msb,lsb = rr[1], rr[2]
        else:
            msb,lsb = rr[3], rr[4]
        return merge_bytes(msb, lsb)

def POLUS_az(port='ttyUSB0', az=''):
    '''
    Получить направление по азимуту/переместить антенну по азимуту
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param az - 0, 1, 2... 65536
    @return - координата по азимуту
    '''
    return POLUS_ae(port, az, '0')

def POLUS_el(port='ttyUSB0', el=''):
    '''
    Получить направление по углу места/переместить антенну по углу места
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param el - 0, 1, 2... 65536
    @return - координата по углу места
    '''
    return POLUS_ae(port, el, '1')

def POLUS_limae(port='ttyUSB0', lim1='', lim2='', e='0'):
    '''
    Получить/задать границы рабочей зоны по азимуту или углу места
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param el - 0, 1, 2... 65536
    @param e - '0' - азимут, '1' - угол места
    @return - границы рабочей зоны по азимуту
    '''
    if lim1 and lim2:
        if e == '0':
            return merge_words(POLUS_cmd(port, cmd='11', param1=lim1, param2=lim2))
        else:
            return merge_words(POLUS_cmd(port, cmd='13', param1=lim1, param2=lim2))
    else:
        if e == '0':
            r = POLUS_cmd(port, '10')
        else:
            r = POLUS_cmd(port, '12')
        if not r:
            return r
        rr = r.split()
        az1 = merge_bytes(rr[1], rr[2])
        az2 = merge_bytes(rr[3], rr[4])
        return '%s %s' % (az1, az2)

def POLUS_limaz(port='ttyUSB0', lim1='', lim2=''):
    '''
    Получить/задать границы рабочей зоны по азимуту
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param lim1 - 0, 1, 2... 65536
    @param lim2 - 0, 1, 2... 65536
    @return - границы рабочей зоны по азимуту
    '''
    return POLUS_limae(port, lim1, lim2, e='0')

def POLUS_limel(port='ttyUSB0', lim1='', lim2=''):
    '''
    Получить/задать границы рабочей зоны по углу места
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param lim1 - 0, 1, 2... 65536
    @param lim2 - 0, 1, 2... 65536
    @return - границы рабочей зоны по углу места
    '''
    return POLUS_limae(port, lim1, lim2, e='1')

def POLUS_ae0(port='ttyUSB0', az='', el=''):
    '''
    Установить новые значения координат по азимуту и углу места
    @n или получить текущие значения по обоим направлениям
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param az - координата по азимуту
    @param el - координата по углу места
    @return - координаты по азимуту и углу места, одной строкой, через пробел
    '''
    if az and el:
        return merge_words(POLUS_cmd(port, cmd='15', param1=az, param2=el))
    else:
        global polus_statuscmd
        return merge_words(POLUS_cmd(port, cmd=polus_statuscmd, param1='0', param2='0'))

def POLUS_stop(port='ttyUSB0'):
    '''
    Остановка перемещений антенны
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @return - байт статуса
    '''
    global polus_statuscmd
    cmd = '0' if polus_statuscmd == '8' else '8'
    return POLUS_cmd(port, cmd=cmd)

