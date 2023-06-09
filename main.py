'''
Portland State University 
Professor Nirupama Bulusu 
IRC Project Authors: Anadi Shakya(ashakya@pdx.edu), Abhishek Das(adas@pdx.edu)
'''

import socket
import threading 
#returns our localhost on which we will be simulating the network interaction
host = socket.gethostname() 
#this can be arbitrary as long as it is above 40000 as ports below 40000 are reserved
port_number = 59400  

#starting the server
server = socket.socket()
#server is bound to the host on the hardcoded "private" port
server.bind((host, port_number))
#server is active and listening for network communication
server.listen() 

#The list of possible clientside writes the user can handle
commands = '\nWelcome to AAIRC. What would you like to do?\n\n' \
               '1.Type "$join roomname" to join or create a room with said roomname\n' \
               '2.Type "$list" to list all the currently active rooms to join in the session\n' \
               '3.Type "$leave" to leave a room \n' \
               '4.Type "$switch roomname" to switch to given roomname\n' \
               '5.Type "$personal name message" to send a direct message to another user with username "name"\n' \
               '6.Type "$help" to list all possible commands at any given moment\n' \
               '7.Type "$quit" to exit the program and close the user session\n' 

#The lists used for client names and dicts used for room and user details
clientList = []
bynames = []
roomInfo = {}
users = {}
roomUserList = {}

'''
TRANSMIT functions as the name indicates by sending client side messages in a room
'''
def TRANSMIT(userentry, roomnumber):
    for client in roomInfo[roomnumber].ppl:
        text = '['+roomnumber+'] '+userentry
        client.send(text.encode('utf-8'))
