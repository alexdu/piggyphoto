#!/usr/bin/env python2.7
import os
from setuptools import setup

import piggyphoto

setup(
    name="piggyphoto",
    version=piggyphoto.__version__,
    author="Alex Dumitrache",
    author_email="alexdu@easynet.ro",
    url="https://github.com/alexdu/piggyphoto",
    description="Python bindings for libgphoto2 (http://www.gphoto.org/)",
    license="MIT",
    keywords=[
        "gphoto",
    ],
    packages=[
        "piggyphoto",
    ],
)
