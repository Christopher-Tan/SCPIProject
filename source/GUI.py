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

    st.set_page_config(page_title="Coupling Measurements", layout="wide")

    def fetch():
        if instrument:
            st.session_state['voltage'] = instrument.voltage
            st.session_state['frequency'] = instrument.frequency
            st.session_state['nPrim'] = instrument.nPrim
            st.session_state['nSec'] = instrument.nSec
            
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

    g = grid([2, 8, 3, 3], [1, 1, 1, 1, 4], vertical_align='center')

    g.empty()
    g.title("Coupling Measurements")
    if g.button("Measure", args=(), key="measure_button"):
        try:
            instrument.measure()
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

    try:
        instrument.voltage = g.number_input("Voltage", key="voltage")
        instrument.frequency = g.number_input("Frequency", key="frequency")
        instrument.nPrim = g.number_input("nPrim", key="nPrim")
        instrument.nSec = g.number_input("nSec", key="nSec")
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