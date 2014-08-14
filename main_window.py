#-*- encoding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor, ep
from state import state

class MainWindow(object):
    def __init__(self, w, h, Widget):
        self.window = gtk.Window()
        self.window.resize(w, h)
        self.window.connect("delete-event", gtk.main_quit)

        self.menu_bar = gtk.MenuBar()
        self.file_menu = gtk.Menu()
        self.file_item = gtk.MenuItem("File")
        self.file_item.set_submenu(self.file_menu)
        self.menu_bar.append(self.file_item)

        self.open_project_item = gtk.MenuItem("Open project ...")
        self.save_project_item = gtk.MenuItem("Save project ...")
        sep_export_import = gtk.SeparatorMenuItem()
        self.export_item = gtk.MenuItem("Export ...")
        self.quit_item = gtk.MenuItem("Quit")
        sep_quit = gtk.SeparatorMenuItem()

        self.file_menu.append(self.open_project_item)
        self.file_menu.append(self.save_project_item)
        self.file_menu.append(sep_export_import)
        self.file_menu.append(self.export_item)
        self.file_menu.append(sep_quit)
        self.file_menu.append(self.quit_item)

        self.export_item.connect("activate", lambda *args: ep.push_event(EVEnum.export_click, args))
        self.open_project_item.connect("activate", lambda *args: ep.push_event(EVEnum.load_project_click, args))
        self.save_project_item.connect("activate", lambda *args: ep.push_event(EVEnum.save_project_click, args))
        self.quit_item.connect("activate", lambda *args: ep.push_event(EVEnum.quit_click, args))

        self.window_vbox = gtk.VBox(homogeneous=False, spacing=0)
        self.window_vbox.pack_start(self.menu_bar, expand=False, fill=False, padding=0)
        self.window.add(self.window_vbox)

        self.widget = Widget()
        self.widget.connect("button_press_event", self.widget.button_press_event)
        self.widget.connect("button_release_event", self.widget.button_release_event)
        self.widget.connect("motion_notify_event", self.widget.motion_notify_event)
        self.widget.connect("scroll_event", self.widget.scroll_event)
        self.window.connect("key_press_event", self.widget.key_press_event)
        self.window.connect("key_release_event", self.widget.key_release_event)
        self.window.set_events(gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK)
        self.widget.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)

        self.__mk_left_vbox()

        self.hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.hbox.pack_start(self.left_vbox, expand=False, fill=False, padding=0)

        self.widget_hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.widget_vbox = gtk.VBox(homogeneous=False, spacing=0)
        self.widget_hscroll = gtk.HScrollbar(gtk.Adjustment(0.0, -1000.0, 1000.0, 0.1, 1.0, 1.0))
        self.widget_hscroll.connect("value-changed", lambda *args: ep.push_event(EVEnum.hscroll, (args)))
        self.widget_vscroll = gtk.VScrollbar(gtk.Adjustment(0.0, -1000.0, 1000.0, 0.1, 1.0, 1.0))
        self.widget_vscroll.connect("value-changed", lambda *args: ep.push_event(EVEnum.vscroll, (args)))
        self.widget_hbox.pack_start(self.widget, expand=True, fill=True, padding=0)
        self.widget_hbox.pack_start(self.widget_vscroll, expand=False, fill=False, padding=0)
        self.widget_vbox.pack_start(self.widget_hbox, expand=True, fill=True)
        self.widget_vbox.pack_start(self.widget_hscroll, expand=False, fill=False, padding=0)
        self.hbox.pack_start(self.widget_vbox, expand=True, fill=True, padding=0)

        self.cursor_pos_label = gtk.Label("")
        self.widget_vbox.pack_start(self.cursor_pos_label, expand=False, fill=False)

        self.__mk_right_vbox()
        self.hbox.pack_start(self.right_vbox, expand=False, fill=False, padding=0)
        gobject.timeout_add(30, self.widget.periodic)
        self.window_vbox.pack_start(self.hbox, expand=True, fill=True, padding=0)

    def run(self):
        self.window.show_all()
        self.window.present()
        gtk.main()

    def new_settings_vbox(self, settings_lst, label):
        for c in self.settings_vb.children():
            self.settings_vb.remove(c)
        if settings_lst == None:
            return
        l = gtk.Label(label)
        self.settings_vb.pack_start(l, expand=False, fill=False, padding=0)
        l.show()
        print settings_lst
        for s in settings_lst:
            dct = {}
            if s.type == "float":
                w = self.__mk_labeled_spin(dct, s.display_name, s, None, s.default, s.min, s.max)
                self.settings_vb.pack_start(w, expand=False, fill=False, padding=0)
            if s.type == "bool":
                w = self.__mk_labeled_checkbox(dct, s.display_name, )

    def mk_question_dialog(self, question):
        md = gtk.Dialog(title=question, parent=self.window, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        yes_button = md.add_button(gtk.STOCK_YES, gtk.RESPONSE_YES)
        no_button = md.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
        yes_button.grab_default()
        vbox = md.get_content_area()
        l = gtk.Label(question)
        l.show()
        vbox.pack_end(l)
        response = md.run()
        ret = True
        if response == gtk.RESPONSE_NO:
            ret = False
        md.destroy()
        return ret

    def mk_textbox_dialog(self, question):
        md = gtk.Dialog(title=question, parent=self.window, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        ok_button = md.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        cancel_button = md.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        ok_button.grab_default()
        vbox = md.get_content_area()

        l = gtk.Label(question)
        l.show()
        vbox.pack_end(l)

        entry = gtk.Entry()
        entry.show()
        vbox.pack_start(entry)
        response = md.run()
        ret = True
        if response == gtk.RESPONSE_CANCEL:
            ret = False, None
        text = entry.get_text()
        md.destroy()
        return ret, text

    def mk_file_dialog(self, name, mimes):
        ret = None
        dialog = gtk.FileChooserDialog(name,
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        for m in mimes:
            filter = gtk.FileFilter()
            filter.set_name(m[0])
            filter.add_mime_type(m[1])
            filter.add_pattern(m[2])
            dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            ret = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        return ret

    def mk_file_save_dialog(self, name, mimes):
        ret = None
        dialog = gtk.FileChooserDialog(name,
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        for m in mimes:
            filter = gtk.FileFilter()
            filter.set_name(m[0])
            filter.add_mime_type(m[1])
            filter.add_pattern(m[2])
            dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            ret = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        return ret
                
    def clear_list(self, lst):
        children = lst.children()
        for c in children:
            lst.remove(c)

    def add_item_to_list(self, lst, label_text, event):
        check_button = gtk.CheckButton("")
        check_button.set_active(True)
        check_button.unset_flags(gtk.CAN_FOCUS)
        check_button.show()
        if event != None:
            check_button.connect("clicked", lambda *args: ep.push_event(event, (label_text, args)))

        label = gtk.Label(label_text)
        label.show()

        hbox = gtk.HBox(homogeneous=False, spacing=0)
        hbox.pack_start(check_button, expand=False, fill=False, padding=0)
        hbox.pack_start(label, expand=False, fill=False, padding=0)
        hbox.show()

        list_item = gtk.ListItem()
        list_item.show()
        list_item.add(hbox)
        lst.add(list_item)

    def __mk_labeled_spin(self, dct, mlabel, data=None, callback=None, value=8, lower=-999.0, upper=999.0, step_incr=1.0, page_incr=5.0):
        if lower == None:
            lower = -999.0
        if upper == None:
            upper = 999.0
        if step_incr == None:
            step_incr = 1.0
        if page_incr == None:
            page_incr = 0.5
        hbox = gtk.HBox(homogeneous=False, spacing=0)
        hbox.show()
        dct["hbox"] = hbox
        label = gtk.Label(mlabel)
        label.show()
        dct["label"] = label
        spin = gtk.SpinButton(adjustment=gtk.Adjustment(value=value, lower=lower, upper=upper, step_incr=step_incr, page_incr=page_incr, page_size=0), climb_rate=0.01, digits=3)
        spin.connect("value-changed", lambda *args: ep.push_event(EVEnum.update_settings, (data, args)))
        spin.show()
        dct["spin"] = spin
        hbox.pack_start(label, expand=False, fill=False, padding=0)
        hbox.pack_start(spin, expand=True, fill=True, padding=0)
        return hbox

    def __mk_labeled_checkbox(self, dct, mlabel, callback=None, default=False):
        hbox = gtk.HBox(homogeneous=False, spacing=0)
        hbox.show()
        dct["hbox"] = hbox
        check = gtk.CheckButton("mlabel")
        check.connect("clicked", lambda *args: ep.push_event(EVEnum.update_settings, (data, check.get_acrive())))
        check.show()
        dct["check"] = check
        hbox.pack_start(check, expand=True, fill=True, padding=0)
        return hbox

    def __mk_right_vbox(self):
        self.right_vbox = gtk.VBox(homogeneous=False, spacing=0)

        self.tool_label = gtk.Label("General settings")
        self.right_vbox.pack_start(self.tool_label, expand=False, fill=False, padding=0)

        settings_lst = state.get_settings_list()
        if settings_lst != None:
            print settings_lst
            for s in settings_lst:
                dct = {}
                if s.type == "int":
                    w = self.__mk_labeled_spin(dct, s.display_name, s, None, s.default, s.min, s.max)
                    self.right_vbox.pack_start(w, expand=False, fill=False, padding=0)
                elif s.type == "bool":
                    w = self.__mk_labeled_checkbox(dct, s.display_name, s, s.default)
                    self.right_vbox.pack_start(w, expand=False, fill=False, padding=0)


        self.settings_vb = gtk.VBox(homogeneous=False, spacing=0)
        self.right_vbox.pack_start(self.settings_vb, expand=False, fill=False, padding=0)

    def __mk_left_vbox(self):
        self.left_vbox = gtk.VBox(homogeneous=False, spacing=0)

        self.new_sprite_button = gtk.Button("New sprite from selection")
        self.new_sprite_button.connect("clicked", lambda *args: ep.push_event(EVEnum.new_sprite_click, args))
        self.left_vbox.pack_start(self.new_sprite_button, expand=False, fill=False, padding=0)

        self.add_to_selected_sprite_button = gtk.Button("Add to selected sprite")
        self.add_to_selected_sprite_button.connect("clicked", lambda *args: ep.push_event(EVEnum.add_to_selected_sprite_click, args))
        self.left_vbox.pack_start(self.add_to_selected_sprite_button, expand=False, fill=False, padding=0)

        self.load_image_button = gtk.Button("Load image")
        self.load_image_button.connect("clicked", lambda *args: ep.push_event(EVEnum.load_image_click, args))
        self.left_vbox.pack_start(self.load_image_button, expand=False, fill=False, padding=0)

        self.sprites_label = gtk.Label("Sprites")
        self.sp_scrolled_window = gtk.ScrolledWindow()
        self.sp_gtklist = gtk.List()
        self.sp_gtklist.connect("selection_changed", lambda *args: ep.push_event(EVEnum.sprites_selection_changed, args))
        self.sp_scrolled_window.add_with_viewport(self.sp_gtklist)

        self.left_vbox.pack_start(self.sprites_label, expand=False, fill=False, padding=0)
        self.left_vbox.pack_start(self.sp_scrolled_window, expand=True, fill=True, padding=0)
        self.sprite_delete_button = gtk.Button("Delete sprite")
        self.sprite_delete_button.connect("clicked", lambda *args: ep.push_event(EVEnum.sprite_delete_button_click, None))
        self.left_vbox.pack_start(self.sprite_delete_button, expand=False, fill=False, padding=0)



