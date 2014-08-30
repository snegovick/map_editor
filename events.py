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
    ctrl_press = "ctrl_press"
    ctrl_release = "ctrl_release"
    pointer_motion = "pointer_motion"
    screen_left_press = "screen_left_press"
    screen_left_release = "screen_left_release"
    import_click = "import_click"
    sprite_put_button_click = "sprite_put_button_click"
    sprites_selection_changed = "sprites_selection_changed"
    layer_add_button_click = "layer_add_button_click"
    layers_selection_changed = "layers_selection_changed"
    layer_objects_selection_changed = "layer_objects_selection_changed"
    general_selection_changed = "general_selection_changed"
    layer_object_add_meta_button_click = "layer_object_add_meta_button_click"
    layer_set_child_button_click = "layer_set_child_button_click"
    load_project_click = "load_project_click"
    save_project_click = "save_project_click"
    export_click = "export_click"
    layer_delete_object_button_click = "layer_delete_object_button_click"
    deselect_all = "deselect_all"
    hscroll = "hscroll"
    vscroll = "vscroll"

class EventProcessor(object):
    event_list = []
    selected_elements = []
    selected_path = None
    selected_tool_operation = None
    left_press_start = None
    pointer_position = None
    relative_coords = {}

    def __init__(self):
        self.events = {
            EVEnum.scroll_up: self.scroll_up,
            EVEnum.scroll_down: self.scroll_down,
            EVEnum.update_settings: self.update_settings,
            EVEnum.shift_press: self.shift_press,
            EVEnum.shift_release: self.shift_release,
            EVEnum.ctrl_press: self.ctrl_press,
            EVEnum.ctrl_release: self.ctrl_release,
            EVEnum.pointer_motion: self.pointer_motion,
            EVEnum.screen_left_press: self.screen_left_press,
            EVEnum.screen_left_release: self.screen_left_release,
            EVEnum.import_click: self.import_click,
            EVEnum.sprite_put_button_click: self.sprite_put_button_click,
            EVEnum.sprites_selection_changed: self.sprites_selection_changed,
            EVEnum.layer_add_button_click: self.layer_add_button_click,
            EVEnum.layers_selection_changed: self.layers_selection_changed,
            EVEnum.layer_objects_selection_changed: self.layer_objects_selection_changed,
            EVEnum.general_selection_changed: self.general_selection_changed,
            EVEnum.layer_object_add_meta_button_click: self.layer_object_add_meta_button_click,
            EVEnum.layer_set_child_button_click: self.layer_set_child_button_click,
            EVEnum.load_project_click: self.load_project_click,
            EVEnum.save_project_click: self.save_project_click,
            EVEnum.export_click: self.export_click,
            EVEnum.layer_delete_object_button_click: self.layer_delete_object_button_click,
            EVEnum.deselect_all: self.deselect_all,
            EVEnum.hscroll: self.hscroll,
            EVEnum.vscroll: self.vscroll,
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
        if state.get_shift_pressed():
            offset = state.get_base_offset()
            self.hscroll_base(offset[0]-state.get_grid_step()[0])
        elif state.get_ctrl_pressed():
            offset = state.get_base_offset()
            self.vscroll_base(offset[1]-state.get_grid_step()[1])
        else:
            scale = state.get_scale()
            state.set_scale((scale[0]+0.1, scale[1]+0.1))
        self.mw.widget.update()

    def scroll_down(self, args):
        if state.get_shift_pressed():
            offset = state.get_base_offset()
            self.hscroll_base(offset[0]+state.get_grid_step()[0])
        elif state.get_ctrl_pressed():
            offset = state.get_base_offset()
            self.vscroll_base(offset[1]+state.get_grid_step()[1])
        else:
            scale = state.get_scale()
            if scale[0]>0.2:
                state.set_scale((scale[0]-0.1, scale[1]-0.1))
                self.mw.widget.update()
        self.mw.widget.update()

    def shift_press(self, args):
        state.set_shift_pressed()

    def shift_release(self, args):
        state.unset_shift_pressed()

    def ctrl_press(self, args):
        state.set_ctrl_pressed()

    def ctrl_release(self, args):
        state.unset_ctrl_pressed()

    def pointer_motion(self, args):
        offset = state.get_offset()
        scale = state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]
        pointer_position = (cx, cy)
        grid_step = state.get_grid_step()

        layer = state.get_active_layer()
        if layer != None:
            if state.get_put_layer_object():
                self.mw.widget.update()

            if state.get_left_press_start() != None:
                prev_position = state.get_pointer_position()

                proxys = layer.get_selected_proxys()

                for p in proxys:
                    if not p in self.relative_coords:
                        self.relative_coords[p] = utils.mk_vect((cx, cy), p.get_position())
                    nx = cx + self.relative_coords[p][0]
                    ny = cy + self.relative_coords[p][1]
                    p.set_position((int(nx/grid_step[0])*grid_step[0], int(ny/grid_step[1])*grid_step[1]))
                    layer.resort_all_proxys()
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
        grid_step = state.get_grid_step()
        layer = state.get_active_layer()
        # if layer != None:
        #     if state.get_put_layer_object():
        #         state.unset_put_layer_object()
        #         nx = int(cx/grid_step[0])*grid_step[0]
        #         ny = int(cy/grid_step[1])*grid_step[1]
        #         pt = [nx, ny]
        #         layer.add_proxy(pt)
        #         self.update_layer_objects_list(None)
                
        #     proxy_lst = layer.get_proxy_lst()

        #     if state.get_shift_pressed():
        #         for p in proxy_lst:
        #             if p.point_in_aabb([cx, cy]):
        #                 if not p.get_selected():
        #                     self.general_set_selected_element({"lst": self.mw.lo_gtklist, "name": p.name, "element": p})
        #                     layer.add_proxy_to_selected(p)
        #                     layer.set_ignore_next_selection_change()
        #                 else:
        #                     if p in self.relative_coords:
        #                         del self.relative_coords[p]
        #                     self.general_unselect_element({"lst": self.mw.lo_gtklist, "name": p.name})
        #                     layer.remove_proxy_from_selected(p)
        #     else:
        #         selected = None
        #         for p in proxy_lst:
        #             if p.point_in_aabb([cx, cy]):
        #                 selected = p
        #         if selected != None:
        #             if selected.get_selected():
        #                 self.relative_coords = {}
        #                 self.general_unselect_all_elements({"lst": self.mw.lo_gtklist})
        #                 print "click"
        #                 layer.unselect_all_proxys()
        #             else:
        #                 self.relative_coords = {}
        #                 self.general_set_selected_element({"lst": self.mw.lo_gtklist, "name": selected.name, "element": selected})
        #                 layer.add_proxy_to_selected(p)
        #                 layer.set_ignore_next_selection_change()

        #     self.mw.widget.update()

        #     selected_proxys = layer.get_selected_proxys()
        #     if len(selected_proxys) == 2:
        #         if layer.get_layer_type() == LayerType.meta:
        #             self.mw.layer_set_child_button.set_sensitive(True)

        #     self.relative_coords = {}
        #     for p in selected_proxys:
        #         self.relative_coords[p] = utils.mk_vect((cx, cy), p.get_position())

    def screen_left_release(self, args):
        offset = state.get_offset()
        scale = state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]

        grid_step = state.get_grid_step()
        layer = state.get_active_layer()

        if layer != None:
            if state.get_put_layer_object():
                state.unset_put_layer_object()
                nx = int(cx/grid_step[0])*grid_step[0]
                ny = int(cy/grid_step[1])*grid_step[1]
                pt = [nx, ny]
                layer.add_proxy(pt)
                self.update_layer_objects_list(None)
                
            proxy_lst = layer.get_proxy_lst()

            if state.get_shift_pressed():
                for p in proxy_lst:
                    if p.point_in_aabb([cx, cy]):
                        if not p.get_selected():
                            self.general_set_selected_element({"lst": self.mw.lo_gtklist, "name": p.name, "element": p})
                            layer.add_proxy_to_selected(p)
                            layer.set_ignore_next_selection_change()
                        else:
                            if p in self.relative_coords:
                                del self.relative_coords[p]
                            self.general_unselect_element({"lst": self.mw.lo_gtklist, "name": p.name})
                            layer.remove_proxy_from_selected(p)
            else:
                selected = None
                for p in proxy_lst:
                    if p.point_in_aabb([cx, cy]):
                        selected = p
                if selected != None:
                    if selected.get_selected():
                        self.relative_coords = {}
                        self.general_unselect_all_elements({"lst": self.mw.lo_gtklist})
                        print "click"
                        layer.unselect_all_proxys()
                    else:
                        self.relative_coords = {}
                        self.general_set_selected_element({"lst": self.mw.lo_gtklist, "name": selected.name, "element": selected})
                        layer.add_proxy_to_selected(p)
                        layer.set_ignore_next_selection_change()

            self.mw.widget.update()

            selected_proxys = layer.get_selected_proxys()
            if len(selected_proxys) == 2:
                if layer.get_layer_type() == LayerType.meta:
                    self.mw.layer_set_child_button.set_sensitive(True)

            self.relative_coords = {}
            for p in selected_proxys:
                self.relative_coords[p] = utils.mk_vect((cx, cy), p.get_position())


        state.unset_left_press_start()

    def update_settings(self, args):
        if hasattr(args[0][1][0], "get_value"):
            new_value = args[0][1][0].get_value()
        else:
            new_value = args[0][1][0].get_active()
        setting = args[0][0]
        setting.set_value(new_value)
        project.push_state(state)
        self.mw.widget.update()

    def general_unselect_all_elements(self, args):
        lst = args["lst"]
        for e in lst.children():
            lst.unselect_child(e)


    def general_unselect_element(self, args):
        lst = args["lst"]
        name = args["name"]
        for e in lst.children():
            hb = e.children()[0]
            if hb.children()[1].get_text() == name:
                lst.unselect_child(e)
                break

    def general_set_selected_element(self, args):
        lst = args["lst"]
        element_name = args["name"]
        element = args["element"]
        for e in lst.children():
            hb = e.children()[0]
            if hb.children()[1].get_text() == element_name:
                lst.select_child(e)
                #self.layer_objects_selection_changed(element)
            # else:
            #     lst.unselect_child(e)

    def general_selection_changed(self, args):
        lst = args[0]["lst"][0]
        cb = args[0]["callback"]
        enumerable = args[0]["enumerable"]
        selection = lst.get_selection()
        if len(selection)>0:
            name = selection[0].children()[0].children()[1].get_text()
            for e in enumerable:
                if e.name == name:
                    cb(e)
                    break
        cb(None)

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
        if len(selection)>0:
            layer = state.get_active_layer()
            if layer == None:
                args[0][0].unselect_child(selection[0])
                return
            if layer.get_layer_type() == LayerType.meta:
                args[0][0].unselect_child(selection[0])
                return
            layer.unselect_layer_object()
            name = selection[0].children()[0].children()[1].get_text()
            for s in state.get_sprites():
                if s.name == name:
                    layer.set_selected_layer_object(s)
                    break

    def sprite_put_button_click(self, args):
        layer = state.get_active_layer()
        if layer != None:
            if layer.get_selected_layer_object()!=None:
                state.set_put_layer_object()

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
            state.add_layer(name, l_type)
            self.update_layers_list(None)

    def update_layer_objects_list(self, args):
        layer = state.get_active_layer()
        if layer!=None:
            proxys = layer.get_proxy_lst()
            if proxys != None:
                self.mw.clear_list(self.mw.lo_gtklist)
                for p in proxys:
                    self.mw.add_item_to_list(self.mw.lo_gtklist, p.name, None)

    def layers_selection_changed(self, args):
        if args!=None:
            state.set_active_layer(args)
            if args.get_layer_type() == LayerType.meta:
                self.mw.layer_object_add_button.set_sensitive(True)
                self.mw.sprite_put_button.set_sensitive(False)
            else:
                self.mw.layer_object_add_button.set_sensitive(False)
                self.mw.sprite_put_button.set_sensitive(True)
                self.mw.layer_set_child_button.set_sensitive(False)
            self.update_layer_objects_list(None)
            self.mw.widget.update()

    def layer_objects_selection_changed(self, args):
        layer = state.get_active_layer()
        if layer != None:
            if args != None:
                self.mw.new_settings_vbox(args.get_settings_list(), "Object "+args.name+" settings")
                
                if not state.get_shift_pressed():
                    layer.unselect_all_proxys()
                layer.add_proxy_to_selected(args)
                layer.set_ignore_next_selection_change()
            else:
                if layer.get_ignore_next_selection_change():
                    layer.unset_ignore_next_selection_change()
                    return
                layer.unselect_all_proxys()
        self.mw.widget.update()

    def layer_object_add_meta_button_click(self, args):
        layer = state.get_active_layer()
        if layer != None:
            layer.set_selected_layer_object(layer.get_new_meta())
        state.set_put_layer_object()

    def layer_set_child_button_click(self, args):
        layer = state.get_active_layer()
        if layer != None:
            selected_proxys = layer.get_selected_proxys()
            if len(selected_proxys) == 2:
                if layer.get_layer_type() == LayerType.meta:
                    layer.link_proxys()
                    self.mw.widget.update()

    def load_project_click(self, args):
        mimes = [("Map project (*.map_project)", "Application/map_project", "*.map_project")]
        result = self.mw.mk_file_dialog("Load project ...", mimes)
        if result!=None:
            project.load(result)
            self.update_layer_objects_list(None)
            self.update_sprites_list(None)
            self.update_layers_list(None)
            self.mw.widget.update()

    def save_project_click(self, args):
        mimes = [("Map project (*.map_project)", "Application/map_project", "*.map_project")]
        result = self.mw.mk_file_save_dialog("Save project ...", mimes)
        if result!=None:
            project.save(result)

    def export_click(self, args):
        mimes = [("Map files (*)", "", "*")]
        result = self.mw.mk_file_save_dialog("Save map files ...", mimes)
        if result!=None:
            state.export(result)

    def layer_delete_object_button_click(self, args):
        layer = state.get_active_layer()
        if layer != None:
            selected_proxys = layer.get_selected_proxys()
            layer.unselect_all_proxys()
            for p in selected_proxys:
                layer.remove_proxy_by_id(p.id)
            self.update_layer_objects_list(None)
            self.mw.widget.update()

    def deselect_all(self, args):
        layer = state.get_active_layer()
        if layer != None:
            selected_proxys = layer.get_selected_proxys()
            layer.unselect_all_proxys()
            state.unset_put_layer_object()
            self.mw.widget.update()            
            self.update_layer_objects_list(None)
            self.update_sprites_list(None)
            self.update_layers_list(None)

    def hscroll_base(self, arg):
        offset = state.get_base_offset()
        state.set_base_offset((arg, offset[1]))
        self.mw.widget.update()

    def hscroll(self, args):
        print args[0][0].get_value()
        self.hscroll_base(args[0][0].get_value())

    def vscroll_base(self, arg):
        offset = state.get_base_offset()
        state.set_base_offset((offset[0], arg))
        self.mw.widget.update()

    def vscroll(self, args):
        print args[0][0].get_value()
        self.vscroll_base(args[0][0].get_value())

ep = EventProcessor()
