# Viewfinder - A Handwritten Math Problem Solver

from tkinter import Tk, Canvas, filedialog, Text
import tkinter as tk
import cv2 as cv

from models.WordRecognition.Model import Model
from models.WordRecognition.ImageLoader import prepareImage
from models.WordRecognition.Batch import Batch

# Model
class State(object):
    def __init__(self):
        self.mode = "start"
        self.file = None
        self.height = 800
        self.width = 800
        self.margin = 25
        self.timerDelay = 50
        self.inputText = ""
        self.generatedText = ""

# View
def startModeRedrawAll(canvas, state):
    # Draw Background
    canvas.create_rectangle(0, 0, state.width, state.height,
                            fill="#004445")

    # Draw Heading
    canvas.create_text(state.width // 2, state.height // 3 - 25,
                       text="Welcome to Viewfinder!",
                       font="Helvetica 48 bold",
                       fill="#ffd800")
    
    # Draw Subheading
    canvas.create_text(state.width // 2, state.height // 3 + 50,
                       text="A handwritten code analysis tool for debugging.",
                       font="Helvetica 21 normal",
                       fill="#ffd800")

    # Draw Button
    canvas.create_rectangle(state.width // 2 - 100, state.height // 2,
                            state.width // 2 + 100, state.height // 2 + 60,
                            fill="#2c7873", outline="")
    canvas.create_text(state.width // 2, state.height // 2 + 30,
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
                       text="Analyze Image", font="Helvetica 21 bold",
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

def redrawAll(root, canvas, state):
    canvas.delete("all")
    if state.mode == "start":
        startModeRedrawAll(canvas, state)
    elif state.mode == "upload":
        uploadModeRedrawAll(canvas, state)
    elif state.mode == "results":
        resultsModeRedrawAll(canvas, state)

def timerFired(root, canvas, state):
    redrawAll(root, canvas, state)
    canvas.after(state.timerDelay, timerFired, canvas, state)

# Controller
def startMousePressed(event, state):
    if (event.x > state.width // 2 - 100 and event.x < state.width // 2 + 100 and
        event.y > state.height // 2 and event.y < state.height // 2 + 60):
        state.mode = "upload"

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
        generateText(state)
        state.mode = "results"

def mousePressed(root, canvas, event, state):
    if state.mode == "start":
        startMousePressed(event, state)
    elif state.mode == "upload":
        uploadMousePressed(event, state)
    redrawAll(root, canvas, state)

def generateText(state):
    # chars = open("./models/WordRecognition/data/chars.txt").read()
    # model = Model(chars, mustRestore=True)
    # img = cv.imread(state.file, cv.IMREAD_GRAYSCALE)
    # img = prepareImage(img, Model.imgSize)
    # batch = Batch([img], None)
    # text = model.validateBatch(batch)
    # state.inputText = text[0]
    state.inputText = "little"
    state.generatedText = '''
ROMEO: little! I am herset me assure.

GONZALO:
He'll be slanderous free;
And he's warm at thy word, sir: this is come nature,
Put that strenks a brib; when the very neck Lewer is both
For petty us: the mocking of himself than yet
unboandliant. Thou know'd a windows who rath,
Should I away.

BIANly be gone: then, and begin
The providence great.

CAPTISTA:
Well neither
Left amendly you of my quarrel?

GROMIO:
Yes, both these time.

ANTONIO:
Well, go we are agues no cormeted till Kath a faultheeght
I would bo heaven, bestrewith you you are well.

PROSPERO:
No; forswear it.

TRANIO:
Why, this shapp'd olves! hath had like a thou not queen;
Faith, lest wont thou now,'STONTIO:
Nay, no, there teeks the most of his own.
'''

def main():
    # Create Instance and State
    root = Tk()
    root.wm_title("Viewfinder - Handwritten Code Analysis")
    root.resizable(height=False, width=False)
    state = State()

    # Draw Interface
    canvas = Canvas(root, height=state.height, width=state.width)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()

    # Event Handling
    root.bind("<Button-1>", lambda event: mousePressed(root, canvas, event, state))

    # Loop
    timerFired(root, canvas, state)
    root.mainloop()

if __name__ == "__main__":
    main()
