import socket
import pickle
import threading
from Crypto.PublicKey import RSA
from datetime import datetime
import sys
import traceback
from encryption import encryption

encryption = encryption()

class Client(object):
    def __init__(self):
        self.HEADER = 10
        self.host = "localhost"
        self.port = 6969
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user = input("Enter userID: ")
        self.public_key = encryption.load_public_key()
        self.private_key = encryption.load_private_key()
        self.receipent_public_key = None

    def createConnection(self):
        self.connection.connect((self.host, self.port))
        self.connection.setblocking(True)
        while True:
            try:
                data = self.connection.recv(1024)
                data = pickle.loads(data)
                if data['Message'] == "YO SEND ME THE DEETS":
                    info = {
                        "userID": self.user,
                        'PublicKey': self.public_key.exportKey(format='PEM')
                    }
                    info = pickle.dumps(info)
                    self.connection.send(info)
                    receive = threading.Thread(target=self.receive)
                    receive.start()
                    send = threading.Thread(target=self.send)
                    send.start()
                    break
            except Exception:
                traceback.print_exc()

    def send(self):
        while True:
            try:
                To = input("").strip()
                public_key = self.request_public_key(To)
                if public_key != "ERROR":
                    message = input("").strip()
                    message = encryption.encrypt_data(message)
                    data = {
                        "To": To,
                        "From": self.user,
                        "key": encryption.encrypt_key(self.receipent_public_key),
                        "Message": message,
                        "DateTime":
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }
                    data = pickle.dumps(data)
                    self.connection.sendall(data)
                else:
                    print("User not online")
            except Exception:
                traceback.print_exc()
                self.send()

    def receive(self):
        while True:
            try:
                data = self.connection.recv(2048)
                data = pickle.loads(data)
                key = encryption.decrypt_key(data['key'])
                print(data["From"] + ": " + encryption.decrypt_data(data["Message"], key))
                print(data["DateTime"])
            except EOFError:
                traceback.print_exc()
                break
                sys.exit()
            else:
                continue

    def request_public_key(self, receipent):
        key = {"Message": "Send key", "Receipent": receipent}
        data = pickle.dumps(key)
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((self.host, 6968))
        connection.send(data)
        receipent_key = pickle.loads(connection.recv(1024))
        if receipent_key != 'ERROR':
            self.receipent_public_key = RSA.import_key(receipent_key)
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        return receipent_key


if __name__ == '__main__':
    client = Client()
    client.createConnection()
