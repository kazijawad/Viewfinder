# Viewfinder - A Handwritten Math Problem Solver

import sys

from tkinter import Tk, Canvas, filedialog, Text
import tkinter as tk
import cv2 as cv
import tensorflow as tf

# Model
class State(object):
    def __init__(self):
        self.mode = "start"
        self.file = None
        self.height = 800
        self.width = 800
        self.margin = 25
        self.timerDelay = 50
        self.previousMode = ""
        self.currentMode = "start"
        self.inputText = ""
        self.generatedText = ""

# View
def startModeRedrawAll(canvas, state):
    # Draw Background
    canvas.create_rectangle(0, 0, state.width, state.height,
                            fill="#004445")

    # Draw Heading
    canvas.create_text(state.width // 2, state.height // 2 - 100,
                       text="Welcome to Viewfinder!", anchor="s",
                       font="Helvetica 48 bold", fill="#ffd800")

    # Draw Subheading
    canvas.create_text(state.width // 2, state.height // 2 - 50,
                       text="A language model for generating paragraphs of text.",
                       anchor="s", font="Helvetica 21 normal", fill="#ffd800")

    # Draw Button
    canvas.create_rectangle(state.width // 2 - 100, state.height // 2 + 50,
                            state.width // 2 + 100, state.height // 2 + 110,
                            fill="#2c7873", outline="")
    canvas.create_text(state.width // 2, state.height // 2 + 80,
                       text="START", font="Helvetica 16 bold",
                       fill="#ffd800")

def uploadModeRedrawAll(canvas, state):
    # Draw Background
    canvas.create_rectangle(0, 0, state.width, state.height,
                            fill="#004445")
    canvas.create_rectangle(state.margin, state.margin,
                            state.width - state.margin,
                            state.height - state.margin - 100,
                            outline="#ffd800", dash=(5, 10),
                            fill="")

    # Upload Button
    canvas.create_rectangle(state.width // 2 - 120, state.height // 2 - 20,
                            state.width // 2 + 120, state.height // 2 - 80,
                            fill="#2c7873", outline="")
    canvas.create_text(state.width // 2, state.height // 2 - 50,
                       text="Upload An Image", font="Helvetica 21 bold",
                       fill="#ffd800")

    # File Text
    if state.file != None:
        canvas.create_text(state.width // 2, state.height // 2 - 100,
                           text=state.file, font="Helvetica 14 normal",
                           fill="#ffd800", anchor="s")

    # Analyze Button
    canvas.create_rectangle(state.width // 2 - 120,
                            state.height - state.margin - 60,
                            state.width // 2 + 120,
                            state.height - state.margin,
                            fill="#2c7873", outline="")
    canvas.create_text(state.width // 2,
                       state.height - state.margin - 30,
                       text="Generate Text", font="Helvetica 21 bold",
                       fill="#ffd800")

def resultsModeRedrawAll(canvas, state):
    # Draw Background
    canvas.create_rectangle(0, 0, state.width, state.height,
                            fill="#004445")

    # Draw Input Heading
    canvas.create_text(state.margin, state.margin,
                       text="Input Text", font="Helvetica 18 bold",
                       anchor="nw", fill="#2c7873")

    # Draw Input Text
    canvas.create_text(state.margin, state.margin + 50,
                       text=state.inputText, font="Helvetica 21 normal",
                       anchor="nw", fill="#ffd800")

    # Draw Output Heading
    canvas.create_text(state.margin, state.margin + 100,
                       text="Generated Text", font="Helvetica 18 bold",
                       anchor="nw", fill="#2c7873")

    # Draw Output Text
    canvas.create_text(state.margin, state.margin + 150,
                       text=state.generatedText, font="Helvetica 12 normal",
                       anchor="nw", fill="#ffd800")

    # Draw Back Button
    canvas.create_rectangle(state.margin,
                            state.height - state.margin - 60,
                            state.margin + 120,
                            state.height - state.margin,
                            fill="#2c7873", outline="")
    canvas.create_text(state.margin + 60,
                       state.height - state.margin - 30,
                       text="Home", font="Helvetica 21 bold",
                       fill="#ffd800")

    # Draw Download Button
    canvas.create_rectangle(state.width - state.margin - 180,
                            state.height - state.margin - 60,
                            state.width - state.margin,
                            state.height - state.margin,
                            fill="#2c7873", outline="")
    canvas.create_text(state.width - state.margin - 90,
                       state.height - state.margin - 30,
                       text="Download", font="Helvetica 21 bold",
                       fill="#ffd800")

def redrawAll(canvas, state):
    canvas.delete("all")
    if state.currentMode == "start":
        startModeRedrawAll(canvas, state)
    elif state.currentMode == "upload":
        uploadModeRedrawAll(canvas, state)
    elif state.currentMode == "results":
        resultsModeRedrawAll(canvas, state)

def timerFired(canvas, state):
    redrawAll(canvas, state)
    canvas.after(state.timerDelay, timerFired, canvas, state)

# Controller
def startMousePressed(event, state):
    if (event.x > state.width // 2 - 100 and event.x < state.width // 2 + 100 and
        event.y > state.height // 2 + 50 and event.y < state.height // 2 + 110):
        state.currentMode = "upload"

def uploadMousePressed(event, state):
    if (event.x > state.width // 2 - 120
        and event.x < state.width // 2 + 120
        and event.y > state.height // 2 - 80
        and event.y < state.height // 2 - 20):
        file = filedialog.askopenfilename(initialdir="/Desktop", title="Select Image")
        if file != "":
            state.file = file
    elif (event.x > state.width // 2 - 120
          and event.x < state.width // 2 + 120
          and event.y > state.height - state.margin - 60
          and event.y < state.height - state.margin
          and state.file != None):
        recognizeText(state)
        generateText(state)
        state.currentMode = "results"

def resultsMousePressed(event, state):
    if (event.x > state.margin
        and event.x < state.margin + 120
        and event.y > state.height - state.margin - 60
        and event.y < state.height - state.margin):
        state.currentMode = "start"
    elif (event.x > state.width - state.margin - 180
          and event.x < state.width - state.margin
          and event.y > state.height - state.margin - 60
          and event.y < state.height - state.margin):
        outputFile = open("generated.txt", "w+")
        outputFile.write(state.generatedText)
        outputFile.close()

def mousePressed(canvas, event, state):
    if state.currentMode == "start":
        startMousePressed(event, state)
    elif state.currentMode == "upload":
        uploadMousePressed(event, state)
    elif state.currentMode == "results":
        resultsMousePressed(event, state)
    redrawAll(canvas, state)

def recognizeText(state):
    from models.TextRecognition.Model import TextRecognition
    from models.TextRecognition.ImageLoader import prepareImage
    from models.TextRecognition.Batch import Batch

    chars = open("./models/TextRecognition/data/chars.txt").read()
    model = TextRecognition(chars, mustRestore=True)
    img = cv.imread(state.file, cv.IMREAD_GRAYSCALE)
    img = prepareImage(img, TextRecognition.imgSize)
    batch = Batch([img], None)
    text = model.validateBatch(batch)
    state.inputText = text[0]

    tf.compat.v1.reset_default_graph()
    tf.compat.v1.enable_eager_execution()

def generateText(state):
    from models.TextGeneration.Model import TextGeneration

    model = TextGeneration("shakespeare.txt",
                           "https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt")
    model.predictModel(state.inputText)
    state.generatedText = model.generatedText

def main():
    # Create Instance and State
    root = Tk()
    root.wm_title("Viewfinder - Language Text Generation")
    root.resizable(height=False, width=False)
    state = State()

    # Draw Interface
    canvas = Canvas(root, height=state.height, width=state.width)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()

    # Event Handling
    root.bind("<Button-1>", lambda event: mousePressed(canvas, event, state))

    # Loop
    timerFired(canvas, state)
    root.mainloop()

if __name__ == "__main__":
    main()
