import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

import os
import sys
import parser

from map_container import *

meta_markers = [(0, 1, 0), (1, 0, 0)]

class Screen(gtk.DrawingArea):
    __gsignals__ = { "expose-event": "override" }
    def __init__(self):
        super(Screen, self).__init__()
        self.scale = 1
        self.ox = 0
        self.oy = 0
        # scale = 1 means that 1 cell is 32 pixel wide
        self.px_scale = 32*self.scale
        self.container = MapContainer()
        self.width = 240
        self.height = 160
        self.current_fname = ""
        self.cairo_maps = []
        self.cairo_tiles = []
        self.active_layer = None
        self.lbutton_pressed = False

    def save(self, path):
        f = open(path, "w")
        f.write(repr(self.container))
        f.close()

    def newMap(self, w, h, scale):
        self.px_scale = scale
        self.container.xtiles = w
        self.container.ytiles = h
        self.cairo_maps = []
        self.container.tilesets = []
        self.active_layer = None
        self.container.newMap(w, h, scale)

    def newTileLayer(self, tileset, meta=""):
        self.cairo_maps.append([[None for x in range(self.width)] for y in range(self.height)])
        self.active_layer = len(self.container.tilesets)
        self.cairo_tiles.append([])

        if meta == "meta":
            tset = []
            for i, (r, g, b) in enumerate(meta_markers):
                tset.append(str(i))
                cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.px_scale, self.px_scale)
                cr = cairo.Context(cr_surf)
                cr.set_source_rgb(r, g ,b)
                cr.rectangle(0, 0, self.px_scale, self.px_scale)
                cr.fill()
                self.cairo_tiles[self.active_layer].append(cr_surf)
            self.container.addMap(tset, meta)
        else:
            self.container.addMap(tileset,  meta)
            for t in tileset:
                print "creating surface for", t
                self.cairo_tiles[self.active_layer].append(cairo.ImageSurface.create_from_png(t))
    def setMap(self, m, layer):
        self.container.setMap(m, layer)

    def periodic(self):
        self.queue_draw()
        return True

    def hscroll(self, val):
        print "hscroll:", val.get_value()
        value = val.get_value()
        self.ox = value*self.container.xtiles*self.px_scale
        print self.ox

    def vscroll(self, val):
        print "vscroll:", val.get_value()
        value = val.get_value()
        self.oy = value*self.container.ytiles*self.px_scale

    def __put_tile(self, x, y):
        tilex = int(x+self.ox)/self.px_scale
        tiley = int(y+self.oy)/self.px_scale
        if tilex<0 or tilex>self.container.xtiles or tiley<0 or tiley>self.container.ytiles:
            return True
        if (self.current_fname!="") and (self.current_fname!="delete"):
            print "cur fname:", self.current_fname, "tileset:", self.container.tilesets[self.active_layer]
            if self.current_fname in self.container.tilesets[self.active_layer]:
                sprite_id = self.container.tilesets[self.active_layer].index(self.current_fname)
                if not (self.container.maps[self.active_layer].tile_map[tiley][tilex] == sprite_id):
                    self.container.maps[self.active_layer].tile_map[tiley][tilex] = sprite_id
                    self.cairo_maps[self.active_layer][tiley][tilex] = self.cairo_tiles[self.active_layer][sprite_id]

    def button_click_event(self, widget, data=None):
        print "data:", data
        self.current_fname = data

    def button_press_event(self, widget, event):
        print event.x, event.y
        print "tilex:", int(event.x)/64, "tiley:", int(event.y)/64
        if event.button == 1:
            self.lbutton_pressed = True
            self.__put_tile(event.x, event.y)
        elif event.button == 3:
            print "right"

    def button_release_event(self, widget, event):
        print "release:", event.x, event.y
        if event.button == 1:
            self.lbutton_pressed = False

    def motion_notify_event(self, widget, event):
        # print "motion:", event.x, event.y
        if (not self.lbutton_pressed):
            return
        self.__put_tile(event.x, event.y)

    def do_expose_event(self, event):

        if self.active_layer == None:
            return
        
        # Create the cairo context
        cr_gdk = self.window.cairo_create()

        surface = cr_gdk.get_target()

        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(cr_surf)

        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()


        cr.set_source_rgb(0,0,0)
        xtiles = self.container.xtiles-self.ox/self.px_scale
        ytiles = self.container.ytiles-self.oy/self.px_scale
        render_xtiles = self.width/self.px_scale + 1
        render_ytiles = self.height/self.px_scale + 1
        if render_xtiles > xtiles:
            render_xtiles = xtiles
        if render_ytiles > ytiles:
            render_ytiles = ytiles

        for x in range(0, int(render_xtiles+1)):
            cr.move_to(self.px_scale*x-(self.ox%self.px_scale), 0)
            cr.line_to(self.px_scale*x-(self.ox%self.px_scale), self.height)
            # for y in m.ytiles:
        cr.stroke()

        for y in range(0, int(render_ytiles+1)):
            cr.move_to(0, self.px_scale*y-(self.oy%self.px_scale))
            cr.line_to(self.width, self.px_scale*y-(self.oy%self.px_scale))
            # for y in m.ytiles:
        cr.stroke()


        start_xtile = self.ox/self.px_scale
        start_xtile = start_xtile if start_xtile<self.container.xtiles else self.container.xtiles-1
        start_ytile = self.oy/self.px_scale
        start_ytile = start_ytile if start_ytile<self.container.ytiles else self.container.ytiles-1

        end_xtile = int(start_xtile+render_xtiles)
        end_xtile = end_xtile if end_xtile<self.container.xtiles else self.container.xtiles

        end_ytile = int(start_ytile+render_ytiles)
        end_ytile = end_ytile if end_ytile<self.container.ytiles else self.container.ytiles


        for l in range(len(self.container.maps)):
            for x in range(int(start_xtile), end_xtile):
                for y in range(int(start_ytile), end_ytile):

                    sprite_id = self.container.maps[l].tile_map[y][x]
                    if sprite_id!=None:
                        sprite = self.cairo_tiles[l][sprite_id]
                        cr.translate(x*self.px_scale-self.ox, y*self.px_scale-self.oy)

                        cr.set_source_surface(sprite, 0, 0)
                        cr.paint_with_alpha(0.8)
                        cr.identity_matrix()
                    text1 = str(x)
                    text2 = str(self.container.ytiles-y)
                    xbearing, ybearing, width, height, xadvance, yadvance = (
                        cr.text_extents(text2))
                    cr.move_to(x*self.px_scale-self.ox, y*self.px_scale-self.oy-height)
                    cr.set_source_rgb(0,0,0)
                    cr.set_font_size(8)
                    cr.show_text(text1)
                    cr.move_to(x*self.px_scale-self.ox, y*self.px_scale-self.oy)
                    cr.show_text(text2)


        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()
