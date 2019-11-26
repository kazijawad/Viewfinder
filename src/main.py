# Viewfinder - A Handwritten Code Analysis Tool

from tkinter import Tk, Canvas, filedialog
import tkinter as tk

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

def redrawAll(canvas, state):
    canvas.delete("all")
    if state.mode == "start":
        startModeRedrawAll(canvas, state)
    elif state.mode == "upload":
        uploadModeRedrawAll(canvas, state)

def timerFired(canvas, state):
    redrawAll(canvas, state)
    canvas.after(state.timerDelay, timerFired, canvas, state)

# Controller
def startMousePressed(event, state):
    if (event.x > state.width // 2 - 100 and event.x < state.width // 2 + 100 and
        event.y > state.height // 2 and event.y < state.height // 2 + 60):
        state.mode = "upload"

def uploadMousePressed(event, state):
    if (event.x > state.width // 2 - 120 and event.x < state.width // 2 + 120 and
        event.y > state.height // 2 - 80 and event.y < state.height // 2 - 20):
        file = filedialog.askopenfilename(initialdir="/Desktop", title="Select Image")
        if file != "":
            print(file)
            state.file = file

def mousePressed(canvas, event, state):
    if state.mode == "start":
        startMousePressed(event, state)
    elif state.mode == "upload":
        uploadMousePressed(event, state)
    redrawAll(canvas, state)

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
    root.bind("<Button-1>", lambda event: mousePressed(canvas, event, state))

    # Loop
    timerFired(canvas, state)
    root.mainloop()

if __name__ == "__main__":
    main()
