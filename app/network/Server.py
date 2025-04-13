import socket
import threading
import time
import json

from network.ClientInfo import ClientInfo

class Server:
    def __init__(self, host="0.0.0.0", tcp_port=0, udp_port=0, max_clients=4):
        self.host = host if host != "0.0.0.0" else self.get_my_ip()

        self.clients: dict[int, ClientInfo] = {} # dicionário de clientes conectados
        self.max_clients = max_clients # número máximo de clientes permitidos

        self.tcp_socket = None
        self.tcp_port = tcp_port

        self.udp_socket = None
        self.udp_port = udp_port

        self.accepting = False
        self.running = False

        self.lock = threading.Lock()

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

    def start_server(self):
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
        threading.Thread(target=self.send_pings, daemon=True).start() # cria uma nova thread para enviar PINGs

    def listen_for_clients(self):
        while self.accepting and self.running:
            try:
                client_tcp_socket, client_tcp_addr = self.tcp_socket.accept() # aceita um novo cliente TCP

                client_id = len(self.clients) # ID do cliente

                self.clients[client_id] = ClientInfo(client_id, client_tcp_addr, client_tcp_socket) # cria um novo ClientInfo

                if self.max_clients and len(self.clients) >= self.max_clients:
                    self.accepting = False

                threading.Thread(target=self.listen_tcp_data, args=(client_id,), daemon=True).start() # cria uma nova thread para lidar com o cliente TCP

            except Exception as e:
                print(f"Error accepting client: {e}")

        print("No longer accepting new clients.")

    def listen_tcp_data(self, client_id):
        client = self.clients[client_id]

        # Envia os dados do server de jogo e recebe os dados de jogo do cliente
        client.tcp_socket.sendall(f"START_GAME_CONNECTION:{client_id};{self.udp_port}|".encode()) # envia os dados do servidor de jogo para o cliente TCP

        while self.running:
            try:
                data = client.tcp_socket.recv(1024) # recebe dados do cliente
                if not data:
                    break
                
                packets = data.split(b"|") # divide os dados recebidos em pacotes
                for packet in packets:
                    if not packet:
                        continue

                    # Processa cada pacote
                    self.process_tcp_data(packet, client_id) # processa os dados recebidos do cliente

            except Exception as e:
                print(f"Error handling client {client_id}: {e}")
                break

            # time.sleep(0.01)
        
        # Remove o cliente da lista de clientes
        if client_id in self.clients:
            del self.clients[client_id]

    def process_tcp_data(self, data, client_id):
        start = time.time() # marca o tempo de início
        try:
            message = data.decode("utf-8") # decodifica os dados recebidos
            # print(f"Received message from client: {message}")

            if message.startswith("PING:"):
                _, timestamp = message.split(":")

                timestamp = float(timestamp)

                if client_id in self.clients:
                    client = self.clients[client_id]
                    with self.lock:
                        client.ping = int((time.monotonic() - timestamp) * 1000) # calcula o ping

                    self.broadcast(f"UPDATE_PING:{client_id};{client.ping}|") # envia o ping atualizado para todos os clientes
                    print(f"Client {client_id} ping: {client.ping}ms")

            # elif message.startswith("DISCONNECT"):
            #     self.broadcast(f"REMOVE_PLAYER:{client_id}|", exclude_client_id=client_id)

            #     try:
            #         self.clients[client_id].tcp_socket.shutdown(socket.SHUT_RDWR) # fecha o socket TCP
            #         self.clients[client_id].tcp_socket.close()

            #     except Exception as e:
            #         print(f"Error closing client {client_id}: {e}")

            #     finally:
            #         del self.clients[client_id]

        except Exception as e:
            print(f"Error processing client data: {e}")

        end = time.time()
        print(f"Processing time server: {end - start:.6f} seconds")

    def send_pings(self):
        while self.running:
            self.broadcast(f"PING:{time.monotonic()}|") # envia um PING para todos os clientes
            time.sleep(1)

    def listen_udp_data(self):
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(1024) # recebe dados do cliente

                # Processa os dados recebidos
                self.process_udp_data(data, addr)

            except Exception as e:
                print(f"Error handling game data: {e}")
                break
            
            time.sleep(0.01)

    def process_udp_data(self, data, addr):
        try:
            message = data.decode("utf-8") # decodifica os dados recebidos
            # print(f"Received game data from client: {message}")

            if message.startswith("HELLO:"):
                print(f"Received HELLO from {addr}")
                _, client_id = message.split(":")
                client_id = int(client_id)

                if client_id in self.clients:
                    client = self.clients[client_id]
                    client.udp_addr = addr # atualiza o endereço do cliente

                    for other_client_id, other_client in self.clients.items():
                        if other_client_id != client_id:
                            client.tcp_socket.sendall(f"ADD_PLAYER:{other_client_id};{other_client.nickname}|".encode()) # envia os dados do cliente para o cliente UDP

                    self.broadcast(f"ADD_PLAYER:{client_id};{client.nickname}|", exclude_client_id=client_id) # envia uma mensagem para todos os clientes que um novo player foi adicionado

            # elif message.startswith("PLAYER_UPDATE:"):
            #     _, info = message.split(":")
            #     client_id, x, y, sprite = info.split(";")

            #     client_id = int(client_id)
            #     x = float(x)
            #     y = float(y)
            #     sprite = tuple(map(int, sprite.strip("()").split(","))) # converte a string em uma tupla

            #     if client_id in self.clients:
            #         client = self.clients[client_id]
            #         client.x = x
            #         client.y = y
            #         client.sprite = sprite

            #         self.broadcast(f"PLAYER_UPDATE:{client_id};{x};{y};{sprite}", exclude_client_id=client_id, udp=True) # envia uma mensagem para todos os clientes que o jogador foi atualizado
        except Exception as e:
            print(f"Error processing game data: {e}")

    def broadcast(self, message, exclude_client_id=None, udp=False):
        for client_id, client in self.clients.items():
            if exclude_client_id and client_id == exclude_client_id:
                continue

            try:
                if udp and client.udp_addr:
                    self.udp_socket.sendto(message.encode(), client.udp_addr) # envia dados para o cliente UDP
                else:
                    client.tcp_socket.sendall(message.encode()) # envia dados para o cliente TCP

            except Exception as e:
                print(f"Error broadcasting to client {client_id}: {e}")

    # def stop_server(self):
    #     self.broadcast("SERVER_SHUTDOWN|")
    #     self.running = False
    #     self.accepting = False

    #     for client_id, client in self.clients.items():
    #         try:
    #             if client.tcp_socket:
    #                 client.tcp_socket.shutdown(socket.SHUT_RDWR) # fecha o socket TCP
    #                 client.tcp_socket.close()

    #         except Exception as e:
    #             print(f"Error closing client {client_id}: {e}")
        
    #     self.clients.clear() # limpa o dicionário de clientes

    #     if self.tcp_socket:
    #         try:
    #             self.tcp_socket.shutdown(socket.SHUT_RDWR) # fecha o socket TCP
    #             self.tcp_socket.close() # fecha o socket TCP
    #         except Exception as e:
    #             print(f"Error closing lobby socket: {e}")

    #         self.tcp_socket = None
    #         self.tcp_port = 0

    #     if self.udp_socket:
    #         try:
    #             self.udp_socket.close() # fecha o socket UDP
    #         except Exception as e:
    #             print(f"Error closing game socket: {e}")

    #         self.udp_socket = None
    #         self.udp_port = 0

    # def start_game(self):
    #     x, y = 10, 10
    #     for client_id, client in self.clients.items():
    #         client.x = x
    #         client.y = y

    #         x += 50
    #         y += 0
    #         client.tcp_socket.sendall(f"POSITION_PLAYER:{client_id};{client.x};{client.y}|".encode())

    #     self.broadcast(f"START_GAME|") # envia uma mensagem para todos os clientes que o jogo começou