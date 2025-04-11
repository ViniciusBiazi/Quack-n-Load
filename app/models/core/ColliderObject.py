import pyxel
from pyxel import *

from models.core.Entity import Entity

class ColliderObject(Entity):
    """Classe que representa um objeto colisor 2D, usado para detectar colisões entre objetos.

    Atributos:
        x (int): Posição X do objeto colisor.
        y (int): Posição Y do objeto colisor.
        width (int): Largura do objeto colisor.
        height (int): Altura do objeto colisor.
        x2 (int): Posição X da borda direita do objeto colisor.
        y2 (int): Posição Y da borda inferior do objeto colisor.
        color (int): Cor do objeto colisor.

    Métodos:
        update_collider(x, y): Atualiza a posição do objeto colisor.
        draw(): Desenha o objeto colisor na tela.
        check_collision_rect(other: ColliderObject) -> bool: Verifica colisão retangular com outro objeto colisor.
        check_collision_left(other: ColliderObject) -> bool: Verifica colisão à esquerda com outro objeto colisor.
        check_collision_right(other: ColliderObject) -> bool: Verifica colisão à direita com outro objeto colisor.
        check_collision_bottom(other: ColliderObject) -> bool: Verifica colisão na parte inferior com outro objeto colisor.
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.x2 = x + width  # Cache da borda direita
        self.y2 = y + height  # Cache da borda inferior

    def update_collider(self, x, y):
        self.set_position(x, y)

        self.x2 = x + self.width
        self.y2 = y + self.height

    def check_collision_rect(self, other: 'ColliderObject') -> bool:
        return (
            self.x < other.x2 and
            self.x2 > other.x and
            self.y < other.y2 and
            self.y2 > other.y
        )

    def check_collision_left(self, other: 'ColliderObject') -> bool:
        return (
            self.check_collision_rect(other) and
            self.x < other.x2 and
            self.x2 > other.x2
        )

    def check_collision_right(self, other: 'ColliderObject') -> bool:
        return (
            self.check_collision_rect(other) and
            self.x2 > other.x and
            self.x < other.x
        )

    def check_collision_bottom(self, other: 'ColliderObject') -> bool:
        return (
            self.check_collision_rect(other) and
            self.y < other.y2 and
            self.y2 > other.y
        )