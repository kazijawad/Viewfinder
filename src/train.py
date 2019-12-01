import cv2 as cv
import editdistance

from classes.ImageLoader import prepareImage, ImageLoader
from classes.Batch import Batch
from classes.Model import Model

# Trains the neural network using the IAM dataset
def train(model, loader):
    # Count of training iterations
    epoch = 0
    bestCharErrorRate = float("inf")
    noImprovementSince = 0
    earlyStop = 5

    while True:
        epoch += 1
        print("Epoch:", epoch)

        # Train using the ImageLoader class for iterations
        print("Training Neural Network")
        loader.trainingSet()
        while loader.hasNext():
            iterationInfo = loader.getIteration()
            batch = loader.getNext()
            loss = model.trainBatch(batch)
            print("Batch:", iterationInfo[0], "/", iterationInfo[1],
                  "Loss:", loss)

        # Validation
        charErrorRate = validate(model, loader)
        if charErrorRate < bestCharErrorRate:
            print("Character Error Rate Improved")
            bestCharErrorRate = charErrorRate
            noImprovementSince = 0
            model.save()
            file = open("../model/accuracy.txt", "w")
            file.write(f"Validation Character Error Rate: {charErrorRate * 100}")
            file.close()
        else:
            print("Character Error Rate Not Improved")
            noImprovementSince += 1

        if noImprovementSince >= earlyStop:
            print(f"No improvements since {earlyStop} epochs. Training stopped.")
            break

# Validates a portion of the dataset against the trained neural network
def validate(model, loader):
    print("Validating Neural Network")
    loader.validationSet()
    charErrorCount = 0
    charTotalCount = 0
    okWordCount = 0
    totalWordCount = 0
    while loader.hasNext():
        iterationInfo = loader.getIteration()
        print("Batch:", iterationInfo[0], "/", iterationInfo[1])
        batch = loader.getNext()
        text = model.detectBatch(batch)

        for index in range(len(text)):
            totalWordCount += 1
            if batch.gtTexts[index] == text[index]:
                okWordCount += 1

            distance = editdistance.eval(text[index], batch.gtTexts[index])
            charErrorCount += distance
            charTotalCount += len(batch.gtTexts[index])
            if distance == 0:
                print("OK")
            else:
                print(f"ERROR: {distance}", "\"" + batch.gtTexts[index] + "\"",
                      "->", "\"" + text[index] + "\"")

    charErrorRate = charErrorCount / charTotalCount
    accuracy = okWordCount / totalWordCount
    print(f"Character Error Rate: {charErrorRate * 100}. Accuracy: {accuracy * 100}")
    return charErrorRate

def main():
    loader = ImageLoader("../data/", Model.batchSize, Model.imgSize, Model.maxTextLength)
    model = Model(loader.chars)
    train(model, loader)

if __name__ == "__main__":
    main()
