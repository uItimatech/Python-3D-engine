'''-------------------------------------------
              3D RENDERING ENGINE
----------------------------------------------
Simple python 3D renderer made from scratch.

Created by ultimatech
First update: 13/03/2021 14:46
Last update: 20/03/2022 12:23
Version: Beta 0.1.5

                    2022
-------------------------------------------'''




# ------------ Import modules --------------

# Default modules
from dis import dis
from time import time, sleep
from os import system
from win32api import EnumDisplayDevices, EnumDisplaySettings

from random import randint
from math import *



# Custom modules
from model_import import obj



# Downloads the missing required modules

# 2D graphics module
try:
    from graphics import *
except ImportError:
    system('python -m pip install graphics.py')
    from graphics import *



# Cuda rendering
try:
    from numba import jit, cuda, timeit
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

class camera:

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
    maxValue = 'auto'     # Leave 'none' for benchmarking
    timer = 0
    counter = object


    if maxValue == 0 or maxValue == 'none':
        maxValue = 999
    elif maxValue == 'auto':
        maxValue = getattr(EnumDisplaySettings(EnumDisplayDevices().DeviceName, -1), 'DisplayFrequency')
    
    lastValue = maxValue



# Sets render settings
renderDebug = dict({
    "wireframe": True,
    "faceNormals": False,
    "faces": True,
    "vertices": True,
    "orthographic": False,
    "cudaRendering": False,
    "coordinates": True,
    "FPSCounter": True
})



# Uses CUDA GPU if available
if "NVIDIA" or "Nvidia" in EnumDisplayDevices().DeviceString:
    renderDebug["cudaRendering"] = True



# Color index for debug face color
color_index = [(255, 0, 0), (235, 0, 0), (0, 255, 0), (0, 235, 0), (0, 0, 255), (0, 0, 235), (128, 128, 0), (98, 128, 0), (128, 0, 128), (128, 0, 98), (0, 128, 128), (0, 98, 128)]
#color_index = [randint(0,255) for i in range(12)]



# Setup projection matrixes
projection_matrix = [[1,0,0],
                     [0,1,0],
                     [0,0,1 ]]


rotation_matrix = [[0,0,1],
                   [0,1,0],
                   [1,0,0]]


# Setups render window
window = GraphWin('Render', window.width, window.height, autoflush=False)
window.setCoords(-window.width, -window.height, window.width, window.height)



# Resets camera position
def resetCoords():

    global camera

    camera.x = -105
    camera.y = 65
    camera.z = -15

    camera.dir.vertical = 0
    camera.dir.horizontal = 0



# Used to converts rgb values into hex
def rgb(red, green, blue):
    hexValue = '#%02x%02x%02x' % (red, green, blue)
    return hexValue



# Used to multiply projection matrixes
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



# Returns an array of points and faces corresponding to a cube
def setCube(originX, originY, originZ, Xsize, Ysize, Zsize, *Rotation):  # Add x, y, z position, size and rotation parameters

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

    return (cubeFaces, pointArray)



# Returns the projection of a 3D point in space onto the camera plane
def getPoint(x, y, z): # Will later support multiple cameras

    dx = x - camera.x
    dy = y - camera.y
    dz = z - camera.z

    dt = sqrt(dy**2 + dz**2)
    distance = sqrt(dt**2 + dx**2)

    try:
        dirX = atan(dz / dx)
        dirY = atan(dy / dx)
    except:
        dirX = 0
        dirY = 0

    #dirX = (dirX - camera.dir.vertical +1)*180
    #dirY = (dirY - camera.dir.horizontal +1)*180

    dirX = (dirX - camera.dir.vertical)
    dirY = (dirY - camera.dir.horizontal)

    '''if dirX > 360:
        dirX -= 360
    if dirX < 0:
        dirX += 360'''



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

    #distance = sqrt((dx)**2 + (dy)**2 + (dz)**2)

    return ((point, x, y, z, distance), dirX, dirY)



# Returns a triangle object for rendering
def getTriangle(point1, point2, point3, id):

    Vertices = [point1[0], point2[0], point3[0]]

    gravityCenterX = (point1[1]+point2[1]+point3[1])/3
    gravityCenterY = (point1[2]+point2[2]+point3[2])/3
    gravityCenterZ = (point1[3]+point2[3]+point3[3])/3

    gravityCenter = getPoint(gravityCenterX, gravityCenterY, gravityCenterZ)[0][0]

    distance = getPoint(gravityCenterX, gravityCenterY, gravityCenterZ)[0][4]

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
        gravityCenter = Circle(gravityCenter, 1/log(distance))
        gravityCenter.setFill("red")
        gravityCenter.draw(window)

    return (Triangle, distance) 



# ---------------- Unrenderer ----------------

def clear():
    # Undraws all faces for next frame
    for item in window.items[:]:
        item.undraw()

# Resets camera position
resetCoords()




# ----------------- Render -------------------

def render():
    
    # Clears last frame
    clear()

    # --------------- Element list ---------------

    elementList = [
            setCube(50, 0, 0, 50, 50, 50),
            setCube(50, 50, 50, 100, 50, 50),
            setCube(50, 0, 50, 50, 50, 50),
            setCube(50, 0, -100, 0, 50, 37),
            ]




    # FPS clock
    global FPS, last_clock_time

    clock_time = time.time() - start_clock_time
    FPS.timer = clock_time - last_clock_time
    FPS.value += 1



    # Querry element faces and vertices to be sorted by distance and rendered
    elementFaces = []
    elementVertices = []

    for currentElement in elementList:

        # Gets all faces
        for currentItem in currentElement[0]:
            elementFaces.append(currentItem)

        # Gets all vertices
        for currentItem in currentElement[1]:
            elementVertices.append(currentItem)


    # Removes unecessary vertices positions
    elementVertices = [(currentVertice[0],currentVertice[4]) for currentVertice in elementVertices]



    # Allows to sort by the farthest distance
    def distanceKey(face):
        return face[1]


    # Sorts arrays by the farthest distance elements
    elementFaces.sort(key=distanceKey,reverse=True)
    elementVertices.sort(key=distanceKey,reverse=True)



    for currentVertice in elementVertices:
        if renderDebug.get("vertices") == True:
            currentVertice = Circle(currentVertice[0], 150/log(currentVertice[1]/(10**8)))
            currentVertice.setFill('orange')
            currentVertice.setOutline('')
            currentVertice.draw(window)

    for currentFace in elementFaces:
        if renderDebug.get("faces") == True or renderDebug.get("wireframe") == True: 
            currentFace[0].draw(window)





    # Draws origin
    origin = Point(0, 0)
    origin = Circle(origin, 3)
    origin.setFill('red')
    origin.draw(window)


    # Sets and displays current FPS
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


    # Displays camera coordinates
    if renderDebug.get("coordinates") == True: 
        infos = str("(" + str(round(camera.x, 3)) + ";" +
                    str(round(camera.y, 3)) + ";" + str(round(camera.z, 3)) + ")")
        posDisplay = Text(Point(0, -window.width+70), infos)
        posDisplay.draw(window)

        infos = str("(" + str(camera.dir.vertical) + ";" + str(camera.dir.horizontal) + ")")
        dirDisplay = Text(Point(0, (-window.width)+30), infos)
        dirDisplay.draw(window)




# ------------ Main loop and keybinds -----------

while True:

    # Render frames
    clock_time = time.time() - start_clock_time
    render()
    update(FPS.maxValue*1.05)



    # Prevents FPS from affecting inputs
    inputSpeed = 1.0 / ((FPS.lastValue+0.01) / 120)


    # Keyboard inputs
    '''if keyboard.is_pressed('s'):

        camera.x = camera.x - (sin(camera.dir.vertical))/360
        camera.z = camera.z - (cos(camera.dir.vertical))/360

    if keyboard.is_pressed('z'):

        camera.x = camera.x + (sin(camera.dir.vertical))
        camera.z = camera.z + (cos(camera.dir.vertical))

    if keyboard.is_pressed('d'):

        camera.dir.vertical += 1

    if keyboard.is_pressed('q'):

        camera.dir.vertical -= 1'''
    
    if keyboard.is_pressed('s'):

        camera.x -= inputSpeed

    if keyboard.is_pressed('z'):

        camera.x += inputSpeed

    if keyboard.is_pressed('space'):

        camera.y += inputSpeed

    if keyboard.is_pressed('shift'):

        camera.y -= inputSpeed

    if keyboard.is_pressed('d'):

        camera.z += inputSpeed

    if keyboard.is_pressed('q'):

        camera.z -= inputSpeed

    if keyboard.is_pressed('left_arrow'):

        camera.dir.vertical -= inputSpeed / 4

    if keyboard.is_pressed('right_arrow'):

        camera.dir.vertical += inputSpeed / 4

    if keyboard.is_pressed('up_arrow'):

        camera.dir.horizontal += inputSpeed / 4

    if keyboard.is_pressed('down_arrow'):

        camera.dir.horizontal -= inputSpeed / 4



    if keyboard.is_pressed('&'):
        if not(renderDebug.get("vertices")):
            renderDebug["vertices"] = True
        else:
            renderDebug["vertices"] = False
        while keyboard.is_pressed('&'):
            sleep(0.1)

    if keyboard.is_pressed('é'):
        if not(renderDebug.get("wireframe")):
            renderDebug["wireframe"] = True
        else:
            renderDebug["wireframe"] = False
        while keyboard.is_pressed('é'):
            sleep(0.1)

    if keyboard.is_pressed('"'):
        if not(renderDebug.get("faces")):
            renderDebug["faces"] = True
        else:
            renderDebug["faces"] = False
        while keyboard.is_pressed('"'):
            sleep(0.1)

    if keyboard.is_pressed("'"):
        if not(renderDebug.get("faceNormals")):
            renderDebug["faceNormals"] = True
        else:
            renderDebug["faceNormals"] = False
        while keyboard.is_pressed("'"):
            sleep(0.1)

    if keyboard.is_pressed("("):
        if not(renderDebug.get("orthographic")):
            renderDebug["orthographic"] = True
        else:
            renderDebug["orthographic"] = False
        while keyboard.is_pressed("("):
            sleep(0.1)

    if camera.dir.vertical < 0:
        camera.dir.vertical += 360

    if camera.dir.vertical > 360:
        camera.dir.vertical -= 360

    if keyboard.is_pressed('esc'):
        window.close()