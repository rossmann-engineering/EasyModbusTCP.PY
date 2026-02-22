import datetime
import logging
import socket
import threading
import time
import traceback
from logging.handlers import RotatingFileHandler
import modbus_client
import modbus_exception
from modbus_protocol import FunctionCode, ModbusType ,ADU

class ModbusServer:

    def __init__(self):
        self.logging_level = logging.INFO
        self.host = '127.0.0.1'
        self.port = 502
        self.holding_registers = [0] * 65535
        self.input_registers = [0] * 65535
        self.coils = [False] * 65535
        self.discrete_inputs = [False] * 65535
        self.__adu = ADU()
        #self.listen()
        self.conn = None


    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:

                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                while True:
                        s.listen()
                        self.conn, addr = s.accept()
                        thread5 = threading.Thread(target=self.modbus_connection, args=(self.conn, addr))
                        thread5.daemon = True
                        thread5.start()

            except Exception:
                try:
                    s.shutdown(socket.SHUT_RDWR)
                    logging.info('Connection closed')
                except Exception:
                    pass
                s.close()
                logging.info('Connection closed')

                time.sleep(10)
                self.listen()

    def modbus_connection(self, conn, addr):
        with conn:
            logging.info(f"Connected by {addr}")
            connection_dt = datetime.datetime.utcnow()
            while True:
                try:
                    data = conn.recv(1024)

                    if datetime.datetime.utcnow() > (connection_dt + datetime.timedelta(seconds=5)):
                        try:
                            conn.close()
                            logging.info('Connection closed')
                        except Exception:
                            pass

                        break

                    if len(data) > 7:

                        self.__adu.decode(ModbusType.TCP, bytearray(data))
                        connection_dt = datetime.datetime.utcnow()
                        self.__execute_server_request()

                        bytes = bytearray(self.__adu.encode(ModbusType.TCP))


                        conn.sendall(bytes)
                except Exception:
                    print('Exception Modbus connection: ' + str(traceback.format_exc()))
                    conn.close()
                    break

    def close(self):
        logging.info('Closing Modbus Server')
        self.conn.close()

    def __execute_server_request(self):
        logging.info("got request" + str(self.__adu))
        starting_address = 0
        quantity = 0
        starting_address_msb = 0
        starting_address_lsb = 0
        if (self.__adu.pdu.function_code == FunctionCode.READ_COILS) | (
                self.__adu.pdu.function_code == FunctionCode.READ_DISCRETE_INPUTS) | (
                self.__adu.pdu.function_code == FunctionCode.READ_INPUT_REGISTERS) | (
                self.__adu.pdu.function_code == FunctionCode.READ_HOLDING_REGISTERS) | (
                self.__adu.pdu.function_code == FunctionCode.WRITE_SINGLE_REGISTER) | (
                self.__adu.pdu.function_code == FunctionCode.WRITE_SINGLE_COIL) | (
                self.__adu.pdu.function_code == FunctionCode.WRITE_MULTIPLE_COILS) | (
                self.__adu.pdu.function_code == FunctionCode.WRITE_MULTIPLE_REGISTERS) | (
                self.__adu.pdu.function_code == FunctionCode.READ_WRITE_MULTIPLE_REGISTERS):
            starting_address_lsb = self.__adu.pdu.data[1]
            starting_address_msb = self.__adu.pdu.data[0]
            starting_address = starting_address_lsb | (starting_address_msb << 8)

            quantity_lsb = self.__adu.pdu.data[3]
            quantity_msb = self.__adu.pdu.data[2]
            quantity = quantity_lsb | (quantity_msb << 8)


        if (self.__adu.pdu.function_code == FunctionCode.READ_COILS) | (
                self.__adu.pdu.function_code == FunctionCode.READ_DISCRETE_INPUTS):
            if (quantity % 8) == 0:
                byte_count = quantity // 8
            else:
                byte_count = quantity // 8 + 1

            length = 3 + byte_count
            length_msb = ((length & 0xFF00) >> 8)
            length_lsb = length & 0xFF
        if self.__adu.pdu.function_code == FunctionCode.READ_COILS:
            send_coil_values = list()
            self.__adu.pdu.data = bytearray()
            self.__adu.pdu.data.append(byte_count)
            for g in range(quantity):
                send_coil_values.append(self.coils[starting_address + 1 + g])

            for i in range(byte_count):
                byte_data = 0
                for j in range(8):
                    if send_coil_values[i * 8 + j]:
                        bool_value = 1
                    else:
                        bool_value = 0
                    byte_data = byte_data | (bool_value << j)
                    if (i * 8 + j + 1) >= quantity:
                        break
                self.__adu.pdu.data.append(byte_data)

        elif self.__adu.pdu.function_code == FunctionCode.READ_DISCRETE_INPUTS:
            send_discrete_input_values = list()
            self.__adu.pdu.data = bytearray()
            self.__adu.pdu.data.append(byte_count)
            for g in range(quantity):
                send_discrete_input_values.append(self.discrete_inputs[starting_address + 1 + g])

            for i in range(byte_count):
                byte_data = 0
                for j in range(8):
                    if send_discrete_input_values[i * 8 + j]:
                        bool_value = 1
                    else:
                        bool_value = 0
                    byte_data = byte_data | (bool_value << j)
                    if (i * 8 + j + 1) >= quantity:
                        break
                self.__adu.pdu.data.append(byte_data)

        elif self.__adu.pdu.function_code == FunctionCode.READ_HOLDING_REGISTERS:
            self.__adu.pdu.data = bytearray()
            byte_count = 2 * quantity
            self.__adu.pdu.data.append(byte_count)



            for i in range(quantity):
                self.__adu.pdu.data.append((self.holding_registers[starting_address + i + 1] & 0xFF00) >> 8)
                self.__adu.pdu.data.append((self.holding_registers[starting_address + i + 1] & 0xFF))

        elif self.__adu.pdu.function_code == FunctionCode.READ_INPUT_REGISTERS:
            self.__adu.pdu.data = bytearray()
            byte_count = 2 * quantity
            self.__adu.pdu.data.append(byte_count)
            for i in range(quantity):
                self.__adu.pdu.data.append((self.input_registers[starting_address + i + 1] & 0xFF00) >> 8)
                self.__adu.pdu.data.append((self.input_registers[starting_address + i + 1] & 0xFF))

        elif self.__adu.pdu.function_code == FunctionCode.WRITE_SINGLE_REGISTER:
            register_value = self.__adu.pdu.data[3] | (self.__adu.pdu.data[2] << 8)
            self.__adu.pdu.data = bytearray()
            self.input_registers[starting_address + 1] = register_value
            self.__adu.pdu.data.append(starting_address_msb)
            self.__adu.pdu.data.append(starting_address_lsb)
            value_lsb = register_value & 0xFF
            value_msb = (register_value & 0xFF00) >> 8
            self.__adu.pdu.data.append(value_msb)
            self.__adu.pdu.data.append(value_lsb)
        elif self.__adu.pdu.function_code == FunctionCode.WRITE_SINGLE_COIL:
            register_value = self.__adu.pdu.data[3] | (self.__adu.pdu.data[2] << 8)
            self.__adu.pdu.data = bytearray()
            if register_value > 0:
                self.coils[starting_address + 1] = True
            else:
                self.coils[starting_address + 1] = False
            self.__adu.pdu.data.append(starting_address_msb)
            self.__adu.pdu.data.append(starting_address_lsb)
            value_lsb = register_value & 0xFF
            value_msb = (register_value & 0xFF00) >> 8
            self.__adu.pdu.data.append(value_msb)
            self.__adu.pdu.data.append(value_lsb)
        elif self.__adu.pdu.function_code == FunctionCode.WRITE_MULTIPLE_REGISTERS:
            for i in range(quantity):
                register_value = self.__adu.pdu.data[6+2*i] | (self.__adu.pdu.data[5+2*i] << 8)
                self.holding_registers[starting_address + 1 + i] = register_value
            self.__adu.pdu.data = bytearray()
            self.__adu.pdu.data.append(starting_address_msb)
            self.__adu.pdu.data.append(starting_address_lsb)
            self.__adu.pdu.data.append(quantity_msb)
            self.__adu.pdu.data.append(quantity_lsb)
        elif self.__adu.pdu.function_code == FunctionCode.WRITE_MULTIPLE_COILS:
            for i in range(quantity):
                shift = i % 16
                mask = 0x1
                mask = mask << (shift)
                if self.__adu.pdu.data[round((i / 16)+5)] & mask == 0:

                    self.coils[starting_address + i + 1] = False
                else:
                    self.coils[starting_address + i + 1] = True
            self.__adu.pdu.data = bytearray()
            self.__adu.pdu.data.append(starting_address_msb)
            self.__adu.pdu.data.append(starting_address_lsb)
            self.__adu.pdu.data.append(quantity_msb)
            self.__adu.pdu.data.append(quantity_lsb)
        else:
            raise modbus_exception.FunctionCodeNotSupportedException(
                'The function code received in the query is not an allowable action for the server')

    @property
    def logging_level(self):
        """
        Sets the logging level - Default is logging.INFO
        """
        return self.__logging_level

    @logging_level.setter
    def logging_level(self, logging_level):
        """
        Sets the logging level - Default is logging.INFO
        """
        self.__logging_level = logging_level
        logging.getLogger().setLevel(self.__logging_level)

    @property
    def debug(self):
        """
        Enables/disables debug mode
        """
        return self.__debug

    @debug.setter
    def debug(self, debug):
        """
        Enables/disables debug mode
        """
        self.__debug = debug
        if self.__debug:
            logging.getLogger().setLevel(self.__logging_level)
            # Add the log message handler to the logger
            handler1 = logging.handlers.RotatingFileHandler(
                'logdata.txt', maxBytes=2000000, backupCount=5)
            logging.getLogger().addHandler(handler1)
            formatter1 = logging.Formatter("%(asctime)s;%(message)s",
                                           "%Y-%m-%d %H:%M:%S")
            handler1.setFormatter(formatter1)

class RegisterOrder:
    lowHigh = 0
    highLow = 1



if __name__ == '__main__':
    modbus_server = ModbusServer()
    modbus_server.logging_level = logging.DEBUG
    modbus_server.coils[1] = True
    modbus_server.listen()
