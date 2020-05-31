import grequests
import json
import os
import os.path as path
import random
import time
from tqdm import tqdm

from utils.signature import StaticMapURLSigner

MAX_NO_OF_TRIES = 2

class TileDownloader(object):
    def __init__(self, tiles_path, tiles_json, clientID, secret_key, skip, logger):
        tiles = tiles_json['tiles']
        self.tiles_path = tiles_path
        #self.key = key
        self.clientID = clientID
        self.secret_key = secret_key

        self.config = tiles_json['config']
        self.primary = tiles['primary']
        self.half = tiles['half']
        self.skip = skip
        self.logger = logger

    def download(self):
        self.download_tiles(self.primary)
        self.download_tiles(self.half, prefix='half-')
        
    def download_tiles(self, tiles, prefix=''):
        batches = chunks(tiles, 5)
        for batch in tqdm(batches):
            self.download_batch(batch, prefix)
            
    def url_signer(self, url):
        staticmap_url_signer = StaticMapURLSigner(private_key=self.secret_key)
        return staticmap_url_signer.sign_url(url)

    def download_batch(self, batch, prefix):
        if self.skip:
            batch = filter(lambda tile: not os.path.isfile(tile_path(self.tiles_path, prefix, tile['x'], tile['y'])), batch)
        batch_size = len(list(batch))
        correct_response_count = 0
        tries = 0
        while correct_response_count !=batch_size and batch_size != 0 and tries<MAX_NO_OF_TRIES:
            random_wait = random.randint(0,5)
            time.sleep(random_wait)
            rs = (grequests.get(self.url_signer('{0}&client={1}'.format(tile['url'], self.clientID))) for tile in list(batch))
            responses = grequests.map(rs)
            tries+=1
            try:
                for response in responses:
                    status_code = response.status_code
                    correct_response_count +=1
            except AttributeError:
                correct_response_count = 0
        

        for index in range(batch_size):
            response = responses[index]
            tile = batch[index]
            if response.status_code == 200:
                file_name = tile_path(self.tiles_path, prefix, tile['x'], tile['y'])
                save_response_to(response, file_name)
            else:
                print(response.status_code)

def tile_path(directory, prefix, x, y):
    return path.join(directory, '{prefix:s}{x:d}x{y:d}.png'.format(prefix=prefix, x=x, y=y))
    
def save_response_to(response, path):
    with open(path, 'wb') as f:
        for chunk in response.iter_content():
            f.write(chunk)
        
def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]
    
