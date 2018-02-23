'''

This is somewhat equivalent to the Caffe Datum class, encapsulating an individual image and all its
related information required to save in a binary string as a key, value pair in LMDBs.

Author: @ysbecca
'''

import pickle
import patch_reader as pr
import numpy as np
from PIL import Image

class Item(object):

	def __init__(self, patch, image_id, coords, label):

		self.channels = patch.shape[2]
		# Assuming only square images.
		self.size = patch.shape[0]
		self.data = patch.tobytes()
		self.label = label # [1, 0, 0, 0] for example
		self.image_id = image_id # 
		self.coords = coords

	def pickle(self):
		return pickle.dumps(self)

	def get_id(self):
		return np.argmax(self.label)

	def get_patch(self):
		return np.fromstring(self.data, dtype=np.uint8).reshape(self.size, self.size, self.channels)

	def get_patch_as_image(self):
		return Image.fromarray(self.get_patch(), 'RGB')


def unpickle(str_item):
	return pickle.loads(str_item)




