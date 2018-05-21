# py-wsi

##IMPORTANT NOTICE:

I am currently working on an update to py_wsi which will add three major improvements which will be helpful in general, and particularly when dealing with much larger datasets:

- better memory management
- much better error checking and handling
- functionality to allow for sampling test patches before sampling from all images

I will also post a blog post on my blog (ysbecca.github.io) soon on understanding patch_size and tile level. The test patch sampling functionality should also be very helpful. **I would strongly suggest downloading the update when it is available, and I appreciate any feedback after that.**

---------

These Python functions deal with whole slide images (WSI), or Aperio .svs files for deep learning, using OpenSlide. py-wsi provides functions to perform patch sampling from .svs files, generation of metadata, and several store options: saving to a lightning memory-mapped database (LMDB), HDF5 files, or disk.

Lim et al. in "[An analysis of image storage systems for scalable training of deep neural networks](http://www.bafst.com/events/asplos16/bpoe7/wp-content/uploads/analysis-image-storage.pdf)" perform a thorough evaluation of the best image storage systems, taking into consideration memory usage and access speed. LMDB, a B+tree based key-value storage, is not the most memory efficient, but provides optimal read time.

py-wsi uses OpenSlide Python. According to the [Python OpenSlide website](http://openslide.org/api/python/), "OpenSlide is a C library that provides a simple interface for reading whole-slide images, also known as virtual slides, which are high-resolution images used in digital pathology. These images can occupy tens of gigabytes when uncompressed, and so cannot be easily read using standard tools or libraries, which are designed for images that can be comfortably uncompressed into RAM. Whole-slide images are typically multi-resolution; OpenSlide allows reading a small amount of image data at the resolution closest to a desired zoom level."

*Note: HDF5 functionality is currently on hold.*

**Check Jupyter Notebook on GitHub to view example usage.**
GitHub repository: [https://github.com/ysbecca/py-wsi/blob/master/Using%20py-wsi.ipynb]

## Setup

This library is dependent on the following, but may be compatible with previous versions.

python 3.6.1
numpy 1.12.1
openslide-python 1.1.1


1. Check dependencies listed in setup.py; notably, openslide-python which requires openslide, and lmdb.

```
brew install openslide
```

2. Install py_wsi using pip.

```
pip install py_wsi
```

3. Check out Jupyter Notebook "Using py-wsi" to see what py-wsi can do and get started!

**Feel free to contact me with any errors, additional functionality requests, and feedback.**

