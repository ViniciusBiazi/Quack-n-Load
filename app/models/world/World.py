import pyxel
from pyxel import *

from models.core.ColliderObject import ColliderObject

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Índice do tilemap
        self.tilemap = 0

        # Carrega as colisões do tilemap
        self.grounds = [
            ColliderObject(0, self.height-8, self.width, 8), # Chão

            ColliderObject(5*8+2, 13*8, 6*8-4, 3), # Plataforma
            ColliderObject(21*8+2, 13*8, 6*8-4, 3), # Plataforma
            ColliderObject(37*8+2, 13*8, 6*8-4, 3), # Plataforma

            ColliderObject(13*8+2, 19*8, 6*8-4, 3), # Plataforma
            ColliderObject(29*8+2, 19*8, 6*8-4, 3), # Plataforma

            ColliderObject(5*8+2, 25*8, 6*8-4, 3), # Plataforma
            ColliderObject(21*8+2, 25*8, 6*8-4, 3), # Plataforma
            ColliderObject(37*8+2, 25*8, 6*8-4, 3), # Plataforma
        ]

        self.walls = [ColliderObject(0, 0, 8, self.height),  # Parede esquerda
                      ColliderObject(self.width-8, 0, 8, self.height)] # Parede direita

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

    def draw(self):
        """ Desenha o tilemap na tela """
        pyxel.bltm(0, 0, self.tilemap, 0, 0, self.width, self.height)

        # for ground in self.grounds:
        #     ground.draw()
        
        # for wall in self.walls:
        #     wall.draw()