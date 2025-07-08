"""SCPI Server for transformer coupling measurements.

Attributes:
    measurements (Measurements): An instance of the Measurements class to hold measurement data.
    parser (SCPIParser): An instance of the SCPIParser to handle SCPI commands
"""

import socket
from CouplingMeasurement import Measurements
from SCPIParser import SCPIParser
from copy import copy

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
                
                def measure():
                    """Perform a measurement and update the new_measurement instance."""
                    new_measurement.measure()
                    measurements.append(copy(new_measurement))
                    
                parser = SCPIParser({
                    ":MEASure:HISTory:COUPling:K?": lambda measurement=-1: measurements[measurement].k,
                    ":MEASure:HISTory:COUPling:K1?": lambda measurement=-1: measurements[measurement].k1,
                    ":MEASure:HISTory:COUPling:K2?": lambda measurement=-1: measurements[measurement].k2,
                    ":MEASure:HISTory:COUPling:LS1Prim?": lambda measurement=-1: measurements[measurement].Ls1_prim,
                    ":MEASure:HISTory:COUPling:LM?": lambda measurement=-1: measurements[measurement].Lm,
                    ":MEASure:HISTory:COUPling:LS2Prim?": lambda measurement=-1: measurements[measurement].Ls2_prim,
                    ":MEASure:HISTory:COUPling:LS?": lambda measurement=-1: measurements[measurement].Ls,
                    ":MEASure:HISTory:COUPling:LP?": lambda measurement=-1: measurements[measurement].Lp,
                    ":MEASure:HISTory:COUPling:N?": lambda measurement=-1: measurements[measurement].N,
                    ":MEASure:HISTory:COUPling:FREQuency?": lambda measurement=-1: measurements[measurement].freq,
                    ":MEASure:HISTory:COUPling:VOLTage?": lambda measurement=-1: measurements[measurement].voltLvl,
                    ":MEASure:HISTory:COUPling:NPRIMary?": lambda measurement=-1: measurements[measurement].nPrim,
                    ":MEASure:HISTory:COUPling:NSECondary?": lambda measurement=-1: measurements[measurement].nSec,
                    ":MEASure:HISTory:COUPling:V1?": lambda measurement=-1: measurements[measurement].v1,
                    ":MEASure:HISTory:COUPling:V2?": lambda measurement=-1: measurements[measurement].v2,
                    ":MEASure:HISTory:COUPling:L1?": lambda measurement=-1: measurements[measurement].L1,
                    ":MEASure:HISTory:COUPling:L2?": lambda measurement=-1: measurements[measurement].L2,
                    ":MEASure:HISTory:COUPling?": lambda measurement=-1: measurements[measurement],
                    
                    ":MEASure[:COUPling]": measure,
                    ":MEASure:COUPling:FREQuency": lambda freq: setattr(new_measurement, 'freq', float(freq)),
                    ":MEASure:COUPling:VOLTage": lambda volt: setattr(new_measurement, 'voltLvl', float(volt)),
                    ":MEASure:COUPling:NPRIMary": lambda nPrim: setattr(new_measurement, 'nPrim', int(nPrim)),
                    ":MEASure:COUPling:NSECondary": lambda nSec: setattr(new_measurement, 'nSec', int(nSec)),
                    ":MEASure:COUPling:FREQuency?": lambda: new_measurement.freq,
                    ":MEASure:COUPling:VOLTage?": lambda: new_measurement.voltLvl,
                    ":MEASure:COUPling:NPRIMary?": lambda: new_measurement.nPrim,
                    ":MEASure:COUPling:NSECondary?": lambda: new_measurement.nSec,
                    
                    ":MEASure:HISTory:COUPling:NUMBer?": lambda: len(measurements) - 1,
                    "*IDN?": lambda: "Raspberry Pi",
                    "*RST": new_measurement.__init__,
                    
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
                        if response is not None:
                            conn.sendall(str(response).encode() + b'\n')
        except Exception as e:
            print(f"Error: {e}")