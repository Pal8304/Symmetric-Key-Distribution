import socket

from diffiehellman import DiffieHellman


class Client:
    def __init__(self, client_id, client_port=8001):
        self.client_id = client_id
        self.client_port = client_port
        self.client_socket = None
        self.authenticated = False
        self.diffie_hellman = DiffieHellman(4)

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
        else:
            print("Failed to authenticate with Key Distribution Center.")
            self.authenticated = False
            self.client_socket.close()
            return
        print("Connected to Key Distribution Center.")

    def close(self):
        if self.client_socket:
            self.client_socket.close()
            print("Connection to Key Distribution Center closed.")

    def send_message(self, message):
        self.client_socket.send(message.encode())

    def receive_message(self):
        message = self.client_socket.recv(1024).decode()
        return message

    def handle_diffie_hellman(self, other_public_key):
        self.diffie_hellman.generate_key(int(other_public_key, 16))
        shared_secret = self.diffie_hellman.get_key()
        print(f"Shared secret generated: {shared_secret}")
        # Send shared secret to KDC for validation
        self.send_message(f"SHARED_SECRET:{shared_secret}")


if __name__ == "__main__":
    client = Client(client_id=1)
    client.connect_to_kdc()
    while client.authenticated:
        try:
            command = input("Enter command: ")
            if command.startswith("REQUEST_CONNECTION"):
                # Extract target address from the command
                _, address_part = command.split(":")
                client.send_message(f"REQUEST_CONNECTION:{address_part}")
                response = client.receive_message()
                print("Response from KDC:", response)
                if response.startswith("PUBLIC_KEY"):
                    _, other_public_key = response.split(":")
                    client.handle_diffie_hellman(other_public_key)
                    # Wait for KDC approval
                    approval = client.receive_message()
                    print("KDC Approval:", approval)
                else:
                    print("Failed to receive public key from KDC.")
            else:
                client.send_message(command)
                response = client.receive_message()
                print("Response from KDC:", response)
        except KeyboardInterrupt:
            print("Closing client.")
            break
    client.close()
