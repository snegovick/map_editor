from generalized_settings import TOSetting
from image import *
from sprite import *

import json
import os

class State:
    def __init__(self, grid_step=[8,8], atlas_size=512, data=None):
        self.scale = [1, 1]
        self.left_press_start = None
        self.shift_pressed = False
        self.pointer_position = None
        self.selected_images = []
        self.selected_sprite = None

        if data == None:
            self.grid_step = grid_step
            self.images = []
            self.sprites = []
            self.atlas_size = 512
        else:
            self.deserialize(data)

    def unselect_sprite(self):
        self.selected_sprite = None

    def get_selected_sprite(self):
        return self.selected_sprite

    def set_selected_sprite(self, s):
        self.selected_sprite = s

    def get_atlas_size(self):
        return self.atlas_size

    def get_sprites(self):
        return self.sprites

    def add_sprite(self, s):
        self.sprites.append(s)

    def remove_sprite(self, s):
        if s in self.sprites:
            self.sprites.remove(s)

    def set_shift_pressed(self):
        self.shift_pressed = True

    def reset_shift_pressed(self):
        self.shift_pressed = False

    def get_shift_pressed(self):
        return self.shift_pressed

    def set_pointer_position(self, pt):
        self.pointer_position = pt
        
    def get_pointer_position(self):
        return self.pointer_position

    def add_im_to_selected(self, im):
        self.selected_images.append(im)
        im.set_selected()

    def remove_im_from_selected(self, im):
        if im in self.selected_images:
            self.selected_images.remove(im)
        im.unselect()

    def get_selected_images(self):
        return self.selected_images

    def unselect_all_images(self):
        for i in self.selected_images:
            i.unselect()
        self.selected_images = []

    def set_left_press_start(self, pt):
        if self.left_press_start == None:
            self.left_press_start = [0,0]
        self.left_press_start[0] = pt[0]
        self.left_press_start[1] = pt[1]

    def reset_left_press_start(self):
        self.left_press_start = None

    def get_left_press_start(self):
        return self.left_press_start

    def set_screen_offset(self, offset):
        pass

    def get_offset(self):
        return [0,0]

    def get_grid_step(self):
        return self.grid_step

    def set_scale(self, scale):
        self.scale[0] = scale[0]
        self.scale[1] = scale[1]

    def get_scale(self):
        return self.scale

    def get_images(self):
        return self.images

    def get_image_by_name(self, name):
        img = None
        for i in self.images:
            if i.name == name:
                img = i
        return img

    def load_image(self, path):
        img = Image(path, os.path.basename(path))
        self.images.append(img)

# service methods

    def get_settings_list(self):
        settings_lst = [TOSetting("int", 0, None, self.grid_step[0], "Grid x step, px: ", self.set_grid_x_s),
                        TOSetting("int", 0, None, self.grid_step[1], "Grid y step, px: ", self.set_grid_y_s),
                        TOSetting("int", 0, None, self.atlas_size, "Atlas size, px: ", self.set_atlas_size_s)]
        return settings_lst

    def set_grid_x_s(self, setting):
        self.grid_step[0] = setting.new_value

    def set_grid_y_s(self, setting):
        self.grid_step[1] = setting.new_value

    def set_atlas_size_s(self, setting):
        self.atlas_size = setting.new_value

    def export(self, path):
        image_path = path+".png"
        f = open(path+".json", "w")
        f.write(json.dumps({"format": 1, "type": "tset", "image": image_path, "atlas_size": self.atlas_size, "images": [i.export() for i in self.images], "sprites": [s.export() for s in self.sprites]}))
        f.close()
        
        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.atlas_size), int(self.atlas_size))
        cr = cairo.Context(cr_surf)

        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.rectangle(0, 0, int(self.atlas_size), int(self.atlas_size))
        cr.fill()

        for i in self.images:
            s = i.get_selected()

            if s:
                i.unselect()

            i.draw(cr)

            if s:
                i.set_selected()

        cr_surf.write_to_png(image_path)

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
