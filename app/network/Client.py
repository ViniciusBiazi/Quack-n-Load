import socket
import threading
import time
import os
from multiprocessing import Queue

from network.ClientInfo import PlayerInfo

class Client:
    def __init__(self, client_to_game_queue: Queue, game_to_client_queue: Queue):
        self.client_id = None # Client ID

        self.game_to_client_queue = game_to_client_queue
        self.client_to_game_queue = client_to_game_queue

        self.host = None # Server address
        self.tcp_port = None # Server TCP port
        self.udp_port = None # Server UDP port

        self.tcp_socket = None # Client TCP socket
        self.udp_socket = None # Client UDP socket

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

            self.client_to_game_queue.put("CONNECTED") # Send a message to the game process

            threading.Thread(target=self.receive_tcp_data, daemon=True).start() # Start a thread to receive lobby data from the server
            threading.Thread(target=self.receive_udp_data, daemon=True).start() # Start a thread to receive game data from the server

        except Exception as e:
            self.client_to_game_queue.put(f"CONNECTION_ERROR:{type(e).__name__}") # Send an error message to the game process
            self.disconnect() # Disconnect if an error occurs

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

                    message = packet.decode() # Decode the received data
                    # print(f"Received lobby data from server: {message}")

                    if message.startswith("SERVER_FULL"):
                        self.client_to_game_queue.put("SERVER_FULL")
                        self.disconnect()

                    elif message.startswith("GAME_CONNECTION:"):
                        _, info = message.split(":")
                        client_id, udp_port = info.split(";")

                        self.client_id = int(client_id)
                        self.udp_port = int(udp_port)
                        self.players[self.client_id] = PlayerInfo(self.client_id) # Add the player to the players dictionary

                        self.client_to_game_queue.put(f"PLAYER_ID:{client_id}") # Send the client ID to the game process

                        # envia um HELLO para o servidor UDP 
                        self.udp_socket.sendto(f"GAME_CONNECTION:{self.client_id}".encode(), (self.host, self.udp_port))
                    
                    elif message.startswith("PING:"):
                        # Respond to the server's PING
                        self.tcp_socket.sendall(message.encode())

                    elif message.startswith("UPDATE_PING:"):
                        _, info = message.split(":")
                        client_id, ping = info.split(";")

                        client_id = int(client_id)
                        ping = int(ping)

                        if client_id in self.players.keys():
                            self.players[client_id].ping = ping
                            self.client_to_game_queue.put(f"UPDATE_PING:{client_id};{ping}") # Send the updated ping to the game process

                    elif message.startswith("ADD_PLAYER:"):
                        _, client_id = message.split(":")

                        client_id = int(client_id)
                        self.players[client_id] = PlayerInfo(client_id)
                        self.client_to_game_queue.put(f"ADD_PLAYER:{client_id}") # Send the new player ID to the game process
                    
                    elif message.startswith("REMOVE_PLAYER:"):
                        _, client_id = message.split(":")
                        client_id = int(client_id)

                        if client_id in self.players.keys():
                            del self.players[client_id]
                            self.client_to_game_queue.put(f"REMOVE_PLAYER:{client_id}")

                    elif message.startswith("SERVER_STOPPED"):
                        self.disconnect()
                        self.client_to_game_queue.put("DISCONNECTED")

                    elif message.startswith("START_GAME"):
                        self.client_to_game_queue.put("START_GAME")
                        self.tcp_socket.sendall("GAME_STARTED|".encode()) # Send a message to the server to start the game

                    elif message.startswith("ADD_GAME_PLAYER:"):
                        self.client_to_game_queue.put(message) # Send the player update to the game process

            except socket.error as e:
                print(f"Error receiving data: {e}")
                break

        self.disconnect() # Disconnect if an error occurs

    def receive_udp_data(self):
        while self.connected:
            try:
                data, _ = self.udp_socket.recvfrom(1024) # Receive data from the server
                if not data:
                    break

                message = data.decode() # Decode the received data
                # print(f"Received game data from server: {message}")

                if message.startswith("UPDATE_PLAYER:"):
                    self.client_to_game_queue.put(message) # Send the player update to the game process

                elif message.startswith("ADD_PROJECTILE:"):
                    self.client_to_game_queue.put(message)

                elif message.startswith("REMOVE_PROJECTILE:"):
                    self.client_to_game_queue.put(message)

                elif message.startswith("ADD_WEAPON_PICKUP:"):
                    self.client_to_game_queue.put(message)

                elif message.startswith("REMOVE_WEAPON_PICKUP:"):
                    self.client_to_game_queue.put(message)

                elif message.startswith("PICKUP_WEAPON:"):
                    self.client_to_game_queue.put(message)

                elif message.startswith("RECEIVE_DAMAGE:"):
                    self.client_to_game_queue.put(message)

            except socket.error as e:
                print(f"Error receiving udp data: {e}")
                break

        self.disconnect() # Disconnect if an error occurs

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
            self.host = None
            self.tcp_port = None
            self.players.clear()

def start_client_process(host, tcp_port, client_to_game_queue: Queue, game_to_client_queue: Queue):
    client = Client(client_to_game_queue, game_to_client_queue) # Create a new client instance
    client.connect(host, tcp_port)

    tickrate = 120
    tick_duration = 1 / tickrate

    pid_pai = os.getppid()

    while client.connected:
        if os.getppid() != pid_pai:
            break
        
        start_time = time.monotonic()

        # Process incoming data from the server
        while not client.game_to_client_queue.empty():
            message = client.game_to_client_queue.get()
            # print(f"Processing message from game: {message}")

            if message == "DISCONNECT":
                client.disconnect()
                client.client_to_game_queue.put("DISCONNECTED")

            elif message.startswith("UPDATE_PLAYER:"):
                client.udp_socket.sendto(message.encode(), (client.host, client.udp_port))

            elif message.startswith("ADD_PROJECTILE:"):
                client.udp_socket.sendto(message.encode(), (client.host, client.udp_port))

            elif message.startswith("REMOVE_PROJECTILE:"):
                client.udp_socket.sendto(message.encode(), (client.host, client.udp_port))
            
            elif message.startswith("TRY_PICKUP_WEAPON:"):
                client.udp_socket.sendto(message.encode(), (client.host, client.udp_port))
            
            elif message.startswith("DROP_WEAPON:"):
                client.udp_socket.sendto(message.encode(), (client.host, client.udp_port))
            
            elif message.startswith("DEAL_DAMAGE:"):
                client.udp_socket.sendto(message.encode(), (client.host, client.udp_port))
        
        elapsed_time = time.monotonic() - start_time
        sleep_time = tick_duration - elapsed_time
        if sleep_time > 0:
            time.sleep(sleep_time)

