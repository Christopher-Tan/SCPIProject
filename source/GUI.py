"""This is the main GUI for the Coupling Measurer application.

Attributes:
    instrument (CouplingMeasurer): The instrument wrapper used for communication."""

ip = "PIIES002.ost.ch"
port = 50024

import sys

if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
    import streamlit as st
    from streamlit_extras.grid import grid
    from streamlit_navigation_bar import st_navbar
    
    from math import log10, floor, isclose
    
    metric_prefixes = {
        'y': 1e24, 
        'z': 1e21,
        'a': 1e18,
        'f': 1e15,
        'p': 1e12,
        'n': 1e9,
        'µ': 1e6,
        'm': 1e3,
        '': 1,
        'k': 1e3,
        'M': 1e6,
        'G': 1e9,
        'T': 1e12,
        'P': 1e15,
        'E': 1e18,
        'Z': 1e21,
        'Y': 1e24,
    }
    def replace_prefix(value, units, recognize_prefix=True, prefixes=metric_prefixes):
        scaling_factor = 1
        if value == 0:
            return value, units, scaling_factor
        
        prefixes = sorted(prefixes.items(), key=lambda x: len(x[0]), reverse=True)
        
        if recognize_prefix:
            for prefix, factor in prefixes:
                if prefix and units.startswith(prefix):
                    value *= factor
                    units = units[len(prefix):]
                    scaling_factor /= factor
                    break
        
        base_units = 10 ** (3 * floor(log10(value) + 1e-9) / 3)
        value /= base_units
        scaling_factor *= base_units
        for prefix, factor in prefixes:
            if isclose(factor, base_units):
                units = prefix + units
                return value, units, scaling_factor
        return value * base_units, units, scaling_factor
    
    def replace_suffix(value, units, recognize_suffix=True, suffix='s'):
        if recognize_suffix:
            if suffix and units.endswith(suffix):
                units = units[:-len(suffix)]
        
        if value >= 1 + 1e-9:
            units += suffix
        return value, units
    
    st.set_page_config(page_title="Coupling Measurements", layout="wide")
    
    if 'history' not in st.session_state:
        st.session_state['history'] = 0
        st.session_state['max_history'] = 0

    def fetch():
        if instrument:
            st.session_state['voltage'], st.session_state['voltage_units'], st.session_state['voltage_scaling'] = replace_prefix(instrument.voltage, "V")
            st.session_state['frequency'], st.session_state['frequency_units'], st.session_state['frequency_scaling'] = replace_prefix(instrument.frequency, "Hz")
            st.session_state['nPrim'], st.session_state['nPrim_units'] = replace_suffix(instrument.nPrim, "Turns")
            st.session_state['nSec'], st.session_state['nSec_units'] = replace_suffix(instrument.nSec, "Turns")
            st.session_state['history'] = int(instrument.n)
            st.session_state['max_history'] = int(instrument.n)
            
    from OST import CouplingMeasurer
    if 'instrument' not in st.session_state:
        try:
            instrument = CouplingMeasurer(f"TCPIP::{ip}::{port}::SOCKET", read_termination="\n", write_termination="\n", timeout=10000)
            st.session_state['instrument'] = instrument
            fetch()
            st.success(f"Connected to {instrument.id}.")
        except Exception as e:
            instrument = None
            st.error(f"Failed to connect to the instrument at {ip}:{port}. Please check the connection and try again.")
    else:
        instrument = st.session_state['instrument']

    g = grid([2, 8, 3, 3], [1, 1, 1, 1, 1, 1, 1, 1], vertical_align='center')

    g.empty()
    g.title("Coupling Measurements")
    if g.button("Measure", args=(), key="measure_button"):
        try:
            instrument.measure()
            fetch()
        except Exception as e:
            print(e)
            st.session_state.pop('instrument', None)
            st.error(f"Failed to connect to and perform a measurement on the instrument")

    if g.button("Reset", args=(), key="reset_button"):
        try:
            instrument.reset()
            fetch()
        except Exception as e:
            print(e)
            st.session_state.pop('instrument', None)
            st.error(f"Failed to connect to and reset the instrument")
            
    if "refresh_before" not in st.session_state:
        st.session_state["refresh_before"] = False
        st.session_state["refresh_after"] = False
        
    def refresh():
        st.session_state["refresh_after"] = True
        
    if st.session_state["refresh_after"]:
        st.session_state["refresh_after"] = False
        fetch()
    try:
        instrument.voltage = g.number_input("Voltage", key="voltage", format="%0.3f", on_change=refresh, step=1.0/st.session_state['voltage_scaling']) * st.session_state['voltage_scaling']
        g.write(st.session_state['voltage_units'])
        instrument.frequency = g.number_input("Frequency", key="frequency", format="%0.3f", on_change=refresh, step=1.0/st.session_state['frequency_scaling']) * st.session_state['frequency_scaling']
        g.write(st.session_state['frequency_units'])
        instrument.nPrim = g.number_input("nPrim", key="nPrim", on_change=refresh, step=1)
        g.write(st.session_state['nPrim_units'])
        instrument.nSec = g.number_input("nSec", key="nSec", on_change=refresh, step=1)
        g.write(st.session_state['nSec_units'])
        
        if st.session_state["refresh_after"]:
            st.session_state["refresh_after"] = False
            st.session_state["refresh_before"] = True
            st.rerun()
    except Exception as e:
        print(e)
        st.session_state.pop('instrument', None)
        st.error(f"Failed to connect to and set the instrument parameters")

    n = st_navbar(["Raw Data", "T-Model", "Gamma-Model"], adjust=False, styles={
            'nav': {
                'background-color': 'rgba(0, 0, 0, 0)',
                'margin': '0px',
                'padding': '0.5rem',
            },
            'div': {
                'background-color': 'rgba(0, 0, 0, 0.1)',
                'margin': '0px',
                'padding': '0.5rem 1rem',
                'border-radius': '4rem',
                'width': '320px',
            },
            'span': {
                'color': 'rgb(50, 50, 65)',
                'margin': '0px',
                'padding': '0px 1rem',
                'border-radius': '4rem',
                'width': '60px',
            },
            'active': {
                'background-color': 'rgb(255, 255, 255)',
            },
            'hover': {
                'background-color': 'rgb(255, 255, 255)',
            },
        }
    )
    try:
        if n == "Raw Data":
            data = {
                'L1': instrument.L1,
                'L2': instrument.L2,
                'k1': instrument.k1,
                'v1': instrument.v1,
                'v2': instrument.v2,
            }
        elif n == "T-Model":
            data = {
                'Ls1_prim': instrument.Ls1_prim,
                'Lm': instrument.Lm,
                'Ls2_prim': instrument.Ls2_prim,
            }
        elif n == "Gamma-Model":
            data = {
                'Ls': instrument.Ls,
                'Lp': instrument.Lp,
                'k': instrument.k,
                'k1': instrument.k1,
                'k2': instrument.k2,
                'N': instrument.N,
            }
        else:
            data = {}
    except Exception as e:
        print(e)
        data = {}

    st.table(data)
elif __name__ == "__main__":
    import subprocess
    import os
    
    process = subprocess.Popen(
        ["python", os.path.join(os.path.dirname(__file__), "SCPIClient.py")],
    )
    
    process.wait()