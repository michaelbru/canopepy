'''
Canopen Exceptions
--------------------

Custom exceptions to be used in the Canopen code.
'''


class CanopenException(Exception):
    ''' Base modbus exception '''

    def __init__(self, string):
        ''' Initialize the exception

        :param string: The message to append to the error
        '''
        self.string = string

    def __str__(self):
        return 'Canopen Error: %s' % self.string


class CanopenIOException(CanopenException):
    ''' Error resulting from data i/o '''

    def __init__(self, string=""):
        ''' Initialize the exception

        :param string: The message to append to the error
        '''
        message = "[Input/Output] %s" % string
        CanopenException.__init__(self, message)


class ParameterException(CanopenException):
    ''' Error resulting from invalid paramater '''

    def __init__(self, string=""):
        ''' Initialize the exception

        :param string: The message to append to the error
        '''
        message = "[Invalid Paramter] %s" % string
        CanopenException.__init__(self, message)


class NoSuchSlaveException(CanopenException):
    ''' Error resulting from making a request to a slave
    that does not exist '''

    def __init__(self, string=""):
        ''' Initialize the exception

        :param string: The message to append to the error
        '''
        message = "[No Such Slave] %s" % string
        CanopenException.__init__(self, message)


class NotImplementedException(CanopenException):
    ''' Error resulting from not implemented function '''

    def __init__(self, string=""):
        ''' Initialize the exception

        :param string: The message to append to the error
        '''
        message = "[Not Implemented] %s" % string
        CanopenException.__init__(self, message)


class ConnectionException(CanopenException):
    ''' Error resulting from a bad connection '''

    def __init__(self, string=""):
        ''' Initialize the exception

        :param string: The message to append to the error
        '''
        message = "[Connection] %s" % string
        CanopenException.__init__(self, message)


#---------------------------------------------------------------------------#
# Exported symbols
#---------------------------------------------------------------------------#
__all__ = [
    "CanopenException", "CanopenIOException",
    "ParameterException", "NotImplementedException",
    "ConnectionException", "NoSuchSlaveException",
]
