import pyxel
from pyxel import *

from models.core.ColliderObject import ColliderObject
from models.core.PhysicsObject import PhysicsObject

from models.world.World import World

class PhysicsManager:
    """ Gerencia a física dos objetos no jogo, incluindo colisões e atualizações de movimento.

    Atributos:
        physics_objects (list[PhysicsObject]): Lista de objetos físicos a serem atualizados.
        wall_objects (list[ColliderObject]): Lista de objetos de parede para verificar colisões.
        ground_objects (list[ColliderObject]): Lista de objetos de chão para verificar colisões.
    
    Métodos:
        update_physics_engine(delta_time: float): Atualiza a física dos objetos e verifica colisões.
        add_physics_object(physics_object: PhysicsObject): Adiciona um objeto físico à lista.
        add_wall_object(wall_object: ColliderObject): Adiciona um objeto de parede à lista.
        add_ground_object(ground_object: ColliderObject): Adiciona um objeto de chão à lista.
        remove_physics_object(physics_object: PhysicsObject): Remove um objeto físico da lista.
        remove_wall_object(wall_object: ColliderObject): Remove um objeto de parede da lista.
        remove_ground_object(ground_object: ColliderObject): Remove um objeto de chão da lista.
        check_ground_collision(physics_object: PhysicsObject, ground_objects: list[ColliderObject]): Verifica colisão com o chão.
        check_wall_collision(physics_object: PhysicsObject, wall_objects: list[ColliderObject]): Verifica colisão com as paredes.
    """
    def __init__(self, world: World):
        self.physics_objects: list[PhysicsObject] = []

        self.wall_objects: list[ColliderObject] = world.walls
        self.ground_objects: list[ColliderObject] = world.grounds
    
    def update_physics_manager(self, delta_time: float):
        for physics_object in self.physics_objects:
            physics_object.update_physics(delta_time)

            self.check_ground_collision(physics_object, self.ground_objects)
            self.check_wall_collision(physics_object, self.wall_objects)

    def draw(self):
        """ Desenha os objetos físicos, paredes e chão para debugging. """
        for wall in self.wall_objects:
            wall.draw()
        
        for ground in self.ground_objects:
            ground.draw()

        for physics_object in self.physics_objects:
            physics_object.draw()

    def add_physics_object(self, physics_object: PhysicsObject):
        self.physics_objects.append(physics_object)

    def remove_physics_object(self, physics_object: PhysicsObject):
        if physics_object in self.physics_objects:
            self.physics_objects.remove(physics_object)
        
    def check_ground_collision(self, physics_object: PhysicsObject, ground_objects: list[ColliderObject]):
        """ Verifica colisão com o chão e atualiza a posição do objeto físico.
        Se o objeto físico estiver colidindo com o chão, ele é posicionado acima do chão e sua velocidade vertical é zerada.
        Se não estiver colidindo, a gravidade é aplicada.
        """
        if physics_object.ascending:
            return
        
        if physics_object.on_ground:
            if physics_object.ground_collider.check_collision_bottom(physics_object.last_ground):
                return
            
            physics_object.on_ground = False
            physics_object.last_ground = None
        
        for ground in ground_objects:
            if physics_object.ground_collider.check_collision_bottom(ground):
                physics_object.on_ground = True
                physics_object.velocity_y = 0  # Reseta a velocidade vertical
                physics_object.set_position(physics_object.x, ground.y - physics_object.height)
                physics_object.last_ground = ground
                return

    def check_wall_collision(self, physics_object: PhysicsObject, wall_objects: list[ColliderObject]):
        """ Verifica colisão com as paredes e atualiza a posição do objeto físico.
        Se o objeto físico estiver colidindo com uma parede, sua velocidade horizontal é zerada e sua posição é ajustada.
        """
        if physics_object.velocity_x == 0:
            return

        for wall in wall_objects:
            if physics_object.entity_collider.check_collision_left(wall):
                physics_object.velocity_x = 0
                physics_object.set_position(wall.x2, physics_object.y)
                physics_object.last_wall = wall
                return
            
            elif physics_object.entity_collider.check_collision_right(wall):
                physics_object.velocity_x = 0
                physics_object.set_position(wall.x - physics_object.width, physics_object.y)
                physics_object.last_wall = wall
                return