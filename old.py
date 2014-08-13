    def load(self, w):
        dialog = gtk.FileChooserDialog("Open..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("Maps")
        filter.add_pattern("*.gmp")
        dialog.add_filter(filter)
        
        response = dialog.run()
        filename = ""
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename(), 'selected'
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
            dialog.destroy()
            return
        dialog.destroy()

        p = parser.Parser()
        values = p.parse(filename[0])

        path = values["path"]
        self.tileset = [path+"/"+fname for fname in values["tileset"]]
        w = int(values["width"])
        h = int(values["height"])

        widget.width = 64*w
        widget.height = 64*h

        self.createTileMap(w, h)
        x = 0
        y = 0
        i = 0
        for v in values["map"]:
            self.tile_map[y][x] = int(v)
            x+=1
            if (x%w==0):
                y+=1
                x=0

        for c in vbox.get_children():
            vbox.remove(c)

        image = gtk.Image()
        image.set_from_file("delete.png")
        image.show()

        button = gtk.Button()
        button.add(image)
        button.show()
        button.connect("clicked", widget.button_click_event, "delete")
        vbox.pack_start(button, False, False)

        for dirname, dirnames, filenames in os.walk(path):
            print "Going into", dirname
            for fname in filenames:
    
                image = gtk.Image()
                image.set_from_file(dirname+"/"+fname)
                image.show()
                button = gtk.Button()
                button.add(image)
                button.show()
                button.connect("clicked", widget.button_click_event, dirname+fname)
                vbox.pack_start(button, False, False)

        width = vbox.get_allocation().width+widget.width
        height = widget.height
        window.resize(width, height)
        self.is_updated = True

    def new(self, w):
        label = gtk.Label("Please enter map dimensions:")
        dialog = gtk.Dialog("My dialog",
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.vbox.pack_start(label)
        label.show()
        ax = gtk.Adjustment(self.xtiles, self.xtiles, 40, 1, 5)
        ay = gtk.Adjustment(self.ytiles, self.ytiles, 40, 1, 5)
        x = gtk.SpinButton(ax, climb_rate = 1, digits = 0)
        y = gtk.SpinButton(ay, climb_rate = 1, digits = 0)
        x.show()
        y.show()
        dialog.action_area.pack_end(x)
        dialog.action_area.pack_end(y)
        response = dialog.run()
        dialog.destroy()

        dialog = gtk.FileChooserDialog("Choose directory..",
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

        self.createTileMap(x.get_value_as_int(), y.get_value_as_int())

        widget.width = 64*self.xtiles
        widget.height = 64*self.ytiles

        for c in vbox.get_children():
            vbox.remove(c)

        image = gtk.Image()
        image.set_from_file("delete.png")
        image.show()

        button = gtk.Button()
        button.add(image)
        button.show()
        button.connect("clicked", widget.button_click_event, "delete")
        vbox.pack_start(button, False, False)

        for dirname, dirnames, filenames in os.walk(path):
            print "Going into", dirname
            for fname in filenames:
    
                image = gtk.Image()
                image.set_from_file(dirname+"/"+fname)
                image.show()
                button = gtk.Button()
                button.add(image)
                button.show()
                button.connect("clicked", widget.button_click_event, dirname+"/"+fname)
                vbox.pack_start(button, False, False)

        vbox.show()


        width = vbox.get_allocation().width+widget.width
        height = widget.height
        window.resize(width, height)
        self.is_updated = True

    def save(self, w):
        dialog = gtk.FileChooserDialog("Save..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("Maps")
        filter.add_pattern("*.gmp")
        dialog.add_filter(filter)
        
        response = dialog.run()
        filename = ""
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename(), 'selected'
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
            dialog.destroy()
            return
        dialog.destroy()
        
        used_sprites = []
        for line in self.tile_map:
            for x in line:
                if x == 0:
                    x = ""
                print x
                if x not in used_sprites:
                    used_sprites.append(x)

        print "used sprites:", used_sprites

        new_map = []
        for line in self.tile_map:
            for x in line:
                if x == 0:
                    x = ""
                idx = used_sprites.index(x)
                new_map.append(float(idx))
        outstr = ""
        for i, l in enumerate(new_map):
            outstr+=str(l)+" "
            if (i+1)%self.xtiles == 0:
                print outstr
                outstr = ""
        outfile = "str path = \""+str(os.path.split(used_sprites[-1])[0])+"\";\n"
        outfile += "real width = "+str(float(self.xtiles))+";\n"
        outfile += "real height = "+str(float(self.ytiles))+";\n"
        outfile += "sarray tileset = {"
        for t in used_sprites:
            if t == "":
                outfile+="\"default.png\", "
            else:
                outfile+="\""+os.path.split(t)[-1]+"\", "
        outfile = outfile[:-2]+"};\n"
        outfile += "array map = {"
        for x in new_map:
            outfile += str(x)+", "
        outfile = outfile[:-2]+"};\n"
        print outfile
        # os.split(x)[-1]
        print "filename:", filename[0]
        f = open(filename[0], "w")
        f.write(outfile)
        f.close()


# Create a GTK+ widget on which we will draw using Cairo
class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    current_fname = ""
    added_tiles = []
    tiles = []
    tiles_coords = []

    def periodic(self):
        self.queue_draw()
        return True

    def button_click_event(self, widget, data=None):
        print "data:", data
        self.current_fname = data
    
    def button_press_event(self, widget, event):
        print event.x, event.y
        tilex = int(event.x)/64
        tiley = int(event.y)/64
        print "tilex:", int(event.x)/64, "tiley:", int(event.y)/64
        if event.button == 1:
            if (self.current_fname!="") and (self.current_fname!="delete"):
                self.added_tiles.append((tilex, tiley, self.current_fname))
        elif event.button == 3:
            print "right"

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context
        cr_gdk = self.window.cairo_create()

        surface = cr_gdk.get_target()

        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(cr_surf)

        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        if self.m.is_updated == True:
            i = 0
            self.tiles_coords = []
            self.tiles = []
            for y, l in enumerate(self.m.tile_map):
                for x, t in enumerate(l):
                    if t!=0:
                        self.tiles_coords.append((x, y))
                        print t
                        tilename = self.m.tileset[t]
                        print "tilename:", tilename
                        self.tiles.append(cairo.ImageSurface.create_from_png(tilename))
                    i+=1
            self.m.is_updated = False
                    

        for i in self.added_tiles:
            if ((i[0], i[1]) in self.tiles_coords):
                idx = self.tiles_coords.index((i[0], i[1]))
                self.tiles[idx] = cairo.ImageSurface.create_from_png(i[2])
            else:
                self.tiles_coords.append((i[0], i[1]))
                self.tiles.append(cairo.ImageSurface.create_from_png(i[2]))

            if i[2] not in self.m.tileset:
                self.m.tileset.append(i[2])
            self.m.tile_map[i[1]][i[0]] = i[2]
            
        self.added_tiles = []
        for (x, y), i in zip(self.tiles_coords, self.tiles):
            cr.translate(x*64, y*64)
            cr.set_source_surface(i, 0, 0)
            cr.paint()
            cr.identity_matrix()

        cr.set_source_rgb(0,0,0)
        for x in range(self.m.xtiles+1):
            cr.move_to(64*x, 0)
            cr.line_to(64*x, self.height)
            # for y in m.ytiles:
        cr.stroke()

        for y in range(self.m.ytiles+1):
            cr.move_to(0, 64*y)
            cr.line_to(self.width, 64*y)
            # for y in m.ytiles:
        cr.stroke()


        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run(Widget):
    global vbox, widget, window
    m = Map()

    window = gtk.Window()
    window.connect("delete-event", gtk.main_quit)
    main_vbox = gtk.VBox()

    window2 = gtk.Window()
    window2.show()

    menubar = gtk.MenuBar()
    filemenu = gtk.Menu()
    filem = gtk.MenuItem("File")
    filem.set_submenu(filemenu)

    new = gtk.MenuItem("New")
    new.connect("activate", m.new)
    filemenu.append(new)

    menubar.append(filem)
    save = gtk.MenuItem("Save")
    save.connect("activate", m.save)
    filemenu.append(save)

    load = gtk.MenuItem("Load")
    load.connect("activate", m.load)
    filemenu.append(load)

    main_vbox.pack_start(menubar, False, False)

    vbox = gtk.VBox()


    widget = Widget()

    image = gtk.Image()
    image.set_from_file("delete.png")
    image.show()
    
    button = gtk.Button()
    button.add(image)
    button.show()
    button.connect("clicked", widget.button_click_event, "delete")
    vbox.pack_start(button, False, False)

    vbox.show()

    hbox = gtk.HBox()

    widget.m = m

    widget.connect("button_press_event", widget.button_press_event)
    widget.set_events(gtk.gdk.BUTTON_PRESS_MASK)
    # print dir(widget)
    # widget.m_window = window
    gobject.timeout_add(10, widget.periodic)
    widget.x = 0.
    widget.y = 0.
    widget.show()
    hbox.pack_start(widget, True, True)
    hbox.pack_start(vbox, False, False)
    hbox.show()
    main_vbox.add(hbox)
    main_vbox.show()
    window.add(main_vbox)
    window.present()

    widget.width = 64*m.xtiles
    widget.height = 64*m.ytiles

    width = vbox.get_allocation().width+widget.width
    height = widget.height
    window.resize(width, height)
    window.show_all()

    gtk.main()


if __name__ == "__main__":
    run(Screen)
