import socket
from CouplingMeasurement import Measurements
from SCPIParser import SCPIParser

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 50024))
s.listen(1)

while True:
    conn, _ = s.accept()
    try:
        with conn:
            measurements = Measurements()
            parser = SCPIParser({
                ":MEASure:COUPling:K?": lambda: measurements.k,
                ":MEASure:COUPling:K1?": lambda: measurements.k1,
                ":MEASure:COUPling:K2?": lambda: measurements.k2,
                ":MEASure:COUPling:LS1Prim?": lambda: measurements.Ls1_prim,
                ":MEASure:COUPling:LM?": lambda: measurements.Lm,
                ":MEASure:COUPling:LS2Prim?": lambda: measurements.Ls2_prim,
                ":MEASure:COUPling:LS?": lambda: measurements.Ls,
                ":MEASure:COUPling:LP?": lambda: measurements.Lp,
                ":MEASure:COUPling:N?": lambda: measurements.N,
                ":MEASure[:COUPling]": measurements.measure,
                ":MEASure:COUPling:FREQuency?": lambda: measurements.freq,
                ":MEASure:COUPling:FREQuency": lambda freq: setattr(measurements, 'freq', float(freq)),
                ":MEASure:COUPling:VOLTage?": lambda: measurements.voltLvl,
                ":MEASure:COUPling:VOLTage": lambda volt: setattr(measurements, 'voltLvl', float(volt)),
                ":MEASure:COUPling:NPRIMary?": lambda: measurements.nPrim,
                ":MEASure:COUPling:NPRIMary": lambda nPrim: setattr(measurements, 'nPrim', int(nPrim)),
                ":MEASure:COUPling:NSECondary?": lambda: measurements.nSec,
                ":MEASure:COUPling:NSECondary": lambda nSec: setattr(measurements, 'nSec', int(nSec)),
                ":MEASure:COUPling:V1?": lambda: measurements.v1,
                ":MEASure:COUPling:V2?": lambda: measurements.v2,
                ":MEASure:COUPling:L1?": lambda: measurements.L1,
                ":MEASure:COUPling:L2?": lambda: measurements.L2,
                ":MEASure:COUPling?": lambda: measurements,
                "*IDN?": lambda: "Raspberry Pi",
                "*RST": measurements.__init__,
            })
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                cmd = data.decode().strip()
                print(cmd)
                response = parser.execute(cmd)
                if cmd.endswith('?'):
                    conn.sendall(str(response).encode() + b'\n')
    except Exception as e:
        print(f"Error: {e}")