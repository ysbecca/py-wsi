"""

Main py-wsi manager, Turtle, which keeps track of a collection of SVS images, and allows for
patch sampling, storing, and accessing. 

Author: @ysbecca

"""
import itertools
import math
import sys

import numpy as np

from PIL import Image
from os import listdir
from os.path import isfile, join


# py-wsi scripts.
from .patch_reader import *
from .store import *
from .helpers import *
from .config import *

class Turtle(object):

    def __init__(self,
    			 file_dir,
    			 db_location,
    			 db_name="",
    			 storage_type='lmdb',
    			 xml_dir=False,
    			 label_map={},
    			 ):
        """ The py-wsi manager class for manipulating svs and patches. 
            - storage_type  expecting 'lmdb', 'hdf5', disk'
            - file_dir      location of all the image files
            - db_location   path where images will be stored
            - db_name       name of database (name for LMDB; prefix of files for HDF5 and disk)
            - xml_dir       path of XML annoation files, if used
            - label_map     dictionary of labels and their integer labels expected in annotation files
        """
        if storage_type not in STORAGE_TYPES:
            print("[py-wsi error]: storage type not recognised; expecting one of", STORAGE_TYPES)
            return

        self.storage_type = storage_type

        # Path to storage directories
        self.file_dir = file_dir
        self.db_location = db_location

        # Database names
        self.db_name = db_name
        self.db_meta_name = self.__get_db_meta_name(db_name)

        # Links to the image filenames
        self.files = self.__get_files_from_dir(file_dir)
        self.num_files = len(self.files)

        # Annotation details
        self.xml_dir = xml_dir
        self.label_map = label_map

        print("======================================================")
        print("Storage type:              ", self.storage_type)
        print("Images directory:          ", self.file_dir)
        print("Data store directory:      ", self.db_location)
        print("Images found:              ", self.num_files)
        print("======================================================")

    def retrieve_tile_dimensions(self, file_name, patch_size=0, overlap=0, tile_size=0):
        """ For a given whole slide image in the dataset, retrieve the available tile dimensions.
            This will help users decide what level to sample at across the dataset. Users may choose
            either patch size or tile size.
            - file_name         the whole slide image filename
            - patch_size        patch size in pixels
            - tile_size         tile size in pixels

            Returns:
            - level count
            - level tiles
            - level dimensions
        """
        patch_dim = patch_size
        tile_dim = tile_size

        # Check that either tile or patch size is set correctly.
        if not (patch_size == 0 and tile_size == 0):
            if patch_size == 0:
                patch_dim = tile_size + 2*overlap
            if tile_size == 0:
                tile_dim = patch_size - 2*overlap
            print("Setting patch size", patch_dim, "and tile size", tile_dim)
        else:
            print("[py-wsi error]: set either tile size or patch size.")
            return 0, [], []

        # Make sure WSI exists.
        if not self.__check_file_found(file_name):
            return 0, [], []

        # Open image and return variables.
        slide = open_slide(self.file_dir + file_name)
        tiles = DeepZoomGenerator(slide, tile_size=tile_dim, overlap=overlap)

        return tiles.level_count, tiles.level_tiles, tiles.level_dimensions

    def retrieve_sample_patch(self, file_name, patch_size, level, overlap=0):
        """ Fetches a sample patch from the centre of a whole slide image for testing.
            - file_name         the whole slide image to sample from
            - patch_size        the size of patch to retrieve
            - level             the integer level (scale) at which to sample
            - overlap           overlap amount in pixels
        """
        # Calculate the tile dimension size.
        tile_dim = patch_size - 2*overlap

        if not self.__check_file_found(file_name):
            return None

        # Open the file and deep zoom generator.
        slide = open_slide(self.file_dir + file_name)
        tiles = DeepZoomGenerator(slide, tile_size=tile_dim, overlap=overlap)

        # Check that tile level requested is valid.
        if level > tiles.level_count - 1:
            print("[py-wsi error]: requested level does not exist. Number of slide levels:", tiles.level_count)
            return None
    
        # Sample from centre of image to maximise likelihood of returning tissue.
        x, y = tiles.level_tiles[level]
        new_tile = tiles.get_tile(level, (int(x / 2), int(y / 2)))
        return new_tile

    def get_set_patches(self, set_id, total_sets, select=[]):
        """ Retrieves all the patches from the database given a set id, and the total
            number of sets. The ith set includes all patches from the ith image.
            - set_id            the set id
            - total_sets        the total number of sets to divide the dataset into
            - select            a custom selection array, optional, to specify which images to 
                                retrieve patches from
        """
        if select == []:
            select = np.zeros(self.num_files)
            select[set_id:self.num_files:total_sets] = 1
        else:
            # Check for invalid inputs.
            if len(select) != self.num_files:
                print("[py-wsi error]: select array provided but does not match the number of files,", self.num_files)
                return []

        # Fetch all the patches from each selected image in dataset.
        all_patches, all_coords, all_cls, all_labels = [], [], [], []
        for i in range(self.num_files):
            if select[i]:
                patches, coords, classes, labels = self.get_patches_from_file(self.files[i])
                all_patches.append(patches)
                all_coords.append(coords)
                all_cls.append(classes)
                all_labels.append(labels)

        # Flatten the data into lists.
        all_patches = list(itertools.chain.from_iterable(x for x in all_patches))
        all_coords = list(itertools.chain.from_iterable(x for x in all_coords))
        all_cls = list(itertools.chain.from_iterable(x for x in all_cls))
        all_labels = list(itertools.chain.from_iterable(x for x in all_labels))

        return all_patches, all_coords, all_cls, all_labels

    def get_patches_from_file(self, file_name, verbose=False):
        """ Fetches the patches from one file, depending on storage method. 
        """
        if not self.__check_file_found(file_name):
            return None

        if self.storage_type == 'disk':
            return self.__get_patches_from_disk(file_name[:-4], verbose=verbose)
        elif self.storage_type == 'hdf5':
            return self.__get_patches_from_hdf5(file_name[:-4], verbose=verbose)
        else:
            # LMDB by default.
            items = self.__get_items_from_file(file_name[:-4])
            return self.__items_to_patches_and_meta(items)

    def sample_and_store_patches(self,
                                 patch_size,
                                 level,
                                 overlap,
                                 load_xml=False,
                                 limit_bounds=True,
                                 rows_per_txn=20):
        """ Samples patches from all whole slide images in the dataset and stores them in the
            specified format.
            - patch_size        the patch size in pixels to sample
            - level             the tile level to sample at
            - overlap           pixel overlap of patches
            - limit_bounds      activates OpenSlide's automatic boundary limits (cuts out some background)
            - rows_per_txn      how many rows in the WSI to sample (save in memory) before saving to disk
                                a smaller number will use less RAM; a bigger number is slightly more
                                efficient but will use more RAM.
        """
        start_time = start_timer()

        # Check for valid parameters.
        if load_xml:
            num_xml_files = len(self.get_xml_files())
            if self.num_files != num_xml_files:
                print("[py-wsi error]: requested to read XML annotations but number of XML files", num_xml_files,
                    "does not match number of .svs files", self.num_files)
                return
        if overlap < 0:
            print("[py-wsi error]: negative overlap not allowed.")
            return

        xml_dir = False
        if load_xml:
            xml_dir = self.xml_dir

        if self.storage_type == 'hdf5':
            self.__sample_store_hdf5(patch_size, level, overlap, xml_dir, limit_bounds, rows_per_txn)
        elif self.storage_type == 'disk':
            self.__sample_store_disk(patch_size, level, overlap, xml_dir, limit_bounds, rows_per_txn)
        else:
            # LMDB by default.
            self.__sample_store_lmdb(patch_size, level, overlap, xml_dir, limit_bounds, rows_per_txn)

        end_timer(start_time)

    ###########################################################################
    #           General class variable access functions                       #
    ###########################################################################

    def set_label_map(self, label_map):
        self.label_map = label_map

    def set_file_dir(self, file_dir):
        self.file_dir = file_dir
        # Update the files list and the total number of files.
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

    ###########################################################################
    #                General class helper functions                           #
    ###########################################################################

    def __get_files_from_dir(self, file_dir, file_type='.svs'):
        """ Returns the names of all the SVS image files in the provided directory. 
        """
        return np.array([file for file in listdir(file_dir) 
            if isfile(join(file_dir, file)) and file_type in file])

    def __get_db_meta_name(self, db_name):
        return db_name + "_meta"

    def __check_file_found(self, file_name):
        """ Checks if a file is found in the file list.
        """
        if file_name not in self.files:
            print("[py-wsi error]: file not found in directory", self.file_dir)
            return False
        if file_name[-4:] != ".svs":
            print("[py-wsi error]: filename should end in .svs extension.")
            return False
        return True

    ###########################################################################
    #                HDF5-specific helper functions                           #
    ###########################################################################

    def __get_patches_from_hdf5(self, file_name, verbose=False):
        """ Loads the numpy patches from HDF5 files.
        """
        patches, coords, classes, labels = [], [], [], []
        
        # Now load the images from H5 file.
        file = h5py.File(self.db_location + file_name + ".h5",'r+')
        dataset = file['/' + 't']
        new_patches = np.array(dataset).astype('uint8')
        for patch in new_patches:
            patches.append(patch)
        file.close()

        # Load the corresponding meta.
        with open(self.db_location + file_name + ".csv", newline='') as metafile:
            reader = csv.reader(metafile, delimiter=' ', quotechar='|')
            for row in reader:
                coords.append([int(row[0]), int(row[1])])
                cl_ = int(row[2])
                classes.append(cl_)
                # If there is a class, assign a label.
                if cl_ != -1:
                    l = np.zeros((len(self.label_map)))
                    l[cl_] = 1
                    labels.append(l)

        if verbose:
            print("[py-wsi] loaded from", file_name, ".h5 file", np.shape(patches))

        return patches, coords, classes, labels


    def __sample_store_hdf5(self, patch_size, level, overlap, xml_dir, limit_bounds, rows_per_txn):
        """ Same parameters as sample_and_store_patches().
        """
        total_count = 0
        for file in self.files:
            print(file, end=" ")
            patch_count = sample_and_store_patches(
                                file,
                                self.file_dir,
                                overlap,
                                patch_size=patch_size,
                                level=level,
                                xml_dir=xml_dir,
                                label_map=self.label_map,
                                limit_bounds=limit_bounds,
                                rows_per_txn=rows_per_txn,
                                db_location=self.db_location,
                                prefix=self.db_name,
                                storage_option='hdf5')

            # Don't stop if one image fails.
            if patch_count <= 0:
                print("[py-wsi error]: no patches sampled from ", file, ". Continuing.")
            total_count += patch_count


    ###########################################################################
    #                Disk-specific helper functions                           #
    ###########################################################################

    def __get_patches_from_disk(self, wsi_name, verbose=False):
        """ Loads all the PNG patch images from disk. Note that this function does NOT 
            distinguish between other PNG images that may be in the directory; everything
            will be loaded.
        """
        # Get all files matching the WSI file name and correct file type.
        patch_files = np.array(
            [file for file in listdir(self.db_location) 
            if isfile(join(self.db_location, file)) and '.png' in file and wsi_name in file])

        patches, coords, classes, labels = [], [], [], []
        for f in patch_files:
            patches.append(np.array(Image.open(self.db_location + f), dtype=np.uint8))

            f_ = f.split('_')
            coords.append([int(f_[1]), int(f_[2])])

            # Check for a label.
            if len(f_[3]) > 4:
                class_ = int(f_[3].split(".")[0])
                classes.append(class_)
                l = np.zeros((len(self.label_map)))
                l[class_] = 1
                labels.append(l)
            else:
                # To be consistant with LMDB implementation.
                classes.append(-1)
        if verbose:
            print("[py-wsi] loaded", len(patches), "patches from", wsi_name)

        return patches, coords, classes, labels


    def __sample_store_disk(self, patch_size, level, overlap, xml_dir, limit_bounds, rows_per_txn):
        """ Same parameters as sample_and_store_patches().
        """
        total_count = 0
        for file in self.files:
            print(file, end=" ")
            patch_count = sample_and_store_patches(
                                file,
                                self.file_dir,
                                overlap,
                                patch_size=patch_size,
                                level=level,
                                xml_dir=xml_dir,
                                label_map=self.label_map,
                                limit_bounds=limit_bounds,
                                rows_per_txn=rows_per_txn,
                                db_location=self.db_location,
                                prefix=self.db_name,
                                storage_option='disk')

            # Don't stop if one image fails.
            if patch_count <= 0:
                print("[py-wsi error]: no patches sampled from ", file, ". Continuing.")
            total_count += patch_count

        print("")
        print("============ Patches Dataset Stats ===========")
        print("Total patches sampled:                    ", total_count)
        print("Patches saved to:                         ", self.db_location)
        print("Patches saved with prefix:                ", self.db_name)
        print("")


    ###########################################################################
    #                LMDB-specific helper functions                           #
    ###########################################################################

    def __get_items_from_file(self, file_name):
        # Get the tile dimensions of the image first from meta database.
        meta_env = read_lmdb(self.db_location, self.db_meta_name)
        x, y = get_meta_from_lmdb(meta_env, file_name)

        # Loop through all the tiles and fetch all the items.
        items = []
        env = read_lmdb(self.db_location, self.db_name)
        with env.begin() as txn:
            for y_ in range(y - 1):
                for x_ in range(x - 1):
                    items.append(get_patch_from_lmdb(txn, x_, y_, file_name))
        return items

    def __items_to_patches_and_meta(self, items):
        """ Converts items back into patches and meta.
        """
        patches = [i.get_patch() for i in items]
        coords = [i.coords for i in items]
        classes = [i.label for i in items]

        # Check if there are labels to be fetched.
        if self.label_map != {}:
            labels = [i.get_label_array(len(self.label_map)) for i in items]
        else:
            print("[py-wsi]: no labels found for these patches.")
            labels = []
        return patches, coords, classes, labels

    def __calculate_map_size(self, patch_size, level, overlap, limit_bounds):
        """ Pre-calculates the LMDB map size for a database given the files.
        """
        total_bytes = 0
        total_meta_bytes = 0

        for file in self.files:
            slide = open_slide(self.file_dir + file)
            tile_size = patch_to_tile_size(patch_size, overlap)
            tiles = DeepZoomGenerator(slide, tile_size=tile_size, overlap=overlap, limit_bounds=limit_bounds)

            # Count total number of tiles.
            x_tiles, y_tiles = tiles.level_tiles[level]
            file_tiles = x_tiles * y_tiles

            # Calculate total patch bytes, assuming colour (3 channels), bytes per int plus buffer.
            # If image is saved in float or double, this may be too conservative.
            total_bytes += (file_tiles * patch_size * patch_size * 3 * (sys.getsizeof(int()) + 4))
            total_meta_bytes += file_tiles * 256

        return total_bytes, total_meta_bytes

    def __sample_store_lmdb(self, patch_size, level, overlap, xml_dir, limit_bounds, rows_per_txn):
        """ Samples patches and saves them in LMDB. Parameters from sample_and_store_patches():
            - patch_size, level, overlap, limit_bounds, rows_per_txn.
        """

        # First iteration to calculate exactly the size of the DB.
        # To deal with very large databases, it is suggested to save k databases, one for each 
        # k-fold cross validation set.
        map_size, meta_map_size = self.__calculate_map_size(patch_size, level, overlap, limit_bounds)
        print("Pre-calculated map sizes:")
        print(" - patch db:    ", map_size, "bytes")
        print(" - meta db:     ", meta_map_size, "bytes")

        # Save to specified database using specified method.
        print("Creating new LMDB environment...")
        env = new_lmdb(self.db_location, self.db_name, map_size)
        meta_env = new_lmdb(self.db_location, self.db_meta_name, meta_map_size)

        for file in self.files:
            print(file, end=" ")
            # Open, sample, and store in multiple transactions per file.
            patch_count = sample_and_store_patches(
                                file,
                                self.file_dir,
                                overlap,
                                env=env,
                                meta_env=meta_env,
                                patch_size=patch_size,
                                level=level,
                                xml_dir=xml_dir,
                                label_map=self.label_map,
                                limit_bounds=limit_bounds,
                                rows_per_txn=rows_per_txn)

            # Don't stop if one image fails.
            if patch_count <= 0:
                print("[py-wsi error]: no patches sampled from ", file, ". Continuing.")

        print("")
        print("====== LMDB " + self.db_name + " Stats ======")
        print(env.stat())
        print("====== LMDB " + self.db_meta_name + " Stats ======")
        print(meta_env.stat())
