'''

Main py-wsi manager, Turtle, which keeps track of a collection of SVS images, and allows for
patch sampling, storing, and accessing. 

Author: @ysbecca


'''
import numpy as np
import time
from datetime import timedelta
from os import listdir
from os.path import isfile, join
import math
import itertools

# py-wsi helper scripts.
from .patch_reader import *
from .store import *


# Helper timing functions.
def start_timer():
	return time.time()

def end_timer(start_time):
	end_time = time.time()
	print("Time usage: " + str(timedelta(seconds=int(round(end_time - start_time)))))


# The py-wsi main class for manipulating svs and patches. Turtles are the best.
class Turtle(object):

	def __init__(self, file_dir, db_location, db_name, xml_dir=False, label_map={}, ):
		self.file_dir = file_dir
		self.db_location = db_location
		self.db_name = db_name
		self.db_meta_name = self.__get_db_meta_name(db_name)
		self.files = self.__get_files_from_dir(file_dir)
		self.num_files = len(self.files)
		self.xml_dir = xml_dir
		self.label_map = label_map

		print(str(self.num_files) + " WSI found in directory.")

	# Retrieves all the patches from the database given a set id, and the total
	# number of sets. The ith set includes all patches from the ith image.
	def get_set_patches(self, set_id, total_sets):
		select = np.zeros(self.num_files)
		select[set_id:self.num_files:total_sets] = 1

		all_items = []
		for i in range(self.num_files):
			if select[i]:
				items = self.get_patches_from_file(self.files[i])
				all_items.append(items)

		all_items = list(itertools.chain.from_iterable(x for x in all_items))
		return all_items

	def get_patches_from_file(self, file_name):
		# Get the dims first from meta database
		meta_env = read_lmdb(self.db_location, self.db_meta_name)
		x, y = get_meta_from_lmdb(meta_env, file_name)

		# Loop through and fetch all the items
		items = []
		env = read_lmdb(self.db_location, self.db_name)
		with env.begin() as txn:
		    for y_ in range(y - 1):
		        for x_ in range(x - 1):
		            items.append(get_patch_from_lmdb(txn, x_, y_, file_name))
		return items

	def __get_files_from_dir(self, file_dir):
		return np.array([file for file in listdir(file_dir) if isfile(join(file_dir, file)) and '.svs' in file])

	def __get_db_meta_name(self, db_name):
		return db_name + "_meta"

	def set_label_map(self, label_map):
		self.label_map = label_map

	def set_file_dir(self, file_dir):
		self.file_dir = file_dir
		self.files = self.__get_files_from_dir(file_dir)
		self.num_files = len(self.files)

	def set_xml_dir(self, xml_dir):
		self.xml_dir = xml_dir

	def get_xml_files(self):
		return self.__get_files_from_dir(self.xml_dir)

	def set_db_location(self, db_location):
		self.db_location = db_location

	def set_db_name(self, db_name):
		self.db_name = db_name
		self.db_meta_name = self.__get_db_meta_name(db_name)

	def sample_and_store_patches(self, patch_size, level, overlap, load_xml=False, est_patches_per_svs=300):
		start_time = start_timer()

		# A rough, generous estimate of how many patches expected per image; can be adjusted if needed.
		# If the DB runs out of memory, increase est_patches_per_svs.
		patches_expected = self.num_files * est_patches_per_svs
		map_size_bytes = (patch_size*patch_size*3) * patches_expected * 10

		# Save to specified database using specified method.
		print("Creating new LMDB environment...")
		env = new_lmdb(self.db_location, self.db_name, map_size_bytes)
		meta_env = new_lmdb(self.db_location, self.db_meta_name, patches_expected*50)

		xml_dir = False
		if load_xml:
			xml_dir = self.xml_dir

		for file in self.files:
			print(file, end=" ")
			patches, coords, tile_dims, labels = sample_patches(
										file, 
										self.file_dir, 
										overlap, 
										patch_size=patch_size, 
										level=level,
										xml_dir=xml_dir,
										label_map=self.label_map)

			patches = np.array(patches).astype(np.uint8)

			# Write this file info to db in a single transaction.
			save_in_lmdb(env, patches, coords, file, labels)
			save_meta_in_lmdb(meta_env, file, tile_dims)

		print("")
		print("====== LMDB " + self.db_name + " Stats ======")
		print(env.stat())
		print("====== LMDB " + self.db_meta_name + " Stats ======")
		print(meta_env.stat())
		end_timer(start_time)








