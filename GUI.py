ip = "146.136.39.137"
port = 50024

import streamlit as st
from streamlit_extras.grid import grid
from streamlit_navigation_bar import st_navbar

st.set_page_config(page_title="Coupling Measurements", layout="wide")



from OST import CouplingMeasurer
instrument = CouplingMeasurer(f"TCPIP::{ip}::{port}::SOCKET", read_termination="\n", write_termination="\n")
g = grid([2, 8, 3, 3], vertical_align='center')

g.empty()
g.title("Coupling Measurements")
if g.button("Measure", args=(), key="measure_button"):
    try:
        instrument.measure()
    except Exception as e:
        print(e)
        st.error(f"Failed to connect to and perform a measurement on the instrument")

if g.button("Reset", args=(), key="reset_button"):
    try:
        instrument.reset()
    except Exception as e:
        print(e)
        st.error(f"Failed to connect to and reset the instrument")

n = st_navbar(["Raw Data", "T-Model", "Gamma-Model"], styles={
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