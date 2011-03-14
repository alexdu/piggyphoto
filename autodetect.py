import piggyphoto as pp

print "libgphoto2 version:"
print pp.library_version()

print "detected cameras:"
cameras = pp.cameraList(autodetect=True)
print cameras
