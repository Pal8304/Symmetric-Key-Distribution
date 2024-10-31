import socket
from threading import Lock, Thread


class KeyDistributionCenter:
    def __init__(self, kdc_port=8000):
        self.kdc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.kdc_port = kdc_port
        self.connected_clients = {}
        self.lock = Lock()  # Protect access to shared resources

    def start(self):
        host = socket.gethostname()
        self.kdc_socket.bind((host, self.kdc_port))
        self.kdc_socket.listen(5)
        print("Key Distribution Center started on port:", self.kdc_port)

        try:
            while True:
                client_socket, addr = self.kdc_socket.accept()
                print("Connection from:", addr)

                thread = Thread(
                    target=self.on_client_request, args=(client_socket, addr)
                )
                thread.daemon = True  # Allows thread to close with main program
                thread.start()

        except KeyboardInterrupt:
            print("Shutting down Key Distribution Center.")
            self.close()

    def close(self):
        with self.lock:
            for client_socket in self.connected_clients.values():
                client_socket.close()
            self.kdc_socket.close()

    def on_client_request(self, client_socket, addr):
        if not self.authenticate_client(addr):
            print("Client not authenticated:", addr)
            client_socket.close()
            return

        with self.lock:
            self.connected_clients[addr] = client_socket
            print("Client authenticated:", addr)

        try:
            while True:
                msg = client_socket.recv(1024).decode("utf-8")
                if not msg:
                    print(f"Client {addr} disconnected.")
                    break
                print(f"Received from Client with {addr}: {msg}")

                # Process request (e.g., send session key or handle other commands)
                # For now, just echoing the message back
                client_socket.sendall(f"ECHO: {msg}".encode("utf-8"))

        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Connection error with {addr}: {e}")

        finally:
            # Clean up after client disconnects
            with self.lock:
                if addr in self.connected_clients:
                    del self.connected_clients[addr]
            client_socket.close()

    def authenticate_client(self, addr):
        # Add some actual authentication logic here
        return True

    def get_connected_clients_list(self):
        with self.lock:
            return list(self.connected_clients.keys())


if __name__ == "__main__":
    kdc = KeyDistributionCenter()
    kdc.start()
