'''

These functions acess the .svs files via the openslide-python API and perform patch
sampling as is typically needed for deep learning.

Author: @ysbecca
'''

import numpy as np
import openslide
from openslide import open_slide  
from openslide.deepzoom import DeepZoomGenerator
from glob import glob

# example_file = "04.svs"
# example_dir = "/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI/"


def sample_patches(file_name,
				   file_dir,
				   patch_size=512,
				   percent_overlap=0.5,
				   level=0,
				   image_id=False,
				   ):
	''' Sample patches of specified size from .svs file.
		- overlap: 0.5 is a 50% overlap; overlap = 0 means no overlap; overlap > 1.0 skips regions in 
			proportion to size of tile
		- level: 0 is highest resolution; level_count - 1 is lowest
		
		Returns arrays of patches, x,y coordinates, and parent image IDs (filename if not specified).

		Note: patch_size is the dimension of the sampled patches, NOT equivalent to openslide's definition
		of tile_size. This implementation was chosen to allow for more intuitive usage.
	'''
	if not image_id:
		im_id = file_name 

	overlap = int(patch_size*percent_overlap / 2.0)
	tile_size = patch_size - overlap*2
	# print("Overlap pixels: " + str(overlap))
	# print("Tile size: " + str(tile_size))

	slide = open_slide(file_dir + file_name) 
	tiles = DeepZoomGenerator(slide, tile_size=tile_size, overlap=overlap, limit_bounds=False)

	if level >= tiles.level_count:
		print("Error: requested level does not exist. Slide level count: " + str(tiles.level_count))
		return
	x_tiles, y_tiles = tiles.level_tiles[level]
	# print("x_tiles: " + str(x_tiles))
	# print("y_tiles: " + str(y_tiles))

	patches, coords = [], []
	x, y = 0, 0
	count = 0
	while y < y_tiles:
		while x < x_tiles:
			new_tile = np.array(tiles.get_tile(level, (x, y)), dtype=np.int)
			# OpenSlide calculates overlap in such a way that sometimes depending on the dimensions, edge 
			# patches are smaller than the others. We will ignore such patches.
			if np.shape(new_tile) == (patch_size, patch_size, 3):
				patches.append(new_tile)
				coords.append(np.array([x, y]))
				count += 1
			x += 1
		y += 1
		x = 0

	image_ids = [im_id]*count
	return patches, np.array(coords), np.array(image_ids)

# def main():
	
	# patches, coords, ids = sample_patches(example_file, example_dir, patch_size=256, percent_overlap=0.5, level=12)
	# print(np.shape(patches))
	# print(np.shape(coords))
	# print(np.shape(ids))

# if __name__ == "__main__":
    # main()










