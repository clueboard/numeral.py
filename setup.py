#!/usr/bin/env python
# Special thanks to Hynek Schlawack for providing excellent documentation:
#
# https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
import os
from setuptools import setup


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='rgb7seg',
    version='0.0.1',
    description='Support for the Clueboard RGB7Segment Display',
    long_description='\n\n'.join((read('README.md'), read('AUTHORS.md'))),
    url='https://github.com/skullydazed/rgb7seg.py',
    license='MIT',
    author='Zach White',
    author_email='skullydazed@gmail.com',
    py_modules=['rgb7seg'],
    include_package_data=True,
    scripts=['rgb7seg_alphabet', 'rgb7seg_breathing', 'rgb7seg_colors', 'rgb7seg_countdown', 'rgb7seg_countup'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Systems Administration',
    ],
)
