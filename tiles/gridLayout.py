from dataclasses import dataclass


class GridLayout:
    def tile_to_pixel(self, x, y, tile_width, tile_height):
        raise NotImplementedError

    def chunk_pixel_size(self, chunk_size, tile_width, tile_height):
        return chunk_size * tile_width, chunk_size * tile_height

    def rotation_angles(self):
        raise NotImplementedError

    def neighbor_position(self, anchor_x, anchor_y, dx, dy, angle, flip_h, flip_v):

        raise NotImplementedError


def _rotate_offset_square(dx, dy, angle):
    turns = (angle // 90) % 4
    for _ in range(turns):
        dx, dy = -dy, dx
    return dx, dy


def _transform_offset_square(dx, dy, angle, flip_h, flip_v):
    if flip_h:
        dx = -dx
    if flip_v:
        dy = -dy
    return _rotate_offset_square(dx, dy, angle)


class SquareGridLayout(GridLayout):
    def tile_to_pixel(self, x, y, tile_width, tile_height):
        return x * tile_width, y * tile_height

    def rotation_angles(self):
        return (0, 90, 180, 270)

    def neighbor_position(self, anchor_x, anchor_y, dx, dy, angle, flip_h, flip_v):
        tdx, tdy = _transform_offset_square(dx, dy, angle, flip_h, flip_v)
        return anchor_x + tdx, anchor_y + tdy


def _offset_to_axial(x, y):
    q = x - (y - (y & 1)) // 2
    r = y
    return q, r


def _axial_to_offset(q, r):
    x = q + (r - (r & 1)) // 2
    y = r
    return x, y


def _rotate_axial60(q, r, angle):
    x, z = q, r
    y = -x - z
    steps = (angle // 60) % 6
    for _ in range(steps):
        x, y, z = -z, -x, -y
    return x, z


def _flip_axial_h(q, r):
    s = -q - r
    return s, r


def _flip_axial_v(q, r):
    s = -q - r
    return q, s


@dataclass
class HexGridLayout(GridLayout):

    row_height_ratio: float = 0.75

    def tile_to_pixel(self, x, y, tile_width, tile_height):
        y_step = tile_height * self.row_height_ratio
        x_offset = (tile_width / 2) if (y % 2) else 0
        return x * tile_width + x_offset, y * y_step

    def chunk_pixel_size(self, chunk_size, tile_width, tile_height):
        y_step = tile_height * self.row_height_ratio
        width = chunk_size * tile_width + tile_width / 2
        height = (chunk_size - 1) * y_step + tile_height
        return width, height

    def rotation_angles(self):
        return (0, 60, 120, 180, 240, 300)

    def neighbor_position(self, anchor_x, anchor_y, dx, dy, angle, flip_h, flip_v):
        q, r = dx, dy
        if flip_h:
            q, r = _flip_axial_h(q, r)
        if flip_v:
            q, r = _flip_axial_v(q, r)
        q, r = _rotate_axial60(q, r, angle)

        aq, ar = _offset_to_axial(anchor_x, anchor_y)
        return _axial_to_offset(aq + q, ar + r)



def _offset_to_axial_flat(x, y):
    q = x
    r = y - (x - (x & 1)) // 2
    return q, r
 
 
def _axial_to_offset_flat(q, r):
    x = q
    y = r + (q - (q & 1)) // 2
    return x, y
 
 
@dataclass
class FlatTopHexGridLayout(GridLayout):
    column_width_ratio: float = 0.75
 
    def tile_to_pixel(self, x, y, tile_width, tile_height):
        x_step = tile_width * self.column_width_ratio
        y_offset = (tile_height / 2) if (x % 2) else 0
        return x * x_step, y * tile_height + y_offset
 
    def chunk_pixel_size(self, chunk_size, tile_width, tile_height):
        x_step = tile_width * self.column_width_ratio
        width = (chunk_size - 1) * x_step + tile_width
        height = chunk_size * tile_height + tile_height / 2
        return width, height
 
    def rotation_angles(self):
        return (0, 60, 120, 180, 240, 300)
 
    def neighbor_position(self, anchor_x, anchor_y, dx, dy, angle, flip_h, flip_v):
        q, r = dx, dy
        if flip_h:
            q, r = _flip_axial_h(q, r)
        if flip_v:
            q, r = _flip_axial_v(q, r)
        q, r = _rotate_axial60(q, r, angle)
 
        aq, ar = _offset_to_axial_flat(anchor_x, anchor_y)
        return _axial_to_offset_flat(aq + q, ar + r)