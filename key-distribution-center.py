import socket
from threading import Thread


class KeyDistributionCenter:
    def __init__(self, kdc_port=8000):
        self.kdc_socket = socket.socket()
        self.kdc_port = kdc_port
        self.connected_clients = []

    def start(self):
        host = socket.gethostname()
        self.kdc_socket.bind((host, self.kdc_port))
        self.kdc_socket.listen(5)
        print("Key Distribution Center started on port: " + str(self.kdc_port))

        try:
            while True:
                clientsocket, addr = self.kdc_socket.accept()
                print("Connection from: " + str(addr))
                thread = Thread(
                    target=self.on_new_client_request, args=(clientsocket, addr)
                )
                thread.start()
            clientsocket.close()
            thread.join()
        except KeyboardInterrupt:
            print("Shutting down Key Distribution Center.")

    def close(self):
        self.kdc_socket.close()

    def on_new_client_request(self, clientsocket, addr):
        while True:
            if addr not in self.connected_clients:
                self.connected_clients.append(addr)
            msg = clientsocket.recv(1024).decode("utf-8")
            if not msg:
                break
            print("Received from client: " + msg)
        clientsocket.close()

    def get_connected_clients_list(self):
        return self.connected_clients


if __name__ == "__main__":
    kdc = KeyDistributionCenter()
    kdc.start()
    print(kdc.get_connected_clients_list())
    kdc.close()
