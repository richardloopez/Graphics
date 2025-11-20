#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import os
import subprocess
import tempfile
import readline

# Request the user for the necessary files and ranges
parm_file = "system_hmass.prmtop"
traj_file = "unified_traj.dcd"

# Create a temporary file for cpptraj commands
with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
    tmpfile_name = tmpfile.name
    
    # Write the cpptraj commands to the temporary file
    tmpfile.write(f"""parm {parm_file}
trajin {traj_file}

#M1

lie :104 :1481 out _FE_lie_I_104_O_1481_BP_HW.dat
lie :104 :1482 out _FE_lie_I_104_O_1482_BP_HW.dat

lie :107 :1481 out _FE_lie_I_107_O_1481_BP_HW.dat
lie :107 :1482 out _FE_lie_I_107_O_1482_BP_HW.dat

lie :108 :1481 out _FE_lie_I_108_O_1481_BP_HW.dat
lie :108 :1482 out _FE_lie_I_108_O_1482_BP_HW.dat

lie :270 :1481 out _FE_lie_I_270_O_1481_BP_HW.dat
lie :270 :1482 out _FE_lie_I_270_O_1482_BP_HW.dat




#M2

lie :844 :1483 out _FE_lie_I_844_O_1483_BP_HH.dat
lie :844 :1484 out _FE_lie_I_844_O_1484_BP_HH.dat

lie :847 :1483 out _FE_lie_I_847_O_1483_BP_HH.dat
lie :847 :1484 out _FE_lie_I_847_O_1484_BP_HH.dat

lie :848 :1483 out _FE_lie_I_848_O_1483_BP_HH.dat
lie :848 :1484 out _FE_lie_I_848_O_1484_BP_HH.dat

lie :1010 :1483 out _FE_lie_I_1010_O_1483_BP_HH.dat
lie :1010 :1484 out _FE_lie_I_1010_O_1484_BP_HH.dat





run
quit
""")

# Execute cpptraj with the temporary command file
subprocess.run(["cpptraj", "-i", tmpfile_name])

# Remove the temporary file after execution
os.remove(tmpfile_name)

print(f"Lie analysis completed.dat'.")

