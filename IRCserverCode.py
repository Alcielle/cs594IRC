'''
Portland State University 
Professor Nirupama Bulusu 
IRC Project Authors: Anadi Shakya(ashakya@pdx.edu), Abhishek Das(adas@pdx.edu)
'''
import socket
import threading 
'''
Server side code including all object names and roles and classifications as well as command behavior 
'''

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
               '4.Type "$swap roomname" to switch to given roomname\n' \
               '5.Type "$dm name message" to send a direct message to another user with username "name"\n' \
               '6.Type "$help" to list all possible commands at any given moment\n' \
               '7.Type "$quit" to exit the program and close the user session\n' \
               '8.Type "$broadcast message" to broadcast the message to all the active users.\n'

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

'''
A User has a name, room details, and room assignments
'''
class User:
    def __init__(self, name):
        self.name = name
        self.roomInfo = []
        self.currRoom = ''

'''
A Room has people in it, a name, and bynames
'''
class Room:
    def __init__(self, name):
        self.ppl = []
        self.bynames = []
        self.name = name

'''
roomDetails contains all the information of the room including userlists of those in the room in the session lists them on being passed the room name.
In the event of no details, an error message is sent
'''
def roomDetails(username):
    name = users[username]
    print(len(roomInfo))
    if len(roomInfo) == 0:
        name.send('Information unavailable for provided room.'.encode('utf-8'))
    else:
        reply = "Room Information: \n"
        for room in roomInfo:
            print(roomInfo[room].name)
            
            reply += roomInfo[room].name
            print(roomInfo[room].bynames)
            space=" User: "

            reply+=space

            for people in roomInfo[room].bynames:
                reply += people + '\n'
        name.send(f'{reply}'.encode('utf-8'))


'''
JOIN serves the dual function of joining existing rooms in the room list as well as creating rooms not in the room list should
a room name be provided that isn't in the list
'''
def JOIN(username, roomname):
    name = users[username]
    user = roomUserList[username]
    if roomname not in roomInfo:
        room = Room(roomname)
        roomInfo[roomname] = room
        room.ppl.append(name)
        room.bynames.append(username)

        user.currRoom = roomname
        user.roomInfo.append(room)
        name.send(f'{roomname} created'.encode('utf-8'))
    else:
        room = roomInfo[roomname]
        if roomname in user.roomInfo:
            name.send('You are already in this room.'.encode('utf-8'))
        else:
            room.ppl.append(name)
            room.bynames.append(username)
            user.currRoom = roomname
            user.roomInfo.append(room)
            TRANSMIT(f'{username} joined the room', roomname)

'''
SWAP switches users between rooms given a room number. Accounts for duplicate user profiles in rooms
'''
def SWAP(username, room_num):
    user = roomUserList[username]
    name = users[username]
    room = roomInfo[room_num]
    if room_num == user.currRoom:
        name.send('You are already in this room.'.encode('utf-8'))
    elif room not in user.roomInfo:
        name.send('You are not a part of the given room. Please join this room or create this room using the $join command'.encode('utf-8'))
    else:
        user.currRoom = room_num
        name.send(f'Switched to {room_num}'.encode('utf-8'))

'''
LEAVE accounts for exiting a room which involves usernameame being taken off the room list. Accounts for users that
haven't joined any rooms
'''
def LEAVE(username):
    user = roomUserList[username]
    name = users[username]
    if user.currRoom == '':
        name.send('You are not part of any room'.encode('utf-8'))
    else:
        room_num = user.currRoom
        room = roomInfo[room_num]
        user.currRoom = ''
        user.roomInfo.remove(room)
        roomInfo[room_num].ppl.remove(name)
        roomInfo[room_num].bynames.remove(username)
        TRANSMIT(f'{username} left the room', room_num)
        name.send('You left the room'.encode('utf-8'))


'''
DM accounts for direct messaging protocols sent to another given user in the call
'''
def DM(message):
    args = message.split(" ")
    user = args[2]
    sender = users[args[0]]
    if user not in users:
        sender.send('User not found'.encode('utf-8'))
    else:
        reciever = users[user]
        #allows for long messages to be sent simulating chat function
        text = ' '.join(args[3:])
        reciever.send(f'[DM] {args[0]}: {text}'.encode('utf-8'))
        sender.send(f'[DM] {args[0]}: {text}'.encode('utf-8'))

'''
QUIT ends the session for the given user and exits the program. Other users are informed said user has left the session
'''
def QUIT(username):
    bynames.remove(username)
    client = users[username]
    user = roomUserList[username]
    user.currRoom = ''
    for room in user.roomInfo:
        print(room.name)
        room.ppl.remove(client)
        print(room.ppl)
        room.bynames.remove(username)
        print(room.bynames)
        TRANSMIT(f'{username} left the room', room.name)
'''
broadcastMessage sends the given inputed message taken in as the slice after argument 0 to all the active clients
'''
def broadcastMessage(username, message):
    message = '[Broadcast from '+username+'] '+ " ".join(message[1:])
    for client in clientList:
        client.send(str(message).encode('utf-8'))

'''
clientInterface serves to read the client input and is the decision making command processing portion of the program
$ is placed as a token in front of client commands in order to be able to differentiate commands from normal text inputs
'''
def clientInterface(client):
    nick=''
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            args = message.split(" ")
            name = users[args[0]]
            nick = args[0]
            if '$help' in message:
                name.send(commands.encode('utf-8'))
            elif '$list' in message:
                roomDetails(args[0])
            elif '$join' in message:
                JOIN(args[0], ' '.join(args[2:]))
            elif '$leave' in message:
                LEAVE(args[0])
            elif '$swap' in message:
                SWAP(args[0], args[2])
            elif '$dm' in message:
                DM(message)
            elif '$broadcast' in message:
                broadcastMessage(args[0],args[1:])
            elif '$quit' in message:
                QUIT(args[0])
                name.send('QUIT'.encode('utf-8'))
                name.close()
            else:
                if roomUserList[args[0]].currRoom == '':
                    name.send(''.encode('utf-8'))
                else:
                    text = ' '.join(args[1:])
                    TRANSMIT(f'{args[0]}: {text}',roomUserList[args[0]].currRoom)

        except Exception as e:
            print("exception occured ", e)
            index = clientList.index(client)
            clientList.remove(client)
            client.close()
            print(f'Username is {nick}')
            if nick in bynames:
                QUIT(nick)
            if nick in bynames:
                bynames.remove(nick)
            break
'''
serverProcessing handles user commands, server details, user information and generally performs the initial setup and handling of the server and the multithreaded processes
'''
def serverProcessing():
    while True:
        client, address = server.accept()
        print(f'connected with {str(address)}')
        print(client)
        client.send('NICK'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        bynames.append(username)
        clientList.append(client)
        user = User(username)
        roomUserList[username] = user
        users[username] = client
        print(f'username of the client is {username}')
        client.send('Connected to the server!'.encode('utf-8'))
        client.send(commands.encode('utf-8'))
        thread = threading.Thread(target=clientInterface, args=(client,))
        thread.start()

print('Server is active and listening...')
serverProcessing()
