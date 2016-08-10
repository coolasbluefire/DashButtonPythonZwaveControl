#=====================================================================
#                             ---Notes---
# Author:    Jonathan Bennett
# Date:      8/7/2016
# Version:   0.9
#
#
# Requirements:
# -------------------------------------------------------
#
# 1.)    You must disable the need for a root password
#        via the terminal prior to using
#
#
#=====================================================================



####################################################################################
####################################################################################
######################   Imports & Global Variables   ##############################
####################################################################################
####################################################################################


#!/usr/bin/env python
import os,glob,subprocess,errno,sys, time
import webbrowser
from Config import * #imports the Config.py file saved in the same directory
# Enter device MAC addresses (lowercase) to watch
present_files = []
allDevices = []
device = {}
startTime = 0.0 #The last time the ARP was found
elapsedSeconds = 0 #Elapsed time




 
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################





#################################################################################################################################################
#################################################################################################################################################
###############################################       FUNCTION DEFINITIONS       ################################################################
#################################################################################################################################################
#################################################################################################################################################




# Find devices connected to the network via the ARP table and send the ARP table to a list variable
def findNetworkDevices( allDevices ):

    #Clears the list variable to ensure it contains no entries
    del allDevices[:]


    # Execute arp command to find all currently known devices
    proc = subprocess.Popen('sudo arp-scan --interface=enp0s3 --localnet | grep "incomplet" -i -v', shell=True, stdout=subprocess.PIPE)
    # Wait for subprocess to exit
    proc.wait()

    # Build array of dictionary entries for all devices found
    for line in proc.stdout:

        item = line.split()

        currentLinePrefix = line[:3] #Creates a variable to check for "192" in the first three characters

        try:
            currentLinePrefix = int(currentLinePrefix)
        except:
            currentLinePrefix = 0
            pass


        if currentLinePrefix == 192: #only adds the current line to the array if it is an IP address (looks for 192 in the first 3 characters)
            device['IP'] = bytes.decode(item[0])
            device['MAC'] = bytes.decode(item[1])
            device['Name'] = bytes.decode(item[2])
            allDevices.append(device.copy())

            #---===Debugging===---
            #print("Item: ", item)
            #print("IP: ", item[0])
            #print("MAC: ", item[1])
            #print("Name: ", item[2])

            #!!!!!!!!!DEBUGGING!!!!!!!!!
            #print(allDevices)

    
    return #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



def clearARPCache(myDashButtons): #Clears the ARP Table's cache

    for iteration in range(0,6): #loops 5 times
        for currentMAC in myDashButtons.items():
            for device in allDevices:
                #print("I'm delting IP Address: " + device.get('IP'))
                proc = subprocess.Popen('sudo arp -d' + device.get('IP'), shell=True, stdout=subprocess.PIPE)
                proc.wait() #Wait for subprocess to exit


   #print("I'm deleting IP Addresses 192.168.1.0 - 192.168.1.255")

    #Iterates from 0 to 255 (the number of IP addresses in subdomain)
    #for num in range (0,256):
        #print("I'm deleting IP Address: 192.168.1.",num)
        #proc = subprocess.Popen('sudo arp -d 192.168.1.', num, shell=True, stdout=subprocess.PIPE)


    return #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def detectButtonPresses(startTime, elapsedSeconds, myDashButtons, device, allDevices): #Detects button presses and performs the desired action. Duplicate ARP requests within X seconds are ignored.


    # Iterate once for each item in the myDashButtons list
    for currentMAC in myDashButtons.items():
        for device in allDevices:

            
            #----Uncomment these lines to unsupress printing
            #----the details of the devices found on the network
            #print(device.get('MAC'), " - ",
                  #device.get('IP'), " - ",
                  #device.get('Name'))


            if device.get('MAC') == '44:65:0d:20:49:85':
                firstButtonPressed(startTime, elapsedSeconds, myDashButtons, device, allDevices, currentMAC); #The first button in the myDashButtons list was pressed
                
            if device.get('MAC') == '44:65:0d:a4:6c:49':
                secondButtonPressed(startTime, elapsedSeconds, myDashButtons, device, allDevices, currentMAC); #The second button in the myDashButtons list was pressed

            if device.get('MAC') == 'f0:27:2d:b3:86:54':
                allLightsButtonPressed(startTime, elapsedSeconds, myDashButtons, device, allDevices, currentMAC); #The button to turn on/off all lights was pressed

    return #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def firstButtonPressed(startTime, elapsedSeconds, myDashButtons, device, allDevices, currentMAC):


    if startTime == 0.0:
        print("\"", currentMAC[1], "\"", "Button was pressed -- 1st occurence within 5 seconds. I will perform an action now.")
        startTime = time.time() #The last time the ARP was found
        time.clock()
        elapsedSeconds = 0


        print("Current MAC is:", currentMAC[0])

        turnLivingRoomLampsOn(); #Turns on the living room light
        
        print("Back From Function Call: LivingRoomLampsStatus =", LivingRoomLampsStatus)


        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network
        

    else: #Performs the below if this is not the first time the MAC address was detected within five seconds
        print("\"", currentMAC[1], "\"", "Button was pressed -- 2nd occurence within 5 seconds. I'm ignoring this button press.")
        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network

    #Clears ARP Table Cache and finds network devices once more for safety
    clearARPCache(myDashButtons); #Clears the ARP Table Cache
    findNetworkDevices( allDevices ); #Finds all devices on network


    print("LivingRoomLampsStatus = ",LivingRoomLampsStatus)


    return() #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def secondButtonPressed(startTime, elapsedSeconds, myDashButtons, device, allDevices, currentMAC):


    if startTime == 0.0:
        print("\"", currentMAC[1], "\"", "Button was pressed -- 1st occurence within 5 seconds. I will perform an action now.")
        startTime = time.time() #The last time the ARP was found
        time.clock()
        elapsedSeconds = 0


        print("Current MAC is:", currentMAC[0])

        turnBedsideLampsOn(); #Turns on the living room light
        
        print("Back From Function Call: BedsideLampsStatus =", BedsideLampsStatus)


        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network
        

    else: #Performs the below if this is not the first time the MAC address was detected within five seconds
        print("\"", currentMAC[1], "\"", "Button was pressed -- 2nd occurence within 5 seconds. I'm ignoring this button press.")
        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network

    #Clears ARP Table Cache and finds network devices once more for safety
    clearARPCache(myDashButtons); #Clears the ARP Table Cache
    findNetworkDevices( allDevices ); #Finds all devices on network


    print("BedsideLampsStatus = ",BedsideLampsStatus)


    return() #exits the function




#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def allLightsButtonPressed(startTime, elapsedSeconds, myDashButtons, device, allDevices, currentMAC):


    if startTime == 0.0:
        print("\"", currentMAC[1], "\"", "Button was pressed -- 1st occurence within 5 seconds. I will perform an action now.")
        startTime = time.time() #The last time the ARP was found
        time.clock()
        elapsedSeconds = 0


        print("Current MAC is:", currentMAC[0])

        turnOnOffAllLights(); #Turns on the living room light
        
        print("Back From Function Call: turnOnOffAllLights =", turnOnOffAllLightsBool)


        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network
        

    else: #Performs the below if this is not the first time the MAC address was detected within five seconds
        print("\"", currentMAC[1], "\"", "Button was pressed -- 2nd occurence within 5 seconds. I'm ignoring this button press.")
        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network

    #Clears ARP Table Cache and finds network devices once more for safety
    clearARPCache(myDashButtons); #Clears the ARP Table Cache
    findNetworkDevices( allDevices ); #Finds all devices on network


    print("turnOnOffAllLightsBool = ",turnOnOffAllLightsBool)


    return() #exits the function








#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



def turnLivingRoomLampsOn():

    #Note: More detail on these types of luup requests can be found at:
    #http://wiki.micasaverde.com/index.php/Luup_Requests


    global LivingRoomLampsStatus


    print("turnLivingRoomLampsOn")

    print("On Function Start: LivingRoomLampsStatus =", LivingRoomLampsStatus)

    if LivingRoomLampsStatus == False:
        #Turn on light
        webbrowser.open('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=8&serviceId=urn%3Aupnp-org%3AserviceId%3ADimming1&action=SetLoadLevelTarget&newLoadlevelTarget=100')
        LivingRoomLampsStatus = True
    else:
        #Turn off light
        webbrowser.open('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=8&serviceId=urn%3Aupnp-org%3AserviceId%3ADimming1&action=SetLoadLevelTarget&newLoadlevelTarget=0')
        
        LivingRoomLampsStatus = False


    print("Before Function Exit: LivingRoomLampsStatus =", LivingRoomLampsStatus)

        
    return() #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def turnBedsideLampsOn():

    #Note: More detail on these types of luup requests can be found at:
    #http://wiki.micasaverde.com/index.php/Luup_Requests


    global BedsideLampsStatus

    print("turnBedsideLampsOn")

    print("On Function Start: BedsideLampsStatus =", BedsideLampsStatus)

    if BedsideLampsStatus == False:
        #Turn on light
        webbrowser.open('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=3&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=100')
        BedsideLampsStatus = True
    else:
        #Turn off light
        webbrowser.open('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=3&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=0')
        
        BedsideLampsStatus = False


    print("Before Function Exit: BedsideLampsStatus =", BedsideLampsStatus)

        
    return() #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def turnOnOffAllLights():

    #Note: More detail on these types of luup requests can be found at:
    #http://wiki.micasaverde.com/index.php/Luup_Requests


    global turnOnOffAllLightsBool
    global LivingRoomLampsStatus
    global BedsideLampsStatus

    print("turnOnOffAllLights")

    print("On Function Start: turnOnOffAllLightsBool =", turnOnOffAllLightsBool)

    if turnOnOffAllLightsBool == False:

        if LivingRoomLampsStatus == False:
            #Turn on light
            webbrowser.open('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=8&serviceId=urn%3Aupnp-org%3AserviceId%3ADimming1&action=SetLoadLevelTarget&newLoadlevelTarget=100')
            LivingRoomLampsStatus = True
            
            webbrowser.open('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=3&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=100')
            BedsideLampsStatus = True

        else:

            #Turn off light
            webbrowser.open('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=8&serviceId=urn%3Aupnp-org%3AserviceId%3ADimming1&action=SetLoadLevelTarget&newLoadlevelTarget=0')
            LivingRoomLampsStatus = False
            
            #Turn off light
            webbrowser.open('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=3&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=0')
            BedsideLampsStatus = False
            
            turnOnOffAllLightsBool = False


    print("Before Function Exit: turnOnOffAllLightsBool =", turnOnOffAllLightsBool)

        
    return() #exits the function






#################################################################################################################################################
#################################################################################################################################################
###############################################      END FUNCTION DEFINITIONS       #############################################################
#################################################################################################################################################
#################################################################################################################################################



#main()

#(1.) Greet the user and provide exit instructions

print("\nThe program is running...\n") #Tells the user the program is running
print("\n[----- To exit this program press Ctrl + C. -----]\n") #Tells the user how to exit the loop



#(2.) Begin loop

try: #Loop until Ctrl + C keypress is detected
    while True: #while True causes the loop to be infinite



#(3.) Find all devices connected to the network
        
        findNetworkDevices( allDevices ); #Populate the "allDevices" list with all devices currently on the network


#(4.) Detect when a button is pressed and perform the desired action
        detectButtonPresses(startTime, elapsedSeconds, myDashButtons, device, allDevices);
        
 


#(5.) Exit the script when Ctrl + C is pressed

except KeyboardInterrupt: # Exit code on detection of Ctrl + C keypress
    print("I detected that Ctrl + C was pressed and am exiting the Python script now...\n")    
    pass #Continues the code onward


sys.exit(proc.returncode) #Exits any open terminal functions
exit() #Exits the python script












