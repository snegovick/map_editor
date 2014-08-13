import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

import os
import sys
import parser

from screen import *

class EditorWindow:
    def __init__(self):
        self.mnew = None
        self.save = None
        self.load = None
        self.added_tiles = []

    def setActiveLayer(self, layer):
        self.screen.active_layer = layer

    def new(self, w, h, scale):
        self.screen.newMap(w, h, scale)
        self.width = 640
        self.height = 480
        self.screen.width = self.width
        self.screen.height = self.height
        self.window.resize(self.width, self.height)

    def newTileLayer(self, tileset, meta=""):
        self.screen.newTileLayer(tileset, meta)

    def button_click_event(self, widget, data = None):
        self.screen.button_click_event(widget, data)

    def saveMap(self, path):
        self.screen.save(path)

    def setMap(self, m, layer):
        self.screen.setMap(m, layer)

    def on_resize(self, args):
        self.width, self.height = args.get_size()
        self.screen.width = self.width
        self.screen.height = self.height
        # self.window.resize(self.width, self.height)
    
    def init(self):
        self.window = gtk.Window()
        self.window.connect("delete-event", gtk.main_quit)
        main_vbox = gtk.VBox()
        self.screen = Screen()
        gobject.timeout_add(10, self.screen.periodic)
        self.screen.connect("button-press-event", self.screen.button_press_event)
        self.screen.connect("button-release-event", self.screen.button_release_event)
        self.screen.connect("motion-notify-event", self.screen.motion_notify_event)
        self.window.connect("check-resize", self.on_resize)
        self.screen.set_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
        
        menubar = gtk.MenuBar()
        filemenu = gtk.Menu()
        filem = gtk.MenuItem("File")
        filem.set_submenu(filemenu)
        
        self.mnew = gtk.MenuItem("New")
        # self.new.connect("activate", self.mnew)
        filemenu.append(self.mnew)
        
        menubar.append(filem)
        self.save = gtk.MenuItem("Save")
        #save.connect("activate", m.save)
        filemenu.append(self.save)
        
        self.load = gtk.MenuItem("Load")
        #load.connect("activate", m.load)
        filemenu.append(self.load)
        
        main_vbox.pack_start(menubar, False, False)
        main_hbox = gtk.HBox()

        main_hbox.pack_start(self.screen, True, True)
        self.vadjustment = gtk.Adjustment(0, 0, 1, 0.1, 0.2)
        self.vscroll = gtk.VScrollbar(self.vadjustment)
        self.vscroll.connect("value-changed", self.screen.vscroll)
        main_hbox.pack_start(self.vscroll, False, False)
        main_vbox.pack_start(main_hbox)
        self.hadjustment = gtk.Adjustment(0, 0, 1, 0.1, 0.2)
        self.hscroll = gtk.HScrollbar(self.hadjustment)
        self.hscroll.connect("value-changed", self.screen.hscroll)
        main_vbox.pack_start(self.hscroll, False, False)
        self.screen.show()
        self.width = 120
        self.height = 160
        self.screen.width = 120
        self.screen.height = 160
        self.window.add(main_vbox)
        self.window.resize(self.width, self.height)
        self.window.present()
        self.window.show_all()
