from setuptools import setup

setup(name='py_wsi',
      version='0.1',
      description='Patch sampling and storing Python package for whole slide image (.svs) analysis',
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
