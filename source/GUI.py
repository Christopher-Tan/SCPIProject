"""This is the main GUI for the Coupling Measurer application.

Attributes:
    instrument (CouplingMeasurer): The instrument wrapper used for communication."""

import yaml
import sys
import os

with open(os.path.join(os.path.dirname(__file__), "config.yaml"), 'r') as file:
    config = yaml.safe_load(file)
    
ip = config['ip']
port = config['port']
properties = config['properties']

if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
    import streamlit as st
    from streamlit_extras.grid import grid
    from streamlit_navigation_bar import st_navbar
    
    from math import log10, floor, isclose
    
    def cleanup():
        try:
            instrument.adapter.close()
        except:
            pass
    
    from streamlit.runtime.scriptrunner import add_script_run_ctx
    from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
    
    from streamlit.runtime import get_instance
    
    import threading
    
    def heartbeat(user):
        thread = threading.Timer(interval=2, function=heartbeat, args=(user,)) # prepare to run in new thread, this current thread will be killed then
        add_script_run_ctx(thread) # inject current main thread context into the to-be-started new thread
    
        ctx = get_script_run_ctx() # fetch own context variables, explicitly for analysis
        
        runtime = get_instance() # main runtime with all instances, including myself
        
        if runtime.is_active_session(session_id=ctx.session_id):
            thread.start() # actually start the new thread to keep this heartbeat going
        else:
            return cleanup()
    
    if "heartbeat" not in st.session_state:
        heartbeat(get_script_run_ctx().session_id)
        st.session_state["heartbeat"] = True
        
    if not config['developerMode']:
        st.markdown("""
            <style>
                .stAppHeader {
                    display: none;
                }
            </style>
        """, unsafe_allow_html=True)
        
    st.markdown("""
        <style>
            h1 {
                padding: 0px !important;
            }
            .block-container {
                padding-top: 0.4rem;
                padding-bottom: 1rem;
                padding-left: 4rem;
                padding-right: 4rem;
            }
        </style>
    """, unsafe_allow_html=True)
    metric_prefixes = {
        'y': 1e-24, 
        'z': 1e-21,
        'a': 1e-18,
        'f': 1e-15,
        'p': 1e-12,
        'n': 1e-9,
        'µ': 1e-6,
        'm': 1e-3,
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
        
        base_units = 10 ** (3 * floor((log10(abs(value)) + 1e-9) / 3))
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
        
        if not isclose(value, 1):
            units += suffix
        return value, units
    
    st.set_page_config(page_title="Coupling Measurements", layout="wide")
    
    if 'history' not in st.session_state:
        st.session_state['history'] = 0
        st.session_state['max_history'] = 0

    def fetch():
        if instrument:
            st.session_state['voltage'], st.session_state['voltage_units'], st.session_state['voltage_scaling'] = replace_prefix(instrument.voltage, properties['voltLvl']['units'])
            st.session_state['frequency'], st.session_state['frequency_units'], st.session_state['frequency_scaling'] = replace_prefix(instrument.frequency, properties['freq']['units'])
            st.session_state['nPrim'], st.session_state['nPrim_units'] = replace_suffix(instrument.nPrim, properties['nPrim']['units'])
            st.session_state['nSec'], st.session_state['nSec_units'] = replace_suffix(instrument.nSec, properties['nSec']['units'])
            nn = int(instrument.n)
            if nn != st.session_state['max_history']:
                st.session_state['history'] = nn
                st.session_state['max_history'] = nn
            
    from OST import CouplingMeasurer
    if 'instrument' not in st.session_state:
        try:
            with st.spinner("Connecting...", show_time=True):
                instrument = CouplingMeasurer(f"TCPIP::{ip}::{port}::SOCKET", read_termination="\n", write_termination="\n", timeout=10000)
            st.session_state['instrument'] = instrument
            fetch()
            st.toast(f"Connected to {instrument.id}.")
        except Exception as e:
            instrument = None
            #st.error(f"Failed to connect to the instrument at {ip}:{port}. Please check the connection and try again.")
    else:
        instrument = st.session_state['instrument']

    g = grid([6, 1.8, 1.8], vertical_align='center')

    g.title("Coupling Measurements")
    if g.button("Measure", args=(), key="measure_button"):
        try:
            with st.spinner("Waiting for measurement to complete...", show_time=True):
                instrument.measure()
            fetch()
        except Exception as e:
            print(e)
            st.session_state.pop('instrument', None)
            #st.error(f"Failed to connect to and perform a measurement on the instrument")

    if g.button("Reset", args=(), key="reset_button"):
        try:
            instrument.reset()
            fetch()
        except Exception as e:
            print(e)
            st.session_state.pop('instrument', None)
            #st.error(f"Failed to connect to and reset the instrument")
            
    if "refresh_before" not in st.session_state:
        st.session_state["refresh_before"] = False
        
    if "refresh_after" not in st.session_state:
        st.session_state["refresh_after"] = False
        
    def refresh():
        st.session_state["refresh_after"] = True
        
    if st.session_state["refresh_before"]:
        st.session_state["refresh_before"] = False
        fetch()
        
    g = grid([0.86, 0.6, 0.86, 0.6, 0.86, 0.6, 0.86, 0.6], vertical_align='bottom')
    try:
        instrument.voltage = g.number_input("Voltage", key="voltage", format="%0.3f", on_change=refresh, step=1.0/st.session_state['voltage_scaling'], min_value=properties['voltLvl']['min']/st.session_state['voltage_scaling'], max_value=properties['voltLvl']['max']/st.session_state['voltage_scaling']) * st.session_state['voltage_scaling']
        g.write(st.session_state['voltage_units'])
        instrument.frequency = g.number_input("Frequency", key="frequency", format="%0.3f", on_change=refresh, step=1.0/st.session_state['frequency_scaling'], min_value=properties['freq']['min']/st.session_state['frequency_scaling'], max_value=properties['freq']['max']/st.session_state['frequency_scaling']) * st.session_state['frequency_scaling']
        g.write(st.session_state['frequency_units'])
        instrument.nPrim = g.number_input("nPrim", key="nPrim", on_change=refresh, step=1, min_value=properties['nPrim']['min'], max_value=properties['nPrim']['max'])
        g.write(st.session_state['nPrim_units'])
        instrument.nSec = g.number_input("nSec", key="nSec", on_change=refresh, step=1, min_value=properties['nSec']['min'], max_value=properties['nSec']['max'])
        g.write(st.session_state['nSec_units'])
        
        if st.session_state["refresh_after"]:
            st.session_state["refresh_after"] = False
            st.session_state["refresh_before"] = True
            st.rerun()
    except Exception as e:
        print(e)
        st.session_state.pop('instrument', None)
        #st.error(f"Failed to connect to and set the instrument parameters")
        
    if "n" not in st.session_state:
        st.session_state["n"] = "Raw Data"

    n = st_navbar(["Raw Data", "T-Model", "Gamma-Model"], selected=st.session_state["n"], adjust=False, styles={
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
    
    if n and n != st.session_state["n"]:
        st.session_state["n"] = n
        st.rerun()

    n = st.session_state["n"]
    
    import schemdraw
    import schemdraw.elements as elm
    
    from io import BytesIO
    
    def render(diagram):
        buf = BytesIO()
        diagram.save(buf, dpi=200)
        buf.seek(0)
        
        _, i, _ = st.columns([1, 2.4, 1], vertical_alignment='center')
        i.image(buf, use_container_width=True)
        
    def t_model(data):
        with schemdraw.Drawing(show=False) as d:
            t = elm.xform.Transformer().label(f'{data["nPrim"]} : {data["nSec"]}', fontsize=10)
            
            p1 = elm.Line().up().at(t.p1).length(0.5)
            p2 = elm.Line().down().at(t.p2).length(0.5)
            s1 = elm.Line().up().at(t.s1).length(0.5)
            s2 = elm.Line().down().at(t.s2).length(0.5)

            l2 = elm.Inductor2().left().at(p1.end).flip().label(data['Ls2_prim'], fontsize=10)
            l1 = elm.Inductor2().left().at(l2.end).flip().label(data['Ls1_prim'], fontsize=10)

            w2 = elm.Line().left().at(p2.end)
            w1 = elm.Line().left().at(w2.end)
            
            lm = elm.Inductor2().down().at(l2.end).to(w2.end).flip().label(data['Lm'], fontsize=10)
            
            elm.Line().right().at(s1.end).length(2)
            elm.Line().right().at(s2.end).length(2)
            
        render(d)
            
    def gamma_model(data):
        with schemdraw.Drawing(show=False) as d:
            t = elm.xform.Transformer().label(f'{1} : {data["N"]}' if data["N"] else ":", fontsize=10)
            
            p1 = elm.Line().up().at(t.p1).length(0.5)
            p2 = elm.Line().down().at(t.p2).length(0.5)
            s1 = elm.Line().up().at(t.s1).length(0.5)
            s2 = elm.Line().down().at(t.s2).length(0.5)
            
            w3 = elm.Line().left().at(p1.end).length(2)
            ls = elm.Inductor2().left().at(w3.end).flip().label(data['Ls'], fontsize=10)

            w2 = elm.Line().left().at(p2.end).length(2)
            w1 = elm.Line().left().at(w2.end)
            
            lp = elm.Inductor2().down().at(w3.end).to(w2.end).flip().label(data['Lp'], fontsize=10)
            
            elm.Line().right().at(s1.end).length(2)
            elm.Line().right().at(s2.end).length(2)

        render(d)
        
    try:
        def format_with_units(value, units):
            value, units, _ = replace_prefix(value, units)
            return f"{value:.3f} {units}"
        
        def special_format(value):
            if isinstance(value, str):
                return value
            return f"{value:.3f}"

        if n == "Raw Data":
            data = {
                'voltage': format_with_units(instrument.channels[st.session_state['history']].voltage, properties['voltLvl']['units']),
                'frequency': format_with_units(instrument.channels[st.session_state['history']].frequency, properties['freq']['units']),
                'L1': format_with_units(instrument.channels[st.session_state['history']].L1, properties['L1']['units']),
                'L2': format_with_units(instrument.channels[st.session_state['history']].L2, properties['L2']['units']),
                'k': special_format(instrument.channels[st.session_state['history']].k),
                'k1': special_format(instrument.channels[st.session_state['history']].k1),
                'k2': special_format(instrument.channels[st.session_state['history']].k2),
                'v1_prim': format_with_units(instrument.channels[st.session_state['history']].v1_prim, properties['v1_prim']['units']),
                'v2_prim': format_with_units(instrument.channels[st.session_state['history']].v2_prim, properties['v2_prim']['units']),
                'v1_sec': format_with_units(instrument.channels[st.session_state['history']].v1_sec, properties['v1_sec']['units']),
                'v2_sec': format_with_units(instrument.channels[st.session_state['should behistory']].v2_sec, properties['v2_sec']['units']),
            }
            st.table(data)
        elif n == "T-Model":
            data = {
                'Ls1_prim': format_with_units(instrument.channels[st.session_state['history']].Ls1_prim, properties['Ls1_prim']['units']),
                'Lm': format_with_units(instrument.channels[st.session_state['history']].Lm, properties['Lm']['units']),
                'Ls2_prim': format_with_units(instrument.channels[st.session_state['history']].Ls2_prim, properties['Ls2_prim']['units']),
                'nPrim': int(instrument.channels[st.session_state['history']].nPrim),
                'nSec': int(instrument.channels[st.session_state['history']].nSec),
            }
            t_model(data)
        elif n == "Gamma-Model":
            data = {
                'Ls': format_with_units(instrument.channels[st.session_state['history']].Ls, properties['Ls']['units']),
                'Lp': format_with_units(instrument.channels[st.session_state['history']].Lp, properties['Lp']['units']),
                'N': special_format(instrument.channels[st.session_state['history']].N),
            }
            gamma_model(data)
    except Exception as e:
        print(e)
        
    if st.session_state['max_history'] > 1:
        v = st.slider("Measurement", min_value=1, max_value=st.session_state['max_history'], value=st.session_state['history'])
        if v != st.session_state['history']:
            st.session_state['history'] = v
            st.rerun()

elif __name__ == "__main__":
    import subprocess
    
    process = subprocess.Popen(
        ["python", os.path.join(os.path.dirname(__file__), "SCPIClient.py")],
    )
    
    process.wait()