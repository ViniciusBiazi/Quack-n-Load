import socket
import threading
import time
from multiprocessing import Queue
import os
import random

from network.ClientInfo import ClientInfo

class Server:
    def __init__(self, server_to_game_queue: Queue, game_to_server_queue: Queue, host="0.0.0.0", tcp_port=0, udp_port=0, max_clients=4):
        self.host = host if host != "0.0.0.0" else self.get_my_ip()

        self.server_to_game_queue = server_to_game_queue 
        self.game_to_server_queue = game_to_server_queue

        self.clients: dict[int, ClientInfo] = {} # dicionário de clientes conectados
        self.max_clients = max_clients # número máximo de clientes permitidos

        self.tcp_socket = None # socket TCP do servidor
        self.tcp_port = tcp_port # porta TCP do servidor

        self.udp_socket = None # socket UDP do servidor
        self.udp_port = udp_port # porta UDP do servidor

        self.running = False # flag para verificar se o servidor está rodando
        self.in_game = False # flag para verificar se o servidor está em jogo

        self.lock = threading.Lock() # lock para proteger o acesso ao dicionário de clientes

        self.player_spawn_points = [(32*8, 18*8),
                                    (16*8, 15*8),
                                    (8*8, 24*8),
                                    (40*8, 24*8)] # Posições de spawn do jogador

        self.weapon_spawn_points = [(8*8, 8*8),
                                    (40*8, 8*8),
                                    (40*8, 20*8),
                                    (8*8, 20*8),
                                    (16*8, 14*8),
                                    (32*8, 14*8)] # Posições de spawn das armas

    # * OK
    def get_my_ip(self):
        try:
            # Essa conexão descarta o IP do loopback e retorna o IP "real"
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.255.255.255", 1))  # não precisa existir
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    # * OK
    def start_server(self):
        try:
            self.accepting = True
            self.running = True

            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria um socket TCP
            self.tcp_socket.bind((self.host, self.tcp_port))
            self.tcp_socket.listen()
            self.tcp_port = self.tcp_socket.getsockname()[1] # pega a porta que o socket está escutando

            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # cria um socket UDP
            self.udp_socket.bind((self.host, self.udp_port))
            self.udp_port = self.udp_socket.getsockname()[1] # pega a porta que o socket está escutando

            # Cria uma thread para escutar novos clientes
            threading.Thread(target=self.listen_for_clients, daemon=True).start()
            threading.Thread(target=self.listen_udp_data, daemon=True).start() # cria uma nova thread para lidar com o cliente UDP
            threading.Thread(target=self.send_pings, daemon=True).start() # cria uma nova thread para manter o servidor ativo

            self.server_to_game_queue.put(f"SERVER_STARTED:{self.host};{self.tcp_port}") # envia uma mensagem para o processo do jogo que o servidor foi iniciado

        except Exception as e:
            self.server_to_game_queue.put(f"SERVER_START_ERROR:{type(e).__name__}") # envia uma mensagem para o processo do jogo que houve um erro ao iniciar o servidor
            self.stop_server()

    # * OK
    def listen_for_clients(self):
        while self.running:            
            try:
                client_tcp_socket, client_tcp_addr = self.tcp_socket.accept() # aceita um novo cliente TCP

                with self.lock:
                    if len(self.clients) >= self.max_clients: # verifica se o número máximo de clientes foi atingido
                        client_tcp_socket.sendall(b"SERVER_FULL|") # envia uma mensagem para o cliente que o servidor está cheio
                        client_tcp_socket.close() # fecha o socket TCP
                        continue
                    
                    ids = set(self.clients.keys()) # pega os ids dos clientes conectados
                    client_id = 0
                    for i in range(self.max_clients):
                        if i not in ids:
                            client_id = i
                            break
                    
                    self.clients[client_id] = ClientInfo(client_id, client_tcp_addr, client_tcp_socket) # cria um novo ClientInfo

                threading.Thread(target=self.listen_tcp_data, args=(client_id,), daemon=True).start() # cria uma nova thread para lidar com o cliente TCP

            except Exception as e:
                print(f"Error accepting client: {e}")

    # * OK
    def send_pings(self):
        while self.running:
            self.broadcast(f"PING:{time.monotonic()}|") # envia um PING para todos os clientes
            time.sleep(1) # espera 1 segundo        

    def listen_tcp_data(self, client_id):
        # pega o cliente da lista de clientes
        client = self.clients[client_id]

        # Envia os dados do server de jogo e recebe os dados de jogo do cliente
        client.tcp_socket.sendall(f"GAME_CONNECTION:{client_id};{self.udp_port}|".encode()) # envia os dados do servidor de jogo para o cliente TCP

        while self.running:
            try:
                data = client.tcp_socket.recv(1024) # recebe dados do cliente
                if not data:
                    break
                
                packets = data.split(b"|") # divide os dados recebidos em pacotes

                for packet in packets:
                    if not packet:
                        continue

                    message = packet.decode() # decodifica o pacote recebido
                    # print(f"Received message from client: {message}")

                    if message.startswith("PING:"):
                        _, time_stamp = message.split(":")
                        time_stamp = float(time_stamp)
                        ping = int((time.monotonic() - time_stamp) * 1000) # calcula o ping

                        # Envia o PING para o cliente
                        self.broadcast(f"UPDATE_PING:{client_id};{ping}|")

                    elif message.startswith("DISCONNECT"):
                        # desconecta o cliente
                        self.broadcast(f"REMOVE_PLAYER:{client_id}|", exclude_client_id=client_id) # envia para os outros clientes que o jogador foi removido
                        break

                    elif message.startswith("GAME_STARTED"):
                        random.shuffle(self.player_spawn_points)
                        with self.lock:
                            for id in self.clients.keys():
                                x, y = self.player_spawn_points[id]
                                
                                client.tcp_socket.sendall(f"ADD_GAME_PLAYER:{id};{x};{y}|".encode())

            except Exception as e:
                print(f"Error handling client {client_id}: {e}")
                break
        
        # Remove o cliente da lista de clientes
        if client_id in self.clients:
            if client.tcp_socket:
                try:
                    client.tcp_socket.shutdown(socket.SHUT_RDWR)
                    client.tcp_socket.close() # fecha o socket TCP

                except Exception as e:
                    print(f"Error closing client {client_id}: {e}")
            
            self.broadcast(f"REMOVE_PLAYER:{client_id}|", exclude_client_id=client_id) # envia para os outros clientes que o jogador foi removido
            del self.clients[client_id] # remove o cliente da lista de clientes

    def listen_udp_data(self):
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(1024) # recebe dados do cliente

                message = data.decode() # decodifica os dados recebidos
                # print(f"Received game data from client: {message}")

                if message.startswith("GAME_CONNECTION:"):
                    _, client_id = message.split(":")
                    client_id = int(client_id)

                    if client_id in self.clients: # verifica se o cliente existe
                        with self.lock:
                            client = self.clients[client_id]
                            client.udp_addr = addr # atualiza o endereço do cliente

                            for other_client_id, other_client in self.clients.items():
                                if other_client_id != client_id:
                                    client.tcp_socket.sendall(f"ADD_PLAYER:{other_client_id}|".encode()) # envia os dados dos clientes ja conectados para o novo cliente

                        self.broadcast(f"ADD_PLAYER:{client_id}|", exclude_client_id=client_id) # envia uma mensagem para todos os clientes que um novo player foi adicionado

                elif message.startswith("UPDATE_PLAYER:"):
                    _, info = message.split(":")
                    client_id = info.split(";")[0]

                    client_id = int(client_id)

                    self.broadcast(message, exclude_client_id=client_id, udp=True)

                elif message.startswith("ADD_PROJECTILE:"):
                    _, info = message.split(":")
                    client_id = info.split(";")[0]

                    client_id = int(client_id)

                    self.broadcast(message, exclude_client_id=client_id, udp=True)
                    
            except Exception as e:
                print(f"Error handling game data: {e}")
                break 
        
        self.stop_server() # fecha o servidor se houver um erro

    def broadcast(self, message, exclude_client_id=None, udp=False):
        with self.lock:
            clients_copy = self.clients.copy() # faz uma cópia do dicionário de clientes

        for client_id, client in clients_copy.items():
            if exclude_client_id is not None and client_id == exclude_client_id:
                continue

            try:
                if udp and client.udp_addr:
                    self.udp_socket.sendto(message.encode(), client.udp_addr) # envia dados para o cliente UDP
                else:
                    client.tcp_socket.sendall(message.encode()) # envia dados para o cliente TCP

            except Exception as e:
                print(f"Error broadcasting to client {client_id}: {e}")

    def stop_server(self):
        self.running = False
        self.accepting = False

        with self.lock:
            clients_copy = self.clients.copy() # faz uma cópia do dicionário de clientes
            self.clients.clear() # limpa o dicionário de clientes

        for client_id, client in clients_copy.items():
            try:
                if client.tcp_socket:
                    client.tcp_socket.close()

            except Exception as e:
                print(f"Error closing client {client_id}: {e}")

        if self.tcp_socket:
            try:
                self.tcp_socket.close() # fecha o socket TCP
            except Exception as e:
                print(f"Error closing lobby socket: {e}")

            self.tcp_socket = None
            self.tcp_port = 0

        if self.udp_socket:
            try:
                self.udp_socket.close() # fecha o socket UDP
            except Exception as e:
                print(f"Error closing game socket: {e}")

            self.udp_socket = None
            self.udp_port = 0

    def start_game(self):
        self.in_game = True
        threading.Thread(target=self.generate_weapon_pickup, daemon=True).start() # cria uma nova thread para gerar pickups de armas
        self.broadcast("START_GAME|")

    def generate_weapon_pickup(self):
        weapon_data = {
            0: {"ammo": 17, "reserve_ammo": 17 * 2}, # pistola
            1: {"ammo": 5, "reserve_ammo": 5 * 3}, # shotgun
            2: {"ammo": 5, "reserve_ammo": 5 * 2}, # rifle
            3: {"ammo": 30, "reserve_ammo": 30 * 2}, # assault rifle
        }
        
        while self.in_game:
            time.sleep(10) # espera 10 segundos para gerar o próximo pickup de arma
            weapon_type = random.randint(0, 3) # gera um tipo de arma aleatório
            weapon_spawn_point = self.weapon_spawn_points.pop(0) # remove o primeiro ponto de spawn da lista
            self.weapon_spawn_points.append(weapon_spawn_point) # adiciona o ponto de spawn no final da lista

            self.broadcast(f"ADD_WEAPON_PICKUP:{weapon_spawn_point[0]};{weapon_spawn_point[1]};{weapon_type};{weapon_data[weapon_type]['ammo']};{weapon_data[weapon_type]['reserve_ammo']};{10}|") # envia uma mensagem para todos os clientes que um novo pickup de arma foi adicionado


def start_server_process(server_to_game_queue: Queue, game_to_server_queue: Queue):
    server = Server(server_to_game_queue, game_to_server_queue)
    server.start_server()

    tickrate = 120
    tick_duration = 1 / tickrate

    pid_pai = os.getppid()

    while server.running:
        # Verifica se o processo pai ainda está ativo
        if os.getppid() != pid_pai:
            break
        
        start_time = time.monotonic()

        # Process incoming data from the server
        while not server.game_to_server_queue.empty():
            message = server.game_to_server_queue.get()
            print(f"Received from game: {message}")

            if message.startswith("STOP_SERVER"):
                server.broadcast("SERVER_STOPPED|")
                server.stop_server()
            
            elif message.startswith("START_GAME"):
                server.start_game()
        
        elapsed_time = time.monotonic() - start_time
        sleep_time = tick_duration - elapsed_time
        if sleep_time > 0:
            time.sleep(sleep_time)