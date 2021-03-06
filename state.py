from tileset_editor.generalized_settings import TOSetting
from tileset_editor import utils

import json
import os
import cairo

from image import Image
from sprite import Sprite
from layer import Layer, LayerType

DEFAULT_SCREEN_SIZE = [1024, 768]

class State:
    def __init__(self, grid_step=[32,32], map_size=[64, 64], screen_size=None, data=None):
        self.scale = [1, 1]
        self.left_press_start = None
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.pointer_position = None
        self.__total_offset = (0,0)
        self.__screen_offset = (0,0)
        self.__base_offset = (0,0)
        self.put_lo = False
        self.active_layer = None
        self.selection_mode = False
        self.selection_box = [0,0,0,0]
        self.prev_selection_box = [0,0,0,0]

        if data == None:
            self.atlas = None
            self.tileset_path = None
            self.grid_step = grid_step
            self.sprites = []
            self.images = []
            self.layers = []
            self.map_size = map_size
            if screen_size == None:
                self.screen_size = DEFAULT_SCREEN_SIZE

        else:
            self.deserialize(data)

    def is_selection_mode(self):
        return self.selection_mode

    def set_selection_mode(self):
        self.selection_mode = True

    def set_selection_box_origin(self, x, y):
        self.selection_box[0] = x
        self.selection_box[1] = y
        self.update_selection_box(x, y)
        self.prev_selection_box = self.selection_box[:]

    def update_selection_box(self, x, y):
        self.prev_selection_box = self.selection_box[:]
        self.selection_box[2] = x
        self.selection_box[3] = y

    def get_selection_box(self):
        return self.selection_box

    def get_update_selection_box_selection(self):
        return True

    def unset_selection_mode(self):
        self.selection_mode = False
        self.selection_box = [0,0,0,0]

    def get_sprite_by_name(self, n):
        for s in self.sprites:
            if s.name == n:
                return s

    def get_active_layer(self):
        return self.active_layer

    def set_active_layer(self, l):
        self.active_layer = l

    def get_layers(self):
        return self.layers

    def add_layer(self, name, layer_type):
        self.layers.append(Layer(name, layer_type))

    def set_put_layer_object(self):
        self.put_lo = True

    def unset_put_layer_object(self):
        self.put_lo = False

    def get_put_layer_object(self):
        return self.put_lo

    def get_shift_pressed(self):
        return self.shift_pressed

    def set_shift_pressed(self):
        self.shift_pressed = True

    def unset_shift_pressed(self):
        self.shift_pressed = False

    def get_ctrl_pressed(self):
        return self.ctrl_pressed

    def set_ctrl_pressed(self):
        self.ctrl_pressed = True

    def unset_ctrl_pressed(self):
        self.ctrl_pressed = False

    def set_left_press_start(self, ps):
        if self.left_press_start == None:
            self.left_press_start = [0,0]
        self.left_press_start[0] = ps[0]
        self.left_press_start[1] = ps[1]

    def unset_left_press_start(self):
        self.left_press_start = None

    def get_left_press_start(self):
        return self.left_press_start

    def set_pointer_position(self, p):
        self.pointer_position = p

    def get_pointer_position(self):
        return self.pointer_position

    def set_screen_offset(self, offset):
        if self.__screen_offset != offset:
            self.__screen_offset = offset
            self.__total_offset = (self.__base_offset[0]+self.__screen_offset[0], self.__base_offset[1]+self.__screen_offset[1])

    def get_scale(self):
        return self.scale

    def set_scale(self, scale):
        self.scale[0] = scale[0]
        self.scale[1] = scale[1]

    def get_screen_size(self):
        return self.screen_size

    def get_offset(self):
        return self.__total_offset

    def get_base_offset(self):
        return self.__base_offset

    def set_base_offset(self, offset):
        self.__base_offset = offset
        self.__total_offset = (self.__base_offset[0]+self.__screen_offset[0], self.__base_offset[1]+self.__screen_offset[1])

    def get_sprites(self):
        return self.sprites

    def get_map_size_px(self):
        return [gs * ms for gs, ms in zip(self.grid_step, self.map_size)]

    def get_grid_step(self):
        return self.grid_step

    def get_image_by_name(self, n):
        for i in self.images:
            if i.name == n:
                return i
        return None

    def imported(self, data):
        print "data:", data
        if data["format"] == 1:
            if data["type"] == "tset":
                self.image_path = data["image"]
                self.atlas = cairo.ImageSurface.create_from_png(self.image_path)
                self.images = [Image(self.atlas, i) for i in data["images"].values()]
                self.sprites = [Sprite(self, s) for s in data["sprites"].values()]
            else:
                print "Unknown file format:", data["type"]
        else:
            print "Unknown data format:", data["format"]

    def load_tileset(self, path):
        self.tileset_path = path
        f = open(path, "r")
        data = f.read()
        f.close()
        self.imported(json.loads(data))


# service methods

    def get_settings_list(self):
        settings_lst = [TOSetting("int", 0, None, self.grid_step[0], "Grid x step, px: ", self.set_grid_x_s),
                        TOSetting("int", 0, None, self.grid_step[1], "Grid y step, px: ", self.set_grid_y_s),
                        TOSetting("int", 0, None, self.map_size[0], "Map size x, px: ", self.set_map_size_x_s),
                        TOSetting("int", 0, None, self.map_size[1], "Map size y, px: ", self.set_map_size_y_s),
                        TOSetting("int", 0, 9999, self.screen_size[0], "Screen size x, px: ", self.set_screen_size_x_s),
                        TOSetting("int", 0, 9999, self.screen_size[1], "Screen size y, px: ", self.set_screen_size_y_s)]
        return settings_lst

    def set_grid_x_s(self, setting):
        self.grid_step[0] = int(setting.new_value)

    def set_grid_y_s(self, setting):
        self.grid_step[1] = int(setting.new_value)

    def set_screen_size_x_s(self, setting):
        self.screen_size[0] = int(setting.new_value)

    def set_screen_size_y_s(self, setting):
        self.screen_size[1] = int(setting.new_value)

    def set_map_size_x_s(self, setting):
        self.map_size[0] = int(setting.new_value)
        self.mw.widget_hscroll.set_range(-self.map_size[0]*self.grid_step[0], self.map_size[0]*self.grid_step[0])

    def set_map_size_y_s(self, setting):
        self.map_size[1] = int(setting.new_value)
        self.mw.widget_vscroll.set_range(-self.map_size[1]*self.grid_step[1], self.map_size[1]*self.grid_step[1])

    def export(self, path):
        if path[-4:] == ".png":
            path = path[:-5]
        elif path[-5:] == ".json":
            path = path[:-5]

        image_path = path+".png"
        
        f = open(path+".json", "w")
        sprites = {}
        for s in self.sprites:
            sprites[s.name] = s.export()
        images = {}
        for i in self.images:
            images[i.name] = i.export()

        layers = {}
        for l in self.layers:
            layers[l.name] = l.export()
        f.write(json.dumps({"format": 1, "type": "map", "atlas_path": os.path.relpath(self.image_path), "layers": layers, "map_size": self.map_size, "grid_step": self.grid_step, "sprites": sprites, "images": images, "screen_size": self.screen_size}))
        f.close()

        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.map_size[1]*self.grid_step[0]), int(self.map_size[1]*self.grid_step[1]))
        cr = cairo.Context(cr_surf)

        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.rectangle(0, 0, int(self.map_size[1]*self.grid_step[0]), int(self.map_size[1]*self.grid_step[1]))
        cr.fill()

        for l in self.layers:
            if l.get_layer_type() == LayerType.sprite:
                for p in l.get_proxy_lst():
                    selected = p.get_selected()
                    if selected:
                        p.unset_selected()
                    
                    p.draw(cr, 1.0)

                    if selected:
                        p.set_selected()

        cr_surf.write_to_png(image_path)


    def serialize(self):
        return {"format": 1, "type": "state", "tileset_path": os.path.relpath(self.tileset_path), "layers": [l.serialize() for l in self.layers], "map_size": self.map_size, "grid_step": self.grid_step}

    def deserialize(self, data):
        self.map_size = data["map_size"]
        self.grid_step = data["grid_step"]
        if ("screen_size" in data):
            self.screen_size = data["screen_size"]
        else:
            self.screen_size = DEFAULT_SCREEN_SIZE

        self.mw.widget_vscroll.set_range(-self.map_size[1]*self.grid_step[1], self.map_size[1]*self.grid_step[1])
        self.mw.widget_hscroll.set_range(-self.map_size[0]*self.grid_step[0], self.map_size[0]*self.grid_step[0])
        if data["tileset_path"] != None:
            self.load_tileset(data["tileset_path"])
        self.layers = [Layer(state=self, data=l) for l in data["layers"]]
        self.mw.update_general_settings()
    
    def set(self, state):
        self = state

state = State()
