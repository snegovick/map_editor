import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys

from state import state, State
from project import project

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
        print "pushing", event 
        self.event_list.append((event, args))

    def process(self):
        for e, args in self.event_list:
            if e in self.events:
                self.events[e](args)
            else:
                print "Unknown event:", e, args
        self.event_list = []

    def scroll_up(self, args):
        pass

    def scroll_down(self, args):
        pass

    def shift_press(self, args):
        pass

    def shift_release(self, args):
        pass

    def pointer_motion(self, args):
        pass

    def screen_left_press(self, args):
        pass

    def screen_left_release(self, args):
        pass

    def update_settings(self, args):
        print "settings update:", args
        new_value = args[0][1][0].get_value()
        setting = args[0][0]
        setting.set_value(new_value)
        project.push_state(state)
        self.mw.widget.update()



ep = EventProcessor()
