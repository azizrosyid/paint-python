from fileinput import filename
from itertools import count
import math
import queue
import random
from re import S

import tkinter
from tkinter import CENTER, LEFT, NW, Image, Label, PhotoImage, messagebox, colorchooser, filedialog
from tkinter.messagebox import NO, askyesno
import tkinter.filedialog

import PIL
from PIL import ImageGrab


class Main:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.coordinates = []
        self.color = "black"
        self.root = tkinter.Tk()
        self.root.iconphoto(True, tkinter.PhotoImage(file="paint.png"))
        self.root.title("Aplikasi Paint")
        self.root.state('zoomed')
        self.addMenu()
        self.createCanvas()
        self.drawPen()
        self.root.mainloop()

    def addMenu(self):
        self.menu = tkinter.Menu(self.root)
        self.root.config(menu=self.menu)

        self.fileMenu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="New", command=self.resetCanvas)
        self.fileMenu.add_command(label="Save", command=self.saveCanvas)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.root.quit)

        # add image menu
        self.imageMenu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Add Image", command=self.addImage)

        self.insertMenu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Insert", menu=self.insertMenu)
        self.insertMenu.add_command(label="Line", command=self.drawLine)
        self.insertMenu.add_command(label="Pen", command=self.drawPen)
        self.insertMenu.add_command(label="Circle", command=self.drawCircle)
        self.insertMenu.add_command(label="Oval", command=self.drawOval)
        self.insertMenu.add_command(
            label="Rectangle", command=self.drawRectangle)

        # menu color picker
        self.colorMenu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Color", command=self.setColor)

        self.colorMenu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Fill Color", command=self.fillColor)

        # menu transform 2d
        self.transformMenu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Transform", menu=self.transformMenu)
        self.transformMenu.add_command(label="Move", command=self.move)
        self.transformMenu.add_command(label="Scale", command=self.scale)

    def createCanvas(self):
        self.canvas = tkinter.Canvas(
            self.root, bg='white')
        # scale canvas to zoom
        self.canvas.config(width=self.root.winfo_screenwidth(),
                           height=self.root.winfo_screenheight())
        self.canvas.pack()

    def resetCanvas(self):
        isReset = askyesno(
            "Reset Canvas", "Are you sure? This will erase all the drawing.")
        if isReset:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")

            self.canvas.delete("all")

        self.canvas.create_polygon(self.coordinates, fill='', outline='black')

    def saveCanvas(self):
        filepath = tkinter.filedialog.asksaveasfilename(
            title="Save Canvas", filetypes=[("PNG", "*.png")])

        if filepath == None:
            return
        ImageGrab.grab(bbox=(
            self.root.winfo_rootx(), self.root.winfo_rooty(), self.root.winfo_rootx() + self.root.winfo_width() + 100, self.root.winfo_rooty() + self.root.winfo_height())).save(filepath)
        messagebox.showinfo("Saved", "Saved to " + filepath)

    def setMousePosition(self, event):
        self.x = event.x
        self.y = event.y

    def drawLine(self):
        self.lineId = self.canvas.create_line(
            0, 0, 0, 0, fill=self.color, width=1)
        self.canvas.bind("<Button-1>", self.setMousePosition)
        self.canvas.bind("<B1-Motion>", self.drawLineMotion)
        self.canvas.bind("<ButtonRelease-1>", self.drawLineStop)

    def drawLineMotion(self, event):
        self.canvas.coords(self.lineId, self.x, self.y, event.x, event.y)

    def drawLineStop(self, event):
        dx = abs(event.x - self.x)
        incrementX = 1 if self.x < event.x else -1
        dy = -abs(event.y - self.y)
        incrementY = 1 if self.y < event.y else -1
        err = dx + dy
        while True:
            self.drawPixel(self.x, self.y)
            if self.x == event.x and self.y == event.y:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                self.x += incrementX
            if e2 <= dx:
                err += dx
                self.y += incrementY

    def drawPen(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

        self.penId = self.canvas.create_oval(
            0, 0, 0, 0, fill=self.color, outline=self.color, width=1)
        self.canvas.bind("<Button-1>", self.setMousePosition)
        self.canvas.bind("<B1-Motion>", self.drawPenMotion)

    def drawPenMotion(self, event):
        self.drawLineStop(event)

    def drawPixel(self, x, y):
        self.coordinates.append(x)
        self.coordinates.append(y)
        self.canvas.create_oval(
            x, y, x+1, y+1, fill=self.color, outline=self.color, width=1)

    def drawCircle(self):
        self.circleId = self.canvas.create_oval(
            0, 0, 0, 0,  outline=self.color)
        self.canvas.bind("<Button-1>", self.setMousePosition)
        self.canvas.bind("<B1-Motion>", self.drawCircleMotion)
        self.canvas.bind("<ButtonRelease-1>", self.drawCircleStop)

    def drawCircleMotion(self, event):
        radius = math.sqrt((event.x - self.x)**2 + (event.y - self.y)**2)

        x = self.x - radius
        y = self.y - radius
        self.canvas.coords(self.circleId, x, y, x + radius * 2, y + radius * 2)

    def drawCircleStop(self, event):
        radius = math.sqrt((event.x - self.x)**2 + (event.y - self.y)**2)

        x = 0
        y = radius
        d = 1 - radius
        while x < y:
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

            self.drawPixel(self.x + x, self.y + y)
            self.drawPixel(self.x - x, self.y + y)
            self.drawPixel(self.x + x, self.y - y)
            self.drawPixel(self.x - x, self.y - y)
            self.drawPixel(self.x + y, self.y + x)
            self.drawPixel(self.x - y, self.y + x)
            self.drawPixel(self.x + y, self.y - x)
            self.drawPixel(self.x - y, self.y - x)

    def drawOval(self):
        self.ovalId = self.canvas.create_oval(
            0, 0, 0, 0, outline=self.color)
        self.canvas.bind("<Button-1>", self.setMousePosition)
        self.canvas.bind("<B1-Motion>", self.drawOvalMotion)
        self.canvas.bind("<ButtonRelease-1>", self.drawOvalStop)

    def drawOvalMotion(self, event):
        self.canvas.coords(self.ovalId, self.x, self.y, event.x, event.y)

    def drawOvalStop(self, event):
        # midpoint ellipse algorithm
        midX = (event.x + self.x) / 2
        midY = (event.y + self.y) / 2

        rx = abs(event.x - self.x) / 2
        ry = abs(event.y - self.y) / 2

        x = 0
        y = ry

        d1 = ((ry * ry) - (rx * rx * ry) + (0.25 * rx * rx))
        dx = 2 * ry * ry * x
        dy = 2 * rx * rx * y

        while dx < dy:
            self.drawPixel(midX + x, midY + y)
            self.drawPixel(midX + x, midY - y)
            self.drawPixel(midX - x, midY + y)
            self.drawPixel(midX - x, midY - y)

            if d1 < 0:
                x += 1
                dx += 2 * ry * ry
                d1 += dx + ry * ry
            else:
                x += 1
                y -= 1
                dx += 2 * ry * ry
                dy -= 2 * rx * rx
                d1 += dx - dy + ry * ry

        d2 = (((ry * ry) * ((x + 0.5) * (x+0.5))) +
              (rx * rx * ((y - 1) * (y - 1)))) - (rx * rx * ry * ry)
        while y >= 0:
            self.drawPixel(midX + x, midY + y)
            self.drawPixel(midX + x, midY - y)
            self.drawPixel(midX - x, midY + y)
            self.drawPixel(midX - x, midY - y)

            if d2 > 0:
                y -= 1
                dy -= 2 * rx * rx
                d2 -= dy + rx * rx
            else:
                y -= 1
                x += 1
                dx += 2 * ry * ry
                dy -= 2 * rx * rx
                d2 += dx - dy + rx * rx

    def drawRectangle(self):
        self.rectangleId = self.canvas.create_rectangle(
            0, 0, 0, 0, outline=self.color)
        self.canvas.bind("<Button-1>", self.setMousePosition)
        self.canvas.bind("<B1-Motion>", self.drawRectangleMotion)
        self.canvas.bind("<ButtonRelease-1>", self.drawRectangleStop)

    def drawRectangleMotion(self, event):
        self.canvas.coords(self.rectangleId, self.x, self.y, event.x, event.y)

    def drawRectangleStop(self, event):
        self.canvas.create_rectangle(
            self.x, self.y, event.x, event.y, outline=self.color, width=1)
        self.canvas.delete(self.rectangleId)

    def fillColor(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

        self.canvas.bind("<Button-1>", self.fillColorPressed)

    def fillColorPressed(self, event):
        count = 0
        id = event.widget.find_overlapping(event.x, event.y, event.x, event.y)
        queuePixel = queue.Queue()
        queuePixel.put((event.x, event.y))

        while not queuePixel.empty():
            count += 1
            x, y = queuePixel.get()
            newId = event.widget.find_overlapping(x, y, x, y)

            if newId == id:
                self.canvas.create_rectangle(x, y, x, y, outline=self.color)
                queuePixel.put((x - 1, y))
                queuePixel.put((x + 1, y))
                queuePixel.put((x, y - 1))
                queuePixel.put((x, y + 1))
        

    def setColor(self):
        # color picker
        colorCode = colorchooser.askcolor()
        self.color = colorCode[1]

    def move(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

        self.canvas.bind("<Button-1>", self.setMousePosition)
        self.canvas.bind("<B1-Motion>", self.moveMotion)

    def moveMotion(self, event):
        self.canvas.move(self.canvas.find_withtag("current"),
                         event.x - self.x, event.y - self.y)
        self.x = event.x
        self.y = event.y

    def scale(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

        self.canvas.bind("<Button-1>", self.setMousePosition)
        self.canvas.bind("<B1-Motion>", self.scaleMotion)

    def scaleMotion(self, event):
        self.canvas.scale(self.canvas.find_withtag("current"),
                          event.x, event.y, event.x / self.x, event.y / self.y)
        self.x = event.x
        self.y = event.y

    def addImage(self):
        image = filedialog.askopenfilename(filetypes=(
            ("PNG files", "*.png"), ("All files", "*.*")))

        tk_image = PhotoImage(file="{}".format(image))
        tk_image = tk_image.subsample(2, 2)
        self.canvas.create_image(20, 20, image=tk_image, anchor=NW)

        labelImage = Label(self.root, text="Image")
        labelImage.image = tk_image
        labelImage.pack(side=LEFT)


Main()
