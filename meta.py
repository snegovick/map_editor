class Meta:
    def __init__(self, sprite=None, position=None, data=None):
        if data == None:
            self.position = position
            self.sprite = sprite
            self.frame = 0
            self.animated = False
            self.animation_speed = 10

    def get_settings_list(self):
        settings_lst = [TOSetting("int", 0, None, self.frame, "Frame number: ", self.set_frame_s),
                        TOSetting("bool", 0, None, self.animated, "Play animation", self.set_animated_s),
                        TOSetting("int", 0, None, self.animation_speed, "Animation speed, ticks per frame: ", self.set_animation_speed_s)
                        ]
        return settings_lst

    def set_frame_s(self, setting):
        self.frame = setting.new_value

    def set_animated_s(self, setting):
        self.animated = setting.new_value

    def set_animation_speed_s(self, setting):
        self.animation_speed = setting.new_value
