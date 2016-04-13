''' Python Wrapper for NiCAN driver under Windows OS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
---------------------------------
NiCAN FRAME API  for C functions
---------------------------------
ncAction               -- Perform an action on an object.
ncCloseObject          -- Close an object.
ncConfig               -- Configure an object before using it.
ncConnectTerminals     -- Connect terminals in the CAN or LIN hardware.
ncCreateNotification   -- Create a notification call back for an object.
ncDisconnectTerminals  -- Disconnect terminals in the CAN or LIN
hardware.
ncGetAttribute         -- Get the value of an object attribute.
ncGetHardwareInfo      -- Get CAN and LIN hardware information.
ncOpenObject           -- Open an object.
ncRead                 -- Read the data value of an object.
ncReadMult             -- Read multiple data values from the queue of an
object.
ncSetAttribute        -- Set the value of an object attribute.
ncStatusToString      -- Convert status code into a descriptive string.
ncWaitForState        -- Wait for one or more states to occur in an object.
ncWrite               -- Write the data value of an object.
ncWriteMult           -- Write multiple frames to a CAN or LIN

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Implemented functions :
    ncStatusToString
    ncRead
    ncWrite
    ncOpenObject
    ncCloseObject
    ncSetAttribute
    ncGetAttribute
    ncConfig
    ncAction
    ncWaitForState
'''
from ctypes import *
import sys
import struct
import logging
import inspect
import time
#------------------------------------------------------------------#
# NiCan constants                                                 #
#------------------------------------------------------------------#
NC_ATTR_ABS_TIME = 0x80000008
NC_ATTR_BAUD_RATE = 0x80000007
NC_ATTR_BEHAV_FINAL_OUT = 0x80010018
NC_ATTR_BKD_CAN_RESPONSE = 0x80010006
NC_ATTR_BKD_CHANGES_ONLY = 0x80000015
NC_ATTR_BKD_PERIOD = 0x8000000F
NC_ATTR_BKD_READ_SIZE = 0x8000000B
NC_ATTR_BKD_TYPE = 0x8000000D
NC_ATTR_BKD_WHEN_USED = 0x8000000E
NC_ATTR_BKD_WRITE_SIZE = 0x8000000C

NC_ATTR_CAN_BIT_TIMINGS = 0x80010005
NC_ATTR_CAN_COMP_STD = 0x80010001
NC_ATTR_CAN_COMP_XTD = 0x80010003
NC_ATTR_CAN_DATA_LENGTH = 0x80010007
NC_ATTR_CAN_MASK_STD = 0x80010002
NC_ATTR_CAN_MASK_XTD = 0x80010004
NC_ATTR_CAN_TX_RESPONSE = 0x80010006

NC_ATTR_COMM_TYPE = 0x80000016
NC_ATTR_COMP_STD = 0x80010001
NC_ATTR_COMP_XTD = 0x80010003
NC_ATTR_DATA_LEN = 0x80010007
NC_ATTR_HW_FORMFACTOR = 0x80020004     # Formfactor of card - NC_HW_FORMFACTOR_???
NC_ATTR_HW_SERIAL_NUM = 0x80020003     # Serial Number of card
NC_ATTR_HW_SERIES = 0x80020005     # Series of Card - NC_HW_SERIES_???
#NC_ATTR_HW_TRANSCEIVER = NC_ATTR_TRANSCEIVER_TYPE # NC_HW_TRANSCEIVER_???
NC_ATTR_INTERFACE_NUM = 0x80020008     # 0 for CAN0, 1 for CAN1, etc...
NC_ATTR_IS_NET_SYNC = 0x8001000E
NC_ATTR_LIN_CHECKSUM_TYPE = 0x80020043
NC_ATTR_LIN_ENABLE_DLC_CHECK = 0x80020045
NC_ATTR_LIN_LOG_WAKEUP = 0x80020046
NC_ATTR_LIN_RESPONSE_TIMEOUT = 0x80020044
NC_ATTR_LIN_SLEEP = 0x80020042
NC_ATTR_LISTEN_ONLY = 0x80010010
NC_ATTR_LOG_BUS_ERROR = 0x80020037
NC_ATTR_LOG_COMM_ERRS = 0x8001000A
NC_ATTR_LOG_START_TRIGGER = 0x80020031
NC_ATTR_LOG_TRANSCEIVER_FAULT = 0x80020038
NC_ATTR_MASK_STD = 0x80010002
NC_ATTR_MASK_XTD = 0x80010004
NC_ATTR_MASTER_TIMEBASE_RATE = 0x80020033
NC_ATTR_NET_SYNC_COUNT = 0x8001000D
NC_ATTR_NOTIFY_MULT_LEN = 0x8001000B
NC_ATTR_NOTIFY_MULT_SIZE = 0x8001000B
NC_ATTR_NUM_CARDS = 0x80020002    # Number of Cards present in system.
NC_ATTR_NUM_PORTS = 0x80020006     # Number of Ports present on card
NC_ATTR_PERIOD = 0x8000000F
NC_ATTR_PROTOCOL = 0x80000001
NC_ATTR_PROTOCOL_VERSION = 0x80000002
NC_ATTR_READ_PENDING = 0x80000011
NC_ATTR_READ_Q_LEN = 0x80000013
NC_ATTR_RESET_ON_START = 0x80010008
NC_ATTR_RTSI_FRAME = 0x80000020
NC_ATTR_RTSI_MODE = 0x80000017
NC_ATTR_RTSI_SIG_BEHAV = 0x80000019
NC_ATTR_RTSI_SIGNAL = 0x80000018
NC_ATTR_RTSI_SKIP = 0x80000021
NC_ATTR_RX_CHANGES_ONLY = 0x80000015
NC_ATTR_RX_ERROR_COUNTER = 0x80010011
NC_ATTR_RX_Q_LEN = 0x8001000C
NC_ATTR_SELF_RECEPTION = 0x80010016
NC_ATTR_SERIAL_NUMBER = 0x800000A0
NC_ATTR_SERIES2_COMP = 0x80010013
NC_ATTR_SERIES2_ERR_ARB_CAPTURE = 0x8001001C
NC_ATTR_SERIES2_FILTER_MODE = 0x80010015
NC_ATTR_SERIES2_MASK = 0x80010014
NC_ATTR_SINGLE_SHOT_TX = 0x80010017
NC_ATTR_SOFTWARE_VERSION = 0x80000003
NC_ATTR_START_ON_OPEN = 0x80000006
NC_ATTR_START_TRIG_BEHAVIOR = 0x80010023
NC_ATTR_STATE = 0x80000009
NC_ATTR_STATUS = 0x8000000A
NC_ATTR_TERMINATION = 0x80020041
NC_ATTR_TIMELINE_RECOVERY = 0x80020035
NC_ATTR_TIMESTAMP_FORMAT = 0x80020032
NC_ATTR_TIMESTAMPING = 0x80000010
NC_ATTR_TRANSCEIVER_EXTERNAL_IN = 0x8001001B
NC_ATTR_TRANSCEIVER_EXTERNAL_OUT = 0x8001001A
NC_ATTR_TRANSCEIVER_MODE = 0x80010019
NC_ATTR_TRANSCEIVER_TYPE = 0x80020007
NC_ATTR_TRANSMIT_MODE = 0x80020029
NC_ATTR_TX_ERROR_COUNTER = 0x80010012
NC_ATTR_TX_RESPONSE = 0x80010006
NC_ATTR_VERSION_BUILD = 0x8002000D     # U32 build (primarily useful for beta)
NC_ATTR_VERSION_COMMENT = 0x8002000E     # String comment on version (max 80 chars)
NC_ATTR_VERSION_MAJOR = 0x80020009    # U32 major version (X in X.Y.Z)
NC_ATTR_VERSION_MINOR = 0x8002000A     # U32 minor version (Y in X.Y.Z)
NC_ATTR_VERSION_PHASE = 0x8002000C     # U32 phase (1=alpha, 2=beta, 3=release)
NC_ATTR_VERSION_UPDATE = 0x8002000B     # U32 minor version (Z in X.Y.Z)
NC_ATTR_VIRTUAL_BUS_TIMING = 0xA0000031
NC_ATTR_WRITE_ENTRIES_FREE = 0x80020034
NC_ATTR_WRITE_PENDING = 0x80000012
NC_ATTR_WRITE_Q_LEN = 0x80000014


NC_BKD_TYPE_PEER2PEER = 0x00000001
NC_BKD_TYPE_REQUEST = 0x00000002
NC_BKD_TYPE_RESPONSE = 0x00000003
NC_BKD_WHEN_PERIODIC = 0x00000001
NC_BKD_WHEN_UNSOLICITED = 0x00000002
NC_BKD_CAN_ZERO_SIZE = 0x00008000


#************ OTHER CONSTANTS ***************************************
NC_TRUE = 1    
NC_FALSE = 0
NC_OP_START = 0x80000001
NC_OP_STOP = 0x80000002
NC_ST_READ_AVAIL = 0x00000001
NC_DURATION_NONE = 0            #  /* zero duration */
NC_DURATION_INFINITE = 0xFFFFFFFF    # /* infinite duration */
NC_DURATION_1MS = 1            #  /* one millisecond */
NC_DURATION_10MS = 10
NC_DURATION_100MS = 100
NC_DURATION_1SEC = 1000         # /* one second */
NC_DURATION_10SEC = 10000
NC_DURATION_100SEC = 100000
NC_DURATION_1MIN = 60000          #/* one minute */

#NCTYPE_PROTOCOL (values for supported protocols) */
NC_PROTOCOL_CAN = 1             # Controller Area Net 
NC_ST_READ_AVAIL = 0x00000001
NC_ST_WRITE_SUCCESS = 0x00000002
NC_ST_ESTABLISHED = 0x00000008
NC_ST_STOPPED = 0x00000004
NC_ST_ERROR = 0x00000010
NC_ST_WARNING =0x00000020
NC_ST_REMOTE_WAKEUP = 0x00000040
NC_ST_WRITE_MULT = 0x00000080
NC_OP_START = 0x80000001
NC_OP_STOP = 0x80000002
NC_OP_RESET = 0x80000003
NC_OP_ACTIVE = 0x80000004
NC_OP_IDLE = 0x80000005
NC_OP_RTSI_OUT = 0x80000004

#NCTYPE_BAUD_RATE (values for baud rates) */
NC_BAUD_10K = 10000
NC_BAUD_100K = 100000
NC_BAUD_125K = 125000
NC_BAUD_250K = 250000
NC_BAUD_500K = 500000
NC_BAUD_1000K = 1000000
# NCTYPE_DURATION (values in one millisecond ticks) */
NC_DURATION_NONE = 0             # /* zero duration */
NC_DURATION_INFINITE = 0xFFFFFFFF    # /* infinite duration */
NC_DURATION_1MS = 1            #  /* one millisecond */
NC_DURATION_10MS = 10
NC_DURATION_100MS = 100
NC_DURATION_1SEC = 1000          # /* one second */
NC_DURATION_10SEC = 10000
NC_DURATION_100SEC = 100000
NC_DURATION_1MIN = 60000         # /* one minute */

NC_FL_CAN_ARBID_XTD = 0x20000000


NC_FRMTYPE_DATA = 0x00
NC_FRMTYPE_REMOTE = 0x01



# Values for NC_ATTR_SERIES2_FILTER_MODE
NC_FILTER_SINGLE_STANDARD = 0;
NC_FILTER_SINGLE_EXTENDED = 1;
NC_FILTER_DUAL_STANDARD = 2;
NC_FILTER_DUAL_EXTENDED = 3;


''' Depending on the number of data bytes in a data frame, 
the length of a data frame varies from 44 to 108 bits.
 However, due to the bit stuffing the actual length of a data frame can be longer'''
CAN_FRAME_SIZE = 14
CAN_STRUCT_SIZE = 22
BUFF = 512
class canError(Exception):
    def __init__(self, canlib, canERR):
        self.canlib = canlib
        self.canERR = canERR

    def __canGetErrorText(self):
        msg = create_string_buffer(80)
        self.canlib.dll.ncStatusToString(self.canERR,sizeof(msg),msg)
        return msg.value

    def __str__(self):
        return "[canError] %s: %s (%d)" % (self.canlib.fn, self.__canGetErrorText(), self.canERR)

class canWarning:
    def __init__(self,canlib,canWarn):
         self.canlib = canlib
         self.canWarn = canWarn

    def __canGetWarnText(self):
        msg = create_string_buffer(80)
        self.canlib.dll.ncStatusToString(self.canWarn,sizeof(msg),msg)

        return msg.value

    def __str__(self):
        return "[canWarn] %s: %s (%d)" % (self.canlib.fn, self.__canGetWarnText(), self.canWarn)

class NCTYPE_CAN_FRAME(Structure):  # size of structure is 14 bytes(4,2,8)
   #By default, Structure and Union fields are aligned in the same way the C compiler does it. 
   #It is possible to override this behavior be specifying a _pack_ class attribute in the subclass definition.
   # This must be set to a positive integer and specifies the maximum alignment for the fields. 
   #This is what #pragma pack(n) also does in MSVC.
    ''' /* Type for ncWrite of CAN Network Interface Object */
        typedef  struct {
           NCTYPE_CAN_ARBID                    ArbitrationId;
           NCTYPE_BOOL                         IsRemote;
           NCTYPE_UINT8                        DataLength;
           NCTYPE_UINT8                        Data[8];
        } NCTYPE_CAN_FRAME;'''
    _pack_= 1    
    _fields_ = [ 
        ("ArbitrationId", c_uint32),#NCTYPE_CAN_ARBID
        ("IsRemote", c_uint8),      #NCTYPE_BOOL     
        ("DataLength", c_uint8),    #NCTYPE_UINT8, length of Data in bytes 
        ("Data", c_uint8*8)        #NCTYPE_UINT8
        ]

    def __str__(self):
        return "[%d:%s]" % ( self.ArbitrationId,self.Data)

class NCTYPE_UINT64(Structure):
    '''
    typedef  struct {
       NCTYPE_UINT32                       LowPart;
       NCTYPE_UINT32                       HighPart;
    } NCTYPE_UINT64;'''
    _pack_= 1    
    _fields_ = [ 
        ("LowPart",c_uint32),
         ("HighPart",c_uint32)
        ]

         
class NCTYPE_CAN_STRUCT(Structure) : #size of structure is 22 bytes (8,4,2,8)
    '''  /* Type for ncRead of CAN Network Interface Object (using FrameType instead of IsRemote).
   Type for ncWrite of CAN Network Interface Object when timed transmission is enabled. */
    typedef  struct {
       NCTYPE_ABS_TIME                     Timestamp;
       NCTYPE_CAN_ARBID                    ArbitrationId;
       NCTYPE_UINT8                        FrameType;
       NCTYPE_UINT8                        DataLength;
       NCTYPE_UINT8                        Data[8];
    } NCTYPE_CAN_STRUCT;
    '''
    _pack_= 1    
    _fields_ = [
        ("TimeStamp", NCTYPE_UINT64) ,     #NCTYPE_ABS_TIME, which is NCTYPE_UINT64, 8 bytes
        ("ArbitrationId", c_ulong), #NCTYPE_CAN_ARBID, which is NCTYPE_UINT32, 4 bytes  
        ("FrameType",c_uint8),       #NCTYPE_UINT8,   RTR or DATA
        ("DataLength", c_uint8),     #NCTYPE_UINT8   
        ("Data", c_uint8*8)          #NCTYPE_UINT8*8
        ]



#----------------------------------------------------------------------#
# Canlib class                                                         #
#----------------------------------------------------------------------#

class canlib(object):

    # definitions
    #canMessage = 8 * c_uint8
     # network interface constants
    #AttrNames = [ 'NC_ATTR_BAUD_RATE','NC_ATTR_START_ON_OPEN']
    #AttrDict = {  NC_ATTR_BAUD_RATE:1000000,NC_ATTR_START_ON_OPEN: NC_FALSE }


    def __init__(self, debug=None):
        fmt = '[%(levelname)s] %(funcName)s: %(message)s'
        if debug:
            logging.basicConfig(stream=sys.stderr,
                                level=logging.DEBUG,
                                format=fmt)
        else:
            logging.basicConfig(stream=sys.stderr,
                                level=logging.ERROR,
                                format=fmt)

        if sys.platform.startswith('win'):
            self.dll = WinDLL('nican')        
          
        else:
            logging.error("This library doesn't support this OS")

        # prototypes

        self.dll.ncGetHardwareInfo.argtypes =  [c_uint, c_uint, c_uint, c_uint,POINTER(None)]
        self.dll.ncGetHardwareInfo.restype = c_int32
        self.dll.ncGetHardwareInfo.errcheck = self._canErrorCheck

        self.dll.ncConfig.argtypes = [c_char_p, c_ulong, POINTER(c_ulong), POINTER(c_ulong)]
        self.dll.ncConfig.restype = c_int32
        self.dll.ncConfig.errcheck = self._canErrorCheck


        self.dll.ncOpenObject.argtypes = [ c_char_p,POINTER(c_ulong)]
        self.dll.ncOpenObject.restype = c_int32
        self.dll.ncOpenObject.errcheck = self._canErrorCheck

        self.dll.ncCloseObject.argtypes = [ c_ulong]
        self.dll.ncCloseObject.restype = c_int32
        self.dll.ncCloseObject.errcheck = self._canErrorCheck

        self.dll.ncGetAttribute.argtypes = [c_ulong,c_uint,c_uint32,POINTER(None)]
        self.dll.ncGetAttribute.restype = c_int32
        self.dll.ncGetAttribute.errcheck = self._canErrorCheck

        self.dll.ncSetAttribute.argtypes = [c_ulong,c_uint,c_uint32,POINTER(None)]
        self.dll.ncSetAttribute.restype = c_int32
        self.dll.ncSetAttribute.errcheck = self._canErrorCheck

        self.dll.ncAction.argtypes = [c_ulong, c_ulong, c_ulong]
        self.dll.ncAction.restype = c_int32
        self.dll.ncAction.errcheck = self._canErrorCheck

        self.dll.ncWrite.argtypes = [c_ulong, c_uint32, POINTER(None)]
        self.dll.ncWrite.restype = c_int32
        self.dll.ncWrite.errcheck = self._canErrorCheck

        self.dll.ncRead.argtypes = [c_ulong, c_uint32, POINTER(None)]
        self.dll.ncRead.restype = c_int32
        self.dll.ncRead.errcheck = self._canErrorCheck

        self.dll.ncWaitForState.argtypes = (c_ulong,c_ulong,c_ulong,POINTER(c_ulong))
        self.dll.ncRead.restype = c_int32
        self.dll.ncRead.errcheck = self._canErrorCheck

        self.dll.ncReadMult.argtypes = (c_ulong,c_ulong, POINTER(None), POINTER(c_ulong))
        self.dll.ncRead.restype = c_int32
        self.dll.ncRead.errcheck = self._canErrorCheck



    def _canErrorCheck(self, result, func, arguments):
        status = "Method: "+ func.__name__
        if result == 0: #OK
            status += "OK Status:" + str(result )
            logging.debug(status)
        elif result < 0: #ERROR
            raise canError(self, result)
        elif result > 0:  # Warning
            logging.warning(canWarning(self,result))            
        return result



    #------------------------------------------------------------------#
    # API                                                              #
    #------------------------------------------------------------------#

    def getHardwareInfo(self, cardNumber = 1, portNumber = 1,AttrId = NC_ATTR_HW_SERIAL_NUM, AttrSize = 4):
        """ This function returns hardware info """
        self.fn = inspect.stack()[0][3]
        res_type = c_uint * 1
        res = res_type()
        self.dll.ncGetHardwareInfo( cardNumber,portNumber,AttrId, AttrSize,byref(res))       
        return res[0]
########## not tested - maybe buggy~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getNumberOfCannels(self):
      return self.getHardwareInfo(AttrId= NC_ATTR_NUM_PORTS)

    def getChannelData_Name(self,ch):
        return  self.getHardwareInfo(AttrId = NC_ATTR_TRANSCEIVER_TYPE|NC_ATTR_INTERFACE_NUM|NC_ATTR_HW_SERIES)

    def getChannelData_EAN(self,ch):
        return self. getHardwareInfo()
##################################################################################################################
    def openChannel(self, channel):
        self.fn = inspect.stack()[0][3]
        ObjName = 'CAN%s'%channel
        return canChannel(self,ObjName)

class canChannel(object):
   
    def __init__(self, canlib, ObjName):
        self.canlib    = canlib
        self.dll       = canlib.dll
        #self.index     = channel
        self.canlib.fn = 'openChannel'
        self.aCanObjHandle = pointer(c_ulong(0))
        self.objName = ObjName
        #init config params
        self.setBaud()
     
          
    def setBaud(self,baud=1000000):
        '''assign baud
        must be called before procedure config 
        '''
        self.baud = baud


    def config(self):
        '''ncConfig: Only the Baudrate and StartOnOpen attributes are used; other values are ignored.
        ---- direct call func from Nican.dll --------------
        ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncConfig(
                    NCTYPE_STRING ObjName,
                    NCTYPE_UINT32 NumAttrs,
                    NCTYPE_ATTRID_P AttrIdList,
                    NCTYPE_UINT32_P AttrValueList);
                    '''
        self.fn = inspect.stack()[0][3]
     
        NumAttrs =c_ulong(2)
        AttrIdArr = 2*c_ulong

        self.AttrIdList = AttrIdArr( NC_ATTR_BAUD_RATE,NC_ATTR_START_ON_OPEN )
        AttrValueArr = 2*c_ulong
        self.AttrValueList = AttrValueArr( self.baud,  NC_FALSE)    
        aObjName = create_string_buffer(bytes(self.objName,'ascii'))
        self.dll.ncConfig(aObjName, NumAttrs, self.AttrIdList, self.AttrValueList)


    def getAttribute(self,AttrId =  NC_ATTR_HW_SERIAL_NUM):
        '''
        ---- direct call func from Nican.dll --------------
        ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncGetAttribute(
                        NCTYPE_OBJH ObjHandle,
                        NCTYPE_ATTRID AttrId,
                        NCTYPE_UINT32 AttrSize,
                        NCTYPE_ANY_P AttrPtr);
        '''
        Attr = c_uint(0)
        #aAttrId  = c_uint(AttrId)      
        self.dll.ncGetAttribute(self.aCanObjHandle.contents, AttrId, 4,byref(Attr))
        return Attr.value

    def setAttribute(self,AttrId = NC_ATTR_SINGLE_SHOT_TX,AttrVal=0):
        '''
         ---- direct call func from Nican.dll --------------
        ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncSetAttribute(
                    NCTYPE_OBJH ObjHandle,
                    NCTYPE_ATTRID AttrId,
                    NCTYPE_UINT32 AttrSize,
                    NCTYPE_ANY_P AttrPtr);
        '''
        Attr = c_ulong(AttrVal)
        #aAttrId  = c_uint(AttrId)       
        self.dll.ncSetAttribute(self.aCanObjHandle.contents, AttrId,  c_uint32(4), byref(Attr))
        #return Attr.value

    def open(self):
        '''  
         OPEN OPEN OPEN OPEN OPEN OPEN OPEN
         ---- direct call func from Nican.dll --------------
        ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncOpenObject(
                    NCTYPE_STRING ObjName,
                    NCTYPE_OBJH_P ObjHandlePtr);
        ''' 
        aObjName = create_string_buffer(bytes(self.objName,'ascii'))
        self.dll.ncOpenObject(aObjName, self.aCanObjHandle)         
       


    def close(self):
        '''  
        CLOSE CLOSE CLOSE CLOSE CLOSE CLOSE CLOSE CLOSE
        ---- direct call func from Nican.dll --------------
        ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncCloseObject(
                        NCTYPE_OBJH ObjHandle);
       '''      
        self.dll.ncCloseObject(self.aCanObjHandle.contents)
       
       
    def action(self):
        '''
        //---- direct call func from Nican.dll --------------
        Its normal use is to start and stop network communication on a
        CAN Network Interface Object
         ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncAction(
                        NCTYPE_OBJH ObjHandle,
                        NCTYPE_OPCODE Opcode,
                        NCTYPE_UINT32 Param);'''
        self.dll.ncAction(self.aCanObjHandle.contents, c_ulong(NC_OP_START), c_ulong(0))


    def write(self,id, data ,extended=False):
        '''//---- direct call func from Nican.dll --------------
         ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncWrite(
                        NCTYPE_OBJH ObjHandle,
                        NCTYPE_UINT32 DataSize,
                        NCTYPE_ANY_P DataPtr);
                        '''
        #id if not extended else  CanID | NC_FL_CAN_ARBID_XTD            
        frame = NCTYPE_CAN_FRAME(IsRemote = NC_FRMTYPE_DATA,
                       ArbitrationId = id if not extended else  id | NC_FL_CAN_ARBID_XTD,      #CanID | NC_FL_CAN_ARBID_XTD; // to make EXTended 29 bit frame
                       Data = (c_uint8*8)(*data),
                       DataLength = len(data)
                       )
        self.dll.ncWrite(self.aCanObjHandle.contents, sizeof(frame), byref(frame))


    def read (self):
        ''' ---- direct call func from Nican.dll --------------
        ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncRead(
                        NCTYPE_OBJH ObjHandle,
                        NCTYPE_UINT32 DataSize,
                        NCTYPE_ANY_P DataPtr);
        '''      
        canStruct =  NCTYPE_CAN_STRUCT()
        self.dll.ncRead(self.aCanObjHandle.contents, CAN_STRUCT_SIZE, byref (canStruct))
        data = [ d for d in canStruct.Data]
        # with extended Id(29bit instead 11bit) you should use mask NC_FL_CAN_ARBID_XTD(0x20000000) to get real id
        # example: canStruct.ArbitrationId&~0x20000000
        return canStruct.ArbitrationId,data[:canStruct.DataLength],canStruct.DataLength
   

    def waitForState(self,canState):
        '''---- direct call func from Nican.dll --------------
        ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
        NCTYPE_STATUS ncWaitForState(
                    NCTYPE_OBJH ObjHandle,
                    NCTYPE_STATE DesiredState,
                    NCTYPE_UINT32 Timeout,
                    NCTYPE_STATE_P StatePtr);
        '''
        #res_type = c_uint
        #statePtr = res_type()
        statePtr = c_ulong()
        self.dll.ncWaitForState(self.aCanObjHandle.contents,canState,NC_DURATION_1SEC,byref(statePtr))
        return statePtr


    def readMult(self):
        '''---- direct call func from Nican.dll --------------
        ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
         NCTYPE_STATUS _NCFUNC_ ncReadMult(
                           NCTYPE_OBJH          ObjHandle,
                           NCTYPE_UINT32        SizeofData,
                           NCTYPE_ANY_P         DataPtr,
                           NCTYPE_UINT32_P      ActualDataSize);'''
        canStructArr_Type =  NCTYPE_CAN_STRUCT*BUFF
        canStructArr = canStructArr_Type()
        ActualDataSize =  c_ulong()
        self.dll.ncReadMult(self.aCanObjHandle.contents,CAN_STRUCT_SIZE*BUFF,byref(canStructArr),byref(ActualDataSize)) #sizeof( NCTYPE_CAN_STRUCT())

        dataSize = ActualDataSize/CAN_STRUCT_SIZE

        data = [(frame.ArbitrationId,frame.DataLength,data[:frame.DataLength])  for frame in canStructArr[i] for i  in  range( dataSize )]
        return data

    #def createNotificationForReadMult(self,RefData):
    #    ''' ---- direct call func from Nican.dll --------------
    #    ~~~~~~~~~~~~~~~~~~C API~~~~~~~~~~~~~~~
    #    NCTYPE_STATUS _NCFUNC_ ncCreateNotification(
    #                       NCTYPE_OBJH          ObjHandle,
    #                       NCTYPE_STATE         DesiredState,
    #                       NCTYPE_DURATION      Timeout,
    #                       NCTYPE_ANY_P         RefData,
    #                       NCTYPE_NOTIFY_CALLBACK Callback);
    #   '''

       
    #def callback(OBJH,STATE,STATUS, RefData ):
    #    '''NCTYPE_NOTIFY_CALLBACK) (
    #                            NCTYPE_OBJH       ObjHandle,
    #                            NCTYPE_STATE      ObjHandle,
    #                            NCTYPE_STATUS     ObjHandle,
    #                            NCTYPE_ANY_P      RefData);'''
    #    canStructArr_Type =  NCTYPE_CAN_STRUCT*BUFF
    #    canStructArr = canStructArr_Type()
    #    ActualDataSize =  c_ulong()
    #    self.dll.ncReadMult(self.aCanObjHandle.contents,CAN_STRUCT_SIZE*BUFF,byref(canStructArr),byref(ActualDataSize)) #sizeof( NCTYPE_CAN_STRUCT())

    #    dataSize = ActualDataSize/CAN_STRUCT_SIZE

    #    data = [(frame.ArbitrationId,frame.DataLength,data[:frame.DataLength])  for frame in canStructArr[i] for i  in  range( dataSize )]


    #canStructArr_Type =  NCTYPE_CAN_STRUCT*BUFF
    #self.dll.ncCreateNotification(self.aCanObjHandle.contents,DesiredState,NC_DURATION_10SEC,byref(canStructArr),


    def isExtended(self,ArbitrationId):
        return ArbitrationId&NC_FL_CAN_ARBID_XTD

    #def filter(self,id):
    #    '''
    #     filter all ids apart from the id 
    #    '''   
    #    self.close()
    #    self.config() 
    #    self.open()
    #    self.setAttribute(NC_ATTR_SERIES2_FILTER_MODE,NC_FILTER_SINGLE_STANDARD)

    #    self.setAttribute( NC_ATTR_SERIES2_COMP,id<<21)        
    #    self.setAttribute( NC_ATTR_SERIES2_MASK,(id^0xFF)<<21|~(0x7F<<21))      
    #    #self.setAttribute(NC_ATTR_CAN_COMP_STD,id)
    #    #self.setAttribute(NC_ATTR_CAN_MASK_STD,0xFF4FFFFF)
    #    self.action()
        

if __name__=='__main__':
    print('Open Canlib')
    c = canlib(debug=True)
    print(c.getHardwareInfo())
    print(c.getHardwareInfo(AttrId= NC_ATTR_NUM_PORTS))
    print(c.getHardwareInfo(AttrId= NC_ATTR_TRANSCEIVER_TYPE))
    print(c.getHardwareInfo(AttrId= NC_ATTR_INTERFACE_NUM))
    print(c.getHardwareInfo(AttrId= NC_ATTR_HW_FORMFACTOR))
    print(c.getHardwareInfo(AttrId= NC_ATTR_HW_SERIES))

    print('Open channel')
    ch = c.openChannel(0)
   
    #call always before config
    ch.setBaud()
    print(ch.config())
    
    print(ch.open())
    #print(ch.config())
    print(ch.getAttribute())
    print(ch.getAttribute(AttrId = NC_ATTR_BAUD_RATE))
    #print(ch.setAttribute(AttrId = NC_ATTR_SERIES2_FILTER_MODE))
    print(ch.action())


    #print(ch.close())
    #print(ch.config())
    #print(ch.open())
    #print(ch.setAttribute(NC_ATTR_SERIES2_FILTER_MODE,NC_FILTER_SINGLE_STANDARD))
    ##print(ch.config())
    
    #print(ch.action())
     
    print('write')
    ch.write(1,[1,2,3,4,5,6,7,8],extended=True)  
    print('wait for queue to be empty????????????')
    #ch.waitForState(NC_ST_WRITE_SUCCESS)
    #ch.filter(0X5)
    while True:
        
        ch.waitForState(NC_ST_READ_AVAIL)
        res = ch.read()
        if ch.isExtended(res[0]):
            print('X')
        else:
            print('N')
        print(res)
        #print(ch.read())
        #time.sleep(0.5)
    #print(ch.read())
        
    print(ch.close())
    #print(c.open())






