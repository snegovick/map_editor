from generalized_settings import TOSetting

import cairo
import os

import utils

class Image:
    def __init__(self, path=None, name=None, data=None):
        if data == None:
            self.path = path
            self.name = name
            self.cairo_img = cairo.ImageSurface.create_from_png(path)
            self.dimensions = [self.cairo_img.get_width(), self.cairo_img.get_height()]
            self.origin = [0,0]
        else:
            self.deserialize(data)

        ex = self.origin[0]+self.dimensions[0]
        ey = self.origin[1]+self.dimensions[1]

        self.aabb = utils.AABB(self.origin[0], self.origin[1], ex, ey)
        self.selected = False

    def draw(self, cr, clean=False):
        cr.translate(self.origin[0], self.origin[1])
        cr.set_source_surface(self.cairo_img, 0, 0)
        cr.paint_with_alpha(1.0)

        if not clean:
            if self.selected:
                cr.set_source_rgba(1, 0, 0, 1)
                cr.set_line_width(1)        
                cr.rectangle(0, 0, self.dimensions[0], self.dimensions[1])
                cr.stroke()
            else:
                cr.set_source_rgba(0.1, 0.1, 0.1, 1)
                cr.set_line_width(0.5)
                
                cr.rectangle(0, 0, self.dimensions[0], self.dimensions[1])
                cr.stroke()
        cr.translate(-self.origin[0], -self.origin[1])

    def set_selected(self):
        self.selected = True

    def unselect(self):
        self.selected = False
        
    def get_selected(self):
        return self.selected

    def get_aabb(self):
        return self.aabb

    def point_in_aabb(self, pt):
        return self.aabb.point_in_aabb(pt)

    def set_origin(self, origin):
        self.origin[0] = origin[0]
        self.origin[1] = origin[1]
        ex = self.origin[0]+self.dimensions[0]
        ey = self.origin[1]+self.dimensions[1]

        self.aabb = utils.AABB(self.origin[0], self.origin[1], ex, ey)

    def get_origin(self):
        return self.origin

    def move_origin(self, delta):
        self.origin[0] += delta[0]
        self.origin[1] += delta[1]
        ex = self.origin[0]+self.dimensions[0]
        ey = self.origin[1]+self.dimensions[1]
        
        self.aabb = utils.AABB(self.origin[0], self.origin[1], ex, ey)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return name

    def serialize(self):
        return {"type": "image", "name": self.name, "origin": self.origin, "path": os.path.relpath(self.path)}

    def deserialize(self, data):
        self.name = data["name"]
        self.origin = data["origin"]
        self.path = data["path"]
        try:
            self.cairo_img = cairo.ImageSurface.create_from_png(self.path)
        except:
            print "Failed to read png from:", self.path
        self.dimensions = [self.cairo_img.get_width(), self.cairo_img.get_height()]

    def export(self):
        return {"name": self.name, "origin": self.origin, "dimensions": self.dimensions}


    def __repr__(self):
        return "<Image %s>" % (self.name, )
