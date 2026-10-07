import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"
BACKEND_DIR = ROOT / "backend"

def get_python_exe() -> str:
    venv_win = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
    venv_unix = BACKEND_DIR / ".venv" / "bin" / "python"
    if venv_win.exists():
        return str(venv_win)
    if venv_unix.exists():
        return str(venv_unix)
    return sys.executable

def run_cmd(cmd: str, cwd: Path | None = None, check: bool = True):
    print(f"\n>> Running: {cmd} (cwd: {cwd or ROOT})")
    res = subprocess.run(cmd, cwd=str(cwd or ROOT), shell=True)
    if check and res.returncode != 0:
        print(f"Command failed with code {res.returncode}")
        sys.exit(res.returncode)
    return res.returncode

def cmd_setup():
    py_exe = get_python_exe()
    if not (BACKEND_DIR / ".venv").exists():
        run_cmd(f'"{sys.executable}" -m venv "{BACKEND_DIR / ".venv"}"')
    run_cmd(f'"{py_exe}" -m pip install -r "{BACKEND_DIR / "requirements.txt"}"')
    run_cmd("npm install", cwd=FRONTEND_DIR)

def cmd_types():
    py_exe = get_python_exe()
    run_cmd(f'"{py_exe}" "{BACKEND_DIR / "export_openapi.py"}"')
    run_cmd("npm run gen:types", cwd=FRONTEND_DIR)

def cmd_test():
    py_exe = get_python_exe()
    print("Running backend tests (pytest)...")
    run_cmd(f'"{py_exe}" -m pytest backend/tests', cwd=ROOT)
    print("Running frontend tests (vitest)...")
    run_cmd("npm run test", cwd=FRONTEND_DIR)

def cmd_check():
    py_exe = get_python_exe()
    print("1. Running ruff check on backend...")
    run_cmd(f'"{py_exe}" -m ruff check backend', cwd=ROOT)
    print("2. Running TypeScript check on frontend...")
    run_cmd("npx tsc --noEmit", cwd=FRONTEND_DIR)
    print("3. Running ESLint on frontend...")
    run_cmd("npm run lint", cwd=FRONTEND_DIR)
    print("4. Running all tests...")
    cmd_test()

def cmd_seed(reset: bool = False):
    py_exe = get_python_exe()
    reset_flag = " --reset" if reset else ""
    seed_script = BACKEND_DIR / "seed" / "seed.py"
    if seed_script.exists():
        run_cmd(f'"{py_exe}" "{seed_script}"{reset_flag}', cwd=ROOT)
    else:
        print("Seed script not yet implemented (scheduled for S1).")

def cmd_dev():
    py_exe = get_python_exe()
    # Concurrently or sequentially run backend and frontend
    print("Starting development servers...")
    print("Backend on http://localhost:8000")
    print("Frontend on http://localhost:3000")
    b_proc = subprocess.Popen(
        f'"{py_exe}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload',
        cwd=str(BACKEND_DIR),
        shell=True,
    )
    f_proc = subprocess.Popen(
        "npm run dev",
        cwd=str(FRONTEND_DIR),
        shell=True,
    )
    try:
        b_proc.wait()
        f_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        b_proc.terminate()
        f_proc.terminate()

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [setup|dev|seed|test|check|types]")
        sys.exit(1)
    
    target = sys.argv[1].lower()
    if target == "setup":
        cmd_setup()
    elif target == "dev":
        cmd_dev()
    elif target == "seed":
        reset = "--reset" in sys.argv
        cmd_seed(reset)
    elif target == "test":
        cmd_test()
    elif target == "check":
        cmd_check()
    elif target == "types":
        cmd_types()
    else:
        print(f"Unknown target: {target}")
        sys.exit(1)

if __name__ == "__main__":
    main()
