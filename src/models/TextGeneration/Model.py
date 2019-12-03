import tensorflow as tf
import numpy as np

class TextGeneration(object):
    sequenceLength = 100
    epochs = 10
    batchSize = 64
    bufferSize = 1000
    embeddingDims = 256
    rnnUnits = 1024

    @staticmethod
    def splitInputTarget(chunk):
        inputText = chunk[:-1]
        targetText = chunk[1:]
        return inputText, targetText

    def __init__(self, file, filePath):
        self.file = tf.keras.utils.get_file(file, filePath)
        self.text = open(self.file, "rb").read().decode("utf-8")
        self.chars = sorted(set(self.text))
        self.charLength = len(self.chars)
        self.charToIndex = {char: index for index, char in enumerate(self.chars)}
        self.indexToChar = np.array(self.chars)
        self.textValue = np.array([self.charToIndex[char] for char in self.text])
        self.examplesPerEpoch = len(self.text) // (TextGeneration.sequenceLength + 1)
        self.charDataset = tf.data.Dataset.from_tensor_slices(self.textValue)
        self.sequences = self.charDataset.batch(TextGeneration.sequenceLength + 1, drop_remainder=True)
        self.dataset = self.sequences.map(TextGeneration.splitInputTarget)
        self.dataset = self.dataset.shuffle(TextGeneration.bufferSize).batch(TextGeneration.batchSize, drop_remainder=True)

    def buildModel(self):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Embedding(self.charLength,
                                      TextGeneration.embeddingDims,
                                      batch_input_shape=[TextGeneration.batchSize, None]),
            tf.keras.layers.GRU(TextGeneration.rnnUnits,
                                return_sequences=True,
                                stateful=True,
                                recurrent_initializer="glorot_uniform"),
            tf.keras.layers.Dense(self.charLength)
        ])

    def loss(self, labels, logits):
        return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

    def trainModel(self):
        self.buildModel()
        self.model.compile(optimizer="adam", loss=self.loss)
        self.model.fit(self.dataset, epochs=TextGeneration.epochs)
        self.model.save_weights("modelWeights.h5")

    def generateText(self, startString):
        charCount = 1000
        inputEval = [self.charToIndex[char] for char in startString]
        inputEval = tf.expand_dims(inputEval, 0)
        generatedText = []
        temperature = 1.0
        self.model.reset_states()
        for _ in range(charCount):
            predictions = self.model(inputEval)
            predictions = tf.squeeze(predictions, 0)
            predictions = predictions / temperature
            predictionID = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()
            inputEval = tf.expand_dims([predictionID], 0)
            generatedText.append(self.indexToChar[predictionID])

        return (startString + "".join(generatedText))

    def predictModel(self, startString):
        TextGeneration.batchSize = 1
        self.buildModel()
        self.model.load_weights("modelWeights.h5")
        self.model.build(tf.TensorShape([1, None]))
        self.generatedText = self.generateText(startString)

if __name__ == "__main__":
    model = TextGeneration("shakespeare.txt",
                           "https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt")
    model.trainModel()
