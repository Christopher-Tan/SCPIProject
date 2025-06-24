ip = "146.136.90.15"
port = 50024

from OST import CouplingMeasurer

instrument = CouplingMeasurer(f"TCPIP::{ip}::{port}::SOCKET", read_termination="\n", write_termination="\n")

import streamlit as st

st.set_page_config(page_title="Coupling Measurements", layout="wide")

st.title("Coupling Measurements")

