import os
from setuptools import find_packages
from distutils.core import setup
from snakehouse import Multibuild, build, monkey_patch_parallel_compilation, find_pyx

monkey_patch_parallel_compilation()

build_kwargs = {}
directives = {'language_level': '3'}
dont_snakehouse = False
multi_kwargs = {}
if 'DEBUG' in os.environ:
    dont_snakehouse = True
    build_kwargs.update(gdb_debug=True)
    directives['embedsignature'] = True
    directives['linetrace'] = True
    multi_kwargs['define_macros'] = [('CYTHON_TRACE', '1')]


setup(version='1.7',
      packages=find_packages(include=['minijson', 'minijson.*']),
      ext_modules=build([Multibuild('minijson', find_pyx('minijson'),
                                    dont_snakehouse=dont_snakehouse,
                                    **multi_kwargs), ],
                        compiler_directives=directives, **build_kwargs),
      python_requires='!=2.7.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,!=3.6.*,!=3.7.*',
      tests_require=[
          "nose2", "mock", "coverage", "nose2[coverage_plugin]"
      ],
      test_suite='nose2.collector.collector',
      zip_safe=False
      )
