import numpy as np

# Handles each batch of samples
class Batch(object):
    def __init__(self, gtTexts, imgs):
        self.gtTexts = gtTexts
        self.imgs = np.stack(imgs, axis=0)
