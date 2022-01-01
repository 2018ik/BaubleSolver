import numpy as np
from shapely.geometry import Polygon
from matplotlib import pyplot as plt
import tkinter as tk
from matplotlib.pyplot import figure
import time
import os 

path = 'gif/'
colors = ["#000000", "#42d4f5", "#f5ce42", "#f59042", "#f1d2fa", "#ff96fa", "#ff1e00", "#ff6f00", "#8b8b8c", "#0004ff", "#a84d4d", "#00660f", "#f7f7f7"]

def showShape(shape):
    # Shows the shape using the cartesian plane
    y,x = np.array(shape).T # swapping x and y b/c how matrices are indexed
    ax = plt.figure().gca()
    plt.scatter(x,y,s=2000)
    plt.gca().invert_yaxis() # invert y-axis b/c how matrices are indexed
    plt.xticks([-1,0,1,2,3,4])
    plt.yticks([-1,0,1,2,3,4])
    plt.show()

def initializeBoard():
    if not os.path.exists(path):
        os.makedirs(path)
    plt.rcParams['axes.facecolor'] = '#363636'
    plt.ion()
    fig, ax = plt.subplots()
    fig.set_size_inches(14, 7, forward=True)
    fig.set_dpi(50)
    lines = []
    for x in range(10):
        numOfPoints = x + 1
        height = 10-x
        offset = 10/2 - (numOfPoints)/2
        for y in range(numOfPoints):
            lines.append(ax.plot(offset + y, height, color="black", linestyle='dashed', marker='o', markersize=40)[0])
    fig.canvas.draw()
    fig.canvas.flush_events()
    return fig, lines

def updateBoard(board, fig, lines, save_image=False):
    iterator = 0
    for x in range(len(board)):
        numOfPoints = x + 1
        for y in range(numOfPoints):
            point = board[x-y][y]
            color = colors[point]
            lines[iterator].set_color(color)
            iterator += 1
    if save_image:
        plt.savefig(path + str(time.time()) + '.png', dpi=70, bbox_inches='tight', pad_inches=0)
    fig.canvas.draw()
    fig.canvas.flush_events()

