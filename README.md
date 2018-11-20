py-wsi Introduction
===============================

It is strongly recommended to use py-wsi version >= 1.0 and to fork and download this repository. This repo contains all the most recent features and fixes. The current version has not been packaged in PyPI yet.

Please feel free to submit any issues to the GitHub repository and I will provide help as I am able to. While suggestions for extra/additional functionality will not be immediately considered, **pull requests are welcome.**

1.0 Current version (py-wsi 2.0): HDF5 and saving patches to disk
---------------------------------------------------------

This update to py_wsi has added two new functionalities:

- saving patches to disk (.png format)
- saving patches in HDF5 (.h5 format), [hierarchical data format](https://en.wikipedia.org/wiki/Hierarchical_Data_Format)

For those using older versions of py_wsi with LMDB storage: this updated version is backwards compatible and your old code will not be affected. Not changing the function signatures turned out tricky -- I should have thought out the code structure more carefully for the initial LMDB version, so apologies for those who dive into the code. There are plenty of comments for those who want to tweak things.

**Check Jupyter Notebook on GitHub to view example usage:** [Example usage of py-wsi](https://github.com/ysbecca/py-wsi/blob/master/Using%20py-wsi.ipynb)


2.0 Overview
---------------------------------------------------------

See this blog post [py_wsi for computer analysis on whole slide .svs images using OpenSlide](https://ysbecca.github.io/programming/2018/05/22/py-wsi.html) for help on understanding the relationship between patch and tile sampling. The test patch sampling functionality in this version will also help users to know exactly what they are sampling. 

### 2.1 Introduction to py_wsi 

py-wsi provides a series of Python classes and functions which deal with databases of whole slide images (WSI), or Aperio .svs files for machine learning, using Python OpenSlide. py-wsi provides functions to perform patch sampling from .svs files, generation of metadata, and several store options for the sampled patches:

- lightning memory-mapped database (LMDB)
- hierarchical data formatted (HDF5) files
- to disk as PNG files

Lim et al. in "[An analysis of image storage systems for scalable training of deep neural networks](http://www.bafst.com/events/asplos16/bpoe7/wp-content/uploads/analysis-image-storage.pdf)" perform a thorough evaluation of the best image storage systems, taking into consideration memory usage and access speed. LMDB, a B+tree based key-value storage, is not the most memory efficient, but provides optimal read time. In my personal research I find that HDF5 performs just as well, and is better for certain use cases. Storing to and loading from disk is significantly slower than both LMDB and HDF5 but the option is included for those who may have need of it.

You can read about the various supported formats and their Python libraries here:

- [LMDB Python binding docs](https://lmdb.readthedocs.io/en/release/)
- [HDF5 for Python (h5py)[https://www.h5py.org/]

py-wsi uses OpenSlide Python. According to the [Python OpenSlide website](http://openslide.org/api/python/), "OpenSlide is a C library that provides a simple interface for reading whole-slide images, also known as virtual slides, which are high-resolution images used in digital pathology. These images can occupy tens of gigabytes when uncompressed, and so cannot be easily read using standard tools or libraries, which are designed for images that can be comfortably uncompressed into RAM. Whole-slide images are typically multi-resolution; OpenSlide allows reading a small amount of image data at the resolution closest to a desired zoom level."

### 2.2 Requirements

This library was built using the following, but may be compatible with previous versions:

python==3.6.1  
numpy==1.15.2  
lmdb==0.93  
openslide-python==1.1.1  
Shapely==1.6.4  
h5py==2.7.0  

1. Check dependencies listed in above and in setup.py; notably, openslide, openslide-python, lmdb, and h5py. The python geometry package Shapely is used for inferring labels from XML annotations.

```
brew install openslide
```

2. **Fork and download this repository, then import into your working directory** (highly recommended, since you will most likely want to customise and add extra features!) OR install py_wsi using pip (not recommended; the version will always be behind).


```
pip install py_wsi
```

3. Check out Jupyter Notebook "Using py-wsi" to see what py-wsi can do and get started!

**Feel free to contact me with any issues and feedback.**

