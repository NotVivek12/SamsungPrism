import subprocess
import sys

result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
print(result.stdout)
print("\n=== Checking for mysql ===")
for line in result.stdout.split('\n'):
    if 'mysql' in line.lower():
        print(line)
