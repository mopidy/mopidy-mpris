from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-MPRIS',
    version=get_version('mopidy_mpris/__init__.py'),
    url='https://github.com/mopidy/mopidy-mpris',
    license='Apache License, Version 2.0',
    author='Stein Magnus Jodal',
    author_email='stein.magnus@jodal.no',
    description=(
        'Mopidy extension for controlling Mopidy through the '
        'MPRIS D-Bus interface'),
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    python_requires='>=2.7, <3',
    install_requires=[
        'Mopidy >= 1.1',
        'Pykka >= 1.1',
        'pydbus >= 0.6.0',
        'setuptools',
    ],
    entry_points={
        'mopidy.ext': [
            'mpris = mopidy_mpris:Extension',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
