import ctypes
import os

# gphoto structures
""" From 'gphoto2-camera.h'
typedef struct {
        char name [128];
        char folder [1024];
} CameraFilePath;
"""
class CameraFilePath(ctypes.Structure):
    _fields_ = [('name', (ctypes.c_char * 128)),
                ('folder', (ctypes.c_char * 1024))]

class CameraAbilities(ctypes.Structure):
    _fields_ = [('model', (ctypes.c_char * 128)), 
                ('status', ctypes.c_int), 
                ('port', ctypes.c_int), 
                ('speed', (ctypes.c_int * 64)), 
                ('operations', ctypes.c_int), 
                ('file_operations', ctypes.c_int), 
                ('folder_operations', ctypes.c_int), 
                ('usb_vendor', ctypes.c_int), 
                ('usb_product', ctypes.c_int), 
                ('usb_class', ctypes.c_int), 
                ('usb_subclass', ctypes.c_int), 
                ('usb_protocol', ctypes.c_int), 
                ('library', (ctypes.c_char * 1024)), 
                ('id', (ctypes.c_char * 1024)), 
                ('device_type', ctypes.c_int), 
                ('reserved2', ctypes.c_int), 
                ('reserved3', ctypes.c_int), 
                ('reserved4', ctypes.c_int), 
                ('reserved5', ctypes.c_int), 
                ('reserved6', ctypes.c_int), 
                ('reserved7', ctypes.c_int), 
                ('reserved8', ctypes.c_int)]

# gphoto constants
# Defined in 'gphoto2-port-result.h'
GP_OK = 0
# CameraCaptureType enum in 'gphoto2-camera.h'
GP_CAPTURE_IMAGE = 0
# CameraFileType enum in 'gphoto2-file.h'
GP_FILE_TYPE_NORMAL = 1

# Load library
gp = ctypes.CDLL('libgphoto2.so.2')

# Init camera
context = gp.gp_context_new()
camera = ctypes.c_void_p()
print "new"
gp.gp_camera_new(ctypes.pointer(camera))
print "init"
print camera, context
gp.gp_camera_init(camera, context)
print "done"


cam_path = CameraFilePath()
print cam_path.__sizeof__(), cam_path.name, cam_path.folder, "fd"

ab = CameraAbilities()
print ab.status
#print camera, ab.status
print dir(ab)
print ab.__sizeof__()
gp.gp_camera_get_abilities(camera, ctypes.pointer(ab))
print ab
print ab.model

raise SystemExit
# Capture image
ans = gp.gp_camera_capture(camera,
                     GP_CAPTURE_IMAGE,
                     ctypes.pointer(cam_path),
                     context)
print ans
# Download and delete
cam_file = ctypes.c_void_p()
fd = os.open('image.jpg', os.O_CREAT | os.O_WRONLY)
gp.gp_file_new_from_fd(ctypes.pointer(cam_file), fd)
gp.gp_camera_file_get(camera,
                      cam_path.folder,
                      cam_path.name,
                      GP_FILE_TYPE_NORMAL,
                      cam_file,
                      context)
gp.gp_camera_file_delete(camera,
                         cam_path.folder,
                         cam_path.name,
                         context)
gp.gp_file_unref(cam_file)

# Release the camera
gp.gp_camera_exit(camera, context)
gp.gp_camera_unref(camera)

print "done"
