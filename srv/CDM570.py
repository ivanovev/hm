
from util.serial import query_serial

def CDM570_cmd(port, addr='0', param='EID', val=''):
    """
    Функция для доступа к параметрам модема CDM570
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param addr - 0, 1, 2...
    @param param - EID, RSL, EBN... см. мануал
    @val - новое значение
    @return - текущее значение
    """
    q = ''
    if val:
        q = '<%s/%s=%s\r' % (addr, param, val)
    else:
        q = '<%s/%s?\r' % (addr, param)
    out = query_serial(port, 9600, 8, 'N', 1, q, '\n', True)
    #print(out)
    if not out:
        return
    if val:
        return val
    oo = out.split('/')
    if len(oo) != 2:
        return
    out = oo[1]
    out = out.replace(param, '')
    out = out.replace('\n', '')
    out = out.replace('\r', '')
    out = out.replace('=', '')
    return out

