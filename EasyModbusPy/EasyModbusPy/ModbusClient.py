'''
Created on 12.09.2016

@author: Stefan Rossmann
'''
import serial
import Exceptions
import socket
from builtins import int
from _testcapi import instancemethod

class ModbusClient(object):
    '''
    classdocs
    '''  
    def __init__(self, *params):
        self.__transactionIdentifier=0
        self.ser = None
        self.tcpClientSocket = None
        #Constructor for RTU
        if len(params) == 1 & isinstance(params[0], str):
            self.serialPort = params[0]
            self.baudrate = 9600
            self.parity = Parity.even
            self.stopbits = Stopbits.one
            self.__transactionIdentifier = 0
            self.ser = serial.Serial()
        #Constructor for TCP
        if (len(params) == 2) & isinstance(params[0], str) & isinstance(params[1], int):
            self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ipAddress = params[0]
            self.port = params[1]
            
            
    def Connect(self):    
        if (self.ser is not None):   
            self.ser.port = self.serialPort
            self.ser.baudrate = self.baudrate
            self.stopbits = Stopbits.one
            self.ser.timeout = 1
            self.parity = Parity.none
            if self.stopbits == 0:               
                self.ser.stopbits = serial.STOPBITS_ONE
            elif self.stopbits == 1:               
                self.ser.stopbits = serial.STOPBITS_TWO
            elif self.stopbits == 2:               
                self.ser.stopbits = serial.STOPBITS_ONE_POINT_FIVE         
            if self.parity == 0:               
                self.ser.parity = serial.PARITY_EVEN
            elif self.parity == 1:               
                self.ser.parity = serial.PARITY_EVEN
            elif self.parity == 2:               
                self.ser.parity = serial.PARITY_EVEN 
            self.ser.open()
        if (self.tcpClientSocket is not None):  
            self.tcpClientSocket.connect((self.ipAddress, self.port))
  
    def close(self):
        if (self.ser is not None):
            self.ser.close()
        if (self.tcpClientSocket is not None):
            self.tcpClientSocket.close()
        
            
    def ReadDiscreteInputs(self, startingAddress, quantity):
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (startingAddress > 65535 | quantity >2000):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 2000");
        self.unitIdentifier = 1
        functionCode = 2
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = startingAddress&0xFF00 >> 8
        quatityLSB = quantity&0xFF
        quatityMSB = (quantity&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB,0,0] )
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
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB] )
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
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (startingAddress > 65535 | quantity >2000):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 2000");
        self.unitIdentifier = 1
        functionCode = 1
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = startingAddress&0xFF00 >> 8
        quatityLSB = quantity&0xFF
        quatityMSB = (quantity&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB,0,0] )
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
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB] )
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
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        if (startingAddress > 65535 | quantity >125):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 125");
        self.unitIdentifier = 1
        functionCode = 3
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = startingAddress&0xFF00 >> 8
        quatityLSB = quantity&0xFF
        quatityMSB = (quantity&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB,0,0] )
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
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB] )
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
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened");
        if (startingAddress > 65535 | quantity >125):
            raise ValueError("Starting address must be 0 - 65535; quantity must be 0 - 125");
        self.unitIdentifier = 1
        functionCode = 4
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = startingAddress&0xFF00 >> 8
        quatityLSB = quantity&0xFF
        quatityMSB = (quantity&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB,0,0] )
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
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,quatityMSB,quatityLSB] )
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
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        self.unitIdentifier = 1
        functionCode = 5
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = startingAddress&0xFF00 >> 8
        if value:
            valueLSB = 0x00
            valueMSB = (0xFF00) >> 8
        else:
            valueLSB = 0x00
            valueMSB = (0x00) >> 8
        if (self.ser is not None):
            data = bytearray([self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,valueMSB,valueLSB,0,0] )
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
            if data[1] == self.unitIdentifier:
                return True 
            else:
                return False  
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,valueMSB,valueLSB] )
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
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened")
        self.unitIdentifier = 1
        functionCode = 6
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = startingAddress&0xFF00 >> 8
        valueLSB = value&0xFF
        valueMSB = (value&0xFF00) >> 8
        if (self.ser is not None):
            data = bytearray([self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,valueMSB,valueLSB,0,0] )
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
            if data[1] == self.unitIdentifier:
                return True 
            else:
                return False   
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB,valueMSB,valueLSB] )
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
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened");
        self.unitIdentifier = 1
        functionCode = 15
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = startingAddress&0xFF00 >> 8
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
            data = bytearray([self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB, quantityMSB, quantityLSB] )
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
            if data[1] == self.unitIdentifier:
                return True 
            else:
                return False 
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB, quantityMSB, quantityLSB] )
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
        self.__transactionIdentifier+=1
        if (self.ser is not None):
            if (self.ser.closed):
                raise Exception.SerialPortNotOpenedException("serial port not opened");
        self.unitIdentifier = 1
        functionCode = 16
        length = 6;
        transactionIdentifierLSB = self.__transactionIdentifier&0xFF
        transactionIdentifierMSB = ((self.__transactionIdentifier&0xFF00) >> 8)
        lengthLSB = length&0xFF
        lengthMSB = (length&0xFF00) >> 8
        startingAddressLSB = startingAddress&0xFF
        startingAddressMSB = startingAddress&0xFF00 >> 8
        quantityLSB = len(values)&0xFF
        quantityMSB = (len(values)&0xFF00) >> 8
        valueToWrite = list()
        for i in range(0, len(values)):
            valueToWrite.append(values[i]);    
        if (self.ser is not None):       
            data = bytearray([self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB, quantityMSB, quantityLSB] )
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
            if data[1] == self.unitIdentifier:
                return True 
            else:
                return False     
        else:
            protocolIdentifierLSB = 0x00;
            protocolIdentifierMSB = 0x00;
            lengthLSB = 0x06;
            lengthMSB = 0x00;
            data = bytearray([transactionIdentifierMSB, transactionIdentifierLSB, protocolIdentifierMSB, protocolIdentifierLSB,lengthMSB,lengthLSB,self.unitIdentifier, functionCode, startingAddressMSB, startingAddressLSB, quantityMSB, quantityLSB] )
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

               

class Parity():
    even = 0
    odd = 1
    none = 2
    
class Stopbits():
    one = 0
    two = 1
    onePointFive = 2
