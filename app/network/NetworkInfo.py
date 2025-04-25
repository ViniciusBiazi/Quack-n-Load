class ClientPlayerInfo:
    def __init__(self, id, nickname=None):
        self.id = id
        self.nickname = nickname if nickname else f"Player {id}"
        self.ping = 0
        self.dead = False

        self.wins = 0
        self.kills = 0
        self.deaths = 0

class ServerPlayerInfo:
    def __init__(self, id, tcp_addr, tcp_socket, nickname=None):
        self.id = id
        self.nickname = nickname if nickname else f"Player {id}"
        self.ping = 0
        self.dead = False

        self.wins = 0
        self.kills = 0
        self.deaths = 0

        # comunicaçao do lobby
        self.tcp_addr = tcp_addr
        self.tcp_socket = tcp_socket

        # comunicaçao do jogo
        self.udp_addr = None

class ServerWeaponPickupInfo:
    def __init__(self, id, remove_timer):
        self.id = id
        self.remove_timer = remove_timer

class ServerProjectileInfo:
    def __init__(self, id, damage, owner_id):
        self.id = id
        self.damage = damage
        self.owner_id = owner_id
