import streamlit as st
from streamlit_ace import st_ace
import io
import contextlib
import traceback
import time
import sys
import signal
import os
import threading
import asyncio

# ========= CONFIG =========
st.set_page_config(page_title="Advanced Python Runner", layout="wide")

EXECUTION_TIMEOUT = 8  # default
BLOCKED_MODULES = {"os", "subprocess", "sys", "shutil", "pathlib", "socket", "asyncio"}
SAFE_EXPORT_DIR = "/tmp"

# ========= SANDBOX HELPERS =========
def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out.")

def block_unsafe_imports(code: str) -> bool:
    for mod in BLOCKED_MODULES:
        if f"import {mod}" in code or f"from {mod}" in code:
            return False
    return True

def safe_open_wrapper(original_open):
    def wrapper(path, mode='r', *args, **kwargs):
        if any(m in mode for m in ("w", "a", "x")):
            if not path.startswith(SAFE_EXPORT_DIR):
                raise PermissionError("Writing outside /tmp is blocked.")
        return original_open(path, mode, *args, **kwargs)
    return wrapper

# ========= UI =========
st.title("🐍 Advanced Python Runner — Execution Upgrades")

st.write("""
Run Python code remotely with optional execution enhancements.  
All enhancements are disabled by default for safety.
""")

# --- Execution upgrade toggles ---
st.subheader("⚙️ Optional Execution Upgrades")

col1, col2, col3 = st.columns(3)

with col1:
    enable_async = st.checkbox("Enable async support", False)
    background_mode = st.checkbox("Run as background job", False)

with col2:
    live_stdout = st.checkbox("Live stdout streaming", False)
    live_plots = st.checkbox("Real-time plot preview", False)

with col3:
    show_file_explorer = st.checkbox("Show file explorer (debug)", False)
    custom_timeout = st.number_input(
        "Execution timeout (seconds):", 2, 60, EXECUTION_TIMEOUT
    )

# Code editor
code = st_ace(
    language="python",
    theme="monokai",
    height=350,
    tab_size=4,
    font_size=15,
)

run_button = st.button("▶️ Run Code")


# ========= EXECUTION FUNCTION =========
import builtins

def execute_user_code(code: str):
    ...
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    global_env = {}
    local_env = {}

    # Patch open()
    original_open = builtins.open
    builtins.open = safe_open_wrapper(original_open)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(custom_timeout)

    try:
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            if enable_async and ("async def" in code or "await " in code):
                exec(code, global_env, local_env)
                coro = next((v for v in local_env.values() if asyncio.iscoroutine(v)), None)
                if coro:
                    asyncio.run(coro)
            else:
                exec(code, global_env, local_env)

    except Exception:
        stderr_buffer.write(traceback.format_exc())

    finally:
        signal.alarm(0)
        builtins.open = original_open  # Restore open()

    return (stdout_buffer.getvalue(), stderr_buffer.getvalue())



# ========= BACKGROUND JOB WRAPPER =========
background_output = st.empty()

def run_background_job():
    out, err = execute_user_code(code)
    background_output.code(out + "\n" + err)


# ========= MAIN RUN BUTTON =========
if run_button:

    if show_file_explorer:
        st.write("📁 Files in `/tmp` BEFORE execution:")
        st.code("\n".join(os.listdir("/tmp")) or "(empty)")

    if background_mode:
        st.info("Running in background…")
        thread = threading.Thread(target=run_background_job)
        thread.start()
        st.stop()

    # Live stdout: override sys.stdout
    if live_stdout:
        live_box = st.empty()

        class LiveWriter(io.StringIO):
            def write(self, s):
                super().write(s)
                live_box.code(self.getvalue())

        sys.stdout = LiveWriter()

    # Live plot preview
    if live_plots:
        import matplotlib.pyplot as plt
        plt.ion()

    # Run code
    stdout, stderr = execute_user_code(code)

    # Reset stdout
    if live_stdout:
        sys.stdout = sys.__stdout__

    # ========= OUTPUT TABS =========
    tabs = st.tabs(["📤 Stdout", "⚠️ Stderr", "📁 File Downloads"])

    with tabs[0]:
        st.code(stdout or "(no output)")
        if stdout:
            st.download_button("📥 Download stdout", stdout, "stdout.txt")

    with tabs[1]:
        st.code(stderr or "(no errors)")
        if stderr:
            st.download_button("📥 Download stderr", stderr, "stderr.txt")

    with tabs[2]:
        files = os.listdir("/tmp")
        if not files:
            st.info("No files in /tmp")
        else:
            for fname in files:
                with open(f"/tmp/{fname}", "rb") as f:
                    st.download_button(
                        f"Download {fname}",
                        f.read(),
                        fname
                    )

    if show_file_explorer:
        st.write("📁 Files in `/tmp` AFTER execution:")
        st.code("\n".join(os.listdir("/tmp")) or "(empty)")
