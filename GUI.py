ip = "146.136.39.137"
port = 50024

from OST import CouplingMeasurer

instrument = CouplingMeasurer(f"TCPIP::{ip}::{port}::SOCKET", read_termination="\n", write_termination="\n")

import streamlit as st
from streamlit_extras.grid import grid

st.set_page_config(page_title="Coupling Measurements", layout="wide")

g = grid([2, 8, .5, 1.5], vertical_align='bottom')

g.empty()
g.title("Coupling Measurements")
g.empty()
g.button("Measure", on_click=instrument.measure, args=(), key="measure_button")
