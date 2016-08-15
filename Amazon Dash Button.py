#============================================================================
#                                ---Notes---
# Author:    Jonathan Bennett
# Date:      8/15/2016
# Version:   1.3
#
# Files:    1.) Amazon Dash Button.py
#           2.) Config.py
#
#
# Requirements:
# ---------------------------------------------------------------------------
#
# 1.)   You must disable the need for a root password
#       via the terminal prior to using
#
# 2.)   Config.py must be located in the same directory as this file
#
#
#============================================================================


#To Do List
#
# 1. Make a subroutine to generate and process URLs instead of having them hardcoded (Note: It must account for dimmable vs non-dimmable light commands in the URL it generates (Ex. bedside lamps can't dim))
# 2. Alexa
# 3. Push notifications (enabled, just need to be added for each action and enable them to be turned on / off 
# 4. Write variable (settings) changes to the Config.py file so they remain static
# 5. Implement error handling
# 6. Add dictionary for node status instead of current global boolean variables






####################################################################################
####################################################################################
######################   Imports & Global Variables   ##############################
####################################################################################
####################################################################################



import os,glob,subprocess,errno,sys, time
import xml.etree.ElementTree as ET #WARNING: Module is not secure against maliciously constructed XML data. 
import urllib.request #urllib.request for Python3 used in place of urllib2 (it's old Python2 name)
import json,http.client #for "Get Pushed" app that handles iOS Push Notifications 
import requests



#CONFIGURATION FILE
#====================
from Config import * #imports the Config.py file saved in the same directory



#GLOBAL VARIABLES
#====================
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

    global networkInterface #Allows access to the global variable listed

    #Clears the list variable to ensure it contains no entries
    del allDevices[:]


    # Execute arp command to find all currently known devices
    proc = subprocess.Popen('sudo arp-scan --interface=' + networkInterface + ' --localnet | grep "incomplet" -i -v', shell=True, stdout=subprocess.PIPE)
    

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
        #print("\"", currentMAC[1], "\"", "Button was pressed -- 1st occurence within 5 seconds. I will perform an action now.")
        startTime = time.time() #The last time the ARP was found
        time.clock()
        elapsedSeconds = 0


        #print("Current MAC is:", currentMAC[0])

        turnLivingRoomLampsOn(); #Turns on the living room light

        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network
        

    else: #Performs the below if this is not the first time the MAC address was detected within five seconds
        #print("\"", currentMAC[1], "\"", "Button was pressed -- 2nd occurence within 5 seconds. I'm ignoring this button press.")
        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network

    #Clears ARP Table Cache and finds network devices once more for safety
    clearARPCache(myDashButtons); #Clears the ARP Table Cache
    findNetworkDevices( allDevices ); #Finds all devices on network


    return() #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def secondButtonPressed(startTime, elapsedSeconds, myDashButtons, device, allDevices, currentMAC):


    if startTime == 0.0:
        #print("\"", currentMAC[1], "\"", "Button was pressed -- 1st occurence within 5 seconds. I will perform an action now.")
        startTime = time.time() #The last time the ARP was found
        time.clock()
        elapsedSeconds = 0


        #print("Current MAC is:", currentMAC[0])

        turnBedsideLampsOn(); #Turns on the living room light

        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network
        

    else: #Performs the below if this is not the first time the MAC address was detected within five seconds
        #print("\"", currentMAC[1], "\"", "Button was pressed -- 2nd occurence within 5 seconds. I'm ignoring this button press.")
        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network

    #Clears ARP Table Cache and finds network devices once more for safety
    clearARPCache(myDashButtons); #Clears the ARP Table Cache
    findNetworkDevices( allDevices ); #Finds all devices on network


    return() #exits the function




#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def allLightsButtonPressed(startTime, elapsedSeconds, myDashButtons, device, allDevices, currentMAC):


    if startTime == 0.0:
        #print("\"", currentMAC[1], "\"", "Button was pressed -- 1st occurence within 5 seconds. I will perform an action now.")
        startTime = time.time() #The last time the ARP was found
        time.clock()
        elapsedSeconds = 0


        #print("Current MAC is:", currentMAC[0])

        turnOnOffAllLights(); #Turns on the living room light
        


        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network
        

    else: #Performs the below if this is not the first time the MAC address was detected within five seconds
        #print("\"", currentMAC[1], "\"", "Button was pressed -- 2nd occurence within 5 seconds. I'm ignoring this button press.")
        while elapsedSeconds < 6:
            time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds we selected to ignore duplicate detections during
            elapsedSeconds = time.time() - startTime
            clearARPCache(myDashButtons); #Clears the ARP Table Cache
            findNetworkDevices( allDevices ); #Finds all devices on network

    #Clears ARP Table Cache and finds network devices once more for safety
    clearARPCache(myDashButtons); #Clears the ARP Table Cache
    findNetworkDevices( allDevices ); #Finds all devicpython gui tutoriales on network


    return() #exits the function








#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



def turnLivingRoomLampsOn():

    #Note: More detail on these types of luup requests can be found at:
    #http://wiki.micasaverde.com/index.php/Luup_Requests


    global LivingRoomLampsStatus #Grants the function access to the global variable stored in the Config.py file

    getZWaveNodeStatus('LivingRoomLightsNode', False, False); #Updates the global variable for the node's status but suppresses printing to the terminal

    if LivingRoomLampsStatus == False:
        #Turn on light
        file = urllib.request.urlopen('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=' +
                                      str(zWaveNetworkNodes.get('LivingRoomLightsNode')) +
                                      '&serviceId=urn%3Aupnp-org%3AserviceId%3ADimming1&action=SetLoadLevelTarget&newLoadlevelTarget=100')
        data = file.read()
        file.close()   
    else:
        #Turn off light
        file = urllib.request.urlopen('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=' +
                                      str(zWaveNetworkNodes.get('LivingRoomLightsNode')) +
                                      '&serviceId=urn%3Aupnp-org%3AserviceId%3ADimming1&action=SetLoadLevelTarget&newLoadlevelTarget=0')
        data = file.read()
        file.close()


    getZWaveNodeStatus('LivingRoomLightsNode', True, True); #Updates the global variable for the node's status and prints to the terminal

        
    return() #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def turnBedsideLampsOn():

    #Note: More detail on these types of luup requests can be found at:
    #http://wiki.micasaverde.com/index.php/Luup_Requests


    global BedsideLampsStatus #Grants the function access to the global variable stored in the Config.py file


    if BedsideLampsStatus == False:
        #Turn on light
        file = urllib.request.urlopen('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=3&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=100')
        data = file.read()
        file.close()
        BedsideLampsStatus = True
    else:
        #Turn off light
        file = urllib.request.urlopen('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=3&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=0')
        data = file.read()
        file.close()
        BedsideLampsStatus = False

        
    return() #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def turnOnOffAllLights():

    #Note: More detail on these types of luup requests can be found at:
    #http://wiki.micasaverde.com/index.php/Luup_Requests


    global allLightsAreOnBool #Grants the function access to the global variable stored in the Config.py file
    global LivingRoomLampsStatus #Grants the function access to the global variable stored in the Config.py file
    global BedsideLampsStatus #Grants the function access to the global variable stored in the Config.py file

    #print("turnOnOffAllLights")

    #print("On Function Start: allLightsAreOnBool =", allLightsAreOnBool)

    if allLightsAreOnBool == False:
        if LivingRoomLampsStatus == False:
            #Turn on light
            file = urllib.request.urlopen('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=8&serviceId=urn%3Aupnp-org%3AserviceId%3ADimming1&action=SetLoadLevelTarget&newLoadlevelTarget=100')
            data = file.read()
            file.close()
            LivingRoomLampsStatus = True
            file = urllib.request.urlopen('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=3&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=100')
            data = file.read()
            file.close()
            BedsideLampsStatus = True
            allLightsAreOnBool = True
        else:
            #Turn off light
            file = urllib.request.urlopen('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=8&serviceId=urn%3Aupnp-org%3AserviceId%3ADimming1&action=SetLoadLevelTarget&newLoadlevelTarget=0')
            data = file.read()
            file.close()
            LivingRoomLampsStatus = False
            file = urllib.request.urlopen('http://192.168.1.145:3480/data_request?id=action&output_format=xml&DeviceNum=3&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=0')
            data = file.read()
            file.close()
            BedsideLampsStatus = False
            allLightsAreOnBool = False

        
    return() #exits the function





#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def getZWaveNodeStatus(deviceNumber, printCurrentNodeStatus,delayStatusCheck):

    #This subroutine gets the current status (On or Off) of the specified device and its dimmer level


    #Pauses, if requested, before polling the node for its status
    if delayStatusCheck == True:
        
        time.sleep(ignoreForXSeconds)  #Pauses for the number of seconds designated in Config.py file



    global LivingRoomLampsStatus #Grants the function access to the global variable stored in the Config.py file
    global BedsideLampsStatus
    global allLightsAreOnBool
    
    

    baseUrl = ('http://192.168.1.145:3480/data_request?id=status&output_format=xml&DeviceNum=' + str(zWaveNetworkNodes.get(deviceNumber)))#The URL for the node's status page in XML format
    resp = requests.get(baseUrl)
    msg = resp.content
    root = ET.fromstring(msg)


    currentIteration = 0 #Integer for iteration counter
    
    for state in root.iter('state'): #Loops through each leaf in the XML tree for the "states" branch
        leafDict = (state.attrib) #allows access to the attributes of the state tags
        
        if currentIteration == 0: #Change the integer of the iteration number you're looking for to return a record lower in the tree's hierarchy
            
            if int(leafDict.get('value')) == 0: #Changes the global variable to reflect the node's current boolean status
                LivingRoomLampsStatus = False
            else:
                LivingRoomLampsStatus = True
        currentIteration = currentIteration + 1 #Increases the iteration counter by 1



    if printCurrentNodeStatus == True: #Only prints the node status if the printCurrentNodeStatus boolean value is True

        if LivingRoomLampsStatus == True:
            nodeStatusString = "On"
        else:
            nodeStatusString = "Off"

                
        print("The node is:", nodeStatusString) #Prints the status of the current node



    return() #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def sendiOSPushNotification(pushMessage, deviceNumber): #(deviceNumber) pass this in as a parameter later

    #This subroutine gets the current status (On or Off) of the specified device and its dimmer level

    connection = http.client.HTTPSConnection('api.pushed.co', 443)
    connection.connect()
    connection.request('POST', '/1/push', json.dumps({ "app_key": "d2SppjFIuWjNElusvS4Z",
                                                       "app_secret": "xeMapROJb3C2j8P1p67eUYdDuEWhRU6inYiIPZ1Xg9gcjqDNgunWOP4ABRieiQBg",
                                                       "target_type": "app",
                                                       "content": "Living room lights turned on @ 12:22 AM"}), #The message goes here
                                                       { "Content-Type": "application/json" } )
    str_response = connection.getresponse().read().decode('utf-8')
    result = json.loads(str_response)
    #print(result) #Commented out to suppress printing of the confirmation message    

    return() #exits the function



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def selectNetworkAdapter():

    #This function allows the user to select the network adapter to use to monitor the network


    global networkInterface #Allows access to the global variable listed


#1.) Alerts the user that an attempt will be made to auto-select the network adapter
    print("\nAttempting to auto-select the network adapter...\n")

    
#2.) List all network devices
    proc = subprocess.Popen('ifconfig', shell=True, stdout=subprocess.PIPE) #runs the ifconfig command in the terminal
    
    # Wait for subprocess to exit
    proc.wait()



    iterationCount = 0 #counts the # of the current loop iteration
    for line in proc.stdout: #loops through each line in the terminal output

        item = line.split()#splits each word of the current line (space delimited) into a list

        if iterationCount == 0: #The network adapter should be the first item so automatically saves it
            networkInterface = bytes.decode(item[iterationCount])
            print("The default network adapter is:", networkInterface)

        iterationCount = iterationCount + 1 #moves the iteration counter up by one



#################################################################################################################################################
#################################################################################################################################################
###############################################      END FUNCTION DEFINITIONS       #############################################################
#################################################################################################################################################
#################################################################################################################################################







#main()

#(1.) Sets the default networka adapter and greets the user and provide exit instructions

selectNetworkAdapter(); #sets the default network adapter
print("\nListening for network activity...\n") #Tells the user the program is running
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












