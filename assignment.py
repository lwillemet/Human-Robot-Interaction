# -*- coding: utf-8 -*-
"""
Control in Human-Robot Interaction Assignment 1: Haptic Rendering
-------------------------------------------------------------------------------
DESCRIPTION:
Creates a simulated haptic device (right) and VR environment (left)

The forces on the virtual haptic device are displayed using pseudo-haptics. The 
code uses the mouse as a reference point to simulate the "position" in the 
user's mind and couples with the virtual haptic device via a spring. the 
dynamics of the haptic device is a pure damper, subjected to perturbations 
from the VR environment. 

IMPORTANT VARIABLES
xc -> x and y coordinates of the center of the haptic device and of the VR
xm -> x and y coordinates of the mouse cursor 
xh -> x and y coordinates of the haptic device (shared between real and virtual panels)
fe -> x and y components of the force fedback to the haptic device from the virtual impedances

TASKS:
1- Implement the impedance control of the haptic device
2- Implement an elastic element in the simulated environment
3- Implement a position dependent potential field that simulates a bump and a hole
4- Implement the collision with a 300x300 square in the bottom right corner 
5- Implement the god-object approach and compute the reaction forces from the wall

REVISIONS:
Initial release MW - 14/01/2021
Added 2 screens and Potential field -  21/01/2021
Added Collision and compressibility (LW, MW) - 25/01/2021
Added Haptic device Robot - TODO

INSTRUCTORS: Michael Wiertlewski & Laurence Willemet & Mostafa Attala
e-mail: {m.wiertlewski,l.willemet,m.a.a.atalla}@tudelft.nl
"""


import pygame
import numpy as np
import math
import matplotlib.pyplot as plt


##################### General Pygame Init #####################
##initialize pygame window
pygame.init()
window = pygame.display.set_mode((1200, 600))   ##twice 600x600 for haptic and VR
pygame.display.set_caption('Virtual Haptic Device')

screenHaptics = pygame.Surface((600,600))
screenVR = pygame.Surface((600,600))

##add nice icon from https://www.flaticon.com/authors/vectors-market
icon = pygame.image.load('robot.png')
pygame.display.set_icon(icon)

##add text on top to debugToggle the timing and forces
font = pygame.font.Font('freesansbold.ttf', 18)

pygame.mouse.set_visible(True)     ##Hide cursor by default. 'm' will toggle it
 
##set up the on-screen debugToggle
text = font.render('Virtual Haptic Device', True, (0, 0, 0),(255, 255, 255))
textRect = text.get_rect()
textRect.topleft = (10, 10)


xc,yc = screenVR.get_rect().center ##center of the screen


##initialize clock
clock = pygame.time.Clock()
FPS = 100

##define some colors
cWhite = (255,255,255)
cDarkblue = (36,90,190)
cLightblue = (0,176,240)
cRed = (255,0,0)
cOrange = (255,100,0)
cYellow = (255,255,0)


##################### Simulation Init #####################

'''*********** Student should fill in ***********'''
####Dynamics parameters, k/b needs to be <1
k = .5       ##Stiffness between cursor and haptic display
b = .8       ##Viscous fieldToggle of the haptic display

####Virtual environment -  Wall
kc = 1.      ##Stiffness between endpoint and the wall
xw = np.array([xc,yc])    ##Actually the top left corner of the wall
fw = np.zeros(2)

####Virtual environment -  Force fieldToggle f(x,y)
##get axis in numpy format
x = np.arange(screenVR.get_rect().left,screenVR.get_rect().right,1)
y = np.arange(screenVR.get_rect().top,screenVR.get_rect().bottom,1)
xx, yy = np.meshgrid(x,y)
sigma = 50

##Compute the height map and the gradient along x and y
heightMap = -np.exp(-(xx-xc-150)**2/(2*sigma**2)) \
                +np.exp(-(xx-xc+150)**2/(2*sigma**2)) ##height as a function of space
dFe = np.gradient(heightMap)                   ##precompute the gradient 
if dFe[1].max():
    dFe = dFe/dFe[1].max()                 ##normalize the gradient

fe = np.zeros(2)
'''*********** !Student should fill in ***********'''


##################### Define sprites #####################

##define sprites
hhandle = pygame.image.load('handle.png')
haptic  = pygame.Rect(*screenHaptics.get_rect().center, 0, 0).inflate(48, 48)
cursor  = pygame.Rect(0, 0, 5, 5)
colorHaptic = cOrange ##color of the wall

xh = np.array(haptic.center)

##Set the old value to 0 to avoid jumps at init
xhold = 0
xmold = 0



'''*********** Student should fill in ***********'''
##Sprites for the VR env
wall    = pygame.Rect(xc, yc, 300, 300)
proxy   = pygame.Rect(*window.get_rect().center, 0, 0).inflate(48, 48)
colorProxy = cOrange

##Sprites for the fieldToggle
surfHeight = pygame.Surface(screenVR.get_size(),pygame.SRCALPHA)  # Creates an empty per-pixel alpha Surface.
surfHeight.fill((255,255,255,150))
surfHeight.lock()
for ii in range(heightMap.shape[0]):
    for jj in range(heightMap.shape[1]):
        pxa= np.round(abs(heightMap[jj,ii])*255)
        surfHeight.set_at((ii,jj),(255,255,255,pxa.astype(np.uint8)))
   
surfHeight.unlock()
'''*********** Student should fill in ***********'''



##################### Main Loop #####################

##Run the main loop
##TODO - Perhaps it needs to be changed by a timer for real-time see: 
##https://www.pygame.org/wiki/ConstantGameSpeed
run = True
ongoingCollision = False
fieldToggle = False
robotToggle = True

debugToggle = False


while run:

    #########Process events  (Mouse, Keyboard etc...)#########
    for event in pygame.event.get():
        ##If the window is close then quit 
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord('m'):   ##Change the visibility of the mouse
                pygame.mouse.set_visible(not pygame.mouse.get_visible())  
            if event.key == ord('q'):   ##Force to quit
                run = False            
            if event.key == ord('d'):
                debugToggle = not debugToggle
            if event.key == ord('r'):
                robotToggle = not robotToggle
            '''*********** Student can add more ***********'''
            if event.key == ord('f'):
                fieldToggle = not fieldToggle
            '''*********** !Student can add more ***********'''


    ##Get mouse position
    cursor.center = pygame.mouse.get_pos()
    
    ######### Main simulation. Everything should  #########
    ##Compute distances and forces between blocks
    xh = np.clip(np.array(haptic.center),0,599)
    xm = np.clip(np.array(cursor.center),0,599)

    
    # ##Compute velocities
    vm = xm - xmold
    vh = xh - xhold
    
    
    '''*********** Student should fill in ***********'''

    ######### Compute forces ########
    ##Viscoelastic forces from the mouse-haptic distance
    fk = k*(xm-xh)             ##Elastic force between mouse and haptic device
    fb = b*vm                  ##Damping of the haptic display

    ##Compute the force produced by the shape
    dFelocal = np.array([dFe[0][xh[1],xh[0]], dFe[1][xh[1],xh[0]]])        ##shitty way to adress the 3d tensor
    if fieldToggle:
        fe = 15*np.flipud(dFelocal)                  
    else:
        fe = np.zeros(2)        ##no potential


    ##Compute reaction from the wall
    if haptic.colliderect(wall):
        
        ##Save the proxy point when the collision is first registered
        if not ongoingCollision:
            xp = xh
            
        ongoingCollision = True      ##flag to find if collision is new

        ##Compute the forces due to the god-object
        if xp[0]-xw[0]<0:       ## horizontal collision
            ##compute wall reaction force 
            fw[0] = kc*(xh[0]-xp[0])
            
            ##display the proxy compressed to the wall
            proxy.height  = haptic.height
            proxy.width = np.clip(np.round(haptic.width*(1-(1/(1+np.exp((xp[0]-xh[0])/20+2.5))))),5,haptic.height)
            proxy.center = (xw[0]-proxy.width/2, xh[1])                    
        
        elif xp[1]-xw[1]<0:     ## vertical collision
            ##compute wall reaction force 
            fw[1] = kc*(xh[1]-xp[1])
            
            ##display the proxy compressed to the wall
            proxy.height = np.clip(np.round(haptic.height*(1-(1/(1+np.exp((xp[1]-xh[1])/20+2.5))))),5,haptic.height)
            proxy.width = haptic.width
            proxy.center = (xh[0], xw[1]-proxy.height/2)   

        else:           ##if no collision despite the detection
            fw[0] = 0
            fw[1] = 0
                    
    else:   ##if no collision 
        ongoingCollision = False   ##flag to find if collision is new
        fw[0] = 0
        fw[1] = 0
        

    ######### Update the positions according to the forces ########
    ##Compute simulation (here there is no inertia)
    dxh = k/b*(xm-xh)-fe/b-fw/b     ##force balance
    '''*********** !Student should fill in ***********'''

    xh = np.round(xh+dxh)  ##update new positon of the end effector
    haptic.center = xh         

    ##Update old samples for velocity computation
    xhold = xh
    xmold = xm


    ######### Update graphical elements #########

    ##Change color based on effort
    colorMaster = (255,\
             255-np.clip(np.linalg.norm(fk)*5,0,255),\
             255-np.clip(np.linalg.norm(fk)*5,0,255)) #if collide else (255, 255, 255)


    ######### Graphical output #########
    ##Render the haptic surface
    screenHaptics.fill(cWhite)
    
    pygame.draw.rect(screenHaptics, colorMaster, haptic,border_radius=4)

    ######### Robot visualization ###################
    # update individual link position
    if robotToggle:
        colorLinks = (150,150,150)
        
        #################### Define Robot #######################
        # ROBOT PARAMETERS
        l = [0.35, 0.45] # links length l1, l2
        window_scale = 400 # conversion from meters to pixels

        xrc = [300,300] ## center location of the robot in pygame
    
        pr = np.array([(xh[0]-xrc[0])/window_scale, -(xh[1]-xrc[1])/window_scale]) ##base is at (0,0) in robot coordinates
        #q = model.IK(pr)
        
        #################### Compute inverse kinematics#######################
        q = np.zeros([2])
        r = np.sqrt(pr[0]**2+pr[1]**2)
        try:
            q[1] = np.pi - math.acos((l[0]**2+l[1]**2-r**2)/(2*l[0]*l[1]))
        except:
            q[1]=0
        
        try:
            q[0] = math.atan2(pr[1],pr[0]) - math.acos((l[0]**2-l[1]**2+r**2)/(2*l[0]*r))
        except:
            q[0]=0
        
        #################### Joint positions #######################

        xr0 =       np.dot(window_scale,[0.0,                      0.0])   #Position of the base
        xr1 = xr0 + np.dot(window_scale,[l[0]*np.cos(q[0]),        l[0]*np.sin(q[0])]) #Position of the first link
        xr2 = xr1 + np.dot(window_scale,[l[1]*np.cos(q[0]+q[1]),   l[1]*np.sin(q[0]+q[1])]) #Position of the second link
        
        #################### Draw the joints and linkages #######################
        pygame.draw.lines (screenHaptics, colorLinks, False,\
                           [(xr0[0] + xrc[0], -xr0[1] + xrc[1]), \
                            (xr1[0] + xrc[0], -xr1[1] + xrc[1])], 15) # draw links
            
        pygame.draw.lines (screenHaptics, colorLinks, False,\
                           [(xr1[0] + xrc[0]      ,-xr1[1] + xrc[1]), \
                            (xr2[0] + xrc[0]      ,-xr2[1] + xrc[1])], 14)
            
        pygame.draw.circle(screenHaptics, (0, 0, 0),\
                           (int(xr0[0]) + xrc[0] ,int(-xr0[1]) + xrc[1]), 15) # draw shoulder / base
        pygame.draw.circle(screenHaptics, (200, 200, 200),\
                           (int(xr0[0]) + xrc[0] ,int(-xr0[1]) + xrc[1]), 6) # draw shoulder / base
        pygame.draw.circle(screenHaptics, (0, 0, 0),\
                           (int(xr1[0]) + xrc[0],int(-xr1[1]) + xrc[1]), 15) # draw elbow
        pygame.draw.circle(screenHaptics, (200, 200, 200),\
                           (int(xr1[0]) + xrc[0],int(-xr1[1]) + xrc[1]), 6) # draw elbow
        pygame.draw.circle(screenHaptics, (255, 0, 0),\
                           (int(xr2[0]) + xrc[0],int(-xr2[1]) + xrc[1]), 5) # draw hand / endpoint
        
    
    ### Hand visualisation
    screenHaptics.blit(hhandle,(haptic.topleft[0],haptic.topleft[1]))
    pygame.draw.line(screenHaptics, (0, 0, 0), (haptic.center),(haptic.center+2*fk))
    
    
    ##Render the VR surface
    screenVR.fill(cLightblue)
    if fieldToggle:
        screenVR.blit(surfHeight,(0,0))
        
    pygame.draw.rect(screenVR,cDarkblue, wall)
    if not ongoingCollision:
        pygame.draw.rect(screenVR, colorHaptic, haptic, border_radius=8)
    else:
        pygame.draw.rect(screenVR, colorProxy, proxy, border_radius=8)

    ##Fuse it back together
    window.blit(screenHaptics, (0,0))
    window.blit(screenVR, (600,0))

    ##Print status in  overlay
    if debugToggle: 
        
        text = font.render("FPS = " + str(round(clock.get_fps())) + \
                            "  xm = " + str(np.round(10*xr1)/10) +\
                            "  xh = " + str(np.round(10*xh)/10) +\
                            "  fk = " + str(np.round(10*fk)/10) +\
                            "  fw = " + str(np.round(10*fw)/10) \
                            , True, (0, 0, 0), (255, 255, 255))
        window.blit(text, textRect)


    pygame.display.flip()    
    ##Slow down the loop to match FPS
    clock.tick(FPS)

pygame.display.quit()
pygame.quit()
