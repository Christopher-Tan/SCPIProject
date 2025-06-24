# import easy_scpi as scpi

ip = "146.136.90.15"
port = 50024

# inst = scpi.Instrument(
#     port=f"TCPIP::{ip}::{port}::SOCKET",
#     read_termination="\n",
#     write_termination="\n",
#     timeout=5000
# )

# inst.connect()
# print(inst.id)

# import socket

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((ip, port))
# s.send("*IDN?".encode())
# print(s.recv(1024).decode())

import pyvisa as visa

rm = visa.ResourceManager()
instr = rm.open_resource(
    f"TCPIP::{ip}::{port}::SOCKET",
    read_termination="\n",
    write_termination="\n"
)
r = instr.query("*IDN?")