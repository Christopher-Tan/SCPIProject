ip = "146.136.39.137"
port = 50024

import streamlit as st
from streamlit_extras.grid import grid
from streamlit_navigation_bar import st_navbar

st.set_page_config(page_title="Coupling Measurements", layout="wide")



from OST import CouplingMeasurer
if 'instrument' not in st.session_state:
    try:
        instrument = CouplingMeasurer(f"TCPIP::{ip}::{port}::SOCKET", read_termination="\n", write_termination="\n")
        st.session_state['instrument'] = instrument
        st.success(f"Connected to {instrument.id}.")
    except Exception as e:
        instrument = None
        st.error(f"Failed to connect to the instrument at {ip}:{port}. Please check the connection and try again.")
else:
    instrument = st.session_state['instrument']

g = grid([2, 8, 3, 3], vertical_align='center')

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
    except Exception as e:
        print(e)
        st.session_state.pop('instrument', None)
        st.error(f"Failed to connect to and reset the instrument")

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
    match n:
        case "Raw Data":
            data = {
                'L1': instrument.L1,
                'L2': instrument.L2,
                'k1': instrument.k1,
                'v1': instrument.v1,
                'v2': instrument.v2,
            }
        case "T-Model":
            data = {
                'Ls1_prim': instrument.Ls1_prim,
                'Lm': instrument.Lm,
                'Ls2_prim': instrument.Ls2_prim,
            }
        case "Gamma-Model":
            data = {
                'Ls': instrument.Ls,
                'Lp': instrument.Lp,
                'k': instrument.k,
                'k1': instrument.k1,
                'k2': instrument.k2,
                'N': instrument.N,
            }
except Exception as e:
    print(e)
    data = {}

st.table(data)