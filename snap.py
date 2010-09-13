import piggyphoto as pp
import os
import time

C = pp.camera()

try:
    C.init()
except:
    os.system("gvfs-mount -s gphoto2")
    time.sleep(1)
    C.init()

print C.abilities
for i in range(100):
    f = C.capture_preview('%d.jpg' % i)
print "done"

