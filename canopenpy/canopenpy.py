import canlib
import ni8473a
import struct
import queue
import logging
from canlib import canError
#CAN communication variable types 
TypeLength = {'integer8': (1,True,'b') , 'integer16':  (2,True,'<h') , 'integer32':  (4,True,'<l') , 
              'unsigned8' :  (1,False,'B') , 'unsigned16': (2,False,'<H') , 'unsigned32': (4,False,'<L') ,'vis string': (-1,False,'B')} 
MapOpt = {'rx':{0x1400,0x1600,0x100},'tx':{0x1800,0x1a00,0x80}} 

SdoAbortCode = { 
0x05030000:
   'Toggle bit not alternated.',
0x05040000: 
   'SDO protocol timed out.',
0x05040001: 
   'Client/server command specifier not valid or unknown.',
0x05040002: 
   'Invalid block size (block mode only).',
0x05040003: 
   'Invalid sequence number (block mode only).',
0x05040004: 
   'CRC error (block mode only)',
0x05040005: 
   'Out of memory',
0x06010000: 
   'Unsupported access to an object',
0x06010001: 
   'Attempt to read a write only object',
0x06010002: 
   'Attempt to write a read only object',
0x06020000: 
   'Object does not exist in the object dictionary',
0x06040041: 
   'Object can not be mapped to the PDO',
0x06040042: 
   'The number and length of the objects to be mapped would exceed PDO length',
0x06040043: 
   'General parameters incompatibilty reason',
0x06040047: 
   'General internal incompatibilty in the device',
0x06060000: 
   'Access failed due to an hardware error',
0x06070010: 
   'Data type does not match, length of service parameters does not match',
0x06070012: 
   'Data type does not match, length of service parameters is too high',
0x06070013: 
   'Data type does not match, length of service parameters is too low',
0x06090011: 
   'Sub-index does not exist',
0x06090030: 
   'Value range of parameters exceeded (only for write access)',
0x06090031: 
   'Value of parameters written too high',
0x06090032: 
   'Value of parameters written too low',
0x06090036: 
   'Maximum value is less then minimum value',
0x08000000: 
   'General error',
0x08000020: 
   'Data can not be transfered or stored to the application',
0x08000021: 
   'Data can not be transfered or stored to the application because of local\ncontrol',
0x08000022: 
   'Data can not be transfered or stored to the application because of the\npresent device state',
0x08000023: 
   'Object dictionary dynamic generation fails or no object dictionary is\npresent (e.g. object dictionary is generated from file and generation fails\nbecause of an file error)',
} 

 

class SimpleList:
    ''' simple list is    
    a list of objects of the form (index,object).
    where index is integer and object is an object of type canlib'''
    def __init__(self):
        self.simpleList = []

    def add(self,ch,hnd):
         for i in range(len(self.simpleList)):
            if  self.simpleList[i][0] == ch:                 
                return 
         self.simpleList.append((ch,hnd))

    def remove(self,ch):
        for i in range(len(self.simpleList)):
            if  self.simpleList[i][0] == ch:
                del self.simpleList[i] 
                break 

    def read(self):
        #for i in range(len(self.simpleList)):
            print( self.simpleList)  #[0],self.simpleList[i][0]

    def get(self,ch):
         for i in range(len(self.simpleList)):
            if  self.simpleList[i][0] == ch:                 
                return self.simpleList[i]
         return None


class Can:
    '''This  factory class  forces the creation of can objects to occur through the coommon factory'''
    class Kvaser(canlib.canlib):
        ''''''
        def __init__(self,):
            canlib.canlib.__init__(self)
            # how many channels are set
            self.channels = self.getNumberOfChannels()
            #create data structure of list of tuples 
            self.kv = [ (ch,self.getChannelData_EAN(ch)) for ch in range(self.channels)]
            # save opened channels in data structure 
            self.openedChannels = SimpleList()
            # baud rates dictionary
            self.BaudTable = {1000000:canlib.canBITRATE_1M,500000:canlib.canBITRATE_500K,
                              250000:canlib.canBITRATE_250K,125000:canlib.canBITRATE_125K,
                              100000:canlib.canBITRATE_100K}
            #current channel 
            self.currentChannel = -1

        def open(self,channel,bitrate):
                    # if channel is active open channel (kvaser)
                    try:
                        if channel in [ ch[0]  for ch in self.kv] :
                            # Don't allow sharing of this circuit between applications
                            self.ch = self.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL)#canlib.canOPEN_EXCLUSIVE)
                            print ("Using channel: %s, EAN: %s" % 
                                   (self.ch.getChannelData_Name(), self.ch.getChannelData_EAN()))

                            self.ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
                            baud = self.BaudTable[bitrate]
                            self.ch.setBusParams(baud)
                            self.ch.busOn()
                            self.openedChannels.add(channel,self.ch)
                    except canError as ce:
                        logging.error(ce)
                    except KeyError as ke:
                        logging.error(ke)


        def close(self,ch=0):
            if ch in [ ch[0]  for ch in self.kv] :
                channel = self.openedChannels.get(ch)
                channel[1].busOff()
                channel[1].close()
                self.openedChannels.remove(ch)


        #def setCurrentChannel( self,ch ):
            #'''if two or more channels had been opened then set one of those for read/write 
            #caution : this procedure is thread unsafe'''
        

        #def ping(self,ch,setCob=None,getCob=None,msg='',Tout = 0.2):
        #    '''
        #    [ch] - type integer - number of channel
        #    [setCob] - type int - communication Id (

        #    [msg] - type str - msg to send '''
        #    #chHandler1 = self.openedChannels.get(1)[1]

        #    try:
        #        if  self.openedChannels.get(ch):
        #            chHandler = self.openedChannels.get(ch)[1]
        #            chHandler.write(ch,msg)
        #            n=max(int(Tout/0.001),1)
        #            while n:
        #                id, msg, dlc, flg, time,returns = chHandler.read(timeout=Tout)

        #                if  returns == canlib.canOK and id == getCob:
        #                    return bytearray(msg)

        #                n-=1

        #    except canError as ce:
        #        logging.error(ce)
        #    else:
        #       return msg

    class NI_8473(ni8473a.canlib):
        def __init__(self,):
            ni8473a.canlib.__init__(self)
            # how many channels are set
            self.channels = self.getNumberOfChannels()
            #create data structure of list of tuples 
            self.kv = [ (ch,self.getChannelData_EAN(ch)) for ch in range(self.channels)]
            # save opened channels in data structure 
            self.openedChannels = SimpleList()
            # baud rates dictionary
            self.BaudTable = {1000000:ni8473a.NC_BAUD_1000K ,500000:ni8473a.NC_BAUD_500K,
                                250000:ni8473a.NC_BAUD_250K,125000:ni8473a.NC_BAUD_125K,
                                100000:ni8473a.NC_BAUD_100K}
            #current channel 
            self.currentChannel = -1

        def open(self,channel,bitrate):
                    # if channel is active open channel (ni)
                    try:
                        if channel in [ ch[0]  for ch in self.kv] :
                            # Don't allow sharing of this circuit between applications
                            self.ch = self.openChannel(channel)#canlib.canOPEN_EXCLUSIVE)
                            print ("Using channel: %s, EAN: %s" % 
                                   (self.ch.getChannelData_Name(), self.ch.getChannelData_EAN()))   
                            #call always before config
                            self.ch.setBaud(baud = self.BaudTable[bitrate])
                            self.ch.config()   
                            self.ch.open()
                            self.ch.action()
                            self.openedChannels.add(channel,self.ch)
                    except ni8473a.canError as ce:
                        logging.error(ce)
                    except KeyError as ke:
                        logging.error(ke)




        def close(self,ch=0):
            if ch in [ ch[0]  for ch in self.kv] :
                channel = self.openedChannels.get(ch)
                channel[1].close()
                self.openedChannels.remove(ch)


    def factory(type):
        #return eval(type + "()")
        try:
            type = type.lower()
            if type == "kvaser": return Kvaser()
            if type == "ni__8473"|\
               type == "8473"|\
               type == "ni": return NI_8473()
        except Exception as ex:
            logging.error(ex)

            assert 0, "Unknown driver name : " + type
       


#TODO : IN init procedure pass as argument string name of driver( Name of type of NI_8473 or Kvaser)
# Use factory class to choose appropriate class 
# Agregate this factory to CanOpen class
class CanOpen():
    def __init__(self,canDriverName="kvaser"):
        """"""
        self.can = Can.factory(canDriverName)



    def AnalyzeSdoAbort( self, errcode): 
        try:
            return SdoAbortCode[ errcode ] ;
        except:
            return 'Unknow SDO abort code'
    

    def pingCanMessage(self,canid,msg):
        try:
            self.can.ch.write(canid,msg)
            wait  = int(self.timeout/0.001)
            while True :
                 id.value, msgList[:dlc.value], dlc.value, flag.value, time.value
            retval = self.h.read(self.timeout)
            
            return retval  
                  
        except (self.can.canError) as ex:
           # print ( ex )
           raise ex

    def read_can_frame(self):
        """
        Low-level function: Read a CAN frame .
        """ 
        if self.can != None:       
            try:   
                can_frame = self.can.ch.read()
            except:raise Exception("CAN frame read error")
            return can_frame
        else:
            raise Exception("CAN frame read error: can not connected")
            
    def setNodeId(self,nodeId):
            self.nodeId = nodeId

    def getNodeId(self):
        return self.nodeId

    def parse_can_frame(self, can_frame):
        """
        Low level function: Parse a given CAN frame into CANopen frame
        """
        canopen_frame = CANopenFrame()        
        if libcanopen.canopen_frame_parse(byref(canopen_frame), byref(can_frame)) == 0:
            return canopen_frame
        else:
            raise Exception("CANopen Frame parse error")
                        


   
    #---------------------------------------------------------------------------
    # SDO related functions
    #

    #
    # EXPEDIATED
    #

    def SDOUploadExp(self, node, index, subindex):
        """
            Expediated SDO upload
        """
        msg =  (64).to_bytes(1,'little')+(index).to_bytes(2,'little')+(subindex).to_bytes(5,'little')         
        self.can.write(node,msg)




    def getSdo( self, ch,NodeId , Index , SubIndex , TypeIn , Timeout = 1 , AbortMsg = None , decode = True ): 
        '''Initiate SDO Upload protocol
        Client request (8 bytes):
        0: 7-5 bits - ccs=2 - initiate upload request(client command specifier)
           4-0 bit - not used ,always 0
        1-3: m- multiplexor.It represents the index/sub-index of the data to be transfer by the SDO
        4-7: data'''
        # function [Value,AbortFlag,CobId,Data] = GetSdo( h , NodeId , Index , SubIndex , Type , Timeout )
        # Purpose: Get SDO 
        #
        # Arguments: 
        # 
        # NodeId: Node ID
        # Index: Object index
        # SubIndex: Object sub index 
        # Type: Received data type, may be:		
        #                          'integer8'
        #                          'integer16'
        #                          'integer32'
        #                          'unsigned8'
        #                          'unsigned16'
        #                          'unsigned32'
        #                          'vis string'
        # Timeout: timeout [sec]
        # AbortMsg: Set to string if a faiure should abort with this string displayed
        #
        # Returns: 
        # Value: Array with received data, or abort code
        # AbortFlag: if 1 then abort code recieved, normaly 0
        # CobId: Received additional communication objects identifiers
        # Data : Received additional data

        #NodeId = self.GetNodeId(h , NodeId) 
        #ch = self.ComPars.handles[h]['ChannelNum']
        Type = TypeIn.lower()
        assert Type in TypeLength.keys() ,'SDO desired for ilegal type, found['+repr(Type)+'] , permitted: ' + repr(TypeLength.keys()) 
        msg =  (64).to_bytes(1,'little')+(Index).to_bytes(2,'little')+(SubIndex).to_bytes(5,'little') # SDO upload init 
        #self.ComPars.handles[h]['CAN_InPool'].clean('cobId',[ NodeId + 0x600 ,  NodeId + 0x580]) # Clear any old junk refering that COB ID 
        msgRet = self.ping( ch , NodeId + 0x600 ,  NodeId + 0x580 ,msg , Tout = Timeout) 
        if msgRet[0] & 0x80 : 
            AbortCode =  struct.unpack_from('L',msgRet,4)[0]  # Return error code + abort 
            assert not( type(AbortMsg) is str), AbortMsg+ ': GetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) 
            return AbortCode,1 # Return error code + abort 
        if (((msgRet[0] & 0xe0 ) >> 5 ) != 2) or ( msgRet[1:4] != msg[1:4] ) : #Bad CCS, multiplexor does not fit 
            logging.error ('Bad response to SDO upload init') 
        if msgRet[0] & 2 : #expedited upload 
            n = 4 - (( msgRet[0] >> 2 ) & 3 ) if ( msgRet[0] & 2 ) else 4 #get number of expedited bytes
            assert ( n >= TypeLength[Type][0] ) ,'No enough bytes in the return message for the desired data type' 
            if Type == 'vis string' :
                return msgRet[4:4+n].decode('ascii') ,0 
            return  struct.unpack_from(TypeLength[Type][2],msgRet,4)[0],0 #Return result, no abort 
        #Segmented
        buf =  (0).to_bytes(8,'little') # Stam 
        msg =  (0x60).to_bytes(8,'little')
        nDelivery = struct.unpack_from('L',msgRet,4)[0] if ( msgRet[0] & 1 ) else -1
        while True:
            msgRet = self.ping( ch , NodeId + 0x600 ,  NodeId + 0x580 ,msg , Tout = Timeout ) 
            msg = (msg[0] ^ 0x10).to_bytes(1,'little') + msg[1:]
            if msgRet[0] & 0x80 : 
                AbortCode =  struct.unpack_from('L',msgRet,4)[0] # Return error code + abort 
                assert not ( type(AbortMsg) is str), AbortMsg+ ': GetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) 
                return AbortCode,1 # Return error code + abort 
            assert (msgRet[0] & 0xe0 ) == 0 , 'Bad response to SDO upload init' # scs error 
            n = 7 - (( msgRet[0] >> 1 ) & 7 )
            buf = buf + msgRet[1:n+1]
            if ( len( buf ) >= nDelivery + 8 ) or msgRet[0] & 1 : # Complete or already message length exceeded
                break

        nDelivery = len(buf)-8 if nDelivery < 0 else nDelivery
        assert nDelivery ==  len(buf)-8 and nDelivery >= TypeLength[Type][0],'Length of SDO upload not as expected'
        if Type == 'vis string' and decode:
            return buf[8:].decode('ascii') ,0 
        else:
            return buf[8:] ,0 
        return  struct.unpack_from(TypeLength[Type][2],buf,8)[0],0 #Return result, no abort 



    
    def setSdo( self ,ch, NodeId , Index , SubIndex  , data , Type , Timeout = 1 , AbortMsg = None ): 
       
        Type = Type.lower()
        assert Type in TypeLength.keys() ,'SDO desired for ilegal type, found['+repr(Type)+'] , prmitted: ' + repr(TypeLength.keys()) 
        if Type == 'vis string': 
            assert type(data) is str ,'Required visible string for non string data'
            msg =  ((1<<5)+1).to_bytes(1,'little')+(Index).to_bytes(2,'little')+(SubIndex).to_bytes(1,'little')+(len(data)).to_bytes(4,'little') # SDO dnload init 
            #print('SetSDO msg:' + str(msg))
        else:
            msg =  ((1<<5)+((4-TypeLength[Type][0])<<2)+(1<<1)+1).to_bytes(1,'little')+(Index).to_bytes(2,'little')+(SubIndex).to_bytes(1,'little')+data.to_bytes(4,'little') # SDO dnload init 
       
        msgRet = self.ping( ch , NodeId + 0x600 ,  NodeId + 0x580 ,msg , Tout = Timeout) 
        #print('SetSDO msgRet:' + str(msgRet))
        if msgRet[0] & 0x80 :   
            AbortCode =  struct.unpack_from('L',msgRet,4)[0]  # Return error code + abort 
            assert not (type(AbortMsg) is str), AbortMsg+ ': SetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) 
            return AbortCode,1 # Return error code + abort 
        if (((msgRet[0] & 0xe0 ) >> 5 ) != 3) or ( msgRet[1:4] != msg[1:4] ) : #Bad CCS, multiplexor does not fit 
            error ('Bad response to SDO download init') 
        #Segmented
        t = 1 ; 
        while len(data) :
            t = 1-t 
            if len(data) > 7 : 
                nNext = 7 
                Complete = 0 
                meser = data[:7]
                data = data[7:]
            else: 
                nNext = len(data)  
                meser  = data + chr(0) * (7-nNext) 
                Complete = 1 
                data = [] 

            msg =  ((t<<4)+((7-nNext)<<1)+Complete).to_bytes(1,'little')+ meser.encode('ascii')
            msgRet = self.ping( ch , NodeId + 0x600 ,  NodeId + 0x580 ,msg , Tout = Timeout ) 
            if msgRet[0] & 0x80 : 
                AbortCode =  struct.unpack_from('L',msgRet,4)[0]  # Return error code + abort 
                assert not ( type(AbortMsg) is str), AbortMsg+ ': SetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) 
                return AbortCode,1 # Return error code + abort 

        return 0 


    

    def SetPdoMapping( self ,h, NodeId , PdoNum , FlagRxTxIn , TransType , IndexArr , SubIndexArr , LenArr , PdoCobId =None ):
# function SetPdoMapping( h , NodeId , PdoNum , FlagRxTx , TransType , IndexArr , SubIndexArr , LenArr )
#
# Purpose: Map the specified PDO 
#
# Arguments: 
# h: Handle to opened communication port 
# NodeId: Node ID
# PdoNum: Number of PDO [1,4]
# FlagRxTx: If PDO Rx then 'Rx', if PDO Tx then 'Tx' 
# TransType: Transmission type. May be in the range  [0...255]
# IndexArr: Array of indices of objects to be mapped
# SubIndexArr: Array of sub-indices of objects to be mapped
# LenArr: Array of lengths of objects to be mapped [bites]
# PdoCobId: Not obligatory, if exists, set PDO cob-id parameter
        FlagRxTx = FlagRxTxIn.tolower()
        assert FlagRxTx in FlagRxTx.keys() ,'Ilegal Tx Rx type : found ['+repr(FlagRxTxIn) +']' 
        assert PdoNum in range(4) ,'Ilegal PdoNum'
        pdoPar = MapOpt[FlagRxTx][0]
        pdoMap = MapOpt[FlagRxTx][1]
        cobId = PdoNum*256 + MapOpt[FlagRxTx][2]
#For changing the PDO mapping the previous PDO must be deleted, the sub-index 0 must be set to 0. 	
        self.SetSdo( h , NodeId , pdoMap, 0 , 0 , 'unsigned8' , AbortMsg = 'Cannot delete previous mapping') ;

        if PdoCobId != None : 
            Value,AbortFlag= self.GetSdo( h , NodeId , pdoPar, 1 , 'unsigned32' ) ;
            if AbortFlag: 
                error( 'Cannot program PDO parameters' )
                pdoCobId = PdoCobId | (3<<30) # No RTR allowed
                self.SetSdo( h , NodeId , pdoPar , 1 , pdoCobId , 'unsigned32' ,'Cannot set transmission type') 

# Send SDO download to set transmission type.
# Transmission type resides at the sub-index 2h of the PDO Communication Parameter record.				
        self.SetSdo( h , NodeId , pdoPar , 2 , TransType , 'unsigned8' ,'Cannot set transmission type') ;

# Mapping loop for all PDO objects to be mapped
        for subIndex in range(len(IndexArr)):
        # The sub-indices from 1 to n contain the information about the mapped objects.
        # Every entry  describes the PDO by its index, sub-index and length
        # according to the Fig.66 CiA DS301 : 
        # 16 most significant bits is object index
        # 8 next bits is sub-index
        # 8 least significant bits is length of object	
            data = IndexArr(subIndex)*65536 + SubIndexArr(subIndex)*256 + LenArr(subIndex) ;
            AbortFlag = self.SetSdo( h , NodeId , pdoMap , subIndex , data , 'unsigned32' ) ;
            if AbortFlag:
                err = self.AnalyzeSdoAbort( AbortFlag ) ;
                error( 'Cannot set mapping: '+err) 

# Send SDO download to set number of entries of the PDO mapped objects 
# Subindex 0 is number of mapped objects in PDO
# For changing the PDO mapping the previous PDO must be deleted, the sub-index 0 must be set to 0. 	
        AbortFlag = self.SetSdo( h , NodeId , pdoMap, 0 , length(IndexArr) , 'unsigned8' ) 
        if AbortFlag:
            err = self.AnalyzeSdoAbort( AbortFlag ) ;
            error( 'Cannot delete previous mapping: {0}'+err) 


        AbortFlag = self.GetSdo( h , NodeId , pdoMap, 0 , 'unsigned8' ) 
        if AbortFlag:
            err = self.AnalyzeSdoAbort( AbortFlag ) ;
            error('Cannot delete previous mapping: '+err ) ;

#Get a recorder vector 
 #h: Communication handle 
 #NodeId: Node Id to bring the data from 
 #BitNumber: The index of the recorded value 
 #unsign: 1 if numbers are to be brought unsigned  
        
    def GetBH( self, h , NodeId = None , BitNumber = 0 , unsign = 0  ) :
# function Arr = GetBH( h , NodeId , BitNumber , usign ) 

        Value,AbortFlag = self.GetSdo( h , NodeId , 8240 , BitNumber , 'vis string' , 3 , decode = False); # 8240 = 0x2030
        
        Value0 = struct.unpack_from('<B',Value)[0] 
        recorderTsMultiplier = Value0 & 0xf 
        dataLength = struct.unpack_from('<H',Value,1)[0] ;
        Arr = [0] * dataLength 
        factor = struct.unpack_from('f',Value,3)[0]  
        outType = (Value0 ,0x30) >> 4  ; #48 = 0x30
        dataType = (Value0 &0xc0) >> 6 ; # 192 = 0xc0
        dataTypeLen = [2,4,8]   

        assert dataType in [0,1,2],'Unknown data type for recorder'
        assert len(Value) == 7 + dataLength * dataTypeLen[dataType] ,'Recorder data stream had incorrect length'
        if ( dataType == 0 ) and (not unsign):
# short signed 
            return [struct.unpack_from('<h',Value,7+i*2)[0] for i in range(dataLength) ]
        elif ( dataType == 0 ) and  unsign:
# short usigned 
            return [struct.unpack_from('<H',Value,7+i*2)[0] for i in range(dataLength) ]
        elif ( dataType == 1 ) and  (not unsign) and (outType != 3) :
# long signed 
            return [struct.unpack_from('<l',Value,7+i*4)[0] for i in range(dataLength) ]
        elif ( dataType == 1 ) and unsign and (outType != 3) :
# long usigned 
            return [struct.unpack_from('<L',Value,7+i*4)[0] for i in range(dataLength) ]
        elif ( dataType == 1 ) : 
# float 
            return [struct.unpack_from('<f',Value,7+i*4)[0] for i in range(dataLength) ]
        else:
# double 
            return [struct.unpack_from('<d',Value,7+i*8)[0] for i in range(dataLength) ]

    def GetRU( self, h , NodeId = None , BitNumber = 0 , unsign = 0 , bDmdRec = 0 ) :
# function Arr = GetBH( h , NodeId , BitNumber , usign ) 

        Value,AbortFlag = self.GetSdo( h , NodeId , 8277 if bDmdRec else 8240 , BitNumber , 'vis string' , 3 , decode = False); # 8240 = 0x2030
        
        dataType = struct.unpack_from('<B',Value)[0] # 0 = short , 1 = long , 2 = float , 3 = double , 4 = __int64
        dataLength = struct.unpack_from('<H',Value,1)[0]
        Arr = [0] * dataLength 
        fac = struct.unpack_from('f',Value,3)[0]
        dataTypeLen = [2,4,4,8,8]   

        assert dataType in [0,1,2,3,4],'Unknown data type for recorder'
        assert len(Value) == 7 + dataLength * dataTypeLen[dataType] ,'Recorder data stream had incorrect length'
        if ( dataType == 0 ) and (not unsign):
# short signed 
            return [struct.unpack_from('<h',Value,7+i*2)[0] for i in range(dataLength) ]
        elif ( dataType == 0 ) and  unsign:
# short usigned 
            return [struct.unpack_from('<H',Value,7+i*2)[0] for i in range(dataLength) ]
        elif ( dataType == 1 ) and  (not unsign) :
# long signed 
            return [struct.unpack_from('<l',Value,7+i*4)[0] for i in range(dataLength) ]
        elif ( dataType == 1 ) and unsign :
# long usigned 
            return [struct.unpack_from('<L',Value,7+i*4)[0] for i in range(dataLength) ]
        elif ( dataType == 2 ) : 
# float 
            return [struct.unpack_from('<f',Value,7+i*4)[0] * fac  for i in range(dataLength) ]
        elif ( dataType == 3 )  and  unsign:
            return [struct.unpack_from('<Q',Value,7+i*8)[0]   for i in range(dataLength) ]
        elif ( dataType == 3 )  :
            return [struct.unpack_from('<q',Value,7+i*8)[0]   for i in range(dataLength) ]
        elif ( dataType == 4 ) : 
            return [struct.unpack_from('<d',Value,7+i*8)[0] for i in range(dataLength) ]
        else:
            error ('Bad data type in RU message') 


    def SetOsIntCmd( self, h  , str , NodeId = None , Timeout = 0.1 ): 
    #function str = SetOsIntCmd( h , NodeId , str , Timeout )
    # Purpose: Send string to OS interpreter 
    #
    # Arguments: 
    # h: Handle to opened communication port 
    # NodeId: Node ID
    # str: String to transmit
    # timeout: Timeout [sec]
    #
    # Returns: 
    # str: Received string
    # Set object 0x1024 (OS mode) to execute immediate      
        self.SetSdo( h , NodeId , 4131 , 1 , str , 'vis string' , Timeout , 'OS interpreter send cmd'); # 4131 = 0x1023

    #Wait till target is ready 
    #Result = 0 for completed, no reply 
    #1 no errors, reply 
    #2 error , no reply 
    #3 error , reply there 
        Value = 255 ;
        while Value == 255 : 
           Value,AbortFlag = self.GetSdo( h , NodeId , 4131 , 2 , 'unsigned8' , Timeout ,'OS interpreter wait ready ');# 4131 = 0x1023

        assert Value & 1 , 'Os interpreter failed' 

        Value,ErrCode = self.GetSdo( h , NodeId , 4131 , 3 , 'vis string' , Timeout ,'OS interpreter get result ');# 4131 = 0x1023
        return Value.replace(chr(0),'') 
        #return ''.join(([chr(i) for i in Value if i]))



#s = SimpleList()
#s.add(0,'a')
#s.add(1,'b')
#s.add(2,'b')
#s.add(3,'b')
#s.remove(0)
#s.read()

#c= kvaser()
#print(c.channels)
#print( c.kv)
#print ( c.openedChannels)
#c.openkvaser(0,1000000)
#c.openkvaser(1,1000000)

#print(c.ping(0,(45,57,58,66,78,45,78,85)))
#c.closekvaser(0)
