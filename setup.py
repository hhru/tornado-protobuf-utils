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
    version=__import__('protoctor').__version__,
    packages=['protoctor'],
    cmdclass={'test': TestHook},
    install_requires=[
        'nose', 'pep8', 'hhwebutils'
    ]
)
