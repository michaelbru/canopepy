import canopenpy as cnp
import canlib 
try:
    ch = canlib.canlib().openChannel(0,canlib.canOPEN_EXCLUSIVE)
    ch.open(bitrate=500000)
    canopen = cnp.CanOpen(ch)
    canopen.setNodeId(1)
except canlib.canError as err:
    print(err)
print(ch.getBusParams())


def getValue(cmd):
    return canopen.SetOsIntCmd(cmd)
   
print(getValue('vr[1]'))