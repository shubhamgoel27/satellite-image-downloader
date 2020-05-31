from PIL import Image
import os.path as path
import json
import gdal
import numpy as np
import os
import time
import math
from distutils.dir_util import mkpath

from maps_stitcher.geo import LatLng, LatLngBounds
from maps_stitcher.geo_utils import GoogleStaticMaps, BoundingBox

from maps_stitcher.TileDownloader import TileDownloader
from maps_stitcher.TileMachine import TileMachine
from maps_stitcher.TileStitcher import TileStitcher

zoom=21
scale=1
size=512
format = 'png'
maptype = 'satellite'
data_dir='aois/'
clientID = os.environ['GOOGLE_CLIENT_ID']
secret_key = os.environ['GOOGLE_SECRET_KEY']
unknown = {}

with open("remaining_aois.json") as f:
    aoi_bounds = json.load(f)
    
TILES_FILE_NAME = 'tiles.json'

for aoi_name in aoi_bounds:
    project_path = aoi_name.split(".")[0]
    aoi = aoi_bounds[aoi_name]
    southwest = str(aoi[0][1][1]) + "," + str(aoi[0][1][0])
    northeast = str(aoi[0][3][1]) + "," + str(aoi[0][3][0])
    raster_path=aoi_name
    
    print("Starting generating tiles for", project_path)
    tile_machine = TileMachine(size=size, zoom=zoom, scale=scale, format=format, maptype=maptype, params=unknown)
    def tiles_to_json(tiles): return map(lambda tile: { 'url': tile.url, 'x': tile.x, 'y': tile.y }, tiles)
    def parse_latlng(latlng_str): return map(lambda a: float(a), latlng_str.split(',', 2))

    bounds = LatLngBounds(
        LatLng(*parse_latlng(southwest)),
        LatLng(*parse_latlng(northeast)))

    project_path = path.join(os.getcwd(), project_path)
    mkpath(project_path)

    tiles = tile_machine.tiles_from_bounds(bounds)
    tiles_file = open(path.join(project_path, TILES_FILE_NAME), 'w')

    output = {
        'config': {
            'zoom': zoom,
            'size': size,
            'scale': scale,
            'southwest': southwest,
            'northeast': northeast
        },
        'tiles': {
            'primary': list(tiles_to_json(tiles['primary'])),
            'half': list(tiles_to_json(tiles['half']))
        }
    }

    json.dump(output, tiles_file)
    #Downloaded all urls in the tiles folder
    tiles_path = path.join(project_path, 'tiles')
    mkpath(tiles_path)
    t_download_start = time.time()
    print("Now starting download for", project_path)
    downloader = TileDownloader(tiles_path, output, clientID, secret_key, skip=False)
    downloader.download()
    t_download_end = time.time()
    print("Downloaded in", t_download_end - t_download_start)
    print("Starting stitching...")
    stitcher = TileStitcher(tiles_path, output, raster_path) #json.load(tiles_json) not working
    stitcher.stitch()
    t_stitch_end = time.time()
    print("Stitched in", t_stitch_end - t_download_end)
    stitcher.georeference()
    print("Georeferenced in", time.time() - t_stitch_end)
    print("Geoferenced image saved for", project_path)
    
print("Operation complete... :D")
