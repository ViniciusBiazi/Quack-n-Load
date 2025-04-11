import socket
import threading

from network.ClientInfo import PlayerInfo

class Client:
    def __init__(self, game_state):
        self.client_id = None

        self.game_state = game_state

        self.host = None
        self.tcp_port = None
        self.udp_port = None

        self.tcp_socket = None
        self.udp_socket = None

        self.connected = False # Flag to check if the client is connected to the server

        self.players: dict[int, PlayerInfo] = {} # Dictionary to store connected players

    def connect(self, host, tcp_port):
        self.host = host
        self.tcp_port = tcp_port

        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP socket
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create a UDP socket
            self.tcp_socket.connect((self.host, self.tcp_port)) # Conecto meu socket TCP ao servidor
            self.connected = True 

            threading.Thread(target=self.receive_tcp_data, daemon=True).start() # Start a thread to receive lobby data from the server
            threading.Thread(target=self.receive_udp_data, daemon=True).start() # Start a thread to receive game data from the server

        except socket.error as e:
            print(f"Error connecting to server: {e}")
            self.connected = False

    def receive_tcp_data(self):
        while self.connected:
            try:
                data = self.tcp_socket.recv(1024) # Receive data from the server
                if not data:
                    break

                packets = data.split(b"|") # Split the received data into packets

                for packet in packets:
                    if not packet:
                        continue

                    # Process each packet
                    self.process_tcp_data(packet)
                    
            except socket.error as e:
                print(f"Error receiving data: {e}")
                break

        self.disconnect() # Disconnect if an error occurs

    def process_tcp_data(self, data):
        try:
            message = data.decode("utf-8") # Decode the received data
            print(f"Received lobby data from server: {message}")

            if message.startswith("PING:"):
                self.tcp_socket.sendall(message.encode())

            elif message.startswith("START_GAME_CONNECTION:"):
                _, info = message.split(":")
                client_id, udp_port = info.split(";")

                self.client_id = int(client_id)
                self.udp_port = int(udp_port)

                self.players[self.client_id] = PlayerInfo(self.client_id) # Add the player to the players dictionary

                # envia um HELLO para o servidor UDP 
                self.udp_socket.sendto(f"HELLO:{self.client_id}".encode(), (self.host, self.udp_port))

            elif message.startswith("UPDATE_PING:"):
                _, info = message.split(":")
                client_id, ping = info.split(";")

                client_id = int(client_id)
                ping = int(ping)

                if client_id in self.players:
                    self.players[client_id].ping = ping

            elif message.startswith("SERVER_SHUTDOWN"):
                print("Server is shutting down.")
                self.disconnect()
            
            elif message.startswith("ADD_PLAYER:"):
                _, info = message.split(":")
                client_id, nickname = info.split(";")

                client_id = int(client_id)

                if client_id not in self.players:
                    self.players[client_id] = PlayerInfo(client_id, nickname)
            
        except Exception as e:
            print(f"Error processing tcp data: {e}")

    def receive_udp_data(self):
        while self.connected:
            try:
                data, _ = self.udp_socket.recvfrom(1024) # Receive data from the server
                if not data:
                    break

                # Process the received data
                self.process_udp_data(data)

            except socket.error as e:
                print(f"Error receiving udp data: {e}")
                break

        self.connected = False
        self.udp_socket.close()

    def process_udp_data(self, data):
        try:
            message = data.decode("utf-8") # Decode the received data
            print(f"Received game data from server: {message}")

        except Exception as e:
            print(f"Error processing udp data: {e}")

    def disconnect(self):
        try:
            if self.tcp_socket:
                self.tcp_socket.close()
            if self.udp_socket:
                self.udp_socket.close()
        except Exception as e:
            print(f"Error closing sockets: {e}")
        finally:
            self.connected = False
            self.tcp_socket = None
            self.udp_socket = None
            self.client_id = None
            self.udp_port = None
            self.server_host = None
            self.tcp_port = None
            self.players.clear()
            print("Disconnected from server.")
            