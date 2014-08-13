from generalized_settings import TOSetting

class State:
    def __init__(self, grid_step=[8,8]):
        self.grid_step = grid_step

    def set_screen_offset(self, offset):
        pass

    def get_offset(self):
        return [0,0]

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
