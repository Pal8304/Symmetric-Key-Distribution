import socket
from threading import Thread

class Client:
    def __init__(self, port , client_id):
        self.client_id = client_id
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', port))
        self.server_socket.listen(5)
        
        # Thread for listening as a server
        thread = Thread(target=self.listen_for_connections)
        thread.daemon = True  # Allows thread to close with main program
        thread.start()
        
    def listen_for_connections(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()
                print(f"Connection from: {addr}")
                thread = Thread(target=self.receive_messages, args=(conn,addr))
                thread.daemon = True  # Allows thread to close with main program
                thread.start()
        
        except Exception as e:
            print(f"Some error occured {e}")
    
    def receive_messages(self, conn ,addr):
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    print(f"Client {addr} disconnected.")
                    break
                print(f"Received: {data}")

        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Connection error with {addr}: {e}")

        except Exception as e:
            print(f"Some error occured {e}")
    
    def connect_port(self):
        connect_port = int(input("Enter the port to connect to: "))
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', connect_port))
        print(f"Successfully conneted to: {self.client_socket.getpeername()}")

        # Thread for handling sending messages
        thread = Thread(target=self.send_commands)
        thread.daemon = True  # Allows thread to close with main program
        thread.start()
    
    def send_commands(self):
        try:
            while True:
                command = input("Enter command: ")
                self.client_socket.sendall(command.encode())

        except Exception as e:
            print("Connection closed some error occured.")
            self.close(self.client_socket)
            self.menu()

    def close(self,socket):
        if socket:
            name = socket.getsockname()
            socket.close()
            print(f"Connection is terminated of socket {name}")

    def menu(self):
        try:
            print("1. Connect to a KDC")
            print("2. Exit")

            choice = int(input("Enter your choice: "))
            if choice==1:
                client.connect_port()

            elif choice==2:
                print("Exiting")
                print("Shutting down client")
                self.close(self.server_socket)

            else:
                print("Invalid option")
                self.menu()

        except KeyboardInterrupt:
                print("Shutting down client.")
                self.close(self.server_socket)
    

port = port = int(input("Enter the port to bind (or 0 for dynamic allocation): "))
client = Client(port,1)
client.menu()

