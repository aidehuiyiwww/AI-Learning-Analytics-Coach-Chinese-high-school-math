import importlib.util
import subprocess
import sys

PACKAGES = {
    "streamlit": "streamlit",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "openai": "openai",
    "sympy": "sympy",
    "dotenv": "python-dotenv",
}

missing = [pip_name for import_name, pip_name in PACKAGES.items() if importlib.util.find_spec(import_name) is None]
if missing:
    print("Installing missing packages:", ", ".join(missing))
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
else:
    print("All required packages are already installed.")
