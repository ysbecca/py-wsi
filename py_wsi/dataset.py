'''

Dataset class (adapted using class from by Hvass-Labs tutorials) customised for whole slide image patches, 
and using py-wsi to load patches from LMDB.

Optionally performs basic augmentation of patches (8 total: rotations of 90 degrees * k, for k={1, 2, 3}
and flips across the horizontal and vertical axes.)

Author: Hvass-Labs and @ysbecca

'''
import math
import numpy as np
import random

class DataSet(object):

  def __init__(self, images, labels, image_cls, coords):

    self._num_images = np.array(images).shape[0]
    self._images = images

    # Boolean array versions of ID
    self._labels = labels 
    # The source image labels
    self._image_cls = image_cls
    # Integer labels
    # self._ids = ids 
    self._coords = coords

    self._epochs_completed = 0
    self._index_in_epoch = 0

  @property
  def images(self):
    return self._images

  @property
  def image_cls(self):
    return self._image_cls

  @property
  def labels(self):
    return self._labels

  @property
  def num_images(self):
    return self._num_images

  # @property
  # def ids(self):
    # return self._ids

  @property
  def set_id(self):
  	return self._set_id

  @property
  def epochs_completed(self):
    return self._epochs_completed

  def set_images(self, images):
    self._images = images

  def set_image_cls(self, cls):
    self._image_cls = cls

  def set_labels(self, labels):
    self._labels = labels

  def set_coords(self, coords):
  	self._coords = coords

  # Shuffles all patches in the dataset object.
  def shuffle_all(self):
    if self.num_images <= 1:
        print("Cannot shuffle when", self.num_images, "images in set.")
        return

    list_all = list(zip(self._images, self._labels, self._image_cls, self._coords))
    random.shuffle(list_all)
    self._images, self._labels, self._image_cls, self._coords = zip(*list_all)

    # [self._images, self._labels, self._image_cls, self._ids, self._coords] = \
      # shuffle_multiple([self._images, self._labels, self._image_cls, self._ids, self._coords])

  def next_batch(self, batch_size, use_pseudo=False):
    """Return the next `batch_size` examples from this data set."""

    start = self._index_in_epoch
    self._index_in_epoch += batch_size

    if self._index_in_epoch > self._num_images:
      # Finished epoch
      self._epochs_completed += 1

      start = 0
      self._index_in_epoch = batch_size
      assert batch_size <= self._num_images
    end = self._index_in_epoch

    return self._images[start:end], self._labels[start:end]

# Helper function which shuffles the object.
def shuffle_multiple(list_of_lists):
  new_list = []
  if(len(list_of_lists) == 0):
    print("ERROR: no elements in list of lists for shuffling.")
    return 0
  perm = np.arange(len(list_of_lists[0]))
  np.random.shuffle(perm)
  for list_ in list_of_lists:
    new_list.append(np.copy(list_[perm]))

  return new_list


def fetch_dataset(turtle, set_id, total_sets, augment):

  if set_id > -1:
    patches, coords, classes, labels = turtle.get_set_patches(set_id, total_sets)

    if augment:
      orig = np.copy(patches)
      if select_augment < 0:
        for j in range(1, 9):
          patches = np.concatenate((au.augment_patches(orig, j), patches), axis=0)
        if labels != []:
          labels = np.tile(labels, (9, 1))
        coords = np.tile(coords, (9, 1))
        classes = np.tile(classes, 9)

    return DataSet(patches, labels, classes, coords)
  else:
    print("Not yet implemented test DB. Need to load all patches from every image from test turtle.")
    return None

def read_datasets(turtle,
					set_id=-1,
					valid_id=-1,
					total_sets=5,
					shuffle_all=True,
					augment=True,
					is_test=False):

    class DataSets(object):
        pass
    dataset = DataSets()
    if is_test:
        dataset.test = fetch_dataset(turtle, -1, -1, False)
    else:
        dataset.train = fetch_dataset(turtle, set_id, total_sets, augment)
        dataset.valid = fetch_dataset(turtle, valid_id, total_sets, augment)
        if shuffle_all:
            dataset.train.shuffle_all()
            dataset.valid.shuffle_all()
    
    return dataset


def augment_patches(patches, augment_id):
	''' We want to augment the patches based on the augment_id. 
	Three rotations:
		A (90 degrees to the left)
		B (180 degrees to the left)
		C (270 degrees to the left)
	'''
	aug_patches = []
	for im in patches:
		if(augment_id == 0): # normal
			return patches
		elif(augment_id == 1): # horizontal mirror
			aug_patches.append(np.fliplr(im))
		elif(augment_id == 2): # vertical mirror
			aug_patches.append(np.flipud(im))
		elif(augment_id == 3): # rotate A from 0
			aug_patches.append(np.rot90(im, 1))
		elif(augment_id == 4): # rotate B from 0
			aug_patches.append(np.rot90(im, 2))
		elif(augment_id == 5): # rotate C from 0
			aug_patches.append(np.rot90(im, 3))
		elif(augment_id == 6): # rotate A from 1
			aug_patches.append(np.rot90(np.fliplr(im), 1))
		elif(augment_id == 7): # rotate B from 1
			aug_patches.append(np.rot90(np.fliplr(im), 2))
		else: # rotate C from 1
			aug_patches.append(np.rot90(np.fliplr(im), 3))
	return np.array(aug_patches)

