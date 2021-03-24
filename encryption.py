import pyAesCrypt
import io
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
import string


class encryption(object):
    def __init__(self):
        self.password = self.generate_password()
        self.bufferSize = 1024
        self.public_key = None
        self.private_key = None
        self.load_key()

    def generate_password(self):
      letters = string.ascii_lowercase
      password = ''.join(random.choice(letters) for i in range(15))
      return password

    def encrypt_data(self, msg):
    	data = msg.encode('utf-8')
    	fIn = io.BytesIO(data)
    	fCiph = io.BytesIO()
    	pyAesCrypt.encryptStream(fIn, fCiph, self.password, self.bufferSize)
    	message = fCiph.getvalue()
    	return message

    def decrypt_data(self, msg, password):
    	fCiph = io.BytesIO()
    	fDec = io.BytesIO()
    	fCiph = io.BytesIO(msg)
    	ctlen = len(fCiph.getvalue())
    	fCiph.seek(0)
    	pyAesCrypt.decryptStream(fCiph, fDec, password, self.bufferSize, ctlen)
    	message = str(fDec.getvalue().decode('utf-8'))
    	return message

    def load_key(self):
      with open("key.pem", "r") as key:
          key = key.read()
          self.private_key = RSA.import_key(key)
          self.public_key = self.private_key.public_key()

    def load_private_key(self):
      return self.private_key
    
    def load_public_key(self):
      return self.public_key

    def encrypt_key(self, public_key):
        encryptor = PKCS1_OAEP.new(public_key)
        key = encryptor.encrypt(self.password.encode())
        return key

    def decrypt_key(self, key):
        decryptor = PKCS1_OAEP.new(self.private_key)
        key = decryptor.decrypt(key)
        key = key.decode()
        return key

# en = encryption()
# print(en.password)
# print(en.encrypt_key(en.public_key))
