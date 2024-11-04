import random
import socket
from threading import Lock, Thread

group = (5, 14, 15, 16, 17, 18)
generator = (2, 3, 5, 7)


class KeyDistributionCenter:
    def __init__(self, kdc_port=8000, kdc_password="password"):
        self.kdc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.kdc_port = kdc_port
        self.connected_clients = {}
        self.connected_clients_diffie_hellman = {}
        self.diffie_hellman_shared_keys = {}  # shared key -> (client1, client2)
        self.kdc_password = kdc_password
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

    def authenticate_client(self, client_socket: socket, addr):
        client_socket.sendto("Enter password:".encode("utf-8"), addr)
        password = client_socket.recv(1024).decode("utf-8")
        if password == self.kdc_password:
            client_socket.sendto("Authenticated successfully".encode("utf-8"), addr)
            return True
        else:
            client_socket.sendto("Authentication failed".encode("utf-8"), addr)
            return False

    def on_client_request(self, client_socket, addr):
        if not self.authenticate_client(client_socket, addr):
            print("Client not authenticated:", addr)
            client_socket.close()
            return

        with self.lock:
            self.connected_clients[addr] = client_socket
            print("Client authenticated:", addr)
            public_key = client_socket.recv(4096).decode("utf-8")
            self.connected_clients_diffie_hellman[addr] = public_key

        try:
            while True:
                msg = client_socket.recv(1024).decode("utf-8")
                if not msg:
                    print(f"Client {addr} disconnected.")
                    break
                print(f"Received from Client with {addr}: {msg}")

                if msg.count("client_list") > 0:
                    client_list_to_send = self.get_other_connected_clients(addr)
                    client_socket.sendto(client_list_to_send.encode("utf-8"), addr)

                elif msg.startswith("REQUEST_CONNECTION"):
                    _, target_addr_str = msg.split(":")
                    target_addr = eval(target_addr_str)
                    session_id = random.randint(10000, 100000000)
                    self.handle_connection_request(
                        client_socket, addr, target_addr, session_id
                    )

                elif msg.startswith("SHARED_KEY"):
                    if msg in self.diffie_hellman_shared_keys:
                        client1 = self.diffie_hellman_shared_keys[msg][0]
                        client2 = self.diffie_hellman_shared_keys[msg][1]
                        if addr == client2:
                            print(f"Shared key {msg} received from {addr}")
                            print(f"Shared keys match between {client1} and {client2}")
                        else:
                            print(f"Shared key {msg} received from {addr}")
                            print(
                                f"Shared keys don't match between {client1} and {client2}"
                            )
                            self.diffie_hellman_shared_keys.pop(msg)

                elif msg.startswith("START_COMMUNICATION"):
                    _, target_addr_str = msg.split(":")
                    target_addr = eval(target_addr_str)
                    if target_addr in self.connected_clients:
                        client_socket.sendto(
                            f"COMMUNICATION ESTABLISHED BETWEEN {addr} AND {target_addr} WRITE 'EXIT' TO TERMINATE COMMUNICATION".encode(),
                            addr,
                        )
                        self.connected_clients[target_addr].sendto(
                            f"COMMUNICATION ESTABLISHED BETWEEN {addr} AND {target_addr} WRITE 'EXIT' TO TERMINATE COMMUNICATION".encode(),
                            target_addr,
                        )
                    else:
                        client_socket.sendto("Client not found".encode("utf-8"), addr)

                elif msg.startswith("MESSAGE"):
                    _, target_addr_str, encrypted_message = msg.split(":")
                    target_addr = eval(target_addr_str)
                    if target_addr in self.connected_clients:
                        self.connected_clients[target_addr].sendto(
                            f"ENCRYPTED:{encrypted_message}".encode(), target_addr
                        )
                    else:
                        client_socket.sendto("Client not found".encode("utf-8"), addr)
                else:
                    client_socket.sendto("Unknown Command".encode("utf-8"), addr)

        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Connection error with {addr}: {e}")

        finally:
            # Clean up after client disconnects
            with self.lock:
                if addr in self.connected_clients:
                    del self.connected_clients[addr]
            client_socket.close()

    def get_other_connected_clients(self, addr) -> str:
        with self.lock:
            client_list = self.connected_clients.keys()
            client_list_to_send = ""
            for index, client in enumerate(client_list):
                if client != addr:
                    client_list_to_send += f"Client {index}: {client}\n"

            if client_list_to_send == "":
                client_list_to_send = "No other clients connected."
            return client_list_to_send

    def handle_connection_request(
        self, client_socket: socket, addr, target_addr, session_id
    ):
        if target_addr in self.connected_clients:
            client_socket.sendto(
                f"DH_PUBLIC_KEY:{self.connected_clients_diffie_hellman[target_addr]}:{session_id}".encode(
                    "utf-8"
                ),
                addr,
            )
            shared_key_from_client = client_socket.recv(4096).decode("utf-8")
            print(f"Shared key from {addr}: {shared_key_from_client}")

            target_socket = self.connected_clients[target_addr]
            self.diffie_hellman_shared_keys[shared_key_from_client] = (
                addr,
                target_addr,
            )

            target_socket = self.connected_clients[target_addr]
            target_socket.sendto(
                f"DH_PUBLIC_KEY:{self.connected_clients_diffie_hellman[addr]}:{session_id}".encode(
                    "utf-8"
                ),
                target_addr,
            )

        else:
            client_socket.sendto("Client not found".encode("utf-8"), addr)

    def close(self):
        with self.lock:
            for client_socket in self.connected_clients.values():
                client_socket.close()
            self.kdc_socket.close()


if __name__ == "__main__":
    kdc = KeyDistributionCenter()
    kdc.start()
