import os

class Map:
    def __init__(self):
        self.xtiles = 0
        self.ytiles = 0
        self.tile_map = []
        self.meta = False

    def mkEmptyMap(self, w, h, meta=""):
        self.xtiles = w
        self.ytiles = h
        self.tile_map = [[None for i in range(w)] for j in range(h)]
        if meta=="meta":
            self.meta = True

    def setMap(self, m):
        for y in range(self.ytiles):
            for x in range(self.xtiles):
                self.tile_map[y][x] = m[y][x]

    def __repr__(self):
        strout = ""
        for l in self.tile_map:
            for t in l:
                # print t
                strout += str(float(t if t != None else -1.0))+", "
            strout+="\n"
        strout = strout[:-3]
        return strout

class MapContainer:
    def __init__(self):
        self.xtiles = 0
        self.ytiles = 0
        self.maps = []
        self.is_updated = False
        self.tilesets = []
        self.tileset_paths = []
        self.px_scale = 0

    def __repr__(self):
        so = "real width = "+str(float(self.xtiles))+";\n"
        so+= "real height = "+str(float(self.ytiles))+";\n"
        so+= "real n_layers = "+str(float(len(self.maps)))+";\n"
        so+= "real px_scale = "+str(float(self.px_scale))+";\n"
        so+= "sarray paths = {"

        if (len(self.tileset_paths) == 0):
            raise ValueError("Empty map")

        for i, tp in enumerate(self.tileset_paths):
            so+= "\""+str(tp)+"\", "
        so = so[:-2]
        so+= "};\n"
        
        for i, ts in enumerate(self.tilesets):
            so+= "sarray tset_"+str(i)+" = {"
            for t in ts:
                so+= "\""+str(str(os.path.split(t)[1]))+"\", "
            so = so[:-2]
            so+= "};\n"
        
        for i, m in enumerate(self.maps):
            so+= "array map_"+str(i)+" = {"+repr(m)+"};\n"

        so+= "sarray meta = {"
        for m in self.maps:
            if m.meta == True:
                so+= "\"meta\", "
            else:
                so+= "\"\", "
        so = so[:-2]
        so+= "};\n"
            
        return so

    def setMap(self, m, layer):
        self.maps[layer].setMap(m)
        
    def newMap(self, w, h, scale):
        self.maps = []
        self.xtiles = w
        self.ytiles = h
        self.px_scale = scale
        self.tilesets = []
        self.is_updated = True

    def addMap(self, tileset, meta=""):
        m = Map()
        m.mkEmptyMap(self.xtiles, self.ytiles, meta)
        self.tilesets.append(tileset)
        self.maps.append(m)
        if meta == "meta":
            self.tileset_paths.append("")
        else:
            self.tileset_paths.append(str(os.path.split(tileset[-1])[0]))

