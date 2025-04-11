import pyxel
from pyxel import *

from models.players.Player import Player

class PlayerGui():
    def __init__(self, x=0, y=0, player: Player = None):
        self.player = player
        self.x = x
        self.y = y

        self.row_width = 50
        self.row_height = 11
        self.row_offset = 10

        self.gui_icons = {
            "health": (64, 16, 7, 7, 6),
            "ammo": [(72, 24, 7, 7, 6), # pistol
                     (64, 24, 7, 7, 6), # shotgun
                     (72, 16, 7, 7, 6), # rifle
                     (72, 16, 7, 7, 6)], # assault rifle
            "reload": (88, 8, 7, 7, 6), # reload icon
        }

        self.background_color = 7
        self.border_color = 0
        self.color = 0
        
    def draw_row(self, row_number: int, icon: tuple, info: str):
        rect(self.x, self.y + self.row_offset * row_number, self.row_width, self.row_height, self.background_color)
        rectb(self.x, self.y + self.row_offset * row_number, self.row_width, self.row_height, self.border_color)
        blt(self.x + 2, self.y + 2 + self.row_offset * row_number, 0,  *icon)
        text(self.x + 12, self.y + 3 + self.row_offset * row_number, info, self.color)

    def draw(self):
        # Draw health
        self.draw_row(0, self.gui_icons["health"], f"{self.player.health}/{self.player.max_health}")

        # Draw ammo
        if self.player.weapon:
            weapon_index = self.player.weapon.weapon_type
            if self.player.weapon.is_reloading:
                # Draw reload icon
                self.draw_row(1, self.gui_icons["reload"], f"{self.player.weapon.ammo}/{self.player.weapon.reserve_ammo}")
            else:
                self.draw_row(1, self.gui_icons["ammo"][weapon_index], f"{self.player.weapon.ammo}/{self.player.weapon.reserve_ammo}")