import os
import random
import numpy as np
import cv2 as cv

from cleanImage import cleanImg

# Handles each sample of imgs and their labeling
class Sample(object):
    def __init__(self, gtTexts, filePath):
        self.gtTexts = gtTexts
        self.filePath = filePath

# Handles each batch of samples
class Batch(object):
    def __init__(self, gtTexts, imgs):
        self.gtTexts = gtTexts
        self.imgs = np.stack(imgs, axis=0)

# Handles loading the image into the model
class ImageLoader(object):
    def __init__(self, filePath, batchSize, imgSize, maxTextLength):
        self.augmentData = False
        self.batchSize = batchSize
        self.imgSize = imgSize
        self.samples = []
        self.currentIndex = 0

        wordFile = open(filePath + "words.txt")
        chars = set()
        bad_samples = []
        bad_samples_reference = ["a01-117-05-02.png", "r06-022-03-05.png"]

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
            chars = chars.union(set([gtText]))

            # Check for empty image
            if not os.path.getsize(fileName):
                bad_samples.append(lines[0] + ".png")

            self.samples.append(Sample(gtText, fileName))

        self.chars = sorted([chars])

        # Print bad files that are not marked with issues
        if set(bad_samples) != set(bad_samples_reference):
            print(f"[WARNING] Damaged Files Found:", bad_samples)
            print(f"[INFO] Expected Damaged FIles:", bad_samples_reference)

        # Split into training set and validation set (95%)
        splitIndex = int(0.95 * len(self.samples))
        self.trainingSamples = self.samples[:splitIndex]
        self.validationSamples = self.samples[splitIndex:]

        # Create lists for the words
        self.trainingWords = [sample.gtText for sample in self.trainingSamples]
        self.validationWords = [sample.gtText for sample in self.validationSamples]

        # Amount of samples per epoch
        self.trainingSamplesPerEpoch = 25000

        # Initialize training set
        self.trainingSet()

    # Account for the cost of labels that repeat for images
    def truncateLabel(self, text, maxTextLength):
        cost = 0
        for index in range(len(text)):
            if (index != 0) and (text[index] == text[index - 1]):
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
            gtTexts.append(self.samples[index])
            img = cv.imread(self.samples[index].filePath, cv.IMREAD_GRAYSCALE)
            cleanedImg = cleanImg(img, self.imgSize, self.augmentData)
            imgs.append(cleanedImg)

        self.currentIndex += self.batchSize
        return Batch(gtTexts, imgs)
