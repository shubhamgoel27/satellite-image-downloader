from PIL import Image
import os.path as path
import gdal
import numpy as np
import os

from utils.geo_utils import GoogleStaticMaps, BoundingBox

class TileStitcher(object):
    def __init__(self, tiles_path, tiles_json, raster_path, raster_dir, logger=None):
        self.tiles = tiles_json['tiles']

        self.tiles_path = tiles_path
        self.config = tiles_json['config']
        self.primary = self.tiles['primary']
        self.half = self.tiles['half']
        self.raster_path = raster_path
        self.raster_dir = raster_dir
        self.zoom= self.config['zoom']
        self.logger = logger
        self.crop_shift = 100

        last_tile = self.primary[-1]
        self.size = self.config['size'] * self.config['scale']
        self.tile_size = self.config['size']
        self.crop = (0, 0, self.size, self.size - 30 * self.config['scale'])
        self.x_tiles = last_tile['x'] + 1
        self.y_tiles = last_tile['y'] + 1

    def stitch(self):
        self.logger.info("Creating image of size:" + str(self.size*self.x_tiles) + "x" + str(self.size*self.y_tiles))
        dst = gdal.GetDriverByName("GTiff").Create(self.raster_dir + "temp_" + self.raster_path, self.size*(1+self.x_tiles), self.size*(1+self.y_tiles),3, options=['COMPRESS=LZW', 'BIGTIFF=YES', 'TILED=YES'])  
        #Creating tiff with cropped bounds 
        cropped_dst = gdal.GetDriverByName("GTiff").Create(self.raster_dir + self.raster_path, self.size*self.x_tiles - self.crop_shift, self.size*self.y_tiles,3, options=['COMPRESS=LZW', 'BIGTIFF=YES', 'TILED=YES']) 
        #print("combining full tiles")
        dst = self.combine_tiles(dst, self.primary)
        #print("combining half tiles")
        dst = self.combine_tiles(dst, self.half, prefix='half-', offset=-self.size//2, crop=True)
        min_bound = self.size//2
        max_x_bound = min_bound + self.size*self.x_tiles
        max_y_bound = min_bound + self.size*self.y_tiles
  
        for i in range(1,4):
            band_array = dst.GetRasterBand(i).ReadAsArray()[min_bound:max_y_bound, min_bound + self.crop_shift:max_x_bound]
            cropped_dst.GetRasterBand(i).WriteArray(band_array)
        cropped_dst.FlushCache() #Saves to disk
        cropped_dst = None
        os.remove(self.raster_dir + "temp_" + self.raster_path)

        return None

    def combine_tiles(self, dst, tiles, prefix='', offset=0, crop=False):
        for tile in tiles:
            x, y = tile['x'], tile['y']
            tile_image_path = path.join(self.tiles_path, '{prefix:s}{x:d}x{y:d}.png'.format(x=x, y=y, prefix=prefix))
            files_not_downloaded = []
            try:
                img = Image.open(tile_image_path)
                if crop:
                    img = img.crop(self.crop)
                img=img.convert("RGB")
                img_np = np.asarray(img)
            except FileNotFoundError:
                img_np = np.zeros((self.size, self.size, 3))
                files_not_downloaded.append(tile_image_path)
            #Writing img_np to raster with an offset of size/2,size/2 from top-left origin
            for i in range(1,4):
                dst.GetRasterBand(i).WriteArray(img_np[:,:,i-1],x*self.size + offset + self.size//2, y*self.size + offset + self.size//2)
        self.logger.info("Tiles not downloaded: " + str(len(files_not_downloaded)) +  " | Tiles:" + str(files_not_downloaded))
        return dst
    
    def get_stitched_tile_bounds(self):
        top_left_tile_coords = [url for url in self.primary[0]['url'].split('?')[1].split('&') if 'center' in url][0].strip('center=').split('%2C') 
        top_left_tile_coords = [float(x) for x in top_left_tile_coords]
        bottom_right_tile_coords = [url for url in self.primary[-1]['url'].split('?')[1].split('&') if 'center' in url][0].strip('center=').split('%2C') 
        bottom_right_tile_coords = [float(x) for x in bottom_right_tile_coords]
        gmaps_top_left_bbox = GoogleStaticMaps(top_left_tile_coords[0], top_left_tile_coords[1],self.tile_size - (self.crop_shift*2),self.tile_size, self.zoom).get_image_bounding_box()
        gmaps_bottom_right_bbox = GoogleStaticMaps(bottom_right_tile_coords[0], bottom_right_tile_coords[1],self.tile_size , self.tile_size, self.zoom).get_image_bounding_box()
        return (gmaps_top_left_bbox.north, gmaps_top_left_bbox.west, gmaps_bottom_right_bbox.south, gmaps_bottom_right_bbox.east)
    
    def georeference(self):
        ullat, ullon, lrlat, lrlon = self.get_stitched_tile_bounds()
        self.logger.info("Bounding box NW: [" +  str(ullat) + ", " + str(ullon) + "] SE: [" + str(lrlat) + ", " + str(lrlon) + "]")
        trans = "gdal_translate -of GTiff -co 'COMPRESS=LZW' -co 'BIGTIFF=YES' -co 'TILED=YES' -a_ullr {ullon} {ullat} {lrlon} {lrlat} -a_srs EPSG:4269 {dir}{path} {dir}ref_{path}".format(
            ullon=ullon,
            ullat=ullat,
            lrlat=lrlat,
            lrlon=lrlon,
            dir=self.raster_dir,
            path=self.raster_path
        )

        wrap = "gdalwarp -of GTiff  -co 'COMPRESS=LZW' -co 'BIGTIFF=YES' -co 'TILED=YES' -t_srs EPSG:3857 {dir}ref_{path} {dir}finished_{path}".format(
            dir=self.raster_dir,
            path=self.raster_path
        )

        os.system(trans)
        os.system(wrap)
        os.remove(self.raster_dir + "ref_" + self.raster_path)
        os.remove(self.raster_dir + self.raster_path)
        os.rename(self.raster_dir + "finished_" + self.raster_path, self.raster_dir + self.raster_path)
        self.logger.info("Georeferenced tiff stored at: " + self.raster_dir + self.raster_path)