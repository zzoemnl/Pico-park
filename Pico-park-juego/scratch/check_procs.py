import subprocess
import os

try:
    out = subprocess.check_output('wmic process where "name like \'%python%\'" get ProcessId,CommandLine', shell=True).decode('latin1', errors='ignore')
    print(out)
except Exception as e:
    print(e)
