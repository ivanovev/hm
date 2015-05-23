
from . import gui, srv
from util.columns import *
from util.misc import app_devtypes, app_devdata

devdata = lambda: app_devdata('HM', get_columns([c_serial, c_addr]), app_devtypes(gui))

