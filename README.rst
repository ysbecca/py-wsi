py-wsi
======

Current version
---------------

**Notice: it is strongly recommended to use py-wsi version >= 1.0.**

The current update to py_wsi has added three major improvements which
are essential for dealing with very large datasets of .svs images:

-  better memory management
-  error handling
-  functionality to allow for sampling test patches before sampling from
   all images

See this blog post `py_wsi for computer analysis on whole slide .svs
images using OpenSlide <https://ysbecca.github.io>`__ for help on
understanding the relationship between patch and tile sampling. The test
patch sampling functionality in this version will also help users to
know exactly what they are sampling.

For any early users who have downloaded previous versions of py_wsi (<
1.0) I would **strongly suggest downloading the update**. Please feel
free to submit any issues to the GitHub repository and I will provide
help as I am able to.

While suggestions for extra/additional functionality will not be
immediately considered, pull requests are welcome.

Introduction to py_wsi
----------------------

py-wsi provides a series of Python classes and functions which deal with
databases of whole slide images (WSI), or Aperio .svs files for machine
learning, using Python OpenSlide. py-wsi provides functions to perform
patch sampling from .svs files, generation of metadata, and several
store options: saving to a lightning memory-mapped database (LMDB), HDF5
files, or disk.

These Python functions deal with whole slide images (WSI), or Aperio
.svs files for deep learning, using OpenSlide. py-wsi provides functions
to perform patch sampling from .svs files, generation of metadata, and
several store options: saving to a lightning memory-mapped database
(LMDB), HDF5 files, or disk.

Lim et al. in “`An analysis of image storage systems for scalable
training of deep neural
networks <http://www.bafst.com/events/asplos16/bpoe7/wp-content/uploads/analysis-image-storage.pdf>`__”
perform a thorough evaluation of the best image storage systems, taking
into consideration memory usage and access speed. LMDB, a B+tree based
key-value storage, is not the most memory efficient, but provides
optimal read time.

py-wsi uses OpenSlide Python. According to the `Python OpenSlide
website <http://openslide.org/api/python/>`__, “OpenSlide is a C library
that provides a simple interface for reading whole-slide images, also
known as virtual slides, which are high-resolution images used in
digital pathology. These images can occupy tens of gigabytes when
uncompressed, and so cannot be easily read using standard tools or
libraries, which are designed for images that can be comfortably
uncompressed into RAM. Whole-slide images are typically
multi-resolution; OpenSlide allows reading a small amount of image data
at the resolution closest to a desired zoom level.”

*Note: HDF5 functionality will not be available until version 1.2*

**Check Jupyter Notebook on GitHub to view example usage:**\ `Example
usage of
py-wsi <https://github.com/ysbecca/py-wsi/blob/master/Using%20py-wsi.ipynb>`__

Setup
-----

This library is dependent on the following, but may be compatible with
previous versions.

python 3.6.1 numpy 1.12.1 openslide-python 1.1.1

1. Check dependencies listed in setup.py; notably, openslide-python
   which requires openslide, and lmdb. The python geometry package
   Shapely is used for inferring labels from XML annotations.

::

    brew install openslide

2. Install py_wsi using pip.

::

    pip install py_wsi

3. Check out Jupyter Notebook “Using py-wsi” to see what py-wsi can do
   and get started!

**Feel free to contact me with any issues and feedback.**
