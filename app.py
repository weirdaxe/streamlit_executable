import streamlit as st
import contextlib
import io
import traceback

st.title("Remote Python Runner (Streamlit Cloud)")

st.write("""
Run Python code remotely.  
This app executes your code on Streamlit Cloud, so API calls and requests will work even if your local machine is blocked.
""")

code = st.text_area(
    "Write your Python code here:",
    height=250,
    placeholder="import requests\nr = requests.get('https://api.github.com')\nprint(r.json())"
)

if st.button("Run code"):
    buffer = io.StringIO()

    # Create isolated execution environments
    global_vars = {}
    local_vars = {}

    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, global_vars, local_vars)

        output = buffer.getvalue()
        st.success("Output:")
        st.code(output if output.strip() else "(no output)")
    except Exception as e:
        st.error("Error during execution:")
        st.code(traceback.format_exc())
