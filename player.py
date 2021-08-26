import socket
import pickle
import threading
import time
from queue import Queue
from typing import Dict, Union, List
from server import HOST, PORT, HEADER_LENGTH


class Player:
    def __init__(self, name: str):
        self.name = name
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.received_message_queue: Queue[Dict] = Queue()
        self.message_to_send: str = ''
        self.move_queue: Queue = Queue()
        self.connected: bool = False
        try:
            self.client.connect((HOST, PORT))
            message = self.receive_object_message()
            if message is not None:
                message_header = list(message['data'].keys())[0]
                if message_header == 'NICK':
                    self.send_object_message({'NICK': self.name})
                    message = self.receive_object_message()
                    if message is not None:
                        message_header = list(message['data'].keys())[0]
                        if message_header != 'OK':
                            raise Exception('Name already in use in a lobby!')
                else:
                    raise Exception('Received package with wrong message header!')
            else:
                raise Exception('Did not receive a demand for a nickname from a server!')
        except Exception as e:
            print(e)
            pass  # self.connected is still false
        else:
            self.connected = True

        self.stop_thread: bool = False
        self.lobby_names: List[str] = list()

    def send_object_message(self, message_object: Dict) -> None:
        """
        Sends message object (dictionary) preceded with header which has const length and info about the length of
        a message.

        :param message_object: for example: {'MSG': 'Hello World'}
        """
        pickled_message_object = pickle.dumps(message_object)
        message_header = bytes(f'{len(pickled_message_object):<{HEADER_LENGTH}}', 'utf-8')
        self.client.send(message_header + pickled_message_object)

    def send(self) -> None:
        """
        Sends messages if any present in message queue.
        """
        while not self.stop_thread:
            try:
                if self.message_to_send != '':
                    self.send_object_message({'MSG': self.message_to_send})
                    self.message_to_send = ''
                if not self.move_queue.empty():
                    # self.send_object_message({'MOV': self.move_queue.get()})
                    pass
            except Exception as e:
                self.client.close()
                self.stop_thread = True
                self.connected = False
                print(e)

    def receive_object_message(self) -> Union[Dict, None]:
        """
        Receives an object message from a server.

        :return: dictionary with encoded package header and decoded message
        """
        message_header = self.client.recv(HEADER_LENGTH)
        if not message_header:
            return None
        message_length = int(message_header.decode('utf-8').strip())
        data = pickle.loads(self.client.recv(message_length))
        if not data:
            return None
        return {'header': message_header, 'data': data}

    def receive(self) -> None:
        """
        Listens for packages from the server.
        """
        while not self.stop_thread:
            try:
                message = self.receive_object_message()
                if message is not None:
                    # Message logic based on package headers
                    message_header = list(message['data'].keys())[0]
                    if message_header == 'MSG':
                        self.received_message_queue.put(message['data'][message_header])
                        # print(f'{message["data"][message_header]["author"]}: {message["data"][message_header]["text"]}')

                    elif message_header == 'MOV':
                        pass
                    elif message_header == 'LOBBY':
                        self.lobby_names = message['data'][message_header]
                        print(self.lobby_names)
                    else:
                        raise Exception('Received package with wrong message header!')
            except Exception as e:
                self.client.close()
                self.stop_thread = True
                self.connected = False
                print(e)


if __name__ == '__main__':
    player = Player('Patryk')
    player.message_to_send = 'Hello'
    thread = threading.Thread(target=player.send)
    thread2 = threading.Thread(target=player.receive)
    thread2.start()
    thread.start()
    time.sleep(2)
    player.message_to_send = 'jolo'
    time.sleep(2)
    p2 = Player('John')
    p2.message_to_send = 'Siema'
    t = threading.Thread(target=p2.send)
    t2 = threading.Thread(target=p2.receive)
    t2.start()
    t.start()
    time.sleep(2)
    p2.message_to_send = 'allah'

