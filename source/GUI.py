"""This is the main GUI for the Coupling Measurer application.

Attributes:
    instrument (CouplingMeasurer): The instrument wrapper used for communication."""

import yaml
import sys
import os

import traceback

if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
    import streamlit as st
    from streamlit_navigation_bar import st_navbar
    from streamlit_extras.stylable_container import stylable_container
    
    from math import log10, floor, isclose
    
    from utils import *
    config = read_config()

    ip = config["server"]['_IP']
    port = config["server"]['port']
    properties = config['properties']
    
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
                .block-container {
                    padding-top: 0.4rem;
                    padding-bottom: 1rem;
                    padding-left: 4rem;
                    padding-right: 4rem;
                }
            </style>
        """, unsafe_allow_html=True)
        
    st.markdown("""
        <style>
            h1 {
                padding: 0px !important;
            }
            .stToast {
                background-color: #88E788;
            }
        </style>
    """, unsafe_allow_html=True)
    
    import re
    def nice(text):
        """Converts various cases (camelCase, kebab-case, snake_case, etc.) into Capitalized Case."""
        if text.startswith("_"):
            return text[1:]
        
        # Replace kebab-case and snake_case with spaces
        text = re.sub(r'[\-_]', ' ', text)
        
        # Split camelCase into words
        text = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
        
        # Capitalize each word and join with a space
        return ' '.join(word.capitalize() for word in text.split())
        
    
    def nested_dict_to_form(data, parent_key=''):
        """Recursively converts a nested dictionary into Streamlit form fields and returns the updated dictionary."""
        updated_data = {}
        for key, value in data.items():
            field_key = f"{parent_key}{path_separator}{key}" if parent_key else key
            if isinstance(value, dict):
                with st.expander(f"**{nice(key)}**"):
                    updated_data[key] = nested_dict_to_form(value, parent_key=field_key)
            else:
                if isinstance(value, bool):
                    updated_data[key] = st.checkbox(f"{nice(key)}", value=value, key=field_key)
                elif isinstance(value, int):
                    updated_data[key] = st.number_input(f"{nice(key)}", value=value, key=field_key, step=1)
                elif isinstance(value, float):
                    updated_data[key] = st.number_input(f"{nice(key)}", value=value, key=field_key, format="%.3f")
                elif isinstance(value, str):
                    updated_data[key] = st.text_input(f"{nice(key)}", value=value, key=field_key).replace(path_separator, '').replace(config_separator, '').replace(SCPI_argument_separator, '').replace(SCPI_command_separator, '')
        return updated_data
    
    @st.dialog("Configuration", width="large")
    def configure():
        with st.form("config_form"):
            from copy import deepcopy
            st.session_state["conf"] = deepcopy(nested_dict_to_form(config))
            if st.form_submit_button("Save"):
                write_config(st.session_state["conf"])
                st.session_state["refresh_before"] = True
                st.rerun()
        st.stop()
    
    with stylable_container("Header", """
        button {
            border: none;
            width: 10px;
            background-color: transparent;
        }
    """):
        s, _, r, c = st.columns([3.6, 6, 1, 1], vertical_alignment='center')
        
        s1, s2, s3 = s.columns(3)
        
        s1.markdown('<p class="dmm1" style="display: none; border-radius: 6px; text-align: center;">DMM1</p>', unsafe_allow_html=True)
        s2.markdown('<p class="dmm2" style="display: none; border-radius: 6px; text-align: center;">DMM2</p>', unsafe_allow_html=True)
        s3.markdown('<p class="lcr" style="display: none; border-radius: 6px; text-align: center;">LCR</p>', unsafe_allow_html=True)
        
        if r.button("↻", key="rerun", use_container_width=True, help="Refresh page without breaking connection"):
            st.session_state["refresh_before"] = True
            st.rerun()
            
        if c.button("⚙️", key="config", use_container_width=True, help="Configuration menu"):
            configure()
            
    if 'history' not in st.session_state:
        st.session_state['history'] = 0
        st.session_state['max_history'] = 0
    def fetch_history():
        if instrument:
            try:
                nn = int(instrument.n)
                if nn != st.session_state['max_history']:
                    st.session_state['history'] = nn
                    st.session_state['max_history'] = nn
                instrument.update_children()
            except (ValueError, TypeError): # a connection to the instrument is still present, but the results are lagging in their buffer
                pass
            except:
                raise

    def fetch():
        if instrument:
            st.session_state['voltage'], st.session_state['voltage_units'], st.session_state['voltage_scaling'] = replace_prefix(instrument.voltage, properties['voltLvl']['units'])
            st.session_state['frequency'], st.session_state['frequency_units'], st.session_state['frequency_scaling'] = replace_prefix(instrument.frequency, properties['freq']['units'])
            st.session_state['nPrim'], st.session_state['nPrim_units'] = replace_suffix(instrument.nPrim, properties['nPrim']['units'])
            st.session_state['nSec'], st.session_state['nSec_units'] = replace_suffix(instrument.nSec, properties['nSec']['units'])

            fetch_history()

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
                    
    from OST import CouplingMeasurer
    if 'instrument' not in st.session_state:
        try:
            with st.spinner("Connecting...", show_time=True):
                instrument = CouplingMeasurer(f"TCPIP::{ip}::{port}::SOCKET", timeout=10000)
                st.cache_data.clear()
            st.session_state['instrument'] = instrument
            fetch()
            st.toast(f"Connected to {instrument.id}.")
            check_server_errors()
        except Exception as e:
            instrument = None
            error(f"<summary>Failed to connect to the instrument at {ip}:{port}. Please check the connection and try again.</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")
    else:
        instrument = st.session_state['instrument']
        if instrument.adapter.resource_name != f"TCPIP::{ip}::{port}::SOCKET":
            st.session_state.pop('instrument', None)
            st.rerun()
        try:
            fetch_history()
        except Exception as e:
            instrument = None
            error(f"<summary>Failed to maintain connection to the instrument, likely server crash</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")

    dmm1, dmm2, lcr = '', '', ''
    def update_connections():
        global dmm1, dmm2, lcr
        dmm1, dmm2, lcr = instrument.dmm1, instrument.dmm2, instrument.lcr
    
    def color(tag, value):
        if value == "True":
            c = "background-color: #88E788;"
        elif value == "False":
            c = "background-color: #FF7F7F;"
        else:
            c = "display: none !important;"
        st.markdown(f"<style>.{tag} {{display: block !important; {c}}}</style>", unsafe_allow_html=True)
    
    if "conf" in st.session_state:
        config = st.session_state["conf"]
        st.session_state.pop("conf", None)
        
        try:
            instrument.config = shared_configs(config)
            #st.rerun()
        except Exception as e:
            error(f"<summary>Failed to apply the configuration</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")

    @st.dialog("Configuration Changed")
    def confirm():
        st.write("Since the last time you've connected, your configuration files and the servers have diverged. This can be due to other users updating the configuration or this could be intentional on your part by manually changing config.yaml. Please choose to either publish your updates to the server or fetch the servers new configuration.")
        
        a, b = st.columns(2)
        if a.button("Publish local changes", use_container_width=True):
            instrument.config = shared_configs(config)
            st.session_state["refresh_before"] = True
            st.rerun()
        elif b.button("Fetch server configuration", use_container_width=True):
            st.session_state["refresh_before"] = True
            st.rerun()
        st.stop()
        
    try:
        new_config = instrument.config
        if "file_change" not in st.session_state:
            st.session_state["file_change"] = True
            if set(new_config.split(config_separator)) != set(shared_configs(config).split(config_separator)):
                confirm()
        apply(config, new_config)
    except Exception as e:
        error(f"<summary>Failed to fetch the configuration from the instrument</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")

    t, e, p, r, h = st.columns([4, 1.4, 1.4, 1.4, 1.4], vertical_alignment='center')

    t.title("Coupling")

    def format_with_units(value, units):
        if isinstance(value, str):
            return value
        value, units, _ = replace_prefix(value, units)
        return f"{value:.3f} {units}"
    
    def special_format(value, percent=False):
        if isinstance(value, str) or isinstance(value, int):
            return value
        if percent:
            return f"{value * 100:.1f} %"
        return f"{value:.3f}"
    
    @st.cache_data
    def get_data(number):
        return {
            'voltage': format_with_units(instrument.channels[number].voltage, properties['voltLvl']['units']),
            'frequency': format_with_units(instrument.channels[number].frequency, properties['freq']['units']),
            'L1': format_with_units(instrument.channels[number].L1, properties['L1']['units']),
            'L2': format_with_units(instrument.channels[number].L2, properties['L2']['units']),
            'k': special_format(instrument.channels[number].k, percent=True),
            'k1': special_format(instrument.channels[number].k1, percent=True),
            'k2': special_format(instrument.channels[number].k2, percent=True),
            'v1_prim': format_with_units(instrument.channels[number].v1_prim, properties['v1_prim']['units']),
            'v2_prim': format_with_units(instrument.channels[number].v2_prim, properties['v2_prim']['units']),
            'v1_sec': format_with_units(instrument.channels[number].v1_sec, properties['v1_sec']['units']),
            'v2_sec': format_with_units(instrument.channels[number].v2_sec, properties['v2_sec']['units']),
            'Ls1_prim': format_with_units(instrument.channels[number].Ls1_prim, properties['Ls1_prim']['units']),
            'Lm': format_with_units(instrument.channels[number].Lm, properties['Lm']['units']),
            'Ls2_prim': format_with_units(instrument.channels[number].Ls2_prim, properties['Ls2_prim']['units']),
            'nPrim': special_format(instrument.channels[number].nPrim),
            'nSec': special_format(instrument.channels[number].nSec),
            'Ls': format_with_units(instrument.channels[number].Ls, properties['Ls']['units']),
            'Lp': format_with_units(instrument.channels[number].Lp, properties['Lp']['units']),
            'N': special_format(instrument.channels[number].N),
        }
    try:
        data = get_data(st.session_state['history'])
        for _, i in data.items():
            if len(str(i)) > 1024:
                get_data.clear(st.session_state['history'])
                st.rerun()
    except Exception as e:
        error(f"<summary>Failed to connect to and fetch the measurement data</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")

    update_connections()
    
    color("dmm1", dmm1)
    color("dmm2", dmm2)
    color("lcr", lcr)
    
    st.markdown("""
    <style>
    .stElementContainer:has(style) {
        display: none;
    }
    .stElementContainer:has(hr) {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    import schemdraw
    import schemdraw.elements as elm
    
    from io import BytesIO
    
    def to_bytes(diagram):
        buf = BytesIO()
        diagram.save(buf, dpi=200)
        buf.seek(0)
        return buf
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QImage
        
        def copy_image(image):
            app = QApplication(sys.argv)
            clipboard = app.clipboard()
            
            data = QImage()
            data.loadFromData(image.getvalue(), "PNG")
            
            clipboard.setImage(data)
    except:
        pass
        
    STANDARD_SHAPE = [1, 2.4, 1]
    DEFORMED_SHAPE = [1, 4.6, 1]
        
    id = 0
    
    def copy_button(item):
        global id
        id += 1
        
        with stylable_container(f"copy{id}"), """
            div {
                text-align: right !important;
            }
            button {
                border: none !important;
                width: 10px;
                background-color: transparent;
            }
        """):
            if isinstance(item, BytesIO):
                if not is_raspberry_pi() and st.columns(DEFORMED_SHAPE)[1].button("", key=str(id)):
                    copy_image(item)
                    st.toast("Copied to clipboard")
            else:
                import pyperclip
                if st.button("", key=str(id)):
                    pyperclip.copy("\n".join(item).replace("*", ""))
                    st.toast("Copied to clipboard")
    
    def render(buf):
        copy_button(buf)
        _, i, _ = st.columns(STANDARD_SHAPE, vertical_alignment='center')
        i.image(buf, use_container_width=True)
        
    @st.cache_data
    def t_model(data, flip=False):
        
        def flip_element(element, invert=True):
            if not invert:
                element.left().flip()
            else:
                element.right()
        
        def adjust_value(value):
            if flip:
                try:
                    v, u = value.split(' ')
                    v, u, _ = replace_prefix(float(v) * (float(data['nSec']) / float(data['nPrim'])) ** 2, u)
                    return f"{v:.3f} {u}"
                except Exception:
                    pass
            return value
        with schemdraw.Drawing(show=False) as d:
            t = elm.xform.Transformer().label(f'{data["nPrim"]} : {data["nSec"]}', fontsize=10, ofst=[0, 0.6])
            if flip:
                t.reverse()
            
            p1 = elm.Line().up().at(t.p1).length(0.5)
            p2 = elm.Line().down().at(t.p2).length(0.5)
            s1 = elm.Line().up().at(t.s1).length(0.5)
            s2 = elm.Line().down().at(t.s2).length(0.5)

            l2 = elm.Inductor2().at(p1.end).label(adjust_value(data['Ls1_prim'] if flip else data['Ls2_prim']), fontsize=10)
            flip_element(l2, invert=flip)
            l1 = elm.Inductor2().at(l2.end).label(adjust_value(data['Ls2_prim'] if flip else data['Ls1_prim']), fontsize=10)
            flip_element(l1, invert=flip)

            w2 = elm.Line().at(p2.end)
            flip_element(w2, invert=flip)
            w1 = elm.Line().at(w2.end)
            flip_element(w1, invert=flip)
            
            lm = elm.Inductor2().down().at(l2.end).to(w2.end).flip().label(adjust_value(data['Lm']), fontsize=10)
            
            c1 = elm.Line().at(s1.end).length(2)
            flip_element(c1, invert=not flip)
            c2 = elm.Line().at(s2.end).length(2)
            flip_element(c2, invert=not flip)
            
            g = elm.Gap(label=[f"$k=${data['k']}", f"$k_1=${data['k1']}", f"$k_2=${data['k2']}"], fontsize=10, lblofst=[0, 0.5 if flip else -0.5]).at(c1.end).to(c2.end)

        return to_bytes(d)
            
    @st.cache_data
    def gamma_model(data):
        with schemdraw.Drawing(show=False) as d:
            t = elm.xform.Transformer().label(f'{1} : {data["N"]}' if data["N"] else ":", fontsize=10, ofst=[0, 0.6])
            
            p1 = elm.Line().up().at(t.p1).length(0.5)
            p2 = elm.Line().down().at(t.p2).length(0.5)
            s1 = elm.Line().up().at(t.s1).length(0.5)
            s2 = elm.Line().down().at(t.s2).length(0.5)
            
            w3 = elm.Line().left().at(p1.end).length(2)
            ls = elm.Inductor2().left().at(w3.end).flip().label(data['Ls'], fontsize=10)

            w2 = elm.Line().left().at(p2.end).length(2)
            w1 = elm.Line().left().at(w2.end)
            
            lp = elm.Inductor2().down().at(w3.end).to(w2.end).flip().label(data['Lp'], fontsize=10)
            
            c1 = elm.Line().right().at(s1.end).length(2)
            c2 = elm.Line().right().at(s2.end).length(2)
            
            g = elm.Gap(label=[f"$k=${data['k']}", f"$k_1=${data['k1']}", f"$k_2=${data['k2']}"], fontsize=10, lblofst=[0, -0.5]).at(c1.end).to(c2.end)

        return to_bytes(d)
    
    @st.cache_data
    def template(data):
        return f"""
**{instrument.channels[st.session_state['history']].time}**  

**Set values**  
Voltage: {data['voltage']}  
Frequency: {data['frequency']}  
nPrim: {data['nPrim']}  
nSec: {data['nSec']}  

**Raw values from measurement**  
L1: {data['L1']}  
L2: {data['L2']}  
k: {data['k']}  
k1: {data['k1']}  
k2: {data['k2']}  
v1_prim: {data['v1_prim']}  
v2_prim: {data['v2_prim']}  
v1_sec: {data['v1_sec']}  
v2_sec: {data['v2_sec']}  

**Calculated values**  
*T-model*:  
Ls1_prim: {data['Ls1_prim']}  
Ls2_prim: {data['Ls2_prim']}  
Lm: {data['Lm']}  
  
*Gamma model*:  
Ls: {data['Ls']}  
Lp: {data['Lp']}  
N: {data['N']}  
""".split("\n\n")
        
    @st.cache_data
    def generate_data(data):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        
        output = BytesIO()
        
        c = canvas.Canvas(output, pagesize=letter)
        width, height = letter
        
        table_data = [["Parameter", "Value"]]
        for key, value in data.items():
            table_data.append([key, value])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'), # Center align the first column
            ('ALIGN', (1, 0), (1, -1), 'LEFT'), # Left align the second column
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            # ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            # ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        table.wrapOn(c, width, height)
        table.drawOn(c, 40, height - 400)
        
        h = height - 200
        for image in [t_model(data), t_model(data, flip=True), gamma_model(data)]:
            img = ImageReader(image)
            c.drawImage(img, 200, h, 300, 150)
            h -= 150
        
        c.showPage()
        c.save()
        
        output.seek(0)
        return output.getvalue()
        
    e.download_button("Export", data=generate_data(data), file_name="coupling_measurement.pdf", key="export_button", use_container_width=True, help="Downloads a PDF containing the current measurement data")

    if p.button("Run", args=(), key="measure_button", use_container_width=True, help="Performs a new measurement"):
        update_connections()
        e = []
        if dmm1 == "False":
            e.append("DMM1")
        if dmm2 == "False":
            e.append("DMM2")
        if lcr == "False":
            e.append("LCR")
        e = ', '.join(e)
        
        if e:
            error(f"Cannot perform my measurement, the following instruments are not connected: {e}. Please connect the instruments and try again.")
        
        try:
            with st.spinner("Waiting for measurement to complete...", show_time=True):
                instrument.measure()
            fetch()
            check_server_errors()
        except Exception as e:
            error(f"<summary>Failed to connect to and perform a measurement on the instrument</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")

    if r.button("Reset", args=(), key="reset_button", use_container_width=True, help="Resets input values to default"):
        try:
            instrument.reset()
            fetch()
            check_server_errors()
        except Exception as e:
            error(f"<summary>Failed to connect to and reset the instrument</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")
            
    if h.button("Clear history", args=(), key="reset_button", use_container_width=True, help="Clears current measurement and all history"):
        try:
            instrument.clear()
            fetch()
            check_server_errors()
        except Exception as e:
            error(f"<summary>Failed to connect to and clear history of the instrument</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")
            
    if "refresh_before" not in st.session_state:
        st.session_state["refresh_before"] = False
        
    def refresh(key, scaling=1):
        if key in st.session_state:
            setattr(instrument, key, st.session_state[key] * scaling)
        fetch()
        
    if st.session_state["refresh_before"]:
        st.session_state["refresh_before"] = False
        fetch()
        
    v, vu, f, fu, p, pu, s, su = [*st.columns([1, 0.24, 1, 0.24,], vertical_alignment='bottom'), *st.columns([1, 0.24, 1, 0.24,], vertical_alignment='bottom')] if is_raspberry_pi() else st.columns([0.86, 0.6, 0.86, 0.6, 0.86, 0.6, 0.86, 0.6], vertical_alignment='bottom')
    try:
        v.number_input("Voltage", args=("voltage",st.session_state['voltage_scaling']), key="voltage", on_change=refresh, step=properties['voltLvl']['step']/st.session_state['voltage_scaling'], min_value=properties['voltLvl']['min']/st.session_state['voltage_scaling'], max_value=properties['voltLvl']['max']/st.session_state['voltage_scaling'], format=properties['voltLvl']['format'])
        vu.write(st.session_state['voltage_units'])
        f.number_input("Frequency", args=("frequency",st.session_state['frequency_scaling']), key="frequency", on_change=refresh, step=properties['freq']['step']/st.session_state['frequency_scaling'], min_value=properties['freq']['min']/st.session_state['frequency_scaling'], max_value=properties['freq']['max']/st.session_state['frequency_scaling'], format=properties['freq']['format'])
        fu.write(st.session_state['frequency_units'])
        p.number_input("nPrim", args=("nPrim",), key="nPrim", on_change=refresh, step=1, min_value=properties['nPrim']['min'], max_value=properties['nPrim']['max'])
        pu.write(st.session_state['nPrim_units'])
        s.number_input("nSec", args=("nSec",), key="nSec", on_change=refresh, step=1, min_value=properties['nSec']['min'], max_value=properties['nSec']['max'])
        su.write(st.session_state['nSec_units'])

        check_server_errors()
    except Exception as e:
        error(f"<summary>Failed to connect to and set the instrument parameters</summary><traceback>Error: {e} {traceback.format_exc()}</traceback>")
        
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
        
    try:

        if n == "Raw Data":
            with stylable_container("Raw", """
                .stMarkdown {
                    text-align: center;
                }
            """):
                st.write(template(data))
        elif n == "T-Model":
            render(t_model(data))
            render(t_model(data, flip=True))
        elif n == "Gamma-Model":
            render(gamma_model(data))
        check_server_errors()
    except Exception as e:
        pass
        
    if st.session_state['max_history'] > 1:
        v = st.slider("Measurement", min_value=1, max_value=st.session_state['max_history'], value=st.session_state['history'])
        if v != st.session_state['history']:
            st.session_state['history'] = v
            st.rerun()
    
    write_config(config)

    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(4000)

elif __name__ == "__main__":
    import subprocess
    
    import sys
    
    process = subprocess.Popen(
        [sys.executable, os.path.join(os.path.dirname(__file__), "SCPIClient.py")],
    )
    
    process.wait()