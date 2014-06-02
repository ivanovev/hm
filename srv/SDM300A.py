
from util.serial import query_serial

def StripData(out):
	n = out.find('_')
	if n != -1: out = out[n + 1:]
	out = out.replace('\n', ';')
	out = out.replace('\r', ';')
	out = out.replace(']', ';')
	out = out.replace(';;', ';')
	out = out.strip(';')
	return out

def SDM300A_cmd(port='ttyUSB0', addr='1', param='REM', val=''):
    """
    Функция для доступа к параметрам модема SDM300A
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param addr - 0, 1, 2...
    @param param - REM, MF, RF... см. мануал
    @param val - новое значение при записи, пустая строка при чтении
    @return - текущее значение
    """
    if val:
        query_serial(port, 9600, 7, 'E', 2, '<%s/REM_\r' % addr, ']')
    if addr == '':
        return
    bp = ((param == 'MF' or param == 'AMRV') and (val != None))
    rf = ''
    if bp:
        rf = SDM300A_cmd(port, addr, 'RF')
    if not val:
        val = ''
    q = '<%s/%s_%s\r' % (addr, param, val)
    out = query_serial(port, 9600, 7, 'E', 2, q, ']')
    if not out:
        return ''
    if bp and rf:
        SDM300A_cmd(port, addr, 'RF', rf)
    if param == 'REM':
        return 'REM'
    return StripData(out)

