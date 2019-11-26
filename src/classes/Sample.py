# Handles each sample of imgs and their labeling
class Sample(object):
    def __init__(self, gtTexts, filePath):
        self.gtTexts = gtTexts
        self.filePath = filePath
