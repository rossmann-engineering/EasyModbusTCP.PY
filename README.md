## EasyModbusTCP - THE standard library for Modbus RTU and Modbus TCP

Visit www.EayModbusTCP.net for more informations and Codesamples

### Installation:

pip install EasyModbus

### Requirements:

Python 2.7  
Python 3.6

pyserial (only for Modbus RTU)

### Table of Contents
1. [Supported Function codes](#functioncodes)
2. [Examples](#examples)  
   2.1. [Example 1 (Read two Holding Registres from Siemens S7-1200 via Modbus-TCP)](#example1)
3. [Library Documentation](#documentation)  
   3.1 [Methods](#methods) 


<div id="functioncodes"/>

### Supported Function codes 

- Read Coils (FC1)
- Read Discrete Inputs (FC2)
- Read Holding Registers (FC3)
- Read Input Registers (FC4)
- Write Single Coil (FC5)
- Write Single Register (FC6)
- Write Multiple Coils (FC15)
- Write Multiple Registers (FC16)

<div id="examples"/>

### Get started - Examples

All examples are available in the folder "examples" in the Git-Repository

<div id="example1"/>

#### Example 1 (Read two Holding Registres from Modbus-TCP Server)
First we create an instance of a Modbus-TCP class (Server IP-Address and Port)
Then we Read 2 Holding Registers from the Server.  
IMPORTANT: Usually there is a Register shift between the request and the server address range
The Server address Range starts with address "1" but the Request that is sent starts with "0"
In the example method call we read Register 1 and 2 (Because register "0" does not exist)
Please check the documentation of your device (or try it out)


```python
import easymodbus.modbusClient

#create an instance of a Modbus-TCP class (Server IP-Address and Port) and connect
modbus_client = easymodbus.modbusClient.ModbusClient('192.168.178.110', 502)
modbus_client.connect()

#The first argument is the starting registers, the second argument is the quantity.
register_values = modbus_client.read_holdingregisters(0, 2)

print("Value of Register #1:" + str(register_values[0]))
print("Value of Register #2:" + str(register_values[1])) 

#Close the Port
modbus_client.close()
```

<div id="documentation"/>

### Library Documentation

Class:  ModbusClient

<div id="methods"/>

#### Methods

**Constructor def \_\_init__(self, \*params)**

<u>Constructor for Modbus RTU (serial line):</u>
modbusClient = ModbusClient.ModbusClient(‘COM1’)
First Parameter is the serial Port

<u>Constructor for Modbus TCP:</u>
modbusClient = ModbusClient.ModbusClient(‘127.0.0.1’, 502)
First Parameter ist the IP-Address of the Server to connect to
Second Parameter is the Port the Server listens to

**def connect(self)**

Connects to a Modbus-TCP Server or a Modbus-RTU Slave with the given Parameters

**def close(self)**

Closes Serial port, or TCP-Socket connection

**def read_discreteinputs(self, starting_address, quantity)**

Read Discrete Inputs from Server device (Function code 2)  
starting_address: First discrete input to read  
quantity: Number of discrete Inputs to read  
returns: List of bool values [0..quantity-1] which contains the discrete Inputs  

**def read_coils(self, starting_address, quantity)**

Read Coils from Server device (Function code 1)  
starting_address: First coil to read  
quantity: Number of coils to read  
returns: List of bool values [0..quantity-1] which contains the coils  

**def read_holdingregisters(self, starting_address, quantity)**

Read Holding Registers from Server device (Function code 3)  
starting_address: First Holding Register to read  
quantity: Number of Holding Registers to read  
returns: List of int values [0..quantity-1] which contains the registers 

**def read_inputregisters(self, starting_address, quantity)**

Read Input Registers from Server device (Function code 4)  
starting_address: First Input Register to read  
quantity: Number of Input Registers to read  
returns: List of int values [0..quantity-1] which contains the registers 

**def write_single_coil(self, starting_address, value)**

Write single Coil to Server device (Function code 5)  
starting_address: Coil to write  
value: Boolean value to write

**def write_single_register(self, starting_address, value)**

Write single Holding Register to Server device (Function code 6)  
starting_address: Holding Register to write  
value: int value to write

**def write_multiple_coils(self, starting_address, values)**

Write multiple Coils to Server device (Function code 15)  
starting_address: First coil to write  
value: List of Boolean values to write

**def write_multiple_registers(self, starting_address, values)**

Write multiple Holding Registers to Server device (Function code 16)  
starting_address: First Holding Register to write  
value: List of int values to write