import cairo

class Meta:
    def __init__(self, text, dimensions):
        self.dimensions = dimensions
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.dimensions[0]), int(self.dimensions[1]))
        cr = cairo.Context(self.surf)
        cr.set_source_rgb(0.1, 0.1, 0.1)
        f_size = 13
        cr.set_font_size(f_size);
        self.text = text
        (x, y, width, height, dx, dy) = cr.text_extents(self.text)
        cr.move_to(dimensions[0]/2-width/2, dimensions[1]/2)
        cr.show_text(text)

    def get_animation_length(self):
        return 1

    def get_dimensions(self):
        return self.dimensions

    def draw_preview(self, cr):
        self.draw_frame(cr, 0, 1.0)

    def draw_frame(self, cr, frame, alpha):
        cr.set_source_rgba(0, 1, 0, alpha)
        cr.set_line_width(1)
        cr.rectangle(0, 0, self.dimensions[0], self.dimensions[1])
        cr.fill()
        cr.set_source_surface(self.surf, 0, 0)
        cr.paint_with_alpha(alpha)
