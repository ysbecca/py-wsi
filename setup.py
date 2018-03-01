from setuptools import setup

description = """Python package for dealing with whole slide images (.svs) for machine learning, including
                intuitive, painless patch sampling using OpenSlide, automatic labeling from ImageScope XML 
                annotation files, and functions for saving these patches and their meta data into lightning
                memory-mapped databases (LMDB) for quick reads.
            """

setup(name='py_wsi',
      version='0.1',
      description=description,
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
      zip_safe=False)