piggyphoto
==========

Python bindings for libgphoto2.

This is a very rough proof of concept. Feel free to play with it and add improvements.

Usage
-----

You have to install [libgphoto2](http://www.gphoto.org/proj/libgphoto2/). It should work with any version, from the one prepackaged in Ubuntu to the latest SVN checkout. In theory, of course :)

    import piggyphoto
    
    C = piggyphoto.camera()
    C.init()
    print C.abilities
    C.capture_preview('preview.jpg')
    C.capture_image('image.jpg')

Enjoy!
