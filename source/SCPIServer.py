"""SCPI Server for transformer coupling measurements.

Attributes:
    measurements (Measurements): An instance of the Measurements class to hold measurement data.
    parser (SCPIParser): An instance of the SCPIParser to handle SCPI commands
"""

import socket
from CouplingMeasurement import Measurements
from SCPIParser import SCPIParser
from copy import copy

import os
import yaml
with open(os.path.join(os.path.dirname(__file__), "config.yaml"), 'r') as file:
    config = yaml.safe_load(file)

import traceback

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 50024))
    import threading

    s.listen(2)  # Allow up to 2 clients to connect

    _default_object = Measurements()
    _default_object.freq = ''
    _default_object.voltLvl = ''
    _default_object.nPrim = ''
    _default_object.nSec = ''

    class UpdatingList(list):
        class Viewer:
            def __init__(self, parent_list, start_index, default_object=_default_object):
                self._parent_list = parent_list
                self._start_index = start_index
                self._default_object = default_object

            def __getitem__(self, index):
                if index < 0:
                    raise IndexError("Index out of range")
                if index == 0:
                    return self._default_object
                return self._parent_list[self._start_index + index - 1]

            def __len__(self):
                return len(self._parent_list) - self._start_index

        def __init__(self, *args):
            super().__init__(*args)
            self._viewers = []

        def create_viewer(self):
            viewer = self.Viewer(self, len(self))
            self._viewers.append(viewer)
            return viewer

        def update_viewers(self):
            min_index = len(self)
            if self._viewers:
                min_index = min([viewer._start_index for viewer in self._viewers])
            self[:] = self[min_index:]
            for viewer in self._viewers:
                viewer._start_index -= min_index

        def remove_viewer(self, viewer):
            self._viewers.remove(viewer)
            self.update_viewers()
            
        def append(self, object):
            super().append(object)
            self.update_viewers()
            
    measurement_list = UpdatingList()
    new_measurement = Measurements()
    
    from collections import deque

    def handle_client(conn):
        errors = deque(maxlen=10)
        try:
            with conn:
                measurements = measurement_list.create_viewer()
                def measure():
                    """Perform a measurement and update the new_measurement instance."""
                    new_measurement.measure()
                    measurements.append(copy(new_measurement))
                    
                parser = SCPIParser({
                    ":MEASure:HISTory:COUPling:K?": lambda measurement=0: measurements[measurement].k,
                    ":MEASure:HISTory:COUPling:K1?": lambda measurement=0: measurements[measurement].k1,
                    ":MEASure:HISTory:COUPling:K2?": lambda measurement=0: measurements[measurement].k2,
                    ":MEASure:HISTory:COUPling:LS1Prim?": lambda measurement=0: measurements[measurement].Ls1_prim,
                    ":MEASure:HISTory:COUPling:LM?": lambda measurement=0: measurements[measurement].Lm,
                    ":MEASure:HISTory:COUPling:LS2Prim?": lambda measurement=0: measurements[measurement].Ls2_prim,
                    ":MEASure:HISTory:COUPling:LS?": lambda measurement=0: measurements[measurement].Ls,
                    ":MEASure:HISTory:COUPling:LP?": lambda measurement=0: measurements[measurement].Lp,
                    ":MEASure:HISTory:COUPling:N?": lambda measurement=0: measurements[measurement].N,
                    ":MEASure:HISTory:COUPling:FREQuency?": lambda measurement=0: measurements[measurement].freq,
                    ":MEASure:HISTory:COUPling:VOLTage?": lambda measurement=0: measurements[measurement].voltLvl,
                    ":MEASure:HISTory:COUPling:NPRIMary?": lambda measurement=0: measurements[measurement].nPrim,
                    ":MEASure:HISTory:COUPling:NSECondary?": lambda measurement=0: measurements[measurement].nSec,
                    ":MEASure:HISTory:COUPling:v1_prim?": lambda measurement=0: measurements[measurement].v1_prim,
                    ":MEASure:HISTory:COUPling:v2_prim?": lambda measurement=0: measurements[measurement].v2_prim,
                    ":MEASure:HISTory:COUPling:v1_sec?": lambda measurement=0: measurements[measurement].v1_sec,
                    ":MEASure:HISTory:COUPling:v2_sec?": lambda measurement=0: measurements[measurement].v2_sec,
                    ":MEASure:HISTory:COUPling:L1?": lambda measurement=0: measurements[measurement].L1,
                    ":MEASure:HISTory:COUPling:L2?": lambda measurement=0: measurements[measurement].L2,
                    ":MEASure:HISTory:COUPling?": lambda measurement=0: measurements[measurement],
                    
                    ":MEASure[:COUPling]": measure,
                    ":MEASure:COUPling:FREQuency": lambda freq: setattr(new_measurement, 'freq', float(freq)) if (config['properties']['freq']['min'] is None or float(freq) >= config['properties']['freq']['min']) and (config['properties']['freq']['max'] is None or float(freq) <= config['properties']['freq']['max']) else errors.append(f"Frequency {freq} out of range"),
                    ":MEASure:COUPling:VOLTage": lambda volt: setattr(new_measurement, 'voltLvl', float(volt)) if (config['properties']['voltLvl']['min'] is None or float(volt) >= config['properties']['voltLvl']['min']) and (config['properties']['voltLvl']['max'] is None or float(volt) <= config['properties']['voltLvl']['max']) else errors.append(f"Voltage {volt} out of range"),
                    ":MEASure:COUPling:NPRIMary": lambda nPrim: setattr(new_measurement, 'nPrim', int(nPrim)) if (config['properties']['nPrim']['min'] is None or int(nPrim) >= config['properties']['nPrim']['min']) and (config['properties']['nPrim']['max'] is None or int(nPrim) <= config['properties']['nPrim']['max']) else errors.append(f"Primary turns {nPrim} out of range"),
                    ":MEASure:COUPling:NSECondary": lambda nSec: setattr(new_measurement, 'nSec', int(nSec)) if (config['properties']['nSec']['min'] is None or int(nSec) >= config['properties']['nSec']['min']) and (config['properties']['nSec']['max'] is None or int(nSec) <= config['properties']['nSec']['max']) else errors.append(f"Secondary turns {nSec} out of range"),
                    ":MEASure:COUPling:FREQuency?": lambda: new_measurement.freq,
                    ":MEASure:COUPling:VOLTage?": lambda: new_measurement.voltLvl,
                    ":MEASure:COUPling:NPRIMary?": lambda: new_measurement.nPrim,
                    ":MEASure:COUPling:NSECondary?": lambda: new_measurement.nSec,
                    
                    ":MEASure:HISTory:COUPling:NUMBer?": lambda: len(measurements),
                    "*IDN?": lambda: "Raspberry Pi",
                    "*RST": new_measurement.__init__,
                    ":SYSTem:ERRor?": lambda: errors.popleft() if errors else "0,No error",
                })
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    data = data.decode()
                    try:
                        for line in data.split('\n'):
                            cmd = line.strip()
                            print(cmd)
                            response = parser.execute(cmd)
                            if response is not None:
                                conn.sendall(str(response).encode() + b'\n')
                    except Exception as e:
                        tb = traceback.format_exc()
                        print(f"Error: {e}")
                        errors.append(f"-300,{e}\n{tb}")
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error: {e}")

    while True:
        conn, _ = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()