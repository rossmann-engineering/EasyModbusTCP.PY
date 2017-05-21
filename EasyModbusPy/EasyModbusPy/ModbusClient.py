'''
Created on 12.09.2016

@author: Stefan Rossmann
'''
#import serial
import importlib
import Exceptions
import socket
import struct
from builtins import int
from _testcapi import instancemethod
from test.test_array import SIGNED_INT16_BE
from tkinter import DoubleVar

class ModbusClient(object):
    """
    Implementation of a Modbus TCP Client and a Modbsu RTU Master
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
        self.__transactionIdentifier=0
        self._unitIdentifier = 1;
        self.ser = None
        self.tcpClientSocket = None
        self.__connected = False
        #Constructor for RTU
        if len(params) == 1 & isinstance(params[0], str):
            serial = importlib.import_module("serial")
            self.serialPort = params[0]
            self._baudrate = 9600
            self._parity = Parity.even
            self._stopbits = Stopbits.one
            self.__transactionIdentifier = 0
            self.ser = serial.Serial()
        #Constructor for TCP
        elif (len(params) == 2) & isinstance(params[0], str) & isinstance(params[1], int):
            self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._ipAddress = params[0]
            self._port = params[1]
            
            
    def Connect(self):
        """
        Connects to a Modbus-TCP Server or a Modbus-RTU Slave with the given Parameters
        """    
        if (self.ser is not None): 
            serial = importlib.import_module("serial")  
            if self._stopbits == 0:               
                self.ser.stopbits = serial.STOPBITS_ONE
            elif self._stopbits == 1:               
                self.ser.stopbits = serial.STOPBITS_TWO
            elif self._stopbits == 2:               
                self.ser.stopbits = serial.STOPBITS_ONE_POINT_FIVE         
            if self._parity == 0:               
                self.ser.parity = serial.PARITY_EVEN
            elif self._parity == 1:               
                self.ser.parity = serial.PARITY_ODD
            elif self._parity == 2:               
                self.ser.parity = serial.PARITY_NONE 
            self.ser = serial.Serial(self.serialPort, self._baudrate, timeout=1, parity=self.ser.parity, stopbits=self.ser.stopbits, xonxoff=0, rtscts=0)
        #print (self.ser)
        if (self.tcpClientSocket is not None):  
            self.tcpClientSocket.connect((self._ipAddress, self._port))
        self.__connected = True
  
    def close(self):
        """
        Closes Serial port, or TCP-Socket connection
        """
        if (self.ser is not None):
            self.ser.close()
        if (self.tcpClientSocket is not None):
            self.tcpClientSocket.shutdown(socket.SHUT_RDWR)
            self.tcpClientSocket.close()
        self.__connected = False
        
            
    def ReadDiscreteInputs(self, startingAddress, quantity):
        """
        Read Discrete Inputs from Master device (Function code 2)
        startingAddress: First discrete input to be read
        quantity: Numer of discrete Inputs to be read
        returns: Boolean Array [0..quantity-1] which contains the discrete Inputs
        """
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (startingAddress > 65535 | quantity >2000):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 2000");
        functionCode = 2
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = (startingAddress&0xFF00) >> 8
        quatityLSB = quantity&0xFF
        quatityMSB = (quantity&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB,0,0] )
            CRC = self.__calculateCRC(data, len(data)-2, 0)
            CrcLSB = CRC&0xFF
            CrcMSB = (CRC&0xFF00) >> 8
            data[6] = CrcLSB
            data[7] = CrcMSB
            self.ser.write(data)
            if (quantity % 8 != 0):
                bytesToRead = 6+int(quantity/8)
            else:
                bytesToRead = 5+int(quantity/8)
            data = self.ser.read(bytesToRead)
            if ((data[1] == 0x82) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x82) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x82) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x82) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            myList = list()
            for i in range(0, quantity):
                myList.append(bool((data[int(i/8)+3] >> int(i%8)) & 0x1))            
            return myList
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB] )
            self.tcpClientSocket.send(data)
            if (quantity % 8 != 0):
                bytesToRead = 10+int(quantity/8)
            else:
                bytesToRead = 9+int(quantity/8)
            data = self.tcpClientSocket.recv(bytesToRead)
            
            if ((data[1 + 6] == 0x82) & (data[2 + 6] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1 + 6] == 0x82) & (data[2+6] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1 + 6] == 0x82) & (data[2+6] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1 + 6] == 0x82) & (data[2+6] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            myList = list()
            for i in range(0, quantity):
                myList.append(bool((data[int(i/8)+3+6] >> int(i%8)) & 0x1))            
            return myList



    def ReadCoils(self, startingAddress, quantity):
        """
        Read Coils from Master device (Function code 1)
        startingAddress:  First coil to be read
        quantity: Numer of coils to be read
        returns:  Boolean Array [0..quantity-1] which contains the coils
        """
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (startingAddress > 65535 | quantity >2000):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 2000");
        functionCode = 1
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = (startingAddress&0xFF00) >> 8
        quatityLSB = quantity&0xFF
        quatityMSB = (quantity&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB,0,0] )
            CRC = self.__calculateCRC(data, len(data)-2, 0)
            CrcLSB = CRC&0xFF
            CrcMSB = (CRC&0xFF00) >> 8
            data[6] = CrcLSB
            data[7] = CrcMSB
            self.ser.write(data)
            if (quantity % 8 != 0):
                bytesToRead = 6+int(quantity/8)
            else:
                bytesToRead = 5+int(quantity/8)
            data = self.ser.read(bytesToRead)
            if ((data[1] == 0x81) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x81) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x81) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x81) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            myList = list()
            for i in range(0, quantity):
                myList.append(bool((data[int(i/8)+3] >> int(i%8)) & 0x1))            
            return myList
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB] )
            self.tcpClientSocket.send(data)
            if (quantity % 8 != 0):
                bytesToRead = 10+int(quantity/8)
            else:
                bytesToRead = 9+int(quantity/8)
            data = self.tcpClientSocket.recv(bytesToRead)
            
            if ((data[1 + 6] == 0x82) & (data[2 + 6] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1 + 6] == 0x82) & (data[2+6] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1 + 6] == 0x82) & (data[2+6] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1 + 6] == 0x82) & (data[2+6] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            myList = list()
            for i in range(0, quantity):
                myList.append(bool((data[int(i/8)+3+6] >> int(i%8)) & 0x1))            
            return myList
        
        
        

    def ReadHoldingRegisters(self, startingAddress, quantity):
        """
        Read Holding Registers from Master device (Function code 3)
        startingAddress: First holding register to be read
        quantity:  Number of holding registers to be read
        returns:  Int Array [0..quantity-1] which contains the holding registers
        """
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (startingAddress > 65535 | quantity >125):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 125");
        functionCode = 3
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = (startingAddress&0xFF00) >> 8
        quatityLSB = quantity&0xFF
        quatityMSB = (quantity&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB,0,0] )
            CRC = self.__calculateCRC(data, len(data)-2, 0)
            CrcLSB = CRC&0xFF
            CrcMSB = (CRC&0xFF00) >> 8
            data[6] = CrcLSB
            data[7] = CrcMSB
            self.ser.write(data)
            bytesToRead = 5+int(quantity*2)
            data = self.ser.read(bytesToRead)
            if ((data[1] == 0x83) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x83) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x83) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x83) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            myList = list()
            for i in range(0, quantity):
                myList.append((data[i*2+3]<<8) +data[i*2+4])            
            return myList 
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB] )
            self.tcpClientSocket.send(data)
            bytesToRead = 9+int(quantity*2)
            data = self.tcpClientSocket.recv(bytesToRead)
            if ((data[1+6] == 0x83) & (data[2+6] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1+6] == 0x83) & (data[2+6] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1+6] == 0x83) & (data[2+6] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1+6] == 0x83) & (data[2+6] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            myList = list()
            for i in range(0, quantity):
                myList.append((data[i*2+3+6]<<8) +data[i*2+4+6])            
            return myList 

    def ReadInputRegisters(self, startingAddress, quantity):
        """
        Read Input Registers from Master device (Function code 4)
        startingAddress :  First input register to be read
        quantity:  Number of input registers to be read
        returns:  Int Array [0..quantity-1] which contains the input registers
        """
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened");
        if (startingAddress > 65535 | quantity >125):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 125");
        functionCode = 4
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = (startingAddress&0xFF00) >> 8
        quatityLSB = quantity&0xFF
        quatityMSB = (quantity&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB,0,0] )
            CRC = self.__calculateCRC(data, len(data)-2, 0)
            CrcLSB = CRC&0xFF
            CrcMSB = (CRC&0xFF00) >> 8
            data[6] = CrcLSB
            data[7] = CrcMSB
            self.ser.write(data)
            bytesToRead = 5+int(quantity*2)
            data = self.ser.read(bytesToRead)
            if ((data[1] == 0x84) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x84) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x84) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x84) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            myList = list()
            for i in range(0, quantity):
                myList.append((data[i*2+3]<<8) +data[i*2+4])            
            return myList 
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB] )
            self.tcpClientSocket.send(data)
            bytesToRead = 9+int(quantity*2)
            data = self.tcpClientSocket.recv(bytesToRead)
            if ((data[1+6] == 0x84) & (data[2+6] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1+6] == 0x84) & (data[2+6] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1+6] == 0x84) & (data[2+6] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1+6] == 0x84) & (data[2+6] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            myList = list()
            for i in range(0, quantity):
                myList.append((data[i*2+3+6]<<8) +data[i*2+4+6])            
            return myList 
        
    def WriteSingleCoil(self, startingAddress, value):
        """
        Write single Coil to Master device (Function code 5)
        startingAddress: Coil to be written
        value:  Coil Value to be written
        """
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        functionCode = 5
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = (startingAddress&0xFF00) >> 8
        if value:
            valueLSB = 0x00
            valueMSB = (0xFF00) >> 8
        else:
            valueLSB = 0x00
            valueMSB = (0x00) >> 8
        if (self.ser is not None):
            data = bytearray([self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,valueMSB,valueLSB,0,0] )
            CRC = self.__calculateCRC(data, len(data)-2, 0)
            CrcLSB = CRC&0xFF
            CrcMSB = (CRC&0xFF00) >> 8
            data[6] = CrcLSB
            data[7] = CrcMSB
            self.ser.write(data)
            bytesToRead = 8
            data = self.ser.read(bytesToRead)
            if ((data[1] == 0x85) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x85) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x85) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x85) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            if data[1] == self._unitIdentifier:
                return True 
            else:
                return False  
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,valueMSB,valueLSB] )
            self.tcpClientSocket.send(data)
            bytesToRead = 12
            data = self.tcpClientSocket.recv(bytesToRead)
            if ((data[1+6] == 0x85) & (data[2+6] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1+6] == 0x85) & (data[2+6] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1+6] == 0x85) & (data[2+6] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1+6] == 0x85) & (data[2+6] == 0x04)):
                raise Exceptions.ModbusException("error reading");

                return True 
   
        
    def WriteSingleRegister(self, startingAddress, value):
        """
        Write single Register to Master device (Function code 6)
        startingAddress:  Register to be written
        value: Register Value to be written
        """
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        functionCode = 6
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = (startingAddress&0xFF00) >> 8
        valueLSB = value&0xFF
        valueMSB = (value&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,valueMSB,valueLSB,0,0] )
            CRC = self.__calculateCRC(data, len(data)-2, 0)
            CrcLSB = CRC&0xFF
            CrcMSB = (CRC&0xFF00) >> 8
            data[6] = CrcLSB
            data[7] = CrcMSB
            self.ser.write(data)
            bytesToRead = 8
            data = self.ser.read(bytesToRead)
            if ((data[1] == 0x86) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x86) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x86) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x86) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            if data[1] == self._unitIdentifier:
                return True 
            else:
                return False   
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,valueMSB,valueLSB] )
            self.tcpClientSocket.send(data)
            bytesToRead = 12
            data = self.tcpClientSocket.recv(bytesToRead)
            if ((data[1+6] == 0x86) & (data[2+6] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1+6] == 0x86) & (data[2+6] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1+6] == 0x86) & (data[2+6] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1+6] == 0x86) & (data[2+6] == 0x04)):
                raise Exceptions.ModbusException("error reading");

                return True            
             
    def WriteMultipleCoils(self, startingAddress, values):
        """
        Write multiple coils to Master device (Function code 15)
        startingAddress :  First coil to be written
        values:  Coil Values [0..quantity-1] to be written
        """
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened");
        functionCode = 15
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = (startingAddress&0xFF00) >> 8
        quantityLSB = len(values)&0xFF
        quantityMSB = (len(values)&0xFF00) >> 8
        valueToWrite = list()
        singleCoilValue = 0;
        for i in range(0, len(values)):
            if ((i % 8) == 0):
                if i > 0:
                    valueToWrite.append(singleCoilValue)
                singleCoilValue = 0;

            if (values[i] == True):
                coilValue = 1
            else:
                coilValue = 0   
            singleCoilValue = ((coilValue)<<(i%8) | (singleCoilValue));
 
        valueToWrite.append(singleCoilValue)
        if (self.ser is not None):    
            data = bytearray([self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB, quantityMSB, quantityLSB] )
            data.append(len(valueToWrite))   #Bytecount 
            for i in range (0, len(valueToWrite)):
                data.append(valueToWrite[i]&0xFF)      
          
            CRC = self.__calculateCRC(data, len(data), 0)
            CrcLSB = CRC&0xFF
            CrcMSB = (CRC&0xFF00) >> 8
            data.append(CrcLSB)
            data.append(CrcMSB)
            self.ser.write(data)
            bytesToRead = 8
            data = self.ser.read(bytesToRead)
            if ((data[1] == 0x8F) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x8F) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x8F) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x8F) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            if data[1] == self._unitIdentifier:
                return True 
            else:
                return False 
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB, quantityMSB, quantityLSB] )
            data.append(len(valueToWrite))   #Bytecount 
            for i in range (0, len(valueToWrite)):
                data.append(valueToWrite[i]&0xFF)      
            self.tcpClientSocket.send(data)
            bytesToRead = 12
            data = self.tcpClientSocket.recv(bytesToRead)
            if ((data[1] == 0x8F) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x8F) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x8F) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x8F) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");

            return True 
           

    def WriteMultipleRegisters(self, startingAddress, values):
        """
        Write multiple registers to Master device (Function code 16)
        startingAddress: First register to be written
        values:  Register Values [0..quantity-1] to be written
        """
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened");
        functionCode = 16
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = (startingAddress&0xFF00) >> 8
        quantityLSB = len(values)&0xFF
        quantityMSB = (len(values)&0xFF00) >> 8
        valueToWrite = list()
        for i in range(0, len(values)):
            valueToWrite.append(values[i]);    
        if (self.ser is not None):       
            data = bytearray([self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB, quantityMSB, quantityLSB] )
            data.append(len(valueToWrite)*2)   #Bytecount 
            for i in range (0, len(valueToWrite)):                 
                data.append((valueToWrite[i]&0xFF00) >> 8) 
                data.append(valueToWrite[i]&0xFF) 
            CRC = self.__calculateCRC(data, len(data), 0)
            CrcLSB = CRC&0xFF
            CrcMSB = (CRC&0xFF00) >> 8
            data.append(CrcLSB)
            data.append(CrcMSB)
            self.ser.write(data)
            bytesToRead = 8
            data = self.ser.read(bytesToRead)
            if ((data[1] == 0x90) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x90) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x90) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x90) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            if data[1] == self._unitIdentifier:
                return True 
            else:
                return False     
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self._unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB, quantityMSB, quantityLSB] )
            data.append(len(valueToWrite)*2)   #Bytecount 
            for i in range (0, len(valueToWrite)):                 
                data.append((valueToWrite[i]&0xFF00) >> 8) 
                data.append(valueToWrite[i]&0xFF) 
            
            self.tcpClientSocket.send(data)
            bytesToRead = 12
            data = self.tcpClientSocket.recv(bytesToRead)
            if ((data[1] == 0x90) & (data[2] == 0x01)):
                raise Exceptions.FunctionCodeNotSupportedException("Function code not supported by master");
            if ((data[1] == 0x90) & (data[2] == 0x02)):
                raise Exceptions.StartingAddressInvalidException("Starting address invalid or starting address + quantity invalid");
            if ((data[1] == 0x90) & (data[2] == 0x03)):
                raise Exceptions.QuantityInvalidException("quantity invalid");
            if ((data[1] == 0x90) & (data[2] == 0x04)):
                raise Exceptions.ModbusException("error reading");
            return True            
  
    def __calculateCRC(self, data, numberOfBytes, startByte):
        crc = 0xFFFF
        for x in range(0, numberOfBytes):
            crc = crc ^ data[x]
            for _ in range(0, 8):
                if ((crc & 0x0001) != 0):
                    crc = crc >> 1
                    crc = crc ^ 0xA001
                else:
                    crc = crc >> 1                 
        return crc
   
    @property
    def Port(self):
        """
        Gets the Port were the Modbus-TCP Server is reachable (Standard is 502)
        """
        return self._port
    
    @Port.setter
    def Port(self, port):
        """
        Sets the Port were the Modbus-TCP Server is reachable (Standard is 502)
        """
        self._port = port;
    
    @property
    def IPAddress(self):
        """
        Gets the IP-Address of the Server to be connected
        """
        return self._ipAddress
    
    @IPAddress.setter
    def IPAddress(self, ipAddress):
        """
        Sets the IP-Address of the Server to be connected
        """
        self._ipAddress = ipAddress;   
    
    @property
    def UnitIdentifier(self):
        """
        Gets the Unit identifier in case of serial connection (Default = 1)
        """
        return self._unitIdentifier
    
    @UnitIdentifier.setter
    def UnitIdentifier(self, unitIdentifier):
        """
        Sets the Unit identifier in case of serial connection (Default = 1)
        """
        self._unitIdentifier = unitIdentifier
    
    @property
    def Baudrate(self):
        """
        Gets the Baudrate for serial connection (Default = 9600)
        """
        return self._baudrate
    
    @Baudrate.setter
    def Baudrate(self, baudrate):
        """
        Sets the Baudrate for serial connection (Default = 9600)
        """
        self._baudrate = baudrate
    
    @property
    def Parity(self):
        """
        Gets the of Parity in case of serial connection
        """
        return self._parity
    
    @Parity.setter
    def Parity(self, parity):
        """
        Sets the of Parity in case of serial connection
        Example modbusClient.Parity = Parity.even
        """
        self._parity = parity
    
    @property
    def Stopbits(self):
        """
        Gets the number of stopbits in case of serial connection
        """
        return self._stopbits
    
    @Stopbits.setter
    def Stopbits(self, stopbits):
        """
        Sets the number of stopbits in case of serial connection
        Example: modbusClient.Stopbits = Stopbits.one
        """
        self._stopbits = stopbits
        
    
    def isConnected(self):
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
      
    """
    Convert 32 Bit Value to two 16 Bit Value to send as Modbus Registers
    doubleValue: Value to be converted
    return: 16 Bit Register values int[]
    """  
def ConvertDoubleToTwoRegisters(doubleValue: int) -> list:
    myList = list()
    myList.append(int(doubleValue & 0x0000FFFF))         #Append Least Significant Word      
    myList.append(int((doubleValue & 0xFFFF0000)>>16))   #Append Most Significant Word      

    return myList
    
    """
    Convert 32 Bit real Value to two 16 Bit Value to send as Modbus Registers
    floatValue: Value to be converted
    return: 16 Bit Register values int[]
    """  
def ConvertFloatToTwoRegisters(floatValue: float) -> list:
    myList = list()
    s = struct.pack('<f', floatValue)       #little endian
    myList.append(s[0] | (s[1]<<8))         #Append Least Significant Word  
    myList.append(s[2] | (s[3]<<8))         #Append Most Significant Word      

    return myList

    """
    Convert two 16 Bit Registers to 32 Bit long value - Used to receive 32 Bit values from Modbus (Modbus Registers are 16 Bit long)
    registers: 16 Bit Registers
    return: 32 bit value
    """  
def ConvertRegistersToDouble(registers: list) -> int:
    returnValue = (int(registers[0]) & 0x0000FFFF) | (int((registers[1])<<16) & 0xFFFF0000)
    return returnValue

    """
    Convert two 16 Bit Registers to 32 Bit real value - Used to receive float values from Modbus (Modbus Registers are 16 Bit long)
    registers: 16 Bit Registers
    return: 32 bit value real
    """  
def ConvertRegistersToFloat(registers: list) -> float:
    b = bytearray(4)
    b [0] = registers[0] & 0xff
    b [1] = (registers[0] & 0xff00)>>8 
    b [2] = (registers[1] & 0xff)
    b [3] = (registers[1] & 0xff00)>>8
    returnValue = struct.unpack('<f', b)            #little Endian
    return returnValue
