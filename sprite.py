class Sprite:
    def __init__(self, state=None, data=None):
        self.state = state
        self.images = []
        self.name = None
        self.imported(data)

    def imported(self, data):
        self.name = data["name"]
        for im_name in data["image_refs"]:
            img = self.state.get_image_by_name(im_name)
            if img != None:
                self.images.append(img)

    def get_dimensions(self):
        if len(self.images) > 0:
            return self.images[0].get_dimensions()
        return (0,0)

    def draw_frame(self, cr, frame, alpha):
        self.images[frame].draw(cr, alpha)

    def draw_preview(self, cr):
        self.draw_frame(cr, 0, 1.0)

    def get_images(self):
        return self.images

    def get_animation_length(self):
        return len(self.images)

    def export(self):
        return {"type": "sprite", "name": self.name, "image_refs": [i.name for i in self.images]}
