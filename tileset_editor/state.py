from generalized_settings import TOSetting
import cairo
import utils
import os

class Image:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.cairo_img = cairo.ImageSurface.create_from_png(path)
        self.dimensions = [self.cairo_img.get_width(), self.cairo_img.get_height()]
        self.origin = [0,0]
        self.aabb = utils.AABB(self.origin[0],self.origin[1],self.dimensions[0],self.dimensions[1])
        self.selected = False

    def draw(self, cr):
        cr.translate(self.origin[0], self.origin[1])
        cr.set_source_surface(self.cairo_img, 0, 0)
        cr.paint_with_alpha(1.0)

        cr.set_source_rgba(1, 0, 0, 1)
        cr.set_line_width(1)

        if self.selected:
            cr.rectangle(0, 0, self.dimensions[0], self.dimensions[1])
            cr.stroke()
        cr.translate(-self.origin[0], -self.origin[1])

    def toggle_selected(self):
        self.selected = not self.selected
        return self.selected

    def unselect(self):
        self.selected = False

    def get_aabb(self):
        return self.aabb

    def point_in_aabb(self, pt):
        return self.aabb.point_in_aabb(pt)

    def set_origin(self, origin):
        self.origin[0] = origin[0]
        self.origin[1] = origin[1]
        self.aabb = utils.AABB(self.origin[0], self.origin[1], self.dimensions[0], self.dimensions[1])

    def move_origin(self, delta):
        self.origin[0] += delta[0]
        self.origin[1] += delta[1]
        self.aabb = utils.AABB(self.origin[0], self.origin[1], self.dimensions[0], self.dimensions[1])

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return name

    def serialize(self):
        return {"type": "image", "name": self.name, "origin": self.origin, "path": self.path}

    def deserialize(self, data):
        self.name = data["name"]
        self.origin = data["origin"]
        self.path = data["path"]
        self.cairo_img = cairo.ImageSurface.create_from_png(self.path)
        self.dimensions = [self.cairo_img.get_width(), self.cairo_img.get_height()]

    def __repr__(self):
        return "<Image %s>" % (self.name, )

class State:
    def __init__(self, grid_step=[8,8]):
        self.grid_step = grid_step
        self.scale = [1, 1]
        self.images = []
        self.left_press_start = None
        self.selected_images = []

        self.pointer_position = None

    def set_pointer_position(self, pt):
        self.pointer_position = pt
        
    def get_pointer_position(self):
        return self.pointer_position

    def add_im_to_selected(self, im):
        self.selected_images.append(im)

    def remove_im_from_selected(self, im):
        self.selected_images.remove(im)

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

    def load_image(self, path):
        img = Image(path, os.path.basename(path))
        self.images.append(img)

# service methods

    def get_settings_list(self):
        settings_lst = [TOSetting("int", 0, None, self.grid_step[0], "Grid x step, px: ", self.set_grid_x_s),
                        TOSetting("int", 0, None, self.grid_step[1], "Grid y step, px: ", self.set_grid_y_s)]
        return settings_lst

    def set_grid_x_s(self, setting):
        self.grid_step[0] = setting.new_value

    def set_grid_y_s(self, setting):
        self.grid_step[1] = setting.new_value

    def serialize(self):
        return {"type": "state", "grid_step": self.grid_step}

    def deserialize(self, data):
        self.grid_step = data["grid_step"]

state = State()
