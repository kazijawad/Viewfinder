# Viewfinder

Viewfinder is an optical character recognition program that analyzes handwritten text and provides generated text in different writing styles.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software

```
Python 3.6.x
OpenCV 3.4.x
Tensorflow 2.x.x
numpy 1.17.x
editdistance 0.5.x
```

### Installing

A step by step series of examples that tell you how to get a development env running

1. Clone the repository
```
git clone https://github.com/kazijawad/Viewfinder.git
```

2. Change directory and run the python script
```
cd src/
python3 main.py
```

## Usage

### Recommended Installation

The ideal scenario I have found to setup Viewfinder with Tensorflow and OpenCV is to use an Anaconda virtual environment. Through the environment, packages are very easy to manage and the environment can easily be removed later.

### User Flow

To test Viewfinder, trained neural networks are already provided in the source directory. In the root directory there are sample files with varying writing complexity to use as input. Please note, each writing style was trained using a different dataset and trained for a short period of time. Thus, the results of the text recognition and text generation may not be the best possible outcome.

## Built With

* [OpenCV](https://opencv.org/) - Computer Vision Library
* [Tensorflow](https://www.tensorflow.org/) - Machine Learning Platform
* [Numpy](https://numpy.org/) - Scientific Computing Library
* [Tkinter](https://docs.python.org/3/library/tkinter.html) - Python Interface Library

## Author

Kazi Jawad

## Acknowledgments

* [15-112 Fundamentals of Programming and Computer Science](https://www.cs.cmu.edu/~112)
* [3Blue1Brown's Neural Network Series](https://www.3blue1brown.com/neural-networks)
* [Handwritten Text Recognition System Design](https://arxiv.org/pdf/1507.05717.pdf)
* [Text Generation with a Recurrent Neural Network](https://www.tensorflow.org/tutorials/text/text_generation)
* [IAM Handwriting Database](http://www.fki.inf.unibe.ch/databases/iam-handwriting-database)
