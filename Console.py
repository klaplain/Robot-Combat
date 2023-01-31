#Thiss piece of code runs on a PC to make it easier for the Match administrator

from tkinter import *
from tkinter.ttk import Label

from ast import keyword
from email import message
import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
import string

mqtt_server = "192.168.4.1"
#mqtt_server = "192.168.0.60"
#mqtt_server = "10.255.128.68"
#mqtt_server = "127.0.0.1"

MQTT_client_ID = "robotcombat_console"

# Our "on MQTT message" event
def messageFunction (client, userdata, message):
    topic = str(message.topic)
    message = str(message.payload.decode("utf-8"))
    if(topic == "timercounter"):
        countdownlabel.config(text=matchtimestr(int(message)))
    if(topic == "blue_status"):
        bluestatuslabel.config(text=message,font=("Tahoma Bold",40),foreground="green")
    if(topic == "red_status"):
        redstatuslabel.config(text=message,font=("Tahoma Bold",40),foreground="green")
#convert seconds to mins:secs
def matchtimestr(countnow):
    counter_mins= int(countnow/60)
    counter_secs = countnow %60
    return "%d:%02d" % (counter_mins,counter_secs)

# update screen functions
def updateredname():
    rednamelabel.config(text=rednameentry.get())
    ourClient.publish("RedName",rednameentry.get())
    
def updatebluename():
    bluenamelabel.config(text=bluenameentry.get())
    ourClient.publish("BlueName",bluenameentry.get())

def updatemaxtime():
    ourClient.publish("TimeMax",timeentry.get())
    countdownlabel.config(text=matchtimestr(int(timeentry.get())))

def statusupdate():
    bluestatuslabel.config(text=combat_match["blue_status"],font=("Tahoma Bold",40),foreground="green")
    redstatuslabel.config(text=combat_match["red_status"],font=("Tahoma Bold",40),foreground="green")
    ourClient.publish("blue_status",combat_match["blue_status"])
    ourClient.publish("red_status",combat_match["red_status"])

def update_clock():
    root.after(1000, update_clock)

def matchstart():
    ourClient.publish("Console","Start")
  
def matchpause():
    ourClient.publish("Console","Pause")

def matchreset():
    ourClient.publish("TimeMax",timeentry.get())
    ourClient.publish("Console","Reset")
    rednamelabel.config(text="********")
    bluenamelabel.config(text="********")
         
root = Tk()
root.title('Combat Robotics Match Control')

#mirror sub frame contains a replica of the big display screen
mirrorsubframe = LabelFrame(root, width=1920,height=300,text="Display",padx=10,pady=10)
mirrorsubframe.pack(padx=10,pady=10)
countdownlabel=Label(mirrorsubframe,text="_____",font=("Tahoma Bold",180))
countdownlabel.grid(row=0,column=0,columnspan=  3)
rednamelabel=Label(mirrorsubframe,text="Red Robot",font=("Tahoma Bold",80),foreground="white",background="red")
rednamelabel.grid(row=1,column=0,padx=50)
bluenamelabel=Label(mirrorsubframe,text="Blue Robot",font=("Tahoma Bold",80),foreground="white",background="blue")
bluenamelabel.grid(row=1,column=2,padx=50)
redstatuslabel=Label(mirrorsubframe,text="Waiting",font=("Tahoma Bold",40),foreground="green")
redstatuslabel.grid(row=2,column=0,padx=50)
bluestatuslabel=Label(mirrorsubframe,text="Waiting",font=("Tahoma Bold",40),foreground="green")
bluestatuslabel.grid(row=2,column=2,padx=50)

#controlsubfrane contains the button that RESETs, PAUSEs or STARTs a match
controlsubframe = LabelFrame(root, width=1920,height=300,text="Control",padx=10,pady=10)
controlsubframe.pack(padx=20,pady=20)
resetbutton =Button(controlsubframe,text="Reset",font=("Tahoma Bold",23),command=matchreset).grid(row=0,column=0, padx=50)
pausebutton =Button(controlsubframe,text="Pause",font=("Tahoma Bold",23),command=matchpause).grid(row=0,column=1,padx=50)
startbutton =Button(controlsubframe,text="Start",font=("Tahoma Bold",23),command=matchstart).grid(row=0,column=2,padx=50)

inputsubframe = LabelFrame(root, width=1920,height=300,text="Robot Name",padx=10,pady=10)
inputsubframe.pack(padx=10,pady=10)

#inputsubframe is where robot names are entered
rednameentry=Entry(inputsubframe, width=20)
rednameentry.grid(row=1,column=0)
rednameentry.insert(0,"**********")

spaceentry=Label(inputsubframe, text="                   ")  # Just to space out the display
spaceentry.grid(row=1,column=3)

bluenameentry=Entry(inputsubframe, width=20)
bluenameentry.grid(row=1,column=4)
bluenameentry.insert(0,"**********")
rednamebutton =Button(inputsubframe,text="OK",command=updateredname).grid(row=1, column=2)
bluenamebutton =Button(inputsubframe,text="OK",command=updatebluename).grid(row=1, column=5)

#timeinputsubframe is where the competion time is entered
timeinputsubframe = LabelFrame(root, width=1920,height=300,text="Time Load (secs)",padx=10,pady=10)
timeinputsubframe.pack(padx=10,pady=10)

timeentry=Entry(timeinputsubframe,width=4)
timeentry.grid(row=0,column=0)
timeentry.insert(0,180)
# timebutton =Button(timeinputsubframe,text="OK",command=updatemaxtime).grid(row=0, column=1)

#This button is how you quit the app
bQuit = Button(root, text="Quit",command=root.quit)
bQuit.pack(pady=20)

#Initialize our MQTT connection and subscriptions
ourClient = mqtt.Client(MQTT_client_ID) # Create a MQTT client object
print("Attempting MQTT connection", mqtt_server, MQTT_client_ID)
ourClient.connect(mqtt_server, 1883) # Connect to the test MQTT broker
print("connected")
ourClient.on_message = messageFunction # Attach the messageFunction to subscription
ourClient.subscribe("timercounter")
ourClient.subscribe("blue_status")
ourClient.subscribe("red_status")

ourClient.loop_start() # Start the MQTT client

#publish initial values
ourClient.publish("TimeMax",timeentry.get())

update_clock()
root.mainloop()


