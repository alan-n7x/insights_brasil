"""Inicia a API Django e o dashboard Streamlit em desenvolvimento."""

import subprocess

processes = [
    subprocess.Popen(["uv", "run", "backend/manage.py", "runserver"]),
    subprocess.Popen(["uv", "run", "streamlit", "run", "frontend/app.py"]),
]

exit_code = 0
try:
    exit_code = processes[0].wait()
finally:
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        process.wait()

raise SystemExit(exit_code)
