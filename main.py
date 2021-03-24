import socket
import pickle
import threading
import sys
import traceback


class Server(object):
    def __init__(self):
        self.host = "localhost"
        self.port = 6969
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.key_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.key_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.key_server.bind((self.host, 6968))
        self.key_server.listen()
        self.clientsConnected = {}
        key = threading.Thread(target=self.get_public_key)
        key.start()

    def createConnection(self):
        while True:
            try:
                connection, address = self.server.accept()
                print(f"connection from {address}")
                data = {'Message': 'YO SEND ME THE DEETS'}
                data = pickle.dumps(data)
                connection.send(data)
                user_info = connection.recv(1024)
                user_info = pickle.loads(user_info)
                user_info["CONNECTION"] = connection
                self.clientsConnected[user_info["userID"]] = user_info
                foward = threading.Thread(
                    target=self.forward,
                    args=(
                        connection,
                        address,
                    ),
                )
                foward.start()
            except Exception:
                traceback.print_exc()
                print(f"Connection closed for {address}")
                continue

    def forward(self, connection, address):
        while True:
            try:
                metaData = connection.recv(2048)
                metaData = pickle.loads(metaData)
                print(len(metaData))
                print(metaData)
                To = metaData["To"]
                data = pickle.dumps(metaData)
                if To in self.clientsConnected:
                    receipent = self.clientsConnected[To]
                    connection = receipent["CONNECTION"]
                    connection.send(data)
            except Exception:
                traceback.print_exc()
                print(f"Connection closed for {address}")
                break

    def get_public_key(self):
        while True:
            connection, address = self.key_server.accept()
            key_request = connection.recv(1024)
            key_request = pickle.loads(key_request)
            key_request = key_request["Receipent"]
            if key_request in self.clientsConnected:
                key_to_send = self.clientsConnected[key_request]
                key_to_send = pickle.dumps(key_to_send["PublicKey"])
                connection.send(key_to_send)
            else:
                data = pickle.dumps("ERROR")
                connection.send(data)

if __name__ == '__main__':
    try:
        server = Server()
        server.createConnection()
    except Exception:
        traceback.print_exc()
        sys.exit()
