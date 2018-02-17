'''

These functions take patches and meta data as input and store them in the specified format.

Author: @ysbecca


'''
import time
from datetime import timedelta

import lmdb
import numpy as np
from item import *

# OPTION 1) Store in a lightning memory-mapped database.

def save_in_lmdb(env, patches, coords, ids, labels=[]):
	use_label = False
	if len(labels) > 0:
		use_label = True

	with env.begin(write=True) as txn:
		# txn is a Transaction object
		for i in range(len(patches)):
			if use_label:
				item = Item(patches[i], ids[i], coords[i], labels[i])
			else:
				item = Item(patches[i], ids[i], coords[i], 0)

			str_id = example_file + '-' + str(coords[i][0]) + '-' + str(coords[i][1])
			txn.put(str_id.encode('ascii'), pickle.dumps(item))


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






