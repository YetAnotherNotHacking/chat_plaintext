import socket
import threading

class Server:
    def __init__(self, host='127.0.0.1', port=45685):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.clients = []
        self.nicknames = []
        self.lock = threading.Lock()  # Add lock initialization

    def broadcast(self, message, sender):
        with self.lock:
            for client in self.clients:
                if client != sender:
                    try:
                        client.sendall(message)
                    except Exception as e:
                        print("Error in the broadcast function, error:", e)

    def handle(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message, client)  # Pass client to broadcast
            except:
                with self.lock:
                    index = self.clients.index(client)
                    self.clients.remove(client)
                    client.close()
                    nickname = self.nicknames[index]
                    self.nicknames.remove(nickname)
                    self.broadcast(f'{nickname} left the chat!'.encode('ascii'), client)
                break

    def receive(self):
        print('Waiting for connections...')
        while True:
            try:
                client, address = self.server.accept()
                print(f'Connected with {str(address)}')

                client.send('NICK'.encode('ascii'))
                nickname = client.recv(1024).decode('ascii')

                with self.lock:
                    self.nicknames.append(nickname)
                    self.clients.append(client)

                print(f'Nickname of the client is {nickname}!')
                self.broadcast(f'{nickname} joined the chat!'.encode('ascii'), client)
                client.send('Connected to the server!'.encode('ascii'))

                thread = threading.Thread(target=self.handle, args=(client,))
                thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def start(self):
        print('Server started...')
        self.receive()

# Instantiate the server and start it
server = Server()
server.start()
