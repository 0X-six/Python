# coding:utf-8

import socket
import os
import json
import hashlib


class FtpClient(object):

    def __init__(self):
        self.client = socket.socket()

    def connect(self, ip, port):
        self.client.connect((ip, port))

    def interactive(self):
        while True:
            cmd = input(">>>:").strip()
            if len(cmd) == 0:
                continue
            cmd_str = cmd.split()[0]
            if hasattr(self, "cmd_%s" % cmd_str):
                func = getattr(self, "cmd_%s" % cmd_str)
                func(cmd)
            else:
                pass
        else:
            pass

    def cmd_put(self, *args):
        cmd_split = args[0].split()
        # print(cmd_split)
        if len(cmd_split) > 1:
            filename = cmd_split[1]
            if os.path.isfile(filename):
                filesize = os.stat(filename).st_size
                mesg_dic = {
                    "filename": filename,
                    "filesize": filesize,
                    "action": "put",
                }
                self.client.send(json.dumps(mesg_dic).encode())
                sever_response = self.client.recv(1024)  # 避免粘包；可通过服务器返回状态码判定磁盘配额、是否有权限等。
                f = open(filename, "rb")
                m = hashlib.md5()
                for line in f:
                    m.update(line)
                    self.client.send(line)
                else:
                    print("send data is successful")
                    f.close()
                    server_md5_check = self.client.recv(1024)  # wait server response then send the md5 for all file
                    # self.client.send(m.hexdigest().encode())
                    server_md5 = server_md5_check.decode()
                    client_md5 = m.hexdigest()
                    print("服务端文件MD5：", server_md5, "\n本地端文件MD5：", client_md5)
                    if server_md5 == client_md5:
                        print("文件MD5校验通过,文件完整")
                    else:
                        print("文件MD5校验失败，文件损坏")
            else:
                print("(", filename, ")is not find")
        else:
            print("input is Error")

    def cmd_get(self, *args):
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            filename = cmd_split[1]
            if os.path.isfile(filename):
                msg = {
                    "filename": filename,
                    "action": "get"
                }
                self.client.send(json.dumps(msg).encode())
                server_response = json.loads(self.client.recv(1024).decode())  # wait server response for file size
                file_size = server_response["filesize"]
                self.client.send(b"client is know ")
                m = hashlib.md5()
                f = open(filename, "wb")
                receive_filesize = 0
                while receive_filesize < file_size:
                    data = self.client.recv(1024)
                    m.update(data)
                    receive_filesize += len(data)
                    f.write(data)
                    # print(receive_filesize,file_size)
                else:
                    print("file write state is successful")
                    file_receive_state = (b"file receive is successful")
                    self.client.send(file_receive_state)  # 隔断连续接收的数据
                    server_file_md5 = self.client.recv(1024)  # 等待server md5
                    server_md5 = server_file_md5.decode()
                    client_md5 = m.hexdigest()
                    print("服务端文件MD5：", server_md5, "\n本地端文件MD5：", client_md5)
                    if server_md5 == client_md5:
                        print("文件MD5校验通过,文件完整")
                    else:
                        print("文件MD5校验失败，文件损坏")
            else:
                print("(", filename, ")is not find")
        else:
            print("input is Error")


ftp_client = FtpClient()
ftp_client.connect("localhost", 9999)
ftp_client.interactive()
