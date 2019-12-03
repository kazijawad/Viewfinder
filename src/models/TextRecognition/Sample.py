'''
A sample is one image of a batch. The samples are trained on the neural
network to improve the weights and yield better results. The training
dataset is provided through the filePath. The target represent the
expected output of a well-trained neural network.
'''
class Sample(object):
    def __init__(self, filePath, target):
        self.filePath = filePath
        self.target = target
