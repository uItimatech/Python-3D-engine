'''---------------------------------
        3D rendering engine
------------------------------------

Created by ultimatech
First update: 13/03/2021 14:46
Last update: 19/03/2022 18:12

             2022
---------------------------------'''

from random import randint
from textwrap import fill
from graphics import *
from math import *
import keyboard
from pygame import Vector2
from time import sleep

player_x = float()
player_y = float()
player_z = float()
player_dir_x = float()
player_dir_y = float()

FOV = 90
VFOV = 45
window_width = 1080
window_height = 1080

renderDebug = dict({
    "wireframe": True,
    "faceNormals": True,
    "faces": False,
    "orthographic": True
})

colors = [randint(0,255) for i in range(12)]

window = GraphWin('Render', window_width, window_height, autoflush=False)
window.setCoords(-window_width, -window_height, window_width, window_height)
#window.master.geometry('%dx%d+%d+%d' % (0, 0, 0, 0))


def resetCoords():

    global player_x
    global player_y
    global player_z
    global player_dir_x
    global player_dir_y

    player_x = -105
    player_y = 65
    player_z = -15

    player_dir_x = 0
    player_dir_y = 0


def rgb(red, green, blue):
    hexValue = '#%02x%02x%02x' % (red, green, blue)
    return hexValue


def drawCube():  # Add x, y, z and rotation parameters

    pointArray = []

    pointArray.append(getPoint(50, 0, 50)[0])
    pointArray.append(getPoint(50, 50, 50)[0])
    pointArray.append(getPoint(50, 0, 0)[0])
    pointArray.append(getPoint(50, 50, 0)[0])
    pointArray.append(getPoint(100, 0, 50)[0])
    pointArray.append(getPoint(100, 50, 50)[0])
    pointArray.append(getPoint(100, 0, 0)[0])
    pointArray.append(getPoint(100, 50, 0)[0])

    faceArray = []

    faceArray.append(drawTriangle(pointArray[0], pointArray[3], pointArray[2], 0))
    faceArray.append(drawTriangle(pointArray[0], pointArray[1], pointArray[3], 1))
    faceArray.append(drawTriangle(pointArray[6], pointArray[5], pointArray[4], 2))
    faceArray.append(drawTriangle(pointArray[6], pointArray[7], pointArray[5], 3))
    faceArray.append(drawTriangle(pointArray[2], pointArray[4], pointArray[0], 4))
    faceArray.append(drawTriangle(pointArray[2], pointArray[6], pointArray[4], 5))
    faceArray.append(drawTriangle(pointArray[1], pointArray[5], pointArray[7], 6))
    faceArray.append(drawTriangle(pointArray[1], pointArray[7], pointArray[3], 7))
    faceArray.append(drawTriangle(pointArray[4], pointArray[5], pointArray[1], 8))
    faceArray.append(drawTriangle(pointArray[4], pointArray[1], pointArray[0], 9))
    faceArray.append(drawTriangle(pointArray[2], pointArray[7], pointArray[6], 10))
    faceArray.append(drawTriangle(pointArray[2], pointArray[3], pointArray[7], 11))

    def distanceKey(face):
        return face[1]

    faceArray.sort(key=distanceKey,reverse=True)

    for face in faceArray:
        if renderDebug.get("faces") == True or renderDebug.get("wireframe") == True: 
            face[0].draw(window)


def getPoint(x, y, z):

    dx = x - player_x
    dy = y - player_y
    dz = z - player_z

    dt = sqrt(dy**2 + dz**2)
    distance = sqrt(dt**2 + dx**2)

    try:
        dirX = atan(dz / dx)
        dirY = atan(dy / dx)
    except:
        dirX = atan(dz)
        dirY = atan(dy)

    dirX = dirX - player_dir_x
    dirY = dirY - player_dir_y

    #pX = (dirX * window_width)/360
    #pY = (dirY * window_height)/360

    pX = dirX * (window.getWidth() * 360 / FOV) / 360 * 2*FOV
    pY = dirY * (window.getHeight() * 360 / VFOV) / 360 * 2*VFOV

    point = Point(pX, pY)

    return ((point, x, y, z), distance, dirX, dirY)


def drawTriangle(point1, point2, point3, id):

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

    Vector = Line(gravityCenter, normalVector)

    Triangle = Polygon(Vertices)

    faceColor = colors[id]
    faceColor = rgb(faceColor, faceColor, faceColor)

    if renderDebug.get("faces") == True: 
        Triangle.setFill(faceColor)
    if renderDebug.get("faces") == True or renderDebug.get("wireframe") == True: 
        #Triangle.draw(window)
        Triangle.setOutline(faceColor)
    if renderDebug.get("wireframe") == True: 
        Triangle.setOutline('black')
    if renderDebug.get("faceNormals") == True: 
        Vector.setFill("orange")
        Vector.draw(window)
        gravityCenter.draw(window)

    return (Triangle, distance)


def clear():

    for item in window.items[:]:
        item.undraw()


def render():

    clear()

    drawCube()

    origin = Point(0, 0)
    origin = Circle(origin, 3)
    origin.setFill(color_rgb(255, 0, 0))
    origin.draw(window)

    infos = str("(" + str(round(player_x, 3)) + ";" +
                str(round(player_y, 3)) + ";" + str(round(player_z, 3)) + ")")
    posDisplay = Text(Point(0, -window.getWidth()/4), infos)
    posDisplay.draw(window)

    infos = str("(" + str(player_dir_x) + ";" + str(player_dir_y) + ")")
    dirDisplay = Text(Point(0, (-window.getWidth()/4)-30), infos)
    dirDisplay.draw(window)


resetCoords()

while True:

    render()
    update(165)


    '''if keyboard.is_pressed('s'):

        player_x = player_x - (sin(player_dir_x))/360
        player_z = player_z - (cos(player_dir_x))/360

    if keyboard.is_pressed('z'):

        player_x = player_x + (sin(player_dir_x))
        player_z = player_z + (cos(player_dir_x))

    if keyboard.is_pressed('d'):

        player_dir_x += 1

    if keyboard.is_pressed('q'):

        player_dir_x -= 1'''
    
    if keyboard.is_pressed('s'):

        player_x -= 1

    if keyboard.is_pressed('z'):

        player_x += 1

    if keyboard.is_pressed('space'):

        player_y += 1

    if keyboard.is_pressed('shift'):

        player_y -= 1

    if keyboard.is_pressed('d'):

        player_z += 1

    if keyboard.is_pressed('q'):

        player_z -= 1

    if keyboard.is_pressed('left_arrow'):

        player_dir_x += 0.2

    if keyboard.is_pressed('right_arrow'):

        player_dir_x -= 0.2

    if keyboard.is_pressed('up_arrow'):

        player_dir_y -= 0.2

    if keyboard.is_pressed('down_arrow'):

        player_dir_y += 0.2

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

    if player_dir_x < 0:

        player_dir_x = player_dir_x + 360

    if player_dir_x > 360:

        player_dir_x = player_dir_x - 360

    if keyboard.is_pressed('esc'):

        window.close()
