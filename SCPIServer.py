import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 50024))
s.listen(1)

while True:
    conn, _ = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            cmd = data.decode().strip()
            print(cmd)
            if cmd == "*IDN?":
                conn.sendall("Raspberry Pi\n".encode())