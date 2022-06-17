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

TIME_STEP = 100.0
MAX_SPEED = 4.0
LED_FREQ = 4.0

x=0.0
y=0.0

surv_time = 0.0

integrity = 100.0
energy = 100.0
integument  = 100.0

diametre = 110.0
ray = 55.0
thymio_degree = (2*math.pi * ray)/5 #### A CHECKER

cst = 125 #50 de base
white = 8.0 #40 ou 140, depend de la lumi
grey = 2.0 #40 ou 140, depend de la lumi
black = 0.0 #40 ou 140, depend de la lumi

proxSensorsVal=[0,0,0,0,0]
proxHisto=[0,0,0,0,0]
circDam=[0,0,0,0,0]

speedDam=[0,0,0,0,0]

damage = 0.0
r_pain = 0.0
c_pain = 0.0
c_pain1 = 0.0
c_pain2 = 0.0

well_being = 0.0
r_pleasure = 0.0
c_pleasure = 0.0

groundSensor=[0,0]

file1 = open("res/res.txt","w+")
intro = "surv_time,integument,energy,integrity, \
def_groom,def_food,def_obstacle,cue_groom,cue_food,cue_obstacle, \
mot_groom,mot_food,mot_avoid,wta,damage,c_pain,well_being,c_pleasure \n"
file1.write(intro)



def compute_angular_speed(ps):

	speed = (2*math.pi) # / TIME_SLEEP
    # 2PIr/T
    # (PI/6 * R) / T

def BraitenGroom():

    if VERBOOSE:
        print("BraitenGROOM START")
    #Parameters of the Braitenberg, to give weight to each wheels
    leftWheel=[-0.5,1.0]
    rightWheel=[1.0,0.5]

    gs=[0,0]

    #adapt gs value    
    for i in range(2):
        gs[i] = groundSensor[i]
        if gs[i]>grey:
            gs[i]=0.0
        else :
            gs[i]=(1.0-(gs[i]/grey))
  
    if VERBOOSE:
        print(gs[0],gs[1])

    wheels=[0.0,0.0]
    for i in range(2):
         wheels[0]=wheels[0]+(gs[i]*leftWheel[i])
         wheels[1]=wheels[1]+(gs[i]*rightWheel[i])
    
    if VERBOOSE:
        print(wheels[0],wheels[1])
        print("BraitenGROOM END")

    return wheels

def BraitenFood():

    if VERBOOSE:
        print("BraitenFood START")

    #Parameters of the Braitenberg, to give weight to each wheels
    leftWheel=[-0.5,1.0]
    rightWheel=[1.0,0.5]

    gs=[0,0]

    #adapt gs value    
    for i in range(2):
        gs[i] = groundSensor[i]
        if gs[i]<grey:
            gs[i]=0.0
        elif gs[i]>white:
            gs[i]=1.0
        else :
            gs[i]=((gs[i]-grey)/white)
    
    if VERBOOSE:
        print(gs[0],gs[1])

    wheels=[0.0,0.0]
    for i in range(2):
         wheels[0]=wheels[0]+(gs[i]*leftWheel[i])
         wheels[1]=wheels[1]+(gs[i]*rightWheel[i])
    
    if VERBOOSE:
        print(wheels[0],wheels[1])
        print("BraitenFood END")

    return wheels


def Braitenberg():
    if VERBOOSE:
        print("Braitenberg START")
  

    #Parameters of the Braitenberg, to give weight to each wheels
    leftWheel=[2,1,-1,-1,-2]
    rightWheel=[-2,-1,1,1,2]

    #Braitenberg algorithm
    wheel = [0.0, 0.0]
    for i in range(5):
         wheel[0]=wheel[0]+(proxSensorsVal[i]*leftWheel[i])
         wheel[1]=wheel[1]+(proxSensorsVal[i]*rightWheel[i])

    wheel[0] = wheel[0]/(5*4500)
    wheel[1] = wheel[1]/(5*4500)

    #print in terminal the values that is sent to each motor
    if VERBOOSE:
        print(wheel[0],wheel[1])
     
    if VERBOOSE:
        print("Braitenberg END")

    return wheel


def hasDamage():

    for i in range(5):
        if(proxSensorsVal[i] > 3000):
            return True

    return False

def hasSpeedDamage():
    global speedDam
    for i in range(5):
        dist  = (abs(proxSensorsVal[i]-proxHisto[i]) / 4500.0) * 100
        if dist>0.01:
            speed = dist /  TIME_STEP # cm/ms
            speedDam[i] = (speedDam[i]+speed)/2.0
        else:
            speedDam[i]=0.0
    print(speedDam[0],speedDam[1],speedDam[2],speedDam[3],speedDam[4])



def hasCircularDamage():
    global circDam
    print("circuDamage")
    for i in range(5):
        if(proxHisto[i] > 2500):
            #extreme sensors
            if(i==0):
                if( abs(proxSensorsVal[i+1]-proxHisto[i]) < (proxHisto[i]*0.5)):
                    circDam[i+1] = (proxSensorsVal[i+1]/4500.0)*100.0
            elif(i==4):
                if( abs(proxSensorsVal[i-1]-proxHisto[i]) < (proxHisto[i]*0.5)):
                    circDam[i-1] = (proxSensorsVal[i-1]/4500.0)*100.0
            #other sensors
            else:
                if( abs(proxSensorsVal[i+1]-proxHisto[i]) < (proxHisto[i]*0.5) ):
                    circDam[i+1] = (proxSensorsVal[i+1]/4500.0)*100.0
                if( abs(proxSensorsVal[i-1]-proxHisto[i]) < (proxHisto[i]*0.5) ):
                    circDam[i-1] = (proxSensorsVal[i-1]/4500.0)*100.0

    for i in range(2,5):
        if(abs(circDam[i]-circDam[i-1]) < 0.5*circDam[i]):
            circDam[i]=2*circDam[i]
            circDam[i-1]=2*circDam[i]

    for i in range(5):
        circDam[i] = circDam[i]/1000.0

    print(circDam[0],circDam[1],circDam[2],circDam[3],circDam[4])

    return True



def canEat():
    tmp = BraitenFood()
    if((tmp[0]+tmp[1]) > 1.0):
        global energy
        energy = energy + 15
        eat()
    return True

def canGroom():
    tmp = BraitenGroom()
    #proxSensorsVal[1]
    if((tmp[0]+tmp[1]) > 1.0):
        global integument
        integument = integument + 15
        Groom()
    return True


def eat():
    print("I eat.")
    for j in range(3) :
        network.SetVariable(robot, "motor.left.target", [-100])
        network.SetVariable(robot, "motor.right.target", [-100])
        for i in range (5):
            time.sleep(0.1)
            hasSpeedDamage()
        network.SetVariable(robot, "motor.left.target", [100])
        network.SetVariable(robot, "motor.right.target", [100])
        for i in range (4):
            time.sleep(0.1)
            hasSpeedDamage()
    return True

def Groom():
    print("I groom")
    for j in range(3) :
        network.SetVariable(robot, "motor.left.target", [-100])
        network.SetVariable(robot, "motor.right.target", [100])
        for i in range (5):
            time.sleep(0.1)
            hasCircularDamage()
        network.SetVariable(robot, "motor.left.target", [100])
        network.SetVariable(robot, "motor.right.target", [-100])
        for i in range (4):
            time.sleep(0.1)
            hasCircularDamage()
    return True

def WTA(v1,v2,v3):
    if(v1>v2 and v1>v3):
        return 1
    if(v2>v1 and v2>v3):
        return 2
    if (v3>v1 and v3>v2):
        return 3
    return 4

def MainLoop():
    global file1
    global surv_time
    surv_time = surv_time + 0.1

    if VERBOOSEMAIN:
        print("Main loop")
    wheel=[0.0, 0.0]

    #get the values of the sensors
    global speedDam
    global circDam
    global damage 
    global damage1 
    global damage2 
    global r_pain
    global c_pain1
    global c_pain2
    global well_being 
    global r_pleasure
    global c_pleasure    

    global proxHisto    
    network.GetVariable(robot, "prox.horizontal",reply_handler=get_variables_reply,error_handler=get_variables_error)
    network.GetVariable(robot, "prox.ground.ambiant",reply_handler=get_variables_reply2,error_handler=get_variables_error)

    #decay circular damage
    for i in range(5):
        if(circDam[i]>0.01):
            circDam[i]=0.7*circDam[i]
        else : 
            circDam[i]=0.0


    #print the proximity sensors value in the terminal
    if VERBOOSEMAIN:
        print(proxHisto[0],proxHisto[1],proxHisto[2],proxHisto[3],proxHisto[4])
        print(proxSensorsVal[0],proxSensorsVal[1],proxSensorsVal[2],proxSensorsVal[3],proxSensorsVal[4])
        print(groundSensor[0],groundSensor[1])

    #variables
    global integument
    global energy
    global integrity
    global x
    global y
 


    if VERBOOSEMAIN:
        print("integument ", integument, " energy ", energy, " integrity ", integrity)
    
    if (integrity > 0.0 and integument > 0.0 and energy > 0.0):
        
        #deficit computation
        energy = energy-0.2
        integument = integument-0.05
        if(hasDamage()):
            integrity = integrity - 0.5

        def_groom  = 100.0 - integument
        def_food  = 100.0 - energy
        def_obstacle  = 100.0 - integrity
        if VERBOOSEMAIN:
            print("def_groom ", def_groom, " def_food ", def_food, " def_obstacle ", def_obstacle)



        #Cue computation
        cue_groom = mean(BraitenGroom())
        cue_food = mean(BraitenFood())
        cue_obstacle = ( abs(Braitenberg()[0]) + abs(Braitenberg()[1]))/2.0
        if VERBOOSEMAIN:
            print("cue_groom ", cue_groom, " cue_food ", cue_food, " cue_obstacle ", cue_obstacle)

        #Motivation computation
        mot_groom = def_groom+(def_groom*cue_groom)
        mot_food = def_food+(def_food*cue_food)
        mot_avoid = def_obstacle+(def_obstacle*cue_obstacle) 

        #pain modulation
        mot_avoid = mot_avoid + c_pain * mot_avoid

        if VERBOOSEMAIN:
            print("mot_groom ", mot_groom, " mot_food ", mot_food, " mot_avoid ", mot_avoid)


        #WTA  motivations
        wta = WTA(mot_groom,mot_food,mot_avoid)
        if VERBOOSEMAIN:
            print("WTA  =  ", wta)

        if (wta == 3):
            if(mot_avoid>mot_food):
                print("avoid")
                wheel=Braitenberg()
                for i in range(2):
                    wheel[i]+wheel[i]*200

        elif (wta==2):
            print("food")
            wheel=BraitenGroom()
            for i in range(2):
                wheel[i]+wheel[i]*200
            canEat()

        elif (wta==1):
            print("groom")
            wheel=BraitenGroom()
            for i in range(2):
                 wheel[i]+wheel[i]*200
            canGroom()
        else :
            wheel=[0.0,0.0]
            print("default")
        
        if(cue_obstacle>0.1):
                print("avoid")
                wheel=Braitenberg()
                for i in range(2):
                    wheel[i]+wheel[i]*200



        #damage computation
        hasCircularDamage()
        hasSpeedDamage()
        damage = 0.0
        damage1 = 0.0
        damage2 = 0.0
        for i in range(5):
            damage1 = (damage1 + speedDam[i])
            damage2 = (damage2 + circDam[i])
            damage = (damage + (speedDam[i]+circDam[i])/2.0)
        print("damage1 = ", damage1)
        print("damage2 = ", damage2)
        print("damage = ", damage)


        #pain computation
        print("x=", x)
        print("y=", y)

        if(damage1>0.2):
            #Tau= 2*PI
            c_pain1 = damage1 * (1-math.exp(-x-2*math.pi))
            if(c_pain1>0):
                y=round(-2*math.pi*math.log(c_pain1))
            else:
                y=-5
            x=x+1
        else:
            c_pain1 = damage1 * math.exp(-y+2*math.pi)
            if( (1-c_pain1) > 0):
                x=round(-2*math.pi*math.log(1-c_pain1))
            else:
                x=-5
            y=y+1
        print("pain1 = ", c_pain1)

        if(damage2>0.2):
            #Tau= 2*PI
            c_pain2 = damage2 * (1-math.exp(-x-2*math.pi))
            if(c_pain2>0):
                y=round(-2*math.pi*math.log(c_pain2))
            else:
                y=-5
            x=x+1
        else:
            c_pain2 = damage1 * math.exp(-y+2*math.pi)
            if( (1-c_pain2) > 0):
                x=round(-2*math.pi*math.log(1-c_pain2))
            else:
                x=-5
            y=y+1
        print("pain1 = ", c_pain2)

        c_pain = (c_pain1+c_pain2)/2.0
        print("pain = ", c_pain)


        #pleasure computation
        well_being =  ((100.0 - def_food - def_groom - def_obstacle)/100.0)
        r_pleasure = 0.2 * well_being
        c_pleasure = min(1.0, c_pleasure * 0.8 + r_pleasure )
        c_pleasure = max(0.0, c_pleasure)
        #c_pleasure = 0.0
        print("pleasure = ", c_pleasure)

        #add a constant speed to each wheels so the robot moves always forward
        wheel[0]=wheel[0] + math.copysign(1,wheel[0])*cst
        wheel[1]=wheel[1] + math.copysign(1,wheel[1])*cst
        
        wheel[0]=wheel[0] + c_pain * wheel[0]
        wheel[1]=wheel[1] + c_pain * wheel[1]


        #send motor value to the robot
        network.SetVariable(robot, "motor.left.target", [wheel[0]])
        network.SetVariable(robot, "motor.right.target", [wheel[1]])
        
        #Data write
        str1 = str(surv_time)+ "," + \
            str(integument) + "," + str(energy) + "," + str(integrity) + "," + \
            str(def_groom) + "," + str(def_food) + "," + str(def_obstacle) + "," + \
            str(cue_groom) + "," + str(cue_food) + "," + str(cue_obstacle) + "," + \
            str(mot_groom) + "," + str(mot_food) + "," + str(mot_avoid) + "," + \
            str(wta) + "," + str(damage) + "," + str(c_pain) + "," + str(well_being) + "," + str(c_pleasure) + "\n"
        file1.write(str1)

        proxHisto = proxSensorsVal
    else:
        file1.close()
        #send motor value to the robot
        network.SetVariable(robot, "motor.left.target", [0])
        network.SetVariable(robot, "motor.right.target", [0])    

    return True

def MainTest():

    return True

def mean(cue):
    return (cue[0]+cue[1])/2.0

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
    handle = gobject.timeout_add (TIME_STEP, MainLoop) #every 0.5 sec
    loop.run()
