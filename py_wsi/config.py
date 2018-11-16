"""

Configuration parameters for package.

Author @ysbecca
"""



STORAGE_TYPES 			= ['lmdb', 'hdf5', 'disk']





"""
UPDATE NOTES
================

lmdb is default so as to be backwards compatible.
database name not required, but used as prefix in non-lmdb cases.

Requires PIL >= 5.0.0
h5py

"""