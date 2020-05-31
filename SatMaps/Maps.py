#Standard imports
from distutils.dir_util import mkpath
import argparse
import json
import os.path as path
import os
import gdal

#Custom imports
from JioMaps.TileMachine import TileMachine
from JioMaps.TileDownloader import TileDownloader
from JioMaps.TileStitcher import TileStitcher
from utils.utils import setup_logger
from utils.geo import LatLng, LatLngBounds


class Maps(object):
    def __init__(self, args, logger, unknown = {}):
        self.args = args
        self.logger = logger
        self.TILES_FILE_NAME = 'tiles.json'
        self.unknown = unknown
        self.project_path = path.join(os.getcwd(), self.args.data_dir, self.args.project)
        self.tiles_path = path.join(self.project_path, 'tiles')
        
    def generate(self):
        
        mkpath(self.project_path)
        self.logger.info('Generating tiles for ' + self.args.project + ' at scale ' + str(self.args.scale))
        #Initialize TileMachine and save all urls to be downloaded
        tile_machine = TileMachine(latlong = self.args.southwest, size=self.args.size, scale=self.args.scale,
                                   format=self.args.format, maptype=self.args.maptype, params=self.unknown, logger=self.logger)
        
        def tiles_to_json(tiles): return map(lambda tile: { 'url': tile.url, 'x': tile.x, 'y': tile.y }, tiles)
        
        def parse_latlng(latlng_str): return map(lambda a: float(a), latlng_str.split(',', 2))

        bounds = LatLngBounds(
            LatLng(*parse_latlng(self.args.southwest)),
            LatLng(*parse_latlng(self.args.northeast)))

        tiles = tile_machine.tiles_from_bounds(bounds)
        tiles_file = open(path.join(self.project_path, self.TILES_FILE_NAME), 'w')

        output = {
            'config': {
                'zoom': tile_machine.get_zoom_level(),
                'size': self.args.size,
                'scale': self.args.scale,
                'southwest': self.args.southwest,
                'northeast': self.args.northeast
            },
            'tiles': {
                'primary': list(tiles_to_json(tiles['primary'])),
                'half': list(tiles_to_json(tiles['half']))
            }
        }
        self.logger.info("Total tiles:" + str(len(tiles['primary']) + len(tiles['half'])))

        json.dump(output, tiles_file)
        return output
    
    def download(self, tiles_json):
        mkpath(self.tiles_path)
        downloader = TileDownloader(self.tiles_path, tiles_json, self.args.clientID, self.args.secret_key, self.args.skip, self.logger)
        downloader.download()
        self.logger.info("Tile download complete for" + self.args.project)
    
    def stitch(self, tiles_json):
        stitcher = TileStitcher(self.tiles_path, tiles_json, self.args.raster_path, self.args.data_dir, self.logger)
        stitcher.stitch()
        stitcher.georeference()
