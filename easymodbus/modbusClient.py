'''
Created on 12.09.2016

@author: Stefan Rossmann
'''
import importlib
import socket
import struct
import threading
import logging
from datetime import time
from logging.handlers import RotatingFileHandler
import math
from modbus_protocol import *


class ModbusClient(object):
    """
    Implementation of a Modbus TCP Client and a Modbus RTU Master
    """
    def __init__(self, *params):
        """
        Constructor for Modbus RTU (serial line):
        modbusClient = ModbusClient.ModbusClient('COM1')
        First Parameter is the serial Port 
        
        Constructor for Modbus TCP:
        modbusClient = ModbusClient.ModbusClient('127.0.0.1', 502)
        First Parameter ist the IP-Address of the Server to connect to
        Second Parameter is the Port the Server listens to
        """
        self.__adu = ADU()
        self.__receivedata = bytearray()
        self.__transactionIdentifier = 0
        self.__unitIdentifier = 1
        self.__timeout = 5
        self.__ser = None
        self.__tcpClientSocket = None
        self.__connected = False
        self.__logging_level = logging.INFO
        # Constructor for RTU
        if len(params) == 1 & isinstance(params[0], str):
            serial = importlib.import_module("serial")
            self.serialPort = params[0]
            self.__baudrate = 9600
            self.__parity = Parity.even
            self.__stopbits = Stopbits.one
            self.__transactionIdentifier = 0
            self.__ser = serial.Serial()

        # Constructor for TCP
        elif (len(params) == 2) & isinstance(params[0], str) & isinstance(params[1], int):
            self.__tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__ipAddress = params[0]
            self.__port = params[1]
        else:
            raise AttributeError ('Argument must be "str" for Modbus-RTU mode, or "str, int" for Modbus-TCP')
        logging.debug("Modbus client class initialized")

    def connect(self):
        """
        Connects to a Modbus-TCP Server or a Modbus-RTU Slave with the given Parameters
        """
        if self.__ser is not None:
            serial = importlib.import_module("serial")
            if self.__stopbits == 0:
                self.__ser.stopbits = serial.STOPBITS_ONE
            elif self.__stopbits == 1:
                self.__ser.stopbits = serial.STOPBITS_TWO
            elif self.__stopbits == 2:
                self.__ser.stopbits = serial.STOPBITS_ONE_POINT_FIVE
            if self.__parity == 0:
                self.__ser.parity = serial.PARITY_EVEN
            elif self.__parity == 1:
                self.__ser.parity = serial.PARITY_ODD
            elif self.__parity == 2:
                self.__ser.parity = serial.PARITY_NONE

            self.__ser = serial.Serial(self.serialPort, self.__baudrate, timeout=self.__timeout,
                                       parity=self.__ser.parity, stopbits=self.__ser.stopbits, xonxoff=0, rtscts=0)
            self.__ser.writeTimeout = self.__timeout

            logging.info(
                "Modbus client connected to serial network, Port: {0}, Baudrate: {1}, Parity: {2}, Stopbits: {3}"
                .format(str(self.serialPort), str(self.__baudrate), str(self.__parity), str(self.__stopbits)))

        # print (self.ser)
        if self.__tcpClientSocket is not None:
            self.__tcpClientSocket.settimeout(5)
            self.__tcpClientSocket.connect((self.__ipAddress, self.__port))

            self.__connected = True
            self.__thread = threading.Thread(target=self.__listen, args=())
            self.__thread.start()
            logging.info(
                "Modbus client connected to TCP network, IP Address: {0}, Port: {1}"
                .format(str(self.__ipAddress), str(self.__port)))

    def __listen(self):
        self.__stoplistening = False
        self.__receivedata = bytearray()
        try:
            while not self.__stoplistening:
                if len(self.__receivedata) == 0:
                    self.__receivedata = bytearray()
                    self.__timeout = 500
                    if self.__tcpClientSocket is not None:
                        self.__receivedata = self.__tcpClientSocket.recv(256)
        except socket.timeout:
            self.__receivedata = None

    def close(self):
        """
        Closes Serial port, or TCP-Socket connection
        """
        if self.__ser is not None:
            self.__ser.close()
        if self.__tcpClientSocket is not None:
            self.__stoplistening = True
            self.__tcpClientSocket.shutdown(socket.SHUT_RDWR)
            self.__tcpClientSocket.close()
        self.__connected = False
        logging.info("Modbus client connection closed")

    def read_discreteinputs(self, starting_address, quantity):
        """
        Only there for compatibility reasons with older versions - read_discrete_inputs should be used instead
        """
        return self.read_discrete_inputs(starting_address, quantity)

    def read_discrete_inputs(self, starting_address, quantity):
        """
        Read Discrete Inputs from Master device (Function code 2)
        starting_address: First discrete input to be read
        quantity: Number of discrete Inputs to be read
        returns: Boolean Array [0..quantity-1] which contains the discrete Inputs
        """
        logging.info("Request to read discrete inputs (FC02), starting address: {0}, quantity: {1}"
                     .format(str(starting_address), str(quantity)))
        return_value = self.execute_read_order(starting_address, quantity, FunctionCode.READ_DISCRETE_INPUTS)
        logging.info("Response to read discrete inputs (FC02), values: {0}"
                     .format(str(return_value)))
        return return_value

    def read_coils(self, starting_address, quantity):
        """
        Read Coils from Master device (Function code 1)
        starting_address:  First coil to be read
        quantity: Number of coils to be read
        returns:  Boolean Array [0..quantity-1] which contains the coils
        """
        logging.info("Request to read coils (FC01), starting address: {0}, quantity: {1}"
                     .format(str(starting_address), str(quantity)))
        return_value = self.execute_read_order(starting_address, quantity, FunctionCode.READ_COILS)
        logging.info("Response to read coils (FC01), values: {0}"
                     .format(str(return_value)))
        return return_value

    def read_holdingregisters(self, starting_address, quantity):
        """
        Only there for compatibility reasons with older versions - read_holding_registers should be used instead
        """
        return self.read_holding_registers(starting_address, quantity)

    def read_holding_registers(self, starting_address, quantity):
        """
        Read Holding Registers from Master device (Function code 3)
        starting_address: First holding register to be read
        quantity:  Number of holding registers to be read
        returns:  Int Array [0..quantity-1] which contains the holding registers
        """
        logging.info("Request to read Holding Registers (FC03), starting address: {0}, quantity: {1}"
                     .format(str(starting_address), str(quantity)))
        return_value = self.execute_read_order(starting_address, quantity, FunctionCode.READ_HOLDING_REGISTERS)
        logging.info("Response to Holding Registers (FC03), values: {0}"
                     .format(str(return_value)))
        return return_value

    def read_inputregisters(self, starting_address, quantity):
        """
        Only there for compatibility reasons with older versions - read_input_registers should be used instead
        """
        return self.read_input_registers(starting_address, quantity)

    def read_input_registers(self, starting_address, quantity):
        """
        Read Input Registers from Master device (Function code 4)
        starting_address :  First input register to be read
        quantity:  Number of input registers to be read
        returns:  Int Array [0..quantity-1] which contains the input registers
        """
        logging.info("Request to read Input Registers (FC04), starting address: {0}, quantity: {1}"
                     .format(str(starting_address), str(quantity)))
        return_value = self.read_analogs(starting_address, quantity, FunctionCode.READ_INPUT_REGISTERS)
        logging.info("Response to Input Registers (FC04), values: {0}"
                     .format(str(return_value)))
        return return_value

    def execute_read_order(self, starting_address, quantity=0, function_code: FunctionCode=FunctionCode.READ_COILS, values=None):
        """
        Read digital values from Master device (Function code 2, Function code 1, Function code 3, Function code 4)
        starting_address: First value input to be read
        quantity: Number of values to be read
        returns:  Array [0..quantity-1] which contains the  values
        """
        self.__adu.mbap_header.transaction_identifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        # Raise Exception for Digitals
        if ((starting_address > 65535) | (quantity > 2000)) & ((
            function_code == FunctionCode.READ_COILS) | (
            function_code == FunctionCode.READ_DISCRETE_INPUTS)):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 2000")
        # Raise Exception for Analogs
        if ((starting_address > 65535) | (quantity > 125)) & ((
            function_code == FunctionCode.READ_HOLDING_REGISTERS) | (
            function_code == FunctionCode.READ_INPUT_REGISTERS)):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 125")
        self.__adu.pdu.function_code = function_code
        self.__adu.mbap_header.length = 6
        self.__adu.mbap_header.unit_identifier = self.unitidentifier
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        if (function_code == FunctionCode.READ_COILS) | (
                function_code == FunctionCode.READ_DISCRETE_INPUTS) | (
                function_code == FunctionCode.READ_INPUT_REGISTERS) | (
                function_code == FunctionCode.READ_HOLDING_REGISTERS):
            quantity_lsb = quantity & 0xFF
            quantity_msb = (quantity & 0xFF00) >> 8
            self.__adu.pdu.data = bytearray(
                [starting_address_msb, starting_address_lsb, quantity_msb,
                 quantity_lsb])
        elif function_code == FunctionCode.WRITE_SINGLE_COIL:
            if values:
                value_lsb = 0x00
                value_msb = 0xFF00 >> 8
            else:
                value_lsb = 0x00
                value_msb = 0x00 >> 8
            self.__adu.pdu.data = bytearray(
                [starting_address_msb, starting_address_lsb, value_msb,
                 value_lsb])
        elif function_code == FunctionCode.WRITE_SINGLE_REGISTER:
            value_lsb = values & 0xFF
            value_msb = (values & 0xFF00) >> 8
            self.__adu.pdu.data = bytearray(
                [starting_address_msb, starting_address_lsb, value_msb,
                 value_lsb])
        elif function_code == FunctionCode.WRITE_MULTIPLE_COILS:
            quantity_lsb = len(values) & 0xFF
            quantity_msb = (len(values) & 0xFF00) >> 8
            value_to_write = list()
            single_coil_value = 0
            for i in range(0, len(values)):
                if (i % 8) == 0:
                    if i > 0:
                        value_to_write.append(single_coil_value)
                    single_coil_value = 0

                if values[i]:
                    coil_value = 1
                else:
                    coil_value = 0
                single_coil_value = (coil_value << (i % 8) | single_coil_value)

            value_to_write.append(single_coil_value)
            self.__adu.pdu.data = bytearray(
                [starting_address_msb, starting_address_lsb, quantity_msb,
                 quantity_lsb])
            self.__adu.pdu.data.append(len(value_to_write))  # Bytecount
            for i in range(0, len(value_to_write)):
                self.__adu.pdu.data.append(value_to_write[i] & 0xFF)
        elif function_code == FunctionCode.WRITE_MULTIPLE_REGISTERS:
            quantity_lsb = len(values) & 0xFF
            quantity_msb = (len(values) & 0xFF00) >> 8
            value_to_write = list()
            for i in range(0, len(values)):
                value_to_write.append(values[i])
            self.__adu.pdu.data = bytearray(
                [starting_address_msb, starting_address_lsb, quantity_msb,
                 quantity_lsb])
            self.__adu.pdu.data.append(len(value_to_write) * 2)  # Bytecount
            for i in range(0, len(value_to_write)):
                self.__adu.pdu.data.append((value_to_write[i] & 0xFF00) >> 8)
                self.__adu.pdu.data.append(value_to_write[i] & 0xFF)

        if self.__ser is not None:
            self.__ser.write(self.__adu.encode(ModbusType.RTU))
            if (function_code == FunctionCode.READ_COILS) | (function_code == FunctionCode.READ_DISCRETE_INPUTS):
                if quantity % 8 != 0:
                    bytes_to_read = 6 + int(quantity / 8)
                else:
                    bytes_to_read = 5 + int(quantity / 8)
            elif (function_code == FunctionCode.READ_HOLDING_REGISTERS) | (
                    function_code == FunctionCode.READ_INPUT_REGISTERS):
                bytes_to_read = 5 + int(quantity * 2)
            else:
                bytes_to_read = 8
            data = self.__ser.read(bytes_to_read)
            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError('Read timeout Exception')
            self.__adu.decode(ModbusType.RTU, bytearray(data))
        else:
            self.__tcpClientSocket.send(self.__adu.encode(modbus_type=ModbusType.TCP))
            self.__receivedata = bytearray()
            try:
                while len(self.__receivedata) == 0:
                    time.sleep(0.001)
            except Exception:
                raise Exception('Read Timeout')
            self.__adu.decode(ModbusType.TCP, bytearray(self.__receivedata))
        if (function_code == FunctionCode.READ_COILS) | (
                function_code == FunctionCode.READ_DISCRETE_INPUTS) | (
                function_code == FunctionCode.READ_INPUT_REGISTERS) | (
                function_code == FunctionCode.READ_HOLDING_REGISTERS):
            return_value = list()

            for i in range(0, quantity):
                if (function_code == FunctionCode.READ_COILS) | (
                        function_code == FunctionCode.READ_DISCRETE_INPUTS):
                    return_value.append(bool((self.__adu.pdu.data[int(i / 8) + 1] >> int(i % 8)) & 0x1))
                elif (function_code == FunctionCode.READ_HOLDING_REGISTERS) | (
                            function_code == FunctionCode.READ_INPUT_REGISTERS):
                    return_value.append((self.__adu.pdu.data[i * 2 + 1] << 8) + self.__adu.pdu.data[i * 2 + 2])
            return return_value
        else:
            return True


    def write_single_coil(self, starting_address, value):
        """
        Write single Coil to Master device (Function code 5)
        starting_address: Coil to be written
        value:  Coil Value to be written
        """
        logging.info("Request to write single coil (FC05), starting address: {0}, value: {1}"
                     .format(str(starting_address), str(value)))
        return_value = self.execute_read_order(starting_address, function_code=FunctionCode.WRITE_SINGLE_COIL, values=value)
        return return_value


    def write_single_register(self, starting_address, value):
        """
        Write single Register to Master device (Function code 6)
        starting_address:  Register to be written
        value: Register Value to be written
        """
        logging.info("Request to write single register (FC06), starting address: {0}, value: {1}"
                     .format(str(starting_address), str(value)))
        return_value = self.execute_read_order(starting_address, function_code=FunctionCode.WRITE_SINGLE_REGISTER,
                                               values=value)
        return return_value

    def write_multiple_coils(self, starting_address, values):
        """
        Write multiple coils to Master device (Function code 15)
        starting_address :  First coil to be written
        values:  Coil Values [0..quantity-1] to be written
        """
        logging.info("Request to write multiple coil (FC15), starting address: {0}, values: {1}"
                     .format(str(starting_address), str(values)))
        return_value = self.execute_read_order(starting_address, function_code=FunctionCode.WRITE_MULTIPLE_COILS,
                                               values=values)
        return return_value

    def write_multiple_registers(self, starting_address, values):
        """
        Write multiple registers to Master device (Function code 16)
        starting_address: First register to be written
        values:  Register Values [0..quantity-1] to be written
        """
        logging.info("Request to write multiple registers (FC16), starting address: {0}, values: {1}"
                     .format(str(starting_address), str(values)))
        return_value = self.execute_read_order(starting_address, function_code=FunctionCode.WRITE_MULTIPLE_REGISTERS,
                                               values=values)
        return return_value


    @property
    def port(self):
        """
        Gets the Port were the Modbus-TCP Server is reachable (Standard is 502)
        """
        return self.__port

    @port.setter
    def port(self, port):
        """
        Sets the Port were the Modbus-TCP Server is reachable (Standard is 502)
        """
        self.__port = port

    @property
    def ipaddress(self):
        """
        Gets the IP-Address of the Server to be connected
        """
        return self.__ipAddress

    @ipaddress.setter
    def ipaddress(self, ipAddress):
        """
        Sets the IP-Address of the Server to be connected
        """
        self.__ipAddress = ipAddress

    @property
    def unitidentifier(self):
        """
        Gets the Unit identifier in case of serial connection (Default = 1)
        """
        return self.__unitIdentifier

    @unitidentifier.setter
    def unitidentifier(self, unitIdentifier):
        """
        Sets the Unit identifier in case of serial connection (Default = 1)
        """
        self.__unitIdentifier = unitIdentifier

    @property
    def baudrate(self):
        """
        Gets the Baudrate for serial connection (Default = 9600)
        """
        return self.__baudrate

    @baudrate.setter
    def baudrate(self, baudrate):
        """
        Sets the Baudrate for serial connection (Default = 9600)
        """
        self.__baudrate = baudrate

    @property
    def parity(self):
        """
        Gets the of Parity in case of serial connection
        """
        return self.__parity

    @parity.setter
    def parity(self, parity):
        """
        Sets the of Parity in case of serial connection
        Example modbusClient.Parity = Parity.even
        """
        self.__parity = parity

    @property
    def stopbits(self):
        """
        Gets the number of stopbits in case of serial connection
        """
        return self.__stopbits

    @stopbits.setter
    def stopbits(self, stopbits):
        """
        Sets the number of stopbits in case of serial connection
        Example: modbusClient.Stopbits = Stopbits.one
        """
        self.__stopbits = stopbits

    @property
    def timeout(self):
        """
        Gets the Timeout
        """
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout):
        """
        Sets the Timeout
        """
        self.__timeout = timeout

    def is_connected(self):
        """
        Returns true if a connection has been established
        """
        return self.__connected

    @property
    def debug(self):
        """
        Enables/disables debug mode
        """
        return self.__debug

    @debug.setter
    def debug(self, debug):
        """
        Enables/disables debug mode
        """
        self.__debug = debug
        if self.__debug:
            logging.getLogger().setLevel(self.__logging_level)
            # Add the log message handler to the logger
            handler1 = logging.handlers.RotatingFileHandler(
                'logdata.txt', maxBytes=2000000, backupCount=5)
            logging.getLogger().addHandler(handler1)
            formatter1 = logging.Formatter("%(asctime)s;%(message)s",
                                           "%Y-%m-%d %H:%M:%S")
            handler1.setFormatter(formatter1)

    @property
    def logging_level(self):
        """
        Sets the logging level - Default is logging.INFO
        """
        return self.__logging_level

    @logging_level.setter
    def logging_level(self, logging_level):
        """
        Sets the logging level - Default is logging.INFO
        """
        self.__logging_level = logging_level
        logging.getLogger().setLevel(self.__logging_level)

class Parity():
    even = 0
    odd = 1
    none = 2


class Stopbits():
    one = 0
    two = 1
    onePointFive = 2

class RegisterOrder():
    lowHigh = 0
    highLow = 1


def convert_double_to_two_registers(doubleValue, register_order=RegisterOrder.lowHigh):
    """
    Convert 32 Bit Value to two 16 Bit Value to send as Modbus Registers
    doubleValue: Value to be converted
    register_order: Desired Word Order (Low Register first or High Register first - Default: RegisterOrder.lowHigh
    return: 16 Bit Register values int[]
    """
    myList = list()

    myList.append(int(doubleValue & 0x0000FFFF))  # Append Least Significant Word
    myList.append(int((doubleValue & 0xFFFF0000) >> 16))  # Append Most Significant Word
    if register_order == RegisterOrder.highLow:
        myList[0] = int((doubleValue & 0xFFFF0000) >> 16)
        myList[1] = int(doubleValue & 0x0000FFFF)
    return myList


def convert_float_to_two_registers(floatValue, register_order=RegisterOrder.lowHigh):
    """
    Convert 32 Bit real Value to two 16 Bit Value to send as Modbus Registers
    floatValue: Value to be converted
    return: 16 Bit Register values int[]
    """
    myList = list()
    s = bytearray(struct.pack('<f', floatValue))  # little endian
    myList.append(s[0] | (s[1] << 8))  # Append Least Significant Word
    myList.append(s[2] | (s[3] << 8))  # Append Most Significant Word
    if register_order == RegisterOrder.highLow:
        myList[0] = s[2] | (s[3] << 8)
        myList[1] = s[0] | (s[1] << 8)
    return myList


def convert_registers_to_double(registers, register_order=RegisterOrder.lowHigh):
    """
    Convert two 16 Bit Registers to 32 Bit long value - Used to receive 32 Bit values from Modbus (Modbus Registers are 16 Bit long)
    registers: 16 Bit Registers
    return: 32 bit value
    """
    returnValue = (int(registers[0]) & 0x0000FFFF) | (int((registers[1]) << 16) & 0xFFFF0000)
    if register_order == RegisterOrder.highLow:
        returnValue = (int(registers[1]) & 0x0000FFFF) | (int((registers[0]) << 16) & 0xFFFF0000)
    return returnValue


def convert_registers_to_float(registers, register_order=RegisterOrder.lowHigh):
    """
    Convert two 16 Bit Registers to 32 Bit real value - Used to receive float values from Modbus (Modbus Registers are 16 Bit long)
    registers: 16 Bit Registers
    return: 32 bit value real
    """
    b = bytearray(4)
    b[0] = registers[0] & 0xff
    b[1] = (registers[0] & 0xff00) >> 8
    b[2] = (registers[1] & 0xff)
    b[3] = (registers[1] & 0xff00) >> 8
    if register_order == RegisterOrder.highLow:
        b[2] = registers[0] & 0xff
        b[3] = (registers[0] & 0xff00) >> 8
        b[0] = (registers[1] & 0xff)
        b[1] = (registers[1] & 0xff00) >> 8
    returnValue = struct.unpack('<f', b)  # little Endian
    return returnValue


if __name__ == "__main__":
    modbus_client = ModbusClient('COM3')
    modbus_client.debug = True
    modbus_client.logging_level = logging.DEBUG
    modbus_client.connect()
    counter = 0
    while (1):
        counter = counter + 1
        modbus_client.unitidentifier = 1
        #registers = [1,2,3,4,5,6,7,8,9]
        #modbus_client.write_multiple_registers(1, registers)
        modbus_client.write_single_coil(1,1)
        modbus_client.write_single_coil(8, 0)
        modbus_client.write_single_register(8, 4711)
        modbus_client.write_multiple_registers(8, [4711, 4712])
        modbus_client.write_multiple_coils(8, [True, True])
        print(modbus_client.read_discreteinputs(1, 1))
        print(modbus_client.read_coils(0, 14))
        print(modbus_client.read_holdingregisters(0, 14))
    modbus_client.close()
