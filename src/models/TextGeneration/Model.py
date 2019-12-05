import tensorflow as tf
import numpy as np

'''
Text Generation Model
The model is a recurrent neural network that is built using Keras on Tensorflow.
The dataset is based on a given piece of literature, ideally in a txt file.
'''
class TextGeneration(object):
    sequenceLength = 100
    epochs = 10
    batchSize = 64
    bufferSize = 1000
    embeddingDims = 256
    rnnUnits = 1024

    # Split dataset between input data and target data
    @staticmethod
    def splitInputTarget(chunk):
        inputText = chunk[:-1]
        targetText = chunk[1:]
        return inputText, targetText

    # Initialize the dataset
    def __init__(self, file, filePath):
        # Retrieve the file and extract the text and relevant information
        self.file = tf.keras.utils.get_file(file, filePath)
        self.text = open(self.file, "rb").read().decode("utf-8")
        self.chars = sorted(set(self.text))
        self.charLength = len(self.chars)
        self.charToIndex = {char: index for index, char in enumerate(self.chars)}
        self.indexToChar = np.array(self.chars)

        # Create a mapping of the text to an integer value
        self.textValue = np.array([self.charToIndex[char] for char in self.text])

        # Calculate the batch size based on the class attributes and text
        self.examplesPerEpoch = len(self.text) // (TextGeneration.sequenceLength + 1)

        # Create the batches and input dataset
        self.charDataset = tf.data.Dataset.from_tensor_slices(self.textValue)
        self.sequences = self.charDataset.batch(TextGeneration.sequenceLength + 1, drop_remainder=True)
        self.dataset = self.sequences.map(TextGeneration.splitInputTarget)

        # Create a shuffled dataset for better training and validation
        self.dataset = self.dataset.shuffle(TextGeneration.bufferSize).batch(TextGeneration.batchSize, drop_remainder=True)

    # Create the model using a Recurrent Neural Network Design
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

    # Return a loss function for categorical values that map characters to integers
    def loss(self, labels, logits):
        return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

    # Train the model
    def trainModel(self, modelName):
        self.buildModel()
        self.model.compile(optimizer="adam", loss=self.loss)
        self.model.fit(self.dataset, epochs=TextGeneration.epochs)
        self.model.save_weights(f"{modelName.lower()}ModelWeights.h5")

    # Used in the prediction function to generate text
    def generateText(self, startString, charCount):
        inputEval = [self.charToIndex[char] for char in startString]
        inputEval = tf.expand_dims(inputEval, 0)
        generatedText = []
        temperature = 1.0 # Defines how far from the original style the generated text should be
        self.model.reset_states()

        # Continue to generate text to the character limit set by the user
        for _ in range(charCount):
            predictions = self.model(inputEval)
            predictions = tf.squeeze(predictions, 0)
            predictions = predictions / temperature
            predictionID = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()
            inputEval = tf.expand_dims([predictionID], 0)
            generatedText.append(self.indexToChar[predictionID])

        return (startString + "".join(generatedText))

    # Generates text based on an input using a trained model
    def predictModel(self, startString, charCount, modelName):
        TextGeneration.batchSize = 1
        self.buildModel()
        self.model.load_weights(f"./models/TextGeneration/{modelName.lower()}ModelWeights.h5")
        self.model.build(tf.TensorShape([1, None]))
        self.generatedText = self.generateText(startString, charCount)
