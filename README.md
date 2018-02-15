# py-wsi

This is a Python library for dealing with whole slide images (WSI), or Aperio .svs files for deep learning, using OpenSlide.

According to the (Python OpenSlide website)[http://openslide.org/api/python/], OpenSlide is a C library that provides a simple interface for reading whole-slide images, also known as virtual slides, which are high-resolution images used in digital pathology. These images can occupy tens of gigabytes when uncompressed, and so cannot be easily read using standard tools or libraries, which are designed for images that can be comfortably uncompressed into RAM. Whole-slide images are typically multi-resolution; OpenSlide allows reading a small amount of image data at the resolution closest to a desired zoom level.

## Setup

This library is dependent on the following, (also included in requirements.txt) but may be compatible

python 3.6.1
numpy 1.12.1
openslide-python 1.1.1


1. Install openslide

```
brew install openslide
```

2. Install Python dependencies
3. Check out Jupyter Notebook "Using py-wsi" to see what py-wsi can do and get started!

## Patch sampling and storing

Most deep learning approaches using WSI require patch sampling and large datasets. Thus, py-wsi provides several options for creating and accessing these patch datasets for best computational and memory efficiency.

### Lightning memory-mapped database (LMDB)

### HDF5 files with meta-data

### Saving patches to disk with meta-data

### Real-time patch sampling from WSI (not recommended)

