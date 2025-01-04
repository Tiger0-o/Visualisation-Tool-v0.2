import tkinter as tk
from tkinter import filedialog, StringVar, Menu, messagebox
from PIL import Image, ImageTk
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation 
import urllib3, PIL, numpy
import numpy as np
import requests
from io import BytesIO

window = tk.Tk()
window.title("Visualisation Tool")
window.geometry("1200x600")
window.configure(bg="white")

import ctypes
iconURL = "https://raw.githubusercontent.com/Tiger0-o/LiDAR-Application-Program-v0.2/3164e6d36620fc709c3f50d759d1716a9a58f417/iconLIDAR.ico"
myappid = u"lidar.visualisation.application.bytiger"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

response = requests.get(iconURL)
icon = ImageTk.PhotoImage(Image.open(BytesIO(response.content)))
window.iconphoto(True, icon)

right_frame = tk.Frame(window, bg="white")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

imageDropdownURL = "https://raw.githubusercontent.com/Tiger0-o/LiDAR-Application-Program-v0.2/03a1bbe2f2a46e8fede9c2c13db321ab0895a591/Animation%20Test%20(1).png"
imageUploadURL = "https://raw.githubusercontent.com/Tiger0-o/LiDAR-Application-Program-v0.2/03a1bbe2f2a46e8fede9c2c13db321ab0895a591/Animation%20Test%20(2).png"

def loadImage(url, size=(50,50)):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image = image.resize(size)
            return ImageTk.PhotoImage(image)
        else:
            print(f"Failed to fetch image. HTTP Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

global filePath
filePath = str()
fontCustomisation = {'family':'Gotham','color':'#9ac0cd','size':15}

programColours = {
    'colorOne': '#2a1d5b',
    'colorTwo': '#9ac0cd',
    'colorThree': '#33995a',
    'colorFour': '#9cbb21',
    'colorFive': '#d9c40a'
}

cmapColours = {
    'Viridis': ['#440154', '#3B528B', '#21908C', '#5DC963', '#FDE725'],
    'Plasma': ['#F0F921', '#F59D15', '#D94801', '#A52301', '#5E4FA2'],
    'Inferno': ['#000004', '#410967', '#932567', '#F1605D', '#FCFDBF'],
    'Magma': ['#000004', '#3B0F70', '#8C2981', '#DE4968', '#FCFDBF'],
    'Cividis': ['#00204C', '#2E4A7D', '#667FA1', '#A5B3B3', '#FFE945']
}

def uploadFile():
    global filePath, fileText
    filePath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if filePath:
        uploadDesc.config(text=f"Valid CSV file uploaded") 
        print(f"File uploaded: {filePath}")

def initializeEmptyPlot():
    global canvaemptyFig, emptyFig
    emptyFig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(5, 5))
    
    ax.set_xlabel('X', fontdict=fontCustomisation)
    ax.set_ylabel('Y', fontdict=fontCustomisation)
    ax.set_zlabel('Z', fontdict=fontCustomisation)
    ax.set_title('LiDAR 3D Points Visualization', fontdict=fontCustomisation, weight='bold')

    canvaemptyFig = FigureCanvasTkAgg(emptyFig, master=right_frame)
    canvaemptyFig.draw()
    canvaemptyFig.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

from mpl_interactions import ioff, panhandler, zoom_factory

def visualise():
    global current_fig, canvas
    if filePath == '' and colour.get() == "CHOOSE Colour Palettes for Visualisation":
        messagebox.showerror("Error", "Please upload a valid CSV file and choose a color palette.")
        return
    elif filePath == '':
        messagebox.showerror("Error", "Please upload a valid CSV file.")
        return
    elif colour.get() == "CHOOSE Colour Palettes for Visualisation":
        messagebox.showerror("Error", "Please choose a color palette.")
        return

    plt.close(emptyFig)
    canvaemptyFig.get_tk_widget().destroy()

    if current_fig:
        plt.close(current_fig)
        current_fig = None
    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None

    try:
        df = pd.read_csv(filePath)
        required_columns = ['Distance', ' Yaw', ' Pitch']
        if not all(col in df.columns for col in required_columns):
            messagebox.showerror("Error", "CSV file does not contain the required columns: 'Distance', 'Yaw', 'Pitch'.")
            return

        r = df['Distance'].round(1).tolist()
        yaw = df[' Yaw'].round(1).tolist()
        pitch = df[' Pitch'].round(1).tolist()

    except Exception as e:
        messagebox.showerror("Error", f"Error reading CSV file: {e}")
        return

    def polarRec(distance, yaw_deg, pitch_deg):
        phi = math.radians(yaw_deg)
        theta = math.radians(pitch_deg)
        x = round(distance * math.cos(theta) * math.cos(phi), 1)
        y = round(distance * math.cos(theta) * math.sin(phi), 1)
        z = round(distance * math.sin(theta), 1)
        return x, y, z

    coordinates = [polarRec(d, y, p) for d, y, p in zip(r, yaw, pitch)]
    xList, yList, zList = zip(*coordinates)

    with ioff:
        current_fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(5, 5))

    z_min = min(zList)
    z_max = max(zList)
    normalized_z = [(z - z_min) / (z_max - z_min) for z in zList]

    selected_palette = colour.get().lower().split(': ')[1] if 'CHOSEN' in colour.get() else ''
    scatter = ax.scatter(xList, yList, zList, c=normalized_z, cmap=selected_palette, marker='o')

    ax.set_xlabel('X', fontdict=fontCustomisation)
    ax.set_ylabel('Y', fontdict=fontCustomisation)
    ax.set_zlabel('Z', fontdict=fontCustomisation)
    ax.set_title('LiDAR 3D Points Visualization', fontdict=fontCustomisation, weight='bold')

    disconnect_zoom = zoom_factory(ax)
    pan_handler = panhandler(current_fig)

    canvas = FigureCanvasTkAgg(current_fig, master=right_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    print("Interactive visualization enabled with zoom and pan.")


def showMenu(event):
    menu = Menu(window, tearoff=0, bg='white', fg=programColours['colorTwo'])
    for color in cmapColours.keys():
        menu.add_command(label=color, command=lambda value=color: setSelectedColor(value))
    menu.post(event.x_root, event.y_root)

def setSelectedColor(value):
    colour.set('Colour Palette CHOSEN: ' + value)
    colourLabel.config(text=value)
    updateColorButtons(value)

def updateColorButtons(palette):
    for widget in frameColorIcons.winfo_children():
        widget.destroy()

    colors = cmapColours.get(palette, ['#ffffff']*5)
    
    for color in colors:
        color_button = tk.Label(
            frameColorIcons,
            bg=color,
            width=4,
            height=2,
            borderwidth=0
        )
        color_button.pack(side=tk.LEFT, padx=5, pady=1)

initializeEmptyPlot()
imageUpload = loadImage(imageDropdownURL)
imageDropdown = loadImage(imageUploadURL)

titlelabel = tk.Label(
    master=window, 
    text='3D LiDAR Visualization Program', 
    font=("Gotham", 20, "bold"),
    bg="white",
    fg=programColours['colorTwo']
)
titlelabel.pack(anchor='w', pady=(10, 20), padx=(20, 0))

frameUpload = tk.Frame(window, bg="white")
frameUpload.pack(pady=(0, 20), anchor='w', padx=(20, 0))

uploadButton = tk.Button(
    frameUpload,
    image=imageUpload,
    command=uploadFile,
    bg="white",
    bd=0
)
uploadButton.pack(side=tk.LEFT, padx=5, pady=5)

frameUploadDesc = tk.Frame(frameUpload, bg="white")
frameUploadDesc.pack(side=tk.LEFT)

uploadLabel = tk.Label(
    frameUploadDesc,
    text="UPLOAD CSV FILE",
    font=("Gotham", 15, "bold"),
    bg="white",
    fg=programColours['colorTwo']
)
uploadLabel.pack(anchor='w', padx=1)

uploadDesc = tk.Label(
    frameUploadDesc,
    text="Please upload a vaild CSV file",
    font=("Gotham", 11),
    bg="white",
    fg=programColours['colorTwo']
)
uploadDesc.pack(anchor='w', padx=1)

frameColour = tk.Frame(window, bg="white")
frameColour.pack(pady=(10, 20), anchor='w', padx=(20, 0))

frameColourDesc = tk.Frame(frameColour, bg="white")
frameColourDesc.pack(side=tk.LEFT)

dropDownIcon = tk.Label(
    frameColourDesc,
    image=imageDropdown,
    bg="white",
    bd=0
)
dropDownIcon.pack(side=tk.LEFT, padx=5, pady=5, anchor='w')

colourDesc = tk.Label(
    frameColourDesc,
    text="COLOUR",
    font=("Gotham", 15, "bold"),
    bg="white",
    fg=programColours['colorTwo']
)
colourDesc.pack(anchor='w')

colour = StringVar()
colour.set("CHOOSE Colour Palettes for Visualisation")

colourLabel = tk.Label(
    frameColourDesc,
    textvariable=colour,
    font=("Gotham", 12),
    bg='white',
    fg=programColours['colorTwo'],
    borderwidth=0,
    relief="flat",
    cursor="hand2"
)
colourLabel.pack(anchor='w')
colourLabel.bind("<Button-1>", showMenu)

frameColorIcons = tk.Frame(frameColourDesc, bg="white")
frameColorIcons.pack(anchor='w', pady=(10, 0))

visualiseButton = tk.Button(
    window,
    text="VISUALISE",
    font=("Gotham", 15, "bold"),
    bg='white',
    fg = programColours['colorTwo'],
    command=visualise
)
visualiseButton.pack(anchor='w', padx=(20, 0))

current_fig = None
canvas = None

window.mainloop()
