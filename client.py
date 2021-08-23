import socket

if __name__ == '__main__':

    HOST = '192.168.0.241'
    PORT = 9999

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect((HOST, PORT))

    socket.send('Hello World'.encode('utf-8'))
    print(socket.recv(1024).decode('utf-8'))