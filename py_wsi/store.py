'''

These functions take patches and meta data as input and store them in the specified format.

Author: @ysbecca


'''
import time
from datetime import timedelta

import lmdb
import numpy as np
from .item import *

# OPTION 1) Store in a lightning memory-mapped database.

def save_in_lmdb(env, patches, coords, file_name, labels=[]):
	use_label = False
	if len(labels) > 0:
		use_label = True

	with env.begin(write=True) as txn:
		# txn is a Transaction object
		for i in range(len(patches)):
			if use_label:
				item = Item(patches[i], coords[i], labels[i])
			else:
				item = Item(patches[i], coords[i], 0)

			str_id = file_name + '-' + str(coords[i][0]) + '-' + str(coords[i][1])
			txn.put(str_id.encode('ascii'), pickle.dumps(item))

def save_meta_in_lmdb(meta_env, file, tile_dims):
	# Saves all tile dimension info along with file name, for loading patches.
	with meta_env.begin(write=True) as txn:
		txn.put(file.encode('ascii'), pickle.dumps(tile_dims))

def get_patch_from_lmdb(txn, x, y, file_name):
	str_id = file_name + '-' + str(x) + '-' + str(y)
	raw_item = txn.get(str_id.encode('ascii'))
	item = pickle.loads(raw_item)
	return item

def get_meta_from_lmdb(meta_env, file):
	# Call get_meta_from_lmdb(read_lmdb(location, name), file) for single read
	with meta_env.begin() as txn:
		raw_dims = txn.get(file.encode())
		dims = pickle.loads(raw_dims)
	return dims

def new_lmdb(location, name, map_size_bytes):
	return lmdb.open(location + name, map_size=map_size_bytes)

def print_lmdb_keys(env):
	with env.begin() as txn:
	    cursor = txn.cursor()
	    for key, value in cursor:
	        print(key)

def read_lmdb(location, name):
	''' Read-only allows for multiple consecutive reads. '''
	return lmdb.open(name, readonly=True)


# OPTION 2) Store in HDF5 files, multiple patches per file and accessible individually.

# def store_hdf5():

# OPTION 3) Save patches to disk as .png files + a single meta-data file.

# def store_disk(dir):






