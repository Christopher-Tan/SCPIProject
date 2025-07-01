"""SCPI Server for transformer coupling measurements.

Attributes:
    measurements (Measurements): An instance of the Measurements class to hold measurement data.
    parser (SCPIParser): An instance of the SCPIParser to handle SCPI commands
"""

import socket
from CouplingMeasurement import Measurements
from SCPIParser import SCPIParser

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 50024))
    s.listen(1)

    while True:
        conn, _ = s.accept()
        try:
            with conn:
                measurements = [Measurements()]
                new_measurement = Measurements()
                parser = SCPIParser({
                    ":MEASure:COUPling:K?": lambda measurement=-1: measurements[measurement].k,
                    ":MEASure:COUPling:K1?": lambda measurement=-1: measurements[measurement].k1,
                    ":MEASure:COUPling:K2?": lambda measurement=-1: measurements[measurement].k2,
                    ":MEASure:COUPling:LS1Prim?": lambda measurement=-1: measurements[measurement].Ls1_prim,
                    ":MEASure:COUPling:LM?": lambda measurement=-1: measurements[measurement].Lm,
                    ":MEASure:COUPling:LS2Prim?": lambda measurement=-1: measurements[measurement].Ls2_prim,
                    ":MEASure:COUPling:LS?": lambda measurement=-1: measurements[measurement].Ls,
                    ":MEASure:COUPling:LP?": lambda measurement=-1: measurements[measurement].Lp,
                    ":MEASure:COUPling:N?": lambda measurement=-1: measurements[measurement].N,
                    ":MEASure:COUPling:FREQuency?": lambda measurement=-1: measurements[measurement].freq,
                    ":MEASure:COUPling:VOLTage?": lambda measurement=-1: measurements[measurement].voltLvl,
                    ":MEASure:COUPling:NPRIMary?": lambda measurement=-1: measurements[measurement].nPrim,
                    ":MEASure:COUPling:NSECondary?": lambda measurement=-1: measurements[measurement].nSec,
                    ":MEASure:COUPling:V1?": lambda measurement=-1: measurements[measurement].v1,
                    ":MEASure:COUPling:V2?": lambda measurement=-1: measurements[measurement].v2,
                    ":MEASure:COUPling:L1?": lambda measurement=-1: measurements[measurement].L1,
                    ":MEASure:COUPling:L2?": lambda measurement=-1: measurements[measurement].L2,
                    ":MEASure:COUPling?": lambda measurement=-1: measurements[measurement],
                    ":MEASure[:COUPling]": lambda: [new_measurement.measure(), measurements.append(new_measurement), new_measurement := Measurements()],
                    ":MEASure:COUPling:FREQuency": lambda freq: setattr(new_measurement, 'freq', float(freq)),
                    ":MEASure:COUPling:VOLTage": lambda volt: setattr(new_measurement, 'voltLvl', float(volt)),
                    ":MEASure:COUPling:NPRIMary": lambda nPrim: setattr(new_measurement, 'nPrim', int(nPrim)),
                    ":MEASure:COUPling:NSECondary": lambda nSec: setattr(new_measurement, 'nSec', int(nSec)),
                    ":MEASure:COUPling:NUMBer?": lambda: len(measurements) - 1,
                    "*IDN?": lambda: "Raspberry Pi",
                    "*RST": lambda: (measurements := [Measurements()]),
                    
                })
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    data = data.decode()
                    for line in data.split('\n'):
                        cmd = line.strip()
                        print(cmd)
                        response = parser.execute(cmd)
                        if cmd.endswith('?'):
                            conn.sendall(str(response).encode() + b'\n')
        except Exception as e:
            print(f"Error: {e}")