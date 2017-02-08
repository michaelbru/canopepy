import canopenpy as cnp
import canlib 
import time
try:
    ch = canlib.canlib().openChannel(0,canlib.canOPEN_EXCLUSIVE)
    ch.open(bitrate=500000)
    canopen = cnp.CanOpen(ch)
    canopen.setNodeId(1)
except canlib.canError as err:
    print(err)
print(ch.getBusParams())


def getValue(cmd):
    try:
        res = canopen.SetOsIntCmd(cmd)
        if res[-1]==';':
            res=res[:-1]
    except Exception as ex:
        res = None
        print('getValue:',ex)
    return res

def sendCommand(cmd):
    try:
       res = canopen.SetOsIntCmd(cmd)
    except :
        print('SendCommand',res)

def console():
 
    while True:
        rs = None
        cmd = input('@>>')
        try:
            if cmd ==';': 
           #     close()
                break
            rs = getValue(cmd)
            if rs is not  None :
                print(rs)
        except Exception as ex:
            print(ex)

print(getValue('vr[1]'))
print(getValue('um'))
print(getValue('mo'))
#print(sendCommand('um=0'))
print(getValue('um'))
print(getValue('mo'))

