'''
Constants For Canopen Server/Client
----------------------------------

This is the single location for storing default
values for the servers and clients.
'''
from interfaces import Singleton



'''Abort code dictionary'''   
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
#
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


class Defaults(Singleton):
    ''' A collection of canopen default values   

  
        
    .. attribute:: Timeout

       The default amount of time a client should wait for a request
       to be processed (0.02 seconds)

   
    .. attribute:: Baudrate

       The speed at which the data is transmitted over the line.
       This defaults to 1000000.

    '''
  
 
    Timeout             = 0.02
    Baudrate            = 1000000
    Bytesize            = 8
   

    CanIds={'NMT Service':(0x0,'From NMT Master'),
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


class Structs(Singleton):
    ''' An enumeration representing the various byte endianess.

    .. attribute:: Auto

       This indicates that the byte order is chosen by the
       current native environment.

    .. attribute:: Big

       This indicates that the bytes are in little endian format

    .. attribute:: Little

       This indicates that the bytes are in big endian format

    .. note:: I am simply borrowing the format strings from the
       python struct module for my convenience.
    '''
    Auto   = '@'
    Big    = '>'
    Little = '<'

    TypeLength = {'integer8': (1,True,'b') , 
                  'integer16':  (2,True,'<h') ,
                  'integer32':  (4,True,'<l') , 
                  'unsigned8' :  (1,False,'B') , 
                  'unsigned16': (2,False,'<H') , 
                  'unsigned32': (4,False,'<L') ,
                  'vis string': (-1,False,'B')} 


#---------------------------------------------------------------------------#
# Exported Identifiers
#---------------------------------------------------------------------------#
__all__ = [
    "Defaults", "Structs"
]
