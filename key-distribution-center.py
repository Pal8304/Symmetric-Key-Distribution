import socket
from threading import Lock, Thread

from diffiehellman import DiffieHellman


class KeyDistributionCenter:
    def __init__(self, kdc_port=8000, kdc_password="password"):
        self.kdc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.kdc_port = kdc_port
        self.connected_clients = {}  # addr -> (socket, DiffieHellman instance)
        self.kdc_password = kdc_password
        self.lock = Lock()

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
            for client_socket, _ in self.connected_clients.values():
                client_socket.close()
            self.kdc_socket.close()

    def on_client_request(self, client_socket, addr):
        if not self.authenticate_client(client_socket, addr):
            print("Client not authenticated:", addr)
            client_socket.close()
            return
        with self.lock:
            self.connected_clients[addr] = (client_socket, None)
            print("Client authenticated:", addr)
        try:
            while True:
                msg = client_socket.recv(1024).decode("utf-8")
                if not msg:
                    print(f"Client {addr} disconnected.")
                    break
                print(f"Received from {addr}: {msg}")
                if msg.startswith("REQUEST_CONNECTION"):
                    _, target_addr_str = msg.split(":")
                    target_addr = eval(target_addr_str)  # Convert string to tuple
                    self.handle_connection_request(client_socket, addr, target_addr)
                elif msg.startswith("SHARED_SECRET"):
                    _, shared_secret = msg.split(":")
                    self.handle_shared_secret(addr, shared_secret)
                else:
                    client_socket.send("Unknown Command".encode())
        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Connection error with {addr}: {e}")
        finally:
            with self.lock:
                if addr in self.connected_clients:
                    del self.connected_clients[addr]
            client_socket.close()

    def authenticate_client(self, client_socket, addr):
        client_socket.send("Enter password:".encode())
        password = client_socket.recv(1024).decode()
        if password == self.kdc_password:
            client_socket.send("Authenticated successfully".encode())
            return True
        else:
            client_socket.send("Authentication failed".encode())
            return False

    def handle_connection_request(self, client_socket, addr, target_addr):
        with self.lock:
            if target_addr not in self.connected_clients:
                client_socket.send("Target client not found.".encode())
                return

            target_socket, _ = self.connected_clients[target_addr]

            # Initialize Diffie-Hellman instances for both clients
            dh_client = DiffieHellman(4)
            dh_target = DiffieHellman(4)

            self.connected_clients[addr] = (client_socket, dh_client)
            self.connected_clients[target_addr] = (target_socket, dh_target)

            client_public_key = dh_client.public_key
            target_public_key = dh_target.public_key

            # Send public keys to both clients
            client_socket.send(f"PUBLIC_KEY:{target_public_key}".encode())
            target_socket.send(f"PUBLIC_KEY:{client_public_key}".encode())

            # Prepare to receive shared secrets from both clients
            dh_client.shared_secret = None
            dh_target.shared_secret = None

    def handle_shared_secret(self, addr, shared_secret):
        with self.lock:
            client_socket, dh_instance = self.connected_clients[addr]
            dh_instance.shared_secret = shared_secret

            # Check if both clients have sent their shared secrets
            other_addr = None
            for a in self.connected_clients:
                if a != addr:
                    other_addr = a
                    break

            if other_addr:
                _, other_dh_instance = self.connected_clients[other_addr]
                if other_dh_instance and other_dh_instance.shared_secret:
                    # Both clients have sent their shared secrets
                    if dh_instance.shared_secret == other_dh_instance.shared_secret:
                        # Approve the connection
                        client_socket.send("Connection approved by KDC.".encode())
                        other_client_socket, _ = self.connected_clients[other_addr]
                        other_client_socket.send("Connection approved by KDC.".encode())
                    else:
                        # Shared secrets do not match
                        client_socket.send("Shared keys do not match.".encode())
                        other_client_socket, _ = self.connected_clients[other_addr]
                        other_client_socket.send("Shared keys do not match.".encode())


if __name__ == "__main__":
    kdc = KeyDistributionCenter()
    kdc.start()
