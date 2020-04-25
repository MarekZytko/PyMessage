from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.asymmetric.x448 import X448PrivateKey
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from secrets import token_bytes


class KeyExchange:
    def __init__(self):
        self.privateKey = X448PrivateKey.generate()
        self.publicKey = self.privateKey.public_key()

        #Via:
        #https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/#serialization

        self.serializedPublicKey = self.publicKey.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
            )

    def sharedKey(self, peerPublicKey:bytes):
        publicKey = x448.X448PublicKey.from_public_bytes(peerPublicKey)
        sharedKey = self.privateKey.exchange(publicKey)
        return sharedKey


class Aes:
    def __init__(self, key:bytes):
        #Key derivation:
        print(key)
        self.key = PBKDF2HMAC(
            algorithm=hashes.SHA3_512(),
            length=32, #bytes
            backend=default_backend(),
            iterations=300_000,
            salt=b'testtest'
        ).derive(key)
        print(self.key)
        self.initializationVector = token_bytes(16)

    def encrypt(self, msg):
        #256 bit key
        msg = msg.encode('utf-8')
        aes = Cipher(algorithms.AES(self.key), modes.CBC(self.initializationVector), backend=default_backend())
        encryptor = aes.encryptor()
        padder = padding.PKCS7(8*32).padder() #method uses bits instead of bytes
        paddedData = padder.update(msg) + padder.finalize()
        encrypted = encryptor.update(paddedData) + encryptor.finalize()
        encrypted = {"msg": encrypted, "IV": self.initializationVector}
        #self.iv = token_bytes(16)
        return encrypted

    def decrypt(self, msg, initializationVector):
        #256 bit key
        aes = Cipher(algorithms.AES(self.key), modes.CBC(initialization_vector=initializationVector), backend=default_backend())
        decryptor = aes.decryptor()
        decryptedData = decryptor.update(msg) + decryptor.finalize()

        unpadder = padding.PKCS7(8*32).unpadder() #method uses bits instead of bytes
        unpaddedData = unpadder.update(decryptedData) + unpadder.finalize()
        #decrypted = decryptor.update(unpaddedData) + decryptor.finalize()
        #decrypted = decrypted.decode('utf-8')
        decrypted = unpaddedData.decode('utf-8')
        return decrypted








if __name__ == "__main__":
    text = "Hello World!"

    alice = KeyExchange()
    bob = KeyExchange()

    alicePublicKey = alice.serializedPublicKey 
    bobPublicKey = bob.serializedPublicKey

    sharedKey = bob.sharedKey(alicePublicKey)
    sharedKey2 = alice.sharedKey(bobPublicKey)

    print(sharedKey, len(sharedKey))
    print('\n\n\n')
    print(sharedKey2, len(sharedKey2))

    text = "AcehLIN2nyECY!LIemy>C!eh>!cmi.EM!C@EMJcil1j2.e!J2lcie127ebjQCNHCGSNRI*^RLOM(URVICXTFBYJ@T"

    alice = Aes(sharedKey)
    bob = Aes(sharedKey2)
    print('\n\n\n')
    encrypted_message = bob.encrypt(text)
    print(encrypted_message)
    print('\n\n\n\n\n')
    decrypted_message = alice.decrypt(encrypted_message['msg'], encrypted_message['IV'])
    print(str(decrypted_message))