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
import sys

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
	def get_set_patches(self, set_id, total_sets, select=[]):
		if select == []:
			select = np.zeros(self.num_files)
			select[set_id:self.num_files:total_sets] = 1
		else:
			if len(select) != self.num_files:
				print("[py-wsi error]: select array provided but does not match the number of files,", self.num_files)
				return []

		all_patches, all_coords, all_cls, all_labels = [], [], [], []
		for i in range(self.num_files):
			if select[i]:
				patches, coords, classes, labels = self.get_patches_from_file(self.files[i])
				all_patches.append(patches)
				all_coords.append(coords)
				all_cls.append(classes)
				all_labels.append(labels)

		all_patches = list(itertools.chain.from_iterable(x for x in all_patches))
		all_coords = list(itertools.chain.from_iterable(x for x in all_coords))
		all_cls = list(itertools.chain.from_iterable(x for x in all_cls))
		all_labels = list(itertools.chain.from_iterable(x for x in all_labels))
		return all_patches, all_coords, all_cls, all_labels


	def __items_to_patches_and_meta(self, items):
		# Conversion from Item back into patches and meta.

		patches = [i.get_patch() for i in items]
		coords = [i.coords for i in items]
		classes = [i.label for i in items]

		if self.label_map != {}:
			labels = [i.get_label_array(len(self.label_map)) for i in items]
		else:
			print("[py-wsi]: no labels found for these patches.")
			labels = []
		return patches, coords, classes, labels

	def get_patches_from_file(self, file_name):
		if not self.__check_file_found(file_name):
			return None
		items = self.get_items_from_file(file_name[:-4])
		return self.__items_to_patches_and_meta(items)

	def get_items_from_file(self, file_name):
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

	def __get_files_from_dir(self, file_dir, file_type='.svs'):
		return np.array([file for file in listdir(file_dir) if isfile(join(file_dir, file)) and file_type in file])

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
		return self.__get_files_from_dir(self.xml_dir, '.xml')

	def set_db_location(self, db_location):
		self.db_location = db_location

	def set_db_name(self, db_name):
		self.db_name = db_name
		self.db_meta_name = self.__get_db_meta_name(db_name)

	def sample_and_store_patches(self, patch_size, level, overlap, load_xml=False, limit_bounds=True, rows_per_txn=20):
		start_time = start_timer()

		if load_xml:
			num_xml_files = len(self.get_xml_files())
			if self.num_files != num_xml_files:
				print("[py-wsi error]: requested to read XML annotations but number of XML files", num_xml_files,
					"does not match number of .svs files", self.num_files)
				return
		if overlap < 0:
			print("[py-wsi error]: negative overlap not allowed.")
			return

		# First iteration to calculate exactly the size of the DB.
		# To deal with larger databases, we suggest saving k databases, one for each k-fold cross
		# validation set. 
		map_size, meta_map_size = self.calculate_map_size(patch_size, level, overlap, limit_bounds)
		print("Pre-calculated map sizes:")
		print(" - patch db:    ", map_size, "bytes")
		print(" - meta db:     ", meta_map_size, "bytes")

		# Save to specified database using specified method.
		print("Creating new LMDB environment...")
		env = new_lmdb(self.db_location, self.db_name, map_size)
		meta_env = new_lmdb(self.db_location, self.db_meta_name, meta_map_size)

		xml_dir = False
		if load_xml:
			xml_dir = self.xml_dir

		for file in self.files:
			print(file, end=" ")
			patch_count = sample_and_store_patches_by_row(
								file, 
								self.file_dir, 
								overlap, 
								env,
								meta_env,
								patch_size=patch_size, 
								level=level,
								xml_dir=xml_dir,
								label_map=self.label_map,
								limit_bounds=limit_bounds,
								rows_per_txn=rows_per_txn)
			if patch_count <= 0:
				print("[py-wsi error]: no patches sampled from ", file, "exiting now.")
				return

		print("")
		print("====== LMDB " + self.db_name + " Stats ======")
		print(env.stat())
		print("====== LMDB " + self.db_meta_name + " Stats ======")
		print(meta_env.stat())
		end_timer(start_time)

	def calculate_map_size(self, patch_size, level, overlap, limit_bounds):
		total_bytes = 0
		total_meta_bytes = 0

		for file in self.files:
			slide = open_slide(self.file_dir + file)
			tile_size = patch_to_tile_size(patch_size, overlap)
			tiles = DeepZoomGenerator(slide, tile_size=tile_size, overlap=overlap, limit_bounds=limit_bounds)

			# Count total number of tiles
			x_tiles, y_tiles = tiles.level_tiles[level]
			file_tiles = x_tiles * y_tiles

			# Calculate total patch bytes, assuming colour (3 channels), bytes per int plus buffer
			total_bytes += (file_tiles * patch_size * patch_size * 3 * (sys.getsizeof(int()) + 4))
			total_meta_bytes += file_tiles * 256

		return total_bytes, total_meta_bytes

	# The following are functions which allow for sampling patches and learning about images / tile_dims
	# before running the sample_and_store_patches function on whole dataset.
	def retrieve_tile_dimensions(self, file_name, patch_size=0, overlap=0, tile_size=0):
		# Allow for users to request by patch or tile size.
		patch_dim = patch_size 
		tile_dim = tile_size
		if patch_size == 0: 
			patch_dim = tile_size + 2*overlap
		if tile_size == 0:
			tile_dim = patch_size - 2*overlap
		print("Setting patch size", patch_dim, "and tile size", tile_dim)

		if not self.__check_file_found(file_name):
			return (0, 0)

		slide = open_slide(self.file_dir + file_name) 
		tiles = DeepZoomGenerator(slide, tile_size=tile_dim, overlap=overlap)

		return tiles.level_count, tiles.level_tiles, tiles.level_dimensions

	def retrieve_sample_patch(self, file_name, patch_size, level, overlap=0):
		tile_dim = patch_size - 2*overlap

		if not self.__check_file_found(file_name):
			return None

		slide = open_slide(self.file_dir + file_name)
		tiles = DeepZoomGenerator(slide, tile_size=tile_dim, overlap=overlap)

		if level > tiles.level_count - 1:
			print("[py-wsi error]: requested level does not exist. Number of slide levels:", tiles.level_count)
			return None
		else:
			# Sample from centre of image to maximise likelihood of returning tissue
			x, y = tiles.level_tiles[level]
			new_tile = tiles.get_tile(level, (int(x / 2), int(y / 2)))
			return new_tile

	def __check_file_found(self, file_name):
		if file_name not in self.files:
			print("[py-wsi error]: file not found in directory", self.file_dir)
			return False
		if file_name[-4:] != ".svs":
			print("[py-wsi error]: filename should end in .svs extension.")
			return False
		return True







