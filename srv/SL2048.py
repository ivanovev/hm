
from util.serial import query_serial
from datetime import datetime

def SL2048_cmd(port, addr, param, val = None):
    """
    Функция для доступа к параметрам модема SL2048
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param addr - 0, 1, 2...
    @param param - TMOD, TBPS, TRATE... см. мануал
    @val - новое значение
    @return - текущее значение
    """
    q = param
    if addr != None and addr != "" and addr != "/" and addr != "/0":
        n = addr.find("/")
        num = ""
        if n == None: num = addr
        else: num = addr[n+1:]
        if num != None and num != "":
            if int(num) >= 2:
                q = "%s #%s" % (q, num)
        if n != None:
            if n >= 2:
                q = "%s %s" % (addr[n - 2:], q)
    if val != None: q = "%s %s" % (q, val)
    q += "\r"
    out = query_serial(port, 9600, 8, 'N', 1, q, "SL2048>")
    if out == None: return
    n = out.find("=")
    if n != -1: out = out[n+2:]
    else:
        n = out.find("\r")
        if n != None: out = out[n+2:]
    out = out.lstrip()
    out = out.lstrip("\0")
    n = out.find("\r")
    if n != None: out = out[:n]
    if val != None and val != "" and val != out:
        t1 = datetime.now()
        while True:
            s = query(port, addr, param)
            if s == val:
                break
            t2 = datetime.now()
            if (t2 - t1).seconds > 1:
                break
    return out
