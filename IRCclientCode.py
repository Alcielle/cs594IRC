'''
Portland State University 
Professor Nirupama Bulusu 
IRC Project Authors: Anadi Shakya(ashakya@pdx.edu), Abhishek Das(adas@pdx.edu)
'''

import threading
import socket
import sys


'''READ function: serves to account for serverside protocols as far as reading and interpreting user commands goes
This includes assigning a unique username (using NICK), exiting using QUIT, as well as a reissue of initial message for wrong inputs
and error catching for server disconnect wherein the user is auto disconnect and session is ended
'''
def READ():
    while True:
        try:
            userentry = client.recv(1024).decode('utf-8')
            if userentry == 'NICK':
                client.send(username.encode('utf-8'))
            elif userentry == 'QUIT':
                sys.exit(2)
            else:
                print(userentry)
        except Exception as exp:
            print('Server not responding')
            client.close()
            sys.exit(2)
'''
WRITE accounts for client side message input making sure it is in utf-8. If unsuccessful encoding, the program auto exits with an error state
'''
def WRITE():
    while True:
        userentry = '{} {}'.format(username, input(''))
        try:
            client.send(userentry.encode('utf-8'))
        except:
            sys.exit(0)



username = input("The Internet Relay Chat is activated. Please enter your unique username: ")
#threads are used to allow for multithreading allowing for multiple parallel running processes in any sequence 
threads = []
#Socket feature is used to connect to a socket and initiate network connection at said socket
client = socket.socket()
#Anything after 40000 is fine. This is a hardcoded connection on a known private line
client.connect((socket.gethostname(), 59400))
#the multithreading is set up
read_thread = threading.Thread(target=READ)
read_thread.start()
threads.append(read_thread)
write_thread = threading.Thread(target=WRITE)
write_thread.start()
threads.append(write_thread)
