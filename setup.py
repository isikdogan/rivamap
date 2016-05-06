import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'rivamap',
    version = '1.0',
    author = 'Leo Isikdogan',
    author_email = 'leo@isikdogan.com',
    description = ('An automated river analysis and mapping engine.'),
    keywords = 'remote sensing, landsat, satellite, river',
    url = 'https://github.com/isikdogan/rivamap',
    packages = ['rivamap'],
    long_description = 'See project webpage for details: http://live.ece.utexas.edu/research/cne/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=['numpy', 'scipy', 'matplotlib', 'gdal'],
)