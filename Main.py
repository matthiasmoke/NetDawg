import sys
import subprocess
import socket
import getopt
import threading

from Tools.Scripts.treesync import raw_input

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0
commandList = ["help", "listen", "execute", "target", "port", "command", "upload"]


def usage():
    print("MiniNetCat")


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode())

        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096).decode()

                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response)

            # wait for more input
            buffer = raw_input("")
            buffer += "\n"

            client.send(buffer.encode())
    except Exception as err:
        print("Error! Exiting\n %s" % str(err))
        client.close();



def server_loop():
    pass


def main():
    global listen
    global command
    global execute
    global upload_destination
    global target
    global port

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",
                                   commandList)
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    # evaluate command
    for o, a in opts:
        if o in ("-h", commandList[0]):
            usage()
        elif o in ("-l", commandList[1]):
            listen = True
        elif o in ("-e", commandList[2]):
            execute = a
        elif o in ("-t", commandList[3]):
            target = a
        elif o in ("-p", commandList[4]):
            port = int(a)
        elif o in ("-c", commandList[5]):
            command = True
        elif o in ("-u", commandList[6]):
            upload_destination = a
        else:
            assert False, "Invalid input"

    # listen or just send data?
    if not listen and len(target) and port > 0:

        # read in buffer from the commandline
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()


main()

