import math

from proxy import Proxy
from meta import Meta

class LayerType:
    meta="meta"
    sprite="sprite"

class Layer:
    def __init__(self, name=None, layer_type=LayerType.meta, state=None, data=None):
        self.proxy_dct = {}
        self.last_id = 0
        self.selected_proxys = []
        self.selected_lo = None
        self.ignore_next_selection_change = False
        self.state = state

        self.adjacency_dct = {}

        if data == None:
            self.layer_type = layer_type
            self.name = name
        else:
            self.deserialize(data)
        

    def get_ignore_next_selection_change(self):
        return self.ignore_next_selection_change

    def set_ignore_next_selection_change(self):
        self.ignore_next_selection_change = True

    def unset_ignore_next_selection_change(self):
        self.ignore_next_selection_change = False
            
    def get_wait_child(self):
        return self.wait_child

    def set_wait_child(self):
        self.wait_child = True

    def unset_wait_child(self):
        self.wait_child = False
            
    def get_current_parent_object(self):
        return self.current_parent_object

    def set_current_parent_object(self, p):
        self.current_parent_object = p

    def link_proxys(self):
        selected = self.get_selected_proxys()
        self.adjacency_dct[selected[0].id].append(selected[1].id)

    def get_new_meta(self):
        from state import state
        return Meta(str(self.last_id), state.get_grid_step())

    def get_layer_type(self):
        return self.layer_type

    def unselect_all_proxys(self):
        for p in self.selected_proxys:
            p.unset_selected()
        self.selected_proxys = []
        print "unselect all"

    def add_proxy_to_selected(self, p):
        if p not in self.selected_proxys:
            self.selected_proxys.append(p)
            p.set_selected()
        print "add:", self.selected_proxys

    def remove_proxy_from_selected(self, p):
        if p in self.selected_proxys:
            self.selected_proxys.remove(p)
            p.unset_selected()

    def unselect_layer_object(self):
        self.selected_lo = None

    def set_selected_layer_object(self, s):
        self.selected_lo = s

    def get_selected_layer_object(self):
        return self.selected_lo

    def get_selected_proxys(self):
        print "selected:", self.selected_proxys
        return self.selected_proxys

    def get_name(self):
        return self.name

    def add_proxy(self, pt):
        p = None
        p = Proxy(self.get_selected_layer_object(), position=pt)
        p.name = str(self.last_id)
        p.id = self.last_id
        self.proxy_dct[self.last_id] = p
        if self.layer_type == LayerType.meta:
            self.adjacency_dct[self.last_id] = []

        self.last_id += 1

    def get_proxy_lst(self):
        return self.proxy_dct.values()        

    def remove_proxy_by_id(self, name):
        if name in self.proxy_list:
            del self.proxy_dct[name]

    def draw(self, cr, alpha):
        print "proxy_dct:", self.proxy_dct
        for p in self.proxy_dct.values():
            p.draw(cr, alpha)


        cr.set_source_rgba(0, 0, 0, alpha)
        cr.set_line_width(1)

        if self.layer_type == LayerType.meta:
            for k, v in self.adjacency_dct.iteritems():
                start = self.proxy_dct[k].get_position()
                for id in self.adjacency_dct[k]:
                    end = self.proxy_dct[id].get_position()
                    print "line:", start, end
                    cr.move_to(start[0], start[1])
                    cr.line_to(end[0], end[1])

                    a = math.atan2(end[1]-start[1], end[0]-start[0])
                    l = 10 # arrow size in px

                    p1 = [end[0]+l*math.cos(a-math.radians(15)-math.pi), end[1]+l*math.sin(a-math.radians(15)-math.pi)]
                    p2 = [end[0]+l*math.cos(a+math.radians(15)-math.pi), end[1]+l*math.sin(a+math.radians(15)-math.pi)]
                    
                    cr.move_to(end[0], end[1])
                    cr.line_to(p1[0], p1[1])
                    cr.move_to(end[0], end[1])
                    cr.line_to(p2[0], p2[1])
                    cr.stroke()


    def serialize(self):
        return {"type": "layer", "name": self.name, "layer_type": self.layer_type, "adjacency_dct": self.adjacency_dct, "proxys": [p.serialize() for p in self.proxy_dct.values()]}

    def deserialize(self, data):
        from state import state
        self.name = data["name"]
        self.layer_type = data["layer_type"]
        self.adjacency_dct = {}
        for k, v in data["adjacency_dct"].iteritems():
            self.adjacency_dct[int(k)] = v
        
        for p in data["proxys"]:
            if self.layer_type == LayerType.meta:
                m = Meta("", state.get_grid_step())
                proxy = Proxy(sprite=m, state=state, data=p)
                m.name= str(proxy.id)
                m.update_text()
            else:
                proxy = Proxy(state=state, data=p)
            self.proxy_dct[proxy.id] = proxy
                
        self.last_id = proxy.id+1
