import socket
import threading

class KeyDistributionCenter:
    def __init__(self, kdc_port=8000):
        self.kdc_socket = socket.socket()
        self.kdc_port = kdc_port
        self.connected_clients = {}
    
    def start(self):
        self.kdc_socket.bind(('localhost', self.kdc_port))
        self.kdc_socket.listen(5)
        print("Key Distribution Center started on port:", self.kdc_port)
        
        # Thread for listening as a server
        threading.Thread(target=self.listen_for_connections).start()
        
    def listen_for_connections(self):
        try:
            while True:
                client_socket, addr = self.kdc_socket.accept()
                print(f"Connection from: {addr}")
                threading.Thread(target=self.receive_messages, args=(client_socket,addr)).start()
        
        except KeyboardInterrupt:
            print("Shutting down Key Distribution Center.")
            self.close()
    
    def authenticate_client(self,client_socket,addr):
        client_socket.sendto("Enter password:".encode("utf-8"), addr)
        password = client_socket.recv(1024).decode("utf-8")

        if password == "gold_medal":
            client_socket.sendto("Authenticated successfully".encode("utf-8"), addr)
            return True
        else:
            client_socket.sendto("Authentication failed".encode("utf-8"), addr)
            return False

    def receive_messages(self, client_socket ,addr):
        try:
            if not self.authenticate_client(client_socket, addr):
                print("Client not authenticated:", addr)
                client_socket.close()
                return
            
            print("Client authenticated:", addr)
            self.connected_clients[addr] = client_socket
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    print(f"Client {addr} disconnected.")
                    break
                print(f"Received: {data}")

        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Connection error with {addr}: {e}")
    
    def close(self):
        for client_socket in self.connected_clients.values():
            client_socket.close()
        self.kdc_socket.close()
    
kdc = KeyDistributionCenter()
kdc.start()