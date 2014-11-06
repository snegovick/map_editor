import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor, ep
from main_window import MainWindow
from state import state

width=640
height=480

class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    step = 0
    event_consumers = []
    active_event_consumer = None

    def periodic(self):
        ep.process()
        return True

    def update(self):
        self.queue_draw()

    def scroll_event(self, widget, event):
        print "event:", event
        if event.direction == gtk.gdk.SCROLL_UP:
            ep.push_event(EVEnum.scroll_up, (None))
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            ep.push_event(EVEnum.scroll_down, (None))
    
    def button_press_event(self, widget, event):
        print "button press:", event.button

        if event.button == 1:
            ep.push_event(EVEnum.screen_left_press, (event.x, event.y))

    def key_press_event(self, widget, event):
        print "key press:", event.keyval
        if event.keyval == 65307: # ESC
            ep.push_event(EVEnum.deselect_all, (None))
        elif event.keyval == 65505: # shift
            ep.push_event(EVEnum.shift_press, (None))
        elif event.keyval == 65507: # ctrl
            ep.push_event(EVEnum.ctrl_press, (None))
        elif event.keyval == 65535: # delete
            ep.push_event(EVEnum.delete_press, (None))
        elif event.keyval == 115: # s key (start selection)
            ep.push_event(EVEnum.set_selection_mode, (None))

    def key_release_event(self, widget, event):
        if event.keyval == 65505: # shift
            ep.push_event(EVEnum.shift_release, (None))
        elif event.keyval == 65507: # ctrl
            ep.push_event(EVEnum.ctrl_release, (None))
        # elif event.keyval == 115: # s key (stop selection)
        #     ep.push_event(EVEnum.unset_selection_mode, (None))

    def button_release_event(self, widget, event):
        if event.button == 1:
            ep.push_event(EVEnum.screen_left_release, (event.x, event.y))

    def motion_notify_event(self, widget, event):
        ep.push_event(EVEnum.pointer_motion, (event.x, event.y))

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context
        #state.offset = (self.allocation.width/2,self.allocation.height/2)
        #state.set_screen_offset((self.allocation.width/2, self.allocation.height/2))
        state.set_screen_offset((0, 0))
        scale = state.get_scale()
        
        offset = state.get_offset()

        cr_gdk = self.window.cairo_create()
        surface = cr_gdk.get_target()
        size = state.get_map_size_px()
        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, event.area.width, event.area.height)
        cr = cairo.Context(cr_surf)
        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, int(size[0]*scale[0]), int(size[1]*scale[1]))
        cr.fill()

        layers = state.get_layers()
        pointer = state.get_pointer_position()
        
        if len(layers) == 0:
            cr.set_source_rgb(0.1, 0.1, 0.1)
            f_size = 13
            cr.set_font_size(f_size)
            text = "There is no layer yet, add one please"
            (x, y, width, height, dx, dy) = cr.text_extents(text)
            cr.move_to(self.allocation.width/2-width/2, self.allocation.height/2)
            cr.show_text(text);
        else:
            layer = state.get_active_layer()
            if state.get_put_layer_object():
                lo = layer.get_selected_layer_object()
                cr.translate(offset[0]+pointer[0], offset[1]+pointer[1])
                cr.scale(scale[0], scale[1])
                lo.draw_preview(cr)
                cr.identity_matrix()

            for l in layers:
                cr.translate(offset[0], offset[1])
                cr.scale(scale[0], scale[1])
                if l == layer:
                    l.draw(cr, 1.0)
                else:
                    l.draw(cr, 0.8)
                cr.identity_matrix()


            cr.set_source_rgb(0, 0, 0)
            cr.set_line_width(0.1)
            cr.translate(offset[0], offset[1])
            cr.scale(scale[0], scale[1])
            grid_step = state.get_grid_step()
            for y in range(0, int(size[1]), grid_step[1]):
                cr.move_to(0, y)
                cr.line_to(size[0], y)

            for x in range(0, int(size[0]), grid_step[0]):
                cr.move_to(x, 0)
                cr.line_to(x, size[1])
            cr.stroke()
            cr.identity_matrix()

        screen_size = state.get_screen_size()
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.5)
        cr.rectangle(int(screen_size[0]*scale[0]), 0, event.area.width, event.area.height)
        cr.fill()

        cr.set_source_rgba(0.5, 0.5, 0.5, 0.5)
        cr.rectangle(0, int(screen_size[1]*scale[1]), event.area.width, event.area.height)
        cr.fill()


        sel_box = state.get_selection_box()
        if state.is_selection_mode():
            sx = min(sel_box[0], sel_box[2])
            ex = max(sel_box[0], sel_box[2])
            sy = min(sel_box[1], sel_box[3])
            ey = max(sel_box[1], sel_box[3])

            w = ex - sx
            h = ey - sy
            sel_box = [sx, sy, w, h]

            #print "sel_box:", sel_box
            #print "offset:", offset, "scale:", scale
            cr.set_source_rgba(0.7, 0.7, 0.9, 0.5)
            cr.rectangle(int(sel_box[0]*scale[0]), int(sel_box[1]*scale[1]), int(sel_box[2]*scale[0]), int(sel_box[3]*scale[1]))
            cr.fill()
        
        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

mw = MainWindow(width, height, Screen)
ep.mw = mw
state.mw = mw

        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run():
    mw.run()

if __name__ == "__main__":
    run()
