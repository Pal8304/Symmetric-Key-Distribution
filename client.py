import socket
import threading

from diffie_helman import DiffieHellman


class Client:
    def __init__(self, client_id, client_port=8001):
        self.client_id = client_id
        self.client_port = client_port
        self.client_socket = None
        self.authenticated = False
        self.running = True  # Control the client loop
        self.diffie_hellman = None

    def connect_to_kdc(self, kdc_host=socket.gethostname(), kdc_port=8000):
        self.client_socket = socket.socket()
        self.client_socket.connect((kdc_host, kdc_port))
        msg = self.client_socket.recv(1024).decode()
        if "password" in msg:
            input_password = input("Enter password: ")
            self.client_socket.send(input_password.encode())
        msg = self.client_socket.recv(1024).decode()
        if msg == "Authenticated successfully":
            print("Authenticated with Key Distribution Center.")
            self.authenticated = True
            self.diffie_hellman = DiffieHellman(4)
            self.client_socket.send(f"{self.diffie_hellman.public_key}".encode())
            # print(f"Sent public key {self.diffie_hellman.public_key}")
        else:
            print("Failed to authenticate with Key Distribution Center.")
            self.authenticated = False
            self.client_socket.close()
            return
        print("Connected to Key Distribution Center.")

    def close(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
            print("Connection to Key Distribution Center closed.")

    def send_message(self):
        while self.running:
            message = input()
            if message:
                try:
                    self.client_socket.send(message.encode())
                    print("Message sent to Key Distribution Center.")
                except Exception as e:
                    print(f"Error sending message: {e}")
                    self.close()
                    break

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(4096).decode(encoding="utf-8")
                if message:
                    print(f"\nReceived: {message}")
                    if message.startswith("DH_PUBLIC_KEY"):
                        _, public_key = message.split(":")
                        self.diffie_hellman.generate_key(int(public_key))
                        self.client_socket.send(
                            f"SHARED_KEY:{self.diffie_hellman.get_key()}".encode()
                        )
                        print("SHARED_KEY:", self.diffie_hellman.get_key())
                else:
                    # Server has closed the connection
                    print("Disconnected from Key Distribution Center.")
                    self.close()
                    break
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.close()
                break


if __name__ == "__main__":
    client = Client(client_id=1)
    client.connect_to_kdc()
    if client.authenticated:
        # Start the thread for receiving messages
        receive_thread = threading.Thread(target=client.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        print("You can start sending messages. Press Ctrl+C to exit.")
        try:
            # Run the send_message function in the main thread
            client.send_message()
        except KeyboardInterrupt:
            print("Shutting down client.")
            client.close()
