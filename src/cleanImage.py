import numpy as np
import cv2 as cv

def cleanImg(img, imgSize):
    '''Remove noise from image and gray-scale it for the model'''
    
    # Handle damaged files in the dataset
    if img is None:
        img = np.zeroes([imgSize[1], imgSize[0]])

    targetWidth, targetHeight = imgSize
    height, width = img

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
        img = img / s
    else:
        img

    return img
