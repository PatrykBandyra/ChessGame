import socket

if __name__ == '__main__':

    HOST = '192.168.0.241'
    PORT = 9999

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket just for accepting connections
    server.bind((HOST, PORT))

    server.listen(5)

    while True:
        communication_socket, address = server.accept()  # Waiting for connections
        print(f'Connected to {address}')
        message = communication_socket.recv(1024).decode('utf-8')
        print(f'Message from client is: {message}')
        communication_socket.send(f'Got your message'.encode('utf-8'))
        communication_socket.close()
        print(f'Connection with {address} ended!')