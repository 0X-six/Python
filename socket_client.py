import socket


client = socket.socket()
client.connect(('localhost', 8088))
print("连接已建立。")
while True:
    send = input("\n>>>:").encode("utf-8")
    # print(type(send))
    client.send(send)
    print("等待命令中 。。。\n")
    data_size = client.recv(1024)
    client.send("已确认连接".encode("utf-8")) # 返回确认连接的包，截断服务器两次发包；
    print(data_size.decode())
    receive_size = 0
    receive_data = b''
    while receive_size < int(data_size.decode()):
        data = client.recv(1024)
        receive_size += len(data)
        receive_data += data
    else:
        print(receive_data.decode())
    # message = date.decode('utf-8')
    # print("server：\n   ", message)
client.close()
