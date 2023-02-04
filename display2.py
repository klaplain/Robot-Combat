# This code runs on the raspberry pi connected to the display screen
# It requires an MQTT Server runing (set in the code here as 192.168.0.60)
# This python must be run from the display console itself i.e. one needs to have a keyboard and mouse connected to this raspberry pi

#this python program is run at boot time and is started from the .bashrc file

from tkinter import *
from tkinter.ttk import Label
import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
# import RPi.GPIO as GPIO

mqtt_server = "192.168.4.1"
#mqtt_server = "192.168.0.60"
#mqtt_server = "10.255.128.68"
#mqtt_server = "127.0.0.1"

MQTT_client_ID = "robotcombat_display"

# **************************************************************
#
# Data elements & variables
#
# **************************************************************

blue_robot_name ="**********"
red_robot_name ="**********"
blue_status = "Waiting"
red_status = "Waiting"
countdownclockstr = "0:00"
matchStatus = "Waiting"
maxtime = 180 #secs
timercounter = maxtime
tenthsecondcounter = 0
solenoidtime = 20

#define port for solenoid trap door
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(7, GPIO.OUT)
# GPIO.output(7,False)

# **************************************************************
#
# MQTT set up
#
# **************************************************************

# Our "on message" event - This is the call back function that is called whenever an MQTT message is received
def messageFunction (client, userdata, message):
    global blue_robot_name
    global red_robot_name
    global blue_status
    global red_status
    global countdownclockstr
    global matchStatus
    global timercounter
    global maxtime

    this_topic =message.topic
    this_message = str(message.payload.decode("utf-8"))

    # Blue Button Pressed
    if(this_topic == "DBB" and this_message == "pressed"):
        if(matchStatus == "Waiting"):
            blue_status = "Ready"
            if(red_status  == "Ready"):
                matchStatus = "Ready"
        elif(matchStatus == "Fighting"):
            blue_status = "Tapped Out"
            matchStatus = "Finished"
        ourClient.publish("blue_status",blue_status)    
        
    # Red Button Pressed
    if(this_topic == "DBR" and this_message == "pressed"):
        if(matchStatus == "Waiting"):
            red_status = "Ready"
            if(blue_status  == "Ready"):
                matchStatus = "Ready"
        elif(matchStatus == "Fighting"):
            red_status = "Tapped Out"
            matchStatus = "Finished"
        ourClient.publish("red_status",red_status) 

    # Blue Name Updated
    if(this_topic == "BlueName"):
        blue_robot_name=this_message

    # Red Name Updated
    if(this_topic == "RedName"):
        red_robot_name = this_message

    # Timer Max in secs
    if(this_topic == "TimeMax"):
        if(matchStatus == "Waiting"):
            maxtime = int(this_message)
            timercounter = maxtime
        ourClient.publish("timercounter",str(timercounter))

    #Console Button pressed
    if(this_topic == "Console"):                    
       
        # Start Button
        if(this_message == "Start"):
            if(matchStatus == "Ready"):
                matchStatus="Fighting"
                timercounter=maxtime

        # Reset Button 
        if(this_message == "Reset"):
            matchStatus="Waiting"
            blue_status="Waiting"
            red_status="Waiting"
            blue_robot_name ="**********"
            red_robot_name ="**********"
            timercounter = maxtime
            ourClient.publish("timercounter",str(int(timercounter)))
            ourClient.publish("blue_status",blue_status)
            ourClient.publish("red_status",red_status)
            # decrementtimercounter()

        # Pause Button 
        if(this_message == "Pause"):
            if(matchStatus == "Fighting"):
                matchStatus = "Pause"
            elif(matchStatus == "Pause"):
                matchStatus = "Fighting"

def matchtimestr(countnow):
    counter_mins= int(countnow/60)
    counter_secs = countnow %60
    return "%d:%02d" % (counter_mins,counter_secs)

def decrementtimercounter():
    global timercounter, matchStatus, blue_status, red_status, tenthsecondcounter,solenoidtime
    tenthsecondcounter=tenthsecondcounter+1
    if(tenthsecondcounter % 10 == 0):
        timercounter=timercounter-1       
        ourClient.publish("timercounter",str(int(timercounter)))
        if(timercounter==0):
            matchStatus = "Finished"
            blue_status = "Finished"
            red_status = "Finished"
            ourClient.publish("blue_status",blue_status)
            ourClient.publish("red_status",red_status)
        if(timercounter == solenoidtime):
            ourClient.publish("solenoid_status","energize")
            # GPIO.output(7,True)
        elif(timercounter == solenoidtime-1):
            ourClient.publish("solenoid_status","de-energize")

    return 


ourClient = mqtt.Client(MQTT_client_ID) # Create a MQTT client object
print("Attempting MQTT connection", mqtt_server, MQTT_client_ID)
ourClient.connect(mqtt_server, 1883) # Connect to the test MQTT broker
print("connected")
ourClient.on_message = messageFunction # Attach the messageFunction to subscription
ourClient.loop_start() # Start the MQTT client

ourClient.subscribe("DBB")
ourClient.subscribe("DBR")
ourClient.subscribe("BlueName")
ourClient.subscribe("RedName")
ourClient.subscribe("Console")
ourClient.subscribe("TimeMax")

ourClient.publish("timercounter",str(timercounter))
ourClient.publish("blue_status",blue_status)
ourClient.publish("red_status",red_status) 
ourClient.publish("solenoid_status","de-energize")

# **************************************************************
#
# clock set up to ensure display updates every 100 ticks
#
# **************************************************************

def update_clock():
    global blue_robot_name
    global red_robot_name
    global blue_status
    global red_status
    global matchStatus
    global maxtime
    if(matchStatus == "Fighting"):
        decrementtimercounter()  #decrement clock 
   
    lab.config(text=matchtimestr(timercounter)) #update clock on display
    blue_name.config(text=blue_robot_name)
    red_name.config(text=red_robot_name)
    bluestatuslabel.config(text=blue_status)
    redstatuslabel.config(text=red_status)
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

