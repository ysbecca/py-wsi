'''

This is an example of using the various functions provided in py-wsi to sample patches from .svs files in 
a directory, saving both patches and meta to a LMDB database, and recording runtime time.

Author: @ysbecca


'''
import numpy as np
import time
from datetime import timedelta


# py-wsi files
from patch_reader import *
from store import *

example_file = "04.svs"
example_dir = "/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI/"

db_location = ""
db_name = "test_lmdb"

def start_timer():
	return time.time()

def end_timer(start_time):
	end_time = time.time()
	print("Time usage: " + str(timedelta(seconds=int(round(end_time - start_time)))))


def main():

	# Read the path directory for .svs files to sample from as the command line arg.
	# If provided, read in the database details.


	# Loop to sample patches and create meta, and save them in batches.

	start_time = start_timer()

	patches, coords, ids = sample_patches(example_file, example_dir, patch_size=256, percent_overlap=0.5, level=12)
	print(np.shape(patches))
	print(np.shape(coords))
	print(np.shape(ids))

	end_timer(start_time)

	# Array of all available .svs file names. 
	# Determine batch size.
	
	map_size_bytes = np.array(patches).nbytes * 10

	# Save to specified database using specified method.
	start_time = start_timer()


	print("Creating new LMDB environment...")
	env = new_lmdb(db_location, db_name, map_size_bytes)
	save_in_lmdb(env, patches, coords, ids) 

	print("Saved in LMDB: " + db_name)

	end_timer(start_time)
	print("====== LMDB Stats ======")
	print(env.stat())
	# print_lmdb_keys(env)


# Output total run-time and memory used for storage.



if __name__ == "__main__":
    main()





