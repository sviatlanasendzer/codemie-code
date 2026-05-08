import sys
import subprocess
import platform
from pathlib import Path

REQUIRED_PYTHON = (3, 10)

ROOT = Path(__file__).parent.resolve()
VENV = ROOT / ".venv"

IS_WINDOWS = platform.system().lower().startswith("win")
PYTHON_BIN = VENV / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")


def run(cmd):
    print("> " + " ".join(map(str, cmd)))
    subprocess.check_call(cmd)


def check_python_version():
    if sys.version_info < REQUIRED_PYTHON:
        sys.exit(
            f"❌ Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ required. "
            f"Found {sys.version.split()[0]}"
        )
    print(f"✅ Python version OK: {sys.version.split()[0]}")


def ensure_venv():
    if not VENV.exists():
        print("📦 Creating virtual environment (.venv)")
        run([sys.executable, "-m", "venv", str(VENV)])
    else:
        print("✅ Virtual environment already exists")


def upgrade_pip():
    run([str(PYTHON_BIN), "-m", "pip", "install", "--upgrade", "pip"])


def install_requirements():
    req = ROOT / "requirements.txt"
    if not req.exists():
        sys.exit("❌ requirements.txt not found")
    run([str(PYTHON_BIN), "-m", "pip", "install", "-r", str(req)])


def main():
    print("\n=== Virtual environment setup ===\n")

    check_python_version()
    ensure_venv()
    upgrade_pip()
    install_requirements()

    print("\n✅ Virtual environment ready")
    print(f"✅ Python used: {PYTHON_BIN}")
    print("\n(No agents were executed)\n")


if __name__ == "__main__":
    main()
