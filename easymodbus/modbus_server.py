import socket
import ModbusException
import ADU

class ModbusServer():

    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 1502
        self.holding_registers = [None] * 2048

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(self.read_holding_registers(data, conn))

    def read_holding_registers(self, receive_data, con):
        transaction_identifier = receive_data[1] & (receive_data[0] << 8)
        protocol_identifier = receive_data[3] & (receive_data[2] << 8)
        length = receive_data[5] & (receive_data[4] << 8)
        unit_identifier = receive_data[6]
        function_code = receive_data[7]
        starting_address = receive_data[9] & (receive_data[8] << 8)
        quantity = receive_data[11] & (receive_data[10] << 8)

        transaction_identifier_msb = ((transaction_identifier & 0xFF00) >> 8)
        transaction_identifier_lsb = transaction_identifier & 0xFF
        protocol_identifier_msb = ((protocol_identifier & 0xFF00) >> 8)
        protocol_identifier_lsb = protocol_identifier & 0xFF
        length = 3 + (2 * quantity)
        length_msb = ((length & 0xFF00) >> 8)
        length_lsb = length & 0xFF
        byte_count = 2 * quantity

        send_data = [transaction_identifier_msb, transaction_identifier_lsb,
                     protocol_identifier_msb, protocol_identifier_lsb,
                     length_msb, length_lsb, unit_identifier, function_code, byte_count,
                     ]

        for i in range(byte_count):
            send_data.append(([starting_address * 2 + 2 + i] & 0xFF00) >> 8)
            send_data.append([starting_address * 2 + 2 + i] & 0xFF)
        return send_data



if __name__ == '__main__':
    modbus_server = ModbusServer()
    modbus_server.listen()