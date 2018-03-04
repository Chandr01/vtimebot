API = '514603679:AAEQKCWG0TbvoYeXPGNgFwfwj1qU7OmyKrE'
import datetime

from dateutil.parser import parse


time = '2018-03-04 22:04:44.033252'
aaa = parse(time)
zzz = datetime.datetime.now() - aaa
print(zzz.min)