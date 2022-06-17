#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
import dbus.mainloop.glib
from gi.repository import GObject as gobject
from optparse import OptionParser
import math
import time

robot  = "thymio-II" 

VERBOOSE = 0
VERBOOSEMAIN = 1

TIME_STEP = 0.5

integrity = 100.0
energy = 100.0
integument  = 100.0

diametre = 110.0
ray = 55.0
thymio_degree = (2*math.pi * ray)/5 #### A CHECKER

cst = 0 #50 de base
grey = 9.0 #40 ou 140, depend de la lumi
black = 0.0 #40 ou 140, depend de la lumi
white = 24.0 #40 ou 140, depend de la lumi

proxSensorsVal=[0,0,0,0,0]

proxHisto=[0,0,0,0,0]
groundSensor=[0,0]

def Braitenberg():
    if VERBOOSE:
        print("Braitenberg START")
  

    #Parameters of the Braitenberg, to give weight to each wheels
    leftWheel=[0.01,0.005,-0.0001,-0.006,-0.015]
    rightWheel=[-0.012,-0.007,0.0002,0.0055,0.011]

    #Braitenberg algorithm
    wheel = [0.0, 0.0]
    for i in range(5):
         wheel[0]=wheel[0]+(proxSensorsVal[i]*leftWheel[i])
         wheel[1]=wheel[1]+(proxSensorsVal[i]*rightWheel[i])

    #print in terminal the values that is sent to each motor
    if VERBOOSE:
        print(wheel[0],wheel[1])
     
    if VERBOOSE:
        print("Braitenberg END")

    return wheel



def MainLoop():
    if VERBOOSEMAIN:
        print("Main loop")
    wheel=[0.0, 0.0]

    #get the values of the sensors
    network.GetVariable(robot, "prox.horizontal",reply_handler=get_variables_reply,error_handler=get_variables_error)
    network.GetVariable(robot, "prox.ground.ambiant",reply_handler=get_variables_reply2,error_handler=get_variables_error)

    #print the proximity sensors value in the terminal
    if VERBOOSEMAIN:
        print(proxHisto[0],proxHisto[1],proxHisto[2],proxHisto[3],proxHisto[4])
        print(proxSensorsVal[0],proxSensorsVal[1],proxSensorsVal[2],proxSensorsVal[3],proxSensorsVal[4])
        print(groundSensor[0],groundSensor[1])

    
        wheel=Braitenberg()
            

       #print(hasCircularDamage())
        #add a constant speed to each wheels so the robot moves always forward
        wheel[0]=wheel[0]+cst
        wheel[1]=wheel[1]+cst


        #send motor value to the robot
        network.SetVariable(robot, "motor.left.target", [wheel[0]])
        network.SetVariable(robot, "motor.right.target", [wheel[1]])
    else:
        #send motor value to the robot
        network.SetVariable(robot, "motor.left.target", [0])
        network.SetVariable(robot, "motor.right.target", [0])    

    return True


def get_variables_reply(r):
    global proxSensorsVal
    proxSensorsVal=r

def get_variables_reply2(r):
    global groundSensor
    groundSensor=r

def get_variables_error(e):
    print('error:')
    print(str(e))
    loop.quit()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--system", action="store_true", dest="system", default=False,help="use the system bus instead of the session bus")

    (options, args) = parser.parse_args()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    if options.system:
        bus = dbus.SystemBus()
    else:
        bus = dbus.SessionBus()

    #Create Aseba network 
    network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')

    #print in the terminal the name of each Aseba NOde
    print(network.GetNodesList())

    #GObject loop
    print('starting loop')
    loop = gobject.MainLoop()
    #call the callback of Braitenberg algorithm
    handle = gobject.timeout_add (100, MainLoop) #every 0.5 sec
    loop.run()
