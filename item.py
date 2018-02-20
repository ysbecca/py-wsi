'''

This is somewhat equivalent to the Caffe Datum class, encapsulating an individual image and all its
related information required to save in a binary string as a key, value pair in LMDBs.

Author: @ysbecca
'''

import pickle
import patch_reader as pr
import numpy as np


class Item(object):

	def __init__(self, patch, image_id, coords, label):

		self.channels = patch.shape[2]
		# Assuming only square images.
		self.size = patch.shape[0]
		self.data = patch.tobytes()
		self.label = label
		self.image_id = image_id
		self.coords = coords

	def pickle(self):
		return pickle.dumps(self)

	def get_patch(self):
		return np.fromstring(self.data, dtype=np.uint64).reshape(self.channels, self.size, self.size)

def unpickle(str_item):
	return pickle.loads(str_item)




