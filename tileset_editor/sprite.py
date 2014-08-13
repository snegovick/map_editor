

class Sprite:
    def __init__(self, images=None, name=None, state=None, data=None):
        self.selected_image = None
        if data == None:
            self.images = images
            self.name = name
        else:
            self.state = state
            self.deserialize(data)

    def reinit(self, images):
        self.images = images

    def set_selected_image(self, s):
        self.selected_image = s

    def remove_selected_image(self):
        if self.selected_image in self.images:
            self.images.remove(self.selected_image)
            self.selected_image = None

    def up_selected_image(self):
        if self.selected_image in self.images:
            idx = self.images.index(self.selected_image)
            if idx != 0:
                temp = self.selected_image
                self.images.remove(self.selected_image)
                self.images.insert(idx-1, temp)

    def down_selected_image(self):
        if self.selected_image in self.images:
            idx = self.images.index(self.selected_image)
            if idx < len(self.images)-1:
                temp = self.selected_image
                self.images.remove(self.selected_image)
                self.images.insert(idx+1, temp)
        
    def get_images(self):
        return self.images

    def add_images(self, images):
        self.images += images

    def export(self):
        return {"name": self.name, "image_refs": [i.name for i in self.images]}

    def serialize(self):
        return {"type": "sprite", "name": self.name, "image_refs": [i.name for i in self.images]}
        
    
    def deserialize(self, data):
        self.name = data["name"]
        self.images = [self.state.get_image_by_name(i) for i in data["image_refs"]]
