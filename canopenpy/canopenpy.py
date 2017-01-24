'''
Abbreviations
--------------
CAN:
Controller Area Network is an internally standardized serial bus system..
COB:
Communication Object. A unit of transportation in a CAN network. Data must be sent across a CAN
Network inside a COB. There are 2048 different COB's in a CAN network. A COB can contain at most
8 bytes of data.
COB-ID:
Each COB is uniquely identified in a CAN network by a number called the COB Identifier (COB-ID).
The COB-ID determines the priority of that COB for the MAC sub-layer.
Remote COB:
A COB whose transmission can be requested by another device.
NMT:
Network Management. One of the service elements of the application layer in the CAN Reference
Model. The NMT serves to configure, initialise, and handle errors in a CAN network.
Node-ID:
The Node-ID of the NMT Slave has to be assigned uniquely, or 0. If 0, the protocol addresses all NMT
Slaves.
PDO:
Process Data Object.
SDO:
Service Data Object.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
service objects
---------------
The functionality the application layer offers to
an application is logically divided over different service objects in the application layer.
Applications interact by invoking services of a service object in the application layer.

..this object exchanges data via the CAN Network with (a) peer service object(s) via a
protocol.This protocol is described in the Protocol Specification of that service object.
There are four different service primitives:
1) request
2) indication
3) response
4) confirmation

Application Layer Service Types
-------------------------------
� A local service involves only the local service object. The application issues a request to its local
service object that executes the requested service without communicating with (a) peer service
object(s).
� An unconfirmed service involves one or more peer service objects. The application issues a
request to its local service object. This request is transferred to the peer service object(s) that
each pass it to their application as an indication. The result is not confirmed back.
� A confirmed service can involve only one peer service object. The application issues a request to
its local service object. This request is transferred to the peer service object that passes it to the
other application as an indication. The other application issues a response that is transferred to
the originating service object that passes it as a confirmation to the requesting application.
� A provider initiated service involves only the local service object. The service object (being the
service provider) detects an event not solicited by a requested service. This event is then
indicated to the application.
Unconfirmed and confirmed services are collectively called remote services.

 General
 -------
Object Dictionary serves as an interface between the communication and the application.
The complete description of a device�s application with respect to the data items in the Object
Dictionary is named device profile.
Each object within the dictionary is addressed using a 16-bit index.
__________________
Index (hex) Object
__________________
0000 not used
0001-001F Static Data Types
0020-003F Complex Data Types
0040-005F Manufacturer Specific Complex Data Types
0060-007F Device Profile Specific Static Data Types
0080-009F Device Profile Specific Complex Data Types
00A0-0FFF Reserved for further use
1000-1FFF Communication Profile Area
2000-5FFF Manufacturer Specific Profile Area
6000-9FFF Standardised Device Profile Area
A000-BFFF Standardised Interface Profile Area
C000-FFFF Reserved for further use

Communication Model
-------------------
� Master/Slave relationship  
Unconfirmed Master Slave Communication:
    master request --> data  --> slave indication
Confirmed Master Slave Communication:
    master request   --> slave indication 
    confirmation <--data <-- responce
� Client/Server relationship 
    client request  --> data -->server indication 
    confirmation <--data <-- server responce
� Producer/Consumer relationship 
Push model :
    producer request -->data-->consumers indication
Pull model :
    producer <-- consumers request
    producer responce --> data --> consumers confirmation / indication

Communication Objects
=====================
Process Data Object (PDO)
--------------------------
Provide interface to the application objects and correspond to entries in device Object Dictionary.
PDOs are described by the PDO communication parameter (20h) and the PDO mapping parameter (21h).
The PDO communication parameter describes the communication capabilities of the PDO.
The PDO mapping parameter contains information about the contents of the PDOs (device variables). 
The indices of the corresponding Object Dictionary entries
are computed by the following formulas:
� RPDO communication parameter index = 1400h + RPDO-number -1
� TPDO communication parameter index = 1800h + TPDO-number -1
� RPDO mapping parameter index = 1600h + RPDO-number -1
� TPDO mapping parameter index = 1A00h + TPDO-number -1
PDO Services
-----------
PDO transmission follows the producer/consumer relationship.
Write PDO - push model is valid
Read PDO - the pull model is valid

Service Data Object (SDO)
-------------------------
The client can control via a multiplexor (index and sub-index of the Object Dictionary) which data set is
to be transferred. The contents of the data set are defined within the Object Dictionary.
transfer type
-------------
For SDOs, it is also possible to transfer a data set of up to four bytes during the initialisation phase. This
mechanism is called an expedited transfer.
segmented - 
block -
After block download the server indicates the client the last successfully received segment of this
block transfer by acknowledging this segment sequence number.
After block upload the client indicates the server the last successfully received segment of this block
transfer by acknowledging this segment sequence number.
For all transfer types it is the client that takes the initiative for a transfer. The owner of the accessed
Object Dictionary is the server of the SDO. Both the client or the server can take the initiative to abort
the transfer of a SDO.
SDOs are described by the SDO communication parameter record (22h).The structure of this data
type is explained in 9.5.4. The SDO communication parameter describes the communication
capabilities of the Server-SDOs and Client-SDOs (CSDO). The indices of the corresponding Object
Dictionary entries are computed by the following formulas:
� SSDO communication parameter index = 1200h + SSDO-number -1
� CSDO communication parameter index = 1280h + CSDO-number -1

SDO Services
------------
The model for the SDO communication is the Client/Server model.

SDO Download, which can be split up into
- Initiate SDO Download
- Download SDO Segment

SDO Upload, which can be split up into
- Initiate SDO Upload
- Upload SDO Segment

Abort SDO Transfer

'''


#import canlib
#import ni8473a
import struct
import queue
import logging
import time
#from canlib import canError
#CAN communication variable types 
TypeLength = {'integer8': (1,True,'b') , 'integer16':  (2,True,'<h') , 'integer32':  (4,True,'<l') , 
              'unsigned8' :  (1,False,'B') , 'unsigned16': (2,False,'<H') , 'unsigned32': (4,False,'<L') ,'vis string': (-1,False,'B')} 
MapOpt = {'rx':{0x1400,0x1600,0x100},'tx':{0x1800,0x1a00,0x80}} 



#CAN ID - message identifier
#From  TO  Communication Objects   Comment
canId={'NMT Service':(0x0,'From NMT Master'),
       'SYNC Message':(0x80,'From SYNC Producer'),
       'Emergency Message':(0x81,0xFF,'From nodes 1 to 127'),
       'Time Stamp Message':(0x100,'From timestamp producer'),
       '1st Transmit PDO':(0x181,0x1FF,'From nodes 1 to 127'),
       '1st Receive PDO':(0x201,0x27F,'For nodes 1 to 127'),
       '2nd Transmit PDO':(0x281,0x2FF,'From nodes 1 to 127'),
       '2nd Receive PDO':(0x301,0x37F,'For nodes 1 to 127'),
       '3rd Transmit PDO':(0x381,0x3FF,'From nodes 1 to 127'),
       '3rd Receive PDO':(0x401,0x47F,'For nodes 1 to 127'),
       '4th Transmit PDO':(0x481,0x4FF,'From nodes 1 to 127'),
       '4th Receive PDO':(0x501,0x57F,'For nodes 1 to 127'),
       'Transmit SDO':(0x581,0x5FF,'From nodes 1 to 127'),
       'Receive SDO':(0x601,0x67F,'For nodes 1 to 127'),
       'NMT Error Control':(0x701,0x77F,'From nodes 1 to 127')}



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
#
# This struct describes and SDO object (8-byte payload data in an CANopen frame)
# command specifier

CANOPEN_SDO_CS_MASK    = 0xE0
CANOPEN_SDO_CS_RX_IDD   =0x20
CANOPEN_SDO_CS_TX_IDD   =0x60
CANOPEN_SDO_CS_IDD_STR = "Initiate Domain Download"
CANOPEN_SDO_CS_RX_DDS  = 0x00
CANOPEN_SDO_CS_TX_DDS  = 0x20
CANOPEN_SDO_CS_DDS_STR = "Download Domain Segment"
CANOPEN_SDO_CS_RX_IDU  = 0x40
CANOPEN_SDO_CS_TX_IDU  = 0x40
CANOPEN_SDO_CS_IDU_STR = "Initiate Domain Upload"
CANOPEN_SDO_CS_RX_UDS  = 0x60
CANOPEN_SDO_CS_TX_UDS  = 0x00
CANOPEN_SDO_CS_UDS_STR = "Upload Domain Segment"
CANOPEN_SDO_CS_RX_ADT  = 0x80
CANOPEN_SDO_CS_TX_ADT  = 0x80
CANOPEN_SDO_CS_ADT_STR = "Abort Domain Transfer"
CANOPEN_SDO_CS_RX_BD   = 0xC0
CANOPEN_SDO_CS_TX_BD  =  0xA0
CANOPEN_SDO_CS_BD_STR = "Block Download"




# initiate download flags
CANOPEN_SDO_CS_ID_N_MASK  =  0x0C    
CANOPEN_SDO_CS_ID_N_SHIFT =  0x02
CANOPEN_SDO_CS_ID_E_FLAG  =  0x02
CANOPEN_SDO_CS_ID_S_FLAG  =  0x01

# domain segment flags
CANOPEN_SDO_CS_DS_N_MASK   = 0x0E
CANOPEN_SDO_CS_DS_N_SHIFT  = 0x01
CANOPEN_SDO_CS_DS_C_FLAG   = 0x01
CANOPEN_SDO_CS_DS_T_FLAG   = 0x10

# block download flags
CANOPEN_SDO_CS_BD_S_FLAG  = 0x02
CANOPEN_SDO_CS_BD_CRC_FLAG =0x04
CANOPEN_SDO_CS_BD_C_FLAG  = 0x80

CANOPEN_SDO_CS_DB_CS_IBD  = 0x00
CANOPEN_SDO_CS_DB_CS_EBD  = 0x01

CANOPEN_SDO_CS_DB_N_MASK  =  0x07
CANOPEN_SDO_CS_DB_N_SHIFT =  0x02

CANOPEN_SDO_CS_DB_SS_IBD_ACK =0x00
CANOPEN_SDO_CS_DB_SS_BD_ACK  =0x02
CANOPEN_SDO_CS_DB_SS_BD_END  =0x01
CANOPEN_SDO_CS_DB_SS_MASK    =0x03


#class SimpleList:
#    ''' simple list is    
#    a list of objects of the form (index,object).
#    where index is integer and object is an object of type canlib'''
#    def __init__(self):
#        self.simpleList = []

#    def add(self,ch,hnd):
#         for i in range(len(self.simpleList)):
#            if  self.simpleList[i][0] == ch:                 
#                return 
#         self.simpleList.append((ch,hnd))

#    def remove(self,ch):
#        for i in range(len(self.simpleList)):
#            if  self.simpleList[i][0] == ch:
#                del self.simpleList[i] 
#                break 

#    def read(self):
#        #for i in range(len(self.simpleList)):
#            print( self.simpleList)  #[0],self.simpleList[i][0]

#    def get(self,ch):
#         for i in range(len(self.simpleList)):
#            if  self.simpleList[i][0] == ch:                 
#                return self.simpleList[i]
#         return None


#class Can:
#    '''This  factory class  forces the creation of can objects to occur through the coommon factory'''
#    class Kvaser(canlib.canlib):
#        ''''''
#        def __init__(self):
#            canlib.canlib.__init__(self)
#            # how many channels are set
#            #self.channels = self.getNumberOfChannels()
#            #create data structure of list of tuples 
#            #self.channels = [ (ch,self.getChannelData_EAN(ch)) for ch in range(self.channels)]
#            # save opened channels in data structure 
#            self.openedChannels = SimpleList()
#            # baud rates dictionary
#            self.BaudTable = {1000000:canlib.canBITRATE_1M,500000:canlib.canBITRATE_500K,
#                              250000:canlib.canBITRATE_250K,125000:canlib.canBITRATE_125K,
#                              100000:canlib.canBITRATE_100K}
#            #current channel 
#            self.currentChannel = -1

#        def open(self,channel,bitrate):
#                    # if channel is active open channel (kvaser)
#                    try:
#                        if channel in [ ch[0]  for ch in self.channels] :
#                            # Don't allow sharing of this circuit between applications
#                            self.ch = self.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL)#canlib.canOPEN_EXCLUSIVE)
#                            print ("Using channel: %s, EAN: %s" % 
#                                   (self.ch.getChannelData_Name(), self.ch.getChannelData_EAN()))

#                            self.ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
#                            baud = self.BaudTable[bitrate]
#                            self.ch.setBusParams(baud)
#                            self.ch.busOn()
#                            self.openedChannels.add(channel,self.ch)
#                            self.setCurrentChannel(channel)
#                    except canError as ce:
#                        logging.error(ce)
#                    except KeyError as ke:
#                        logging.error(ke)


#        def close(self,ch=0):
#            if ch in [ ch[0]  for ch in self.channels] :
#                channel = self.openedChannels.get(ch)
#                channel[1].busOff()
#                channel[1].close()
#                self.openedChannels.remove(ch)

        
#        def setCurrentChannel( self,ch ):
#            '''if two or more channels had been opened then set one of those for read/write 
#            caution : this procedure is thread unsafe'''
#            self.currentChannel=ch


#    class NI_8473(ni8473a.canlib):
#        def __init__(self):
#            ni8473a.canlib.__init__(self)
#            # how many channels are set
#            #self.channels = self.getNumberOfChannels()
#            #create data structure of list of tuples 
#            #self.channels = [ (ch,self.getChannelData_EAN(ch)) for ch in range(self.channels)]
#            # save opened channels in data structure 
#            self.openedChannels = SimpleList()
#            # baud rates dictionary
#            self.BaudTable = {1000000:ni8473a.NC_BAUD_1000K ,500000:ni8473a.NC_BAUD_500K,
#                                250000:ni8473a.NC_BAUD_250K,125000:ni8473a.NC_BAUD_125K,
#                                100000:ni8473a.NC_BAUD_100K}
#            #current channel 
#            self.currentChannel = -1

#        def open(self,channel,bitrate):
#                    # if channel is active open channel (ni)
#                    try:
#                        if channel in [ ch[0]  for ch in self.channels] :
#                            # Don't allow sharing of this circuit between applications
#                            self.ch = self.openChannel(channel)#canlib.canOPEN_EXCLUSIVE)
#                            print ("Using channel: %s, EAN: %s" % 
#                                   (self.ch.getChannelData_Name(), self.ch.getChannelData_EAN()))   
#                            #call always before config
#                            self.ch.setBaud(baud = self.BaudTable[bitrate])
#                            self.ch.config()   
#                            self.ch.open()
#                            self.ch.action()
#                            self.openedChannels.add(channel,self.ch)
#                            self.setCurrentChannel(channel)
#                    except ni8473a.canError as ce:
#                        logging.error(ce)
#                        raise Exception(ce)
#                    except :
#                        logging.error('Unknown error')
#                        raise Exception('Unknown error')



#        def close(self,ch=0):
#            if ch in [ ch[0]  for ch in self.channels] :
#                channel = self.openedChannels.get(ch)
#                channel[1].close()
#                self.openedChannels.remove(ch)

#        def setCurrentChannel( self,ch ):
#            '''if two or more channels had been opened then set one of those for read/write 
#            caution : this procedure is thread unsafe'''
#            self.currentChannel=ch

#    def factory(self,type):
#        #return eval(type + "()")
#        try:
#            type = type.lower()
#            if type == "kvaser": return self.Kvaser()
#            if type == "ni__8473" or\
#               type == "8473"or\
#               type == "ni": return self.NI_8473()
#        except Exception as ex:
#            logging.error(ex)

#           # assert 0, "Unknown driver name : " + type
       


#TODO : IN init procedure pass as argument string name of driver( Name of type of NI_8473 or Kvaser)
# Use factory class to choose appropriate class 
# Agregate this factory to CanOpen class
class CanOpen():
    def __init__(self,canlib):
        """"""
        self.can = canlib
        self.timeout = 0.002

    def AnalyzeSdoAbort( self, errcode): 
        try:
            return SdoAbortCode[ errcode ] ;
        except:
            return 'Unknow SDO abort code'
    

    def open(self,ch=0,baud=1000000):
        self.can.open(ch,baud)

    def close(self,ch=0):
        self.can.close(ch)

    def pingCanMessage(self,nodeIdSend,nodeIdReply,msg):
        '''
        :param nodeIdSend : Communication object ID for request
        :param nodeIdReply: Communication object Id for responce
        :param msg        : message to be sent 
        :returns          : responce message
        '''
        try:
            self.can.ch.write(nodeIdSend,msg)
            wait  = int(self.timeout/0.001)          
            while   wait:              
                ret = self.can.ch.read(self.timeout)
                if ret[0] == nodeIdReply: 
                    break
                time.sleep(0.001)
                wait-=1                        
            return bytearray(ret[1])
                  
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

  
   
    #---------------------------------------------------------------------------
    # SDO related functions
    #

    #
    # 
    #---------------------------------------------------------------------------

    def SDOUpload(self, index, subindex,TypeIn,AbortMsg = None):
        """
            The Initiate SDO Upload - Request
            =================================
            bit 7..5 - ccs: Client Command Specifier = 2 ( bin(64)='0b1000000' )
            bit 4..0 - x: reserved

            The Multiplexor contains the Index and Subindex of the OD entry that the
            client wants to read  


            The Initiate SDO Upload - Response
            ==================================
            This is the response sent back from the SDO server to the client 
            indicating that the previously received upload (read) request can be processed.
            If expedited transfer is used, the data read from the Object Dictionary 
            is part of the response, otherwise additional segmented transfers are used. 
            The default CAN identifier used for this message is 580h plus 
            the Node ID of the node implementing the SDO server
            
            bit 7..5 - scs: Server Command Specifier = 2
            bit 4    - x: reserved
            bit 3..2 - n: if e=s=1, number of data bytes in Byte 4..7 that do not contain data
            bit 1    - e: set to 1 for expedited transfer (data is in bytes 4-7)
            bit 0    - s: set to 1 if data size is indicated
        """
        Type = TypeIn.lower()
        if  Type not in TypeLength.keys():
            logging.error('SDO desired for ilegal type, found['+repr(Type)+'] , permitted: ' + repr(TypeLength.keys()) )
            raise Exception('SDO desired for ilegal type, found['+repr(Type)+'] , permitted: ' + repr(TypeLength.keys()))
      
        #SDO request message
        msg =  (64).to_bytes(1,'little')+(index).to_bytes(2,'little')+(subindex).to_bytes(5,'little') 
        #Sends SDO requests to each node by using message ID:600h + Node ID  
        #Expects reply in message ID: 580h + Node ID      
        msgRet = self.pingCanMessage( nodeId + 0x600 ,  nodeId + 0x580 ,msg , tout = 0.02) 

        # verify returned message~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Test abort message
        if msgRet[0] & CANOPEN_SDO_CS_RX_ADT : 
            AbortCode =  struct.unpack_from('L',msgRet,4)[0]  # Return error code + abort 
            logging.error ( 'Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] \
            for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) )
            raise Exception(  'Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] \
            for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) )

        #Test command specifier and multiplexor
        if (((msgRet[0] & CANOPEN_SDO_CS_MASK ) >> 5 ) != 2) or ( msgRet[1:4] != msg[1:4] ) : 
            logging.error ('Bad response to SDO upload init') 
            raise Exception('Bad response to SDO upload init')


        #Test  expedited upload
        if msgRet[0] & 2 : 
            # calculate number of data bytes
            n = 4 - (( msgRet[0] >> 2 ) & 3 ) if ( msgRet[0] & 2 ) else 4 #get number of expedited bytes
            if  n <= TypeLength[Type][0]:
                logging.error('No enough bytes in the return message for the desired data type' )
                raise Exception('No enough bytes in the return message for the desired data type')
           

            if Type == 'vis string' :
                return msgRet[4:4+n].decode('ascii')  
            return  struct.unpack_from(TypeLength[Type][2],msgRet,4)[0] #Return result, no abort 


        #Segmented~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        '''If in the initiation sequence a segmented transfer was negotiated, 
        this message is used to request that the next segment (of up to 7 bytes)
        be transmitted from SDO server to client.

        The Upload SDO Segment  Request
        ================================
            bit 7..5  - ccs: Client Command Specifier = 3 ( bin(0x60)='0b1100000' )
            bit 4     - t: toggle bit  set to 0 in first segment request, 
                              toggled with each subsequent request
            bit 0..3  - x: reserved

        The Upload SDO Segment  Response
        =================================
         bit 7..5 - scs:Server Command Specifier = 0
         bit 4    - t: toggle bit  set to 0 in first segment, 
                     toggled with each subsequent response 
         bit 3..1 -    n: number of data bytes in Byte 1..7 that do not contain data
         bit 0    - c: set to 1 if this is the last segment/fragment
        
            
        '''
        # assign buffer for data
        buf =  (0).to_bytes(8,'little')  
        # assing Upload SDO Segment Request msg 
        msg =  (0x60).to_bytes(8,'little')
        # number of data bytes to recieve
        nDelivery = struct.unpack_from('L',msgRet,4)[0] if ( msgRet[0] & 1 ) else -1
        while True:
            msgRet = self.pingCanMessage( nodeId + 0x600 ,  nodeId + 0x580 ,msg , tout = 0.02) 
            # toggle bit
            msg = (msg[0] ^ 0x10).to_bytes(1,'little') + msg[1:]
            # verify returned message~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #Test abort message
            if msgRet[0] & CANOPEN_SDO_CS_RX_ADT : 
                AbortCode =  struct.unpack_from('L',msgRet,4)[0] # Return error code + abort 
                logging.error ( 'Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] \
                for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) )  
                               
                raise Exception(  'Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] \
                for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) )
                #return AbortCode

            #Test command specifier 
            if (msgRet[0] & CANOPEN_SDO_CS_MASK ) != 0:
                logging.error ('Bad response to SDO upload init') 
                raise Exception('Bad response to SDO upload init')

           # number of data bytes in Byte 1..7 that do not contain data
            n = 7 - (( msgRet[0] >> 1 ) & 7 )
            # add 7-n bytes to buf
            buf = buf + msgRet[1:n+1]
            # is all data sent?
            if ( len( buf ) >= nDelivery + 8 ) or msgRet[0] & 1 : # Complete or already message length exceeded
                break
        # 0<=nDelivery
        nDelivery = len(buf)-8 if nDelivery < 0 else nDelivery
        if nDelivery !=  len(buf)-8 or nDelivery <= TypeLength[Type][0]:
            raise Exception('Length of SDO upload not as expected')
       
        if Type == 'vis string' :#and decode:
            return buf[8:].decode('ascii') 
        else:
            return buf[8:] 
        return  struct.unpack_from(TypeLength[Type][2],buf,8)[0]


        logging.error ('Unknown error') 
        raise Exception('Unknown error')



    def SDODownload(self, node, index, subindex, data , Type,AbortMsg = None ):
        """
        SetSdo~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


        The Initiate SDO Download – Request
        ===================================
        The client (typically the node trying to configure a CANopen slave)
        sends this request to a SDO server (implemented within a CANopen slave)
        by using the CAN identifier 600h plus the Node ID of the CANopen slave addressed.
        The download request is a request to write to a specific Object Dictionary entry.

        bit 7..5 - ccs: Client Command Specifier = 1
        bit 4    - x: reserved
        bit 3..2 - n: if e=s=1, number of data bytes in Byte 4..7 that do not contain data
        bit 1    - e: set to 1 for expedited transfer (data is in bytes 4-7)
        bit 0    - s: set to 1 if data size is indicated
        
        The Initiate SDO Download – Response
        ====================================      
        This is the response sent back from the SDO server to the client indicating that the
        previously received download (write) request was processed successfully. 
        The default CAN identifier used for this message is 580h plus the Node ID
        of the node implementing the SDO server.

        bit 7..5 - scs: Server Command Specifier = 3
        bit 4..0 - x: reserved
        """
        # test type message  
        Type = Type.lower()
        if  Type not in TypeLength.keys():
            logging.error('SDO desired for ilegal type, found['+repr(Type)+'] , permitted: ' + repr(TypeLength.keys()) )
            raise Exception('SDO desired for ilegal type, found['+repr(Type)+'] , permitted: ' + repr(TypeLength.keys()))
        
        #test data on 'vis string' and create message
        if Type == 'vis string': 
            if not type(data)  is str:
                #logging.error('Required visible string for non string data' )
                raise Exception('Required visible string for non string data')
           # The Initiate SDO Download with indicated data size 
            msg =  ((1<<5)+1).to_bytes(1,'little')+(Index).to_bytes(2,'little')+\
                (SubIndex).to_bytes(1,'little')+(len(data)).to_bytes(4,'little') # SDO dnload init 
           
        else:
            msg =  ((1<<5)+((4-TypeLength[Type][0])<<2)+(1<<1)+1).to_bytes(1,'little')+(Index).to_bytes(2,'little')+\
                (SubIndex).to_bytes(1,'little')+data.to_bytes(4,'little') # SDO dnload init 

        #Sends SDO requests to each node by using message ID:600h + Node ID  
        #Expects reply in message ID: 580h + Node ID     
        msgRet = self.pingCanMessage( nodeId + 0x600 ,  nodeId + 0x580 ,msg , tout = 0.02) 
         
        # verify returned message~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Test abort message
        if msgRet[0] & CANOPEN_SDO_CS_RX_ADT : 
                AbortCode =  struct.unpack_from('L',msgRet,4)[0] # Return error code + abort 
                assert not (type(AbortMsg) is str), AbortMsg+ ': SetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + ']\
                for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) 
                #logging.error ( 'Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] \
                #for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) )                
                raise Exception(  'Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] \
                for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) )
        
        #Test command specifier and multiplexor
        if (((msgRet[0] & CANOPEN_SDO_CS_MASK ) >> 5 ) != 3) or ( msgRet[1:4] != msg[1:4] ) : 
            raise Exception('Bad response to SDO download init') 


        '''The Download SDO Segment – Request
           ==================================
        If in the initiation sequence a segmented transfer was negotiated, 
        this message is used to transmit the next segment (of up to 7 bytes)
        from client to SDO server.

        bit 7..5 - ccs: Client Command Specifier = 0
        bit 4    - t: toggle bit – set to 0 in first segment, toggled with each subsequent request
        bit 3..1 - n: number of data bytes in Byte 1..7 that do not contain data
        bit 0    - c: set to 1 if this is the last segment/fragment
       
        
        
         The Download SDO Segment – Response 
         ====================================
         This is the response sent back from the SDO server to the client 
         indicating that the previously received download (write) segment 
         request was processed successfully

        bit 7..5 - scs: Server Command Specifier = 1
        bit 4    - t: toggle bit – set to 0 in first segment, toggled with each subsequent request
        bit 3..0 - x: reserved
       
       
           '''
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
            #Sends SDO requests to each node by using message ID:600h + Node ID  
            #Expects reply in message ID: 580h + Node ID     
            msgRet = self.pingCanMessage( nodeId + 0x600 ,  nodeId + 0x580 ,msg , tout = 0.02) 
                
            # verify returned message~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #Test abort message
            if msgRet[0] & CANOPEN_SDO_CS_RX_ADT : 
                    AbortCode =  struct.unpack_from('L',msgRet,4)[0] # Return error code + abort 
                    logging.error ( 'Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] \
                    for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) )                
                    raise Exception(  'Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] \
                    for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) )
        

        return 0 




    def SDOUploadBlock(self, node, index, subindex, size):
        """
        Block SDO upload.
        """



    def SDODownloadBlock(self, node, index, subindex, str_data, size):
        """
        Initiate Block Download
        =======================
        To initiate a block download the client sends the request to the server 
        to which the server sends a response.

        Message contents of the request
        bit 7..5 - ccs: Client Command Specifier = 6
        bit 4..3 - x: Reserved
        bit 2    - cc: Client CRC support, set to 1 if client supports CRC
        bit 1    - s: Size indicator, set if size of data to transmit is indicated
        bit 0    - cs: Client subcommand = 0
        byte 1-3 - The Multiplexor contains the Index and Subindex of the OD entry that the
                   client wants to write to
        byte 4-7 -size: Contains the size of the data block in bytes, if s is set
        """
    

    def SetPdoMapping( self , NodeId , PdoNum , FlagRxTxIn , TransType , IndexArr , SubIndexArr , LenArr , PdoCobId =None ):
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
        self.SDODownload( NodeId , pdoMap, 0 , 0 , 'unsigned8' , AbortMsg = 'Cannot delete previous mapping') ;

        if PdoCobId != None : 
            Value,AbortFlag= self.SDOUpload(  NodeId , pdoPar, 1 , 'unsigned32' ) ;
            if AbortFlag: 
                error( 'Cannot program PDO parameters' )
                pdoCobId = PdoCobId | (3<<30) # No RTR allowed
                self.SDODownload( h , NodeId , pdoPar , 1 , pdoCobId , 'unsigned32' ,'Cannot set transmission type') 

# Send SDO download to set transmission type.
# Transmission type resides at the sub-index 2h of the PDO Communication Parameter record.				
        self.SDODownload( h , NodeId , pdoPar , 2 , TransType , 'unsigned8' ,'Cannot set transmission type') ;

# Mapping loop for all PDO objects to be mapped
        for subIndex in range(len(IndexArr)):
        # The sub-indices from 1 to n contain the information about the mapped objects.
        # Every entry  describes the PDO by its index, sub-index and length
        # according to the Fig.66 CiA DS301 : 
        # 16 most significant bits is object index
        # 8 next bits is sub-index
        # 8 least significant bits is length of object	
            data = IndexArr(subIndex)*65536 + SubIndexArr(subIndex)*256 + LenArr(subIndex) ;
            AbortFlag = self.SDODownload( h , NodeId , pdoMap , subIndex , data , 'unsigned32' ) ;
            if AbortFlag:
                err = self.AnalyzeSdoAbort( AbortFlag ) ;
                error( 'Cannot set mapping: '+err) 

# Send SDO download to set number of entries of the PDO mapped objects 
# Subindex 0 is number of mapped objects in PDO
# For changing the PDO mapping the previous PDO must be deleted, the sub-index 0 must be set to 0. 	
        AbortFlag = self.SDODownload( h , NodeId , pdoMap, 0 , length(IndexArr) , 'unsigned8' ) 
        if AbortFlag:
            err = self.AnalyzeSdoAbort( AbortFlag ) ;
            error( 'Cannot delete previous mapping: {0}'+err) 


        AbortFlag = self.SDOUpload( h , NodeId , pdoMap, 0 , 'unsigned8' ) 
        if AbortFlag:
            err = self.AnalyzeSdoAbort( AbortFlag ) ;
            error('Cannot delete previous mapping: '+err ) ;

#Get a recorder vector 
 #h: Communication handle 
 #NodeId: Node Id to bring the data from 
 #BitNumber: The index of the recorded value 
 #unsign: 1 if numbers are to be brought unsigned  
        
    def GetBH( self , NodeId = None , BitNumber = 0 , unsign = 0  ) :
# function Arr = GetBH( h , NodeId , BitNumber , usign ) 

        Value,AbortFlag = self.SDOUpload( NodeId , 8240 , BitNumber , 'vis string' , 3 , decode = False); # 8240 = 0x2030
        
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

    def GetRU( self, NodeId = None , BitNumber = 0 , unsign = 0 , bDmdRec = 0 ) :
# function Arr = GetBH( h , NodeId , BitNumber , usign ) 

        Value = self.SDOUpload(  NodeId , 8277 if bDmdRec else 8240 , BitNumber , 'vis string' , 3 , decode = False); # 8240 = 0x2030
        
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


    def SetOsIntCmd( self , str , NodeId = None  ): 
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
        self.SDODownload(  NodeId , 4131 , 1 , str , 'vis string' , 'OS interpreter send cmd'); # 4131 = 0x1023

    #Wait till target is ready 
    #Result = 0 for completed, no reply 
    #1 no errors, reply 
    #2 error , no reply 
    #3 error , reply there 
        Value = 255 ;
        while Value == 255 : 
           Value,AbortFlag = self.SDOUpload( NodeId , 4131 , 2 , 'unsigned8' , 'OS interpreter wait ready ');# 4131 = 0x1023

        assert Value & 1 , 'Os interpreter failed' 

        Value = self.SDOUpload( h , NodeId , 4131 , 3 , 'vis string' , Timeout ,'OS interpreter get result ');# 4131 = 0x1023
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

