import os
from cvars import ConVar

def get_addon_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return path

path = get_addon_path()+"/svar/svar.txt"
file = open(path)
lines = [line.rstrip('\n') for line in file]
	
for line in lines:
	if not line.startswith('//'):
		if line != "":
			ConVar(line, "0").set_int(0)
			#ConVar(line).set_int(1)
			#ConVar(line).set_int(0)
file.close()