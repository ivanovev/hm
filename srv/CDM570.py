
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
    endstr = '\n'
    if param.upper() == 'FRW':
        endstr = ''
    out = query_serial(port, 9600, 8, 'N', 1, q, endstr, True)
    #print(out)
    if not out:
        return
    if val:
        return val
    i = out.find('=')
    if i > 0:
        out = out[i+1:]
    out = out.strip()
    return out

