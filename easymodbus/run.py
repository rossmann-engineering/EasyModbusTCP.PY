#!/usr/bin/env python
'''
Created on 12.09.2016

@author: Stefan Rossmann
'''

# @UnresolvedImport
from easymodbus.modbusClient import *
# @UnresolvedImport
    
modbusClient = ModbusClient('127.0.0.1', 502)
#modbusClient = ModbusClient('COM4')
modbusClient.parity = Parity.even
modbusClient.unitidentifier = 2
modbusClient.baudrate = 9600
modbusClient.stopbits = Stopbits.one
modbusClient.connect()
discreteInputs = modbusClient.read_discreteinputs(0, 8)
print (discreteInputs)

holdingRegisters = convert_registers_to_float(modbusClient.read_holdingregisters(0, 2))
print (holdingRegisters)
inputRegisters = modbusClient.read_inputregisters(0, 8)
print (inputRegisters)
coils = modbusClient.read_coils(0, 8)
print (coils)

modbusClient.write_single_coil(0, True)
modbusClient.write_single_register(0, 777)
modbusClient.write_multiple_coils(0, [True,True,True,True,True,False,True,True])
modbusClient.write_multiple_registers(0, convert_float_to_two_registers(3.141517))
modbusClient.close()