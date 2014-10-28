# coding=utf-8

from distutils.core import setup
from setuptools.command.test import test


class TestHook(test):
    def run(self):
        test.run(self)

        import nose
        nose.main(argv=['tests', '-v'])


setup(
    name='hh-tornado-protobuf-utils',
    version='0.0.1',
    packages=['protoctor'],
    cmdclass={'test': TestHook},
    install_requires=[
        'nose', 'pep8'
    ]
)
