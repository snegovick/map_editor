class Sprite:
    def __init__(self, state=None, data=None):
        self.state = state
        self.imported(data)

    def imported(self, data):
        for im_name in data["image_refs"]:
            img = self.state.get_image_by_name(im_name)
            if img != None:
                self.images.append(img)
