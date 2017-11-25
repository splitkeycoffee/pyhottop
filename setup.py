#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pyhottop',
    version='0.1.0',
    description='',
    url="https://github.com/9b/pyhottop",
    author="Brandon Dixon",
    author_email="brandon@splitkeycoffee.com",
    license="MIT",
    packages=find_packages(),
    install_requires=['pyserial'],
    long_description=read('README.rst'),
    classifiers=[],
    package_data={
        'pyhottop': [],
    },
    entry_points={
        'console_scripts': [
            'pyhottop-test = pyhottop.cli.config:main'
        ]
    },
    include_package_data=True,
    zip_safe=False,
    keywords=['coffee', 'coffee roasting', 'hottop', 'coffee tech'],
    download_url='https://github.com/9b/pyhottop/archive/master.zip'
)