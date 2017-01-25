'''
Contains base classes for Canopen request/response/error packets
'''
from interfaces import Singleton
from exceptions import NotImplementedException
from constants import Defaults

#---------------------------------------------------------------------------#
# Logging
#---------------------------------------------------------------------------#
import logging
_logger = logging.getLogger(__name__)


#---------------------------------------------------------------------------#
# Base PDU's
#---------------------------------------------------------------------------#
class CanopenPDU(object):
    '''
    Base class for all Canopen mesages

    .. attribute:: can_id
     
       This value is used to uniquely identify a request or
       response message. 

 
    .. attribute:: skip_encode

       This is used when the message payload has already been encoded.
       Generally this will occur when the PayloadBuilder is being used
       to create a complicated message. By setting this to True, the
       request will pass the currently encoded message through instead
       of encoding it again.
    '''

    def __init__(self, **kwargs):
        ''' Initializes the base data for a Canopen request '''
       #self.can_id = kwargs.get('canId', Defaults.)
     
        self.skip_encode = kwargs.get('skip_encode', False)
       

    def encode(self):
        ''' Encodes the message

        :raises: A not implemented exception
        '''
        raise NotImplementedException()

    def decode(self, data):
        ''' Decodes data part of the message.

        :param data: is a string object
        :raises: A not implemented exception
        '''
        raise NotImplementedException()

 

class CanopenRequest(CanopenPDU):
    ''' Base class for a Canopen request PDU '''

    def __init__(self, **kwargs):
        ''' Proxy to the lower level initializer '''
        CanopenPDU.__init__(self, **kwargs)

    def doException(self, exception):
        ''' Builds an error response based on the function

        :param exception: The exception to return
        :raises: An exception response
        '''
        _logger.error("Exception Response F(%d) E(%d)" %
                (self.function_code, exception))
        return ExceptionResponse(self.function_code, exception)


class CanopenResponse(CanopenPDU):
    ''' Base class for a Canopen response PDU

    .. attribute:: _rtu_frame_size

       Indicates the size of the Canopen rtu response used for
       calculating how much to read.
    '''

   
    def __init__(self, **kwargs):
        ''' Proxy to the lower level initializer '''
        CanopenPDU.__init__(self, **kwargs)


    def doException(self, exception):
        ''' Builds an error response based on the function

        :param exception: The exception to return
        :raises: An exception response
        '''
        _logger.error("Exception Response F(%d) E(%d)" %
                (self.function_code, exception))
        return ExceptionResponse(self.function_code, exception)

#---------------------------------------------------------------------------#
# Exception PDU's
#---------------------------------------------------------------------------#
class CanopenExceptions(Singleton):
    '''
    An enumeration of the valid Canopen exceptions
    '''

    @classmethod
    def decode(cls, code):
        ''' Given an error code, translate it to a
        string error name. 
        
        :param code: The code number to translate
        '''
        values = dict((v, k) for k, v in cls.__dict__.iteritems()
            if not k.startswith('__') and not callable(v))
        return values.get(code, None)


class ExceptionResponse(CanopenResponse):
    ''' Base class for a  c anopen exception PDU '''
    ExceptionOffset = 0x80
    _rtu_frame_size = 5

    def __init__(self, function_code, exception_code=None, **kwargs):
        ''' Initializes the Canopen exception response

        :param function_code: The function to build an exception response for
        :param exception_code: The specific Canopen exception to return
        '''
        CanopenResponse.__init__(self, **kwargs)
        self.original_code = function_code
        self.function_code = function_code | self.ExceptionOffset
        self.exception_code = exception_code

    def encode(self):
        ''' Encodes a Canopen exception response

        :returns: The encoded exception packet
        '''
        return chr(self.exception_code)

    def decode(self, data):
        ''' Decodes a Canopen exception response

        :param data: The packet data to decode
        '''
        self.exception_code = ord(data[0])

    def __str__(self):
        ''' Builds a representation of an exception response

        :returns: The string representation of an exception response
        '''
        message = CanopenExceptions.decode(self.exception_code)
        parameters = (self.function_code, self.original_code, message)
        return "Exception Response(%d, %d, %s)" % parameters


class IllegalFunctionRequest(CanopenRequest):
    '''
    Defines the Canopen slave exception type 'Illegal Function'
    This exception code is returned if the slave::

        - does not implement the function code **or**
        - is not in a state that allows it to process the function
    '''
    ErrorCode = 1

    def __init__(self, function_code, **kwargs):
        ''' Initializes a IllegalFunctionRequest

        :param function_code: The function we are erroring on
        '''
        CanopenRequest.__init__(self, **kwargs)
        self.function_code = function_code

    def decode(self, data):
        ''' This is here so this failure will run correctly

        :param data: Not used
        '''
        pass

    def execute(self, context):
        ''' Builds an illegal function request error response

        :param context: The current context for the message
        :returns: The error response packet
        '''
        return ExceptionResponse(self.function_code, self.ErrorCode)

#---------------------------------------------------------------------------#
# Exported symbols
#---------------------------------------------------------------------------#
__all__ = [
    'CanopenRequest', 'CanopenResponse', 'CanopenExceptions',
    'ExceptionResponse', 'IllegalFunctionRequest',
]
