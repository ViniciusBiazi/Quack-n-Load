import pyxel
from pyxel import *

class Entity:
    """Classe base para objetos do jogo.

    Atributos:
        x (int): Posição X do objeto.
        y (int): Posição Y do objeto.
        width (int): Largura do objeto.
        height (int): Altura do objeto.
        center_x (int): Posição X do centro do objeto.
        center_y (int): Posição Y do centro do objeto.
    
    Métodos:
        set_position(x, y): Atualiza a posição do objeto.
        set_center_position(x, y): Atualiza a posição do objeto com base nas coordenadas do centro.
        update_center(x, y): Atualiza as coordenadas do centro do objeto.
        draw(): Desenha o objeto na tela.
    """
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.center_x = x + width // 2
        self.center_y = y + height // 2

        # Calculate the center coordinates
        self.update_center()

    def set_position(self, x: int, y: int):
        # Update the position of the entity
        self.x = x
        self.y = y
        self.update_center()

    def set_center_position(self, x: int, y: int):
        # Update the position of the entity based on center coordinates
        self.x = x - self.width // 2
        self.y = y - self.height // 2
        self.update_center()

    def update_center(self):
        # Update the center coordinates of the entity
        self.center_x = self.x + self.width // 2
        self.center_y = self.y + self.height // 2

    def draw(self):
        """ Desenha o objeto na tela para fins de depuração. """
        rectb(self.x, self.y, self.width, self.height, 7)
        rectb(self.center_x, self.center_y, 1, 1, 7)