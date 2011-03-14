# piggyphoto.py
# Copyright (C) 2010 Alex Dumitrache
# Based on:
# - a small code example by Mario Boikov, http://pysnippet.blogspot.com/2009/12/when-ctypes-comes-to-rescue.html
# - libgphoto2 Python bindings by David PHAM-VAN <david@ab2r.com>
# - ctypes_gphoto2.py by Hans Ulrich Niedermann <gp@n-dimensional.de>

# Some functions return errors which can be fixed by retrying.
# For example, capture_preview on Canon 550D fails the first time, but subsequent calls are OK.
# Retries are performed on: camera.capture_preview, camera.capture_image and camera.init()
retries = 1

# This is run if gp_camera_init returns -60 (Could not lock the device) and retries >= 1.
unmount_cmd = 'gvfs-mount -s gphoto2'

#libgphoto2dll = 'libgphoto2.so.2.4.0'
libgphoto2dll = 'libgphoto2.so'
# 2.4.6
#libgphoto2dll = '/usr/lib/libgphoto2.so'
# 2.4.8
#libgphoto2dll = '/usr/local/lib/libgphoto2.so.2'
# SVN
#libgphoto2dll = '/usr/local/lib/libgphoto2.so.6'

import re
import ctypes
gp = ctypes.CDLL(libgphoto2dll)
context = gp.gp_context_new()

def library_version(verbose = True):
    gp.gp_library_version.restype = ctypes.POINTER(ctypes.c_char_p)
    if not verbose:
        arrText = gp.gp_library_version(GP_VERSION_SHORT)
    else:
        arrText = gp.gp_library_version(GP_VERSION_VERBOSE)

    v = ''
    for s in arrText:
        if s is None:
            break
        v += '%s\n' % s
    return v

import os, string, time
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

#cdef extern from "gphoto2/gphoto2-port-version.h":
#  ctypedef enum GPVersionVerbosity:
GP_VERSION_SHORT = 0
GP_VERSION_VERBOSE = 1

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

# the GPPortInfo data structure is a pointer in SVN
# in stable versions, it is a struct
if library_version().split('\n')[0] == '2.4.99':
    class PortInfo(ctypes.c_void_p):
        pass
else:
    class PortInfo(ctypes.Structure):
        _fields_ = [
                ('type', ctypes.c_int), # enum is 32 bits on 32 and 64 bit Linux
                ('name', (ctypes.c_char * 64)),
                ('path', (ctypes.c_char * 64)),
                ('library_filename', (ctypes.c_char * 1024))
                ]

# gphoto constants
# Defined in 'gphoto2-port-result.h'
GP_OK = 0
# CameraCaptureType enum in 'gphoto2-camera.h'
GP_CAPTURE_IMAGE = 0
# CameraFileType enum in 'gphoto2-file.h'
GP_FILE_TYPE_NORMAL = 1



GP_WIDGET_WINDOW = 0  # Window widget This is the toplevel configuration widget. It should likely contain multiple GP_WIDGET_SECTION entries.
GP_WIDGET_SECTION = 1 # Section widget (think Tab).
GP_WIDGET_TEXT = 2    # Text widget.
GP_WIDGET_RANGE = 3   # Slider widget.
GP_WIDGET_TOGGLE = 4  # Toggle widget (think check box).
GP_WIDGET_RADIO = 5   # Radio button widget.
GP_WIDGET_MENU = 6    # Menu widget (same as RADIO).
GP_WIDGET_BUTTON = 7  # Button press widget.
GP_WIDGET_DATE = 8    # Date entering widget.
widget_types = ['Window', 'Section', 'Text', 'Range', 'Toggle', 'Radio', 'Menu', 'Button', 'Date']

class CameraWidget(ctypes.Structure):
    _fields_ = [('type', ctypes.c_int),
                ('label', (ctypes.c_char * 256)),
                ('info', (ctypes.c_char * 1024)),
                ('name', (ctypes.c_char * 256)),
                ('parent', (ctypes.c_void_p)),
                ('value_string', ctypes.c_char_p),
                ('value_int', ctypes.c_int),
                ('value_float', ctypes.c_float),
                ('choice', (ctypes.c_void_p)),
                ('choice_count', ctypes.c_int),
                ('min', ctypes.c_float),
                ('max', ctypes.c_float),
                ('increment', ctypes.c_float),
                ('children', (ctypes.c_void_p)),
                ('children_count', (ctypes.c_int)),
                ('changed', (ctypes.c_int)),
                ('readonly', (ctypes.c_int)),
                ('ref_count', (ctypes.c_int)),
                ('id', (ctypes.c_int)),
                ('callback', (ctypes.c_void_p))]


class libgphoto2error(Exception):
    def __init__(self, result, message):
        self.result = result
        self.message = message
    def __str__(self):
        return self.message + ' (' + str(self.result) + ')'

def check(result):
    if result < 0:
        gp.gp_result_as_string.restype = ctypes.c_char_p
        message = gp.gp_result_as_string(result)
        raise libgphoto2error(result, message)
    return result

def check_unref(result, camfile):
    if result!=0:
        gp.gp_file_unref(camfile._cf)
        gp.gp_result_as_string.restype = ctypes.c_char_p
        message = gp.gp_result_as_string(result)
        raise libgphoto2error(result, message)

class camera(object):
    def __init__(self, autoInit = True):
        self._cam = ctypes.c_void_p()
        self._leave_locked = False
        check(gp.gp_camera_new(PTR(self._cam)))
        self.initialized = False
        if autoInit:
            self.init()

    def init(self):
        if self.initialized:
            print "Camera is already initialized."
        ans = 0
        for i in range(1 + retries):
            ans = gp.gp_camera_init(self._cam, context)
            if ans == 0:
                break
            elif ans == -60:
                print "***", unmount_cmd
                os.system(unmount_cmd)
                time.sleep(1)
                print "camera.init() retry #%d..." % (i)
        check(ans)
        self.initialized = True

    def reinit(self):
        gp.gp_camera_free(self._cam)
        self.__new__()
        self.init()

    def __del__(self):
        if not self._leave_locked:
            check(gp.gp_camera_exit(self._cam))
            check(gp.gp_camera_free(self._cam))

    def leave_locked(self):
        self._leave_locked = True

    def ref(self):
        check(gp.gp_camera_ref(self._cam))

    def unref(self):
        check(gp.gp_camera_unref(self._cam))

    def exit(self):
        check(gp.gp_camera_exit(self._cam, context))

    def _get_summary(self):
        txt = CameraText()
        check(gp.gp_camera_get_summary(self._cam, PTR(txt), context))
        return txt.text
    summary = property(_get_summary, None)

    def _get_manual(self):
        txt = CameraText()
        check(gp.gp_camera_get_manual(self._cam, PTR(txt), context))
        return txt.text
    manual = property(_get_manual, None)

    def _get_about(self):
        txt = CameraText()
        check(gp.gp_camera_get_about(self._cam, PTR(txt), context))
        return txt.text
    about = property(_get_about, None)

    def _get_abilities(self):
        ab = cameraAbilities()
        check(gp.gp_camera_get_abilities(self._cam, PTR(ab._ab)))
        return ab
    def _set_abilities(self, ab):
        check(gp.gp_camera_set_abilities(self._cam, ab._ab))
    abilities = property(_get_abilities, _set_abilities)

    def _get_config(self):
        window = cameraWidget(GP_WIDGET_WINDOW)
        check(gp.gp_camera_get_config(self._cam, PTR(window._w), context))
        window.populate_children()
        return window
    def _set_config(self, window):
        check(gp.gp_camera_set_config(self._cam, window._w, context))
    config = property(_get_config, _set_config)

    def _get_port_info(self):
        raise NotImplementedError
    def _set_port_info(self, info):
        check(gp.gp_camera_set_port_info(self._cam, info))
    port_info = property(_get_port_info, _set_port_info)

    def capture_image(self, destpath = None):
        path = CameraFilePath()

        ans = 0
        for i in range(1 + retries):
            ans = gp.gp_camera_capture(self._cam, GP_CAPTURE_IMAGE, PTR(path), context)
            if ans == 0: break
            else: print "capture_image(%s) retry #%d..." % (destpath, i)
        check(ans)

        if destpath:
            self.download_file(path.folder, path.name, destpath)
        else:
            return (path.folder, path.name)

    def capture_preview(self, destpath = None):
        path = CameraFilePath()
        cfile = cameraFile()

        ans = 0
        for i in range(1 + retries):
            ans = gp.gp_camera_capture_preview(self._cam, cfile._cf, context)
            if ans == 0: break
            else: print "capture_preview(%s) retry #%d..." % (destpath, i)
        check(ans)

        if destpath:
            cfile.save(destpath)
        else:
            return cfile

    def download_file(self, srcfolder, srcfilename, destpath):
        cfile = cameraFile(self._cam, srcfolder, srcfilename)
        cfile.save(destpath)
        gp.gp_file_unref(cfile._cf)

    def trigger_capture(self):
        check(gp.gp_camera_trigger_capture(self._cam, context))

    def wait_for_event(self, timeout):
        raise NotImplementedError

    def list_folders(self, path = "/"):
        l = cameraList()
        check(gp.gp_camera_folder_list_folders(self._cam, str(path), l._l, context));
        return l.toList()

    def list_files(self, path = "/"):
        l = cameraList()
        check(gp.gp_camera_folder_list_files(self._cam, str(path), l._l, context));
        return l.toList()

    def _list_config(self, widget, cfglist, path):
        children = widget.children
        if children:
            for c in children:
                self._list_config(c, cfglist, path + "." + c.name)
        else:
            print path, "=", widget.value
            cfglist.append(path)

    def list_config(self):
        cfglist = []
        cfg = self.config
        self._list_config(cfg, cfglist, cfg.name)
        return cfglist

    def ptp_canon_eos_requestdevicepropvalue(self, prop):
        params = ctypes.c_void_p(self._cam.value + 12)
        gp.ptp_generic_no_data(params, PTP_OC_CANON_EOS_RequestDevicePropValue, 1, prop)

    # TODO: port_speed, init, config

class cameraFile(object):
    def __init__(self, cam = None, srcfolder = None, srcfilename = None):
        self._cf = ctypes.c_void_p()
        check(gp.gp_file_new(PTR(self._cf)))
        if cam:
            check_unref(gp.gp_camera_file_get(cam, srcfolder, srcfilename, GP_FILE_TYPE_NORMAL, self._cf, context), self)


    def open(self, filename):
        check(gp.gp_file_open(PTR(self._cf), filename))

    def save(self, filename = None):
        if filename is None: filename = self.name
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
        check(gp.gp_file_set_name(self._cf, str(name)))
    name = property(_get_name, _set_name)

    # TODO: new_from_fd (?), new_from_handler (?), mime_tipe, mtime, detect_mime_type, adjust_name_for_mime_type, data_and_size, append, slurp, python file object?

class cameraAbilitiesList(object):
    _static_l = None
    def __init__(self):
        if cameraAbilitiesList._static_l is None:
            cameraAbilitiesList._static_l = ctypes.c_void_p()
            check(gp.gp_abilities_list_new(PTR(cameraAbilitiesList._static_l)))
            check(gp.gp_abilities_list_load(cameraAbilitiesList._static_l, context))
        self._l = cameraAbilitiesList._static_l

    def __del__(self):
        # don't free, since it is only created once
        #check(gp.gp_abilities_list_free(self._l))
        pass

    def detect(self, il, l):
        check(gp.gp_abilities_list_detect(self._l, il._l, l._l, context))

    def lookup_model(self, model):
        return check(gp.gp_abilities_list_lookup_model(self._l, model))

    def get_abilities(self, model_index, ab):
        check(gp.gp_abilities_list_get_abilities(self._l, model_index, PTR(ab._ab)))

class cameraAbilities(object):
    def __init__(self):
        self._ab = CameraAbilities()

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

class portInfoList(object):
    _static_l = None
    def __init__(self):
        if portInfoList._static_l is None:
            portInfoList._static_l = ctypes.c_void_p()
            check(gp.gp_port_info_list_new(PTR(portInfoList._static_l)))
            check(gp.gp_port_info_list_load(portInfoList._static_l))
        self._l = portInfoList._static_l

    def __del__(self):
        # don't free, since it is only created once
        #check(gp.gp_port_info_list_free(self._l))
        pass

    def count(self):
        c = gp.gp_port_info_list_count(self._l)
        check(c)
        return c

    def lookup_path(self, path):
        index = gp.gp_port_info_list_lookup_path(self._l, path)
        check(index)
        return index

    def get_info(self, path_index):
        info = PortInfo()
        check(gp.gp_port_info_list_get_info(self._l, path_index, PTR(info)))
        return info

class cameraList(object):
    def __init__(self, autodetect=False):
        self._l = ctypes.c_void_p()
        check(gp.gp_list_new(PTR(self._l)))

        if autodetect == True:
            if hasattr(gp, 'gp_camera_autodetect'):
                gp.gp_camera_autodetect(self._l, context)
            else:
                # this is for stable versions of gphoto <= 2.4.10.1
                xlist = cameraList()
                il = portInfoList()
                il.count()
                al = cameraAbilitiesList()
                al.detect(il, xlist)
                for i in xrange(xlist.count()):
                    model = xlist.get_name(i)
                    path = xlist.get_value(i)
                    if re.match(r'usb:\d{3},\d{3}', path):
                        self.append(model, path)
                del al
                del il
                del xlist

    def ref(self):
        check(gp.gp_list_ref(self._l))

    def unref(self):
        check(gp.gp_list_ref(self._l))

    def __del__(self):
        # this failed once in gphoto 2.4.6
        check(gp.gp_list_free(self._l))
        pass

    def reset(self):
        #check(gp.gp_list_free(self._l))
        #check(gp.gp_list_new(PTR(self._l)))
        check(gp.gp_list_reset(self._l))

    def append(self, name, value):
        check(gp.gp_list_append(self._l, str(name), str(value)))

    def sort(self):
        check(gp.gp_list_sort(self._l))

    def count(self):
        return check(gp.gp_list_count(self._l))

    def find_by_name(self, name):
        index = ctypes.c_int()
        check(gp.gp_list_find_by_name(self._l, PTR(index), str(name)))
        return index.value

    def get_name(self, index):
        name = ctypes.c_char_p()
        check(gp.gp_list_get_name(self._l, int(index), PTR(name)))
        return name.value

    def get_value(self, index):
        value = ctypes.c_char_p()
        check(gp.gp_list_get_value(self._l, int(index), PTR(value)))
        return value.value

    def set_name(self, index, name):
        check(gp.gp_list_set_name(self._l, int(index), str(name)))

    def set_value(self, index, value):
        check(gp.gp_list_set_value(self._l, int(index), str(value)))

    def __str__(self):
        header = "cameraList object with %d elements:\n" % self.count()
        contents = ["%d: (%s, %s)" % (i, self.get_name(i), self.get_value(i))
            for i in range(self.count())]

        return header + string.join(contents, "\n")

    def toList(self):
        return [(self.get_name(i), self.get_value(i)) for i in xrange(self.count())]
        xlist = []
        for i in range(self.count()):
            n, v = self.get_name(i), self.get_value(i)
            if v is None:
                xlist.append(n)
            else:
                xlist.append((n, v))
        return xlist

    def toDict(self):
        return dict(self.toList())

class cameraWidget(object):

    def __init__(self, type = None, label = ""):
        self._w = ctypes.c_void_p()
        if type is not None:
            check(gp.gp_widget_new(int(type), str(label), PTR(self._w)))
            check(gp.gp_widget_ref(self._w))
        else:
            self._w = ctypes.c_void_p()

    def ref(self):
        check(gp.gp_widget_ref(self._w))

    def unref(self):
        check(gp.gp_widget_unref(self._w))

    def __del__(self):
        # TODO fix this or find a good reason not to
        #print "widget(%s) __del__" % self.name
        #check(gp.gp_widget_unref(self._w))
        pass

    def _get_info(self):
        info = ctypes.c_char_p()
        check(gp.gp_widget_get_info(self._w, PTR(info)))
        return info.value
    def _set_info(self, info):
        check(gp.gp_widget_set_info(self._w, str(info)))
    info = property(_get_info, _set_info)

    def _get_name(self):
        name = ctypes.c_char_p()
        check(gp.gp_widget_get_name(self._w, PTR(name)))
        return name.value
    def _set_name(self, name):
        check(gp.gp_widget_set_name(self._w, str(name)))
    name = property(_get_name, _set_name)

    def _get_id(self):
        id = ctypes.c_int()
        check(gp.gp_widget_get_id(self._w, PTR(id)))
        return id.value
    id = property(_get_id, None)

    def _set_changed(self, changed):
        check(gp.gp_widget_set_changed(self._w, str(changed)))
    def _get_changed(self):
        return gp.gp_widget_changed(self._w)
    changed = property(_get_changed, _set_changed)

    def _get_readonly(self):
        readonly = ctypes.c_int()
        check(gp.gp_widget_get_readonly(self._w, PTR(readonly)))
        return readonly.value
    def _set_readonly(self, readonly):
        check(gp.gp_widget_set_readonly(self._w, int(readonly)))
    readonly = property(_get_readonly, _set_readonly)

    def _get_type(self):
        type = ctypes.c_int()
        check(gp.gp_widget_get_type(self._w, PTR(type)))
        return type.value
    type = property(_get_type, None)

    def _get_typestr(self):
        return widget_types[self.type]
    typestr = property(_get_typestr, None)

    def _get_label(self):
        label = ctypes.c_char_p()
        check(gp.gp_widget_get_label(self._w, PTR(label)))
        return label.value
    def _set_label(self, label):
        check(gp.gp_widget_set_label(self._w, str(label)))
    label = property(_get_label, _set_label)

    def _get_value(self):
        value = ctypes.c_void_p()
        ans = gp.gp_widget_get_value(self._w, PTR(value))
        if self.type in [GP_WIDGET_MENU, GP_WIDGET_RADIO, GP_WIDGET_TEXT]:
            value = ctypes.cast(value.value, ctypes.c_char_p)
        elif self.type == GP_WIDGET_RANGE:
            value = ctypes.cast(value.value, ctypes.c_float_p)
        elif self.type in [GP_WIDGET_TOGGLE, GP_WIDGET_DATE]:
            #value = ctypes.cast(value.value, ctypes.c_int_p)
            pass
        else:
            return None
        check(ans)
        return value.value
    def _set_value(self, value):
        if self.type in (GP_WIDGET_MENU, GP_WIDGET_RADIO, GP_WIDGET_TEXT):
            value = ctypes.c_char_p(value)
        elif self.type == GP_WIDGET_RANGE:
            value = ctypes.c_float_p(value) # this line not tested
        elif self.type in (GP_WIDGET_TOGGLE, GP_WIDGET_DATE):
            value = PTR(ctypes.c_int(value))
        else:
            return None # this line not tested
        check(gp.gp_widget_set_value(self._w, value))
    value = property(_get_value, _set_value)

    def append(self, child):
        check(gp.gp_widget_append(self._w, child._w))

    def prepend(self, child):
        check(gp.gp_widget_prepend(self._w, child._w))

    def count_children(self):
        return gp.gp_widget_count_children(self._w)

    def get_child(self, child_number):
        w = cameraWidget()
        check(gp.gp_widget_get_child(self._w, int(child_number), PTR(w._w)))
        check(gp.gp_widget_ref(w._w))
        return w

    def get_child_by_label(self, label):
        w = cameraWidget()
        check(gp.gp_widget_get_child_by_label(self._w, str(label), PTR(w._w)))
        return w

    def get_child_by_id(self, id):
        w = cameraWidget()
        check(gp.gp_widget_get_child_by_id(self._w, int(id), PTR(w._w)))
        return w

    def get_child_by_name(self, name):
        w = cameraWidget()
        # this fails in 2.4.6 (Ubuntu 9.10)
        check(gp.gp_widget_get_child_by_name(self._w, str(name), PTR(w._w)))
        return w

    def _get_children(self):
        children = []
        for i in range(self.count_children()):
            children.append(self.get_child(i))
        return children
    children = property(_get_children, None)

    def _get_parent(self):
        w = cameraWidget()
        check(gp.gp_widget_get_parent(self._w, PTR(w._w)))
        return w
    parent = property(_get_parent, None)

    def _get_root(self):
        w = cameraWidget()
        check(gp.gp_widget_get_root(self._w, PTR(w._w)))
        return w
    root = property(_get_root, None)

    def _set_range(self, range):
        """cameraWidget.range = (min, max, increment)"""
        float = ctypes.c_float
        min, max, increment = range
        check(gp.gp_widget_set_range(self._w, float(min), float(max), float(increment)))
        return w
    def _get_range(self, range):
        """cameraWidget.range => (min, max, increment)"""
        min, max, increment = ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
        check(gp.gp_widget_set_range(self._w, PTR(min), PTR(max), PTR(increment)))
        return (min.value, max.value, increment.value)
    range = property(_get_range, _set_range)

    def add_choice(self, choice):
        check(gp.gp_widget_add_choice(self._w, str(choice)))

    def count_choices(self, choice):
        return gp.gp_widget_count_choices(self._w)

    def get_choice(self, choice_number):
        choice = ctypes.c_char_p()
        check(gp.gp_widget_add_choice(self._w, int(choice_number), PTR(choice)))
        return choice.value

    def createdoc(self):
        label = "Label: " + self.label
        info = "Info: " + (self.info if self.info != "" else "n/a")
        type = "Type: " + self.typestr
        #value = "Current value: " + str(self.value)
        childs = []
        for c in self.children:
            childs.append("  - " + c.name + ": " + c.label)
        if len(childs):
            childstr = "Children:\n" + string.join(childs, "\n")
            return label + "\n" + info + "\n" + type + "\n" + childstr
        else:
            return label + "\n" + info + "\n" + type

    def _pop(widget, simplewidget):
        #print widget
        for c in widget.children:
            simplechild = cameraWidgetSimple()
            if c.count_children():
                setattr(simplewidget, c.name, simplechild)
                simplechild.__doc__ = c.createdoc()
                c._pop(simplechild)
            else:
                setattr(simplewidget, c.name, c)

            #print c.name, simplewidget.__doc__
        #print dir(simplewidget)

    def populate_children(self):
        simplewidget = cameraWidgetSimple()
        setattr(self, self.name, simplewidget)
        simplewidget.__doc__ = self.createdoc()
        self._pop(simplewidget)

    def __repr__(self):
        return "%s:%s:%s:%s:%s" % (self.label, self.name, self.info, self.typestr, self.value)

class cameraWidgetSimple(object):
    pass
