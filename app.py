import streamlit as st
import io
import contextlib
import traceback
import time

st.set_page_config(page_title="Remote Python Runner", layout="wide")

st.title("🐍 Remote Python Runner (Public)")

st.write("""
This public app runs Python **code remotely on Streamlit Cloud**.  
Useful if your local machine blocks API requests, scraping, or network access.

⚠️ **Warning:** This is a public sandbox.  
Do not paste secrets, passwords, API keys, or personal data.
""")

code = st.text_area(
    "Write Python code here:",
    height=280,
    placeholder=(
        "# Example:\n"
        "import requests\n"
        "r = requests.get('https://httpbin.org/get')\n"
        "print(r.json())"
    )
)

run_btn = st.button("▶️ Run Code")

if run_btn:
    buffer = io.StringIO()
    start_time = time.time()

    # Isolated execution environments
    global_env = {}
    local_env = {}

    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, global_env, local_env)

        output = buffer.getvalue()
        runtime = time.time() - start_time

        st.success(f"Execution finished in {runtime:.3f} seconds.")
        st.code(output if output.strip() else "(no output)")

        # Download output button
        st.download_button(
            label="📥 Download Output",
            data=output,
            file_name="output.txt",
            mime="text/plain"
        )

    except Exception:
        err = traceback.format_exc()
        st.error("An error occurred:")
        st.code(err)

        st.download_button(
            label="📥 Download Error Log",
            data=err,
            file_name="error.txt",
            mime="text/plain"
        )
