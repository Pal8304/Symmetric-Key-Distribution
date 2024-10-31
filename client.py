import socket


class Client:
    def __init__(self, client_id, client_port=8001):
        self.client_id = client_id
        self.client_port = client_port

    def connect_to_kdc(self, kdc_host=socket.gethostname(), kdc_port=8000):
        client_socket = socket.socket()
        client_socket.connect((kdc_host, kdc_port))
        print("Connected to Key Distribution Center.")
        return client_socket

    def close(self, client_socket):
        client_socket.close()
        print("Connection to Key Distribution Center closed.")

    def send_message(self, client_socket, message):
        client_socket.send(message.encode())
        print("Message sent to Key Distribution Center.")

    def receive_message(self, client_socket):
        message = client_socket.recv(1024).decode()
        print("Received from Key Distribution Center: " + message)
        return message


if __name__ == "__main__":
    client = Client(client_id=1)
    client_socket = client.connect_to_kdc()
    client.send_message(client_socket, "Hello from client!")
    client.close(client_socket)
