import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys

from state import state, State
from project import project
from sprite import Sprite
from tileset_editor import utils
from layer import LayerType, Layer
from proxy import Proxy

class EVEnum:
    scroll_up = "scroll_up"
    scroll_down = "scroll_down"
    update_settings = "update_settings"
    shift_press = "shift_press"
    shift_release = "shift_release"
    pointer_motion = "pointer_motion"
    screen_left_press = "screen_left_press"
    screen_left_release = "screen_left_release"
    import_click = "import_click"
    sprite_put_button_click = "sprite_put_button_click"
    sprites_selection_changed = "sprites_selection_changed"
    layer_add_button_click = "layer_add_button_click"
    layers_selection_changed = "layers_selection_changed"

class EventProcessor(object):
    event_list = []
    selected_elements = []
    selected_path = None
    selected_tool_operation = None
    left_press_start = None
    pointer_position = None
    shift_pressed = False
    relative_coords = {}

    def __init__(self):
        self.events = {
            EVEnum.scroll_up: self.scroll_up,
            EVEnum.scroll_down: self.scroll_down,
            EVEnum.update_settings: self.update_settings,
            EVEnum.shift_press: self.shift_press,
            EVEnum.shift_release: self.shift_release,
            EVEnum.pointer_motion: self.pointer_motion,
            EVEnum.screen_left_press: self.screen_left_press,
            EVEnum.screen_left_release: self.screen_left_release,
            EVEnum.import_click: self.import_click,
            EVEnum.sprite_put_button_click: self.sprite_put_button_click,
            EVEnum.sprites_selection_changed: self.sprites_selection_changed,
            EVEnum.layer_add_button_click: self.layer_add_button_click,
            EVEnum.layers_selection_changed: self.layers_selection_changed,
        }

    def reset(self):
        self.selected_elements = []
        self.selected_path = None
        self.selected_tool_operation = None
        self.left_press_start = None

    def push_event(self, event, *args):
        #print "pushing", event 
        self.event_list.append((event, args))

    def process(self):
        for e, args in self.event_list:
            if e in self.events:
                self.events[e](args)
            else:
                print "Unknown event:", e, args
        self.event_list = []

    def scroll_up(self, args):
        scale = state.get_scale()
        state.set_scale((scale[0]+0.1, scale[1]+0.1))
        self.mw.widget.update()

    def scroll_down(self, args):
        scale = state.get_scale()
        if scale[0]>0.2:
            state.set_scale((scale[0]-0.1, scale[1]-0.1))
            self.mw.widget.update()

    def shift_press(self, args):
        state.set_shift_pressed()

    def shift_release(self, args):
        state.unset_shift_pressed()

    def pointer_motion(self, args):
        offset = state.get_offset()
        scale = state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]
        pointer_position = (cx, cy)
        grid_step = state.get_grid_step()

        layer = state.get_active_layer()
        if layer != None:
            if state.get_put_sprite():
                self.mw.widget.update()

            if state.get_left_press_start() != None:
                prev_position = state.get_pointer_position()

                proxys = layer.get_selected_proxys()

                for p in proxys:
                    nx = cx + self.relative_coords[p][0]
                    ny = cy + self.relative_coords[p][1]
                    p.set_position((int(nx/grid_step[0])*grid_step[0], int(ny/grid_step[1])*grid_step[1]))
                self.mw.widget.update()
        nx = int(pointer_position[0]/grid_step[0])*grid_step[0]
        ny = int(pointer_position[1]/grid_step[1])*grid_step[1]
        pointer_position = [nx, ny]
        state.set_pointer_position(pointer_position)
        self.mw.cursor_pos_label.set_text("%.3f:%.3f"%(cx, cy))

    def screen_left_press(self, args):
        offset = state.get_offset()
        scale = state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]
        state.set_left_press_start((cx, cy))

        layer = state.get_active_layer()
        if layer != None:
            if state.get_put_sprite():
                state.unset_put_sprite()
                p = Proxy(state.get_selected_sprite(), [cx, cy])
                layer.add_proxy(p)
                

            proxy_lst = layer.get_proxy_lst()

            if state.get_shift_pressed():
                for p in proxy_lst:
                    if p.point_in_aabb([cx, cy]):
                        if not layer.get_selected():
                            layer.add_proxy_to_selected(p)
                        else:
                            del self.relative_coords[p]
                            layer.remove_proxy_from_selected(p)
            else:
                selected = None
                for p in proxy_lst:
                    if p.point_in_aabb([cx, cy]):
                        selected = p
                if selected != None:
                    if selected.get_selected():
                        layer.unselect_all_proxys()
                        self.relative_coords = {}
                    else:
                        layer.unselect_all_proxys()
                        self.relative_coords = {}
                        layer.add_proxy_to_selected(selected)
                    
            self.mw.widget.update()

            selected_proxys = layer.get_selected_proxys()
            self.relative_coords = {}
            for p in selected_proxys:
                self.relative_coords[p] = utils.mk_vect((cx, cy), p.get_position())

    def screen_left_release(self, args):
        offset = state.get_offset()
        scale = state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]

        state.unset_left_press_start()

    def update_settings(self, args):
        new_value = args[0][1][0].get_value()
        setting = args[0][0]
        setting.set_value(new_value)
        project.push_state(state)
        self.mw.widget.update()

    def update_sprites_list(self, args):
        sprites = state.get_sprites()
        if sprites != None:
            self.mw.clear_list(self.mw.sp_gtklist)
            for p in sprites:
                self.mw.add_item_to_list(self.mw.sp_gtklist, p.name, None)
        project.push_state(state)

    def import_click(self, args):
        mimes = [("Tileset (*.json)", "Application/json", "*.json")]
        result = self.mw.mk_file_dialog("Open tileset ...", mimes)
        if result != None:
            tset_name = result
            state.load_tileset(tset_name)
            self.update_sprites_list(None)
            self.mw.widget.update()

    def sprites_selection_changed(self, args):
        selection = args[0][0].get_selection()
        state.unselect_sprite()
        name = selection[0].children()[0].children()[1].get_text()
        for s in state.get_sprites():
            if s.name == name:
                state.set_selected_sprite(s)
                break

    def sprite_put_button_click(self, args):
        state.set_put_sprite()

    def update_layers_list(self, args):
        layers = state.get_layers()
        if layers != None:
            self.mw.clear_list(self.mw.l_gtklist)
            for l in layers:
                self.mw.add_item_to_list(self.mw.l_gtklist, l.name, None)
        project.push_state(state)

    def layer_add_button_click(self, args):
        ok, name, meta = self.mw.mk_addlayer_dialog("Enter the name for new layer:")
        if ok:
            l_type = (LayerType.meta if meta else LayerType.sprite)
            state.add_layer(name, meta)
            self.update_layers_list(None)

    def layers_selection_changed(self, args):
        selection = args[0][0].get_selection()
        name = selection[0].children()[0].children()[1].get_text()
        for l in state.get_layers():
            if l.name == name:
                print "active layer:", l.name
                state.set_active_layer(l)
                self.mw.widget.update()
                break

ep = EventProcessor()
