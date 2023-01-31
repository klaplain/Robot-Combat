# This code runs on the raspberry pi connected to the display screen
# It requires an MQTT Server runing (set in the code here as 192.168.0.60)
# This python must be run from the display console itself i.e. one needs to have a keyboard and mouse connected to this raspberry pi

#this python program is run at boot time and is started from the .bashrc file

from tkinter import *
from tkinter.ttk import Label
import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from statemachine import StateMachine, State

class MatchManagerMachine(StateMachine):
    waiting = State('Waiting', initial=True)
    readyToFight = State('Ready To Fight')
    fighting = State('Fighting')
    paused = State('Paused')
    finished = State('Finished')

    bothTappedIn = waiting.to(readyToFight)
    startFight = readyToFight.to(fighting)
    pausing = fighting.to(paused)
    unpausing = paused.to(fighting)
    tappedOut = fighting.to(finished)
    timedOut = fighting.to(finished)
    reset =finished.to(waiting)

class TapButton(StateMachine):
    notTappedIn = State('Not Tapped In', initial= True)
    tappedIn = State('Tapped In')

    tappingIn = notTappedIn.to(tappedIn)
    tappingOut = tappedIn.to(notTappedIn)

# **************************************************************
#
# Data elements & variables
#
# **************************************************************

combat_match = {'countdown':"0:00", 'blue_robot_name': "**********", 'blue_status':"Waiting", 'red_robot_name':"**********",'red_status':"Waiting",'matchststus':"stopped" }

print("TESTTT")
while(True):
        print("")

match_manager = MatchManagerMachine()
blue_button = TapButton()
red_button = TapButton()

fred =""

# **************************************************************
#
# MQTT set up
#
# **************************************************************

# Our "on message" event - This is the call back function that is called whenever an MQTT message is received
def messageFunction (client, userdata, message):
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)
 

ourClient = mqtt.Client("robotcombat_display") # Create a MQTT client object
ourClient.connect("192.168.0.60", 1883) # Connect to the test MQTT broker
#for key, value in combat_match.items():    # subscribe to a
#   ourClient.subscribe(key)


print("attaching callback")
ourClient.on_message = messageFunction # Attach the messageFunction to subscription
print("starting loop")
ourClient.loop_start() # Start the MQTT client
print("Subscribing")
ourClient.subscribe("blue_dome_button",qos=0)

while(True):
        print(fred)

p=0
i=9

# **************************************************************
#
# clock set up to ensure display updates every 100 ticks
#
# **************************************************************

def update_clock():
        lab.config(text=combat_match['countdown'])
        blue_name.config(text=combat_match['blue_robot_name'])
        red_name.config(text=combat_match['red_robot_name'])
        bluestatuslabel.config(text=combat_match['blue_status'])
        redstatuslabel.config(text=combat_match['red_status'])
        root.after(100, update_clock)


# **************************************************************
#
# create display
#
# **************************************************************



root = Tk()
root.overrideredirect(1)
frame = Frame(root, width=1920, height=1290,borderwidth=2,background="black")
frame.pack_propagate(False)
frame.pack()

lab=Label(frame,text="",font=("Arial Bold",255),foreground="white",background="black")
lab.pack()

robotsubframe = LabelFrame(frame, width=1920, height=300,text="",background="black", borderwidth=0)
robotsubframe.pack()
red_name= Label(robotsubframe, text="**********",font=("Arial Bold",110), foreground="white",background="red")
red_name.grid(row=0,column=0,pady=50)

spaceentry=Label(robotsubframe,text="          ",background="black")
spaceentry.grid(row=0,column=1)

blue_name = Label(robotsubframe,text="*********",font=("Arial Bold",110),foreground="white",background="blue")
blue_name.grid(row=0, column=2)

redstatuslabel=Label(robotsubframe,text="xxxx",font=("Arial",40),background="black",foreground="white")
redstatuslabel.grid(row=1,column=0,padx=50)
bluestatuslabel=Label(robotsubframe,text="xxxx",font=("Arial",40),background="black",foreground="white")
bluestatuslabel.grid(row=1,column=2,padx=50)

bQuit = Button(frame, text="Quit",command=root.quit)
bQuit.pack(pady=20)

# **************************************************************
#
# initialize clock
#
# **************************************************************

update_clock()

# **************************************************************
#
# and loop forever
#
# **************************************************************

root.mainloop()
