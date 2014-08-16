class LayerType:
    meta="meta"
    sprite="sprite"

class Layer:
    def __init__(self, name=None, layer_type=LayerType.meta):
        self.layer_type = layer_type
        self.proxy_dct = {}
        self.last_id = 0
        self.name = name
        self.selected_proxys = []

    def unselect_all_proxys(self):
        for p in self.selected_proxys:
            p.unset_selected()
        self.selected_proxys = []

    def add_proxy_to_selected(self, p):
        if p not in self.selected_proxys:
            self.selected_proxys.append(p)
            p.set_selected()

    def get_selected_proxys(self):
        return self.selected_proxys

    def get_name(self):
        return self.name

    def add_proxy(self, proxy):
        proxy.id = self.last_id
        self.proxy_dct[self.last_id] = proxy
        self.last_id += 1

    def get_proxy_lst(self):
        return self.proxy_dct.values()        

    def remove_proxy_by_id(self, pid):
        if pid in self.proxy_list:
            del self.proxy_dct[pid]

    def draw(self, cr):
        for p in self.proxy_dct.values():
            p.draw(cr)

    
