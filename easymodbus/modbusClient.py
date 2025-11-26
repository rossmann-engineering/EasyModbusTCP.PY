from modbus_client import ModbusClient
from modbus_client import Parity, Stopbits, RegisterOrder
from modbus_client import (convert_double_to_two_registers, convert_registers_to_double,
                           convert_registers_to_float, convert_float_to_two_registers)
import warnings
warnings.warn("deprecated, use 'modbus_client' instead", DeprecationWarning)
