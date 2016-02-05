#!/usr/bin/env python

# Copyright (c) 2013-2015, Kevin Greenan (kmgreen2@gmail.com)
# Copyright (c) 2013-2015, Tushar Gohad (tusharsg@gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.  THIS SOFTWARE IS
# PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import platform
import sys

from ctypes import *
from ctypes.util import *
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.sysconfig import EXEC_PREFIX as _exec_prefix
from distutils.sysconfig import get_python_lib
from distutils.sysconfig import get_python_inc

try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

from setuptools import Extension
from setuptools.command.install import install as _install

platform_str = platform.platform()
default_python_incdir = get_python_inc()


# utility routines
def _read_file_as_str(name):
    with open(name, "rt") as f:
        s = f.readline().strip()
    return s


def _find_library(name):
    target_lib = None
    if os.name == 'posix' and sys.platform.startswith('linux'):
        from ctypes.util import _findLib_gcc
        target_lib = _findLib_gcc(name)
    else:
        target_lib = find_library(name)
    if target_lib:
        target_lib = os.path.abspath(target_lib)
        if os.path.islink(target_lib):
            p = os.readlink(target_lib)
            if os.path.isabs(p):
                target_lib = p
            else:
                target_lib = os.path.join(os.path.dirname(target_lib), p)
    # return absolute path to the library if found
    return target_lib


class build(_build):

    def check_liberasure(self):
        library_basename = "liberasurecode"
        library_version = "1"
        library = library_basename + "-" + library_version
        library_url = "https://bitbucket.org/tsg-/liberasurecode.git"

        if platform_str.find("Darwin") > -1:
            liberasure_file = \
                library_basename + "." + library_version + ".dylib"
        else:
            liberasure_file = \
                library_basename + ".so." + library_version

        found_path = _find_library("erasurecode")
        if found_path:
            if found_path.endswith(library_version) or \
                    found_path.find(library_version + ".") > -1:
                # call 1.x.x the only compatible version for now
                return

        print("**************************************************************")
        print("***                                                           ")
        print("*** Can not locate %s" % (liberasure_file))
        print("***                                                ")
        print("*** Install - ")
        print("***   Manual: %s" % library_url)
        print("***   Fedora/Red Hat variants: liberasurecode-devel")
        print("***   Debian/Ubuntu variants: liberasurecode-dev")
        print("***                                                           ")
        print("**************************************************************")

        sys.exit(-1)

    def run(self):
        self.check_liberasure()
        _build.run(self)


class clean(_clean):

    def run(self):
        _clean.run(self)


class install(_install):

    def run(self):

        install_cmd = self.distribution.get_command_obj('install')
        install_lib = self.distribution.get_command_obj('install_lib')
        for cmd in (install_lib, install_cmd):
            cmd.ensure_finalized()

        # ensure that the paths are absolute so we don't get lost
        opts = {'exec_prefix': install_cmd.exec_prefix,
                'root': install_cmd.root}
        for optname, value in list(opts.items()):
            if value is not None:
                opts[optname] = os.path.abspath(value)

        installroot = install_lib.install_dir
        _install.run(self)

        # Another Mac-ism...  If the libraries are installed
        # in a strange place, DYLD_LIRBARY_PATH needs to be
        # updated.
        if platform_str.find("Darwin") > -1:
            ldpath_str = "DYLD_LIBRARY_PATH"
        else:
            ldpath_str = "LD_LIBRARY_PATH"
        print("***************************************************")
        print("**                                                 ")
        print("** PyECLib libraries have been installed to:       ")
        print("**   %s" % installroot)
        print("**                                                 ")
        print("** Any user using this library must update:        ")
        print("**   %s" % ldpath_str)
        print("**                                                 ")
        print("** Run 'ldconfig' or place this line:              ")
        print("**   export %s=%s" % (ldpath_str, "%s"
                                     % installroot))
        print("**                                                 ")
        print("** into .bashrc, .profile, or the appropriate shell")
        print("** start-up script!  Also look at ldconfig(8) man  ")
        print("** page for a more static LD configuration         ")
        print("**                                                 ")
        print("***************************************************")


module = Extension('pyeclib_c',
                   define_macros=[('MAJOR VERSION', '1'),
                                  ('MINOR VERSION', '2')],
                   include_dirs=[default_python_incdir,
                                 'src/c/pyeclib_c',
                                 '/usr/include',
                                 '/usr/include/liberasurecode',
                                 '%s/include/liberasurecode' % sys.prefix,
                                 '%s/include' % sys.prefix],
                   libraries=['erasurecode'],
                   # The extra arguments are for debugging
                   # extra_compile_args=['-g', '-O0'],
                   sources=['src/c/pyeclib_c/pyeclib_c.c'])

setup(name='PyECLib',
      version='1.2.0',
      author='Kevin Greenan',
      author_email='kmgreen2@gmail.com',
      maintainer='Kevin Greenan and Tushar Gohad',
      maintainer_email='kmgreen2@gmail.com, tusharsg@gmail.com',
      url='https://bitbucket.org/kmgreen2/pyeclib',
      description='This library provides a simple Python interface for \
                   implementing erasure codes.  To obtain the best possible \
                   performance, the underlying erasure code algorithms are \
                   written in C.',
      platforms='Linux',
      license='BSD',
      ext_modules=[module],
      packages=['pyeclib'],
      package_dir={'pyeclib': 'pyeclib'},
      cmdclass={'build': build, 'install': install, 'clean': clean},
      py_modules=['pyeclib.ec_iface', 'pyeclib.core'],
      test_suite='test')
