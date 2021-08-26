import socket
import threading

HOST = '192.168.0.241'
PORT = 9999
PASSWORD = 'adminpass'

if __name__ == '__main__':

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    clients = []
    nicknames = []


    def broadcast(message):
        for client in clients:
            client.send(message)


    def handle(client):
        while True:
            try:
                message = client.recv(1024)
                if message.decode('utf-8').startswith('KICK'):
                    if nicknames[clients.index(client)] == 'admin':
                        name_to_kick = message.decode('utf-8')[5:]
                        kick_user(name_to_kick)
                        print(f'{name_to_kick} was kicked!')
                    else:
                        client.send('Command was refused!').encode('utf-8')
                elif message.decode('utf-8').startswith('BAN'):
                    if nicknames[clients.index(client)] == 'admin':
                        name_to_ban = message.decode('utf-8')[4:]
                        kick_user(name_to_ban)
                        with open('chat_room/bans.txt', 'a') as f:
                            f.write(f'{name_to_ban}\n')
                        print(f'{name_to_ban} was banned!')
                    else:
                        client.send('Command was refused!'.encode('utf-8'))
                else:
                    broadcast(message)
            except:
                if client in clients:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    nickname = nicknames[index]
                    broadcast(f'{nickname} left the chat'.encode('utf-8'))
                    nicknames.remove(nickname)
                    break


    def receive():
        while True:
            client, address = server.accept()
            print(f'Connected with {str(address)}')

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            with open('chat_room/bans.txt', 'r') as f:
                bans = f.readlines()

            if nickname+'\n' in bans:
                client.send('BAN'.encode('utf-8'))
                client.close()
                continue

            if nickname == 'admin':
                client.send('PASS'.encode('utf-8'))
                password = client.recv(1024).decode('utf-8')
                if password != PASSWORD:
                    client.send('REFUSE'.encode('utf-8'))
                    client.close()
                    continue

            nicknames.append(nickname)
            clients.append(client)

            print(f'Nickname of the client is {nickname}!')
            broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
            client.send('Connected to the server'.encode('utf-8'))

            thread = threading.Thread(target=handle, args=[client])
            thread.start()


    def kick_user(name):
        if name in nicknames:
            name_index = nicknames.index(name)
            client_to_kick = clients[name_index]
            clients.remove(client_to_kick)
            client_to_kick.send('You were kicked by an admin!'.encode('utf-8'))
            client_to_kick.close()
            nicknames.remove(name)
            broadcast(f'{name} was kicked by the admin!'.encode('utf-8'))

    print('Server is listening...')
    receive()