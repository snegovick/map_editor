import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

import os
import sys
import parser

import screen

class LayerList:
    def __init__(self):
        self.liststore = gtk.ListStore(str)
        self.treeview = gtk.TreeView(self.liststore)

        self.cell = gtk.CellRendererText()
        self.tvcolumn = gtk.TreeViewColumn('Layers')
        self.tvcolumn.pack_start(self.cell, False)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        self.treeview.append_column(self.tvcolumn)
        self.layers = []
        
    def init(self):
        self.treeview.get_selection().connect("changed", self.application.treeview_row_activated)

    def addLayer(self):
        self.liststore.append(str(len(self.layers)))
        self.layers.append(len(self.layers))

    def getWidget(self):
        return self.treeview

class ButtonList:
    def __init__(self):
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.vbox = gtk.VBox()
        self.scrolled_window.add_with_viewport(self.vbox)
        self.button_layers = []
        self.active_layer = 0
        self.application = None
        self.window = None
        
    def setActiveLayer(self, layer):
        self.active_layer = layer
        for c in self.vbox.get_children():
            self.vbox.remove(c)

        for b in self.button_layers[self.active_layer]:
            self.vbox.pack_start(b, False, False)
    
    def getWidget(self):
        return self.scrolled_window
        
    def addLayer(self, tileset, meta=""):
        for c in self.vbox.get_children():
            self.vbox.remove(c)

        self.active_layer = len(self.button_layers)
        self.button_layers.append([])
        
        image = gtk.Image()
        image.set_from_file("delete.png")
        image.show()

        button = gtk.Button()
        button.add(image)
        button.show()
        button.connect("clicked", self.application.button_click_event, "delete")
        self.button_layers[self.active_layer].append(button)
        self.vbox.pack_start(button, False, False)

        if meta == "meta":
            for i, (r, g, b) in enumerate(screen.meta_markers):
                color_string = "#"
                color = int(255*r)
                color_string+=hex(color)[2:].zfill(2)
                color = int(255*g)
                color_string+=hex(color)[2:].zfill(2)
                color = int(255*b)
                color_string+=hex(color)[2:].zfill(2)

                
                xpm_data = ["64 64 1 1",
                            "a c "+color_string]
                for y in range(64):
                    s = ""
                    for x in range(64):
                        s+="a"
                    xpm_data.append(s)
                for l in xpm_data:
                    print l
                pixmap, mask = gtk.gdk.pixmap_create_from_xpm_d(self.window.window, None,xpm_data)
                image = gtk.Image()
                image.set_from_pixmap(pixmap, mask)
                image.show()
                button = gtk.Button()
                button.add(image)
                button.show()
                button.connect("clicked", self.application.button_click_event, str(i))
                self.button_layers[self.active_layer].append(button)
                self.vbox.pack_start(button, False, False)
        else:
            for t in tileset:    
                image = gtk.Image()
                image.set_from_file(t)
                image.show()
                button = gtk.Button()
                button.add(image)
                button.show()
                button.connect("clicked", self.application.button_click_event, t)
                self.button_layers[self.active_layer].append(button)
                self.vbox.pack_start(button, False, False)
        self.vbox.show()

class ControlWindow:
    def __init__(self):
        self.application = None

    def setActiveLayer(self, layer):
        self.button_list.setActiveLayer(layer)

    def init(self):
        self.window = gtk.Window()
        self.window.connect("delete-event", gtk.main_quit)
        self.main_vbox = gtk.VBox()

        toolbar = gtk.Toolbar()
        new_tilemap_b = toolbar.append_item("Add map", "Adds new tile map", None, None, None, None)
        new_tilemap_b.connect("clicked", self.application.newTileLayer, "")
        new_map_b = toolbar.append_item("Add metamap", "Adds new meta map", None, None, None, None)
        new_map_b.connect("clicked", self.application.newTileLayer, "meta")
        delete_map_b = toolbar.append_item("Delete map", "Deletes map", None, None, None, None)
        self.main_vbox.pack_start(toolbar, False, False)

        self.layer_list = LayerList()
        self.layer_list.application = self.application
        self.layer_list.init()
        self.button_list = ButtonList()
        self.button_list.application = self.application
        self.button_list.window = self.window
        
        self.main_vbox.pack_start(self.layer_list.getWidget())

        self.main_vbox.pack_start(self.button_list.getWidget())

        width = 120
        height = 320
        self.window.add(self.main_vbox)
        self.window.resize(width, height)
        self.window.show_all()

    def new(self, path):
        pass

    def newMetaLayer(self):
        pass

    def newTileLayer(self, tileset, meta=""):
        self.button_list.addLayer(tileset, meta)
        self.layer_list.addLayer()
