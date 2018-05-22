
'''

An image-displaying function from imagepy.toolkit on GitHub:

https://github.com/ysbecca/imagepy-toolkit

Author: @ysbecca


'''

import matplotlib.pyplot as plt


def show_images(images, per_row, per_column):
    ''' Displays up to per_row*per_column images with per_row images per row, per_column images per column.
	'''
    fig = plt.figure(figsize=(25, 25))
    data = images[:(per_row*per_column)]

    for i, image in enumerate(data):
        plt.subplot(per_column, per_row, i+1)
        plt.imshow(image)
        plt.axis("off")
    
    plt.show()


def show_labeled_patches(images, clss):
    fig = plt.figure(figsize=(20, 10))
    data = images[:50]
    labels = clss[:50]

    for i, image in enumerate(data):
        plt.subplot(5, 10, i+1)
        plt.imshow(image)
        plt.title(str(labels[i]))
        plt.axis("off")

    plt.show()


