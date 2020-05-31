import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
import argparse
from SatMaps.Maps import Maps
from utils.utils import setup_logger
from distutils.dir_util import mkpath

def parse_args():
    """Evaluation options for SatMaps download tool"""
    parser = argparse.ArgumentParser(description='Satellite Map Generator')
    # input_folder
    parser.add_argument('project', action='store', help='Directory to store this project in')
    parser.add_argument('--southwest', action='store', required=True, help='Southwest latitude and longitude. e.g. --southwest=39.1,-83.2')
    parser.add_argument('--northeast', action='store', required=True, help='Northeast latitude and longitude, e.g. --northeast=40.3,-82.4')
    parser.add_argument('--scale', action='store', type=int, default=1, help='Scale of image (1, 2)')
    parser.add_argument('--size', action='store', type=int, default=2048, help='Size of image')
    parser.add_argument('--format', action='store', default='png', help='File type')
    parser.add_argument('--maptype', action='store', default='satellite', help='Map type')
    parser.add_argument('--clientID', action='store',default=os.environ['GOOGLE_CLIENT_ID'], help='Google API client ID')
    parser.add_argument('--secret_key', action='store', default=os.environ['GOOGLE_SECRET_KEY'], help='Google API secret key')
    parser.add_argument('--skip', action='store_true', help='Redownload existing tiles')
    parser.add_argument('--raster_path', action='store', default='output.tif', help='Output Raster path')
    parser.add_argument('--data_dir', type=str, default='data/',
                        help='data directory (default: /data/input/)')
    
    args, unknown = parser.parse_known_args()

    return args, unknown

if __name__ == "__main__":
    args, unknown = parse_args()
    wrdr = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mkpath(args.data_dir)
    logger = setup_logger('gis_logger',
                               os.path.join(args.data_dir,"Maps.log"))
    logger.info('Logger initialized')
    maps = Maps(args, logger, unknown)
    tiles = maps.generate()
    maps.download(tiles)
    maps.stitch(tiles)
