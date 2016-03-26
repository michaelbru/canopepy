from ctypes import *
import sys
import struct
import logging
import inspect
import time
#------------------------------------------------------------------#
# Canlib constants                                                 #
#------------------------------------------------------------------#

canOK                                   =    0
canERR_PARAM                            =   -1
canERR_NOMSG                            =   -2
canERR_NOTFOUND                         =   -3
canERR_NOCHANNELS                       =   -5
canERR_TIMEOUT                          =   -7
canERR_INVHANDLE                        =  -10
canERR_NOCARD                           =  -26
canERR_NOT_IMPLEMENTED                  =  -32

canOPEN_EXCLUSIVE                       = 0x0008
canOPEN_REQUIRE_EXTENDED                = 0x0010
canOPEN_ACCEPT_VIRTUAL                  = 0x0020
canOPEN_OVERRIDE_EXCLUSIVE              = 0x0040
canOPEN_REQUIRE_INIT_ACCESS             = 0x0080
canOPEN_NO_INIT_ACCESS                  = 0x0100
canOPEN_ACCEPT_LARGE_DLC                = 0x0200

canBITRATE_1M                           = -1
canBITRATE_500K                         = -2
canBITRATE_250K                         = -3
canBITRATE_125K                         = -4
canBITRATE_100K                         = -5
canBITRATE_62K                          = -6
canBITRATE_50K                          = -7
canBITRATE_83K                          = -8
canBITRATE_10K                          = -9

canIOCTL_PREFER_EXT                     = 1
canIOCTL_PREFER_STD                     = 2
canIOCTL_CLEAR_ERROR_COUNTERS           = 5
canIOCTL_SET_TIMER_SCALE                = 6
canIOCTL_SET_TXACK                      = 7
canIOCTL_GET_RX_BUFFER_LEVEL            = 8
canIOCTL_GET_TX_BUFFER_LEVEL            = 9
canIOCTL_FLUSH_RX_BUFFER                = 10
canIOCTL_FLUSH_TX_BUFFER                = 11
canIOCTL_GET_TIMER_SCALE                = 12
canIOCTL_SET_TXRQ                       = 13
canIOCTL_GET_EVENTHANDLE                = 14
canIOCTL_SET_BYPASS_MODE                = 15
canIOCTL_SET_WAKEUP                     = 16
canIOCTL_MAP_RXQUEUE                    = 18
canIOCTL_GET_WAKEUP                     = 19
canIOCTL_SET_REPORT_ACCESS_ERRORS       = 20
canIOCTL_GET_REPORT_ACCESS_ERRORS       = 21
canIOCTL_CONNECT_TO_VIRTUAL_BUS         = 22
canIOCTL_DISCONNECT_FROM_VIRTUAL_BUS    = 23
canIOCTL_SET_USER_IOPORT                = 24
canIOCTL_GET_USER_IOPORT                = 25
canIOCTL_SET_BUFFER_WRAPAROUND_MODE     = 26
canIOCTL_SET_RX_QUEUE_SIZE              = 27
canIOCTL_SET_USB_THROTTLE               = 28
canIOCTL_GET_USB_THROTTLE               = 29
canIOCTL_SET_BUSON_TIME_AUTO_RESET      = 30
canIOCTL_GET_TXACK                      = 31
canIOCTL_SET_LOCAL_TXECHO               = 32
canIOCTL_SET_ERROR_FRAMES_REPORTING     = 33
canIOCTL_GET_CHANNEL_QUALITY            = 34
canIOCTL_GET_ROUNDTRIP_TIME             = 35
canIOCTL_GET_BUS_TYPE                   = 36
canIOCTL_GET_DEVNAME_ASCII              = 37
canIOCTL_GET_TIME_SINCE_LAST_SEEN       = 38
canIOCTL_GET_TREF_LIST                  = 39

canCHANNELDATA_CHANNEL_CAP              = 1
canCHANNELDATA_TRANS_CAP                = 2
canCHANNELDATA_CHANNEL_FLAGS            = 3
canCHANNELDATA_CARD_TYPE                = 4
canCHANNELDATA_CARD_NUMBER              = 5
canCHANNELDATA_CHAN_NO_ON_CARD          = 6
canCHANNELDATA_CARD_SERIAL_NO           = 7
canCHANNELDATA_TRANS_SERIAL_NO          = 8
canCHANNELDATA_CARD_FIRMWARE_REV        = 9
canCHANNELDATA_CARD_HARDWARE_REV        = 10
canCHANNELDATA_CARD_UPC_NO              = 11
canCHANNELDATA_TRANS_UPC_NO             = 12
canCHANNELDATA_CHANNEL_NAME             = 13
canCHANNELDATA_DLL_FILE_VERSION         = 14
canCHANNELDATA_DLL_PRODUCT_VERSION      = 15
canCHANNELDATA_DLL_FILETYPE             = 16
canCHANNELDATA_TRANS_TYPE               = 17
canCHANNELDATA_DEVICE_PHYSICAL_POSITION = 18
canCHANNELDATA_UI_NUMBER                = 19
canCHANNELDATA_TIMESYNC_ENABLED         = 20
canCHANNELDATA_DRIVER_FILE_VERSION      = 21
canCHANNELDATA_DRIVER_PRODUCT_VERSION   = 22
canCHANNELDATA_MFGNAME_UNICODE          = 23
canCHANNELDATA_MFGNAME_ASCII            = 24
canCHANNELDATA_DEVDESCR_UNICODE         = 25
canCHANNELDATA_DEVDESCR_ASCII           = 26
canCHANNELDATA_DRIVER_NAME              = 27
canCHANNELDATA_CHANNEL_QUALITY          = 28
canCHANNELDATA_ROUNDTRIP_TIME           = 29
canCHANNELDATA_BUS_TYPE                 = 30
canCHANNELDATA_DEVNAME_ASCII            = 31
canCHANNELDATA_TIME_SINCE_LAST_SEEN     = 32
canCHANNELDATA_REMOTE_OPERATIONAL_MODE  = 33
canCHANNELDATA_REMOTE_PROFILE_NAME      = 34
#The following flags can be returned from canRead()
canMSG_MASK                             = 0x00ff
canMSG_RTR                              = 0x0001
canMSG_STD                              = 0x0002
canMSG_EXT                              = 0x0004
canMSG_WAKEUP                           = 0x0008
canMSG_NERR                             = 0x0010
canMSG_ERROR_FRAME                      = 0x0020
canMSG_TXACK                            = 0x0040
canMSG_TXRQ                             = 0x0080
canMSGERR_MASK                          = 0xff00
canMSGERR_HW_OVERRUN                    = 0x0200
canMSGERR_SW_OVERRUN                    = 0x0400
canMSGERR_STUFF                         = 0x0800
canMSGERR_FORM                          = 0x1000
canMSGERR_CRC                           = 0x2000
canMSGERR_BIT0                          = 0x4000
canMSGERR_BIT1                          = 0x8000
canMSGERR_OVERRUN                       = 0x0600
canMSGERR_BIT                           = 0xC000
canMSGERR_BUSERR                        = 0xF800

canDRIVER_NORMAL                        = 4
canDRIVER_SILENT                        = 1
canDRIVER_SELFRECEPTION                 = 8
canDRIVER_OFF                           = 0

kvEVENT_TYPE_KEY                        = 1

kvSCRIPT_STOP_NORMAL                    = 0
kvSCRIPT_STOP_FORCED                    = -9

kvDEVICE_MODE_INTERFACE                 = 0
kvDEVICE_MODE_LOGGER                    = 1

class canError(Exception):
    def __init__(self, canlib, canERR):
        self.canlib = canlib
        self.canERR = canERR

    def __canGetErrorText(self):
        msg = create_string_buffer(80)
        self.canlib.dll.canGetErrorText(self.canERR, msg, sizeof(msg))
        return msg.value

    def __str__(self):
        return "[canError] %s: %s (%d)" % (self.canlib.fn, self.__canGetErrorText(), self.canERR)


class canNoMsg(Exception):
    def __init__(self, canlib, canERR):
        self.canlib = canlib
        self.canERR = canERR

    def __str__(self):
        return "No messages available"


class canVersion(Structure):
    _fields_ = [
        ("minor", c_uint8),
        ("major", c_uint8),
        ]

    def __str__(self):
        return "%d.%d" % (self.major, self.minor)


class bitrateSetting(object):
    def __init__(self, freq=1000000, tseg1=4, tseg2=3, sjw=1, nosamp=1, syncMode=0):
        self.freq     = freq
        self.tseg1    = tseg1
        self.tseg2    = tseg2
        self.sjw      = sjw
        self.nosamp   = nosamp
        self.syncMode = syncMode

    def __str__(self):
        txt  = "freq    : %8d\n" % self.freq
        txt += "tseg1   : %8d\n" % self.tseg1
        txt += "tseg2   : %8d\n" % self.tseg2
        txt += "sjw     : %8d\n" % self.sjw
        txt += "nosamp  : %8d\n" % self.nosamp
        txt += "syncMode: %8d\n" % self.syncMode
        return txt


#----------------------------------------------------------------------#
# Canlib class                                                         #
#----------------------------------------------------------------------#

class canlib(object):

    # definitions
    canMessage = 8 * c_uint8

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
            self.dll = WinDLL('canlib32')
            self.dll.canInitializeLibrary()
        else:
            self.dll = CDLL('libcanlib.so')

        # protptypes
        self.dll.canGetVersion.argtypes = []
        self.dll.canGetVersion.restype = c_short
        self.dll.canGetVersion.errchk = self._canErrorCheck

        self.dll.canGetNumberOfChannels.argtypes = [POINTER(c_int)]
        self.dll.canGetNumberOfChannels.errcheck = self._canErrorCheck

        self.dll.canGetChannelData.argtypes = [c_int, c_int, POINTER(None), c_size_t]
        self.dll.canGetChannelData.errcheck = self._canErrorCheck

        self.dll.canOpenChannel.argtypes = [c_int, c_int]
        self.dll.canOpenChannel.errcheck = self._canErrorCheck

        self.dll.canClose.argtypes = [c_int]
        self.dll.canClose.errcheck = self._canErrorCheck

        self.dll.canSetBusParams.argtypes = [c_int, c_long, c_uint,
                                             c_uint, c_uint, c_uint, c_uint]
        self.dll.canSetBusParams.errcheck = self._canErrorCheck

        self.dll.canGetBusParams.argtypes = [c_int, POINTER(c_long), POINTER(c_uint),
                                             POINTER(c_uint), POINTER(c_uint),
                                             POINTER(c_uint), POINTER(c_uint)]
        self.dll.canGetBusParams.errcheck = self._canErrorCheck

        self.dll.canBusOn.argtypes = [c_int]
        self.dll.canBusOn.errcheck = self._canErrorCheck

        self.dll.canBusOff.argtypes = [c_int]
        self.dll.canBusOff.errcheck = self._canErrorCheck

        self.dll.canTranslateBaud.argtypes = [POINTER(c_long),
                                              POINTER(c_uint),
                                              POINTER(c_uint),
                                              POINTER(c_uint),
                                              POINTER(c_uint),
                                              POINTER(c_uint)]
        self.dll.canTranslateBaud.errcheck = self._canErrorCheck

        self.dll.canWrite.argtypes = [c_int, c_long, POINTER(None), c_uint, c_uint]
        self.dll.canWrite.errcheck = self._canErrorCheck

        self.dll.canWriteWait.argtypes = [c_int, c_long, POINTER(None), c_uint, c_uint, c_ulong]
        self.dll.canWriteWait.errcheck = self._canErrorCheck

        self.dll.canReadWait.argtypes = [c_int, POINTER(c_long), POINTER(None),
                                         POINTER(c_uint), POINTER(c_uint),
                                         POINTER(c_ulong), c_ulong]
        self.dll.canReadWait.errcheck = self._canErrorCheck

        try:
            self.dll.canReadSpecificSkip.argtypes = [c_int, c_long, POINTER(None),
                                                     POINTER(c_uint), POINTER(c_uint),
                                                     POINTER(c_ulong)]
            self.dll.canReadSpecificSkip.errcheck = self._canErrorCheck
        
        except e:
            print ('Info:', e, '(Not implemented in Linux)')

        try:
            self.dll.canReadSyncSpecific.argtypes = [c_int, c_long, c_ulong]
            self.dll.canReadSyncSpecific.errcheck = self._canErrorCheck
        except  e:
            print ('Info:', e, '(Not implemented in Linux)')

        self.dll.canSetBusOutputControl.argtypes = [c_int, c_ulong]
        self.dll.canSetBusOutputControl.errcheck = self._canErrorCheck

        self.dll.canIoCtl.argtypes = [c_int, c_uint, POINTER(None), c_uint]
        self.dll.canIoCtl.errcheck = self._canErrorCheck

#        try:
#            self.dll.kvReadDeviceCustomerData.argtypes = [c_int, c_int, c_int, POINTER(None), c_size_t]
#            self.dll.kvReadDeviceCustomerData.errcheck = self._canErrorCheck
#
#            self.dll.kvScriptSendEvent.argtypes = [c_int, c_int, c_int, c_int, c_uint]
#            self.dll.kvScriptSendEvent.errcheck = self._canErrorCheck
#
#            self.dll.kvScriptStart.argtypes = [c_int, c_int]
#            self.dll.kvScriptStart.errcheck = self._canErrorCheck
#                        
#            self.dll.kvScriptStop.argtypes = [c_int, c_int, c_int] 
#            self.dll.kvScriptStop.errcheck = self._canErrorCheck
#                        
#            self.dll.kvScriptUnload.argtypes = [c_int, c_int] 
#            self.dll.kvScriptUnload.errcheck = self._canErrorCheck
#            
#            self.dll.kvScriptLoadFileOnDevice.argtypes = [c_int, c_int, c_char_p]
#            self.dll.kvScriptLoadFileOnDevice.errcheck = self._canErrorCheck
#            
#            self.dll.kvScriptLoadFile.argtypes = [c_int, c_int, c_char_p]
#            self.dll.kvScriptLoadFile.errcheck = self._canErrorCheck
#
#        except  kve:
#            print ('Info:', kve, '(Not implemented in Linux)')

#        self.dll.kvDeviceSetMode.argtypes = [c_int, c_int]
#        self.dll.kvDeviceSetMode.errcheck = self._canErrorCheck
#
#        self.dll.kvDeviceGetMode.argtypes = [c_int, POINTER(c_int)]
#        self.dll.kvDeviceGetMode.errcheck = self._canErrorCheck


    def __del__(self):
        self.dll.canUnloadLibrary()

    def _canErrorCheck(self, result, func, arguments):
        if result == canERR_NOMSG:
            raise canNoMsg(self, result)
        elif result < 0:
            raise canError(self, result)
        return result

    #------------------------------------------------------------------#
    # API                                                              #
    #------------------------------------------------------------------#

    def getVersion(self):
        """ This API call returns the version of the CANLIB API DLL 
        (canlib32.dll). The most significant byte is the major version
        number and the least significant byte is the minor version number """
        self.fn = inspect.stack()[0][3]
        v = self.dll.canGetVersion()
        version = canVersion(v & 0xff, v >> 8)
        return version

    def getNumberOfChannels(self):
        """This function returns the number of available CAN channels 
        in the computer. The virtual channels are included in this number."""
        self.fn = inspect.stack()[0][3]
        chanCount = c_int()
        self.dll.canGetNumberOfChannels(chanCount)
        return chanCount.value

    def getProductName(self, channel):
        ''' This function returns  the product name of the
            device as a zero-terminated ASCII string
        Parameters: 
        channel - 
         The number of the channel you are interested in. 
        Channel numbers are integers in the interval beginning at 0 (zero) 
        and ending at the value returned by canGetNumberOfChannels() minus 1.  
        return channel name ( for example: Kvaser Leaf Light HS)'''
        
        self.fn = inspect.stack()[0][3]
        name = create_string_buffer(80)
        '''returns  the product name of the
            device as a zero-terminated ASCII string'''
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_DEVDESCR_ASCII,
                                   byref(name), sizeof(name))
        return "%s" % name.value
    
    
    def getChannelNumber(self,channel):
        '''This function receives the channel number on the card.
        Parameters: 
        channel - 
         The number of the channel you are interested in. 
        Channel numbers are integers in the interval beginning at 0 (zero) 
        and ending at the value returned by canGetNumberOfChannels() minus 1.  
        return channel name ( for example: Kvaser Leaf Light HS)'''
        buf_type = c_uint * 1
        buf = buf_type()
        
        '''  receives the channel number on the card.'''
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_CHAN_NO_ON_CARD,
                                   byref(buf), sizeof(buf))
        return "(channel %d)" % (buf[0])
    
    def getChannelData_Name(self, channel):
        ''' This function returns  the product name of the
        device as a zero-terminated ASCII string
        Parameters: 
        channel - 
        The number of the channel you are interested in. 
        Channel numbers are integers in the interval beginning at 0 (zero) 
        and ending at the value returned by canGetNumberOfChannels() minus 1.  
        return channel name ( for example: Kvaser Leaf Light HS)'''
        
        self.fn = inspect.stack()[0][3]
        name = create_string_buffer(80)
        '''returns  the product name of the
            device as a zero-terminated ASCII string'''
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_DEVDESCR_ASCII,
                                   byref(name), sizeof(name))
        buf_type = c_uint * 1
        buf = buf_type()
        
        '''  receives the channel number on the card.'''
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_CHAN_NO_ON_CARD,
                                   byref(buf), sizeof(buf))
        return "%s (channel %d)" % (name.value,buf[0])
    

    def getChannelDataCardNumber(self, channel):
        '''This function returns the serial number of the card
         Parameters:
         channel  - 
        The number of the channel you are interested in. 
        Channel numbers are integers in the interval beginning at 0 (zero) 
        and ending at the value returned by canGetNumberOfChannels() minus 1.  
        return channel name
        '''
        self.fn = inspect.stack()[0][3]
        buf_type = c_ulong
        buf = buf_type()
        ''' This function can be used to retrieve certain 
        pieces of information about a channel.
        constant canCHANNELDATA_CARD_NUMBER receives the serial number of the card '''
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_CARD_NUMBER,
                                   byref(buf), sizeof(buf))
        return buf.value

    def getChannelData_EAN(self, channel):
        '''This function receives the UPC-Universal Product Code (EAN) number for the card
         If there is no UPC number, the buffer is filled with zeros. 
         The UPC (EAN) number is coded as a BCD string with the LSB first, 
         so e.g. 733-0130-00122-0 is coded as 0x30001220 0x00073301
        '''
        self.fn = inspect.stack()[0][3]
        buf_type = c_ulong * 2
        buf = buf_type()
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_CARD_UPC_NO,
                                   byref(buf), sizeof(buf))
        (ean_lo, ean_hi) = struct.unpack('LL', buf)

        return "%02x-%05x-%05x-%x" % (ean_hi >> 12,
                                      ((ean_hi & 0xfff) << 8) | (ean_lo >> 24),
                                      (ean_lo >> 4) & 0xfffff, ean_lo & 0xf)

    def getChannelData_EAN_short(self, channel):
        '''This function receives the UPC-Universal as getChannelData_EAN
        and returns in short format'''
        self.fn = inspect.stack()[0][3]
        buf_type = c_ulong * 2
        buf = buf_type()
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_CARD_UPC_NO,
                                   byref(buf), sizeof(buf))
        (ean_lo, ean_hi) = struct.unpack('LL', buf)
        return "%04x-%x" % ((ean_lo >> 4) & 0xffff, ean_lo & 0xf)


    def getChannelData_Serial(self, channel):
        '''This function receives the serial number of the card
        retunt serial low number'''
        self.fn = inspect.stack()[0][3]
        buf_type = c_ulong * 2
        buf = buf_type()
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_CARD_SERIAL_NO,
                                   byref(buf), sizeof(buf))
        (serial_lo, serial_hi) = struct.unpack('LL', buf)
        # serial_hi is always 0
        return serial_lo

    def getChannelData_DriverName(self, channel):
        '''This function  receives the name of the device driver (e.g. "kcans")  
        return driver name value'''
        self.fn = inspect.stack()[0][3]
        name = create_string_buffer(80)
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_DRIVER_NAME,
                                   byref(name), sizeof(name))
        return name.value


    def getChannelData_Firmware(self, channel):
        ''' function  receives the firmware revision number on the card
        return tuple(major minor build) '''
        self.fn = inspect.stack()[0][3]
        buf_type = c_ushort * 4
        buf = buf_type()
        self.dll.canGetChannelData(channel,
                                   canCHANNELDATA_CARD_FIRMWARE_REV,
                                   byref(buf), sizeof(buf))
        (build, release, minor, major) = struct.unpack('HHHH', buf)
        return (major, minor, build)

    def openChannel(self, channel, flags=0):
        '''Opens a CAN channel (circuit) and returns a handle which is used in subsequent calls to CANLIB.
        Channel numbering is dependent on the installed hardware. The first channel always has number 0.
        For example,
        If you have a single LAPcan, the channels are numbered 0 and 1. 
        If you have a USBcan Professional, the channels are numbered 0-1 according to the labels on the cables. 
        The virtual channels come after all physical channels
        Parameters:
        channel - The number of the channel. Channel numbering is hardware dependent
        flags  - A combination of canOPEN_xxx flags(for more information about flags for this function see canlib.h ) 
        
        Returns object of type canChannel of  opened circuit, or canERR_xxx (negative) if the call failed
        '''
        self.fn = inspect.stack()[0][3]
        return canChannel(self, channel, flags)

    def translateBaud(self, freq=1000000, tseg1=4, tseg2=3, sjw=1, nosamp=1, syncMode=0):
        '''This function translates the canBITRATE_xxx constants to their corresponding bus parameter values.
        At return, this freq contains the actual bit rate (in bits per second). TSeg1 is the number of quanta (less one)
        in a bit before the sampling point. TSeg2 is the number of quanta after the sampling point.
            Parameters:
        [in] freq is a value which contains the canBITRATE_xxx constant to translate  
        [in] tseg1 is a value of kvaser controller register ( btr1 ) which receives the Time segment 1, that is, the number of
            quanta from (but not including) the Sync Segment to the sampling point.  
        [in] tseg2 is a value  of kvaser controller register ( btr1 ) which receives the Time segment 2, that is, the number of
            quanta from the sampling point to the end of the bit.  
        [in] sjwis a value of kvaser controller register ( btr0 ) which receives the Synchronization Jump Width; can be 1,2,3, or 4.  
        [in] nosamp A pointer to a buffer which receives the number of sampling points; can be 1 or 3.  
        [in] syncMode Unsupported, always read as zero. 
        
         '''
        self.fn    = inspect.stack()[0][3]
        freq_p     = c_long(freq)
        tseg1_p    = c_int(tseg1)
        tseg2_p    = c_int(tseg2)
        sjw_p      = c_int(sjw)
        nosamp_p   = c_int(nosamp)
        syncMode_p = c_int(syncMode)
        self.dll.canTranslateBaud(byref(freq_p),
                                  byref(tseg1_p),
                                  byref(tseg2_p),
                                  byref(sjw_p),
                                  byref(nosamp_p),
                                  byref(syncMode_p))
        rateSetting = bitrateSetting(freq=freq_p.value, tseg1=tseg1_p.value, tseg2=tseg2_p.value,
                                     sjw=sjw_p.value, nosamp=nosamp_p.value, syncMode=syncMode_p.value)
        return rateSetting

    def unloadLibrary(self):
        self.dll.canUnloadLibrary()

    def reinitializeLibrary(self):
        self.dll.canUnloadLibrary()
        self.dll.canInitializeLibrary()


class canChannel(object):
    '''the class ussualy created in openChannel function of canlib object
    and handle opened circuit'''
    def __init__(self, canlib, channel, flags=0):
        self.canlib    = canlib
        self.dll       = canlib.dll
        self.index     = channel
        self.canlib.fn = 'openChannel'
        self.handle    = self.dll.canOpenChannel(channel, flags)

    def close(self):
        '''This function closes the channel associated with the handle.
        If no other threads are using the CAN circuit, it is taken off bus.
        The handle can not be used for further references to the channel,
        so any variable containing it should be zeroed'''
        self.canlib.fn = inspect.stack()[0][3]
        self.dll.canClose(self.handle)
        self.handle = -1

    def setBusParams(self, freq, tseg1=0, tseg2=0, sjw=0, noSamp=0, syncmode=0):
        '''This function sets the bus timing parameters for the specified CAN controller
        Parameters: 
    freq - Bit rate (measured in bits per second); or one of the predefined constants canBITRATE_xxx, which are described below.  
    tseg1 - Time segment 1, that is, the number of quanta from (but not including) the Sync Segment to the sampling point.  
    tseg2 - Time segment 2, that is, the number of quanta from the sampling point to the end of the bit.  
    sjw - The Synchronization Jump Width; can be 1,2,3, or 4.  
    noSamp - The number of sampling points; can be 1 or 3.  
    syncmode - Unsupported and ignored. 
    '''
        self.canlib.fn = inspect.stack()[0][3]
        self.dll.canSetBusParams(self.handle, freq, tseg1, tseg2, sjw,
                                 noSamp, syncmode)

    def getBusParams(self):
        ''' This function retrieves the current bus parameters for the specified channel
        Parameters:
[in] hnd An open handle to a CAN controller.  
[out] freq Bit rate (bits per second).  
[out] tseg1 Time segment 1, that is, the number of quanta from (but not including) the Sync Segment to the sampling point.  
[out] tseg2 Time segment 2, that is, the number of quanta from the sampling point to the end of the bit.  
[out] sjw The Synchronization Jump Width; can be 1,2,3, or 4.  
[out] noSamp The number of sampling points; can be 1 or 3.  
[out] syncmode Unsupported, always read as zero. 
'''
        self.canlib.fn = inspect.stack()[0][3]
        freq = c_long()
        tseg1 = c_uint()
        tseg2 = c_uint()
        sjw = c_uint()
        noSamp = c_uint()
        syncmode = c_uint()
        self.dll.canGetBusParams(self.handle, byref(freq), byref(tseg1),
                                 byref(tseg2), byref(sjw), byref(noSamp),
                                 byref(syncmode))
        return freq.value, tseg1.value, tseg2.value, sjw.value, noSamp.value, syncmode.value


    '''When the CAN controller is on bus, it is receiving messages and is sending
        acknowledge bits in response to all correctly received messages.
        A controller that is off bus is not taking part in the bus communication at all
    '''
    def busOn(self):
        ''' This function takes the specified channel on-bus
        If you are using multiple handles to the same physical channel,
        for example if you are writing a threaded application, 
        you must call canBusOn() once for each handle. 
        The same applies to canBusOff() - the physical channel will not go off
        bus until the last handle to the channel goes off bus.
        '''
        self.canlib.fn = inspect.stack()[0][3]
        self.dll.canBusOn(self.handle)

    def busOff(self):
        ''' This function takes the specified channel off-bus.'''
        self.canlib.fn = inspect.stack()[0][3]
        self.dll.canBusOff(self.handle)

    def write(self, id, msg, flag=0):
        '''This function sends a CAN message. The call returns immediately 
        after queuing the message to the driver.
        If you are using the same channel via multiple handles, 
        note that the default behaviour is that the different handles will
        "hear" each other just as if each handle referred to a channel of its own.
        If you open, say, channel 0 from thread A and thread B and then send
        a message from thread A, it will be "received" by thread B.
        This behaviour can be changed using canIOCTL_SET_LOCAL_TXECHO.
        '''
        self.canlib.fn = inspect.stack()[0][3]
        data = (c_ubyte * len(msg))(*msg)
        self.dll.canWrite(self.handle, id, byref(data), len(msg), flag)

    def writeWait(self, id, msg, flag=0, timeout=0):
        '''This function sends a CAN message. It returns when the message is sent, or the timeout expires
        If you are using the same channel via multiple handles, 
        note that the default behaviour is that the different handles
        will "hear" each other just as if each handle referred to a channel of its own.
        If you open, say, channel 0 from thread A and thread B and then send a message
        from thread A, it will be "received" by thread B. This behaviour can be 
        changed using canIOCTL_SET_LOCAL_TXECHO.
        '''
        self.canlib.fn = inspect.stack()[0][3]
        data = (c_ubyte * len(msg))(*msg)
        self.dll.canWriteWait(self.handle, id, byref(data), len(msg), flag, timeout)

    def read(self, timeout=0):
        '''Reads a message from the receive buffer. If no message is available,
        the function returns immediately with return code canERR_NOMSG
        If you are using the same channel via multiple handles,
        note that the default behaviour is that the different handles
        will "hear" each other just as if each handle referred to a channel of its own.
        If you open, say, channel 0 from thread A and thread B and then send
        a message from thread A, it will be "received" by thread B.
        This behaviour can be changed using canIOCTL_SET_LOCAL_TXECHO.'''
        self.canlib.fn = inspect.stack()[0][3]
        msg = self.canlib.canMessage()
        id = c_long()
        dlc = c_uint()
        flag = c_uint()
        time = c_ulong()
       # .canReadWait the function from canlib dll for more information see Kvaser CanLib
        self.dll.canReadWait(self.handle, byref(id), byref(msg), byref(dlc),
                             byref(flag), byref(time), timeout)
        msgList = [msg[i] for i in range(len(msg))]
        return id.value, msgList[:dlc.value], dlc.value, flag.value, time.value

#    def readDeviceCustomerData(self, userNumber=100, itemNumber=0):
#        
#        self.fn = inspect.stack()[0][3]
#        buf_type = c_uint8 * 8
#        buf = buf_type()
#        user = c_int(userNumber)
#        item = c_int(itemNumber)
#        self.dll.kvReadDeviceCustomerData(self.handle, user, item, byref(buf), sizeof(buf))
#        return struct.unpack('!Q', buf)[0]

    def readSpecificSkip(self, id, timeout=0):
        '''Reads a message with a specified identifier from the receive buffer.
        Any preceding message not matching the specified identifier will be 
        removed in the receive buffer. If no message with the specified 
        identifier is available, the function returns immediately with an error code.
        Parameters:
       
        [out] id The desired CAN identifier.  
        [out] dlc Pointer to a buffer which receives the message length.  
        [out] flag Pointer to a buffer which receives the message flags,
        which is a combination of the canMSG_xxx and canMSGERR_xxx values.  
        [out] time Pointer to a buffer which receives the message time stamp. 

        '''
        self.canlib.fn = inspect.stack()[0][3]
        msg = self.canlib.canMessage()
        id = c_long(id)
        dlc = c_uint()
        flag = c_uint()
        time = c_ulong(timeout)
        self.dll.canReadSpecificSkip(self.handle, id, byref(msg), byref(dlc),
                                     byref(flag), byref(time))
        msgList = [msg[i] for i in range(len(msg))]
        return id.value, msgList[:dlc.value], dlc.value, flag.value, time.value

    def readSyncSpecific(self, id, timeout=0):
        '''Reads a message with a specified identifier from the receive buffer.
        Any preceding message not matching the specified identifier will be kept
        in the receive buffer. If no message with the specified identifier is available,
        the function returns immediately with an error code.'''
        self.canlib.fn = inspect.stack()[0][3]
        id = c_long(id)
        self.dll.canReadSyncSpecific(self.handle, id, timeout)

#    def scriptSendEvent(self, slotNo=0, eventType=kvEVENT_TYPE_KEY, eventNo=ord('a'), data=0):
#        self.canlib.fn = inspect.stack()[0][3]
#        self.dll.kvScriptSendEvent(self.handle, c_int(slotNo), c_int(eventType),
#                                   c_int(eventNo), c_uint(data))

    def setBusOutputControl(self, drivertype=canDRIVER_NORMAL):
        '''This function sets the driver type for a CAN controller.
        This corresponds loosely to the bus output control register
        in the CAN controller, hence the name of this function. 
        CANLIB does not allow for direct manipulation of the bus 
        output control register; instead, symbolic constants 
        are used to select the desired driver type.
        '''

        self.canlib.fn = inspect.stack()[0][3]
        self.dll.canSetBusOutputControl(self.handle, drivertype)

    def ioCtl_flush_rx_buffer(self):
        '''
        This API call performs several different functions;
        these are described below. The functions are handle-specific 
        unless otherwise noted; this means that they affect only the
        handle you pass to canIoCtl(), whereas other open handles will 
        remain unaffected. The contents of buf after the call is dependent
        on the function code you specified.
        '''
        self.canlib.fn = inspect.stack()[0][3]
        self.dll.canIoCtl(self.handle, canIOCTL_FLUSH_RX_BUFFER, None, 0)

    def getChannelData_Name(self):
        '''This function returns  the product name of the
        device as a zero-terminated ASCII string'''
        self.canlib.fn = inspect.stack()[0][3]
        return self.canlib.getChannelData_Name(self.index)

    def getChannelData_CardNumber(self):
        '''This function returns the serial number of the card'''
        self.canlib.fn = inspect.stack()[0][3]
        return self.canlib.getChannelData_CardNumber(self.index)

    def getChannelData_EAN(self):
        '''This function receives the UPC-Universal Product Code (EAN)'''
        self.canlib.fn = inspect.stack()[0][3]
        return self.canlib.getChannelData_EAN(self.index)

    def getChannelData_EAN_short(self):
        '''This function receives the UPC-Universal Product Code (EAN) 
        and returns  LSB'''
        self.canlib.fn = inspect.stack()[0][3]
        return self.canlib.getChannelData_EAN_short(self.index)

    def getChannelData_Serial(self):
        '''This function receives the serial number of the card
        retunt serial low number (see getChannelData_Serial in canlib) '''
        self.canlib.fn = inspect.stack()[0][3]
        return self.canlib.getChannelData_Serial(self.index)

    def getChannelData_DriverName(self):
        '''This function  receives the name of the device driver (e.g. "kcans")  
        return driver name value'''
        self.canlib.fn = inspect.stack()[0][3]
        return self.canlib.getChannelData_DriverName(self.index)

    def getChannelData_Firmware(self):
        '''function  receives the firmware revision number on the card
        return tuple(major minor build)'''
        self.canlib.fn = inspect.stack()[0][3]
        return self.canlib.getChannelData_Firmware(self.index)
    
#    def scriptStart(self, slot):
#        self.dll.kvScriptStart(self.handle, slot)
#        
#    def scriptStop(self, slot, mode):
#        self.dll.kvScriptStop(self.handle, slot, mode)
#
#    def scriptUnload(self, slot):
#        self.dll.kvScriptUnload(self.handle, slot)
#
#    def scriptLoadFileOnDevice(self, slot, localFile):
#        self.dll.kvScriptLoadFileOnDevice(self.handle, slot, c_char_p(localFile))
#
#    def scriptLoadFile(self, slot, filePathOnPC):
#        self.dll.kvScriptLoadFile(self.handle, slot, c_char_p(filePathOnPC))
#
#    def kvDeviceSetMode(self, mode):
#        self.canlib.fn = inspect.stack()[0][3]
#        self.dll.kvDeviceSetMode(self.handle, c_int(mode))
#
#    def kvDeviceGetMode(self):
#        self.canlib.fn = inspect.stack()[0][3]
#        mode = c_int()
#        self.dll.kvDeviceGetMode(self.handle, byref(mode))
#        return mode.value

if __name__ == '__main__':
    
    cl = canlib()
   
    channels = cl.getNumberOfChannels()

    print ("canlib version: %s" % cl.getVersion())
    print ("canlib channels: %d" % channels)
    chlist=[None,None]
    if len(sys.argv) != 2:
        print ("Please enter channel, example: %s 3\n" % sys.argv[0])
        for ch in range(0, channels):
            try:
                print ("%d.   %s %s (%s / %s)" % (ch,cl.getProductName(ch), cl.getChannelNumber(ch),cl.getChannelData_EAN(ch),cl.getChannelData_Serial(ch)))
            except (canError) as ex:
                print (ex)
        #sys.exit()
# assign  first channel form command prompt
    #ch = int(sys.argv[1])
    #if ch >= channels:
    #    print ("Invalid channel number")
    #    sys.exit()
#   open channel 
    
            try:
                ch1 = cl.openChannel(ch, canOPEN_ACCEPT_VIRTUAL)
                print ("Using channel: %s, EAN: %s" % (ch1.getChannelData_Name(), ch1.getChannelData_EAN()))
                cl.translateBaud()
                ch1.setBusOutputControl(canDRIVER_NORMAL)
                ch1.setBusParams(canBITRATE_1M)
                ch1.busOn()
                chlist[ch]=ch1
            except (canError) as ex:
                print (ex)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
####    create channel object and get its information 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #for i in range(128):
    ch1 = chlist[1]
    ch = chlist[0]
    ch.write(0, (45,57,58,66,78,45,78,85)) 
    time.sleep(1)
    try:
        while True:
            try:
                id, msg, dlc, flg, time = ch1.read()
                print ("%9d  %9d  0x%02x  %d  %s" % (id, time, flg, dlc, msg))
                for i in range(dlc):
                    msg[i] = (msg[i]+1) % 256
                ch.write(id, msg, flg)
            except (canNoMsg) as ex:
                print (ex.canERR,ex)
            except (canError) as ex:
                print (ex)

    finally:

            ch1.busOff()
            ch1.close()



