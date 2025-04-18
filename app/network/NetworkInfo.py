import time

class PlayerInfo:
    def __init__(self, id, nickname=None):
        self.id = id
        self.nickname = nickname if nickname else f"Player {id}"
        self.ping = 0

        # dados do jogador
        self.x = 0
        self.y = 0
        self.health = 100
        self.sprite = (0, 0, 0, 0)

        # dados da arma se existir
        self.weapon: WeaponInfo = None

class WeaponInfo:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.sprite = (0, 0, 0, 0)
        self.rotation = 0

class ClientInfo(PlayerInfo):
    def __init__(self, id, tcp_addr, tcp_socket, nickname=None):
        super().__init__(id, nickname)
        
        # comunicaçao do lobby
        self.tcp_addr = tcp_addr
        self.tcp_socket = tcp_socket

        # comunicaçao do jogo
        self.udp_addr = None

class ServerWeaponPickupInfo:
    def __init__(self, id, remove_timer):
        self.id = id
        self.remove_timer = remove_timer
