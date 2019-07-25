'''

These functions take patches and meta data as input and store them in the specified format.

Author: @ysbecca


'''
import csv
import time
import h5py
from datetime import timedelta

from PIL import Image

import lmdb
import numpy as np
from .item import *


###########################################################################
#                Option 1: Save to LMDB                                   #
###########################################################################

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
    return lmdb.open(location + name, readonly=True)


###########################################################################
#                Option 2: store to HDF5 files                            #
###########################################################################

def save_to_hdf5(db_location, patches, coords, file_name, labels):
    """ Saves the numpy arrays to HDF5 files. All patches from a single WSI will be saved
        to the same HDF5 file, regardless of the transaction size specified by rows_per_txn,
        because this is the most efficient way to use HDF5 datasets.
        - db_location       folder to save images in
        - patches           numpy images
        - coords            x, y tile coordinates
        - file_name         original source WSI name
        - labels            patch labels (opt)
    """

    # Save patches into hdf5 file.
    file    = h5py.File(db_location + file_name + '.h5','w')
    dataset = file.create_dataset('t', np.shape(patches), h5py.h5t.STD_I32BE, data=patches)

    # Save all label meta into a csv file.
    with open(db_location + file_name + '.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in range(len(labels)):
            writer.writerow([coords[i][0], coords[i][1], labels[i]])


###########################################################################
#                Option 3: save patches to disk                           #
###########################################################################

def save_to_disk(db_location, patches, coords, file_name, labels):
    """ Saves numpy patches to .png files (full resolution). 
        Meta data is saved in the file name.
        - db_location       folder to save images in
        - patches           numpy images
        - coords            x, y tile coordinates
        - file_name         original source WSI name
        - labels            patch labels (opt)
    """
    save_labels = len(labels)
    for i, patch in enumerate(patches):
        # Construct the new PNG filename
        patch_fname = file_name + "_" + str(coords[i][0]) + "_" + str(coords[i][1]) + "_"

        if save_labels:
            patch_fname += str(labels[i])

        # Save the image.
        Image.fromarray(patch).save(db_location + patch_fname + ".png")
