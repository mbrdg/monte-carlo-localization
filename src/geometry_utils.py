import math

from shapely.geometry import LineString


def sign(x):
    return -1 if x < 0 else 1


def circle_line_collision(l1, l2, cpt, r):
    x1 = l1[0] - cpt[0]
    y1 = l1[1] - cpt[1]
    x2 = l2[0] - cpt[0]
    y2 = l2[1] - cpt[1]
    dx = x2 - x1
    dy = y2 - y1
    dr = math.sqrt(dx*dx + dy*dy)
    D = x1 * y2 - x2 * y1
    discriminant = r*r*dr*dr - D*D
    if discriminant < 0:
        return []
    if discriminant == 0:
        xa = (D * dy) / (dr * dr)
        ya = (-D * dx) / (dr * dr)
        ta = (xa-x1)*dx/dr + (ya-y1)*dy/dr
        return [(xa + cpt[0], ya + cpt[1])] if 0 < ta < dr else []

    xa = (D * dy + sign(dy) * dx * math.sqrt(discriminant)) / (dr * dr)
    ya = (-D * dx + abs(dy) * math.sqrt(discriminant)) / (dr * dr)
    ta = (xa-x1)*dx/dr + (ya-y1)*dy/dr
    xpt = [(xa + cpt[0], ya + cpt[1])] if 0 < ta < dr else []

    xb = (D * dy - sign(dy) * dx * math.sqrt(discriminant)) / (dr * dr)
    yb = (-D * dx - abs(dy) * math.sqrt(discriminant)) / (dr * dr)
    tb = (xb-x1)*dx/dr + (yb-y1)*dy/dr
    xpt += [(xb + cpt[0], yb + cpt[1])] if 0 < tb < dr else []
    return xpt


def line_line_intersection(line1, line2):
    line1 = LineString(line1)
    line2 = LineString(line2)

    res = line1.intersection(line2)
    return (res.x, res.y) if res.geom_type == "Point" else None
