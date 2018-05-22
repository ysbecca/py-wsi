from setuptools import setup
from os import path

description = """Python package for dealing with whole slide images (.svs) for machine learning, including
                intuitive, painless patch sampling using OpenSlide, automatic labeling from ImageScope XML 
                annotation files, and functions for saving these patches and their meta data into lightning
                memory-mapped databases (LMDB) for quick reads.
            """

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='py_wsi',
      version='1.0',
      description=description,
      long_description=long_description,
      url='https://github.com/ysbecca/py-wsi',
      author='Rebecca Stone',
      author_email='ysbecca@gmail.com',
      license='GNU General Public License v3.0',
      packages=['py_wsi'],
      install_requires=[
          'shapely',
          'numpy',
          'openslide-python',
          'lmdb',
          'Pillow',
      ],
      keywords='whole slide images svs openslide lmdb machine learning', 
      zip_safe=False)