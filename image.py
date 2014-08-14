class Image:
    def __init__(self, atlas, data):
        self.dimensions = data["dimensions"]
        self.origin = data["origin"]
        self.name = data["name"]

        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.dimensions[0]), int(self.dimensions[1]))
        cr = cairo.Contex(self.surf)
        cr.set_source_surface(atlas, self.origin[0], self.origin[1])

    def draw_at(self, position):
        pass
