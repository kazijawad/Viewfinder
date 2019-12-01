import os
import random
import numpy as np
import cv2 as cv

from classes.Sample import Sample
from classes.Batch import Batch

'''
Prepares the image for the neural network. To yield the most consistent
results, all the images will have the same dimensions and color gamut for
training.
'''
def prepareImage(img, imgSize, augmentData=False):    
    '''
    If an image is damaged or corrupt, we generated a matrix of zeros to
    the desired size. A matrix of zeros is ignored by the neural network,
    as it focuses on the portions of the image involving ones.
    '''
    if img is None:
        img = np.zeros([imgSize[1], imgSize[0]])

    '''
    Data augmentation is a regularization method used within neural networks
    that adds variability to the training set and can improve the model to
    be generalized for general purpose. For computer vision, a simple
    augmentation is changing the aspect ratio of the image. The parameter
    is optional because we only want to be augmenting the data during
    training.
    '''
    if augmentData:
        stretch = random.random() - 0.5
        widthStretch = max(int(img.shape[1] * (1 + stretch)), 1)
        img = cv.resize(img, (widthStretch, img.shape[0]))

    '''
    For tensorflow to properly handle each image that is given to the neural
    network, it must be the same height and width. To be consistent, we need
    to account for augmentations and the aspect ratio of the image.
    '''
    targetWidth, targetHeight = imgSize
    height, width = img.shape
    frameX = width / targetWidth
    frameY = height / targetHeight
    frame = max(frameX, frameY)
    newSize = (max(min(targetWidth, int(width / frame)), 1),
               max(min(targetHeight, int(height / frame)), 1))

    # Create the image
    img = cv.resize(img, newSize)
    targetImg = np.ones([targetHeight, targetWidth]) * 256
    targetImg[0:newSize[1], 0:newSize[0]] = img
    img = cv.transpose(targetImg)

    # Normalize the image
    mean, std = cv.meanStdDev(img)
    mean = mean[0][0]
    std = std[0][0]
    img = img - mean
    if std > 0:
        img = img / std

    return img

'''
ImageLoader handles the dataset through the training process of the
neural network. Iterations are the number of batches needed to complete
one epoch.
'''
class ImageLoader(object):
    def __init__(self, filePath, batchSize, imgSize, maxTextLength):
        self.batchSize = batchSize
        self.imgSize = imgSize
        self.augmentData = False
        self.currentIndex = 0
        self.samples = []

        wordFile = open(filePath + "words.txt")
        chars = set()

        '''
        The word file contains all the information on the IAM dataset. We can
        retrieve the target value for each image, which is the output we expect
        our neural network to return after training.
        '''
        for line in wordFile:
            # Ignore inital comments on the top of the file
            if not line or line[0] == "#":
                continue

            '''
            From each line we want to extract the target value and the
            characters used in the target value. These characters will be used
            later on as a list for all possible outcomes the image can yield.
            '''
            lines = line.strip().split(" ")
            fileNames = lines[0].split("-")
            fileName = (filePath + "words/" +
                        fileNames[0] + "/" +
                        fileNames[0] + "-" +
                        fileNames[1] + "/" +
                        lines[0] + ".png")
            target = self.truncateLabel(" ".join(lines[8:]), maxTextLength)
            chars = chars.union(set(list(target)))

            '''
            We don't want to include empty images to our sample dataset.
            These files will be ignored and not used throughout training.
            '''
            if not os.path.getsize(fileName):
                continue

            self.samples.append(Sample(fileName, target))

        '''
        In supervised learning, we want to split our dataset into a training
        portion and validation portion. The validation portion is used to test
        against a trained neural network for it's accuracy. There are more ideal
        and advanced validation methods, such as cross validation, but we kept it
        simple at a 95% - 5% split.
        '''
        splitIndex = int(0.95 * len(self.samples))
        self.trainingSamples = self.samples[:splitIndex]
        self.validationSamples = self.samples[splitIndex:]

        self.trainingWords = [sample.target for sample in self.trainingSamples]
        self.validationWords = [sample.target for sample in self.validationSamples]
        self.samplesPerEpoch = 25000
        self.trainingSet()
        self.chars = sorted(list(chars))

    # Account for the cost of labels that repeat for images
    def truncateLabel(self, text, maxTextLength):
        cost = 0
        for index in range(len(text)):
            if index != 0 and text[index] == text[index - 1]:
                cost += 2
            else:
                cost += 1
            if cost > maxTextLength:
                return text[:index]
        return text

    # Initialze the images for neural network training
    def trainingSet(self):
        self.augmentData = True
        self.currentIndex = 0
        random.shuffle(self.trainingSamples)
        self.samples = self.trainingSamples[:self.samplesPerEpoch]

    # Initialize the images for neural network validation
    def validationSet(self):
        self.augmentData = False
        self.currentIndex = 0
        self.samples = self.validationSamples

    # Returns iteration
    def getIteration(self):
        return (self.currentIndex // self.batchSize + 1,
                len(self.samples) // self.batchSize)

    # Check for more batches
    def hasNext(self):
        return (self.currentIndex + self.batchSize <= len(self.samples))

    # Returns next batch
    def getNext(self):
        targets = []
        imgs = []
        for index in range(self.currentIndex, self.currentIndex + self.batchSize):
            targets.append(self.samples[index].target)
            img = cv.imread(self.samples[index].filePath, cv.IMREAD_GRAYSCALE)
            img = prepareImage(img, self.imgSize, self.augmentData)
            imgs.append(img)

        self.currentIndex += self.batchSize
        return Batch(imgs, targets)
