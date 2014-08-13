import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

import os
import sys
from parser import Parser

from screen import *
from map_container import *
from editor_window import *
from control_window import *

class Application:
    def __init__(self):
        self.editor = EditorWindow()
        self.control = ControlWindow()
        self.control.application = self

    def button_click_event(self, widget, data = None):
        self.editor.button_click_event(widget, data)

    def treeview_row_activated(self, selection):
        (model, iter) = selection.get_selected()
        text = model[iter][0]
        print "text:", text
        self.editor.setActiveLayer(int(text))
        self.control.setActiveLayer(int(text))

    def run(self):
        self.editor.init()
        self.editor.mnew.connect("activate", self.new)
        self.editor.save.connect("activate", self.save)
        self.editor.load.connect("activate", self.load)
        self.control.init()
        gtk.main()

    def save(self, w):
        dialog = gtk.FileChooserDialog("Save file..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        path = ""
        if response == gtk.RESPONSE_OK:
            path = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
            dialog.destroy()
            return
        dialog.destroy()

        self.editor.saveMap(path)

    def load(self, w):
        dialog = gtk.FileChooserDialog("Open file..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        path = ""
        if response == gtk.RESPONSE_OK:
            path = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
            dialog.destroy()
            return
        dialog.destroy()

        p = Parser()
        values = p.parse(path)

        n_layers = int(values["n_layers"])
        width = int(values["width"])
        height = int(values["height"])
        px_scale = int(values["px_scale"])

        self.editor.new(int(width), int(height), int(px_scale))
        print "paths:", values["paths"]
        for i, meta in enumerate(values["meta"]):
            tileset = values["tset_"+str(i)]
            tset = []
            if meta != "meta":
                for j, t in enumerate(tileset):
                    path = values["paths"][i]
                    tset.append(path+"/"+t)

            print "tileset", i, ":", tset
            m = values["map_"+str(i)]
            mp = [[None for x in range(width)] for y in range(height)]
            for y, l in enumerate(mp):
                for x, v in enumerate(l):
                    mp[y][x] = int(m[x+y*width]) if m[x+y*width]>=0 else None
            self.editor.newTileLayer(tset, meta)
            self.editor.setMap(mp, i)
            self.control.newTileLayer(tset, meta)
                        

        #self.editor.loadMap(values)


    def new(self, w):
        label = gtk.Label("Please enter map dimensions:")
        dialog = gtk.Dialog("Enter map dimensions",
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label.show()
        hbox = gtk.HBox()
        hbox.show()
        dialog.vbox.pack_start(hbox)
        hbox.pack_start(label)
        ax = gtk.Adjustment(0, 0, 1000, 1, 5)
        ay = gtk.Adjustment(0, 0, 1000, 1, 5)
        x = gtk.SpinButton(ax, climb_rate = 1, digits = 0)
        y = gtk.SpinButton(ay, climb_rate = 1, digits = 0)
        x.show()
        y.show()
        hbox.pack_start(x)
        hbox.pack_start(y)

        hbox = gtk.HBox()
        hbox.show()
        dialog.vbox.pack_start(hbox)
        label = gtk.Label("Tile dimensions:")
        hbox.pack_start(label)

        label.show()

        ascale = gtk.Adjustment(0, 0, 128, 1, 5)
        scale = gtk.SpinButton(ascale, climb_rate = 1, digits = 0)
        scale.show()
        hbox.pack_end(scale)

        response = dialog.run()
        dialog.destroy()

        self.editor.new(x.get_value_as_int(), y.get_value_as_int(), scale.get_value_as_int())

    def newTileLayer(self, w, arg):

        if arg=="meta":
            self.editor.newTileLayer([], arg)
            self.control.newTileLayer([], arg)
            return
        dialog = gtk.FileChooserDialog("Choose tileset directory..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        path = ""
        if response == gtk.RESPONSE_OK:
            path = dialog.get_current_folder()
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
            dialog.destroy()
            return
        dialog.destroy()

        tileset = []
        for dirname, dirnames, filenames in os.walk(path):
            for fname in filenames:
                tileset.append(dirname+"/"+fname)
                print "adding ", fname, "to tileset"

        self.editor.newTileLayer(tileset, arg)
        self.control.newTileLayer(tileset, arg)

        

if __name__ == "__main__":
    a = Application()
    a.run()
