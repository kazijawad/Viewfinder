# Viewfinder - A Handwritten Math Problem Solver

from tkinter import Tk, Canvas, filedialog, Text
import tkinter as tk
import cv2 as cv

from classes.Model import Model
from classes.ImageLoader import cleanImage
from classes.Batch import Batch

# Model
class State(object):
    def __init__(self):
        self.mode = "start"
        self.file = None
        self.height = 800
        self.width = 800
        self.margin = 25
        self.timerDelay = 50

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
                           text={state.file}, font="Helvetica 12 normal",
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

def loadModeRedrawAll(canvas, state):
    # Draw Background
    canvas.create_rectangle(0, 0, state.width, state.height,
                            fill="#004445")

    # Draw Heading
    canvas.create_text(state.width // 2, state.height // 2,
                       text="Analyzing Handwritten Text",
                       font="Helvetica 48 bold",
                       fill="#ffd800")

    # Draw Subheading
    canvas.create_text(state.width // 2, state.height // 2 + 75,
                       text="This may take awhile...",
                       font="Helvetica 21 normal",
                       fill="#6fb98f")

def editModeRedrawAll(root, canvas, state):
    # Draw Background
    canvas.create_rectangle(0, 0, state.width, state.height,
                            fill="#004445")

    # Draw Textbox
    textbox = Text(root)
    textbox.insert("end", state.text)
    canvas.create_window(state.margin, state.margin,
                         window=textbox, anchor="nw")
    state.text = textbox.get("1.0", "end")

    # Draw Execute Button
    canvas.create_rectangle(state.margin, state.height - state.margin - 60,
                            state.margin + 240, state.height - state.margin,
                            fill="#2c7872", outline="")
    canvas.create_text(state.margin + 120, state.height - state.margin - 30,
                       text="Execute Code", font="Helvetica 21 bold",
                       fill="#ffd800")

def resultModeRedrawAll(canvas, state):
    # Draw Background
    canvas.create_rectangle(0, 0, state.width, state.height,
                            fill="#004445")

    # Draw Execution
    canvas.create_text(state.width // 2, state.height // 2,
                       text={exec('"Hi"')}, font="Helvetica 21 bold",
                       fill="#ffd800")

def redrawAll(root, canvas, state):
    canvas.delete("all")
    if state.mode == "start":
        startModeRedrawAll(canvas, state)
    elif state.mode == "upload":
        uploadModeRedrawAll(canvas, state)
    elif state.mode == "load":
        loadModeRedrawAll(canvas, state)
    elif state.mode == "edit":
        editModeRedrawAll(root, canvas, state)
    elif state.mode == "result":
        resultModeRedrawAll(canvas, state)

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
        analyzeText(state)
        state.mode = "edit"

def executeMousePressed(root, canvas, event, state):
    if (event.x > state.margin
        and event.x < state.margin + 240
        and event.y > state.height - state.margin - 60
        and event.y < state.height - state.margin):
        state.mode = "result"

def mousePressed(root, canvas, event, state):
    if state.mode == "start":
        startMousePressed(event, state)
    elif state.mode == "upload":
        uploadMousePressed(event, state)
    elif state.mode == "edit":
        executeMousePressed(root, canvas, event, state)
    redrawAll(root, canvas, state)

def analyzeText(state):
    model = Model(open("../model/chars.txt").read(), mustRestore=True)
    img = cv.imread(state.file, cv.IMREAD_GRAYSCALE)
    cleanedImg = cleanImage(img, Model.imgSize)
    batch = Batch(None, [cleanedImg])
    text = model.detectBatch(batch)
    state.text = text[0]

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
