import socketserver
import json
import os
import hashlib
import time


class MyTCPhandeler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            try:
                self.data = self.request.recv(1024).strip()
                print("{} wrote:".format(self.client_address[0]))
                print(self.data)
                cmd_dic = json.loads(self.data.decode())
                action = cmd_dic["action"]
                if hasattr(self, action):
                    func = getattr(self, action)
                    func(cmd_dic)
            except ConnectionResetError as e:
                print(" Error ", e)
                break

    def put(self, *args):
        cmd_dic = args[0]
        filename = cmd_dic["filename"]
        filesize = cmd_dic["filesize"]
        f = open(filename, "wb")
        self.request.send(b"server stae is best")
        resives_size = 0
        m = hashlib.md5()
        if os.path.isfile(filename):
            while resives_size < filesize:
                data = self.request.recv(1024)
                m.update(data)
                resives_size += len(data)
                f.write(data)
                # print(resives_size, filesize)
            else:
                print("{} send data is successful:".format(self.client_address[0]))
                time.sleep(0.5)
                self.request.send(m.hexdigest().encode())

    def get(self, *args):
        cmd_dic = args[0]
        filename = cmd_dic["filename"]
        if os.path.isfile(filename):
            file_size = os.stat(filename).st_size
            file_state = {
                "filesize": file_size
            }
            self.request.send(json.dumps(file_state).encode())
            client_ack = self.request.recv(1024)
            m = hashlib.md5()
            f = open(filename,"rb")
            for line in f:
                m.update(line)
                self.request.send(line)
            else:
                print("send data is over")
                client_receive_state = self.request.recv(1024)
                print(client_receive_state.decode())
                self.request.send(m.hexdigest().encode())
                f.close()


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPhandeler)
    server.serve_forever()
