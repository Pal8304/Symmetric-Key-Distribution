import socket


class Client:
    def __init__(self, client_id, client_port=8001):
        self.client_id = client_id
        self.client_port = client_port
        self.client_socket = None
        self.authenticated = False

    def connect_to_kdc(self, kdc_host=socket.gethostname(), kdc_port=8000):
        self.client_socket = socket.socket()
        self.client_socket.connect((kdc_host, kdc_port))
        msg = self.client_socket.recv(1024).decode()
        if msg.count("password") > 0:
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
        print("Message sent to Key Distribution Center.")

    def receive_message(self):
        message = self.client_socket.recv(1024).decode()
        # print("Received from Key Distribution Center: " + message)
        return message


if __name__ == "__main__":
    client = Client(client_id=1)
    client.connect_to_kdc()
    while True and client.authenticated:
        try:
            message = input("Enter command: ")
            client.send_message(message)
            response = client.receive_message()
            print("Response from Key Distribution Center:", response)
            if response == "exit":
                break
        except KeyboardInterrupt:
            print("Shutting down client.")
            break
    client.close()
