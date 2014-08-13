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
    export_click = "export_click"
    save_project_click = "save_click"
    load_project_click = "load_click"
    sprites_selection_changed = "sprites_selection_changed"
    add_to_selected_sprite_click = "add_to_selected_sprite_click"
    sprite_elements_list_selection_changed = "sprite_elements_list_selection_changed"
    sprite_image_remove_button_click = "sprite_image_remove_button_click"
    sprite_image_up_click = "sprite_image_up_click"
    sprite_image_down_click = "sprite_image_down_click"


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
            EVEnum.export_click: self.export_click,
            EVEnum.save_project_click: self.save_project_click,
            EVEnum.load_project_click: self.load_project_click,
            EVEnum.sprites_selection_changed: self.sprites_selection_changed,
            EVEnum.add_to_selected_sprite_click: self.add_to_selected_sprite_click,
            EVEnum.sprite_elements_list_selection_changed: self.sprite_elements_list_selection_changed,
            EVEnum.sprite_image_remove_button_click: self.sprite_image_remove_button_click,
            EVEnum.sprite_image_up_click: self.sprite_image_up_click,
            EVEnum.sprite_image_down_click: self.sprite_image_down_click,
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
        print "scale:", scale

    def scroll_down(self, args):
        scale = state.get_scale()
        if scale[0]>0.2:
            state.set_scale((scale[0]-0.1, scale[1]-0.1))
            self.mw.widget.update()
        print "scale:", scale

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

    def export_click(self, args):
        mimes = [("Tileset (*)", "", "*")]
        result = self.mw.mk_file_save_dialog("Save tileset ...", mimes)
        if result!=None:
            state.export(result)
        

    def save_project_click(self, args):
        mimes = [("Tileset project (*.tset)", "Application/tset", "*.tset")]
        result = self.mw.mk_file_save_dialog("Save project ...", mimes)
        if result!=None:
            project.save(result)

    def load_project_click(self, args):
        mimes = [("Tileset project (*.tset)", "Application/tset", "*.tset")]
        result = self.mw.mk_file_dialog("Open project ...", mimes)
        if result!=None:
            project.load(result)
            self.update_images_list(None)
            self.update_sprites_list(None)
            self.mw.widget.update()

    def update_sprite_images_list(self, args):
        sprite = state.get_selected_sprite()
        if sprite!=None:
            images = sprite.get_images()
            if images != None:
                self.mw.clear_list(self.mw.sprite_gtklist)
                for p in images:
                    self.mw.add_item_to_list(self.mw.sprite_gtklist, p.name, None)

    def sprites_selection_changed(self, args):
        selection = args[0][0].get_selection()
        state.unselect_sprite()
        name = selection[0].children()[0].children()[1].get_text()
        for s in state.get_sprites():
            if s.name == name:
                state.set_selected_sprite(s)
                self.update_sprite_images_list(None)
                print state.get_selected_sprite()
                break

    def add_to_selected_sprite_click(self, args):
        sprite = state.get_selected_sprite()
        if sprite != None:
            images = state.get_selected_images()
            if images != []:
                sprite.add_images(images)
                self.update_sprite_images_list(None)

    def sprite_elements_list_selection_changed(self, args):
        selection = args[0][0].get_selection()
        if selection != []:
            name = selection[0].children()[0].children()[1].get_text()
            sprite = state.get_selected_sprite()
            print "sprite:", sprite
            if sprite != None:
                for i in sprite.get_images():
                    if i.name == name:
                        sprite.set_selected_image(i)
                        break

    def sprite_image_remove_button_click(self, args):
        sprite = state.get_selected_sprite()
        print sprite
        if sprite != None:
            sprite.remove_selected_image()
            self.update_sprite_images_list(None)

    def sprite_image_down_click(self, args):
        sprite = state.get_selected_sprite()
        if sprite != None:
            if len(sprite.get_images()) > 1:
                sprite.down_selected_image()
                self.update_sprite_images_list(None)

    def sprite_image_up_click(self, args):
        sprite = state.get_selected_sprite()
        if sprite != None:
            if len(sprite.get_images()) > 1:
                sprite.up_selected_image()
                self.update_sprite_images_list(None)

ep = EventProcessor()
