import numpy as np

'''
A batch represents a portion of images from the sample used for training. The
portion is dictated by the batch size. The targets per batch represent the
expected output of the neural network. Each of the targets will be compared
against the neural network to calculate a cost function and adjust the weights
accordingly. This is more efficient over sending our entire training dataset
through the neural network.
'''
class Batch(object):
    def __init__(self, imgs, targets):
        self.imgs = np.stack(imgs, axis=0)
        self.targets = targets
