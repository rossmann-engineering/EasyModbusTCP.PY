"""
Created on 18.12.2019
@author: Stefan Roßmann

Python 3.8

To install the Module: pip install EasyModbus

This example explains how to use the Modbus client module. We use Modbus-TCP to read and write data from and
to a Siemens S7 PLC. The Siemens PLC is an S7-1200 (6ES7211-1AE40-0XB0) with 4 digital outputs, 6 digital inputs and
1 analog input. The connection is established via the built-in Profinet interface.

This is a very common use case of the library to read out data from machines and systems and to send
them to cloud platforms.

Used Siemens CPU: CPU 1211C DC/DC/DC (6ES7 211-1AE40-0XB0) - FW: V 4.1.3
TIA-Portal V16
The Siemens S7 acts as Modbus-TCP Server (IP-Address 192.168.178.110)

Once the Function-Block MB_Server is called we can use Modbus Requests to Read and Write Digital and Analog In-Outs
Directly. They are mapped as follows:
Coils: 0...8191 mapped to Q0.0 to Q1023.7
Discrete Inputs: 0...8191 mapped to I0.0 to I1023.7
Input Registers: 0...1021 mapped to IW0 to IW1022
"""
import easymodbus.modbusClient
modbus_client = easymodbus.modbusClient.ModbusClient('192.168.178.110', 502)
modbus_client.connect()
modbus_client.write_single_register(0,140)                  #We write "140" to the first Holding Register
modbus_client.write_single_register(1,385)                  #We write "385" to the second Holding Register
register_values = modbus_client.read_holdingregisters(0,2)  #We Read 2 Holding Registers from the Server
print ("Value of Register #1:" + str(register_values[0]))    #Should be 140
print ("Value of Register #2:" + str(register_values[1]))    #Should be 385
                  #We write the First Digital Output to "True"
print ("Current State of DI0: " + str(modbus_client.read_discreteinputs(0,1)[0]))   #We Read the Current state of the First Digital Input

modbus_client.close()



