from pprint import pprint
import piggyphoto as pp
import os
import time

# doesn't work...

C = pp.camera()
C.leave_locked()

#print C.abilities
#C.list_config()

C.config.main.imgsettings.iso.value = 3
print C.config.main.imgsettings.iso

C.config.main.actions.bulb.value = 1
print C.config.main.actions.bulb
time.sleep(1)
print C.config.main.actions.bulb.value
print C.config.main.actions.bulb

#print dir(C.config.main.actions)
#print dir(cfg.main)
#for i in range(10):
#C.capture_preview('preview.jpg')

print "done"

