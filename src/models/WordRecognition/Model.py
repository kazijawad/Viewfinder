# Model Design: https://towardsdatascience.com/build-a-handwritten-text-recognition-system-using-tensorflow-2326a3487cd5

import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

'''
Handwritten Text Recognition Model
The model is a convolutional neural network that is built using Tensorflow. The
dataset is the IAM dataset for handwriting recognition. Through the dataset,
we can do supervised learning, as they provide the target values. A standard
batch size of 64 was used.
'''
class Model(object):
    batchSize = 64
    imgSize = (128, 32)
    maxTextLength = 32

    # Model Flow: CNN --> RNN --> CTC
    def __init__(self, chars, mustRestore=False, dump=False):
        self.chars = chars
        self.mustRestore = mustRestore
        self.dump = dump
        self.snapshotCount = 0

        # Determines whether to use normalization over a batch
        self.isTraining = tf.placeholder(tf.bool, name="is_train")

        # Input image batch
        self.inputImgs = tf.placeholder(tf.float32,
                                        shape=(None,
                                               Model.imgSize[0],
                                               Model.imgSize[1]))

        # Setup different layers of the neural network
        self.setupCNN()
        self.setupRNN()
        self.setupCTC()

        # Setup optimizations
        self.trainedBatches = 0
        self.learningRate = tf.placeholder(tf.float32, shape=[])
        self.updateOps = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(self.updateOps):
            self.optimizer = tf.train.RMSPropOptimizer(self.learningRate).minimize(self.loss)

        self.session, self.saver = self.setupTF()

    # Returns convolutional neural network layers
    def setupCNN(self):
        # Creates a one dimensional tensor
        cnn = tf.expand_dims(input=self.inputImgs, axis=3)

        # Parameters needed for the layers
        kernels = [5, 5, 3, 3, 3]
        features = [1, 32, 64, 128, 128, 256]
        pools = [(2, 2), (2, 2), (1, 2), (1, 2), (1, 2)]
        strides = pools
        count = len(strides)

        # First Layer Input
        pool = cnn

        # Create layers
        for layer in range(count):
            # Layer needs to range from 0 to 1 for normalization
            normal = tf.truncated_normal([kernels[layer], kernels[layer],
                                          features[layer], features[layer + 1]],
                                         stddev=0.1)
            kernel = tf.Variable(normal)
            conv = tf.nn.conv2d(pool, kernel, padding="SAME", strides=(1, 1, 1, 1))
            normalConv = tf.layers.batch_normalization(conv, training=self.isTraining)
            relu = tf.nn.relu(normalConv)
            pool = tf.nn.max_pool(relu,
                                  (1, pools[layer][0],pools[layer][1], 1),
                                  (1, strides[layer][0], strides[layer][1], 1),
                                  "VALID")

        self.cnn = pool

    # Returns recurrent neural network layers
    def setupRNN(self):
        # Start the layer with the CNN as an input
        rnn = tf.squeeze(self.cnn, axis=[2])

        # Generate cells for RNN
        hiddenCount = 256
        layerCount = 2
        cells = []
        for _ in range(layerCount):
            lstmCell = tf.nn.rnn_cell.LSTMCell(num_units=hiddenCount,
                                               state_is_tuple=True)
            cells.append(lstmCell)

        # Stack cells into RNN
        stack = tf.nn.rnn_cell.MultiRNNCell(cells, state_is_tuple=True)

        # Bidirectional RNN
        (forward, backward), _ = tf.nn.bidirectional_dynamic_rnn(cell_fw=stack,
                                                                 cell_bw=stack,
                                                                 inputs=rnn,
                                                                 dtype=rnn.dtype)
        concat = tf.expand_dims(tf.concat([forward, backward], 2), 2)

        # Create normalized layers
        normal = tf.truncated_normal([1, 1, hiddenCount * 2, len(self.chars) + 1],
                                     stddev=0.1)
        kernel = tf.Variable(normal)
        conv = tf.nn.atrous_conv2d(value=concat, filters=kernel, rate=1, padding="SAME")
        self.rnn = tf.squeeze(conv, axis=[2])

    # Returns the final evaluation of the model, a CTC loss and decoder
    def setupCTC(self):
        self.ctc = tf.transpose(self.rnn, [1, 0, 2])
        self.targets = tf.SparseTensor(tf.placeholder(tf.int64, shape=[None, 2]),
                                       tf.placeholder(tf.int32, [None]),
                                       tf.placeholder(tf.int64, [2]))

        # Calculate loss for the current batch
        self.sequenceLength = tf.placeholder(tf.int32, [None])
        loss = tf.nn.ctc_loss(labels=self.targets,
                              inputs=self.ctc,
                              sequence_length=self.sequenceLength,
                              ctc_merge_repeated=True)
        self.loss = tf.reduce_mean(loss)

        # Calculate loss for each image to calculate label probability
        self.ctcInput = tf.placeholder(tf.float32,
                                       shape=[Model.maxTextLength, None, len(self.chars) + 1])
        self.imageLoss = tf.nn.ctc_loss(labels=self.targets,
                                        inputs=self.ctcInput,
                                        sequence_length=self.sequenceLength,
                                        ctc_merge_repeated=True)

        # Use the built in greedy decoder
        self.decoder = tf.nn.ctc_greedy_decoder(inputs=self.ctc,
                                                sequence_length=self.sequenceLength)

    # Start tensorflow session
    def setupTF(self):
        session = tf.Session()
        saver = tf.train.Saver(max_to_keep=1)
        # snapshot = tf.train.latest_checkpoint("../../../models/")
        snapshot = True

        if self.mustRestore and not snapshot:
            raise Exception("No saved model found")

        if snapshot:
            saver.restore(session, "/Users/kazijawad/Documents/Projects/Viewfinder/models/snapshot-38.index")
        else:
            session.run(tf.global_variables_initializer())

        return session, saver

    # Creates a sparse for training
    def generateSparse(self, texts):
        indexes = []
        values = []
        shape = [len(texts), 0]

        for batchItem, text in enumerate(texts):
            labels = [self.chars.index(char) for char in text]
            if len(labels) > shape[1]:
                shape[1] = len(labels)

            for index, label in enumerate(labels):
                indexes.append([batchItem, index])
                values.append(label)

        return indexes, values, shape

    # Extracts the text from the CTC decoder
    def extractOutput(self, ctc, batchSize):
        encodedLabels = [[] for _ in range(batchSize)]
        output = ctc[0][0]
        for index1, index2 in enumerate(output.indices):
            label = output.values[index1]
            batchItem = index2[0]
            encodedLabels[batchItem].append(label)
        
        text = []
        for label in encodedLabels:
            labelChars = []
            for char in label:
                labelChars.append(self.chars[char])
            text.append(str().join(labelChars))
        return text

    # Trains a batch of training set through the neural network
    def trainBatch(self, batch):
        batchItemCount = len(batch.imgs)
        sparse = self.generateSparse(batch.targets)

        # Decaying learning rate
        if self.trainedBatches < 10:
            rate = 0.01
        else:
            if self.trainedBatches < 1000:
                rate = 0.001
            else:
                rate = 0.0001

        fetches = [self.optimizer, self.loss]
        feed = {
            self.inputImgs: batch.imgs,
            self.targets: sparse,
            self.sequenceLength: [Model.maxTextLength] * batchItemCount,
            self.learningRate: rate,
            self.isTraining: True
        }

        _, loss = self.session.run(fetches, feed_dict=feed)
        return loss

    # Feeds validation batch into a trained neural network
    def validateBatch(self, batch):
        batchItemCount = len(batch.imgs)
        evals = [self.decoder] + []
        feed = {
            self.inputImgs: batch.imgs,
            self.sequenceLength: [Model.maxTextLength] * batchItemCount,
            self.isTraining: False
        }

        result = self.session.run(evals, feed)
        decoded = result[0]
        text = self.extractOutput(decoded, batchItemCount)
        return text

    # Saves a snapshot of the model as a file
    def save(self):
        self.snapshotCount += 1
        self.saver.save(self.session, "/Users/kazijawad/Documents/Projects/Viewfinder/models", global_step=self.snapshotCount)
