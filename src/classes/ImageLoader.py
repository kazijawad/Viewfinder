import os
import random
import numpy as np
import cv2 as cv

from Sample import Sample
from Batch import Batch

# Remove noise from image and gray-scale it for the model
def cleanImage(img, imgSize, augmentData=False):    
    # Handle damaged files in the dataset
    if img is None:
        img = np.zeros([imgSize[1], imgSize[0]])

    # Increase dataset size by horizontal stretching images
    if augmentData:
        stretch = random.random() - 0.5
        widthStretch = max(int(img.shape[1] * (1 + stretch)), 1)
        img = cv.resize(img, (widthStretch, img.shape[0]))

    targetWidth, targetHeight = imgSize
    height, width = img.shape

    fx = width / targetWidth
    fy = height / targetHeight
    f = max(fx, fy)

    # Size scales to f with a minimum 1 and max of target width/height
    newSize = (max(min(targetWidth, int(width / f)), 1),
               max(min(targetHeight, int(height / f)), 1))

    # Create the new sized image
    img = cv.resize(img, newSize)
    targetImg = np.ones([targetHeight, targetWidth]) * 256
    targetImg[0:newSize[1], 0:newSize[0]] = img

    # Tensorflow requires a transposed image
    img = cv.transpose(targetImg)

    # Normalize the image
    mean, std = cv.meanStdDev(img)
    mean = mean[0][0]
    std = std[0][0]
    img = img - mean
    if std > 0:
        img = img / std

    return img

# Handles loading the image into the model
class ImageLoader(object):
    def __init__(self, filePath, batchSize, imgSize, maxTextLength):
        self.batchSize = batchSize
        self.imgSize = imgSize
        self.augmentData = False
        self.currentIndex = 0
        self.samples = []

        wordFile = open(filePath + "words.txt")
        chars = set()
        badSamples = []
        badSampleReferences = ["a01-117-05-02.png", "r06-022-03-05.png"]

        # Retrieve name of each file and its expected outcome
        for line in wordFile:
            # Ignore comments
            if not line or line[0] == "#":
                continue

            lines = line.strip().split(" ")
            fileNames = lines[0].split("-")
            fileName = (filePath + "words/" +
                        fileNames[0] + "/" +
                        fileNames[0] + "-" +
                        fileNames[1] + "/" +
                        lines[0] + ".png")

            # GT text start at column 9
            gtText = self.truncateLabel(" ".join(lines[8:]), maxTextLength)
            chars = chars.union(set(list(gtText)))

            # Check for empty image
            if not os.path.getsize(fileName):
                badSamples.append(lines[0] + ".png")
                continue

            self.samples.append(Sample(gtText, fileName))

        # Print bad files that are not marked with issues
        if set(badSamples) != set(badSampleReferences):
            print(f"[WARNING] Damaged Files Found:", badSamples)
            print(f"[INFO] Expected Damaged FIles:", badSampleReferences)

        # Split into training set and validation set (95%)
        splitIndex = int(0.95 * len(self.samples))
        self.trainingSamples = self.samples[:splitIndex]
        self.validationSamples = self.samples[splitIndex:]

        # Create lists for the words
        self.trainingWords = [sample.gtTexts for sample in self.trainingSamples]
        self.validationWords = [sample.gtTexts for sample in self.validationSamples]

        # Amount of samples per epoch
        self.trainingSamplesPerEpoch = 25000

        # Initialize training set
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

    # Load image for training
    def trainingSet(self):
        self.augmentData = True
        self.currentIndex = 0
        random.shuffle(self.trainingSamples)
        self.samples = self.trainingSamples[:self.trainingSamplesPerEpoch]

    # Load image for validation
    def validationSet(self):
        self.augmentData = False
        self.currentIndex = 0
        self.samples = self.validationSamples

    # Returns iteration
    def getInteratorInfo(self):
        return (self.currentIndex // self.batchSize + 1,
                len(self.samples) // self.batchSize)

    # Checks whether there are more batches left
    def hasNext(self):
        return (self.currentIndex + self.batchSize <= len(self.samples))

    # Gets next batch of images based on size and index
    def getNext(self):
        gtTexts = []
        imgs = []
        for index in range(self.currentIndex, self.currentIndex + self.batchSize):
            gtTexts.append(self.samples[index].gtTexts)
            img = cv.imread(self.samples[index].filePath, cv.IMREAD_GRAYSCALE)
            cleanedImg = cleanImage(img, self.imgSize, self.augmentData)
            imgs.append(cleanedImg)

        self.currentIndex += self.batchSize
        return Batch(gtTexts, imgs)
