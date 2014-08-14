import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys

from state import state, State
from project import project
from sprite import Sprite
from tileset_editor import utils

class EVEnum:
    scroll_up = "scroll_up"
    scroll_down = "scroll_down"
    update_settings = "update_settings"
    shift_press = "shift_press"
    shift_release = "shift_release"
    pointer_motion = "pointer_motion"
    screen_left_press = "screen_left_press"
    screen_left_release = "screen_left_release"

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
        new_value = args[0][1][0].get_value()
        setting = args[0][0]
        setting.set_value(new_value)
        project.push_state(state)
        self.mw.widget.update()

ep = EventProcessor()
