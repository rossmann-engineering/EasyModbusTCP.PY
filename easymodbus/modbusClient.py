'''
Created on 12.09.2016

@author: Stefan Rossmann
'''
import importlib
import easymodbus.modbusException as Exceptions
import socket
import struct
import threading


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
        self.__receivedata = bytearray()
        self.__transactionIdentifier = 0
        self.__unitIdentifier = 1
        self.__timeout = 5
        self.__ser = None
        self.__tcpClientSocket = None
        self.__connected = False
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
        # print (self.ser)
        if self.__tcpClientSocket is not None:
            self.__tcpClientSocket.settimeout(5)
            self.__tcpClientSocket.connect((self.__ipAddress, self.__port))

            self.__connected = True
            self.__thread = threading.Thread(target=self.__listen, args=())
            self.__thread.start()

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

    def read_discreteinputs(self, starting_address, quantity):
        """
        Read Discrete Inputs from Master device (Function code 2)
        starting_address: First discrete input to be read
        quantity: Numer of discrete Inputs to be read
        returns: Boolean Array [0..quantity-1] which contains the discrete Inputs
        """
        self.__transactionIdentifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (starting_address > 65535) | (quantity > 2000):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 2000")
        function_code = 2
        length = 6
        transaction_identifier_lsb = self.__transactionIdentifier & 0xFF
        transaction_identifier_msb = ((self.__transactionIdentifier & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        length_msb = (length & 0xFF00) >> 8
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        quantity_lsb = quantity & 0xFF
        quantity_msb = (quantity & 0xFF00) >> 8
        if self.__ser is not None:
            data = bytearray(
                [self.__unitIdentifier, function_code, starting_address_msb, starting_address_lsb, quantity_msb,
                 quantity_lsb, 0, 0])
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            data[6] = crcLSB
            data[7] = crcMSB
            self.__ser.write(data)
            if quantity % 8 != 0:
                bytes_to_read = 6 + int(quantity / 8)
            else:
                bytes_to_read = 5 + int(quantity / 8)
            data = self.__ser.read(bytes_to_read)
            b = bytearray(data)
            data = b
            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError('Read timeout Exception')
            if (data[1] == 0x82) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x82) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1] == 0x82) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1] == 0x82) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            if (crcLSB != data[len(data) - 2]) & (crcMSB != data[len(data) - 1]):
                raise Exceptions.CRCCheckFailedException("CRC check failed")
            myList = list()
            for i in range(0, quantity):
                myList.append(bool((data[int(i / 8) + 3] >> int(i % 8)) & 0x1))
            return myList
        else:
            protocolIdentifierLSB = 0x00
            protocolIdentifierMSB = 0x00
            length_lsb = 0x06
            length_msb = 0x00
            data = bytearray(
                [transaction_identifier_msb, transaction_identifier_lsb, protocolIdentifierMSB, protocolIdentifierLSB,
                 length_msb, length_lsb, self.__unitIdentifier, function_code, starting_address_msb,
                 starting_address_lsb, quantity_msb, quantity_lsb])
            self.__tcpClientSocket.send(data)
            self.__receivedata = bytearray()
            if quantity % 8 != 0:
                bytes_to_read = 9 + int(quantity / 8)
            else:
                bytes_to_read = 8 + int(quantity / 8)
            try:
                while len(self.__receivedata) == 0:
                    pass
            except Exception:
                raise Exception('Read Timeout')

            data = bytearray(self.__receivedata)

            if (data[1 + 6] == 0x82) & (data[2 + 6] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1 + 6] == 0x82) & (data[2 + 6] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1 + 6] == 0x82) & (data[2 + 6] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1 + 6] == 0x82) & (data[2 + 6] == 0x04):
                raise Exceptions.ModbusException("error reading")
            myList = list()
            for i in range(0, quantity):
                myList.append(bool((data[int(i / 8) + 3 + 6] >> int(i % 8)) & 0x1))
            return myList

    def read_coils(self, starting_address, quantity):
        """
        Read Coils from Master device (Function code 1)
        starting_address:  First coil to be read
        quantity: Numer of coils to be read
        returns:  Boolean Array [0..quantity-1] which contains the coils
        """
        self.__transactionIdentifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (starting_address > 65535) | (quantity > 2000):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 2000")
        function_code = 1
        length = 6
        transaction_identifier_lsb = self.__transactionIdentifier & 0xFF
        transaction_identifier_msb = ((self.__transactionIdentifier & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        length_msb = (length & 0xFF00) >> 8
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        quantity_lsb = quantity & 0xFF
        quantity_msb = (quantity & 0xFF00) >> 8
        if self.__ser is not None:
            data = bytearray(
                [self.__unitIdentifier, function_code, starting_address_msb, starting_address_lsb, quantity_msb,
                 quantity_lsb, 0, 0])
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            data[6] = crcLSB
            data[7] = crcMSB
            self.__ser.write(data)
            if quantity % 8 != 0:
                bytes_to_read = 6 + int(quantity / 8)
            else:
                bytes_to_read = 5 + int(quantity / 8)
            data = self.__ser.read(bytes_to_read)
            b = bytearray(data)
            data = b
            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError('Read timeout Exception')
            if (data[1] == 0x81) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x81) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1] == 0x81) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1] == 0x81) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            if (crcLSB != data[len(data) - 2]) & (crcMSB != data[len(data) - 1]):
                raise Exceptions.CRCCheckFailedException("CRC check failed")
            myList = list()
            for i in range(0, quantity):
                myList.append(bool((data[int(i / 8) + 3] >> int(i % 8)) & 0x1))
            return myList
        else:
            protocolIdentifierLSB = 0x00
            protocolIdentifierMSB = 0x00
            length_lsb = 0x06
            length_msb = 0x00
            data = bytearray(
                [transaction_identifier_msb, transaction_identifier_lsb, protocolIdentifierMSB, protocolIdentifierLSB,
                 length_msb, length_lsb, self.__unitIdentifier, function_code, starting_address_msb,
                 starting_address_lsb, quantity_msb, quantity_lsb])
            self.__tcpClientSocket.send(data)
            self.__receivedata = bytearray()
            if (quantity % 8 != 0):
                bytes_to_read = 10 + int(quantity / 8)
            else:
                bytes_to_read = 9 + int(quantity / 8)
            try:
                while len(self.__receivedata) == 0:
                    pass
            except Exception:
                raise Exception('Read Timeout')
            data = bytearray(self.__receivedata)
            if (data[1 + 6] == 0x82) & (data[2 + 6] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1 + 6] == 0x82) & (data[2 + 6] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1 + 6] == 0x82) & (data[2 + 6] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1 + 6] == 0x82) & (data[2 + 6] == 0x04):
                raise Exceptions.ModbusException("error reading")
            myList = list()
            for i in range(0, quantity):
                myList.append(bool((data[int(i / 8) + 3 + 6] >> int(i % 8)) & 0x1))
            return myList

    def read_holdingregisters(self, starting_address, quantity):
        """
        Read Holding Registers from Master device (Function code 3)
        starting_address: First holding register to be read
        quantity:  Number of holding registers to be read
        returns:  Int Array [0..quantity-1] which contains the holding registers
        """
        self.__transactionIdentifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (starting_address > 65535) | (quantity > 125):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 125")
        function_code = 3
        length = 6
        transaction_identifier_lsb = self.__transactionIdentifier & 0xFF
        transaction_identifier_msb = ((self.__transactionIdentifier & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        length_msb = (length & 0xFF00) >> 8
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        quantity_lsb = quantity & 0xFF
        quantity_msb = (quantity & 0xFF00) >> 8
        if self.__ser is not None:
            data = bytearray(
                [self.__unitIdentifier, function_code, starting_address_msb, starting_address_lsb, quantity_msb,
                 quantity_lsb, 0, 0])

            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            data[6] = crcLSB
            data[7] = crcMSB

            self.__ser.write(data)
            bytes_to_read = 5 + int(quantity * 2)
            data = self.__ser.read(bytes_to_read)
            b = bytearray(data)
            data = b

            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError('Read timeout Exception')
            if (data[1] == 0x83) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x83) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1] == 0x83) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1] == 0x83) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            if (crcLSB != data[len(data) - 2]) & (crcMSB != data[len(data) - 1]):
                raise Exceptions.CRCCheckFailedException("CRC check failed")

            myList = list()
            for i in range(0, quantity):
                myList.append((data[i * 2 + 3] << 8) + data[i * 2 + 4])
            return myList
        else:
            protocolIdentifierLSB = 0x00
            protocolIdentifierMSB = 0x00
            length_lsb = 0x06
            length_msb = 0x00
            data = bytearray(
                [transaction_identifier_msb, transaction_identifier_lsb, protocolIdentifierMSB, protocolIdentifierLSB,
                 length_msb, length_lsb, self.__unitIdentifier, function_code, starting_address_msb,
                 starting_address_lsb, quantity_msb, quantity_lsb])
            self.__tcpClientSocket.send(data)
            bytes_to_read = 9 + int(quantity * 2)
            self.__receivedata = bytearray()
            try:
                while len(self.__receivedata) == 0:
                    pass
            except Exception:
                raise Exception('Read Timeout')
            data = bytearray(self.__receivedata)
            if (data[1 + 6] == 0x83) & (data[2 + 6] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1 + 6] == 0x83) & (data[2 + 6] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1 + 6] == 0x83) & (data[2 + 6] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1 + 6] == 0x83) & (data[2 + 6] == 0x04):
                raise Exceptions.ModbusException("error reading")
            myList = list()
            for i in range(0, quantity):
                myList.append((data[i * 2 + 3 + 6] << 8) + data[i * 2 + 4 + 6])
            return myList

    def read_inputregisters(self, starting_address, quantity):
        """
        Read Input Registers from Master device (Function code 4)
        starting_address :  First input register to be read
        quantity:  Number of input registers to be read
        returns:  Int Array [0..quantity-1] which contains the input registers
        """
        self.__transactionIdentifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (starting_address > 65535) | (quantity > 125):
            raise ValueError("Starting address must be 0 - 65535 quantity must be 0 - 125")
        function_code = 4
        length = 6
        transaction_identifier_lsb = self.__transactionIdentifier & 0xFF
        transaction_identifier_msb = ((self.__transactionIdentifier & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        length_msb = (length & 0xFF00) >> 8
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        quantity_lsb = quantity & 0xFF
        quantity_msb = (quantity & 0xFF00) >> 8
        if self.__ser is not None:
            data = bytearray(
                [self.__unitIdentifier, function_code, starting_address_msb, starting_address_lsb, quantity_msb,
                 quantity_lsb, 0, 0])
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            data[6] = crcLSB
            data[7] = crcMSB

            self.__ser.write(data)
            bytes_to_read = 5 + int(quantity * 2)

            data = self.__ser.read(bytes_to_read)

            b = bytearray(data)
            data = b

            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError("Read timeout Exception")
            if (data[1] == 0x84) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x84) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1] == 0x84) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1] == 0x84) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            if (crcLSB != data[len(data) - 2]) & (crcMSB != data[len(data) - 1]):
                raise Exceptions.CRCCheckFailedException("CRC check failed")
            myList = list()
            for i in range(0, quantity):
                myList.append((data[i * 2 + 3] << 8) + data[i * 2 + 4])
            return myList
        else:
            protocolIdentifierLSB = 0x00
            protocolIdentifierMSB = 0x00
            length_lsb = 0x06
            length_msb = 0x00
            data = bytearray(
                [transaction_identifier_msb, transaction_identifier_lsb, protocolIdentifierMSB, protocolIdentifierLSB,
                 length_msb, length_lsb, self.__unitIdentifier, function_code, starting_address_msb,
                 starting_address_lsb, quantity_msb, quantity_lsb])
            self.__tcpClientSocket.send(data)
            bytes_to_read = 9 + int(quantity * 2)
            self.__receivedata = bytearray()
            try:
                while len(self.__receivedata) == 0:
                    pass
            except Exception:
                raise Exception('Read Timeout')
            data = bytearray(self.__receivedata)
            if (data[1 + 6] == 0x84) & (data[2 + 6] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1 + 6] == 0x84) & (data[2 + 6] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1 + 6] == 0x84) & (data[2 + 6] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1 + 6] == 0x84) & (data[2 + 6] == 0x04):
                raise Exceptions.ModbusException("error reading")
            myList = list()
            for i in range(0, quantity):
                myList.append((data[i * 2 + 3 + 6] << 8) + data[i * 2 + 4 + 6])
            return myList

    def write_single_coil(self, starting_address, value):
        """
        Write single Coil to Master device (Function code 5)
        starting_address: Coil to be written
        value:  Coil Value to be written
        """
        self.__transactionIdentifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        function_code = 5
        length = 6
        transaction_identifier_lsb = self.__transactionIdentifier & 0xFF
        transaction_identifier_msb = ((self.__transactionIdentifier & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        length_msb = (length & 0xFF00) >> 8
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        if value:
            valueLSB = 0x00
            valueMSB = (0xFF00) >> 8
        else:
            valueLSB = 0x00
            valueMSB = (0x00) >> 8
        if self.__ser is not None:
            data = bytearray(
                [self.__unitIdentifier, function_code, starting_address_msb, starting_address_lsb, valueMSB, valueLSB,
                 0, 0])
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            data[6] = crcLSB
            data[7] = crcMSB
            self.__ser.write(data)
            bytes_to_read = 8
            data = self.__ser.read(bytes_to_read)
            b = bytearray(data)
            data = b
            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError('Read timeout Exception')
            if (data[1] == 0x85) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x85) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException("Address invalid")
            if (data[1] == 0x85) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("Value invalid")
            if (data[1] == 0x85) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            if (crcLSB != data[len(data) - 2]) & (crcMSB != data[len(data) - 1]):
                raise Exceptions.CRCCheckFailedException("CRC check failed")
            if data[1] == self.__unitIdentifier:
                return True
            else:
                return False
        else:
            protocolIdentifierLSB = 0x00
            protocolIdentifierMSB = 0x00
            length_lsb = 0x06
            length_msb = 0x00
            data = bytearray(
                [transaction_identifier_msb, transaction_identifier_lsb, protocolIdentifierMSB, protocolIdentifierLSB,
                 length_msb, length_lsb, self.__unitIdentifier, function_code, starting_address_msb,
                 starting_address_lsb, valueMSB, valueLSB])
            self.__tcpClientSocket.send(data)
            bytes_to_read = 12
            self.__receivedata = bytearray()
            try:
                while len(self.__receivedata) == 0:
                    pass
            except Exception:
                raise Exception('Read Timeout')
            data = bytearray(self.__receivedata)
            if (data[1 + 6] == 0x85) & (data[2 + 6] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1 + 6] == 0x85) & (data[2 + 6] == 0x02):
                raise Exceptions.starting_addressInvalidException("Address invalid")
            if (data[1 + 6] == 0x85) & (data[2 + 6] == 0x03):
                raise Exceptions.QuantityInvalidException("Value invalid")
            if (data[1 + 6] == 0x85) & (data[2 + 6] == 0x04):
                raise Exceptions.ModbusException("error reading")

                return True

    def write_single_register(self, starting_address, value):
        """
        Write single Register to Master device (Function code 6)
        starting_address:  Register to be written
        value: Register Value to be written
        """
        self.__transactionIdentifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        function_code = 6
        length = 6
        transaction_identifier_lsb = self.__transactionIdentifier & 0xFF
        transaction_identifier_msb = ((self.__transactionIdentifier & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        length_msb = (length & 0xFF00) >> 8
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        valueLSB = value & 0xFF
        valueMSB = (value & 0xFF00) >> 8
        if self.__ser is not None:
            data = bytearray(
                [self.__unitIdentifier, function_code, starting_address_msb, starting_address_lsb, valueMSB, valueLSB,
                 0, 0])
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            data[6] = crcLSB
            data[7] = crcMSB
            self.__ser.write(data)
            bytes_to_read = 8
            data = self.__ser.read(bytes_to_read)
            b = bytearray(data)
            data = b
            # Check for Exception
            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError('Read timeout Exception')
            if (data[1] == 0x86) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x86) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException("Register address invalid")
            if (data[1] == 0x86) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("Invalid Register Value")
            if (data[1] == 0x86) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            if (crcLSB != data[len(data) - 2]) & (crcMSB != data[len(data) - 1]):
                raise Exceptions.CRCCheckFailedException("CRC check failed")

            if data[1] == self.__unitIdentifier:
                return True
            else:
                return False
        else:
            protocolIdentifierLSB = 0x00
            protocolIdentifierMSB = 0x00
            length_lsb = 0x06
            length_msb = 0x00
            data = bytearray(
                [transaction_identifier_msb, transaction_identifier_lsb, protocolIdentifierMSB, protocolIdentifierLSB,
                 length_msb, length_lsb, self.__unitIdentifier, function_code, starting_address_msb,
                 starting_address_lsb, valueMSB, valueLSB])
            self.__tcpClientSocket.send(data)
            bytes_to_read = 12
            self.__receivedata = bytearray()
            try:
                while (len(self.__receivedata) == 0):
                    pass
            except Exception:
                raise Exception('Read Timeout')
            data = bytearray(self.__receivedata)
            if (data[1 + 6] == 0x86) & (data[2 + 6] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1 + 6] == 0x86) & (data[2 + 6] == 0x02):
                raise Exceptions.starting_addressInvalidException("Register address invalid")
            if (data[1 + 6] == 0x86) & (data[2 + 6] == 0x03):
                raise Exceptions.QuantityInvalidException("Invalid Register Value")
            if (data[1 + 6] == 0x86) & (data[2 + 6] == 0x04):
                raise Exceptions.ModbusException("error reading")

                return True

    def write_multiple_coils(self, starting_address, values):
        """
        Write multiple coils to Master device (Function code 15)
        starting_address :  First coil to be written
        values:  Coil Values [0..quantity-1] to be written
        """
        self.__transactionIdentifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        function_code = 15
        length = 6
        transaction_identifier_lsb = self.__transactionIdentifier & 0xFF
        transaction_identifier_msb = ((self.__transactionIdentifier & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        length_msb = (length & 0xFF00) >> 8
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        quantityLSB = len(values) & 0xFF
        quantityMSB = (len(values) & 0xFF00) >> 8
        valueToWrite = list()
        singleCoilValue = 0
        for i in range(0, len(values)):
            if ((i % 8) == 0):
                if i > 0:
                    valueToWrite.append(singleCoilValue)
                singleCoilValue = 0

            if values[i] == True:
                coilValue = 1
            else:
                coilValue = 0
            singleCoilValue = ((coilValue) << (i % 8) | (singleCoilValue))

        valueToWrite.append(singleCoilValue)
        if self.__ser is not None:
            data = bytearray(
                [self.__unitIdentifier, function_code, starting_address_msb, starting_address_lsb, quantityMSB,
                 quantityLSB])
            data.append(len(valueToWrite))  # Bytecount
            for i in range(0, len(valueToWrite)):
                data.append(valueToWrite[i] & 0xFF)

            crc = self.__calculateCRC(data, len(data), 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            data.append(crcLSB)
            data.append(crcMSB)
            self.__ser.write(data)
            bytes_to_read = 8
            data = self.__ser.read(bytes_to_read)
            b = bytearray(data)
            data = b
            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError('Read timeout Exception')
            if (data[1] == 0x8F) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x8F) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1] == 0x8F) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1] == 0x8F) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            if (crcLSB != data[len(data) - 2]) & (crcMSB != data[len(data) - 1]):
                raise Exceptions.CRCCheckFailedException("CRC check failed")
            if data[1] == self.__unitIdentifier:
                return True
            else:
                return False
        else:
            protocolIdentifierLSB = 0x00
            protocolIdentifierMSB = 0x00
            length_lsb = 0x06
            length_msb = 0x00
            data = bytearray(
                [transaction_identifier_msb, transaction_identifier_lsb, protocolIdentifierMSB, protocolIdentifierLSB,
                 length_msb, length_lsb, self.__unitIdentifier, function_code, starting_address_msb,
                 starting_address_lsb, quantityMSB, quantityLSB])
            data.append(len(valueToWrite))  # Bytecount
            for i in range(0, len(valueToWrite)):
                data.append(valueToWrite[i] & 0xFF)
            self.__tcpClientSocket.send(data)
            bytes_to_read = 12
            self.__receivedata = bytearray()
            try:
                while (len(self.__receivedata) == 0):
                    pass
            except Exception:
                raise Exception('Read Timeout')
            data = bytearray(self.__receivedata)
            if (data[1] == 0x8F) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x8F) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1] == 0x8F) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1] == 0x8F) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")

            return True

    def write_multiple_registers(self, starting_address, values):
        """
        Write multiple registers to Master device (Function code 16)
        starting_address: First register to be written
        values:  Register Values [0..quantity-1] to be written
        """
        self.__transactionIdentifier += 1
        if self.__ser is not None:
            if self.__ser.closed:
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        function_code = 16
        length = 6
        transaction_identifier_lsb = self.__transactionIdentifier & 0xFF
        transaction_identifier_msb = ((self.__transactionIdentifier & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        length_msb = (length & 0xFF00) >> 8
        starting_address_lsb = starting_address & 0xFF
        starting_address_msb = (starting_address & 0xFF00) >> 8
        quantityLSB = len(values) & 0xFF
        quantityMSB = (len(values) & 0xFF00) >> 8
        valueToWrite = list()
        for i in range(0, len(values)):
            valueToWrite.append(values[i])
        if self.__ser is not None:
            data = bytearray(
                [self.__unitIdentifier, function_code, starting_address_msb, starting_address_lsb, quantityMSB,
                 quantityLSB])
            data.append(len(valueToWrite) * 2)  # Bytecount
            for i in range(0, len(valueToWrite)):
                data.append((valueToWrite[i] & 0xFF00) >> 8)
                data.append(valueToWrite[i] & 0xFF)
            crc = self.__calculateCRC(data, len(data), 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            data.append(crcLSB)
            data.append(crcMSB)
            self.__ser.write(data)
            bytes_to_read = 8
            data = self.__ser.read(bytes_to_read)
            b = bytearray(data)
            data = b
            if len(data) < bytes_to_read:
                raise Exceptions.TimeoutError('Read timeout Exception')
            if (data[1] == 0x90) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x90) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1] == 0x90) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1] == 0x90) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            crc = self.__calculateCRC(data, len(data) - 2, 0)
            crcLSB = crc & 0xFF
            crcMSB = (crc & 0xFF00) >> 8
            if (crcLSB != data[len(data) - 2]) & (crcMSB != data[len(data) - 1]):
                raise Exceptions.CRCCheckFailedException("CRC check failed")
            if data[1] == self.__unitIdentifier:
                return True
            else:
                return False
        else:
            protocolIdentifierLSB = 0x00
            protocolIdentifierMSB = 0x00
            length_lsb = 0x06
            length_msb = 0x00
            data = bytearray(
                [transaction_identifier_msb, transaction_identifier_lsb, protocolIdentifierMSB, protocolIdentifierLSB,
                 length_msb, length_lsb, self.__unitIdentifier, function_code, starting_address_msb,
                 starting_address_lsb, quantityMSB, quantityLSB])
            data.append(len(valueToWrite) * 2)  # Bytecount
            for i in range(0, len(valueToWrite)):
                data.append((valueToWrite[i] & 0xFF00) >> 8)
                data.append(valueToWrite[i] & 0xFF)

            self.__tcpClientSocket.send(data)
            bytes_to_read = 12
            self.__receivedata = bytearray()
            try:
                while len(self.__receivedata) == 0:
                    pass
            except Exception:
                raise Exception('Read Timeout')
            data = bytearray(self.__receivedata)
            if (data[1] == 0x90) & (data[2] == 0x01):
                raise Exceptions.function_codeNotSupportedException("Function code not supported by master")
            if (data[1] == 0x90) & (data[2] == 0x02):
                raise Exceptions.starting_addressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            if (data[1] == 0x90) & (data[2] == 0x03):
                raise Exceptions.QuantityInvalidException("quantity invalid")
            if (data[1] == 0x90) & (data[2] == 0x04):
                raise Exceptions.ModbusException("error reading")
            return True

    def __calculateCRC(self, data, numberOfBytes, startByte):
        crc = 0xFFFF
        for x in range(0, numberOfBytes):
            crc = crc ^ data[x]
            for _ in range(0, 8):
                if (crc & 0x0001) != 0:
                    crc = crc >> 1
                    crc = crc ^ 0xA001
                else:
                    crc = crc >> 1
        return crc

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


class Parity():
    even = 0
    odd = 1
    none = 2


class Stopbits():
    one = 0
    two = 1
    onePointFive = 2


def convert_double_to_two_registers(doubleValue):
    """
    Convert 32 Bit Value to two 16 Bit Value to send as Modbus Registers
    doubleValue: Value to be converted
    return: 16 Bit Register values int[]
    """
    myList = list()
    myList.append(int(doubleValue & 0x0000FFFF))  # Append Least Significant Word
    myList.append(int((doubleValue & 0xFFFF0000) >> 16))  # Append Most Significant Word
    return myList


def convert_float_to_two_registers(floatValue):
    """
    Convert 32 Bit real Value to two 16 Bit Value to send as Modbus Registers
    floatValue: Value to be converted
    return: 16 Bit Register values int[]
    """
    myList = list()
    s = bytearray(struct.pack('<f', floatValue))  # little endian
    myList.append(s[0] | (s[1] << 8))  # Append Least Significant Word
    myList.append(s[2] | (s[3] << 8))  # Append Most Significant Word

    return myList


def convert_registers_to_double(registers):
    """
    Convert two 16 Bit Registers to 32 Bit long value - Used to receive 32 Bit values from Modbus (Modbus Registers are 16 Bit long)
    registers: 16 Bit Registers
    return: 32 bit value
    """
    returnValue = (int(registers[0]) & 0x0000FFFF) | (int((registers[1]) << 16) & 0xFFFF0000)
    return returnValue


def convert_registers_to_float(registers):
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
    returnValue = struct.unpack('<f', b)  # little Endian
    return returnValue


if __name__ == "__main__":
    modbus_client = ModbusClient("192.168.178.33", 502)
    modbus_client.connect()
    counter = 0
    while (1):
        counter = counter + 1
        modbus_client.unitidentifier = 200
        modbus_client.write_single_register(1, counter)
        print(modbus_client.read_holdingregisters(1, 1))
    modbus_client.close()
