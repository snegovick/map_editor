from tileset_editor import utils

import time

class Proxy:
    def __init__(self, sprite=None, position=None, data=None):
        self.animation_timer = time.time()
        self.animation_frame = 0
        self.is_selected = False
        if data == None:
            self.position = position
            self.sprite = sprite
            self.frame = 0
            self.animated = False
            self.frame_time = 10
        self.dimensions = self.sprite.get_images()[0].get_dimensions()
        ex = self.position[0]+self.dimensions[0]
        ey = self.position[1]+self.dimensions[1]
        self.aabb = utils.AABB(self.position[0], self.position[1], ex, ey)

    def get_selected(self):
        return self.is_selected

    def set_selected(self):
        self.is_selected = True

    def unset_selected(self):
        self.is_selected = False

    def point_in_aabb(self, pt):
        return self.aabb.point_in_aabb(pt)

    def get_position(self):
        return self.position

    def set_position(self, p):
        self.position[0] = p[0]
        self.position[1] = p[1]
        ex = self.position[0]+self.dimensions[0]
        ey = self.position[1]+self.dimensions[1]
        self.aabb = utils.AABB(self.position[0], self.position[1], ex, ey)

    def get_settings_list(self):
        settings_lst = [TOSetting("int", 0, None, self.frame, "Frame number: ", self.set_frame_s),
                        TOSetting("bool", 0, None, self.animated, "Play animation", self.set_animated_s),
                        TOSetting("int", 0, None, self.frame_time, "Frame time, ms: ", self.set_frame_time_s)
                        ]
        return settings_lst        

    def set_frame_s(self, setting):
        self.frame = setting.new_value

    def set_animated_s(self, setting):
        self.animated = setting.new_value

    def set_frame_time_s(self, setting):
        self.frame_time = setting.new_value

    def draw(self, cr):
        cr.translate(self.position[0], self.position[1])
        if self.animated:
            if (time.time()-self.animation_timer > self.frame_time):
                self.animation_frame = (self.animation_frame + 1) % self.sprite.get_animation_length()
                self.animation_timer = time.time()
            self.sprite.draw_frame(cr, self.animation_frame)
        else:
            self.sprite.draw_frame(cr, self.frame)

        cr.set_source_rgba(1, 0, 0, 1)
        cr.set_line_width(1)
        if self.is_selected:
            cr.rectangle(0, 0, self.dimensions[0], self.dimensions[1])
            cr.stroke()
        cr.translate(-self.position[0], -self.position[1])
