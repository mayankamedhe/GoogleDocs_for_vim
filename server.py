import json
import socket
import sys
import threading
import socketserver

readSocket = None
writeSocket = None
fileData = ""

class RequestHandler(socketserver.BaseRequestHandler):

    # Handle Requests will only be made by the Vim instance
    # whose things are getting copied to the other instance.
    # One Handle Request will be made with the Reading Vim
    # to establish a connection
    def handle(self):
        global readSocket
        global fileData
        global writeSocket

        theSocket = self.request
        while True:
            try:
                data = self.request.recv(4096).decode('utf-8')
            except socket.error:
                break
            except IOError:
                break

            if data == '':
                break

            try:
                decoded = json.loads(data)
            except ValueError:
                print("json decoding failed")
                decode = [-1, '']
            
            if decoded[0] == 1:
                if decoded[1] == "%%write_signal%%":
                    writeSocket = self.request
                elif decoded[1] == "%%read_signal%%":
                    readSocket = self.request
            elif decoded[0] >= 1:
                fileData = decoded[1]
                message = "[\"ex\", \":normal! o" +fileData+ "\"]"
                readSocket.sendall(message.encode('utf-8'))
                
        readSocket = None
        writeSocket = None

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): 
    pass

if __name__ == "__main__":
    HOST1, PORT1 = "localhost", 8765
    HOST2, PORT2 = "localhost", 8766

    readServer = ThreadedTCPServer((HOST1,PORT1), RequestHandler)
    ip1, port1 = readServer.server_address

    writeServer = ThreadedTCPServer((HOST2,PORT2), RequestHandler)
    ip2, port2 = writeServer.server_address

    writeServer_thread = threading.Thread(target=writeServer.serve_forever)
    readServer_thread = threading.Thread(target=readServer.serve_forever)

    writeServer_thread.daemon = True
    writeServer_thread.start()
    readServer_thread.daemon = True
    readServer_thread.start()

    while True:
        typed = sys.stdin.readline()
        if "quit" in typed:
            print("END SESSION")
            break

    writeServer.shutdown()
    writeServer.server_close()
    readServer.shutdown()
    readServer.server_close()

