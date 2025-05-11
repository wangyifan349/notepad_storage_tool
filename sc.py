import socket
import threading
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
# -----------------------------------------------------------------------------
def derive_aes_key(shared_key):
    """
    Derive an AES key from the shared X25519 key using HKDF.
    """
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(shared_key)
# -----------------------------------------------------------------------------
def aes_gcm_encrypt(key, plaintext):
    """
    Encrypt a message using AES-GCM. Returns nonce + tag + ciphertext.
    """
    nonce = get_random_bytes(12)  # Use a 12-byte nonce for GCM
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + tag + ciphertext
# -----------------------------------------------------------------------------
def aes_gcm_decrypt(key, encrypted_message):
    """
    Decrypt a message using AES-GCM. Assumes input is nonce + tag + ciphertext.
    """
    nonce = encrypted_message[:12]
    tag = encrypted_message[12:28]
    ciphertext = encrypted_message[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
# -----------------------------------------------------------------------------
def handle_client(client_socket, derived_key):
    """
    Handle messages from a connected client.
    """
    try:
        while True:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break
            try:
                # Attempt to decrypt the received message
                decrypted_message = aes_gcm_decrypt(derived_key, encrypted_message)
                print("Received:", decrypted_message.decode())

                # Encrypt a response and send it back to the client
                response = aes_gcm_encrypt(derived_key, b"Message received from server.")
                client_socket.sendall(response)
            except Exception as e:
                print(f"Failed to decrypt message: {e}")
                break
    finally:
        client_socket.close()
# -----------------------------------------------------------------------------
def server():
    """
    Main server function to accept connections and spawn client handlers.
    """
    server_private_key = x25519.X25519PrivateKey.generate()
    server_public_key = server_private_key.public_key().public_bytes()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(5)
    print("Server running...")
    while True:
        try:
            client_socket, addr = server_socket.accept()
            print("Connection from", addr)
            # Send server's public key
            client_socket.sendall(server_public_key)
            # Receive client's public key
            client_public_key_bytes = client_socket.recv(32)
            client_public_key = x25519.X25519PublicKey.from_public_bytes(client_public_key_bytes)
            # Derive shared key
            shared_key = server_private_key.exchange(client_public_key)
            derived_key = derive_aes_key(shared_key)
            # Handle client in a new thread
            client_handler = threading.Thread(target=handle_client, args=(client_socket, derived_key))
            client_handler.start()
        except Exception as e:
            print(f"An error occurred with a client: {e}")
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    server_thread = threading.Thread(target=server)
    server_thread.start()







import socket
import threading
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
# -----------------------------------------------------------------------------
def derive_aes_key(shared_key):
    """
    Derive an AES key from the shared X25519 key using HKDF.
    """
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(shared_key)
# -----------------------------------------------------------------------------
def aes_gcm_encrypt(key, plaintext):
    """
    Encrypt a message using AES-GCM. Returns nonce + tag + ciphertext.
    """
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + tag + ciphertext
# -----------------------------------------------------------------------------
def aes_gcm_decrypt(key, encrypted_message):
    """
    Decrypt a message using AES-GCM. Assumes input is nonce + tag + ciphertext.
    """
    nonce = encrypted_message[:12]
    tag = encrypted_message[12:28]
    ciphertext = encrypted_message[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
# -----------------------------------------------------------------------------
def receive_messages(client_socket, derived_key):
    """
    Continuously receive and decrypt messages from the server.
    """
    try:
        while True:
            encrypted_response = client_socket.recv(1024)
            if not encrypted_response:
                break
            try:
                # Attempt to decrypt the server's response
                decrypted_response = aes_gcm_decrypt(derived_key, encrypted_response)
                print("Server:", decrypted_response.decode())
            except Exception as e:
                print(f"Failed to decrypt message from server: {e}")
    finally:
        client_socket.close()
# -----------------------------------------------------------------------------
def client():
    """
    Main client function to connect to the server and exchange messages.
    """
    client_private_key = x25519.X25519PrivateKey.generate()
    client_public_key = client_private_key.public_key().public_bytes()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 8080))
        # Receive server's public key
        server_public_key_bytes = client_socket.recv(32)
        server_public_key = x25519.X25519PublicKey.from_public_bytes(server_public_key_bytes)
        # Send client's public key
        client_socket.sendall(client_public_key)
        # Derive shared key
        shared_key = client_private_key.exchange(server_public_key)
        derived_key = derive_aes_key(shared_key)
        # Start receiving thread
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, derived_key))
        receive_thread.start()
        try:
            while True:
                # Read user input and send encrypted message to the server
                message = input("Enter message: ").encode()
                encrypted_message = aes_gcm_encrypt(derived_key, message)
                client_socket.sendall(encrypted_message)
        except KeyboardInterrupt:
            print("Client shutting down.")
            client_socket.close()
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    client()

