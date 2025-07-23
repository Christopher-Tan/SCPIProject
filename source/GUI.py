"""This is the main GUI for the Coupling Measurer application.

Attributes:
    instrument (CouplingMeasurer): The instrument wrapper used for communication."""

import yaml
import sys
import os

with open(os.path.join(os.path.dirname(__file__), "config.yaml"), 'r') as file:
    config = yaml.safe_load(file)
    
ip = config["server"]['_IP']
port = config["server"]['port']
properties = config['properties']

def write_config():
    with open(os.path.join(os.path.dirname(__file__), "config.yaml"), 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
    import streamlit as st
    from streamlit_extras.grid import grid
    from streamlit_navigation_bar import st_navbar
    from streamlit_extras.stylable_container import stylable_container
    
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
    
    from bs4 import BeautifulSoup
    
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
        
    def fetch_server_errors():
        try:
            return [i[1] for i in instrument.check_errors()]
        except:
            pass
        return []

    def check_server_errors(): # sometimes the client side has no errors we still need to check
        errors = fetch_server_errors()
        if errors:
            error(f"", errors, replace_instrument=False)
    
    def special_write(error):
        try:
            html = BeautifulSoup(error)
            summary = html.body.find('summary').text
            trace = html.body.find('traceback').text
            with st.expander(summary):
                st.write(trace)
        except:
            st.write(error)
    
    @st.dialog("Error")
    def error(main_error, likely_causes=[], replace_instrument=True): # sometimes the client side error is a direct result of the server side error, we show these errors first
        st.markdown("""
            <style>
                [role="dialog"] {
                    background-color: #FF7F7F;
                }
            </style>
        """, unsafe_allow_html=True)

        likely_causes.extend(fetch_server_errors())
        if likely_causes:
            for cause in likely_causes:
                special_write(cause)

        if replace_instrument:
            cleanup()
            st.session_state.pop('instrument', None)
            
        special_write(main_error)
        
        with stylable_container("Retry", """
                button {
                    background-color: #FF7F7F;
                }
        """):
        
            if st.button("Retry"):
                st.session_state["refresh_before"] = True
                st.rerun()
            
        st.stop()
        
    if not config["client"]['developerMode']:
        fetch_server_errors()
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
            .stToast {
                background-color: #88E788;
            }
        </style>
    """, unsafe_allow_html=True)
    
    import re
    def nice(text):
        """Converts various cases (camelCase, kebab-case, snake_case, etc.) into Capitalized Case."""
        
        # Replace kebab-case and snake_case with spaces
        text = re.sub(r'[\-_]', ' ', text)
        
        # Split camelCase into words
        text = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
        
        # Capitalize each word and join with a space
        return ' '.join(word.capitalize() for word in text.split())
        
    
    def nested_dict_to_form(data, parent_key='', separator='_'):
        """Recursively converts a nested dictionary into Streamlit form fields and returns the updated dictionary."""
        updated_data = {}
        for key, value in data.items():
            field_key = f"{parent_key}{separator}{key}" if parent_key else key
            if isinstance(value, dict):
                with st.expander(f"**{nice(key)}**", expanded=True):
                    updated_data[key] = nested_dict_to_form(value, parent_key=field_key, separator=separator)
            else:
                if isinstance(value, int):
                    updated_data[key] = st.number_input(f"{nice(key)}", value=value, key=field_key, step=1)
                elif isinstance(value, float):
                    updated_data[key] = st.number_input(f"{nice(key)}", value=value, key=field_key, format="%.3f")
                elif isinstance(value, bool):
                    updated_data[key] = st.checkbox(f"{nice(key)}", value=value, key=field_key)
                elif isinstance(value, str):
                    updated_data[key] = st.text_input(f"{nice(key)}", value=value, key=field_key)
        return updated_data
    
    @st.dialog("Configuration")
    def configure():
        with st.form("config_form"):
            global config
            config = nested_dict_to_form(config)
            if st.form_submit_button("Save"):
                write_config()
                st.session_state["refresh_before"] = True
                st.rerun()
    
    with stylable_container("Header", """
        button {
            border: none;
            width: 10px;
        }
    """):
        _, r, c = st.columns([8, 1, 1])
        
        if r.button("↻", key="rerun", use_container_width=True):
            st.session_state["refresh_before"] = True
            st.rerun()
            
        if c.button("⚙️", key="config", use_container_width=True):
            configure()
            
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
            check_server_errors()
        except Exception as e:
            instrument = None
            error(f"Failed to connect to the instrument at {ip}:{port}. Please check the connection and try again.")
    else:
        instrument = st.session_state['instrument']

    g = grid([6, 1.8, 1.8], vertical_align='center')

    g.title("Coupling Measurements")
    if g.button("Measure", args=(), key="measure_button"):
        try:
            with st.spinner("Waiting for measurement to complete...", show_time=True):
                instrument.measure()
            fetch()
            check_server_errors()
        except Exception as e:
            print(e)
            st.session_state.pop('instrument', None)
            error(f"Failed to connect to and perform a measurement on the instrument")

    if g.button("Reset", args=(), key="reset_button"):
        try:
            instrument.reset()
            fetch()
            check_server_errors()
        except Exception as e:
            print(e)
            st.session_state.pop('instrument', None)
            error(f"Failed to connect to and reset the instrument")
            
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
        check_server_errors()
    except Exception as e:
        print(e)
        st.session_state.pop('instrument', None)
        error(f"Failed to connect to and set the instrument parameters")
        
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
        },
        key="navbar"
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
            if isinstance(value, str):
                return value
            value, units, _ = replace_prefix(value, units)
            return f"{value:.3f} {units}"
        
        def special_format(value, percent=False):
            if isinstance(value, str) or isinstance(value, int):
                return value
            if percent:
                return f"{value * 100:.3f} %"
            return f"{value:.3f}"

        if n == "Raw Data":
            data = {
                'voltage': format_with_units(instrument.channels[st.session_state['history']].voltage, properties['voltLvl']['units']),
                'frequency': format_with_units(instrument.channels[st.session_state['history']].frequency, properties['freq']['units']),
                'L1': format_with_units(instrument.channels[st.session_state['history']].L1, properties['L1']['units']),
                'L2': format_with_units(instrument.channels[st.session_state['history']].L2, properties['L2']['units']),
                'k': special_format(instrument.channels[st.session_state['history']].k, percent=True),
                'k1': special_format(instrument.channels[st.session_state['history']].k1, percent=True),
                'k2': special_format(instrument.channels[st.session_state['history']].k2, percent=True),
                'v1_prim': format_with_units(instrument.channels[st.session_state['history']].v1_prim, properties['v1_prim']['units']),
                'v2_prim': format_with_units(instrument.channels[st.session_state['history']].v2_prim, properties['v2_prim']['units']),
                'v1_sec': format_with_units(instrument.channels[st.session_state['history']].v1_sec, properties['v1_sec']['units']),
                'v2_sec': format_with_units(instrument.channels[st.session_state['history']].v2_sec, properties['v2_sec']['units']),
            }
            st.table(data)
        elif n == "T-Model":
            data = {
                'Ls1_prim': format_with_units(instrument.channels[st.session_state['history']].Ls1_prim, properties['Ls1_prim']['units']),
                'Lm': format_with_units(instrument.channels[st.session_state['history']].Lm, properties['Lm']['units']),
                'Ls2_prim': format_with_units(instrument.channels[st.session_state['history']].Ls2_prim, properties['Ls2_prim']['units']),
                'nPrim': special_format(instrument.channels[st.session_state['history']].nPrim),
                'nSec': special_format(instrument.channels[st.session_state['history']].nSec),
            }
            t_model(data)
        elif n == "Gamma-Model":
            data = {
                'Ls': format_with_units(instrument.channels[st.session_state['history']].Ls, properties['Ls']['units']),
                'Lp': format_with_units(instrument.channels[st.session_state['history']].Lp, properties['Lp']['units']),
                'N': special_format(instrument.channels[st.session_state['history']].N),
            }
            gamma_model(data)
        check_server_errors()
    except Exception as e:
        print(e)
        
    if st.session_state['max_history'] > 1:
        v = st.slider("Measurement", min_value=1, max_value=st.session_state['max_history'], value=st.session_state['history'])
        if v != st.session_state['history']:
            st.session_state['history'] = v
            st.rerun()

    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(4000)

elif __name__ == "__main__":
    import subprocess
    
    import sys
    
    process = subprocess.Popen(
        [sys.executable, os.path.join(os.path.dirname(__file__), "SCPIClient.py")],
    )
    
    process.wait()