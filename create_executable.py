import subprocess
import sys
import os
import shutil

SCRIPT_NAME = "gui.py"

def run_command(command):
    print(f"[RUN] {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        sys.exit(1)

def ensure_pyinstaller():
    try:
        import PyInstaller  # noqa
    except ImportError:
        print("[INFO] PyInstaller not installed. Installing...")
        run_command(f'"{sys.executable}" -m pip install pyinstaller')

def build_exe():
    print(f"[INFO] Copying {SCRIPT_NAME} to .exe...")
    run_command(f'"{sys.executable}" -m PyInstaller --onefile --windowed {SCRIPT_NAME}')

def cleanup():
    print("[INFO] Removing temporary files...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists(f"{os.path.splitext(SCRIPT_NAME)[0]}.spec"):
        os.remove(f"{os.path.splitext(SCRIPT_NAME)[0]}.spec")

def main():
    ensure_pyinstaller()
    build_exe()
    cleanup()
    print("\n✅ Done! Folder containing .exe in: dist")

if __name__ == "__main__":
    main()