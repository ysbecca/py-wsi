'''

This is an example of using the various functions provided in py-wsi to sample patches from .svs files in 
a directory, saving both patches and meta to a LMDB database, and recording runtime time.

Author: @ysbecca


'''
import numpy as np
import time
from datetime import timedelta
from os import listdir
from os.path import isfile, join
import math

# py-wsi files
from patch_reader import *
from store import *

# example_file = "04.svs"
example_dir = "/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI/"

db_location = ""
db_name = "test_lmdb"

def start_timer():
	return time.time()

def end_timer(start_time):
	end_time = time.time()
	print("Time usage: " + str(timedelta(seconds=int(round(end_time - start_time)))))


def main():

	# Read in command line args, if used.

	# Read the path directory for .svs files to sample from as the command line arg.
	files = np.array([file for file in listdir(example_dir) if isfile(join(example_dir, file)) and '.svs' in file])
	print(str(len(files)) + " found in directory. Starting timer.")


	start_time = start_timer()

	patch_size = 256
	patches_expected = 4000 # Approximate only
	map_size_bytes = (patch_size*patch_size*3) * patches_expected * 10


	# Save to specified database using specified method.
	print("Creating new LMDB environment...")
	env = new_lmdb(db_location, db_name, map_size_bytes)

	for file in files:
		print(file)
		patches, coords, ids = sample_patches(file, example_dir, patch_size=patch_size, percent_overlap=0, level=12)
		print(np.shape(patches))

		# Write this file info to db in a single transaction.
		save_in_lmdb(env, patches, coords, ids, file)
		print(env.stat())

	end_timer(start_time)

	print("Saved in LMDB: " + db_name)
	print("====== LMDB Stats ======")
	print(env.stat())



if __name__ == "__main__":
    main()





