#!/usr/bin/python3
''' Python SQL logging bot
Author: Nick Seelert

Basic bot connects to server via ssl and logs to PostgreSQL database.
Requires PyGreSQL -- install with pip3 install pygresql

'''


import socket, ssl
from pg import DB

# irc server
server = "chat.freenode.net"
sslport = 6697
channel = ""

# bot params
botnick = "ElliotAlderson"
adminname = "MrRobot"
exitcode = ".halt"

# database params
dbname = 'db1'
dbuser = 'postgres'
dbpwd = NULL
dbhost = 'localhost'
dbport = 5432


# connect to server
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, sslport))
sslsock = ssl.wrap_socket(ircsock)
sslsock.send(bytes("USER " + botnick + " " + botnick + " " + botnick + " " + botnick + "\n", "UTF-8"))
sslsock.send(bytes("NICK " + botnick + "\n", "UTF-8"))


# connect to database
db = DB(dbname=db1, host=dbhost, port=dbport, user=dbuser, passwd=dbpwd)

# log to database
def logmsg(recvd):
    if recvd[0] == ':':
        # see db insert statements for var explanations
        p = recvd.split('!', 1)[0][1:]
        n = recvd.split('~', 1)[1].split('@', 1)[0]
        h = recvd.split('@', 1)[1].split(' ', 1)[0]
        c = recvd.split(' ', 2)[1]

        if c == 'PRIVMSG':
            m = recvd.split('PRIVMSG', 1)[1].split(':', 1)[1]
            db.insert(dbname, pseud=p, name=n, host=h, cmd=c, msg=m)
        else:
            db.insert(dbname, pseud=p, name=n, host=h, cmd=c)


# join channel
def joinchan(chan):
    sslsock.send(bytes("JOIN " + chan + "\n", "UTF-8"))
    ircmsg = ""
    while ircmsg.find("End of /NAMES list.") == -1:
        ircmsg = sslsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)


# respond to server pings
def ping():
    sslsock.send(bytes("PONG :pingis\n", "UTF-8"))


# send msg to channel or user
def sendmsg(msg, target=channel):
    sslsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))


# send ctcp to channel or user
def sendctcp(msg, command, target=channel):
    sslsock.send(bytes("PRIVMSG " + target + " :\x01" + command + " " + msg + "\x01\n", "UTF-8"))


def main():
    joinchan(channel)
    while 1:
        ircmsg = sslsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')

        print(ircmsg)
        logmsg(ircmsg)

        if ircmsg.find("PRIVMSG") != -1:
            # split at ! and drop the leading :
            name = ircmsg.split('!', 1)[0][1:]
            # first split at the PRIVMSG cmd, then at the first :
            # split( ,1) means it will only split on the first :
            message = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
            if len(name) < 17:
                if message.find('Hi ' + botnick) != -1:
                    sendmsg("Hello " + name + "!")
                if name.lower() == adminname.lower() and message.rstrip() == exitcode:
                    sendctcp("has caught fire...", 'ACTION')
                    sslsock.send(bytes("QUIT\n", "UTF-8"))
                    db.close()
                    return
        else:
            if ircmsg.find("PING :") != -1:
                ping()

main()