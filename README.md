## EasyModbusTCP - THE standard library for Modbus RTU and Modbus TCP

### Installation:

pip install EasyModbus

### Requirements:

Python 2.7  
Python 3.6

pyserial (only for Modbus RTU)

### Supported Function codes

- Read Coils (FC1)
- Read Discrete Inputs (FC2)
- Read Holding Registers (FC3)
- Read Input Registers (FC4)
- Write Single Coil (FC5)
- Write Single Register (FC6)
- Write Multiple Coils (FC15)
- Write Multiple Registers (FC16)

#### Get started - Example 1 (Read two Holding Registres from Modbus-TCP Server)
First we create an instance of a Modbus-TCP class (Server IP-Address and Port)
Then we Read 2 Holding Registers from the Server.  
IMPORTANT: Usually there is a Register shift between the request and the server address range
The Server address Range starts with address "1" but the Request that is sent starts with "0"
In the example method call we read Register 1 and 2 (Because register "0" does not exist)
Thats how it is specified, but unfortunatelly not always implemented as specified from some devices
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


####See the following codesamples in the "examples" folder:

Example 1.1: Data exchange to a Siemens S7 PLC - Simple Example which Read and Writes some Values to the PLC and Print it at the console

Visit www.EayModbusTCP.net for more informations and Codesamples