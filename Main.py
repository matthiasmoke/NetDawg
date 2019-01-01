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

MSG_SUCCESS = "Successfully saved file to %s\r\n" % upload_destination
MSG_FAIL = "Successfully saved file to %s\r\n" % upload_destination
PROMPT = "ND>"


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


def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):

        # read in bytes and write to destination
        file_buffer = ""

        while True:
            data = client_socket.recv(1024).decode()

            if not data:
                break
            else:
                file_buffer += data

        # try to write bytes out

        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send(MSG_SUCCESS.encode())
        except socket.error as err:
            print(err)
        except Exception:
            client_socket.send(MSG_FAIL.encode())

    # check for command execution
    if len(execute):

        output = run_command(execute)

        client_socket.send(output.encode())

        if command:

            while True:
                client_socket.send(PROMPT.encode())

                cmd_buffer = ""
                while"\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024).decode()

                # send back command output

                response = run_command(cmd_buffer)

                client_socket.send(response.encode())


def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # thread to handle new client
        client_thread = threading.Thread(client_handler(client_socket))
        client_thread.start()


def run_command(curr_command):

    # trim newline
    curr_command = curr_command.rstrip()

    # run command and get output back
    try:
        output = subprocess.check_output(curr_command, stderr=subprocess.STDOUT, shell=True)
    except Exception:
        output = "Failed to execute the command.\r\n"

    return output


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

