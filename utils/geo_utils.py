import math

tile_size = 256
earth_radius = 6378137  # meters
initial_resolution = 2 * math.pi * earth_radius / tile_size
origin_shift = 2 * math.pi * earth_radius / 2.0

class BoundingBox(object):
    def __init__(self, south: float, west: float, north: float, east: float):
        self.south = south
        self.west = west
        self.north = north
        self.east = east

    def to_tuple(self):
        """Return data as a tuple of (x_min, y_min, x_max, y_max)"""
        return (self.west, self.south, self.east, self.north)

    def __str__(self):
        return "(s:%f, w:%f, n:%f, e:%f)" % (self.south, self.west, self.north, self.east)

class GoogleStaticMaps(object):

    def __init__(self, center_lat: float, center_lng: float, image_w: int=640, image_h: int=640, zoom: int=20) -> None:
        self.center_lat, self.center_lng = center_lat, center_lng
        self.image_w, self.image_h, self.zoom = image_w, image_h, zoom
        return

    def _get_resolution(self, zoom: int) -> float:
        return initial_resolution / (2 ** zoom)

    def _pixels_to_meters(self, px: int, zoom: int) -> float:
        res = self._get_resolution(zoom)
        return px * res - origin_shift

    def _meters_to_lat_lon(self, mx: float, my: float) -> (float, float):
        lon = (mx / origin_shift) * 180.0
        lat = (my / origin_shift) * 180.0

        lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
        return lat, lon

    def _meters_to_pixels(self, mx, my):
        res = self._get_resolution(self.zoom)
        px = (mx + origin_shift) / res
        py = (my + origin_shift) / res
        return px, py

    def _lat_lon_to_meters(self, lat, lon):
        mx = lon * origin_shift / 180.0
        my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
        my = my * origin_shift / 180.0
        return mx, my

    def get_image_bounding_box(self) -> BoundingBox:
        mx, my = self._lat_lon_to_meters(self.center_lat, self.center_lng)
        pixel_x, pixel_y = self._meters_to_pixels(mx, my)
        w_pixel_x, e_pixel_x = pixel_x - self.image_w / 2, pixel_x + self.image_w / 2
        s_pixel_y, n_pixel_y = pixel_y - self.image_h / 2, pixel_y + self.image_h / 2

        w_meter_x = self._pixels_to_meters(w_pixel_x, self.zoom)
        e_meter_x = self._pixels_to_meters(e_pixel_x, self.zoom)
        s_meter_y = self._pixels_to_meters(s_pixel_y, self.zoom)
        n_meter_y = self._pixels_to_meters(n_pixel_y, self.zoom)

        s_lat, w_lng = self._meters_to_lat_lon(w_meter_x, s_meter_y)
        n_lat, e_lng = self._meters_to_lat_lon(e_meter_x, n_meter_y)

        return BoundingBox(s_lat, w_lng, n_lat, e_lng)