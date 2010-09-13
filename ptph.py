import re

f = open("ptp.h")
out = open("ptp.py", "w")
out.write("# Constants extracted from gphoto2's ptp.h\n\n")
lines = f.readlines()

for line in lines:
    line = line.strip()
    reg = r"^#define\s+([a-zA-Z0-9_]+)\s+(.*)"
    m = re.match(reg, line)
    if m:
        #print line
        g = m.groups()
        name, value = g[0], g[1]
        value = value.replace("/*", "#")
        value = value.replace("//", "#")
        out.write("%s = %s\n" % (name, value))
