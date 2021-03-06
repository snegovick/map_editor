import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor, ep
from main_window import MainWindow
from state import state
from project import project
import utils

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

    def key_release_event(self, widget, event):
        if event.keyval == 65505: # shift
            ep.push_event(EVEnum.shift_release, (None))

    def button_release_event(self, widget, event):
        if event.button == 1:
            ep.push_event(EVEnum.screen_left_release, (event.x, event.y))

    def motion_notify_event(self, widget, event):
        ep.push_event(EVEnum.pointer_motion, (event.x, event.y))

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context
        #state.offset = (self.allocation.width/2,self.allocation.height/2)
        state.set_screen_offset((self.allocation.width/2, self.allocation.height/2))
        scale = state.get_scale()
        
        offset = state.get_offset()

        cr_gdk = self.window.cairo_create()
        surface = cr_gdk.get_target()
        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(state.atlas_size*scale[0]), int(state.atlas_size*scale[1]))
        cr = cairo.Context(cr_surf)
        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, int(state.atlas_size*scale[0]), int(state.atlas_size*scale[1]))
        cr.fill()

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(0.1)
        cr.translate(offset[0], offset[1])
        cr.scale(scale[0], scale[1])
        grid_step = state.get_grid_step()
        for y in range(0, int(self.allocation.height/scale[1]), grid_step[1]):
            cr.move_to(0, y)
            cr.line_to(self.allocation.width/scale[0], y)

        for x in range(0, int(self.allocation.width/scale[0]), grid_step[0]):
            cr.move_to(x, 0)
            cr.line_to(x, self.allocation.height/scale[1])
        cr.stroke()
        cr.identity_matrix()

        
        images = state.get_images()
        cr.translate(offset[0], offset[1])
        cr.scale(state.scale[0], state.scale[1])
        for img in images:
            img.draw(cr)
        cr.identity_matrix()
        
        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

mw = MainWindow(width, height, Screen)
ep.mw = mw

        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run():
    mw.run()

if __name__ == "__main__":
    usage = "pythone tileset_editor.py [-h] [--reexport] [--project <path>] [--out <path>]"
    if len(sys.argv) > 1:
        description = {"-h": {"arglen": 0, "arg": None, "present": False},
                       "--reexport": {"arglen": 0, "arg": None, "present": False},
                       "--project": {"arglen": 1, "arg": None, "present": False},
                       "--out": {"arglen": 1, "arg": None, "present": False}}
        if utils.parse_args(sys.argv, description) == True:
            if description["-h"]["present"]:
                print usage
                exit(0)
            elif description["--reexport"]["present"]:
                if description["--project"]["present"] and description["--out"]["present"]:
                    project_path = description["--project"]["arg"]
                    out_path = description["--out"]["arg"]
                    print "Loading project from:", project_path
                    project.load(project_path)
                    print "Exporting project to:", out_path
                    state.export(out_path)
                    exit(0)
    run()
