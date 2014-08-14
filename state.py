from tileset_editor.generalized_settings import TOSetting

import json
import os

class State:
    def __init__(self, grid_step=[8,8], map_size=[64, 64], data=None):
        self.scale = [1, 1]
        self.left_press_start = None
        self.shift_pressed = False
        self.pointer_position = None
        self.selected_sprite = None

        if data == None:
            self.atlas = None
            self.grid_step = grid_step
            self.sprites = []
            self.images = []
            self.metas = []
            self.map_size = map_size
        else:
            self.deserialize(data)

    def get_sprites(self):
        return self.sprites

    def get_image_by_name(self, n):
        for i in self.images:
            if i.name == n:
                return i
        return None

    def imported(self, data):
        if data["format"] == 1:
            if data["type"] == "tset":
                image_path = data["image"]
                self.atlas = cairo.ImageSurface.create_from_png(image_path)
                self.images = [Image(self.atlas, i) for i in data["images"]]
                self.sprites = [Sprite(self, s) for s in data["sprites"]]
            else:
                print "Unknown file format:", data["type"]
        else:
            print "Unknown data format:", data["format"]


# service methods

    def get_settings_list(self):
        settings_lst = [TOSetting("int", 0, None, self.grid_step[0], "Grid x step, px: ", self.set_grid_x_s),
                        TOSetting("int", 0, None, self.grid_step[1], "Grid y step, px: ", self.set_grid_y_s),
                        TOSetting("int", 0, None, self.map_size[0], "Map size x, px: ", self.set_map_size_x_s),
                        TOSetting("int", 0, None, self.map_size[1], "Map size y, px: ", self.set_map_size_y_s)]
        return settings_lst

    def set_grid_x_s(self, setting):
        self.grid_step[0] = setting.new_value

    def set_grid_y_s(self, setting):
        self.grid_step[1] = setting.new_value

    def set_map_size_x_s(self, setting):
        self.map_size[0] = setting.new_value

    def set_map_size_y_s(self, setting):
        self.map_size[1] = setting.new_value

    def export(self, path):
        pass

    def serialize(self):
        return {"type": "state", "grid_step": self.grid_step, "atlas_size": self.atlas_size, "images": [i.serialize() for i in self.images], "sprites": [s.serialize() for s in self.sprites]}

    def deserialize(self, data):
        self.grid_step = data["grid_step"]
        self.atlas_size = data["atlas_size"]
        self.images = [Image(data=i) for i in data["images"]]
        self.sprites = [Sprite(state=self, data=s) for s in data["sprites"]]
    
    def set(self, state):
        self = state

state = State()
