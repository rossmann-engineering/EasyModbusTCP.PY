## EasyModbusTCP - THE standard library for Modbus RTU and Modbus TCP

Visit www.EasyModbusTCP.net for more informations and Codesamples

### Table of Contents
1. [Installation](#installation)
2. [Supported Function codes](#functioncodes)  
3. [Basic Usage](#basicusage)  
   3.1. [Instantiation](#instatiation)  
   3.2. [Connect](#connect)  
   3.3. [Close connection](#close)  
   3.4. [Read values](#readvalues)  
   3.5. [Write single values](#writesinglevalues)  
4. [Examples](#examples)  
   4.1. [Example 1 (Read two Holding Registres from Siemens S7-1200 via Modbus-TCP)](#example1)  
5. [Library Documentation](#documentation)  
   5.1 [Methods](#methods)  
   5.2 [Properties](#properties)  
   5.3 [Helper functions](#functions)

<div id="installation"/>

### 1. Installation:

pip install EasyModbus

### Requirements:

>Python 3.8

pyserial (only for Modbus RTU)


<div id="functioncodes"/>

### 2. Supported Function codes 

- Read Coils (FC1)
- Read Discrete Inputs (FC2)
- Read Holding Registers (FC3)
- Read Input Registers (FC4)
- Write Single Coil (FC5)
- Write Single Register (FC6)
- Write Multiple Coils (FC15)
- Write Multiple Registers (FC16)

<div id="basicusage"/>

### 3. Basic usage

<div id="instantiation"/>

#### 3.1 Instantiate ModbusClient class

The arguments passed during the instantiation are important in order to differentiate between Modbus RTU (via the serial interface) and Modbus TCP (via Ethernet).  
If an argument is passed during the instantiation, it is the serial interface that is used with Modbus RTU (e.g. 'COM1' or '/dev/ttyUSB0').
Two arguments must be passed for Modbus TCP. This is the IP address and the port (usually 502)  

Example for **Modbus RTU**  
```python
import easymodbus.modbus_client
modbus_client = easymodbus.modbus_client.ModbusClient('/dev/ttyUSB0')
```

Example for **Modbus TCP**  
```python
import easymodbus.modbus_client
modbus_client = easymodbus.modbus_client.ModbusClient('192.168.178.52', 502)
```

<div id="connect"/>

#### 3.2 Connect

To connect to a Modbus-TCP Server or to a Modbus-RTU Slave simply use the "connect" Method. If Modbus-RTU is used, make sure to set the properties for serial connection (Baudrate, Parity, Stopbits), if they differ from the default values, **before** the "connect" Method is executed. 

```python
modbus_client.connect()
```

<div id="close"/>

#### 3.3 Close connection

To close the connection to a Modbus-TCP Server or to a Modbus-RTU Slave simply use the "close" Method.

```python
modbus_client.close()
```

<div id="readvalues"/>

#### 3.4 Read Values

The following functioncodes are used to read values from the remote device (Modbus-TCP Server or Modbus-RTU Client)

- Read Coils (FC1) - Method "read_coils"
- Read Discrete Inputs (FC2) - Method "read_discrete_inputs"
- Read Holding Registers (FC3) - Method "read_holding_registers"
- Read Input Registers (FC4) - Method "read_input_registers"

IMPORTANT: Usually there is a Register shift between the request and the server address range
The Server address Range starts with address "1" but the Request that is sent starts with "0"
In the example method call we read Register 1 and 2 (Because register "0" does not exist)
Please check the documentation of your device (or try it out)

```python
import easymodbus.modbus_client

#create an instance of a Modbus-TCP class (Server IP-Address and Port) and connect
modbus_client = easymodbus.modbus_client.ModbusClient('192.168.178.110', 502)
modbus_client.connect()

#The first argument is the starting address, the second argument is the quantity.
coils = modbus_client.read_coils(0, 2)	#Read coils 1 and 2 from server 
discrete_inputs = modbus_client.read_discrete_inputs(10, 10)	#Read discrete inputs 11 to 20 from server 
input_registers = modbus_client.read_input_registers(0, 10)	#Read input registers 1 to 10 from server 
holding_registers = modbus_client.read_holding_registers(0, 5)	#Read holding registers 1 to 5 from server 
modbus_client.close()
```

<div id="writesinglevalues"/>

#### 3.5 Write single Values

The following functioncodes are used to write single values (Holding Registers or Coils) from the remote device (Modbus-TCP Server or Modbus-RTU Client)

- Write Single Coil (FC5) - Method "write_single_coil"
- Write Single Register (FC6) - Method "write_single_register"

IMPORTANT: Usually there is a Register shift between the request and the server address range
The Server address Range starts with address "1" but the Request that is sent starts with "0"
In the example method call we write to Register 1 (Because register "0" does not exist)
Please check the documentation of your device (or try it out)

```python
import easymodbus.modbus_client

#create an instance of a Modbus-TCP class (Server IP-Address and Port) and connect
modbus_client = easymodbus.modbus_client.ModbusClient('192.168.178.110', 502)
modbus_client.connect()

holding_register_value = 115
coil_value = True
#The first argument is the address, the second argument is the value.
modbus_client.write_single_register(0, holding_register_value)	#Write value "115" to Holding Register 1 
modbus_client.write_single_coil(10, coil_value)	#Set Coil 11 to True
modbus_client.close()
```

<div id="examples"/>

### 4. Get started - Examples

All examples are available in the folder "examples" in the Git-Repository

<div id="example1"/>

#### 4.1 Example 1 (Read two Holding Registers from Modbus-TCP Server)
First we create an instance of a Modbus-TCP class (Server IP-Address and Port)
Then we Read 2 Holding Registers from the Server.  
IMPORTANT: Usually there is a Register shift between the request and the server address range
The Server address Range starts with address "1" but the Request that is sent starts with "0"
In the example method call we read Register 1 and 2 (Because register "0" does not exist)
Please check the documentation of your device (or try it out)


```python
import easymodbus.modbus_client

#create an instance of a Modbus-TCP class (Server IP-Address and Port) and connect
modbus_client = easymodbus.modbus_client.ModbusClient('192.168.178.110', 502)
modbus_client.connect()

#The first argument is the starting registers, the second argument is the quantity.
register_values = modbus_client.read_holdingregisters(0, 2)

print("Value of Register #1:" + str(register_values[0]))
print("Value of Register #2:" + str(register_values[1])) 

#Close the Port
modbus_client.close()
```

<div id="documentation"/>

### 5. Library Documentation

Class:  ModbusClient

<div id="methods"/>

#### 5.1 Methods

**Constructor def \_\_init__(self, \*params)**

<u>Constructor for Modbus RTU (serial line):</u>
modbusClient = modbus_client.ModbusClient(‘COM1’)
First Parameter is the serial Port

<u>Constructor for Modbus TCP:</u>
modbusClient = modbus_client.ModbusClient(‘127.0.0.1’, 502)
First Parameter ist the IP-Address of the Server to connect to
Second Parameter is the Port the Server listens to

**def connect(self)**

Connects to a Modbus-TCP Server or a Modbus-RTU Slave with the given Parameters

**def close(self)**

Closes Serial port, or TCP-Socket connection

**def read_discrete_inputs(self, starting_address, quantity)**

Read Discrete Inputs from Server device (Function code 2)  
starting_address: First discrete input to read  
quantity: Number of discrete Inputs to read  
returns: List of bool values [0..quantity-1] which contains the discrete Inputs  

**def read_coils(self, starting_address, quantity)**

Read Coils from Server device (Function code 1)  
starting_address: First coil to read  
quantity: Number of coils to read  
returns: List of bool values [0..quantity-1] which contains the coils  

**def read_holding_registers(self, starting_address, quantity)**

Read Holding Registers from Server device (Function code 3)  
starting_address: First Holding Register to read  
quantity: Number of Holding Registers to read  
returns: List of int values [0..quantity-1] which contains the registers 

**def read_input_registers(self, starting_address, quantity)**

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

**def read_discreteinputs(self, starting_address, quantity)**

deprecated - Use "read_discrete_inputs" instead

**def read_holdingregisters(self, starting_address, quantity)**

deprecated - Use "read_holding_registers" instead

**def read_inputregisters(self, starting_address, quantity)**

deprecated - Use "read_input_registers" instead

<div id="properties"/>

#### 5.2 Properties

**port**

Datatype: int  
Port were the Modbus-TCP Server is reachable (Standard is 502)

**ipaddress**

Datatype: str  
IP-Address of the Server to be connected

**unitidentifier**

Datatype: int  
Unit identifier in case of serial connection (Default = 1)

**baudrate**

Datatype: int  
Baudrate for serial connection (Default = 9600)

**parity**

Datatype: int  
Parity in case of serial connection 
The Helper class "Parity" can be used to define the parity (Default = Parity.even)  
For example: modbus_client.parity = easymodbus.modbusClient.Parity.odd  
Possible values are:
even = 0  
odd = 1  
none = 2  

**stopbits**

Datatype: int  
Stopbits in case of serial connection (Default = Stopbits.one) 
The Helper class "Stopbits" can be used to define the number of stopbits  
For example: modbus_client.stopbits = easymodbus.modbusClient.Stopbits.one  
Possible values are:
one = 0  
two = 1  
onePointFive = 2  

**timeout**

Datatype: int  
Max. time before an Exception is thrown (Default = 5)  

**is_connected**

Datatype: bool  
Returns true if a connection has been established (only read)

**debug**

Datatype: bool  
Enables/disables debug mode - In debug mode Request and Response and depending in the logging level the RAW-Data are displayed at the console output and stored in a logfile "logdata.txt"  
Disabled at default

**logging_level**
 
Sets or gets the logging level. Default value is logging.INFO. In this Request and Response including arguments are logged (if debug is enabled)  
if the level is set to logging.DEBUG also the RAW data transmitted and received are logged for debugging purposes.  
The are logged at the console output and stored in logfile.txt 


<div id="functions"/>

#### 5.3 Helper functions

**def convert_double_to_two_registers(doubleValue, register_order=RegisterOrder.lowHigh)**

Convert 32 Bit Value to two 16 Bit Value to send as Modbus Registers  
doubleValue: Value to be converted  
register_order: Desired Word Order (Low Register first or High Register first - Default: RegisterOrder.lowHigh  
return: 16 Bit Register values int[]  

**def convert_float_to_two_registers(floatValue, register_order=RegisterOrder.lowHigh)**

Convert 32 Bit real Value to two 16 Bit Value to send as Modbus Registers  
floatValue: Value to be converted  
register_order: Desired Word Order (Low Register first or High Register first - Default: RegisterOrder.lowHigh  
return: 16 Bit Register values int[]  

**def convert_registers_to_double(registers, register_order=RegisterOrder.lowHigh)**

Convert two 16 Bit Registers to 32 Bit long value - Used to receive 32 Bit values from Modbus (Modbus Registers are 16 Bit long)  
registers: 16 Bit Registers  
register_order: Desired Word Order (Low Register first or High Register first - Default: RegisterOrder.lowHigh  
return: 32 bit value  

**def convert_registers_to_float(registers, register_order=RegisterOrder.lowHigh)**

Convert two 16 Bit Registers to 32 Bit real value - Used to receive float values from Modbus (Modbus Registers are 16 Bit long)  
registers: 16 Bit Registers  
register_order: Desired Word Order (Low Register first or High Register first - Default: RegisterOrder.lowHigh  
return: 32 bit value real 