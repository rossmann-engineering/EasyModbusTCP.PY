import logging
from dataclasses import dataclass
from enum import Enum, IntEnum
import modbus_exception as exceptions
import modbus_exception


class ModbusType(Enum):
    TCP = 0
    RTU = 1
    UDP = 2
    ASCII = 3


class FunctionCode(IntEnum):
    READ_COILS = 1
    READ_DISCRETE_INPUTS = 2
    READ_HOLDING_REGISTERS = 3
    READ_INPUT_REGISTERS = 4
    WRITE_SINGLE_COIL = 5
    WRITE_SINGLE_REGISTER = 6
    READ_EXCEPTION_STATUS = 7
    DIAGNOSTICS = 8
    GET_COMM_EVENT_COUNTER = 11
    GET_COMM_EVENT_LOG = 12
    WRITE_MULTIPLE_COILS = 15
    WRITE_MULTIPLE_REGISTERS = 16
    REPORT_SERVER_ID = 17
    READ_FILE_RECORD = 20
    WRITE_FILE_RECORD = 21
    MASK_WRITE_REGISTER = 22
    READ_WRITE_MULTIPLE_REGISTERS = 23
    READ_FIFO_QUEUE = 24
    ENCAPSULATED_INTERFACE_TRANSPORT = 43


class ExceptionCodes(IntEnum):
    ILLEGAL_FUNCTION = 1
    ILLEGAL_DATA_ADDRESS = 2
    ILLEGAL_DATA_VALUE = 3
    SERVER_DEVICE_FAILURE = 4
    ACKNOWLEDGE = 5
    SERVER_DEVICE_BUSY = 6
    MEMORY_PARITY_ERROR = 8
    GATEWAY_PATH_UNAVAILABLE = 10
    GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 11

@dataclass
class MBAPHeader:
    """
    Dataclass which represents the MBAP (Modbus Application protocol) Header for Modbus TCP
    transaction_identifier(2 Bytes): Identification of a MODBUS Request / Response transaction.
    protocol_identifier(2 Bytes): 0 = MODBUS protocol
    length(2 Bytes): Number of following bytes
    unit_identifier(1 Byte): Only needed for routing purposes, if pure Modbus TCP is used it should be set to 0xff
    """
    transaction_identifier: int = 0
    length: int = 0
    unit_identifier: int = 0xFF
    protocol_identifier: int = 0

    def encode(self):
        transaction_identifier_lsb = self.transaction_identifier & 0xFF
        transaction_identifier_msb = ((self.transaction_identifier & 0xFF00) >> 8)
        length_lsb = self.length & 0xFF
        length_msb = (self.length & 0xFF00) >> 8
        protocol_identifier_lsb = self.protocol_identifier & 0xFF
        protocol_identifier_msb = ((self.protocol_identifier & 0xFF00) >> 8)
        return bytearray(
            [transaction_identifier_msb, transaction_identifier_lsb, protocol_identifier_msb, protocol_identifier_lsb,
             length_msb, length_lsb, self.unit_identifier])

    def decode(self, data: bytearray):
        self.transaction_identifier = data[1] | (data[0] << 8)
        self.protocol_identifier = data[3] | (data[2] << 8)
        self.length = data[5] | (data[4] << 8)
        self.unit_identifier = data[6]

@dataclass
class PDU:
    """
    Dataclass which represents the PDU (Protocol Data Unit) - Both for Modbus RTU and Modbus TCP
    function_code(1 Byte): Service specified by the Function code
    """
    function_code: FunctionCode = FunctionCode.READ_COILS
    data: bytearray = bytearray()
    def encode(self):
        return_value = bytearray()
        return_value.append(self.function_code)
        return_value.extend(self.data)
        return return_value

    def decode(self, data):
        self.function_code = data[0]
        if self.function_code >= 128:
            exception_code = data[1]
            if exception_code == 1:
                raise exceptions.FunctionCodeNotSupportedException("Function code not supported by master")
            elif exception_code == 2:
                raise exceptions.StartingAddressInvalidException(
                    "Starting address invalid or starting address + quantity invalid")
            elif exception_code == 3:
                raise exceptions.QuantityInvalidException("quantity invalid")
            elif exception_code == 4:
                raise exceptions.ModbusException("error reading")

        self.data = data[1:len(data)]

@dataclass
class ADU:
    """
    Dataclass which represents the ADU (Application Data Unit) - Both for Modbus RTU and Modbus TCP
    mbap_header: only relevant for Modbus TCP
    pdu: both for Modbus TCP and RTU
    crc: Error check only relevant for Modbus RTU
    """
    mbap_header: MBAPHeader = MBAPHeader()
    pdu: PDU = PDU()
    crc: int = 0
    def encode(self, modbus_type: ModbusType):
        return_value = bytearray()
        if modbus_type == ModbusType.TCP:
            return_value.extend(self.mbap_header.encode())
        if modbus_type == ModbusType.RTU:
            return_value.append(self.mbap_header.unit_identifier)

        return_value.extend(self.pdu.encode())
        if modbus_type == ModbusType.RTU:
            self.crc = self.__calculate_crc(return_value, len(return_value), 0)
            crc_lsb = self.crc & 0xFF
            crc_msb = (self.crc & 0xFF00) >> 8
            return_value.append(crc_lsb)
            return_value.append(crc_msb)
        logging.debug("---------Transmit: {0}"
                      .format(str(return_value.hex(' '))))
        return return_value

    def decode(self, modbus_type: ModbusType, data: bytearray):
        logging.debug("---------Receive: {0}"
                      .format(str(data.hex(' '))))
        if modbus_type == ModbusType.TCP:
            self.mbap_header.decode(data)
            self.pdu.decode(data[7:len(data)])
        if modbus_type == ModbusType.RTU:
            self.pdu.decode(data[1:(len(data)-2)])
            crc = self.__calculate_crc(data, len(data) - 2, 0)
            crc_lsb = crc & 0xFF
            crc_msb = (crc & 0xFF00) >> 8
            if (crc_lsb != data[len(data) - 2]) & (crc_msb != data[len(data) - 1]):
                raise exceptions.CRCCheckFailedException("CRC check failed")

    @staticmethod
    def __calculate_crc(data, number_of_bytes, start_byte):
        crc = 0xFFFF
        for x in range(0, number_of_bytes):
            crc = crc ^ data[x]
            for _ in range(0, 8):
                if (crc & 0x0001) != 0:
                    crc = crc >> 1
                    crc = crc ^ 0xA001
                else:
                    crc = crc >> 1
        return crc