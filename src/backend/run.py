import os
import subprocess
import sys

print("working path",os.getcwd())
print("my path", sys.executable)

base_path = os.path.dirname(sys.executable)  # folder where run.exe is
main_path = os.path.join(base_path, 'other_exe/main.exe')
nes_path = os.path.join(base_path, 'other_exe/nes.exe')

try:
    subprocess.Popen([nes_path], cwd=base_path)
except Exception as e:
    print("Failed to launch nes.exe:", e)

try:
    subprocess.Popen([main_path], cwd=base_path)
except Exception as e:
    print("Failed to launch main.exe:", e)


