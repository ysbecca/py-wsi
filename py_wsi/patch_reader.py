'''

These functions acess the .svs files via the openslide-python API and perform patch
sampling as is typically needed for deep learning.

Author: @ysbecca
'''

import numpy as np
from openslide import open_slide  
from openslide.deepzoom import DeepZoomGenerator
from glob import glob
from xml.dom import minidom
from shapely.geometry import Polygon, Point



def generate_label(regions, region_labels, point, label_map):
    # regions = array of vertices (all_coords)
    # point [x, y]
    for i in range(len(region_labels)):
        poly = Polygon(regions[i])
        if poly.contains(Point(point[0], point[1])):
            return label_map[region_labels[i]]
    return label_map['Normal']


def get_regions(path):
	''' Parses the xml at the given path, assuming annotation format importable by ImageScope. '''
	xml = minidom.parse(path)
	# The first region marked is always the tumour delineation
	regions_ = xml.getElementsByTagName("Region")
	regions, region_labels = [], []
	for region in regions_:
		vertices = region.getElementsByTagName("Vertex")
		attribute = region.getElementsByTagName("Attribute")
		if len(attribute) > 0:
			r_label = attribute[0].attributes['Value'].value
		else:
			r_label = region.getAttribute('Text')
		region_labels.append(r_label)

		# Store x, y coordinates into a 2D array in format [x1, y1], [x2, y2], ...
		coords = np.zeros((len(vertices), 2))
	    
		for i, vertex in enumerate(vertices):
			coords[i][0] = vertex.attributes['X'].value
			coords[i][1] = vertex.attributes['Y'].value
	        
		regions.append(coords)
	return regions, region_labels

def sample_patches(file_name,
				   file_dir,
				   percent_overlap,
				   patch_size=512,
				   level=0,
				   image_id=False,
				   xml_dir=False,
				   label_map={}
				   ):
	''' Sample patches of specified size from .svs file.
		- overlap: 0.5 is a 50% overlap; overlap = 0 means no overlap; overlap > 1.0 skips regions in 
			proportion to size of tile
		- level: 0 is highest resolution; level_count - 1 is lowest
		
		Returns arrays of patches, x,y coordinates, and parent image IDs (filename if not specified).

		Note: patch_size is the dimension of the sampled patches, NOT equivalent to openslide's definition
		of tile_size. This implementation was chosen to allow for more intuitive usage.
	'''
	
	overlap = int(patch_size*percent_overlap / 2.0)
	tile_size = patch_size - overlap*2

	slide = open_slide(file_dir + file_name) 
	tiles = DeepZoomGenerator(slide, tile_size=tile_size, overlap=overlap, limit_bounds=False)

	if xml_dir:
		# Expect filename of XML annotations to match SVS file name
		regions, region_labels = get_regions(xml_dir + file_name[:-4] + ".xml")

	if level >= tiles.level_count:
		print("Error: requested level does not exist. Slide level count: " + str(tiles.level_count))
		return
	x_tiles, y_tiles = tiles.level_tiles[level]

	patches, coords, labels = [], [], []
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

				# Calculate the patch label based on centre point.
				if xml_dir:
					converted_coords = tiles.get_tile_coordinates(level, (x, y))[0]
					labels.append(generate_label(regions, region_labels, converted_coords, label_map))
			x += 1
		y += 1
		x = 0

	return patches, np.array(coords), (x_tiles, y_tiles), np.array(labels)

