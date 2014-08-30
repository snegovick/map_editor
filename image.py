from tileset_editor.utils import *

import cairo

class Image:
    def __init__(self, atlas, data):
        self.dimensions = data["dimensions"]
        self.origin = data["origin"]
        self.name = data["name"]
        print "origin:", self.origin

        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.dimensions[0]), int(self.dimensions[1]))
        cr = cairo.Context(self.surf)
        cr.set_source_surface(atlas, -self.origin[0], -self.origin[1])
        cr.paint_with_alpha(1.0)

    def get_dimensions(self):
        return self.dimensions

    def draw(self, cr, alpha):
        #print "image name:", self.name
        cr.set_source_surface(self.surf, 0, 0)
        cr.paint_with_alpha(alpha)

    def export(self):
        return {"type": "image", "dimensions": self.dimensions, "origin": self.origin, "name": self.name}
