# coding=utf-8

import os

from distutils.core import setup
from setuptools.command.build_py import build_py
from setuptools.command.test import test

from protoctor.version import version


class TestHook(test):
    def run(self):
        test.run(self)

        import nose
        nose.main(argv=['tests', '-v'])


class BuildHook(build_py):
    def run(self):
        build_py.run(self)

        build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.build_lib, 'protoctor')
        with open(os.path.join(build_dir, 'version.py'), 'w') as version_file:
            version_file.write('version = "{0}"\n'.format(version))


setup(
    name='hh-tornado-protobuf-utils',
    version=__import__('protoctor').__version__,
    packages=['protoctor'],
    cmdclass={'build_py': BuildHook, 'test': TestHook},
    install_requires=[
        'nose', 'hhwebutils'
    ],
    tests_require=[
        'pep8 < 1.6'
    ]
)
