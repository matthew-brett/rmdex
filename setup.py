#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Installation script for rmdex package '''
import re
import os
from os.path import join as pjoin, split as psplit, splitext

from setuptools import setup

import versioneer

# Get install requirements from requirements.txt file
with open('requirements.txt', 'rt') as fobj:
    install_requires = [line.strip() for line in fobj
                        if line.strip() and not line[0] in '#-']
# Get any extra test requirements
with open('test-requirements.txt', 'rt') as fobj:
    test_requires = [line.strip() for line in fobj
                     if line.strip() and not line[0] in '#-']

# Requires for distutils (only used in pypi interface?)
break_ver = re.compile(r'(\S+?)(\[\S+\])?([=<>!]+\S+)')
requires = [break_ver.sub(r'\1 (\3)', req) for req in install_requires]

# See: https://github.com/matthew-brett/myscripter
from distutils.command.install_scripts import install_scripts
from distutils import log

BAT_TEMPLATE = \
r"""@echo off
REM wrapper to use shebang first line of {FNAME}
set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set /p line1=<%pyscript%
if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1
:goodstart
set py_exe=%line1:~2%
call "%py_exe%" %pyscript% %*
"""

class my_install_scripts(install_scripts):
    """ Install .bat wrapper for scripts on Windows """
    def run(self):
        install_scripts.run(self)
        if not os.name == "nt":
            return
        for filepath in self.get_outputs():
            # If we can find an executable name in the #! top line of the
            # script file, make .bat wrapper for script.
            with open(filepath, 'rt') as fobj:
                first_line = fobj.readline()
            if not (first_line.startswith('#!') and
                    'python' in first_line.lower()):
                log.info("No #!python executable found, skipping .bat "
                            "wrapper")
                continue
            pth, fname = psplit(filepath)
            froot, ext = splitext(fname)
            bat_file = pjoin(pth, froot + '.bat')
            bat_contents = BAT_TEMPLATE.replace('{FNAME}', fname)
            log.info("Making %s wrapper for %s" % (bat_file, filepath))
            if self.dry_run:
                continue
            with open(bat_file, 'wt') as fobj:
                fobj.write(bat_contents)


cmdclass = versioneer.get_cmdclass()
cmdclass['install_scripts'] = my_install_scripts


setup(name='rmdex',
      version=versioneer.get_version(),
      cmdclass=cmdclass,
      description='Utilities for processing exercises in notebooks',
      author='Matthew Brett',
      author_email='matthew.brett@gmail.com',
      maintainer='Matthew Brett',
      maintainer_email='matthew.brett@gmail.com',
      url='http://github.com/matthew-brett/rmdex',
      packages=['rmdex',
                'rmdex.tests'],
      package_data = {'rmdex': [
          'tests/data/*',
      ]},
      license='BSD license',
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Operating System :: MacOS',
        ],
      long_description = open('README.rst', 'rt').read(),
      install_requires = install_requires,
      extras_require = {'test': test_requires},
      # For pip versions >= 9
      python_requires = '>=3.4',
      scripts = [pjoin('scripts', 'rmdex_check') ,
                 pjoin('scripts', 'rmdex_add_marks')],
      )
