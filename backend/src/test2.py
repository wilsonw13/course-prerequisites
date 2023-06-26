import subprocess
import os

print("HI FROM TEST2")
subprocess.run(f"py -m da --rules src/test.da",
               env={**os.environ, "PYTHONPATH": "src:da:ps"}
               )
