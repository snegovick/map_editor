import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys

from state import state, State
from project import project
from sprite import Sprite
import utils

class EVEnum:
    scroll_up = "scroll_up"
    scroll_down = "scroll_down"
    update_settings = "update_settings"
    shift_press = "shift_press"
    shift_release = "shift_release"
    pointer_motion = "pointer_motion"
    screen_left_press = "screen_left_press"
    screen_left_release = "screen_left_release"
    load_image_click = "load_image_click"
    image_list_selection_changed = "image_list_selection_changed"
    new_sprite_click = "new_sprite_click"

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
            EVEnum.load_image_click: self.load_image_click,
            EVEnum.image_list_selection_changed: self.image_list_selection_changed,
            EVEnum.new_sprite_click: self.new_sprite_click,
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
        if scale[0]<=1:
            state.set_scale((scale[0]+0.1, scale[1]+0.1))
        else:
            state.set_scale((scale[0]+1, scale[1]+1))
        self.mw.widget.update()

    def scroll_down(self, args):
        scale = state.get_scale()
        if scale[0]>0.1:
            if scale[0]<=1:
                state.set_scale((scale[0]-0.1, scale[1]-0.1))
            else:
                state.set_scale((scale[0]-1, scale[1]-1))
            self.mw.widget.update()

    def shift_press(self, args):
        state.set_shift_pressed()

    def shift_release(self, args):
        state.reset_shift_pressed()

    def pointer_motion(self, args):
        offset = state.get_offset()
        scale = state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]
        pointer_position = (cx, cy)

        if state.get_left_press_start() != None:
            prev_position = state.get_pointer_position()
            grid_step = state.get_grid_step()
            images = state.get_selected_images()

            for i in images:
                nx = cx + self.relative_coords[i][0]
                ny = cy + self.relative_coords[i][1]
                i.set_origin((int(nx/grid_step[0])*grid_step[0], int(ny/grid_step[1])*grid_step[1]))
            self.mw.widget.update()
        state.set_pointer_position(pointer_position)
        self.mw.cursor_pos_label.set_text("%.3f:%.3f"%(cx, cy))

    def screen_left_press(self, args):
        offset = state.get_offset()
        scale = state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]
        state.set_left_press_start((cx, cy))
        images = state.get_images()
        selected_images = state.get_selected_images()
        
        if state.get_shift_pressed():
            for img in images:
                if img.point_in_aabb([cx, cy]):
                    if not img.get_selected():
                        state.add_im_to_selected(img)
                    else:
                        del self.relative_coords[img]
                        state.remove_im_from_selected(img)
        else:
            selected = None
            for img in images:
                if img.point_in_aabb([cx, cy]):
                    selected = img
            if selected != None:
                if selected.get_selected():
                    state.unselect_all_images()
                    self.relative_coords = {}
                else:
                    state.unselect_all_images()
                    self.relative_coords = {}
                    state.add_im_to_selected(selected)
                    
        self.mw.widget.update()

        selected_images = state.get_selected_images()
        self.relative_coords = {}
        for i in selected_images:
            self.relative_coords[i] = utils.mk_vect((cx, cy), i.get_origin())

    def screen_left_release(self, args):
        offset = state.get_offset()
        scale = state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]

        state.reset_left_press_start()

    def update_settings(self, args):
        print "settings update:", args
        new_value = args[0][1][0].get_value()
        setting = args[0][0]
        setting.set_value(new_value)
        project.push_state(state)
        self.mw.widget.update()

    def update_images_list(self, args):
        images = state.get_images()
        if  images != None:
            self.mw.clear_list(self.mw.gtklist)
            for p in images:
                self.mw.add_item_to_list(self.mw.gtklist, p.name, None)
        project.push_state(state)

    def load_image_click(self, args):
        mimes = [("Images (*.png)", "Image/png", "*.png")]
        result = self.mw.mk_file_dialog("Open ...", mimes)
        if result != None:
            image_name = result
            state.load_image(image_name)
            self.update_images_list(None)
            self.mw.widget.update()

    def update_sprites_list(self, args):
        sprites = state.get_sprites()
        if sprites != None:
            self.mw.clear_list(self.mw.sp_gtklist)
            for p in sprites:
                self.mw.add_item_to_list(self.mw.sp_gtklist, p.name, None)
        project.push_state(state)

    def new_sprite_click(self, args):
        selected = state.get_selected_images()
        print selected
        if selected != []:
            res, text = self.mw.mk_textbox_dialog("Enter sprite name:")
            print "result:", res, text
            if res:
                s = Sprite(selected, text)
                state.add_sprite(s)
                self.update_sprites_list(None)

    def image_list_selection_changed(self, args):
        selection = args[0][0].get_selection()
        state.unselect_all_images()
        for i in selection:
            name = i.children()[0].children()[1].get_text()
            for img in state.get_images():
                if img.name == name:
                    state.add_im_to_selected(img)
        self.mw.widget.update()

ep = EventProcessor()
