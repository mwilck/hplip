#!/usr/bin/env python

from distutils.core import setup, Extension, Command
import distutils.core
import os, sys


setup( name="cupsext",
       ext_modules=[ Extension(  "cupsext", [ "cupsext.c" ], libraries=["cups"] ) ],
       version="0.1" )
