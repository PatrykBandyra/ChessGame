import socket
import threading
from server import HOST, PORT

if __name__ == '__main__':
    nickname = input('Choose a nickname: ')

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    def receive():
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    client.send(nickname.encode('utf-8'))
                else:
                    print(message)
            except:
                print('An error occurred!')
                client.close()
                break

    def write():
        while True:
            message = f'{nickname}: {input()}'
            client.send(message.encode('utf-8'))

    receive_thread = threading.Thread(target=receive)
    write_thread = threading.Thread(target=write)
    receive_thread.start()
    write_thread.start()

