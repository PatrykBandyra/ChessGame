import socket
import threading
from typing import List, Union, Dict, Tuple
import pickle

HOST = '192.168.0.241'
PORT = 1234
HEADER_LENGTH = 10
MAX_LOBBY_SIZE = 6


class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen()

        self.clients: List[Tuple[socket.socket, str]] = list()

    def broadcast(self, message: Dict) -> None:
        """
        Broadcasts message to all clients.

        :param message:
        """
        for client in self.clients:
            Server.send_object_message(client[0], message)

    @staticmethod
    def receive_object_message(client: socket.socket) -> Union[Dict, None]:
        """
        Receives an object message from a client.

        :param client: socket
        :return: dictionary with encoded package header and decoded message
        """
        message_header = client.recv(HEADER_LENGTH)
        if not message_header:
            return None
        message_length = int(message_header.decode('utf-8').strip())
        data = pickle.loads(client.recv(message_length))
        if not data:
            return None
        return {'header': message_header, 'data': data}

    @staticmethod
    def send_object_message(client: socket.socket, message_object: Dict) -> None:
        """
        Sends message object (dictionary) preceded with header which has const length and info about the length of
        a message.

        :param client: socket
        :param message_object: for example: {'MSG': 'Hello World'}
        """
        pickled_message_object = pickle.dumps(message_object)
        message_header = bytes(f'{len(pickled_message_object):<{HEADER_LENGTH}}', 'utf-8')
        client.send(message_header + pickled_message_object)

    def receive(self) -> None:
        """
        Deals with the first contact of a client with the server.
        """
        while True:
            client_socket, address = self.server.accept()
            print(f'Connected with {address}')
            nickname = None
            try:
                if len(self.clients) >= MAX_LOBBY_SIZE:
                    Server.send_object_message(client_socket, {'NO_SPACE': ''})
                else:
                    Server.send_object_message(client_socket, {'NICK': ''})
                    message = Server.receive_object_message(client_socket)
                    if message is not None:
                        message_header = list(message['data'].keys())[0]
                        if message_header == 'NICK':
                            nickname = message['data'][message_header]
                            if nickname in [client[1] for client in self.clients]:
                                self.send_object_message(client_socket, {'NICK_IN_USE': ''})
                            else:
                                self.send_object_message(client_socket, {'OK': ''})
                                self.clients.append((client_socket, nickname))
                                print(f'{nickname} joined')

                                # Broadcast lobby players state
                                self.broadcast({'LOBBY': [client[1] for client in self.clients]})

                                thread = threading.Thread(target=self.handle, args=[client_socket, nickname])
                                thread.start()
                        else:
                            raise Exception('First message from client should have a nickname!')
            except Exception as e:
                if nickname is not None:  # Exception occurred after appending socket and nickname to self.clients
                    self.clients.remove((client_socket, nickname))
                    # Broadcast lobby players state
                    self.broadcast({'LOBBY': [client[1] for client in self.clients]})
                client_socket.close()
                print(e)

    def handle(self, client: socket.socket, nickname: str) -> None:
        """
        Deals with communication with a client.

        :param client: socket
        :param nickname:
        """
        first_iter = True
        while True:
            try:
                message = Server.receive_object_message(client)
                if message is not None:
                    message_header = list(message['data'].keys())[0]
                    if message_header == 'MSG':
                        self.broadcast({'MSG': {'author': nickname, 'text': message['data'][message_header]}})
                        print(f'Received message from {nickname}:\n{message["data"][message_header]}')

                    elif message_header == 'MOV':
                        pass

                    else:
                        raise Exception('Undefined message header received!')

            except Exception as e:
                self.clients.remove((client, nickname))
                client.close()
                # Broadcast lobby players state
                self.broadcast({'LOBBY': [client[1] for client in self.clients]})
                print(e)
                break


def main() -> None:
    server = Server()
    server.receive()


if __name__ == '__main__':
    main()