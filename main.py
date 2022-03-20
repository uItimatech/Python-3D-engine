'''-------------------------------------------
              3D RENDERING ENGINE
----------------------------------------------
Simple python 3D renderer made from scratch.

Created by ultimatech
First update: 13/03/2021 14:46
Last update: 20/03/2022 12:23
Version: Beta 0.1.4

                    2022
-------------------------------------------'''




# ------------ Import libraries --------------

from time import time, sleep 
from os import system
from turtle import window_width
from win32api import EnumDisplayDevices, EnumDisplaySettings

from random import randint
from math import *



# Downloads the missing required modules 

# 2D graphics module
try:
    from graphics import *
except ImportError:
    system('python -m pip install graphics.py')
    from graphics import *


# Cuda rendering
try:
    from numba import jit, cuda
except ImportError:
    system('python -m pip install numba')
    from numba import jit, cuda


# Keyboard support
try:
    import keyboard
except ImportError:
    system('python -m pip install keyboard')
    import keyboard




# ----------- Initialize variables -----------

class player:

    x = float
    y = float
    z = float

    class dir:
        vertical = float
        horizontal = float


class window:
    width = 1024
    height = 1024
    vertical_resolution = 256
    horizontal_resolution = 256


class FOV:
    horizontal = 90
    vertical = 45

start_clock_time = time.time()
last_clock_time = 0


class FPS:
    value = int()
    maxValue = 'none'     # Leave 'none' for benchmarking
    timer = 0
    counter = object


    if maxValue == 0 or maxValue == 'none':
        maxValue = 999
    elif maxValue == 'auto':
        maxValue = getattr(EnumDisplaySettings(EnumDisplayDevices().DeviceName, -1), 'DisplayFrequency')
    
    lastValue = maxValue


renderDebug = dict({
    "wireframe": True,
    "faceNormals": True,
    "faces": False,
    "orthographic": False,
    "cudaRendering": False
})

# Uses CUDA GPU if available
if "NVIDIA" or "Nvidia" in EnumDisplayDevices().DeviceString:
    renderDebug["cudaRendering"] = True


# Color index for debug face color
color_index = [(255, 0, 0), (255, 0, 0), (0, 255, 0), (0, 255, 0), (0, 0, 255), (0, 0, 255), (128, 128, 0), (128, 128, 0), (128, 0, 128), (128, 0, 128), (0, 128, 128), (0, 128, 128)]
#color_index = [randint(0,255) for i in range(12)]


# Setup projection matrixes
projection_matrix = [[1,0,0],
                     [0,1,0],
                     [0,0,1 ]]

rotation_matrix = [[0,0,1],
                   [0,1,0],
                   [1,0,0]]



window = GraphWin('Render', window.width, window.height, autoflush=False)
window.setCoords(-window.width, -window.height, window.width, window.height)




def resetCoords():

    global player

    player.x = -105
    player.y = 65
    player.z = -15

    player.dir.vertical = 0
    player.dir.horizontal = 0




def rgb(red, green, blue):
    hexValue = '#%02x%02x%02x' % (red, green, blue)
    return hexValue




def multiplyMatrix(matrix1, matrix2):

    matrix1_rows = len(matrix1)
    matrix1_columns = len(matrix1[0])

    matrix2_rows = len(matrix2)
    matrix2_columns = len(matrix2[0])
    
    # Dot product matrix dimentions = matrix1_rows x b_columns
    product = [[0 for i in range(matrix2_columns)] for j in range(matrix1_rows)]

    if matrix1_columns == matrix2_rows:
        for i in range(matrix1_rows):
            for j in range(matrix2_columns):
                for k in range(matrix2_rows):
                    product[i][j] += matrix1[i][k] * matrix2[k][j]
    else:
        print("INCOMPATIBLE MATRIX SIZES")

    return product     




def drawCube(originX, originY, originZ, Xsize, Ysize, Zsize, *rotation):  # Add x, y, z and rotation parameters

    pointArray = []

    pointArray.append(getPoint(originX, originY, originZ + Zsize)[0])
    pointArray.append(getPoint(originX, originY + Ysize, originZ + Zsize)[0])
    pointArray.append(getPoint(originX, originY, originZ)[0])
    pointArray.append(getPoint(originX, originY + Ysize, originZ)[0])
    pointArray.append(getPoint(originX + Xsize, originY, originZ + Zsize)[0])
    pointArray.append(getPoint(originX + Xsize, originY + Ysize, originZ + Zsize)[0])
    pointArray.append(getPoint(originX + Xsize, originY, originZ)[0])
    pointArray.append(getPoint(originX + Xsize, originY + Ysize, originZ)[0])

    cubeFaces = []

    cubeFaces.append(getTriangle(pointArray[0], pointArray[3], pointArray[2], 0))
    cubeFaces.append(getTriangle(pointArray[0], pointArray[1], pointArray[3], 1))
    cubeFaces.append(getTriangle(pointArray[6], pointArray[5], pointArray[4], 2))
    cubeFaces.append(getTriangle(pointArray[6], pointArray[7], pointArray[5], 3))
    cubeFaces.append(getTriangle(pointArray[2], pointArray[4], pointArray[0], 4))
    cubeFaces.append(getTriangle(pointArray[2], pointArray[6], pointArray[4], 5))
    cubeFaces.append(getTriangle(pointArray[1], pointArray[5], pointArray[7], 6))
    cubeFaces.append(getTriangle(pointArray[1], pointArray[7], pointArray[3], 7))
    cubeFaces.append(getTriangle(pointArray[4], pointArray[5], pointArray[1], 8))
    cubeFaces.append(getTriangle(pointArray[4], pointArray[1], pointArray[0], 9))
    cubeFaces.append(getTriangle(pointArray[2], pointArray[7], pointArray[6], 10))
    cubeFaces.append(getTriangle(pointArray[2], pointArray[3], pointArray[7], 11))

    return cubeFaces




def getPoint(x, y, z):

    dx = x - player.x
    dy = y - player.y
    dz = z - player.z

    dt = sqrt(dy**2 + dz**2)
    distance = sqrt(dt**2 + dx**2)

    try:
        dirX = atan(dz / dx)
        dirY = atan(dy / dx)
    except:
        dirX = 0
        dirY = 0

    #dirX = (dirX - player.dir.vertical +1)*180
    #dirY = (dirY - player.dir.horizontal +1)*180

    dirX = (dirX - player.dir.vertical)
    dirY = (dirY - player.dir.horizontal)

    '''if dirX > 360:
        dirX -= 360
    if dirX < 0:
        dirX += 360'''

    #print(dirX, dirY)

    if renderDebug.get("orthographic") == False:

        #pointX = dirX *(window.width*360/FOV.horizontal)/360
        #pointY = dirY *(window.height*360/FOV.vertical)/360

        pointX = dirX * (window.width * 360 / FOV.horizontal) / 360 * 2*FOV.horizontal
        pointY = dirY * (window.height * 360 / FOV.vertical) / 360 * 2*FOV.vertical

    elif renderDebug.get("orthographic") == True:
        rotate_x = multiplyMatrix(rotation_matrix, [[dy/2], [dx/2], [dz/2]])
        rotate_y = multiplyMatrix(rotation_matrix, rotate_x)
        rotate_z = multiplyMatrix(rotation_matrix, rotate_y)
        point_2d = multiplyMatrix(projection_matrix, rotate_z)
    
        pointX = (point_2d[0][0] * 10) #- window.width/2
        pointY = (point_2d[1][0] * 10) #- window.height/2

    point = Point(pointX, pointY)

    distance = sqrt((dx)**2 + (dy)**2 + (dz)**2)

    return ((point, x, y, z), distance, dirX, dirY)




def getTriangle(point1, point2, point3, id):

    Vertices = [point1[0], point2[0], point3[0]]

    gravityCenterX = (point1[1]+point2[1]+point3[1])/3
    gravityCenterY = (point1[2]+point2[2]+point3[2])/3
    gravityCenterZ = (point1[3]+point2[3]+point3[3])/3

    gravityCenter = getPoint(gravityCenterX, gravityCenterY, gravityCenterZ)[0][0]
    gravityCenter.setFill("red")

    distance = getPoint(gravityCenterX, gravityCenterY, gravityCenterZ)[1]

    dirVector1 = [point2[1] - point1[1], point2[2] - point1[2], point2[3] - point1[3]]
    dirVector2 = [point3[1] - point1[1], point3[2] - point1[2], point3[3] - point1[3]]

    normalX = (dirVector1[1] * dirVector2[2] - dirVector1[2] * dirVector2[1])/300
    normalY = (dirVector1[2] * dirVector2[0] - dirVector1[0] * dirVector2[2])/300
    normalZ = (dirVector1[0] * dirVector2[1] - dirVector1[1] * dirVector2[0])/300

    normalVector = getPoint(normalX+gravityCenterX, normalY+gravityCenterY, normalZ+gravityCenterZ)[0][0]

    normalVector = Line(gravityCenter, normalVector)

    Triangle = Polygon(Vertices)

    faceColor = color_index[id]
    faceColor = rgb(faceColor[0],faceColor[1],faceColor[2])

    if renderDebug.get("faces") == True: 
        Triangle.setFill(faceColor)
    if renderDebug.get("faces") == True or renderDebug.get("wireframe") == True: 
        Triangle.setOutline(faceColor)
    if renderDebug.get("wireframe") == True: 
        Triangle.setOutline('black')
    if renderDebug.get("faceNormals") == True: 
        normalVector.setFill("orange")
        normalVector.draw(window)
        gravityCenter.draw(window)

    return (Triangle, distance) 




def clear():
    # Undraws all faces for next frame
    for item in window.items[:]:
        item.undraw()




def render():

    # FPS clock
    global FPS, last_clock_time

    clock_time = time.time() - start_clock_time
    FPS.timer = clock_time - last_clock_time
    FPS.value += 1

    # Clears window
    clear()

    # Querry element faces to be sorted by distance and rendered
    faceArray = []

    faceArray.append(drawCube(50, 0, 0, 50, 50, 50))
    faceArray.append(drawCube(50, 0, 50, 50, 50, 50))
    faceArray.append(drawCube(50, 50, 50, 50, 50, 50))

    faceArray = [currentFace for currentFaces in range(len(faceArray)) for currentFace in faceArray[currentFaces]]


    def distanceKey(face):
        return face[1]

    faceArray.sort(key=distanceKey,reverse=True)

    for currentFace in faceArray:
        if renderDebug.get("faces") == True or renderDebug.get("wireframe") == True: 
            currentFace[0].draw(window)


    origin = Point(0, 0)
    origin = Circle(origin, 3)
    origin.setFill(color_rgb(255, 0, 0))
    origin.draw(window)

    if FPS.timer > 1:
        FPS.lastValue = FPS.value
        FPS.value = 0
        last_clock_time = clock_time

    FPS.counter = Text(Point(-window.width+50+len(str(FPS.lastValue))*9, window.height-25), "FPS:"+str(FPS.lastValue))
    
    if FPS.lastValue <= FPS.maxValue/3:
        FPS.counter.setTextColor("red")
    elif FPS.lastValue <= FPS.maxValue/1.5:
        FPS.counter.setTextColor("orange")
    else:
        FPS.counter.setTextColor("green")

    FPS.counter.draw(window)
    infos = str("(" + str(round(player.x, 3)) + ";" +
                str(round(player.y, 3)) + ";" + str(round(player.z, 3)) + ")")
    posDisplay = Text(Point(0, -window.width+70), infos)
    posDisplay.draw(window)

    infos = str("(" + str(player.dir.vertical) + ";" + str(player.dir.horizontal) + ")")
    dirDisplay = Text(Point(0, (-window.width)+30), infos)
    dirDisplay.draw(window)




# ------------ Render and keybinds -----------

resetCoords()

while True:

    clock_time = time.time() - start_clock_time

    render()

    update(FPS.maxValue*1.05)


    # Prevents FPS from affecting inputs
    inputSpeed = 1.0 / ((FPS.lastValue+0.01) / 120)

    '''if keyboard.is_pressed('s')f:

        player.x = player.x - (sin(player.dir.vertical))/360
        player.z = player.z - (cos(player.dir.vertical))/360

    if keyboard.is_pressed('z'):

        player.x = player.x + (sin(player.dir.vertical))
        player.z = player.z + (cos(player.dir.vertical))

    if keyboard.is_pressed('d'):

        player.dir.vertical += 1

    if keyboard.is_pressed('q'):

        player.dir.vertical -= 1'''
    
    if keyboard.is_pressed('s'):

        player.x -= inputSpeed

    if keyboard.is_pressed('z'):

        player.x += inputSpeed

    if keyboard.is_pressed('space'):

        player.y += inputSpeed

    if keyboard.is_pressed('shift'):

        player.y -= inputSpeed

    if keyboard.is_pressed('d'):

        player.z += inputSpeed

    if keyboard.is_pressed('q'):

        player.z -= inputSpeed

    if keyboard.is_pressed('left_arrow'):

        player.dir.vertical -= inputSpeed / 4

    if keyboard.is_pressed('right_arrow'):

        player.dir.vertical += inputSpeed / 4

    if keyboard.is_pressed('up_arrow'):

        player.dir.horizontal += inputSpeed / 4

    if keyboard.is_pressed('down_arrow'):

        player.dir.horizontal -= inputSpeed / 4

    if keyboard.is_pressed('&'):
        if not(renderDebug.get("wireframe")):
            renderDebug["wireframe"] = True
        else:
            renderDebug["wireframe"] = False
        while keyboard.is_pressed('&'):
            sleep(0.1)

    if keyboard.is_pressed('é'):
        if not(renderDebug.get("faces")):
            renderDebug["faces"] = True
        else:
            renderDebug["faces"] = False
        while keyboard.is_pressed('é'):
            sleep(0.1)

    if keyboard.is_pressed('"'):
        if not(renderDebug.get("faceNormals")):
            renderDebug["faceNormals"] = True
        else:
            renderDebug["faceNormals"] = False
        while keyboard.is_pressed('"'):
            sleep(0.1)

    if keyboard.is_pressed("'"):
        if not(renderDebug.get("orthographic")):
            renderDebug["orthographic"] = True
        else:
            renderDebug["orthographic"] = False
        while keyboard.is_pressed("'"):
            sleep(0.1)

    if player.dir.vertical < 0:
        player.dir.vertical += 360

    if player.dir.vertical > 360:
        player.dir.vertical -= 360

    if keyboard.is_pressed('esc'):
        window.close()