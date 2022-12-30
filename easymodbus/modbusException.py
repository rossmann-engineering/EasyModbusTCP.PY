'''
Created on 14.09.2016

@author: Stefan Rossmann
'''


class ModbusException(Exception):
    '''
    classdocs
    '''

    def __init__(self, message):
        """ Exception to be thrown if Modbus Server returns error code "Function Code not executed (0x04)"
        Attributes:
            message -- explanation of the error
        """
        self.message = message

class TimeoutError(ModbusException):
    '''
    classdocs
    '''

    def __init__(self, message):
        """ Exception to be thrown if read times out
        Attributes:
            message -- explanation of the error
        """
        self.message = message


class SerialPortNotOpenedException(ModbusException):
    '''
    classdocs
    '''

    def __init__(self, message):
        """ Exception to be thrown if serial port is not opened
        Attributes:
            message -- explanation of the error
        """
        self.message = message


class ConnectionException(ModbusException):
    '''
    classdocs
    '''

    def __init__(self, message):
        """ Exception to be thrown if Connection to Modbus device failed
        Attributes:
            message -- explanation of the error
        """
        self.message = message


class FunctionCodeNotSupportedException(ModbusException):
    '''
    classdocs
    '''

    def __init__(self, message):
        """ Exception to be thrown if Modbus Server returns error code "Function code not supported"
        Attributes:
            message -- explanation of the error
        """
        self.message = message


class QuantityInvalidException(ModbusException):
    '''
    classdocs
    '''

    def __init__(self, message):
        """ Exception to be thrown if Modbus Server returns error code "quantity invalid"
        Attributes:
            message -- explanation of the error
        """
        self.message = message


class StartingAddressInvalidException(ModbusException):
    '''
    classdocs
    '''

    def __init__(self, message):
        """ Exception to be thrown if Modbus Server returns error code "starting adddress and quantity invalid"
        Attributes:
            message -- explanation of the error
        """
        self.message = message


class CRCCheckFailedException(ModbusException):
    '''
    classdocs
    '''

    def __init__(self, message):
        """ Exception to be thrown if CRC Check failed
        Attributes:
            message -- explanation of the error
        """
        self.message = message
