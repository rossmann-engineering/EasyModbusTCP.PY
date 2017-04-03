#!/usr/bin/env python
'''
Created on 12.09.2016

@author: Stefan Rossmann
'''
import ModbusClient
    
modbusClient = ModbusClient.ModbusClient('127.0.0.1',502)
modbusClient.Connect()
discreteInputs = modbusClient.ReadDiscreteInputs(0, 8)
print (discreteInputs)

holdingRegisters = modbusClient.ReadHoldingRegisters(0, 8)
print (holdingRegisters)
inputRegisters = modbusClient.ReadInputRegisters(0, 8)
print (inputRegisters)
coils = modbusClient.ReadCoils(0, 8)
print (coils)
modbusClient.WriteSingleCoil(0, True)
modbusClient.WriteSingleRegister(0, 777)
modbusClient.WriteMultipleCoils(0, [True,True,True,True,True,False,True])
modbusClient.WriteMultipleRegisters(0, [1,2,3,4,5,6,7,8])
modbusClient.close()