# piggyphoto.py
# Copyright (C) 2010 Alex Dumitrache
# Based on:
# - a small code example by Mario Boikov, http://pysnippet.blogspot.com/2009/12/when-ctypes-comes-to-rescue.html
# - libgphoto2 Python bindings by David PHAM-VAN <david@ab2r.com>
# - ctypes_gphoto2.py by Hans Ulrich Niedermann <gp@n-dimensional.de>

import ctypes
gp = ctypes.CDLL('libgphoto2.so')

import os
from ptp import *

PTR = ctypes.pointer

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

class CameraText(ctypes.Structure):
    _fields_ = [('text', (ctypes.c_char * (32 * 1024)))]


#cdef extern from "gphoto2/gphoto2-abilities-list.h":
#  ctypedef enum CameraDriverStatus:
GP_DRIVER_STATUS_PRODUCTION = 0
GP_DRIVER_STATUS_TESTING = 1
GP_DRIVER_STATUS_EXPERIMENTAL = 2
GP_DRIVER_STATUS_DEPRECATED = 3

#  ctypedef enum CameraOperation:
GP_OPERATION_NONE = 0
GP_OPERATION_CAPTURE_IMAGE = 1
GP_OPERATION_CAPTURE_VIDEO = 2
GP_OPERATION_CAPTURE_AUDIO = 3
GP_OPERATION_CAPTURE_PREVIEW = 4
GP_OPERATION_CONFIG = 5

#  ctypedef enum CameraFileOperation:
GP_FILE_OPERATION_NONE = 0
GP_FILE_OPERATION_DELETE = 1
GP_FILE_OPERATION_PREVIEW = 2
GP_FILE_OPERATION_RAW = 3
GP_FILE_OPERATION_AUDIO = 4
GP_FILE_OPERATION_EXIF = 5

#  ctypedef enum CameraFolderOperation:
GP_FOLDER_OPERATION_NONE = 0
GP_FOLDER_OPERATION_DELETE_ALL = 1
GP_FOLDER_OPERATION_PUT_FILE = 2
GP_FOLDER_OPERATION_MAKE_DIR = 3
GP_FOLDER_OPERATION_REMOVE_DIR = 4

#cdef extern from "gphoto2/gphoto2-port-info-list.h":
#  ctypedef enum GPPortType:
GP_PORT_NONE = 0
GP_PORT_SERIAL = 1
GP_PORT_USB = 2



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


# Init camera
#context = ctypes.c_void_p(gp.gp_context_new())
#print context, type(context)

context = gp.gp_context_new()

def ptr_add(ptr, offset):
    address = ctypes.addressof(ptr.contents) + offset
    return ctypes.pointer(type(ptr.contents).from_address(address))


def check(result):
    if result!=0:
        gp.gp_result_as_string.restype = ctypes.c_char_p
        txt = gp.gp_result_as_string(result)
        raise Exception('Error ('+str(result)+') : '+txt)

def check_unref(result, camfile):
    if result!=0:
        gp.gp_file_unref(camfile._cf)
        gp.gp_result_as_string.restype = ctypes.c_char_p
        txt = gp.gp_result_as_string(result)
        raise Exception('Error ('+str(result)+') : '+txt)
    
class camera(object):
    _cam = ctypes.c_void_p()
    def __init__(self):
        check(gp.gp_camera_new(PTR(self._cam)))
        
        
    def init(self):
        check(gp.gp_camera_init(self._cam, context))

    def reinit(self):
        gp.gp_camera_free(self._cam)
        self.__new__()
        self.init()

    def __dealloc__(self):
        print "dealloc"
        #check(gp.gp_camera_exit(self._cam, context))
        #check(gp.gp_camera_unref(self._cam))        
        #check(gp.gp_camera_free(self._cam))
        print "dealloc done"

    def _get_summary(self):
        txt = CameraText()
        check(gp.gp_camera_get_summary(self._cam, PTR(txt), context))
        return txt.text
    summary = property(_get_summary, None)


    def _get_abilities(self):
        ab = cameraAbilities()
        check(gp.gp_camera_get_abilities(self._cam, PTR(ab._ab)))
        return ab
    def _set_abilities(self, ab): 
        print "setting camera abilities (doesn't seem to work...)"
        check(gp.gp_camera_set_abilities(self._cam, ab._ab))
    
    abilities = property(_get_abilities, _set_abilities)

    def capture_image(self, destpath = None):
        path = CameraFilePath()
        check(gp.gp_camera_capture(self._cam, GP_CAPTURE_IMAGE, PTR(path), context))
        if destpath:
            self.download_file(path.folder, path.name, destpath)
        else:
            return (path.folder, path.name)

    def capture_preview(self, destpath = None):
        path = CameraFilePath()
        cfile = cameraFile()
        check(gp.gp_camera_capture_preview(self._cam, cfile._cf, context))
        if destpath:
            cfile.save(destpath)
        else:
            return cfile

    def download_file(self, srcfolder, srcfilename, destpath):
        cfile = cameraFile(self._cam, srcfolder, srcfilename)
        cfile.save(destpath)
        gp.gp_file_unref(cfile._cf)
        
        
    def ptp_canon_eos_requestdevicepropvalue(self, prop):
        params = ctypes.c_void_p(self._cam.value + 12)
        gp.ptp_generic_no_data(params, PTP_OC_CANON_EOS_RequestDevicePropValue, 1, prop)
        pass


class cameraFile:
    _cf = ctypes.c_void_p()
    
    def __init__(self, cam = None, srcfolder = None, srcfilename = None):
        check(gp.gp_file_new(PTR(self._cf)))
        if cam:
            check_unref(gp.gp_camera_file_get(cam, srcfolder, srcfilename, GP_FILE_TYPE_NORMAL, self._cf, context), self )
            

    def open(self, filename):
        check(gp.gp_file_open(PTR(self._cf), filename))

    def save(self, filename = None):
        if filename is None: filename = self.name
        print "Saving", filename
        check(gp.gp_file_save(self._cf, filename))

    def ref(self):
        check(gp.gp_file_ref(self._cf))
        
    def unref(self):
        check(gp.gp_file_unref(self._cf))

    def clean(self):
        check(gp.gp_file_clean(self._cf))

    def copy(self, source):
        check(gp.gp_file_copy(self._cf, source._cf))

    def __dealoc__(self, filename):
        check(gp.gp_file_free(self._cf))

    def _get_name(self):
        name = ctypes.c_char_p()
        check(gp.gp_file_get_name(self._cf, PTR(name)))
        return name.value

    def _set_name(self, name):
        check(gp.gp_file_set_name(self._cf, name))
        
    name = property(_get_name, _set_name)
        
class cameraAbilities:
    _ab = CameraAbilities()

    def __init__(self):
        pass

    def __repr__(self):
        return "Model : %s\nStatus : %d\nPort : %d\nOperations : %d\nFile Operations : %d\nFolder Operations : %d\nUSB (vendor/product) : 0x%x/0x%x\nUSB class : 0x%x/0x%x/0x%x\nLibrary : %s\nId : %s\n" % (self._ab.model, self._ab.status, self._ab.port, self._ab.operations, self._ab.file_operations, self._ab.folder_operations, self._ab.usb_vendor, self._ab.usb_product, self._ab.usb_class, self._ab.usb_subclass, self._ab.usb_protocol, self._ab.library, self._ab.id)
    
    model = property(lambda self: self._ab.model, None)
    status = property(lambda self: self._ab.status, None)
    port = property(lambda self: self._ab.port, None)
    operations = property(lambda self: self._ab.operations, None)
    file_operations = property(lambda self: self._ab.file_operations, None)
    folder_operations = property(lambda self: self._ab.folder_operations, None)
    usb_vendor = property(lambda self: self._ab.usb_vendor, None)
    usb_product = property(lambda self: self._ab.usb_product, None)
    usb_class = property(lambda self: self._ab.usb_class, None)
    usb_subclass = property(lambda self: self._ab.usb_subclass, None)
    usb_protocol = property(lambda self: self._ab.usb_protocol, None)
    library = property(lambda self: self._ab.library, None)
    id = property(lambda self: self._ab.id, None)
