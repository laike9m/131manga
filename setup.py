#!/usr/bin/env python
#coding=utf-8

import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = "simple_PyQt4",
        version = "0.1",
        description = "Sample cx_Freeze PyQt4 script",
        options = {"build_exe" : {"includes" : "atexit" }},
        executables = [Executable("131manhua.py", base = base,icon = "icon.ico")])

