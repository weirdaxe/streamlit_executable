import streamlit as st
import contextlib
import io
import traceback

st.set_page_config(page_title="Remote Python Runner", layout="wide")
st.title("🐍 Remote Python Runner (Streamlit Cloud)")

st.write("""
Run Python code remotely on Streamlit Cloud.  
You can execute API calls, web requests, and other Python code directly from this app.
""")

# ----------------- Code input -----------------
code = st.text_area(
    "Write your Python code here:",
    height=250,
    placeholder=(
        "# Example:\n"
        "import requests\n"
        "r = requests.get('https://api.github.com')\n"
        "print(r.json())"
    )
)

# ----------------- Run button -----------------
if st.button("▶️ Run code"):
    buffer = io.StringIO()
    global_vars = {}
    local_vars = {}

    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, global_vars, local_vars)

        output = buffer.getvalue()
        st.success("✅ Output:")
        st.code(output if output.strip() else "(no output)", language="python")

        # ----------------- Download output -----------------
        if output.strip():
            st.download_button(
                label="📥 Download Output",
                data=output,
                file_name="output.txt",
                mime="text/plain"
            )

    except Exception:
        st.error("❌ Error during execution:")
        st.code(traceback.format_exc(), language="python")
