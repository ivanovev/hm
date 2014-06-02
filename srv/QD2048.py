
from util.serial import query_serial

def QD2048_cmd(port, addr, param, val = None):
    """
    Функция для доступа к параметрам QD2048
    @param port - для windows: COM1, COM2..., для *nix: ttyS*, ttyUSB*...
    @param addr - 0, 1, 2...
    @param param - EBNO, BER... см. мануал
    @val - новое значение
    @return - текущее значение
    """
    q = param
    if addr != "" and addr != "/":
        n = addr.find("/");
        if n == 0:
            q = "R%s %s" % (addr[1:], q)
        elif n == len(addr) - 1:
            q = "%s %s" % (addr[0:n-1], q)
        elif n != -1:
            q = "%s R%s %s" % (addr[0:n-2], addr[n:], q)
    if val != None:	q += " " + val
    q += "\r"
    out = query_serial(port, 9600, 8, 'N', 1, q, "QD2048>");
    if out == None: return
    x = out.find("=")
    if x != -1:
        n = out.find("\r", x, len(out))
        out = out[x+1:n]
    else:
        m = out.find("\r")
        out = out[m+1:]
        out = out.lstrip()
        n = out.find("\r", m + 2, len(out))
        out = out[:n]
    out = out.lstrip()
    return out;
