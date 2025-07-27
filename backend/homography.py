import numpy as np
import cv2

def get_homography(src_points, dst_points):
    '''
    src_points: 4 točke na slici (iz videa)
    dst_points: 4 točke na 2D terenu (ciljne koordinate)
    '''
    H, _ = cv2.findHomography(np.array(src_points), np.array(dst_points))
    return H

def map_point(point, H):
    '''
    point: (x, y) na slici
    H: homografijska matrica
    '''
    pt = np.array([ [point[0], point[1], 1] ]).T
    mapped = H @ pt
    mapped = mapped / mapped[2]
    return (float(mapped[0]), float(mapped[1])) 