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

    def draw_frame(self, cr, frame):
        self.images[frame].draw(cr)

    def get_images(self):
        return self.images

    def get_animation_length(self):
        return len(self.images)
