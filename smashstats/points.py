import math

def euclid_distance(point1, point2):
    """
    Calculate the euclidean distance between two points
    """
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def offset(point1, point2, scale=1):
    """
    Offsets a point by a given offset and scale
    """
    return (int(round(point1[0] + (point2[0] * scale))), int(round(point1[1] + point2[1] * scale)))

def scale_point(point1, scale):
    """
    Scale a point by the given scale
    """
    return (int(round(point1[0] * scale)), int(round(point1[1] * scale)))

def remove_neighbors(points, distance=5):
    """
    Remove neighbors selects a single point from a cluster of points in a given distance
    """
    consolidated = []
    for point in points:
        near = False
        for chosen_point in consolidated:
            if euclid_distance(point, chosen_point) < distance:
                near = True
        if not near:
            consolidated.append(point)
    return consolidated
